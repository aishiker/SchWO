# T8am/T7bu Fig.5/Fig.6 Review-Grid Diagnostics Design

Date: 2026-07-14

Status: user-approved for direct execution after T0 self-review and planning.

## 1. Decision

The next Phase-5 slice is a bounded, read-only diagnostic plotting and sampling
review stage. It uses only the independently accepted T8aj exact spin-2
review-grid artifact and T8al scalar Kirchhoff comparison baseline.

The selected route is preferred over:

1. starting the 40-frequency production scan before inspecting the accepted
   nonuniform review grid; and
2. producing paper-style figures from 18 review frequencies.

The first alternative risks an expensive 40-point run before knowing whether
`Delta(kM)=0.1` is adequate. The second would overstate sparse review data as
production-quality evidence.

## 2. Enabling Evidence

Accepted exact spin-2 review-grid inputs:

```text
NPZ      a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
JSON     2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
manifest 86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
```

Accepted Kirchhoff comparison inputs:

```text
NPZ      66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55
JSON     0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3
manifest fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632
```

Both artifacts contain the same ordered 18-frequency by eight-Table-I-point
grid. T7br accepted the exact grid; T7bt accepted the Kirchhoff metadata and
proved that its 16 non-metadata arrays remain identical to T8ak.

## 3. Objective And Non-Goals

### Objective

Produce two self-contained review-grid diagnostic figures and a deterministic
sampling report that help T0 decide whether the next solver stage should begin
with `Delta(kM)=0.1`, require `0.05`, or first run targeted midpoint probes.

### Non-goals

- No solver, radial, Q018, polarization, flat-baseline, or Kirchhoff
  recomputation.
- No interpolation, resampling, smoothing, fill, clipping, or synthetic dense
  curves.
- No change to formulas, branches, normalization, masks, thresholds, `lmax`,
  boundary policies, or accepted artifacts.
- No 40-frequency or 79-frequency production run.
- No paper-style, benchmark, journal-candidate, Appendix D/E, or final
  reproduction claim.
- No automatic continuation to production after T7bu. Only T0 may authorize
  the next scientific stage.

## 4. Architecture And File Boundary

Create a focused visualization module rather than extending the already large
`src/schwgw/viz/results.py`:

```text
src/schwgw/viz/tablei_review_grid.py
```

Public API:

```python
def plot_tablei_review_grid_diagnostics(
    exact_npz: str | Path,
    kirchhoff_npz: str | Path,
    *,
    output_dir: str | Path,
    dpi: int = 300,
    created_by_cli: bool = False,
) -> dict[str, Path]:
    ...
```

Add one CLI command:

```text
schwgw plot-tablei-review-grid EXACT_NPZ KIRCHHOFF_NPZ --out-dir DIR --dpi 300
```

Required source/test paths:

```text
src/schwgw/viz/tablei_review_grid.py
src/schwgw/viz/__init__.py
src/schwgw/cli.py
tests/unit/test_viz_tablei_review_grid.py
tests/regression/test_plot_review_grid_cli.py
```

Do not modify the accepted compute, IO, solver, scattering, radial, Q018,
config, fixture, or artifact-generation paths.

## 5. Fail-Closed Input Contract

The plotting API must reject the request unless all conditions hold:

- both NPZ files and their `.npz.json` sidecars exist;
- both sibling manifests exist;
- all six current hashes equal the frozen hashes in Section 2;
- exact schema is `phase5_t8aj_fig5_fig6_review_grid_v2`;
- Kirchhoff schema is
  `phase5_t8al_kirchhoff_review_grid_v2_units_dtype`;
- `kM_values`, point IDs, coordinates, radii, angles, and paper
  `xi/xi0` arrays agree exactly between sources;
- the frequency vector is exactly the accepted 18-value review grid;
- all matrix shapes are `(18, 8)` and masks have Boolean dtype;
- exact and Kirchhoff valid masks are honored independently;
- embedded metadata agrees with each sidecar under the source schema's
  documented output-hash exception;
