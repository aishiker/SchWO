# T8ak Kirchhoff Review-Grid Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement an isolated Li–Hou–Zhao Eq. (47) scalar Kirchhoff comparison API and generate a verified artifact on the already accepted 18-frequency by 8-point T8aj review grid.

**Architecture:** Keep special-function evaluation in a new pure `schwgw.scattering.kirchhoff` module with a lazy optional `mpmath` backend. Keep artifact validation and serialization in a separate `schwgw.io.kirchhoff` module plus a thin script; neither module may call or modify the Schwarzschild solver, pointwise amplification denominator, masks, normalization, or polarization paths.

**Tech Stack:** Python 3.10+, NumPy, project-local optional `mpmath`, pytest, NPZ/JSON/Markdown artifacts, Codex task messaging.

---

## File Map

- Create `src/schwgw/scattering/kirchhoff.py`: Eq. (47) evaluation and immutable result contract.
- Modify `src/schwgw/scattering/__init__.py`: export the isolated API without eagerly importing `mpmath`.
- Create `tests/unit/test_kirchhoff.py`: formula, branch, validation, backend, and solver-separation tests.
- Create `src/schwgw/io/kirchhoff.py`: accepted-source validation and NPZ/JSON/manifest serialization.
- Modify `src/schwgw/io/__init__.py`: export the artifact generator.
- Create `scripts/phase5_generate_kirchhoff_baseline.py`: thin command-line entry point.
- Create `tests/unit/test_kirchhoff_artifact.py`: artifact schema, hash, eta, and non-claim tests.
- Create `runs/phase5/fig5_fig6_kirchhoff_baseline/*`: ignored review artifact only.
- Modify `status.md` and `docs/handoffs/T8_current.md`: exact T8ak state, evidence, and downstream dispatch status.

The following files are forbidden in this implementation slice: existing production solver modules, `src/schwgw/scattering/transmission.py`, existing T8aj artifacts, visualization modules, configs, fixtures, and paper-style outputs.

### Task 1: Establish The Project-Local Special-Function Backend

**Files:**
- Verify: `pyproject.toml`
- Local-only environment: `.venv/`

- [ ] **Step 1: Record the current backend capability**

Run:

```bash
.venv/bin/python - <<'PY'
import scipy
from scipy import special

print("scipy", scipy.__version__)
try:
    special.hyp1f1(0.2j, 1.0, 0.3j)
except TypeError as exc:
    print("scipy_complex_hyp1f1_unavailable", type(exc).__name__)

try:
    import mpmath
except ModuleNotFoundError:
    print("mpmath_missing")
else:
    print("mpmath", mpmath.__version__)
PY
```

Expected before installation: SciPy reports a `TypeError` for complex `a`, and the current environment may report `mpmath_missing`.

- [ ] **Step 2: Install only the already-declared optional oracle dependency into `.venv`**

Run:

```bash
.venv/bin/python -m pip install -e '.[dev,oracle]'
```

Expected: installation succeeds inside `.venv`; no global interpreter or tracked dependency file changes.

- [ ] **Step 3: Verify high-precision complex Gamma and Kummer support**

Run:

```bash
.venv/bin/python - <<'PY'
import mpmath as mp

with mp.workdps(60):
    gamma = mp.mpf("-8")
    eta = mp.mpf("2.60379158596394")
    value = (
        mp.exp(mp.pi * gamma / 2)
        * mp.exp((-1j * gamma) * mp.log(-gamma))
        * mp.gamma(1 + 1j * gamma)
        * mp.hyp1f1(-1j * gamma, 1, -1j * gamma * eta**2)
    )
    assert mp.isfinite(value.real) and mp.isfinite(value.imag)
    print(mp.nstr(value, 20))
PY
```

Expected: one finite complex value. If installation or this probe fails, stop with `YELLOW / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE PARTIAL`; do not write source code or dispatch T7bs.

### Task 2: Add The Isolated Eq. (47) API With TDD

**Files:**
- Create: `tests/unit/test_kirchhoff.py`
- Create: `src/schwgw/scattering/kirchhoff.py`
- Modify: `src/schwgw/scattering/__init__.py`

- [ ] **Step 1: Write the failing API tests**

Create `tests/unit/test_kirchhoff.py` with:

