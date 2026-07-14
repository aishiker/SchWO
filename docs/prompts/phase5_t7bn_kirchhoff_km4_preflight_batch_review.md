# Phase 5 T7bn Prompt: Kirchhoff And kM=4 Preflight Batch Review

You are T7bn: validation and batch gate review.

Run this only after both T1j and T4v have completed.

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T1_current.md`
6. `docs/handoffs/T4_current.md`
7. `docs/handoffs/T7_current.md`
8. `docs/handoffs/T8_current.md`
9. `docs/handoffs/T10_current.md`
10. `docs/physics_spec.md`
11. `docs/equation_map.md`
12. `docs/numerics.md`
13. `docs/validation_plan.md`
14. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
15. `references/notes/kirchhoff_eq47_conventions.md`
16. `docs/phase5_km4_tablei_radial_q018_preflight.md`
17. any metadata-only JSON under
    `runs/phase5/km4_tablei_radial_q018_preflight/`.

Before reviewing, check whether installed plugins/skills are relevant.  Use
local verification/review skills if appropriate.  Do not use web lookup unless
local documentation is internally inconsistent.

## Scope

This is one compressed-cadence batch review of the two prerequisites for later
Fig.5/Fig.6 dense Table-I review-grid work:

- T1j Kirchhoff Eq. (47) convention freeze;
- T4v `kM=4` Table-I radial/Q018 preflight.

Allowed updates:

- `status.md`
- `docs/handoffs/T7_current.md`

Forbidden:

- modifying `src/`, tests, configs, references notes, physics docs, accepted
  artifacts, T4 metadata, or `runs/`;
- running dense production, field maps, plotting, fixtures, Kirchhoff
  implementation, or 40-frequency scans;
- authorizing paper-level Fig.5/Fig.6 reproduction directly.

## Review Questions

Answer directly:

1. Did T1j freeze enough Kirchhoff Eq. (47) branch/phase/sign conventions for a
   later implementation, or are named open items still blocking?
2. Did T1j preserve project Fourier/harmonic/tetrad/RW/Zerilli/Route B
   conventions?
3. Did T4v cover the required `kM=[2.0,2.5,3.0,3.5,4.0]`, Table-I radii,
   odd/even sectors, ell probes, and Q018 metadata?
4. Is `kM=4` free of uncovered Q018 fail-closed branches and nonfinite radial
   outputs at the required Table-I radii?
5. Did T4v avoid source/test/config changes and avoid dense production
   artifacts?
6. Is it now reasonable to let T8 run only the conservative eight-point review
   grid from T10g, or is another T1/T4 followup required first?
7. What exact restrictions must T8 keep if allowed to proceed?

## Required Checks

Run:

```bash
test -f references/notes/kirchhoff_eq47_conventions.md
test -f docs/phase5_km4_tablei_radial_q018_preflight.md
rg -n "KIRCHHOFF EQ47|gamma|Gamma|Kummer|1F1|theta_F|comparison baseline|denominator" references/notes/kirchhoff_eq47_conventions.md docs/physics_spec.md docs/equation_map.md
rg -n "KM4 TABLE-I|kM=4|Q018|odd|even|L_seed|nonfinite|uncovered|T8" docs/phase5_km4_tablei_radial_q018_preflight.md
find runs/phase5/km4_tablei_radial_q018_preflight -maxdepth 2 -type f -print 2>/dev/null | sort
```

Do not run pytest unless T1j or T4v modified code/tests or their recorded test
results are missing/inconsistent.  If T4v records a focused radial test command,
you may rerun that command if runtime is reasonable.

## Decision Labels

Use exactly one:

```text
ACCEPT GREEN / KIRCHHOFF-KM4 PREFLIGHT READY FOR T8 REVIEW-GRID SCAN
ACCEPT YELLOW / T8 REVIEW-GRID SCAN ALLOWED WITH NAMED LIMITS
ACCEPT YELLOW / NEED T1-T4 FOLLOWUP BEFORE T8
RED / KIRCHHOFF-KM4 PREFLIGHT UNSAFE
```

Meaning:

- GREEN/YELLOW allowed means T8 may run only the conservative eight-point review
  grid from T10g, not the 40-frequency production grid.
- FOLLOWUP means do not start T8 dense scanning.
- RED stops this branch until T0 designs a repair.

## Required Updates

Update `status.md` and `docs/handoffs/T7_current.md` with:

- decision label;
- files read;
- commands/checks run;
- changed files;
- T1j review result;
- T4v review result;
- whether T8 conservative review-grid scan is allowed;
- forbidden actions that remain;
- exact next T0 action.

