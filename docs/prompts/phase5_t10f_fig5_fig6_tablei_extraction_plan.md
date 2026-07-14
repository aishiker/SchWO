# Phase 5 T10f Prompt: Fig.5/Fig.6 Table-I Extraction Planning

You are T10f: literature/numerics planning support for Li-Hou-Zhao Fig.5/Fig.6 Table-I point-frequency extraction.

## Mandatory Context

Before doing anything else, check whether installed plugins or skills are relevant. Use local project notes before the raw PDF unless there is a conflict or missing detail.

Read:

- `project.md`
- `status.md`
- `docs/physics_spec.md`
- `docs/equation_map.md`
- `docs/numerics.md`
- `docs/validation_plan.md`
- `docs/phase5_fig4_exact_angular_closeout.md`
- `docs/phase5_m5_four_frequency_closeout.md`
- `docs/phase4_production_closeout.md`
- `references/manifest.md`
- `references/notes/t10d_li_hou_zhao_figure_inventory.md`
- `references/notes/t10e_fig4_fig5_reproduction_plan.md`
- `docs/prompts/phase5_t10e_fig4_fig5_reproduction_planning.md`
- `docs/prompts/phase5_t7at_fig4_fig5_plan_review.md`
- `runs/phase5/m5_four_frequency_amplification_artifacts/manifest.md`

You may inspect the existing M5 four-frequency amplification NPZ metadata read-only to confirm grid, frequency, field, mask, and point availability. Do not create numerical artifacts.

## Task

Create a planning note:

- `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`

Update:

- `status.md`

Do not modify `src`, tests, configs, frozen convention docs, result artifacts, fixtures, plots, or `runs/` contents.

This is a planning-only slice. Do not run the solver, do not generate `.npz`, `.h5`, `.png`, `.pdf`, fixtures, or new configs.

## Required Planning Content

The note must clearly separate three scopes:

1. **Read-only four-frequency Table-I extraction pilot**
   - Uses the existing archive under `runs/phase5/m5_four_frequency_amplification_artifacts/`.
   - Frequencies are exactly `kM=[0.5,1.0,1.5,2.0]`.
   - Table-I points lie on the existing `dx=0.5M` x-z grid; require exact grid-index selection, not interpolation.
   - This is a schema/provenance pilot only, not paper-level Fig.5/Fig.6 reproduction.

2. **Future dense `Mk` scan to about `4`**
   - Requires a separate production plan, runtime/storage estimate, adaptive convergence policy, and explicit `kM=4` gate.
   - Must not be authorized by this T10f plan.

3. **Future Kirchhoff baseline**
   - Requires a separate T1/T10 convention freeze before implementation.
   - Must cover Eq. (47) convention details, branch choices, `Gamma(1+i gamma)`, Kummer `1F1`, phase conventions, and whether the comparison applies identically to plus/cross packaged-polarization ratios.

## Table-I Points

Include the eight point IDs and coordinates:

| point_id | group | x/M | y/M | z/M | phi |
|---|---|---:|---:|---:|---:|
| `near_axis_x0_z30` | Fig.5 near-axis | 0 | 0 | 30 | 0 |
| `near_axis_x1_z30` | Fig.5 near-axis | 1 | 0 | 30 | 0 |
| `near_axis_x2_z30` | Fig.5 near-axis | 2 | 0 | 30 | 0 |
| `near_axis_x3_z30` | Fig.5 near-axis | 3 | 0 | 30 | 0 |
| `far_axis_x10_z30` | Fig.6 far-axis | 10 | 0 | 30 | 0 |
| `far_axis_x15_z30` | Fig.6 far-axis | 15 | 0 | 30 | 0 |
| `far_axis_x20_z30` | Fig.6 far-axis | 20 | 0 | 30 | 0 |
| `far_axis_x25_z30` | Fig.6 far-axis | 25 | 0 | 30 | 0 |

For each point, derive and record:

- `r = sqrt(x^2 + z^2)`
- `theta = atan2(abs(x), z)`
- `phi = 0`
- paper Table-I `theta_deg`
- paper Table-I `xi_over_xi0`