```python
from __future__ import annotations

import importlib

import mpmath as mp
import numpy as np
import pytest

import schwgw.numerics.radial_solver as radial_solver
import schwgw.scattering.kirchhoff as kirchhoff_module
from schwgw.scattering.kirchhoff import (
    KirchhoffEq47Result,
    compute_kirchhoff_eq47,
)


def test_eq47_shapes_eta_axis_value_and_metadata() -> None:
    kM = np.array([0.1, 1.0, 4.0])
    r_over_M = np.array([30.0, np.hypot(25.0, 30.0)])
    theta = np.array([0.0, np.arctan2(25.0, 30.0)])

    result = compute_kirchhoff_eq47(
        kM_values=kM,
        r_over_M=r_over_M,
        theta=theta,
        dps=60,
    )

    assert isinstance(result, KirchhoffEq47Result)
    assert result.F_complex.shape == (3, 2)
    np.testing.assert_allclose(result.gamma, -2.0 * kM, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(
        result.eta,
        0.5 * np.sqrt(r_over_M) * np.tan(theta),
        rtol=0.0,
        atol=2.0e-15,
    )
    assert result.valid_mask.all()
    np.testing.assert_allclose(result.abs_F, np.abs(result.F_complex))
    np.testing.assert_allclose(result.arg_F_principal, np.angle(result.F_complex))
    assert result.metadata["baseline"]["comparison_only"] is True
    assert result.metadata["baseline"]["not_denominator"] is True
    assert result.metadata["baseline"]["polarization_independent"] is True

    with mp.workdps(80):
        gamma = mp.mpf("-0.2")
        axis_value = mp.exp(
            mp.pi * gamma / 2
            + (-1j * gamma) * mp.log(-gamma)
            + mp.loggamma(1 + 1j * gamma)
        )
    assert result.F_complex[0, 0] == pytest.approx(complex(axis_value), rel=2e-14)


def test_eq47_matches_kummer_transformation_at_high_risk_corner() -> None:
    r_over_M = np.array([np.hypot(25.0, 30.0)])
    theta = np.array([np.arctan2(25.0, 30.0)])
    result = compute_kirchhoff_eq47(
        kM_values=np.array([4.0]),
        r_over_M=r_over_M,
        theta=theta,
        dps=80,
    )

    with mp.workdps(100):
        gamma = mp.mpf("-8")
        eta = mp.mpf(str(result.eta[0]))
        a = -1j * gamma
        z = -1j * gamma * eta**2
        prefactor = mp.exp(
            mp.pi * gamma / 2
            + (-1j * gamma) * mp.log(-gamma)
            + mp.loggamma(1 + 1j * gamma)
        )
        transformed = prefactor * mp.exp(z) * mp.hyp1f1(1 - a, 1, -z)

    assert result.F_complex[0, 0] == pytest.approx(
        complex(transformed), rel=3e-13, abs=3e-13
    )


def test_eq47_never_calls_radial_solver(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("Kirchhoff comparison must not call the radial solver")

    monkeypatch.setattr(radial_solver, "solve_radial_mode", forbidden)
    result = compute_kirchhoff_eq47(
        kM_values=np.array([0.5]),
        r_over_M=np.array([30.0]),
        theta=np.array([0.0]),
        dps=40,
    )
    assert result.valid_mask.tolist() == [[True]]


@pytest.mark.parametrize(
    ("kM", "r_over_M", "theta", "message"),
    [
        ([0.0], [30.0], [0.0], "kM_values"),
        ([0.1], [-1.0], [0.0], "r_over_M"),
        ([0.1], [30.0], [np.pi / 2], "theta"),
    ],
)
def test_eq47_rejects_invalid_domain(kM, r_over_M, theta, message) -> None:
    with pytest.raises(ValueError, match=message):
        compute_kirchhoff_eq47(
            kM_values=np.asarray(kM),
            r_over_M=np.asarray(r_over_M),
            theta=np.asarray(theta),
        )


def test_eq47_reports_missing_optional_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = importlib.import_module

    def fake_import(name: str):
        if name == "mpmath":
            raise ModuleNotFoundError("mpmath")
        return real_import(name)

    monkeypatch.setattr(kirchhoff_module.importlib, "import_module", fake_import)
    with pytest.raises(RuntimeError, match=r"\[oracle\]"):
        compute_kirchhoff_eq47(
            kM_values=np.array([0.1]),
            r_over_M=np.array([30.0]),
            theta=np.array([0.0]),
        )
```

