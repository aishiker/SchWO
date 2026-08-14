from __future__ import annotations

import copy
import hashlib

import pytest

from schwgw.validation import phase6_bhpt_direct_bounded as bounded


def _node(*, wp: int, pg: int, digits: int) -> dict[str, object]:
    phase = {"imag": "0", "real": "-0.6"}
    reflection = {"imag": "0", "real": "0.6"}
    transmission = {"imag": "0", "real": "0.8"}
    records = [
        {
            "basis_wronskian_abs": "1",
            "flux_unitarity_residual_abs": "0",
            "fraction": fraction,
            "incidence": {"imag": "0", "real": "1.25"},
            "phase_factor": dict(phase),
            "radius_M": radius,
            "reflection": {"imag": "0", "real": "0.75"},
            "reflection_ratio": dict(reflection),
            "transmission": dict(transmission),
        }
        for fraction, radius in (("0.8", "240"), ("0.88", "264"), ("0.96", "288"))
    ]
    return {
        "boundary_conditions_solved": ["In", "Up"],
        "global_green_permitted": False,
        "key": {"ell": 2, "kM": "0.5", "sector": "odd"},
        "loaded_numerical_integration": {
            "path": "/tmp/overlay/Kernel/NumericalIntegration.m",
            "sha256": "a" * 64,
        },
        "match_records": records,
        "matching_radius_phase_spread_abs": "0",
        "method": "NumericalIntegration",
        "outer_boundary_radius_M": "300",
        "parity_derived_even_used": False,
        "phase_factor": dict(phase),
        "potential": "ReggeWheeler",
        "precision": {
            "accuracy_goal_decimal_digits": pg,
            "precision_goal_decimal_digits": pg,
            "serialized_output_digits": digits,
            "working_precision_decimal_digits": wp,
        },
        "reflection_ratio": dict(reflection),
        "runtime": {"system_id": "test", "wolfram_version": "test"},
        "schema": bounded.NODE_SCHEMA,
        "selected_flux_unitarity_residual_abs": "0",
        "selected_match_index": 1,
        "solver_elapsed_seconds": "1",
        "transmission": dict(transmission),
    }


def test_overlay_replaces_exactly_two_statements(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = (
        b"prefix\n"
        + bounded.ORIGINAL_OUTER_LINE
        + b"\nmid\n"
        + bounded.ORIGINAL_OUTER_LINE
        + b"\nsuffix\n"
    )
    monkeypatch.setitem(
        bounded.EXPECTED_SOURCE_SHA256,
        "Kernel/NumericalIntegration.m",
        hashlib.sha256(raw).hexdigest(),
    )
    transformed = bounded._overlay_bytes(raw)
    assert transformed.count(bounded.OVERLAY_OUTER_LINE) == 2
    assert bounded.ORIGINAL_OUTER_LINE not in transformed


def test_validate_node_and_precision_comparison_pass() -> None:
    low = bounded.validate_node(
        _node(wp=40, pg=20, digits=30),
        expected_key={"ell": 2, "kM": "0.5", "sector": "odd"},
        precision_node=bounded.PRECISION_NODES[0],
        overlay_sha256="a" * 64,
    )
    high = bounded.validate_node(
        _node(wp=60, pg=30, digits=40),
        expected_key={"ell": 2, "kM": "0.5", "sector": "odd"},
        precision_node=bounded.PRECISION_NODES[1],
        overlay_sha256="a" * 64,
    )
    comparison = bounded.compare_precision_nodes(low, high)
    assert comparison["overall_state"] == "PASS"
    assert all(check["state"] == "PASS" for check in comparison["checks"].values())


def test_validate_node_rejects_parity_derivation() -> None:
    payload = copy.deepcopy(_node(wp=40, pg=20, digits=30))
    payload["parity_derived_even_used"] = True
    with pytest.raises(bounded.BHPTBoundedDirectError, match="method/parity"):
        bounded.validate_node(
            payload,
            expected_key={"ell": 2, "kM": "0.5", "sector": "odd"},
            precision_node=bounded.PRECISION_NODES[0],
            overlay_sha256="a" * 64,
        )
