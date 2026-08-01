# T1 Current Handoff

Last updated: 2026-08-01

Thread role: T1, literature and physics-convention adjudication.

## 2026-08-01 project sync

T1 has no active task, but it is the natural owner of the next convention
gate. Figures 3–7 are numerically generated but not paper-equivalent. Before
any new full-grid calculation, a future T1 task must resolve, from the paper
and first principles, (i) the real-time Eq. (42) to complex
positive-frequency \(h_+,h_\times\) bridge, (ii) incident/total/scattered
field definitions used by Fig.4, and (iii) the exact normalization and
observable in the Fig.5/6 Kirchhoff integral. The previous T1j comparison
baseline is historical and is not sufficient evidence that the current
Kirchhoff curve matches the paper. See `status.md` and the current figure
report under `docs/reports/`.

## 1. Thread Role And Current Status

T1 owns physics conventions and literature-to-project convention bridges.  T1
does not implement solvers, generate production artifacts, or change source
code unless a future prompt explicitly assigns a convention-facing code task.

Current status:

- No active T1 task is pending.
- The latest T1 convention slice, T1j Kirchhoff Eq. (47), is complete and
  accepted downstream as sufficient for later bounded Kirchhoff baseline work.
- `status.md` is the global authority.  As of the latest status, T7bq has
  accepted the Fig.5/Fig.6 review-grid radial gate, and T0's next scheduled
  implementation slice is T8aj conservative review-grid data resume, not a T1
  task.

## 2. Completed Work

- Phase 0 convention freeze:
  - Fourier convention `exp(-i k t)`.
  - Spherical harmonics, spin-weighted harmonics, Wigner-D convention.
  - `A_plus/A_cross/A_L/A_R`.
  - Regge-Wheeler gauge and odd/even master-variable normalization.
  - Strict NP versus project packaged polarization-scalar distinction.
  - `Psi0/Psi4 -> h_plus/h_cross` production bridge policy.
- Q014/Q014 curved production bridge:
  - Production finite-radius polarization uses the incident-frame electric
    tidal projection / Route B packaged bridge, not flat type-N or helicity
    packaging.
  - Li-Hou-Zhao Eq. (35g)-(35h) stars are not same-positive-`k`, same-`m`
    conjugation rules in the project positive-frequency API.
- Q005/M5 transmission-normalization design:
  - Project M5 production quantity is pointwise wave-optics amplification
    `h_lensed/h_unlensed`, not radial horizon transmission/absorption.
  - Denominator is the flat/no-lens production-compatible polarization field
    with the same `exp(-i k t)`, amplitudes, coordinates, and Route B bridge.
- T1j Kirchhoff Eq. (47) convention freeze:
  - Decision: `GREEN / EQ47 COMPARISON BASELINE CONVENTIONS FROZEN`.
  - Eq. (47) is frozen as a scalar/eikonal Kirchhoff comparison baseline only.
  - Main note: `references/notes/kirchhoff_eq47_conventions.md`.

## 3. Incomplete Work

- No current T1 work is required before T8aj.
- Potential future T1/T6 task, only if T0 schedules it: strict `Psi4` Fig.2
  diagnostic convention/API design.
- Future Kirchhoff implementation still needs numerical backend validation for
  complex `Gamma` and `1F1`, but that is T8/T7 implementation-review scope
  unless it exposes a new convention conflict.

## 4. Blocking Issues And Non-Blocking Warnings

Blocking issues:

- None for the current T0/T8aj path.

Non-blocking warnings:

- Do not treat old historical status entries saying Kirchhoff Eq. (47) was
  unfrozen as current.  The current status and T1j note supersede them.
- T10 handoff may be stale relative to T10g/T7be, but `status.md` and the
  relevant notes contain the authoritative trail.
- Kirchhoff Eq. (47) is not a production spin-2 observable; confusing it with
  `F_plus_complex/F_cross_complex` normalization would be a convention error.

## 5. Must-Read Files For Next T1

Read in this order:

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T1_current.md`
5. `docs/prompts/phase5_new_thread_startup_T0_T10.md`
6. `docs/physics_spec.md`
7. `docs/equation_map.md`
8. `references/manifest.md`
9. `references/notes/kirchhoff_eq47_conventions.md`
10. `docs/m5_transmission_normalization.md`
11. `references/notes/q014_weyl_transform_bridge.md`
12. `references/notes/q014_curved_polarization_bridge.md`
13. `references/notes/q013_flat_nolens_polarization_convention.md`
14. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
15. `docs/handoffs/T0_current.md`
16. `docs/handoffs/T7_current.md`
17. `docs/handoffs/T8_current.md`

Only inspect PDFs after local notes/specs are insufficient.

## 6. Frozen Decisions

- Fourier convention is `exp(-i k t)`.
- With this Fourier convention:
  - `exp(-i k r_star)` is ingoing from spatial infinity.
  - `exp(+i k r_star)` is outgoing toward spatial infinity.
- Strict NP scalars and project packaged polarization scalars are distinct
  objects.
- Curved production polarization uses the incident-frame electric tidal
  projection / Route B packaged bridge.
- M5 production amplification uses the flat/no-lens production-compatible
  denominator, not a tiny-`M` Schwarzschild solve, radial `A_in/A_out`, phase
  shifts, horizon flux, or Kirchhoff baseline.
- Kirchhoff Eq. (47) frozen formula:

```text
F_K = exp(pi gamma/2)
      * (-gamma)^(-i gamma)
      * Gamma(1+i gamma)
      * 1F1(-i gamma, 1; -i gamma (xi/xi0)^2)

