# Phase 5 T8y Prompt: Fig.4 Exact kM=2 Read-Only Angular Plot

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8y`。

只在 T7at 返回 **ACCEPT GREEN FOR FIG.4/FIG.5 PLAN ONLY** 后运行。本 slice 只做一件事：
从已经由 T7as 接受的 R60_K2 angular production NPZ 中读取 `kM=2` exact finite-radius
`h_plus/h_cross` 数据，生成一个 fixed-`phi=0` 的 Fig.4 exact angular curve PNG 和 JSON sidecar。

不要运行 solver，不要生成新的 NPZ/HDF5/fixture，不要生成 lower-frequency angular artifacts，不要做
Fig.5/Fig.6 extraction，不要实现 Kirchhoff baseline，不要实现 Appendix D/E asymptotic comparison，不要输出 strict
`Psi4`。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_r60_k2_angular_production_readiness.md`
8. `docs/phase5_m5_four_frequency_closeout.md`
9. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
10. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
11. `docs/prompts/phase5_t10e_fig4_fig5_reproduction_planning.md`
12. `docs/prompts/phase5_t7at_fig4_fig5_plan_review.md`
13. `src/schwgw/cli.py`
14. `src/schwgw/viz/__init__.py`
15. `src/schwgw/viz/results.py`
16. `src/schwgw/io/results.py`
17. `tests/unit/test_viz_results.py`
18. `tests/regression/test_plot_cli.py`
19. Accepted source artifact:
    `runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging、test-driven development、verification before
completion。此任务不需要外部文献检索；如发现 plot policy 与 T10e/T7at 冲突，停止交 T0/T10。

## 2. Scope

允许修改：

- `src/schwgw/viz/results.py`
- `src/schwgw/viz/__init__.py`
- `src/schwgw/cli.py`
- `tests/unit/test_viz_results.py`
- `tests/regression/test_plot_cli.py`
- `status.md`

允许生成：

```text
runs/phase5/q018_r60_k2_angular_production_first_pass/plots/r60_k2_fig4_exact_phi0_curves.png
runs/phase5/q018_r60_k2_angular_production_first_pass/plots/r60_k2_fig4_exact_phi0_curves.png.json
```

禁止：

- 运行 `schwgw.cli run` 或任何 solver/grid-production command；
- 调用 `compute_polarization`、`solve_radial_mode`、`run_solver_grid`、T4/T6 physics code、oracles、scattering code；
- 在 `src/schwgw/viz/` 中导入 `schwgw.scattering`、`schwgw.numerics`、`schwgw.angular`、`schwgw.backgrounds`、
  `schwgw.perturbations`；
- 生成 `.npz`、`.h5`、`.hdf5`、regression fixture、lower-frequency output、R60_K4、`kM=4`、larger-domain 或
  arbitrary-direction output；
- 平均 `phi`；
- 标注 strict `Psi4`、asymptotic amplitude、scattering amplitude、Kirchhoff baseline 或 all-frequency Fig.4。

## 3. Required Implementation

Add a read-only visualization helper:

```text
plot_fig4_exact_angular_from_result(
    result_path,
    *,
    output_path,
    phi=0.0,
    dpi=300,
)
```

Required behavior:

- load with `schwgw.io.results.load_results`;
- require saved grid kind `angular`;
- require `theta` and `phi` are 1D arrays;
- require `h_plus.shape == h_cross.shape == (theta.size, phi.size)`;
- require requested `phi` matches an existing saved phi value within a strict tolerance, default `phi=0.0`;
- select exactly that phi index, default index `0`;
- plot `abs(h_plus[:, phi_index])` and `abs(h_cross[:, phi_index])` vs `theta/pi`;
- label y-axis as exact finite-radius amplitude, not `Psi4`;
- title or caption text may say `r=60M, kM=2, fixed phi=0`, but must not imply all-frequency reproduction;
- support PNG output; PDF support is optional but not required in T8y;
- write a JSON sidecar at `output_path + ".json"`.

Add CLI:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig4-exact-angular \
  RESULT --out OUT.png --phi 0.0 --dpi 300
```

The CLI must call only the viz helper. It must not import solver/scattering/radial modules.

## 4. Required Sidecar Fields

The sidecar must include at least:

