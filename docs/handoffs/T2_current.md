# T2 Current Handoff

Last updated: 2026-08-01

Thread role: T2, Schwarzschild background and RW/Zerilli foundation.

## 2026-08-01 project sync

T2 remains complete and inactive. The current Fig.3–7 discrepancies occur
downstream of the accepted Schwarzschild/RWZ foundation; no evidence supports
changing the background or RW/Zerilli potentials. Any future paper-facing
probe must preserve this layer byte-for-byte unless an isolated regression
demonstrates otherwise. Current global state is in `status.md`.

## 1. Thread Role And Current Status

T2 owns the basic Schwarzschild background API and the RW/Zerilli foundation
API used by later radial, reconstruction, observable, and visualization
threads.

Current status:

- T2 foundation is complete.
- There is no active T2 implementation task.
- `status.md` is the global authority.  As of the current project state, the
  project is in Phase 5 and T4/T7 have already accepted later radial-gate
  work.  T2 should not resume early Phase 1 implementation unless T0 assigns a
  specific T2 formula/API bug or extension-interface task.

## 2. Completed Work

Implemented and stabilized:

- `SchwarzschildBackground`
  - `M > 0` validation.
  - `horizon_radius = 2M`.
  - `f(r) = 1 - 2M/r`.
  - `df_dr(r) = 2M/r^2`.
  - `drstar_dr(r) = 1/f(r)`.
  - `r_star(r) = r + 2M log(r/(2M)-1)` for `r > 2M`.
  - `r_from_r_star(r_star)` using the principal real exterior Lambert-W
    branch.
  - scalar input returns a Python scalar; array-like input returns a NumPy
    array.
- RW/Zerilli potentials:
  - `lambda_parameter(ell) = (ell-1)(ell+2)/2`.
  - `regge_wheeler_potential(ell, r, bg)` and public alias `V_RW`.
  - `zerilli_potential(ell, r, bg)` and public alias `V_Zerilli`.
  - `ell < 2` rejects explicitly.
  - potentials require exterior `r > 2M`.
- Sector enum:
  - `Sector.ODD.value == "odd"`.
  - `Sector.EVEN.value == "even"`.
  - package import exposes `Sector`.

Primary files:

- `src/schwgw/backgrounds/base.py`
- `src/schwgw/backgrounds/schwarzschild.py`
- `src/schwgw/backgrounds/__init__.py`
- `src/schwgw/perturbations/potentials.py`
- `src/schwgw/perturbations/sectors.py`
- `src/schwgw/perturbations/__init__.py`
- `tests/unit/test_schwarzschild_background.py`
- `tests/unit/test_rwz_potentials.py`
- `tests/unit/test_sectors.py`

## 3. Incomplete Work

No incomplete T2 foundation work is known.

Work that is not T2 and must remain outside this thread unless T0 explicitly
reassigns it:

- radial ODE/matching and Q018 policy: T4;
- incident plane-wave coefficients: T5;
- metric reconstruction, Weyl/tetrad transform, polarization assembly: T6;
- validation and regression gate review: T7;
- saved output, CLI, visualization, production artifacts: T8;
- non-Schwarzschild extension-interface design: T9.

## 4. Blocking Issues And Non-Blocking Warnings

Blocking issues:

- None for T2.

Non-blocking warnings:

- `r_from_r_star` is implemented for the exterior real branch.  Do not reinterpret
  it as an interior, complex, or alternative-branch inverse without a new
  convention review.
- `V_RW` and `V_Zerilli` are formula-layer functions.  Do not add radial RHS,
  ODE integration, matching, phase shifts, or boundary conditions to
  `potentials.py`.
- Later Phase 5 radial/Q018 adapters depend on T2 potentials as frozen inputs.
  Do not change T2 formulas to fix a downstream high-ell radial issue.
- Equivalent literature formulas may use different master-variable
  normalizations.  Project code follows `docs/physics_spec.md`, not Moncrief or
  review-paper variables directly.

## 5. Must-Read Files For Next T2

