# Phase 4 T7v Prompt: M4-Lite Closeout and Artifact Manifest

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7v`。

## 0. 任务定位

本任务是 Phase 4 的 `M4-lite / validation-grade` closeout。不要把它解释为
journal-grade production 图全部完成，也不要进入 transmission factor。

T7u 已接受 T8l/Q018 后的四频 Fig.3-lite saved artifacts。本 slice 的目标是
把 M4-lite 已完成内容、artifact manifest、剩余限制和下一阶段 gate 正式冻结，
防止后续线程混淆：

- Fig.3-lite validation-grade artifacts；
- future M4-production / journal-grade 高分辨率图；
- M5 transmission-factor work。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/phase3_closeout.md`
6. `docs/architecture.md`
7. `docs/numerics.md`
8. `docs/validation_plan.md`
9. `docs/prompts/phase4_t7u_fig3_multifrequency_q018_review.md`
10. T8l/T7u changed files and artifact paths listed in `status.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Required Artifacts

Verify these existing artifacts only; do not regenerate them unless a file is
corrupt and the reason is documented first.

```text
/tmp/t8j_li_fig3_xz_k0p5_hires.npz
/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz
/tmp/t8j_li_fig3_xz_k1p5_hires.npz
/tmp/t8j_li_fig3_xz_k2p0_hires.npz
/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png
/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png.json
```

## 3. Goals

1. Create or update `docs/phase4_closeout.md`.
2. Record an artifact manifest for the four NPZ files and the 2x4 panel:
   - path;
   - case id / `kM`;
   - grid shape and spacing;
   - valid/invalid counts;
   - final adjacent lmax pair and pass/fail;
   - radial warning counts and warning codes;
   - samples per wavelength;
   - plotting sidecar metadata.
3. State exactly what M4-lite validates:
   - YAML-driven saved computation;
   - raw complex NPZ/HDF5-capable output path;
   - x-z finite-radius wave-field schema;
   - read-only plotting over saved results;
   - adaptive lmax final-pair convergence metadata;
   - Q018 structured evanescent-tail warning metadata for current grid.
4. State exactly what M4-lite does not validate:
   - journal-grade high-resolution production maps;
   - `kM=4` stress;
   - `R60_K2` / `R60_K4` regression fixtures;
   - transmission factors;
   - arbitrary observer grids beyond saved `valid_until_r`;
   - arbitrary incident direction.
5. Update `status.md` with changed files, commands run, test results, open
   issues, and next-action recommendation.

## 4. Hard Limits

- Do not modify `src/`.
- Do not modify frozen Fourier, harmonic, tetrad, RW/Zerilli, Route B, or
  polarization conventions.
- Do not change thresholds or lmax values.
- Do not create new numeric fixtures.
- Do not run `kM=4` stress.
- Do not implement or plot transmission.
- Do not move accepted artifacts out of `/tmp`; just record their paths.

## 5. Verification

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run a small independent metadata inspection over the six required artifact
paths. It may be an inline Python script, but it must not call solver or physics
code.

## 6. Pass Conditions

Pass only if:

- all six artifacts exist and are readable;
- all four NPZ saved results have finite valid complex fields and correct masks;
- final adjacent lmax pairs are recorded as passing;
- `kM=2.0` Q018 warnings are structured and cover the current grid via
  `valid_until_r`;
- plotting remains read-only over saved results;
- `docs/phase4_closeout.md` clearly separates M4-lite, future M4-production,
  and M5 transmission;
- full pytest passes.

## 7. Stop Conditions

Stop and update `status.md` if any artifact is missing/corrupt, metadata is
inconsistent with T7u, Q018 warning metadata is missing, a final pair is not
passing, plotting imports solver/physics modules, or tests fail.

## 8. status.md Update Requirements

Update:

- current phase / target;
- M4 milestone row;
- T7 row;
- latest update log.

The next-action recommendation should be one of:

1. `M4-lite closed; T0 may choose M4-production high-resolution maps next`;
2. `M4-lite closed; T0 may open M5 transmission-normalization design next`;
3. `M4-lite not closed; blocker is ...`.

Do not provide implementation prompts for M4-production or M5 from inside this
T7v slice unless T0 has already added them.
