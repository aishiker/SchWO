# Phase 5 T7bi Prompt: Fig.3 Four-Frequency dx=0.25M Production Plan Review

你现在是 **T7bi：Fig.3 four-frequency dx=0.25M production plan review**。

## Must Read First

1. `project.md`
2. `status.md`
3. `docs/handoffs/T7_current.md`
4. `docs/handoffs/T8_current.md`
5. `docs/prompts/phase5_t8ag_fig3_four_frequency_dx0p25_production_plan.md`
6. `docs/phase5_fig3_four_frequency_dx0p25_production_plan.md`
7. `docs/phase5_fig3_k2_dx0p25_hires_pilot_closeout.md`
8. `configs/li_fig3_xz_production_k0p5_dx0p25.yaml`
9. `configs/li_fig3_xz_production_k1p0_dx0p25.yaml`
10. `configs/li_fig3_xz_production_k1p5_dx0p25.yaml`
11. `configs/li_fig3_xz_production_k2p0_dx0p25.yaml`

Before doing task work, check whether installed plugins/skills are relevant. Use only those that help with local plan/config review.

## Goal

Independently review whether T8ag produced a safe, complete planning-only package for a future Fig.3 four-frequency `dx=0.25M` production run.

This is review-only. Do not run production.

## Review Requirements

Verify:

1. The task remained planning-only:
   - no solver run;
   - no new NPZ/HDF5/PNG/PDF/CSV production artifact;
   - no `src/` changes;
   - no test changes;
   - no accepted artifact mutation.
2. Draft configs exist for:
   - `kM=0.5`;
   - `kM=1.0`;
   - `kM=1.5`;
   - `kM=2.0`.
3. Each draft config has:
   - `M=1.0`;
   - `A_plus=0.9+1.1i`;
   - `A_cross=0.4+0.6i`;
   - x/z range `[-30,30]`;
   - step `0.25`;
   - endpoint `true`;
   - invalid radius policy `mask`;
   - `lmax=180`;
   - boundary settings matching T8ae;
   - convergence lmax values `[108,132,156,180]`;
   - project-local output under `runs/phase5/fig3_four_frequency_dx0p25_production/`.
4. The production plan inherits:
   - Q018 same-domain guard;
   - final adjacent-pair pass requirement;
   - early adjacent pairs as diagnostics only;
   - nearest audit / bilinear display-only policy;
   - T8af sidecar provenance fields;
   - no paper-level or final journal-grade claim.
5. The plan explicitly separates:
   - rerun-all-four option;
   - reuse-by-reference of accepted `kM=2` pilot option;
   - the recommended route and its tradeoff.
6. The plan does not authorize:
   - `dx=0.2M`;
   - `kM=4`;
   - R60/R60_K4;
   - Fig.2 strict `Psi4`;
   - fixtures;
   - dense Fig.5/Fig.6 scans;
   - Kirchhoff implementation;
   - Appendix D/E curves;
   - paper-level/final-journal-grade claims.

## Commands / Checks

Run:

```bash
find configs -maxdepth 1 -name 'li_fig3_xz_production_k*p*_dx0p25.yaml' -print | sort
find runs/phase5/fig3_four_frequency_dx0p25_production -maxdepth 2 -type f -print 2>/dev/null || true
find src tests -type f -newer docs/prompts/phase5_t8ag_fig3_four_frequency_dx0p25_production_plan.md -print | sort
```

Run an independent Python/YAML inspection of the four draft configs. Do not import solver/scattering/radial/physics APIs.

Pytest is not required unless source/tests changed. If source/tests changed, run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## Decision Labels

Use one of:

- **ACCEPT GREEN / FOUR-FREQUENCY DX0.25 PRODUCTION PLAN READY**:
  plan/configs are complete, no production run occurred, and T0 can schedule a future T8ah Goal-mode production run.
- **ACCEPT YELLOW / PLAN USABLE WITH NAMED FIXES BEFORE PRODUCTION**:
  no unsafe artifact mutation occurred, but plan/config metadata must be fixed before production.
- **RED / PLANNING SCOPE FAILURE**:
  production was run, accepted artifacts were changed, source/tests/conventions changed without authorization, or configs would drive an unsafe production run.

## Required Updates

Update only:

- `status.md`
- `docs/handoffs/T7_current.md`

Record:

- files inspected;
- commands/checks run;
- decision label;
- whether future T8ah production can be scheduled;
- whether T8ah should rerun all four frequencies or reuse the accepted `kM=2` pilot by reference;
- remaining gates and forbidden actions.

## Next-Step Guidance

If GREEN:

- Recommend T0 create a separate T8ah Goal-mode production prompt.
- Do not run production from T7.

If YELLOW:

- Provide the exact narrow T8 follow-up prompt needed to fix the plan.

If RED:

- Stop and recommend planning/artifact-integrity triage before any computation.
