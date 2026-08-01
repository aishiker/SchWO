# T6 Current Handoff

Last updated: 2026-08-01

Thread: T6, metric reconstruction / Weyl / polarization / observable
extraction.

## 2026-08-01 project sync

T6 is the primary implementation owner for the unresolved paper-facing
observable. The strict NP and Route-B packaged outputs remain internally
tested, but Fig.3–6 show that internal consistency is not proof of the
Li–Hou–Zhao plotting convention. A future T6 task must begin with one
low-cost Fig.4 point and explicitly bind the real-time/positive-frequency
reality convention, \(\Psi_2\) contribution, transverse projection, and
incident/total/scattered surface. It may not empirically map
\(F_+\leftarrow F_\times\), add a flat incident field, or launch a full grid
before the point regression passes. Current evidence is summarized in
`status.md` and `docs/reports/li_hou_zhao_figures_3_8_completion_20260801.md`.

## 1. Thread Role And Current Status

T6 owns the finite-radius observable extraction path:

```text
T5 incident coefficients
  -> T4 radial mode values
  -> T6b RW-gauge metric reconstruction
  -> T6c strict NP Weyl/tetrad transform
  -> Route B packaged polarization extraction
  -> h_plus / h_cross
```

T6 also owns the pure M5 pointwise amplification calculation API in
`src/schwgw/scattering/transmission.py`.

Current status:

- M3 Weyl/polarization is closed. Q014 is resolved by T7f independent
  validation and must not be casually reopened.
- T6k API/type hardening is complete: strict NP scalars, electric tidal
  components, and packaged polarization scalars are distinct typed objects.
- T6m M5 pointwise amplification API is complete:
  `compute_pointwise_amplification(...)`,
  `PointwiseAmplificationResult`, and
  `flat_no_lens_baseline_at_point(...)`.
- M5 accepted four-frequency pointwise wave-optics amplification archive is
  closed at the project level after later T8/T7 work. T6 should not redo IO,
  CLI, plotting, or artifact-generation work.
- No active T6 implementation task is currently scheduled. The active global
  workstream is on T8/T7 Fig.5/Fig.6 and Fig.3 rendering/radial gates.

## 2. Completed Work

Major T6 milestones completed:

- T6a: formula/interface audit for reconstruction, Weyl scalars, and
  polarization extraction.
- T6b: RW-gauge metric reconstruction operators.
- T6c: Weyl scalar mode components, Kinnersley/incident tetrads, and strict
  NP transform infrastructure.
- T6d: finite-radius partial-wave polarization extraction.
- Q013: true flat/no-lens oracle and diagnostic split; no tiny-`M`
  Schwarzschild solve as no-lens baseline.
- Q014: strict NP/package bridge repair and Route B production bridge.
- T6k: API/type hardening and Phase 3 closeout documentation.
- T6m: pure M5 pointwise wave-optics amplification API.

Key implemented APIs:

```text
src/schwgw/scattering/partial_wave.py
  compute_polarization(...)
  compute_flat_no_lens_polarization(...)
  compute_flat_no_lens_partial_wave_diagnostic(...)
  direct_cartesian_tt_packaged_weyl(...)
  direct_cartesian_tt_strict_np_weyl(...)

src/schwgw/scattering/weyl.py
  StrictNPScalars
  WeylModeComponents
  weyl_mode_components(...)
  assemble_weyl_scalars(...)
  transform_strict_np_weyl_to_incident_tetrad(...)
  compute_packaged_polarization_scalars(...)

src/schwgw/scattering/observables.py
  ElectricTidalComponents
  PackagedPolarizationScalars
  PolarizationResult
  polarization_from_packaged_scalars(...)
  polarization_from_weyl(...)  # compatibility wrapper for packaged inputs only

src/schwgw/scattering/transmission.py
  PointwiseAmplificationResult
  compute_pointwise_amplification(...)
  flat_no_lens_baseline_at_point(...)
```

Most relevant completed tests:

```text
tests/unit/test_polarization_extraction.py
tests/unit/test_weyl_modes.py
tests/unit/test_transmission.py
tests/physics/test_phase3_validation.py
tests/physics/test_partial_wave_observables.py
```

