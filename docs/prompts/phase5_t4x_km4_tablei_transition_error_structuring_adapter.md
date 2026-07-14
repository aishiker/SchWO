# Phase 5 T4x Prompt: kM=4 Table-I Transition Error Structuring And Adapter Gate

You are T4x: radial-method/error-structuring and narrow production-adapter
gate for the `kM=4` Table-I Fig.5/Fig.6 transition modes.

Use Goal mode.

Goal objective:

```text
Resolve the T12 Stage 1 blocker at kM=4, required_eval_radius=39.051248M,
ell=177 odd/even without weakening radial/Q018 policy.  First make the raw
bidirectional SVD failure structured and test-covered.  Then rerun the full
continuous default classification.  Only if that classification is clean and
the direct Riccati/log-derivative oracle validates the complete measured
transition set, implement a narrow opt-in kM=4 Table-I adapter envelope.
Stop YELLOW rather than starting T8 or bypassing any physics/numerics gate.
```

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T0_current.md`
6. `docs/handoffs/T4_current.md`
7. `docs/handoffs/T7_current.md`
8. `docs/handoffs/T12_current.md`
9. `docs/phase5_km4_tablei_adapter_closeout.md`
10. `runs/phase5/km4_tablei_adapter_validation/stage1_yellow_blocker_metadata.json`
11. `docs/phase5_km4_tablei_radial_q018_preflight.md`
12. `docs/phase5_km4_tablei_transition_oracle_probe.md`
13. `runs/phase5/km4_tablei_radial_q018_preflight/radial_q018_preflight_metadata.json`
14. `runs/phase5/km4_tablei_transition_oracle_probe/transition_oracle_probe_metadata.json`
15. `docs/numerics.md`
16. `docs/validation_plan.md`
17. `src/schwgw/numerics/radial_solver.py`
18. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
19. relevant tests under `tests/physics/`, `tests/unit/`, and `tests/regression/`.

Before editing, check installed plugins/skills.  Use `systematic-debugging`
for the blocker, `test-driven-development` for source changes, and
`verification-before-completion` before claiming any pass.

## Hard Rules

- Do not start T8, plotting, Kirchhoff implementation, dense Fig.5/Fig.6
  production, fixtures, or any paper-style figure generation.
- Do not lower `lmax`, relax thresholds, weaken convergence checks, change
  frozen Fourier/harmonic/tetrad/RW/Zerilli/Route-B conventions, or alter the
  physical meaning of Q018 fail-closed policy.
- Do not silently catch numerical errors and continue with invalid data.
- Any raw `numpy.linalg.LinAlgError` in the bidirectional fallback must become
  either a tested structured radial no-go or a tested recoverable path with
  finite diagnostics.
- Preserve the existing R60_K2 `q018_riccati` envelope unless a test proves it
  is unchanged.
- If three focused repair attempts hit the same blocker, stop YELLOW and
  document the blocker.

## Stage A: Reproduce And Localize The T12 Blocker

Reproduce the T12 blocker with:

```text
M=1
k=4
required_eval_radius=39.051248
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
ell=177
sector=odd/even
default no-oracle production path
```

Confirm whether the raw failure occurs in:

- `np.linalg.solve(match_matrix, incoming_match)`;
- `np.linalg.cond(match_matrix)`;
- residual/jump computation after a solve;
- or another bidirectional fallback boundary.

Record the match radius, finite/non-finite entries, determinant scale if
available, condition-number behavior if computable, and barrier action.

## Stage B: TDD For Structured Bidirectional Linear-Algebra Failure

Before changing production code, add the smallest focused test that fails on
the current raw `LinAlgError` leak for the reproduced `ell=177` default path.

Acceptable target behavior:

- preferred: the default path returns the existing structured
  `evanescent_tail_required_radius_uncovered` no-go when the certified
  zero-tail domain does not cover `required_eval_radius`;
- or, if the default bidirectional path can be made genuinely finite without
  changing thresholds, it must return a normal finite `RadialSolution` with
  all existing diagnostics finite and passing existing thresholds.

Unacceptable target behavior:

- raw `LinAlgError` leaks to callers;
- fake covered result with zero/NaN/inf fields;
- threshold relaxation;
- using the experimental oracle without explicit opt-in.

Implement the smallest source change needed, likely by wrapping the
bidirectional match linear algebra and converting `LinAlgError`/non-finite
match diagnostics into a structured fallback failure that the existing
evanescent-tail/Q018 required-radius path can handle.

## Stage C: Continuous Default Classification

After Stage B passes targeted tests, rerun the full default no-oracle
classification for:

```text
kM=4
ell=2..360
sector=odd/even
required_eval_radius=39.051248
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
```

Write metadata to:

```text
runs/phase5/km4_tablei_adapter_validation/t4x_default_classification_metadata.json
```

The metadata must include:

- parameters;
- counts by classification;
- exact `ell,sector` list for default covered modes;
- exact `ell,sector` list for structured required-radius uncovered modes;
- exact list of any other errors;
- runtime summary;
- source SHA or, if no git repo exists, a deterministic source file hash list.

Stop YELLOW if `default_error_other` is nonzero.

## Stage D: Direct Oracle Validation For The Complete Measured Transition Set

Only if Stage C has no other errors, validate the direct Riccati/log-derivative
oracle for the complete measured transition set that requires adapter support.
Do not assume the set is only `ell=177,178,180,204,228,240`; use the measured
Stage C list.

For each measured `ell,sector`, record:

- finite `psi`;
- finite `dpsi_dr`;
- finite `A_in`;
- finite `A_out`;
- `abs(A_in - 1)`;
- outer-boundary residual;
- normalization residual;
- log-derivative match residual;
- repeat stability;
- loose/tight sensitivity if runtime permits.

Write metadata to:

```text
runs/phase5/km4_tablei_adapter_validation/t4x_oracle_validation_metadata.json
```

Stop YELLOW if any oracle result is non-finite or fails existing residual or
stability thresholds.  Do not tune thresholds.

## Stage E: Narrow Opt-In Adapter Implementation

Only if Stages C and D pass, implement a narrow explicit opt-in production
adapter envelope for the validated `kM=4` Table-I transition set.

Use a separate name from the old R60_K2 envelope, for example:

```text
experimental_required_radius_oracle="q018_tablei_km4_transition"
```

The new envelope must be exact and fail-closed:

```text
background = Schwarzschild
M = 1
k = 4
required_eval_radius = 39.051248
r_out = 300
r_in_eps = 1e-6
rtol = 1e-10
atol = 1e-12
ell,sector = exactly the Stage C/D validated transition set
```

Required tests:

- old `q018_riccati` R60_K2 envelope behavior is unchanged;
- unknown oracle names fail closed;
- the new opt-in envelope rejects out-of-envelope `M`, `k`, `r_out`,
  `required_eval_radius`, tolerances, `ell`, and sector;
- ordinary default-covered modes still use the ordinary production path;
- in-envelope `ell,sector` modes use the new adapter and return finite fields
  at the required radius;
- metadata/warnings clearly identify the adapter as reviewed opt-in and
  limited to the Table-I transition envelope.

## Verification

At minimum run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If the full suite is too slow, first run the targeted suite above, document why
full pytest was deferred, and keep the decision YELLOW rather than GREEN.

## Required Outputs

Update or create:

- `docs/phase5_km4_tablei_transition_error_structuring_adapter.md`
- `runs/phase5/km4_tablei_adapter_validation/t4x_default_classification_metadata.json`
- `runs/phase5/km4_tablei_adapter_validation/t4x_oracle_validation_metadata.json`
- `docs/handoffs/T4_current.md`
- `status.md`

If source/tests changed, list every changed file in `status.md`.

## Decision Labels

Use exactly one:

```text
GREEN / KM4 TABLE-I TRANSITION ERROR STRUCTURED AND ADAPTER IMPLEMENTED
YELLOW / KM4 TABLE-I TRANSITION BLOCKER STRUCTURED BUT ADAPTER NOT READY
RED / KM4 TABLE-I TRANSITION RADIAL METHOD UNSOUND
```

GREEN requires:

- no raw `LinAlgError` leak for the reproduced blocker;
- full default classification has no `default_error_other`;
- complete measured transition set has passing direct-oracle validation;
- narrow opt-in adapter implemented with tests;
- full pytest passes or a clearly justified targeted substitute passes with
  no source-risk left untested;
- no T8/plot/Kirchhoff/dense artifact generated.

