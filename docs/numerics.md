# Numerics plan

版本：v0.1-design

## 1. 总体数值策略

主算法是 finite-radius partial-wave scattering。观测者位于有限半径 `r_obs`，径向函数不使用远场渐近展开来生成主输出。渐近形式只用于边界条件、outer matching 和对照验证。

## 2. 径向方程

对每个 `(sector, ell, k)` 求解：

```text
d^2 psi/dr_star^2 + [k^2 - V_l(r)] psi = 0
```

实际积分推荐转写为 `r` 变量的一阶系统。

由于：

```text
d/dr_star = f(r) d/dr
```

有：

```text
f^2 psi''(r) + f f'(r) psi'(r) + [k^2 - V(r)] psi(r) = 0
```

一阶系统：

```text
y0 = psi
y1 = dpsi/dr

dy0/dr = y1
dy1/dr = -[f f' y1 + (k^2 - V)y0]/f^2
```

near-horizon 处 `f -> 0`，推荐从 `r_in = 2M(1 + eps)` 起步，使用 ingoing ansatz 初始化。

## 3. Horizon boundary condition

Horizon ingoing wave:

```text
psi ~ exp(-i k r_star)
dpsi/dr = (-i k / f) exp(-i k r_star)
```

初始化：

```text
psi(r_in) = exp(-i k r_star(r_in))
dpsi_dr(r_in) = (-i k / f(r_in)) psi(r_in)
```

必要时添加 Frobenius correction；第一版可先用 leading asymptotic，并通过 `eps` sensitivity test 判断稳定性。

## 4. Outer matching

在 `r_out` 处匹配：

```text
psi(r_out)      = A_in exp(-i k r_star) + A_out exp(+i k r_star)
dpsi/dr(r_out) = (-i k/f) A_in exp(-i k r_star) + (+i k/f) A_out exp(+i k r_star)
```

求解 2x2 线性系统得到 `A_in`, `A_out`。

目标边界要求：

```text
A_in_target = c_lm
A_out_target = -(-1)^ell exp(2i delta_l) c_lm
```

若从 unit horizon ingoing solution 得到 `A_in_unit`，则缩放：

```text
scale = c_lm / A_in_unit
psi_scaled = scale * psi_unit
A_out_scaled = scale * A_out_unit
```

当前实现允许内部使用不同归一化。低势垒模式仍使用 unit horizon
ingoing outward shooting；高势垒模式使用 unit incoming-at-infinity BVP，
因此返回的 `A_in` 应接近 1。上层只应依赖 `A_in` 表示外边界
`exp(-i k r_star)` 的入射系数，并用 `scale=c_lm/A_in` 归一到目标入射波。

phase shift：

```text
exp(2i delta_l) = - A_out_scaled / [(-1)^ell c_lm]
```

若存在长程相位修正或 convention 差异，必须在 `physics_spec.md` 更新。

## 5. Flux / Wronskian diagnostics

对于实势，Wronskian：

```text
W = psi^* dpsi/dr_star - psi dpsi^*/dr_star
  = f(r) [psi^* dpsi/dr - psi dpsi^*/dr]
```

沿径向应为常数。

记录：

```text
wronskian_residual = max(|W(r)-median(W)|) / max(|median(W)|, eps)
```

Outer matching flux sanity：

```text
Flux_inf ~ |A_in|^2 - |A_out|^2
Flux_hor ~ |A_hor|^2
```

符号和归一化需由 convention sheet 固定。第一版至少检查 residual 随 tolerance 降低。

### 5.1 High-ell stabilized architecture

Phase 3 Q012 diagnostics showed that unit-horizon outward shooting is not a
reliable flux/Wronskian diagnostic in high-`ell`, low-`k` tunneling regimes:
the physical solution grows into an exponentially large outer basis and the
subdominant flux-carrying component is lost by cancellation.

The current stabilized branch is selected by a WKB-like barrier action

```text
S = integral sqrt(max(V_l(r)-k^2,0)) dr_star
```

over the solved domain.  For large `S`, `solve_radial_mode` solves a
two-point boundary value problem in `r_star`:

```text
d psi/dr_star = p
d p/dr_star = -(k^2 - V) psi
```

with horizon ingoing boundary condition `p + i k psi = 0` and outer boundary
condition

