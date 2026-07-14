# T10i Prompt: Fig.3 dx=0.25M Figure-Quality And Literature Review

You are T10i: literature and numerical-method support.

Use Goal mode.  Continue until the review note, `status.md`, and
`docs/handoffs/T10_current.md` are complete, or until a hard stop condition
below is met.

## Read First

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T0_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T8_current.md`
7. `docs/handoffs/T10_current.md`
8. `docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md`
9. `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`
10. `references/manifest.md`
11. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
12. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
13. `references/notes/t10h_fig2_fig3_journal_readiness.md`

Before doing the review, check whether an installed plugin/skill is relevant.
Use local notes first.  Only consult PDFs or external literature tools if the
local notes are insufficient for the specific figure-comparison question.

## Scope

Review only.  Do not run the solver, do not call production/scattering APIs, do
not regenerate plots, and do not mutate accepted artifacts.

You may inspect metadata, hashes, sidecars, image dimensions, and PNGs.  You may
use read-only scripts or Python snippets for inspection.  Do not create NPZ,
HDF5, CSV, PNG, PDF, or fixture artifacts in this task.

## Review Questions

Answer these questions in a source-grounded way:

1. Does the accepted archive correspond to the Li-Hou-Zhao Fig.3 physical
   content: `h_plus/h_cross`, four frequencies `kM=[0.5,1.0,1.5,2.0]`,
   `x/M,z/M in [-30,30]`, event horizon/light-ring overlays, and the paper's
   stated amplitudes?
2. Is `dx=0.25M` saved-data resolution scientifically adequate for a Fig.3
   production archive within the current project conventions?
3. Is the current visual roughness, if any, primarily a numerical-resolution
   issue or a rendering/layout issue?
4. Would a read-only publication-style rendering from the accepted NPZs be the
   next lowest-risk step?
5. Is a `dx=0.2M` numerical run justified now, or should it remain gated until
   after read-only rendering review?
6. What claims are supported now, and what claims are still not supported?

Use these known samples-per-wavelength facts unless your local inspection
finds an inconsistency:

- `kM=0.5`: about `50.27` samples per wavelength at `dx=0.25M`;
- `kM=1.0`: about `25.13`;
- `kM=1.5`: about `16.76`;
- `kM=2.0`: about `12.57`.

Also account for:

- all four final adjacent pairs passed `[156,180]`;
- Q018 is zero-warning for `kM=0.5,1.0,1.5`;
- Q018 for `kM=2.0` is structured `evanescent_tail_suppressed`, ell
  `153..180`, with same-domain coverage margin over `rmax`;
- nearest is the audit plot;
- bilinear is display-only smoothing and not numerical evidence.

## Required Output

Create:

```text
references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md
```

The note must contain:

- bottom-line decision recommendation;
- evidence read;
- comparison to Li-Hou-Zhao Fig.3;
- numerical-resolution assessment;
- rendering/layout assessment;
- whether `dx=0.2M` is justified now;
- allowed next branch;
- explicit non-claims;
- hard stops or open risks.

Use exactly one of these recommendation labels:

```text
READY_FOR_T7_FIGURE_QUALITY_REVIEW
NEEDS_READONLY_RENDER_POLISH
NEEDS_DX02_PLANNING
BLOCKED_BY_LITERATURE_CONVENTION
```

## Required Status/Handoff Updates

Update:

- `status.md`
- `docs/handoffs/T10_current.md`

Record:

- changed files;
- files read;
- commands/checks run;
- whether any skill/plugin was used;
- test result or why tests were not relevant;
- open issues;
- exact next T7bl prompt.

## Forbidden Actions

- Do not modify `src/`, tests, configs, or accepted artifacts.
- Do not generate or overwrite figures.
- Do not run `dx=0.2M`.
- Do not run `kM=4`.
- Do not create fixtures.
- Do not modify frozen physics conventions, thresholds, `lmax`, or boundary
  policies.
- Do not claim final journal-grade readiness.  You may recommend that T7 review
  whether read-only publication rendering is sufficient.

## Verification Commands

At minimum, run read-only existence/content checks:

```bash
test -f references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md
test -f runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md
rg -n "READY_FOR_T7_FIGURE_QUALITY_REVIEW|NEEDS_READONLY_RENDER_POLISH|NEEDS_DX02_PLANNING|BLOCKED_BY_LITERATURE_CONVENTION|dx=0\\.25|dx=0\\.2|Li-Hou-Zhao|Fig\\.3|samples per wavelength|Q018|nearest|bilinear|non-claim" references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md
```

Full pytest is required only if source/tests change, which this task should not
do.

## Definition Of Done

- The T10i note exists and answers all review questions.
- `status.md` and `docs/handoffs/T10_current.md` are updated.
- No source/test/config/accepted-artifact mutation occurred.
- The next T7bl review prompt is explicitly recorded.

