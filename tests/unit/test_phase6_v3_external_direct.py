from __future__ import annotations

import ast
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import stat

import mpmath as mp
import pytest

import schwgw.validation.phase6_v3_external_direct as direct
import schwgw.validation.phase6_v3_mode_greybody_external_direct_replacement as replacement
from schwgw.validation.phase6_v3_external_direct import ExternalDirectContractError


FROZEN_WLS_ARGV = [
    "/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel",
    "-script",
    "/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/scripts/"
    "phase6_v3_1_x_bhpt_direct.wls",
    "REQUEST",
    "OUTPUT",
]


def _scalar(value: mp.mpf, node: dict[str, object]) -> dict[str, object]:
    if value == 0:
        return {
            "decimal": "0",
            "exact_zero": True,
            "source_precision_digits": None,
            "source_accuracy_digits": None,
            "serialized_significant_digits": 0,
        }
    digits = int(node["precision_goal"])
    text = mp.nstr(value, max(int(node["working_precision"]), digits + 12))
    significant = direct._decimal_significant_digits(text, "fake")
    assert significant >= digits
    return {
        "decimal": text,
        "exact_zero": False,
        "source_precision_digits": int(node["working_precision"]),
        "source_accuracy_digits": int(node["accuracy_goal"]),
        "serialized_significant_digits": significant,
    }


def _complex(value: mp.mpc, node: dict[str, object]) -> dict[str, object]:
    return {"real": _scalar(value.real, node), "imag": _scalar(value.imag, node)}


def fake_raw(
    expected: dict[str, object],
    *,
    reflection_abs: str = "1.7320508075688772935274463415058723669428",
) -> dict[str, object]:
    mp.mp.dps = max(mp.mp.dps, 160)
    key = expected["key"]
    node = expected["node"]
    assert isinstance(key, dict) and isinstance(node, dict)
    k = mp.mpf(str(key["kM"]))
    perturbation = mp.power(10, -(int(node["working_precision"]) - 9))
    a_in = mp.mpf(2) + perturbation
    a_out = mp.mpf(reflection_abs)
    h = a_in + a_out
    hdot = 1j * k * (a_out - a_in)
    overlaps = [
        {
            "fraction": label,
            "radius_M": _scalar(radius * (1 + perturbation), node),
            "H": _complex(mp.mpc(h), node),
            "Hdot": _complex(mp.mpc(hdot), node),
            "U": _complex(mp.mpc(1 + perturbation), node),
            "Udot": _complex(mp.mpc(0, k + perturbation), node),
        }
        for label, radius in zip(
            direct.OVERLAP_LABELS,
            direct.overlap_radii(key, node),
            strict=True,
        )
    ]
    variant = direct.OVERLAY_VARIANTS[node["overlay_variant"]]
    loaded = [
        {
            "context": context,
            "path": path,
            "sha256": "a" * 64,
            "size": 1,
            "mode": 0o444,
            "nlink": 1,
        }
        for context, path in zip(
            direct.LOADED_SOURCE_CONTEXTS, direct.LOADED_SOURCE_PATHS, strict=True
        )
    ]
    numerator, denominator = direct.exact_frequency_fraction(str(key["kM"]))
    return {
        "schema": "schwo.phase6.v3_1_x.external_direct_raw_node.v1",
        "call_ordinal": expected["call_ordinal"],
        "key_ordinal": expected["key_ordinal"],
        "key": key,
        "node_ordinal": expected["node_ordinal"],
        "node": node,
        "method": "NumericalIntegration",
        "potential": "ReggeWheeler",
        "boundary_conditions": ["In", "Up"],
        "frequency": {
            "label": key["kM"],
            "exact_numerator": numerator,
            "exact_denominator": denominator,
            "input_precision_digits": node["working_precision"] + 20,
        },
        "external_api_call_count": 1,
        "external_boundary_solution_count": 2,
        "mst_call_count": 0,
        "internal_solver_call_count": 0,
        "overlay": {
            "variant": variant.name,
            "numerical_source_sha256": variant.sha256,
        },
        "overlaps": overlaps,
        "loaded_contexts_start": list(direct.LOADED_SOURCE_CONTEXTS),
        "loaded_contexts_end": list(direct.LOADED_SOURCE_CONTEXTS),
        "loaded_source_start": loaded,
        "loaded_source_end": loaded,
        "runtime": {"elapsed_seconds": "1.0"},
    }


