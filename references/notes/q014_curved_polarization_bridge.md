# Q014 curved strict-NP -> packaged polarization bridge

Date: 2026-07-05

Scope: finite-radius Schwarzschild scattered field, incident-aligned tetrad, and the bridge from strict Newman-Penrose (NP) Weyl scalars to the project packaged polarization scalars consumed by `polarization_from_weyl(...)`.

This note is a convention-support note for T1/T6/T7. It does not change `src/` or tests.

## Executive conclusion

For the curved finite-radius production path, the least ambiguous bridge is not

```text
strict incident-tetrad Psi0_NP/Psi4_NP -> polarization_from_weyl(...)
```

but the electric-tidal projection

```text
metric / Weyl tensor in the incident observer frame
  -> E_xx = C(e0, ex, e0, ex), E_xy = C(e0, ex, e0, ey)
  -> Psi4_pack = -E_xx + i E_xy
     Psi0_pack = -E_xx - i E_xy
  -> h_plus = 2 E_xx / k^2, h_cross = 2 E_xy / k^2 .
```

Here `Psi0_pack/Psi4_pack` are project packaging variables for positive-frequency polarization recovery. They are not strict NP scalars in general. Li-Hou-Zhao Eq. (39)-(40) should remain a strict-NP tetrad transform only.

The helicity-channel rule used by the current flat diagnostic is useful as an `M=0` and asymptotic-helicity diagnostic, but I do not find enough support in Li-Hou-Zhao to promote it to a finite-radius curved production bridge. The paper explicitly notes that the scattered-wave propagation direction is not uniquely defined at finite radius; this is exactly the regime where a local type-N/helicity completion becomes convention-dependent.

## Sources read

