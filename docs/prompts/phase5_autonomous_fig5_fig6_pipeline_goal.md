# Phase 5 Autonomous Prompt: Fig.5/Fig.6 Gated Pipeline To Journal-Candidate Artifacts

You are the Fig.5/Fig.6 autonomous gated pipeline thread.

Use Goal mode.

Goal objective:

```text
Starting from the T7bo GREEN decision, advance the Fig.5/Fig.6 pipeline as far as safely possible toward journal-candidate Fig.5 and Fig.6 artifacts. Continue automatically only when each stage's self-checks pass. If a stage fails, diagnose and attempt at most two focused repair iterations inside the same stage. Stop rather than bypassing physics, radial/Q018, convention, provenance, threshold, or validation gates.
```

## Role Boundary

You are a combined execution/coordinator thread, not a replacement for final
independent review.  You may self-check and continue through low-risk gates
when the checks below pass, but the final artifacts must be labeled
`journal-candidate pending independent review`, not final journal-grade
acceptance.

Do not claim pixel-level reproduction or final paper acceptance.

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T0_current.md`
6. `docs/handoffs/T4_current.md`
7. `docs/handoffs/T7_current.md`
8. `docs/handoffs/T8_current.md`
9. `docs/handoffs/T10_current.md`
10. `docs/physics_spec.md`
11. `docs/equation_map.md`
12. `docs/numerics.md`
13. `docs/validation_plan.md`
14. `docs/phase5_km4_tablei_radial_q018_preflight.md`
15. `docs/phase5_km4_tablei_transition_oracle_probe.md`
16. `runs/phase5/km4_tablei_radial_q018_preflight/radial_q018_preflight_metadata.json`
17. `runs/phase5/km4_tablei_transition_oracle_probe/transition_oracle_probe_metadata.json`
18. `references/manifest.md`
19. `references/notes/kirchhoff_eq47_conventions.md`
20. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
21. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
22. `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
23. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
24. `src/schwgw/numerics/radial_solver.py`
25. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
26. `src/schwgw/io/results.py`
27. `src/schwgw/io/tablei.py`
28. `src/schwgw/scattering/transmission.py`
29. `src/schwgw/viz/results.py`
30. relevant tests under `tests/physics/`, `tests/unit/`, and `tests/regression/`.

Before starting each stage, check installed plugins/skills.  Use
`systematic-debugging` for failures, `test-driven-development` for code changes,
`scientific-visualization` for final plotting, and
`verification-before-completion` before every stage-complete claim.

## Global Hard Rules

- Update `status.md` and the relevant handoff after every stage.
- Do not lower `lmax`, relax thresholds, weaken convergence criteria, or hide
  failed modes.
- Do not change frozen Fourier, harmonic, tetrad, RW/Zerilli, Route B,
  Q014/Q015/Q018, or Kirchhoff branch conventions.
- Do not use Kirchhoff Eq. (47) as denominator, mask, correction, or production
  normalization.  It is a scalar comparison baseline only.
- Do not use interpolation or smoothing to fake dense `Mk` curves.
- Do not produce paper-style Fig.5/Fig.6 plots from sparse four-frequency data.
- If any source/test/config/runs artifact is modified, record it in `status.md`.
- If a command runs longer than 2 hours without progress, stop that stage and
  record a YELLOW runtime blocker.
- If you hit three consecutive failures with the same blocker, stop and report
  the blocker rather than trying a fourth repair.

## Stage 1: T4x kM=4 Table-I Production Adapter

### Goal

Convert the T4w experimental evidence into a narrowly reviewed production
adapter path for the exact `kM=4` Table-I review-grid radial/Q018 envelope.

### Required Design

Do not directly reuse the old R60_K2 envelope.  Implement a separate named
internal envelope for this scope, for example:

```text
q018_tablei_km4_transition
```

Required envelope:

```text
background = Schwarzschild M=1
k = 4.0
required_eval_radius = 39.051248
r_out = 300.0
r_in_eps = 1e-6
rtol = 1e-10
atol = 1e-12
sector = odd/even
```

Before implementing the adapter, measure the continuous default fail-closed
set for `ell=2..360`, odd/even, using:

```text
BoundaryConfig(required_eval_radius=39.051248, r_out=300,
               r_in_eps=1e-6, rtol=1e-10, atol=1e-12)
```

Classify every mode as:

- default-covered;
- default fail-closed with `evanescent_tail_required_radius_uncovered`;
- default error other than uncovered;
- already `evanescent_tail_suppressed` and radius-covered.

For every default fail-closed mode required by `lmax=360`, validate the direct
experimental oracle at `k=4`, `required_radius=39.051248`.  The adapter envelope
may include only modes with direct finite oracle evidence.

