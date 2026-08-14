from __future__ import annotations

import json
import os
from pathlib import Path
import stat

import mpmath as mp
import pytest

from schwgw.validation import phase6_mpmath_radial_repair as repair


def _failure(
    *, kM: str, sector: str, ell: int, severity: str, ordinal: int
) -> repair.FailureKey:
    identity = {
        "mode": 0o444,
        "nlink": 1,
        "path": f"/immutable/source/{ordinal}.json",
        "sha256": f"{ordinal:064x}",
        "size": 100 + ordinal,
    }
    return repair.FailureKey(
        kM=kM,
        sector=sector,
        ell=ell,
        shard_id=f"shard_{ordinal:03d}",
        shard_ordinal=ordinal,
        selected_r_out_M="300",
        turning_severity=severity,
        checkpoint_identity=identity,
        run_contract_identity={
            **identity,
            "path": f"/immutable/contract/{ordinal}.json",
        },
    )


def _synthetic_failure_domain() -> tuple[repair.FailureKey, ...]:
    k_values = ("0.5", "1.5", "2.5", "4")
    severity_values = ("0.04", "0.08", "0.14")
    result = []
    ordinal = 0
    for k_index, kM in enumerate(k_values):
        for sector in repair.SECTORS:
            for severity_index, severity in enumerate(severity_values):
                result.append(
                    _failure(
                        kM=kM,
                        sector=sector,
                        ell=2 + 10 * k_index + severity_index,
                        severity=severity,
                        ordinal=ordinal,
                    )
                )
                ordinal += 1
    return tuple(result)


def _anchor(anchor_id: str, *, sector: str = "even") -> repair.RepairAnchor:
    return repair.RepairAnchor(
        anchor_id=anchor_id,
        source=_failure(kM="0.5", sector=sector, ell=2, severity="0.08", ordinal=2),
        k_band="low",
        severity_band="moderate",
        stratum_candidate_count=1,
        ell_quantile_target="0.5",
    )


def _plan(anchors: tuple[repair.RepairAnchor, ...]) -> dict[str, object]:
    return {
        "anchors": [anchor.to_record() for anchor in anchors],
        "campaign_kind": "TWO_ANCHOR_TIMING_BENCHMARK",
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "planned_anchor_count": len(anchors),
        "run_id": "unit_timing_benchmark",
        "schema": repair.PLAN_SCHEMA,
        "scientific_acceptance": False,
    }


def _accepted_result(anchor: repair.RepairAnchor) -> dict[str, object]:
    return {
        "anchor": anchor.to_record(),
        "convention_uncertainty_budget": {"overall_state": "FROZEN"},
        "elapsed_seconds": 1.25,
        "global_green_permitted": False,
        "ladder_closed": True,
        "numerical_uncertainty_budget": {"overall_state": "PASS"},
        "schema": repair.ANCHOR_RESULT_SCHEMA,
        "scientific_acceptance": True,
        "status": "LADDER_CLOSED",
    }


def test_selection_is_deterministic_and_covers_all_24_strata() -> None:
    failures = _synthetic_failure_domain()
    first = repair.select_repair_anchors(failures)
    second = repair.select_repair_anchors(tuple(reversed(failures)))

    assert first == second
    assert len(first) == 24
    assert (
        len({(item.k_band, item.source.sector, item.severity_band) for item in first})
        == 24
    )
    assert {item.source.sector for item in first} == {"odd", "even"}

    timing = repair.benchmark_anchors(first)
    assert [item.source.sector for item in timing] == ["odd", "even"]
    assert [(item.k_band, item.severity_band) for item in timing] == [
        ("low", "moderate"),
        ("high", "severe"),
    ]


def test_rw_and_zerilli_potentials_are_direct_arbitrary_precision_formulas() -> None:
    with mp.workdps(80):
        radius = mp.mpf("17.25")
        ell = 9
        lapse = 1 - 2 / radius
        odd_expected = lapse * (ell * (ell + 1) / radius**2 - 6 / radius**3)
        lam = mp.mpf((ell - 1) * (ell + 2)) / 2
        even_expected = (
            lapse
            / radius**2
            * (
                2 * lam**2 * (lam + 1)
                + 6 * lam**2 / radius
                + 18 * lam / radius**2
                + 18 / radius**3
            )
            / (lam + 3 / radius) ** 2
        )

        assert repair.radial_potential("odd", ell, radius) == odd_expected
        assert mp.almosteq(
            repair.radial_potential("even", ell, radius),
            even_expected,
            rel_eps=mp.mpf("1e-75"),
        )


