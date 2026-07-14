# T4z Delta(kM)=0.1 Risk-Pilot Radial Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure and test the exact radial/Q018 transition envelope needed by the nine-frequency risk pilot, then add one fail-closed opt-in adapter for only that envelope.

**Architecture:** A deterministic script first classifies every requested `(kM, sector, ell, Table-I radius)` record and writes atomic per-frequency checkpoints. It validates the direct Q018 oracle for structured recoverable records and generates a small immutable Python envelope module. `radial_solver.py` consumes that exact module; no interpolation or general frequency broadening is allowed.

**Tech Stack:** Python 3.10+, NumPy, SciPy, existing mpmath-backed Q018 oracle, pytest, Ruff, JSON.

---

## Frozen File Map

Implementation commit paths are exactly:

```text
scripts/phase5_delta0p1_risk_radial_gate.py
src/schwgw/numerics/q018_delta0p1_risk_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

Generated/coordination paths are separate from that commit:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/
docs/phase5_delta0p1_risk_pilot_radial_gate.md
status.md
docs/handoffs/T4_current.md
docs/handoffs/archive/T4_2026-07-14_pre_t4z_delta0p1_risk_pilot.md
```

### Task 1: Freeze Constants And Establish TDD RED

**Files:**
- Modify: `tests/physics/test_q018_production_integration_design.py`
- Modify: `tests/physics/test_radial_solver.py`

- [ ] **Step 1: Add exact test constants**

```python
Q018_DELTA0P1_RISK_FREQUENCIES = (0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9)
Q018_DELTA0P1_RISK_ORACLE = "q018_tablei_delta0p1_risk_pilot_transition"
Q018_DELTA0P1_LMAX = {
    0.4: (24, 36, 60, 84), 0.8: (24, 36, 60, 84),
    0.9: (24, 36, 60, 84), 1.6: (72, 96, 120, 144),
    1.7: (84, 108, 132, 156), 2.8: (180, 204, 228, 252),
    2.9: (192, 216, 240, 264), 3.8: (276, 300, 324, 348),
    3.9: (288, 312, 336, 360),
}
```

- [ ] **Step 2: Add the RED unsupported-adapter test**

```python
def test_delta0p1_risk_adapter_name_is_supported() -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _tablei_review_grid_boundary_config(
        float(np.sqrt(25.0**2 + 30.0**2)),
        experimental_required_radius_oracle=Q018_DELTA0P1_RISK_ORACLE,
    )
    solution = solve_radial_mode(Sector.ODD, 190, 2.8, background, config)
    assert isinstance(solution, RadialSolution)
```

- [ ] **Step 3: Prove RED**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/physics/test_q018_production_integration_design.py::test_delta0p1_risk_adapter_name_is_supported
```

Expected: FAIL containing `unsupported experimental_required_radius_oracle`.

### Task 2: Build The Deterministic Classification Script

**Files:**
- Create: `scripts/phase5_delta0p1_risk_radial_gate.py`

- [ ] **Step 1: Define the exact contract**

```python
FREQUENCIES = (0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9)
LMAX_VALUES = {
    0.4: (24, 36, 60, 84), 0.8: (24, 36, 60, 84),
    0.9: (24, 36, 60, 84), 1.6: (72, 96, 120, 144),
    1.7: (84, 108, 132, 156), 2.8: (180, 204, 228, 252),
    2.9: (192, 216, 240, 264), 3.8: (276, 300, 324, 348),
    3.9: (288, 312, 336, 360),
}
BOUNDARY = {"r_out": 300.0, "r_in_eps": 1e-6, "rtol": 1e-10, "atol": 1e-12}
OUTPUT_DIR = Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate")
```

Import exact point IDs/radii from `schwgw.io.tablei.TABLEI_POINTS`; never copy rounded paper radii.

- [ ] **Step 2: Implement atomic writes and checkpoint matching**

```python
def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)

def _checkpoint_matches(payload: Mapping[str, Any], contract_sha256: str) -> bool:
    return (
        payload.get("schema_version") == "phase5_t4z_delta0p1_radial_checkpoint_v1"
        and payload.get("contract_sha256") == contract_sha256
        and payload.get("complete") is True
        and payload.get("decision") == "PASS"
    )