```text
plot_type = fig4_exact_angular_curves
source_npz_path
source_npz_sha256
source_npz_size_bytes
source_case_id
source_grid_kind = angular
source_r = 60.0
source_kM = 2.0
source_lmax = 180
field_names = ["h_plus", "h_cross"]
plotted_quantities = ["abs_h_plus", "abs_h_cross"]
curve_extraction_policy = fixed_phi_cut
phi_selected = 0.0
phi_selected_index = 0
theta_count = 65
phi_count = 64
theta_range
phi_range
no_phi_average = true
no_solver_rerun = true
no_field_recomputation = true
no_strict_psi4 = true
no_asymptotic_comparison = true
convergence_caveat = selected_17x8_final_pair_only_not_full_grid
final_lmax_pair = [156,180]
final_selected_max_relative_change
final_near_axis_max_relative_change
selected_threshold
near_axis_threshold
q018_oracle_warning_count = 56
q018_oracle_warning_code = q018_required_radius_oracle_used
q018_oracle_ell_range = [153,180]
q018_oracle_ell_count = 28
q018_oracle_sectors = ["even","odd"]
q018_required_eval_radius = 60.0
q018_opt_in = q018_riccati
q018_valid_at_required_radius = true
radial_cache_unique_solution_count = 358
radial_cache_key_count = 358
radial_cache_hit_count = 1644506
created_by_cli
created_at
requested_dpi = 300
output_format = png
git_commit = null
git_status_available = false
source_code_sha_policy = unavailable_not_git_repository
```

Use values from the source NPZ metadata where available. If a field is absent, do not fabricate physics values; either
derive it directly from arrays/metadata or fail with a clear `PlotError`.

## 5. Tests

Use TDD. Add focused tests before implementation where practical.

Required unit tests in `tests/unit/test_viz_results.py`:

1. `plot_fig4_exact_angular_from_result` writes PNG and JSON sidecar from a synthetic angular result.
2. Sidecar records `plot_type`, fixed phi policy, `no_solver_rerun`, `no_phi_average`, fields, theta/phi counts, and
   source SHA.
3. The helper rejects x-z plane results.
4. The helper rejects a requested `phi` not present in saved phi coordinates.

Required CLI regression tests in `tests/regression/test_plot_cli.py`:

1. `plot-fig4-exact-angular` writes PNG and JSON sidecar from a synthetic angular NPZ.
2. Monkeypatch `cli.compute_polarization` to raise if called; the plot command must still pass.
3. CLI sidecar records `plot_type == "fig4_exact_angular_curves"`, `curve_extraction_policy == "fixed_phi_cut"`,
   `no_solver_rerun is true`, and `no_strict_psi4 is true`.

Preserve all existing plot commands and tests.

## 6. Required Production Plot

After tests pass, run exactly:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig4-exact-angular \
  runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz \
  --phi 0.0 \
  --dpi 300 \
  --out runs/phase5/q018_r60_k2_angular_production_first_pass/plots/r60_k2_fig4_exact_phi0_curves.png
```

Expected:

- one PNG;
- one sidecar JSON;
- no other files in the `plots/` directory unless explicitly produced by this command and listed.

Inspect the sidecar and confirm source SHA:

```text
065b2d3dacd5ab8657d0aa8e95fe3ee8b149efd3dd7d1d8b7375ac5df6cfadb2
```

## 7. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|numerics|angular|backgrounds|perturbations)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz src/schwgw/cli.py || true
find runs/phase5/q018_r60_k2_angular_production_first_pass -maxdepth 3 -type f -print
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' -o -iname '*.h5' -o -iname '*.hdf5' \) -print
```

The static `rg` may show existing allowed CLI imports for non-plot commands. You must inspect whether the new
`plot-fig4-exact-angular` path itself imports/calls forbidden modules. `src/schwgw/viz` must not import forbidden
physics modules.

## 8. Decision Labels

Use exactly one:

- **GREEN / READY FOR T7au FIG.4 PLOT REVIEW**:
  CLI/helper/tests are implemented; production PNG and sidecar exist; sidecar metadata matches the accepted source NPZ;
  no solver/data-generation/forbidden imports/scope expansion occurred; targeted and full pytest pass.
- **YELLOW / PLOT DIAGNOSTIC ONLY**:
  plot exists but sidecar metadata is incomplete, tests are partial, PNG is visually/structurally suspect, or static
  boundary needs review before acceptance.
- **REJECT RED**:
  solver or physics computation ran, forbidden data/fixtures were generated, strict/package convention was mixed,
  sidecar fabricates metadata, tests fail, or scope expands beyond accepted `kM=2` fixed-`phi=0` plotting.

## 9. status.md Update

Update `status.md` with:

- changed files;
- generated files;
- files read;
- plugin/skill check;
- implementation summary;
- production plot command;
- sidecar inspection summary;
- static/output search results;
- targeted/full pytest results;
- decision label;
- open issues;
- exact next action:

```text
你现在是 T7au。请读取并严格执行 docs/prompts/phase5_t7au_fig4_exact_k2_plot_review.md。
```

