from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import mpmath as mp
import pytest

from schwgw.validation.phase6_v3_hp_unitarity_oracle import (
    HPUnitarityOracleError,
    gamma_decimal_value,
    independent_geometry,
    precision_schedule,
    validate_oracle_ladder,
)
from schwgw.validation.phase6_v3_mode_greybody import (
    V31ContractError,
    build_mode_inventory,
)
from schwgw.validation.phase6_v3_mode_greybody_hp_replacement import (
    build_route_map,
    geometry_preflight,
    synthetic_payload,
    validate_import_isolation,
    validate_route_map,
)


def _views(*, small: bool = True) -> list[dict[str, object]]:
    views = []
    for ordinal, key in enumerate(build_mode_inventory()):
        exponent = -14 if small else -2
        gamma = mp.mpf("1.25") * mp.power(10, exponent)
        views.append(
            {
                "ordinal": ordinal,
                "mode": key.payload(),
                "Gamma_flux_decimal": {"exponent10": exponent, "mantissa": "1.25"},
                "log_Gamma_flux": mp.nstr(mp.log(gamma), 50),
                "source_record_sha256": hashlib.sha256(
                    str(ordinal).encode()
                ).hexdigest(),
            }
        )
    return views


def _complex_record(value: mp.mpc, digits: int = 210) -> dict[str, str]:
    real, imag = mp.nstr(value.real, digits), mp.nstr(value.imag, digits)
    z = mp.mpc(real, imag)
    return {"real": real, "imag": imag, "abs": mp.nstr(abs(z), digits)}


def _ladder() -> list[dict[str, object]]:
    records = []
    schedule = [80, 120, 180]
    with mp.workdps(220):
        for ordinal, dps in enumerate(schedule):
            gamma = mp.mpf("1e-14") * (1 + mp.mpf(ordinal) * mp.mpf("1e-12"))
            modulus = mp.sqrt(1 - gamma)
            s_value = modulus * mp.e ** (mp.mpf("0.3") * 1j)
            records.append(
                {
                    "schema": "schwo.phase6.v3_1_u.oracle_node.v1",
                    "mode": {"kM": "0.005", "ell": 2, "parity": "odd"},
                    "mode_ordinal": 0,
                    "precision_ordinal": ordinal,
                    "requested_dps": dps,
                    "guard_digits": dps - 14,
                    "precision_schedule": schedule,
                    "route_map_sha256": "a" * 64,
                    "fresh_call_id": str(ordinal) * 64,
                    "fresh_call_count": 1,
                    "route_b_record_or_cache_reused": False,
                    "route_a_numerical_code_shared": False,
                    "protected_radial_imported": False,
                    "S_U": _complex_record(s_value),
                    "Gamma_S_U": mp.nstr(gamma, 210),
                    "log_Gamma_S_U": mp.nstr(mp.log(gamma), 210),
                }
            )
    return records


def test_precision_schedule_and_direct_decimal_fail_closed() -> None:
    assert precision_schedule({"exponent10": -14, "mantissa": "1.25"}) == (80, 120, 180)
    assert precision_schedule({"exponent10": -91, "mantissa": "9.0"}) == (140, 180, 240)
    assert gamma_decimal_value({"exponent10": -14, "mantissa": "1.25"}) > 0
    with pytest.raises(HPUnitarityOracleError):
        precision_schedule({"exponent10": -14, "mantissa": "0.99"})
    with pytest.raises(HPUnitarityOracleError):
        precision_schedule({"exponent10": -14, "mantissa": "nan"})


def test_geometry_closed_boundary_neighbours_and_ambient_precision() -> None:
    decisions: list[tuple[int, str]] = []
    for ambient in (37, 120, 220, 301):
        with mp.workdps(ambient):
            k = mp.mpf("0.005")
            match = mp.sqrt(110) / k
            radius, exponent = independent_geometry(
                ell=10, k=k, k_decimal="0.005", match_radius=match
            )
            decisions.append((exponent, mp.nstr(radius / match, 10)))
    assert decisions == [(2, "4.0")] * 4

    with mp.workdps(100):
        # Canonical decimal values immediately below/above the q=1 and q=0
        # fixed-radius boundaries retain the first-admissible ordering.
        for k_text, expected in (
            ("0.069", 2),
            ("0.071", 1),
            ("0.139", 1),
            ("0.141", 0),
        ):
            k = mp.mpf(k_text)
            match = max(mp.mpf(300), mp.sqrt(110) / k)
            assert (
                independent_geometry(ell=10, k=k, k_decimal=k_text, match_radius=match)[
                    1
                ]
                == expected
            )
        with pytest.raises(HPUnitarityOracleError, match="match radius"):
            independent_geometry(
                ell=10,
                k=mp.mpf("0.1"),
                k_decimal="0.1",
                match_radius=mp.mpf(301),
            )
        for bad_ell, bad_k, bad_radius in (
            (True, mp.mpf("0.1"), mp.mpf(300)),
            (1, mp.mpf("0.1"), mp.mpf(300)),
            (2, mp.mpf("nan"), mp.mpf(300)),
            (2, mp.mpf("0.1"), mp.mpf("inf")),
        ):
            with pytest.raises(HPUnitarityOracleError):
                independent_geometry(
                    ell=bad_ell,
                    k=bad_k,
                    k_decimal=mp.nstr(bad_k, 20),
                    match_radius=bad_radius,
                )


