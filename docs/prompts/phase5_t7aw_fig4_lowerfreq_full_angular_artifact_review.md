# Phase 5 T7aw Prompt: Review Fig.4 Lower-Frequency Full Angular Artifacts

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7aw`。

只在 T8aa 完成后运行。你的任务是独立复核 T8aa 生成的 `kM=0.5,1.0,1.5` lower-frequency full angular
production NPZ artifacts。本 review 通过只表示这些 lower-frequency exact angular artifacts 可用于后续单独调度的
Fig.4 all-frequency read-only plotting；不要从 T7aw 直接授权 Fig.5/Fig.6、fixtures、R60_K4、`kM=4`、larger-domain、
arbitrary incident direction、Kirchhoff baseline、Appendix D/E asymptotic curves 或 strict `Psi4` outputs。

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
10. `docs/prompts/phase5_t8aa_fig4_lowerfreq_full_angular_production.md`
11. T8aa changed/generated files listed in `status.md`
12. the three production configs:
    - `configs/r60_k0p5_fig4_exact_angular_first_pass.yaml`
    - `configs/r60_k1p0_fig4_exact_angular_first_pass.yaml`
    - `configs/r60_k1p5_fig4_exact_angular_first_pass.yaml`
13. the three generated production NPZs:
    - `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz`
    - `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和 verification-before-completion。
本 review 不需要外部文献检索。

## 2. Scope Checks

Verify:

- T8aa did not modify `src/**`, `tests/**`, `configs/**`, convention docs, numerics docs, or reference notes.
- T8aa generated exactly the three authorized full angular NPZ files.
- T8aa did not generate plots, fixtures, HDF5, R60_K4, `kM=4`, larger-domain, arbitrary-direction, Fig.5/Fig.6, Kirchhoff,
  Appendix D/E, or strict `Psi4` outputs.
- The lower-frequency production configs do not contain `experimental_required_radius_oracle` or `q018_riccati`.
- The selected-probe readiness directory still contains only the three T7av-accepted smoke NPZs.

## 3. Artifact Checks

For each production NPZ, independently inspect and record:

| kM | expected case id | expected output | expected shape | lmax | expected final pair |
|---:|---|---|---|---:|---|
| 0.5 | `R60_K0P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz` | `65 x 64` | 84 | `[72,84]` |
| 1.0 | `R60_K1P0_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz` | `65 x 64` | 108 | `[96,108]` |
| 1.5 | `R60_K1P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz` | `65 x 64` | 156 | `[132,156]` |

Required checks:

- SHA-256 and file size recorded;
- case id and `kM` match expected;
- grid kind `angular`, `r=60.0`;
- `theta.shape == (65,)`, `phi.shape == (64,)`;
- `h_plus/h_cross.shape == (65,64)`;
- all saved valid `h_plus/h_cross` values are finite;
- duplicate `2pi` is not present in `phi`;
- final adjacent pair is the expected final pair;
- `diagnostics.lmax_convergence_policy.final_pair_passed is true` for GREEN;
- final selected max relative change `<= 1e-4`;
- final near-axis max relative change `<= 1e-3`;
- no `q018_required_radius_oracle_used` warnings;
- no forbidden `experimental_required_radius_oracle` metadata;
- no `evanescent_tail_required_radius_uncovered` failure metadata;
- radial cache metadata exists and records unique/key/hit counts;
- source/config metadata points to the expected config and not to `/tmp`.

For `kM=1.5`, explicitly report `max_match_condition_number`. If it remains extremely large while boundary residual,
Wronskian proxy, finite fields, warning count, and final-pair convergence pass, classify it as a recorded diagnostic
rather than silently ignoring it. Do not relax any threshold to hide it.

## 4. Bounded Direct Consistency Check

Run a bounded consistency check for at least one saved angular point per frequency:

- compare the saved field at `theta=0`, `phi=0` against a direct one-point computation using the same production config parameters;
- use the same boundary policy and no Q018 oracle;
- compare `h_plus` and `h_cross` with `rtol=1e-10`, `atol=1e-12`;
- record the command/script, values, and max absolute/relative differences.

If this direct check exceeds `90 min` total, stop **YELLOW / direct consistency check runtime too high** and record which artifacts were otherwise inspectable.

## 5. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
find runs/phase5/fig4_exact_angular_k0p5 runs/phase5/fig4_exact_angular_k1p0 runs/phase5/fig4_exact_angular_k1p5 -maxdepth 2 -type f -print
find runs/phase5/fig4_lowerfreq_angular_readiness -maxdepth 2 -type f -print
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' -o -iname '*.h5' -o -iname '*.hdf5' \) -print
rg -n "experimental_required_radius_oracle|q018_riccati" configs/r60_k0p5_fig4_exact_angular_first_pass.yaml configs/r60_k1p0_fig4_exact_angular_first_pass.yaml configs/r60_k1p5_fig4_exact_angular_first_pass.yaml || true
```

Also run a Python metadata inspection script over the three production NPZs and record the resulting table in `status.md`.

## 6. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR LOWER-FREQUENCY FIG.4 PRODUCTION ARTIFACTS ONLY**:
  all three full angular NPZs are scoped, finite, final-pair converged, directly consistent at bounded probe points, and tests pass.
  T0 may schedule a separate read-only all-frequency Fig.4 plotting prompt using these three artifacts plus the already accepted `kM=2` artifact.
- **ACCEPT YELLOW / DIAGNOSTIC ARTIFACTS ONLY**:
  artifacts are scoped and useful, but one or more convergence/runtime/direct-check/diagnostic concerns prevent GREEN acceptance.
- **REJECT RED**:
  forbidden outputs were generated, configs/source were modified outside scope, tests fail broadly, physics/numerics policy changed, or artifact metadata is inconsistent.

## 7. status.md Update

Update `status.md` with:

- changed/generated/reviewed files;
- files read;
- skill/plugin check;
- scope checks;
- artifact inspection table;
- bounded direct consistency check result;
- validation commands and test results;
- decision label;
- open issues;
- exact next action recommendation.

If GREEN, recommend that T0 schedule a separate T8 read-only all-frequency Fig.4 plotting prompt. Do not write that plotting prompt from T7aw.
