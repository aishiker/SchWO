# T8an Delta(kM)=0.1 Nine-Frequency Risk Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate nine new, point-only, resumable Table-I amplification frequencies that directly test the accepted high-risk sampling intervals at spacing no larger than Delta(kM)=0.1.

**Architecture:** A focused IO module owns the frozen pilot contract, frequency-local domain-aware radial cache, atomic frequency artifacts, checkpoint ledger, aggregation, and sampling audit. A thin script invokes the module. The accepted T8aj artifact is immutable and supplies hash-verified interval endpoints only.

**Tech Stack:** Python 3.10+, NumPy, existing SchWO Route-B solver and T7bv-accepted Q018 adapter, JSON/NPZ, pytest, Ruff.

---

## Frozen File Map

Implementation commit paths are exactly:

```text
src/schwgw/io/tablei_risk_pilot.py
src/schwgw/io/__init__.py
scripts/phase5_run_delta0p1_risk_pilot.py
tests/unit/test_tablei_risk_pilot.py
tests/regression/test_delta0p1_risk_pilot_script.py
```

Generated/coordination paths are separate:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot/
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-14_pre_t8an_delta0p1_risk_pilot.md
```

### Task 1: Define The Contract With TDD RED

**Files:**
- Create: `tests/unit/test_tablei_risk_pilot.py`
- Create: `tests/regression/test_delta0p1_risk_pilot_script.py`

- [ ] **Step 1: Write import and frozen-constant tests**

```python
from schwgw.io.tablei_risk_pilot import (
    PILOT_FREQUENCIES,
    PILOT_LMAX_VALUES,
    PilotContractError,
    run_delta0p1_risk_pilot,
)

def test_frozen_pilot_contract() -> None:
    assert PILOT_FREQUENCIES == (0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9)
    assert PILOT_LMAX_VALUES[3.9] == (288, 312, 336, 360)
```

- [ ] **Step 2: Write resume/failure tests with fake solvers**

Cover exact skip of a complete frequency, quarantine on source-hash mismatch, rejection of `.tmp` as complete, final-pair failure, unexpected-file failure, and missing T7bv GREEN failure.

- [ ] **Step 3: Prove RED**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/unit/test_tablei_risk_pilot.py tests/regression/test_delta0p1_risk_pilot_script.py
```

Expected: collection fails because `schwgw.io.tablei_risk_pilot` is absent.

### Task 2: Implement Contract, Hashes, And Atomic Transactions

**Files:**
- Create: `src/schwgw/io/tablei_risk_pilot.py`
- Modify: `src/schwgw/io/__init__.py`

- [ ] **Step 1: Add constants and exception**

```python
PILOT_FREQUENCIES = (0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9)
PILOT_LMAX_VALUES = {
    0.4: (24, 36, 60, 84), 0.8: (24, 36, 60, 84),
    0.9: (24, 36, 60, 84), 1.6: (72, 96, 120, 144),
    1.7: (84, 108, 132, 156), 2.8: (180, 204, 228, 252),
    2.9: (192, 216, 240, 264), 3.8: (276, 300, 324, 348),
    3.9: (288, 312, 336, 360),
}
ADAPTER_NAME = "q018_tablei_delta0p1_risk_pilot_transition"
CONVERGENCE_TOLERANCE = 1e-4

class PilotContractError(ValueError):
    pass
```

- [ ] **Step 2: Hash the complete contract deterministically**

Use sorted compact JSON and SHA256. Include exact points, frequencies, lmax windows, boundary values, amplitudes, adapter, T8aj triplet hashes, and T4z/T7bv gate hashes.

- [ ] **Step 3: Add atomic JSON/NPZ writers**

Write to a sibling `.tmp`, close, hash, and replace. Never write into the T8aj directory. Allow only `frequencies/`, `quarantine/`, ledger, aggregate, audit, and manifest names.

- [ ] **Step 4: Implement exact resume validation**

A frequency is complete only when its NPZ/JSON hashes, ledger entry, contract hash, adapter, points, lmax window, and all source/gate hashes agree. Quarantine mismatched pairs and recompute only that frequency.

