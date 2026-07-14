# Phase 4 T8f Prompt: x-z Plane Schema for Li Fig.3-Lite

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8f`。

## 启动条件

- T8e cached saved-benchmark runner 已完成。
- T7n independent cached benchmark review 已通过。
- `R60_K1_LI_FIG4_LITE` fixed-radius angular saved benchmark 已可生成并被复核。
- Q014 remains closed。
- Q015 remains separate structured radial diagnostic metadata。
- Q016 remains resolved。

## 背景和裁决

本 slice 进入 Li Fig.3-lite 的前置工作，但只做 **x-z plane spatial-grid schema + smoke output**。

不要直接生成论文级 Fig.3 大图。当前目标是让保存结果能够表达：

- Cartesian-like x-z plane observer grid；
- 每个 grid point 对应的 `(r, theta, phi)`；
- horizon/interior mask；
- raw complex `h_plus/h_cross`；
- read-only plotting from saved x-z result。

完成后再由后续 slice 决定是否运行 benchmark-grade Fig.3-lite grid。

## 先读

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/architecture.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase4_t8e_cached_benchmark_runner.md`
8. `docs/prompts/phase4_t7n_cached_benchmark_review.md`
9. `references/manifest.md`
10. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
11. `src/schwgw/io/config.py`
12. `src/schwgw/io/results.py`
13. `src/schwgw/viz/results.py`
14. `src/schwgw/cli.py`
15. `tests/unit/test_io_config.py`
16. `tests/unit/test_io_results.py`
17. `tests/unit/test_viz_results.py`
18. `tests/regression/test_io_cli.py`
19. `tests/regression/test_plot_cli.py`

## 目标

1. Extend YAML config to support a backward-compatible `observer.kind`.
2. Keep existing angular configs valid when `observer.kind` is omitted.
3. Add `observer.kind: xz_plane` with explicit `x_values` and `z_values`.
4. Convert x-z points to Schwarzschild spherical coordinates for the production solver:

```text
r = sqrt(x^2 + z^2)
theta = arccos(z / r)
phi = 0 for x >= 0, pi for x < 0
```

5. Mask invalid points with `r <= 2M` or non-finite coordinates; do not call the solver there.
6. Save x-z coordinate arrays and `valid_mask` in `.npz` and `.h5`.
7. Let `plot-wavefield` render x-z plane results from saved data only.
8. Add a small x-z smoke config and tests.

## 允许修改

- `src/schwgw/io/config.py`
- `src/schwgw/io/results.py`
- `src/schwgw/viz/results.py`
- `src/schwgw/cli.py` only if tiny wiring is needed
- `tests/unit/test_io_config.py`
- `tests/unit/test_io_results.py`
- `tests/unit/test_viz_results.py`
- `tests/regression/test_io_cli.py`
- `tests/regression/test_plot_cli.py`
- `configs/r60_k1_xz_plane_smoke.yaml`
- `docs/architecture.md`
- `docs/numerics.md`
- `docs/validation_plan.md`
- `status.md`

## 禁止修改

- 不修改 T2-T6 physics code。
- 不修改 `src/schwgw/numerics/radial_solver.py`。
- 不修改 Wigner-D/angular code。
- 不改变 Fourier/harmonic/tetrad/RW-Zerilli/polarization conventions。
- 不实现 transmission factor。
- 不生成 R60_K2/R60_K4。
- 不运行 paper-scale Fig.3 grid。
- 不把 smoke grid 称为 physics benchmark。
- 不让 plotting code 调用 solver。

## Config schema

Existing angular configs must remain valid:

```yaml
observer:
  r: 60.0
  theta_values: [0.0]
  phi_values: [0.0]
```

Treat omitted `observer.kind` as `angular`.

New x-z plane config:

```yaml
observer:
  kind: xz_plane
  x_values: [-12.0, -6.0, 0.0, 6.0, 12.0]
  z_values: [4.0, 8.0, 16.0, 32.0, 48.0, 60.0]
  invalid_radius_policy: mask
```

Validation rules:

- `observer.kind` must be `angular` or `xz_plane`.
- For `angular`, require `r`, `theta_values`, `phi_values` as before.
- For `xz_plane`, require nonempty numeric `x_values` and `z_values`.
- `invalid_radius_policy` may only be `mask` in this slice.
- Do not require all x-z points to have `r>2M`; invalid points are masked.
- Require at least one valid point.
- `numerics.boundary.r_out` must be greater than the maximum valid radius.

## Result schema

Angular outputs must remain backward compatible:

```text
theta
phi
h_plus
h_cross
metadata_json
```

x-z outputs must include:

```text
x
z
r
theta
phi
valid_mask
h_plus
h_cross
metadata_json
```

Shape convention:

