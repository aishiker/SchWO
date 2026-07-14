# T8am — Fig.5/Fig.6 Review-Grid Diagnostics

You are the existing T8 task. Execute a bounded, fail-closed, read-only
diagnostic plotting slice from the already accepted T8aj exact spin-2
review-grid artifact and the already accepted T8al Kirchhoff scalar baseline.
This task does not authorize a solver run, physics recomputation, dense
production, or paper-style rendering.

## Required Reading And Skills

Read completely before editing:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/superpowers/specs/2026-07-14-t8am-t7bu-review-grid-diagnostics-design.md`
7. `docs/superpowers/plans/2026-07-14-t8am-review-grid-diagnostics.md`
8. this prompt
9. `docs/prompts/phase5_t7bu_fig5_fig6_review_grid_diagnostics_review.md`
10. the existing visualization, CLI, and test files named by the plan

Use `executing-plans`, `test-driven-development`,
`scientific-visualization`, and `verification-before-completion`. Follow the
approved plan task by task. If a skill conflicts with the frozen scientific
or scope contract, the frozen contract wins and you must stop and notify T0.

## Frozen Inputs

The exact spin-2 triplet is:

```text
runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
runs/phase5/fig5_fig6_dense_review_grid/manifest.md
```

Its frozen SHA256 values are:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
```

The Kirchhoff comparison triplet is:

```text
runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz
runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json
runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md
```

Its frozen SHA256 values are:

```text
66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55
0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3
fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632
```

Recompute all six hashes before implementation and again before generation.
Any mismatch is a stop condition. Do not regenerate or repair either source.

## Authorized Scope

Implementation and tests may change only:

```text
src/schwgw/viz/tablei_review_grid.py
src/schwgw/viz/__init__.py
src/schwgw/cli.py
tests/unit/test_viz_tablei_review_grid.py
tests/regression/test_plot_review_grid_cli.py
```

Generated/document changes may be only:

```text
runs/phase5/fig5_fig6_review_grid_plots/
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-14_pre_t8am_review_grid_diagnostics.md
```

Preserve and exclude every pre-existing unrelated worktree change, especially
the T1/T2/T3/T5/T6 handoff files. Do not touch `src/schwgw/viz/results.py`,
solver/scattering/numerics/IO code, configs, regression fixtures, accepted
artifacts, or other handoffs.

## Required Work

Execute every checkbox in
`docs/superpowers/plans/2026-07-14-t8am-review-grid-diagnostics.md`:

- establish the specified TDD RED before implementation;
- implement a fail-closed paired-source loader and deterministic adjacent
  sampling metrics;
- render the two frozen near/far `2x2` figures from saved values only;
- expose the frozen API and CLI;
- generate exactly eight named artifacts;
- inspect both PNGs visually and validate both PDFs;
- run focused tests, Ruff, full pytest, source/output hash checks, scope checks,
  and forbidden-production checks;
- update `status.md` and archive/replace the T8 handoff.

The exact data use markers with only thin adjacent-valid-sample guide
segments. The scalar, polarization-independent Kirchhoff comparison uses
dashed lines and must never enter normalization, masks, solver logic, or
polarization channels. Do not interpolate, smooth, fill, clip, infer missing
values, or connect invalid gaps.

The output directory must contain exactly:

```text
fig5_near_axis_review_grid.png
fig5_near_axis_review_grid.pdf
fig5_near_axis_review_grid.json
fig6_far_axis_review_grid.png
fig6_far_axis_review_grid.pdf
fig6_far_axis_review_grid.json
sampling_diagnostics.json
manifest.md
```

The phase-spacing proxy is diagnostic rather than a theorem or production
authorization:

```text
projected_phase_step_0p1 = 0.1 * max_observed_phase_slope
safety_projected_phase_step_0p1 = 1.5 * projected_phase_step_0p1
phase_proxy_pass = safety_projected_phase_step_0p1 < pi/2
```

Do not invent a magnitude threshold. Record exactly one sampling
recommendation permitted by the design.

## Decisions And Stop Conditions

Record exactly one T8am decision:

```text
GREEN / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS GENERATED
YELLOW / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS PARTIAL
RED / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS BLOCKED
```

Exact GREEN requires all frozen source contracts, exact output cardinality,
provenance/hashes, visual and PDF inspection, deterministic metrics, focused
tests, Ruff, full pytest, forbidden checks, scoped commit, `status.md`, and T8
handoff to pass fresh verification. A code commit must contain exactly the
five authorized implementation/test paths. Generated artifacts and
coordination documents must not be smuggled into that code commit.

Stop without T7 dispatch on any hash, schema, grid, point, mask, dtype,
metadata, visualization, metric, test, Ruff, scope, provenance, cardinality,
or forbidden-output failure. Scientific/test failures do not qualify for a
model switch. A clear model-capacity/system interruption may be recovered in
the same task only under T0's safe-state policy.

## Downstream Dispatch

Only after exact GREEN and fresh completion verification, send this message to
the existing T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed` using
`gpt-5.6-sol`, thinking `high`:

```text
你现在是 T7bu：Fig.5/Fig.6 review-grid diagnostics 与 production-spacing 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bu_fig5_fig6_review_grid_diagnostics_review.md。T8am 只能从已接受 T8aj/T8al artifacts 只读生成诊断图和 sampling metrics；请独立重算 metrics、核验八文件 hashes/provenance、检查 PNG/PDF 可读性与 Kirchhoff scalar 标签、运行 fresh tests，并给 T0 exact decision。不得修改实现或 artifacts，不得启动 40/79-frequency production。
```

Also notify T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` with the exact
decision, code commit, eight output hashes, sampling recommendation, metric
maxima, fresh test results, scope checks, and T7 dispatch status. On YELLOW,
RED, incomplete, or ambiguous status, notify T0 only and do not start T7bu.

T8 must not push GitHub and must not start any production or later scientific
stage.
