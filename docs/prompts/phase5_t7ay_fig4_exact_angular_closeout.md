# Phase 5 T7ay Prompt: Fig.4 Exact-Angular Closeout

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ay`。

## 0. 任务定位

T8ab 已生成 fixed-`phi=0` all-frequency Fig.4 exact finite-radius angular PNG/JSON sidecar，T7ax 已独立复核通过。
你的任务是正式 close out 这组 Fig.4 exact-angular artifacts：冻结 accepted scope、source artifacts、plot artifact、
provenance、验证结论、限制、diagnostic caveats 和 remaining gates，防止后续线程把它误当成 Fig.5/Fig.6、Kirchhoff、
Appendix D/E、strict `Psi4`、`kM=4`、R60_K4、larger-domain 或 arbitrary-direction 验证。

This is a documentation/status closeout slice. Do not generate new numerical artifacts, do not modify `src/`, tests,
configs, source NPZs, or plot artifacts, and do not change physics conventions.

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
8. `docs/prompts/phase5_t8ab_fig4_all_frequency_readonly_plot.md`
9. `docs/prompts/phase5_t7ax_fig4_all_frequency_plot_review.md`
10. T8ab/T7ax records in `status.md`
11. accepted source artifacts:
    - `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz`
12. accepted plot artifacts:
    - `runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png`
    - `runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png.json`

Before task actions, check whether installed plugins/connectors/skills are directly useful. Use only directly relevant
ones and record any used skill in `status.md`. This closeout does not need web lookup.

## 2. Required Output

Create:

```text
docs/phase5_fig4_exact_angular_closeout.md
```

Update:

```text
status.md
```

Do not modify `src/`, tests, configs, source NPZs, plot artifacts, or reference notes unless a blocking inconsistency is
found. If a blocking inconsistency is found, stop and record it in `status.md`.

## 3. Closeout Document Requirements

`docs/phase5_fig4_exact_angular_closeout.md` must include:

1. Status and date.
2. Accepted scope:
   - Fig.4 exact finite-radius angular curves.
   - Frequencies `kM=[0.5,1.0,1.5,2.0]`.
   - Observer radius `r=60M`.
   - Angular grid `theta_count=65`, `phi_count=64`.
   - Fixed `phi=0` extraction only; no `phi` averaging.
   - Fields `h_plus`, `h_cross`; plotted quantities `|h_plus|`, `|h_cross|`.
   - Default `+z` incident direction and Route B packaged-polarization production path.
3. Accepted source artifact table:
   - path;
   - case id;
   - SHA-256;
   - file size;
   - `lmax`;
   - final adjacent pair;
   - selected and near-axis final relative changes;
   - Q018 oracle status.
4. Accepted plot artifact table:
   - PNG path, size, SHA-256;
   - JSON sidecar path, size, SHA-256;
   - plot type and extraction policy.
5. Provenance summary:
   - T8x/T7as accepted `kM=2` source;
   - T8y/T7au accepted single-frequency `kM=2` plot boundary;
   - T8z/T7av accepted lower-frequency readiness;
   - T8aa/T7aw accepted lower-frequency source artifacts;
   - T8ab/T7ax accepted all-frequency read-only plot.
6. Physics and convention summary:
   - Uses project production `h_plus/h_cross`, not strict NP scalars.
   - No Fourier, harmonic, tetrad, RW/Zerilli, Route B, Q014, Q015, or Q018 policy changes occurred in plotting/closeout.
   - The plot is exact finite-radius packaged-polarization output, not an asymptotic scattering amplitude.
7. Verification summary:
   - T7ax checked source SHAs, sidecar, nonblank PNG, fixed-`phi=0` policy, read-only viz boundary, and full pytest.
   - `src/schwgw/viz` remains free of solver/scattering imports.
   - No solver or new data-generation command was run by plotting.
8. Q018 / radial limitations:
   - `kM=2` source uses reviewed `q018_riccati` opt-in for ell range `153..180`.
   - `kM=0.5,1.0,1.5` sources use no Q018 oracle.
   - `kM=1.5` retains `max_match_condition_number=4.939017032749817e+144` as an explicit diagnostic caveat.
   - Convergence caveat: source convergence was selected `17 x 8` final-pair convergence, not full-grid convergence proof.
9. Explicit non-scope:
   - Fig.5/Fig.6 scans;
   - fixtures;
   - R60_K4;
   - `kM=4`;
   - larger-domain artifacts;
   - arbitrary incident direction;
   - Kirchhoff baseline;
   - Appendix D/E asymptotic curves;
   - strict `Psi4` outputs;
   - scalar baseline validation;
   - radial horizon transmission/absorption diagnostics;
   - pixel-for-pixel reference-paper reproduction.
10. Next-decision menu for T0:
   - Fig.5/Fig.6 Table-I point-frequency extraction planning;
   - dense Fig.5/Fig.6 scan with explicit `kM=4` gate;
   - Kirchhoff/Appendix D/E baseline convention review;
   - arbitrary incident direction / Wigner-D rotation integration;
   - larger-domain or R60_K4 Q018 re-check.

## 4. Required Verification

Run:

```bash
shasum -a 256 \
  runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz \
  runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz \
  runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz \
  runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz \
  runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png \
  runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png.json
find runs/phase5/fig4_all_frequency_exact_angular -maxdepth 2 -type f -print | sort
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' -o -iname '*.h5' -o -iname '*.hdf5' \) -print
```

Also inspect the Fig.4 sidecar JSON and record the source/plot SHA table in `status.md`.

Do not run `schwgw run`. Do not create new numerical artifacts.

## 5. Status Update Requirements

Update `status.md` with:

- changed files;
- files read;
- commands run and results;
- closeout decision;
- artifact/source SHA table;
- open issues;
- next action.

If the closeout passes, mark Fig.4 exact-angular all-frequency read-only artifacts as closed/accepted for their stated
scope and keep these gates explicitly open:

```text
Fig.5/Fig.6 scans
fixtures
R60_K4
kM=4
larger-domain artifacts
arbitrary incident direction
Kirchhoff baseline
Appendix D/E asymptotic curves
strict Psi4 outputs
```

## 6. Stop Conditions

Stop and update `status.md` if:

- any expected source or plot artifact is missing;
- any expected SHA-256 differs from T7ax records without a documented T0 decision;
- plot sidecar is inconsistent with T7ax records;
- the closeout would require modifying `src/`, tests, configs, source NPZs, or plot artifacts;
- full pytest fails;
- any convention drift is found;
- any new solver/data artifact is needed to write the closeout.

## 7. Handoff

If passed, recommend that T0 open a separate Fig.5/Fig.6 Table-I point-frequency extraction planning slice next.
Do not write implementation prompts for future slices inside T7ay unless the user explicitly asks for them.
