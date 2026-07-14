# Phase 5 T7bs Prompt: Review Fig.5/Fig.6 Kirchhoff Baseline

You are T7bs: independent reviewer for the T8ak bounded Kirchhoff Eq. (47)
scalar comparison baseline on the accepted Fig.5/Fig.6 review grid.

Prefer read-only inspection and independent fresh verification. Do not repair
the implementation, regenerate the baseline, or create plots, 40-frequency
production, fixtures, or paper-style candidates.

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
13. `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz`
14. `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json`
15. `runs/phase5/fig5_fig6_dense_review_grid/manifest.md`
16. `runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz`
17. `runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json`
18. `runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md`
19. all T8ak changed source, test, and script files.

Use `verification-before-completion` before the final decision and
`systematic-debugging` if any fresh check fails.

## Review Questions

Answer explicitly:

1. Does the source implement the frozen Eq. (47) exactly, with
   `gamma=-2Mk`, coordinate-derived `eta`, principal positive-real log,
   principal complex Gamma, Kummer M, and no conjugation?
2. Is the backend project-local `mpmath`, lazy/optional, finite and stable on
   all 144 values, with backend version and dps recorded?
3. Are the source `kM` and point arrays bitwise/exactly identical to T8aj,
   with the three accepted T8aj hashes unchanged?
4. Does coordinate-derived eta agree with the rounded paper values to below
   `5e-5`, while storing both without silently substituting one for the other?
5. Are `F_kirchhoff_complex`, magnitude, principal phase, display-only
   unwrapped phase, and validity mask shaped `(18,8)` and finite?
6. Does an independent 100-dps computation agree with the artifact, and does
   the Kummer transformation agree at the high-risk corners?
7. Do NPZ, JSON, and manifest schemas/hashes/metadata agree?
8. Is the API completely separate from the Schwarzschild solver and
   production pointwise amplification denominator, masks, normalization, and
   polarization channels?
9. Did T8ak avoid visualization, configs, fixtures, 40-frequency production,
   paper-style artifacts, and mutation of the T8aj source artifact?
10. Do focused tests, Ruff, and full pytest pass freshly?

## Required Fresh Checks

First verify source and output hashes:

```bash
shasum -a 256 \
  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz \
  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json \
  runs/phase5/fig5_fig6_dense_review_grid/manifest.md \
  runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz \
  runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json \
  runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md
```

