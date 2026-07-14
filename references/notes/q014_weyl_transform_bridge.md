# Q014 Weyl transform bridge decision

Date: 2026-07-05

Scope:
- Adjudicate the bridge between Li-Hou-Zhao Eq. (35), Eq. (39), Eq. (42),
  strict Newman-Penrose Weyl scalars, and the project's positive-frequency
  polarization packaging.
- No `src/` production code was modified in this adjudication.

## Sources checked

- `docs/physics_spec.md`
- `docs/equation_map.md`
- `docs/validation_plan.md`
- `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
- `references/notes/phase3_formula_audit.md`
- `references/notes/q013_flat_nolens_polarization_convention.md`
- `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`, especially Eq. (30), Eq. (34)-(35), Eq. (39)-(42)
- Read-only code:
  - `src/schwgw/scattering/weyl.py`
  - `src/schwgw/scattering/partial_wave.py`
  - `src/schwgw/angular/spin_weighted.py`
  - `src/schwgw/angular/wigner.py`

## 1. Two objects must be kept distinct

### Strict NP scalars

Strict Newman-Penrose scalars are the tetrad contractions defined by
Li-Hou-Zhao Eq. (30):

```text
Psi0_NP = -C(l,m,l,m)
Psi1_NP = -C(l,n,l,m)
Psi2_NP = -C(l,m,n,mbar)
Psi3_NP = -C(l,n,n,mbar)
Psi4_NP = -C(n,mbar,n,mbar)
```

These are tetrad components of the Weyl tensor. They transform under a
tetrad change as tensor components. Li-Hou-Zhao Eq. (39)-(40) belongs to
this category.

### Project packaged scalars

The project stores positive-frequency `k>0` complex amplitudes and wants a
linear recovery of `h_plus_tilde` and `h_cross_tilde`. For that purpose it
uses packaged quantities:

```text
hddot_plus_tilde  = Psi4_pack + Psi0_pack
hddot_cross_tilde = i (Psi4_pack - Psi0_pack)

h_plus_tilde  = -(Psi4_pack + Psi0_pack)/k^2
h_cross_tilde = -i(Psi4_pack - Psi0_pack)/k^2
```

`Psi0_pack/Psi4_pack` are not strict NP scalars in general. They are a
positive-frequency geodesic-deviation packaging of tidal information.

Consequence:
- Strict NP scalars may be transformed by Eq. (39)-(40), after the rotation
  convention is fixed.
- Packaged scalars must not be transformed by Eq. (39)-(40), because they
  are not Weyl tensor tetrad components.

## 2. Direct flat +z TT derivation

Use signature `(-,+,+,+)` and the project positive-frequency convention:

```text
h_ij(t,z) = H_ij exp(i k z) exp(-i k t)
```

with TT amplitudes:

```text
h_xx =  H_plus  exp(i k z) exp(-i k t)
h_yy = -H_plus  exp(i k z) exp(-i k t)
h_xy =  H_cross exp(i k z) exp(-i k t)
```

The incident Cartesian tetrad is:

```text
lhat = (1/sqrt(2)) (1,0,0, 1)
nhat = (1/sqrt(2)) (1,0,0,-1)
mhat = (1/sqrt(2)) (0,1,i,0)
```

The phase covector is proportional to `(-k,0,0,k)`, so:

```text
k_mu lhat^mu = 0
k_mu nhat^mu != 0
```

The direct linearized Riemann contraction therefore gives, for a +z wave:

```text
Psi0_NP = 0
Psi1_NP = 0
Psi2_NP = 0
Psi3_NP = 0
Psi4_NP = -k^2 (H_plus - i H_cross) exp(i k z)
```

This agrees with the standard NP direction diagnostic: with `lhat` aligned
with the +z propagation direction, a +z TT wave is carried by strict
`Psi4_NP`, not strict `Psi0_NP`.

The electric tidal projections for the same wave are:

```text
R_txtx = (k^2/2) H_plus  exp(i k z)
R_txty = (k^2/2) H_cross exp(i k z)
```

The project packaging that recovers `H_plus/H_cross` linearly is:

```text
Psi4_pack = -R_txtx + i R_txty
          = -(k^2/2)(H_plus - i H_cross) exp(i k z)

Psi0_pack = -R_txtx - i R_txty
          = -(k^2/2)(H_plus + i H_cross) exp(i k z)