def test_exact_318_by_3_geometry_inventory_is_solver_free(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    calls = {"science": 0}

    def forbidden(*_args, **_kwargs):
        calls["science"] += 1
        raise AssertionError("geometry proof called a numerical solver")

    monkeypatch.setattr(replacement, "solve_oracle_node", forbidden)
    monkeypatch.setattr(replacement.cycle2, "solve_route_a_mode", forbidden)
    monkeypatch.setattr(replacement.cycle2, "solve_ap_node", forbidden)
    monkeypatch.setattr(replacement.cycle2, "run_external_records", forbidden)
    result = geometry_preflight()
    assert result == {
        "schema": "schwo.phase6.v3_1_u.geometry_preflight.v1",
        "route_map_sha256": (
            "5eee07ece78204265fe45069ef57a653a61a8ee9d09ff4b4d7e8928bb385c822"
        ),
        "key_count": 318,
        "node_count": 954,
        "node_inventory_sha256": result["node_inventory_sha256"],
        "ambient_precision_invariant": True,
        "science_solver_calls": 0,
        "original_failed_key_exponents": [2, 2, 2],
    }
    assert len(result["node_inventory_sha256"]) == 64
    assert calls == {"science": 0}


def test_route_map_exact_counts_boundary_and_mutation() -> None:
    small = build_route_map(_views(small=True))
    assert small["route_u_count"] == 496
    validate_route_map(small)
    large = build_route_map(_views(small=False))
    assert large["route_u_count"] == 0
    one = _views(small=False)
    one[0]["Gamma_flux_decimal"] = {"exponent10": -9, "mantissa": "9.9"}
    one[0]["log_Gamma_flux"] = mp.nstr(mp.log(mp.mpf("9.9e-9")), 50)
    assert build_route_map(one)["route_u_count"] == 1
    tampered = json.loads(json.dumps(small))
    tampered["entries"][0]["selector"]["use_route_u"] = False
    with pytest.raises(V31ContractError):
        validate_route_map(tampered)


def test_selector_rejects_extra_or_residual_control_fields() -> None:
    values = _views()
    values[0]["route_agreement_residual"] = 0.0
    with pytest.raises(V31ContractError, match="schema"):
        build_route_map(values)
    values = _views()
    values[1]["S"] = {"real": 1.0, "imag": 0.0}
    with pytest.raises(V31ContractError, match="schema"):
        build_route_map(values)


def test_oracle_ladder_admission_and_negative_surfaces() -> None:
    records = _ladder()
    result = validate_oracle_ladder(records)
    assert result["status"] == "PASS"
    with pytest.raises(HPUnitarityOracleError, match="three"):
        validate_oracle_ladder(records[:2])
    reordered = [records[1], records[0], records[2]]
    with pytest.raises(HPUnitarityOracleError, match="order"):
        validate_oracle_ladder(reordered)
    reused = json.loads(json.dumps(records))
    reused[0]["route_b_record_or_cache_reused"] = True
    with pytest.raises(HPUnitarityOracleError, match="provenance"):
        validate_oracle_ladder(reused)
    bad_gamma = json.loads(json.dumps(records))
    bad_gamma[-1]["Gamma_S_U"] = "-1e-14"
    with pytest.raises(HPUnitarityOracleError):
        validate_oracle_ladder(bad_gamma)


def test_oracle_source_isolation_and_no_float64_deficit_recovery() -> None:
    result = validate_import_isolation()
    assert result["forbidden"] == []
    source = Path(result["oracle_path"]).read_text()
    tree = ast.parse(source)
    imports = {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert not any(value.startswith("schwgw.numerics") for value in imports)
    assert "Gamma_S_U = -expm1" not in source  # evidence key is not a second formula
    assert "gamma_s = -mp.expm1(2 * log_abs_s)" in source
    assert "float64" not in source


def test_synthetic_exact_graphs_preserve_frozen_routes_and_certificates() -> None:
    for count in (0, 1, 496):
        payload = synthetic_payload(count)
        assert payload["counts"]["route_a_modes"] == 496
        assert payload["counts"]["route_a_nodes"] == 9920
        assert payload["counts"]["route_u_keys"] == count
        assert payload["counts"]["route_u_nodes"] == 3 * count
        assert payload["counts"]["route_b_keys"] == 102
        assert payload["counts"]["route_b_nodes"] == 458
        assert payload["counts"]["route_c_records"] == 23
        assert payload["counts"]["thresholds"] == 16
        assert payload["counts"]["certificates"] == 5


def test_start_gate_and_protected_identities_are_exact() -> None:
    from schwgw.validation.phase6_v3_mode_greybody_hp_replacement import (
        verify_start_gate,
    )

    gate = verify_start_gate()
    protected = gate["package"]["protected_radial_identities"]
    assert len(protected) == 7
    assert all(len(value) == 64 for value in protected.values())
    assert gate["geometry_preflight"]["node_count"] == 954


@pytest.mark.parametrize(
    ("path_name", "message"),
    [
        ("PACKAGE_PATH", "identity drift"),
        ("DESIGN_PATH", "identity drift"),
        ("T4_PROMPT_PATH", "identity drift"),
        ("T7_REVIEW_PROMPT_PATH", "identity drift"),
        ("T7_APPROVAL_PATH", "identity drift"),
        ("REPAIR_PACKAGE_PATH", "identity drift"),
        ("REPAIR_PACKAGE_REVIEW_PATH", "identity drift"),
        ("TERMINAL_REVIEW_PATH", "identity drift"),
        ("CLARIFICATION_PATH", "identity drift"),
    ],
)
def test_start_gate_rejects_changed_immutable_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    path_name: str,
    message: str,
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    changed = tmp_path / path_name
    changed.write_text("changed authority\n")
    monkeypatch.setattr(replacement, path_name, changed)
    with pytest.raises(V31ContractError, match=message):
        replacement.verify_start_gate()


def test_start_gate_rejects_terminal_failure_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    copied = tmp_path / "failed_root"
    copied.mkdir()
    for name in (*replacement.FAILED_IDENTITIES, "unitarity_route_map.json"):
        shutil.copyfile(replacement.FAILED_ROOT / name, copied / name)
    (copied / "failure.json").write_text("{}\n")
    monkeypatch.setattr(replacement, "FAILED_ROOT", copied)
    with pytest.raises(V31ContractError):
        replacement.verify_start_gate()


def test_start_gate_rejects_protected_identity_drift_in_reviewed_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    package = json.loads(replacement.REPAIR_PACKAGE_PATH.read_text())
    protected = next(iter(package["protected_radial_identities"]))
    package["protected_radial_identities"][protected] = "0" * 64
    changed = tmp_path / "package.json"
    from schwgw.validation.phase6_v3_mode_greybody import canonical_bytes

    changed.write_bytes(canonical_bytes(package))
    monkeypatch.setattr(replacement, "REPAIR_PACKAGE_PATH", changed)
    monkeypatch.setattr(
        replacement, "REPAIR_PACKAGE_SHA256", replacement.sha256(changed)
    )
    with pytest.raises(V31ContractError):
        replacement.verify_start_gate()


def _dispatch_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[object, Path, dict[str, object], dict[str, object]]:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    review = tmp_path / "implementation_review.md"
    current_hashes = {
        str(replacement.ROOT / path): replacement.sha256(
            (replacement.ROOT / path).resolve(strict=True)
        )
        for path in replacement.ALLOWED_IMPLEMENTATION_PATHS
    }
    review.write_text(
        "\n".join((*replacement.IMPLEMENTATION_REVIEW_TOKENS, *current_hashes.values()))
        + "\n"
    )
    dispatch = tmp_path / "dispatch.json"
    monkeypatch.setattr(replacement, "IMPLEMENTATION_REVIEW_PATH", review)
    monkeypatch.setattr(replacement, "DISPATCH_PATH", dispatch)
    package = json.loads(replacement.REPAIR2_PACKAGE_PATH.read_text())
    official_parent = tmp_path / "classic_scattering"
    official_parent.mkdir()
    monkeypatch.setattr(replacement, "OFFICIAL_ROOT_PARENT", official_parent)
    root = (
        official_parent / "v3_1_hp_unitarity_deficit_repair2_v1_20260813T060000Z_py314"
    )
    sentinel_root = (
        official_parent / "v3_1_u_route_c_sentinel_repair2_v1_20260813T050000Z_py314"
    )
    sentinel_root.mkdir()
    environment_authority = replacement._load_sentinel_environment_authority()
    runtime_boundary = replacement.validate_sentinel_runtime_boundary(
        launcher=Path(environment_authority["execution_boundary"]["launcher"]["path"]),
        executable=environment_authority["execution_boundary"]["executable"],
        argv=environment_authority["execution_boundary"]["argv"],
        cwd=Path(environment_authority["execution_boundary"]["cwd"]),
        requested_environment=environment_authority["requested_environment"][
            "exact_execve_map"
        ],
        observed_environment=environment_authority["observed_environment"][
            "exact_post_startup_map"
        ],
    )
    sentinel_bindings = {}
    for name, value in (
        (
            "dispatch_consumption.json",
            {
                "single_use": True,
                "environment_authority": runtime_boundary["environment_authority"],
                "requested_environment": runtime_boundary["requested_environment"],
                "observed_environment": runtime_boundary["observed_environment"],
                "runtime_boundary": runtime_boundary,
            },
        ),
        ("sentinel_result.json", {"status": "PASS", "record_count": 23}),
        (
            "manifest.json",
            {
                "overall_state": "PASS",
                "gate_id": replacement.GATE_ID,
                "terminal": True,
            },
        ),
    ):
        path = sentinel_root / name
        path.write_bytes(replacement.canonical_bytes(value))
        path.chmod(0o444)
        sentinel_bindings[name] = {
            "path": str(path),
            "identity": replacement._file_identity(path),
        }
    sentinel_root.chmod(0o555)
    sentinel_review = tmp_path / "sentinel_review.md"
    sentinel_review.write_text("\n".join(replacement.SENTINEL_REVIEW_TOKENS) + "\n")
    monkeypatch.setattr(replacement, "SENTINEL_REVIEW_PATH", sentinel_review)
    payload: dict[str, object] = {
        "schema": "schwo.phase6.v3_1_u.repair_cycle2_official_dispatch.v1",
        "gate_id": replacement.GATE_ID,
        "repair_id": package["repair_id"],
        "exact_root": str(root),
        "single_use": True,
        "created_at_utc": "2026-08-12T06:00:00Z",
        "repair_package": {
            "path": str(replacement.REPAIR2_PACKAGE_PATH),
            "sha256": replacement.REPAIR2_PACKAGE_SHA256,
        },
        "package_review": {
            "path": str(replacement.REPAIR2_PACKAGE_REVIEW_PATH),
            "sha256": replacement.REPAIR2_PACKAGE_REVIEW_SHA256,
        },
        "implementation_review": {
            "path": str(review),
            "sha256": replacement.sha256(review),
        },
        "implementation_hashes": current_hashes,
        "environment_authority": replacement._sentinel_environment_authority_binding(),
        "sentinel_review": {
            "path": str(sentinel_review),
            "sha256": replacement.sha256(sentinel_review),
        },
        "sentinel_terminal": {
            "root": str(sentinel_root),
            "dispatch_consumption": sentinel_bindings["dispatch_consumption.json"],
            "result": sentinel_bindings["sentinel_result.json"],
            "manifest": sentinel_bindings["manifest.json"],
        },
        "frozen_cli": {
            "path": str(replacement.ROOT / "scripts/phase6_v3_1_hp_unitarity.py"),
            "sha256": (
                "01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4"
            ),
        },
        "protected_radial_identities": package["protected_radial_identities"],
        "source_bindings": package["source_bindings"],
        "required_verdict_tokens": [
            *replacement.IMPLEMENTATION_REVIEW_TOKENS,
            *replacement.SENTINEL_REVIEW_TOKENS,
        ],
        "predecessor_science_reused": False,
        "sentinel_science_reused": False,
    }
    start_gate = {"repair2_package": package}
    return replacement, root, payload, start_gate


def _publish_dispatch(path: Path, payload: dict[str, object]) -> None:
    from schwgw.validation.phase6_v3_mode_greybody import canonical_bytes

    path.write_bytes(canonical_bytes(payload))
    path.chmod(0o444)


def test_fixed_dispatch_positive_and_fail_closed_surfaces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    replacement, root, payload, start_gate = _dispatch_fixture(tmp_path, monkeypatch)
    _publish_dispatch(replacement.DISPATCH_PATH, payload)
    result = replacement._validate_dispatch(root, start_gate)
    assert result["implementation_hashes"] == payload["implementation_hashes"]

    # A consumed exact-root dispatch cannot authorize another invocation.
    root.mkdir()
    with pytest.raises(V31ContractError, match="not fresh"):
        replacement._validate_dispatch(root, start_gate)


def test_future_implementation_review_has_one_fixed_archive_path() -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    expected = (
        replacement.ROOT / "docs/handoffs/archive/"
        "T7_2026-08-13_v3_1_u_repair_cycle2_implementation_delta_recheck_2.md"
    )
    assert replacement.IMPLEMENTATION_REVIEW_PATH == expected


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("extra", "schema"),
        ("wrong_root", "authority binding"),
        ("wrong_hash", "implementation hash"),
        ("wrong_review_digest", "implementation-review identity"),
        ("wrong_environment_authority", "authority binding"),
        ("wrong_protected", "frozen-source"),
        ("predecessor_yellow", "authority binding"),
        ("live_handoff", "authority binding"),
    ],
)
def test_fixed_dispatch_adversaries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
    message: str,
) -> None:
    replacement, root, payload, start_gate = _dispatch_fixture(tmp_path, monkeypatch)
    if mutation == "extra":
        payload["extra"] = True
    elif mutation == "wrong_root":
        payload["exact_root"] = str(tmp_path / "other")
    elif mutation == "wrong_hash":
        payload["implementation_hashes"] = {
            **payload["implementation_hashes"],
            str(replacement.ROOT / replacement.ALLOWED_IMPLEMENTATION_PATHS[0]): "0"
            * 64,
        }
    elif mutation == "wrong_review_digest":
        payload["implementation_review"] = {
            "path": str(replacement.IMPLEMENTATION_REVIEW_PATH),
            "sha256": "0" * 64,
        }
    elif mutation == "wrong_environment_authority":
        payload["environment_authority"] = {
            "path": str(replacement.SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
            "sha256": "0" * 64,
        }
    elif mutation == "wrong_protected":
        payload["protected_radial_identities"] = {}
    elif mutation == "predecessor_yellow":
        payload["implementation_review"] = {
            "path": str(
                replacement.ROOT / "docs/handoffs/archive/"
                "T7_2026-08-13_v3_1_u_repair_cycle2_package_review.md"
            ),
            "sha256": (
                "08e206d58b178bbed0ae96f7aa395db67f4c2bcb4620a5cd996f00afb028b23f"
            ),
        }
    else:
        payload["implementation_review"] = {
            "path": str(replacement.ROOT / "docs/handoffs/T7_current.md"),
            "sha256": "0" * 64,
        }
    _publish_dispatch(replacement.DISPATCH_PATH, payload)
    with pytest.raises(V31ContractError, match=message):
        replacement._validate_dispatch(root, start_gate)


@pytest.mark.parametrize("mutation", ["authority", "requested", "observed", "runtime"])
def test_sentinel_environment_consumption_is_exact(mutation: str) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    authority = replacement._load_sentinel_environment_authority()
    boundary = replacement.validate_sentinel_runtime_boundary(
        launcher=Path(authority["execution_boundary"]["launcher"]["path"]),
        executable=authority["execution_boundary"]["executable"],
        argv=authority["execution_boundary"]["argv"],
        cwd=Path(authority["execution_boundary"]["cwd"]),
        requested_environment=authority["requested_environment"]["exact_execve_map"],
        observed_environment=authority["observed_environment"][
            "exact_post_startup_map"
        ],
    )
    consumption = {
        "environment_authority": boundary["environment_authority"],
        "requested_environment": boundary["requested_environment"],
        "observed_environment": boundary["observed_environment"],
        "runtime_boundary": boundary,
    }
    assert replacement._validate_sentinel_environment_consumption(consumption)
    changed = json.loads(json.dumps(consumption))
    if mutation == "authority":
        changed["environment_authority"]["identity"]["sha256"] = "0" * 64
    elif mutation == "requested":
        changed["requested_environment"]["PYTHONPATH"] = "wrong"
    elif mutation == "observed":
        changed["observed_environment"]["LC_CTYPE"] = "wrong"
    else:
        changed["runtime_boundary"]["argv"].append("--extra")
    with pytest.raises(V31ContractError):
        replacement._validate_sentinel_environment_consumption(changed)


def test_fixed_dispatch_missing_and_wrong_review_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    replacement, root, payload, start_gate = _dispatch_fixture(tmp_path, monkeypatch)
    with pytest.raises(FileNotFoundError):
        replacement._validate_dispatch(root, start_gate)


def test_official_dispatch_requires_formal_sentinel_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    replacement, root, payload, start_gate = _dispatch_fixture(tmp_path, monkeypatch)
    replacement.SENTINEL_REVIEW_PATH.unlink()
    _publish_dispatch(replacement.DISPATCH_PATH, payload)
    with pytest.raises(FileNotFoundError):
        replacement._validate_dispatch(root, start_gate)


def test_fixed_dispatch_rejects_missing_future_review_and_extra_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    replacement, root, payload, start_gate = _dispatch_fixture(tmp_path, monkeypatch)
    replacement.IMPLEMENTATION_REVIEW_PATH.unlink()
    _publish_dispatch(replacement.DISPATCH_PATH, payload)
    with pytest.raises(FileNotFoundError):
        replacement._validate_dispatch(root, start_gate)

    replacement.IMPLEMENTATION_REVIEW_PATH.write_text(
        "\n".join(
            (
                *replacement.IMPLEMENTATION_REVIEW_TOKENS,
                *payload["implementation_hashes"].values(),
            )
        )
        + "\n"
    )
    payload["implementation_review"] = {
        "path": str(replacement.IMPLEMENTATION_REVIEW_PATH),
        "sha256": replacement.sha256(replacement.IMPLEMENTATION_REVIEW_PATH),
        "alternate_path": "forbidden",
    }
    replacement.DISPATCH_PATH.chmod(0o644)
    replacement.DISPATCH_PATH.write_bytes(b"")
    _publish_dispatch(replacement.DISPATCH_PATH, payload)
    with pytest.raises(V31ContractError, match="implementation-review schema"):
        replacement._validate_dispatch(root, start_gate)


def test_official_root_namespace_is_exact_and_alias_free(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    parent = tmp_path / "classic_scattering"
    parent.mkdir()
    monkeypatch.setattr(replacement, "OFFICIAL_ROOT_PARENT", parent)
    canonical = parent / "v3_1_hp_unitarity_deficit_repair2_v1_20260813T061122Z_py314"
    assert replacement._validate_official_root_path(canonical) == canonical

    wrong_parent = (
        tmp_path / "v3_1_hp_unitarity_deficit_repair2_v1_20260813T061122Z_py314"
    )
    with pytest.raises(V31ContractError, match="parent"):
        replacement._validate_official_root_path(wrong_parent)
    with pytest.raises(V31ContractError, match="namespace"):
        replacement._validate_official_root_path(parent / "not-an-official-root")
    malformed = parent / "v3_1_hp_unitarity_deficit_repair2_v1_20261340T256199Z_py314"
    with pytest.raises(V31ContractError, match="timestamp"):
        replacement._validate_official_root_path(malformed)

    alias = tmp_path / "classic_scattering_alias"
    alias.symlink_to(parent, target_is_directory=True)
    with pytest.raises(V31ContractError, match="alias"):
        replacement._validate_official_root_path(alias / canonical.name)


def test_source_end_rehashes_cached_authority_identities(
    tmp_path: Path,
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    authority = tmp_path / "authority.json"
    authority.write_text('{"state":"start"}\n')
    cached_start_gate = {
        "identities": {str(authority): replacement._file_identity(authority)}
    }
    source_start = replacement.build_source_ledger(cached_start_gate)
    assert source_start[str(authority)]["sha256"] == replacement.sha256(authority)

    authority.write_text('{"state":"drift"}\n')
    with pytest.raises(V31ContractError, match="source authority identity drift"):
        replacement.build_source_ledger(cached_start_gate)


def test_start_gate_has_no_mutable_live_handoff_equality_surface() -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    source = Path(replacement.__file__).read_text()
    for forbidden in (
        "T7_CURRENT_PATH",
        "T7_CURRENT_SHA256",
        "STATUS_START_SHA256",
        "T0_START_SHA256",
    ):
        assert forbidden not in source


def test_exact_sentinel_invocation_and_grammar_adversaries(
    tmp_path: Path,
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    exact = replacement.SENTINEL_INVOCATION
    replacement.validate_sentinel_invocation(
        executable=exact["executable"],
        argv=exact["argv"],
        cwd=Path(exact["cwd"]),
        environment=exact["environment_allowlist"],
    )
    mutations = [
        [exact["argv"][0], "-c", "import schwgw"],
        [exact["argv"][0], "-m", "other.module", "route-c-sentinel"],
        exact["argv"][:-1],
        [*exact["argv"], "--root", str(tmp_path)],
    ]
    for argv in mutations:
        with pytest.raises(V31ContractError, match="invocation"):
            replacement.validate_sentinel_invocation(
                executable=exact["executable"],
                argv=argv,
                cwd=Path(exact["cwd"]),
                environment=exact["environment_allowlist"],
            )
    with pytest.raises(V31ContractError, match="invocation"):
        replacement.validate_sentinel_invocation(
            executable=exact["executable"],
            argv=exact["argv"],
            cwd=tmp_path,
            environment=exact["environment_allowlist"],
        )
    with pytest.raises(V31ContractError, match="invocation"):
        replacement.validate_sentinel_invocation(
            executable=exact["executable"],
            argv=exact["argv"],
            cwd=Path(exact["cwd"]),
            environment={**exact["environment_allowlist"], "EXTRA": "1"},
        )


@pytest.mark.parametrize(
    "environment",
    [
        {
            "LC_CTYPE": "C.UTF-8",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": "runs/phase5/paper_figures/runtime_overlays/"
            "mpmath_1p4p1_py314:src",
        },
        {
            "LC_CTYPE": "C",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": "runs/phase5/paper_figures/runtime_overlays/"
            "mpmath_1p4p1_py314:src",
            "__CF_USER_TEXT_ENCODING": "0x1F5:0x19:0x34",
        },
        {
            "LC_CTYPE": "C.UTF-8",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": "runs/phase5/paper_figures/runtime_overlays/"
            "mpmath_1p4p1_py314:src",
            "__CF_USER_TEXT_ENCODING": "0x1F5:0x19:0x34",
            "EXTRA_UNREVIEWED_SENTINEL_AUTHORITY": "1",
        },
        {
            "LC_CTYPE": "C.UTF-8",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": "runs/phase5/paper_figures/runtime_overlays/"
            "mpmath_1p4p1_py314:src",
            "__CF_USER_TEXT_ENCODING": "0x1F5:0x19:0x34",
            "SCHWO_V31_AUTHORITY": "forbidden",
        },
    ],
)
def test_actual_sentinel_runtime_rejects_unprojected_environment(
    monkeypatch: pytest.MonkeyPatch, environment: dict[str, str]
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    exact = replacement.SENTINEL_INVOCATION
    monkeypatch.chdir(Path(exact["cwd"]))
    monkeypatch.setattr(replacement.os, "environ", environment)
    with pytest.raises(V31ContractError):
        replacement._validate_current_sentinel_runtime(exact["argv"])


def test_actual_sentinel_runtime_exact_environment_and_module_entry_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    exact = replacement.SENTINEL_INVOCATION
    authority = replacement._load_sentinel_environment_authority()
    monkeypatch.chdir(Path(exact["cwd"]))
    monkeypatch.setattr(
        replacement.os,
        "environ",
        dict(authority["observed_environment"]["exact_post_startup_map"]),
    )
    replacement._validate_current_sentinel_runtime(exact["argv"])
    monkeypatch.setattr(
        replacement,
        "verify_start_gate",
        lambda: (_ for _ in ()).throw(AssertionError("start gate reached")),
    )
    replacement.os.environ["EXTRA"] = "1"
    with pytest.raises(V31ContractError):
        replacement._sentinel_module_main(exact["argv"])


@pytest.mark.parametrize(
    "argv",
    [
        ["python3.14", "-m", "other.module", "route-c-sentinel"],
        [
            "python3.14",
            "-m",
            "schwgw.validation.phase6_v3_mode_greybody_hp_replacement",
            "route-c-sentinel",
            "--extra",
        ],
    ],
)
def test_actual_sentinel_runtime_rejects_alternate_argv(
    monkeypatch: pytest.MonkeyPatch, argv: list[str]
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    exact = replacement.SENTINEL_INVOCATION
    authority = replacement._load_sentinel_environment_authority()
    monkeypatch.chdir(Path(exact["cwd"]))
    monkeypatch.setattr(
        replacement.os,
        "environ",
        dict(authority["observed_environment"]["exact_post_startup_map"]),
    )
    with pytest.raises(V31ContractError, match="invocation"):
        replacement._validate_current_sentinel_runtime(argv)


def test_clean_env_i_and_direct_execve_observation_reach_only_validation() -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    authority = replacement._load_sentinel_environment_authority()
    requested = authority["requested_environment"]["exact_execve_map"]
    boundary = authority["execution_boundary"]
    probe = "import json,os;print(json.dumps(dict(os.environ),sort_keys=True))"
    env_i = subprocess.run(
        [
            "/usr/bin/env",
            "-i",
            *(f"{key}={value}" for key, value in requested.items()),
            boundary["executable"],
            "-c",
            probe,
        ],
        cwd=boundary["cwd"],
        check=True,
        capture_output=True,
        text=True,
    )
    direct = subprocess.run(
        [boundary["executable"], "-c", probe],
        cwd=boundary["cwd"],
        env=requested,
        check=True,
        capture_output=True,
        text=True,
    )
    for completed in (env_i, direct):
        observed = json.loads(completed.stdout)
        result = replacement.validate_sentinel_runtime_boundary(
            launcher=Path(boundary["launcher"]["path"]),
            executable=boundary["executable"],
            argv=boundary["argv"],
            cwd=Path(boundary["cwd"]),
            requested_environment=requested,
            observed_environment=observed,
        )
        assert result["observed_environment"] == observed
    assert not replacement.SENTINEL_DISPATCH_PATH.exists()
    assert not replacement.DISPATCH_PATH.exists()


@pytest.mark.parametrize(
    "mutation",
    [
        "requested_missing",
        "requested_changed",
        "requested_extra",
        "observed_missing",
        "observed_changed",
        "observed_extra",
        "argv",
        "module",
        "executable",
        "cwd",
        "launcher",
    ],
)
def test_sentinel_runtime_boundary_adversaries_fail_closed(mutation: str) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    authority = replacement._load_sentinel_environment_authority()
    boundary = authority["execution_boundary"]
    values = {
        "launcher": Path(boundary["launcher"]["path"]),
        "executable": boundary["executable"],
        "argv": list(boundary["argv"]),
        "cwd": Path(boundary["cwd"]),
        "requested_environment": dict(
            authority["requested_environment"]["exact_execve_map"]
        ),
        "observed_environment": dict(
            authority["observed_environment"]["exact_post_startup_map"]
        ),
    }
    if mutation == "requested_missing":
        values["requested_environment"].pop("PYTHONDONTWRITEBYTECODE")
    elif mutation == "requested_changed":
        values["requested_environment"]["PYTHONPATH"] = "wrong"
    elif mutation == "requested_extra":
        values["requested_environment"]["SCHWO_AUTHORITY"] = "forbidden"
    elif mutation == "observed_missing":
        values["observed_environment"].pop("LC_CTYPE")
    elif mutation == "observed_changed":
        values["observed_environment"]["__CF_USER_TEXT_ENCODING"] = "wrong"
    elif mutation == "observed_extra":
        values["observed_environment"]["EXTRA"] = "forbidden"
    elif mutation == "argv":
        values["argv"].append("--extra")
    elif mutation == "module":
        values["argv"][2] = "other.module"
    elif mutation == "executable":
        values["executable"] = "/usr/bin/false"
    elif mutation == "cwd":
        values["cwd"] = Path("/tmp")
    else:
        values["launcher"] = Path("/usr/bin/true")
    with pytest.raises(V31ContractError):
        replacement.validate_sentinel_runtime_boundary(**values)


def test_sentinel_namespace_and_official_namespace_are_disjoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    parent = tmp_path / "classic_scattering"
    parent.mkdir()
    monkeypatch.setattr(replacement, "OFFICIAL_ROOT_PARENT", parent)
    sentinel = parent / "v3_1_u_route_c_sentinel_repair2_v1_20260813T070000Z_py314"
    official = parent / "v3_1_hp_unitarity_deficit_repair2_v1_20260813T080000Z_py314"
    assert replacement._validate_sentinel_root_path(sentinel) == sentinel
    assert replacement._validate_official_root_path(official) == official
    with pytest.raises(V31ContractError):
        replacement._validate_sentinel_root_path(official)
    with pytest.raises(V31ContractError):
        replacement._validate_official_root_path(sentinel)


def test_direct_import_sentinel_execution_is_forbidden(tmp_path: Path) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    with pytest.raises(V31ContractError, match="direct-import"):
        replacement.run_route_c_sentinel(tmp_path / "forbidden")
    assert not (tmp_path / "forbidden").exists()