- `docs/physics_spec.md`, especially the frozen separation between strict NP scalars and project packaged scalars.
- `docs/equation_map.md`, especially the Q014 notes for `partial_wave.py`, `weyl.py`, and `observables.py`.
- `docs/numerics.md`, especially the finite-radius partial-wave scope.
- `references/notes/q014_weyl_transform_bridge.md`
- `references/notes/q013_flat_nolens_polarization_convention.md`
- `references/notes/phase3_formula_audit.md`
- `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
- `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`, especially Eq. (30), Eq. (34)-(42), and Appendix D.
- `src/schwgw/scattering/partial_wave.py`
- `src/schwgw/scattering/weyl.py`
- `src/schwgw/scattering/observables.py`

## Established results

1. Strict NP scalars are Weyl tensor contractions.

   With the project convention,

   ```text
   Psi0_NP = -C(l, m, l, m),
   Psi1_NP = -C(l, n, l, m),
   Psi2_NP = -C(l, m, mbar, n),
   Psi3_NP = -C(l, n, mbar, n),
   Psi4_NP = -C(n, mbar, n, mbar).
   ```

   These are geometric/tetrad quantities. They should be transformed by strict tensor/tetrad rules such as Li-Hou-Zhao Eq. (39)-(40) or the project's validated tensor-contraction matrix.

2. Project `Psi0_pack/Psi4_pack` are positive-frequency polarization packaging variables, not strict NP scalars.

   The project extraction convention is

   ```text
   h_plus  = -(Psi4_pack + Psi0_pack) / k^2,
   h_cross = -i (Psi4_pack - Psi0_pack) / k^2.
   ```

   Equivalently, in the incident observer frame,

   ```text
   Psi4_pack = -E_xx + i E_xy,
   Psi0_pack = -E_xx - i E_xy,
   E_AB = C(e0, eA, e0, eB).
   ```

   This gives

   ```text
   h_plus  = 2 E_xx / k^2,
   h_cross = 2 E_xy / k^2.
   ```

   Under the flat project oracle, `E_xx = (k^2/2) H_plus exp(ikz)` and `E_xy = (k^2/2) H_cross exp(ikz)`, so the formula recovers the stored complex amplitudes.

3. A `+z` flat TT plane wave in the strict incident NP tetrad has one-sided strict radiative content.

   With `lhat` aligned with `+z`, the strict NP convention gives

   ```text
   Psi0_NP = Psi1_NP = Psi2_NP = Psi3_NP = 0,
   Psi4_NP = -k^2 (H_plus - i H_cross) exp(ikz).
   ```

   Therefore strict `Psi4_NP` is not the same object as project `Psi4_pack`; feeding it directly to the packaged extraction loses the strict/package distinction.

4. Li-Hou-Zhao's finite-radius output is tied to geodesic deviation.

   Eq. (41)-(42) express observed apparent polarizations through the Riemann/Weyl tidal response in the chosen tetrad. The paper states that the scattered wavefront is distorted and a unique propagation direction is not available at finite radius; they choose the first null leg aligned with the incident wave at future infinity. That choice is a measurement convention, not a proof that the local field is type N.

5. Li-Hou-Zhao Appendix D is asymptotic-helicity information.

   Appendix D gives far-zone reflected-wave amplitudes and an even/odd phase-shift matrix. The diagonal terms are parity-even, while parity-odd terms can mix the two circular polarization channels. This is valuable for asymptotic phase-shift or helicity validation, but it is not a finite-radius tidal projection formula.

## Project convention choices

- Keep `weyl_mode_components(...)`, `assemble_weyl_scalars(...)`, and `transform_strict_np_weyl_to_incident_tetrad(...)` as strict-NP APIs.
- Treat `polarization_from_weyl(...)` as a packaged-scalar API despite its current name. A future rename such as `polarization_from_packaged_weyl(...)` would reduce convention drift.
- Do not pass strict incident-tetrad `Psi0_NP/Psi4_NP` directly to `polarization_from_weyl(...)`.
- Define production finite-radius polarization through the incident-frame electric tidal components `E_xx` and `E_xy`.
- Keep the flat type-N completion and helicity packaging as diagnostics, not as a curved production bridge.

## Derivation assumptions

- Vacuum perturbation, so the relevant curvature for geodesic deviation is the linearized Weyl/Riemann tidal tensor.
- Observer tetrad is the incident-aligned tetrad used by the project:

  ```text
  e0 = (lhat + nhat) / sqrt(2),
  ez = (lhat - nhat) / sqrt(2),
  ex = (mhat + mbarhat) / sqrt(2),
  ey = (mhat - mbarhat) / (i sqrt(2)).
  ```

- The displayed `h_plus/h_cross` are apparent finite-radius polarizations in that frame, not asymptotic radiation-zone spin-weight amplitudes.
- The project works with positive-frequency complex amplitudes; full real-field reconstruction requires the negative-frequency partner and the `m -> -m` harmonic conjugation relation.

## Candidate bridge formulas

### A. Strict NP scalars -> packaged scalars

There are two different versions of this route.

#### A0. Direct two-scalar identification

Rejected formula class:

```text
Psi4_pack = a Psi4_NP + b Psi0_NP,
Psi0_pack = c Psi4_NP + d Psi0_NP
```

with fixed constants or a flat-derived factor.

Reason for rejection:

- It confuses strict NP contractions with positive-frequency packaging variables.
- It can reproduce selected flat diagnostics only after adding extra helicity or type-N assumptions.
- It has no support as a finite-radius Schwarzschild formula, where `Psi1_NP`, `Psi2_NP`, and `Psi3_NP` are not guaranteed to vanish in the incident frame.
- T6i already found that two convergent candidates give different `h_plus/h_cross`; lmax convergence alone cannot select this map.

#### A1. Full tensor reconstruction from all five strict NP scalars

Conditionally legal but not recommended as the first production implementation.

One may reconstruct the Weyl tensor from the full strict NP quintuple in a fixed tetrad and then compute

```text
E_xx = C(e0, ex, e0, ex),
E_xy = C(e0, ex, e0, ey),
Psi4_pack = -E_xx + i E_xy,
Psi0_pack = -E_xx - i E_xy.
```

This is mathematically just the tidal-tensor route in disguise. It is acceptable only if the full complex Weyl tensor and the positive-frequency reality convention are unambiguously represented. It should not be implemented as a shortcut using only strict `Psi0_NP/Psi4_NP`.

Risk:

- Current project data flow assembles strict mode scalars from Li-Hou-Zhao Eq. (35), where `Z1/Z0` involve starred upper components. Until the `(-k,-m)` reality bridge and tensor-basis phases are frozen, the full strict quintuple may not be a trustworthy complete positive-frequency Weyl tensor.

### B. Direct reconstructed metric / tidal tensor projection

Recommended production route.

Compute the incident-frame electric tidal block from the reconstructed metric or from explicitly reconstructed Weyl/Riemann tensor components:

```text
E_xx = C(e0, ex, e0, ex),
E_xy = C(e0, ex, e0, ey).
```

Then package only for the existing extraction API:

```text
Psi4_pack = -E_xx + i E_xy,
Psi0_pack = -E_xx - i E_xy,
h_plus  = -(Psi4_pack + Psi0_pack) / k^2 = 2 E_xx / k^2,
h_cross = -i (Psi4_pack - Psi0_pack) / k^2 = 2 E_xy / k^2.
```

Advantages:

- It matches Li-Hou-Zhao Eq. (41)-(42) as a geodesic-deviation/tidal measurement.
- It does not require interpreting strict `Psi0_NP/Psi4_NP` as packaged scalars.
- It remains meaningful at finite radius when local propagation direction is ambiguous.
- It naturally includes non-radiative/apparent finite-radius effects in the same incident observer frame.

Implementation consequence:

- T6j should either compute `E_xx/E_xy` directly from reconstructed metric/tensor-harmonic contributions, or add an explicit `strict_np_to_electric_tidal(...)` routine that reconstructs the tensor from all five strict NP scalars and is tested against direct tensor contraction.
- The public production path should call `polarization_from_weyl(...)` only after this packaging step, or bypass it with the equivalent `h_plus/h_cross` formulas.

### C. Helicity-channel packaging rule

Flat diagnostic rule:

```text
right-helicity channel -> Psi4_pack,
left-helicity channel  -> Psi0_pack,
```

up to the project's flat normalization factors.

Asymptotic support:

- Li-Hou-Zhao Appendix D expresses the far reflected field through circular polarization amplitudes and phase shifts.
- Even-parity and odd-parity phase shifts enter differently; parity-odd terms can mix the two circular channels.

Reason not to use as finite-radius production bridge:

- It is naturally an asymptotic scattering-amplitude statement, not a local finite-radius tidal measurement.
- At finite radius the field is not generally type N in the incident frame.
- The local propagation direction of the scattered wave is not unique, so helicity assignment is frame/convention dependent.
- Odd/even phase shifts can mix/reverse helicity asymptotically; importing that rule locally would require a separate derivation of the finite-radius spin basis and radial phase convention.

Allowed use:

- `M=0` flat no-lens diagnostic.
- Future far-zone helicity or phase-shift validation.
- A non-production diagnostic comparing asymptotic Appendix D behavior at large `r`.

## Li-Hou-Zhao Eq. (35g)-(35h) star convention

Eq. (35g)-(35h) should not be implemented as same-positive-`k`, same-`m` complex conjugation.

The relevant spin-weighted harmonic identity is

```text
[_sY_lm(theta, phi)]^* = (-1)^(s+m) _{-s}Y_l,-m(theta, phi).
```

For a real time-domain field expanded as positive and negative frequency modes, a schematic reality bridge has the form

```text
amplitude_s(l, m, -k)
  ~ phase(l, m, s, tensor basis) * amplitude_-s(l, -m, +k)^* .
