from __future__ import annotations

import ast
from pathlib import Path

from schwgw.numerics.legacy import paper_oracles


ROOT = Path(__file__).resolve().parents[2]
CORE_SOURCE = ROOT / "src/schwgw/numerics/radial_solver.py"
LEGACY_SOURCE = ROOT / "src/schwgw/numerics/legacy/paper_oracles.py"


def test_paper_oracle_inventory_is_confined_to_legacy_module() -> None:
    core_tree = ast.parse(CORE_SOURCE.read_text(encoding="utf-8"))
    legacy_tree = ast.parse(LEGACY_SOURCE.read_text(encoding="utf-8"))

    core_imports = {
        alias.name
        for node in ast.walk(core_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        str(node.module)
        for node in ast.walk(core_tree)
        if isinstance(node, ast.ImportFrom)
    }
    core_definitions = {
        node.name
        for node in ast.walk(core_tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
    core_literals = {
        node.value
        for node in ast.walk(core_tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    legacy_literals = {
        node.value
        for node in ast.walk(legacy_tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }

    assert not any("q018_" in name for name in core_imports)
    assert not any(name.startswith("_validate_q018") for name in core_definitions)
    assert not any("near_axis_x" in value for value in core_literals)
    assert not any("far_axis_x" in value for value in core_literals)
    assert any("near_axis_x" in value for value in legacy_literals)
    assert any("far_axis_x" in value for value in legacy_literals)


def test_legacy_oracle_inventory_remains_exact_and_opt_in() -> None:
    expected = {
        "q018_riccati",
        "q018_tablei_km4_transition",
        "q018_tablei_review_grid_transition",
        "q018_tablei_delta0p1_risk_pilot_transition",
        "q018_tablei_targeted_adaptive_transition",
        "q018_tablei_further_local_transition",
        "q018_tablei_literal_failed_child_transition",
        "q018_tablei_another_bounded_local_transition",
    }

    assert set(paper_oracles._SUPPORTED_REQUIRED_RADIUS_ORACLE_NAMES) == expected
    assert all(paper_oracles.is_legacy_oracle_supported(name) for name in expected)
    assert not paper_oracles.is_legacy_oracle_supported(None)
    assert not paper_oracles.is_legacy_oracle_supported("unknown")
