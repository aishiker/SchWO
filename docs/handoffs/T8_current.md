# T8 Current Handoff

Last updated: 2026-07-09

## Thread Role And Status

T8ai completed the Fig.3 `dx=0.25M` read-only publication-rendering
package from the T7bl-accepted archive.

Decision:

```text
GREEN / READY FOR T0 BATCH T7 IMAGE-REVIEW DECISION
```

This is a rendering/panel-polish package only. It is not a final
journal-grade claim, not pixel-level reproduction, and not new numerical
production.

## Completed Work

- Read and followed
  `docs/prompts/phase5_t8ai_fig3_dx0p25_publication_rendering_goal.md`.
- Used Goal mode.
- Read the required project context, T7/T8/T10 handoffs, closeout, literature
  review note, accepted production manifest, and Fig.3 plotting code/tests.
- Read/applied local `scientific-visualization` and
  `verification-before-completion` skill instructions.
- Generated a publication-rendering package under:
  - `runs/phase5/fig3_dx0p25_publication_rendering/`
- Updated:
  - `src/schwgw/viz/results.py`
  - `src/schwgw/cli.py`
  - `tests/regression/test_plot_cli.py`
  - `status.md`
  - `docs/handoffs/T8_current.md`
- Archived the previous T8 handoff at:
  - `docs/handoffs/archive/T8_2026-07-09_fig3_dx0p25_publication_rendering_pre.md`

## Source Archive

Read-only source archive:

- `runs/phase5/fig3_four_frequency_dx0p25_production/`

Accepted source NPZ hashes rechecked:

```text
b93582cf10a20f8340b105f6c82f1faed9398c93dd83c6a003270a3417d21873  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz
0de560ce7a2696074e708506240c69e43eb4d40520447ec378208b37f64c0132  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz
1f146a6c67192976538820b68e94118a3a6e636ba71ecebb045cbca123e5e7f2  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz
b560f9ae072495590e59ae7c49d54ee0353e395a0bd9d60b4cf5b717d11c34fc  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz
```

The accepted source archive was not modified.

## Output Artifacts

Required output directory:

- `runs/phase5/fig3_dx0p25_publication_rendering/`

Files generated:

```text
runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bicubic.pdf
runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bicubic.pdf.json
runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bicubic_600dpi.png
runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bicubic_600dpi.png.json
runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bilinear.pdf
runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bilinear.pdf.json
runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bilinear_600dpi.png
runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bilinear_600dpi.png.json
runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_nearest_audit_600dpi.png
runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_nearest_audit_600dpi.png.json
runs/phase5/fig3_dx0p25_publication_rendering/manifest.md
```

Output hashes:

```text
95d26e0301cf0391724fbf3e87b2a3704e9ecfdfed983e378536fdb78e8bd6e7  runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bicubic.pdf
79362716e047a9bb580e428a37765e25afd45d57f9ed76ba8ec31a7cfdc2cd76  runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bicubic.pdf.json
5bf6eade3928db09b5d9e37bc62c44bb054869aedb5a4efaf5e48062948c4b39  runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bicubic_600dpi.png
85d43b18d8d9d8a854b067f1e95868350eaa1ccc2695e8bb823c1cab7271dc7d  runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bicubic_600dpi.png.json
2321450e3b97d4f94f16cd9670b3fa684e140f3a3ff75f295829fe7817fac8bf  runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bilinear.pdf
1069193168707eda3542fd647e8b4aa8b3e6d1b71406c4734ef17753c2f13973  runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bilinear.pdf.json
baa91c8253ab31782f23624cf5b5b22d8542a596b76d41822f86a3b3a8f271df  runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bilinear_600dpi.png
40896e1dbf5c3923dd4c8bb6477b16c8935ae48af2d7a70df3ab8b852e4c1e45  runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_bilinear_600dpi.png.json
482b241443f7376d3c68e390b1c9613784bbd0e44dc487218971d2a8ad51fa1f  runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_nearest_audit_600dpi.png
3fc81632528dd2a8dddf8aa7866a9199d99f03ce1b97578647b54af518848384  runs/phase5/fig3_dx0p25_publication_rendering/fig3_dx0p25_publication_nearest_audit_600dpi.png.json
577eb73ab2fffba00ad4d57e06b229039d49c9e3d8f94535f3350e63854d48be  runs/phase5/fig3_dx0p25_publication_rendering/manifest.md
```

