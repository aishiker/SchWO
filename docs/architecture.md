# Architecture

版本：v0.1-design

## 1. 设计原则

1. 物理公式集中化：每个公式只在一个模块中实现。
2. 数据流单向：配置 -> 求解 -> 保存 -> 绘图。绘图层不做物理求解。
3. 可替换背景：Schwarzschild 是第一个 backend，而不是硬编码到所有模块。
4. 可验证优先：每个模块必须暴露 diagnostics。
5. 可复现：所有输出包含 config、git commit、tolerances、lmax、library versions。

## 2. Python 包层级

```text
src/schwgw/
├─ backgrounds/      # metric functions and tortoise coordinate
├─ perturbations/    # sectors, potentials, master equations, reconstruction
├─ waves/            # incident GW and polarization basis
├─ angular/          # spherical/spin-weighted/tensor harmonics, Wigner-D
├─ numerics/         # ODE integration, boundary matching, convergence, cache
├─ scattering/       # partial-wave sum, Weyl scalars, tetrad transform, observables
├─ io/               # config/result schemas
└─ viz/              # plots from saved data only
```

## 2.1 Reference assets

文献和公式追踪不放入 `src/`，统一维护在项目根目录的 `references/`：

```text
references/
├─ manifest.md       # 每篇文献的用途、优先级、对应模块、关键公式范围
├─ papers/           # 原始 PDF
└─ notes/            # Codex 整理出的公式笔记、convention 对照、推导检查
```

公式映射的正式位置是 `docs/equation_map.md`。实现公式时，优先依据 `docs/physics_spec.md` 和 `references/notes/` 中已经整理并消歧的版本；PDF 原文是最终来源材料，但不应作为唯一上下文。若必须从 PDF 提取新公式，先把公式、符号定义、适用条件和 convention 差异写入 `references/notes/` 或 `docs/physics_spec.md`，再实现代码，并同步 `docs/equation_map.md`。

## 3. Core dataclasses

### 3.1 `WaveOpticsConfig`

```python
@dataclass(frozen=True)
class WaveOpticsConfig:
    background: BackgroundConfig
    wave: IncidentWaveConfig
    observer: ObserverGridConfig
    numerics: NumericsConfig
    outputs: OutputConfig
```

### 3.2 `RadialModeKey`

```python
@dataclass(frozen=True)
class RadialModeKey:
    sector: Literal["odd", "even"]
    ell: int
    m: int
    k: float
```

### 3.3 `RadialSolution`

```python
@dataclass
class RadialSolution:
    key: RadialModeKey
    r_grid: NDArray[float]
    rstar_grid: NDArray[float]
    psi: NDArray[complex]
    dpsi_dr: NDArray[complex]
    c_in: complex
    a_horizon: complex
    phase_shift: complex | float
    diagnostics: RadialDiagnostics
```

### 3.4 `FieldResult`

```python
@dataclass
class FieldResult:
    k: float
    r: NDArray[float]
    theta: NDArray[float]
    phi: NDArray[float]
    h_plus: NDArray[complex]
    h_cross: NDArray[complex]
    psi0: NDArray[complex] | None
    psi4: NDArray[complex] | None
    metadata: dict[str, Any]
```

## 4. Interfaces

### 4.1 `StaticSphericalBackground`

```python
class StaticSphericalBackground(Protocol):
    name: str
    M: float

    def f(self, r: ArrayLike) -> ArrayLike: ...
    def horizon_radius(self) -> float: ...
    def r_star(self, r: ArrayLike) -> ArrayLike: ...
    def drstar_dr(self, r: ArrayLike) -> ArrayLike: ...
    def asymptotic_region_hint(self, k: float, ell: int) -> float: ...
```

### 4.2 `MasterSector`

