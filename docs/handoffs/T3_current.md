# T3 Current Handoff

Last updated: 2026-08-01

Thread role: T3, angular basis and rotations.

## 2026-08-01 project sync

T3 remains complete and inactive. The current paper-facing mismatch has not
been localized to the accepted harmonic/Wigner basis. Do not alter angular
sign or phase conventions speculatively. A future change requires a
single-point paper-facing regression that distinguishes an angular error from
the downstream polarization/field-definition boundaries listed in
`status.md`.

## 1. Thread Role And Current Status

T3 owns the angular basis layer:

- scalar spherical harmonics `Y_lm`;
- spin-weighted spherical harmonics `_sY_lm`;
- Wigner-D wrapper and project small-d convention;
- tensor-harmonic label/parity/RW-gauge registry checks.

Current status:

- No active T3 task is pending.
- T3h high-`ell` Wigner-D hardening is complete.
- Q016 is resolved and independently revalidated by T7h through the R60_K1
  fixture path.
- `status.md` is the global authority.  As of the current project state, the
  next active path is not T3; T0/T8/T7 scheduling around Fig.5/Fig.6 review-grid
  data is current.

## 2. Completed Work

- Phase 1 angular foundation:
  - `scalar_sph_harm(ell, m, theta, phi)`;
  - `wigner_D(ell, m, mp, alpha, beta, gamma)`;
  - `spin_weighted_sph_harm(s, ell, m, theta, phi)`;
  - `tensor_harmonic_labels()`;
  - `tensor_harmonic_parity(label)`;
  - `rw_gauge_radiative_labels(parity=None)`;
  - `is_rw_gauge_radiative_label(label)`.
- Unit coverage for:
  - low-order scalar harmonic values;
  - scalar conjugation identity and quadrature normalization;
  - Wigner-D identity rotation, `ell=0`, unitarity, scalar relation;
  - spin-zero relation, representative spin-weighted orthonormality, and
    conjugation identity;
  - tensor-harmonic frozen labels, parity split, and RW-gauge radiative labels.
- T3h / Q016 hardening:
  - root cause: old Wigner small-d finite-sum code converted large factorial
    products to float and overflowed near `ell=60`;
  - rejected alternative: direct log-domain summation avoided overflow but was
    too cancellation-sensitive in high-`ell` oscillatory regions;
  - accepted algorithm: Jacobi-polynomial small-d closed form with `gammaln`
    normalization, preserving the established project wrapper index order;
  - high-`ell` tests now cover finite checks for `ell=60,72,120`, boundary
    angles `beta=0,pi`, high-`ell` spin-zero relation, and high-`ell`
    spin-weighted conjugation.
- T7h revalidation:
  - finite high-`ell` smoke for `ell=60,72`;
  - R60_K1 adaptive sweep reached `lmax=108` without Wigner overflow;
  - R60_K1 fixture path confirmed Q016 is no longer the blocker.

## 3. Incomplete Work

- Generic/arbitrary incident direction is not implemented.
- Incident-direction Wigner-D rotation of `m=±2` incoming states remains future
  work.  The current T5 implementation is still `+z` incidence only.
- Full tensor harmonics are not implemented in T3; current tensor support is a
  normalization/label/parity registry only.
- Spin-weighted spheroidal harmonics, Kerr/Teukolsky angular bases, and any
  non-Schwarzschild angular generalization are outside the current project
  implementation.
- No current benchmark or plotting task belongs to T3.

## 4. Blocking Issues And Non-Blocking Warnings

Blocking issues:

- None for T3.

Non-blocking warnings:

- The project Wigner small-d wrapper uses an established index order that is
  guarded by downstream Phase 3 flat partial-wave diagnostics.  Do not change
  it to a library's apparent default without a full convention review.
- The T3h Jacobi implementation deliberately preserves the previous wrapper
  index order even though an alternate order may appear attractive from a
  scalar-limit derivation.  A T3h experiment with altered index order made
  angular unit tests pass but broke `tests/physics/test_phase3_validation.py`.
- Q016 is resolved for `ell=60,72,120` finite checks and the R60_K1 path; this
  does not by itself authorize arbitrary larger-`ell` claims, R60_K4, `kM=4`,
  or dense production scans.
- Generic incident direction remains a convention-sensitive extension because
  active/passive rotation, index order, and phase conventions must stay
  compatible with `docs/physics_spec.md`.

## 5. Must-Read Files For Next T3

Read in this order:

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T3_current.md`
5. `docs/prompts/phase5_new_thread_startup_T0_T10.md`
6. `docs/physics_spec.md`
7. `docs/equation_map.md`
8. `docs/validation_plan.md`
9. `src/schwgw/angular/wigner.py`
10. `src/schwgw/angular/spin_weighted.py`
11. `src/schwgw/angular/scalar_harmonics.py`
12. `src/schwgw/angular/tensor_harmonics.py`
13. `src/schwgw/angular/__init__.py`
14. `tests/unit/test_wigner.py`
15. `tests/unit/test_spin_weighted_harmonics.py`
16. `tests/unit/test_scalar_harmonics.py`
17. `tests/unit/test_tensor_harmonics.py`
18. `tests/physics/test_phase3_validation.py`
19. `docs/prompts/phase3_t3h_high_ell_wigner.md`
20. `docs/prompts/phase3_t7h_fixture_after_wigner.md`
21. `docs/handoffs/T0_current.md`
22. `docs/handoffs/T7_current.md`
23. `docs/handoffs/T8_current.md`

Only inspect older prompts for provenance unless T0 explicitly assigns them.

## 6. Frozen Decisions

- Scalar spherical harmonics use the frozen project convention in
  `docs/physics_spec.md` Sec. 1.2:

```text
Y_lm(theta,phi)
  = (-1)^m sqrt((2l+1)/(4pi) * (l-m)!/(l+m)!)
    P_l^m(cos theta) exp(i m phi)
