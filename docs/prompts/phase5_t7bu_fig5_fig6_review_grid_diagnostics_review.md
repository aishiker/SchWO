# T7bu — Fig.5/Fig.6 Review-Grid Diagnostics Independent Review

You are the existing T7 review task. Independently review T8am's read-only
Fig.5/Fig.6 review-grid diagnostics and its evidence for a possible
`Delta(kM)=0.1` production pilot. You are not a repair thread and do not
authorize or start production.

## Start Gate

Begin only after T8am reports exactly:

```text
GREEN / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS GENERATED
```

If that exact decision, the code commit, the eight artifacts, or the fresh T8
verification record is absent or ambiguous, stop and notify T0. Do not repair
T8am or infer acceptance.

## Required Reading

Read completely:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/superpowers/specs/2026-07-14-t8am-t7bu-review-grid-diagnostics-design.md`
7. `docs/superpowers/plans/2026-07-14-t8am-review-grid-diagnostics.md`
8. `docs/prompts/phase5_t8am_fig5_fig6_review_grid_diagnostics.md`
9. this prompt
10. the five authorized T8am implementation/test paths
11. both accepted source triplets and all eight T8am outputs

Use `receiving-code-review` and `verification-before-completion` as helpful,
but the frozen scientific, scope, and independence rules control.

## Immutable Sources

Independently recompute the accepted source hashes. They must be exactly:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  exact NPZ
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  exact JSON
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  exact manifest
66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55  Kirchhoff NPZ
0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3  Kirchhoff JSON
fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632  Kirchhoff manifest
```

Any mismatch is RED. Do not regenerate a source.

## Allowed Review Writes

You may modify only:

```text
status.md
docs/handoffs/T7_current.md
docs/handoffs/archive/T7_2026-07-14_pre_t7bu_review_grid_diagnostics.md
```

Do not modify implementation, tests, configs, sources, artifacts, plots,
fixtures, T8 handoff, or unrelated handoffs. Preserve and exclude all existing
T1/T2/T3/T5/T6 worktree changes. Do not commit repairs.

## Independent Checks

Perform and record all of these checks rather than relying on T8am's claims:

1. **Commit and scope:** inspect the T8am code commit and require exactly the
   five authorized implementation/test paths. Require no forbidden production,
   solver, IO, config, fixture, accepted-source, or unrelated-handoff diff.
2. **No recomputation:** statically inspect the plotting module and trace the
   CLI path. It must not import or call solver, scattering, radial, Q018,
   numerical-production, `compute_*`, or `solve_*` functionality. It must load
   only the two accepted triplets.
3. **Paired source contract:** independently check schemas, embedded and
   sidecar flags, units/dtypes, exact `kM` and eight-point arrays, shapes,
   masks, finiteness, polarization meaning, and the scalar comparison-only
   Kirchhoff contract.
4. **Sampling metrics:** load the accepted NPZ files directly without calling
   the T8am plotting or metric API. Independently recompute every adjacent
   absolute/relative magnitude and unwrapped-phase step/slope, maxima,
   point/interval attribution, `0.1` projection, `1.5` safety projection, and
   `< pi/2` proxy. Compare exactly or to a justified serialization tolerance.
   Confirm the recorded recommendation follows the frozen logic and is not
   described as proof or production authorization.
5. **Eight-file contract:** require exactly the eight frozen filenames, no
   extras, nonblank PNGs, valid `%PDF-` headers, JSON readability, current
   output hashes, manifest consistency, both source triplets, and every frozen
   no-recompute/no-interpolation/no-smoothing/no-fill/non-production flag.
6. **Visual review:** inspect both PNGs and render/inspect both PDFs. Require
   four readable nonblank panels, correct near/far point membership, distinct
   point encodings, exact-data markers plus adjacent-valid-only thin guides,
   dashed scalar Kirchhoff lines, correct magnitude/phase axes and units,
   legible legends/labels, the diagnostic-only subtitle, and no invalid-gap
   connection. Reject clipping, misleading interpolation, unlabeled scalar
   comparison, or paper-style claims.
7. **Tests:** rerun the focused T8am unit/regression tests fresh and require
   every test to pass.
8. **Static quality and full regression:** run Ruff on all five authorized
   Python paths and run the full project pytest suite fresh. Existing known
   warnings are acceptable only if there is no new T8am-related failure or
   non-finite behavior.
9. **Isolation and non-claims:** require no production outputs, no source
   mutation, no solver rerun, no interpolation/smoothing/fill, no altered
   masks, no `Delta(kM)=0.1` production run, and no automatic later-stage
   dispatch.

The phase proxy is a conservative diagnostic with a stated factor `1.5`; it
is not a band-limit theorem. Magnitude evidence has no frozen automatic
threshold. If the phase proxy passes but visual or magnitude evidence remains
scientifically unresolved, YELLOW is permitted and must name the exact
targeted midpoint or spacing evidence still required.

## Required Fresh Commands

At minimum run:

```bash
shasum -a 256 runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json runs/phase5/fig5_fig6_dense_review_grid/manifest.md runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md
PYTHONPATH=src .venv/bin/python -m pytest -q tests/unit/test_viz_tablei_review_grid.py tests/regression/test_plot_review_grid_cli.py
.venv/bin/python -m ruff check src/schwgw/viz/tablei_review_grid.py src/schwgw/viz/__init__.py src/schwgw/cli.py tests/unit/test_viz_tablei_review_grid.py tests/regression/test_plot_review_grid_cli.py
PYTHONPATH=src .venv/bin/python -m pytest -q
git diff -- src/schwgw/scattering src/schwgw/numerics src/schwgw/io configs tests/regression/fixtures
find runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_kirchhoff_baseline_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
```

The final two commands must have empty output. Also perform an independent
audit script for metrics and artifact hashes, and use local image/PDF
inspection tools; do not substitute T8am's own API for independent metric
recomputation.

## Exact Decision

Record exactly one:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW GRID SUPPORTS DELTA KM 0.1 PRODUCTION PILOT
ACCEPT YELLOW / FIG5-FIG6 REVIEW GRID SAMPLING REMAINS UNRESOLVED
REJECT RED / FIG5-FIG6 REVIEW GRID DIAGNOSTICS INVALID
```

GREEN requires all nine independent checks. It means only that the current
evidence supports T0 designing a separate bounded `Delta(kM)=0.1` production
pilot; it does not authorize that pilot. YELLOW must identify a bounded
missing diagnostic or targeted midpoint set. RED must identify an invalid
source, implementation, artifact, metric, test, visualization, provenance, or
scope condition.

Update `status.md`, archive the prior T7 handoff, and write the new T7 handoff
with exact evidence, hashes, test counts, warnings, scope results, and any
limitations. Notify T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` with the
exact decision and concise evidence.

Do not repair T8am, push GitHub, dispatch another task, or start a 40/79-point
production, midpoint probe, `Delta(kM)=0.05` scan, or paper-style stage.
