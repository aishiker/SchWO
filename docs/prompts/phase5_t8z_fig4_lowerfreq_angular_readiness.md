# Phase 5 T8z Prompt: Fig.4 Lower-Frequency Angular Readiness

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8z`。

T7au 已接受 `kM=2` fixed-`phi=0` read-only Fig.4 plot。下一步不是直接跑三频 full angular production，
而是先做 lower-frequency Fig.4 exact angular readiness：为 `kM=0.5,1.0,1.5` 创建 production config drafts，
并运行 bounded selected-probe smoke artifacts，确认 schema、metadata、radial coverage、finite fields、final-pair
convergence 和 no-Q018-oracle policy 都可复核。

本 slice 不生成 full `65 x 64` production angular artifacts，不画图，不生成 fixtures，不运行 `kM=2` 或 `kM=4`，
不实现 Kirchhoff baseline，不做 Fig.5/Fig.6 extraction，不改物理 convention。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
8. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
9. `docs/prompts/phase5_t7au_fig4_exact_k2_plot_review.md`
10. `configs/r60_k2_q018_angular_production_first_pass.yaml`
11. `src/schwgw/io/config.py`
12. `src/schwgw/io/results.py`
13. `src/schwgw/cli.py`
14. `tests/unit/test_io_config.py`
15. `tests/regression/test_io_cli.py`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging、verification-before-completion；如果你修改
config parser 或 IO tests，再使用 test-driven development。本 slice 不需要 web lookup。

## 2. Scope

允许修改/新增：

- lower-frequency production draft configs:
  - `configs/r60_k0p5_fig4_exact_angular_first_pass.yaml`
  - `configs/r60_k1p0_fig4_exact_angular_first_pass.yaml`
  - `configs/r60_k1p5_fig4_exact_angular_first_pass.yaml`
- bounded selected-probe smoke configs:
  - `configs/r60_k0p5_fig4_exact_angular_selected_probe.yaml`
  - `configs/r60_k1p0_fig4_exact_angular_selected_probe.yaml`
  - `configs/r60_k1p5_fig4_exact_angular_selected_probe.yaml`
- if needed, narrowly scoped config/IO tests for existing range parsing only;
- `status.md`.

允许生成 bounded selected-probe smoke NPZs only:

```text
runs/phase5/fig4_lowerfreq_angular_readiness/r60_k0p5_fig4_exact_angular_selected_probe.npz
runs/phase5/fig4_lowerfreq_angular_readiness/r60_k1p0_fig4_exact_angular_selected_probe.npz
runs/phase5/fig4_lowerfreq_angular_readiness/r60_k1p5_fig4_exact_angular_selected_probe.npz
```

禁止：

- 不生成 full `65 x 64` lower-frequency production NPZ；
- 不生成 plot、PNG、PDF、fixture、HDF5；
- 不运行 accepted `kM=2` source again；
- 不运行 `kM=4`、R60_K4、larger-domain 或 arbitrary incident direction；
- 不使用 `experimental_required_radius_oracle` for `kM=0.5,1.0,1.5`；
- 不修改 physics formulas、radial solver、Q018 policy、thresholds、`lmax` policy、Route B convention；
- 不把 selected-probe smoke 说成 full Fig.4 all-frequency acceptance。

## 3. Required Configs

Use common settings:

```yaml
background:
  M: 1.0
wave:
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: angular
  r: 60.0
numerics:
  boundary:
    r_in_eps: 1.0e-6
    r_out: 300.0
    rtol: 1.0e-10
    atol: 1.0e-12
    required_eval_radius: 60.0
```

Do **not** include `experimental_required_radius_oracle`.

Production draft observer grid for all three frequencies:

```yaml
theta_range:
  start: 0.0
  stop: 3.141592653589793
  step: 0.04908738521234052
  endpoint: true
phi_range:
  start: 0.0
  stop: 6.283185307179586
  step: 0.09817477042468103
  endpoint: false
```

Selected-probe smoke observer grid for all three frequencies:

```yaml
theta_values:
  - 0.0
  - 0.19634954084936207
  - 0.39269908169872414
  - 0.5890486225480862
  - 0.7853981633974483
  - 0.9817477042468103
  - 1.1780972450961724
  - 1.3744467859455345
  - 1.5707963267948966
  - 1.7671458676442586
  - 1.9634954084936207
  - 2.1598449493429825
  - 2.356194490192345
  - 2.552544031041707
  - 2.748893571891069
  - 2.945243112740431
  - 3.141592653589793
phi_values:
  - 0.0
  - 0.7853981633974483
  - 1.5707963267948966
  - 2.356194490192345
  - 3.141592653589793
  - 3.9269908169872414
  - 4.71238898038469
  - 5.497787143782138
