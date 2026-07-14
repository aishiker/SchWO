# Phase 5 T7br Prompt: Review Fig.5/Fig.6 Conservative Review-Grid Data

You are T7br: independent review for the T8aj conservative Fig.5/Fig.6
review-grid data artifact.

Do not generate plots, Kirchhoff baselines, dense production scans, fixtures,
or paper-style artifacts.  Prefer read-only inspection plus fresh verification.

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
15. `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz`
16. `runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json`
17. `runs/phase5/fig5_fig6_dense_review_grid/manifest.md`

Use `verification-before-completion` before the final decision.  Use
`systematic-debugging` if any check fails.

## Review Questions

Answer explicitly:

1. Did T8aj generate exactly the conservative review-grid data artifact and no
   downstream Kirchhoff/plot/dense-production/paper-style artifacts?
2. Are `kM_values` exactly the 18-value review grid?
3. Are the eight Table-I points exactly `z=30`, `x=[0,1,2,3,10,15,20,25]`?
4. Are `F_plus_complex` and `F_cross_complex` shape `(18, 8)` and finite where
   masks say valid?
5. Are plus/cross masks separate and consistent with invalid denominator
   policy?
6. Did final adjacent-pair convergence pass for all frequencies, points, and
   components?
7. Does sidecar metadata record lmax values/final pairs/final deltas for every
   frequency?
8. Does radial/Q018 metadata show only reviewed adapter use, especially
   `q018_tablei_review_grid_transition_oracle_used` for the high-frequency
   transition set?
9. Was Kirchhoff not used as denominator, correction, mask, normalization, or
   comparison output in this slice?
10. Were frozen conventions, thresholds, `lmax`, boundary policy, Q018 policy,
    and Route B polarization preserved?

## Required Fresh Checks

Run:

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
assert data["kM_values"].shape == (18,)
assert data["point_x"].shape == (8,)
assert data["point_z"].shape == (8,)
side = json.loads(Path(str(p) + ".json").read_text())
for key in ["no_kirchhoff", "no_plotting", "no_paper_level_production", "no_interpolation", "no_smoothing"]:
    assert side[key] is True, key
PY

find runs/phase5/fig5_fig6_kirchhoff_baseline runs/phase5/fig5_fig6_review_grid_plots runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
```

If source/tests changed in T8aj, run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If T8aj only generated data artifacts, run targeted metadata checks instead
and explain why full pytest is not needed.

## Outputs

Update:

- `status.md`;
- `docs/handoffs/T7_current.md`.

Do not mutate the T8aj NPZ/JSON/manifest except for a clearly documented
metadata typo fix.  Prefer no artifact mutation.

## Decision Labels

Use exactly one:

```text
ACCEPT GREEN / FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA ACCEPTED
ACCEPT YELLOW / FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA PARTIAL
REJECT RED / FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA FAILED
```

GREEN allows T0 to schedule the next bounded stage: Kirchhoff Eq. (47)
comparison baseline for the same review grid, followed by read-only
review-grid diagnostic plots.  GREEN does not authorize 40-frequency production
or paper-style candidates by itself.

