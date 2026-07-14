# Phase 5 T7bo Prompt: kM=4 Transition Oracle Probe Review

You are T7bo: validation and radial-method gate review.

Run this only after T4w completes.

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
10. `docs/phase5_km4_tablei_transition_oracle_probe.md`
11. `runs/phase5/km4_tablei_radial_q018_preflight/radial_q018_preflight_metadata.json`
12. any metadata-only JSON under
    `runs/phase5/km4_tablei_transition_oracle_probe/`
13. `references/notes/q018_spin2_tail_bound.md`
14. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
15. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
16. `src/schwgw/numerics/radial_solver.py`

Before reviewing, check relevant installed skills/plugins.  Use
`verification-before-completion`.  Do not use web lookup unless local records
contradict each other.

## Scope

Review only.  Allowed updates:

- `status.md`
- `docs/handoffs/T7_current.md`

Forbidden:

- modify `src/`, tests, configs, notes, accepted artifacts, or `runs/`;
- run T8, dense scans, production adapter implementation, field maps, plots,
  fixtures, Kirchhoff implementation, or 40-frequency scans;
- authorize paper-level Fig.5/Fig.6 production.

## Review Questions

Answer directly:

1. Did T4w keep the probe experimental and avoid production adapter changes?
2. Were all core failing T4v modes covered?
   - `kM=4`, odd/even, `ell=178,180,204,228,240`,
     `required_radius=39.051248`.
3. Are all core probe outputs finite?
4. Do normalization and residual diagnostics satisfy the stated thresholds?
5. Are repeat and sensitivity checks strong enough to trust the method as a
   candidate for a later reviewed production adapter?
6. Did T4w preserve fail-closed policy, thresholds, `lmax`, boundary policy,
   Q018 policy, and frozen conventions?
7. What is the exact next T0 action?

## Required Checks

Run:

```bash
test -f docs/phase5_km4_tablei_transition_oracle_probe.md
rg -n "KM4 TABLE-I|TRANSITION ORACLE|GREEN|YELLOW|RED|ell=178|ell=180|ell=204|ell=228|ell=240|outer_boundary_residual|normalization_residual|log_derivative_match_residual|T8" docs/phase5_km4_tablei_transition_oracle_probe.md
find runs/phase5/km4_tablei_transition_oracle_probe -maxdepth 2 -type f -print 2>/dev/null | sort
find src tests configs -type f -newer docs/phase5_km4_tablei_transition_oracle_probe.md -print | sort
```

If T4w recorded a focused test command, rerun it unless runtime is clearly
excessive.  Do not run full pytest unless source/tests changed unexpectedly.

If metadata JSON exists, independently inspect it and summarize:

- record count;
- success/error counts;
- maximum residuals;
- repeat/sensitivity status;
- whether any field arrays or production data were written.

## Decision Labels

Use exactly one:

```text
ACCEPT GREEN / KM4 TRANSITION ORACLE PROBE ACCEPTED FOR T4X ADAPTER DESIGN
ACCEPT YELLOW / KM4 TRANSITION ORACLE PROBE PARTIAL - T4 FOLLOWUP REQUIRED
RED / KM4 TRANSITION ORACLE PROBE UNSAFE
```

Meaning:

- GREEN authorizes T0 to schedule a separate T4x production-adapter design or
  implementation prompt for `kM=4` Table-I review-grid scope only.  It does not
  authorize T8 scans.
- YELLOW means another T4 method followup is needed before adapter design.
- RED stops the branch until T0 redesigns the radial method path.

## Required Updates

Update `status.md` and `docs/handoffs/T7_current.md` with:

- decision label;
- files read;
- commands/checks run;
- changed files;
- diagnostics summary;
- whether T4x adapter design may be scheduled;
- explicit statement that T8 remains blocked unless/until a later T7 gate
  accepts the adapter/preflight result.