def _valid_loaded_source_ledger() -> list[dict[str, object]]:
    return [
        {
            "context": context,
            "path": path,
            "sha256": f"{ordinal + 1:064x}",
            "size": ordinal + 1,
            "mode": 0o444,
            "nlink": 1,
        }
        for ordinal, (context, path) in enumerate(
            zip(
                direct.LOADED_SOURCE_CONTEXTS,
                direct.LOADED_SOURCE_PATHS,
                strict=True,
            )
        )
    ]


def derived_record(expected: dict[str, object], **kwargs: str) -> dict[str, object]:
    return direct.derive_node_record(fake_raw(expected, **kwargs), expected)


def test_exact_domain_graphs_and_static_contract() -> None:
    inventory = direct.route_c_inventory()
    assert len(inventory) == 23
    assert inventory[0] == {
        "anchor_id": "V3A-MODE-BHPT-RW-001",
        "ell": 2,
        "kM": "0.1",
        "parity": "odd",
    }
    assert inventory[-1] == {
        "anchor_id": "V3A-MODE-BHPT-RW-001",
        "ell": 28,
        "kM": "4",
        "parity": "odd",
    }
    assert (
        hashlib.sha256(direct.compact_bytes(inventory)).hexdigest()
        == direct.CANONICAL_KEY_SHA256
    )
    official = direct.official_plan()
    sentinel = direct.sentinel_plan()
    assert (len(official), 2 * len(official), 3 * len(official)) == (161, 322, 483)
    assert (len(sentinel), 2 * len(sentinel), 3 * len(sentinel)) == (35, 70, 105)
    assert [item["node"]["node_id"] for item in official[:7]] == list(direct.NODE_ORDER)
    assert [item["key_ordinal"] for item in sentinel[:23]] == list(range(23))
    assert {item["key_ordinal"] for item in sentinel[23:]} == {3, 22}
    contract = direct.static_contract()
    assert contract["science_solver_calls"] == contract["wolfram_launches"] == 0
    assert contract["mst_call_count"] == contract["internal_solver_call_count"] == 0


@pytest.mark.parametrize(
    "label, fraction",
    [("0.1", (1, 10)), ("0.5", (1, 2)), ("1", (1, 1)), ("2", (2, 1)), ("4", (4, 1))],
)
def test_exact_frequency_map(label: str, fraction: tuple[int, int]) -> None:
    assert direct.exact_frequency_fraction(label) == fraction
    with pytest.raises(ExternalDirectContractError):
        direct.exact_frequency_fraction(label + "0")


def test_all_six_first_occurrence_overlays_and_inventory(tmp_path: Path) -> None:
    base = direct.NUMERICAL_SOURCE.read_bytes()
    assert base.count(direct.OLD_RIN) == base.count(direct.OLD_ROUT) == 2
    for name, variant in direct.OVERLAY_VARIANTS.items():
        transformed = direct.transformed_numerical_source(base, name)
        assert hashlib.sha256(transformed).hexdigest() == variant.sha256
        assert transformed.count(direct.OLD_RIN) == 1
        assert transformed.count(direct.OLD_ROUT) == 1
        root = tmp_path / name
        identity = direct.materialize_overlay(direct.BHPT_SNAPSHOT_ROOT, root, name)
        assert identity["file_count"] == 25
        assert identity["source_bytes_modified"] == 1
        assert stat.S_IMODE(root.stat().st_mode) == 0o555
        assert all(
            stat.S_IMODE(path.stat().st_mode) == 0o444
            for path in root.rglob("*")
            if path.is_file()
        )


def test_base_snapshot_rebuilds_content_and_five_field_identity_indices(
    tmp_path: Path,
) -> None:
    identity = direct.base_snapshot_identity()
    assert identity["content_inventory_sha256"] == direct.BHPT_CONTENT_SHA256
    assert identity["identity_inventory_sha256"] == direct.BHPT_IDENTITY_SHA256
    assert identity["directory_paths"] == list(direct.SNAPSHOT_DIRECTORIES)
    copied = tmp_path / "snapshot"
    shutil.copytree(direct.BHPT_SNAPSHOT_ROOT, copied, copy_function=shutil.copy2)
    for path in [copied, *[item for item in copied.rglob("*") if item.is_dir()]]:
        os.chmod(path, 0o555)
    assert (
        direct.base_snapshot_identity(copied)["identity_inventory_sha256"]
        == direct.BHPT_IDENTITY_SHA256
    )
    changed = copied / "Kernel/ReggeWheeler.m"
    os.chmod(changed, 0o644)
    with pytest.raises(ExternalDirectContractError):
        direct.base_snapshot_identity(copied)


