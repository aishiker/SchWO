# Phase 5 T8ab Prompt: Fig.4 All-Frequency Read-Only Angular Plot

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8ab`。

T7aw 已给出 **ACCEPT GREEN FOR LOWER-FREQUENCY FIG.4 PRODUCTION ARTIFACTS ONLY**。本 slice 的唯一目标是从四个已经
独立接受的 angular NPZ artifacts 读取数据，生成 one read-only all-frequency Fig.4 exact finite-radius angular plot
和 JSON sidecar。

本 slice 不运行 solver，不生成 NPZ/HDF5/fixtures，不改物理 convention，不做 Fig.5/Fig.6，不运行 `kM=4`/R60_K4，
不实现 arbitrary incident direction，不引入 Kirchhoff baseline，不输出 strict `Psi4`。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
8. `docs/prompts/phase5_t8y_fig4_exact_k2_readonly_plot.md`
9. `docs/prompts/phase5_t7au_fig4_exact_k2_plot_review.md`
10. `docs/prompts/phase5_t8aa_fig4_lowerfreq_full_angular_production.md`
11. `docs/prompts/phase5_t7aw_fig4_lowerfreq_full_angular_artifact_review.md`
12. `src/schwgw/viz/results.py`
13. `src/schwgw/viz/__init__.py`
14. `src/schwgw/cli.py`
15. `tests/unit/test_viz_results.py`
16. `tests/regression/test_plot_cli.py`
17. accepted source artifacts:
    - `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging、test-driven development、
verification-before-completion；如可用，使用 scientific-visualization 指导图像布局。此任务不需要外部文献检索。

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
runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png
runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png.json
```

禁止：

- 运行 `schwgw.cli run` 或任何 solver/grid-production command；
- 调用 `compute_polarization`、`solve_radial_mode`、`run_solver_grid`、T4/T6 physics code、oracles、scattering code；
- 在 `src/schwgw/viz/` 中导入 `schwgw.scattering`、`schwgw.numerics`、`schwgw.angular`、`schwgw.backgrounds`、
  `schwgw.perturbations`；
- 生成 `.npz`、`.h5`、`.hdf5`、regression fixture、R60_K4、`kM=4`、larger-domain 或 arbitrary-direction output；
- 平均 `phi`；
- 标注 strict `Psi4`、asymptotic amplitude、scattering amplitude、Kirchhoff baseline、Appendix D/E curve、或 Fig.5/Fig.6。

## 3. Required Implementation

Add a read-only visualization helper:

```text
plot_fig4_all_frequency_exact_angular_from_results(
    result_paths,
    *,
    output_path,
    phi=0.0,
    dpi=300,
)
```

Required behavior:

- require exactly four input paths in increasing `kM=[0.5,1.0,1.5,2.0]` order;
- load each source with `schwgw.io.results.load_results`;
- require saved grid kind `angular`;
- require each source has 1D `theta` and `phi`;
- require all four sources share identical `theta` and `phi` arrays within `atol=1e-12`, `rtol=0`;
- require `h_plus.shape == h_cross.shape == (65,64)` for each production source;
- require requested `phi` matches a saved phi value within strict tolerance, default `phi=0.0`;
- select exactly that phi index from each source; do not average over `phi`;
- plot two panels:
  - top or left panel: `abs(h_plus[:, phi_index])` vs `theta/pi`, four curves labeled by `kM`;
  - bottom or right panel: `abs(h_cross[:, phi_index])` vs `theta/pi`, four curves labeled by `kM`;
- label y-axis as exact finite-radius amplitude, not `Psi4`;
- title/caption may say `r=60M, kM=0.5,1.0,1.5,2.0, fixed phi=0`;
- support PNG output;
- write a JSON sidecar at `output_path + ".json"`;
- return the sidecar path.

Add CLI:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig4-all-frequency-exact-angular \
  RESULT_K0P5 RESULT_K1P0 RESULT_K1P5 RESULT_K2P0 \
  --out OUT.png --phi 0.0 --dpi 300
```

The CLI must call only the viz helper. It must not import solver/scattering/radial modules on this path.

## 4. Required Source Metadata

The four accepted source artifacts are:

| kM | case id | path | expected SHA-256 | lmax | final pair | Q018 oracle |
|---:|---|---|---|---:|---|---|
| 0.5 | `R60_K0P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz` | `a0d06ba4d3073c4f18e086439f1dd88255569a8a08afedf1ae47622738ce6c97` | 84 | `[72,84]` | absent |
| 1.0 | `R60_K1P0_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz` | `f76e975f0f70c3d83b10aa9320bce929d9f975d343f95945ee368a82055d7f09` | 108 | `[96,108]` | absent |
| 1.5 | `R60_K1P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz` | `76074eb9de412b4e7b94d27a78ffa1aa0541f17a1f0585dff94de5dc6c7c0931` | 156 | `[132,156]` | absent |
| 2.0 | `R60_K2_Q018_ANGULAR_PRODUCTION_FIRST_PASS` | `runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz` | `065b2d3dacd5ab8657d0aa8e95fe3ee8b149efd3dd7d1d8b7375ac5df6cfadb2` | 180 | `[156,180]` | `q018_riccati`, ell `153..180` |

