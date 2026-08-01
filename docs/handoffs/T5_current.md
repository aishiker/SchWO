# T5 Current Handoff

Last updated: 2026-08-01

Thread role: T5, incident plane gravitational-wave amplitudes and boundary
coefficients.

## 2026-08-01 project sync

T5 remains inactive, but the next Fig.4 probe must explicitly verify whether
the paper plots incident, scattered, or total fields. The current outer
boundary already contains incident/reflected content, so adding an incident
wave by hand is forbidden without a derivation and regression. Preserve the
accepted incident coefficients and inspect only their downstream
total/scattered use. See `status.md` and the Figure 3–8 report.

## 1. Thread Role And Current Status

T5 owns the incident plane GW public API and the conversion from input
polarizations to partial-wave boundary coefficients:

- `A_plus/A_cross <-> A_L/A_R`
- `A_lm^(+)` / `A_lm^(-)` for default `+z` incidence
- `c_lm^(+)` / `c_lm^(-)`
- flat-space `M -> 0` regular spherical-Bessel master functions

Current status:

- No active T5 task is pending.
- Phase 2 / T5 is complete and has been independently covered by T7 final
  synchronization.
- `status.md` is the global authority.  Current project state is much later
  than Phase 2; T5 remains a stable foundation consumed by T6/T8 and by
  no-lens / flat-space validation paths.
- Generic incident directions are not implemented.  The only supported
  `incident_direction` is `"+z"`.

## 2. Completed Work

Implemented source files:

- `src/schwgw/waves/polarizations.py`
- `src/schwgw/waves/incident.py`
- `src/schwgw/waves/__init__.py`

Implemented public API:

- `linear_to_circular(A_plus, A_cross)`
- `circular_to_linear(A_L, A_R)`
- `sigma_l(ell)`
- `IncidentPlaneGW(k, A_plus, A_cross, incident_direction="+z")`
- `IncidentPlaneGW.A_L`
- `IncidentPlaneGW.A_R`
- `IncidentPlaneGW.A_lm_plus(ell, m)`
- `IncidentPlaneGW.A_lm_even(ell, m)`
- `IncidentPlaneGW.A_lm_minus(ell, m)`
- `IncidentPlaneGW.A_lm_odd(ell, m)`
- `IncidentPlaneGW.c_lm_even(ell, m)`
- `IncidentPlaneGW.c_lm_odd(ell, m)`
- `IncidentPlaneGW.flat_space_master_even(ell, m, r)`
- `IncidentPlaneGW.flat_space_master_odd(ell, m, r)`

Implemented conventions:

```text
A_L = (A_plus + i A_cross)/sqrt(2)
A_R = (A_plus - i A_cross)/sqrt(2)

A_plus  = (A_L + A_R)/sqrt(2)
A_cross = -i (A_L - A_R)/sqrt(2)

sigma_l = (ell-1) ell (ell+1) (ell+2)

A_lm^(±) = i^ell sqrt(2pi(2ell+1)/sigma_l)
           * (A_L delta_{m,-2} ± A_R delta_{m,2})

c_lm^(-) = -[i^(ell+1)/2] A_lm^(-)
c_lm^(+) =  [i^(ell+1)/k] A_lm^(+)

D_lm^(-)(k,r) = -k r A_lm^(-)(k) j_l(k r)
D_lm^(+)(k,r) =  2 r A_lm^(+)(k) j_l(k r)
```

Tests:

- `tests/unit/test_incident_wave.py`
- `tests/physics/test_incident_flat_space.py`

T7 final synchronization confirmed T5 coverage for:

- polarization conversion;
- invalid `k` and invalid direction behavior;
- `m=±2` selection;
- even/odd coefficient signs;
- `c_lm` exponent-binding trap;
- exact flat-space spherical-Bessel formulas;
- large-`kr` asymptotic sanity check.

## 3. Incomplete Work

Not implemented by T5:

- arbitrary incident direction;
- Wigner-D rotation of incident state;
- radial ODE solving;
- Weyl scalars;
- metric reconstruction;
- polarization extraction;
- partial-wave assembly;
- plotting, saved-result IO, CLI, benchmarks, or regression fixtures.

These are intentionally outside the T5 slice and belong to T3/T4/T6/T7/T8/T9
depending on the future prompt.

## 4. Blocking Issues And Non-Blocking Warnings

Blocking issues:

- None for current `+z` incident coefficients.

Non-blocking warnings:

- The `m=±2` selection rule is only valid for default `+z` incidence.  Do not
  reuse it for a generic incident direction without a new Wigner-D rotation
  design and tests.
- The handedness labels `A_L` and `A_R` are convention-sensitive.  The
  algebraic formulas in `docs/physics_spec.md` Sec. 7 are authoritative.
- `flat_space_master_even/odd` are regular flat-space Bessel master functions;
  do not replace them with a tiny-`M` Schwarzschild horizon-ingoing solve.
- Historical Phase 2 prompts are completed provenance, not active tasks.

## 5. Must-Read Files For Next T5

