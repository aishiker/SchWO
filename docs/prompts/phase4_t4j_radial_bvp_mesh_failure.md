# Phase 4 T4j Prompt: kM=1.5 Radial BVP Mesh-Node Failure

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4j`。

## 0. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/phase3_closeout.md`
8. `src/schwgw/numerics/radial_solver.py`
9. `src/schwgw/numerics/boundary_conditions.py`
10. `tests/unit/test_radial_solver.py`
11. `tests/physics/test_radial_solver.py`
12. `configs/li_fig3_xz_k1p5_hires.yaml`

## 1. 背景

T8j 已经实现 read-only multi-frequency plotting interface，并成功生成
`kM=0.5` x-z saved result。但真实 `kM=1.5` run 在写出 NPZ 前停止：

```text
Stabilized radial BVP solve failed: The maximum number of mesh nodes is exceeded.
```

T0 已做只读定位，失败不是绘图层问题，而是单个 radial mode 首次失败：

```text
config: k=1.5, lmax=156, r_out=300, rtol=1e-10, atol=1e-12
first failure: sector=odd, ell=10, barrier_action≈8.54602
```

临界模额外诊断：

```text
ell=9  odd/even: outward_shooting succeeds, barrier_action≈5.136
ell=10 odd/even: outward_shooting succeeds, BVP fails max_nodes
ell=11 odd/even: outward_shooting succeeds with worse raw Wronskian, BVP fails max_nodes
ell=12 odd/even: outward_shooting succeeds with poor raw Wronskian, BVP fails max_nodes
```

这看起来像高频、长 `r_*` 区间上 BVP 分支策略或 BVP formulation 的数值问题。
不要把它归因给 T8，也不要通过降低 `lmax`、放松 convergence threshold、删除 mode、
插值平滑图像或改变物理 convention 来绕过。

## 2. 目标

找出并修复 `kM=1.5, r_out=300` Fig.3-lite 配置下 stabilized radial BVP
在 transition/high-barrier modes 上耗尽 mesh nodes 的问题。

修复应保持 T4 public API：

```python
solve_radial_mode(sector, ell, k, background, boundary_config)
```

并保持已有 radial diagnostics 语义清楚、可审计。

## 3. 非目标和硬限制

- 不修改 frozen Fourier、harmonic、tetrad、RW/Zerilli、polarization conventions。
- 不修改 T2/T3/T5/T6 physics formulas。
- 不修改 plotting 代码。
- 不生成 Fig.3 panel、fixtures 或 benchmark images。
- 不降低 `lmax`，不放松 `lmax_convergence` thresholds。
- 不把 high-ell/transition modes 静默跳过。
- 不把明显不可靠的 raw Wronskian 失败伪装成通过；如果需要采用不同有效诊断，必须写入 structured metadata/warning。
- 不把 Q015 混入 Q014；Q014 保持 closed。

## 4. 工作步骤

### 4.1 复现和定位

写一个临时只读诊断脚本或测试辅助，直接扫描：

```text
k=1.5, M=1, r_out=300, r_in_eps=1e-6, rtol=1e-10, atol=1e-12
ell=2..至少20, sector=odd/even
```

记录每个失败或 transition 模式的：

- `sector`
- `ell`
- `barrier_action`
- selected solver branch
- initial mesh size if BVP
- `max_nodes`
- solve status/message
- boundary residual
- flux/Wronskian diagnostics if available
- `|A_in|` or unit-infinity normalization indicator

如果当前 error message 缺少 mode context，先让 raised exception 包含
`sector/ell/k/r_out/barrier_action/solver/max_nodes`，并加测试覆盖。

### 4.2 判断根因

比较以下路径，不要只凭猜测修改：

1. 当前 BVP branch 在 `barrier_action > 8` 附近是否过早切换。
2. BVP 是否因长区间高频振荡、初始 guess、mesh density 或 `max_nodes` 策略失败。
3. Outward shooting 在 transition modes 上是否可作为有结构诊断的 fallback。
4. 对 high-barrier modes，outward solution 的巨大 `A_in` 是否导致 normalized field 或 Wronskian 诊断不可信。

### 4.3 实现最小稳健修复

优先选择局部、可测试、可解释的 T4 修复。可接受方向包括但不限于：

- 对 transition-band modes 增加 evidence-based fallback policy，并在 diagnostics 中明确记录；
- 对 BVP 增加有限次数 adaptive retry，例如更合理的 initial mesh / max nodes / tolerance strategy；
- 改善 BVP initial guess 或采用 oscillation-reduced formulation，但不要大改 public API；
- 如果无法在合理时间内给出可信修复，停止并写明 no-go 根因、失败 mode、已尝试策略和下一步建议。

任何修复都必须说明为什么它不是物理 convention 改动，也不是 lmax 截断。

## 5. 必须验证

至少运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

另外必须运行一个直接 radial scan：

```text
k=1.5, r_out=300, ell=2..20, sector=odd/even
```

如果修复声称支持 T8j 恢复，尽量继续扫描到 `ell=156`；若完整扫描超过合理运行时间，
至少记录已完成范围、运行时间、失败/警告模式，并明确 T8k 仍需真实 saved run 验证。

## 6. 停止条件

遇到以下任一情况立即停止并更新 `status.md`：

- 修复需要改变 frozen convention 或 T6 Route B production bridge。
- 只能通过降低 `lmax`、放松 threshold、跳过 modes 或平滑图像来“解决”。
- 三种独立数值策略都失败，且失败仍集中在 BVP mesh-node exhaustion。
- 单个 targeted mode 求解超过 10 分钟，或完整 radial scan 超过 30 分钟仍不能给出可解释结论。
- 诊断显示现有 T8j `kM=1.5` 参数本身需要 T0/T1/T7 重新裁决。

## 7. status.md 更新要求

完成或停止时更新 `status.md`：

- changed files
- commands run
- test results
- direct radial scan result
- whether Q017 is resolved, still open, or replaced by a narrower issue
- whether T8k may proceed
- open issues
- next action

不要修改 `src/schwgw/viz/*`，不要生成 plotting artifacts。
