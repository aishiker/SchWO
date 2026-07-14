# Equation Map

版本：v0.1-frozen

状态：Phase 0 / T1 convention freeze。`docs/physics_spec.md` v0.1 已冻结核心 physics conventions；本文件记录实现模块到公式来源的映射。

## 1. 职责

本文件是代码模块到物理公式来源的正式映射。它回答三个问题：

1. 某个代码模块实现了哪些物理公式。
2. 这些公式来自哪些文献、notes 或 `docs/physics_spec.md` 小节。
3. 哪些 convention 差异已经被检查，哪些仍是 open issue。

`references/manifest.md` 负责登记文献用途和优先级；`references/notes/` 负责保存 Codex 整理出的公式笔记；本文件负责把实现模块和公式来源连接起来。

## 2. Map Template

```markdown
## path/to/module.py

Status: planned | implemented | tested | frozen

Implements:
- Formula name:
  - Project convention:
  - Source:
  - Notes:
  - Tests:
  - Caveats:
```

## 3. Current Map

## `src/schwgw/backgrounds/schwarzschild.py`

Status: implemented, unit-tested, T1-frozen for formula convention.

Implements:
- Schwarzschild lapse `f(r) = 1 - 2M/r`
  - Project convention: `G = c = 1`, exterior Schwarzschild coordinates.
  - Source: `docs/physics_spec.md` Sec. 2; Li-Hou-Zhao Eq. (1); `references/notes/li_hou_zhao_2025_spin_wave_optics.md`.
  - Notes: Review source confirms standard Schwarzschild exterior notation; no alternate normalization involved.
  - Tests: `tests/unit/test_schwarzschild_background.py`.
  - Caveats: valid for Schwarzschild exterior; do not reuse as generic static-spherical interface.
- Tortoise coordinate `r_star = r + 2M log(r/(2M)-1)`
  - Project convention: real exterior coordinate for `r > 2M`.
  - Source: `docs/physics_spec.md` Sec. 2; Li-Hou-Zhao Eq. (13); `references/notes/li_hou_zhao_2025_spin_wave_optics.md`.
  - Notes: log branch is the exterior real branch. Near-horizon numerical cutoffs are T4 scope.
  - Tests: `tests/unit/test_schwarzschild_background.py`.
  - Caveats: near-horizon numerical use requires explicit cutoff, handled by later T4.
- Derivative `dr_star/dr = 1/f`
  - Project convention: derivative with respect to Schwarzschild areal radius.
  - Source: `docs/physics_spec.md` Sec. 2.
  - Tests: `tests/unit/test_schwarzschild_background.py`.

## `src/schwgw/perturbations/potentials.py`

Status: implemented, unit-tested, T1-frozen for formula convention.

Implements:
- Regge-Wheeler odd-parity potential
  - Project convention: `V_l^(-)(r) = f(r)/r^2 [l(l+1) - 6M/r]`.
  - Source: `docs/physics_spec.md` Sec. 5; Li-Hou-Zhao Eq. (8)-(9); `references/notes/li_hou_zhao_2025_spin_wave_optics.md`; cross-check `references/notes/regge1957.md`.
  - Notes: uses `exp(-i k t)` and the master equation `d^2/dr_star^2 + [k^2 - V]`. Regge-Wheeler 1957 is historical support, not the software normalization source.
  - Tests: `tests/unit/test_rwz_potentials.py`.
  - Caveats: radiative modes require `ell >= 2`.
- Zerilli even-parity potential
  - Project convention: `lambda = (ell-1)(ell+2)/2`, `Lambda = lambda + 3M/r`, formula as in `docs/physics_spec.md` Sec. 5.
  - Source: `docs/physics_spec.md` Sec. 5; Li-Hou-Zhao Eq. (8), (10); `references/notes/li_hou_zhao_2025_spin_wave_optics.md`; cross-check `references/notes/moncrief1974.md` and `references/notes/schwarzschild_perturbations_review.md`.
  - Notes: equivalent published forms may use `mu=(ell-1)(ell+2)=2 lambda`; do not copy those formulas without converting.
  - Tests: `tests/unit/test_rwz_potentials.py`.
  - Caveats: equivalent published forms differ by algebraic rearrangement and master-variable normalization.

## `src/schwgw/waves/incident.py`

Status: implemented, unit/physics-tested, T1-frozen for formula convention.

