# T1 Current Handoff

Date: 2026-07-09

Thread: T1j Kirchhoff Eq. (47) convention freeze

Decision: GREEN / EQ47 COMPARISON BASELINE CONVENTIONS FROZEN

## Summary

Li-Hou-Zhao Eq. (47) is frozen as a scalar Kirchhoff comparison baseline for
later Fig. 5/Fig. 6 diagnostic overlays. It is not a production spin-2
observable and not the denominator for project pointwise wave-optics
amplification.

## Frozen Decisions

- Fourier compatibility: project `exp(-i k t)` and Li-Hou-Zhao Eq. (46)
  `exp(i k r cos(theta))` are compatible for the `+z` positive-frequency
  incident plane wave. Do not apply an extra same-positive-`k` conjugation.
- `gamma = -2 M k`.
- `(-gamma)^(-i gamma)` uses the principal real log of `-gamma=2Mk>0`.
- `Gamma(1+i gamma)` uses the principal complex Euler gamma function.
- `1F1(-i gamma,1;-i gamma (xi/xi0)^2)` is Kummer's regular confluent
  hypergeometric function `M(a,b,z)`.
- `xi/xi0 = (1/2) sqrt(r/M) tan(theta)`.
- `theta_F = Arg(F_K)` uses the principal argument in `(-pi, pi]`; phase
  unwrapping is display-only metadata.
- The baseline is polarization independent. The same scalar curve may be
  plotted against `F_plus_complex` and `F_cross_complex` only when labeled as
  a Kirchhoff scalar comparison baseline.

## Changed Files

- `references/notes/kirchhoff_eq47_conventions.md`
- `docs/physics_spec.md`
- `docs/equation_map.md`
- `references/manifest.md`
- `status.md`
- `docs/handoffs/T1_current.md`

## Files Read

- `project.md`
- `status.md`
- `docs/codex_instructions.md`
- `docs/handoffs/README.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/T10_current.md`
- `docs/physics_spec.md`
- `docs/equation_map.md`
- `docs/numerics.md`
- `references/manifest.md`
- `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
- `references/notes/t10d_li_hou_zhao_figure_inventory.md`
- `references/notes/t10e_fig4_fig5_reproduction_plan.md`
- `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
- `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
- `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`
- local `pdf` and `verification-before-completion` skill instructions.

Note: `docs/handoffs/T1_current.md` did not exist when this task started; this
file was created as the current T1 handoff.

## Commands And Verification

- Local text/PDF inspections were run with `sed`, `rg`, `pdfinfo`, and
  `pdftotext`.
- Required prompt checks passed:
  - `test -f references/notes/kirchhoff_eq47_conventions.md`
  - required `rg` checks over note/spec/map/manifest/status/handoff.
  - `find src tests configs runs -type f -newer references/notes/kirchhoff_eq47_conventions.md -print | sort` returned no output.
- No pytest was run because this pass did not modify source code or tests.
- No source, tests, configs, or run artifacts were modified.

## Open Items

- No Eq. (47) convention blocker remains.
- Future implementation must still choose and test the numerical backend for
  complex `Gamma` and `1F1`.
- T8 dense Fig. 5/Fig. 6 review-grid scanning remains unauthorized until both
  T1j and T4v are reviewed together by T7bn.

## Exact Next Action

T4v may proceed independently:

```text
你现在是 T4v。请使用 Goal 模式，读取并严格执行 docs/prompts/phase5_t4v_km4_tablei_radial_q018_preflight.md。
```

After T4v completes, run the batch review:

```text
你现在是 T7bn。请读取并严格执行 docs/prompts/phase5_t7bn_kirchhoff_km4_preflight_batch_review.md。
```
