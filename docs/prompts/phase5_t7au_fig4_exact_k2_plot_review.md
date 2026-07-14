# Phase 5 T7au Prompt: Review Fig.4 Exact kM=2 Read-Only Plot

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7au`。

只在 T8y 完成后运行。你的任务是独立复核 T8y 是否只从 T7as 已接受的 R60_K2 NPZ 读取数据，生成
fixed-`phi=0` Fig.4 exact finite-radius `|h_plus|/|h_cross|` plot 和 JSON sidecar。

本 review 通过只接受这个 `kM=2` read-only plot。不要授权 lower-frequency angular artifacts、all-frequency
Fig.4、Fig.5/Fig.6 scans、fixtures、R60_K4、`kM=4`、larger-domain、arbitrary incident direction、Kirchhoff baseline、
Appendix D/E asymptotic curves 或 strict `Psi4` outputs。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_r60_k2_angular_production_readiness.md`
8. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
9. `docs/prompts/phase5_t8y_fig4_exact_k2_readonly_plot.md`
10. T8y changed files listed in `status.md`
11. Source artifact:
    `runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz`
12. Plot artifact:
    `runs/phase5/q018_r60_k2_angular_production_first_pass/plots/r60_k2_fig4_exact_phi0_curves.png`
13. Plot sidecar:
    `runs/phase5/q018_r60_k2_angular_production_first_pass/plots/r60_k2_fig4_exact_phi0_curves.png.json`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和 verification-before-completion。
本 review 不需要外部文献检索。

## 2. Scope Checks

Verify:

- T8y did not run solver or generate new NPZ/HDF5/fixtures;
- T8y generated only the authorized PNG/JSON sidecar under the `plots/` directory;
- source NPZ still has SHA-256
  `065b2d3dacd5ab8657d0aa8e95fe3ee8b149efd3dd7d1d8b7375ac5df6cfadb2`;
- plot sidecar records that source SHA exactly;
- no R60_K4, `kM=4`, lower-frequency angular production, larger-domain, arbitrary-direction, Fig.5/Fig.6, Kirchhoff,
  Appendix D/E, or strict `Psi4` output was generated;
- `src/schwgw/viz` has no imports from `schwgw.scattering`, `schwgw.numerics`, `schwgw.angular`,
  `schwgw.backgrounds`, or `schwgw.perturbations`;
- the new CLI plot path does not call `compute_polarization`, `run_solver_grid`, `solve_radial_mode`, or any physics
  solver.

## 3. Artifact Checks

Inspect the sidecar. Required values:

```text
plot_type == fig4_exact_angular_curves
source_case_id == R60_K2_Q018_ANGULAR_PRODUCTION_FIRST_PASS
source_grid_kind == angular
source_r == 60.0
source_kM == 2.0
source_lmax == 180
field_names == ["h_plus", "h_cross"]
plotted_quantities == ["abs_h_plus", "abs_h_cross"]
curve_extraction_policy == fixed_phi_cut
phi_selected == 0.0
phi_selected_index == 0
theta_count == 65
phi_count == 64
no_phi_average == true
no_solver_rerun == true
no_field_recomputation == true
no_strict_psi4 == true
no_asymptotic_comparison == true
convergence_caveat == selected_17x8_final_pair_only_not_full_grid
final_lmax_pair == [156,180]
q018_oracle_warning_count == 56
q018_oracle_warning_code == q018_required_radius_oracle_used
q018_oracle_ell_range == [153,180]
q018_oracle_sectors includes even and odd
q018_opt_in == q018_riccati
output_format == png
requested_dpi == 300
```

Inspect the PNG:

- file exists and starts with PNG magic bytes;
- file size is nonzero and not suspiciously tiny;
- image array read by matplotlib/Pillow is finite/nonblank;
- axis/legend text need not be OCR-verified, but sidecar and code labels must not mention strict `Psi4` or asymptotic
  amplitudes.

Optionally perform a direct source-array check:

- load source NPZ;
- extract `theta`, `phi`, `abs(h_plus[:,0])`, `abs(h_cross[:,0])`;
- confirm sidecar selected `phi_selected_index=0` corresponds to `phi[0] == 0.0`.

Do not recompute polarization.

## 4. Validation Commands

Run at minimum:

```bash
test -f runs/phase5/q018_r60_k2_angular_production_first_pass/plots/r60_k2_fig4_exact_phi0_curves.png
test -f runs/phase5/q018_r60_k2_angular_production_first_pass/plots/r60_k2_fig4_exact_phi0_curves.png.json
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|numerics|angular|backgrounds|perturbations)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz src/schwgw/cli.py || true
find runs/phase5/q018_r60_k2_angular_production_first_pass -maxdepth 3 -type f -print
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' -o -iname '*.h5' -o -iname '*.hdf5' \) -print
```

If static `rg` reports existing CLI solver code for non-plot commands, inspect it and distinguish it from the new
Fig.4 plot path. Any forbidden import in `src/schwgw/viz` is RED.

## 5. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR FIG.4 kM=2 READ-ONLY PLOT ONLY**:
  PNG/sidecar exist and are scoped; source SHA/case/grid/frequency/phi/convergence/Q018 metadata are correct; tests
  pass; static checks show no forbidden viz imports or plot-path solver calls; no forbidden artifacts were generated.
- **ACCEPT YELLOW / PLOT DIAGNOSTIC ONLY**:
  plot exists but metadata, visual nonblank checks, static boundaries, or tests need a T8y revision before acceptance.
- **REJECT RED**:
  solver/physics recomputation occurred, metadata is fabricated or wrong, forbidden outputs were generated, tests fail,
  strict/package conventions are mixed, or source NPZ mismatch is found.

## 6. status.md Update

Update `status.md` with:

- changed files;
- files read;
- plugin/skill check;
- scope checks;
- sidecar inspection summary;
- PNG inspection summary;
- commands and test results;
- decision label;
- open issues;
- exact next action recommendation.

If GREEN, recommend that T0 choose one of the next separately gated directions:

1. lower-frequency Fig.4 exact angular artifacts;
2. read-only Table-I sparse four-frequency extraction from accepted M5 archive;
3. dense Fig.5/Fig.6 scan planning with `kM=4` gate;
4. T1/T10 Kirchhoff Eq. (47) convention freeze.

Do not authorize any of those directions from T7au itself.

