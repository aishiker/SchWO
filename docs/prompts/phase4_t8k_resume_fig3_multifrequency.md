# Phase 4 T8k Prompt: Resume Fig.3 Multi-Frequency After T4j

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8k`。

## 0. 前置条件

只有在 `status.md` 明确记录 T4j 已经解除或足够收窄 Q017 后，才开始本任务。
如果 Q017 仍 open 且没有 T4j 给出的可执行 radial policy，不要运行本任务；更新
`status.md` 后停止。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/architecture.md`
4. `docs/numerics.md`
5. `docs/validation_plan.md`
6. `docs/phase3_closeout.md`
7. `docs/prompts/phase4_t8j_fig3_multifrequency_panel.md`
8. `configs/li_fig3_xz_k0p5_hires.yaml`
9. `configs/li_fig3_xz_k1p5_hires.yaml`
10. `configs/li_fig3_xz_k2p0_hires.yaml`
11. `configs/r60_k1_li_fig3_lite_xz_hires.yaml`

## 2. 目标

恢复 T8j 未完成的真实 multi-frequency Fig.3-lite saved results：

- reuse accepted `kM=1` artifact:
  `/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz`
- reuse existing `kM=0.5` artifact if still valid:
  `/tmp/t8j_li_fig3_xz_k0p5_hires.npz`
- generate missing:
  `/tmp/t8j_li_fig3_xz_k1p5_hires.npz`
  `/tmp/t8j_li_fig3_xz_k2p0_hires.npz`
- generate read-only 2x4 panel:
  `/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png`

保持 T8j 的原始物理参数、grid、`lmax` 和 convergence windows。

## 3. 禁止事项

- 不修改 T2-T6 physics/convention code。
- 不修改 radial solver；如果 radial 层仍失败，返回 T4/T0。
- 不降低 `lmax`。
- 不放松 convergence threshold。
- 不生成 `R60_K2`/`R60_K4` regression fixtures。
- 不运行 `kM=4` stress benchmark。
- 不实现 transmission factor。
- 绘图仍然只能读取 saved results，不得重新计算核心物理。

## 4. 执行步骤

### 4.1 检查已有 artifacts

检查并记录：

- `/tmp/t8j_li_fig3_xz_k0p5_hires.npz`
- `/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz`

确认它们：

- `grid.kind == "xz_plane"`
- shape `(61,61)`
- valid/invalid counts 与 horizon mask 一致
- final adjacent pair passed
- valid complex fields finite
- metadata 中包含 run-scoped radial cache 与 convergence history

如果 `kM=0.5` artifact 缺失或 metadata 不一致，可以用原 config 重新生成。

### 4.2 生成缺失频率

依次运行：

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_k1p5_hires.yaml --out /tmp/t8j_li_fig3_xz_k1p5_hires.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_k2p0_hires.yaml --out /tmp/t8j_li_fig3_xz_k2p0_hires.npz
```

每个 run 完成后立即检查 metadata 和 field finiteness。若任一频率失败，不要继续伪造 panel；
更新 `status.md` 并停止。

### 4.3 生成 read-only panel

四个文件都存在并通过检查后，运行 multi-frequency panel CLI。输入顺序必须是：

```text
kM=0.5, kM=1.0, kM=1.5, kM=2.0
```

panel 必须：

- top row: `real(h_plus)`
- bottom row: `real(h_cross)`
- use matching x-z grid
- use row-wise symmetric color scales
- overlay event horizon and light ring
- sidecar records source paths, case ids, kM values, final convergence metadata,
  samples per wavelength, grid spacing, interpolation, color scales, overlays, and conventions

## 5. 验证命令

至少运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

并用一个检查脚本确认四个 NPZ 的 metadata、finite fields、final convergence pair 和 samples per wavelength。

## 6. 停止条件

- T4j 没有解除/收窄 Q017。
- `kM=1.5` 或 `kM=2.0` 仍然 radial failure。
- 单个 saved run 超过 45 分钟仍未写出结果。
- final adjacent pair 不通过。
- valid fields 出现非有限值。
- plotting path 调用了 solver 或 physics modules。
- sidecar metadata 缺少 source/convergence/sampling/provenance 信息。

## 7. status.md 更新要求

记录：

- changed files
- commands run
- runtimes
- artifact paths
- per-frequency convergence result
- per-frequency valid/invalid counts
- samples per wavelength
- test results
- open issues
- whether T7t independent review may proceed

如果 T8k 完成，下一步发给 T7：

```text
你现在是 T7t。请读取并严格执行 docs/prompts/phase4_t7t_fig3_multifrequency_after_t4j_review.md。
```
