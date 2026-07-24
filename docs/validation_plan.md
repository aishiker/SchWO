# Validation plan

版本：v0.1-design

## 1. 验证哲学

本项目的可信度来自分层验证，而不是最终图像相似。所有核心结论必须能定位到某一层测试：公式、数值、物理、回归、可视化。

## 2. Test tiers

### Tier 0：静态公式测试

| 测试 | 目标 | 方法 |
|---|---|---|
| Schwarzschild `f` | 避免背景硬错误 | 取样比较 `1-2M/r` |
| tortoise derivative | phase 关键 | 有限差分验证 `dr_star/dr=1/f` |
| RW potential | odd sector | horizon -> 0, infinity 主导项 |
| Zerilli potential | even sector | horizon -> 0, infinity 主导项 |
| lambda/sigma definitions | 入射系数 | 对 `l=2,3,4` 手算值 |

### Tier 1：角向基测试

| 测试 | 目标 | 方法 |
|---|---|---|
| `Y_lm` normalization | angular correctness | quadrature integral |
| `_sY_lm` spin-weight convention | Weyl scalar correctness | compare recurrence or Wigner-D |
| Wigner-D identities | tetrad transform | symmetry and identity rotation |
| plane wave m-selection | incident wave | +z 入射只允许 `m=±2` |

### Tier 2：径向 ODE 测试

| 测试 | 目标 | 方法 |
|---|---|---|
| horizon ingoing residual | boundary correctness | 检查 local derivative ratio |
| outer matching residual | phase correctness | 2x2 matching 反代 |
| Wronskian conservation | ODE correctness | 全径向网格 residual |
| tolerance convergence | 数值稳定 | rtol/atol sweep |
| `r_out` convergence | 边界稳定 | 多个 outer radii |

### Tier 3：物理 sanity tests

| 测试 | 目标 | 方法 |
|---|---|---|
| `M -> 0` flat limit | 全链路最关键 | radial solution -> spherical Bessel plane wave |
| no-lens polarization recovery | 极化 sign | 输出 `h_plus/cross` 对齐输入 |
| optical-axis finite value | 主论文方法关键 | finite-radius partial-wave sum 不发散 |
| `lmax` convergence | partial-wave 可信 | `lmax` sweep |
| far-angle asymptotic comparison | 对照 | 与传统 asymptotic 方法定性一致 |

### Tier 4：回归测试

固定若干参数输出 selected values，作为 CI 里的 regression fixtures。

建议 probes：

```yaml
probes:
  - {r: 60, theta: 0.0, phi: 0.0}
  - {r: 60, theta: 0.05, phi: 0.0}
  - {r: 60, theta: 0.2, phi: 0.0}
  - {r: 60, theta: 1.0, phi: 0.0}
```

记录：

```text
h_plus.real, h_plus.imag
h_cross.real, h_cross.imag
Psi0, Psi4
selected phase shifts
convergence residual
```

## 3. Acceptance thresholds

初始阈值建议：

| 项 | 阈值 |
|---|---|
| unit formula relative error | `< 1e-12` |
| angular normalization | `< 1e-8` |
| Wronskian residual | `< 1e-7` first pass, later `< 1e-9` |
| boundary residual | `< 1e-8` |
| interpolated radial ODE residual | `< 3e-4` first pass |
| M→0 field relative error | `< 1e-5` first pass |
| lmax convergence on selected probes | `< 1e-4` first pass |
| near-axis lmax-refinement relative change | `< 1e-3` first pass |
| far-axis asymptotic comparison | `< 5e-2` first pass, comparison only |

阈值必须随着实现成熟收紧，并记录在 `status.md`。

For adaptive `lmax` validation, early adjacent pairs are diagnostics rather
than immediate failures.  A selected-probe sweep passes only when the final
adjacent pair in the adaptive window satisfies both the selected-probe
threshold `<1e-4` and the near-axis threshold `<1e-3`.  If an earlier pair
already satisfies the threshold but the next higher pair degrades, stop and
diagnose the instability before declaring convergence.

### 3.1 Tolerance policy