@pytest.mark.parametrize("mutation", ["old_extra", "old_missing", "unknown"])
def test_overlay_occurrence_and_variant_fail_closed(mutation: str) -> None:
    base = direct.NUMERICAL_SOURCE.read_bytes()
    if mutation == "old_extra":
        base += direct.OLD_RIN
    elif mutation == "old_missing":
        base = base.replace(direct.OLD_ROUT, b"other", 1)
    with pytest.raises(ExternalDirectContractError):
        direct.transformed_numerical_source(
            base, "missing" if mutation == "unknown" else "rin10_m1"
        )


def test_overlay_rejects_wrong_byte_mode_link_and_extra(tmp_path: Path) -> None:
    root = tmp_path / "overlay"
    direct.materialize_overlay(direct.BHPT_SNAPSHOT_ROOT, root, "rin10_m1")
    os.chmod(root, 0o755)
    numerical = root / "Kernel/NumericalIntegration.m"
    os.chmod(numerical, 0o644)
    numerical.write_bytes(numerical.read_bytes() + b"x")
    with pytest.raises(ExternalDirectContractError):
        direct.validate_overlay(root, "rin10_m1")
    linked = tmp_path / "overlay_linked"
    direct.materialize_overlay(direct.BHPT_SNAPSHOT_ROOT, linked, "rin10_m1")
    os.chmod(linked, 0o755)
    os.chmod(linked / "Kernel", 0o755)
    os.link(
        linked / "Kernel/ReggeWheeler.m",
        linked / "Kernel/ReggeWheeler.alias.m",
    )
    os.chmod(linked / "Kernel/ReggeWheeler.alias.m", 0o444)
    os.chmod(linked / "Kernel", 0o555)
    os.chmod(linked, 0o555)
    with pytest.raises(ExternalDirectContractError):
        direct.validate_overlay(linked, "rin10_m1")


def test_wronskian_sign_amplitudes_and_direct_flux_are_derived_in_python() -> None:
    expected = direct.official_plan()[0]
    result = derived_record(expected)
    selected = result["overlaps"][1]
    a_in = direct._mp_complex(selected["A_in_horizon_normalized"], "Ain")
    a_out = direct._mp_complex(selected["A_out_horizon_normalized"], "Aout")
    s_value = direct._mp_complex(selected["S"], "S")
    assert abs(a_in - 2) < mp.mpf("1e-80")
    assert abs(a_out - mp.sqrt(3)) < mp.mpf("1e-15")
    assert abs(s_value + mp.sqrt(3) / 2) < mp.mpf("1e-15")
    assert abs(direct._mp_real(selected["Gamma_flux"], "gf") - mp.mpf("0.25")) < mp.mpf(
        "1e-40"
    )
    assert abs(direct._mp_real(selected["Gamma_S"], "gs") - mp.mpf("0.25")) < mp.mpf(
        "1e-15"
    )
    assert abs(direct._mp_real(selected["signed_current_balance"], "balance")) < mp.mpf(
        "1e-15"
    )


def test_direct_flux_is_not_inferred_from_s() -> None:
    expected = direct.official_plan()[0]
    result = derived_record(expected, reflection_abs="1")
    selected = result["overlaps"][1]
    assert abs(direct._mp_real(selected["Gamma_flux"], "gf") - mp.mpf("0.25")) < mp.mpf(
        "1e-75"
    )
    assert abs(direct._mp_real(selected["Gamma_S"], "gs") - mp.mpf("0.75")) < mp.mpf(
        "1e-75"
    )
    assert direct._mp_real(selected["signed_current_balance"], "balance") != 0


@pytest.mark.parametrize(
    "mutation",
    [
        "frequency",
        "method",
        "mst",
        "internal",
        "source",
        "key",
        "overlap",
        "zero_determinant",
        "nonfinite",
    ],
)
def test_raw_node_adversaries_fail_closed(mutation: str) -> None:
    expected = direct.official_plan()[0]
    raw = fake_raw(expected)
    if mutation == "frequency":
        raw["frequency"]["input_precision_digits"] = 53
    elif mutation == "method":
        raw["method"] = "MST"
    elif mutation == "mst":
        raw["mst_call_count"] = 1
    elif mutation == "internal":
        raw["internal_solver_call_count"] = 1
    elif mutation == "source":
        raw["loaded_source_end"] = []
    elif mutation == "key":
        raw["key"] = {
            "anchor_id": "V3A-MODE-BHPT-RW-001",
            "ell": 3,
            "kM": "0.1",
            "parity": "odd",
        }
    elif mutation == "overlap":
        raw["overlaps"].reverse()
    elif mutation == "zero_determinant":
        raw["overlaps"][0]["Udot"] = raw["overlaps"][0]["U"]
    else:
        raw["overlaps"][0]["H"]["real"] = "nan"
    with pytest.raises(ExternalDirectContractError):
        direct.derive_node_record(raw, expected)


