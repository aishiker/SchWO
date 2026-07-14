from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def test_risk_pilot_script_has_frozen_scope() -> None:
    path = Path("scripts/phase5_run_delta0p1_risk_pilot.py")
    text = path.read_text(encoding="utf-8")
    assert "run_delta0p1_risk_pilot" in text
    assert "--output-dir" in text
    assert "--accepted-review-npz" in text
    assert "--radial-gate-dir" in text
    assert "--resume" in text
    assert "kirchhoff" not in text.lower()
    assert "schwgw.viz" not in text
    spec = importlib.util.spec_from_file_location("phase5_risk_pilot", path)
    assert spec is not None


def test_risk_pilot_script_passes_only_frozen_arguments(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = Path("scripts/phase5_run_delta0p1_risk_pilot.py")
    spec = importlib.util.spec_from_file_location("phase5_risk_pilot", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    received: dict[str, object] = {}

    def fake_run(**kwargs: object) -> Path:
        received.update(kwargs)
        return tmp_path / "risk_pilot_values.npz"

    monkeypatch.setattr(module, "run_delta0p1_risk_pilot", fake_run)
    output = tmp_path / "out"
    review = tmp_path / "review.npz"
    gate = tmp_path / "gate"
    assert module.main([
        "--output-dir", str(output),
        "--accepted-review-npz", str(review),
        "--radial-gate-dir", str(gate),
        "--resume",
    ]) == 0
    assert received == {
        "output_dir": output,
        "accepted_review_npz": review,
        "radial_gate_dir": gate,
        "resume": True,
    }