- 容差按 test tier 管理，不允许在单个测试中随意放宽而不更新本文件。
- Tier 0 公式测试默认目标是 double precision 解析一致性；若使用有限差分，应在测试名或注释中说明差分步长和误差来源。
- Tier 1 角向积分测试允许受 quadrature 网格影响，但必须记录网格规则。
- Tier 2 及以上数值 ODE 测试必须同时记录 `rtol`、`atol`、domain cutoff、method 和 residual definition。
- Tier 2 interpolated ODE residual uses the stored radial interpolation plus a finite-difference derivative check; it is not a direct `solve_ivp` local truncation error.
- High-`ell` radial Wronskian conservation is covered by the active Q012
  stabilized-solver tests in `tests/physics/test_radial_solver.py`.
  Outward unit-horizon shooting remains documented as the failed baseline,
  but high-barrier production solves use a unit-incoming-at-infinity BVP.
  The `<1e-7` target is unchanged for the `ell=8,k=0.5` and `ell=6,k=0.2`
  barrier cases; `ell=12,k=0.5` must remain finite with small boundary
  residual and a non-exploding stabilized diagnostic.
- Transition BVP modes whose horizon flux scale is near `sqrt(eps)` may show
  raw-Wronskian relative residuals above `<1e-7` while collocation residual,
  boundary residual, field convergence, and matching condition number remain
  stable.  These are radial diagnostic warnings, not automatic benchmark
  blockers, and must be documented per case rather than hidden by changing
  the global Wronskian threshold.
- Q015-style radial warnings must be structured metadata.  A warning record
  must include enough context to diagnose the mode later: code, severity,
  sector, `ell`, `k`, solver branch, barrier action, raw and effective
  Wronskian residuals, flux and boundary residuals, expected flux scale, and
  matching condition number.  Warning metadata must be JSON-safe and must not
  replace numeric scalar diagnostics.
- Tier 3 fast physics tests must use small selected probes and finite-value/diagnostic assertions; expensive convergence and asymptotic comparisons belong in `full_regression`.
- Far-axis asymptotic comparison is a baseline check only; it must not define or renormalize the finite-radius partial-wave algorithm.
- Q013 no-lens validation must use a true flat-space oracle. It must not use
  tiny-`M` Schwarzschild horizon-ingoing radial solves as the oracle. As of
  2026-07-05, the public no-lens oracle is a direct Cartesian TT linearized
  Riemann/Weyl calculation in Minkowski space, projected to
  `incident_cartesian_tetrad()` and converted by `polarization_from_weyl(...)`.
  This active recovery test must pass at `<1e-5`; the direct oracle itself is
  tested at `<1e-10`.
- The T5 regular spherical-Bessel -> T6b/T6c/T6d path remains as
  `compute_flat_no_lens_partial_wave_diagnostic(...)`, not as the no-lens
  oracle.  After the T6h flat bridge repair and T7e/T7f independent checks,
  this diagnostic is genuine: it does not call the direct Cartesian oracle,
  its `lmax=2,5,10,40` outputs change, its per-ell contribution norms are
  nonzero, and `lmax=40` recovers the direct flat oracle below `<1e-5`.
- 所有容差变化必须同步写入 `status.md` 的验证记录。

### 3.1.1 Q018 production-integration validation boundary

Q018 experimental oracle success is not broad R60 production readiness.  T4u
keeps the reviewed explicit opt-in adapter and extends it to the continuous
R60_K2 suppressed band, while default production tests must still assert that

```text
solve_radial_mode(..., BoundaryConfig(required_eval_radius=60.0))
```

raises `evanescent_tail_required_radius_uncovered` for
`M=1,k=2,r_out=300,ell=153..180`, odd/even.

T4r adds a design-only opt-in placeholder,
`BoundaryConfig.experimental_required_radius_oracle="q018_riccati"`, and T4u
implements it as a run-level permission: ordinary default-covered modes remain
on the normal production path, while modes that fail with
`evanescent_tail_required_radius_uncovered` may use the reviewed oracle only
inside the continuous T4u envelope.  Tests require unknown opt-in names and
out-of-envelope opt-in requests to fail closed.  Opt-in production tests
require finite `RadialSolution` output, unit incoming-at-infinity
normalization, `A_in≈1`, residual proxies matching the oracle thresholds, and
JSON-safe provenance metadata.

No R60_K2 regression fixture may be committed until:

- default fail-closed behavior remains tested;
- opt-in production radial tests pass for the reviewed continuous
  `ell=153..180`, odd/even matrix;
- T7 independently compares opt-in production radial outputs to the
  experimental oracle and reviews continuous coverage;
- selected-probe partial-wave convergence passes with final adjacent-pair
  global `<1e-4` and near-axis `<1e-3` thresholds;
- saved-result metadata records every radial oracle provenance record per
  mode.

This boundary does not validate `kM=4`, R60_K4, arbitrary incident direction,
larger domains, scalar-cutoff-only proofs, or T8 artifacts.

### 3.4 Phase 3 validation structure

Phase 3 separates validation entrypoints into two classes:

- Fast physics tests: small selected probes, finite output checks, diagnostics presence, `lmax` scaling smoke checks, parity-sector/m-selection consistency, and API-independent polarization sign tests.
- Slow/full validation tests: no-lens or `M -> 0` polarization recovery, selected-probe convergence to `<1e-4`, near-axis refinement to `<1e-3`, far-axis asymptotic comparison to `<5e-2`, and future numeric regression fixtures.

Current Phase 3 T7a skeleton file:

```text
tests/physics/test_phase3_validation.py
```

T7a keeps default pytest green by marking full-validation oracles that are not frozen yet as skipped or expected-failing. The Q013 direct Cartesian TT no-lens oracle is now active and its recovery assertion is no longer expected-failing. The diagnostic-only partial-wave flat path remains an active localization test showing that the remaining O(1) mismatch is not fixed by the Q011 star toggle alone.

### 3.5 M5 transmission-normalization validation

M5 tests must validate pointwise wave-optics amplification, not radial horizon
transmission or absorption.  They must be added and independently reviewed
before any M5 plot or artifact can be accepted.

Required tests:

| 测试 | 目标 | 方法 / acceptance |
|---|---|---|
| no-lens identity ratio | baseline convention | Replace the lensed field by the flat/no-lens production baseline; every unmasked `F_plus_complex`, `F_cross_complex`, and `F_pol_norm` must equal `1` within `<1e-10` for direct flat baselines or the active flat-oracle tolerance for partial-wave diagnostics. |
| baseline path guard | avoid tiny-`M` and radial contamination | Monkeypatch or instrument `solve_radial_mode` / radial boundary helpers and require denominator generation to use `compute_flat_no_lens_polarization(...)` or the frozen equivalent without horizon boundary, `A_in/A_out`, phase-shift, or tiny-`M` solve. |
| same-convention metadata | prevent convention drift | Saved metadata must record `exp(-i k t)`, same `k`, same `A_plus/A_cross`, observer-coordinate matching, `+z` incident direction for v0.1, Route B packaged-polarization bridge, and baseline API. |
| independent component masks | handle polarization zeros | Pure plus input must make the cross ratio NaN/masked while plus remains finite; pure cross input must make the plus ratio NaN/masked while cross remains finite.  Masks must be independent. |
| combined norm mask | scalar summary without hiding zeros | `F_pol_norm` and `I_pol_ratio` are finite if `sqrt(|h_plus_unlensed|^2+|h_cross_unlensed|^2)` passes its mask, even if one component denominator is zero; they are NaN only where the norm mask is false. |
| denominator threshold regression | reproducibility | Tests must assert the stored `eps_plus`, `eps_cross`, `eps_norm`, `denominator_atol_factor=1e-14`, and `denominator_rtol_factor=1e-12` are used to build saved masks. |
| saved schema round trip | output reliability | NPZ/HDF5 readers must preserve complex `F_plus_complex/F_cross_complex`, real `F_pol_norm/I_pol_ratio`, masks, NaNs, and normalization metadata exactly enough for plotting without recomputation. |
| direct-division selected points | local formula check | For selected valid points, recompute the flat/no-lens baseline independently and compare saved ratios to direct division of saved `h_plus/h_cross` by the baseline. |
| read-only plotting boundary | no hidden physics in plots | M5 plotting must read saved ratio fields and masks only.  Static tests must reject imports or calls from plotting code into solver, radial, scattering, or baseline recomputation paths. |
| terminology/API guard | avoid two meanings of transmission | User-facing field names and metadata must distinguish `pointwise_wave_optics_amplification` from `radial_mode_transmission`, `radial_horizon_transmission`, `radial_absorption`, `A_in/A_out`, and phase-shift diagnostics. |