def test_official_record_totality_duplicate_gap_reorder_and_cross_key() -> None:
    plan = direct.official_plan()
    records = [derived_record(item) for item in plan]
    direct.validate_node_records(records, "official")
    for mutant in (
        records[:-1],
        [records[0], *records],
        [records[1], records[0], *records[2:]],
    ):
        with pytest.raises(ExternalDirectContractError):
            direct.validate_node_records(mutant, "official")
    wrong = copy.deepcopy(records)
    wrong[7]["key"] = wrong[0]["key"]
    with pytest.raises(ExternalDirectContractError):
        direct.validate_node_records(wrong, "official")


def test_ladder_budget_separation_and_threshold_drift() -> None:
    records = [derived_record(item) for item in direct.official_plan()[:7]]
    budget = direct.aggregate_key_records(records)
    assert budget["numerical_budget"]["status"] == "PASS"
    assert budget["numerical_budget"] != budget["convention_budget"]
    broken = copy.deepcopy(records)
    broken[-1]["overlaps"][1]["S"] = {"real": "0.5", "imag": "0"}
    assert direct.aggregate_key_records(broken)["numerical_budget"]["status"] == "FAIL"


def test_json_and_jsonl_canonical_torn_rejection(tmp_path: Path) -> None:
    path = tmp_path / "x.jsonl"
    path.write_bytes(direct.compact_jsonl_record({"b": 2, "a": 1}))
    assert direct.load_jsonl(path) == [{"a": 1, "b": 2}]
    path.write_bytes(b'{"a":1}')
    with pytest.raises(ExternalDirectContractError, match="torn"):
        direct.load_jsonl(path)
    path.write_bytes(b'{"a": 1}\n')
    with pytest.raises(ExternalDirectContractError, match="noncanonical"):
        direct.load_jsonl(path)


def test_resource_projection_exact_graph_and_stop_gates() -> None:
    records = [derived_record(item) for item in direct.sentinel_plan()]
    projection = direct.resource_projection(records, free_bytes=1_000_000_000)
    assert projection["sentinel_call_count"] == 35
    assert projection["official_call_count"] == 161
    assert projection["runtime_gate_passed"] is True
    assert projection["disk_gate_passed"] is True
    stopped = direct.resource_projection(records, free_bytes=1)
    assert stopped["disk_gate_passed"] is False


def test_sentinel_budget_rejects_any_admission_metric_and_missing_ladder() -> None:
    records = [derived_record(item) for item in direct.sentinel_plan()]
    payload = direct.build_sentinel_budgets(records)
    assert payload["status"] == "PASS"
    direct.validate_sentinel_budgets(payload, records)
    broken = copy.deepcopy(records)
    broken[7]["overlaps"][1]["signed_current_balance"] = "8.0"
    assert direct.build_sentinel_budgets(broken)["status"] == "FAIL"
    with pytest.raises(ExternalDirectContractError):
        direct.validate_sentinel_budgets(payload, broken)
    with pytest.raises(ExternalDirectContractError):
        direct.build_sentinel_budgets(records[:-1])


@pytest.mark.parametrize(
    "mutation", ["missing", "extra", "reorder", "alias", "mode", "link"]
)
def test_loaded_source_and_precision_witness_adversaries_fail_closed(
    mutation: str,
) -> None:
    expected = direct.official_plan()[0]
    raw = fake_raw(expected)
    expected_sources = copy.deepcopy(raw["loaded_source_start"])
    if mutation == "missing":
        raw["loaded_source_end"] = raw["loaded_source_end"][:-1]
    elif mutation == "extra":
        raw["loaded_source_end"].append(copy.deepcopy(raw["loaded_source_end"][-1]))
    elif mutation == "reorder":
        raw["loaded_source_end"][0], raw["loaded_source_end"][1] = (
            raw["loaded_source_end"][1],
            raw["loaded_source_end"][0],
        )
    elif mutation == "alias":
        raw["loaded_source_end"][0]["path"] = "Kernel/alias.m"
    elif mutation == "mode":
        raw["loaded_source_end"][0]["mode"] = 0o644
    else:
        raw["loaded_source_end"][0]["nlink"] = 2
    with pytest.raises(ExternalDirectContractError):
        direct.derive_node_record(
            raw, expected, expected_loaded_sources=expected_sources
        )


