# Phase 3 T7a Prompt: 物理验证设计与测试骨架

你现在是 `T7：验证与基准` 线程。本 slice 可在 T6a/T6b 之后启动，但不要阻塞 T6 实现。任务是为阶段 3 的物理验证建立测试骨架、阈值和 oracle 设计。若 T6d 尚未完成，允许写清晰的 skipped/expected-failing tests，但不得声称验证完成。

## 必读文件

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `docs/prompts/phase3_t6a_formula_interface_audit.md`
9. `docs/prompts/phase3_t6d_polarization_partial_wave.md`
10. 已存在的 `tests/unit/`, `tests/physics/`, `tests/regression/`

## 目标

建立阶段 3 validation structure：

- partial-wave convergence tests。
- `lmax ~ k r` scaling smoke tests。
- near-axis finite behavior tests。
- far-axis comparison with asymptotic scattering 的测试入口和阈值策略。
- unlensed / `M -> 0` limit 的 oracle strategy。
- parity sector consistency tests。
- polarization consistency tests。

## 允许修改

- `tests/physics/test_phase3_validation.py`
- `tests/unit/test_polarization_extraction.py` 仅补充 API-independent sign tests
- `tests/regression/test_fixture_schema.py` 仅当需要登记新字段 schema
- `docs/validation_plan.md`
- `status.md`

原则上不要修改 `src/`。若发现 T6 实现 bug，先写失败测试并记录；除非是很小的 import/export 修复，否则交回 T6。

## 验证设计要求

把测试分为两类：

1. Fast physics tests：本地默认可运行，不生成大型数据。
2. Slow/full validation tests：可标记为 `full_regression` 或保留为未默认运行的 benchmark plan。

建议 first-pass thresholds：

- `M -> 0` field relative error `< 1e-5`，沿用 `docs/validation_plan.md`。
- selected-probe `lmax` convergence `< 1e-4`，沿用 `docs/validation_plan.md`。
- near-axis finite behavior：所有输出和 diagnostics finite；小角度 probes 的 lmax-refinement relative change `< 1e-3` first pass。
- polarization sign tests 应接近 double precision，因为不依赖 ODE。
- far-axis asymptotic comparison first pass 可用 `< 5e-2`，但必须标为对照验证，不作为主算法定义。

若阈值需要调整，必须先更新 `docs/validation_plan.md` 并在 `status.md` 说明原因。

## 测试骨架建议

使用小参数避免 slow tests 混入 fast suite：

```text
M = 1
k = 0.5
r = 20
lmax values = [3, 4, 5]
A_plus = 0.9 + 0.2j
A_cross = 0.1 - 0.3j
probes = [(r, 0.0, 0.0), (r, 0.05, 0.0), (r, 0.4, 0.0)]
```

对 expensive cases 使用 markers，不让默认 `pytest -q` 变慢到不可接受。

## 停止条件

立即停止并更新 `status.md`：

- T6 public API 不存在且无法设计稳定 import boundary。
- `docs/physics_spec.md` 与 T6 prompt 的 observable convention 冲突。
- no-lens oracle 需要改变 T5 incident coefficients。
- 需要生成 numeric regression fixtures，但 T6d 尚未通过 smoke tests。
- 需要实现 plotting 或 transmission factor。

## 完成条件

- `tests/physics/test_phase3_validation.py` 存在，并且在 T6d 未完成时不会把 default pytest 错误地标为失败。
- `docs/validation_plan.md` 记录阶段 3 validation thresholds 或确认沿用 v0.1 thresholds。
- `status.md` 记录哪些 tests 是 ready、skipped、expected-failing 或等待 T6d。
- 当前可运行测试通过：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```
