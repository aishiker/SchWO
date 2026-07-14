# T8ai Prompt: Fig.3 dx=0.25M Read-Only Publication Rendering

You are T8ai: visualization and CLI / figure-output thread.

Use Goal mode.  Continue until a complete read-only Fig.3 publication-rendering
candidate package is generated and self-checked, or until a hard stop condition
below is met.

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
11. existing Fig.3 plotting code:
    - `src/schwgw/viz/results.py`
    - `src/schwgw/cli.py`
    - `tests/regression/test_plot_cli.py`

Before doing the task, check whether installed plugins/skills are relevant.
For this task, the local `scientific-visualization` skill is relevant.  Use it
for figure sizing, layout, and export criteria.

## Context

T7bl returned:

```text
ACCEPT GREEN / FIG3 DX0.25 ARCHIVE IS READY FOR READ-ONLY PUBLICATION RENDERING
```

Meaning:

- Use the accepted `dx=0.25M` NPZ archive as the source.
- Do not run solver, scattering, radial, angular, or production code.
- Do not run `dx=0.2M`.
- Do not claim final journal-grade readiness.
- This is a read-only rendering and panel-polish pass.

Accepted source archive:

```text
runs/phase5/fig3_four_frequency_dx0p25_production/
```

Output directory for this task:

```text
runs/phase5/fig3_dx0p25_publication_rendering/
```

## T7 Frequency Compression Rule

Do not stop after each individual rendering variant for a separate T7 review.
T8 should produce a complete self-checked rendering package first.  T7 is only
needed later for batch review / promotion to paper-quality claim, or immediately
if this task hits a hard stop.

## Required Outputs

Create a complete rendering package under:

```text
runs/phase5/fig3_dx0p25_publication_rendering/
```

Minimum outputs:

1. A nearest-neighbor audit panel, regenerated in the new directory from the
   accepted NPZ files.
2. A display-only publication candidate PNG using bilinear interpolation.
3. A display-only publication candidate PDF using the same data/layout.
4. Optionally, a bicubic display-only PNG/PDF if it improves visual continuity
   without obscuring physical structure.
5. JSON sidecars for every output.
6. A manifest:

```text
runs/phase5/fig3_dx0p25_publication_rendering/manifest.md
```

The manifest must list:

- all source NPZ paths, sizes, and SHA-256 hashes;
- all output paths, sizes, and SHA-256 hashes;
- exact commands run;
- interpolation/display policy;
- image/PDF dimensions or metadata;
- non-claims;
- T7bl decision reference;
- whether any source/test code was modified.

## Implementation Policy

First try to use existing read-only CLI commands:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel \
  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz \
  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz \
  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz \
  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz \
  --quantity real \
  --interpolation bilinear \
  --dpi 600 \
  --out runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bilinear_600dpi.png
```

If the existing renderer cannot produce a publication-style panel with clear
labels, readable colorbars, appropriate figure size, and good layout, you may
modify only the read-only visualization/CLI layer:

- `src/schwgw/viz/results.py`
- `src/schwgw/cli.py`
- `tests/regression/test_plot_cli.py`

Allowed code change examples:

- add a publication-style Fig.3 renderer or CLI command;
- add figure-size/layout/DPI/PDF export options;
- add sidecar fields for display-only policy and source SHA provenance;
- add tests proving the command reads saved data and does not call solver code.

Forbidden code changes:

- `src/schwgw/scattering/`
- `src/schwgw/numerics/`
- `src/schwgw/perturbations/`
- `src/schwgw/backgrounds/`
- physics conventions;
- thresholds, `lmax`, Q018 policy, boundary policy, or normalization.

## Sidecar Requirements

Every new output sidecar must record:

- source NPZ paths;
- source NPZ SHA-256 hashes and sizes;
- source case IDs;
- `kM_values=[0.5,1.0,1.5,2.0]`;
- components `h_plus/h_cross`;
- quantity `real`;
- interpolation;
- whether it is numerical audit evidence;
- whether it is display-only smoothing;
- requested DPI and output format;
- final adjacent-pair status from source metadata;
- Q018 same-domain summary;
- non-claim flags:
  - `not_final_journal_grade=true`;
  - `not_pixel_level_reproduction=true`;
  - `not_dx02_production=true`;
  - `not_kM4_production=true`;
  - `not_R60_production=true`;
  - `not_fig2_strict_psi4_artifact=true`.

Policy:

- nearest output: `numerical_evidence_plot=true`,
  `display_only_smoothing=false`.
- bilinear/bicubic outputs: `numerical_evidence_plot=false`,
  `display_only_smoothing=true`.

## Self-Checks

Run these checks before finishing:

```bash
find runs/phase5/fig3_dx0p25_publication_rendering -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig3_dx0p25_publication_rendering/*
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz src/schwgw/cli.py || true
```

Run a read-only Python inspection that:

- opens all new PNGs with PIL;
- checks they are nonblank;
- records dimensions and DPI if available;
- loads all JSON sidecars;
- checks source NPZ hashes;
- verifies interpolation/display-only policy;
- verifies non-claim flags;
- verifies no output path is inside
  `runs/phase5/fig3_four_frequency_dx0p25_production/`.

If source/tests are changed, run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression/test_plot_cli.py tests/unit/test_viz_results.py
```

If no source/tests are changed, focused pytest is optional; record why it was
not needed.  Full pytest is not required for pure read-only rendering unless
source/tests changed or a static check indicates a risk.

## Hard Stop Conditions

Stop and return to T0 if:

- generating a publication-style panel requires rerunning solver/scattering;
- source NPZ metadata are inconsistent with T7bl/T10i facts;
- sidecars cannot preserve source hashes and non-claim policy;
- rendering code would need physics formula changes;
- the accepted archive would need mutation;
- any visual problem appears tied to saved-data resolution, not rendering.

If a hard stop occurs, do not schedule T7 directly; update `status.md` and
`docs/handoffs/T8_current.md` with the blocker and exact T0 question.

## Required Updates

Update:

- `status.md`
- `docs/handoffs/T8_current.md`

Record:

- changed files;
- created output files;
- commands run;
- source artifact hashes;
- output hashes;
- image dimensions;
- whether source/tests changed;
- test results;
- open issues;
- exact next T0 action.

## Definition Of Done

- A complete read-only Fig.3 publication-rendering candidate package exists in
  `runs/phase5/fig3_dx0p25_publication_rendering/`.
- Manifest and sidecars include source hashes, output hashes, interpolation
  policy, Q018/final-pair provenance, and non-claim flags.
- Accepted production artifacts are not modified.
- No solver/scattering/radial/production code is called.
- T8 self-checks pass.
- `status.md` and `docs/handoffs/T8_current.md` are updated.

