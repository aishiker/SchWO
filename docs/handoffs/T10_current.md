# T10 Current Handoff

Last updated: 2026-08-01

Thread: T10, literature and numerical-method support.

## 2026-08-01 project sync

T10i is historical and no T10 task is active. The present literature need is
more specific than render polish: determine whether the paper, supplementary
material, author code, or cited conventions specify the complex-frequency
reality bridge, total/scattered field used in Fig.4, Kirchhoff normalization
in Figs.5/6, and apparent-mode projection in Fig.7. Literature findings must
be converted into numerical point regressions before another production run.
See `status.md`.

## Current Status

T10i is complete.

Latest recommendation label:

```text
NEEDS_READONLY_RENDER_POLISH
```

The current next gate is:

```text
T7bl independent review of references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md
```

T10i was review-only.  It did not run the solver, call production/scattering
APIs, regenerate plots, create artifacts, modify source/tests/configs, or
mutate accepted `runs/` artifacts.

## Completed Work

- Created:
  - `references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md`
- Updated:
  - `status.md`
  - `docs/handoffs/T10_current.md`
- Read the required T10i prompt:
  - `docs/prompts/phase5_t10i_fig3_dx0p25_figure_quality_literature_goal.md`
- Read required project/context files:
  - `project.md`
  - `status.md`
  - `docs/handoffs/README.md`
  - `docs/handoffs/T0_current.md`
  - `docs/handoffs/T7_current.md`
  - `docs/handoffs/T8_current.md`
  - `docs/handoffs/T10_current.md`
  - `docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md`
  - `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`
  - `references/manifest.md`
  - `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
  - `references/notes/t10d_li_hou_zhao_figure_inventory.md`
  - `references/notes/t10h_fig2_fig3_journal_readiness.md`
- Checked skill/plugin relevance:
  - Read/applied local `scientific-visualization` skill for publication figure quality criteria.
  - No external connector/web lookup/PDF reread was needed.
- Inspected accepted archive metadata:
  - Archive-level nearest and bilinear PNGs are `3360x1680`, RGBA, about 300 DPI.
  - NPZ metadata records `kM=[0.5,1.0,1.5,2.0]`, `A_plus=0.9+1.1i`,
    `A_cross=0.4+0.6i`, `x,z in [-30,30]`, shape `(241,241)`, valid count
    `57884`, and final-pair pass.
  - Sidecars distinguish nearest audit rendering from bilinear display-only
    smoothing.

## T10i Findings

- The accepted archive matches Li-Hou-Zhao Fig.3 physical content:
  physical `h_plus/h_cross`, four frequencies, `[-30,30]^2`, paper amplitudes,
  event-horizon/light-ring overlays, and project/paper `exp(-i k t)` convention.
- `dx=0.25M` saved-data resolution is scientifically adequate within current
  project conventions:
  - samples per wavelength are about `[50.27, 25.13, 16.76, 12.57]`;
  - all four final adjacent pairs `[156,180]` passed;
  - Q018 is zero-warning for `kM=0.5,1.0,1.5`;
  - `kM=2.0` has structured same-domain `evanescent_tail_suppressed` warnings
    covering `rmax`.
- Current visual roughness, if any, is primarily a rendering/layout issue:
  nearest exposes grid cells for audit, while bilinear smooths display without
  changing physical stripe structure.
- `dx=0.2M` is not justified now.  It should remain gated until after T7bl and
  any read-only publication-rendering review.
- The next lowest-risk branch is read-only publication-style rendering from
  the accepted NPZ files, followed by T7 image review.

## Incomplete Work

- T7bl has not reviewed T10i.
- No read-only publication-style rendering pass has been generated.
- No final journal-grade or paper-level Fig.3 claim is authorized.
- `dx=0.2M` planning remains gated.

## Blocking Issues

None for T7bl review.

For final publication promotion:

- Need T7bl decision.
- Need a read-only publication-rendering pass if T7bl agrees with T10i.
- Need a follow-up T7 image review before any final journal-grade claim.

## Non-Blocking Warnings

- Nearest is numerical/audit provenance, not a polished publication render.
- Bilinear is display-only smoothing and must not be used as numerical
  evidence.
- Q018 evidence is same-domain only for `[-30,30]^2`; it does not validate
  `kM=4`, R60/R60_K4, or larger domains.
- Pixel-level reproduction of Li-Hou-Zhao Fig.3 is still not claimed.
- Fig.2 strict `Psi4`, dense Fig.5/Fig.6, Kirchhoff, and Appendix D/E remain
  separate workstreams.

## Must-Read Files For Next Thread

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/handoffs/T10_current.md`
7. `docs/prompts/phase5_t7bl_fig3_dx0p25_figure_quality_review.md`
8. `references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md`
9. `docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md`
10. `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`
11. all ten PNG sidecars under `runs/phase5/fig3_four_frequency_dx0p25_production/`