Use the Table-I values already recorded in `references/notes/t10d_li_hou_zhao_figure_inventory.md`.

## Proposed Read-Only Extraction Schema

Specify a future output location, but do not create it:

- `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/`

Propose saved data files:

- `tablei_four_frequency_amplification_values.npz`
- `tablei_four_frequency_amplification_values.npz.json`

The proposed schema must preserve complex ratios as authoritative:

- `F_plus_complex`
- `F_cross_complex`
- `abs_F_plus`
- `abs_F_cross`
- `arg_F_plus_principal`
- `arg_F_cross_principal`
- `arg_F_plus_unwrapped`
- `arg_F_cross_unwrapped`
- masks for invalid plus/cross ratios and invalid field values
- point metadata
- frequency metadata
- source NPZ paths, sizes, and SHA-256 hashes
- source M4 field SHA provenance if present
- selected grid indices
- explicit `no_interpolation=true`
- explicit `no_solver_rerun=true`
- explicit `no_kirchhoff_baseline=true`
- explicit `not_paper_level_dense_scan=true`

Phase policy:

- Principal phases are in `(-pi, pi]`.
- Unwrap only along increasing `kM` for each point/component separately.
- Do not unwrap across invalid or masked values.
- The four-frequency unwrapped phase is diagnostic because the grid is too sparse for paper-level phase curves.

Mask/NaN policy:

- Invalid ratios must be masked or stored as `NaN`.
- Do not fill, clip, smooth, regularize, or interpolate invalid values.

## Acceptance Gates For A Future T8 Extraction Slice

Define gates that T8 must satisfy if T0 later schedules implementation:

- Exact Table-I grid indices verified in every source NPZ.
- Source NPZ SHA-256 values recorded.
- No solver imports/calls from the extraction/plotting helper.
- No interpolation.
- No new physics conventions.
- Complex arrays preserved.
- Sidecar records scope limits and non-scope.
- No claim of dense Fig.5/Fig.6 reproduction.

## Stop Conditions

Return **GREEN / PLAN READY FOR T7az REVIEW** only if the note separates the three scopes above, records all eight Table-I points, proposes a concrete read-only schema, and keeps dense scan/Kirchhoff/`kM=4` gated.

Return **YELLOW / PLAN REVISION NEEDED** if local artifact metadata is incomplete but the planning boundary is still safe.

Return **RED** if the existing archive does not contain the Table-I grid points, or if any source suggests this plan would silently require interpolation, solver reruns, or new physics conventions.

## Verification Commands

Run read-only checks. Suggested commands:

```bash
test -f references/notes/t10f_fig5_fig6_tablei_extraction_plan.md
find runs/phase5/m5_four_frequency_amplification_artifacts -maxdepth 1 -type f -print | sort
PYTHONPATH=src /opt/homebrew/bin/python3 - <<'PY'
import numpy as np
from pathlib import Path
points = [(0,30),(1,30),(2,30),(3,30),(10,30),(15,30),(20,30),(25,30)]
for p in sorted(Path("runs/phase5/m5_four_frequency_amplification_artifacts").glob("*_amplification.npz")):
    with np.load(p, allow_pickle=True) as data:
        x = data["x"] if "x" in data.files else data["x_values"]
        z = data["z"] if "z" in data.files else data["z_values"]
        missing = []
        for px, pz in points:
            if not np.any(np.isclose(x, px)) or not np.any(np.isclose(z, pz)):
                missing.append((px, pz))
        print(p.name, "missing", missing)
PY
```

If the inspection script needs different key names, adapt it read-only and record the actual keys.

Do not run full pytest unless you modify code, tests, or configs despite the scope.

## Status Update

Update `status.md` with:

- changed files
- files read
- commands run and results
- decision label
- whether the existing archive supports a read-only four-frequency Table-I pilot
- open issues
- exact next action:

```text
你现在是 T7az。请读取并严格执行 docs/prompts/phase5_t7az_fig5_fig6_tablei_plan_review.md。
```
