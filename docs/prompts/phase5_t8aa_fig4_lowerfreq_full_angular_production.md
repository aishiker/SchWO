# Phase 5 T8aa Prompt: Fig.4 Lower-Frequency Full Angular Production

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8aa`。

T7av 已给出 **ACCEPT GREEN FOR LOWER-FREQUENCY FIG.4 READINESS ONLY**。本 slice 的唯一目标是运行已经通过 readiness review 的
`kM=0.5,1.0,1.5` lower-frequency full angular production configs，生成三个 `65 x 64` exact angular NPZ artifacts。

本 slice 不画图，不生成 fixtures，不生成 HDF5，不改 `src`，不改 configs，不重跑 `kM=2`，不运行 `kM=4`/R60_K4，不做
Fig.5/Fig.6，不实现 arbitrary incident direction，不引入 Kirchhoff baseline，不输出 strict `Psi4`。

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
9. `docs/prompts/phase5_t7av_fig4_lowerfreq_angular_readiness_review.md`
10. the three production configs:
    - `configs/r60_k0p5_fig4_exact_angular_first_pass.yaml`
    - `configs/r60_k1p0_fig4_exact_angular_first_pass.yaml`
    - `configs/r60_k1p5_fig4_exact_angular_first_pass.yaml`
11. the three selected-probe smoke configs:
    - `configs/r60_k0p5_fig4_exact_angular_selected_probe.yaml`
    - `configs/r60_k1p0_fig4_exact_angular_selected_probe.yaml`
    - `configs/r60_k1p5_fig4_exact_angular_selected_probe.yaml`
12. `src/schwgw/cli.py`
13. `src/schwgw/io/config.py`
14. `src/schwgw/io/results.py`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和 verification-before-completion；本 slice 不需要 web lookup。

## 2. Allowed Outputs

只允许生成以下三个 NPZ 文件：

```text
runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz
runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz
runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz
```

允许修改：

- `status.md`

禁止修改：

- `src/**`
- `tests/**`
- `configs/**`
- `docs/physics_spec.md`
- `docs/equation_map.md`
- `docs/numerics.md`
- `docs/validation_plan.md`
- any reference notes

If any of the three target NPZ files already exists before the run, stop **YELLOW / EXISTING ARTIFACTS NEED T0 DECISION** and do not overwrite.

## 3. Preflight

Before running solver commands, verify and record:

- T7av decision in `status.md` is GREEN for readiness only.
- All three selected-probe smoke NPZs exist and match the T7av accepted paths.
- Production directories are absent or empty.
- The three production configs have:
  - `observer.kind: angular`
  - `observer.r: 60.0`
  - expanded grid `theta_count=65`, `phi_count=64`
  - duplicate `2pi` excluded by `phi_range.endpoint: false`
  - `numerics.boundary.required_eval_radius: 60.0`
  - no `experimental_required_radius_oracle`
  - no `q018_riccati`
  - `numerics.lmax == convergence.lmax_values[-1]`

Expected production table:

| kM | case id | output | lmax | final pair |
|---:|---|---|---:|---|
| 0.5 | `R60_K0P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz` | 84 | `[72,84]` |
| 1.0 | `R60_K1P0_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz` | 108 | `[96,108]` |
| 1.5 | `R60_K1P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz` | 156 | `[132,156]` |

If preflight fails, stop RED or YELLOW with exact reason and do not run production.

## 4. Production Commands

Run exactly these three commands:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k0p5_fig4_exact_angular_first_pass.yaml --out runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1p0_fig4_exact_angular_first_pass.yaml --out runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1p5_fig4_exact_angular_first_pass.yaml --out runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz
```

Runtime stop conditions:

- Stop **YELLOW / runtime too high** if any single production run exceeds `3 h`.
- Stop **YELLOW / total runtime too high** if the total production run time exceeds `6 h`.
- Do not reduce `lmax`, remove grid points, relax convergence thresholds, add oracle opt-in, or alter configs to force completion.

## 5. Artifact Inspection

For each generated NPZ, inspect and record:

- SHA-256 and file size;
- case id;
- `kM`;
- grid kind `angular`, `r=60.0`;
- `theta.shape == (65,)`, `phi.shape == (64,)`;
- `h_plus/h_cross.shape == (65,64)`;
- all saved valid field values finite;
- final adjacent pair is the expected final pair;
- `diagnostics.lmax_convergence_policy.final_pair_passed is true`;
- final selected max relative change `<= 1e-4`;
- final near-axis max relative change `<= 1e-3`;
- no `q018_required_radius_oracle_used` warnings;
- no `evanescent_tail_required_radius_uncovered` failures;
- no forbidden `experimental_required_radius_oracle` metadata;
- radial cache metadata exists and records unique/key/hit counts;
- radial summary records Wronskian/boundary/condition diagnostics.

For `kM=1.5`, explicitly record `max_match_condition_number`. A very large condition number is a diagnostic for T7aw review; it is not by itself permission to relax thresholds.

## 6. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
find runs/phase5/fig4_exact_angular_k0p5 runs/phase5/fig4_exact_angular_k1p0 runs/phase5/fig4_exact_angular_k1p5 -maxdepth 2 -type f -print
find runs/phase5/fig4_lowerfreq_angular_readiness -maxdepth 2 -type f -print
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' -o -iname '*.h5' -o -iname '*.hdf5' \) -print
rg -n "experimental_required_radius_oracle|q018_riccati" configs/r60_k0p5_fig4_exact_angular_first_pass.yaml configs/r60_k1p0_fig4_exact_angular_first_pass.yaml configs/r60_k1p5_fig4_exact_angular_first_pass.yaml || true
```

Expected:

- targeted/full tests pass;
- production directories contain exactly the three authorized lower-frequency NPZs, one per directory;
- readiness directory still contains only the three selected-probe NPZs;
- no R60_K4/`kM=4`/HDF5/fixture outputs were generated;
- lower-frequency production configs still contain no Q018 oracle or Riccati opt-in.

## 7. Decision Labels

Use exactly one:

- **GREEN / READY FOR T7aw LOWER-FREQUENCY PRODUCTION ARTIFACT REVIEW**:
  all three full angular NPZs were generated, scoped, finite, final-pair converged, and tests passed.
- **YELLOW / DIAGNOSTIC PRODUCTION ARTIFACTS ONLY**:
  artifacts are scoped and useful, but one or more runtime/convergence/diagnostic concerns require T0/T7 decision.
- **RED / DO NOT REVIEW AS PRODUCTION**:
  forbidden outputs were generated, configs/source were modified outside scope, tests fail broadly, or physics/numerics policy changed.

## 8. status.md Update

Update `status.md` with:

- changed/generated files;
- files read;
- skill/plugin check;
- preflight result;
- exact production commands and runtimes;
- artifact inspection table;
- validation commands and results;
- decision label;
- open issues;
- exact next action:

```text
你现在是 T7aw。请读取并严格执行 docs/prompts/phase5_t7aw_fig4_lowerfreq_full_angular_artifact_review.md。
```
