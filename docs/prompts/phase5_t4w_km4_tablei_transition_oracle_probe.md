# Phase 5 T4w Prompt: kM=4 Table-I Transition-Band Oracle Probe

You are T4w: radial/Q018 method followup.

Use Goal mode for this task.

Goal objective:

```text
Probe whether the existing experimental Riccati/log-derivative oracle can stably cover the kM=4 Table-I transition-band modes that failed T4v, without changing production behavior or generating dense production artifacts.
```

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T4_current.md`
6. `docs/handoffs/T7_current.md`
7. `docs/numerics.md`
8. `docs/validation_plan.md`
9. `docs/phase5_km4_tablei_radial_q018_preflight.md`
10. `runs/phase5/km4_tablei_radial_q018_preflight/radial_q018_preflight_metadata.json`
11. `references/notes/q018_spin2_tail_bound.md`
12. `references/notes/q018_scalar_partial_wave_cutoff.md`
13. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
14. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
15. `src/schwgw/numerics/radial_solver.py`
16. `tests/physics/test_q018_rescaled_oracle.py`
17. `tests/physics/test_q018_production_integration_design.py`
18. `tests/physics/test_radial_solver.py`

Before starting, check installed plugins/skills.  This is a numerical blocker:
use `systematic-debugging` and `verification-before-completion`.

## Problem Statement

T7bn accepted T1j but blocked T8 because T4v found uncovered `kM=4`
transition-band branches:

```text
required_eval_radius = 39.051248M
kM = 4
sector = odd/even
ell = 178, 180, 204, 228, 240
error code = evanescent_tail_required_radius_uncovered
```

The current production adapter for `q018_riccati` is reviewed only for
`k=2`, `required_eval_radius=60`, `r_out=300`, and `ell=153..180`.
Do not expand that adapter in this task.

## Scope

This is an experimental method probe only.

Allowed updates:

- `docs/phase5_km4_tablei_transition_oracle_probe.md`
- optional metadata-only JSON under
  `runs/phase5/km4_tablei_transition_oracle_probe/`
- `status.md`
- `docs/handoffs/T4_current.md`

Forbidden:

- Do not modify `src/`, tests, configs, accepted artifacts, plotting code, or
  production adapter envelope.
- Do not change thresholds, `lmax`, boundary policy, Q018 policy, physics
  conventions, or Kirchhoff policy.
- Do not run T8, field maps, pointwise amplification, dense scan production,
  40-frequency scans, fixtures, plots, NPZ/HDF5 production outputs, or
  Kirchhoff implementation.
- Do not make `q018_riccati` production-ready for `kM=4` in this slice.

## Required Probe Matrix

Use `SchwarzschildBackground(M=1)` and direct calls to the experimental oracle:

```python
RescaledOracleRequest(
    sector=sector,
    ell=ell,
    k=4.0,
    required_radius=39.051248,
    r_out=300.0,
    r_in_eps=1e-6,
    rtol=1e-10,
    atol=1e-12,
    precision_dps=80,
    method_hint="rescaled_log_amplitude",
)
```

Required core matrix:

```text
ell = [178, 180, 204, 228, 240]
sector = [odd, even]
```

Add context probes if runtime allows:

```text
ell = [169, 241, 252, 300, 360]
sector = [odd, even]
```

The context probes should compare ordinary successful branches versus the
transition-band oracle behavior.  They are not a substitute for the core matrix.

## Required Diagnostics

For every probe record:

- `kM`, `ell`, `sector`;
- required radius and `r_out`;
- success/error status;
- finite flags for `psi`, `dpsi_dr`, `A_in`, `A_out`;
- `abs(A_in-1)`;
- `outer_boundary_residual`;
- `normalization_residual`;
- `log_derivative_match_residual`;
- `match_condition_number`;
- `riccati_steps`, `outward_steps`, `runtime_seconds`;
- repeat-call relative differences for `psi`, `dpsi_dr`, and `A_out`;
- sensitivity check for at least one tolerance variation for each core mode if
  runtime allows:
  - baseline `rtol=1e-10, atol=1e-12`;
  - loose `rtol=1e-9, atol=1e-11`;
  - tight `rtol=1e-11, atol=1e-13`.

If full sensitivity over all core modes is too slow, run it at minimum for:

```text
(odd, 178), (even, 178), (odd, 240), (even, 240)
```

## Decision Labels

Use exactly one in `docs/phase5_km4_tablei_transition_oracle_probe.md`:

```text
GREEN / KM4 TABLE-I TRANSITION ORACLE PROBE PASSED
YELLOW / KM4 TABLE-I ORACLE PROBE PARTIAL WITH NAMED LIMITS
YELLOW / KM4 TABLE-I ORACLE PROBE NEEDS NEW RADIAL METHOD
RED / KM4 TABLE-I ORACLE PROBE FAILED
```

GREEN requires:

- every core mode returns finite `psi`, `dpsi_dr`, `A_in`, `A_out`;
- `abs(A_in-1) < 1e-8`;
- `outer_boundary_residual < 1e-8`;
- `normalization_residual < 1e-8`;
- `log_derivative_match_residual < 1e-7`;
- repeat calls agree at least to `rel <= 1e-10` for `psi`, `dpsi_dr`, and
  `A_out`;
- sensitivity checks show no large instability beyond the existing Q018 scales.

YELLOW partial is acceptable if the oracle works for some but not all core
modes, or if runtime prevents full sensitivity.  Name exact missing modes.

RED if the oracle produces nonfinite values, inconsistent normalization, or
cannot be trusted without changing frozen conventions/policies.

## Required Report

`docs/phase5_km4_tablei_transition_oracle_probe.md` must include:

1. decision label;
2. matrix and parameters;
3. per-mode diagnostic table;
4. repeat/sensitivity summary;
5. comparison with T4v fail-closed records;
6. recommendation:
   - whether T4x production-adapter design for `kM=4` is worth scheduling;
   - or whether a new radial method is needed first;
7. explicit non-claims and forbidden next steps.

If metadata JSON is written, it must be scalar diagnostics/provenance only.
It must not contain field arrays, dense scan arrays, plots, NPZ/HDF5 production
data, or Kirchhoff values.

## Required Verification

Run:

```bash
test -f docs/phase5_km4_tablei_transition_oracle_probe.md
rg -n "KM4 TABLE-I|TRANSITION ORACLE|ell=178|ell=180|ell=204|ell=228|ell=240|outer_boundary_residual|normalization_residual|log_derivative_match_residual|T8" docs/phase5_km4_tablei_transition_oracle_probe.md status.md docs/handoffs/T4_current.md
find runs/phase5/km4_tablei_transition_oracle_probe -maxdepth 2 -type f -print 2>/dev/null | sort
find src tests configs -type f -newer docs/phase5_km4_tablei_transition_oracle_probe.md -print | sort
```

Also run focused existing tests:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py
```

Do not run full pytest unless source/tests changed unexpectedly.

The final `find src tests configs ...` should return no output.

## Stop Conditions

Stop and record YELLOW/RED if:

- any core mode takes more than 20 minutes;
- the oracle returns nonfinite values;
- residuals fail the GREEN thresholds;
- repeat/sensitivity checks are unstable;
- completing the task would require modifying `src`, tests, configs,
  thresholds, conventions, or production adapter envelope.

## Final Handoff

Update `status.md` and `docs/handoffs/T4_current.md` with:

- decision label;
- files read;
- changed files;
- commands run;
- diagnostics summary;
- test results;
- exact next T7 action:
  `你现在是 T7bo。请读取并严格执行 docs/prompts/phase5_t7bo_km4_transition_oracle_probe_review.md。`

