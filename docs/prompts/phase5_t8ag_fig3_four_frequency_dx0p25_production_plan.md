# Phase 5 T8ag Prompt: Fig.3 Four-Frequency dx=0.25M Production Plan

你现在是 **T8ag：Fig.3 four-frequency dx=0.25M production planning**。

## Mode

Use Goal mode if available. Continue until the Definition of Done is met or a stop condition is reached.

This is a **planning-only** slice. Do not run production.

## Must Read First

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/phase4_production_closeout.md`
7. `docs/m4_production_plan.md`
8. `docs/phase5_fig3_k2_dx0p25_hires_pilot_closeout.md`
9. `docs/prompts/phase5_t8ae_fig3_k2_dx0p25_hires_goal.md`
10. `docs/prompts/phase5_t7bg_fig3_k2_dx0p25_hires_review.md`
11. `docs/prompts/phase5_t8af_fig3_k2_dx0p25_sidecar_hardening.md`
12. `docs/prompts/phase5_t7bh_fig3_k2_dx0p25_sidecar_review.md`
13. `configs/li_fig3_xz_production_k2p0_dx0p25_pilot.yaml`
14. `configs/li_fig3_xz_production_k0p5_dx0p5.yaml`
15. `configs/li_fig3_xz_production_k1p0_dx0p5.yaml`
16. `configs/li_fig3_xz_production_k1p5_dx0p5.yaml`
17. `configs/li_fig3_xz_production_k2p0_dx0p5.yaml`

Before doing task work, check whether installed plugins/skills are relevant. Use only those that are actually helpful for this local planning/config task.

## Goal

Create a reviewed plan for a future Fig.3 four-frequency high-resolution production run:

```text
kM = [0.5, 1.0, 1.5, 2.0]
dx = dz = 0.25M
x/M, z/M in [-30, 30]
Route B/M4 production path
```

The plan must inherit the T8ae/T8af/T7bh requirements:

- Q018 same-domain guard;
- final adjacent-pair convergence policy;
- nearest = audit plot;
- bilinear = display-only plot;
- detached PNG sidecars carry source NPZ path/SHA/size, run JSON path, Q018 summary, non-claim flags, interpolation policy, final pair, grid spacing, DPI, valid/invalid counts;
- no paper-level or final journal-grade claim.

## Strict Scope

Allowed:

- Create a planning document:
  - `docs/phase5_fig3_four_frequency_dx0p25_production_plan.md`
- Create draft not-run configs:
  - `configs/li_fig3_xz_production_k0p5_dx0p25.yaml`
  - `configs/li_fig3_xz_production_k1p0_dx0p25.yaml`
  - `configs/li_fig3_xz_production_k1p5_dx0p25.yaml`
  - `configs/li_fig3_xz_production_k2p0_dx0p25.yaml`
- Update:
  - `status.md`
  - `docs/handoffs/T8_current.md`

Forbidden:

- Do not run `schwgw.cli run`.
- Do not call solver/scattering/radial production APIs from Python.
- Do not generate NPZ/HDF5/PNG/PDF/CSV production artifacts.
- Do not modify `src/`.
- Do not modify tests.
- Do not modify existing accepted NPZ/PNG files.
- Do not modify `runs/phase4/m4_production_first_pass/`.
- Do not modify `runs/phase5/fig3_k2_dx0p25_hires_pilot/` except reading it.
- Do not run `dx=0.2M`.
- Do not run `kM=4`.
- Do not run R60/R60_K4.
- Do not generate Fig.2 strict `Psi4`.
- Do not create fixtures.
- Do not implement Kirchhoff or Appendix D/E curves.
- Do not make paper-level or final journal-grade claims.

## Required Config Content

Each draft config must use:

```yaml
background:
  M: 1.0
wave:
  kM: <0.5|1.0|1.5|2.0>
  A_plus:
    real: 0.9
    imag: 1.1
  A_cross:
    real: 0.4
    imag: 0.6
observer:
  kind: xz_plane
  x_range:
    start: -30.0
    stop: 30.0
    step: 0.25
    endpoint: true
  z_range:
    start: -30.0
    stop: 30.0
    step: 0.25
    endpoint: true
  invalid_radius_policy: mask
numerics:
  lmax: 180
  boundary:
    r_in_eps: 1.0e-6
    r_out: 300.0
    rtol: 1.0e-10
    atol: 1.0e-12
