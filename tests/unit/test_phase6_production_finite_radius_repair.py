from __future__ import annotations

from pathlib import Path
import runpy
import stat

import pytest

from schwgw.numerics.scaled_tortoise_radial import (
    solve_scaled_tortoise_radial_at_radius,
)
from schwgw.validation.phase6_production_finite_radius_repair import (
    EXPECTED_FAILURE_COUNT,
    execute_repair_mode,
    load_repair_inventory,
    repair_key_id,
)

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN_ROOT = (
    ROOT / "runs/phase6/radial_validation/"
    "v1_production_finite_radius_campaign_v1_20260808_py314"
)
DOMAIN_ROOT = ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
EXECUTION_ROOT = ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
RUNNER_PATH = ROOT / "scripts/phase6_run_production_finite_radius_repair.py"


@pytest.fixture(scope="module")
def inventory():
    return load_repair_inventory(
        CAMPAIGN_ROOT,
        domain_root=DOMAIN_ROOT,
        execution_root=EXECUTION_ROOT,
    )


@pytest.fixture(scope="module")
def runner():
    return runpy.run_path(str(RUNNER_PATH))


def test_inventory_is_exact_immutable_failure_ledger(inventory) -> None:
    assert len(inventory.modes) == EXPECTED_FAILURE_COUNT == 3_382
    assert inventory.inventory_sha256 == (
        "e39a6b9ab94514d7ac3dd7f3e7f341b8222e4b725834701d3d690dd12a9d0e02"
    )
    assert repair_key_id(inventory.modes[0].key) == "kM=0.3;sector=odd;ell=5"
    assert repair_key_id(inventory.modes[-1].key) == "kM=4;sector=even;ell=114"
    assert [site.x_M for site in inventory.frozen.sites] == [
        0.0,
        1.0,
        2.0,
        3.0,
        10.0,
        15.0,
        20.0,
        25.0,
    ]
    assert {mode.predecessor_payload_identity["path"] for mode in inventory.modes}
    assert not any(
        "v1_production_finite_radius_k0p5_odd_v1_20260808_py314"
        in str(mode.predecessor_payload_identity["path"])
        for mode in inventory.modes
    )


def test_one_backend_call_returns_all_exact_eight_states(inventory) -> None:
    calls = []

    def spy(request, background):
        calls.append(request)
        return solve_scaled_tortoise_radial_at_radius(request, background)

    record = execute_repair_mode(
        inventory.modes[0],
        inventory.frozen.sites,
        solver=spy,
    )

    assert len(calls) == 1
    assert record["status"] == "MEASURED"
    assert record["solver_call_count"] == 1
    assert record["scientific_acceptance"] is False
    assert record["global_green_permitted"] is False
    states = record["result"]["states"]
    assert len(states) == 8
    assert [state["radius_M_decimal"] for state in states] == [
        site.radius_M_decimal for site in inventory.frozen.sites
    ]
    diagnostics = record["result"]["diagnostics"]
    assert diagnostics["riccati_variable_used"] is False
    assert diagnostics["pseudoinverse_used"] is False
    assert diagnostics["scientific_acceptance"] is False
    assert record["result"]["flux_diagnostics"]["interpretation"] == (
        "internal signed-current identity only"
    )


def test_runner_strictly_resumes_per_key_and_seals(
    tmp_path: Path,
    inventory,
    runner,
) -> None:
    output_root = tmp_path / "repair_resume"
    solve_calls = 0

    def interrupt_second(request, background):
        nonlocal solve_calls
        solve_calls += 1
        if solve_calls == 2:
            raise KeyboardInterrupt("simulated process interruption")
        return solve_scaled_tortoise_radial_at_radius(request, background)

    with pytest.raises(KeyboardInterrupt, match="simulated process interruption"):
        runner["run"](
            output_root,
            campaign_root=CAMPAIGN_ROOT,
            domain_root=DOMAIN_ROOT,
            execution_root=EXECUTION_ROOT,
            limit=2,
            solver=interrupt_second,
            kernel_unit_test_only=True,
        )
    assert len(list((output_root / "records").glob("*.json"))) == 1
    assert not (output_root / "run_result.json").exists()
    first_bytes = next((output_root / "records").glob("*.json")).read_bytes()

    result = runner["run"](
        output_root,
        campaign_root=CAMPAIGN_ROOT,
        domain_root=DOMAIN_ROOT,
        execution_root=EXECUTION_ROOT,
        limit=2,
        solver=solve_scaled_tortoise_radial_at_radius,
        kernel_unit_test_only=True,
    )
    assert next((output_root / "records").glob("*.json")).read_bytes() == first_bytes
    assert result["terminal_mode_count"] == 2
    assert result["solver_call_count"] == 2
    assert result["scientific_acceptance"] is False
    assert result["kernel_unit_test_only"] is True
    assert stat.S_IMODE(output_root.stat().st_mode) == 0o555
    assert all(
        stat.S_IMODE(path.stat().st_mode) == 0o444
        for path in (output_root / "records").glob("*.json")
    )


def test_single_writer_lock_is_fail_closed(tmp_path: Path, runner) -> None:
    root = tmp_path / "locked"
    with runner["_writer_lock"](root):
        with pytest.raises(runner["RepairRunError"], match="another writer"):
            with runner["_writer_lock"](root):
                pass


def test_repair_is_source_isolated_from_legacy_solver() -> None:
    module_source = (
        ROOT / "src/schwgw/validation/phase6_production_finite_radius_repair.py"
    ).read_text(encoding="utf-8")
    runner_source = RUNNER_PATH.read_text(encoding="utf-8")

    assert "solve_scaled_tortoise_radial_at_radius" in module_source
    assert "solve_conditioned_radial_at_radius" not in module_source
    assert "np.linalg.pinv" not in module_source
    assert "--limit" in runner_source
    assert "LOCK_EX | fcntl.LOCK_NB" in runner_source