The first three must remain exactly:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
```

Run an independent all-grid 100-dps calculation. Do not call the T8ak compute
function for the reference values:

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path

import mpmath as mp
import numpy as np

source_path = Path("runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz")
baseline_path = Path("runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz")
with np.load(source_path, allow_pickle=False) as source, np.load(baseline_path, allow_pickle=False) as baseline:
    np.testing.assert_array_equal(baseline["kM_values"], source["kM_values"])
    for key in ["point_ids", "point_x", "point_y", "point_z", "point_r", "point_theta", "paper_xi_over_xi0"]:
        np.testing.assert_array_equal(baseline[key], source[key])
    kM = source["kM_values"].copy()
    radius = source["point_r"].copy()
    theta = source["point_theta"].copy()
    saved = baseline["F_kirchhoff_complex"].copy()
    eta_saved = baseline["eta"].copy()
    np.testing.assert_allclose(
        eta_saved,
        0.5 * np.sqrt(radius) * np.tan(theta),
        rtol=0.0,
        atol=2e-15,
    )
    assert np.max(np.abs(baseline["eta_minus_paper"])) < 5e-5
    assert baseline["valid_kirchhoff_mask"].all()
    np.testing.assert_allclose(baseline["abs_F_kirchhoff"], np.abs(saved))
    np.testing.assert_allclose(
        baseline["arg_F_kirchhoff_principal"], np.angle(saved), rtol=0.0, atol=1e-15
    )
    np.testing.assert_allclose(
        baseline["arg_F_kirchhoff_unwrapped"],
        np.unwrap(np.angle(saved), axis=0),
        rtol=0.0,
        atol=1e-14,
    )

reference = np.empty_like(saved)
with mp.workdps(100):
    for i, kM_value in enumerate(kM):
        gamma = -2 * mp.mpf(str(float(kM_value)))
        prefactor = mp.exp(
            mp.pi * gamma / 2
            + (-1j * gamma) * mp.log(-gamma)
            + mp.loggamma(1 + 1j * gamma)
        )
        for j, eta_value in enumerate(eta_saved):
            eta = mp.mpf(str(float(eta_value)))
            reference[i, j] = complex(
                prefactor * mp.hyp1f1(-1j * gamma, 1, -1j * gamma * eta**2)
            )

np.testing.assert_allclose(saved, reference, rtol=5e-13, atol=5e-13)

for i, j in [(0, 0), (0, 7), (17, 0), (17, 7)]:
    with mp.workdps(120):
        gamma = -2 * mp.mpf(str(float(kM[i])))
        eta = mp.mpf(str(float(eta_saved[j])))
        a = -1j * gamma
        z = -1j * gamma * eta**2
        prefactor = mp.exp(
            mp.pi * gamma / 2
            + (-1j * gamma) * mp.log(-gamma)
            + mp.loggamma(1 + 1j * gamma)
        )
        transformed = prefactor * mp.exp(z) * mp.hyp1f1(1 - a, 1, -z)
    np.testing.assert_allclose(saved[i, j], complex(transformed), rtol=8e-13, atol=8e-13)

metadata = json.loads(Path(str(baseline_path) + ".json").read_text(encoding="utf-8"))
for key in [
    "comparison_only", "not_denominator", "not_mask", "not_normalization",
    "polarization_independent", "no_solver_rerun", "no_plotting",
    "not_40_frequency_production", "no_fixtures", "no_paper_style_candidates",
]:
    assert metadata[key] is True, key
print("T7BS_INDEPENDENT_100DPS_AUDIT=PASS")
PY
```

Run code/test checks:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_kirchhoff.py tests/unit/test_kirchhoff_artifact.py -q
.venv/bin/python -m ruff check src/schwgw/scattering/kirchhoff.py src/schwgw/io/kirchhoff.py scripts/phase5_generate_kirchhoff_baseline.py tests/unit/test_kirchhoff.py tests/unit/test_kirchhoff_artifact.py src/schwgw/scattering/__init__.py src/schwgw/io/__init__.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Full pytest is mandatory because T8ak changes source code.

Run scope and forbidden-output checks:

```bash
git status --short
git diff HEAD~2..HEAD -- src tests scripts pyproject.toml configs
git diff -- src/schwgw/scattering/transmission.py src/schwgw/numerics src/schwgw/viz configs tests/regression/fixtures
find \
  runs/phase5/fig5_fig6_review_grid_plots \
  runs/phase5/fig5_fig6_dense_scan_production \
  runs/phase5/fig5_fig6_paper_style_candidates \
  -maxdepth 2 -type f -print 2>/dev/null | sort
```

The review must inspect actual commits and worktree state rather than assuming
that `HEAD~2..HEAD` contains only T8ak. Any unrelated change is reported and
excluded from the scientific decision unless it affects the reviewed paths.

## Allowed Review Writes

Only:

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-14_pre_t7bs_kirchhoff_baseline.md`

Do not modify source, tests, script, T8ak artifacts, T8aj artifacts, configs,
or any other handoff.

## Decision Labels

Use exactly one:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE ACCEPTED
ACCEPT YELLOW / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE PARTIAL
REJECT RED / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE FAILED
```

GREEN requires every formula/branch/grid/hash/schema/isolation/test check to
pass. A scientific or test failure must not be bypassed by switching models.

## Completion And Signal

Archive the pre-T7bs T7 handoff, update `status.md` and
`docs/handoffs/T7_current.md`, then freshly verify both documents.

Send the exact decision, output hashes, independent-audit result, pytest
result, and changed review files to T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636` using the Codex task messaging tool.

Do not start diagnostic plotting or any later task. Only T0 may inspect the
decision, perform the major-node GitHub synchronization, and design the next
gate.