```text
psi = exp(-i k r_star) + A_out exp(+i k r_star)
p   = -i k exp(-i k r_star) + i k A_out exp(+i k r_star).
```

This is equivalent to matching a horizon-ingoing solution to explicit outer
incoming/outgoing bases, but avoids propagating an exponentially amplified
unit-horizon amplitude through the forbidden region.  The BVP branch returns
unit incoming-at-infinity normalization (`A_in ~= 1`); `psi`, `dpsi/dr`,
`A_out`, `phase_factor`, and interpolation helpers are all stored in that
same normalization.

For BVP high-barrier modes the raw Wronskian can be physically tiny at the
horizon and cancellation-sensitive in double precision.  The diagnostic
therefore uses the raw Wronskian residual when the horizon flux scale is
resolved; otherwise it records the larger of the collocation residual and
outer-boundary residual as the meaningful conservation/stability check.  This
does not relax the Tier-2 `<1e-7` target: the high-`ell` tests now require the
stabilized diagnostic below that threshold for `ell=8,k=0.5` and finite,
small-boundary-residual behavior for `ell=12,k=0.5`.

Transition modes with barrier action just above the BVP threshold can sit
near the raw/stabilized diagnostic switch.  For example, `k=0.2, ell=3` has
`S ~= 8.30` and horizon flux scale `~2.9e-8`, only about twice
`sqrt(eps)`.  In that regime a raw Wronskian relative residual of `O(1e-6)`
can correspond to an absolute Wronskian drift of only `O(5e-14)`, while the
BVP collocation residual, outer-boundary residual, field convergence, and
matching condition number remain healthy.  Such a case should be recorded as
a transition-regime warning unless accompanied by field-convergence failure,
large boundary residual, non-finite radial data, or unstable branch/domain
sensitivity.  It is not a license to relax the global Wronskian target.

`RadialDiagnostics` stores this distinction explicitly:

```text
raw_wronskian_residual       # direct Wronskian-grid residual
wronskian_residual           # effective diagnostic used by current branch
flux_residual                # BVP collocation/boundary diagnostic or raw outward W residual
expected_flux_scale          # estimated horizon flux scale for BVP modes
warnings                    # structured RadialDiagnosticWarning records
```

The Q015 transition case is represented by warning code
`transition_raw_wronskian_warning`.  Each warning is JSON-safe through
`to_metadata()` and includes sector, `ell`, `k`, solver branch, barrier
action, raw/effective Wronskian residuals, flux and boundary residuals,
expected flux scale, and matching condition number.  Result-file or benchmark
metadata should carry these warning records separately from scalar maxima such
as `max_wronskian_residual`; existing scalar diagnostics must remain numeric.

### 5.2 Extreme evanescent-tail policy

Q018 exposed a more extreme regime at `k=2`, `r_out=300`, beginning at
`ell=153`: the BVP mesh reaches `max_nodes`, while bidirectional basis
propagation overflows the useful double-precision dynamic range in the
forbidden region.  The barrier action is `S ~= 706.303`, so the radial tail
scale is `exp(-S) ~= 1.8e-307`, already at the edge of IEEE double precision.
Forcing direct propagation in this regime is not a better physical diagnostic.

The scalar finite-radius result summarized in arXiv:2508.17253 is used only
as a strong prior for this policy, not as a spin-2 proof.  It supports the
expectation that modes far beyond the observer scale `ell ~ k r_obs` are
centrifugally suppressed at finite radius.  The spin-2 Regge-Wheeler and
Zerilli potentials share the same large-`ell` leading centrifugal scaling

```text
V_l(r) = f(r) ell(ell+1)/r^2 + lower-order spin/parity terms,
```

but parity sectors, reconstruction factors, tensor angular structures, and
possible polynomial `ell` prefactors must still be reviewed in saved
benchmark metadata.  This is why the solver does not silently reduce
`ell_max`; it records an explicit radial warning.

When the ordinary BVP fails and the barrier action satisfies
`S >= 706`, `solve_radial_mode` may return an
`evanescent_tail_suppressed` solution, but only on the interior domain where
the local WKB tail action from `r` to the outer turning point is at least 55.
The returned `RadialSolution.valid_until_r` enforces that domain for
`psi_at`, `dpsi_dr_at`, and `dpsi_drstar_at`.  Within this domain the radial
master field is represented by zero, with unit incoming-at-infinity
normalization (`A_in=1`) and the total-reflection phase convention
`A_out=-(-1)^ell`, so `phase_factor=1`.  The diagnostic residuals are set by
the explicit suppression bound, not by inflating a denominator.

