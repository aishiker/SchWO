# Phase 5 T7af Prompt: M5 Four-Frequency Closeout

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7af`。

## 0. 任务定位

T8s 已生成四频 M5 pointwise amplification archive，T7ae 已独立复核通过。
你的任务是正式 close out 这批四频 M5 artifacts：冻结 manifest、适用范围、
provenance、验证结论、限制和剩余 gates，防止后续线程把它误当成 `kM=4`、R60、
arbitrary incident direction、larger-domain 或 scalar/Kirchhoff baseline 验证。

This is a documentation/status closeout slice.  Do not generate new numerical
artifacts, do not modify `src/`, and do not change physics conventions.

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
12. `docs/prompts/phase5_t7ae_four_frequency_m5_artifact_review.md`
13. T8s/T7ae records in `status.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Required Output

Create:

```text
docs/phase5_m5_four_frequency_closeout.md
```

Update:

```text
status.md
```

Do not modify `src/`, tests, configs, or existing artifact files unless a
blocking inconsistency is found.  If a blocking inconsistency is found, stop and
record it in `status.md`.

## 3. Closeout Document Requirements

`docs/phase5_m5_four_frequency_closeout.md` must include:

1. Status and date.
2. Accepted scope:
   - M5 pointwise wave-optics amplification, not radial horizon transmission or
     absorption.
   - `kM=[0.5,1.0,1.5,2.0]`.
   - `x/M,z/M in [-30,30]`.
   - `dx=dz=0.5M`, shape `(121,121)`.
   - default `+z` incident direction.
   - source M4 artifacts from
     `runs/phase4/m4_production_first_pass/`.
   - archive directory
     `runs/phase5/m5_four_frequency_amplification_artifacts/`.
3. Artifact manifest summary:
   - four amplification NPZ files;
   - sixteen PNG plots;
   - sixteen JSON sidecars;
   - one `manifest.md`;
   - generated checksums are recorded in the T8s manifest.
4. Provenance summary:
   - source M4 SHA-256 checksums;
   - generated amplification SHA-256 checksums;
   - source SHA embedded in every generated amplification NPZ metadata and
     every plot sidecar.
5. Physics and convention summary:
   - Q005 production quantity is pointwise wave-optics amplification
     `h_lensed/h_unlensed`;
   - denominator masks are independent;
   - invalid ratios remain NaN/masked;
   - Route B packaged-polarization bridge remains active;
   - no Q014/Q005 convention change occurred.
6. Verification summary:
   - T7ae independently checked checksums, schema, masks, NaN policy, complex
     ratio phases, sidecars, read-only viz boundary, and full pytest.
   - `src/schwgw/viz` remains free of solver/scattering imports.
   - No full solver grid was run for M5 artifact generation.
7. Q018 / radial limitation:
   - `kM=2.0` carries the accepted same-domain Q018
     `evanescent_tail_suppressed` metadata inherited from M4 production.
   - This closeout is valid only for the accepted `[-30,30]^2` domain; larger
     domains must re-check `valid_until_r`.
8. Explicit non-scope:
   - `kM=4`;
   - R60_K2/R60_K4 fixtures;
   - arbitrary incident direction;
   - larger domains;
   - scalar/Kirchhoff baselines;
   - radial horizon transmission/absorption;
   - `A_in/A_out`, phase shifts, horizon flux, or asymptotic scattering
     observables as M5 production outputs;
   - pixel-for-pixel reference-paper reproduction.
9. Next-decision menu for T0:
   - `kM=4` stress;
   - R60_K2/R60_K4 regression fixtures;
   - arbitrary incident direction / Wigner-D rotation integration;
   - scalar/Kirchhoff baseline comparisons;
   - larger-domain Q018 re-check;
   - or M5 closeout-to-paper plotting/reporting.

## 4. Required Verification

Run:

```bash
shasum -a 256 runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k0p5_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p5_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz
find runs/phase5/m5_four_frequency_amplification_artifacts -maxdepth 1 -type f -print | sort
find runs/phase5/m5_four_frequency_amplification_artifacts -mindepth 2 -print
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz || true
```

Also inspect:

```text
runs/phase5/m5_four_frequency_amplification_artifacts/manifest.md
status.md
```

Do not run `schwgw run`.  Do not create new artifacts.

## 5. Status Update Requirements

Update `status.md` with:

- changed files;
- files read;
- commands run and results;
- closeout decision;
- open issues;
- next action.

If the closeout passes, mark the current Phase 5 four-frequency M5 archive as
closed/accepted and keep these gates explicitly open:

```text
kM=4
R60_K2/R60_K4
arbitrary incident direction
larger-domain Q018 re-check
scalar/Kirchhoff baseline comparisons
radial horizon transmission/absorption diagnostics
```

## 6. Stop Conditions

Stop and update `status.md` if:

- the four-frequency archive manifest is missing or inconsistent;
- expected source checksums do not match;
- generated artifact count or layout is inconsistent with T7ae;
- source SHA-256 is not embedded in generated NPZ metadata or sidecars;
- the closeout would require modifying `src/`, tests, configs, or existing
  artifacts;
- full pytest fails;
- any convention drift is found.

## 7. Handoff

If passed, recommend that T0 choose the next scientific slice from the
next-decision menu.  Do not provide implementation prompts for those future
slices inside T7af unless the user explicitly asks for them.
