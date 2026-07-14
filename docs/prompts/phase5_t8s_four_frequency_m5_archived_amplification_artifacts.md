# Phase 5 T8s Prompt: Four-Frequency M5 Archived Amplification Artifacts

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8s`。

## 0. 任务定位

T8r 已从接受的 M4-production `kM=1.0` saved result 生成第一件项目内 M5
pointwise amplification artifact，并已通过 T7ad 独立复核。T7ad 还记录了一个
非阻塞 provenance hardening 建议：source SHA-256 目前只在 manifest 中，不在
amplification NPZ / plot sidecar metadata 中。

你的任务是生成四频 M5 archived amplification artifacts，并同时做这个窄
metadata hardening：每个生成的 amplification NPZ metadata 和每个 plot sidecar
都必须记录对应 M4 source SHA-256。

This is a saved-result artifact-generation slice.  It must not run a new
wave-field solver grid.

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
11. `docs/prompts/phase5_t7ad_m5_first_artifact_review.md`
12. T8p/T8q/T8r changed files listed in `status.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Source Artifacts

Use exactly these accepted M4-production saved results and expected SHA-256
checksums:

| kM | Source path | Expected SHA-256 |
|---:|---|---|
| 0.5 | `runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k0p5_dx0p5.npz` | `e477100337cebb7f351b2fffa423264b76b25264c1ffb46b13e8cd04da2c98e7` |
| 1.0 | `runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz` | `1923663926ce09eae26bdc10eb94ac4092b9d3af2358f52164356312bef7a8e9` |
| 1.5 | `runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p5_dx0p5.npz` | `1c52852f4820aa09c2f53e456bea6674d0818aaf0d61dbffe223998a793e7c32` |
| 2.0 | `runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz` | `a06c2e8d7f26773c790214630d3eab5f6cd09c5013ac12151ec0992b09160762` |

Verify all four source checksums before use.  Stop if any checksum mismatches.

## 3. Output Directory

Create and use:

```text
runs/phase5/m5_four_frequency_amplification_artifacts/
```

All accepted outputs from this slice must live under this directory.  Temporary
files under `/tmp` are allowed during work, but no accepted artifact may remain
only under `/tmp`.

## 4. Required Generated Artifacts

For each `kM in [0.5, 1.0, 1.5, 2.0]`, generate one amplification NPZ:

```text
t8s_li_fig3_xz_k0p5_dx0p5_amplification.npz
t8s_li_fig3_xz_k1p0_dx0p5_amplification.npz
t8s_li_fig3_xz_k1p5_dx0p5_amplification.npz
t8s_li_fig3_xz_k2p0_dx0p5_amplification.npz
```

For each frequency, generate four read-only 300 DPI plots and sidecars:

```text
F_pol_norm
I_pol_ratio
amplification_plus
amplification_cross
```

Use filenames of this form:

```text
t8s_li_fig3_xz_k{K}_F_pol_norm_300dpi.png
t8s_li_fig3_xz_k{K}_I_pol_ratio_300dpi.png
t8s_li_fig3_xz_k{K}_amplification_plus_300dpi.png
t8s_li_fig3_xz_k{K}_amplification_cross_300dpi.png
```

where `{K}` is exactly one of `0p5`, `1p0`, `1p5`, `2p0`.  Each PNG must have
the usual `.png.json` sidecar.

Also write:

```text
runs/phase5/m5_four_frequency_amplification_artifacts/manifest.md
```

## 5. Metadata Hardening Requirement

For each generated amplification NPZ, metadata must include:

```text
source_lensed_sha256
source_lensed_size_bytes
source_lensed_result_path
source_case_id
case_id
normalization
baseline_api
grid
k
lmax
```

For each plot sidecar, metadata must include:

```text
source_lensed_sha256
source_lensed_size_bytes
source_amplification_sha256
source_amplification_result_path
source_lensed_result_path
quantity
mask_field
valid_count
invalid_count
finite_valid_count
nonfinite_valid_count
normalization
baseline
grid_kind
x_range
z_range
requested_dpi
```

Implementation guidance:

