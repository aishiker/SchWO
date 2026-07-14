# Phase 5 T8al Prompt: Kirchhoff Units/Dtype Metadata Contract

You are T8al: bounded metadata-contract hardening for the T7bs YELLOW.

## Objective

Add explicit `units` and `dtype` fields to the Kirchhoff baseline embedded NPZ
metadata, JSON sidecar, and manifest. Regenerate only the same three baseline
files and prove every non-metadata array is byte-identical to T8ak.

Enabling decision:

```text
ACCEPT YELLOW / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE PARTIAL
```

The YELLOW is metadata-only. Formula, branches, all 144 values, 100/120-dps
checks, hashes, isolation, focused tests, Ruff, and full pytest passed.

## Read First

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/superpowers/specs/2026-07-14-t8ak-t7bs-kirchhoff-auto-dispatch-design.md`
7. `docs/superpowers/plans/2026-07-14-t8al-kirchhoff-metadata-contract.md`
8. `docs/prompts/phase5_t8al_fig5_fig6_kirchhoff_metadata_contract.md`
9. `docs/prompts/phase5_t7bt_fig5_fig6_kirchhoff_metadata_contract_review.md`
10. `src/schwgw/io/kirchhoff.py`
11. `tests/unit/test_kirchhoff_artifact.py`
12. the three T8ak baseline files and three unchanged T8aj source files.

Use `executing-plans`, `test-driven-development`,
`verification-before-completion`, and `systematic-debugging` if needed.

## Exact Work

Execute
`docs/superpowers/plans/2026-07-14-t8al-kirchhoff-metadata-contract.md`
task-by-task. The mappings, tests, frozen pre-hardening array fingerprints,
commands, labels, and T7bt dispatch message are normative.

## Allowed Changes

- `src/schwgw/io/kirchhoff.py`
- `tests/unit/test_kirchhoff_artifact.py`
- exactly three files under `runs/phase5/fig5_fig6_kirchhoff_baseline/`
- `status.md`
- `docs/handoffs/T8_current.md`
- `docs/handoffs/archive/T8_2026-07-14_pre_t8al_metadata_contract.md`

## Forbidden Actions

- No change to `src/schwgw/scattering/kirchhoff.py`, formula, branches,
  precision, backend, input grid, or numerical values.
- No T8aj mutation, solver, transmission, Q018, polarization, visualization,
  config, fixture, plot, 40-frequency, interpolation, smoothing, or
  paper-style work.
- No extra file in the project baseline directory.
- No weakening the units/dtype mapping or tests.
- No GitHub push; T0 owns milestone sync after independent GREEN.

## Decision And Dispatch

Use exactly one T8al label from the plan. Only exact GREEN may dispatch the
frozen T7bt prompt to existing T7 with 5.6 Sol High. Otherwise notify T0 only.
Scientific/test failures are not model-capacity failures.
