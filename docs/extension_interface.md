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
