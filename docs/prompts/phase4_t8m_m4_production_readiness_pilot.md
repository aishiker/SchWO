# Phase 4 T8m Prompt: M4-Production Readiness Pilot

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8m`。

## 0. 任务定位

M4-lite 已由 T7v 关闭。这个 slice 不是完整 journal-grade production run，
而是 M4-production readiness pilot：为后续高分辨率 finite-radius wave-field /
diffraction maps 明确采样、运行成本、metadata、图像质量和停止条件。

不要进入 M5 transmission，不要生成 R60_K2/R60_K4 regression fixtures，不要跑
`kM=4` stress。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/phase4_closeout.md`
4. `docs/architecture.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/physics_spec.md`
8. `docs/equation_map.md`
9. existing Fig.3-lite configs in `configs/`
10. T8/T7 changed files listed in `status.md` for T8i/T8j/T8l/T7u/T7v

Before task actions, check installed plugins/connectors/skills. For figure
quality decisions, use the available `scientific-visualization` skill guidance
if accessible, and record it in `status.md`.

## 2. Goals

1. Create `docs/m4_production_plan.md`.
2. Define a production-map target matrix, without running the full matrix:
   - primary paper-like Fig.3 frequencies: `kM=[0.5,1.0,1.5,2.0]`;
   - current domain: `x/M,z/M in [-30,30]`;
   - candidate production spacings:
     - `dx=dz=0.5M` for `kM<=2` as the first production target;
     - `dx=dz=0.25M` only as a future `kM=4` stress candidate, not run now.
3. Estimate runtime, memory, file size, and cache behavior from existing
   accepted artifacts and any allowed pilot.
4. Specify image-quality requirements for journal-grade figures:
   - saved-data resolution, not just PNG DPI;
   - 300 DPI minimum export;
   - row-wise symmetric color scales;
   - horizon/light-ring overlays;
   - sidecar records grid spacing, samples per wavelength, interpolation,
     color scale, source paths, conventions, and convergence final pairs.
5. Check whether current CLI/config schema can support production grids
   ergonomically. If explicit arrays are too large, document whether a future
   range-based config schema is needed before full production.
6. Optionally run one bounded pilot only if it is cheap enough:
   - preferred pilot: `kM=2.0`, same physics/convergence as accepted T8l,
     but a small high-resolution x-z subdomain or sparse test grid that
     verifies `dx=0.5M` metadata and plotting behavior;
   - hard runtime cap: 30 minutes;
   - if a pilot requires awkward manual YAML arrays or risks exceeding the cap,
     skip it and document the blocker.

## 3. Hard Limits

- Do not modify T2-T6 physics or frozen conventions.
- Do not modify radial solver behavior.
- Do not relax thresholds or reduce accepted `lmax` windows to hide failures.
- Do not run the full four-frequency production grid.
- Do not run `kM=4`.
- Do not generate R60_K2/R60_K4 fixtures.
- Do not implement transmission.
- Plotting must remain read-only over saved results.
- Any new config must be a pilot/template config, clearly named as non-final.

## 4. Required Analysis

Use existing accepted artifact metadata:

```text
/tmp/t8j_li_fig3_xz_k0p5_hires.npz
/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz
/tmp/t8j_li_fig3_xz_k1p5_hires.npz
/tmp/t8j_li_fig3_xz_k2p0_hires.npz
/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png.json
```

Compute or record:

- grid point scaling from `61x61` to `121x121` for `dx=0.5M`;
- expected samples per wavelength for each `kM`;
- current per-frequency runtime records, especially `kM=2.0 real 628.54s`;
- whether radial cache unique-solve count should remain tied to `(sector,ell,k)`
  rather than grid-point count;
- Q018 finite-radius coverage implication for same domain but denser grid;
- future risk if domain expands beyond `rmax=sqrt(30^2+30^2)`.

## 5. Verification

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If a pilot artifact is generated, inspect it for finite valid fields,
correct masks, convergence metadata, warning metadata, and read-only plotting
sidecar. Do not call solver from plotting.

## 6. Stop Conditions

Stop and update `status.md` if:

- the current config schema cannot express the pilot safely;
- a pilot exceeds 30 minutes;
- final-pair convergence fails;
- `kM=2.0` Q018 warning metadata does not cover the pilot grid;
- fields are non-finite on valid points;
- plotting imports solver/physics code;
- tests fail.

## 7. status.md Update Requirements

Record:

- changed files;
- whether a pilot was run or skipped;
- commands and runtimes;
- artifact paths if any;
- production readiness conclusion;
- open issues;
- whether T7w may review.

If T8m completes without blockers, next prompt:

```text
你现在是 T7w。请读取并严格执行 docs/prompts/phase4_t7w_m4_production_readiness_review.md。
```