```

- Wigner-D convention remains:

```text
D^l_{m m'}(alpha,beta,gamma)
  = exp(-i m alpha) d^l_{m m'}(beta) exp(-i m' gamma)
```

- Spin-weighted spherical harmonics remain:

```text
_sY_lm(theta,phi)
  = (-1)^s sqrt((2l+1)/(4pi)) [D^l_{m,-s}(phi,theta,0)]^*
```

- `_0Y_lm = Y_lm` remains a required convention check.
- The current Wigner small-d numerical implementation uses a Jacobi-polynomial
  closed form plus `gammaln` normalization to avoid high-`ell` factorial
  overflow.
- The project wrapper's established small-d index order must remain unchanged
  unless T0/T1 explicitly reopen the convention and T7 reviews downstream
  physics tests.
- Tensor-harmonic labels and parity split follow `docs/physics_spec.md` Sec. 3:

```text
labels: {tt, Rt, L0, T0, Et, E1, Bt, B1, E2, B2}
even:   {tt, Rt, L0, T0, Et, E1, E2}
odd:    {Bt, B1, B2}
RW gauge radiative:
  odd:  {Bt, B1}
  even: {tt, Rt, L0, T0}
```

## 7. Forbidden Actions

Do not do any of the following from T3 without a new T0 prompt and appropriate
review path:

- Change scalar harmonic, Wigner-D, spin-weighted harmonic, tensor-label, or
  parity conventions.
- Replace the current Wigner-D convention with an external library default
  without wrapper tests proving all frozen identities and downstream Phase 3
  diagnostics.
- Modify `src/schwgw/numerics/`, radial solver behavior, Q018 adapters, T6
  Weyl/polarization logic, plotting, CLI, saved artifacts, or regression
  fixtures for a pure T3 task.
- Generate R60/R60_K2/R60_K4 artifacts, Fig.3/Fig.4/Fig.5/Fig.6 plots, dense
  scans, Kirchhoff baselines, or paper-style artifacts.
- Use high-`ell` finite checks as proof of arbitrary production convergence.
- Reuse T3h as an active task; it is complete.

## 8. Superseded Prompts That Must Not Be Reused As Active Tasks

Completed historical prompts:

- `docs/prompts/phase1_t3_angular_goal.md`
- `docs/prompts/phase3_t3h_high_ell_wigner.md`
- `docs/prompts/phase3_t7h_fixture_after_wigner.md`

Related non-T3 prompts that should not be used to start T3:

- `docs/prompts/phase4_t8_smoke_plot_cli.md` is superseded by the later
  data-output-first Phase 4 path.
- Any T8/T7 plotting or artifact prompt is not a T3 task unless T0 explicitly
  routes an angular bug back to T3.

The current startup reference for a replacement T3 is:

- `docs/prompts/phase5_new_thread_startup_T0_T10.md`

## 9. Exact Next Task

For T3 specifically:

```text
No active T3 task. Stand by until T0 assigns arbitrary incident direction,
angular-regression, or Wigner-D/spin-weighted harmonic work.
```

If replacing all threads, use the T3 section of:

```text
docs/prompts/phase5_new_thread_startup_T0_T10.md
```

The current non-T3 project next task in the latest handoff/startup flow is T8aj:

```text
你现在是 T8aj：Fig.5/Fig.6 conservative review-grid data resume 线程。请读取并严格执行 docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md。
```

## 10. Allowed/Forbidden Files, Verification Commands, Definition Of Done

Allowed files for a future T3 angular task, if T0 explicitly assigns one:

- `src/schwgw/angular/__init__.py`
- `src/schwgw/angular/scalar_harmonics.py`
- `src/schwgw/angular/spin_weighted.py`
- `src/schwgw/angular/tensor_harmonics.py`
- `src/schwgw/angular/wigner.py`
- `tests/unit/test_scalar_harmonics.py`
- `tests/unit/test_spin_weighted_harmonics.py`
- `tests/unit/test_tensor_harmonics.py`
- `tests/unit/test_wigner.py`
- narrowly relevant physics tests when the prompt explicitly requires them,
  usually `tests/physics/test_phase3_validation.py`
- `docs/handoffs/T3_current.md`
- `docs/handoffs/archive/T3_<date>_<slug>.md`
- `status.md`

Forbidden unless explicitly assigned:

- `src/schwgw/numerics/`
- `src/schwgw/scattering/`
- `src/schwgw/perturbations/`
- `src/schwgw/waves/`
- `src/schwgw/viz/`
- `configs/`
- `runs/`
- `tests/regression/fixtures/`
- production artifacts, plots, dense scans, or benchmark data

Useful verification commands for current T3 state:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_wigner.py tests/unit/test_spin_weighted_harmonics.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_scalar_harmonics.py tests/unit/test_tensor_harmonics.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_phase3_validation.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Useful handoff verification commands:

```bash
test -f docs/handoffs/T3_current.md
rg -n "No active T3 task|Q016|Jacobi|Wigner-D|arbitrary incident direction|Superseded Prompts|Definition Of Done" docs/handoffs/T3_current.md
rg -n "Handoff 硬规则|T\\*_current|Required Content|Update Rule" project.md docs/handoffs/README.md
```

Definition of done for this handoff update:

- `docs/handoffs/T3_current.md` exists.
- It contains all required handoff sections from `docs/handoffs/README.md`.
- It records T3h/Q016 as complete and revalidated by T7h.
- It states that T3 has no active task.
- It points future T3 work to the authoritative must-read files and current
  startup prompt.
- It forbids casual convention changes and non-angular artifact/solver work.