- exact source records `no_interpolation`, `no_smoothing`, `no_fill`,
  `no_plotting`, `no_kirchhoff`, and `no_paper_level_production` as true;
- Kirchhoff records comparison-only, polarization-independent,
  not-denominator, not-mask, not-normalization, no-interpolation,
  no-smoothing, and no-solver-rerun as true.

Any mismatch is an error. The plotting layer must not repair or reinterpret an
accepted artifact.

## 6. Figure Design

Create two logical figures:

```text
Fig.5 diagnostic: near-axis points x/M = 0, 1, 2, 3 at z/M = 30
Fig.6 diagnostic: far-axis points  x/M = 10, 15, 20, 25 at z/M = 30
```

Each is a double-column `7.0 x 5.4` inch, `2 x 2` layout:

```text
(A) |F_plus|                  (B) |F_cross|
(C) unwrapped arg F_plus     (D) unwrapped arg F_cross
```

Rendering rules:

- exact spin-2 data use a colorblind-safe Okabe-Ito point palette;
- point identity is encoded by both color and marker shape;
- exact points may use a thin solid segment between adjacent saved samples as
  a visual guide, explicitly labeled `guide through saved samples`; this is
  not an interpolated output array;
- the scalar Kirchhoff value for the same Table-I point uses the same point
  color with a dashed line and no spin-2 marker;
- legends explicitly say `exact F_plus`, `exact F_cross`, and
  `Kirchhoff scalar comparison`; the scalar curve is never called plus/cross;
- panels use uppercase `(A)`–`(D)` labels, shared frequency axis, consistent
  font/line widths, no top/right spines, and only a light major grid;
- magnitude axes are dimensionless; phase axes use radians;
- title/subtitle states `18-point nonuniform review grid — diagnostic only`;
- PDF is the vector authority; PNG is rendered at 300 DPI for review;
- do not embed paper raster images or claim pixel-level agreement.

The existing four-frequency plotting helper is not modified. T8am uses its
general project style only; it must not inherit the four-frequency-only schema
or no-Kirchhoff assumptions.

## 7. Output Contract

Create exactly eight files under:

```text
runs/phase5/fig5_fig6_review_grid_plots/
```

Files:

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

Each figure sidecar records:

- both source NPZ/JSON/manifest paths, sizes, and SHA256 values;
- both schema versions and case IDs;
- ordered frequency and point lists;
- plotted arrays, mask policy, phase policy, palette, markers, line styles,
  panel layout, DPI, and PDF/PNG hashes;
- explicit flags for read-only, no solver, no recomputation, no interpolation,
  no smoothing, no fill, review-grid-only, not-production, not-paper-style,
  Kirchhoff comparison-only, and polarization-independent Kirchhoff;
- git commit/status information when available.

The manifest lists all seven companion files and their hashes; it does not
hash itself.

## 8. Sampling Diagnostics

The diagnostics are computed only from saved arrays and masks. For each
group, component, point, and adjacent frequency interval, record:

```text
delta_kM
absolute magnitude step
relative magnitude step using max(1, |left|, |right|) as scale
absolute unwrapped-phase step
absolute unwrapped-phase slope = step / delta_kM
valid endpoint pair
```

Also record group/component maxima and their exact intervals/point IDs.

Define a conservative phase-sampling proxy for candidate spacing `0.1`:

```text
projected_phase_step_0p1 = 0.1 * max_observed_phase_slope
safety_projected_phase_step_0p1 = 1.5 * projected_phase_step_0p1
phase_proxy_pass = safety_projected_phase_step_0p1 < pi/2
```

The factor `1.5` is a stated diagnostic safety factor, not a theorem. It does
not prove band limitation or guarantee that no unobserved extremum lies
between review points.

Current T0 pre-design evidence, which T8am must recompute rather than trust:

