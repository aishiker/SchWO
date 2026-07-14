# Phase 4 T8n Prompt: Production Schema and Output Hardening

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8n`。

## 0. 任务定位

T7w 已复核 T8m production-readiness pilot，并建议在 full
M4-production high-resolution Fig.3 run 之前，先做 config/range 或
output-layout hardening。本 slice 就是这个 hardening。

不要运行完整四频 production grid，不要进入 M5 transmission，不要运行
`kM=4` stress，不要生成 R60_K2/R60_K4 fixtures。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/phase4_closeout.md`
4. `docs/m4_production_plan.md`
5. `docs/architecture.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `docs/prompts/phase4_t8m_m4_production_readiness_pilot.md`
9. `docs/prompts/phase4_t7w_m4_production_readiness_review.md`
10. Relevant current files in `src/schwgw/io`, `src/schwgw/viz`, `src/schwgw/cli.py`, `configs/`, and tests.

Before task actions, check installed plugins/connectors/skills. Use
`scientific-visualization` guidance if directly useful for figure-output
metadata and record any used skill in `status.md`.

## 2. Goals

Implement production-readiness hardening without changing physics:

1. Add range-based x-z observer config support:
   - Support explicit arrays as before.
   - Add `x_range` / `z_range` with `start`, `stop`, `step`, and
     `endpoint: true`.
   - Expand ranges into saved explicit coordinate arrays for reproducibility.
   - Reject ambiguous configs that provide both `x_values` and `x_range` for
     the same axis.
   - Add parser tests for endpoint inclusion, invalid step, inconsistent
     range, and backward compatibility.
2. Add production template config(s), but do not run them:
   - `configs/li_fig3_xz_production_k2p0_dx0p5.yaml` or similar single-frequency
     template is acceptable.
   - Mark clearly in comments/status that it is a production template, not an
     accepted artifact.
3. Harden plot output metadata:
   - `plot-fig3-panel` sidecar must include saved convergence final pair and
     final-pair pass flag, matching multi-frequency behavior.
   - Add configurable DPI for Fig.3 single and multi-frequency plot commands,
     defaulting to existing behavior if necessary, but allowing `dpi >= 300`.
   - Sidecar must record requested DPI and actual output format.
   - If PDF/vector export is straightforward, add it; otherwise document as a
     future output-layout item, not a blocker.
4. Keep plotting read-only over saved result files.
5. Update docs:
   - `docs/m4_production_plan.md` or a short addendum section noting the
     hardening result.
   - `docs/architecture.md` / `docs/validation_plan.md` only if needed to
     describe the new range config and production sidecar requirements.

## 3. Hard Limits

- Do not modify T2-T6 physics or frozen conventions.
- Do not modify radial solver behavior.
- Do not relax convergence thresholds.
- Do not reduce accepted `lmax` windows.
- Do not run full `121x121` four-frequency production.
- Do not run `kM=4`.
- Do not implement transmission.
- Do not move accepted `/tmp` artifacts.

## 4. Verification

Use TDD where practical. Required commands:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run a small smoke using range config only if cheap:

- one tiny x-z config with `x_range/z_range` and low `lmax`, saved to `/tmp`;
- plot it with `--dpi 300`;
- inspect the sidecar for range-expanded coordinates, DPI, final pair metadata
  if convergence is enabled, and read-only provenance.

## 5. Stop Conditions

Stop and update `status.md` if:

- range config cannot be implemented without large API churn;
- backward compatibility for explicit x/z arrays breaks;
- sidecar convergence metadata cannot be populated from saved results;
- plotting starts calling solver/physics code;
- tests fail;
- any required change touches T2-T6 physics or radial solver behavior.

## 6. status.md Update Requirements

Record changed files, commands run, test results, smoke artifact paths if any,
open issues, and whether T7x may review.

If T8n completes, next prompt:

```text
你现在是 T7x。请读取并严格执行 docs/prompts/phase4_t7x_production_schema_output_review.md。
```
