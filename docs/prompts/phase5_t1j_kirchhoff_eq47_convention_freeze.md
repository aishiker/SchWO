# Phase 5 T1j Prompt: Kirchhoff Eq. (47) Convention Freeze

You are T1j: literature and physics-convention freeze.

Use Goal mode for this task.

Goal objective:

```text
Freeze the Li-Hou-Zhao Eq. (47) Kirchhoff comparison-baseline conventions needed for later Fig.5/Fig.6 dense-scan plotting. Do not implement Kirchhoff, do not run solvers, do not generate plots or numerical artifacts, and do not modify source code.
```

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T1_current.md`
6. `docs/handoffs/T7_current.md`
7. `docs/handoffs/T10_current.md`
8. `docs/physics_spec.md`
9. `docs/equation_map.md`
10. `docs/numerics.md`
11. `references/manifest.md`
12. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
13. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
14. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
15. `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
16. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`

Before starting, check whether installed plugins/skills are relevant.  If local
notes are insufficient to freeze Eq. (47), inspect `references/papers/` or use
an installed PDF/literature skill.  Do not use web lookup unless local sources
are insufficient; if web lookup is needed, record why in `status.md`.

## Task

Create a convention note and update project convention docs so later T8/T7
threads can implement or compare Kirchhoff without re-opening frozen project
physics conventions.

Freeze, or explicitly mark unresolved, the following:

- compatibility with project Fourier convention `exp(-i k t)`;
- sign and definition of the Kirchhoff parameter `gamma`, especially whether
  the project convention uses `gamma = -2 M k`;
- branch convention for `(-gamma)^(-i gamma)`;
- branch and numerical interpretation of `Gamma(1+i gamma)`;
- Kummer confluent hypergeometric convention for `1F1`;
- exact `1F1` argument, including signs and relation to `xi/xi0`;
- global plotted phase convention `theta_F`;
- whether the Kirchhoff baseline is scalar/eikonal and polarization-independent
  or directly comparable to both packaged `F_plus_complex` and
  `F_cross_complex`;
- metadata label stating Kirchhoff is a comparison baseline only, not the
  production denominator or normalization.

## Allowed Updates

- `references/notes/kirchhoff_eq47_conventions.md`
- `docs/physics_spec.md`
- `docs/equation_map.md`
- `references/manifest.md`
- `status.md`
- `docs/handoffs/T1_current.md`

## Forbidden

- Do not modify `src/`, tests, configs, or `runs/`.
- Do not implement Kirchhoff.
- Do not run solver/scattering/radial/plotting commands.
- Do not change frozen Fourier, harmonic, tetrad, RW/Zerilli, Route B
  packaged-polarization, Q014, Q015, or Q018 conventions.
- Do not authorize dense Fig.5/Fig.6 production.
- Do not claim Li-Hou-Zhao pixel-level or final journal-grade reproduction.

## Required Note Structure

`references/notes/kirchhoff_eq47_conventions.md` must include:

1. **Decision Label**
   - One of:
     - `GREEN / KIRCHHOFF EQ47 CONVENTIONS FROZEN`
     - `YELLOW / KIRCHHOFF EQ47 CONVENTIONS PARTIALLY FROZEN WITH NAMED OPEN ITEMS`
     - `RED / KIRCHHOFF EQ47 CONVENTION CONFLICT`
2. **Source Basis**
   - List exact local notes/PDF pages/files used.
3. **Formula Map**
   - Record the Eq. (47) form as used for this project, without excessive
     quotation.
4. **Branch And Phase Decisions**
   - Explicit decisions for `gamma`, `(-gamma)^(-i gamma)`,
     `Gamma(1+i gamma)`, Kummer `1F1`, and `theta_F`.
5. **Comparison Policy**
   - State how the baseline relates to project
     `F_plus_complex = h_plus_lensed / h_plus_unlensed` and
     `F_cross_complex = h_cross_lensed / h_cross_unlensed`.
6. **Implementation Guardrails**
   - Metadata keys future T8 must write.
   - Actions future T8 must not take.
7. **Open Items**
   - If any item remains unresolved, identify exactly what evidence is missing.

## Required Verification

Run:

```bash
test -f references/notes/kirchhoff_eq47_conventions.md
rg -n "gamma|Gamma|Kummer|1F1|theta_F|comparison baseline|denominator|Fourier|exp\\(-i k t\\)" references/notes/kirchhoff_eq47_conventions.md docs/physics_spec.md docs/equation_map.md references/manifest.md
rg -n "KIRCHHOFF EQ47|T1j|Kirchhoff Eq\\. \\(47\\)|dense Fig\\.5/Fig\\.6" status.md docs/handoffs/T1_current.md
find src tests configs runs -type f -newer references/notes/kirchhoff_eq47_conventions.md -print | sort
```

The final `find` command should return no output.  If it does, stop and explain
why source/test/config/run files changed.

Do not run pytest unless code/tests were changed unexpectedly.

## Final Handoff

Update `status.md` and `docs/handoffs/T1_current.md` with:

- decision label;
- files read;
- changed files;
- commands run;
- verification results;
- frozen decisions;
- open issues;
- exact next T0/T7 action.

If GREEN or YELLOW, say that T4 `kM=4` preflight may proceed independently, but
T8 dense review-grid scanning still requires both T1j and T4v to be reviewed.

