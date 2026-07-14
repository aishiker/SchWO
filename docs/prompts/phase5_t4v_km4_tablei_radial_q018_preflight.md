# Phase 5 T4v Prompt: kM=4 Table-I Radial/Q018 Preflight

You are T4v: radial solver and Q018 preflight.

Use Goal mode for this task.

Goal objective:

```text
Perform a bounded radial/Q018 preflight for future Fig.5/Fig.6 dense Table-I scans up to kM=4. Report whether the existing radial solver/Q018 policy can support a later eight-point conservative review-grid scan. Do not generate dense production artifacts, field maps, plots, fixtures, or Kirchhoff data.
```

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T4_current.md`
6. `docs/handoffs/T7_current.md`
7. `docs/handoffs/T8_current.md`
8. `docs/numerics.md`
9. `docs/validation_plan.md`
10. `docs/phase5_m5_four_frequency_closeout.md`
11. `docs/phase5_tablei_extraction_closeout.md`
12. `docs/phase5_tablei_reporting_closeout.md`
13. `references/notes/q018_spin2_tail_bound.md`
14. `references/notes/q018_scalar_partial_wave_cutoff.md`
15. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
16. relevant radial/Q018 source and tests under `src/schwgw/numerics/`,
    `src/schwgw/perturbations/`, `src/schwgw/scattering/`, and `tests/physics/`.

Before starting, check whether installed plugins/skills are relevant.  This is a
numerical/radial debugging task; use any local debugging/TDD skill if needed.

## Scope

This is a preflight only.  It may call existing radial solver APIs to evaluate
diagnostics, but it must not compute or save dense Table-I pointwise
amplification arrays and must not run a full dense frequency scan.

Target physical points are the eight Table-I radii at `z/M=30`:

```text
x/M = [0, 1, 2, 3, 10, 15, 20, 25]
r/M = [
  30.000000,
  30.016662,
  30.066593,
  30.149627,
  31.622777,
  33.541020,
  36.055513,
  39.051248
]
```

Preflight frequencies:

```text
kM = [2.0, 2.5, 3.0, 3.5, 4.0]
```

Use `kM=2.0` as the accepted anchor comparison and `kM=4.0` as the gate stress.

For each frequency, define:

```text
L_seed(kM) = ceil_to_multiple_of_12(max(84, 90*kM))
```

Required ell probes:

- `ell_turn = ceil(kM * r/M)` at `r/M=30.0` and `r/M=39.051248`;
- `ell_turn-12`, `ell_turn`, `ell_turn+12`, clipped to `ell >= 2`;
- `L_seed-24`, `L_seed`;
- any continuous Q018 band triggered by the current solver policy.

Check both odd/RW and even/Zerilli sectors.

## Allowed Updates

- `docs/phase5_km4_tablei_radial_q018_preflight.md`
- optional metadata-only JSON under
  `runs/phase5/km4_tablei_radial_q018_preflight/`
- `status.md`
- `docs/handoffs/T4_current.md`

The optional `runs/` JSON must contain diagnostics/provenance only.  It must not
contain field arrays, dense scan arrays, plots, NPZ/HDF5 production artifacts,
or Kirchhoff values.

## Forbidden

- Do not modify `src/`, tests, or configs unless an existing API bug prevents
  even bounded preflight.  If that happens, stop with a YELLOW/RED finding
  instead of silently implementing a new radial method.
- Do not generate dense scan NPZ/HDF5, field maps, figures, fixtures, or
  Kirchhoff baseline data.
- Do not run `kM=4` full x-z grids or any `40`-frequency dense scan.
- Do not change thresholds, `lmax` policy, boundary policy, Q018 policy, or
  physics conventions.
- Do not claim T8 dense production is authorized.

## Required Preflight Report

`docs/phase5_km4_tablei_radial_q018_preflight.md` must include:

1. **Decision Label**
   - One of:
     - `GREEN / KM4 TABLE-I RADIAL-Q018 PREFLIGHT PASSED`
     - `YELLOW / KM4 TABLE-I PREFLIGHT PASSED WITH NAMED LIMITS`
     - `YELLOW / KM4 TABLE-I PREFLIGHT NEEDS RADIAL METHOD FOLLOWUP`
     - `RED / KM4 TABLE-I PREFLIGHT FAILED`
2. **Matrix Covered**
   - Frequencies, radii, sectors, ell probes, boundary settings, and Q018 oracle
     settings actually evaluated.
3. **Diagnostics**
   - For every evaluated `(kM, ell, sector)` record finite/nonfinite status,
     warning codes, Q018 branch/oracle metadata, matching/Wronskian/residual
     diagnostics if available, and whether requested Table-I radii are inside
     the reliable evaluation domain.
4. **kM=4 Gate**
   - Explicitly state whether `kM=4` has no uncovered Q018 branch and no
     nonfinite radial output at the required radii.
5. **T8 Readiness Recommendation**
   - State whether T8 may later run only the conservative eight-point review
     grid after T7 review, or whether T4 followup is required first.
6. **Non-Claims**
   - No dense production, no Kirchhoff, no paper-level Fig.5/Fig.6 claim, no
     `dx=0.2M`, no R60_K4, no fixture promotion.

## Stop Conditions

Stop and record YELLOW/RED if:

- nonfinite radial values occur at a Table-I radius;
- an uncovered Q018 fail-closed branch appears;
- the existing solver requires a new unreviewed radial method for `kM=4`;
- diagnostics cannot identify the Q018 branch/oracle used;
- runtime exceeds a practical interactive window before the `kM=4` gate can be
  sampled.  Record completed matrix entries and do not broaden scope.

## Required Verification

Run relevant focused radial/Q018 tests, at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py
```

Also run:

```bash
test -f docs/phase5_km4_tablei_radial_q018_preflight.md
rg -n "KM4 TABLE-I|kM=4|Q018|odd|even|L_seed|Table-I|nonfinite|uncovered|T8" docs/phase5_km4_tablei_radial_q018_preflight.md status.md docs/handoffs/T4_current.md
find runs/phase5/km4_tablei_radial_q018_preflight -maxdepth 2 -type f -print 2>/dev/null | sort
find src tests configs -type f -newer docs/phase5_km4_tablei_radial_q018_preflight.md -print | sort
```

The final `find src tests configs ...` should return no output unless you stopped
and explicitly reported an API bug that forced no preflight completion.

## Final Handoff

Update `status.md` and `docs/handoffs/T4_current.md` with:

- decision label;
- files read;
- changed files;
- commands run;
- diagnostics summary;
- test results;
- exact T7/T0 next action;
- whether T1j Kirchhoff convention freeze is independent and still required.