Acceptance notes:

- Component ratios are complex amplitude ratios.  Amplitude and intensity
  ratios are derived summaries and must be named explicitly.
- Invalid denominator masks must produce NaN, not clipped, floored, zero-filled,
  or one-filled ratios.
- The flat/no-lens diagnostic partial-wave path may be tested, but it is not
  the production denominator unless a later reviewed convention update
  replaces the baseline API.
- Scalar/Kirchhoff/eikonal/asymptotic-helicity baselines are comparison
  diagnostics only until separately frozen.

### 3.2 Phase 0 pytest skeleton

`pyproject.toml` 是 pytest 配置入口：

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
  "physics: tests that require implemented physics or numerical solver oracles",
  "regression: selected-value regression fixture checks",
  "full_regression: larger benchmark/regression checks outside the fast local suite",
]
```

Phase 0 本地测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

如果环境中 `pytest` 不在默认 `python3` 下，必须使用明确解释器路径或项目本地虚拟环境，并在 `status.md` 记录。

### 3.3 Command boundaries

Phase 0 只要求 skeleton 和 Tier 0 公式测试通过，不要求生成完整物理 benchmark。

```bash
# 全部当前本地测试；Phase 0 必须通过
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q

# 快速公式/unit 测试
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit

# regression fixture schema 测试；不生成 benchmark 数值
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
```

后续实现物理求解器后：

```bash
# physics tests: Wronskian、M->0、partial-wave convergence 等
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics

# full regression: committed selected-value fixtures 或登记的大型 benchmark
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m "regression or full_regression" tests/regression
```

任何 slow/full regression 数据依赖必须登记在 `benchmarks/reference_data_registry.md`；fast/local 测试不得依赖大型二进制数据。

## 4. Benchmark parameter sets

### B001：single-frequency base

```yaml
M: 1
kM: 1.0
r_obs: 60
A_plus: 0.9 + 1.1j
A_cross: 0.4 + 0.6j
lmax: 80
```

T8d uses a saved-result `R60_K1_LI_FIG4_LITE` variant of B001 with
`r_obs=60`, `kM=1`, `lmax_values=[60,72,84,96,108]`, and a fixed-radius
angular line at `phi=0`.  This is a Li Fig.4-like angular diffraction lite
benchmark only; it is not a full paper reproduction, not the Fig.3 x-z
spatial wavefield, and not a transmission-factor benchmark.

T8e runs the same benchmark through a run-scoped radial cache and aligns the
boundary settings with the committed `R60_K1` fixture-generation record
(`r_out=300`, `rtol=1e-10`, `atol=1e-12`).  Cache metadata and structured
radial warnings are validation artifacts; the cache must not alter formulas,
thresholds, or the final adjacent-pair convergence criterion.

T8f introduces `R60_K1_XZ_PLANE_SMOKE` as a schema and plotting smoke only:
`kind=xz_plane`, explicit `x_values` and `z_values`, `lmax=8`, and saved
convergence metadata for `lmax_values=[4,6,8]`.  Acceptance for this slice is
limited to config compatibility, coordinate-conversion metadata, valid-mask
behavior, skipped solver calls for invalid radii, NPZ/HDF5 field shape checks,
and read-only x-z plotting from saved results.  It is not a benchmark-grade
Li Fig.3 reproduction, does not introduce R60_K2/R60_K4, and does not address
the transmission-factor normalization.

T8g promotes the x-z schema to a first saved benchmark:
`R60_K1_LI_FIG3_LITE_XZ`.  It is still limited to one frequency, `kM=1`, on a
`21x21` explicit grid over `x/M,z/M in [-30,30]`, with the R60_K1 high-ell
window `lmax_values=[60,72,84,96,108]` and the same boundary settings as the
R60_K1 fixture-generation record (`r_out=300`, `rtol=1e-10`, `atol=1e-12`).
Acceptance requires finite valid-grid `h_plus/h_cross`, correct masking of
the black-hole center, run-scoped cache statistics that do not scale with the
number of grid points, JSON-safe radial warning metadata, saved convergence
history, and final adjacent pair `[96,108]` passing both selected and
near-axis thresholds.  This is a Li Fig.3-lite single-frequency benchmark; it
is not a four-frequency paper-scale panel and does not validate transmission.

T8h validates the visualization-only Fig.3-lite panel layer.  Acceptance is
limited to read-only plotting from saved x-z results: `plot-fig3-panel` must
write PNG and JSON sidecar outputs for NPZ and, when available, HDF5 result
files; reject non-`xz_plane` results clearly; reject missing `x`, `z`, or
`valid_mask`; support only `quantity=real`; mask invalid/non-finite points;
use one symmetric finite color scale shared by `h_plus` and `h_cross`; and
record event-horizon/light-ring overlay metadata derived from saved
`config.background.M` when present.  Static tests must keep `src/schwgw/viz`
free of solver or physics-layer imports.  T8h does not alter convergence
thresholds, T2-T6 formulas, transmission, R60_K2/R60_K4, or multi-frequency
Fig.3 validation.

T8i is a high-sampling follow-up to T8g/T8h, not a new physics convention.
It keeps the same single-frequency `kM=1` physics parameters and convergence
window, but changes the x-z grid from `21x21` with `dx=dz=3M` to `61x61`
with `dx=dz=1M`.  For `kM=1`, this increases the visual sampling from about
`2.09` to about `6.28` samples per wavelength.  Acceptance still requires
the final adjacent pair `[96,108]` to pass both selected and near-axis
thresholds, finite valid fields, structured diagnostic metadata, and a
read-only plotting path.  Plot sidecars should record interpolation choice,
grid spacing, and samples per wavelength.  T8i remains single-frequency
Fig.3-lite; it is not the four-frequency paper panel and does not validate
R60_K2/R60_K4 or transmission.
The accepted T8i integer grid masks all saved points with `r <= 2M`, giving
`13` invalid points and expected saved field shape `(61,61)`.  The default
`plot-fig3-panel --interpolation nearest` panel is the acceptance plot; any
`bilinear` or `bicubic` panel is a visual comparison only and must not be used
to relax field convergence or hide saved-grid artifacts.

T8j extends the accepted Fig.3-lite path to the four frequencies shown in
Li-Hou-Zhao Fig.3: `kM=[0.5,1.0,1.5,2.0]`.  It must reuse the accepted T8i
`kM=1` saved result and generate only the three missing x-z saved results.
The grid remains `61x61` over `[-30M,30M]`; samples per wavelength are about
`12.57`, `6.28`, `4.19`, and `3.14` for the four frequencies.  Acceptance
requires per-frequency final adjacent-pair convergence, finite valid fields,
bounded run-scoped radial cache metadata, JSON-safe warnings, and a read-only
`2x4` multi-frequency panel with row-wise symmetric color scales.  T8j is not
a transmission slice, does not generate `R60_K2`/`R60_K4` regression fixtures,
and does not run the `kM=4` stress benchmark.

T8n hardens production schema and output layout before any full production
run.  Acceptance for this slice requires range-based x-z config parsing with
`x_range` / `z_range`, endpoint inclusion, invalid-range rejection, and
backward compatibility for explicit arrays.  The parser must expand ranges
into saved explicit coordinates.  `plot-fig3-panel` and
`plot-fig3-multifrequency-panel` must remain read-only over saved results,
accept `--dpi` for publication-resolution exports, record `requested_dpi` and
`output_format` in sidecars, and include saved final-pair convergence metadata
for single-frequency Fig.3 panels.  A tiny range-config smoke may run, but the
`121x121` production template must not be run in this slice.

### B002：low-frequency wave optics

```yaml
M: 1
kM: 0.1
r_obs: 60
A_plus: 0.9 + 1.1j
A_cross: 0.4 + 0.6j
lmax: 20
```

### B003：high-frequency stress

```yaml
M: 1
kM: 4.0
r_obs: 60
A_plus: 0.9 + 1.1j
A_cross: 0.4 + 0.6j
lmax: 280
```

## 4.1 Test data directories

```text
tests/data/                 # 小型测试输入，必须可提交
tests/regression/fixtures/  # regression fixture 文件，必须有 schema/version
data/fixtures/              # 可复用 benchmark fixture 或生成后的轻量数据
data/raw/                   # 原始外部数据，不默认纳入测试
data/processed/             # 处理后数据，不默认纳入 fast tests
```

大型二进制数据不得进入 fast test path；若必须使用，应登记在 `benchmarks/reference_data_registry.md`。

## 4.2 Regression fixture format

Regression JSON fixture schema v0.2 records selected values plus convergence
and radial diagnostic metadata.  Future HDF5/NPZ output can coexist with this
selected-values schema.

```json
{
  "schema_version": "0.2",
  "case_id": "R60_K1",
  "conventions": {
    "fourier": "exp(-i k t)",
    "units": "G=c=M=1",
    "gauge": "Regge-Wheeler"
  },
  "parameters": {
    "M": 1.0,
    "kM": 1.0,
    "r_obs": 60.0,
    "A_plus": {"real": 0.9, "imag": 1.1},
    "A_cross": {"real": 0.4, "imag": 0.6},
    "lmax": 80,
    "lmax_values": [40, 60, 80]
  },
  "observables": {
    "selected_points": [
      {
        "r": 60.0,
        "theta": 0.0,
        "phi": 0.0,
        "h_plus": {"real": null, "imag": null},
        "h_cross": {"real": null, "imag": null}
      }
    ]
  },
  "diagnostics": {
    "boundary_residual": null,
    "wronskian_residual": null,
    "flux_residual": null,
    "match_condition_number": null,
    "lmax_convergence": null,
    "near_axis_lmax_convergence": null,
    "final_lmax_pair": null,
    "radial_diagnostic_warnings": []
  }
}
```

`null` values are allowed only in schema templates, not in committed numeric regression fixtures.
`radial_diagnostic_warnings` is always a list.  When it records a warning such
as Q015, each entry must include enough metadata to identify the mode and
diagnostic source.  It should serialize `RadialDiagnosticWarning.to_metadata()`
records, including `code`, `severity`, `sector`, `ell`, `k`, `solver`,
`barrier_action`, `raw_wronskian_residual`,
`effective_wronskian_residual`, `flux_residual`, `boundary_residual`,
`expected_flux_scale`, and `match_condition_number`.  Result writers may also
add fixture-level aliases such as `kM`, but they must not drop the mode-level
warning context.

Phase 0 模板文件：`tests/regression/fixtures/schema_template.json`。该模板只冻结字段形状和 convention metadata；`h_plus`、`h_cross` 和 diagnostics 中的 `null` 不是物理 expected values。`tests/regression/test_fixture_schema.py` 会检查模板字段，并要求未来提交的 numeric fixture 不含 `null`。

## 5. Plot validation

Plots are not primary validation, but must satisfy metadata consistency:

- component: `h_plus`, `h_cross`, `abs`, `real`, `phase`。
- frequency `kM`。
- `r_obs` for angular grids, or `grid_kind=xz_plane` with `x_range`,
  `z_range`, valid/invalid point counts, and coordinate-conversion metadata.
- `lmax`。
- normalization。
- phase/time snapshot convention。
- input amplitudes。

## 6. CI stages

### Fast CI

- Tier 0。
- small angular tests。
- ODE smoke test with `l=2,k=0.5`。

### Physics CI

- Wronskian tests。
- M→0 selected probes。
- small partial-wave sum。

### Full regression

- B001/B002 selected probes。
- B003 optional nightly run。

## 7. Manual review checklist

Before claiming physics correctness:

- [ ] `physics_spec.md` convention matches implementation.
- [ ] M→0 test passes.
- [ ] Wronskian residual acceptable.
- [ ] `lmax` sweep shown.
- [ ] optical-axis value finite and stable.
- [ ] plot generated from saved data, not ad hoc arrays.
- [ ] status updated with command, config, commit, diagnostics.

## 8. T4ae methods-only equivalence gate

本节冻结 implementation-comparison 的 validation matrix。它是 pre-result
contract，不表示 legacy baseline、optimized benchmark 或最终 T4ae decision
已经产生。

### 8.1 Exact existing benchmark matrix

Cold legacy baseline 必须在任何 code edit 之前从 exact legacy implementation
生成。Optimized run 必须使用同一 machine、interpreter、NumPy/SciPy、
BLAS-thread environment、physical inputs、ordering 和 output contract。

五个 frequency cases 都是既有 T8as evidence，不是新 frequency：

| `kM` | exact `lmax` window | role | immutable legacy NPZ SHA-256 |
|---:|---|---|---|
| `0.86875` | `[24,36,60,84]` | low-frequency / max-lmax 84 | `58768a1c4be7b351dd5c44351b98ecd61b80b96f74ebebd5f4f3d156d2ad42c5` |
| `1.58125` | `[72,96,120,144]` | transition / max-lmax 144 | `4edbfcd8d6024876f6efdebd29e47736d36f1385ed29a8ad3ff6adf0e6704b9e` |
| `2.91875` | `[192,216,240,264]` | mid-high / max-lmax 264 | `d6b81923284142dfe5faf13e8932b4e5c12aed1cd253c459ab10641ab0949b8b` |
| `3.759375` | `[276,300,324,348]` | phase-failure neighborhood / max-lmax 348 | `22a82e643a9b348b82999f2f065f25e9e47b017582da964d1b33d2ec3473b386` |
| `3.89375` | `[288,312,336,360]` | high-frequency / max-lmax 360 | `770340a9dcfbd17abb5de160f6289de473c184c1de75297fb45a8e23626b35d3` |

每个 frequency 使用 exact 四个 lmax rows 和 exact 八个 ordered points：

```text
near_axis_x0_z30, near_axis_x1_z30,
near_axis_x2_z30, near_axis_x3_z30,
far_axis_x10_z30, far_axis_x15_z30,
far_axis_x20_z30, far_axis_x25_z30
```

共同 boundary contract 是 `M=1`、`r_in_eps=1e-6`、`r_out=300`、
`rtol=1e-10`、`atol=1e-12`。

Downstream full-image regression 是 read-only golden：

```text
runs/phase5/fig3_four_frequency_dx0p25_production/
  t8ah_li_fig3_xz_k1p0_dx0p25.npz