```

The contract hash covers the frequency, lmax map, exact points, boundary values, and selected source/script hashes. Quarantine mismatches; never reuse them.

- [ ] **Step 3: Implement default-path classification**

For every frequency, sector, integer `ell=2..max(LMAX_VALUES[kM])`, and point, call `solve_radial_mode` without an experimental oracle. Use only:

```python
DEFAULT_COVERED = "default_covered"
FAIL_UNCOVERED = "default_fail_closed_uncovered"
FAIL_SOLVER = "default_fail_closed_solver_failed"
FAIL_OTHER = "default_error_other"
```

Require `FAIL_OTHER == 0`; retain structured exception metadata without local tracebacks.

- [ ] **Step 4: Validate every structured transition with the direct oracle**

Use the exact frozen boundary values and `precision_dps=80`. Require finite `psi`, `dpsi_dr`, `A_in`, `A_out`, `abs(A_in-1)<1e-8`, effective residual `<1e-7`, and boundary/normalization residuals `<1e-8`. Repeat deterministic anchors at 70/80/100 dps and require maximum relative sensitivity `<5e-6`.

- [ ] **Step 5: Compress without interpolation**

Group only consecutive integer ells with identical exact point-ID sets at the same frequency. Emit `(ell_min, ell_max, point_ids)` and assert that expansion reproduces the raw transition-record set exactly.

- [ ] **Step 6: Check the script**

```bash
.venv/bin/python -m py_compile scripts/phase5_delta0p1_risk_radial_gate.py
.venv/bin/python -m ruff check scripts/phase5_delta0p1_risk_radial_gate.py
```

Expected: both pass.

### Task 3: Execute Classification And Generate The Envelope

**Files:**
- Generate: `runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/checkpoint/`
- Generate: `runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/classification_manifest.json`
- Generate: `runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/oracle_validation.json`
- Create: `src/schwgw/numerics/q018_delta0p1_risk_envelope.py`

- [ ] **Step 1: Freeze pre-run hashes**

```bash
shasum -a 256 src/schwgw/numerics/radial_solver.py src/schwgw/numerics/experimental/q018_rescaled_oracle.py src/schwgw/io/tablei.py scripts/phase5_delta0p1_risk_radial_gate.py
```

- [ ] **Step 2: Run in increasing frequency order**

```bash
PYTHONPATH=src .venv/bin/python scripts/phase5_delta0p1_risk_radial_gate.py
```

Expected: one atomic complete checkpoint per frequency. Re-running safely skips only exact matching checkpoints.

- [ ] **Step 3: Require the independent cardinality audit**

Verify nine checkpoints, two sectors, eight exact points, complete ell ranges, zero other errors, raw/compressed set identity, and oracle count equal to transition count. Print `T4Z_CLASSIFICATION_AND_ORACLE_AUDIT=PASS`.

- [ ] **Step 4: Generate the immutable envelope module**

It has this exact interface and literal data only:

```python
FREQUENCIES: tuple[float, ...]
POINTS: tuple[tuple[str, float], ...]
TRANSITION_SEGMENTS: dict[float, tuple[tuple[int, int, tuple[str, ...]], ...]]
CLASSIFICATION_SHA256: str
ORACLE_VALIDATION_SHA256: str
```

It must not load `runs/` at import time.

### Task 4: Integrate The Exact Adapter

**Files:**
- Modify: `src/schwgw/numerics/radial_solver.py`
- Modify: `tests/physics/test_q018_production_integration_design.py`
- Modify: `tests/physics/test_radial_solver.py`

- [ ] **Step 1: Add constants and support name**

```python
_Q018_DELTA0P1_RISK_ORACLE_NAME = "q018_tablei_delta0p1_risk_pilot_transition"
_Q018_DELTA0P1_RISK_ORACLE_SOLVER = "q018_tablei_delta0p1_risk_pilot_transition_oracle"
```

Import the generated envelope and add only this name to `_SUPPORTED_REQUIRED_RADIUS_ORACLE_NAMES`.

- [ ] **Step 2: Add a strict validator**

Mirror the existing T4y validator. Check exact background, `M`, sector, frequency, point radius, measured `(ell, point_id)` membership, `r_out`, `r_in_eps`, `rtol`, and `atol` using `_strict_float_equal`. Any mismatch raises structured `q018_experimental_oracle_out_of_envelope` with reasons.

- [ ] **Step 3: Add the recovery branch**

Use exact metadata:

```text
warning code = q018_tablei_delta0p1_risk_pilot_transition_oracle_used
review id = T4z/T7bv-pending
evidence = T4z complete measured Delta0p1 risk-pilot transition set
```

Default-covered modes stay on the ordinary path and emit no adapter warning.

- [ ] **Step 4: Add positive and negative tests**

Cover both sectors; every frequency with transitions; direct-oracle equality; default-covered modes; and rejection of wrong `M`, frequency, radius, `r_out`, tolerances, ell, and point membership.

- [ ] **Step 5: Run focused tests**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/physics/test_q018_production_integration_design.py tests/physics/test_radial_solver.py
```

Expected: all pass; only known fail-closed SciPy warnings are allowed.

### Task 5: Fresh Verification, Commit, And Handoff

**Files:**
- Generate: `runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/resume_preflight.json`
- Generate: `runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/manifest.md`
- Create: `docs/phase5_delta0p1_risk_pilot_radial_gate.md`
- Modify: `status.md`
- Modify: `docs/handoffs/T4_current.md`
- Create: `docs/handoffs/archive/T4_2026-07-14_pre_t4z_delta0p1_risk_pilot.md`

- [ ] **Step 1: Re-run every transition through the adapter**

Compare with direct-oracle records; require finite fields, residual bounds, exact warning/point/adapter identities. Write `resume_preflight.json` atomically.

- [ ] **Step 2: Run Ruff and the full suite**

```bash
.venv/bin/python -m ruff check scripts/phase5_delta0p1_risk_radial_gate.py src/schwgw/numerics/q018_delta0p1_risk_envelope.py src/schwgw/numerics/radial_solver.py tests/physics/test_q018_production_integration_design.py tests/physics/test_radial_solver.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

- [ ] **Step 3: Require forbidden-output and scope checks**

```bash
find runs/phase5/fig5_fig6_delta0p1_risk_pilot runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
git diff --name-only -- src tests scripts
```

Expected: `find` is empty and the diff has exactly the five frozen implementation paths.

- [ ] **Step 4: Commit exactly the five implementation paths**

```bash
git add scripts/phase5_delta0p1_risk_radial_gate.py src/schwgw/numerics/q018_delta0p1_risk_envelope.py src/schwgw/numerics/radial_solver.py tests/physics/test_q018_production_integration_design.py tests/physics/test_radial_solver.py
git diff --cached --name-only
git diff --cached --check
git commit -m "feat: add delta0p1 risk-pilot radial gate"
```

- [ ] **Step 5: Archive/update handoff and record one decision**

```text
GREEN / DELTA0P1 RISK-PILOT RADIAL GATE READY
YELLOW / DELTA0P1 RISK-PILOT RADIAL GATE PARTIAL
RED / DELTA0P1 RISK-PILOT RADIAL GATE BLOCKED
```

Only exact GREEN may dispatch frozen T7bv. Do not run T8an, push GitHub, or start later work.
