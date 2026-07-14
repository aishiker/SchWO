# Phase 5 T7ae Prompt: Four-Frequency M5 Artifact Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ae`。

## 0. 任务定位

T8s 应已从四个被接受的 M4-production saved results 生成四频 M5 pointwise
amplification archive，并把 source SHA-256 写入 generated amplification NPZ
metadata 和 plot sidecars。你的任务是独立复核该四频 archive 是否可以被接受。

This is an artifact-review gate.  Do not generate new production artifacts.

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
10. `runs/phase5/m5_four_frequency_amplification_artifacts/manifest.md`
11. `docs/prompts/phase5_t8s_four_frequency_m5_archived_amplification_artifacts.md`
12. T8s changed/generated files listed in `status.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Review Checklist

Verify:

1. Source artifacts are exactly the four accepted M4-production saved results
   for `kM=[0.5,1.0,1.5,2.0]`.
2. Source SHA-256 checksums match the accepted M4 manifest:
   - `kM=0.5`: `e477100337cebb7f351b2fffa423264b76b25264c1ffb46b13e8cd04da2c98e7`
   - `kM=1.0`: `1923663926ce09eae26bdc10eb94ac4092b9d3af2358f52164356312bef7a8e9`
   - `kM=1.5`: `1c52852f4820aa09c2f53e456bea6674d0818aaf0d61dbffe223998a793e7c32`
   - `kM=2.0`: `a06c2e8d7f26773c790214630d3eab5f6cd09c5013ac12151ec0992b09160762`
3. T8s generated artifacts only under:

   ```text
   runs/phase5/m5_four_frequency_amplification_artifacts/
   ```

4. The artifact directory contains:
   - four amplification NPZ files;
   - sixteen PNG plots;
   - sixteen JSON sidecars;
   - one `manifest.md`.
5. Every amplification NPZ loads as an `AmplificationGridResult` with:
   - shape `(121,121)`;
   - `grid.kind="xz_plane"`;
   - source path, source case, source SHA-256, source byte size;
   - pointwise amplification normalization metadata;
   - baseline API metadata;
   - independent norm/plus/cross masks;
   - NaN/masked invalid entries.
6. `F_plus_complex/F_cross_complex` remain complex ratios with phase
   information and were not replaced by magnitudes.
7. Required plots exist for all four frequencies:
   - `F_pol_norm`;
   - `I_pol_ratio`;
   - `amplification_plus`;
   - `amplification_cross`.
8. Every sidecar records source SHA-256, amplification NPZ SHA-256, source path,
   quantity, mask field, valid/invalid counts, finite/nonfinite valid counts,
   normalization metadata, baseline metadata, grid kind, output path, requested
   DPI, and x-z coordinate ranges.
9. `kM=2.0` source Q018 warning metadata is acknowledged in the manifest and
   remains within the accepted M4-production domain; no larger-domain inference
   is made.
10. No full solver grid, radial solve, partial-wave recomputation, accepted M4
    artifact mutation, `kM=4`, R60_K2/R60_K4, arbitrary incident direction, or
    larger-domain work occurred.

## 3. Verification Commands

Run:

```bash
shasum -a 256 runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k0p5_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p5_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz
find runs/phase5/m5_four_frequency_amplification_artifacts -maxdepth 1 -type f -print | sort
find runs/phase5/m5_four_frequency_amplification_artifacts -mindepth 2 -print
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_transmission.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression/test_io_cli.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz || true
```

Also run an independent local inspection of all four generated amplification
NPZ files and all sixteen sidecar JSON files.  The inspection may use
`load_amplification_results(...)`, NumPy, JSON, `Path.stat()`, and SHA-256
hashing.  It must not call solver, radial, partial-wave, baseline, or plotting
computation paths.

## 4. Pass Conditions

Pass only if:

- all review checklist items pass;
- source and generated checksums are recorded and consistent;
- source SHA-256 appears in every generated amplification NPZ metadata and
  every plot sidecar;
- targeted tests and full pytest pass;
- no convention drift or hidden solver recomputation is found;
- `status.md` records changed files, commands, test results, open issues, and
  next action.

If passed, recommend the next T0 decision as one of:

```text
T7af M5 four-frequency closeout
```

or, if a concrete weakness remains:

```text
T8s-fix metadata/artifact hardening, then rerun T7ae
```

Do not recommend `kM=4`, R60_K2/R60_K4, arbitrary incident direction, or
larger-domain work until the four-frequency archive is either closed or
explicitly rejected.

## 5. Stop Conditions

Stop and update `status.md` if:

- source checksum mismatch;
- generated artifacts are missing or outside the project archive;
- source SHA-256 is absent from generated NPZ metadata or sidecars;
- sidecars or manifest do not identify source/normalization/baseline/mask
  policy;
- invalid entries are finite-filled instead of NaN/masked;
- T8s mutated accepted M4 artifacts;
- T8s ran a full solver grid or opened gated `kM=4`/R60/arbitrary-direction
  scope;
- tests fail.
