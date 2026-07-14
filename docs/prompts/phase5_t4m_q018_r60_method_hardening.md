# Phase 5 T4m Prompt: Q018 R60 Method Hardening For kM=2

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4m`。

T7ag 已经把 T4l 的 Q018 larger-domain readiness 复核为 **ACCEPT YELLOW**：
当前 `kM=2` Q018 policy 只覆盖 accepted `[-30,30]^2`，不覆盖 R60_K2
或更大 observer domain。你的任务是做一个小而严谨的 radial-method
hardening slice，目标是决定是否能科学地支持 R60_K2。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_larger_domain_readiness.md`
8. `docs/phase4_production_closeout.md`
9. `docs/phase5_m5_four_frequency_closeout.md`
10. `docs/prompts/phase5_t4l_q018_larger_domain_readiness.md`
11. `docs/prompts/phase5_t7ag_q018_larger_domain_readiness_review.md`
12. `src/schwgw/numerics/radial_solver.py`
13. `src/schwgw/numerics/boundary_conditions.py`
14. `tests/physics/test_radial_solver.py`

也要按项目规则先检查是否有已安装且适用的 plugin/skill；本 slice 是 bug/method
hardening，优先使用系统化 debugging / TDD 相关 skill。记录到 `status.md`。

## 2. Scope

允许修改：

- `src/schwgw/numerics/boundary_conditions.py`
- `src/schwgw/numerics/radial_solver.py`
- `tests/physics/test_radial_solver.py`
- 必要的 `tests/unit/test_radial_solver.py`
- `docs/numerics.md`
- 新增方法说明文档：
  `docs/q018_r60_method_hardening.md`
- `status.md`

除非确有必要，不要修改 scattering、IO、CLI、plotting、configs 或 artifacts。

禁止：

- 不要生成 R60_K2 wave-field artifact。
- 不要绘图。
- 不要运行 `kM=4`。
- 不要修改 Fourier/harmonic/tetrad/RWZ/Route B/Q005/Q014 convention。
- 不要降低 `lmax`。
- 不要放宽现有 residual/convergence threshold。
- 不要仅通过降低 `_EVANESCENT_SUPPRESSION_TAIL_ACTION` 或
  `_EVANESCENT_SUPPRESSION_BARRIER_ACTION` 来让 R60 通过。
- 不要把 scalar-field paper 的 `ell_max~kr` 截断直接当作 spin-2 证明。

## 3. Required Technical Direction

当前问题：

```text
k=2, ell>=153 的 evanescent_tail_suppressed solution 只保证到
valid_until_r≈42.47...53.33；R60_K2 需要 r=60。
```

你必须选择并实现/记录以下三种路线之一：

### Route A: evaluation-radius-aware suppression policy

给 `BoundaryConfig` 或 radial solver 增加显式、向后兼容的目标评估半径参数，
例如：

```python
BoundaryConfig(..., required_eval_radius: float | None = None)
```

语义：

- `None` 保持当前行为。
- 若设置为 `R`, 任何 structured suppression 必须保证 `valid_until_r >= R`。
- 如果当前 suppression policy 不能保证到 `R`，不得返回一个会在 `r=R`
  被当作有效的 zero-tail solution；必须改走更强 solver/bound，或抛出清楚的
  structured failure / no-go。

### Route B: conservative WKB tail bound at requested radius

实现一个保守的 helper，计算目标半径处的 local WKB tail action/bound，并把
spin-2 RW/Zerilli potential、sector、`ell`、`k`、target radius、outer turning point
都记录在 metadata 中。

只有在下列条件同时满足时，才允许把 target radius 标为 covered：

- bound 明确在 target radius 处评估，而不是从旧 `valid_until_r` 外推；
- bound 包含一个保守 polynomial prefactor allowance，避免忽略 reconstruction /
  tensor-harmonic 的 `ell` 依赖；
- bound 小于明确记录的 tolerance；
- T7 可以从 metadata 复算或审计这个结论。

如果你不能给出足够保守的 spin-2 prefactor allowance，不要强行 GREEN。

### Route C: documented no-go

如果 Route A/B 无法在本 slice 内科学完成，则不要写危险的近似。创建
`docs/q018_r60_method_hardening.md`，明确记录：

- 为什么当前 solver/policy 无法支持 R60_K2；
- 需要怎样的 rescaled/log-amplitude radial architecture；
- 哪些 tests 应作为未来 RED tests；
- T8 为什么仍不能跑 R60_K2。

Route C 是可接受结果，只要论证清楚、测试仍通过、状态记录完整。

## 4. Required Tests

先写测试，再改实现。

至少覆盖：

1. 当前默认行为不变：
   - `solve_radial_mode(Sector.ODD,153,2.0,..., BoundaryConfig(r_out=300))`
     仍返回 `evanescent_tail_suppressed`，且覆盖 accepted `[-30,30]^2`。
2. R60 请求不能被旧 policy 静默接受：
   - 若采用 Route A/B，应测试 `required_eval_radius=60.0` 的行为。
   - 允许结果是：
     - 返回一个 metadata 明确覆盖 `r=60` 的 solution；或
     - 抛出清楚的 `RuntimeError` / structured failure，说明 R60 未覆盖。
   - 不允许结果是旧的 `valid_until_r≈42.47` 仍被误认为 R60 covered。
3. Warning metadata 必须 JSON-safe，并包含足够字段让 T7 判断 target radius、
   covered/uncovered、bound 或 no-go 原因。
4. Full pytest 仍通过。

如果实现 Route B，还要加测试：

- bound 在 `r=60` 被实际计算并写入 warning metadata；
- metadata 中包含 `required_eval_radius`、`tail_action_at_required_radius`
  或等价字段、`tail_bound_at_required_radius` 或等价字段。

## 5. Diagnostics To Run

至少运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

还要运行一个 targeted snippet：

```text
M=1
k=2.0
r_out=300.0
required_eval_radius=60.0
ell in [153,156,168,180]
sector in [odd, even]
```

记录每个 mode：

- solver branch；
- whether R60 is covered；
- `valid_until_r`；
- warning metadata；
- if Route B: target-radius bound/action；
- if no-go: exact failure message。

## 6. Stop Conditions

停止并只更新文档/status，不要继续改代码，如果：

- 你发现 supporting R60_K2 需要重写 radial architecture，而不是小 slice；
- 你无法给出 spin-2 reconstruction-aware conservative bound；
- 任何 probe 单个 mode 超过 20 分钟；
- full pytest 失败且不是本 slice 能局部修复的问题；
- 你发现需要修改 physics convention。

## 7. status.md Update

结束时更新 `status.md`：

- changed files；
- files read；
- skill/plugin check；
- chosen Route A/B/C；
- tests added/changed；
- targeted radial diagnostic table；
- whether R60_K2 is GREEN/YELLOW/RED after this slice；
- commands run；
- test results；
- open issues；
- next action prompt recommendation for T7ah review。

不要声称 R60_K2 production 可以运行，除非你提供了可复核的 GREEN evidence。