```python
class MasterSector(Protocol):
    name: Literal["odd", "even"]
    ell_min: int

    def potential(self, ell: int, r: ArrayLike, bg: StaticSphericalBackground) -> ArrayLike: ...
    def rhs(self, r: float, y: NDArray[complex], ell: int, k: float, bg: StaticSphericalBackground) -> NDArray[complex]: ...
    def incident_coefficient(self, ell: int, m: int, k: float, wave: IncidentWave) -> complex: ...
```

### 4.3 `ReconstructionOperator`

```python
class ReconstructionOperator(Protocol):
    def metric_components(self, sol: RadialSolution, r_eval: ArrayLike) -> MetricComponents: ...
```

### 4.4 `ObservableExtractor`

```python
class ObservableExtractor(Protocol):
    def weyl_scalars(self, modes: Sequence[RadialSolution], grid: ObserverGrid) -> WeylScalars: ...
    def polarizations(self, weyl: WeylScalars, k: float) -> PolarizationFields: ...
```

## 5. Execution pipeline

```python
cfg = load_config(path)
bg = build_background(cfg.background)
sectors = build_sectors(bg)
wave = build_incident_wave(cfg.wave)
grid = build_observer_grid(cfg.observer)

radial_cache = []
for k in cfg.wave.k_values:
    lmax = choose_lmax(k, grid.r_max, cfg.numerics)
    for ell in range(2, lmax + 1):
        for m in allowed_m_values(wave, ell):
            for sector in sectors:
                c_lm = sector.incident_coefficient(ell, m, k, wave)
                if abs(c_lm) == 0:
                    continue
                sol = solve_radial_mode(sector, bg, ell, m, k, c_lm, cfg.numerics)
                radial_cache.append(sol)

fields = assemble_fields(radial_cache, bg, wave, grid, cfg.numerics)
save_results(fields, radial_cache, cfg)
```

## 6. Output schema

T8a lightweight solver outputs use the same data-flow boundary, but store only
observer-grid fields and metadata.  The original angular-grid schema remains:

```text
results.npz
├─ theta              # 1D float array
├─ phi                # 1D float array
├─ h_plus             # complex array with shape (n_theta, n_phi)
├─ h_cross            # complex array with shape (n_theta, n_phi)
└─ metadata_json      # JSON string
```

The JSON metadata records `case_id`, creation timestamp, frozen convention
summary, full parsed config, `lmax`, boundary settings, per-point solver
diagnostics, diagnostic maxima, and source command when launched via CLI.
Optional `.h5/.hdf5` output uses `/fields/{theta,phi,h_plus,h_cross}` plus a
root `metadata_json` attribute when `h5py` is available.

T8f adds a backward-compatible spatial-grid schema for saved x-z plane
outputs.  Existing angular configs may omit `observer.kind`, which defaults to
`angular`; x-z configs may use explicit coordinate lists:

```yaml
observer:
  kind: xz_plane
  x_values: [...]
  z_values: [...]
  invalid_radius_policy: mask
```

T8n adds range-based x-z coordinate input for production ergonomics.  A config
may provide `x_range` / `z_range` instead of explicit arrays:

```yaml
observer:
  kind: xz_plane
  x_range: {start: -30.0, stop: 30.0, step: 0.5, endpoint: true}
  z_range: {start: -30.0, stop: 30.0, step: 0.5, endpoint: true}
  invalid_radius_policy: mask
```

The parser expands ranges into explicit `x_values` and `z_values` in the
parsed config and saved metadata.  Supplying both `x_values` and `x_range`, or
both `z_values` and `z_range`, is rejected.  Range endpoints must be explicit
and land exactly on `stop`; `endpoint: false` is not supported in this schema.

The x-z result schema is:

```text
results.npz
├─ x                 # 1D float array, shape (n_x,)
├─ z                 # 1D float array, shape (n_z,)
├─ r                 # float array, shape (n_z, n_x)
├─ theta             # float array, shape (n_z, n_x)
├─ phi               # float array, shape (n_z, n_x)
├─ valid_mask        # bool array, shape (n_z, n_x)
├─ h_plus            # complex array, shape (n_z, n_x)
├─ h_cross           # complex array, shape (n_z, n_x)
└─ metadata_json
```