Implements:
- Linear/circular polarization conversion:
  - Project convention:
    - `A_L = (A_plus + i A_cross)/sqrt(2)`.
    - `A_R = (A_plus - i A_cross)/sqrt(2)`.
    - `A_plus = (A_L + A_R)/sqrt(2)`.
    - `A_cross = -i(A_L - A_R)/sqrt(2)`.
  - Source: `docs/physics_spec.md` Sec. 7; Li-Hou-Zhao Eq. (16)-(17), (22); `references/notes/li_hou_zhao_2025_spin_wave_optics.md`.
  - Tests: `tests/unit/test_incident_wave.py`.
  - Caveats: naming of handedness is convention-sensitive; the algebraic conversion above is authoritative.
- Plane-wave partial-wave amplitudes:
  - Project convention:
    - `sigma_l = (l-1) l (l+1) (l+2)`.
    - `A_lm^(±) = i^l sqrt(2pi(2l+1)/sigma_l) (A_L delta_{m,-2} ± A_R delta_{m,2})`.
    - `c_lm^(-) = -[i^(l+1)/2] A_lm^(-)`.
    - `c_lm^(+) = [i^(l+1)/k] A_lm^(+)`.
  - Source: `docs/physics_spec.md` Sec. 7; Li-Hou-Zhao Eq. (20)-(27); `references/notes/li_hou_zhao_2025_spin_wave_optics.md`.
  - Tests: `tests/unit/test_incident_wave.py`; `tests/physics/test_incident_flat_space.py`.
  - Caveats: `m=±2` rule holds only for incident direction `+z`; generic directions require Wigner-D rotation.

## `src/schwgw/perturbations/rwz.py`

Status: planned, T1-frozen for master-equation convention, not implemented.

Implements:
- RW/Zerilli master equation:
  - Project convention: `[d^2/dr_star^2 + k^2 - V_l^(±)(r)] psi_tilde^(±) = 0`.
  - Source: `docs/physics_spec.md` Sec. 5; Li-Hou-Zhao Eq. (8); `references/notes/li_hou_zhao_2025_spin_wave_optics.md`.
  - Tests: T4 should cover boundary derivative ratios and Wronskian/flux diagnostics.
  - Caveats: no source terms in first-stage vacuum scattering.
- Master-variable normalization:
  - Project convention:
    - `psi_tilde^(-) = -f h_tilde^(B1)/r`.
    - `psi_tilde^(+) = Lambda^(-1) [h_tilde^(T0)/r + f h_tilde^(Rt)/(i k)]`.
  - Source: `docs/physics_spec.md` Sec. 4; Li-Hou-Zhao Eq. (6)-(7); cross-check caveats in `references/notes/moncrief1974.md` and `references/notes/schwarzschild_perturbations_review.md`.
  - Tests: T6/T7 should verify flat-limit reconstruction against Eq. (24)-(27) of the target paper.
  - Caveats: not identical to all Moncrief/Martel-Poisson master functions.

## `src/schwgw/numerics/radial_solver.py`

Status: implemented, unit/physics-tested for low-`ell` outward shooting and
high-`ell` stabilized BVP radial solves; Phase 3 Q012 blocker resolved for
the covered high-barrier diagnostics.

Implements:
- Schwarzschild RW/Zerilli radial ODE in areal radius:
  - Project convention: `f^2 psi'' + f f' psi' + (k^2 - V) psi = 0`, equivalent to `d^2 psi/dr_star^2 + (k^2 - V) psi = 0`.
  - Source: `docs/physics_spec.md` Sec. 5; `docs/numerics.md` Sec. 2.
  - Tests: `tests/unit/test_radial_solver.py`; `tests/physics/test_radial_solver.py`.
  - Caveats: high-barrier modes are routed to the stabilized `r_star` BVP branch rather than the outward unit-horizon shooting branch.
- Horizon ingoing data:
  - Project convention: `psi(r_in)=exp(-i k r_star(r_in))`, `dpsi/dr=(-i k/f) psi`.
  - Source: `docs/physics_spec.md` Sec. 6; `docs/numerics.md` Sec. 3.
  - Tests: `tests/unit/test_radial_solver.py`.
- Outer asymptotic matching:
  - Project convention: `A_in exp(-i k r_star) + A_out exp(+i k r_star)`.
  - Source: `docs/physics_spec.md` Sec. 1.1 and Sec. 6; `docs/numerics.md` Sec. 4.
  - Tests: `tests/unit/test_radial_solver.py`.
