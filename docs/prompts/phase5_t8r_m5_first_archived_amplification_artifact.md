# Phase 5 T8r Prompt: First Archived M5 Amplification Artifact

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8r`。

## 0. 任务定位

T6m/T8p/T8q 已经实现并通过 T7ab/T7ac 复核：

- M5 pointwise amplification core API；
- saved amplification schema / CLI smoke；
- saved amplification read-only plotting。

你的任务是生成第一件可归档的 M5 pointwise amplification artifact。只使用已经被
T7y/T7z 接受并归档在项目内的 M4-production saved result，不重新运行主物理求解器，
不生成四频 benchmark，不进入 `kM=4`、R60_K2/R60_K4 或 arbitrary incident
direction。

This is the first archived M5 artifact slice, not a broad production campaign.

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/m5_transmission_normalization.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/validation_plan.md`
7. `docs/phase4_production_closeout.md`
8. `runs/phase4/m4_production_first_pass/manifest.md`
9. `docs/prompts/phase5_t6m_m5_amplification_api.md`
10. `docs/prompts/phase5_t8p_m5_saved_output_schema.md`
11. `docs/prompts/phase5_t7ab_m5_api_schema_review.md`
12. `docs/prompts/phase5_t8q_m5_readonly_plotting_smoke.md`
13. `docs/prompts/phase5_t7ac_m5_plotting_review.md`
14. T8p/T8q changed files listed in `status.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Source Artifact

Use exactly one accepted M4-production saved result:

```text
runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz
```

Expected SHA-256 from the accepted manifest:

```text
1923663926ce09eae26bdc10eb94ac4092b9d3af2358f52164356312bef7a8e9
```

Verify the checksum before use.  Stop if it does not match.

Rationale for choosing `kM=1.0`: it is inside the accepted M4-production first
pass, has no Q018 evanescent-tail warnings, and is the smallest useful
first-artifact step before four-frequency M5 work.

## 3. Output Directory

Create and use:

```text
runs/phase5/m5_first_amplification_artifact/
```

All accepted outputs from this slice must live under this directory.  Temporary
files under `/tmp` are allowed during work, but no accepted artifact may remain
only under `/tmp`.

Suggested filenames:

```text
t8r_li_fig3_xz_k1p0_dx0p5_amplification.npz
t8r_li_fig3_xz_k1p0_F_pol_norm_300dpi.png
t8r_li_fig3_xz_k1p0_F_pol_norm_300dpi.png.json
t8r_li_fig3_xz_k1p0_I_pol_ratio_300dpi.png
t8r_li_fig3_xz_k1p0_I_pol_ratio_300dpi.png.json
t8r_li_fig3_xz_k1p0_amplification_plus_300dpi.png
t8r_li_fig3_xz_k1p0_amplification_plus_300dpi.png.json
t8r_li_fig3_xz_k1p0_amplification_cross_300dpi.png
t8r_li_fig3_xz_k1p0_amplification_cross_300dpi.png.json
manifest.md
```

## 4. Required Work

1. Verify the source artifact checksum.
2. Run the existing M5 CLI to compute amplification from the saved lensed
   result:

   ```bash
   PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli compute-amplification \
     runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz \
     --out runs/phase5/m5_first_amplification_artifact/t8r_li_fig3_xz_k1p0_dx0p5_amplification.npz
   ```

3. Plot the saved amplification result read-only, using the existing M5 plotting
   CLI:

   ```bash
   PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-amplification \
     runs/phase5/m5_first_amplification_artifact/t8r_li_fig3_xz_k1p0_dx0p5_amplification.npz \
     --quantity F_pol_norm \
     --out runs/phase5/m5_first_amplification_artifact/t8r_li_fig3_xz_k1p0_F_pol_norm_300dpi.png \
     --dpi 300

   PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-amplification \
     runs/phase5/m5_first_amplification_artifact/t8r_li_fig3_xz_k1p0_dx0p5_amplification.npz \
     --quantity I_pol_ratio \
     --out runs/phase5/m5_first_amplification_artifact/t8r_li_fig3_xz_k1p0_I_pol_ratio_300dpi.png \
     --dpi 300

   PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-amplification \
     runs/phase5/m5_first_amplification_artifact/t8r_li_fig3_xz_k1p0_dx0p5_amplification.npz \
     --quantity amplification_plus \
     --out runs/phase5/m5_first_amplification_artifact/t8r_li_fig3_xz_k1p0_amplification_plus_300dpi.png \
     --dpi 300

   PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-amplification \
     runs/phase5/m5_first_amplification_artifact/t8r_li_fig3_xz_k1p0_dx0p5_amplification.npz \
     --quantity amplification_cross \
     --out runs/phase5/m5_first_amplification_artifact/t8r_li_fig3_xz_k1p0_amplification_cross_300dpi.png \
     --dpi 300
   ```

4. Inspect the saved amplification result and plot sidecars.  Record at least:
   - shape;
   - source case id and source path;
   - source SHA-256;
   - `k`, `lmax`;
   - valid/invalid counts for norm/plus/cross masks;
   - finite/nonfinite valid counts for plotted quantities;
   - denominator threshold metadata;
   - baseline API metadata;
   - normalization kind;
   - grid kind and x-z ranges;
   - whether invalid entries remain NaN/masked.
5. Write `manifest.md` in the output directory with:
   - source artifact path and checksum;
   - generated artifact list;
   - file sizes and SHA-256 checksums;
   - commands run;
   - result metadata summary;
   - scope and exclusions.

## 5. Hard Limits

- Do not run `schwgw run` or any full solver grid.
- Do not call `run_solver_grid`, `compute_polarization`, or `solve_radial_mode`
  directly from this slice.
- Do not change `src/` unless a clear T8r blocker is found; if a blocker is
  found, stop and update `status.md` instead of silently patching production
  code.
- Do not change T6m formulas, T8p schema, T8q plotting semantics, Q005/Q014
  conventions, T4 radial solver behavior, thresholds, `lmax`, or accepted M4
  artifact metadata.
- Do not generate four-frequency M5 artifacts.
- Do not generate or validate `kM=4`, R60_K2/R60_K4, arbitrary incident
  direction, or larger-domain artifacts.
- Do not accept artifacts that exist only under `/tmp`.

## 6. Verification Commands

Run:

```bash
shasum -a 256 runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli compute-amplification --help
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-amplification --help
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_transmission.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression/test_io_cli.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz || true
```

Also run a small local inspection script or command that loads the generated
amplification NPZ and sidecar JSON files through the public IO functions or
standard JSON/NumPy readers.  Record the key metadata in `status.md`.

## 7. Stop Conditions

Stop and update `status.md` if:

- source checksum mismatch;
- `compute-amplification` tries to run the full solver grid;
- output generation is too slow for a single `121x121` `kM=1.0` artifact;
- result metadata lacks source/normalization/baseline/mask fields needed for
  review;
- plot sidecars cannot identify quantity, mask field, valid/invalid counts, or
  source path;
- invalid values are filled instead of remaining NaN/masked;
- tests fail.

## 8. Handoff

If passed, update `status.md` with changed files, generated artifacts, commands
run, test results, open issues, and next action.  Recommend:

```text
T7ad should independently review the first archived M5 amplification artifact before T0 opens four-frequency M5 artifacts or any R60/kM=4 work.
```