- [ ] **Step 2: Run the tests to confirm the missing module failure**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_kirchhoff.py -q
```

Expected: collection fails because `schwgw.scattering.kirchhoff` does not exist.

- [ ] **Step 3: Implement the minimal pure API**

Create `src/schwgw/scattering/kirchhoff.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass
import importlib
from types import MappingProxyType
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class KirchhoffEq47Result:
    gamma: np.ndarray
    eta: np.ndarray
    F_complex: np.ndarray
    abs_F: np.ndarray
    arg_F_principal: np.ndarray
    valid_mask: np.ndarray
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "gamma", np.asarray(self.gamma, dtype=float))
        object.__setattr__(self, "eta", np.asarray(self.eta, dtype=float))
        object.__setattr__(self, "F_complex", np.asarray(self.F_complex, dtype=complex))
        object.__setattr__(self, "abs_F", np.asarray(self.abs_F, dtype=float))
        object.__setattr__(
            self, "arg_F_principal", np.asarray(self.arg_F_principal, dtype=float)
        )
        object.__setattr__(self, "valid_mask", np.asarray(self.valid_mask, dtype=bool))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


def compute_kirchhoff_eq47(
    *,
    kM_values: np.ndarray,
    r_over_M: np.ndarray,
    theta: np.ndarray,
    dps: int = 50,
) -> KirchhoffEq47Result:
    """Evaluate the frozen scalar Eq. (47) comparison on a frequency/point grid."""

    kM = _positive_vector(kM_values, name="kM_values")
    radius = _positive_vector(r_over_M, name="r_over_M")
    angle = _theta_vector(theta, expected_size=radius.size)
    precision = int(dps)
    if precision != dps or precision < 30:
        raise ValueError("dps must be an integer greater than or equal to 30.")

    mp = _load_mpmath()
    gamma = -2.0 * kM
    eta = 0.5 * np.sqrt(radius) * np.tan(angle)
    values = np.empty((kM.size, radius.size), dtype=np.complex128)
    with mp.workdps(precision):
        for frequency_index, gamma_value in enumerate(gamma):
            gamma_mp = mp.mpf(str(float(gamma_value)))
            log_prefactor = (
                mp.pi * gamma_mp / 2
                + (-1j * gamma_mp) * mp.log(-gamma_mp)
                + mp.loggamma(1 + 1j * gamma_mp)
            )
            prefactor = mp.exp(log_prefactor)
            for point_index, eta_value in enumerate(eta):
                eta_mp = mp.mpf(str(float(eta_value)))
                kummer = mp.hyp1f1(
                    -1j * gamma_mp,
                    1,
                    -1j * gamma_mp * eta_mp**2,
                )
                values[frequency_index, point_index] = complex(prefactor * kummer)

    valid = np.isfinite(values.real) & np.isfinite(values.imag)
    if not valid.all():
        bad = np.argwhere(~valid).tolist()
        raise RuntimeError(f"Eq. (47) backend returned non-finite values at {bad}.")

    metadata = {
        "baseline": {
            "kind": "kirchhoff_eq47_scalar_comparison",
            "source": "Li-Hou-Zhao Eq. (47)",
            "fourier": "exp(-i k t)",
            "gamma_definition": "gamma = -2 M k",
            "power_branch": "principal real log for -gamma=2Mk>0",
            "gamma_function_branch": "principal complex Gamma(1+i gamma)",
            "kummer": "1F1(a,b,z)=Kummer M(a,b,z)",
            "argument": "-i gamma eta^2",
            "theta_F": "principal Arg(F_K) in (-pi, pi]",
            "comparison_only": True,
            "not_denominator": True,
            "not_mask": True,
            "not_normalization": True,
            "polarization_independent": True,
            "backend": "mpmath",
            "backend_version": str(mp.__version__),
            "dps": precision,
        }
    }
    return KirchhoffEq47Result(
        gamma=gamma,
        eta=eta,
        F_complex=values,
        abs_F=np.abs(values),
        arg_F_principal=np.angle(values),
        valid_mask=valid,
        metadata=metadata,
    )


def _load_mpmath():
    try:
        return importlib.import_module("mpmath")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Kirchhoff Eq. (47) requires the project optional dependency; "
            "install with `pip install -e '.[oracle]'`."
        ) from exc