- High-barrier BVP normalization:
  - Project convention: public `A_in` still denotes the outer `exp(-i k r_star)` coefficient; in the stabilized branch the internal normalization is unit incoming at infinity, so `A_in ~= 1`.
  - Source: `docs/numerics.md` Sec. 5.1.
  - Tests: `tests/physics/test_radial_solver.py`.
- Wronskian diagnostics:
  - Project convention: `W=f(psi^* dpsi/dr - psi dpsi^*/dr)`.
  - Source: `docs/numerics.md` Sec. 5.
  - Tests: low-`ell` raw-Wronskian tests and high-`ell` stabilized diagnostics in `tests/physics/test_radial_solver.py`.
  - Caveats: for high barriers with unresolved horizon flux, diagnostics use the larger of BVP collocation and boundary residuals rather than cancellation-dominated raw double-precision Wronskian samples.
- Structured radial warning metadata:
  - Project convention: Q015 transition raw-Wronskian cases are recorded as `RadialDiagnosticWarning(code="transition_raw_wronskian_warning", ...)` without relaxing thresholds or changing the effective scalar diagnostics.
  - Source: `docs/numerics.md` Sec. 5.1.
  - Frozen interface:
    - `RadialDiagnosticWarning`
    - `RadialDiagnosticWarning.to_metadata()`
    - `RadialDiagnostics.raw_wronskian_residual`
    - `RadialDiagnostics.expected_flux_scale`
    - `RadialDiagnostics.warnings`
  - Tests: `tests/physics/test_radial_solver.py`.
  - Caveats: `PolarizationResult.diagnostics` remains numeric-only; benchmark/result metadata should serialize warning records separately from scalar maxima.

## `src/schwgw/angular/*`

Status: implemented, unit-tested, T1-frozen for convention.

Implements:
- Scalar spherical harmonics:
  - Project convention: Condon-Shortley phase, `int Y_lm^* Y_l'm' sin(theta)dtheta dphi = delta_ll' delta_mm'`, `Y_l,-m = (-1)^m Y_lm^*`.
  - Source: `docs/physics_spec.md` Sec. 1.2; target paper Appendix A assumes spherical harmonics but does not fully specify software phase; cross-check `references/notes/schwarzschild_perturbations_review.md`.
  - Tests: normalization, conjugation, selected analytic values.
  - Caveats: do not use a library default without wrapper tests.
- Wigner-D:
  - Project convention: `D^l_{m m'}(alpha,beta,gamma) = exp(-i m alpha) d^l_{m m'}(beta) exp(-i m' gamma)`.
  - Source: `docs/physics_spec.md` Sec. 1.2; Li-Hou-Zhao Eq. (39)-(40) for tetrad transformation context.
  - Tests: identity rotation, unitarity, conjugation identities, scalar-harmonic relation.
  - Caveats: active/passive rotation conventions must not be inferred from library names.
- Spin-weighted spherical harmonics:
  - Project convention: `_sY_lm = (-1)^s sqrt((2l+1)/(4pi)) [D^l_{m,-s}(phi,theta,0)]^*`.
  - Source: `docs/physics_spec.md` Sec. 1.2; Li-Hou-Zhao Eq. (34); cross-check review spin-weighted harmonic appendix.
  - Tests: `_0Y_lm = Y_lm`, orthonormality for `s=0,±1,±2`, conjugation relation.
  - Caveats: spin-weight sign conventions are one of the highest-risk sources of global phase errors.
- Tensor-harmonic normalization registry:
  - Project convention: preserve target paper Appendix A tensor labels and `epsilon^(a)` factors separately from unit-sphere scalar harmonic normalization.
  - Source: Li-Hou-Zhao Appendix A; `references/notes/li_hou_zhao_2025_spin_wave_optics.md`.
  - Tests: parity label registry and projection normalization smoke tests.
  - Caveats: target paper projection formulas contain explicit powers of `r`.

## `src/schwgw/perturbations/reconstruction.py`

Status: implemented, unit-tested, T6a-audited for formula/interface freeze.

