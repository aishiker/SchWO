# Phase 5 T8ak Prompt: Fig.5/Fig.6 Review-Grid Kirchhoff Baseline

You are T8ak: implementation and data-output thread for the bounded
Li–Hou–Zhao Eq. (47) scalar Kirchhoff comparison baseline on the accepted
Fig.5/Fig.6 review grid.

## Objective

Implement an isolated Eq. (47) API and generate only the exact 18-frequency
by eight-Table-I-point Kirchhoff comparison artifact. Do not generate plots,
40-frequency production, fixtures, paper-style candidates, or any new
Schwarzschild solver data.

The enabling gate is:

```text
ACCEPT GREEN / FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA ACCEPTED
```

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T0_current.md`
6. `docs/handoffs/T7_current.md`
7. `docs/handoffs/T8_current.md`
8. `docs/superpowers/specs/2026-07-14-t8ak-t7bs-kirchhoff-auto-dispatch-design.md`
9. `docs/superpowers/plans/2026-07-14-t8ak-kirchhoff-review-grid.md`
10. `docs/prompts/phase5_t8ak_fig5_fig6_review_grid_kirchhoff_baseline.md`
11. `docs/prompts/phase5_t7bs_fig5_fig6_review_grid_kirchhoff_baseline_review.md`
12. `references/notes/kirchhoff_eq47_conventions.md`
13. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
14. `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz`
15. `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json`
16. `runs/phase5/fig5_fig6_dense_review_grid/manifest.md`
17. `pyproject.toml`
18. `src/schwgw/scattering/transmission.py`
19. `src/schwgw/io/tablei.py`

Check available skills first. You must use `executing-plans` to execute the
approved plan task-by-task, `test-driven-development` before implementation,
`systematic-debugging` for unexpected failures, and
`verification-before-completion` before any completion claim.

## Exact Execution Plan

Execute
`docs/superpowers/plans/2026-07-14-t8ak-kirchhoff-review-grid.md` exactly.
The plan contains the frozen API, tests, artifact schema, commands, hashes,
decision labels, and automatic T7bs dispatch procedure.

Do not replace the plan with the older T12/T12b autonomous prompt. Those
prompts are superseded for immediate execution after T7br.

## Frozen Formula And Branches

Use only:

```text
F_K = exp(pi gamma/2) * (-gamma)^(-i gamma)
      * Gamma(1+i gamma)
      * 1F1(-i gamma, 1, -i gamma eta^2)
gamma = -2 M k
eta = 0.5 * sqrt(r/M) * tan(theta)
```

Keep the principal real logarithm for `-gamma=2Mk>0`, principal complex
Gamma, Kummer `M=1F1`, positive-`k` project Fourier convention
`exp(-i k t)`, and principal stored phase. Do not conjugate Eq. (47).

The same scalar value is comparison-only and polarization-independent. It is
not a plus/cross prediction.

## Backend Rule

The current system SciPy does not support the required complex-parameter
`hyp1f1`, while `pyproject.toml` already declares `mpmath` in the `oracle`
optional dependency. Use only the existing project `.venv`; if needed, install
the already-declared extras there with:

```bash
.venv/bin/python -m pip install -e '.[dev,oracle]'
```

Do not install globally. Do not add an undeclared dependency. Do not write an
unreviewed special-function approximation. If the project-local backend is
unavailable or unstable on the exact domain, stop YELLOW.

## Input Integrity

The accepted source hashes are:

```text
NPZ      a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
JSON     2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
manifest 86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
```

Verify them before generation. Never write to, rename, delete, or regenerate
the T8aj source artifact.

Use its exact arrays and ordering. Do not reconstruct, round, interpolate,
smooth, fill, or expand the frequency or point grid. Store both coordinate-
derived `eta` and rounded paper `xi/xi0`, and require their maximum difference
to be below `5e-5`.

## Allowed Changes

Only these implementation paths are allowed:

- `src/schwgw/scattering/kirchhoff.py`
- `src/schwgw/scattering/__init__.py`
- `tests/unit/test_kirchhoff.py`
- `src/schwgw/io/kirchhoff.py`
- `src/schwgw/io/__init__.py`
- `scripts/phase5_generate_kirchhoff_baseline.py`
- `tests/unit/test_kirchhoff_artifact.py`
- `runs/phase5/fig5_fig6_kirchhoff_baseline/`
- `status.md`
- `docs/handoffs/T8_current.md`
- `docs/handoffs/archive/T8_2026-07-14_pre_t8ak_kirchhoff_baseline.md`

The plan permits exact-path commits for the new source/tests/script files.
Do not stage or commit unrelated existing worktree changes. Do not commit the
ignored run artifacts. Do not push GitHub; milestone synchronization is T0-only
after T7bs acceptance.

## Forbidden Actions

- Do not modify `src/schwgw/scattering/transmission.py` or any production
  pointwise amplification denominator, mask, normalization, or polarization
  path.
- Do not call or modify radial/scattering solvers, Q018, `lmax`, boundary
  policies, configs, existing fixtures, or visualization code.
- Do not use Kirchhoff to accept, repair, mask, normalize, calibrate, or
  replace T8aj values.
- Do not create review-grid PNG/PDF, 40-frequency data, interpolation,
  smoothing, paper-style candidates, Appendix D/E curves, or fixtures.
- Do not weaken tests, tolerances, branch checks, hash checks, or metadata
  non-claims to obtain GREEN.
- Do not start T7bs before all T8ak code, artifact, tests, status, and T8
  handoff writes have completed and been freshly verified.
- Do not create a new Codex task if an existing target is unavailable.

## Required Verification

At minimum run every command in Tasks 1–5 of the implementation plan,
including focused pytest, Ruff, fresh artifact assertions, the full pytest
suite, source-hash recheck, forbidden-output check, and `git diff --check`.

Because source code changes, full pytest is mandatory for GREEN.

## Status And Handoff

Before stopping, update:

- `status.md`;
- `docs/handoffs/T8_current.md`;
- archive the pre-T8ak handoff at
  `docs/handoffs/archive/T8_2026-07-14_pre_t8ak_kirchhoff_baseline.md`.

Record every changed file, command, test count, backend/version/dps, input and
output SHA-256, maximum eta mismatch, warnings, non-claims, and dispatch result.

## Decision Labels

Use exactly one:

```text
GREEN / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE GENERATED
YELLOW / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE PARTIAL
RED / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE BLOCKED
```

GREEN requires all code/tests/artifacts/fresh checks and documentation to pass.

## Automatic Dispatch

The user explicitly authorized cross-task automatic dispatch. On exact GREEN
only, send the message frozen in Task 5 of the implementation plan to existing
T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed` using model `gpt-5.6-sol` and
thinking `high`. Then notify T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636` of the decision, hashes, test result,
and T7 dispatch status.

On YELLOW, RED, incomplete, failed verification, or ambiguity, do not start
T7bs. Notify T0 only.

If the Codex messaging tool is unavailable after scientific GREEN, retain the
scientific result, record `auto-dispatch blocked`, notify T0 if possible, and
stop. Do not create a replacement task.

An explicit model-capacity interruption may be recovered by T0 in this same
task using 5.6 Terra High. Scientific failures are not capacity failures and
must not trigger model fallback.
