# T7bm Prompt: Fig.3 dx=0.25M Publication Rendering Batch Review

You are T7bm: validation and batch image/package review.

This is a compressed-cadence T7 review.  Review the complete T8ai package once;
do not turn each rendering variant into a separate review loop.

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T8_current.md`
7. `docs/handoffs/T10_current.md`
8. `docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md`
9. `references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md`
10. `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`
11. `runs/phase5/fig3_dx0p25_publication_rendering/manifest.md`
12. every JSON sidecar under
    `runs/phase5/fig3_dx0p25_publication_rendering/`
13. T8ai code changes:
    - `src/schwgw/viz/results.py`
    - `src/schwgw/cli.py`
    - `tests/regression/test_plot_cli.py`

Before reviewing, check whether installed plugins/skills are relevant.  For
this image/package review, the local `scientific-visualization` and
`verification-before-completion` skills are relevant.

## Scope

Review only.  Do not generate new production data, do not rerun plotting into
the accepted output directory, and do not modify T8ai outputs.

Allowed files to update:

- `status.md`
- `docs/handoffs/T7_current.md`

Forbidden:

- modifying `src/`, tests, configs, accepted production artifacts, or T8ai
  rendering artifacts;
- running solver/scattering/radial/production commands;
- running `dx=0.2M`, `kM=4`, R60/R60_K4, Fig.2 strict `Psi4`, fixtures, dense
  Fig.5/Fig.6, Kirchhoff, or Appendix D/E work;
- claiming pixel-level reproduction.

## Review Questions

Answer these directly:

1. Does the T8ai package exist and contain exactly the expected PNG/PDF,
   sidecar, and manifest files?
2. Did T8ai preserve the accepted source archive and source NPZ hashes?
3. Are nearest, bilinear, and bicubic policies correctly separated?
4. Do the sidecars preserve source hashes, final-pair status, Q018 same-domain
   summary, display policy, and non-claim flags?
5. Do the new source changes stay inside read-only visualization/CLI/tests?
6. Does `plot-fig3-multifrequency-panel --style publication` remain a
   read-only plotting path and not a solver path?
7. Are the images nonblank, readable, and consistent with a double-column
   publication candidate?
8. Which display-only rendering should be recommended as primary for draft
   paper use: bilinear or bicubic?  State the reason.
9. Is there any evidence that `dx=0.2M` is now required?

## Required Checks

Run:

```bash
find runs/phase5/fig3_dx0p25_publication_rendering -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig3_dx0p25_publication_rendering/*
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz src/schwgw/cli.py || true
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression/test_plot_cli.py tests/unit/test_viz_results.py
```

Also run an independent read-only Python inspection that:

- loads all sidecars;
- verifies source NPZ hashes and sizes;
- verifies output hashes and sizes;
- verifies non-claim flags;
- verifies interpolation/display policy;
- verifies no output path is under
  `runs/phase5/fig3_four_frequency_dx0p25_production/`;
- checks PNG dimensions/nonblank stats;
- checks PDF MediaBox dimensions.

Visually inspect at least:

- `runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bilinear_600dpi.png`
- `runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bicubic_600dpi.png`
- optionally the nearest audit PNG if there is any doubt about smoothing.

Full pytest is not required unless focused tests or static checks indicate a
broader source risk.

## Required Decision Label

Use exactly one:

```text
ACCEPT GREEN / FIG3 DX0.25 PUBLICATION RENDERING PACKAGE ACCEPTED
ACCEPT YELLOW / MINOR READ-ONLY RENDER POLISH NEEDED
ACCEPT YELLOW / SAVED-DATA RESOLUTION REVIEW NEEDED BEFORE FIG3 PROMOTION
RED / PACKAGE OR SCOPE MISMATCH
```

Interpretation:

- GREEN accepts the package as the current Fig.3 paper-draft rendering
  candidate.  It still does not claim pixel-level reproduction or final
  journal-grade acceptance.
- YELLOW render polish means T8 may continue with another low-risk read-only
  rendering pass without opening a new production or T7 per-variant loop.
- YELLOW resolution review means T0 should investigate whether `dx=0.2M`
  planning is justified, but still should not start production directly.
- RED stops Fig.3 promotion.

## Required Updates

Update:

- `status.md`
- `docs/handoffs/T7_current.md`

Record:

- decision label;
- files read;
- commands/checks run;
- changed files;
- image review result;
- recommended primary display rendering;
- whether `dx=0.2M` remains gated;
- test results;
- exact next T0 action.

## Definition Of Done

- T7bm records one required decision label.
- The rendering package is independently inspected.
- Focused tests are run and recorded.
- No artifacts/source/tests/configs are modified except `status.md` and
  `docs/handoffs/T7_current.md`.
- T0 has a clear next step.

