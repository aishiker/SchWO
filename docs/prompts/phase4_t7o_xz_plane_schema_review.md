# Phase 4 T7o Prompt: x-z Plane Schema Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7o`。

## 启动条件

- 只在 T8f 完成 x-z plane schema + smoke output 后启动。
- 如果 `configs/r60_k1_xz_plane_smoke.yaml` 或 `/tmp/t8f_r60_k1_xz_plane_smoke.npz` 不存在，不要代替 T8 实现；记录 blocker 并交回 T8/T0。

## 先读

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/architecture.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase4_t8f_xz_plane_schema.md`
8. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
9. `configs/r60_k1_xz_plane_smoke.yaml`
10. T8f-changed `src/schwgw/io/config.py`
11. T8f-changed `src/schwgw/io/results.py`
12. T8f-changed `src/schwgw/viz/results.py`
13. T8f-changed tests

## 目标

独立复核 T8f 是否正确加入 x-z plane saved-result schema，并保持：

- angular configs/results backward compatible；
- x-z coordinate conversion correct；
- invalid/horizon points masked and skipped；
- saved `.npz`/`.h5` schema JSON-safe；
- plotting read-only over saved result；
- convergence metadata still present；
- no T2-T6 physics/convention changes。

## 允许修改

- `tests/regression/*` only for lightweight review tests if needed
- `docs/validation_plan.md` only for review checklist wording
- `status.md`

原则上不要修改 `src/`、configs 或 artifacts。若发现 implementation issue，record failure and return to T8f.

## 禁止修改

- 不修改 T2-T6 physics code。
- 不修改 radial solver equations/boundaries/thresholds。
- 不修改 Wigner-D/angular code。
- 不改变 conventions。
- 不实现 transmission factor。
- 不生成 R60_K2/R60_K4。
- 不运行 paper-scale Fig.3 grid。
- 不把 smoke grid 称为 benchmark。

## 复核任务

1. Config compatibility
   - Existing angular configs still parse.
   - `configs/r60_k1_xz_plane_smoke.yaml` parses with `observer.kind=xz_plane`.
   - Invalid schema cases fail clearly:
     - missing `x_values`;
     - all points inside `r<=2M`;
     - unsupported `invalid_radius_policy`.

2. Coordinate conversion
   - For representative points, verify:

```text
r = sqrt(x^2 + z^2)
theta = arccos(z/r)
phi = 0 for x >= 0, pi for x < 0
```

   - Confirm at least one masked point test exists or is manually inspected.

3. Saved result schema
   - Run or inspect `/tmp/t8f_r60_k1_xz_plane_smoke.npz`.
   - Confirm arrays:
     - `x`
     - `z`
     - `r`
     - `theta`
     - `phi`
     - `valid_mask`
     - `h_plus`
     - `h_cross`
     - `metadata_json`
   - Confirm shapes:

```text
x.shape == (n_x,)
z.shape == (n_z,)
r/theta/phi/valid_mask/h_plus/h_cross shape == (n_z,n_x)
```

   - Confirm invalid points, if any, have `valid_mask=False` and `nan+nanj` fields.
   - Confirm valid points are finite.
   - Confirm metadata has `grid.kind == "xz_plane"` and valid/invalid counts.

4. Runner behavior
   - Confirm solver is called only for valid points.
   - Confirm run-scoped radial cache still works and metadata includes `diagnostics.run_radial_cache`.
   - Confirm `diagnostics.radial_diagnostic_warnings` remains a JSON-safe list.
   - Confirm convergence metadata still exists for the smoke config.

5. Plot review
   - Generate from saved result:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8f_r60_k1_xz_plane_smoke.npz --component h_plus --quantity abs --out /tmp/t7o_xz_hplus_abs.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8f_r60_k1_xz_plane_smoke.npz --component h_cross --quantity abs --out /tmp/t7o_xz_hcross_abs.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8f_r60_k1_xz_plane_smoke.npz --out /tmp/t7o_xz_convergence.png
```

   - Confirm PNGs are non-empty.
   - Confirm sidecar JSON records source path, grid kind, case id, component/quantity, `kM`, lmax, coordinate ranges, valid/invalid counts, and convention.

6. Read-only plotting boundary
   - Scan `src/schwgw/viz/*`.
   - Confirm no imports from:
     - `schwgw.scattering`
     - `schwgw.perturbations`
     - `schwgw.angular`
     - `schwgw.numerics`
     - `schwgw.backgrounds`
   - Confirm `plot-wavefield` and `plot-convergence` do not call solver or `run_solver_grid(...)`.

## 必须运行

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/unit/test_wigner.py tests/unit/test_spin_weighted_harmonics.py tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_xz_plane_smoke.yaml --out /tmp/t7o_r60_k1_xz_plane_smoke.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t7o_r60_k1_xz_plane_smoke.npz --component h_plus --quantity abs --out /tmp/t7o_xz_hplus_abs.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t7o_r60_k1_xz_plane_smoke.npz --component h_cross --quantity abs --out /tmp/t7o_xz_hcross_abs.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t7o_r60_k1_xz_plane_smoke.npz --out /tmp/t7o_xz_convergence.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If HDF5 exists or `h5py` is available:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_xz_plane_smoke.yaml --out /tmp/t7o_r60_k1_xz_plane_smoke.h5
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t7o_r60_k1_xz_plane_smoke.h5 --component h_plus --quantity abs --out /tmp/t7o_xz_hplus_abs_h5.png
```

Run an explicit metadata inspection script or one-liner and record:

- grid kind;
- x/z shape;
- valid/invalid point counts;
- finite valid field check;
- convergence final pair and pass/fail;
- run cache stats;
- warning count.

## 停止条件

Stop and report to T0 if:

- x-z result schema cannot be loaded without breaking angular result loading;
- coordinate conversion is wrong or undocumented;
- invalid points call solver or are not masked;
- plotting imports/calls physics solver;
- smoke run is too slow for local review;
- tests fail outside T7o review scope;
- T8f changed T2-T6 physics/conventions.

## 完成后

Update `status.md` with:

- changed files;
- commands run;
- test results;
- x-z schema review;
- metadata/artifact summary;
- read-only plotting boundary result;
- open issues;
- go/no-go:
  - If passed: T0 may start a later T8g benchmark-grade Li Fig.3-lite run using the x-z schema.
  - If failed: return to T8f with exact failure mode.