Implements:
- RW-gauge metric reconstruction operators:
  - Project convention: `h_tilde^{(a)}_{lm} = J_hat_l^{(a)} psi_tilde^(±)`, with all derivatives interpreted as `d/dr`.
  - Source: `docs/physics_spec.md` Sec. 8; Li-Hou-Zhao Eq. (28)-(29); `references/notes/li_hou_zhao_2025_spin_wave_optics.md`; full T6 transcription in `references/notes/phase3_formula_audit.md`.
  - Notes:
    - Odd components: `B1`, `Bt`.
    - Even components: `T0`, `Rt`, `L0`, `tt`.
    - Required radial inputs are only `psi` and `dpsi/dr`; `dpsi/dr_star` can be converted by dividing by `f`.
    - No independent `d2psi/dr_star2` public API is needed for T6b.
  - Frozen interface:
    - `MetricModeComponents`
    - `reconstruct_metric_mode(sector, ell, k, r, psi, dpsi_dr, background)`
  - Tests: `tests/unit/test_metric_reconstruction.py`.
  - Caveats: reconstruction is gauge dependent and is not an observable; formulas are Schwarzschild RW-gauge specific.

## `src/schwgw/scattering/tetrads.py`

Status: implemented, unit-tested, T6a-audited for formula/interface freeze.

Implements:
- Kinnersley and incident-aligned tetrads:
  - Project convention:
    - Kinnersley tetrad `l=(f^-1,1,0,0)`, `n=(1/2)(1,-f,0,0)`, `m=(1/(sqrt(2)r))(0,0,1,i csc theta)`.
    - Incident Cartesian tetrad `lhat=(1/sqrt(2))(1,0,0,1)`, `nhat=(1/sqrt(2))(1,0,0,-1)`, `mhat=(1/sqrt(2))(0,1,i,0)`.
  - Source: `docs/physics_spec.md` Sec. 9; Li-Hou-Zhao Eq. (31), (36)-(40); `references/notes/phase3_formula_audit.md`.
  - Frozen interface:
    - `NullTetrad`
    - `kinnersley_tetrad(background, r, theta)`
    - `incident_cartesian_tetrad()`
    - `tetrad_inner_product(...)`
    - `tetrad_inner_products(...)`
  - Tests: `tests/unit/test_tetrads.py`.
  - Caveats: incident-aligned tetrad is a convention, not a unique local propagation direction for the scattered wave.

## `src/schwgw/scattering/weyl.py`

Status: implemented, unit-tested, Q014-adjudicated for API semantics;
strict-NP transform and flat packaged bridge fixed for Q014 T6g.

Implements:
- Weyl scalar definitions and assembly:
  - Project convention: `weyl_mode_components(...)` and `assemble_weyl_scalars(...)` are intended to compute strict Newman-Penrose Weyl tensor tetrad contractions in the Schwarzschild Kinnersley tetrad. Any incident-tetrad transform is also a strict-NP operation, not a polarization-packaging operation.
  - Source: `docs/physics_spec.md` Sec. 9; Li-Hou-Zhao Eq. (30)-(40); `references/notes/li_hou_zhao_2025_spin_wave_optics.md`; full T6 transcription in `references/notes/phase3_formula_audit.md`; Q014 bridge decision in `references/notes/q014_weyl_transform_bridge.md`.
  - Notes:
    - Spin weights are fixed as `Psi_4: -2`, `Psi_3: -1`, `Psi_2: 0`, `Psi_1: +1`, `Psi_0: +2`.
    - `Z_4`, `Z_3`, and `Z_2` require only `psi` and `dpsi/dr`.
    - Q014 decision: Li-Hou-Zhao Eq. (35g)-(35h) stars must not be read as same-positive-`k`, same-`m` conjugation of stored amplitudes. The consistent bridge involves the full real-field reality relation, the `-k` and `-m` partners, and spin-weighted harmonic conjugation. Until that bridge is derived, lower strict NP scalars must be fixed against direct tensor-contraction tests.
    - Q014 decision: Li-Hou-Zhao Eq. (39)-(40) is a strict-NP tetrad/Riemann transform only. It must not be applied to `Psi0_pack/Psi4_pack`.
    - Q014 T6g status: `transform_strict_np_weyl_to_incident_tetrad(...)` is validated against direct flat tensor contraction for off-axis probes. `transform_weyl_to_incident_tetrad(...)` remains as a compatibility alias.
    - Existing T4 `RadialSolution` is sufficient after rescaling by `c_lm/A_in`.
  - Frozen interface:
    - `WeylModeComponents`
    - `weyl_mode_components(sector, ell, m, k, r, theta, phi, metric_mode, background)`
    - `assemble_weyl_scalars(...)`
    - `transform_strict_np_weyl_to_incident_tetrad(...)`
    - `transform_weyl_to_incident_tetrad(...)`
  - Tests: `tests/unit/test_weyl_modes.py`.
  - Caveats: in curved spacetime only `psi4` is strictly gauge invariant; finite-radius use of all Weyl scalars follows the target-paper prescription. Q014 T6g validates the flat strict-NP transform bridge, but T7d still must rerun curved partial-wave lmax convergence.

