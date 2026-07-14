# Phase 5 T4o Prompt: Q018 Rescaled Oracle Prerequisites And RED Tests

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4o`。

T4n/T7ai 的结论是 **ACCEPT YELLOW / DESIGN ONLY**：当前没有稳定的
`psi(60)` / `dpsi_dr(60)` oracle，也没有 production-ready rescaled/log radial
architecture。T4o 的目标不是实现完整方法，而是建立下一步实现所需的测试边界和
可选高精度原型入口。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `pyproject.toml`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `docs/q018_larger_domain_readiness.md`
9. `docs/q018_r60_method_hardening.md`
10. `docs/q018_rescaled_radial_architecture_spike.md`
11. `references/notes/q018_spin2_tail_bound.md`
12. `src/schwgw/numerics/radial_solver.py`
13. `src/schwgw/numerics/boundary_conditions.py`
14. `tests/physics/test_radial_solver.py`

按项目规则先检查已安装 plugin/skill。本 slice 是测试/原型准备，使用 TDD 和
systematic debugging；不要跳过 RED evidence。

## 2. Scope

允许修改：

- `pyproject.toml`
- `src/schwgw/numerics/experimental/` 下的新 experimental module
- `tests/physics/` 或 `tests/experimental/` 下的新测试
- `docs/q018_rescaled_radial_architecture_spike.md`
- `docs/numerics.md`
- `status.md`

禁止：

- 不要修改 production `solve_radial_mode(...)` 默认路径。
- 不要生成 R60_K2 wave-field artifact。
- 不要绘图。
- 不要运行或验证 `kM=4`。
- 不要修改 frozen physics conventions。
- 不要降低 `lmax` 或放宽 thresholds。
- 不要绕过 T4m `required_eval_radius` fail-closed guard。
- 不要安装全局包。若需要 `mpmath`，只能通过项目可选依赖或清楚记录环境缺失。

## 3. Required Design

建立一个清楚的 experimental boundary，例如：

```text
src/schwgw/numerics/experimental/q018_rescaled_oracle.py
```

这个 module 可以只包含 dataclass/API skeleton 和明确 `NotImplementedError`，
但必须定义未来实现的 contract，例如：

```python
@dataclass(frozen=True)
class RescaledOracleRequest:
    sector: Sector
    ell: int
    k: float
    required_radius: float
    r_out: float
    r_in_eps: float
    rtol: float
    atol: float

@dataclass(frozen=True)
class RescaledOracleResult:
    psi: complex
    dpsi_dr: complex
    A_in: complex
    A_out: complex
    diagnostics: dict[str, float | int | str | bool]

def solve_q018_rescaled_oracle(...): ...
```

Contract requirements:

- output is unit incoming-at-infinity normalized;
- output must be valid at `required_radius`;
- `A_in` must be close to `1`;
- diagnostics must record method, precision/tolerance, matching radius,
  finite checks, and Wronskian/flux proxy;
- implementation is explicitly experimental and not used by production
  `solve_radial_mode(...)`.

## 4. RED Tests

Add tests that are useful for the future implementation slice but do not break
the default fast suite if optional high-precision dependency is unavailable.

Recommended pattern:

1. A default-suite test verifies that the experimental module is not wired into
   production and that the public contract is documented.
2. A targeted RED test, marked clearly as `full_regression` or skipped unless
   an explicit environment variable is set, expects a future oracle to return
   finite values for:

```text
M=1
k=2
r=60
r_out=300
ell=153
sector=odd
```

3. The RED test must fail with the current `NotImplementedError` when run
   explicitly with its opt-in marker/env enabled. Record this RED evidence in
   `status.md`.

Do not hide the RED test as a permanent skip without documenting exactly how
future implementers should activate it.

## 5. Optional Dependency Boundary

If using `mpmath` is the preferred future oracle route, add only an optional
dependency group such as:

```toml
[project.optional-dependencies]
oracle = ["mpmath"]
```

Do not install it globally. Do not make default tests depend on it.

If you decide not to add the optional dependency, document why.

## 6. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run the explicit opt-in RED oracle test command, for example:

```bash
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
```

Expected current result may be RED due `NotImplementedError`; record it. The
default full suite must remain GREEN.

## 7. Stop Conditions

Stop and report if:

- adding the experimental boundary would require production solver changes;
- tests would make default `pytest -q` fail;
- optional dependency handling would require global installation;
- you cannot make the RED test opt-in and clearly documented;
- any production convention or threshold would need to change.

## 8. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- optional dependency decision;
- experimental API contract;
- RED test command and result;
- default test results;
- open issues;
- next prompt recommendation for T7aj review.

Do not authorize T8 R60_K2 production from this slice.