### Task 3: Implement Safe Domain-Aware Radial Reuse

**Files:**
- Modify: `src/schwgw/io/tablei_risk_pilot.py`
- Modify: `tests/unit/test_tablei_risk_pilot.py`

- [ ] **Step 1: Add a frequency-local cache key without requested radius**

The key includes sector, ell, k, background, `r_out`, `r_in_eps`, `rtol`, `atol`, and adapter. Cache entries retain the solution and certified upper radius.

- [ ] **Step 2: Reuse only certified domains**

```python
def _covers(solution: Any, required_radius: float) -> bool:
    upper = solution.r_grid[-1] if solution.valid_until_r is None else solution.valid_until_r
    return float(required_radius) <= float(upper)
```

Process Table-I points in decreasing radius. Reuse only when `_covers` is true. A new solution replaces an old entry only if its certified domain is no smaller. Record solve/reuse counts.

- [ ] **Step 3: Test the safety boundary**

With fake solutions, prove a far solution serves nearer points, a near-only solution never serves farther points, and keys change with adapter or tolerances.

### Task 4: Compute One Frequency Transaction

**Files:**
- Modify: `src/schwgw/io/tablei_risk_pilot.py`
- Modify: `tests/unit/test_tablei_risk_pilot.py`

- [ ] **Step 1: Use exact point geometry**

Read `TABLEI_POINTS`; use `r=point.r`, `theta=atan2(point.x, point.z)`, `phi=0`. Do not use rounded paper radii/angles.

- [ ] **Step 2: Compute Route-B lensed and flat fields**

For each lmax/point call `compute_polarization` with the T7bv adapter and cache, and `compute_flat_no_lens_polarization` with the same parameters. Form independent plus/cross masks and the same lensed/unlensed complex ratios as T8aj.

- [ ] **Step 3: Check the final adjacent pair**

```python
delta = abs(final - previous) / np.maximum(1.0, np.maximum(abs(final), abs(previous)))
pass_mask = delta <= 1e-4
```

Require both components at all eight points. One `+24` or `+48` extension is allowed only when all new modes are inside the accepted radial envelope; otherwise stop with exact failure metadata.

- [ ] **Step 4: Write the transaction**

NPZ includes exact point geometry, final complex ratios, magnitudes, principal phases, masks, lmax history, and deltas. JSON includes runtime, cache counts, warnings, adapter counts, source/gate hashes, git state, checkpoint provenance, and frozen non-claims.

- [ ] **Step 5: Run unit tests**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/unit/test_tablei_risk_pilot.py
```

Expected: all fake-solver tests pass; no real pilot executes.

### Task 5: Aggregate And Produce Sampling Audit Data

**Files:**
- Modify: `src/schwgw/io/tablei_risk_pilot.py`

- [ ] **Step 1: Require exactly nine valid transactions**

Reject missing, duplicate, extra, or mismatched frequency files. Aggregate shape is exactly `(9,8)`.

- [ ] **Step 2: Load T8aj endpoints read-only**

Require exact hashes:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
```

- [ ] **Step 3: Build exactly five local sequences**

```text
[0.3,0.4,0.5]
[0.75,0.8,0.9,1.0]
[1.5,1.6,1.7,1.75]
[2.75,2.8,2.9,3.0]
[3.75,3.8,3.9,4.0]
```

For every point/component record complex, magnitude, scale-normalized magnitude, and unwrapped-phase steps, total variation, interior extrema, and maxima attribution. Do not emit an acceptance decision; T7bw decides independently.

- [ ] **Step 4: Write aggregate, audit, ledger, and manifest**

Required names:

```text
frequencies/kM_<token>.npz
frequencies/kM_<token>.npz.json
checkpoint_ledger.json
risk_pilot_values.npz
risk_pilot_values.npz.json
risk_pilot_sampling_audit.json
manifest.md
```

The manifest hashes every file and states `not 40-frequency production`.

### Task 6: Add The Thin Script And Regression Coverage

