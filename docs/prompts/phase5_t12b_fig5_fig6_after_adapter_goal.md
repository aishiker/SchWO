# Phase 5 T12b Prompt: Fig.5/Fig.6 Pipeline After Accepted kM=4 Adapter Gate

You are T12b: autonomous Fig.5/Fig.6 continuation after the T7bp GREEN adapter
gate.

Use Goal mode.

Goal objective:

```text
Starting from T7bp ACCEPT GREEN for the kM=4 Table-I transition adapter gate,
advance the Fig.5/Fig.6 pipeline through review-grid data, Kirchhoff comparison
baseline, review-grid plots, 40-frequency production-like point scan, and
paper-style Fig.5/Fig.6 candidate plots. Continue automatically only when each
stage's self-checks pass. If a stage fails, diagnose and attempt at most two
focused repair iterations inside that stage. Stop rather than bypassing
physics, radial/Q018, convention, provenance, threshold, lmax, or validation
gates.
```

## Role Boundary

You are an execution thread that may perform T8-like data/plotting work and
self-checks. You are not a replacement for final independent review.

If all stages pass, label the final artifacts:

```text
journal-candidate pending independent review
```

Do not claim final journal-grade acceptance or pixel-level reproduction.

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
10. `docs/handoffs/T12_current.md`
11. `docs/physics_spec.md`
12. `docs/equation_map.md`
13. `docs/numerics.md`
14. `docs/validation_plan.md`
15. `docs/phase5_km4_tablei_transition_error_structuring_adapter.md`
16. `runs/phase5/km4_tablei_adapter_validation/t4x_default_classification_metadata.json`
17. `runs/phase5/km4_tablei_adapter_validation/t4x_oracle_validation_metadata.json`
18. `docs/phase5_km4_tablei_adapter_closeout.md`
19. `runs/phase5/km4_tablei_adapter_validation/stage1_yellow_blocker_metadata.json`
20. `references/manifest.md`
21. `references/notes/kirchhoff_eq47_conventions.md`
22. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
23. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
24. `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
25. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
26. relevant source/tests under `src/`, `tests/`, `configs/`.

Before each stage, check installed plugins/skills. Use:

- `systematic-debugging` for failures;
- `test-driven-development` for code changes;
- `scientific-visualization` for plotting;
- `verification-before-completion` before every stage-complete claim.

## Global Hard Rules

- Do not rerun or reimplement the T4x adapter gate except for a short smoke
  check. T7bp already accepted it.
- Do not lower `lmax`, relax thresholds, weaken convergence criteria, or hide
  failed modes.
- Do not change frozen Fourier, harmonic, tetrad, RW/Zerilli, Route B,
  Q014/Q015/Q018, or Kirchhoff branch conventions.
- Do not use Kirchhoff Eq. (47) as denominator, mask, correction, or production
  normalization. It is a scalar comparison baseline only.
- Do not use interpolation, smoothing, or curve fitting to fake dense exact
  spin-2 data.
- Save all result and plot artifacts under `runs/phase5/...` inside the
  project. Do not place final artifacts in temporary/private folders.
- If any source/test/config/run artifact is modified, record it in `status.md`
  and the handoff.
- If a command runs longer than 2 hours without progress, stop that stage and
  record a YELLOW runtime blocker.
- If three consecutive attempts hit the same blocker, stop and report it.

## Stage 0: Adapter Gate Sanity Check

Confirm from `status.md` and `docs/handoffs/T7_current.md` that:

```text
ACCEPT GREEN / KM4 TABLE-I TRANSITION ADAPTER GATE PASSED
```

Run a minimal smoke check that the new opt-in adapter name
`q018_tablei_km4_transition` is available and that a representative in-envelope
mode, e.g. `k=4`, `ell=177`, odd and even, is finite at
`required_eval_radius=39.051248`.

If this fails, stop YELLOW and do not start Stage 1.

## Stage 1: Conservative Eight-Point Review-Grid Scan

Generate a saved Table-I dense-review artifact at the eight Table-I points:

```text
z/M = 30
x/M = [0, 1, 2, 3, 10, 15, 20, 25]
```

Use:

```text
kM_review =
[0.1, 0.2, 0.3, 0.5,
 0.75, 1.0, 1.25, 1.5, 1.75, 2.0,
 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0]
