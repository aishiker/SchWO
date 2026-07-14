# Phase 5 T4n Prompt: Q018 Rescaled Radial Architecture Spike

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4n`。

T7ah 已经接受 T4m 为 **ACCEPT YELLOW / fail-closed**。这说明当前代码不会
再误用 Q018 zero-tail suppression 生成 R60_K2 结果，但也说明 R60_K2 仍未解锁。

本 slice 的目标不是生成 R60_K2 artifact，而是做一个受控方法 spike：

```text
判断能否用 rescaled/log-amplitude/high-precision radial architecture
可靠计算 k=2, r=60, ell=153..180 odd/even 的 radial fields。
```

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_larger_domain_readiness.md`
8. `docs/q018_r60_method_hardening.md`
9. `references/notes/q018_spin2_tail_bound.md`
10. `docs/prompts/phase5_t4m_q018_r60_method_hardening.md`
11. `docs/prompts/phase5_t7ah_q018_r60_method_review.md`
12. `src/schwgw/numerics/radial_solver.py`
13. `src/schwgw/numerics/boundary_conditions.py`
14. `tests/physics/test_radial_solver.py`

按项目规则先检查已安装 plugin/skill。这个 slice 是数值方法 spike，优先使用
systematic debugging / TDD；如要查公式或方法，可使用本地 references/notes，必要时
使用文献检索插件。

## 2. Scope

允许：

- 新建方法设计/实验记录：
  `docs/q018_rescaled_radial_architecture_spike.md`
- 新增 isolated experimental helper 或 test-only helper，但必须清楚标为
  prototype，不得被 production `solve_radial_mode(...)` 默认调用。
- 新增 tests，用于锁定 T4m fail-closed 行为或 prototype 的有限性检查。
- 更新 `docs/numerics.md` 和 `status.md`。

除非证据非常充分，不要改 production solver path。优先设计和小样本 prototype。

禁止：

- 不要生成 R60_K2 wave-field artifact。
- 不要绘图。
- 不要运行 `kM=4`。
- 不要修改 Fourier/harmonic/tetrad/RWZ/Route B/Q005/Q014 convention。
- 不要降低 `lmax`。
- 不要放宽 residual/convergence/suppression thresholds。
- 不要把 scalar `ell_max~kr` 当作 spin-2 proof。
- 不要绕过 T4m `required_eval_radius` guard。

## 3. Candidate Methods To Assess

至少评估以下三种路线，给出是否可行、风险和最小下一步：

### Method A: high-precision bidirectional matching oracle

用 `mpmath` 或其它已可用高精度工具，对 selected modes 做离线 oracle：

```text
k=2
r_out=300
required radius r=60
ell=[153,156,168,180]
sector=[odd, even]
```

目标不是生产速度，而是判断是否能得到有限、稳定的 `psi(60)` 和 `dpsi/dr(60)`。

如果本地环境没有高精度 ODE 所需能力，记录 no-go，不要安装全局包。

### Method B: logarithmic / Riccati / scaled-amplitude propagation

设计一个避免跨越完整 `exp(S≈700)` 动态范围的方案。至少说明：

- 状态变量是什么；
- 如何保留 complex phase；
- 如何匹配 horizon ingoing 和 outer incoming/outgoing boundary data；
- 如何恢复 `psi` 与 `dpsi/dr` 的 normalization；
- 如何定义 Wronskian/flux diagnostics；
- 预计如何接入 `RadialSolution`。

可以实现最小 prototype，但不要默认接入 production。

### Method C: observable-level conservative bound

基于 T10b note，判断是否能给出足够保守的 spin-2 observable bound。
如果不能，明确写 no-go。不要把 `p=0` radial-only bound 当作 production proof。

## 4. Required Spike Outputs

创建：

```text
docs/q018_rescaled_radial_architecture_spike.md
```

必须包含：

1. Problem statement。
2. Why T4m fail-closed is correct but insufficient。
3. Candidate method assessment table。
4. Selected modes diagnostic table。
5. If prototype exists: exact API, limitations, and whether values are finite/stable。
6. Whether R60_K2 can be promoted to a future GREEN implementation slice。
7. If not: precise no-go and required future work。
8. Explicit statement that `kM=4` remains unvalidated。

## 5. Minimal Diagnostics

Run a targeted diagnostic for:

```text
M=1
k=2
r=60
r_out=300
ell=[153,156,168,180]
sector=[odd, even]
```

For each mode record:

- current production solver outcome with `required_eval_radius=60`;
- candidate method attempted;
- finite/non-finite result;
- sensitivity to precision/tolerance if applicable;
- runtime;
- whether the result could be used as a future regression oracle.

## 6. Validation Commands

At minimum run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If you add prototype tests, run those explicitly and record RED/GREEN history.

## 7. Stop Conditions

Stop and report without forcing implementation if:

- high-precision prototype is unavailable or takes more than 20 minutes per mode;
- scaled/log architecture requires a major rewrite not suitable for this slice;
- candidate method cannot preserve complex phase and normalization;
- diagnostics are finite but unstable under precision/tolerance changes;
- supporting R60_K2 would require changing physics convention;
- any full test failure cannot be locally explained.

## 8. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- candidate methods assessed;
- selected modes diagnostic summary;
- whether this is GREEN/YELLOW/RED for a future implementation slice;
- commands run;
- test results;
- open issues;
- next prompt recommendation for T7ai review.

Do not authorize T8 R60_K2 production from this spike alone.