SHA-256 0de560ce7a2696074e708506240c69e43eb4d40520447ec378208b37f64c0132
shape 241x241
valid/masked 57884/197
convergence probes 48
```

Methods gate 可在 isolated benchmark directory 重现 exact config，但不得
覆盖 golden、生成 publication plot 或提升为 production artifact。87 个
diagnostic failed-child midpoints 明确不在上述 matrix 中。

### 8.2 Exact and floating equivalence budgets

以下内容必须 exact equal：

- array names、shapes、dtypes、units、axes、masks；
- frequency/point/lmax/history/final-row order；
- finite/nonfinite pattern；
- convention metadata；
- mode/channel 和 serial/two-worker reduction order；
- cache identity payload/rejection reason；
- checkpoint membership 和 canonical manifest order。
- 每 case 的 raw-warning `(category, source, line, message, count)` tuples、
  structured warning codes/count 和 warning order；unknown warning count 必须为
  zero。

Legacy 与 optimized radial/observable complex arrays 同时满足：

```text
max absolute difference             <= 5e-12
max normalized relative difference  <= 5e-10
```

当 legacy 与 optimized magnitudes 都大于 `1e-10` 时，按冻结 phase
convention 的 principal phase difference 必须 `<=5e-9 rad`。Guard 以下仍
必须比较 complex value，不能用 phase mask 隐藏 near-zero mismatch。
Magnitude 的 absolute/relative budget 相同。

Final-pair deltas 各自仍须 `<=1e-4`，legacy/new delta difference
`<=1e-10`。Boundary、Wronskian 和 effective residual 必须继续通过既有 hard
gates，且 optimized 不得恶化超过：

```text
max(legacy * 1.05, legacy + 5e-13)
```

Full-image 还必须满足：

| quantity | gate |
|---|---|
| coordinates、`valid_mask` | exact |
| complex `h_plus/h_cross` | abs `<=5e-12` 且 normalized rel `<=5e-10` |
| real/imag/abs pixel NRMSE | `<=1e-11` |
| normalized pixel L-infinity | `<=5e-10` |
| guarded phase difference | `<=5e-9 rad` |

不允许 resampling、smoothing、clipping、colormap trick、lower resolution
或 image-only normalization。

### 8.3 Performance and resource gates

Legacy 与 optimized 的每个 case 及 aggregate record 必须保存 wall time、
user CPU、system CPU、peak RSS、ODE/oracle solve counts、cache hit/miss/
rejection counts、stage timings、Python/NumPy/SciPy/platform/CPU/BLAS 和
controlled thread environment，以及 implementation/physics/solver/config/
source/gate/environment/artifact hashes。
Raw warnings 与 structured warnings 必须分别保存 exact tuples/codes/counts
和 classification；不得只保存一个总 warning 数。

Methods GREEN 除全部 equivalence gates 外还要求：

```text
total ODE/oracle solve count <= 0.70 * legacy
aggregate wall time          <= 0.85 * legacy
aggregate CPU time           <= 0.85 * legacy
each case wall time          <= 1.05 * legacy
peak RSS                     <= 1.25 * legacy
```

Timing noise 导致任一条件不满足时，结果是 YELLOW evidence incomplete；不得
降低 scientific work、放宽 tolerance 或删除 check。

### 8.4 Required layered and fault tests

Focused/fresh validation 至少覆盖：

- `ConventionMetadata`、six-component `ProvenanceIdentity`、scalar/coupled
  `ChannelSpec`、deterministic `ModeKey`、generic `ObserverPoint`、
  immutable complex `RadialStateBatch` 和十个 structural Protocol；
- non-Schwarzschild coupled mock 与 future time-domain mock，全部
  boundary/source/angular/backend/projector/writer components 均显式
  `physical_claim=false`；
- ordered sparse source/angular `m` tuple 和 `None -> -ell..+ell` fallback，
  generic test 不写入 `+z`/`m=±2` 假设；
- 默认 `compute_polarization` 恰好经过一次
  `LegacyScalarRWZAdapter.compute_polarization` full-path facade，并对
  accepted scalar RWZ path 做 golden/direct exact equivalence；private fast
  path 与 public typed amplitude path 一致，generic scalar amplitude 必须是
  exact shape `(1,)`；
- ordinary dense reuse 只发生在 certified interval，`valid_until_r` 和
  out-of-domain request fail closed；
- exact oracle hit，以及逐一改变 implementation/physics/solver/config/
  source/gate、artifact hash、schema、snapshot、origin、mode、point、radius、
  tolerance，以及 record 内嵌 diagnostics tolerance 后的 rejection；
- serial 与 two-worker results/order exact 一致，worker count `>2` 拒绝；
- truncated、corrupt、interrupted、stale-schema、wrong-identity、wrong-key、
  wrong-payload checkpoint quarantine；
- complete matching checkpoint reuse 且 worker 不被调用；partial/mismatched
  unit 不 reuse；
- exact downstream schema/full image arrays、stage profile 和 performance
  regression；matrix audit 必须是 exact five frozen frequencies 加 full
  `241x241` image 的六 case、exact order、无重复/遗漏，并同时生成 per-case
  与 aggregate resources。

还必须运行 current focused Q018 tests、exact-scope Ruff、fresh full pytest、
`git diff --check`、implementation/worktree/source identity checks 和
forbidden-output searches。任何 warning、test、identity、scope 或 provenance
mismatch 都不能用 benchmark performance 抵消。

### 8.5 Decision and non-claims

只有 code/tests、exact implementation identity、source/config identity、
resume contract、五频和 full-image evidence 全部冻结并通过后，T4ae 才能返回
`GREEN / EQUIVALENCE-PRESERVING METHODS GATE READY`。若仅 timing/performance
未达 GREEN，或其余 validity checks 均通过但 runtime evidence genuinely
missing，则返回 frozen YELLOW；若 identity/scope/source/config/artifact/
test/provenance/equivalence 任一 mismatch 或 failure，则 fail closed 返回
frozen RED。三种 decision 都必须保存当时可得的完整 evidence。本文档本身：

- 不改变 physics、tolerances、modes、frequencies、points 或 thresholds；
- 不实现或验证新的 spin-2/Teukolsky/coupled-channel theory；
- 不把 87 个 diagnostic midpoints 变成 scientific inputs；
- 不授权或启动 T7ch、T8、new frequency、production、plot、fixture、
  Kirchhoff、paper-style output 或 GitHub action。
