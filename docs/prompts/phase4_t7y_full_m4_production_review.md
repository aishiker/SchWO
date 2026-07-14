# Phase 4 T7y Prompt: Full M4-Production First-Pass Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7y`。

## 0. 前置条件

Only start after T8o has updated `status.md`. If T8o stopped or any required
artifact is missing, record the blocker and do not pass this review.

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/phase4_closeout.md`
4. `docs/m4_production_plan.md`
5. `docs/architecture.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `docs/prompts/phase4_t8o_full_m4_production_first_pass.md`
9. T8o changed files and artifact paths listed in `status.md`

Before task actions, check installed plugins/connectors/skills. Use directly
relevant ones only and record them in `status.md`.

## 2. Required Artifacts

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

## 3. Review Checklist

For each NPZ:

- `grid.kind == "xz_plane"`;
- shape is `121x121`;
- x/z domain is `[-30,30]` with spacing `0.5`;
- valid/invalid counts are `14592/49`;
- horizon mask matches `r <= 2M`;
- valid fields are finite, invalid fields are complex NaN;
- final adjacent pair passes selected and near-axis thresholds;
- cache metadata is bounded and plausible;
- warning metadata is JSON-safe;
- for `kM=2.0`, all suppressed-mode `valid_until_r` values cover
  `rmax=sqrt(30^2+30^2)`.

For panels:

- sidecars list the four source paths in `kM=[0.5,1.0,1.5,2.0]` order;
- `requested_dpi=300`;
- `output_format` matches PNG/PDF;
- components are `h_plus/h_cross`, quantity `real`, interpolation `nearest`;
- row-wise symmetric color limits are recorded;
- final pairs and pass flags are recorded;
- horizon and light-ring overlays are recorded;
- convention metadata is recorded.

Also confirm `src/schwgw/viz` remains read-only over saved results and does not
import solver/physics modules.

## 4. Verification

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
```

Run an independent metadata inspection script over all required artifacts. Do
not rerun solver to create missing artifacts.

## 5. Pass Conditions

Pass only if:

- all required artifacts exist;
- all four saved results satisfy the checklist;
- both PNG and PDF sidecars satisfy the checklist;
- full pytest passes;
- no hidden changes to physics/conventions/radial solver/thresholds/lmax were
  introduced;
- no scope creep into `kM=4`, R60_K2/R60_K4, or M5 transmission occurred.

## 6. Stop Conditions

Stop and update `status.md` if any required artifact is missing, final-pair
convergence fails, valid fields are non-finite, Q018 coverage is insufficient,
plotting imports solver/physics code, tests fail, or sidecar metadata is
incomplete.

## 7. status.md Update Requirements

Record changed files, commands, test results, artifact review summary,
production acceptance decision, open issues, and next-action recommendation.

If passed, recommend whether Phase 4 M4-production first pass can be marked
accepted, and identify remaining gated items: `kM=4`, R60_K2/R60_K4,
transmission, arbitrary incident direction.