## 3. Incomplete Work

No incomplete T6 implementation slice is currently open.

Work explicitly outside current T6 ownership unless T0 assigns a new prompt:

- T8 saved-output schema, CLI, plotting, sidecar, and artifact work.
- T4 radial solver/Q018 adapter design and radial thresholds.
- T3 angular/Wigner-D implementation.
- Generic incident direction.
- Fig.2 strict `Psi4` production artifact design.
- Kirchhoff/scalar comparison baseline implementation.
- Radial horizon transmission/absorption observables.

## 4. Blocking Issues And Non-Blocking Warnings

No current T6 blocker.

Non-blocking warnings relevant to future T6 work:

- Q015 remains a radial diagnostic warning, not a Q014 polarization bridge
  problem.
- Q018 and later high-ell radial adapter work are T4/T7-gated; do not treat
  T6 formulas as the cause of radial `required_eval_radius` failures unless a
  new local T6 diagnostic proves it.
- `polarization_from_weyl(...)` has legacy wording but packaged-scalar
  semantics. Prefer `polarization_from_packaged_scalars(...)` in production
  code.
- M5 "transmission" in this project means pointwise wave-optics amplification
  unless explicitly named radial horizon transmission or absorption.

## 5. Must-Read Files For Next T6

Read in this order:

1. `status.md`
2. `docs/handoffs/T6_current.md`
3. `docs/handoffs/README.md`
4. `project.md`
5. `docs/physics_spec.md`
6. `docs/equation_map.md`
7. `docs/phase3_closeout.md`
8. `docs/m5_transmission_normalization.md`
9. `docs/validation_plan.md`
10. `references/notes/q014_curved_polarization_bridge.md`
11. `references/notes/q014_weyl_transform_bridge.md`
12. `references/notes/q013_flat_nolens_polarization_convention.md`
13. `references/notes/q012_high_ell_radial_methods.md`
14. `src/schwgw/scattering/observables.py`
15. `src/schwgw/scattering/weyl.py`
16. `src/schwgw/scattering/partial_wave.py`
17. `src/schwgw/scattering/transmission.py`
18. `tests/unit/test_polarization_extraction.py`
19. `tests/unit/test_weyl_modes.py`
20. `tests/unit/test_transmission.py`
21. Relevant active prompt file assigned by T0/user, if any.

If the task touches saved outputs, CLI, plotting, or archived artifacts, read
the current T8 handoff first and do not assume T6 owns that layer.

## 6. Frozen Decisions

- Fourier convention remains `exp(-i k t)`.
- Background scope remains Schwarzschild GR unless a new T0/T1-gated
  extension prompt says otherwise.
- Strict NP scalars are Weyl tensor tetrad contractions and are not packaged
  polarization scalars.
- Packaged polarization scalars are positive-frequency recovery variables.
- Production polarization uses Route B:

  ```text
  strict NP full quintuple
    -> incident-frame electric tidal projection / packaged scalars
    -> polarization extraction
  ```

- Raw strict `Psi0_NP/Psi4_NP` must not be passed directly to packaged
  extraction.
- Flat/no-lens baseline must use `compute_flat_no_lens_polarization(...)` or
  an exactly equivalent flat contract; no tiny-`M`, no Schwarzschild horizon
  boundary, no radial solve.
- M5 production factor is pointwise wave-optics amplification:

  ```text
  F_plus_complex  = h_plus_lensed / h_plus_unlensed
  F_cross_complex = h_cross_lensed / h_cross_unlensed
  ```

- M5 denominator masks are independent plus/cross/norm masks; invalid ratios
  are NaN, not zero-filled, one-filled, clipped, or floored.
- Radial `A_in/A_out`, phase shifts, Wronskians, horizon flux, and absorption
  are not M5 production amplification factors.
- Existing validation thresholds, `lmax` policy, radial boundary policy, and
  Q018 fail-closed behavior remain unchanged.

## 7. Forbidden Actions

Do not do any of the following from T6 without a new explicit T0/T1/T7 gate:

- Reopen Q014 because of later radial or plotting issues.
- Change Fourier, tetrad, spin-weighted harmonic, Wigner-D, RW/Zerilli, or
  master-variable conventions.
