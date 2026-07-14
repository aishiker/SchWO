# Phase 5 T8aj Prompt: Resume Fig.5/Fig.6 Conservative Review-Grid Data

You are T8aj: data-output thread for the Fig.5/Fig.6 conservative eight-point
review-grid after the T7bq radial gate acceptance.

## Objective

Generate the conservative review-grid Table-I point-frequency data artifact
only.  Do not generate Kirchhoff baselines, plots, dense 40-frequency
production scans, fixtures, or paper-style candidates.

The current enabling gate is:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW-GRID RADIAL GATE PASSED
```

from T7bq.  Use the reviewed opt-in radial adapter
`q018_tablei_review_grid_transition` only within its accepted envelope.

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T0_current.md`
6. `docs/handoffs/T4_current.md`
7. `docs/handoffs/T7_current.md`
8. `docs/handoffs/T8_current.md`
9. `docs/handoffs/T12b_current.md`
10. `docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md`
11. `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
12. `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json`
13. `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json`
14. `runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json`
15. `runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json`
16. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
17. `references/notes/kirchhoff_eq47_conventions.md`
18. `src/schwgw/io/tablei.py`
19. relevant T8 IO/result/config/CLI modules and tests.

Before starting, check installed plugins/skills. Use `systematic-debugging` for
failures, `test-driven-development` for source changes, and
`verification-before-completion` before claiming completion.

## Hard Rules

- Do not modify physics conventions, radial thresholds, `lmax` policy, Route B
  polarization, Q018 policy, or the reviewed radial adapter envelopes.
- Do not broaden `q018_tablei_review_grid_transition`.
- Do not use Kirchhoff Eq. (47) as denominator, correction, mask, or
  normalization.
- Do not implement or generate Kirchhoff outputs in this slice.
- Do not generate plots, PNG/PDF, paper-style figures, Appendix D/E curves,
  fixtures, or 40-frequency production-like scans.
- Save all new artifacts under `runs/phase5/fig5_fig6_dense_review_grid/`.
- Preserve the previous T12b `stage1_yellow_error.json`; do not delete or
  overwrite it.

## Review Grid

Use exactly these Table-I points:

```text
z/M = 30
x/M = [0, 1, 2, 3, 10, 15, 20, 25]
```

Use the point definitions from `src/schwgw/io/tablei.py`.

Use exactly:

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

The denominator remains the project flat/no-lens Route-B-compatible
polarization field, not Kirchhoff.

## lmax Policy

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
`F_plus_complex` and `F_cross_complex` at all eight points.

If the final pair fails, attempt one reviewed extension by `+24` or `+48`.
If it still fails, stop YELLOW with exact failing frequency, point, component,
and deltas.

## Radial Adapter Use

For `kM in {2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0}` at the Table-I radii, use
`experimental_required_radius_oracle="q018_tablei_review_grid_transition"` in
the boundary config so the reviewed adapter can handle measured transition
modes.  Ordinary default-covered modes must remain on the normal radial path.

For lower `kM`, do not force this adapter unless T4y/T7bq metadata explicitly
includes the mode/radius/frequency.

Stop YELLOW if any radial failure appears outside the T7bq-reviewed envelope.

## Output

Create:

```text
runs/phase5/fig5_fig6_dense_review_grid/
  tablei_dense_review_values.npz
  tablei_dense_review_values.npz.json
  manifest.md
```

The NPZ and JSON sidecar must include:

- `kM_values`;
- point coordinates and labels;
- complex `F_plus_complex`, `F_cross_complex`;
- `abs_F_plus`, `abs_F_cross`;
- principal and unwrapped phases for plus/cross;
- plus/cross masks separately;
- per-frequency `lmax_values`, final pair, and final-pair deltas;
- radial/Q018 warning summaries, including counts/codes for
  `q018_tablei_review_grid_transition_oracle_used`;
- reference to T4y/T7bq radial-gate metadata paths;
- source/config hashes or deterministic source file hashes for this non-git
  workspace;
- `no_kirchhoff=true`;
- `no_plotting=true`;
- `no_paper_level_production=true`;
- `no_interpolation=true`;
- `no_smoothing=true`.

## Verification

Run focused tests for any changed modules.  If source/tests changed, run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Always run artifact checks:

```bash
python - <<'PY'
import json
import numpy as np
from pathlib import Path
p = Path("runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz")
assert p.exists(), p
data = np.load(p, allow_pickle=False)
assert data["F_plus_complex"].shape == (18, 8)
assert data["F_cross_complex"].shape == (18, 8)
assert np.isfinite(data["abs_F_plus"]).all()
assert np.isfinite(data["abs_F_cross"]).all()
side = json.loads(Path(str(p) + ".json").read_text())
assert side["no_kirchhoff"] is True
assert side["no_plotting"] is True
assert side["no_paper_level_production"] is True
assert side["no_interpolation"] is True
assert side["no_smoothing"] is True
PY

find runs/phase5/fig5_fig6_kirchhoff_baseline runs/phase5/fig5_fig6_review_grid_plots runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
```

The `find` command must return no files created by this slice.

## Update Required

Update:

- `status.md`;
- `docs/handoffs/T8_current.md`.

If this slice changes source/tests/configs, list every changed file and command
in `status.md`.

## Decision Labels

Use exactly one:

```text
GREEN / FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA GENERATED
YELLOW / FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA PARTIAL
RED / FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA BLOCKED
```

GREEN requires the NPZ/JSON/manifest artifact set, final adjacent-pair
convergence, radial/Q018 metadata, no Kirchhoff/plot/dense-production
artifacts, and relevant tests/checks passing.

