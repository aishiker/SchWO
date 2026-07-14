# Phase 5 T7bq Prompt: Review Fig.5/Fig.6 Review-Grid Radial Gate

You are T7bq: independent review for the T4y Fig.5/Fig.6 review-grid radial
gate.

Do not start T8 and do not generate Fig.5/Fig.6 data/plots. Prefer read-only
inspection plus fresh verification.

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T0_current.md`
6. `docs/handoffs/T4_current.md`
7. `docs/handoffs/T7_current.md`
8. `docs/handoffs/T12b_current.md`
9. `docs/prompts/phase5_t4y_fig5_fig6_review_grid_radial_gate.md`
10. `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
11. `runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json`
12. `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json`
13. `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json`
14. `runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json`
15. `src/schwgw/numerics/radial_solver.py`
16. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
17. relevant tests under `tests/physics/`, `tests/unit/`, and `tests/regression/`.

Use `systematic-debugging` if a verification fails and
`verification-before-completion` before the final decision.

## Review Questions

Answer explicitly:

1. Did T4y reproduce the T12b `kM=2.5`, `ell=160`, Table-I required-radius
   blocker?
2. Did T4y classify the remaining high-frequency review-grid radial coverage
   instead of only fixing one mode?
3. Are all default failures either structured no-go or covered by a reviewed
   opt-in adapter?
4. If a new adapter was added, is it separate from `q018_tablei_km4_transition`
   and `q018_riccati`, exact, opt-in, and fail-closed?
5. Does the measured transition set in classification metadata exactly match
   the oracle-validation metadata?
6. Are all oracle values finite and within existing residual/stability
   thresholds?
7. Do ordinary default-covered modes stay on the normal radial path?
8. Were frozen conventions, thresholds, `lmax`, boundary policy, Q018 policy,
   and Kirchhoff policy preserved?
9. Did T4y avoid T8, Kirchhoff outputs, plots, fixtures, dense production, and
   paper-style artifacts?

## Required Fresh Checks

Run at least:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Parse the T4y metadata and independently confirm:

- no unstructured default errors remain in the reviewed high-frequency grid;
- classification and oracle-validation sets match;
- residual/stability maxima meet thresholds;
- adapter warnings and metadata identify the exact opt-in name and envelope;
- no forbidden downstream artifacts were created:

```bash
find runs/phase5/fig5_fig6_kirchhoff_baseline runs/phase5/fig5_fig6_review_grid_plots runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
```

## Outputs

Update:

- `status.md`
- `docs/handoffs/T7_current.md`

If GREEN, say T0 may schedule a T8 resume prompt for the conservative
eight-point review-grid scan from the T12b Stage 1 boundary. Do not start T8.

## Decision Labels

Use exactly one:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW-GRID RADIAL GATE PASSED
ACCEPT YELLOW / FIG5-FIG6 REVIEW-GRID RADIAL GATE PARTIAL
REJECT RED / FIG5-FIG6 REVIEW-GRID RADIAL GATE FAILED
```

GREEN requires all review questions to pass, fresh tests to pass, and no
forbidden downstream artifacts.