Read in this order:

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T2_current.md`
5. `docs/prompts/phase5_new_thread_startup_T0_T10.md`
6. `docs/physics_spec.md`
7. `docs/equation_map.md`
8. `docs/architecture.md`
9. `docs/validation_plan.md`
10. `references/manifest.md`
11. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
12. `references/notes/regge1957.md`
13. `references/notes/moncrief1974.md`
14. `references/notes/schwarzschild_perturbations_review.md`
15. `src/schwgw/backgrounds/`
16. `src/schwgw/perturbations/`
17. `tests/unit/test_schwarzschild_background.py`
18. `tests/unit/test_rwz_potentials.py`
19. `tests/unit/test_sectors.py`

Only inspect PDFs after local specs and notes are insufficient.

## 6. Frozen Decisions

- Units: `G = c = 1`; default project mass scale uses `M`.
- Schwarzschild exterior coordinates use `r > 2M`.
- Tortoise coordinate:

```text
r_star = r + 2M log(r/(2M)-1)
dr_star/dr = 1/f(r)
```

- Inverse tortoise uses the principal real exterior Lambert-W branch.
- Odd Regge-Wheeler potential:

```text
V_l^(-)(r) = f(r)/r^2 * [l(l+1) - 6M/r]
```

- Even Zerilli potential:

```text
lambda = (l-1)(l+2)/2
Lambda = lambda + 3M/r
V_l^(+)(r) = f(r)/r^2 * Lambda^(-2) * [
  2 lambda^2(lambda+1)
  + 6 lambda^2(M/r)
  + 18 lambda(M/r)^2
  + 18(M/r)^3
]
```

- Radiative RW/Zerilli modes require `ell >= 2`.
- Project master-variable normalization follows the target-paper normalization
  frozen in `docs/physics_spec.md`; do not silently switch to Moncrief,
  Martel-Poisson, or review-paper normalizations.
- Sector values are string-stable public API: `"odd"` and `"even"`.

## 7. Forbidden Actions

Do not do any of the following from T2 without a new T0 prompt and a clear
review path:

- Reopen or alter frozen Fourier, harmonic, tetrad, RW/Zerilli, Route B, Q018,
  or Kirchhoff conventions.
- Modify `src/schwgw/angular/`, `src/schwgw/waves/`,
  `src/schwgw/numerics/`, `src/schwgw/scattering/`, `src/schwgw/viz/`,
  production configs, or `runs/` artifacts.
- Add radial ODE solver logic, matching coefficients, incident coefficients,
  metric reconstruction, Weyl scalars, polarization extraction, plotting, or
  saved-output logic to T2 files.
- Change RW/Zerilli formulas to make downstream radial tests pass.
- Relax validation thresholds or numerical tolerances without updating
  `docs/validation_plan.md` and obtaining the appropriate review.
- Treat scalar/Kirchhoff/eikonal comparison results as validation of spin-2
  RW/Zerilli formula changes.

## 8. Superseded Prompts That Must Not Be Reused As Active Tasks

Completed historical prompt:

- `docs/prompts/phase1_t2_background_rwz_goal.md`

Read it only for provenance.  Do not restart it as an active implementation
goal unless T0 explicitly requests a T2 refactor or bugfix.

Current replacement-thread startup reference:

- `docs/prompts/phase5_new_thread_startup_T0_T10.md`

## 9. Exact Next Task

For T2 specifically:

```text
No active T2 task. Stand by until T0 assigns a background, RW/Zerilli formula,
Sector enum, or extension-interface issue.
```

If replacing all threads, use the T2 section of:

```text
docs/prompts/phase5_new_thread_startup_T0_T10.md
```

If T0 assigns a future T2 bugfix, start with:

```text
读取 project.md、status.md、docs/handoffs/README.md、docs/handoffs/T2_current.md、docs/physics_spec.md、docs/equation_map.md、相关 src/schwgw/backgrounds 或 src/schwgw/perturbations 文件和对应 tests。先写或更新失败测试，再做最小实现；不得修改 T3-T8 范围文件；最后运行 T2 定向测试、必要的 full pytest，并更新 status.md 与 T2 handoff。
```

## 10. Allowed/Forbidden Files, Verification Commands, Definition Of Done

Allowed files for a future T2 bugfix, if explicitly assigned:

- `src/schwgw/backgrounds/base.py`
- `src/schwgw/backgrounds/schwarzschild.py`
- `src/schwgw/backgrounds/__init__.py`
- `src/schwgw/perturbations/potentials.py`
- `src/schwgw/perturbations/sectors.py`
- `src/schwgw/perturbations/__init__.py`
- `tests/unit/test_schwarzschild_background.py`
- `tests/unit/test_rwz_potentials.py`
- `tests/unit/test_sectors.py`
- `docs/handoffs/T2_current.md`
- `status.md`

Forbidden unless a later T0 prompt explicitly changes ownership:

- `src/schwgw/angular/`
- `src/schwgw/waves/`
- `src/schwgw/numerics/`
- `src/schwgw/scattering/`
- `src/schwgw/viz/`
- `configs/`
- `runs/`
- production artifacts and regression fixtures

Useful verification commands:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_schwarzschild_background.py tests/unit/test_rwz_potentials.py tests/unit/test_sectors.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "No active T2 task|SchwarzschildBackground|r_from_r_star|V_RW|V_Zerilli|Sector|Superseded Prompts|Definition Of Done" docs/handoffs/T2_current.md
```

Definition of done for this handoff:

- `docs/handoffs/T2_current.md` exists.
- It contains all required sections from `docs/handoffs/README.md`.
- It states that T2 foundation is complete and has no active task.
- It records the stable public API and frozen formula decisions.
- It identifies superseded T2 prompts and forbidden actions.
- It points a replacement T2 to the current startup prompt and authoritative
  specs/status files.