Read in this order:

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T5_current.md`
5. `docs/physics_spec.md`
6. `docs/equation_map.md`
7. `docs/validation_plan.md`
8. `references/manifest.md`
9. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
10. `src/schwgw/waves/polarizations.py`
11. `src/schwgw/waves/incident.py`
12. `src/schwgw/waves/__init__.py`
13. `tests/unit/test_incident_wave.py`
14. `tests/physics/test_incident_flat_space.py`
15. `docs/prompts/phase2_t5_incident_wave_goal.md`
16. `docs/prompts/phase2_t7_physics_tests_goal.md`

If the future task is arbitrary incident direction, additionally read:

1. `src/schwgw/angular/wigner.py`
2. `src/schwgw/angular/spin_weighted.py`
3. `tests/unit/test_wigner.py`
4. `tests/unit/test_spin_weighted_harmonics.py`

## 6. Frozen Decisions

- Fourier convention is `exp(-i k t)`.
- Default incident direction is `+z`.
- T5 supports only radiative modes `ell >= 2` and valid `|m| <= ell`.
- For default `+z` incidence, nonzero incident coefficients occur only for
  `m=-2` and `m=+2`.
- Code name mapping:

```text
A_lm_plus  = A_lm_even = A_lm^(+)
A_lm_minus = A_lm_odd  = A_lm^(-)
c_lm_odd   = c_lm^(-)
c_lm_even  = c_lm^(+)
```

- Parentheses in `c_lm^(-) = -[i^(ell+1)/2] A_lm^(-)` are part of the frozen
  convention.  The exponent-binding test uses `ell=3` because `ell=2` does not
  distinguish the common mistake.
- Flat-space master functions use `scipy.special.spherical_jn` and preserve
  scalar versus array-like `r` behavior.

## 7. Forbidden Actions

Do not do any of the following from T5 without a new T0/T1-approved prompt and
the necessary tests/review path:

- Change `A_plus/A_cross <-> A_L/A_R` signs or normalization.
- Change `A_lm^(±)` signs, `m=±2` selection, `sigma_l`, or `c_lm` phase
  convention.
- Implement arbitrary incident direction by ad hoc formulas.
- Modify `src/schwgw/angular/`, `src/schwgw/numerics/`,
  `src/schwgw/backgrounds/`, `src/schwgw/perturbations/`,
  `src/schwgw/scattering/`, or `src/schwgw/viz/` for a pure T5 task.
- Treat `flat_space_master_even/odd` as a curved Schwarzschild radial
  solution.
- Generate production artifacts, plots, benchmarks, or regression fixtures.
- Claim validation of `kM=4`, R60_K4, larger domains, arbitrary incident
  direction, paper-level reproduction, or final-journal readiness from T5
  alone.

## 8. Superseded Prompts That Must Not Be Reused As Active Tasks

Completed historical prompts/provenance:

- `docs/prompts/phase2_t5_incident_wave_goal.md`
- `docs/prompts/phase2_t7_physics_tests_goal.md`

Read these only to understand the original Phase 2 contract and T7
synchronization criteria.  Do not restart them as active goals unless T0
explicitly schedules a revalidation or repair.

## 9. Exact Next Task

For T5 specifically:

```text
No active T5 task. Stand by until T0 assigns a new incident-wave task.
```

If a future T0 prompt opens arbitrary incident direction support, the first
safe task should be:

```text
Design and test Wigner-D rotation of the incident state for generic
incident_direction without changing the existing +z coefficients.  Add
round-trip/identity tests proving the new path reduces exactly to the current
T5 +z API before exposing any public generic-direction interface.
```

Current non-T5 project next tasks must be taken from `status.md` and the
current T0 handoff, not inferred from T5.

## 10. Allowed/Forbidden Files, Verification Commands, Definition Of Done

Allowed files for a future pure T5 repair or extension:

- `src/schwgw/waves/__init__.py`
- `src/schwgw/waves/polarizations.py`
- `src/schwgw/waves/incident.py`
- `tests/unit/test_incident_wave.py`
- `tests/physics/test_incident_flat_space.py`
- `docs/handoffs/T5_current.md`
- `docs/handoffs/archive/T5_<date>_<slug>.md`
- `status.md`

Conditionally allowed for a future arbitrary-direction T5 prompt:

- `src/schwgw/waves/rotations.py`
- new focused tests under `tests/unit/` or `tests/physics/`

Forbidden unless explicitly assigned:

- `src/schwgw/angular/`
- `src/schwgw/numerics/`
- `src/schwgw/backgrounds/`
- `src/schwgw/perturbations/`
- `src/schwgw/scattering/`
- `src/schwgw/viz/`
- `configs/`
- `runs/`
- benchmark/regression fixture generation

Useful verification commands:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_incident_wave.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_incident_flat_space.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_incident_wave.py tests/physics/test_incident_flat_space.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Useful handoff/documentation checks:

```bash
test -f docs/handoffs/T5_current.md
rg -n "No active T5 task|IncidentPlaneGW|m=±2|arbitrary incident direction|Superseded Prompts|Definition Of Done" docs/handoffs/T5_current.md
rg -n "Handoff 硬规则|T\\*_current|Required Content|Update Rule" project.md docs/handoffs/README.md
```

Definition of done for a future T5 task:

- T5 formulas remain consistent with `docs/physics_spec.md` Sec. 7 and
  `docs/equation_map.md`.
- Focused T5 unit/physics tests pass.
- Any new generic-direction support proves identity reduction to current `+z`
  behavior.
- No forbidden module is modified without explicit prompt authorization.
- `status.md` and this handoff are updated.