def test_repair2_loaded_source_projection_is_exact_ordered_eight() -> None:
    records = _valid_loaded_source_ledger()
    expected = [
        [record[field] for field in replacement.SOURCE_FIELD_ORDER]
        for record in records
    ]
    projection = replacement.normalize_loaded_source_ledger(records)
    assert projection == expected
    assert len(projection) == 8
    assert [item[0] for item in projection] == list(direct.LOADED_SOURCE_CONTEXTS)
    assert [item[1] for item in projection] == list(direct.LOADED_SOURCE_PATHS)


def test_repair2_projection_accepts_every_object_member_order() -> None:
    records = _valid_loaded_source_ledger()
    expected = replacement.normalize_loaded_source_ledger(records)
    for field_order in itertools.permutations(replacement.SOURCE_FIELD_ORDER):
        permuted = [
            {field: record[field] for field in field_order} for record in records
        ]
        assert replacement.normalize_loaded_source_ledger(permuted) == expected


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_field",
        "extra_field",
        "wrong_context_type",
        "wrong_path_type",
        "wrong_sha_type",
        "bool_size",
        "wrong_mode_type",
        "wrong_nlink_type",
        "wrong_context",
        "wrong_sha",
        "negative_size",
        "wrong_mode",
        "wrong_nlink",
        "missing_record",
        "extra_record",
        "duplicate_record",
        "reorder",
        "duplicate_context",
        "duplicate_path",
        "traversal",
        "dot_component",
        "absolute_path",
        "case_variant",
        "unicode_variant",
    ],
)
def test_repair2_loaded_source_projection_adversaries_fail_closed(
    mutation: str,
) -> None:
    records = _valid_loaded_source_ledger()
    if mutation == "missing_field":
        records[0].pop("sha256")
    elif mutation == "extra_field":
        records[0]["extra"] = "forbidden"
    elif mutation == "wrong_context_type":
        records[0]["context"] = 1
    elif mutation == "wrong_path_type":
        records[0]["path"] = [direct.LOADED_SOURCE_PATHS[0]]
    elif mutation == "wrong_sha_type":
        records[0]["sha256"] = b"a" * 64
    elif mutation == "bool_size":
        records[0]["size"] = True
    elif mutation == "wrong_mode_type":
        records[0]["mode"] = "0444"
    elif mutation == "wrong_nlink_type":
        records[0]["nlink"] = 1.0
    elif mutation == "wrong_context":
        records[0]["context"] = "ReggeWheeler`Wrong`"
    elif mutation == "wrong_sha":
        records[0]["sha256"] = "A" * 64
    elif mutation == "negative_size":
        records[0]["size"] = -1
    elif mutation == "wrong_mode":
        records[0]["mode"] = 0o644
    elif mutation == "wrong_nlink":
        records[0]["nlink"] = 2
    elif mutation == "missing_record":
        records.pop()
    elif mutation == "extra_record":
        records.append(copy.deepcopy(records[-1]))
    elif mutation == "duplicate_record":
        records[1] = copy.deepcopy(records[0])
    elif mutation == "reorder":
        records[0], records[1] = records[1], records[0]
    elif mutation == "duplicate_context":
        records[1]["context"] = records[0]["context"]
    elif mutation == "duplicate_path":
        records[1]["path"] = records[0]["path"]
    elif mutation == "traversal":
        records[0]["path"] = "Kernel/../Kernel/ReggeWheeler.m"
    elif mutation == "dot_component":
        records[0]["path"] = "Kernel/./ReggeWheeler.m"
    elif mutation == "absolute_path":
        records[0]["path"] = "/Kernel/ReggeWheeler.m"
    elif mutation == "case_variant":
        records[0]["path"] = "kernel/ReggeWheeler.m"
    else:
        records[0]["path"] = "Kernel/Re\N{COMBINING ACUTE ACCENT}ggeWheeler.m"
    with pytest.raises(ExternalDirectContractError, match="loaded-source"):
        replacement.normalize_loaded_source_ledger(records)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"path":"a","path":"a"}',
        b'{"path":"a","path":"b"}',
        b'{"outer":{"sha256":"a","sha256":"a"}}',
        b'{"outer":{"sha256":"a","sha256":"b"}}',
    ],
)
def test_repair2_duplicate_json_members_reject_before_semantic_loading(
    raw: bytes, tmp_path: Path
) -> None:
    with pytest.raises(ExternalDirectContractError, match="duplicate JSON member"):
        replacement._loads_unique_json(raw, label="unit duplicate")
    path = tmp_path / "duplicate.json"
    path.write_bytes(raw + b"\n")
    with pytest.raises(ExternalDirectContractError, match="duplicate JSON member"):
        replacement.load_canonical(path)


