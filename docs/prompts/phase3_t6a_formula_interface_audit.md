# Phase 3 T6a Prompt: 公式审计与接口冻结

你现在是 `T6：metric reconstruction, Weyl scalars, polarization extraction` 线程。本 slice 只做公式审计和接口冻结，不写大规模实现。阶段 3 已进入数值物理主链，目标是先把高风险公式、符号和 public API 锁住，避免后续返工。

## 必读文件

按顺序阅读：

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/architecture.md`
7. `docs/numerics.md`
8. `docs/validation_plan.md`
9. `references/manifest.md`
10. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
11. `src/schwgw/backgrounds/schwarzschild.py`
12. `src/schwgw/perturbations/potentials.py`
13. `src/schwgw/numerics/radial_solver.py`
14. `src/schwgw/waves/incident.py`
15. `src/schwgw/angular/spin_weighted.py`
16. `src/schwgw/angular/wigner.py`

## 目标

建立 T6 后续实现前必须遵守的公式和接口清单：

- RW-gauge metric reconstruction operators `J_l^(a)` 的输入、输出和依赖导数。
- Weyl scalar mode components `Z_{n,lm}^{(±)}` 的来源、spin weight 和 assembly rule。
- Kinnersley tetrad 与 incident-wave-aligned tetrad 的坐标/签名约定。
- Wigner-D based `Psi_hat` transformation 的 active/passive convention 检查项。
- `hddot_plus/cross` 和 `h_plus/cross = -hddot/k^2` 的 complex-amplitude convention。
- high-level observable API 的最小形状，不实现 plotting。

## 允许修改

- `docs/equation_map.md`
- `references/notes/phase3_formula_audit.md`
- `docs/prompts/phase3_t6*.md` 仅当发现接口 prompt 需要同步修正
- `status.md`

本 slice 不应修改 `src/` 或 `tests/`。如果发现一个很小的 import/export 损坏，也先记录，不要顺手修。

## 审计清单

逐项核对并记录：

- `docs/physics_spec.md` Sec. 8-9 是否足够支撑 Eq. (28)-(42) 实现。
- `references/notes/li_hou_zhao_2025_spin_wave_optics.md` 是否已经整理出 reconstruction 和 Weyl 公式；若没有，补 `references/notes/phase3_formula_audit.md`，不要直接只依赖 PDF。
- 每个 `J_l^(a)` 需要 `psi`、`dpsi/dr`、`dpsi/dr_star`、`d2psi/dr_star2` 还是可用 master equation 消去。
- T4 `RadialSolution` 已暴露的 derivative 是否满足 reconstruction 使用；若不满足，记录最小 API 缺口。
- T3 spin-weighted harmonic convention 是否与 T6 Weyl mode spin weights 相容。
- T5 incident coefficient normalization 是否能直接乘到 radial master functions。

## 建议接口草案

只在文档中冻结，不在本 slice 实现：

```text
src/schwgw/perturbations/reconstruction.py
  MetricModeComponents
  reconstruct_metric_mode(sector, ell, k, r, psi, dpsi_dr, background)

src/schwgw/scattering/tetrads.py
  kinnersley_tetrad(background, r, theta)
  incident_cartesian_tetrad()
  tetrad_inner_products(...)

src/schwgw/scattering/weyl.py
  WeylModeComponents
  weyl_mode_components(sector, ell, m, k, r, theta, phi, metric_mode, background)
  assemble_weyl_scalars(...)
  transform_weyl_to_incident_tetrad(...)

src/schwgw/scattering/observables.py
  PolarizationResult
  polarization_from_weyl(k, psi0_hat, psi4_hat)
```

若现有代码风格建议不同命名，可以调整，但必须在 `docs/equation_map.md` 和 `status.md` 说明。

## 停止条件

立即停止并更新 `status.md`：

- 需要修改 `docs/physics_spec.md v0.1-frozen` 才能继续。
- Eq. (28)-(42) 在 notes 中缺失或存在无法消除的 sign/normalization 冲突。
- 发现 T2-T5 public API 无法支撑 T6，且不是小型 adapter 能解决。
- 需要实现 plotting、transmission factor 或 generic incident direction 才能完成本 slice。
- 需要生成 numeric regression fixtures，但 T6 公式尚未审计完成。

## 完成条件

- `references/notes/phase3_formula_audit.md` 存在，列出 T6 实现将使用的公式、符号、输入输出、未决风险。
- `docs/equation_map.md` 中 T6 相关条目更新到足够指导实现。
- `status.md` 记录 changed files、commands/checks、结论、open issues。
- 没有引入 T6 源码实现。