Each suppressed mode carries warning code `evanescent_tail_suppressed` with
`suppression_bound` and `valid_until_r`.  Downstream production runs must
preserve these warning records in result metadata, and validation must check
that every evaluation radius lies within `valid_until_r`.  For the current
`61x61` x-z Fig.3-lite grid with `r_max=sqrt(30^2+30^2) ~= 42.426`,
`ell=153` has `valid_until_r ~= 42.472`, so the first suppressed mode still
covers the grid.  `ell=152` remains in the bidirectional branch.

### 5.3 Evaluation-radius-aware suppression guard

Q018 larger-domain review showed that the same `k=2`, `ell>=153`
suppressed modes do not cover R60: their recorded `valid_until_r` values are
about `42.47M` through `53.33M`.  A suppressed radial solution that is valid
for the accepted `[-30,30]^2` x-z domain must therefore not be reused as
evidence for `r=60M`.

`BoundaryConfig.required_eval_radius` is the explicit guard for this case.
Its default value is `None`, which keeps the historical behavior: the solver
may return an `evanescent_tail_suppressed` solution and the caller must
respect `RadialSolution.valid_until_r`.  If it is set to a finite radius `R`,
then an `evanescent_tail_suppressed` solution is allowed only when
`valid_until_r >= R`.  If the current tail policy cannot certify that radius,
`solve_radial_mode` raises a structured `RuntimeError` with code
`evanescent_tail_required_radius_uncovered` and JSON metadata containing the
sector, `ell`, `k`, solver branch, barrier action, suppression bound,
`valid_until_r`, `required_eval_radius`, coverage boolean, and no-go reason.

This guard is not a new spin-2 tail bound and it does not lower `ell_max`,
relax residual thresholds, or modify Fourier/radial phase conventions.  It is
a fail-closed method hardening: R60_K2 remains gated until a reviewed
target-radius conservative bound or a rescaled/log-amplitude radial
architecture certifies the requested radius.

### 5.4 Rescaled radial architecture spike status

T4n assessed R60_K2 follow-up methods without changing the production solver.
High-precision bidirectional matching could not be executed in the current
local environments because `mpmath`/equivalent arbitrary-precision ODE
support is unavailable and no global dependency was installed.  A direct
double-precision call to the existing bidirectional branch for `k=2`,
`ell=153`, odd, fails with floating-point overflow/invalid warnings followed
by the step-size error already associated with Q018.  Loosening or tightening
standard ODE tolerances does not make it a usable oracle.

The target-radius WKB diagnostic at `r=60` remains a no-go for a GREEN
spin-2 observable bound: the first suppressed modes have local actions well
below the existing `S_tail>=55` criterion, and polynomial reconstruction /
tensor-harmonic / curvature prefactors cannot be ignored.  The next viable
method work is therefore a real rescaled/log-amplitude radial architecture
with explicit complex phase, matching, normalization recovery, and
Wronskian/flux diagnostics in the scaled variables.  Until that exists,
R60_K2 production remains gated.

T4o adds only implementation prerequisites for that future method.  The
experimental module `schwgw.numerics.experimental.q018_rescaled_oracle`
defines a request/result contract.  T4o originally left
`solve_q018_rescaled_oracle(...)` fail-closed; T4p now implements an
experimental prototype behind the same non-production boundary.  The module
is not imported by `schwgw.numerics`, is not called by `solve_radial_mode`,
and is not part of the production radial path.  The oracle contract is unit
incoming-at-infinity normalized (`A_in ~= 1`) and must return finite
`psi(required_radius)`, `dpsi/dr(required_radius)`, `A_out`, and diagnostics
recording method, precision/tolerance, matching radius, finite checks, and a
Wronskian/flux proxy.  The opt-in oracle test targets
`M=1,k=2,r=60,r_out=300,ell=153,sector=odd`; default pytest skips that
full-regression assertion and remains GREEN.

T4p implements the first experimental prototype behind that boundary.  It
does not modify the production solver.  The method propagates the
horizon-ingoing logarithmic derivative

