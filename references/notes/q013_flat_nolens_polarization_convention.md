# Q013 flat no-lens polarization convention note

Date: 2026-07-05

Scope:
- Trigger context: T6e established a direct Cartesian TT no-lens oracle and localized the remaining O(1) mismatch below the local tetrad/Weyl/polarization layer, in the partial-wave/RW reconstruction/Weyl assembly path.
- This note records the convention audit requested for Li-Hou-Zhao Eq. (39)-(42), Newman-Penrose `Psi0/Psi4` propagation direction, and the `+z` incident plane-wave limit.
- No code changes are made here.

## Sources checked

- Li, Hou, Zhao 2025, `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`, especially Eq. (30), Eq. (36), Eq. (39)-(42).
- Project frozen convention: `docs/physics_spec.md` Sec. 1 and Sec. 9.
- Project formula audit: `references/notes/phase3_formula_audit.md`.
- Project direct oracle implementation, read-only: `src/schwgw/scattering/partial_wave.py`.
- Review cross-check: Bishop and Rezzolla, "Extraction of gravitational waves in numerical relativity", Living Reviews in Relativity 2016, Sec. 3.3. This review defines `psi4` by NP contraction and states that, with the usual outgoing tetrad at infinity, `psi4` describes outgoing gravitational radiation and is related to the TT strain.

## Li-Hou-Zhao equations relevant to this issue

Li-Hou-Zhao first define NP scalars by the tetrad contractions

```text
psi0 = -C(l,m,l,m)
psi1 = -C(l,n,l,m)
psi2 = -C(l,m,n,mbar)
psi3 = -C(l,n,n,mbar)
psi4 = -C(n,mbar,n,mbar)
```

where the tetrad order is `{l,n,m,mbar}`. Their Schwarzschild-stage tetrad is the Kinnersley tetrad, then they introduce an incident-aligned Cartesian tetrad

```text
lhat = (1/sqrt(2)) (1, 0, 0,  1)
nhat = (1/sqrt(2)) (1, 0, 0, -1)
mhat = (1/sqrt(2)) (0, 1, i,  0)
```

The paper says the first null leg is aligned with the `z` axis / incident null direction.

They transform Kinnersley Weyl scalars to this incident tetrad using

```text
Psi_hat_{2-m} = sum_s Lambda_{2ms} Psi_{2-s},
```

with a Wigner-D coefficient. This is an active/passive and index-order risk; the project freezes the Wigner-D convention in `docs/physics_spec.md` and should not infer it from external library names.

Finally, Eq. (41)-(42) defines real-time polarizations through geodesic deviation:

```text
hddot_plus  = Re(Psi_hat_4) + Re(Psi_hat_0)
hddot_cross = -(Im(Psi_hat_4) - Im(Psi_hat_0))
```

The project converts this to positive-frequency complex amplitudes as

```text
hddot_plus_tilde  = Psi_hat_4_tilde + Psi_hat_0_tilde
hddot_cross_tilde = i (Psi_hat_4_tilde - Psi_hat_0_tilde)

h_plus_tilde  = -(Psi_hat_4_tilde + Psi_hat_0_tilde) / k^2
h_cross_tilde = -i (Psi_hat_4_tilde - Psi_hat_0_tilde) / k^2
```

This conversion is a project storage convention, not a generic NP textbook identity.

## Direction convention: should a +z plane wave be Psi0 or Psi4?

Assume flat spacetime, signature `(-,+,+,+)`, positive-frequency convention

```text
h_ij(t,z) = H_ij exp(i k z) exp(-i k t)
```

so the wave propagates in the `+z` direction. With the incident-aligned tetrad,

```text
lhat^mu = (1,0,0, 1)/sqrt(2)
nhat^mu = (1,0,0,-1)/sqrt(2)
```

the contravariant wave vector is parallel to `lhat`, while the phase covector is proportional to `(-1,0,0,1)`. Therefore

```text
k_mu lhat^mu = 0,
k_mu nhat^mu != 0.
```

For a plane wave the linearized curvature is quadratic in the phase covector. Hence the NP contraction with two `lhat` legs vanishes, while the contraction with two `nhat` legs is nonzero:

```text
Psi0 = -C(lhat,mhat,lhat,mhat) = 0,
Psi4 = -C(nhat,mhatbar,nhat,mhatbar) != 0.
```

Thus, in the standard NP direction sense used by numerical-relativity extraction, a `+z` plane wave corresponds to `Psi4`, not `Psi0`, when `lhat` is aligned with `+z`.

Conversely, a wave propagating in `-z` would have `Psi4 = 0` and nonzero `Psi0` in the same tetrad.

## Explicit flat TT check

For a `+z` TT plane wave

```text
h_xx =  H_plus  exp(i k z) exp(-i k t)
h_yy = -H_plus  exp(i k z) exp(-i k t)
h_xy =  H_cross exp(i k z) exp(-i k t)
```

the linearized Riemann electric components satisfy, with the project sign convention,