```

Use pointwise wave-optics amplification:

```text
F_plus_complex  = h_plus_lensed / h_plus_unlensed
F_cross_complex = h_cross_lensed / h_cross_unlensed
```

Use the accepted Table-I point definitions from `src/schwgw/io/tablei.py`.

### lmax Policy

For each frequency:

```text
L_seed(kM) = ceil_to_multiple_of_12(max(84, 90*kM))
lmax_values = sorted unique [L_seed-72, L_seed-48, L_seed-24, L_seed]
```

Clip to `lmax >= 24`, and include accepted anchor overrides:

- `kM=0.5`: final at least `84`;
- `kM=1.0`: include `108`;
- `kM=1.5`: include `156`;
- `kM=2.0`: include `180`.

Acceptance depends on final adjacent-pair convergence of complex
`F_plus_complex` and `F_cross_complex` at all eight points. The seed rule is
not sufficient.

If the final pair fails, attempt one reviewed extension by `+24` or `+48`.
If it still fails, stop YELLOW with exact failing frequency, point, component,
and deltas.

### Stage 1 Output

Create:

```text
runs/phase5/fig5_fig6_dense_review_grid/
  tablei_dense_review_values.npz
  tablei_dense_review_values.npz.json
  manifest.md
```

The NPZ/JSON must include:

- `kM_values`;
- point coordinates/labels;
- complex `F_plus_complex`, `F_cross_complex`;
- magnitudes and principal/unwrapped phases;
- plus/cross masks separately;
- per-frequency `lmax_values`, final pair, final-pair deltas;
- radial/Q018 warning summaries, including `q018_tablei_km4_transition` use at
  `kM=4`;
- source/config hash policy for this non-git workspace;
- `no_kirchhoff=true`;
- `no_paper_level_production=true`;
- `no_interpolation=true`;
- `no_smoothing=true`.

Do not generate plots in Stage 1.

## Stage 2: Kirchhoff Eq. (47) Baseline For Review Grid

Implement or reuse Kirchhoff Eq. (47) as a scalar comparison baseline only,
using the T1j frozen convention:

- Fourier `exp(-i k t)`;
- `gamma = -2 M k`;
- principal real log for `(-gamma)^(-i gamma)` because `-gamma=2Mk>0`;
- principal complex Euler `Gamma(1+i gamma)`;
- Kummer `1F1(-i gamma, 1, -i gamma (xi/xi0)^2)`;
- `xi/xi0 = 0.5 * sqrt(r/M) * tan(theta)`;
- `theta_F = Arg(F_K)` principal phase; unwrapped phase is display-only.

Do not use Kirchhoff as denominator, correction, mask, or normalization.

Create:

```text
runs/phase5/fig5_fig6_kirchhoff_baseline/
  tablei_kirchhoff_baseline_values.npz
  tablei_kirchhoff_baseline_values.npz.json
  manifest.md
```

Add focused tests if source code is added. Stop YELLOW if the complex
Gamma/Kummer backend is unavailable or unstable.

## Stage 3: Review-Grid Diagnostic Plots

Create read-only diagnostic plots from Stage 1 and Stage 2 artifacts only.
Do not recompute physics inside plotting.

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

These are review-grid plots, not final paper-style plots. Use
`scientific-visualization` guidance.

If the plots or metadata show obvious phase aliasing or sparse-curve
inadequacy, stop YELLOW and recommend whether `Delta(kM)=0.1` or `0.05` is
needed.

## Stage 4: 40-Frequency Production-Like Point Scan

Run only if Stages 1-3 pass.

Use:

```text
kM_production = [0.1, 0.2, ..., 3.9, 4.0]
```

Same eight points and convergence policy. Save:

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

Stop YELLOW if runtime is excessive, any frequency fails final-pair
convergence after one reviewed extension, phase sampling appears aliased, or
`kM=4` adapter evidence fails.

## Stage 5: Paper-Style Fig.5/Fig.6 Candidate Plots

Run only if Stage 4 passes.

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

Publication-candidate requirements:

- vector PDF;
- at least 600 DPI PNG;
- readable labels, legends, and line widths;
- sidecars with source artifact hashes;
- no smoothing/fake interpolation of exact data;
- `journal_candidate_pending_independent_review=true`.

## Final Verification

Run focused tests for all changed modules. If source/tests changed, run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Always run:

```bash
find runs/phase5/fig5_fig6_dense_review_grid runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
rg -n "journal_candidate_pending_independent_review|no_interpolation|comparison baseline|source.*sha|final_pair|kM=4|q018_tablei_km4_transition" runs/phase5/fig5_fig6_* -g '*.json' -g '*.md' 2>/dev/null
```

Update:

- `status.md`;
- `docs/handoffs/T12_current.md` or a new `docs/handoffs/T12b_current.md`;
- archive superseded handoff if useful.

## Final Status Labels

Use exactly one:

```text
GREEN / FIG5-FIG6 JOURNAL-CANDIDATE ARTIFACTS GENERATED PENDING INDEPENDENT REVIEW
YELLOW / FIG5-FIG6 PIPELINE PARTIAL - NEXT GATE IDENTIFIED
RED / FIG5-FIG6 PIPELINE BLOCKED BY PHYSICS OR NUMERICS
```

Even on GREEN, state that independent review remains required before final
journal-grade acceptance.

