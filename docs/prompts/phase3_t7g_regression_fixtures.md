# Phase 3 T7g Prompt: Regression Fixture Metadata and First Benchmark Fixture

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7g`。

背景：

- T6j/T7f 已验证 Route B production bridge。
- Q014 已由 T0g 正式关闭。
- T4-lite 已将 Q015 triage 为 `k=0.2, ell=3` transition-regime radial diagnostic warning，不是 solver/field-convergence blocker。
- 本 slice 的目标是进入 regression fixture 阶段，但必须先把 fixture metadata/schema 做到能记录 radial diagnostics 和 Q015 warning。

先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `tests/regression/test_fixture_schema.py`
8. `tests/regression/fixtures/schema_template.json`
9. `tests/physics/test_phase3_validation.py`
10. `src/schwgw/scattering/partial_wave.py`

任务：

1. 复核当前状态
   - 确认 `status.md` 中 Q014 为 resolved。
   - 确认 Q015 为 non-blocking transition warning。
   - 不重新打开 Q014，不把 Q015 混入 Q014。

2. 扩展 regression fixture schema
   - 如果 schema 结构变化，将 `schema_version` 从 `0.1` 升到 `0.2`。
   - 更新 `tests/regression/test_fixture_schema.py` 和 `tests/regression/fixtures/schema_template.json`。
   - 新 schema 至少必须能记录：
     - `boundary_residual`
     - `wronskian_residual`
     - `flux_residual`
     - `match_condition_number`
     - `lmax_convergence`
     - `near_axis_lmax_convergence`
     - `lmax_values`
     - `final_lmax_pair`
     - `radial_diagnostic_warnings`
   - `radial_diagnostic_warnings` 应为 list；允许为空。若记录 Q015 warning，必须包含足够 metadata，例如 `kM`, `ell`, `sector`, `warning_type`, `raw_wronskian_residual`, `flux_residual`, `boundary_residual`, `barrier_action`, `expected_flux_scale`。

3. 生成第一组 numeric regression fixture
   - 优先生成一个小而可信的 committed JSON fixture：
     - 文件建议：`tests/regression/fixtures/R60_K1.json`
     - 参数：`M=1`, `r_obs=60`, `kM=1.0`, `A_plus=0.9+1.1j`, `A_cross=0.4+0.6j`
     - selected probes 使用 `docs/validation_plan.md` 的建议角点：`theta=0.0,0.05,0.2,1.0`, `phi=0.0`
   - 使用 adaptive `lmax` convergence loop；不要把 `lmax ~= k r` 当充分条件。
   - fixture 中存储 final adjacent pair 的 convergence metadata。
   - 如果 R60_K1 运行时间过长、adaptive convergence 不通过、输出不稳定、或 diagnostics 违反当前 policy，则不要提交 numeric fixture；只提交 schema 更新并在 `status.md` 写清 blocker。
   - 不要在本 slice 强行生成 `kM=2` 或 `kM=4` fixture。若 R60_K1 已稳定且运行成本很低，可以在 `status.md` 建议下一 slice 扩展。

4. 验证 fixture 可复现
   - 至少运行 regression schema tests。
   - 若生成 numeric fixture，重新读取该 fixture 并让 schema test 覆盖它。
   - 若有 fixture-generation helper/script，只保留小型、可维护、无 plotting 的实现；不要写 notebook 依赖。

允许修改：

- `tests/regression/test_fixture_schema.py`
- `tests/regression/fixtures/schema_template.json`
- `tests/regression/fixtures/*.json`
- 必要的小型 fixture generation helper 或 test helper
- `docs/validation_plan.md`，仅限 fixture schema/metadata policy
- `status.md`

禁止修改：

- 不修改 `src/schwgw/scattering/` 的物理公式。
- 不修改 `src/schwgw/numerics/` 的 radial solver。
- 不放宽 `docs/validation_plan.md` 的全局 Wronskian、boundary、lmax 阈值。
- 不生成 plotting 输出。
- 不生成大型二进制数据。
- 不把 direct flat oracle 输出当作 curved regression fixture。

停止条件：

- 需要改变 Fourier、tetrad、harmonic、RW gauge、master-variable 或 polarization convention。
- Adaptive final adjacent pair 不满足当前 `docs/numerics.md` / `docs/validation_plan.md` 阈值。
- Q015 warning 伴随 boundary residual 变大、非有限 radial data、field convergence failure、或 condition number 异常。
- 生成 fixture 需要修改 T4/T6 production code。
- R60_K1 运行成本不适合本地 fast/regression workflow。

必须运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_phase3_validation.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

完成时更新 `status.md`：

- changed files
- commands run
- test results
- generated fixture 文件路径，或明确说明为什么没有生成 numeric fixture
- diagnostics summary，包括 final `lmax` pair 和 radial warning metadata
- open issues
- next action，特别说明 T8 plotting 是否可以启动，或仍需 T7 后续 fixture slice
