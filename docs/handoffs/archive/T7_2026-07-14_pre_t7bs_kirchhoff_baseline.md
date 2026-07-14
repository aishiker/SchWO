# T7 Current Handoff

Last updated: 2026-07-14

Thread: T7br, Fig.5/Fig.6 conservative review-grid data independent review.

## Thread Role And Current Status

T7br completed an independent read-only review of the T8aj conservative
Fig.5/Fig.6 Table-I review-grid data artifact.

Decision recorded exactly:

```text
ACCEPT GREEN / FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA ACCEPTED
```

This acceptance is limited to the exact 18-frequency by eight-point review
grid. It permits T0 to consider scheduling a separate bounded Kirchhoff
Eq. (47) scalar comparison-baseline slice for the same grid. It does not
authorize review-grid plots, a 40-frequency production scan, fixtures, or
paper-style candidates.

The previous T7bq handoff was archived at:

```text
docs/handoffs/archive/T7_2026-07-14_pre_t7br_review_grid_data.md
```

## Review Answers

1. T8aj generated the required NPZ/JSON/manifest artifact set. The directory
   also retains the required T12b error record and a documented resolved
   T8aj cache-domain diagnostic. No downstream Kirchhoff, plot, dense-scan,
   fixture, or paper-style artifact was found.

2. `kM_values` exactly equals:
   `[0.1,0.2,0.3,0.5,0.75,1.0,1.25,1.5,1.75,2.0,2.25,2.5,2.75,3.0,3.25,3.5,3.75,4.0]`.

3. The eight points exactly match `src/schwgw/io/tablei.py`:
   `z=30`, `x=[0,1,2,3,10,15,20,25]`, with matching point IDs, radii,
   angles, and azimuths.

4. `F_plus_complex` and `F_cross_complex` both have shape `(18,8)`. All
   values selected by their masks are finite. Saved magnitudes and principal
   and unwrapped phases reproduce direct NumPy derivations.

5. Plus, cross, and norm masks are separate Boolean `(18,8)` arrays. All are
   true for this artifact. Finiteness matches the plus/cross masks exactly,
   consistent with the frozen independent-mask/NaN-on-invalid denominator
   policy.

6. All 18 final adjacent pairs pass. The maximum saved final-pair deltas are
   `5.3077050459232115e-15` for plus and
   `4.70627521105483e-14` for cross, below `1e-4`.

7. The sidecar has exactly 18 frequency records. Each records the planned
   `lmax_values`, last adjacent pair, component maxima, pass flag, warning
   summary, cache counts, and runtime. Every saved list matches the prompt's
   seed/anchor policy and the NPZ arrays.

8. Radial metadata contains `3506` structured warnings:
   `2 transition_raw_wronskian_warning`,
   `1886 evanescent_tail_suppressed`, and
   `1618 q018_tablei_review_grid_transition_oracle_used`. The 1618 unique
   `(k, point_id, ell, sector)` Q018 records exactly equal both the T4y
   measured transition set and oracle-validation set. Q018 adapter use is
   restricted to `kM={2.5,2.75,3.0,3.25,3.5,3.75,4.0}` and the reviewed
   Table-I envelope.

9. Metadata records `no_kirchhoff=true`; the baseline API is
   `compute_flat_no_lens_polarization`, normalization is pointwise
   wave-optics amplification, and the Route B polarization bridge is used.
   No Kirchhoff output or downstream artifact was found.

10. Source hashes all match current files. Git reports no changes under
    `src/`, `tests/`, or `configs/`. Fourier, Route B, thresholds, `lmax`,
    boundary, Q018, and adapter-envelope policies are unchanged.

## Completed Work

- Read and followed
  `docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md`.
- Read all prompt-required project, handoff, T8aj, radial-gate, and artifact
  inputs.
- Loaded the NPZ with `allow_pickle=False` and parsed both embedded and
  external JSON metadata; they are identical.
- Recomputed artifact, preserved-error, config, and source hashes.
- Compared Q018 warning membership against T4y classification and oracle
  validation metadata as exact sets.
- Checked mask, finiteness, magnitude, phase, convergence, `lmax`, and warning
  consistency.
- Checked forbidden downstream directories and T8aj source/test/config scope.
- Updated `status.md` and this handoff without mutating the T8aj artifacts.