The coordinate convention is `r=sqrt(x^2+z^2)`,
`theta=arccos(z/r)`, and `phi=0 if x>=0 else pi`.  Points with
non-finite radius or `r <= 2M` are masked, are not passed to the solver, and
store `nan+nanj` in both polarization arrays.  Metadata records
`grid.kind="xz_plane"`, the coordinate lists, valid/invalid point counts, and
the coordinate-conversion string.  HDF5 x-z output stores the same fields
under `/fields`.

T8g uses this schema for the first Li Fig.3-lite saved benchmark:
`R60_K1_LI_FIG3_LITE_XZ`, a single-frequency `kM=1` x-z plane over
`x/M,z/M in [-30,30]` with a `21x21` explicit grid and convergence window
`[60,72,84,96,108]`.  This benchmark stores raw complex `h_plus/h_cross` and
saved convergence metadata.  It is not the four-frequency paper Fig.3 panel,
does not include R60_K2/R60_K4, and does not implement transmission.

T8b plotting reads only these saved result files.  `plot-wavefield` supports
`h_plus` and `h_cross` components with `real`, `imag`, `abs`, or `phase`
quantities, then writes a PNG plus a `plot.png.json` sidecar.  The sidecar
records the source result path, plotted component/quantity, `case_id`, `kM`,
observer radius, `lmax`, convention summary, and source result creation time.
For 1x1 or 1D smoke outputs the plotter uses a point/line fallback rather than
requiring a 2D field map.  For x-z results, `plot-wavefield` renders `x`
horizontally and `z` vertically, masks invalid/NaN pixels, and adds grid kind,
coordinate ranges, valid/invalid counts, and coordinate-conversion metadata to
the sidecar.  Plotting remains read-only over saved results.  As of T8g, the
x-z plotter does not draw event-horizon or light-ring overlays; that remains
non-blocking visualization polish.

T8h adds a dedicated read-only `plot-fig3-panel` entry point for the
single-frequency Li Fig.3-lite x-z saved benchmark.  It accepts only
`quantity=real`, requires an `xz_plane` result with saved `x`, `z`, and
`valid_mask`, and renders side-by-side `h_plus` and `h_cross` panels with
`x` horizontal and `z` vertical.  Invalid or non-finite pixels are masked.
The two panels share one symmetric diverging color scale computed from the
valid saved real values of both components.  If the saved metadata contains
`config.background.M`, the plot overlays the light-ring radius `3M` before
the event-horizon disk radius `2M`; older files without `M` remain plottable
and record `overlays.drawn=false` in the sidecar.  The sidecar records source
path, `case_id`, plot type, grid kind, quantity, components, `kM`, `lmax`,
coordinate ranges, mask counts, color limits, overlays, and convention.  As of
T8n, the sidecar also records saved final-pair convergence metadata when
present, plus `requested_dpi` and `output_format`; the CLI accepts `--dpi` for
journal-resolution raster export while preserving default `180` DPI for
backward-compatible plots.  This
panel is visualization polish over saved data only; it does not rerun the
solver and is not the four-frequency paper Fig.3 reproduction.

T8i follows with a higher-sampling single-frequency x-z saved result using
the same physics parameters as T8g but a `61x61` grid over `[-30M,30M]` with
`dx=dz=1M`.  The result and panel remain read-only after the run; plotting
metadata should record the display interpolation, grid spacing, and samples
per wavelength.  The default display should show saved samples honestly,
while optional smoother interpolation is only presentation metadata and must
not be treated as a physics or convergence fix.
The `plot-fig3-panel` command now accepts `--interpolation` values
`nearest`, `bilinear`, or `bicubic`, defaulting to `nearest`.  Its sidecar
records `interpolation`, `grid_spacing={"x": dx, "z": dz}` for monotone
evenly spaced saved coordinates, and `samples_per_wavelength` when `kM` is
available via `lambda/M=2*pi/kM`.