### Stage 1 Stop Conditions

Stop YELLOW if:

- any default fail-closed mode cannot be certified by direct oracle;
- any non-uncovered default error appears;
- continuous validation is too slow to finish;
- adapter implementation requires broad radial architecture changes.

Stop RED if:

- default no-oracle behavior changes;
- out-of-envelope opt-in passes silently;
- thresholds, `lmax`, conventions, or Q018 fail-closed policy are weakened;
- the adapter routes ordinary covered modes through the oracle unnecessarily.

### Stage 1 Tests

Use TDD.  Add or update focused tests proving:

- default no-oracle behavior remains unchanged;
- unknown opt-in names fail closed;
- the old `q018_riccati` R60_K2 envelope remains unchanged;
- the new `q018_tablei_km4_transition` opt-in covers only the measured
  `kM=4`, `required_eval_radius=39.051248` fail-closed set;
- ordinary low-ell/default-covered modes still use the normal radial path;
- true out-of-envelope cases fail closed, including `required_eval_radius=60`,
  `k=4.0` outside the Table-I radius, `k=3.5` unless explicitly reviewed,
  and `ell` outside the measured envelope;
- metadata records review id, oracle name, envelope name, residuals, finite
  flags, and `A_in` role.

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py
```

Run full pytest if source/tests were changed:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

### Stage 1 Output

Create:

- `docs/phase5_km4_tablei_adapter_closeout.md`
- optional metadata-only JSON under
  `runs/phase5/km4_tablei_adapter_validation/`

If Stage 1 is GREEN, continue to Stage 2.  If YELLOW/RED, stop.

## Stage 2: Conservative Eight-Point Review-Grid Scan

### Goal

Generate a saved Table-I dense-review artifact at only the eight Table-I
points, using the T10g conservative review grid:

```text
kM_review =
[0.1, 0.2, 0.3, 0.5,
 0.75, 1.0, 1.25, 1.5, 1.75, 2.0,
 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0]
```

Points:

```text
z/M = 30
x/M = [0, 1, 2, 3, 10, 15, 20, 25]
```

Use pointwise wave-optics amplification:

```text
F_plus_complex  = h_plus_lensed / h_plus_unlensed
F_cross_complex = h_cross_lensed / h_cross_unlensed
```

### Required Numerics

For each frequency use:

```text
L_seed(kM) = ceil_to_multiple_of_12(max(84, 90*kM))
lmax_values = sorted unique [L_seed-72, L_seed-48, L_seed-24, L_seed]
```

Include accepted anchor overrides where appropriate:

- `kM=0.5`: final at least `84`;
- `kM=1.0`: include `108`;
- `kM=1.5`: include `156`;
- `kM=2.0`: include `180`.

Acceptance depends on final adjacent-pair convergence of the complex
`F_plus_complex` and `F_cross_complex` at all eight points.  The seed rule is
not itself sufficient.

### Stage 2 Output

Create:

```text
runs/phase5/fig5_fig6_dense_review_grid/
  tablei_dense_review_values.npz
  tablei_dense_review_values.npz.json
  manifest.md
```

The NPZ/JSON must include:

- `kM_values`;
- eight point coordinates and labels;
- complex `F_plus_complex`, `F_cross_complex`;
- magnitudes and principal/unwrapped phases;
- plus/cross masks separately;
- per-frequency `lmax_values`, final pair, final-pair deltas;
- radial/Q018 warning summaries;
- source code/config hash policy for this non-git workspace;
- no-Kirchhoff flag;
- no-paper-level-production flag.

### Stage 2 Checks

Run focused tests for any new IO/CLI/schema helpers.  Verify:

- all arrays finite or explicitly masked;
- no interpolation/fill/smoothing;
- no missing sidecar provenance;
- final adjacent pair passes for all frequencies and points;
- `kM=4` uses only the reviewed Table-I adapter envelope;
- no plots are generated in Stage 2.

If Stage 2 is GREEN, continue to Stage 3.  If convergence fails after one
reviewed `+24` or `+48` lmax extension, stop YELLOW with exact failing
frequency/point/component.

## Stage 3: Kirchhoff Eq. (47) Baseline Implementation

### Goal

Implement Kirchhoff Eq. (47) as a scalar comparison baseline only, using the
T1j frozen convention.

### Required Formula Policy

Use:

- project Fourier `exp(-i k t)`;
- `gamma = -2 M k`;
- principal real log for `(-gamma)^(-i gamma)` because `-gamma=2Mk>0`;
- principal complex Euler `Gamma(1+i gamma)`;
- Kummer `1F1(-i gamma, 1, -i gamma (xi/xi0)^2)`;
- `xi/xi0 = 0.5 * sqrt(r/M) * tan(theta)`;
- `theta_F = Arg(F_K)` principal phase, with unwrapped phase display-only.

Do not use Kirchhoff as denominator or correction.

### Stage 3 Output

Create:

```text
runs/phase5/fig5_fig6_kirchhoff_baseline/
  tablei_kirchhoff_baseline_values.npz
  tablei_kirchhoff_baseline_values.npz.json
  manifest.md
