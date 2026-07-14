# Phase 5 T7ax Prompt: Review Fig.4 All-Frequency Read-Only Plot

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ax`。

只在 T8ab 完成后运行。你的任务是独立复核 T8ab 生成的 read-only all-frequency Fig.4 exact finite-radius angular
plot 和 JSON sidecar。这个 review 通过只表示该 fixed-`phi=0` all-frequency Fig.4 plot artifact 可被接受；不要从
T7ax 授权 Fig.5/Fig.6、fixtures、R60_K4、`kM=4`、larger-domain、arbitrary incident direction、Kirchhoff baseline、
Appendix D/E asymptotic curves 或 strict `Psi4` outputs。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
8. `docs/prompts/phase5_t8ab_fig4_all_frequency_readonly_plot.md`
9. T8ab changed/generated files listed in `status.md`
10. `src/schwgw/viz/results.py`
11. `src/schwgw/viz/__init__.py`
12. `src/schwgw/cli.py`
13. `tests/unit/test_viz_results.py`
14. `tests/regression/test_plot_cli.py`
15. source artifacts:
    - `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz`
16. generated plot artifacts:
    - `runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png`
    - `runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png.json`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和 verification-before-completion；如可用，可用
scientific-visualization 辅助图像质量检查。本 review 不需要外部文献检索。

## 2. Scope Checks

Verify:

- T8ab did not run `schwgw.cli run` or generate any new solver/data NPZ.
- T8ab generated exactly the authorized PNG and JSON sidecar under
  `runs/phase5/fig4_all_frequency_exact_angular/`.
- T8ab did not generate fixtures, HDF5, R60_K4, `kM=4`, larger-domain, arbitrary-direction, Fig.5/Fig.6, Kirchhoff,
  Appendix D/E, or strict `Psi4` outputs.
- `src/schwgw/viz` does not import forbidden physics modules.
- The new `plot-fig4-all-frequency-exact-angular` CLI path does not call `compute_polarization`, `run_solver_grid`,
  `solve_radial_mode`, scattering code, radial code, or Q018 oracle code.
- The plot does not average over `phi`; it is fixed `phi=0`.

## 3. Source Artifact Checks

Confirm the four source artifacts and SHAs:

| kM | expected case id | expected SHA-256 | expected shape | lmax | final pair |
|---:|---|---|---|---:|---|
| 0.5 | `R60_K0P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `a0d06ba4d3073c4f18e086439f1dd88255569a8a08afedf1ae47622738ce6c97` | `65 x 64` | 84 | `[72,84]` |
| 1.0 | `R60_K1P0_FIG4_EXACT_ANGULAR_FIRST_PASS` | `f76e975f0f70c3d83b10aa9320bce929d9f975d343f95945ee368a82055d7f09` | `65 x 64` | 108 | `[96,108]` |
| 1.5 | `R60_K1P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `76074eb9de412b4e7b94d27a78ffa1aa0541f17a1f0585dff94de5dc6c7c0931` | `65 x 64` | 156 | `[132,156]` |
| 2.0 | `R60_K2_Q018_ANGULAR_PRODUCTION_FIRST_PASS` | `065b2d3dacd5ab8657d0aa8e95fe3ee8b149efd3dd7d1d8b7375ac5df6cfadb2` | `65 x 64` | 180 | `[156,180]` |

Confirm all four sources have:

- grid kind `angular`, `r=60.0`;
- shared `theta` and `phi` arrays;
- no duplicate `2pi` in `phi`;
- finite saved fields;
- final-pair convergence accepted in their source metadata;
- Q018 oracle usage only for `kM=2`.

## 4. Plot And Sidecar Checks

For the generated PNG:

- file exists and starts with PNG signature;
- file size is nontrivial;
- visual inspection is not blank;
- it contains two panels or otherwise clearly separates `|h_plus|` and `|h_cross|`;
- each panel has four distinguishable curves labeled by `kM`;
- axes are `theta/pi` and exact finite-radius amplitude;
- no label says `Psi4`, asymptotic amplitude, Kirchhoff, Appendix D/E, or Fig.5/Fig.6.

For the JSON sidecar, verify:

- `plot_type == "fig4_all_frequency_exact_angular_curves"`;
- `source_kM_values == [0.5, 1.0, 1.5, 2.0]`;
- source paths and SHA-256 values exactly match the expected table;
- `source_lmax_values == [84, 108, 156, 180]`;
- `field_names == ["h_plus", "h_cross"]`;
- `plotted_quantities == ["abs_h_plus", "abs_h_cross"]`;
- `curve_extraction_policy == "fixed_phi_cut"`;
- `phi_selected == 0.0`;
- `phi_selected_index == 0`;
- `theta_count == 65`;
- `phi_count == 64`;
- `no_phi_average is true`;
- `no_solver_rerun is true`;
- `no_field_recomputation is true`;
- `no_strict_psi4 is true`;
- `no_asymptotic_comparison is true`;
- `no_kirchhoff_baseline is true`;
- `final_lmax_pairs == [[72,84], [96,108], [132,156], [156,180]]`;
- `k1p5_max_match_condition_number_diagnostic == 4.939017032749817e+144` or an equivalent JSON number;
- lower-frequency Q018 counts are zero/null as appropriate;
- `kM=2` Q018 metadata records the reviewed `q018_riccati` opt-in and ell range `153..180`.

## 5. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|numerics|angular|backgrounds|perturbations)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz src/schwgw/cli.py || true
find runs/phase5/fig4_all_frequency_exact_angular -maxdepth 2 -type f -print
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' -o -iname '*.h5' -o -iname '*.hdf5' \) -print
```

Also run a Python sidecar/source inspection script and record the resulting table in `status.md`.

## 6. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR FIG.4 ALL-FREQUENCY READ-ONLY PLOT ONLY**:
  PNG and sidecar are scoped, nonblank, source SHAs match, fixed-`phi=0` policy is recorded, no solver/data generation happened,
  and targeted/full pytest pass. T0 may decide whether to schedule a closeout note for Fig.4 exact angular artifacts or move to
  a separate Fig.5/Fig.6 planning/extraction slice.
- **ACCEPT YELLOW / FIG.4 PLOT DIAGNOSTIC ONLY**:
  plot exists and is scoped but sidecar, visual quality, tests, or static boundary require follow-up before acceptance.
- **REJECT RED**:
  solver or physics computation ran, forbidden outputs were generated, source SHAs mismatch without T0 authorization, tests fail broadly,
  sidecar fabricates metadata, or scope expands beyond fixed-`phi=0` all-frequency Fig.4 plotting.

## 7. status.md Update

Update `status.md` with:

- changed/generated/reviewed files;
- files read;
- skill/plugin check;
- scope checks;
- source artifact SHA table;
- plot/sidecar inspection summary;
- static/output search results;
- targeted/full pytest results;
- decision label;
- open issues;
- exact next action recommendation.

If GREEN, recommend that T0 either schedule a short Fig.4 exact-angular closeout note, or open a separate Fig.5/Fig.6 Table-I point-frequency scan planning/extraction slice. Do not write those prompts from T7ax.
