from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_script() -> object:
    path = Path("scripts/phase5_run_targeted_adaptive_refinement.py")
    spec = importlib.util.spec_from_file_location("phase5_targeted_adaptive", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_has_only_frozen_scope() -> None:
    path = Path("scripts/phase5_run_targeted_adaptive_refinement.py")
    text = path.read_text(encoding="utf-8")
    assert "run_targeted_adaptive_refinement" in text
    assert "--accepted-review-npz" in text
    assert "--accepted-risk-pilot-dir" in text
    assert "--radial-gate-dir" in text
    assert "--resume" in text
    assert "kirchhoff" not in text.lower()
    assert "schwgw.viz" not in text


def test_script_passes_only_frozen_arguments(tmp_path: Path, monkeypatch: object) -> None:
    module = _load_script()
    received: dict[str, object] = {}

    def fake_run(**kwargs: object) -> Path:
        received.update(kwargs)
        return tmp_path / "adaptive_refinement_values.npz"

    monkeypatch.setattr(module, "run_targeted_adaptive_refinement", fake_run)
    output = tmp_path / "out"
    review = tmp_path / "review.npz"
    risk = tmp_path / "risk"
    gate = tmp_path / "gate"
    assert module.main(
        [
            "--output-dir",
            str(output),
            "--accepted-review-npz",
            str(review),
            "--accepted-risk-pilot-dir",
            str(risk),
            "--radial-gate-dir",
            str(gate),
            "--resume",
        ]
    ) == 0
    assert received == {
        "output_dir": output,
        "accepted_review_npz": review,
        "accepted_risk_pilot_dir": risk,
        "radial_gate_dir": gate,
        "resume": True,
    }