def test_repair2_canonical_loader_accepts_duplicate_free_bytes(tmp_path: Path) -> None:
    path = tmp_path / "canonical.json"
    payload = {"outer": {"path": "Kernel/ReggeWheeler.m"}, "value": 1}
    path.write_bytes(direct.canonical_bytes(payload))
    assert replacement.load_canonical(path) == payload
    assert (
        replacement._loads_unique_json(
            json.dumps(payload).encode(), label="unit unique"
        )
        == payload
    )


def test_repair2_overlay_inode_inventory_detects_same_byte_replacement(
    tmp_path: Path,
) -> None:
    root = tmp_path / "overlay"
    direct.materialize_overlay(direct.BHPT_SNAPSHOT_ROOT, root, "rin10_m1")
    start = replacement._overlay_inode_inventory(root.absolute())
    target = root / "Kernel/ReggeWheeler.m"
    original = target.read_bytes()
    parent = target.parent
    os.chmod(parent, 0o755)
    substitute = parent / "ReggeWheeler.same-bytes.tmp"
    substitute.write_bytes(original)
    os.chmod(substitute, 0o444)
    os.replace(substitute, target)
    os.chmod(parent, 0o555)
    end = replacement._overlay_inode_inventory(root.absolute())
    start_record = next(
        item for item in start["files"] if item["path"] == "Kernel/ReggeWheeler.m"
    )
    end_record = next(
        item for item in end["files"] if item["path"] == "Kernel/ReggeWheeler.m"
    )
    assert start_record["sha256"] == end_record["sha256"]
    assert start_record["size"] == end_record["size"]
    assert start_record["ino"] != end_record["ino"]
    assert start != end


@pytest.mark.parametrize("mutation", ["short", "padded", "forged", "cross_node"])
def test_precision_witness_adversaries_fail_closed(mutation: str) -> None:
    expected = direct.official_plan()[1]
    raw = fake_raw(expected)
    witness = raw["overlaps"][0]["H"]["real"]
    if mutation == "short":
        witness["decimal"] = "1.2345"
        witness["serialized_significant_digits"] = 5
    elif mutation == "padded":
        witness["decimal"] = witness["decimal"] + "0"
    elif mutation == "forged":
        witness["source_accuracy_digits"] = 1
    else:
        witness["source_precision_digits"] = 90
    with pytest.raises(ExternalDirectContractError):
        direct.derive_node_record(raw, expected)


@pytest.mark.parametrize(
    "text, digits",
    [
        ("1.2034", 5),
        ("1.2034e-300", 5),
        ("-0.0012034e+12", 5),
    ],
)
def test_canonical_precision_digits_preserve_interior_zero_and_exponent(
    text: str, digits: int
) -> None:
    assert direct._decimal_significant_digits(text, "test") == digits
    mantissa, *exponent = text.split("e", maxsplit=1)
    padded = mantissa + "0" + ("e" + exponent[0] if exponent else "")
    with pytest.raises(ExternalDirectContractError, match="padded"):
        direct._decimal_significant_digits(padded, "test")


def test_precision_witness_rejects_forged_exact_nonzero_and_wls_parity() -> None:
    expected = direct.official_plan()[0]
    raw = fake_raw(expected)
    witness = raw["overlaps"][0]["H"]["real"]
    assert isinstance(witness, dict)
    witness["exact_zero"] = True
    witness["decimal"] = "1.2034"
    witness["source_precision_digits"] = None
    witness["source_accuracy_digits"] = None
    witness["serialized_significant_digits"] = 0
    with pytest.raises(ExternalDirectContractError, match="exact-zero"):
        direct.derive_node_record(raw, expected)
    source = replacement.WLS_PATH.read_text()
    assert 'StringReplace[digits, RegularExpression["^0+"] -> ""]' in source
    assert '"exact_value"' not in source


def test_source_ast_has_no_solver_or_mst_import_and_wls_exact_call() -> None:
    tree = ast.parse(
        direct.CORE_PATH.read_text()
        if hasattr(direct, "CORE_PATH")
        else Path(direct.__file__).read_text()
    )
    imports = [
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    ]
    assert not any(name.startswith("schwgw.numerics") for name in imports)
    source = replacement.WLS_PATH.read_text()
    assert source.count("ReggeWheelerRadial[") == 1
    assert '"BoundaryConditions" -> {"In", "Up"}' in source
    assert 'Method -> {"NumericalIntegration", "Domain" -> domainRules}' in source
    assert 'Method -> "MST"' not in source
    assert "solve_radial" not in source


