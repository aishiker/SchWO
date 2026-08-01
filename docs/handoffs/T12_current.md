# T12 Current Handoff

Date: 2026-08-01

Thread: T12, Fig.5/Fig.6 autonomous gated pipeline.

## 2026-08-01 project sync

This autonomous pipeline is superseded and inactive. A later direct pipeline
did produce the complete \(40\times8\) Table-I grid and 600-dpi Fig.5/6
renders, but paper equivalence failed: exact plus/cross values and Kirchhoff
magnitudes differ materially from the published panels. Do not resume Stage
1 or run another dense grid. The only valid next step is one paper-facing
Table-I point with a frozen Kirchhoff normalization and observable. See
`status.md` and `docs/reports/li_hou_zhao_figures_3_8_completion_20260801.md`.

## Current Status

T12 stopped in Stage 1 with:

```text
YELLOW / PIPELINE PARTIAL - NEXT GATE IDENTIFIED
```

The pipeline did not implement the `kM=4` Table-I production adapter and did
not continue to Stage 2.

## Completed Work

- Created Goal mode objective for the autonomous pipeline.
- Read and followed:
  - `docs/prompts/phase5_autonomous_fig5_fig6_pipeline_goal.md`
- Read the required project context, handoffs, physics/numerics/validation
  docs, T4v/T4w reports, metadata, and relevant radial/oracle source/tests.
- Used applicable skills:
  - `using-superpowers`
  - `test-driven-development`
  - `systematic-debugging`
  - `verification-before-completion`
  - `scientific-visualization` was read for downstream plotting gates but not
    used because the pipeline stopped before plotting.
- Started the required Stage 1 default no-oracle continuous scan for
  `kM=4`, `ell=2..360`, odd/even, with
  `required_eval_radius=39.051248`, `r_out=300`, `r_in_eps=1e-6`,
  `rtol=1e-10`, `atol=1e-12`.
- Wrote:
  - `docs/phase5_km4_tablei_adapter_closeout.md`
  - `runs/phase5/km4_tablei_adapter_validation/stage1_yellow_blocker_metadata.json`

## Blocker

The required pre-implementation scan reached the printed checkpoint:

```text
ell=160
default_covered=318
default_fail_closed_uncovered=0
default_error_other=0
evanescent_tail_suppressed_radius_covered=0
```

Then it aborted in the transition region with:

```text
numpy.linalg.LinAlgError: SVD did not converge
```

The first reproduced blocker is `kM=4`, `ell=177`, odd/even.  The default
production path fails in bidirectional fallback condition-number SVD with
`barrier_action ~= 702.798961`.  This is a non-uncovered default error, not a
structured `evanescent_tail_required_radius_uncovered` fail-closed result.

The direct experimental oracle returned finite values for `ell=177` odd/even
with residuals around `1e-16`, but that does not permit bypassing the default
scan stop condition.

## Incomplete Work

- No `q018_tablei_km4_transition` adapter was implemented.
- No tests were added for the new adapter because the required precondition
  failed before implementation.
- Stage 2 review-grid scan was not started.
- No Kirchhoff baseline, plots, dense production scan, or paper-style
  candidate artifacts were generated.

## Frozen Decisions

- Fourier convention remains `exp(-i k t)`.
- Radial phase convention remains `exp(-i k r_star)` ingoing and
  `exp(+i k r_star)` outgoing.
- `A_in` remains the outer `exp(-i k r_star)` incoming coefficient.
- Existing `q018_riccati` R60_K2 envelope remains unchanged.
- Kirchhoff Eq. (47) remains scalar comparison baseline only.
- Q018 `required_eval_radius` remains fail-closed.
- No thresholds, `lmax`, boundary settings, or physics conventions were
  changed.

## Forbidden Actions

Until a new radial gate resolves the Stage 1 blocker:

- do not run T8 conservative review-grid scan;
- do not run dense Fig.5/Fig.6 production;
- do not generate 40-frequency scans, plots, fixtures, or Kirchhoff values;
- do not implement a `kM=4` adapter by skipping `ell=177`;
- do not lower `lmax`, relax thresholds, or change Q018 fail-closed policy.

## Must-Read Files For Next Thread

1. `status.md`
2. `docs/handoffs/T12_current.md`
3. `docs/phase5_km4_tablei_adapter_closeout.md`
4. `runs/phase5/km4_tablei_adapter_validation/stage1_yellow_blocker_metadata.json`
5. `docs/prompts/phase5_autonomous_fig5_fig6_pipeline_goal.md`
6. `docs/phase5_km4_tablei_radial_q018_preflight.md`
7. `docs/phase5_km4_tablei_transition_oracle_probe.md`
8. `runs/phase5/km4_tablei_radial_q018_preflight/radial_q018_preflight_metadata.json`
9. `runs/phase5/km4_tablei_transition_oracle_probe/transition_oracle_probe_metadata.json`
10. `src/schwgw/numerics/radial_solver.py`
11. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
12. `tests/physics/test_radial_solver.py`
13. `tests/physics/test_q018_production_integration_design.py`

## Exact Next Task

Schedule a focused T4 radial-method/error-structuring slice for the
`kM=4`, Table-I-radius transition blocker at `ell=177` odd/even.  The slice
should not start T8 or any Fig.5/Fig.6 artifact generation.

## Definition Of Done For This Stop

- Closeout document exists.
- Blocker metadata exists.
- `status.md` and this handoff record the YELLOW stop.
- No source, tests, configs, thresholds, conventions, adapter envelope, dense
  artifacts, plots, or Kirchhoff values are changed.

## Verification Commands And Results

Focused Stage 1 tests:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py
```

Results:

```text
141 passed, 12 subtests passed in 88.72s (0:01:28)
8 passed in 0.43s
```

Final file/provenance checks:

```bash
find runs/phase5/fig5_fig6_dense_review_grid runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
rg -n "journal_candidate_pending_independent_review|no_interpolation|comparison baseline|source.*sha|final_pair|kM=4|q018" runs/phase5/fig5_fig6_* -g '*.json' -g '*.md' 2>/dev/null
find src tests configs -type f -newer docs/phase5_km4_tablei_adapter_closeout.md -print | sort
```

Results:

- Stage 2/5/6 file listing returned no output.
- Keyword check matched only pre-existing
  `fig5_fig6_tablei_four_frequency_readonly` artifacts.
- `src/tests/configs` freshness check returned no output.