## Rendering Policy

- Nearest audit PNG:
  - `numerical_evidence_plot=true`
  - `display_only_smoothing=false`
- Bilinear PNG/PDF:
  - `numerical_evidence_plot=false`
  - `display_only_smoothing=true`
- Bicubic PNG/PDF:
  - `numerical_evidence_plot=false`
  - `display_only_smoothing=true`

The bilinear and bicubic outputs are display-only publication candidates.
They must not be used as additional numerical evidence.

## Image And Sidecar Summary

- PNG dimensions: `4260 x 2190`.
- PNG DPI: about `600`.
- PDF MediaBox: `7.1 x 3.65 in`.
- All PNGs were opened with PIL and were nonblank.
- Bilinear and bicubic PNGs were visually inspected.
- Every output has a JSON sidecar.
- Sidecars record source NPZ paths/SHA/sizes, source case IDs,
  `kM_values=[0.5,1.0,1.5,2.0]`, `components=h_plus/h_cross`,
  `quantity=real`, interpolation policy, display/audit policy,
  final adjacent-pair status, Q018 same-domain summary, requested DPI/output
  format, and non-claim flags.

Non-claim flags present in every sidecar:

- `not_final_journal_grade=true`
- `not_pixel_level_reproduction=true`
- `not_dx02_production=true`
- `not_kM4_production=true`
- `not_R60_production=true`
- `not_fig2_strict_psi4_artifact=true`

## Code Scope

Allowed source/test changes were used only for read-only rendering:

- Added `--style publication` to `plot-fig3-multifrequency-panel`.
- Added a publication render style for the existing Fig.3 multifrequency
  plotting helper.
- Added a focused CLI regression test for the publication style.

Not changed:

- `src/schwgw/scattering/`
- `src/schwgw/numerics/`
- `src/schwgw/perturbations/`
- `src/schwgw/backgrounds/`
- physics conventions
- thresholds
- `lmax`
- Q018/boundary/normalization policy
- accepted production NPZs or production manifest

## Verification Commands Run

```bash
find runs/phase5/fig3_dx0p25_publication_rendering -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig3_dx0p25_publication_rendering/*
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz src/schwgw/cli.py || true
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression/test_plot_cli.py tests/unit/test_viz_results.py
```

Additional independent inspection:

- opened all new PNGs with PIL;
- checked PNG dimensions/DPI/nonblank statistics;
- inspected PDF MediaBox dimensions;
- loaded every sidecar;
- checked source NPZ hashes and file sizes;
- checked interpolation/display policies;
- checked non-claim flags;
- checked no output path is inside the accepted source archive;
- checked manifest contents.

Results:

- Focused pytest: `59 passed in 5.84s`.
- Independent inspection: `PASS`.
- Static search had no matches in `src/schwgw/viz`.
- Static search matches in `src/schwgw/cli.py` are pre-existing non-rendering
  solver branches/import hooks; the new plot command path uses only
  `schwgw.viz`.
- `git status --short` was attempted, but this mounted path is not a Git
  repository (`fatal: not a git repository`).

## Incomplete Work

- No T7 image review has yet reviewed the new publication-rendering package.
- No final journal-grade or paper-level claim is made.
- No `dx=0.2M` evidence was generated.
- No `kM=4`, R60/R60_K4, Fig.2 strict `Psi4`, fixtures, dense Fig.5/Fig.6,
  Kirchhoff, Appendix D/E, or convention/threshold/`lmax`/boundary work was
  authorized or performed.

## Blocking Issues

No T8ai execution blocker remains.

Remaining gate:

- T0 must decide whether to schedule one batch T7 image review for the
  package under `runs/phase5/fig3_dx0p25_publication_rendering/`.

## Must-Read Files For A Future T7 Image Review

1. `project.md`
2. `status.md`
3. `docs/handoffs/T7_current.md`
4. `docs/handoffs/T8_current.md`
5. `docs/handoffs/T10_current.md`
6. `docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md`
7. `references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md`
8. `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`
9. `runs/phase5/fig3_dx0p25_publication_rendering/manifest.md`
10. Every JSON sidecar under
    `runs/phase5/fig3_dx0p25_publication_rendering/`

## Exact Next Task

Return to T0. T0 should decide whether to schedule a batch T7 image review for
the T8ai publication-rendering package, or pause Fig.3 and choose another
gated workstream.