```

The exact phase is not only the spin-weighted harmonic phase. It can also include tensor-harmonic basis conventions, parity-sector phases, and Li-Hou-Zhao's definitions of `Y_j` and `S_j` in Appendix A/B. Therefore the star in Eq. (35g)-(35h) should be treated as a full real-field bridge involving `(-k, -m)` until that phase is explicitly derived.

Practical consequence:

- Do not use Eq. (35g)-(35h) to manufacture positive-frequency lower strict scalars by same-`k`, same-`m` conjugation.
- Do not use the no-star linearized version either unless it passes direct tensor-contraction tests.
- If T6 needs lower strict NP scalars, derive them by direct tensor contraction from reconstructed metric components or freeze the full `(-k,-m)` bridge first.

## Why T6h flat type-N completion is only an M=0 diagnostic

The T6h completion enforces that a flat `+z` plane wave is type N in the incident tetrad:

```text
Psi0_NP = Psi1_NP = Psi2_NP = Psi3_NP = 0,
Psi4_NP nonzero.
```

This is correct for the flat no-lens oracle and for checking the partial-wave assembly against a known type-N plane wave. It should not be generalized to curved finite-radius fields because:

- Schwarzschild scattering creates a superposition of directions in the incident observer frame.
- Near-field and finite-radius tidal components need not satisfy type-N algebraic conditions.
- The scattered wave's propagation direction is not unique at finite radius in Li-Hou-Zhao's own discussion.
- Imposing type-N completion would erase or mispackage legitimate `Psi1/Psi2/Psi3` content and would hide convention errors rather than solve them.

## Rejected options

1. Feed strict incident `Psi0_NP/Psi4_NP` directly to `polarization_from_weyl(...)`.

   Rejected because the function consumes packaged scalars by project convention.

2. Promote the flat helicity packaging candidate to production because it converges with `lmax`.

   Rejected because another non-equivalent bridge also converges; convergence tests cannot adjudicate a convention bridge.

3. Apply the flat type-N completion to curved scattered fields.

   Rejected because finite-radius curved fields are not guaranteed to be type N in the incident tetrad.

4. Literal same-`k`, same-`m` conjugation for Li-Hou-Zhao Eq. (35g)-(35h).

   Rejected because the star belongs to the real-field relation involving negative frequency, `m -> -m`, and spin/tensor-basis phases.

## Recommendation to T1

Freeze Route B as the production convention:

```text
finite-radius packaged polarization scalars are defined by incident-frame electric tidal projections,
not by strict one-sided NP scalars.
```

Recommended wording for the frozen convention:

```text
At finite radius, compute project packaged scalars from the electric part of the linearized Weyl/Riemann tensor in the incident observer frame:
Psi4_pack = -C(e0, ex, e0, ex) + i C(e0, ex, e0, ey),
Psi0_pack = -C(e0, ex, e0, ex) - i C(e0, ex, e0, ey).
Strict NP scalars may be used only after reconstructing the full tensor and projecting these electric components; strict Psi0_NP/Psi4_NP themselves are not packaged scalars.
```

Also freeze that the helicity-channel bridge is diagnostic/asymptotic unless a new derivation proves a finite-radius local rule.

## Minimal formulas T6j should implement if adjudicated

Minimum production bridge:

```text
e0 = (lhat + nhat) / sqrt(2)
ex = (mhat + mbarhat) / sqrt(2)
ey = (mhat - mbarhat) / (i sqrt(2))