T8j introduces a read-only multi-frequency Fig.3-lite panel over saved x-z
results.  The command should accept four already-saved x-z result files in
increasing `kM=[0.5,1.0,1.5,2.0]`, require matching grids, and render a
`2x4` panel with `real(h_plus)` on the top row and `real(h_cross)` on the
bottom row.  It must not call the solver.  The sidecar should record all
source paths, case ids, frequencies, grid spacing, samples per wavelength,
final convergence metadata, row-wise symmetric color limits, overlays, and
conventions.  T8n hardens the same command with `--dpi`, `requested_dpi`,
`output_format`, and PNG/PDF suffix-based output.

`plot-convergence` is read-only over saved metadata.  If a result file lacks
saved `lmax_convergence_history`, the command returns a clear nonzero error
and does not rerun the solver.

T8c adds an optional YAML `convergence` block for solver-run time only:

```yaml
convergence:
  enabled: true
  lmax_values: [2, 3, 4]
  theta_values: [0.0, 0.05]
  phi_values: [0.0]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
```

When enabled, `numerics.lmax` must equal the final `lmax_values` entry.  The
solver writes adjacent-pair history under
`metadata["diagnostics"]["lmax_convergence_history"]`, with rows containing
`previous_lmax`, `current_lmax`, `max_relative_change`,
`near_axis_max_relative_change`, `probe_count`, `near_axis_probe_count`, and
optional `worst_probe`.  The relative-change denominator is
`max(abs(new), abs(old), tiny)`, with `tiny=1e-30`; no automatic lmax increase
is performed.  The corresponding policy is stored in
`metadata["diagnostics"]["lmax_convergence_policy"]`, including thresholds,
probe lists, denominator convention, and `final_pair_passed`.  The final
adjacent pair is stored as `metadata["diagnostics"]["final_lmax_pair"]`.

`plot-convergence` plots only saved adjacent-pair history against
`current_lmax` and writes a PNG plus a sidecar JSON containing the source
result path, `case_id`, `kM`, observer radius, `lmax_values`, final pair,
final pass/fail flag, thresholds, and denominator convention.

T8e adds a run-scoped radial cache inside the saved-result runner.  The cache
is shared across all main-grid points and convergence probes during one
`run_solver_grid(...)` call; it does not change radial equations, boundary
conditions, or scattering formulas.  Result metadata records:

```text
metadata["diagnostics"]["run_radial_cache"] = {
  "enabled": true,
  "unique_solution_count": ...,
  "hit_count": ...,
  "key_count": ...
}
metadata["diagnostics"]["radial_diagnostic_warnings"] = [...]
```

`radial_diagnostic_warnings` is a JSON-safe list of structured warning
records from cached radial solutions.  It may be empty, and it must not
replace numeric scalar diagnostic summaries such as boundary, Wronskian,
flux, or condition-number maxima.

Recommended HDF5 layout:

```text
/results.h5
├─ attrs/
│  ├─ project_version
│  ├─ git_commit
│  ├─ created_at
│  ├─ config_yaml
│  └─ convention_hash
├─ radial/
│  └─ k_{value}/sector_{odd|even}/l_{ell}/m_{m}/
│     ├─ r
│     ├─ rstar
│     ├─ psi
│     ├─ dpsi_dr
│     └─ diagnostics
├─ fields/
│  └─ k_{value}/
│     ├─ r
│     ├─ theta
│     ├─ phi
│     ├─ h_plus
│     ├─ h_cross
│     ├─ psi0
│     └─ psi4
└─ plots_metadata/
```

## 7. Dependency policy

Preferred dependencies:

