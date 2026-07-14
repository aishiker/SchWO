# Phase 5 T7av Prompt: Review Fig.4 Lower-Frequency Angular Readiness

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7av`。

只在 T8z 完成后运行。你的任务是独立复核 `kM=0.5,1.0,1.5` Fig.4 exact angular readiness：
production config drafts 是否正确，bounded selected-probe smoke artifacts 是否有限且通过 final-pair convergence，
lower-frequency configs 是否没有使用 Q018 oracle，是否没有误生成 full production grids、plots、fixtures、R60_K4、
`kM=4` 或 Fig.5/Fig.6 outputs。

本 review 通过只表示 T0 可以考虑后续单独调度 lower-frequency full angular production run；不要从 T7av 直接授权
full production 或 all-frequency Fig.4 plotting。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
8. `docs/prompts/phase5_t8z_fig4_lowerfreq_angular_readiness.md`
9. T8z changed/generated files listed in `status.md`
10. All six lower-frequency configs created by T8z.
11. All selected-probe smoke NPZs created by T8z.

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和 verification-before-completion。
本 review 不需要外部文献检索。

## 2. Scope Checks

Verify:

- T8z did not run full `65 x 64` lower-frequency production grids;
- T8z did not generate plots, fixtures, HDF5, R60_K4, `kM=4`, larger-domain, arbitrary-direction, Fig.5/Fig.6, Kirchhoff,
  Appendix D/E, or strict `Psi4` outputs;
- production draft configs exist but production output directories are empty or absent;
- selected-probe readiness directory contains only the three authorized NPZs;
- lower-frequency configs do not contain `experimental_required_radius_oracle` or `q018_riccati`;
- `required_eval_radius=60.0` is present in all lower-frequency configs;
- `numerics.lmax == convergence.lmax_values[-1]` in all six configs.

## 3. Config Checks

For production configs:

- `kM=0.5`, case `R60_K0P5_FIG4_EXACT_ANGULAR_FIRST_PASS`, output
  `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz`, `lmax=84`,
  `lmax_values=[36,48,60,72,84]`;
- `kM=1.0`, case `R60_K1P0_FIG4_EXACT_ANGULAR_FIRST_PASS`, output
  `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz`, `lmax=108`,
  `lmax_values=[60,72,84,96,108]`;
- `kM=1.5`, case `R60_K1P5_FIG4_EXACT_ANGULAR_FIRST_PASS`, output
  `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz`, `lmax=156`,
  `lmax_values=[84,108,132,156]`.

All production configs must expand to angular `theta_count=65`, `phi_count=64`, duplicate `2pi` excluded.

For smoke configs:

- case ids end with `_SELECTED_PROBE`;
- output paths are under `runs/phase5/fig4_lowerfreq_angular_readiness/`;
- angular grid expands to `theta_count=17`, `phi_count=8`;
- convergence probes use the same `17 x 8` selected subset;
- thresholds are `selected_threshold=1e-4` and `near_axis_threshold=1e-3`.

## 4. Smoke Artifact Checks

For each smoke NPZ:

- expected case id;
- grid kind `angular`, `r=60.0`;
- `theta.shape == (17,)`, `phi.shape == (8,)`;
- `h_plus/h_cross.shape == (17,8)`;
- all saved valid `h_plus/h_cross` values are finite;
- final adjacent pair is the last pair of the configured `lmax_values`;
- `diagnostics.lmax_convergence_policy.final_pair_passed is true` for GREEN;
- final selected max relative change `<= 1e-4`;
- final near-axis max relative change `<= 1e-3`;
- no `q018_required_radius_oracle_used` warnings;
- no forbidden `experimental_required_radius_oracle` metadata;
- run radial cache metadata exists and records unique/key/hit counts.

If any final pair fails, classify as YELLOW rather than GREEN.

## 5. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
find runs/phase5/fig4_lowerfreq_angular_readiness -maxdepth 2 -type f -print
find runs/phase5/fig4_exact_angular_k0p5 runs/phase5/fig4_exact_angular_k1p0 runs/phase5/fig4_exact_angular_k1p5 -maxdepth 2 -type f -print 2>/dev/null || true
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' -o -iname '*.h5' -o -iname '*.hdf5' \) -print
rg -n "experimental_required_radius_oracle|q018_riccati" configs/r60_k0p5_fig4_exact_angular_first_pass.yaml configs/r60_k1p0_fig4_exact_angular_first_pass.yaml configs/r60_k1p5_fig4_exact_angular_first_pass.yaml configs/r60_k0p5_fig4_exact_angular_selected_probe.yaml configs/r60_k1p0_fig4_exact_angular_selected_probe.yaml configs/r60_k1p5_fig4_exact_angular_selected_probe.yaml || true
```

Also run a Python metadata inspection script over the three smoke NPZs and record the table in `status.md`.

## 6. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR LOWER-FREQUENCY FIG.4 READINESS ONLY**:
  configs and selected-probe smoke artifacts are scoped; all three final pairs pass; no Q018 oracle is used; tests pass;
  no forbidden outputs/scope changes occurred. T0 may schedule a separate full production run prompt.
- **ACCEPT YELLOW / PARTIAL READINESS ONLY**:
  one or more frequencies fail convergence/runtime/radial coverage but the diagnostics are scoped and useful.
- **REJECT RED**:
  forbidden outputs were generated, lower-frequency configs use Q018 oracle, tests fail broadly, or physics/numerics
  policy changed.

## 7. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- scope checks;
- config inspection summary;
- smoke artifact inspection summary;
- commands and test results;
- decision label;
- open issues;
- exact next action recommendation.

If GREEN, recommend that T0 schedule a separate T8 production prompt for lower-frequency full angular artifacts, followed
by another T7 artifact review. Do not write that production prompt from T7av.