```text
R_txtx = (k^2/2) H_plus  exp(i k z)
R_txty = (k^2/2) H_cross exp(i k z)
```

The actual NP contractions with the incident tetrad give

```text
Psi0_NP = 0,
Psi4_NP = -k^2 (H_plus - i H_cross) exp(i k z).
```

For a `-z` wave the corresponding result is

```text
Psi0_NP = -k^2 (H_plus + i H_cross) exp(-i k z),
Psi4_NP = 0.
```

This is the clean direction diagnostic. If a `+z` direct NP contraction produces dominant `Psi0`, then either the `l/n` assignment, propagation direction, or phase convention has been reversed.

## Why this does not directly equal the project positive-frequency Eq. (42) storage

Li-Hou-Zhao Eq. (42) is written as a real-time statement using real and imaginary parts of the Weyl scalars. For a single real outgoing wave, the usual textbook/NR statement is schematically

```text
Psi4(t) = hddot_plus(t) - i hddot_cross(t)
```

up to overall sign conventions. That real-time statement is not complex-linear in arbitrary stored positive-frequency amplitudes if one extracts `h_plus` and `h_cross` by taking real and imaginary parts at the amplitude level.

The project stores only `k > 0` complex amplitudes and requires linearity in `H_plus` and `H_cross`. Therefore `docs/physics_spec.md` encodes the Li-Hou-Zhao Eq. (42) real relation as the linear combination

```text
hddot_plus_tilde  = Psi4_tilde + Psi0_tilde
hddot_cross_tilde = i(Psi4_tilde - Psi0_tilde).
```

Under this storage convention, a flat direct no-lens oracle may package the electric tidal components into a pair

```text
Psi4_pack = -R_txtx + i R_txty
Psi0_pack = -R_txtx - i R_txty
```

so that

```text
-(Psi4_pack + Psi0_pack)/k^2      = H_plus exp(i k z)
-i(Psi4_pack - Psi0_pack)/k^2     = H_cross exp(i k z).
```

This `Psi0_pack/Psi4_pack` pair is a project-compatible geodesic-deviation packaging for positive-frequency amplitudes. It should not be confused with the strict NP propagation-direction diagnostic above, where the same `+z` wave has `Psi0_NP=0` and nonzero `Psi4_NP`.

## Implications for T6/T7

1. The answer to the direction question is:

```text
With lhat aligned with +z, a +z plane wave is Psi4 in standard NP direction convention.
```

2. T6e's direct Cartesian TT oracle passing means the local geodesic-deviation extraction layer can recover `H_plus/H_cross` under the project's positive-frequency packaging. It does not by itself validate every Wigner-D, spin-weighted harmonic, or RW reconstruction phase in the partial-wave path.

3. If a future diagnostic wants to test actual NP direction, it should contract the linearized Weyl tensor by Eq. (30), not use the packaged `direct_cartesian_tt_weyl(...)` values designed for Eq. (42) amplitude recovery.

4. The old axis symptom

```text
h_cross = i h_plus
```

in the partial-wave diagnostic is consistent with mixing a helicity/NP-direction convention with the positive-frequency `h_plus/h_cross` extraction convention. It is not fixed by merely toggling the Eq. (35g)-(35h) complex conjugation star.

5. Priority for further localization:
- First test flat partial-wave assembly at the level of `Psi4_NP` direction: for a `+z` TT wave in the incident tetrad, the strict NP contraction should be `Psi0_NP = 0`.
- Then separately test the Eq. (42) positive-frequency packaging needed to recover `H_plus/H_cross`.
- Do not use one test to validate both conventions simultaneously.

## Convention risks to record

- `Psi0`/`Psi4` direction depends on which null leg is called `l` and which is called `n`.
- The common statement "`Psi4` is outgoing radiation" assumes `l` is the outgoing null vector and `n` is incoming.
- Li-Hou-Zhao align the first null leg `lhat` with the incident `+z` direction. Therefore the incident `+z` wave is `Psi4` in strict NP language.
- Eq. (42)'s `Re/Im` formulas are real-time formulas. Translating them to stored complex amplitudes requires a convention choice and can otherwise introduce antilinear operations or helicity mixing.
- The project's `polarization_from_weyl` is a positive-frequency storage rule. It is valid for project-packaged `Psi0/Psi4`; it is not automatically the same as plugging in a one-sided strict NP `Psi4_NP` amplitude.

## Recommendation

Do not change the frozen tetrad vectors in `docs/physics_spec.md`.

For documentation/tests, explicitly distinguish:

```text
strict NP direction scalars:
  +z wave with lhat along +z -> Psi4_NP nonzero, Psi0_NP zero

project positive-frequency polarization packaging:
  use Psi4_pack + Psi0_pack and i(Psi4_pack - Psi0_pack)
  to recover H_plus and H_cross linearly
```

If T6/T7 continue investigating the partial-wave flat diagnostic, the next likely target is not the incident Cartesian tetrad itself, but the mapping from spin-weighted partial-wave/RW reconstruction quantities into the strict NP scalars and then into the project packaging used by Eq. (42).
