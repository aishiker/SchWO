# Phase 5 T7be Prompt: Fig.5/Fig.6 Dense Scan And Kirchhoff Plan Review

You are T7be: independent validation/review for the T10g Fig.5/Fig.6 dense scan and Kirchhoff readiness plan.

This is a review-only slice. Do not modify `src`, tests, configs, references other than T7 handoff/status, accepted artifacts, generated plotting artifacts, or `runs/`.

## Required Reads

Read, in order:

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T0_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T10_current.md`
7. `docs/physics_spec.md`
8. `docs/equation_map.md`
9. `docs/numerics.md`
10. `docs/validation_plan.md`
11. `docs/phase5_m5_four_frequency_closeout.md`
12. `docs/phase5_tablei_extraction_closeout.md`
13. `docs/phase5_tablei_reporting_closeout.md` if it exists
14. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
15. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
16. `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
17. `references/notes/q018_spin2_tail_bound.md`
18. `references/notes/q018_scalar_partial_wave_cutoff.md`
19. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`

## Task

Review whether T10g gives a safe, source-grounded, implementation-ready plan for moving from the current sparse Table-I reporting pilot toward paper-level Fig.5/Fig.6 reproduction.

Allowed updates:

- `status.md`
- `docs/handoffs/T7_current.md`

## Review Checklist

Verify that the T10g plan:

- clearly explains why T8ad PNGs are intentionally simple;
- does not authorize solver runs, dense production, fixtures, plotting-as-paper-reproduction, or `kM=4` production;
- separates:
  - accepted four-frequency Table-I pilot;
  - dense `Mk` scan planning;
  - `kM=4` radial/Q018 preflight;
  - Kirchhoff Eq. (47) convention freeze;
  - later T8 production and plotting;
- keeps M5 as pointwise wave-optics amplification, not radial transmission/absorption;
- preserves Route B packaged polarization conventions;
- does not change frozen Fourier/harmonic/tetrad/RW/Zerilli conventions;
- gives concrete next prompts for T1/T4/T7/T8 with dependencies and stop conditions;
- includes enough metadata/schema requirements for later T8 output reproducibility;
- gives a staged runtime/storage plan rather than jumping directly to a full dense production run;
- marks Kirchhoff as comparison baseline only.

## Required Commands

Run:

```bash
test -f references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md
rg -n "dense|kM=4|Kirchhoff|Q018|Route B|pointwise|Gamma|Kummer|1F1|theta_F|T1|T4|T8" references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md
rg -n "T10g|T7be|dense|Kirchhoff|kM=4" status.md docs/handoffs/T10_current.md docs/handoffs/T7_current.md
```

Do not run pytest unless T10g incorrectly changed code/tests.

## Decision Labels

Use one of:

- `ACCEPT GREEN / FIG5-FIG6 DENSE-KIRCHHOFF PLAN ACCEPTED`
- `ACCEPT YELLOW / PLAN ACCEPTED WITH NAMED OPEN RISKS`
- `REJECT RED / PLAN UNSAFE OR INCOMPLETE`

If GREEN/YELLOW, recommend the next T0 step from the plan, but do not directly authorize T8 dense production unless all prerequisites are already satisfied.