- Modify T4 radial solver behavior, radial thresholds, Q018 adapters, or
  radial boundary policy.
- Treat M5 pointwise amplification as radial horizon transmission,
  absorption, `A_in/A_out`, phase shift, or Kirchhoff/scalar baseline.
- Generate benchmark fixtures, production artifacts, plots, or paper-style
  figures.
- Modify `src/schwgw/io/*`, `src/schwgw/viz/*`, `src/schwgw/cli.py`,
  `configs/*`, or `runs/*` from a T6 task unless the prompt explicitly
  authorizes it.
- Use same-positive-`k`, same-`m` literal conjugation for Li-Hou-Zhao
  Eq. (35g)-(35h) in the positive-frequency production API.
- Promote flat type-N/helicity diagnostics to curved finite-radius production.

## 8. Superseded Prompts Not To Reuse As Current Tasks

These are historical/completed prompts. They may be read for context but
should not be restarted as the current next task:

- `docs/prompts/phase3_t6a_formula_interface_audit.md`
- `docs/prompts/phase3_t6b_metric_reconstruction.md`
- `docs/prompts/phase3_t6c_weyl_tetrad_transform.md`
- `docs/prompts/phase3_t6d_polarization_partial_wave.md`
- `docs/prompts/phase3_blocker_t6_flat_space_nolens_adapter.md`
- `docs/prompts/phase3_t6k_closeout_api_hardening.md`
- `docs/prompts/phase5_t6m_m5_amplification_api.md`

Older Q013/Q014 diagnostic prompts in `docs/prompts/phase3_t6*.md` are also
historical unless T0 explicitly creates a new follow-up prompt.

## 9. Exact Next Task

No T6 task is currently scheduled.

If the user or T0 asks for T6 to resume without a new prompt, first do:

```bash
sed -n '1,220p' status.md
sed -n '1,260p' docs/handoffs/T6_current.md
rg -n "T6|Q014|Q005|PointwiseAmplification|compute_pointwise_amplification|strict NP|Route B" status.md docs/equation_map.md docs/physics_spec.md
```

Then ask whether the intended work is:

1. a T6 API bugfix;
2. a new T6 physics/convention design task;
3. support for a T8/T7 review finding.

For a concrete T6 API bugfix, use TDD: write a failing test first in the
smallest relevant test file, then patch the T6 source file only, run targeted
tests, run full pytest, and update `status.md` plus this handoff.

## 10. Allowed Files, Verification, Definition Of Done

Allowed files for a typical T6 API/observable fix:

```text
src/schwgw/scattering/observables.py
src/schwgw/scattering/weyl.py
src/schwgw/scattering/partial_wave.py
src/schwgw/scattering/transmission.py
src/schwgw/scattering/__init__.py
tests/unit/test_polarization_extraction.py
tests/unit/test_weyl_modes.py
tests/unit/test_transmission.py
tests/physics/test_phase3_validation.py
tests/physics/test_partial_wave_observables.py
docs/equation_map.md
docs/physics_spec.md only for wording/convention clarification
docs/handoffs/T6_current.md
status.md
```

Forbidden by default:

```text
src/schwgw/numerics/*
src/schwgw/angular/*
src/schwgw/io/*
src/schwgw/viz/*
src/schwgw/cli.py
configs/*
runs/*
```

Core verification commands:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_polarization_extraction.py tests/unit/test_weyl_modes.py tests/unit/test_transmission.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_phase3_validation.py tests/physics/test_partial_wave_observables.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "radial_horizon_transmission|radial_absorption|A_in|A_out|solve_radial_mode" src/schwgw/scattering/transmission.py tests/unit/test_transmission.py
```

Definition of done for future T6 work:

- New behavior has a RED/GREEN regression test.
- No frozen convention changes without matching `docs/physics_spec.md`,
  `docs/equation_map.md`, and `status.md` decision entry.
- Route B strict/package separation is preserved.
- M5 baseline and denominator policy remain consistent with
  `docs/m5_transmission_normalization.md`.
- Relevant targeted tests and full pytest pass, or failures are documented
  with exact command output.
- `status.md` and `docs/handoffs/T6_current.md` are updated before handoff.