```text
near plus  max slope ~= 2.7962 rad/(kM); safety-projected 0.1 step ~= 0.4194 rad
near cross max slope ~= 3.6257 rad/(kM); safety-projected 0.1 step ~= 0.5439 rad
far plus   max slope ~= 8.7630 rad/(kM); safety-projected 0.1 step ~= 1.3145 rad
far cross  max slope ~= 7.5544 rad/(kM); safety-projected 0.1 step ~= 1.1332 rad
```

All are below `pi/2`, but the far-axis margin is materially smaller. T8am may
report `DELTA_0P1_PHASE_PROXY_PASS` only if its fresh recomputation matches.
It must not convert that proxy into production authorization.

Magnitude steps and visual sparsity remain review evidence rather than an
automatic pass/fail threshold. T8am records one recommendation:

```text
DELTA_0P1_PROVISIONAL_REVIEW
DELTA_0P05_OR_TARGETED_MIDPOINT_REVIEW
SAMPLING_RECOMMENDATION_BLOCKED
```

The first label requires all phase proxies to pass, finite/masked data to be
consistent, and no detected provenance/shape failure. T7bu independently
reviews the figures and metrics before T0 decides on production.

## 9. Tests And Verification

Use TDD for the new API and CLI. Tests must cover:

- successful synthetic exact/Kirchhoff paired loading;
- failure on missing sidecar/manifest or wrong source hash;
- failure on grid, point, schema, shape, dtype, mask, or metadata mismatch;
- exact eight-file output cardinality and names;
- nonblank PNGs, valid PDF headers, and JSON/manifest output hashes;
- preservation of invalid masks without fill or line connection across invalid
  endpoints;
- correct deterministic sampling metrics and recommendation labels;
- CLI success and fail-closed error path;
- static absence of solver/scattering/radial/Q018/compute imports in the new
  visualization module.

Run focused unit/regression tests, Ruff on changed Python paths, full pytest,
source hash checks, output cardinality/hash checks, and forbidden-output/scope
checks. Do not add pixel-perfect image fixtures.

## 10. T8am To T7bu State Machine

T8am exact labels:

```text
GREEN / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS GENERATED
YELLOW / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS PARTIAL
RED / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS BLOCKED
```

Only exact GREEN after code/tests/artifacts/status/T8 handoff fresh
verification may dispatch T7bu to the existing T7 task with 5.6 Sol High.

T7bu is an independent sampling/provenance review, not a plot-polish review.
Its exact labels are:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW GRID SUPPORTS DELTA KM 0.1 PRODUCTION PILOT
ACCEPT YELLOW / FIG5-FIG6 REVIEW GRID SAMPLING REMAINS UNRESOLVED
REJECT RED / FIG5-FIG6 REVIEW GRID DIAGNOSTICS INVALID
```

T7bu independently recomputes sampling metrics, validates all source/output
hashes, inspects PNG/PDF legibility and nonblank output, confirms the scalar
Kirchhoff labeling, reruns focused/Ruff/full pytest, and checks forbidden
scope. It does not repair T8am and starts no production task.

T0 alone interprets T7bu and may later design a 40-frequency pilot, targeted
midpoint probes, or a `Delta(kM)=0.05` plan.

## 11. Stop Conditions

Stop without downstream dispatch if:

- either accepted source hash changes;
- schemas, grids, points, masks, or metadata fail the paired contract;
- any output is blank, malformed, mislabeled, or missing provenance;
- the new module imports or calls solver/scattering/radial/Q018/compute code;
- a plotting path interpolates, smooths, fills, clips, or recomputes physics;
- sampling metrics cannot be reproduced deterministically;
- focused, Ruff, full pytest, scope, or forbidden-output checks fail.

Model-capacity/system interruption may use the existing same-task Terra
recovery policy only after safe-state inspection. Scientific, test, scope,
provenance, or visualization failures do not qualify.

## 12. GitHub And Existing Worktree

T8 and T7 never push. If T7bu returns exact GREEN, T0 decides whether the
sampling gate is a major node and performs any required scope-explicit,
non-force private-GitHub synchronization only after fresh local verification.

The unrelated local T1/T2/T3/T5/T6 handoff changes predate this design and
must remain untouched and excluded from all scoped commits.
