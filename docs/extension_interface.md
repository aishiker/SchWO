# Extension interface for new static spherical black holes

版本：v0.1-design

## 1. 目标

本项目为后续静态球对称黑洞扩展预留接口，但不假设任意新黑洞只需替换 Schwarzschild 的 `f(r)`。引力波扰动是 spin-2 问题；新背景需要完整扰动理论输入。

## 2. 最小接入资料

接入一个新静态球对称黑洞，至少需要：

1. Metric ansatz，例如：

```text
ds^2 = -A(r) dt^2 + B(r) dr^2 + R(r)^2 dΩ^2
```

或可规约到 `f(r)` 形式。

2. Horizon / boundary structure：

```text
r_horizon
r_in_rule
r_out_rule
```

3. Tortoise coordinate：

```text
dr_star/dr = sqrt(B(r)/A(r))
```

若适用。

4. Master sectors：

```text
sector names
ell_min
effective potential V_sector(l,r)
master equation form
```

5. Boundary asymptotics：

```text
horizon ingoing form
infinity incident/outgoing form
possible long-range phase corrections
```

6. Incident wave matching：

```text
how plane GW coefficients map to master variables
flat or asymptotic normalization
```

7. Reconstruction：

```text
metric reconstruction or direct Weyl/observable reconstruction
```

8. Physical polarizations：

```text
GR two tensor polarizations only, or extra modes?
which Weyl/tetrad definitions remain valid?
```

9. Benchmarks：

```text
known limits
published data
analytic checks
```

## 3. Abstract interfaces

### 3.1 Background

```python
class StaticSphericalBackground(Protocol):
    name: str

    def metric_functions(self, r):
        """Return A(r), B(r), R(r) or equivalent."""

    def horizon_radius(self) -> float:
        ...

    def r_star(self, r):
        ...

    def drstar_dr(self, r):
        ...

    def coordinate_domain(self) -> tuple[float, float]:
        ...
```

### 3.2 Master sector

```python
class MasterSector(Protocol):
    name: str
    parity: Literal["odd", "even", "axial", "polar", "other"]
    ell_min: int

    def potential(self, ell, r, background):
        ...

    def ode_rhs(self, r, y, ell, k, background):
        ...

    def horizon_initial_data(self, ell, k, r_in, background):
        ...

    def infinity_basis(self, ell, k, r_out, background):
        ...
```

### 3.3 Incident matching

```python
class IncidentMatcher(Protocol):
    def coefficients(self, ell, m, k, wave, sector, background) -> complex:
        ...
```

### 3.4 Reconstruction / observables

```python
class ObservableModel(Protocol):
    def reconstruct_metric(self, radial_solution, grid):
        ...

    def weyl_scalars(self, metric_components, grid):
        ...

    def polarizations(self, weyl_scalars, k):
        ...
```

## 4. Schwarzschild backend as reference implementation

Schwarzschild backend must implement all interfaces without special casing in high-level pipeline. This is a hard requirement: if the high-level code imports `schwarzschild.py` directly, the abstraction failed.

Allowed:

```python
bg = BackgroundRegistry.create("schwarzschild", M=1.0)
model = PerturbationRegistry.create("schwarzschild_rwz", bg)
```

Not allowed:

```python
from schwgw.backgrounds.schwarzschild import f
# used inside generic scattering code
```

## 5. Mock extension test

Create a mock background with a trivial potential:

```text
V(l,r) = l(l+1)/r^2
```

Purpose: test that radial solver and partial-wave assembly can call a non-Schwarzschild backend. This does not claim physical correctness; it tests interface separation.

## 6. Extension readiness checklist

- [ ] New background passes coordinate-domain tests.
- [ ] `r_star` monotonic outside horizon.
- [ ] Each sector has stable boundary conditions.
- [ ] Incident matcher documented.
- [ ] Observable map documented.
- [ ] At least one analytic or published benchmark.
- [ ] No Schwarzschild-specific formula imported by generic modules.