```text
y = (d psi/dr_star) / psi
dy/dr = [V_l(r) - k^2 - y^2] / f(r)
```

from the near-horizon cutoff to the requested radius.  At the requested
radius it sets a temporary unit-amplitude radial state with
`dpsi/dr = y psi / f`, integrates that state outward to `r_out`, and matches
the outer asymptotic form to recover the scale needed for unit
incoming-at-infinity normalization.  This avoids subtracting two large outer
basis functions at the requested radius; the small target-radius field is
obtained from the outer `A_in` normalization instead.

For the opt-in target mode `M=1,k=2,r=60,r_out=300,ell=153,sector=odd`, the
prototype returns finite `psi(60)` and `dpsi/dr(60)` with `A_in=1` and records
`method=riccati_log_derivative_match`, double-precision SciPy tolerances,
outer matching residual, normalization residual, log-derivative matching
residual, condition number, step counts, and runtime.  This is still an
experimental one-mode oracle prototype, not R60_K2 production readiness; it
does not authorize wave-field artifacts, plots, `kM=4`, larger-domain runs,
or bypassing `BoundaryConfig.required_eval_radius`.

T4q/T7al later broadened this experimental validation to
`ell=[153,156,168,180]`, odd/even, at the same
`M=1,k=2,r=60,r_out=300,r_in_eps=1e-6,rtol=1e-10,atol=1e-12` settings.
T4s then wired this reviewed method into `solve_radial_mode(...)` only through
the explicit `BoundaryConfig.experimental_required_radius_oracle="q018_riccati"`
opt-in, preserving default fail-closed behavior when the opt-in is `None`.
T4u extended the reviewed opt-in production envelope to the continuous
suppressed-mode band `ell=153..180`, odd/even, at the same R60_K2 settings.
This is still not broad R60 production readiness.

### 5.5 Q018 reviewed opt-in production adapter

T4r reserved, and T4s implemented, an explicit opt-in:

```python
BoundaryConfig(
    required_eval_radius=60.0,
    experimental_required_radius_oracle="q018_riccati",
)
```

The default is `None`, which does not call the experimental module and still
fails closed at R60 through `evanescent_tail_required_radius_uncovered`.
Unknown values are rejected.  The T4u adapter treats `"q018_riccati"` as a
run-level permission: ordinary modes first use the normal production radial
branches, and the oracle is only attempted after the normal branch fails with
`evanescent_tail_required_radius_uncovered`.  The adapter keeps `A_in` as the outer
`exp(-i k r_star)` incoming coefficient so that partial-wave assembly can
continue to use `scale = c_lm / A_in` without special cases.

The opt-in envelope is no broader than the reviewed matrix: Schwarzschild
`M=1`, `k=2`, `required_eval_radius=60`, `r_out=300`,
`r_in_eps=1e-6`, `rtol=1e-10`, `atol=1e-12`, `ell=153..180`, and
odd/even sectors.  Out-of-envelope requests must fail closed with structured
metadata rather than silently falling back to zero-tail suppression or
changing `ell_max`.

Every affected radial diagnostic or warning record includes method provenance
(`q018_riccati`,
`riccati_log_derivative_match`), the reviewed evidence slice, requested
radius, mode parameters, tolerances, finite flags, residual proxies, step
counts, runtime, and `unit_incoming_at_infinity=True`.  T8 saved artifacts
must serialize these records per mode.  See
`docs/q018_production_integration_design.md` for the full policy.

## 6. `lmax` 策略

`lmax ~= k r_obs` 只能作为初始估计，不能作为充分收敛条件。建议的初始值为：

```text
lmax0 = ceil(k * r_obs + margin)
margin = max(10, ceil(0.15 * k * r_obs))
```

production validation 必须使用 adaptive convergence loop，而不是固定的
`lmax_values = [0.6 kr, 0.8 kr, 1.0 kr, 1.2 kr]`：

```text
step = max(4, ceil(0.2 * k * r_obs))
lmax_values = [lmax0, lmax0 + step, lmax0 + 2 step, ...]
```

每次加入新的 `lmax` 后记录相邻两次 partial-wave sum 的变化：

```text
rel_change = ||h(lmax_i) - h(lmax_{i-1})|| / ||h(lmax_i)||
```

