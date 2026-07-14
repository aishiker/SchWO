from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


pytestmark = pytest.mark.regression

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SCHEMA_TEMPLATE = FIXTURE_DIR / "schema_template.json"


def test_schema_template_matches_v02_contract() -> None:
    fixture = _load_json(SCHEMA_TEMPLATE)

    _assert_fixture_schema(fixture, allow_template_nulls=True)


def test_committed_numeric_regression_fixtures_match_schema() -> None:
    fixture_paths = sorted(
        path for path in FIXTURE_DIR.glob("*.json") if path != SCHEMA_TEMPLATE
    )

    for path in fixture_paths:
        _assert_fixture_schema(_load_json(path), allow_template_nulls=False)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict), f"{path} must contain a JSON object"
    return data


def _assert_fixture_schema(
    fixture: dict[str, Any], *, allow_template_nulls: bool
) -> None:
    assert set(fixture) == {
        "schema_version",
        "case_id",
        "conventions",
        "parameters",
        "observables",
        "diagnostics",
    }
    assert fixture["schema_version"] == "0.2"
    assert _nonempty_string(fixture["case_id"])

    _assert_conventions(fixture["conventions"])
    _assert_parameters(fixture["parameters"])
    _assert_observables(
        fixture["observables"], allow_template_nulls=allow_template_nulls
    )
    _assert_diagnostics(
        fixture["diagnostics"], allow_template_nulls=allow_template_nulls
    )


def _assert_conventions(conventions: Any) -> None:
    assert isinstance(conventions, dict)
    assert set(conventions) == {"fourier", "units", "gauge"}
    assert conventions["fourier"] == "exp(-i k t)"
    assert conventions["units"] == "G=c=M=1"
    assert conventions["gauge"] == "Regge-Wheeler"


def _assert_parameters(parameters: Any) -> None:
    assert isinstance(parameters, dict)
    assert set(parameters) == {
        "M",
        "kM",
        "r_obs",
        "A_plus",
        "A_cross",
        "lmax",
        "lmax_values",
    }
    assert _real_number(parameters["M"])
    assert _real_number(parameters["kM"])
    assert _real_number(parameters["r_obs"])
    assert isinstance(parameters["lmax"], int)
    assert parameters["lmax"] >= 2
    _assert_lmax_values(parameters["lmax_values"])
    assert parameters["lmax"] == parameters["lmax_values"][-1]
    _assert_complex_pair(parameters["A_plus"], allow_template_nulls=False)
    _assert_complex_pair(parameters["A_cross"], allow_template_nulls=False)


def _assert_observables(observables: Any, *, allow_template_nulls: bool) -> None:
    assert isinstance(observables, dict)
    assert set(observables) == {"selected_points"}
    selected_points = observables["selected_points"]
    assert isinstance(selected_points, list)
    assert selected_points

    for point in selected_points:
        assert isinstance(point, dict)
        assert set(point) == {"r", "theta", "phi", "h_plus", "h_cross"}
        assert _real_number(point["r"])
        assert _real_number(point["theta"])
        assert _real_number(point["phi"])
        _assert_complex_pair(point["h_plus"], allow_template_nulls=allow_template_nulls)
        _assert_complex_pair(
            point["h_cross"], allow_template_nulls=allow_template_nulls
        )


def _assert_diagnostics(diagnostics: Any, *, allow_template_nulls: bool) -> None:
    assert isinstance(diagnostics, dict)
    assert set(diagnostics) == {
        "boundary_residual",
        "wronskian_residual",
        "flux_residual",
        "match_condition_number",
        "lmax_convergence",
        "near_axis_lmax_convergence",
        "final_lmax_pair",
        "radial_diagnostic_warnings",
    }
    for key in (
        "boundary_residual",
        "wronskian_residual",
        "flux_residual",
        "match_condition_number",
        "lmax_convergence",
        "near_axis_lmax_convergence",
    ):
        value = diagnostics[key]
        if value is None:
            assert allow_template_nulls
        else:
            assert _real_number(value)
    _assert_final_lmax_pair(
        diagnostics["final_lmax_pair"], allow_template_nulls=allow_template_nulls
    )
    _assert_radial_diagnostic_warnings(diagnostics["radial_diagnostic_warnings"])


def _assert_lmax_values(value: Any) -> None:
    assert isinstance(value, list)
    assert len(value) >= 2
    previous = 1
    for item in value:
        assert isinstance(item, int)
        assert item > previous
        previous = item


def _assert_final_lmax_pair(value: Any, *, allow_template_nulls: bool) -> None:
    if value is None:
        assert allow_template_nulls
        return
    assert isinstance(value, list)
    assert len(value) == 2
    assert all(isinstance(item, int) for item in value)
    assert value[0] < value[1]


def _assert_radial_diagnostic_warnings(value: Any) -> None:
    assert isinstance(value, list)
    for warning in value:
        assert isinstance(warning, dict)
        assert set(warning) == {
            "kM",
            "ell",
            "sector",
            "warning_type",
            "raw_wronskian_residual",
            "flux_residual",
            "boundary_residual",
            "barrier_action",
            "expected_flux_scale",
        }
        assert _real_number(warning["kM"])
        assert isinstance(warning["ell"], int)
        assert warning["ell"] >= 2
        assert warning["sector"] in {"odd", "even"}
        assert _nonempty_string(warning["warning_type"])
        for key in (
            "raw_wronskian_residual",
            "flux_residual",
            "boundary_residual",
            "barrier_action",
            "expected_flux_scale",
        ):
            assert _real_number(warning[key])


def _assert_complex_pair(value: Any, *, allow_template_nulls: bool) -> None:
    assert isinstance(value, dict)
    assert set(value) == {"real", "imag"}
    for component in value.values():
        if component is None:
            assert allow_template_nulls
        else:
            assert _real_number(component)


def _real_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