E_xx = C(e0, ex, e0, ex)
E_xy = C(e0, ex, e0, ey)

Psi4_pack = -E_xx + i E_xy
Psi0_pack = -E_xx - i E_xy

h_plus  = 2 E_xx / k^2
h_cross = 2 E_xy / k^2
```

Minimum API guard:

- Add or rename a function so the production path says `compute_packaged_polarization_scalars(...)` or equivalent.
- Assert or test that this function does not pass strict `Psi0_NP/Psi4_NP` directly to packaged extraction.
- Keep `transform_strict_np_weyl_to_incident_tetrad(...)` strict-only.

Minimum tests for T6/T7:

- Flat direct TT pure plus: `h_plus` recovers input and `h_cross` is zero.
- Flat direct TT pure cross: `h_cross` recovers input and fixes the sign of `E_xy`.
- Flat circular/helicity cases: verify the packaged pair recovers the project `A_plus/A_cross`, not a one-sided strict NP scalar.
- Curved path: compare direct metric/tidal projection against any full-Weyl-tensor reconstruction from strict NP scalars at several off-axis points. This is a tensor-consistency test, not a helicity-convergence test.
- Large-`r` optional diagnostic: compare asymptotic helicity trends with Appendix D phase-shift expectations, but keep it separate from finite-radius production validation.

## Questions for Li-Hou-Zhao authors if needed

1. In Eq. (42), are `hat{Psi}_0` and `hat{Psi}_4` intended as real time-domain NP scalars after adding the `-k` sector, or as positive-frequency amplitudes stored at fixed `k>0`?
2. In numerical implementation of Eq. (35g)-(35h), does the star map `Z4(l,m,k)` to a `(-k,-m)` coefficient with spin-weighted harmonic conjugation, or is another tensor-basis phase convention being used?
3. Are Eq. (39)-(40) intended only as strict NP tetrad transformations, or do they also include a polarization packaging convention not written explicitly in the paper?
4. For the finite-radius plots, were `h_plus/h_cross` computed from direct geodesic-deviation tidal components, from strict NP `Psi0/Psi4`, or from a helicity-channel reconstruction?
5. Is Appendix D's helicity mixing matrix intended only for asymptotic reflected spherical waves, or is there an unpublished finite-radius local helicity packaging rule?

## Open issue

The literature and local notes are sufficient to reject strict-mixed production extraction and flat type-N promotion. They are not sufficient to freeze a finite-radius helicity-channel packaging rule. If T1 wants a helicity production bridge instead of Route B, the missing derivation is the finite-radius mapping from parity-separated RW/Zerilli amplitudes to incident-frame positive-frequency `Psi0_pack/Psi4_pack`, including odd/even phase shifts, `m -> -m`, and tensor-basis phases.