**Files:**
- Create: `scripts/phase5_run_delta0p1_risk_pilot.py`
- Modify: `tests/regression/test_delta0p1_risk_pilot_script.py`

- [ ] **Step 1: Add arguments**

```text
--output-dir
--accepted-review-npz
--radial-gate-dir
--resume
```

Defaults are the frozen project paths. The script calls only `run_delta0p1_risk_pilot` and exits nonzero on a contract error.

- [ ] **Step 2: Test script scope**

Use injected fake compute functions. Require exact outputs, resume behavior, unexpected-file rejection, and no Kirchhoff/visualization imports or calls.

- [ ] **Step 3: Run focused checks**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/unit/test_tablei_risk_pilot.py tests/regression/test_delta0p1_risk_pilot_script.py
.venv/bin/python -m ruff check src/schwgw/io/tablei_risk_pilot.py src/schwgw/io/__init__.py scripts/phase5_run_delta0p1_risk_pilot.py tests/unit/test_tablei_risk_pilot.py tests/regression/test_delta0p1_risk_pilot_script.py
```

Expected: all pass and Ruff clean.

### Task 7: Execute The Background Pilot

**Files:**
- Generate: `runs/phase5/fig5_fig6_delta0p1_risk_pilot/`

- [ ] **Step 1: Require T7bv exact GREEN and matching hashes**

Do not start without `ACCEPT GREEN / DELTA0P1 RISK-PILOT RADIAL GATE ACCEPTED`.

- [ ] **Step 2: Run with resume enabled**

```bash
PYTHONPATH=src .venv/bin/python scripts/phase5_run_delta0p1_risk_pilot.py --resume
```

Run in increasing frequency order and checkpoint after each. Healthy work may exceed the four-hour soft budget. A capacity/system resume reruns this command and reuses only verified transactions.

- [ ] **Step 3: Perform a direct artifact audit**

Load each frequency pair directly and verify frequency/point arrays, shapes, dtypes, finiteness, masks, final pairs, hashes, warning metadata, ledger, aggregate equality, and no extra files. Print `T8AN_NINE_FREQUENCY_ARTIFACT_AUDIT=PASS`.

### Task 8: Full Verification, Commit, And Handoff

**Files:**
- Modify: `status.md`
- Modify: `docs/handoffs/T8_current.md`
- Create: `docs/handoffs/archive/T8_2026-07-14_pre_t8an_delta0p1_risk_pilot.md`

- [ ] **Step 1: Run fresh checks**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/unit/test_tablei_risk_pilot.py tests/regression/test_delta0p1_risk_pilot_script.py
.venv/bin/python -m ruff check src/schwgw/io/tablei_risk_pilot.py src/schwgw/io/__init__.py scripts/phase5_run_delta0p1_risk_pilot.py tests/unit/test_tablei_risk_pilot.py tests/regression/test_delta0p1_risk_pilot_script.py
PYTHONPATH=src .venv/bin/python -m pytest -q
find runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
```

Expected: tests pass, Ruff is clean, and forbidden-output search is empty.

- [ ] **Step 2: Commit exactly the five implementation paths**

```bash
git add src/schwgw/io/tablei_risk_pilot.py src/schwgw/io/__init__.py scripts/phase5_run_delta0p1_risk_pilot.py tests/unit/test_tablei_risk_pilot.py tests/regression/test_delta0p1_risk_pilot_script.py
git diff --cached --name-only
git diff --cached --check
git commit -m "feat: add delta0p1 nine-frequency risk pilot"
```

- [ ] **Step 3: Archive/update handoff and record one decision**

```text
GREEN / DELTA0P1 NINE-FREQUENCY RISK PILOT GENERATED
YELLOW / DELTA0P1 NINE-FREQUENCY RISK PILOT PARTIAL
RED / DELTA0P1 NINE-FREQUENCY RISK PILOT BLOCKED
```

Only exact GREEN may dispatch frozen T7bw. Do not start full-grid completion, `0.05` scans, plots, fixtures, or GitHub actions.