## `src/schwgw/scattering/observables.py`

Status: implemented, unit/physics-tested, Q014-adjudicated for packaged-input semantics;
name remains compatibility wording.

Implements:
- `Psi_0`, `Psi_4` to `h_plus`, `h_cross`:
  - Project convention:
    - Inputs are project packaged polarization scalars `Psi0_pack/Psi4_pack`, not one-sided strict NP scalars.
    - `hddot_plus_tilde = Psi4_pack + Psi0_pack`.
    - `hddot_cross_tilde = i(Psi4_pack - Psi0_pack)`.
    - `h_plus_tilde = -(Psi4_pack + Psi0_pack)/k^2`.
    - `h_cross_tilde = -i(Psi4_pack - Psi0_pack)/k^2`.
  - Source: `docs/physics_spec.md` Sec. 9; Li-Hou-Zhao Eq. (41)-(42); Fourier sign from Eq. (2); `references/notes/li_hou_zhao_2025_spin_wave_optics.md`; `references/notes/phase3_formula_audit.md`; `references/notes/q014_weyl_transform_bridge.md`.
  - Frozen interface:
    - `ElectricTidalComponents`
    - `PackagedPolarizationScalars`
    - `PolarizationResult`
    - `package_electric_tidal_components(tidal_components)`
    - `packaged_scalars_to_mapping(packaged_scalars)`
    - `polarization_acceleration_from_packaged_scalars(packaged_scalars)`
    - `polarization_acceleration_from_weyl(psi0_hat, psi4_hat)`
    - `polarization_from_packaged_scalars(k, packaged_scalars)`
    - `polarization_from_weyl(k, psi0_hat, psi4_hat)`
  - Tests: `tests/unit/test_polarization_extraction.py`; `tests/physics/test_partial_wave_observables.py`.
  - Caveats: Eq. (42) is written for real time-domain geodesic-deviation components; the complex-amplitude formulas above are the project storage convention derived from `exp(-i k t)`. Passing strict `Psi0_NP=0`, `Psi4_NP=-k^2(H_plus-iH_cross) exp(ikz)` for a `+z` plane wave to `polarization_from_weyl(...)` is a convention error. `polarization_from_packaged_scalars(...)` is the typed production API. `polarization_from_weyl(...)` remains only as a compatibility wrapper for explicitly packaged scalar inputs.

## `src/schwgw/scattering/partial_wave.py`

Status: implemented, unit/physics-tested, Q014 curved production bridge implemented
in T6j for `compute_polarization(...)`.