- `numpy`
- `scipy`
- `h5py`
- `pyyaml`
- `matplotlib`
- optional: `numba`, `joblib`, `spherical-functions` or equivalent for spin-weighted harmonics

Rule: optional dependencies must have fallbacks or clear error messages.

## 8. Performance design

- Cache radial functions by `(sector,l,k)`; for default +z incidence, `m` only enters through amplitude scaling.
- Cache spin-weighted harmonics by `(s,l,m,theta,phi)`.
- Vectorize angular sums over observer grids.
- Parallelize over `k` and `l` before parallelizing over spatial grid.
- Avoid repeated ODE integrations when only `A_plus/A_cross` changes; rescale coefficients where possible.

## 9. Error handling

All numerical routines return diagnostics instead of silently failing.

Minimum diagnostics:

```python
@dataclass
class RadialDiagnostics:
    boundary_residual: float
    wronskian_residual: float
    ode_n_steps: int
    ode_status: str
    r_in: float
    r_out: float
    atol: float
    rtol: float
    match_condition_number: float | None
```

## 10. Module ownership

- `backgrounds`, `perturbations`: T2
- `angular`: T3
- `numerics`: T4
- `waves`: T5
- `scattering`: T6
- `tests`, `benchmarks`: T7
- `viz`, `io`, `examples`: T8
- interfaces and abstractions: T9

## 11. T4ae methods-only typed boundary

本节追加 T4ae 的 pre-result methods contract，不替换上面的历史 v0.1
接口，也不改变任何物理公式、容差、mode/frequency/point、输出 schema 或
acceptance threshold。它只把可复用计算的边界显式化，使 legacy path 与
后续可能的 backend 能在同一组 fail-closed contract 下比较。

### 11.1 Typed values and identity

`src/schwgw/scattering/contracts.py` 定义以下 immutable values：

| 类型 | 冻结语义 |
|---|---|
| `ProvenanceIdentity` | 恰好六个 lowercase 64-hex SHA-256：`implementation_sha256`、`physics_sha256`、`solver_sha256`、`config_sha256`、`source_sha256`、`gate_sha256`；缺失、大小写错误、长度错误或非 hex 都拒绝。`canonical_digest` 是上述六字段的 sorted compact JSON SHA-256。 |
| `ConventionMetadata` | 必须显式给出 `units`、`metric_signature`、`fourier_sign`、`tortoise_definition`、`ingoing_phase`、`outgoing_phase`、`normalization`、`phase_convention` 和 typed `provenance`；任何一项都没有 silent default。 |
| `ChannelSpec` | 显式记录 field spin、polarization、parity、`scalar`/`coupled` radial structure、ordered component names 和 `physical_claim`。Scalar 恰好一个 component；coupled 至少两个且名称唯一。 |
| `ModeKey` | 以 `(frequency, ell, m, channel)` 构成 deterministic total order；非有限 frequency 被拒绝。 |
| `ObserverPoint` | 保存 label、显式 coordinate-system 名称和任意有限维 coordinate tuple；不把 Schwarzschild `r,theta,phi` 写死为 generic API。 |
| `RadialStateBatch` | 保存 shape `(n_point,n_component)` 的 complex values/derivatives、component names 和逐元素 finite pattern；输入数组被复制到 read-only immutable backing，scalar 与 coupled shape 使用同一 contract。 |

核心 provenance identity 始终只有上述六个 scientific/implementation
components。Benchmark runner 可在这一 identity 之外另行绑定
`environment_sha256`，用于同机 timing/checkpoint family；这不是第七个
`ProvenanceIdentity` 字段，也不得弱化六字段逐项匹配。

### 11.2 Ten structural boundaries

T4ae 使用十个 `runtime_checkable` structural Protocol。Protocol matching
只说明调用形状兼容，不说明数学模型或物理结论正确。

