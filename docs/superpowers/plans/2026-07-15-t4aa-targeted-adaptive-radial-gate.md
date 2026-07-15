# T4aa Targeted Adaptive Radial/Q018 Gate Implementation Plan

Date: 2026-07-15

## Goal

Measure the complete radial/Q018 support required by the thirteen frozen
targeted-adaptive frequencies, validate every structured transition against
the direct oracle, and add one exact fail-closed adapter that contains only
the measured `(kM, sector, ell, point_id)` envelope.

This is a radial gate only. It must not compute amplification factors, sampling
metrics, plots, fixtures, Kirchhoff data, or a production frequency grid.

## Frozen Inputs

```text
frequencies = [
  0.35, 0.45, 0.85, 0.95, 1.55, 1.65, 1.725,
  2.775, 2.85, 2.95, 3.775, 3.85, 3.95,
]
sectors = [odd, even]
points = exact eight TABLEI_POINTS
M = 1
r_out = 300
r_in_eps = 1e-6
rtol = 1e-10
atol = 1e-12
```

Exact lmax windows:

```text
0.35  [24,36,60,84]
0.45  [24,36,60,84]
0.85  [24,36,60,84]
0.95  [24,48,72,96]
1.55  [72,96,120,144]
1.65  [84,108,132,156]
1.725 [84,108,132,156]
2.775 [180,204,228,252]
2.85  [192,216,240,264]
2.95  [204,228,252,276]
3.775 [276,300,324,348]
3.85  [276,300,324,348]
3.95  [288,312,336,360]
```

The independently derived default-classification cardinality is exactly
`42,224` records: for every frequency, both sectors, every integer
`ell=2..max(lmax_values)`, and all eight exact points. Transition cardinality
is measured, not assumed.

## Frozen File Map

The implementation commit may contain exactly:

```text
scripts/phase5_targeted_adaptive_radial_gate.py
src/schwgw/numerics/q018_targeted_adaptive_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

Additional generated/coordination writes are limited to:

```text
runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/
docs/phase5_targeted_adaptive_radial_gate.md
status.md
docs/handoffs/T4_current.md
docs/handoffs/archive/T4_2026-07-15_pre_t4aa_targeted_adaptive_radial_gate.md
```

Preserve and exclude unrelated T1/T2/T3/T5/T6 working-tree changes.

## Task 1 — Preflight And TDD RED

- [ ] Read the frozen design, this plan, both T4aa/T7by prompts, current T0/T4/T7
      handoffs, the T4z gate note/artifacts, `radial_solver.py`, existing Q018
      envelope modules, and the two frozen test modules.
- [ ] Freshly hash the five accepted T8ao root artifacts, the T8aj triplet, and
      the T4z classification/oracle/preflight files. Stop on any mismatch.
- [ ] Record the exact source blobs for `radial_solver.py`, the direct oracle,
      Table-I points, this plan, design, and T4aa prompt in the new contract.
- [ ] Add tests for the thirteen exact frequency tokens, lmax windows, adapter
      name, strict boundary values, and expected `42,224` classification rows.
- [ ] Add a test demonstrating that
      `q018_tablei_targeted_adaptive_transition` is initially unsupported.
- [ ] Run the single test and capture the expected fail-closed RED. Any other
      failure must be diagnosed before continuing.

## Task 2 — Deterministic Classification And Atomic Checkpoints

- [ ] Implement `scripts/phase5_targeted_adaptive_radial_gate.py` with literal
      frequency/token/lmax data from the design and exact `TABLEI_POINTS`.
- [ ] Use only these default classifications:

```text
default_covered
default_fail_closed_uncovered
default_fail_closed_solver_failed
default_error_other
```

- [ ] Require `default_error_other == 0`; record structured exceptions without
      hiding nonfinite or unexpected failures.
- [ ] Write exactly thirteen atomic files
      `checkpoint/kM_<token>.json`. A checkpoint is reusable only if schema,
      complete input contract, selected source hashes, output hash,
      `complete=true`, and `decision=PASS` all match. Quarantine any mismatch.
- [ ] On resume, independently validate a matching checkpoint before skipping
      its frequency. Never trust filename presence alone.
- [ ] Require a complete `42,224`-record union with no duplicate or omitted
      key before generating an envelope.

## Task 3 — Direct Oracle Evidence And Literal Envelope

- [ ] Validate every structured recoverable transition with the existing
      direct Riccati/log-amplitude oracle using the frozen boundary values.
- [ ] Record requested precision and actual backend precision separately.
- [ ] Require finite `psi`, `dpsi_dr`, `A_in`, `A_out`, normalization and
      boundary consistency, effective residual `<1e-7`, normalization/boundary
      residuals `<1e-8`, and maximum tolerance sensitivity `<5e-6`.
- [ ] Repeat a deterministic cross-frequency/cross-sector/cross-radius anchor
      matrix at requested 70/80/100 dps and with frozen tolerance perturbations.
- [ ] Compress only consecutive integer ells that have identical exact point
      sets at the same frequency and sector. Expand the generated segments and
      require exact set equality with all raw transition keys.
- [ ] Generate a literal, import-time IO-free module
      `q018_targeted_adaptive_envelope.py` carrying frequency tokens, exact
      points, transition segments, source hashes, classification hash, and
      oracle-validation hash.

## Task 4 — Exact Fail-Closed Adapter

- [ ] Add only the adapter name
      `q018_tablei_targeted_adaptive_transition` to `radial_solver.py`.
- [ ] Validate exact Schwarzschild background, `M`, sector, binary64 frequency,
      point radius/ID, literal `(ell, point_id)` membership, `r_out`,
      `r_in_eps`, `rtol`, and `atol` with the existing strict comparison
      convention (`rtol=0`, `atol=1e-15` where applicable).
- [ ] Keep default-covered records on the ordinary solver path with zero
      adapter calls and no adapter warning.
- [ ] Use structured warning
      `q018_tablei_targeted_adaptive_transition_oracle_used` only for measured
      recoverable transitions.
- [ ] Add positive tests across all thirteen frequencies, both sectors and all
      transition point groups; add negative tests for every wrong contract
      field, unmeasured ell/point pairs, and near-but-not-exact frequencies.
- [ ] Compare adapter results directly with the saved oracle records.

## Task 5 — Resume Preflight, Evidence And Verification

- [ ] Re-run every transition through the integrated adapter without calling
      the classification compressor and write `resume_preflight.json`
      atomically. Require exact key equality, finite fields, frozen residual
      bounds, adapter identity, warning identity, and zero failures.
- [ ] Write only:

```text
classification_manifest.json
oracle_validation.json
resume_preflight.json
checkpoint/kM_<token>.json  # exactly thirteen
manifest.md
```

- [ ] Produce `docs/phase5_targeted_adaptive_radial_gate.md` with counts,
      hashes, backend qualification, maxima, runtimes, limitations, and exact
      non-claims.
- [ ] Run focused tests:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/physics/test_q018_production_integration_design.py \
  tests/physics/test_radial_solver.py
```