```

Then:

```text
-(Psi4_pack + Psi0_pack)/k^2  = H_plus exp(i k z)
-i(Psi4_pack - Psi0_pack)/k^2 = H_cross exp(i k z)
```

Thus `Psi4_pack` equals one half of the strict outgoing `Psi4_NP` for the
helicity combination it shares, and `Psi0_pack` is not the strict NP
`Psi0_NP` of the +z wave. It is the companion package needed for linear
positive-frequency plus/cross recovery.

## 3. Eq. (35g)-(35h) star audit

Li-Hou-Zhao Eq. (35g)-(35h) write:

```text
Z1^(sector) = (2/f) [Z3^(sector)]^*
Z0^(sector) = (2/f)^2 [Z4^(sector)]^*
```

This star must not be interpreted as "take the same positive-k, same-m
stored amplitude and complex conjugate it" inside a linear positive-frequency
API. That interpretation is antilinear in `A_plus/A_cross` and conflicts
with the project's stored-amplitude convention.

The star is instead tied to the real field / full Fourier reality relation.
For the angular factors:

```text
[_sY_lm(theta,phi)]^* = (-1)^(s+m) _{-s}Y_{l,-m}(theta,phi)
```

Therefore a conjugated upper-spin contribution changes spin weight and
also couples the mode label `m` to `-m`. In a full real Fourier expansion
it also couples positive and negative frequencies through the reality
condition schematically:

```text
h_tilde(-k,l,-m) ~ h_tilde(k,l,m)^*
```

with basis-dependent phase factors. Consequently, Eq. (35g)-(35h) cannot be
implemented as a local same-`k`, same-`m` conjugation rule for strict
positive-frequency coefficients. A strict positive-frequency implementation
must either:

1. compute `Psi0_NP/Psi1_NP` by direct tensor contraction from the
   reconstructed metric, or
2. derive the explicit `(-k,-m)` reality bridge including spin-weighted
   harmonic conjugation and tensor-basis phases, then document it before
   implementation.

The local diagnostics already show that toggling same-mode literal
conjugation is not sufficient: both current linear and literal-conjugate
variants remain O(1) wrong in the flat partial-wave diagnostic.

## 4. Eq. (39)-(40) audit

Li-Hou-Zhao Eq. (39)-(40) are a tetrad/Riemann component transformation.
They should be applied only to strict NP scalars.

They should not be applied to `Psi0_pack/Psi4_pack`, because packaged
scalars are not a rank-4 Weyl tensor component set.

Under the project Wigner-D convention:

```text
D^l_{m m'}(alpha,beta,gamma)
  = exp(-i m alpha) d^l_{m m'}(beta) exp(-i m' gamma)
```

and:

```text
_sY_lm(theta,phi)
  = (-1)^s sqrt((2l+1)/(4pi)) [D^l_{m,-s}(phi,theta,0)]^*
```

the paper's printed `D^2_{m s}(phi,theta,0)` cannot be used by name alone.
The active/passive sense, the `m,s` index order, and signs of `theta/phi`
must be fixed by comparison with direct tensor contraction.

Current diagnostic status:
- Axis cases can pass accidentally.
- Off-axis, feeding exact direct strict Kinnersley NP scalars into the
  current `transform_weyl_to_incident_tetrad(...)` fails at O(1).
- A simple one-line Wigner-D index/sign/conjugation toggle was not found.

Decision:
- Treat the current Eq. (39)-(40) implementation as an unvalidated
  candidate transform, not a frozen convention.
- The production transform should be rederived as a strict-NP tetrad
  transform against direct tensor contraction tests.
- Its API should be named accordingly, e.g.
  `transform_strict_np_weyl_to_incident_tetrad`.

## 5. Bridge decision for project APIs

### APIs that should return strict NP scalars

These APIs should represent strict NP Weyl scalars, after Q014 fixes:

```text
weyl_mode_components(...)
assemble_weyl_scalars(...)
transform_strict_np_weyl_to_incident_tetrad(...)
```

The current `weyl_mode_components(...)` is intended to be strict Kinnersley
NP, but its lower scalar path is not yet validated because Eq. (35g)-(35h)
was previously treated as a positive-frequency source rule. It should not
silently return packaged scalars.

### APIs that should return packaged polarization scalars

These APIs should return packaged scalars:

```text
direct_cartesian_tt_weyl(...)        # current implementation semantics
future package_tidal_polarization_scalars(...)
```

Because `direct_cartesian_tt_weyl(...)` currently returns
`Psi0_pack/Psi4_pack`, not strict NP scalars, it should be renamed in a
future code slice to a name such as:

```text
direct_cartesian_tt_packaged_weyl(...)
```

or split into:

```text
direct_cartesian_tt_strict_np_weyl(...)
direct_cartesian_tt_packaged_weyl(...)
```

### `polarization_from_weyl(...)`

`polarization_from_weyl(k, psi0_hat, psi4_hat)` receives packaged scalars:

```text
psi0_hat = Psi0_pack
psi4_hat = Psi4_pack
```

It does not receive one-sided strict NP scalars. Passing strict
`Psi0_NP=0`, `Psi4_NP=-k^2(H_plus-iH_cross) exp(ikz)` for a +z wave into
this function is a convention error and can produce helicity/plus-cross
mixing.

Future API recommendation:

```text
polarization_from_packaged_weyl(k, psi0_pack, psi4_pack)
```

The old name may remain temporarily as a compatibility alias only if the
docstring clearly states the packaged-input contract.

### `transform_weyl_to_incident_tetrad(...)`

The current name is ambiguous. It should be split/renamed in a future code
slice:

```text
transform_strict_np_weyl_to_incident_tetrad(...)
```

and should be corrected by strict tensor-contraction RED tests before being
used in production partial-wave validation.

It should not transform packaged scalars.

## 6. Consequences for Q014

Q014 is not a T4 radial problem and not a direct polarization-packaging
problem. It is a bridge problem:

1. Eq. (35g)-(35h) star cannot be used as same-positive-k same-mode
   conjugation.
2. Eq. (39)-(40) applies to strict NP scalars only and must be rederived
   under the project Wigner convention.
3. `polarization_from_weyl` is currently a packaged-scalar extraction
   function, despite its generic name.

Next implementation slice should:

- add strict direct TT NP tests:
  `+z -> Psi4_NP nonzero, Psi0_NP=0`;
- add off-axis strict Kinnersley-to-incident transform tests from direct
  tensor contraction;
- rename/split the transform and polarization APIs;
- only then re-run partial-wave flat diagnostic and lmax convergence.

No author query is required for this bridge decision. The paper's printed
formulas are not declared wrong here; the issue is their translation into a
one-sided positive-frequency software API.