- Prefer the existing public IO functions and CLIs.
- If the current CLI does not embed source SHA in amplification metadata, it is
  acceptable in this artifact slice to run a small local Python enrichment step
  after `compute-amplification`: load the generated
  `AmplificationGridResult`, copy its metadata, add `source_lensed_sha256` and
  `source_lensed_size_bytes`, then save it back with
  `save_amplification_results(...)`.
- If the current plotting sidecar does not include these SHA fields, augment
  the generated sidecar JSON files after plotting.  Record this augmentation in
  `manifest.md` and `status.md`.
- Do not change `src/` unless a clear blocker prevents artifact generation or
  review.  If source changes are necessary, stop first and record the blocker in
  `status.md`.

## 6. Required Work

1. Verify all four source checksums.
2. For each source file, run:

   ```bash
   PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli compute-amplification SOURCE --out OUT
   ```

   Replace `SOURCE` and `OUT` with the exact paths listed above.
3. Apply the metadata hardening requirement to each generated amplification
   NPZ.
4. Plot `F_pol_norm`, `I_pol_ratio`, `amplification_plus`, and
   `amplification_cross` from each generated amplification NPZ using:

   ```bash
   PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-amplification OUT --quantity QUANTITY --out PNG --dpi 300
   ```

5. Apply the plot-sidecar metadata hardening requirement to each sidecar if
   needed.
6. Inspect all generated artifacts.  Record at least:
   - shape;
   - source case id and source path;
   - source SHA-256 and source byte size;
   - amplification NPZ SHA-256 and byte size;
   - `k`, `lmax`;
   - grid kind and x-z ranges;
   - norm/plus/cross valid and invalid mask counts;
   - finite/nonfinite valid counts for all plotted quantities;
   - denominator threshold metadata;
   - baseline API metadata;
   - normalization kind;
   - Q018 warning count and warning codes inherited from the source metadata,
     especially for `kM=2.0`;
   - whether invalid entries remain NaN/masked.
7. Write `manifest.md` with:
   - source artifact table and checksums;
   - generated artifact table and checksums;
   - per-frequency metadata summary;
   - commands run;
   - source-SHA hardening notes;
   - scope and exclusions.

## 7. Hard Limits

- Do not run `schwgw run` or any full solver grid.
- Do not call `run_solver_grid`, `compute_polarization`, or `solve_radial_mode`
  directly from this slice.
- Do not change frozen physics conventions, T6m formulas, T8p schema semantics,
  T8q plotting semantics, Q005/Q014, T4 radial solver behavior, thresholds,
  `lmax`, or accepted M4 artifact metadata.
- Do not generate `kM=4`.
- Do not generate R60_K2/R60_K4 fixtures.
- Do not implement or generate arbitrary incident direction artifacts.
- Do not extend to larger observer domains.
- Do not accept artifacts that exist only under `/tmp`.

## 8. Verification Commands

Run:

```bash
shasum -a 256 runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k0p5_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p5_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli compute-amplification --help
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-amplification --help
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_transmission.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression/test_io_cli.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz || true
find runs/phase5/m5_four_frequency_amplification_artifacts -maxdepth 1 -type f -print | sort
```

Also run a local inspection script using `load_amplification_results(...)`,
NumPy, JSON, `Path.stat()`, and SHA-256 hashing.  The script must not call
solver, radial, partial-wave, baseline, or plotting computation paths.

## 9. Stop Conditions

Stop and update `status.md` if:

- any source checksum mismatches;
- `compute-amplification` tries to run the full solver grid;
- output generation is too slow for the four accepted `121x121` saved results;
- result metadata or sidecars cannot record source SHA-256;
- result metadata lacks source/normalization/baseline/mask fields needed for
  review;
- invalid values are filled instead of remaining NaN/masked;
- tests fail.

## 10. Handoff

If passed, update `status.md` with changed files/generated artifacts, commands
run, test results, open issues, and next action.  Recommend:

```text
T7ae should independently review the four-frequency M5 archived amplification artifacts before T0 opens kM=4, R60_K2/R60_K4, arbitrary incident direction, or larger-domain work.
```