- [ ] Run Ruff on the exact five implementation paths and then fresh full
      pytest with `PYTHONPATH=src .venv/bin/python -m pytest -q`.
- [ ] Require the implementation diff path set to equal the frozen five paths,
      `git diff --check` to pass, exactly thirteen complete checkpoints, no
      active `.tmp`, no ambiguous quarantine state, and no T8ap/full-grid/
      `0.025`-scan/plot/fixture/Kirchhoff/paper output.
- [ ] Commit exactly the five implementation/test paths. Do not include run
      products or unrelated handoffs.
- [ ] Archive the predecessor T4 handoff, update T4 current and `status.md`, and
      record exactly one decision:

```text
GREEN / TARGETED ADAPTIVE RADIAL GATE READY
YELLOW / TARGETED ADAPTIVE RADIAL GATE PARTIAL
RED / TARGETED ADAPTIVE RADIAL GATE BLOCKED
```

## Dispatch And Stop Rules

Only exact GREEN with fresh artifact/test/scope verification may dispatch the
frozen T7by prompt to the existing T7 task. T4aa must notify T0 with the exact
decision, commit, thirteen checkpoint hashes, classification/oracle/preflight
hashes, counts, maxima, backend precision, runtimes, tests, and dispatch state.

Stop YELLOW/RED on any source mismatch, incomplete cardinality, unstructured
error, nonfinite oracle value, residual/sensitivity failure, checkpoint or
resume ambiguity, scope drift, test/Ruff failure, or forbidden output. Do not
relax thresholds, omit modes/points/frequencies, interpolate the envelope,
broaden another adapter, run T8ap, or push GitHub.

## Definition Of Done

- all `42,224` classification records and thirteen atomic checkpoints exist;
- every transition is independently oracle-validated and exactly represented
  by the literal envelope;
- strict adapter positive/negative/default-path tests pass;
- focused tests, Ruff, full pytest, scope, provenance, resume, and isolation
  checks pass fresh;
- one exact decision, coordination records, and downstream dispatch state are
  complete without any observable artifact.
