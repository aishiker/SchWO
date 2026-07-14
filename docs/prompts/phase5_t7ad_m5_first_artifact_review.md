# Phase 5 T7ad Prompt: First Archived M5 Artifact Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ad`。

## 0. 任务定位

T8r 应已从一个被接受的 M4-production saved result 生成第一件项目内归档的
M5 pointwise amplification artifact。你的任务是独立复核该 artifact 是否可以
被接受为 M5 first archived artifact。

This is an artifact-review gate.  Do not generate a new production artifact
unless a small temporary independent inspection file is unavoidable; no accepted
artifact may live only in `/tmp`.

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/m5_transmission_normalization.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/validation_plan.md`
7. `docs/phase4_production_closeout.md`
8. `runs/phase4/m4_production_first_pass/manifest.md`
9. `runs/phase5/m5_first_amplification_artifact/manifest.md`
10. `docs/prompts/phase5_t8r_m5_first_archived_amplification_artifact.md`
11. T8r changed/generated files listed in `status.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Review Checklist

Verify:

1. Source artifact is exactly:

   ```text
   runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz
   ```

2. Source SHA-256 matches:

   ```text
   1923663926ce09eae26bdc10eb94ac4092b9d3af2358f52164356312bef7a8e9
   ```

3. T8r generated artifacts only under:

   ```text
   runs/phase5/m5_first_amplification_artifact/
   ```

4. The amplification result is a saved `AmplificationGridResult` and preserves:
   - x-z grid shape `(121,121)`;
   - source path and source case metadata;
   - pointwise amplification normalization metadata;
   - baseline API metadata;
   - independent norm/plus/cross masks;
   - NaN/masked invalid entries.
5. `F_plus_complex/F_cross_complex` remain complex ratios and were not replaced
   by magnitudes.
6. `F_pol_norm`, `I_pol_ratio`, `amplification_plus`, and
   `amplification_cross` plots exist with JSON sidecars.
7. Plot sidecars record quantity, mask field, valid/invalid counts, source
   amplification result path, normalization metadata, baseline metadata, grid
   kind, output path, requested DPI, and coordinate ranges.
8. No full solver grid, radial solve, partial-wave recomputation, or accepted
   M4 artifact mutation occurred.
9. T8r did not open four-frequency M5, `kM=4`, R60_K2/R60_K4, arbitrary
   incident direction, or larger-domain work.

## 3. Verification Commands

Run:

```bash
shasum -a 256 runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz
find runs/phase5/m5_first_amplification_artifact -maxdepth 1 -type f -print | sort
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_transmission.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression/test_io_cli.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz || true
```

Also run an independent local inspection of:

```text
runs/phase5/m5_first_amplification_artifact/t8r_li_fig3_xz_k1p0_dx0p5_amplification.npz
```

and all T8r sidecar JSON files.  The inspection may use
`load_amplification_results(...)`, NumPy, and JSON.  It must not call solver,
radial, partial-wave, baseline, or plotting computation paths.

## 4. Pass Conditions

Pass only if:

- all review checklist items pass;
- artifact files exist under the project archive directory;
- source and generated checksums are recorded;
- targeted tests and full pytest pass;
- no convention drift or hidden solver recomputation is found;
- `status.md` records changed files, commands, test results, open issues, and
  next action.

If passed, recommend the next T0 decision as either:

```text
T8s four-frequency M5 archived amplification artifacts from accepted M4-production saved results
```

or a narrower metadata/visual-review hardening slice if any sidecar or manifest
field is acceptable but weak.

## 5. Stop Conditions

Stop and update `status.md` if:

- source checksum mismatch;
- generated artifacts are missing or outside the project archive;
- sidecars or manifest do not identify source/normalization/baseline/mask
  policy;
- invalid entries are finite-filled instead of NaN/masked;
- T8r mutated accepted M4 artifacts;
- T8r ran a full solver grid or opened gated `kM=4`/R60/arbitrary-direction
  scope;
- tests fail.