Implements:
- Finite-radius partial-wave polarization assembly:
  - Project convention:
    - Loop `ell=2..lmax`, `m=-ell..ell`.
    - Odd/even sectors are weighted by T5 `c_lm^(-)` and `c_lm^(+)`.
    - T4 radial solutions expose the physical outer incoming coefficient `A_in`; each sector mode is rescaled by `scale = c_lm/A_in` before T6b metric reconstruction. Low-barrier solves are unit-horizon-normalized, while high-barrier BVP solves are unit incoming at infinity.
    - Frozen curved production bridge: after metric reconstruction, compute incident-frame electric tidal components
      `E_xx=C(e0,ex,e0,ex)` and `E_xy=C(e0,ex,e0,ey)` from the linearized Weyl/Riemann tensor, package
      `Psi4_pack=-E_xx+iE_xy` and `Psi0_pack=-E_xx-iE_xy`, then call the typed `polarization_from_packaged_scalars(...)` API or the equivalent direct formulas `h_plus=2E_xx/k^2`, `h_cross=2E_xy/k^2`.
    - T6k-hardened implementation routes `strict Kinnersley NP sum -> transform_strict_np_weyl_to_incident_tetrad(...) -> StrictNPScalars.from_mapping(...) -> compute_packaged_polarization_scalars(...) -> polarization_from_packaged_scalars(...)`, so production no longer passes strict-NP `Psi0/Psi4` directly to packaged extraction.
    - Direct two-scalar maps from strict `Psi0_NP/Psi4_NP` to packaged scalars are rejected for curved finite-radius production.
    - Full tensor reconstruction from all five strict NP scalars is conditionally legal only as a tensor-consistency diagnostic or future alternative after the positive-frequency full-tensor bridge is frozen; v0.1 production should use direct metric/tidal projection.
  - Source: `docs/physics_spec.md` Sec. 7 and Sec. 9; Li-Hou-Zhao Eq. (20)-(42); `references/notes/phase3_formula_audit.md`; `references/notes/q014_weyl_transform_bridge.md`; `references/notes/q014_curved_polarization_bridge.md`.
  - Frozen interface:
    - `compute_polarization(background, k, r, theta, phi, A_plus, A_cross, lmax, boundary_config=None)`
    - `compute_flat_no_lens_polarization(k, r, theta, phi, A_plus, A_cross, lmax, q011_z_conjugation="linear")`
    - `compute_flat_no_lens_partial_wave_diagnostic(k, r, theta, phi, A_plus, A_cross, lmax, q011_z_conjugation="linear")`
    - `compute_flat_no_lens_partial_wave_strict_np_weyl(k, r, theta, phi, A_plus, A_cross, lmax, tetrad="incident")`
    - `direct_cartesian_tt_packaged_weyl(k, z, A_plus, A_cross)`
    - `direct_cartesian_tt_strict_np_weyl(k, z, A_plus, A_cross, tetrad=None)`
    - `direct_cartesian_tt_polarization(k, z, A_plus, A_cross)`
    - `direct_cartesian_tt_weyl(k, z, A_plus, A_cross)`
    - `flat_no_lens_expected_polarization(k, r, theta, A_plus, A_cross)`
    - `StrictNPScalars`
    - `compute_packaged_polarization_scalars(strict_np_scalars) -> PackagedPolarizationScalars`
  - Tests: `tests/unit/test_polarization_extraction.py`; `tests/physics/test_partial_wave_observables.py`.
  - Diagnostics:
    - `lmax`
    - `mode_count`
    - `nonzero_coefficient_count`
    - `radial_solve_count`
    - `max_boundary_residual`
    - `max_wronskian_residual`
    - `max_match_condition_number`
    - `flat_no_lens`
    - `q011_conjugation_literal`
  - Caveats: current implementation is for incident direction `+z` only and does not include plotting, transmission-factor extraction, generic incident-direction rotation, or large regression fixtures.
- M=0 no-lens validation adapter:
  - Project convention:
    - The public `compute_flat_no_lens_polarization(...)` oracle is a direct Cartesian TT flat-space curvature calculation. It uses `h_xx=A_plus exp(i k z)`, `h_yy=-A_plus exp(i k z)`, `h_xy=A_cross exp(i k z)` with the frozen `exp(-i k t)` convention, evaluates the linearized Riemann/tidal components in Minkowski space, packages them as `Psi0_pack/Psi4_pack`, and then calls `polarization_from_weyl(...)`.
    - This oracle bypasses spherical harmonics, Wigner-D rotation, RW reconstruction, radial master functions, and `solve_radial_mode`.
    - The older T5 regular spherical-Bessel path is retained as `compute_flat_no_lens_partial_wave_diagnostic(...)`. It feeds `D_lm^(-) = -k r A_lm^(-) j_l(k r)` and `D_lm^(+) = 2 r A_lm^(+) j_l(k r)` with analytic `dD/dr` through T6b reconstruction and the Q014 strict/package bridge.
    - Neither path approximates the no-lens limit with a tiny-`M` horizon-ingoing Schwarzschild solve.
    - `direct_cartesian_tt_packaged_weyl(...)` returns packaged scalars for `polarization_from_weyl(...)`; `direct_cartesian_tt_strict_np_weyl(...)` returns strict tensor-contraction NP scalars. `direct_cartesian_tt_weyl(...)` remains a packaged compatibility alias.
    - The flat type-N completion and helicity-channel packaged bridge used by this diagnostic are allowed only for `M=0` no-lens checks and future far-zone/asymptotic helicity checks. They are not allowed as curved finite-radius production formulas.
    - Li-Hou-Zhao Eq. (35g)-(35h) star is not a same-positive-`k`, same-`m` conjugation rule in the project API; curved production must not depend on that literal interpretation.
  - Source: `docs/physics_spec.md` Sec. 7 and Sec. 9; Li-Hou-Zhao Eq. (24), Eq. (35), Eq. (41)-(42); `references/notes/phase3_formula_audit.md`; `references/notes/q014_weyl_transform_bridge.md`; `references/notes/q014_curved_polarization_bridge.md`.
  - Tests: `tests/physics/test_phase3_validation.py`.
  - Current diagnostic: the direct Cartesian TT oracle recovers input `A_plus/A_cross` with relative error below `1e-10`, and the public `compute_flat_no_lens_polarization(...)` recovery test is active. After Q014 T6g, the diagnostic-only partial-wave flat path recovers the generic probe with relative error `9.551385933171753e-16` at `M=0,k=0.5,r=20,theta=0.4,phi=0,A_plus=0.9+0.2j,A_cross=0.1-0.3j,lmax=40`.