```text
x.shape == (n_x,)
z.shape == (n_z,)
r.shape == theta.shape == phi.shape == valid_mask.shape == (n_z, n_x)
h_plus.shape == h_cross.shape == (n_z, n_x)
```

Invalid masked points:

- `valid_mask == False`
- `h_plus` and `h_cross` should be `nan + nan*j`
- diagnostics should count skipped/invalid points
- solver must not be called for invalid points

Metadata must include:

```python
metadata["grid"] = {
    "kind": "xz_plane",
    "x_values": [...],
    "z_values": [...],
    "valid_point_count": ...,
    "invalid_point_count": ...,
    "coordinate_conversion": "r=sqrt(x^2+z^2), theta=arccos(z/r), phi=0 if x>=0 else pi",
}
```

For angular output, metadata may use `metadata["grid"]["kind"] = "angular"` if convenient, but must not break existing readers/tests.

## Plotting

`plot-wavefield` must detect x-z result metadata/arrays and render:

- x on horizontal axis;
- z on vertical axis;
- masked invalid values as blank/transparent or masked-array NaN gaps;
- no physics recomputation.

Sidecar JSON should include:

- source result path;
- grid kind;
- case id;
- component/quantity;
- `kM`;
- lmax;
- coordinate ranges;
- valid/invalid point counts;
- convention summary.

Do not modify `plot-convergence` except for tiny metadata compatibility if necessary.

## Smoke config

Create `configs/r60_k1_xz_plane_smoke.yaml`:

```yaml
case_id: R60_K1_XZ_PLANE_SMOKE
output: /tmp/r60_k1_xz_plane_smoke.npz
background:
  M: 1.0
wave:
  kM: 1.0
  A_plus:
    real: 0.9
    imag: 1.1
  A_cross:
    real: 0.4
    imag: 0.6
observer:
  kind: xz_plane
  x_values: [-12.0, -6.0, 0.0, 6.0, 12.0]
  z_values: [4.0, 8.0, 16.0, 32.0, 48.0, 60.0]
  invalid_radius_policy: mask
numerics:
  lmax: 8
  boundary:
    r_in_eps: 1.0e-6
    r_out: 120.0
    rtol: 1.0e-9
    atol: 1.0e-11
convergence:
  enabled: true
  lmax_values: [4, 6, 8]
  theta_values: [0.0, 0.05, 0.2]
  phi_values: [0.0]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
```

This is schema/CLI/plot smoke only. It is not a benchmark-quality Fig.3 reproduction.

## Tests

Add or update tests proving:

1. Angular configs still parse and old smoke tests still pass.
2. x-z configs parse into a typed observer config.
3. invalid x-z points are masked and skipped.
4. coordinate conversion matches expected `r, theta, phi`.
5. saved `.npz` and `.h5` include x-z arrays and `valid_mask`.
6. fake solver is called only on valid x-z points.
7. run-scoped radial cache metadata is still present for x-z runs when production-like solver accepts `radial_solver`.
8. `plot-wavefield` can render x-z result PNG + sidecar from saved `.npz`.
9. `plot-wavefield` does not call solver.
10. existing angular plotting/convergence tests still pass.

## 必须运行

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression/test_io_cli.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_xz_plane_smoke.yaml --out /tmp/t8f_r60_k1_xz_plane_smoke.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8f_r60_k1_xz_plane_smoke.npz --component h_plus --quantity abs --out /tmp/t8f_xz_hplus_abs.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8f_r60_k1_xz_plane_smoke.npz --component h_cross --quantity abs --out /tmp/t8f_xz_hcross_abs.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8f_r60_k1_xz_plane_smoke.npz --out /tmp/t8f_xz_convergence.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If HDF5 is available:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_xz_plane_smoke.yaml --out /tmp/t8f_r60_k1_xz_plane_smoke.h5
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8f_r60_k1_xz_plane_smoke.h5 --component h_plus --quantity abs --out /tmp/t8f_xz_hplus_abs_h5.png
```

## 停止条件

Stop and update `status.md` if:

- x-z schema requires changing T2-T6 physics APIs.
- plotting must call solver.
- invalid/horizon mask cannot be represented JSON-safely.
- existing angular configs/readers break.
- smoke x-z run is too slow for local review.
- convergence metadata cannot coexist with x-z grid metadata.
- implementing full Fig.3 benchmark becomes necessary to test schema.

## 完成后

Update `status.md` with:

- changed files;
- commands run;
- tests;
- x-z schema summary;
- artifact paths;
- valid/invalid point counts;
- convergence metadata summary;
- read-only plotting boundary result;
- open issues;
- next action:

```text
Send T7: 你现在是 T7o。请读取并严格执行 docs/prompts/phase4_t7o_xz_plane_schema_review.md。
```

