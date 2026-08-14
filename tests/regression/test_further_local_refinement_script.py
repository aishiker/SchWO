from __future__ import annotations

import importlib.util
from pathlib import Path


def test_further_local_runner_has_frozen_scope() -> None:
    path = Path("scripts/phase5_run_further_local_refinement.py")
    spec = importlib.util.spec_from_file_location("phase5_further_local", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    text = path.read_text(encoding="utf-8")
    assert "run_further_local_refinement" in text
    assert "--accepted-review-npz" in text
    assert "--accepted-risk-pilot-dir" in text
    assert "--accepted-adaptive-dir" in text
    assert "--accepted-t7bz-evidence" in text
    assert "--radial-gate-dir" in text
    assert "--resume" in text
    assert "kirchhoff" not in text.lower()
    assert "schwgw.viz" not in text


def test_runner_passes_only_frozen_arguments(
    tmp_path: Path, monkeypatch: object
) -> None:
    path = Path("scripts/phase5_run_further_local_refinement.py")
    spec = importlib.util.spec_from_file_location("phase5_further_local", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    received: dict[str, object] = {}

    def fake_run(**kwargs: object) -> Path:
        received.update(kwargs)
        return tmp_path / "further_local_values.npz"

    monkeypatch.setattr(module, "run_further_local_refinement", fake_run)
    values = {
        "output_dir": tmp_path / "out",
        "accepted_review_npz": tmp_path / "review.npz",
        "accepted_risk_pilot_dir": tmp_path / "risk",
        "accepted_adaptive_dir": tmp_path / "adaptive",
        "accepted_t7bz_evidence": tmp_path / "T7bz.md",
        "accepted_t4aa_gate_dir": tmp_path / "t4aa",
        "radial_gate_dir": tmp_path / "gate",
    }
    argv: list[str] = []
    options = {
        "output_dir": "--output-dir",
        "accepted_review_npz": "--accepted-review-npz",
        "accepted_risk_pilot_dir": "--accepted-risk-pilot-dir",
        "accepted_adaptive_dir": "--accepted-adaptive-dir",
        "accepted_t7bz_evidence": "--accepted-t7bz-evidence",
        "accepted_t4aa_gate_dir": "--accepted-t4aa-gate-dir",
        "radial_gate_dir": "--radial-gate-dir",
    }
    for key, option in options.items():
        argv.extend((option, str(values[key])))
    argv.append("--resume")
    assert module.main(argv) == 0
    assert received == {**values, "resume": True}