def _positive_vector(values: np.ndarray, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional array.")
    if not np.isfinite(array).all() or np.any(array <= 0.0):
        raise ValueError(f"{name} must contain positive finite values.")
    return array


def _theta_vector(values: np.ndarray, *, expected_size: int) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size != expected_size:
        raise ValueError("theta must be one-dimensional and match r_over_M.")
    if not np.isfinite(array).all() or np.any(np.abs(array) >= np.pi / 2):
        raise ValueError("theta must be finite and satisfy abs(theta) < pi/2.")
    return array
```

Add `KirchhoffEq47Result` and `compute_kirchhoff_eq47` imports and names to
`src/schwgw/scattering/__init__.py`. Do not import `mpmath` there; the new
module already loads it lazily inside the call.

- [ ] **Step 4: Run focused tests and style checks**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_kirchhoff.py -q
.venv/bin/python -m ruff check src/schwgw/scattering/kirchhoff.py tests/unit/test_kirchhoff.py src/schwgw/scattering/__init__.py
```

Expected: all focused tests pass and Ruff reports no errors.

- [ ] **Step 5: Commit the isolated API only**

Run:

```bash
git add src/schwgw/scattering/kirchhoff.py src/schwgw/scattering/__init__.py tests/unit/test_kirchhoff.py
git diff --cached --check
git commit -m "feat: add isolated Kirchhoff Eq47 baseline"
```

Expected: the commit contains exactly those three paths.

### Task 3: Add Accepted-Grid Artifact Serialization With TDD

**Files:**
- Create: `tests/unit/test_kirchhoff_artifact.py`
- Create: `src/schwgw/io/kirchhoff.py`
- Modify: `src/schwgw/io/__init__.py`
- Create: `scripts/phase5_generate_kirchhoff_baseline.py`

- [ ] **Step 1: Write an artifact contract test**

The test must construct a synthetic source with the exact 18-frequency and
eight-point coordinate arrays, call the generator with
`enforce_accepted_source=False`, and assert all of the following exact fields:

```python
required_arrays = {
    "kM_values",
    "point_ids",
    "point_x",
    "point_y",
    "point_z",
    "point_r",
    "point_theta",
    "paper_xi_over_xi0",
    "gamma",
    "eta",
    "eta_minus_paper",
    "F_kirchhoff_complex",
    "abs_F_kirchhoff",
    "arg_F_kirchhoff_principal",
    "arg_F_kirchhoff_unwrapped",
    "valid_kirchhoff_mask",
    "metadata_json",
}
```

The assertions must include:

```python
assert data["F_kirchhoff_complex"].shape == (18, 8)
assert data["valid_kirchhoff_mask"].all()
assert np.max(np.abs(data["eta_minus_paper"])) < 5.0e-5
assert metadata["comparison_only"] is True
assert metadata["not_denominator"] is True
assert metadata["not_mask"] is True
assert metadata["not_normalization"] is True
assert metadata["polarization_independent"] is True
assert metadata["no_solver_rerun"] is True
assert metadata["no_plotting"] is True
assert metadata["not_40_frequency_production"] is True
assert metadata["no_fixtures"] is True
assert metadata["no_paper_style_candidates"] is True
assert metadata["output_npz_sha256"] == file_sha256(output_npz)
```

Also add a rejection test that mutates one `kM_values` entry and expects a
`ValueError` containing `exact accepted 18-frequency grid`.

- [ ] **Step 2: Run the artifact test to verify it fails**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_kirchhoff_artifact.py -q
```

Expected: collection fails because `schwgw.io.kirchhoff` does not exist.

- [ ] **Step 3: Implement the serializer with frozen validation constants**

Create `src/schwgw/io/kirchhoff.py`. It must define these exact constants:

```python
EXPECTED_KM_VALUES = np.array(
    [0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0,
     2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0],
    dtype=float,
)
EXPECTED_POINT_X = np.array([0.0, 1.0, 2.0, 3.0, 10.0, 15.0, 20.0, 25.0])
EXPECTED_POINT_Z = np.full(8, 30.0)
EXPECTED_SOURCE_NPZ_SHA256 = "a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb"
EXPECTED_SOURCE_JSON_SHA256 = "2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537"
EXPECTED_SOURCE_MANIFEST_SHA256 = "86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf"
```

Implement
`generate_kirchhoff_review_grid_artifact(source_npz, output_dir, dps=60,
enforce_accepted_source=True)`. The function must:

1. Require the source NPZ, its `.npz.json` sidecar, and sibling `manifest.md`.
2. When `enforce_accepted_source=True`, compare all three SHA-256 values to
   the constants above before loading data.
3. Load with `allow_pickle=False` and require exact equality of `kM_values`,
   `point_x`, `point_z`, point ids, `point_r`, `point_theta`, and
   `paper_xi_over_xi0`.
4. Recompute `eta = 0.5 * sqrt(point_r) * tan(point_theta)`, require the maximum
   difference from the rounded paper values to be below `5.0e-5`, and retain
   both arrays plus their difference.
5. Call `compute_kirchhoff_eq47` once, with no solver, amplification, mask, or
   visualization call.
6. Store principal phase and `np.unwrap(principal_phase, axis=0)` separately.
7. Write the NPZ first, calculate its SHA-256, then write a JSON sidecar whose
   `output_npz_sha256` matches the saved file, then write `manifest.md` with
   source and output hashes.
8. Embed the formula/branch metadata from the API and the exact boolean
   non-claims asserted in Step 1.
9. Return `(output_npz, sidecar, manifest)`.

The NPZ output path must be
`tablei_kirchhoff_baseline_values.npz`; do not accept a caller-provided output
filename. The function must not overwrite or open the T8aj artifact for write.

Export the generator from `src/schwgw/io/__init__.py`.

- [ ] **Step 4: Add the thin executable script**

Create `scripts/phase5_generate_kirchhoff_baseline.py` with:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.io.kirchhoff import generate_kirchhoff_review_grid_artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(
            "runs/phase5/fig5_fig6_dense_review_grid/"
            "tablei_dense_review_values.npz"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_kirchhoff_baseline"),
    )
    parser.add_argument("--dps", type=int, default=60)
    args = parser.parse_args()
    paths = generate_kirchhoff_review_grid_artifact(
        args.source,
        args.output_dir,
        dps=args.dps,
    )
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run focused tests and style checks**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_kirchhoff.py tests/unit/test_kirchhoff_artifact.py -q
.venv/bin/python -m ruff check src/schwgw/scattering/kirchhoff.py src/schwgw/io/kirchhoff.py scripts/phase5_generate_kirchhoff_baseline.py tests/unit/test_kirchhoff.py tests/unit/test_kirchhoff_artifact.py src/schwgw/scattering/__init__.py src/schwgw/io/__init__.py
```

Expected: all focused tests pass and Ruff reports no errors.

- [ ] **Step 6: Commit the artifact writer only**

Run:

```bash
git add src/schwgw/io/kirchhoff.py src/schwgw/io/__init__.py scripts/phase5_generate_kirchhoff_baseline.py tests/unit/test_kirchhoff_artifact.py
git diff --cached --check
git commit -m "feat: write Kirchhoff review-grid artifact"
```

Expected: the commit contains exactly those four paths.

### Task 4: Generate And Freshly Verify The Accepted 18x8 Artifact

**Files:**
- Read only: `runs/phase5/fig5_fig6_dense_review_grid/*`
- Create: `runs/phase5/fig5_fig6_kirchhoff_baseline/*`

- [ ] **Step 1: Reconfirm the accepted source hashes**

Run:

```bash
shasum -a 256 \
  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz \
  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json \
  runs/phase5/fig5_fig6_dense_review_grid/manifest.md
```

Expected hashes, in order:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
```

Stop YELLOW before generation if any hash differs.

- [ ] **Step 2: Generate the bounded baseline**

Run:

```bash
PYTHONPATH=src .venv/bin/python scripts/phase5_generate_kirchhoff_baseline.py --dps 60
```

Expected: exactly the NPZ, JSON, and manifest paths under
`runs/phase5/fig5_fig6_kirchhoff_baseline/` are printed.

- [ ] **Step 3: Run fresh artifact assertions**

Run:

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
import hashlib
import json
from pathlib import Path

import numpy as np

p = Path("runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz")
sidecar = Path(str(p) + ".json")
manifest = p.parent / "manifest.md"
assert p.exists() and sidecar.exists() and manifest.exists()
with np.load(p, allow_pickle=False) as data:
    assert data["kM_values"].shape == (18,)
    assert data["point_x"].shape == (8,)
    assert data["F_kirchhoff_complex"].shape == (18, 8)
    assert data["abs_F_kirchhoff"].shape == (18, 8)
    assert data["arg_F_kirchhoff_principal"].shape == (18, 8)
    assert data["arg_F_kirchhoff_unwrapped"].shape == (18, 8)
    assert data["valid_kirchhoff_mask"].all()
    assert np.isfinite(data["F_kirchhoff_complex"].real).all()
    assert np.isfinite(data["F_kirchhoff_complex"].imag).all()
    assert np.max(np.abs(data["eta_minus_paper"])) < 5.0e-5
meta = json.loads(sidecar.read_text(encoding="utf-8"))
for key in [
    "comparison_only", "not_denominator", "not_mask", "not_normalization",
    "polarization_independent", "no_solver_rerun", "no_plotting",
    "not_40_frequency_production", "no_fixtures", "no_paper_style_candidates",
]:
    assert meta[key] is True, key
sha = hashlib.sha256(p.read_bytes()).hexdigest()
assert meta["output_npz_sha256"] == sha
print("kirchhoff_artifact_fresh_checks_passed", sha)
PY
```

Expected: `kirchhoff_artifact_fresh_checks_passed` and the new NPZ SHA-256.

- [ ] **Step 4: Run the full relevant test suite because source code changed**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Expected: all tests pass. Any failure blocks GREEN even if it appears unrelated;
record the exact failure and determine whether it predates this slice before
choosing YELLOW or RED.

- [ ] **Step 5: Verify forbidden outputs and source mutation are absent**

Run:

```bash
find \
  runs/phase5/fig5_fig6_review_grid_plots \
  runs/phase5/fig5_fig6_dense_scan_production \
  runs/phase5/fig5_fig6_paper_style_candidates \
  -maxdepth 2 -type f -print 2>/dev/null | sort
git diff -- src/schwgw/scattering/transmission.py src/schwgw/numerics src/schwgw/viz configs tests/regression/fixtures
shasum -a 256 runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
```

Expected: the `find` and `git diff` commands produce no slice-created content;
the T8aj NPZ hash remains
`a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb`.

### Task 5: Record T8ak And Auto-Dispatch T7bs

**Files:**
- Modify: `status.md`
- Modify/archive as required: `docs/handoffs/T8_current.md`, `docs/handoffs/archive/T8_2026-07-14_pre_t8ak_kirchhoff_baseline.md`

- [ ] **Step 1: Record the exact scientific decision**

Use exactly one label:

```text
GREEN / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE GENERATED
YELLOW / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE PARTIAL
RED / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE BLOCKED
```

Record backend/version/dps, input and output hashes, eta mismatch maximum, test
counts, changed files, commands, non-claims, and any warnings. Archive the
pre-T8ak T8 handoff before replacing it because this is a new review boundary.

- [ ] **Step 2: Freshly verify the documentation after writing it**

Run:

```bash
rg -n "T8ak|KIRCHHOFF BASELINE|mpmath|dps|SHA256|T7bs|no plotting|40-frequency" status.md docs/handoffs/T8_current.md
git diff --check
git status --short
```

Expected: the exact decision and evidence are present with no whitespace
errors; unrelated existing worktree changes remain unstaged and untouched.

- [ ] **Step 3: Dispatch only on exact GREEN**

If and only if the exact T8ak decision is GREEN and all fresh checks pass, use
the Codex task messaging tool to send this message to T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` with model `gpt-5.6-sol` and thinking
`high`:

```text
你现在是 T7bs：Fig.5/Fig.6 review-grid Kirchhoff Eq. (47) scalar comparison-baseline 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bs_fig5_fig6_review_grid_kirchhoff_baseline_review.md。T8ak 已报告 exact GREEN；请先独立核验当前文件、hash、公式分支和 fresh tests，不得依赖 T8 的结论，不得修改实现或生成新 baseline/plots/dense-production。完成后按 prompt 更新 status/T7 handoff，并把 exact decision 发送给 T0 task 019f5ec5-84ba-79e2-8c77-1160b150a636。默认使用当前 5.6 Sol High；科学失败不得通过更换模型绕过。
```

Also send T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` the T8ak decision,
artifact paths/hashes, test result, and whether T7bs dispatch succeeded.

For YELLOW, RED, incomplete, missing artifacts, failed checks, or ambiguous
state: do not start T7bs. Send only the exact stop report to T0.

If task messaging is unavailable after a scientific GREEN, retain the GREEN
but report `auto-dispatch blocked` to T0; T0 will perform the already-authorized
dispatch. Do not create a new task.

## T7bs Review Boundary

T7bs follows the separate frozen prompt
`docs/prompts/phase5_t7bs_fig5_fig6_review_grid_kirchhoff_baseline_review.md`.
It must independently recompute all 144 values at higher precision, use the
Kummer transformation at high-risk corners, run the focused and full tests,
verify source isolation and hashes, and return one exact decision to T0. T7bs
must not repair code, generate plots, start dense production, or schedule a
later stage.

## Execution Route

The user explicitly selected execution in the existing T8 task followed by
automatic dispatch to the existing T7 task. This supersedes the generic
subagent-versus-inline choice in the planning workflow. T8 must use
`executing-plans` to execute this file task-by-task with checkpoints.