def test_independent_jost_pair_freezes_complex_conjugate_ordering() -> None:
    with mp.workdps(60):
        incoming = repair.independent_jost_basis(
            sector="even", ell=8, k=mp.mpf("0.7"), radius=mp.mpf(300), sign=-1, order=80
        )
        outgoing = repair.independent_jost_basis(
            sector="even", ell=8, k=mp.mpf("0.7"), radius=mp.mpf(300), sign=1, order=80
        )
        assert mp.almosteq(outgoing[0], mp.conj(incoming[0]), rel_eps=mp.mpf("1e-50"))
        assert mp.almosteq(outgoing[1], mp.conj(incoming[1]), rel_eps=mp.mpf("1e-50"))


def test_ladder_delta_is_evaluated_above_the_process_default_precision() -> None:
    left = {"real": "1.0", "imag": "0.0"}
    right = {
        "real": "1.0000000000000000000000000000000000000001",
        "imag": "0.0",
    }

    assert repair._relative_complex(left, right) > mp.mpf("1e-41")


def test_one_even_node_uses_mpmath_full_state_without_parity_derivation() -> None:
    result = repair.solve_anchor_node(
        _anchor("even_smoke"), precision_dps=35, maximum_step_rstar="2"
    )

    assert result["status"] == "COMPLETED"
    assert result["backend"] == {
        "actual_decimal_digits": 35,
        "actual_precision_bits": result["backend"]["actual_precision_bits"],
        "arithmetic": f"mpmath {mp.__version__}",
        "even_independent_solve": True,
        "numpy_used": False,
        "parity_derived_even_used": False,
        "scipy_used": False,
    }
    assert result["integration_steps"] > 0


def test_call_graph_isolation_accepts_only_the_dedicated_module_and_runner() -> None:
    root = Path(__file__).resolve().parents[2]
    result = repair.prove_call_graph_isolation(
        (
            root / "src/schwgw/validation/phase6_mpmath_radial_repair.py",
            root / "scripts/phase6_run_mpmath_radial_repair.py",
        )
    )

    assert result["isolated"] is True
    assert result["numpy_used"] is False
    assert result["scipy_used"] is False


def test_call_graph_isolation_rejects_old_backend_import(tmp_path: Path) -> None:
    source = tmp_path / "bad.py"
    source.write_text(
        "from schwgw.validation.phase6_mpmath_radial import solve_mode_batch\n",
        encoding="utf-8",
    )

    with pytest.raises(repair.APRadialRepairError, match="prohibited backend"):
        repair.prove_call_graph_isolation((source,))


def test_campaign_is_append_only_resumable_and_seals_immutable(tmp_path: Path) -> None:
    anchors = (_anchor("timing_one", sector="odd"), _anchor("timing_two"))
    plan = _plan(anchors)
    output = tmp_path / "timing_campaign"
    calls = 0

    def interrupted_solver(anchor: repair.RepairAnchor) -> dict[str, object]:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("simulated interruption")
        return _accepted_result(anchor)

    with pytest.raises(RuntimeError, match="simulated interruption"):
        repair.run_repair_campaign(
            output_root=output,
            plan=plan,
            solver=interrupted_solver,
        )

    assert stat.S_IMODE(output.stat().st_mode) == 0o700
    first = output / "anchor_00__timing_one.json"
    assert stat.S_IMODE(first.stat().st_mode) == 0o444
    first_bytes = first.read_bytes()

    summary = repair.run_repair_campaign(
        output_root=output,
        plan=plan,
        resume=True,
        solver=_accepted_result,
    )

    assert first.read_bytes() == first_bytes
    assert summary["scientific_acceptance"] is False
    assert summary["status"] == "TIMING_BENCHMARK_COMPLETE_NO_SCIENTIFIC_ACCEPTANCE"
    assert summary["completed_anchor_count"] == 2
    assert stat.S_IMODE(output.stat().st_mode) == 0o555
    assert not (output / ".writer.lock").exists()
    for child in output.iterdir():
        assert stat.S_IMODE(child.stat().st_mode) == 0o444
        assert child.stat().st_nlink == 1
        payload = json.loads(child.read_bytes())
        assert child.read_bytes() == repair.canonical_json_bytes(payload)


def test_campaign_rejects_a_manual_scientific_promotion(tmp_path: Path) -> None:
    anchor = _anchor("bad_promotion")

    def bad_solver(item: repair.RepairAnchor) -> dict[str, object]:
        result = _accepted_result(item)
        result["ladder_closed"] = False
        return result

    with pytest.raises(repair.APRadialRepairError, match="result schema"):
        repair.run_repair_campaign(
            output_root=tmp_path / "bad",
            plan=_plan((anchor,)),
            solver=bad_solver,
        )

    assert os.access(tmp_path / "bad", os.W_OK)