gamma = -2 M k
xi/xi0 = (1/2) sqrt(r/M) tan(theta)
theta_F = Arg(F_K)
```

- `(-gamma)^(-i gamma)` uses the principal real log of `-gamma=2Mk>0`.
- `Gamma(1+i gamma)` uses the principal complex Euler Gamma branch.
- `1F1` is Kummer `M(a,b,z)`.
- Kirchhoff Eq. (47) is polarization independent and comparison-only.

## 7. Forbidden Actions

Do not do any of the following from T1 without a new T0 prompt and, where
appropriate, a T7 review path:

- Reopen Fourier, harmonic, tetrad, RW/Zerilli, Q005/M5, Q014, Q018, Route B,
  or Kirchhoff Eq. (47) conventions casually.
- Modify `src/`, `tests/`, `configs/`, or `runs/` for a pure convention task.
- Run solvers, scattering jobs, radial production jobs, dense scans, or
  plotting tasks.
- Treat Kirchhoff Eq. (47) as a denominator, mask, correction, calibration, or
  production spin-2 prediction.
- Authorize dense Fig.5/Fig.6 production or paper-style artifacts.
- Claim final journal-grade or pixel-level reproduction from current T1
  convention work.

## 8. Superseded Prompts That Must Not Be Reused As Active Tasks

These prompts are completed historical prompts or no longer the current next
action.  Read them only for provenance if needed:

- `docs/prompts/phase0_t1_physics_conventions.md`
- `docs/prompts/phase5_t1_m5_transmission_normalization.md`
- `docs/prompts/phase5_t1j_kirchhoff_eq47_convention_freeze.md`
- `docs/prompts/phase5_t7aa_m5_normalization_review.md`
- `docs/prompts/phase5_t7bn_kirchhoff_km4_preflight_batch_review.md`

The current startup reference for a replacement T1 is:

- `docs/prompts/phase5_new_thread_startup_T0_T10.md`

## 9. Exact Next Task

For T1 specifically:

```text
No active T1 task. Stand by until T0 assigns a new convention/literature gap.
```

If replacing all threads, use the T1 section of:

```text
docs/prompts/phase5_new_thread_startup_T0_T10.md
```

The current non-T1 project next task is T8aj:

```text
你现在是 T8aj：Fig.5/Fig.6 conservative review-grid data resume 线程。请读取并严格执行 docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md。
```

## 10. Allowed/Forbidden Files, Verification Commands, Definition Of Done

Allowed files for a future pure T1 convention task, if T0 explicitly assigns
one:

- `docs/physics_spec.md`
- `docs/equation_map.md`
- `docs/validation_plan.md` when validation policy changes
- `references/manifest.md`
- `references/notes/*.md`
- `docs/handoffs/T1_current.md`
- `docs/handoffs/archive/T1_<date>_<slug>.md`
- `status.md`

Forbidden unless explicitly assigned:

- `src/`
- `tests/`
- `configs/`
- `runs/`
- production artifacts, plots, fixtures, or dense-scan outputs

Useful verification commands for the current T1 handoff:

```bash
test -f docs/handoffs/T1_current.md
test -f docs/handoffs/archive/T1_2026-07-14_kirchhoff_eq47_pre_handoff_format.md
rg -n "No active T1 task|EQ47 COMPARISON BASELINE CONVENTIONS FROZEN|gamma = -2 M k|Kirchhoff Eq\\. \\(47\\)|Superseded Prompts|Definition Of Done" docs/handoffs/T1_current.md
rg -n "Handoff 硬规则|T\\*_current|Required Content|Update Rule" project.md docs/handoffs/README.md
```

Definition of done for this handoff update:

- The old T1 handoff is archived.
- `docs/handoffs/T1_current.md` contains all required handoff sections from
  `docs/handoffs/README.md`.
- The file states that T1 has no current active task.
- The file preserves the T1j Kirchhoff Eq. (47) GREEN decision and its
  comparison-only guardrails.
- The file points the next T1 to the authoritative must-read files and current
  startup prompt.
