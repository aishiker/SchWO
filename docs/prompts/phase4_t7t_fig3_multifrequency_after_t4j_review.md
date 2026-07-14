# Phase 4 T7t Prompt: Fig.3 Multi-Frequency Review After T4j/T8k

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7t`。

## 0. 前置条件

只有在 `status.md` 记录 T8k 已完成四频 saved results 和 2x4 read-only panel 后，
才做通过态复核。如果 T8k 停止或 artifacts 缺失，本任务只能记录 blocker，不得给出 pass。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/phase3_closeout.md`
6. `docs/architecture.md`
7. `docs/numerics.md`
8. `docs/validation_plan.md`
9. `docs/prompts/phase4_t8j_fig3_multifrequency_panel.md`
10. `docs/prompts/phase4_t4j_radial_bvp_mesh_failure.md`
11. `docs/prompts/phase4_t8k_resume_fig3_multifrequency.md`
12. T4j/T8k changed files listed in `status.md`

## 2. 目标

独立复核 T4j/T8k 后的 multi-frequency Fig.3-lite path 是否可信：

- Q017 是否真正解除或被更窄问题替代；
- T4j 是否没有通过 convention change、threshold relaxation、mode truncation 或 plotting workaround 隐藏 radial 问题；
- T8k 是否生成四个同网格 x-z saved results；
- read-only 2x4 panel 是否只读取 saved results；
- per-frequency convergence/metadata 是否满足 Phase 4 acceptance。

## 3. 必查 artifacts

```text
/tmp/t8j_li_fig3_xz_k0p5_hires.npz
/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz
/tmp/t8j_li_fig3_xz_k1p5_hires.npz
/tmp/t8j_li_fig3_xz_k2p0_hires.npz
/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png
/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png.json
```

## 4. 复核内容

### 4.1 T4j radial fix review

检查 T4j changed files 和 tests：

- no frozen convention changed;
- no T6 Route B change;
- no lmax truncation;
- no relaxed convergence thresholds;
- radial diagnostics remain structured and JSON-safe;
- any fallback policy is explicit in diagnostics;
- direct `k=1.5,r_out=300` targeted radial scan result is recorded.

### 4.2 Saved-result validation

对四个 NPZ 独立检查：

- `grid.kind == "xz_plane"`;
- x/z arrays identical and monotone over `[-30,30]` with step `1`;
- shape `(61,61)`;
- horizon mask matches `r <= 2M`;
- valid/invalid counts are consistent;
- valid `h_plus/h_cross` values are finite complex numbers;
- invalid entries are masked/NaN as expected;
- metadata contains `lmax_convergence_history`;
- final adjacent pair passed selected and near-axis thresholds;
- run-scoped radial cache metadata is bounded and plausible;
- radial warnings, if any, are structured and not acceptance-blocking unless severity says otherwise.

### 4.3 Panel validation

检查 panel sidecar：

- source paths are exactly the four accepted saved results;
- kM order is `[0.5,1.0,1.5,2.0]`;
- components are `h_plus` and `h_cross`;
- quantity is real part;
- interpolation is recorded;
- row-wise symmetric color scales are recorded;
- event horizon and light-ring overlay metadata are present;
- samples per wavelength are about `12.57`, `6.28`, `4.19`, `3.14`;
- sidecar records final convergence metadata for every source.

Also confirm `src/schwgw/viz` still has no imports or calls into solver/physics modules.

## 5. 验证命令

至少运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

并运行独立 metadata inspection script。不要重跑 solver 生成缺失 artifacts。

## 6. 通过条件

只有同时满足以下条件才可通过：

- Q017 no longer blocks T8j/T8k artifacts;
- four saved results exist and pass metadata/finiteness/convergence checks;
- panel and sidecar exist and are read-only over saved results;
- T4j did not hide failures by changing conventions, thresholds, or truncation;
- full pytest passes.

## 7. 停止条件

- 任一 required artifact 缺失；
- 任一 final adjacent pair fail；
- 任一 valid field 非有限；
- sidecar 缺少关键 provenance/convergence/sampling metadata；
- plotting code imports solver/physics modules；
- T4j radial fix 改变 physics convention 或隐藏 mode failure。

## 8. status.md 更新要求

完成后更新：

- changed files
- commands run
- test results
- artifact review summary
- Q017 final state
- open issues
- next action

如果通过，明确写明 multi-frequency Fig.3-lite accepted；如果失败，写明返回 T4 还是 T8。