## `src/schwgw/scattering/transmission.py`

Status: implemented in T6m as the pure pointwise amplification calculation
layer; M5 saved-output schema/CLI/plotting remains future T8 scope.

Implements:
- Pointwise wave-optics amplification:
  - Project convention:
    - `F_plus_complex = h_plus_lensed / h_plus_unlensed`.
    - `F_cross_complex = h_cross_lensed / h_cross_unlensed`.
    - These are complex amplitude ratios.  Absolute-value and intensity
      summaries must be explicitly named, e.g. `amplification_plus` or
      `intensity_plus_ratio`.
    - Combined scalar summaries:
      `H_norm=sqrt(|h_plus|^2+|h_cross|^2)`,
      `F_pol_norm=H_norm_lensed/H_norm_unlensed`, and
      `I_pol_ratio=H_norm_lensed^2/H_norm_unlensed^2`.
  - Source: `docs/physics_spec.md` Sec. 10.3; `docs/m5_transmission_normalization.md`.
  - Public API:
    - `PointwiseAmplificationResult`
    - `compute_pointwise_amplification(...)`
    - `flat_no_lens_baseline_at_point(...)`
  - Required baseline:
    - Use the flat/no-lens production-compatible polarization path
      `compute_flat_no_lens_polarization(...)` or a future API with the same
      contract.
    - Same `exp(-i k t)`, same `k`, same `A_plus/A_cross`, same observer
      coordinates, same incident tetrad/polarization convention, and same
      Route B packaged-polarization bridge as the lensed field.
    - Do not use tiny-`M` Schwarzschild solves, horizon boundary conditions,
      radial RW/Zerilli matching, `A_in/A_out`, or phase shifts to generate
      the denominator.
  - Denominator policy:
    - Use independent plus, cross, and norm denominator masks.
    - Store NaN where a denominator mask is false; plus and cross ratios may
      be NaN independently.
    - Store threshold values and mask names in metadata.
  - Tests: `tests/unit/test_transmission.py`; future saved-schema and plotting
    tests described in `docs/validation_plan.md` Sec. 3.5 remain T8/T7 scope.
  - Caveats:
    - This module must not expose radial horizon transmission or absorption
      under the bare name `transmission`.
    - The finite-radius pointwise factor is not an asymptotic scattering
      amplitude or Kirchhoff/scalar baseline.

## `src/schwgw/io/results.py` (M5 saved amplification schema)

Status: implemented in T8p as a saved-output schema for M5 pointwise
amplification.  Existing wave-field `GridResult` readers/writers remain
backward compatible; M5 ratio output uses the focused
`AmplificationGridResult` plus `save_amplification_results(...)` and
`load_amplification_results(...)`.

Implements:
- Saved amplification fields and metadata:
  - Project convention:
    - Arrays: `F_plus_complex`, `F_cross_complex`, `F_pol_norm`,
      `I_pol_ratio`, `valid_ratio_plus_mask`, `valid_ratio_cross_mask`,
      `valid_ratio_norm_mask`.
    - Optional derived arrays may include component amplitude and intensity
      ratios if they are computed from the complex ratios and carry the same
      masks.
    - Metadata must include
      `normalization.kind="pointwise_wave_optics_amplification"`,
      `normalization.version="m5a_t1_v1"`,
      `normalization.baseline="flat_no_lens"`,
      `normalization.baseline_api="compute_flat_no_lens_polarization"`,
      Fourier convention, Route B bridge, denominator thresholds, mask field
      names, and explicit exclusion of radial horizon transmission.
  - Source: `docs/physics_spec.md` Sec. 10.3; `docs/m5_transmission_normalization.md`.
  - CLI smoke: `schwgw compute-amplification LENSED_RESULT --out OUT`
    reads a saved lensed result, evaluates the flat/no-lens baseline at saved
    observer points, calls the T6m pointwise amplification API, and saves the
    M5 ratio fields.
  - Tests: `tests/unit/test_io_results.py` and
    `tests/regression/test_io_cli.py` cover NPZ/HDF5 round trips, complex
    NaNs, masks, normalization metadata, CLI source metadata, and pure-plus
    component masking.
  - Caveats: result writers must not silently recompute the flat baseline
    during plotting.

