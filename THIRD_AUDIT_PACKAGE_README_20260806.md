# SchWO third-audit package — 2026-08-06

This package is prepared for an independent third audit of the repairs and
recalculations triggered by `audits/SchWO_second_audit_20260803.md`.

## Read first

1. `audits/SchWO_second_audit_20260803.md`
2. `audits/SchWO_second_audit_response_20260803.md`
3. `docs/handoffs/T0_current.md`
4. `status.md`

The current verdict is **not** strict Li-paper reproduction GREEN.  The
production Jost/r-out/frame repairs and the latest Fig.5/6 full recomputation
are complete, but scientific-equivalence boundaries remain YELLOW.

## Authoritative new numerical evidence

- `runs/phase5/paper_figures/second_audit_refinement_20260803_v2/`
- `runs/phase5/paper_figures/fig2_jost_rout_full_20260803/`
- `runs/phase5/paper_figures/fig2_jost_rout_production_20260803_py314_v2/`
- `runs/phase5/paper_figures/fig4_k2_full_shell_audit_20260803_py314/`
- `runs/phase5/paper_figures/fig4_k2_jost_rout_static_20260803_py314/`
- `runs/phase5/paper_figures/fig4_k2_jost_rout_li_20260803_py314/`
- `runs/phase5/paper_figures/fig4_k2_jost_rout_static_n2049_l240_20260803_py314/`
- `runs/phase5/paper_figures/fig4_k2_jost_rout_li_n2049_l240_20260803_py314/`
- `runs/phase5/paper_figures/fig56_jost_rout_static_20260803_py314/`
- `runs/phase5/paper_figures/fig56_jost_rout_li_20260803_py314/`
- `runs/phase5/paper_figures/fig8_direct_mst_jost_rout_20260803_py314/`
- `runs/phase5/paper_figures/bhpt_mst_benchmark_20260803_v4/`

All paper-facing computations listed above were produced with exact CPython
3.14.6 where applicable.  Failed, superseded, Python-3.10, and incomplete
recalculation roots are intentionally excluded.

## Latest figures and comparison images

- Latest Fig.5/6 static-frame render:
  `runs/phase5/paper_figures/fig56_jost_rout_render_static_20260806_py314/`
- Latest Fig.5/6 Li-literal-frame render:
  `runs/phase5/paper_figures/fig56_jost_rout_render_li_20260806_py314/`
- Published-raster comparisons for both frames:
  `runs/phase5/paper_figures/fig56_jost_rout_comparison_*_20260806_py314/`
- The Aug-02 audited figure/render baseline and paper-reference page crops:
  `runs/phase5/paper_figures/audit_repairs_20260802/`
- Additional Fig.1–3 contextual renders are included under their named
  `runs/phase5/paper_figures/` directories.

The Aug-02 baseline images predate the final Jost/r-out Fig.5/6 recomputation;
they are included only for historical and raster-comparison context.  The
Aug-06 Fig.5/6 directories are authoritative for the latest Fig.5/6 result.

## Important unresolved boundaries

1. Fig.4 `kM=2` has been fully audited through `ell=240`, two observer
   frames, three outer radii, four `lmax` checkpoints and four selected
   angles.  It remains YELLOW because the maximum checkpoint relative delta
   is about `0.4032263561`, despite small r-out uncertainty.  This is a
   diagnosed high-ell/conditioning problem, not an unstarted calculation.
2. The external BHPT benchmark independently solves the odd Regge-Wheeler
   sector.  Its even values are obtained through the exact
   Chandrasekhar/Starobinsky parity relation; the package does not claim an
   algebraically independent even-sector MST radial solve.
3. The latest full Fig.5/6 amplitudes are YELLOW-GREEN, but their phases
   remain YELLOW.  Removing a fitted global phase offset does not eliminate
   the residual.
4. Fig.8 retains `strict_paper_reproduction_claim=false`.

## Reproducibility material

The package includes the complete current `src/`, `scripts/`, `tests/`, and
`configs/` trees, the project configuration, relevant scientific documents,
the target paper, and a generated `SHA256SUMS.txt` covering every packaged
file except the checksum file itself.
