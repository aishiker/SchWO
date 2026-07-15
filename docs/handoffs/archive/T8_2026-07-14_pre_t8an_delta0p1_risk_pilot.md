# T8 Current Handoff

Last updated: 2026-07-14

## Thread Role And Current Status

T8am completed the bounded, read-only Fig.5/Fig.6 review-grid diagnostics
slice from the accepted T8aj exact 18×8 artifact and accepted T8al Kirchhoff
scalar comparison baseline.

Exact decision:

```text
GREEN / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS GENERATED
```

The predecessor T8al handoff is archived at
`docs/handoffs/archive/T8_2026-07-14_pre_t8am_review_grid_diagnostics.md`.

## Completed Work

- Executed the frozen T8am plan, with loader/metrics/rendering/CLI/tests
  restricted to the five authorized code/test paths.
- Generated exactly eight artifacts under
  `runs/phase5/fig5_fig6_review_grid_plots/` from saved values only.
- Recovered after the UI-reported `Selected model is at capacity` interruption
  without rerunning a solver, recomputing physics, restarting TDD, or changing
  any source triplet.
- Retained `f6d32b1 feat: add Fig5 Fig6 review-grid diagnostics`; follow-up
  commit `1542f5e fix: reserve review-grid diagnostic layout margins` makes the
  minimal authorized constrained-layout repair. Together they touch exactly:
  `src/schwgw/viz/tablei_review_grid.py`, `src/schwgw/viz/__init__.py`,
  `src/schwgw/cli.py`, `tests/unit/test_viz_tablei_review_grid.py`, and
  `tests/regression/test_plot_review_grid_cli.py`.

## Artifacts And Hashes

```text
f8ffcee55ce2a4d07e9a2ff91320baa0122bd37f43701cfde8d5eab5e963c386  fig5_near_axis_review_grid.png
e19c28ca4a6532adc079f99137853115b9f90e0764bed84957d133d3b9167c11  fig5_near_axis_review_grid.pdf
627903f91de69edf3d4e527419511a6a898979e8ae8c6dd57e6cee70ee93cb98  fig5_near_axis_review_grid.json
e949bd7436617bf8cadb59515a3861e8bc8503e17337347a81be7598ef061855  fig6_far_axis_review_grid.png
02b05bbe092f0c5934bcc389ca16d305208202637182c88038eeb5ff511a77ec  fig6_far_axis_review_grid.pdf
06142d333dabba5dd17f76642a4a792dfa6603beee6a73ce8cc712c07073f534  fig6_far_axis_review_grid.json
cb40d6cae967699b86f0ef3d863e8cbe9ce2555f56dcd3427f8f5d64d44190a4  sampling_diagnostics.json
f09c24abb30c1ec64abcd3cd9dd2679061dfa23d746c2c96c49ffdd4e04c327b  manifest.md
```

All six accepted source hashes were freshly rechecked and match their frozen
values. The output directory contains no ninth file.

## Diagnostic Result

- Exact recommendation: `DELTA_0P1_PROVISIONAL_REVIEW`.
- All four diagnostic phase proxies pass; this is not a production approval.
- Maximum observed unwrapped-phase slopes:
  - near `F_plus`: 2.796164802757737 at `near_axis_x1_z30`, [3.75, 4.0];
  - near `F_cross`: 3.625714958231235 at `near_axis_x2_z30`, [2.75, 3.0];
  - far `F_plus`: 8.763007426859136 at `far_axis_x20_z30`, [0.3, 0.5];
  - far `F_cross`: 7.5544095996424385 at `far_axis_x10_z30`, [1.5, 1.75].

## Tests And Verification

- Focused tests: `10 passed in 1.69s`.
- Ruff: `All checks passed!`.
- Full pytest: `568 passed, 117 skipped, 1 xfailed, 85 warnings, 79 subtests
  passed in 288.83s`.
- Independent source/output/cardinality/provenance/hash audit: PASS.
- Independent adjacent-metric recomputation: PASS.
- Both regenerated PNGs and both rendered one-page PDFs were individually
  inspected. The far-axis frozen subtitle and bottom point caption/legend are
  fully inside the frame, with no overlap.
- The retained warnings are the existing Weyl/Wigner/radial warnings; no
  diagnostics-path warning was introduced.

## Frozen Decisions

- Exact spin-2 values use markers and thin adjacent-valid-sample guides only.
- Kirchhoff is scalar, polarization-independent, dashed comparison-only data;
  it never enters masks, normalization, solver logic, or polarization channels.
- No interpolation, smoothing, fill, clipping, inference, solver rerun,
  physics recomputation, 40/79-frequency production, fixture, or paper-style
  claim is authorized by this diagnostic result.

## Downstream And Exact Next Task

T7bu was dispatched to the existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` using `gpt-5.6-sol`, thinking `high`.
It must execute
`docs/prompts/phase5_t7bu_fig5_fig6_review_grid_diagnostics_review.md`,
perform an independent read-only review, report one exact decision to T0, and
must not modify artifacts or begin production.

T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` receives this GREEN, the
two commits, eight hashes, maxima, recommendation, and verification evidence.

## Allowed/Forbidden Files And Definition Of Done

- T8am implementation is complete. Its code commit range is frozen to the
  five paths named above; generated files live only in the eight-file output
  directory; coordination changes are limited to `status.md`, this handoff,
  and the archived predecessor handoff.
- T7bu is review-only. Any visualization, provenance, metric, test, scope, or
  scientific failure must return to T0 as YELLOW/RED and must not be bypassed
  by changing models or starting a later stage.