## 7. T4ae generic typed extension boundary

T4ae 在上述 v0.1 sketches 之外增加一个 methods-only typed boundary。它不把
“可被 Protocol 调用”解释为“新背景或新 spin-2 theory 已接入”。Extension
必须分别提供并验证：

1. `BackgroundGeometryProtocol`；
2. `PotentialProviderProtocol`；
3. `RadialSystemProtocol`；
4. `BoundaryAsymptoticsProtocol`；
5. `IncidentSourceProtocol`；
6. `AngularModeCouplingProtocol`；
7. `DomainDriverProtocol`；
8. `SolverBackendProtocol`；
9. `ObservableProjectorProtocol`；
10. `ArtifactWriterProtocol`。

这些 boundary 不假设 Schwarzschild separability、单 component state 或
uncoupled channels。Potential 可以是 matrix，radial values/derivatives 的
shape 是 `(n_point,n_component)`，inner boundary 也不在 generic 名称中预设
为 event horizon。Scalar extension 使用一个 component；coupled extension
至少使用两个有序且唯一的 component names。

### 7.1 Sparse angular support

`IncidentSourceProtocol` 和 `AngularModeCouplingProtocol` 都暴露：

```python
def supported_m_values(ell: int) -> tuple[int, ...] | None:
    ...
```

返回 tuple 表示 extension 自己认证的 ordered sparse support；返回 `None`
表示调用者必须使用 generic full fallback `-ell..+ell`。空缺不能被猜测成
legacy `+z` support，tuple 也不能转换成 set 后重排。Legacy
`m=(-2,+2)` 仅属于 `LegacyIncidentSourceAdapter` 的现有 `+z` model，不是
extension contract。

### 7.2 Provenance and conventions

任何可缓存或可写出的 extension 结果都必须绑定完整
`ConventionMetadata`，以及恰好六段的 `ProvenanceIdentity`：

```text
implementation, physics, solver, config, source, gate
```

每一段都是 exact lowercase 64-hex SHA-256。Cache/checkpoint/oracle 不得仅凭
background name、class name 或部分 config 判断兼容。Units、metric
signature、Fourier sign、tortoise definition、ingoing/outgoing phases、
normalization 与 phase convention 必须逐项显式记录；不同 convention 的
结果不可复用。

### 7.3 Non-claim onboarding rule

用于验证 structural separation 的十个 boundary toy（包括 source、
angular coupling、boundary/asymptotics、solver backend、projector 和 writer）
都必须显式设置 `physical_claim=false`。这样的 mock 可以验证：

- runtime Protocol matching；
- scalar/coupled shape 和 component order；
- generic coordinate chart；
- ordered sparse support 与 `None` full fallback；
- deterministic orchestration 与 writer boundary。

它不能验证新 perturbation equation、boundary asymptotics、incident
normalization、observable map 或 spin-2 physics。要把 extension 提升为物理
backend，仍需完成本文件第 2 节的全部理论输入、独立 benchmark、convention
审查和 `docs/validation_plan.md` 中相应的 physics gates。

现有 `compute_polarization(..., mode_source=None)` 先进入
`LegacyScalarRWZAdapter.compute_polarization(...)` full-path facade；该
facade 只构造 exact legacy source，并把 background、solver、reconstruction
与 observable packaging 原样委托给 private frozen implementation。它是
accepted Schwarzschild scalar-master path 的兼容桥，不是第十一个 Protocol，
也不声称新的 backend。其 private scalar coefficient fast path 不是
extension 接口；新 source 必须实现 public typed
`amplitude(mode, channel)`，并返回 exact shape `(1,)` 的 scalar component
array。

本节不实现或验证新的 spin-2/Teukolsky/coupled-channel theory，不改变现有
physics/tolerances/modes/points，也不授权 87 个 diagnostic midpoints、
T7ch、T8、new frequency 或 production。
