# Phase 0 T1 Prompt: 文献与物理约定冻结

你现在是 `T1：文献与物理约定` 线程。当前阶段是 Phase 0 / M0：项目启动与规格冻结。目标不是写求解器，而是冻结后续实现必须遵守的物理 convention 和公式来源，防止后面返工。

请先按顺序阅读：

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `references/manifest.md`
7. 相关 `references/notes/*.md`；如果 notes 还不存在，再查 `references/papers/*.pdf`

你的任务：

1. 冻结 `docs/physics_spec.md` 到 `v0.1`，只做 convention 和公式规格，不写 solver。
2. 明确并记录：
   - Fourier convention：时间因子、频域导数符号、boundary phase。
   - scalar spherical harmonics convention：归一化、Condon-Shortley phase、`theta/phi` 参数顺序。
   - spin-weighted spherical harmonics convention：定义、归一化、与 Wigner-D 的关系。
   - Wigner-D convention：Euler angles、index order、复共轭/相位约定。
   - `A_plus`, `A_cross`, `A_L`, `A_R` 定义。
   - RW gauge convention。
   - master variables `psi_even`, `psi_odd` 的 normalization。
   - `Psi_0`, `Psi_4` 到 `h_plus`, `h_cross` 的关系，尤其 `exp(-ikt)` 下 `h = -hddot/k^2` 的符号。
3. 在 `references/notes/` 中为目标论文和关键基础文献建立 Codex 可读公式笔记。不要只依赖 PDF 原文。
4. 更新 `docs/equation_map.md`：每个将来实现模块都要能追溯到 `docs/physics_spec.md`、notes 或 manifest 中的文献范围。
5. 更新 `status.md`：
   - 记录已冻结 convention。
   - 记录仍有歧义或需要文献核查的问题。
   - 记录 commands run。

边界：

- 不实现 `src/` 中的新物理代码。
- 不修改数值算法。
- 不修改 plotting 或 Weyl 实现代码。
- 如果发现现有公式实现和将要冻结的 convention 冲突，先在 `status.md` 标为 blocking issue，不要直接改代码。

退出条件：

- `docs/physics_spec.md` 明确标记为 `v0.1-frozen` 或列出未冻结项。
- `references/notes/` 至少包含目标论文的公式笔记。
- `docs/equation_map.md` 能覆盖 Phase 1 需要实现的 background、RW/Zerilli、incident wave、angular、Weyl/polarization 模块。
- `status.md` 有 T1 更新记录。
