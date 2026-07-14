# Workstreams / Codex threads

版本：v0.1-design

## 总规则

每个线程必须：

1. 先读 `project.md`、`status.md` 和本线程相关文档。
2. 涉及物理公式、文献依据或 convention 时，先读 `references/manifest.md`，再读相关 `references/notes/*.md`；必要时才回到 `references/papers/*.pdf`。
3. 开始任务前在 `status.md` 中登记。
4. 修改代码后运行本线程相关 tests。
5. 完成后更新 `status.md`：改动、测试结果、未解决问题。
6. 不跨线程重构，除非先在 `status.md` 提交 interface decision。

## T0：项目协调与规格冻结

职责：

- 维护 `project.md`、`status.md`。
- 冻结 milestone 和接口变更。
- 审查是否出现重复公式实现或 convention 冲突。

交付：

- 更新的状态文件。
- 合并前 checklist。
- `convention_hash` 生成规则。

验收：

- 所有线程能从 status 恢复上下文。
- 接口变更都有 decision log。

## T1：文献与物理约定

职责：

- 整理目标论文和基础文献中的公式。
- 固定 Fourier convention、harmonic convention、Weyl scalar signs、tetrad convention。
- 维护 `references/manifest.md`：每篇文献的用途、优先级、对应模块、关键公式范围。
- 在 `references/notes/` 中整理 Codex 可复用的公式笔记、符号表、convention 对照和推导检查。
- 建立并维护 `docs/equation_map.md`。

交付：

- `docs/physics_spec.md` 完整版。
- `references/manifest.md`。
- `references/notes/*.md`。
- `docs/equation_map.md`。
- `benchmarks/reference_parameters.md`。

验收：

- 每个代码模块引用的物理公式都能回到本文件。
- 每个实现公式能追溯到 `references/notes/` 或 `references/manifest.md` 中登记的文献范围。
- 至少列出 10 个 sign/normalization traps。

## T2：背景与主方程

职责：

- 实现 `SchwarzschildBackground`。
- 实现 RW/Zerilli potentials。
- 实现 radial ODE RHS。

交付：

- `src/schwgw/backgrounds/schwarzschild.py`
- `src/schwgw/perturbations/potentials.py`
- `src/schwgw/perturbations/rwz.py`
- unit tests。

验收：

- `dr_star/dr = 1/f` 数值测试通过。
- potentials 在 horizon 处趋近 0。
- infinity 极限与 `l(l+1)/r^2` 主导项一致。

## T3：角向基与旋转

职责：

- scalar spherical harmonics。
- spin-weighted spherical harmonics。
- Wigner-D。
- Tensor harmonic normalization registry。

交付：

- `src/schwgw/angular/*`
- angular unit tests。

验收：

- 数值正交归一测试通过。
- `_sY_lm` 与 Wigner-D 定义一致。
- `+z` 入射下只激活 `m=±2`。

## T4：径向 ODE 与匹配

职责：

- 实现 complex ODE integration。
- 实现 horizon ingoing boundary condition。
- 实现 outer matching。
- 计算 phase shift/transmission。

交付：

- `src/schwgw/numerics/radial_solver.py`
- `src/schwgw/numerics/boundary_conditions.py`
- `src/schwgw/numerics/matching.py`

验收：

- 单个 `(l,k,sector)` 可求解。
- Wronskian / flux residual 在阈值内。
- 改变 `r_out` 后 phase shift 稳定。

## T5：入射平面波与边界系数

职责：

- `A_plus/A_cross` 到 `A_L/A_R`。
- `A_lm^(±)` 和 `c_lm^(±)`。
- M→0 平面波测试的输入构造。

交付：

- `src/schwgw/waves/incident.py`
- `src/schwgw/waves/polarizations.py`

验收：

- 对 `+z` 入射，非零模式为 `m=±2`。
- circular polarization 特例符号正确。
- M→0 master function 与 spherical Bessel 形式一致。

## T6：重构、Weyl 和极化

职责：

- RW-gauge metric reconstruction。
- Weyl scalar assembly。
- tetrad transformation。
- `h_plus`, `h_cross` 提取。

交付：

- `src/schwgw/perturbations/reconstruction.py`
- `src/schwgw/scattering/weyl.py`
- `src/schwgw/scattering/tetrad.py`
- `src/schwgw/scattering/observables.py`

验收：

- 频域 `h = -hddot/k^2` 测试通过。
- 平面波无 lens 时恢复输入极化。
- Weyl scalar 维度和 spin weight 一致。

## T7：验证与基准

职责：

- 建立 test matrix。
- 生成 reference fixtures。
- 写 regression threshold。

交付：

- `docs/validation_plan.md`
- `tests/unit`, `tests/physics`, `tests/regression`
- `benchmarks/reference_data_registry.md`

验收：

- 所有核心模块至少一项 unit test。
- 至少一个 end-to-end small run regression。
- status 中记录误差阈值和最后结果。

## T8：可视化与 CLI

职责：

- 配置驱动运行。
- HDF5/NPZ output。
- wave field、diffraction、convergence、transmission plots。

交付：

- `src/schwgw/io/*`
- `src/schwgw/viz/*`
- `examples/*`
- CLI entry points。

验收：

- 一条命令生成 results 文件。
- 一条命令从 results 生成图，不重新计算物理公式。
- 图像 metadata 记录 component、normalization、phase。

## T9：扩展接口

职责：

- 抽象新黑洞接入接口。
- 保证 Schwarzschild 实现是接口的一个 backend。
- 写 mock background/sector 测试。

交付：

- `docs/extension_interface.md`
- `src/schwgw/backgrounds/base.py`
- `src/schwgw/perturbations/sectors.py`

验收：

- mock background 可以注册。
- mock sector 可以被 radial solver 调用。
- Schwarzschild end-to-end 不因抽象层破坏。