def _frozen_wls_argv_accepted(argv: list[str], script_argv: list[str]) -> bool:
    return argv == FROZEN_WLS_ARGV and script_argv == []


@pytest.mark.parametrize(
    "argv,script_argv",
    [
        ([], []),
        (FROZEN_WLS_ARGV[:-1], []),
        ([*FROZEN_WLS_ARGV, "EXTRA"], []),
        ([*FROZEN_WLS_ARGV[:3], "OUTPUT", "REQUEST"], []),
        (["/alternate/WolframKernel", *FROZEN_WLS_ARGV[1:]], []),
        ([FROZEN_WLS_ARGV[0], "-file", *FROZEN_WLS_ARGV[2:]], []),
        ([*FROZEN_WLS_ARGV[:2], "/alternate/WLS", *FROZEN_WLS_ARGV[3:]], []),
        (FROZEN_WLS_ARGV, [FROZEN_WLS_ARGV[2], "REQUEST", "OUTPUT"]),
    ],
)
def test_frozen_wls_commandline_model_rejects_every_alternate_shape(
    argv: list[str], script_argv: list[str]
) -> None:
    assert not _frozen_wls_argv_accepted(argv, script_argv)


def test_wls_uses_only_exact_five_commandline_before_request_import() -> None:
    argv = list(FROZEN_WLS_ARGV)
    assert argv[:3] == [
        str(replacement.WOLFRAM_KERNEL),
        "-script",
        str(replacement.WLS_PATH),
    ]
    assert _frozen_wls_argv_accepted(argv, [])
    source = replacement.WLS_PATH.read_text()
    assert (
        'expectedKernel = "/Volumes/JohnnyTforGR/Applications/Wolfram.app/'
        'Contents/MacOS/WolframKernel";' in source
    )
    assert (
        'expectedScript = "/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/'
        'SchWO/scripts/phase6_v3_1_x_bhpt_direct.wls";' in source
    )
    required = (
        "Length[$CommandLine] =!= 5",
        "$CommandLine[[1]] =!= expectedKernel",
        '$CommandLine[[2]] =!= "-script"',
        "$CommandLine[[3]] =!= expectedScript",
        "$ScriptCommandLine =!= {}",
        "requestPath = ExpandFileName[$CommandLine[[4]]]",
        "outputPath = ExpandFileName[$CommandLine[[5]]]",
    )
    assert all(token in source for token in required)
    assert "$ScriptCommandLine[[" not in source
    assert source.count("$ScriptCommandLine") == 1
    assert "Take[$CommandLine" not in source
    assert "Drop[$CommandLine" not in source
    assert "Environment[" not in source[: source.index("request = Quiet[Check[Import[")]
    guard = source.index("Length[$CommandLine] =!= 5")
    absent_request = source.index("request must exist and output must be absent")
    request_import = source.index("request = Quiet[Check[Import[")
    source_load = source.index('Needs["PacletManager`"]')
    solver = source.index("ReggeWheelerRadial[")
    assert guard < absent_request < request_import < source_load < solver


def test_wls_has_one_ordered_projection_and_micro_exits_before_sole_solver() -> None:
    source = replacement.WLS_PATH.read_text()
    assert source.count("sourceFieldOrder = {") == 1
    assert (
        'sourceFieldOrder = {"context", "path", "sha256", "size", "mode", '
        '"nlink"};' in source
    )
    assert source.count("normalizeSourceRecord[record_") == 1
    assert source.count("normalizeLedger[records_]") == 1
    assert "Sort[records]" not in source
    assert "DeleteDuplicates[records]" not in source
    assert "Union[records]" not in source
    assert (
        'expectedProjection = normalizeLedger[request["loaded_source_records"]]'
        in source
    )
    assert "actualStartProjection = normalizeLedger[loadedStart]" in source
    assert "actualEndProjection = normalizeLedger[loadedEnd]" in source


def test_wls_distinguishes_installed_paclet_candidates_from_loaded_context() -> None:
    source = replacement.WLS_PATH.read_text()
    assert "If[preLoadReggeWheelerPackages =!= {}," in source
    assert "preLoadReggeWheelerPaclets =!= {}" not in source
    assert '"regge_wheeler_paclet_candidate_count" ->' in source
    assert '"find_file_before_load" -> preLoadFindFileRecord' in source
    assert '"candidate_count_after_load" -> Length[loadedReggeWheelerPaclets]' in source
    assert "found = Quiet[Check[ExpandFileName[FindFile[context]], $Failed]]" in source
    assert "found =!= path" in source
    micro = source.index('If[operation === "source_load_micro_sentinel",')
    micro_end = source.index("actualEndProjection = normalizeLedger[loadedEnd]", micro)
    publish = source.index("publishResult[microResult]", micro_end)
    early_exit = source.index("Exit[0]", publish)
    solver = source.index("ReggeWheelerRadial[")
    assert source.count("ReggeWheelerRadial[") == 1
    assert micro < micro_end < publish < early_exit < solver
    assert "ReggeWheelerRadial[" not in source[micro:solver]
    assert '"regge_wheeler_radial_call_count" -> 0' in source[micro:solver]
    assert '"scientific_call_count" -> 0' in source[micro:solver]