If any source SHA differs, stop **YELLOW / SOURCE ARTIFACT CHANGED** and do not generate the production plot without T0 decision.

## 5. Required Sidecar Fields

The sidecar must include at least:

```text
plot_type = fig4_all_frequency_exact_angular_curves
source_npz_paths
source_npz_sha256
source_npz_size_bytes
source_case_ids
source_grid_kind = angular
source_r_values = [60.0, 60.0, 60.0, 60.0]
source_kM_values = [0.5, 1.0, 1.5, 2.0]
source_lmax_values = [84, 108, 156, 180]
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
no_kirchhoff_baseline = true
convergence_caveat = selected_17x8_final_pair_only_not_full_grid
final_lmax_pairs = [[72,84], [96,108], [132,156], [156,180]]
final_selected_max_relative_changes
final_near_axis_max_relative_changes
selected_thresholds
near_axis_thresholds
q018_oracle_warning_counts
q018_oracle_warning_codes
q018_oracle_ell_ranges
q018_opt_ins
radial_cache_unique_solution_counts
radial_cache_key_counts
radial_cache_hit_counts
k1p5_max_match_condition_number_diagnostic = 4.939017032749817e+144
created_by_cli
created_at
requested_dpi = 300
output_format = png
git_commit = null
git_status_available = false
source_code_sha_policy = unavailable_not_git_repository
```

For lower-frequency sources, Q018 fields should explicitly record no oracle usage, e.g. warning count `0`, opt-in `null`,
and ell range `null`. Do not fabricate physics values; derive from arrays/metadata or fail with a clear `PlotError`.

## 6. Tests

Use TDD. Add focused tests before implementation where practical.

Required unit tests in `tests/unit/test_viz_results.py`:

1. `plot_fig4_all_frequency_exact_angular_from_results` writes PNG and JSON sidecar from four synthetic angular results.
2. Sidecar records `plot_type`, fixed-phi policy, kM values, source SHA list, final pairs, `no_solver_rerun`,
   `no_phi_average`, `no_strict_psi4`, and `no_kirchhoff_baseline`.
3. The helper rejects non-four input count.
4. The helper rejects wrong `kM` ordering.
5. The helper rejects mismatched theta/phi grids.
6. The helper rejects a requested `phi` not present in saved phi coordinates.

Required CLI regression tests in `tests/regression/test_plot_cli.py`:

1. `plot-fig4-all-frequency-exact-angular` writes PNG and JSON sidecar from four synthetic angular NPZs.
2. Monkeypatch `cli.compute_polarization` to raise if called; the plot command must still pass.
3. CLI sidecar records `plot_type == "fig4_all_frequency_exact_angular_curves"`, `curve_extraction_policy == "fixed_phi_cut"`,
   `source_kM_values == [0.5, 1.0, 1.5, 2.0]`, `no_solver_rerun is true`, and `no_strict_psi4 is true`.

Preserve all existing plot commands and tests.

## 7. Required Production Plot

After tests pass, run exactly:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig4-all-frequency-exact-angular \
  runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz \
  runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz \
  runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz \
  runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz \
  --phi 0.0 \
  --dpi 300 \
  --out runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png
```

Expected:

- one PNG;
- one sidecar JSON;
- no new `.npz`, `.h5`, `.hdf5`, fixture, R60_K4, `kM=4`, larger-domain, Fig.5/Fig.6, Kirchhoff, Appendix D/E, or strict `Psi4` output.

## 8. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|numerics|angular|backgrounds|perturbations)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz src/schwgw/cli.py || true
find runs/phase5/fig4_all_frequency_exact_angular -maxdepth 2 -type f -print
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' -o -iname '*.h5' -o -iname '*.hdf5' \) -print
```

The static `rg` may show existing allowed CLI imports for non-plot commands. Inspect whether the new
`plot-fig4-all-frequency-exact-angular` path itself imports/calls forbidden modules. `src/schwgw/viz` must not import
forbidden physics modules.

## 9. Decision Labels

Use exactly one:

- **GREEN / READY FOR T7ax FIG.4 ALL-FREQUENCY PLOT REVIEW**:
  CLI/helper/tests are implemented; production PNG and sidecar exist; sidecar metadata matches all accepted source NPZs;
  no solver/data-generation/forbidden imports/scope expansion occurred; targeted and full pytest pass.
- **YELLOW / ALL-FREQUENCY PLOT DIAGNOSTIC ONLY**:
  plot exists but sidecar metadata is incomplete, tests are partial, PNG is visually/structurally suspect, or static boundary needs review.
- **REJECT RED**:
  solver or physics computation ran, forbidden data/fixtures were generated, strict/package convention was mixed,
  sidecar fabricates metadata, tests fail, or scope expands beyond accepted all-frequency fixed-`phi=0` plotting.

## 10. status.md Update

Update `status.md` with:

- changed files;
- generated files;
- files read;
- plugin/skill check;
- implementation summary;
- production plot command;
- sidecar inspection summary, including all four source SHAs;
- static/output search results;
- targeted/full pytest results;
- decision label;
- open issues;
- exact next action:

```text
你现在是 T7ax。请读取并严格执行 docs/prompts/phase5_t7ax_fig4_all_frequency_plot_review.md。
```