## `src/schwgw/viz/results.py` (M5 read-only amplification plotting)

Status: implemented in T8q as a read-only visualization layer for saved M5
pointwise amplification maps.

Implements:
- Plotting from saved pointwise amplification fields:
  - Project convention:
    - `plot_amplification_from_result(...)` loads an
      `AmplificationGridResult` with `load_amplification_results(...)` and
      reads only saved scalar/ratio fields, masks, and metadata.
    - CLI smoke path:
      `schwgw plot-amplification AMPLIFICATION_RESULT --quantity F_pol_norm --out OUT`.
    - Required quantities are `F_pol_norm`, `I_pol_ratio`,
      `amplification_plus`, and `amplification_cross`; small derived saved
      views such as component magnitude/phase use the same saved complex
      ratio fields.
    - `F_pol_norm` and `I_pol_ratio` use `valid_ratio_norm_mask`;
      plus-component quantities use `valid_ratio_plus_mask`; cross-component
      quantities use `valid_ratio_cross_mask`.
    - Honor NaN and denominator masks; never interpolate over masked zeros as
      if they were physical finite ratios.
    - Sidecars record `plot_type="pointwise_wave_optics_amplification"`,
      quantity, mask field, source amplification result path, source case/grid
      metadata, normalization/baseline metadata, grid kind, shape, valid and
      invalid counts, output path, requested DPI, and x-z coordinate ranges
      when present.
  - Source: `docs/physics_spec.md` Sec. 10.3; `docs/m5_transmission_normalization.md`; `docs/validation_plan.md` Sec. 3.5.
  - Tests: `tests/unit/test_viz_results.py` and
    `tests/regression/test_plot_cli.py` cover PNG/sidecar output, mask-field
    selection, NaN invalid policy, unsupported quantity errors, CLI smoke, and
    the static import boundary.
  - Caveats: any plot label using "transmission" must identify the quantity as
    pointwise wave-optics amplification, not radial horizon transmission.
    This plotting path must not rerun solvers, recompute the flat/no-lens
    baseline, or recompute M5 ratios.

## Future Kirchhoff Eq. (47) scalar comparison baseline

Status: planned, T1j convention-frozen; not implemented in source code.

Implements:
- Li-Hou-Zhao Kirchhoff comparison factor:
  - Project convention:
    - Fourier compatibility uses `exp(-i k t)`. Li-Hou-Zhao Eq. (46)
      `exp(i k r cos(theta))` matches the project flat `+z`
      positive-frequency plane wave `exp(i k z)`.
    - Frozen formula:
      `F_K = exp(pi gamma/2) (-gamma)^(-i gamma) Gamma(1+i gamma)
      1F1(-i gamma,1;-i gamma (xi/xi0)^2)`.
    - `gamma = -2 M k`.
    - `xi/xi0 = (1/2) sqrt(r/M) tan(theta)`.
    - `(-gamma)^(-i gamma)` uses the principal real log of
      `-gamma=2Mk>0`.
    - `Gamma(1+i gamma)` uses the principal complex Gamma branch.
    - `1F1` is Kummer `M(a,b,z)`.
    - `theta_F = Arg(F_K)` uses the principal complex argument; any unwrapped
      phase is display-only metadata.
  - Source:
    - Li-Hou-Zhao Eq. (45)-(47), Table I, Fig. 5/Fig. 6 captions.
    - `docs/physics_spec.md` Sec. 10.4.
    - `references/notes/kirchhoff_eq47_conventions.md`.
  - Notes:
    - This is a scalar/eikonal, polarization-independent comparison baseline.
    - It may be plotted as the same dashed comparison curve against
      `F_plus_complex` and `F_cross_complex`.
  - Tests:
    - Future T8/T7 scope after T1j and T4v are jointly reviewed by T7bn.
  - Caveats:
    - Do not use this as the denominator for project pointwise amplification.
    - Do not use it to mask, normalize, correct, or calibrate spin-2
      partial-wave results.
    - Do not present it as a production spin-2 prediction.
