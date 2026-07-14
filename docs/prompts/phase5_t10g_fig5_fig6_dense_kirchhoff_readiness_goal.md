# Phase 5 T10g Goal Prompt: Fig.5/Fig.6 Dense Scan And Kirchhoff Readiness

You are T10g: literature/numerics planning support for paper-level Li-Hou-Zhao Fig.5/Fig.6 reproduction readiness.

Use Codex Goal mode for this task.

Goal objective:

```text
Produce a source-grounded, implementation-ready planning note for paper-level Fig.5/Fig.6 reproduction, covering dense Mk scan requirements, kM=4 gate, radial/Q018 risks, Kirchhoff Eq. (47) convention freeze requirements, artifact schema, runtime/storage estimates, and exact next prompts. Do not run solvers, modify src, generate plots, generate fixtures, or implement Kirchhoff.
```

## Required Reads

Read, in order:

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T0_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T8_current.md`
7. `docs/physics_spec.md`
8. `docs/equation_map.md`
9. `docs/numerics.md`
10. `docs/validation_plan.md`
11. `docs/phase5_m5_four_frequency_closeout.md`
12. `docs/phase5_tablei_extraction_closeout.md`
13. `docs/phase5_tablei_reporting_closeout.md` if it exists
14. `references/manifest.md`
15. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
16. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
17. `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
18. `references/notes/q018_spin2_tail_bound.md`
19. `references/notes/q018_scalar_partial_wave_cutoff.md`
20. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`

If a locally installed skill or plugin is appropriate for reading literature/math/numerics, use it. Do not use web lookup unless the local notes and manifest are insufficient; if web lookup is needed, stop first and record why.

## Output

Create:

- `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`

Create or update:

- `status.md`
- `docs/handoffs/T10_current.md`

Do not modify any other files.

## Required Planning Content

The note must clearly distinguish established facts, project conventions, assumptions, and open items.

It must include these sections:

1. **Why T8ad Fig.5/Fig.6 Looks Simple**
   - State that it is only a four-frequency Table-I reporting pilot.
   - Explain that paper-level Fig.5/Fig.6 requires dense `Mk` curves from near zero to about `4`, exact points/dots, phase curves, and Kirchhoff dashed comparison curves.
   - State that no interpolation or visual smoothing may be used to fake dense curves.

2. **Paper Fig.5/Fig.6 Requirements From Local Notes**
   - Table-I points.
   - Frequency range.
   - Exact quantities: complex pointwise wave-optics amplification, magnitude, phase.
   - Plus/cross treatment.
   - Kirchhoff comparison role.

3. **Dense Mk Scan Candidate Design**
   - Propose at least two candidate frequency grids:
     - a conservative review grid;
     - a production-like grid.
   - Include explicit `kM=4` handling.
   - Include adaptive `lmax` policy tied to final adjacent-pair convergence, not merely `lmax≈kr`.
   - Include per-frequency metadata requirements.
   - Include stop conditions for nonconvergence, Q018 warnings, missing masks, or high runtime.

4. **Radial/Q018 And kM=4 Gate**
   - Explain why four-frequency acceptance does not validate `kM=4`.
   - Identify what T4/T7 must preflight before any dense production run.
   - Give a minimal preflight matrix over frequencies, `ell` ranges, sectors, and Table-I radii.
   - State what evidence would be enough for GREEN/YELLOW/RED.

5. **Kirchhoff Eq. (47) Convention Freeze Requirements**
   - List exact conventions that T1/T10 must freeze before implementation:
     - project Fourier sign `exp(-i k t)`;
     - sign of `gamma`;
     - branch of `(-gamma)^(-i gamma)`;
     - branch/implementation of `Gamma(1+i gamma)`;
     - Kummer `1F1` argument and branch;
     - plotted phase convention `theta_F`;
     - whether the baseline is scalar/eikonal only or directly comparable to packaged plus/cross ratios.
   - State that Kirchhoff must be labeled as comparison baseline, not denominator or production normalization.

6. **Artifact Schema And Output Layout**
   - Define a proposed dense scan NPZ/JSON layout.
   - Include source config hash, source code hash policy for non-git workspace, per-frequency convergence metadata, masks, complex ratios, phases, unwrapping segments, and sidecar scope flags.
   - Propose output directories, but do not create them.

7. **Runtime And Storage Estimate**
   - Use current accepted archive sizes, grid counts, and known high-ell behavior to estimate order of magnitude.
   - Distinguish wall-clock uncertainty from storage uncertainty.
   - Provide a recommended staged run plan to avoid wasting time.

8. **Recommended Next Thread Sequence**
   - Give concrete prompt text for:
     - T1: Kirchhoff convention freeze;
     - T4: `kM=4`/dense scan radial preflight;
     - T7: review of T10g plan;
     - later T8 dense pilot only if T7 accepts prerequisites.
   - Make dependencies explicit.

## Forbidden Actions

Do not:

- run `schwgw run`;
- call `compute_polarization`, `run_solver_grid`, `solve_radial`, or `compute_pointwise_amplification`;
- generate NPZ/HDF5/CSV/PNG/PDF artifacts;
- modify `src`, tests, configs, accepted artifacts, plotting artifacts, or `runs/`;
- implement Kirchhoff;
- authorize dense production directly;
- claim the current T8ad PNGs are paper-level Fig.5/Fig.6.

## Stop Conditions

Stop and report RED if:

- local notes are insufficient to identify the Fig.5/Fig.6 requirements and you would need raw PDF/web verification;
- you discover a convention conflict that invalidates current Route B/M5 definitions;
- the plan would require changing frozen Fourier/harmonic/tetrad/polarization conventions;
- you cannot separate dense scan planning from Kirchhoff implementation;
- you would need to run solvers or create artifacts to finish the plan.

## Verification Commands

Run:

```bash
test -f references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md
rg -n "T8ad|four-frequency|dense|kM=4|Kirchhoff|Q018|Gamma|Kummer|1F1|theta_F" references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md
rg -n "T10g|dense|Kirchhoff|kM=4" status.md docs/handoffs/T10_current.md
```

Do not run full pytest; no code/test changes are allowed.

## Final Status Label

Use one of:

- `GREEN / FIG5-FIG6 DENSE-KIRCHHOFF READINESS PLAN READY FOR T7be REVIEW`
- `YELLOW / PLAN READY WITH EXPLICIT OPEN RISKS`
- `RED / PLAN BLOCKED`

If GREEN or YELLOW, final handoff must say:

```text
你现在是 T7be。请读取并严格执行 docs/prompts/phase5_t7be_fig5_fig6_dense_kirchhoff_plan_review.md。
```
