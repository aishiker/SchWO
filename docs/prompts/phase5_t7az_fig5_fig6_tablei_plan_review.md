# Phase 5 T7az Prompt: Fig.5/Fig.6 Table-I Plan Review

You are T7az: independent validation/review for the T10f Fig.5/Fig.6 Table-I extraction plan.

## Mandatory Context

Before doing anything else, check whether installed plugins or skills are relevant. This is a review task; use local project notes and artifact metadata first.

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
- `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
- `docs/prompts/phase5_t10f_fig5_fig6_tablei_extraction_plan.md`
- `runs/phase5/m5_four_frequency_amplification_artifacts/manifest.md`

## Scope

This is a plan-only review. Do not modify `src`, tests, configs, frozen convention docs, result artifacts, fixtures, plots, or `runs/` contents.

You may update only:

- `status.md`

Do not run a solver. Do not generate `.npz`, `.h5`, `.png`, `.pdf`, fixtures, or configs.

## Review Checklist

Verify that T10f:

- Created `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`.
- Changed no code/tests/configs/artifacts except `status.md` and the new note.
- Clearly separates:
  - read-only four-frequency Table-I extraction pilot;
  - future dense `Mk` scan to about `4`;
  - future Kirchhoff baseline convention/implementation.
- Does not authorize `kM=4`, R60_K4, dense Fig.5/Fig.6 scans, Kirchhoff implementation, Appendix D/E curves, strict `Psi4`, arbitrary incident direction, fixtures, or new solver runs.
- Records all eight Table-I points with correct `x,z`, point IDs, group labels, derived `r/theta/phi`, paper `theta_deg`, and paper `xi_over_xi0`.
- Confirms the existing four-frequency M5 archive contains the required x-z grid points exactly, or explicitly marks the plan YELLOW/RED if it does not.
- Requires exact grid-index selection and `no_interpolation=true`.
- Preserves complex `F_plus_complex` and `F_cross_complex` as authoritative.
- Specifies principal and unwrapped phase policy without claiming sparse four-frequency phases are paper-level dense curves.
- Keeps invalid ratios masked/NaN, with no filling, clipping, smoothing, regularization, or interpolation.
- Requires source NPZ SHA-256 provenance and sidecar scope flags.

## Independent Read-Only Checks

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
        print("FILE", p.name, "keys", sorted(data.files))
        x_key = "x" if "x" in data.files else "x_values"
        z_key = "z" if "z" in data.files else "z_values"
        x = data[x_key]
        z = data[z_key]
        missing = []
        for px, pz in points:
            if not np.any(np.isclose(x, px)) or not np.any(np.isclose(z, pz)):
                missing.append((px, pz))
        print("missing", missing)
PY
```

Adapt key names only if needed and record the actual keys. Do not write output files.

Run targeted or full pytest only if T10f changed code/tests/configs despite its scope.

## Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR FIG.5/FIG.6 TABLE-I EXTRACTION PLAN ONLY**
  - The plan is internally consistent, artifact-supported, read-only, and safe for a later T8 implementation prompt.

- **ACCEPT YELLOW / PLAN REVISION NEEDED**
  - The planning boundary is safe, but metadata, point mapping, schema, or provenance needs a correction before T8 can implement extraction.

- **REJECT RED**
  - The plan silently authorizes solver reruns, interpolation, `kM=4`, Kirchhoff implementation, new conventions, unsupported paper-level claims, or uses artifacts that do not contain the required points.

## Status Update

Update `status.md` with:

- files read
- commands run and results
- decision label
- changed files
- whether T0 may schedule T8 read-only four-frequency Table-I extraction
- remaining gates
- exact next action for T0

If GREEN, recommend this exact next action:

```text
T0 may schedule T8ac read-only four-frequency Table-I extraction from the existing M5 archive, followed by T7ba review. Do not schedule dense Mk scan, kM=4, Kirchhoff baseline, or plotting-as-paper-reproduction yet.
```