convergence:
  enabled: true
  lmax_values: [108, 132, 156, 180]
  theta_values: [0.0, 0.05, 0.2, 1.0, 2.0, 3.0]
  phi_values: [0.0, 3.141592653589793]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
```

Use project-local output paths under:

```text
runs/phase5/fig3_four_frequency_dx0p25_production/
```

Do not use `/tmp` output paths.

## Planning Document Requirements

`docs/phase5_fig3_four_frequency_dx0p25_production_plan.md` must include:

1. Scope:
   - four frequencies only: `kM=[0.5,1.0,1.5,2.0]`;
   - `dx=dz=0.25M`;
   - domain `[-30,30]^2`;
   - Route B/M4 production path;
   - not Fig.2, not M5 transmission, not R60, not `kM=4`.
2. Inputs:
   - draft config paths;
   - accepted `kM=2.0` pilot artifact path/hash as prior evidence, not as automatic production promotion unless T7/T0 later accepts that route.
3. Execution options:
   - Option A: rerun all four frequencies into one uniform production directory.
   - Option B: run `kM=0.5,1.0,1.5` and reference the accepted `kM=2.0` pilot by immutable hash.
   - Recommend one option and justify it in terms of reproducibility, runtime, and avoiding scope/promotion ambiguity.
4. Runtime/storage estimates:
   - use T8ae `kM=2` runtime `4220.79 s` and T10h estimate `6-8 h` as conservative four-frequency budget;
   - record expected shape `(241,241)` and approximate NPZ total size scale.
5. Q018 policy:
   - same-domain only;
   - every produced run must record Q018 summary;
   - `kM=2` suppressed modes must cover `rmax=42.42640687119285M`;
   - any uncovered warning is a stop condition.
6. Convergence policy:
   - final adjacent pair must pass;
   - early adjacent pairs are diagnostics only.
7. Plot/output policy:
   - solver produces saved complex data first;
   - plotting reads saved data only;
   - nearest audit panels required;
   - bilinear panels optional display-only;
   - all plot sidecars must inherit T8af provenance fields.
8. Required future production artifacts:
   - one NPZ and one run JSON per frequency;
   - per-frequency nearest audit PNG plus sidecar;
   - optional per-frequency bilinear display PNG plus sidecar;
   - optional four-frequency panel from saved NPZs only;
   - manifest with hashes, commands, test results, and non-claims.
9. Stop conditions for future T8ah production:
   - any solver run exceeds planned wall-time threshold without progress record;
   - final pair fails;
   - Q018 coverage fails;
   - mask/finite/NaN policy fails;
   - output goes outside project-local `runs/`;
   - any source/test/physics convention change is needed.
10. Exact next prompts:
   - T7bi review prompt;
   - if T7bi GREEN, a recommended future T8ah Goal-mode production prompt outline, but do not create the T8ah prompt unless T0 asks.

## Verification Commands

Run read-only checks:

```bash
find configs -maxdepth 1 -name 'li_fig3_xz_production_k*p*_dx0p25.yaml' -print | sort
find runs/phase5/fig3_four_frequency_dx0p25_production -maxdepth 2 -type f -print 2>/dev/null || true
```

Run a small Python/YAML inspection that verifies draft config fields, without importing solver/scattering/physics APIs.

Pytest is not required because this is planning/config-only and must not change source or tests. If you do change source/tests by accident, stop and explain.

## Stop Conditions

Stop and report YELLOW/RED if:

- any production artifact already exists in the planned output directory and would be overwritten;
- a draft config would need to overwrite a hand-edited file with incompatible content;
- you cannot make project-local output paths;
- the plan cannot preserve T8af sidecar provenance requirements;
- the plan would require changing physics conventions, thresholds, `lmax`, source code, or tests.

## Required Updates

Update `status.md` with:

- changed files;
- commands/checks run;
- planning decision;
- draft configs created;
- whether any production outputs were found;
- open issues;
- exact next action for T7bi.

Update `docs/handoffs/T8_current.md` with:

- current state after T8ag;
- changed files;
- forbidden actions;
- exact T7bi review prompt;
- definition of done for T7bi.

## Definition of Done

- Planning doc exists and clearly separates planning from production.
- Draft configs exist and point to project-local production output paths.
- No production run, NPZ, PNG, fixture, source change, test change, convention change, or threshold change was made.
- `status.md` and `docs/handoffs/T8_current.md` are updated.
- T7 can review with:

```text
你现在是 T7bi。请读取并严格执行 docs/prompts/phase5_t7bi_fig3_four_frequency_dx0p25_plan_review.md。
```