| Boundary | 责任 |
|---|---|
| `BackgroundGeometryProtocol` | coordinate domain、tortoise map 与 Jacobian；不要求 Schwarzschild `f(r)`。 |
| `PotentialProviderProtocol` | 返回 scalar 的 `1x1` 或 coupled 的 matrix potential。 |
| `RadialSystemProtocol` | 在任意 component count 上计算 first-order RHS。 |
| `BoundaryAsymptoticsProtocol` | 提供 generic inner state 与 outer basis；generic 名称不假定 inner boundary 必为 horizon。 |
| `IncidentSourceProtocol` | 提供 channel amplitude 和可选 ordered sparse `m` support。 |
| `AngularModeCouplingProtocol` | angular evaluation、mode coupling 和可选 ordered sparse `m` support。 |
| `DomainDriverProtocol` | 隔离 frequency-domain 与 future time-domain orchestration。 |
| `SolverBackendProtocol` | 求解 scalar 或 coupled radial system 并返回 `RadialStateBatch`。 |
| `ObservableProjectorProtocol` | 将 ordered radial states 投影到 observer-space artifact。 |
| `ArtifactWriterProtocol` | 连同完整 `ConventionMetadata` 写出 artifact。 |

十个 boundary 都显式暴露 `physical_claim: bool`。因此 solver backend 和
artifact writer 也不能依靠类名或调用位置暗示物理认证；所有只用于 structural
testing 的实现都必须显式为 `false`。

`supported_m_values(ell)` 返回 tuple 时，该 tuple 是 source/basis 声明的
scientific order，必须由调用者原样保持；返回 `None` 表示 generic full
fallback `m=-ell,...,+ell`。Generic contract 不包含 `+z` 或 `m=±2`
假设，也不允许以 unordered set 改变 reduction order。

### 11.3 Legacy scalar RWZ bridge

现有 Schwarzschild scalar-master RW/Zerilli 行为通过
`LegacyScalarRWZAdapter`、`LegacyIncidentSourceAdapter` 和两个显式
scalar `ChannelSpec` 保留。`compute_polarization(..., mode_source=None)`
先进入 `LegacyScalarRWZAdapter.compute_polarization(...)` 的 full-path
delegation facade；facade 构造 exact legacy source，再把完整调用委托给
private frozen implementation。因此默认调用保持原来的 odd/even
coefficients、normalization、radial solver、reconstruction 和 observable
packaging；facade 本身不重写公式，也不成为新的 generic physics backend。

Generic source 通过 `IncidentSourceProtocol.amplitude(mode, channel)` 返回
exact shape `(1,)` 的 component array。只有 type 恰为
`LegacyIncidentSourceAdapter` 的 source 可走 private `coefficient(...)`
fast path，以避免在现有 scalar inner loop 中分配 one-element array；这一
private branch 不是 extension API，不得被用来把 odd/even、Schwarzschild
separability 或 one-component state 写入 generic Protocol。Subclass 和任何
其他 structural source 都走 public typed amplitude path，也不能继承
legacy-zero shortcut。

### 11.4 Methods controls and non-claims

Radial dense reuse、exact oracle admission、deterministic at-most-two-worker
execution 和 atomic resume 的细节见 `docs/numerics.md`；exact equivalence、
fault 和 performance gates 见 `docs/validation_plan.md`。

本 architecture addition：

- 不实现或验证任何新的 spin-2、Teukolsky 或 coupled-channel theory；
- non-Schwarzschild/coupled mocks 必须记录 `physical_claim=false`，只能证明
  interface separation；
- 不改变 `G=c=M=1`、metric/Fourier/tortoise/ingoing/outgoing/normalization/
  phase conventions、solver tolerances、modes、frequencies 或 observer points；
- 不把 87 个 diagnostic failed-child midpoints 变成 run inputs；
- 不授权 T7ch、T8、new frequency、production、plot、fixture、Kirchhoff、
  paper-style output 或 GitHub action。