早期 adjacent pairs 是 diagnostics，用来暴露 pre-asymptotic behavior 或数值异常，
不能单独作为通过依据。只有最终 adjacent pair 同时满足阈值时，才判定
partial-wave convergence 通过：

```text
global rel_change < 1.0e-4
near-axis rel_change < 1.0e-3
```

如果某个 early pair 看似通过、但后续 pair 变差，应继续扩展或降低到 diagnostic
状态，而不是提前冻结结果。每次验证都必须记录最终使用的 `lmax_values`、final
adjacent pair、global/near-axis 最大变化，以及 Wronskian、boundary residual 等径向
diagnostics。对 optical axis 附近单独记录，因为那里最敏感。

## 7. Observer grid

支持三类网格：

### 7.1 Angular grid

```yaml
r_obs: 60
kind: angular
n_theta: 1000
phi: 0
```

用于 diffraction pattern。

### 7.2 Plane grid

```yaml
kind: xz_plane
x_values: [-12.0, -6.0, 0.0, 6.0, 12.0]
z_values: [4.0, 8.0, 16.0, 32.0, 48.0, 60.0]
invalid_radius_policy: mask
```

For production-scale uniform x-z maps, T8n also supports range input:

```yaml
kind: xz_plane
x_range: {start: -30.0, stop: 30.0, step: 0.5, endpoint: true}
z_range: {start: -30.0, stop: 30.0, step: 0.5, endpoint: true}
invalid_radius_policy: mask
```

The parser expands ranges into explicit coordinate arrays before the solver
runs, and the saved result metadata stores the expanded arrays.  Explicit
arrays remain supported.  A single axis may not provide both `*_values` and
`*_range`; range `step` must be positive, `stop > start`, `endpoint` must be
`true`, and the step must land exactly on `stop`.

转换：

```text
r = sqrt(x^2 + z^2)
theta = arccos(z/r)
phi = 0 if x >= 0 else pi
```

`r <= 2M` 或非有限半径点按 `invalid_radius_policy: mask` 处理：不调用
polarization solver，`valid_mask=False`，`h_plus/h_cross=nan+nanj`。配置仍要求
至少一个有效点，且 `numerics.boundary.r_out` 必须大于最大有效半径。T8f/T8n
只完成 schema/smoke 输出与 production-readiness hardening；benchmark-grade Li
Fig.3 x-z 空间图仍需单独的性能和验证 slice。

### 7.3 Selected probes

```yaml
kind: probes
points:
  - [r, theta, phi]
```

用于 regression fixtures。

## 8. Caching

径向解与 `m` 的关系：

- ODE 本身不依赖 `m`。
- `m` 只通过 incident coefficient 和角向函数进入。
- 因此可缓存 unit solution by `(sector, ell, k)`，再按 `m` 缩放。

缓存键：

```text
sector, ell, k, bg_name, bg_params, r_in, r_out, atol, rtol, ode_method
```

## 9. Parallelization

优先级：

1. frequency `k`。
2. multipole `ell`。
3. sector。
4. spatial grid chunks。

避免在每个 grid point 重新求 radial ODE。

## 10. Failure modes

| 症状 | 可能原因 | 处理 |
|---|---|---|
| phase shift 随 `r_out` 大幅变化 | outer matching 不够远或长程相位 convention 错 | 增大 `r_out`，检查 `r_star` |
| Wronskian residual 高 | ODE tolerance 不够或 horizon 初始化不稳 | 降低 `eps`/提高精度/Frobenius |
| optical axis 发散 | 错用了 asymptotic scattering amplitude 或 partial-wave sum 未收敛 | 确认 finite-radius radial functions，增加 `lmax` |
| `h_plus/cross` 相位翻转 | Fourier convention 或 Weyl sign 错 | 跑 M→0 极化测试 |
| 图像像旋转了 | spin-weighted harmonics 或 Wigner-D convention 错 | 跑 angular tests |

## 11. Recommended first numerical target

```yaml
M: 1
kM: 1.0
r_obs: 60
A_plus: 0.9 + 1.1j
A_cross: 0.4 + 0.6j
lmax: [40, 60, 75, 90]
r_in_eps: 1e-6
r_out: 300
ode_method: DOP853
rtol: 1e-10
atol: 1e-12
```

先生成 selected probes，再生成 full field map。