def test_start_gate_rehashes_package_snapshot_and_six_implementation_paths() -> None:
    gate = replacement.verify_start_gate()
    assert gate["static_contract"]["official"] == {
        "keys": 23,
        "calls": 161,
        "boundary_solutions": 322,
        "overlaps": 483,
    }
    assert len(gate["implementation_hashes"]) == 6
    assert gate["scientific_evidence"] is False


def test_future_dispatch_namespace_review_may_be_absent_during_zero_science_preflight() -> (
    None
):
    expected = Path(
        "docs/handoffs/archive/"
        "T7_2026-08-13_v3_1_x_sentinel_repair_cycle2_source_ledger_"
        "implementation_delta_review.md"
    )
    assert (
        replacement.IMPLEMENTATION_REVIEW_PATH.relative_to(replacement.ROOT) == expected
    )
    assert not replacement.IMPLEMENTATION_REVIEW_PATH.exists()
    gate = replacement.verify_start_gate()
    assert gate["scientific_evidence"] is False
    assert len(gate["implementation_hashes"]) == 6


def test_dispatch_namespace_and_review_lineage_are_exact_and_non_circular() -> None:
    assert replacement.MICRO_DISPATCH_PATTERN.fullmatch(
        "T0_2026-08-13_v3_1_x_source_load_micro_sentinel_dispatch_attempt_0001.json"
    )
    assert replacement.SENTINEL_DISPATCH_PATTERN.fullmatch(
        "T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0003.json"
    )
    assert replacement.IMPLEMENTATION_REVIEW_REQUIRED_AUTHORITY_HASHES == (
        "2f4f2304b4e9507a3627ee26d3aadd9d7632152d7367653746bedf1ec591673c",
        "4acf5aa7e09874576da100a3b9c7c6acee2ea033d7da798dde689f1611da5685",
        "582bc3248a6acf7164485203d317b2cdc0d2a7819a13dcdb584e86e9a90bebdf",
        "bdbe1c1d05b086cac50d3dd5b99759a5d131b86e73788f92b0788bc9775eba1b",
        "d78e6ba25a8b8f8885d75552e50fbe52f9715fd4288d1a58982021448da2d97f",
        "52096dc832fed2bc64153273e3d5d69ac446ac96ccf63bf468d12e7b25162aa1",
        "1cf801469dc13fd076a5dd87e86c728b3b5c1c681c24f5d59e507f6172ab7c75",
        "7f002b2e2abb5a80d0836ff4d458a52842af4aad337db0d1e50c8dc1ce8da232",
    )
    assert replacement.OFFICIAL_DISPATCH_PATTERN.pattern == (
        r"T0_\d{4}-\d{2}-\d{2}_v3_1_x_external_direct_official_dispatch_"
        r"attempt_0001\.json"
    )
    assert replacement.OFFICIAL_DISPATCH_PATTERN.fullmatch(
        "T0_2026-08-13_v3_1_x_external_direct_official_dispatch_attempt_0001.json"
    )
    assert replacement.OFFICIAL_DISPATCH_PATTERN.fullmatch(
        "T0_2099-12-31_v3_1_x_external_direct_official_dispatch_attempt_0001.json"
    )
    assert not replacement.OFFICIAL_DISPATCH_PATTERN.fullmatch(
        "T0_2026-08-13_v3_1_x_external_direct_official_dispatch_attempt_0002.json"
    )


def test_clean_launch_environment_has_no_wildcards_or_ignored_keys() -> None:
    expected = dict(replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT)
    assert replacement.validate_clean_launch_environment(expected)
    for key in tuple(expected):
        broken = dict(expected)
        broken.pop(key)
        assert not replacement.validate_clean_launch_environment(broken)
    for key in tuple(expected):
        broken = dict(expected)
        broken[key] = "changed"
        assert not replacement.validate_clean_launch_environment(broken)
    assert not replacement.validate_clean_launch_environment(
        {**expected, "SCHWO_UNREVIEWED_EXTRA": "1"}
    )
