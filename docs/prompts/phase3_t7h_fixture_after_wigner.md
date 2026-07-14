# Phase 3 T7h Prompt: First Numeric Fixture After Wigner-D Hardening

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7h`。

启动条件：

- 只能在 T3h 完成并在 `status.md` 明确说明 Q016 high-`ell` Wigner-D overflow 已解决后启动。
- 如果 Q016 仍 open，不要生成 numeric fixture；回到 T3。

先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase3_t3h_high_ell_wigner.md`
8. `tests/regression/test_fixture_schema.py`
9. `tests/regression/fixtures/schema_template.json`
10. `tests/physics/test_phase3_validation.py`
11. `src/schwgw/scattering/partial_wave.py`

目标：

在 high-`ell` Wigner-D 修复后，重新尝试生成第一组可信 numeric regression fixture。优先尝试 R60_K1；如果 R60_K1 运行成本仍不适合 fast/local regression，则选择一个更小但已经由 T7f 物理验证支持的 first fixture。

任务：

1. 复核 Q016
   - 运行 high-`ell` Wigner-D / spin-weighted harmonic smoke check，确认 `ell=60,72` finite 且无 overflow。
   - 确认 T3h 没有改变 frozen Wigner-D convention。

2. 重新尝试 R60_K1
   - 参数：
     - `M=1`
     - `kM=1.0`
     - `r_obs=60`
     - `A_plus=0.9+1.1j`
     - `A_cross=0.4+0.6j`
     - probes: `theta=0.0,0.05,0.2,1.0`, `phi=0.0`
   - 使用 adaptive `lmax` convergence loop，不把 `lmax ~= k r` 当充分条件。
   - 记录每个 `lmax` 的 runtime、global convergence、near-axis convergence、max radial diagnostics。
   - 如果 R60_K1 在合理本地时间内完成且 final adjacent pair 通过阈值，则生成：
     - `tests/regression/fixtures/R60_K1.json`
   - 如果 R60_K1 仍过慢、未收敛或 diagnostics 不达标，不要强行提交 R60_K1。

3. fallback：更小但可信的 first fixture
   - 若 R60_K1 不适合 fast/local regression，优先选择 T7f 已验证过的 small fixture：
     - 建议 case id：`R20_K0p5`
     - `M=1`
     - `kM=0.5`
     - `r_obs=20`
     - `A_plus=0.9+0.2j`
     - `A_cross=0.1-0.3j`
     - probes: `theta=0.0,0.01,0.05,0.4`, `phi=0.0`
     - adaptive window should reproduce or improve T7f final pair `24->28`, max selected/near-axis relative change `~4.43e-8`.
   - 该 fallback fixture 必须在 metadata 中明确标记为 first numeric smoke/regression fixture，不是 paper-scale R60 benchmark。
   - 如果选择 `kM=0.2`，必须把 Q015 `ell=3` transition warning 写入 `radial_diagnostic_warnings`；如果选择 `kM=0.5` 且没有 warning，`radial_diagnostic_warnings` 可以为空。

4. fixture schema
   - 使用 schema v0.2。
   - 所有 numeric fixture 必须通过 `tests/regression/test_fixture_schema.py`。
   - `diagnostics` 必须包含：
     - `boundary_residual`
     - `wronskian_residual`
     - `flux_residual`
     - `match_condition_number`
     - `lmax_convergence`
     - `near_axis_lmax_convergence`
     - `lmax_values`
     - `final_lmax_pair`
     - `radial_diagnostic_warnings`

允许修改：

- `tests/regression/fixtures/*.json`
- `tests/regression/test_fixture_schema.py`，仅限 schema bugfix
- `docs/validation_plan.md`，仅限记录 first fixture policy
- `benchmarks/reference_data_registry.md`，如果需要登记 fixture
- `status.md`

禁止修改：

- 不修改 `src/` 物理实现。
- 不修改 Wigner-D convention。
- 不修改 radial solver 或 thresholds。
- 不生成 plotting 输出。
- 不生成大型二进制数据。

停止条件：

- Q016 仍未解决。
- R60_K1 和 fallback fixture 都无法满足 adaptive final-pair convergence。
- 需要修改 T4/T6/T3 production code 才能生成 fixture。
- fixture runtime 不适合本地 regression workflow，且没有更小可信 fallback。

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
- generated fixture path or reason no fixture was generated
- R60_K1 go/no-go and fallback decision
- final `lmax` pair and convergence diagnostics
- radial diagnostic warning metadata
- whether T8 plotting can start