## Artifact Hashes Rechecked

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  runs/phase5/fig5_fig6_dense_review_grid/manifest.md
15802fbf5e4a6a579ec42551d7a6f8db29bafe933ae5e292b7413a07fd911e54  runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json
56eb140c45ceea850e065ff6a1f0cf1a79ee9d4beda9055da659c22919ab6ddb  runs/phase5/fig5_fig6_dense_review_grid/t8aj_run_error_20260714T045939Z.json
```

## Checks Run

Fresh prompt-required artifact assertions passed with the project interpreter:

```text
PROMPT_REQUIRED_ARTIFACT_CHECK=PASS
```

The comprehensive independent metadata/set audit returned:

```text
COMPREHENSIVE_ARTIFACT_AUDIT=PASS
grid_shape=18x8
all_masks_true True True True
max_final_delta_plus 5.3077050459232115e-15
max_final_delta_cross 4.70627521105483e-14
warning_code_counts {'transition_raw_wronskian_warning': 2, 'evanescent_tail_suppressed': 1886, 'q018_tablei_review_grid_transition_oracle_used': 1618}
q018_unique_set 1618 exactly_matches_T4y_transition_and_oracle_sets
all_source_hashes_match=True
```

Additional checks:

```text
FORBIDDEN_DOWNSTREAM_ARTIFACT_CHECK=PASS (0 files)
T8AJ_SOURCE_TEST_CONFIG_CHANGE_CHECK=PASS (0 changes)
```

Full pytest was not rerun because T8aj changed no source, tests, or configs.
The prompt explicitly permits targeted metadata checks for an artifact-only
slice; the comprehensive audit directly exercised the acceptance contract.

## Incomplete Work

- T0 has not yet independently inspected this T7br decision or scheduled the
  next bounded stage.
- No Kirchhoff comparison baseline or review-grid plot exists.
- No 40-frequency production, fixture, or paper-style artifact is authorized.

## Blocking Issues And Non-Blocking Warnings

- No blocker remains for T0 to inspect this review and decide whether to open
  the separate Kirchhoff-baseline gate.
- Q018 warning records retain the implementation identifier
  `production_integration_review_id="T4y/T7bq-pending"`, which is frozen in
  the reviewed source/tests. It is not used as the current gate decision;
  the sidecar enabling gate, exact set equality, status timeline, and archived
  T7bq decision independently establish acceptance. Do not edit the accepted
  artifact solely to relabel this legacy identifier.

## Files The Next Thread Must Read

1. `status.md`
2. `docs/handoffs/T7_current.md`
3. `docs/handoffs/T8_current.md`
4. `runs/phase5/fig5_fig6_dense_review_grid/manifest.md`
5. `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json`
6. `docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md`
7. `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
8. `references/notes/kirchhoff_eq47_conventions.md`
9. `docs/physics_spec.md`
10. `docs/equation_map.md`

## Frozen Decisions

- Fourier convention remains `exp(-i k t)`.
- Route B packaged polarization remains the production path.
- Pointwise amplification uses the flat/no-lens Route-B-compatible
  polarization field as denominator.
- Kirchhoff Eq. (47) is a separate scalar comparison baseline only.
- Plus/cross denominator masks remain independent and invalid ratios remain
  NaN.
- Q018 `required_eval_radius` remains fail-closed.
- Existing thresholds, `lmax` policy, boundary policy, and the exact
  `q018_tablei_review_grid_transition` envelope remain unchanged.

## Forbidden Actions

- Do not mutate the accepted T8aj NPZ/JSON/manifest.
- Do not rerun the T8aj solver merely for review or recovery.
- Do not generate Kirchhoff data or plots from T7.
- Do not start a 40-frequency scan, fixtures, Appendix D/E, or paper-style
  candidates.
- Do not broaden Q018 adapter envelopes, lower `lmax`, relax thresholds, skip
  modes/points, or change frozen conventions.
- Do not treat this GREEN as authorization for downstream work beyond a new
  T0-issued bounded prompt.

## Superseded Prompts

- `docs/prompts/phase5_t7bq_fig5_fig6_review_grid_radial_gate_review.md` is a
  completed historical gate and is not the next task.
- `docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md` is complete and
  must not be rerun for reconciliation.
- Historical T12/T12b autonomous prompts that include later production stages
  remain superseded.

## Exact Next Task

Return to T0. T0 must independently inspect the synchronized T8aj artifacts,
this exact T7br GREEN decision, and fresh-check evidence. If T0 agrees, it may
issue a new prompt for a separate bounded T8 Kirchhoff Eq. (47) scalar
comparison-baseline artifact on the same 18-by-8 review grid, followed by a
separate T7 review. T7br itself does not start that task.

## Allowed Files, Verification Commands, And Definition Of Done

For this completed T7br slice, the only writable files were:

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-14_pre_t7br_review_grid_data.md`

The T8aj NPZ/JSON/manifest and all source/test/config files were read-only.

Definition of done is satisfied when the exact GREEN decision is recorded,
all 10 review questions are answered from fresh evidence, the artifact and
forbidden-output checks pass, accepted artifacts remain byte-identical, and
status plus T7 handoff are updated.