```

Convergence probes should use the same `17 x 8` selected subset, not full-grid convergence.

Frequency-specific settings:

| kM | production case id | smoke case id | production output | smoke output | lmax | lmax_values |
|---:|---|---|---|---|---:|---|
| 0.5 | `R60_K0P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `R60_K0P5_FIG4_EXACT_ANGULAR_SELECTED_PROBE` | `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz` | `runs/phase5/fig4_lowerfreq_angular_readiness/r60_k0p5_fig4_exact_angular_selected_probe.npz` | 84 | `[36,48,60,72,84]` |
| 1.0 | `R60_K1P0_FIG4_EXACT_ANGULAR_FIRST_PASS` | `R60_K1P0_FIG4_EXACT_ANGULAR_SELECTED_PROBE` | `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz` | `runs/phase5/fig4_lowerfreq_angular_readiness/r60_k1p0_fig4_exact_angular_selected_probe.npz` | 108 | `[60,72,84,96,108]` |
| 1.5 | `R60_K1P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `R60_K1P5_FIG4_EXACT_ANGULAR_SELECTED_PROBE` | `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz` | `runs/phase5/fig4_lowerfreq_angular_readiness/r60_k1p5_fig4_exact_angular_selected_probe.npz` | 156 | `[84,108,132,156]` |

Thresholds:

```yaml
selected_threshold: 1.0e-4
near_axis_threshold: 1.0e-3
```

## 4. Preflight Checks

Before running smoke configs, parse all six configs and verify:

- production configs expand to `theta_count=65`, `phi_count=64`, total `4160`;
- smoke configs expand to `theta_count=17`, `phi_count=8`, total `136`;
- `required_eval_radius=60.0` is present;
- `experimental_required_radius_oracle` is absent;
- `numerics.lmax == convergence.lmax_values[-1]`;
- no output path points to `/tmp`;
- no output path overlaps the accepted R60_K2 output directory;
- no config references `kM=2`, `kM=4`, R60_K4, or arbitrary incident direction.

If any preflight check fails, stop RED without running smoke.

## 5. Required Smoke Runs

Run the three smoke configs only:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k0p5_fig4_exact_angular_selected_probe.yaml --out runs/phase5/fig4_lowerfreq_angular_readiness/r60_k0p5_fig4_exact_angular_selected_probe.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1p0_fig4_exact_angular_selected_probe.yaml --out runs/phase5/fig4_lowerfreq_angular_readiness/r60_k1p0_fig4_exact_angular_selected_probe.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1p5_fig4_exact_angular_selected_probe.yaml --out runs/phase5/fig4_lowerfreq_angular_readiness/r60_k1p5_fig4_exact_angular_selected_probe.npz
```

Runtime cap: stop and report **YELLOW / runtime too high** if any single smoke run exceeds `90 min`. Do not reduce
`lmax`, remove points, relax thresholds, or add oracle opt-in to force completion.

For GREEN, each smoke artifact must satisfy:

- expected case id;
- angular grid `theta.shape=(17,)`, `phi.shape=(8,)`;
- `h_plus/h_cross.shape == (17,8)`;
- all saved valid field values finite;
- `diagnostics.final_lmax_pair` is the final adjacent pair in its `lmax_values`;
- `diagnostics.lmax_convergence_policy.final_pair_passed is true`;
- final selected max relative change `<= 1e-4`;
- final near-axis max relative change `<= 1e-3`;
- no `q018_required_radius_oracle_used` warnings;
- no `evanescent_tail_required_radius_uncovered` failures;
- radial diagnostic warnings, if any, are JSON-safe and not Q018 oracle usage.

If a lower-frequency smoke fails due to radial coverage at `r=60`, stop YELLOW/RED with the exact error and do not
generate production drafts beyond files already written.

## 6. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
find runs/phase5/fig4_lowerfreq_angular_readiness -maxdepth 2 -type f -print
find runs/phase5/fig4_exact_angular_k0p5 runs/phase5/fig4_exact_angular_k1p0 runs/phase5/fig4_exact_angular_k1p5 -maxdepth 2 -type f -print 2>/dev/null || true
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' -o -iname '*.h5' -o -iname '*.hdf5' \) -print
rg -n "experimental_required_radius_oracle|q018_riccati" configs/r60_k0p5_fig4_exact_angular_first_pass.yaml configs/r60_k1p0_fig4_exact_angular_first_pass.yaml configs/r60_k1p5_fig4_exact_angular_first_pass.yaml configs/r60_k0p5_fig4_exact_angular_selected_probe.yaml configs/r60_k1p0_fig4_exact_angular_selected_probe.yaml configs/r60_k1p5_fig4_exact_angular_selected_probe.yaml || true
```

Expected:

- targeted/full tests pass;
- readiness directory contains only the three selected-probe NPZs;
- full production directories contain no files yet;
- no R60_K4/`kM=4`/HDF5/fixture outputs;
- the `rg` command returns no output for lower-frequency configs.

## 7. Decision Labels

Use exactly one:

- **GREEN / READY FOR T7av LOWER-FREQUENCY READINESS REVIEW**:
  configs are created; preflight passes; all three selected-probe smoke artifacts pass final-pair convergence and finite
  checks; no Q018 oracle is used; tests pass; no forbidden outputs/scope changes occurred.
- **YELLOW / PARTIAL READINESS ONLY**:
  one or more smoke runs time out, fail radial coverage, or fail convergence, while scope remains controlled and
  diagnostics are useful.
- **REJECT RED**:
  configs use forbidden oracle, wrong outputs are generated, `kM=4`/R60_K4/production grids run accidentally, tests fail
  broadly, or physics/numerics policy is changed.

## 8. status.md Update

Update `status.md` with:

- changed files;
- generated files;
- files read;
- skill/plugin check;
- preflight table for all six configs;
- smoke artifact inspection table for each frequency;
- convergence summary;
- warning/error summary;
- commands and test results;
- decision label;
- open issues;
- exact next action:

```text
你现在是 T7av。请读取并严格执行 docs/prompts/phase5_t7av_fig4_lowerfreq_angular_readiness_review.md。
```