## Frozen Decisions

- Fourier convention remains `exp(-i k t)`.
- Route B packaged polarization remains the production path for physical
  `h_plus/h_cross`.
- Strict NP scalars and packaged polarization scalars remain separated.
- T8ah/T7bj/T7bk accepted the Option A four-frequency `dx=0.25M` production
  archive.
- Nearest is the audit/numerical-provenance plot.
- Bilinear is display-only smoothing and not numerical evidence.
- `dx=0.2M`, `kM=4`, R60/R60_K4, Fig.2 strict `Psi4`, fixtures, dense
  Fig.5/Fig.6, Kirchhoff, and Appendix D/E remain gated.

## Forbidden Actions

- Do not run solvers from T10.
- Do not call production/scattering/radial APIs from T10 review tasks.
- Do not generate NPZ/HDF5/CSV/PNG/PDF artifacts from T10i.
- Do not modify `src`, tests, configs, accepted artifacts, plotting artifacts,
  fixtures, or `runs/`.
- Do not rerun plotting or overwrite accepted figures.
- Do not run `dx=0.2M` or `kM=4`.
- Do not claim final journal-grade readiness from T10i alone.
- Do not generalize Q018 beyond the accepted same-domain archive.

## Superseded Prompts

Completed T10 prompts that should not be rerun unless inconsistency is found:

- `docs/prompts/phase5_t10e_fig4_fig5_reproduction_planning.md`
- `docs/prompts/phase5_t10f_fig5_fig6_tablei_extraction_plan.md`
- `docs/prompts/phase5_t10g_fig5_fig6_dense_kirchhoff_readiness_goal.md`
- `docs/prompts/phase5_t10i_fig3_dx0p25_figure_quality_literature_goal.md`

T10h was user-specified directly in Goal mode and did not have a separate
prompt file.

## Exact Next Task

Run:

```text
你现在是 T7bl。请读取并严格执行 docs/prompts/phase5_t7bl_fig3_dx0p25_figure_quality_review.md。
```

## Allowed / Forbidden Files For T7bl

Allowed:

- `status.md`
- `docs/handoffs/T7_current.md`
- any T7bl review note if required by its prompt

Forbidden unless explicitly opened by T7bl's prompt:

- `src/`
- tests
- configs
- accepted artifacts under `runs/phase5/fig3_four_frequency_dx0p25_production/`
- generated figures
- fixtures

## Verification Commands

T10i verification commands:

```bash
test -f references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md
test -f runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md
rg -n "READY_FOR_T7_FIGURE_QUALITY_REVIEW|NEEDS_READONLY_RENDER_POLISH|NEEDS_DX02_PLANNING|BLOCKED_BY_LITERATURE_CONVENTION|dx=0\\.25|dx=0\\.2|Li-Hou-Zhao|Fig\\.3|samples per wavelength|Q018|nearest|bilinear|non-claim" references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md
```

## Definition Of Done For T10i

- T10i note exists and answers the prompt's six review questions.
- `status.md` records changed files, files read, commands/checks, skill/plugin
  use, tests, open issues, and exact T7bl prompt.
- This handoff reflects T10i as the latest T10 work.
- No source/test/config/accepted-artifact mutation occurred.
- No solver, plot regeneration, fixture generation, `dx=0.2M`, or `kM=4` work
  was performed.
