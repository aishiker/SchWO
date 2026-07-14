# Phase 5 T7bb Prompt: Table-I Extraction Closeout

You are T7bb: closeout writer for the accepted Fig.5/Fig.6 Table-I four-frequency extraction pilot.

## Mandatory Context

Before doing anything else, check whether installed plugins or skills are relevant. This is a documentation/closeout task; use local project notes, handoffs, manifests, sidecars, and source metadata first.

Read:

- `project.md`
- `status.md`
- `docs/handoffs/README.md`
- `docs/handoffs/T0_current.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/T8_current.md`
- `docs/physics_spec.md`
- `docs/equation_map.md`
- `docs/numerics.md`
- `docs/validation_plan.md`
- `docs/phase5_m5_four_frequency_closeout.md`
- `docs/phase5_fig4_exact_angular_closeout.md`
- `references/manifest.md`
- `references/notes/t10d_li_hou_zhao_figure_inventory.md`
- `references/notes/t10e_fig4_fig5_reproduction_plan.md`
- `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
- `docs/prompts/phase5_t8ac_fig5_fig6_tablei_readonly_extraction.md`
- `docs/prompts/phase5_t7ba_fig5_fig6_tablei_extraction_review.md`
- `docs/prompts/phase5_t7bb_tablei_extraction_closeout.md`
- `runs/phase5/m5_four_frequency_amplification_artifacts/manifest.md`
- `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json`

## Scope

Create a closeout document for the accepted Table-I extraction pilot:

```text
docs/phase5_tablei_extraction_closeout.md
```

Update:

```text
status.md
docs/handoffs/T7_current.md
```

Do not modify `src`, tests, configs, references, source artifacts, extraction artifacts, plots, or `runs/`.

## Required Closeout Content

The closeout must record:

- Decision label:
  `CLOSED / ACCEPTED FOR FIG.5/FIG.6 TABLE-I FOUR-FREQUENCY READ-ONLY EXTRACTION ONLY`
- Accepted artifact paths and SHA-256:
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz`
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json`
- Accepted source archive and source SHA table from T7ba.
- Exact accepted scope:
  - four frequencies `kM=[0.5,1.0,1.5,2.0]`;
  - eight Table-I points;
  - exact grid-index extraction from accepted M5 archive;
  - complex `F_plus_complex/F_cross_complex` as authoritative values;
  - phase arrays are derived summaries;
  - four-frequency unwrap is diagnostic only.
- Point IDs, `x/z`, `x_indices/z_indices`, and note that source arrays are indexed as `[z_index, x_index]`.
- Verification evidence from T7ba:
  - exact value comparison against source NPZs;
  - metadata/sidecar match;
  - static no-solver/no-baseline boundary;
  - targeted and full pytest results.
- Explicit non-scope:
  - dense `Mk` scan;
  - `kM=4`;
  - R60_K4;
  - Kirchhoff baseline;
  - Appendix D/E curves;
  - strict `Psi4`;
  - arbitrary incident direction;
  - fixtures;
  - plotting;
  - paper-level Fig.5/Fig.6 reproduction.
- Next-decision menu for T0:
  - read-only plotting/reporting-planning slice using the accepted Table-I data;
  - dense `Mk` scan planning with explicit `kM=4` gate;
  - Kirchhoff convention freeze with T1/T10;
  - no action / pause.

## Required Checks

Run:

```bash
test -f docs/phase5_tablei_extraction_closeout.md
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json
```

Do not run full pytest unless you modify code/tests/configs despite the scope.

## Decision Labels

Use:

- **CLOSED / ACCEPTED FOR FIG.5/FIG.6 TABLE-I FOUR-FREQUENCY READ-ONLY EXTRACTION ONLY**
  - The closeout is complete and consistent with T7ba.
- **YELLOW / CLOSEOUT REVISION NEEDED**
  - The artifact remains accepted, but the closeout document has metadata/scope gaps.
- **RED / STOP**
  - The closeout cannot be written without contradicting T7ba or local artifact metadata.

## Status And Handoff

Update `status.md` and `docs/handoffs/T7_current.md` with:

- changed files;
- files read;
- commands run and results;
- decision label;
- remaining gates;
- exact next action for T0.

Recommended exact next action if GREEN:

```text
T0 may schedule a separate read-only Table-I plotting/reporting-planning slice, or pause. Do not schedule dense Mk scan, kM=4, Kirchhoff baseline, fixtures, or paper-level Fig.5/Fig.6 reproduction without a new gate.
```