```

Use the same `kM_review` grid first.  If Stage 4 later proceeds to the
40-frequency grid, create a separate production-like Kirchhoff baseline file.

### Stage 3 Checks

Add focused tests for:

- branch/sign convention metadata;
- finite values for all Table-I points and `kM_review`;
- principal/unwrapped phase policy;
- no use as denominator;
- comparison-only sidecar flags.

If complex `Gamma`/`1F1` backend is unavailable or unstable, stop YELLOW.

## Stage 4: Review-Grid Plots

Create read-only review-grid diagnostic plots from the Stage 2 and Stage 3
artifacts only.  Do not recompute physics inside plotting.

Output:

```text
runs/phase5/fig5_fig6_review_grid_plots/
  fig5_near_axis_review_grid.png
  fig5_near_axis_review_grid.pdf
  fig6_far_axis_review_grid.png
  fig6_far_axis_review_grid.pdf
  sidecars...
  manifest.md
```

Use `scientific-visualization` guidance.  These are review-grid plots, not final
paper-style plots.

If Stage 4 plots reveal obvious phase aliasing or sparse-curve inadequacy, stop
YELLOW and recommend whether `Delta(kM)=0.1` or `0.05` is needed.

If Stage 4 is GREEN, continue to Stage 5.

## Stage 5: 40-Frequency Production-Like Point Scan

Run only if Stage 2 and Stage 4 passed.

Use:

```text
kM_production = [0.1, 0.2, ..., 3.9, 4.0]
```

Same eight points and same convergence policy.  Save:

```text
runs/phase5/fig5_fig6_dense_scan_production/
  tablei_dense_production_values.npz
  tablei_dense_production_values.npz.json
  manifest.md
```

Also create matching Kirchhoff production-like baseline under:

```text
runs/phase5/fig5_fig6_kirchhoff_baseline_production/
```

Stop YELLOW if:

- runtime is excessive;
- any frequency fails final-pair convergence after one reviewed extension;
- phase sampling appears aliased and requires `Delta(kM)=0.05`;
- `kM=4` adapter evidence fails at any required mode.

## Stage 6: Paper-Style Fig.5/Fig.6 Candidate Plots

Run only if Stage 5 passes.

Create:

```text
runs/phase5/fig5_fig6_paper_style_candidates/
  fig5_near_axis_paper_style_candidate.png
  fig5_near_axis_paper_style_candidate.pdf
  fig6_far_axis_paper_style_candidate.png
  fig6_far_axis_paper_style_candidate.pdf
  sidecars...
  manifest.md
```

Plot exact spin-2 plus/cross pointwise amplification magnitude and phase as
markers/curves, with Kirchhoff Eq. (47) as dashed scalar comparison baseline.

Use publication-grade output:

- vector PDF;
- at least 600 DPI PNG;
- readable labels, legends, and line widths;
- sidecars with source artifact hashes;
- no smoothing/fake interpolation of exact data;
- explicit `journal_candidate_pending_independent_review=true`.

## Final Required Verification

Run focused tests for all changed modules.  If source/tests changed during the
pipeline, run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Always run final file/provenance checks:

```bash
find runs/phase5/fig5_fig6_dense_review_grid runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
rg -n "journal_candidate_pending_independent_review|no_interpolation|comparison baseline|source.*sha|final_pair|kM=4|q018" runs/phase5/fig5_fig6_* -g '*.json' -g '*.md' 2>/dev/null
```

Update:

- `status.md`;
- the relevant handoff file, preferably `docs/handoffs/T12_current.md` if this
  thread is named T12, otherwise `docs/handoffs/T0_current.md`;
- create an archive handoff if replacing an existing current file.

## Final Status Labels

Use exactly one final label:

```text
GREEN / FIG5-FIG6 JOURNAL-CANDIDATE ARTIFACTS GENERATED PENDING INDEPENDENT REVIEW
YELLOW / PIPELINE PARTIAL - NEXT GATE IDENTIFIED
RED / PIPELINE BLOCKED BY PHYSICS OR NUMERICS
```

Even on GREEN, state that independent review is still required before final
journal-grade acceptance.

