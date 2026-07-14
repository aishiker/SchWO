# Phase 4 T7z Prompt: M4-Production First-Pass Closeout

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7z`。

## 0. 任务定位

本任务是 Phase 4 的 `M4-production first-pass` closeout。T8o 已生成四个
`dx=dz=0.5M` production saved maps，T7y 已独立复核并接受这些 artifacts。
本 slice 的目标是把这批 production first-pass artifacts、适用范围和剩余 gate
正式冻结，防止后续把它和 `kM=4` stress、R60_K2/R60_K4 fixtures、M5
transmission 或 arbitrary incident direction 混在一起。

这不是新求解器开发任务，也不是绘图改进任务。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/phase3_closeout.md`
6. `docs/phase4_closeout.md`
7. `docs/m4_production_plan.md`
8. `docs/architecture.md`
9. `docs/numerics.md`
10. `docs/validation_plan.md`
11. `docs/prompts/phase4_t8o_full_m4_production_first_pass.md`
12. `docs/prompts/phase4_t7y_full_m4_production_review.md`
13. T8o/T7y changed files and artifact paths listed in `status.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Required Artifacts

Verify these existing artifacts only. Do not regenerate, move, rename, or edit
them unless a file is corrupt and the reason is documented first.

```text
/tmp/t8o_li_fig3_xz_k0p5_dx0p5.npz
/tmp/t8o_li_fig3_xz_k1p0_dx0p5.npz
/tmp/t8o_li_fig3_xz_k1p5_dx0p5.npz
/tmp/t8o_li_fig3_xz_k2p0_dx0p5.npz
/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.png
/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.png.json
/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf
/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf.json
```

## 3. Goals

1. Create `docs/phase4_production_closeout.md`.
2. Record an artifact manifest for the four production NPZ files and the
   PNG/PDF 2x4 panels:
   - path;
   - case id / `kM`;
   - grid domain, shape, and spacing;
   - valid/invalid counts;
   - final adjacent `lmax` pair and pass/fail;
   - radial cache counts;
   - radial warning counts and warning codes;
   - samples per wavelength;
   - plotting sidecar metadata.
3. State exactly what M4-production first pass validates:
   - full-domain `x/M,z/M in [-30,30]` Fig.3-style saved wave-field maps;
   - `dx=dz=0.5M`, `121x121` production sampling for `kM=[0.5,1.0,1.5,2.0]`;
   - raw complex NPZ output with masks and metadata;
   - PNG/PDF 300 DPI read-only plotting from saved results;
   - adaptive final-pair convergence metadata;
   - Q018 structured evanescent-tail metadata covering this domain.
4. State exactly what this closeout does not validate:
   - `kM=4` stress;
   - R60_K2/R60_K4 regression fixtures;
   - M5 transmission factors or Q005 normalization;
   - arbitrary incident direction;
   - larger observer domains beyond current Q018 `valid_until_r` coverage;
   - any claim of pixel-for-pixel reproduction of the reference paper.
5. Update `status.md` with changed files, commands run, test results, open
   issues, and next-action recommendation.

## 4. Hard Limits

- Do not modify `src/`.
- Do not modify frozen Fourier, harmonic, tetrad, RW/Zerilli, Route B, or
  polarization conventions.
- Do not change thresholds or `lmax` values.
- Do not create new numeric fixtures.
- Do not run `kM=4`.
- Do not run R60_K2/R60_K4.
- Do not implement or plot transmission.
- Do not implement arbitrary incident direction.
- Do not regenerate plots unless a sidecar/file readability check proves an
  existing artifact is corrupt.
- Do not move accepted artifacts out of `/tmp`; record their paths only.

## 5. Verification

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run a small independent metadata inspection over the eight required
artifact paths. It may be an inline Python script, but it must only load saved
files and sidecars; it must not call solver, scattering, radial, angular, or
physics code.

Run the read-only plotting boundary scan:

```bash
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
```

## 6. Pass Conditions

Pass only if:

- all eight artifacts exist and are readable;
- all four NPZ saved results have shape `(121,121)`, domain `[-30,30]^2`,
  spacing `dx=dz=0.5M`, valid/invalid counts `14592/49`, finite valid complex
  fields, and complex-NaN invalid fields;
- final adjacent `lmax` pairs are recorded as passing:
  `[[72,84],[96,108],[132,156],[156,180]]`;
- `kM=2.0` Q018 warnings are structured and cover the production domain via
  `valid_until_r > sqrt(30^2+30^2)`;
- PNG and PDF sidecars record `requested_dpi=300`, correct source order, final
  pairs, pass flags, grid spacing, overlays, and convention metadata;
- plotting remains read-only over saved results;
- `docs/phase4_production_closeout.md` clearly separates M4-production
  first-pass acceptance from future `kM=4`, R60 fixtures, M5 transmission, and
  arbitrary-direction work;
- full pytest passes.

## 7. Stop Conditions

Stop and update `status.md` if any required artifact is missing/corrupt,
metadata is inconsistent with T7y, Q018 warning metadata is missing or does not
cover the current grid, a final pair is not passing, plotting imports solver or
physics modules, or tests fail.

## 8. status.md Update Requirements

Update:

- current phase / target;
- M4 milestone row;
- T7 row;
- latest update log.

Recommended next-action wording after pass:

```text
M4-production first pass closed. Recommended next scientific slice: M5
transmission-normalization design for Q005, unless T0 explicitly chooses
`kM=4`, R60_K2/R60_K4, or arbitrary incident direction first.
```

Do not provide implementation prompts for M5 from inside this T7z slice unless
T0 has already added them.
