# T8 Current Handoff

Last updated: 2026-07-14

## Thread Role And Current Status

T8aj generated and freshly verified the Fig.5/Fig.6 conservative Table-I
review-grid data artifact after the T7bq radial-gate acceptance.

Decision:

```text
GREEN / FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA GENERATED
```

This is a data-only review grid, not a Kirchhoff comparison, plot package,
40-frequency production scan, fixture, or paper-style result. T7br independent
data review is still required.

## Completed Work

- Read and followed
  `docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md`.
- Generated the exact 18-frequency, eight-point Table-I artifact set:
  - `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz`
  - `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json`
  - `runs/phase5/fig5_fig6_dense_review_grid/manifest.md`
- Grid: `kM=[0.1,0.2,0.3,0.5,0.75,1.0,1.25,1.5,1.75,2.0,2.25,2.5,2.75,3.0,3.25,3.5,3.75,4.0]`;
  Table-I `x/M=[0,1,2,3,10,15,20,25]`, `z/M=30`.
- All 18 frequencies have final adjacent-pair complex plus/cross convergence
  below `1e-4`; all final plus/cross/norm masks are true and saved arrays are
  finite.
- Q018 use is bounded to the reviewed high-frequency set
  `{2.5,2.75,3.0,3.25,3.5,3.75,4.0}` and exact Table-I radii. Adapter-use
  count is `1618`; there is no lower-frequency use.
- Preserved `stage1_yellow_error.json` without changes.
- A foreground model-capacity interruption occurred after the background run
  had started. The process completed naturally; recovery only performed
  fresh read-only verification and did not rerun the solver or restart at
  `kM=2.75`.

## Artifact Hashes

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  runs/phase5/fig5_fig6_dense_review_grid/manifest.md
15802fbf5e4a6a579ec42551d7a6f8db29bafe933ae5e292b7413a07fd911e54  runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json
56eb140c45ceea850e065ff6a1f0cf1a79ee9d4beda9055da659c22919ab6ddb  runs/phase5/fig5_fig6_dense_review_grid/t8aj_run_error_20260714T045939Z.json
```

The retained T8aj error JSON records the resolved cache-domain runner issue;
do not delete it and do not treat it as a remaining radial/physics failure.

## Incomplete Work

- T7br has not independently reviewed the data artifact.
- No Kirchhoff baseline, review-grid plot, 40-frequency production-like scan,
  fixture, or paper-style candidate is authorized from this handoff.

## Blocking Issues And Non-Blocking Warnings

- No T8aj data-generation blocker remains.
- T7br independent review is the next gate.
- Standard radial diagnostic warnings are recorded in the sidecar; all final
  masks, finite checks, convergence checks, and accepted Q018-envelope checks
  passed.

## Files The Next Thread Must Read

1. `status.md`
2. `docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md`
3. `docs/handoffs/T8_current.md`
4. `docs/handoffs/T7_current.md`
5. `runs/phase5/fig5_fig6_dense_review_grid/manifest.md`
6. `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json`
7. `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz`
8. `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
9. `runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json`
10. `runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json`

## Frozen Decisions

- Fourier, harmonic, tetrad, RW/Zerilli, Route B, boundary, `lmax`, and Q018
  conventions remain frozen.
- The flat/no-lens Route-B-compatible polarization is the amplification
  denominator. Kirchhoff is not a denominator, correction, mask, or
  normalization.
- `q018_tablei_review_grid_transition` remains opt-in and limited to the
  exact T4y/T7bq reviewed high-frequency/Table-I-radius envelope.
- No interpolation, smoothing, fill, or skipped invalid points are permitted.

## Forbidden Actions

- Do not rerun the T8aj solver merely for review or recovery.
- Do not modify `src/`, `tests/`, `configs/`, physics conventions, thresholds,
  `lmax`, boundary policy, or Q018 envelope in the T7br review slice.
- Do not generate Kirchhoff artifacts, plots, 40-frequency production,
  fixtures, Appendix D/E curves, or paper-style candidates.
- Do not overwrite or delete `stage1_yellow_error.json` or the retained T8aj
  cache-domain diagnostic.

## Superseded Prompts

- Historical T12/T12b pipeline prompts that include later Kirchhoff, plotting,
  and production stages are superseded for the immediate next step.
- Do not reuse the pre-T4y T8 continuation boundary; the reviewed T7bq gate
  and this completed T8aj data artifact supersede it.

## Exact Next Task

```text
你现在是 T7br：Fig.5/Fig.6 conservative review-grid data independent review 线程。请读取并严格执行 docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md。
```

## Allowed Files, Verification Commands, And Definition Of Done

- T7br may read the artifact set and write only its own review/status/handoff
  records as authorized by its prompt. It must not mutate the T8aj NPZ/JSON or
  manifest.
- Fresh T8aj verification completed:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 - <<'PY'
# load NPZ/JSON; assert (18,8), exact grid/points, finite arrays, all masks,
# 18 passing final pairs, reviewed-envelope-only Q018 use, and preserved SHA
PY

find runs/phase5/fig5_fig6_kirchhoff_baseline runs/phase5/fig5_fig6_review_grid_plots runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
```

- Definition of done for T8aj: the three artifacts exist with the hashes
  above; metadata proves all 18 final-pair/mask/finite checks and bounded Q018
  use; old stage1 error is unchanged; forbidden-output search is empty; and
  status/T8 handoff are updated. All conditions are met.
