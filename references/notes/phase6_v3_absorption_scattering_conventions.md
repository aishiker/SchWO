# Phase 6 V3.0 absorption and scattering conventions

Scientific stage: `V3.0`

Artifact revision: `r1`

Created: `2026-08-11T11:27:39Z` (`UTC`)

Execution class: primary-literature and convention freeze only; no science run

## 1. Scope and fixed background

This note translates primary-source Schwarzschild absorption and scattering
formulae into the existing SchWO convention. It does not alter any V1/V2
identity. Throughout,

\[
G=c=1,\qquad e^{-i\omega t},\qquad kM\equiv \omega M>0,
\]

and

\[
r_* = r+2M\ln\!\left(\frac{r}{2M}-1\right).
\]

The radiative multipoles begin at \(\ell=2\). `odd` means axial/
Regge--Wheeler and `even` means polar/Zerilli. All cross sections have
dimension \(M^2\); `sigma_over_M2` is dimensionless.

## 2. Radial amplitudes, currents, fluxes, and S matrices

For either parity \(p\in\{o,e\}\), the future-horizon-regular homogeneous
solution is normalized only after extracting

\[
 \psi_{\ell}^{p}\sim
 \begin{cases}
 A_H^p e^{-i\omega r_*},&r_*\to-\infty,\\
 A_{\rm in}^p e^{-i\omega r_*}
 +A_{\rm out}^p e^{+i\omega r_*},&r_*\to+\infty.
 \end{cases}
\]

For the real RW/Zerilli potentials, use the signed Wronskian current

\[
 j[\psi]=\frac{1}{2i}
 \left(\psi^*\partial_{r_*}\psi-\psi\partial_{r_*}\psi^*\right).
\]

Thus an ingoing plane wave has negative signed current and an outgoing plane
wave has positive signed current:

\[
j_{\rm in}=-\omega|A_{\rm in}|^2,\quad
j_H=-\omega|A_H|^2,\quad
j_{\rm out}=+\omega|A_{\rm out}|^2.
\]

Positive physical fluxes are defined as
\(F_{\rm in}=-j_{\rm in}\), \(F_H=-j_H\), and
\(F_{\rm out}=+j_{\rm out}\), including the same master-normalization factor
on both sides. A signed current must never be labelled a positive absorption
flux.

The SchWO complex mode S matrix is

\[
 S_\ell^p=e^{2i\delta_\ell^p}
 =(-1)^{\ell+1}\frac{A_{\rm out}^p}{A_{\rm in}^p}
 =-\frac{A_{\rm out}^p}{(-1)^\ell A_{\rm in}^p}.
\]

This is exactly the Schwarzschild RW definition in Dolan (2008), PRD 77,
Eq. (8), and Folacci--Ould El Hadj (2019), Eq. (9). It includes the fixed
SchWO tortoise/Jost/free reference phase; no additional arbitrary
\(\ell\)-dependent rephasing is allowed. The free reference is
\(S_\ell^p=1\).

Define

\[
R_\ell^p=|S_\ell^p|^2,\qquad
\Gamma_{\ell,\mathrm{flux}}^p=\frac{F_H^p}{F_{\rm in}^p},\qquad
\Gamma_{\ell,S}^p=1-|S_\ell^p|^2.
\]

`Gamma_flux` is the direct horizon route. `Gamma_S` is an independent
Wronskian/S-matrix consistency route, never a substitute for the direct
horizon flux. For Schwarzschild, \(0\leq\Gamma\leq1\) and
\(R+\Gamma=1\). Extremely small positive values are stored as
`log_gamma = log(Gamma)` together with sign/validity metadata; an underflowed
binary64 zero is not acceptable evidence of zero absorption.

## 3. Odd/even relation and its limitation

Let

\[
\sigma_\ell=(\ell-1)\ell(\ell+1)(\ell+2).
\]

The Chandrasekhar--Detweiler relation gives

\[
S_\ell^e=
\frac{\sigma_\ell+12iM\omega}
     {\sigma_\ell-12iM\omega}S_\ell^o.
\]

This is Dolan PRD 77 Eq. (9) and Folacci--Ould El Hadj Eq. (12). Its ratio
has unit modulus, hence \(R_\ell^e=R_\ell^o\) and
\(\Gamma_\ell^e=\Gamma_\ell^o\) in exact Schwarzschild theory. The relation
is a parity-consistency benchmark, not permission to call parity-derived even
data an independent even solve. V3.1 requires independent odd and even radial
solutions; the relation is checked only after both are obtained.

## 4. Partial and total absorption cross section

For a plane gravitational wave in Schwarzschild, with the two parity sectors
weighted equally,

\[
\sigma_{\ell}^{\rm abs}(\omega)=
\frac{\pi}{2\omega^2}(2\ell+1)
\left(\Gamma_\ell^o+\Gamma_\ell^e\right),\qquad \ell\ge2,
\]

\[
\sigma_{\rm abs}(\omega)=\sum_{\ell=2}^{\infty}
\sigma_{\ell}^{\rm abs}(\omega).
\]

Because the exact Schwarzschild probabilities are isospectral, this reduces
to \(\pi\omega^{-2}\sum_{\ell=2}^{\infty}(2\ell+1)\Gamma_\ell\).
It follows directly from Dolan CQG 25 Eq. (18) after using
\(|{}_{-2}Y_{\ell2}(0)|^2=(2\ell+1)/(4\pi)\), and agrees with the general
spin-s formula in Ould El Hadj (2025), Eq. (2). This normalization is for one
unit-flux plane-wave helicity; in Schwarzschild it is helicity independent and
is also the unpolarized average. No extra factor of two is inserted.

For \(M\omega\ll1\), Page (1976), Eq. (19), specialized to \(a=0\) and
horizon area \(A=16\pi M^2\), gives

\[
\sigma_{\rm abs}^{(s=2)}=
\frac{256\pi}{45}M^2(M\omega)^4\,[1+o(1)]
=\frac{4\pi}{45}(2M)^6\omega^4\,[1+o(1)].
\]

The leading term comes from \(\ell=2\), implying
\(\Gamma_2=(4/225)(2M\omega)^6[1+o(1)]\). This is an asymptotic benchmark,
not a pointwise identity at finite frequency.

For \(M\omega\gg1\), null-geodesic capture gives

\[
b_c=3\sqrt3\,M,\qquad
\sigma_{\rm geo}=\pi b_c^2=27\pi M^2.
\]

Dolan CQG 25 Sec. 6.1 and Page Eq. (19) discussion independently state this
Schwarzschild high-frequency limit. The pointwise quantum cross section
oscillates around the capture scale; V3.2 treats oscillatory corrections as
diagnostic and tests the capture limit through a frozen frequency-window
average, not by demanding every point equal \(27\pi M^2\).

## 5. Differential scattering amplitudes

Set \(x=\cos\theta\). The adopted exact Schwarzschild representation is the
Folacci--Ould El Hadj Eqs. (1)--(4):

\[
\frac{d\sigma}{d\Omega}=|f^+(\omega,x)|^2+|f^-(\omega,x)|^2,
\qquad f\equiv f^+,\quad g\equiv f^- ,
\]

\[
\widetilde f^{\,\pm}(\omega,x)=\frac{1}{2i\omega}
\sum_{\ell=2}^{\infty}\frac{2\ell+1}{\sigma_\ell}
\left[\frac{S_\ell^e\pm S_\ell^o}{2}
-\frac{1\pm1}{2}\right]P_\ell(x),
\]

\[
f^\pm(\omega,x)=\widehat L_x^\pm\widetilde f^{\,\pm}(\omega,x),
\]

\[
\widehat L_x^\pm=(1\pm x)^2\frac{d}{dx}
\left\{(1\mp x)\frac{d^2}{dx^2}
\left[(1\mp x)\frac{d}{dx}\right]\right\}.
\]

The plus channel contains
\((S_\ell^e+S_\ell^o)/2-1\), while the minus channel contains
\((S_\ell^e-S_\ell^o)/2\). This is the exact total/free/scattered separation:
the scattering amplitude contains `S-1`; the incident plane wave is not
summed as an ordinary convergent null-infinity series. An ordinary total
plane-wave sum at null infinity is forbidden.

The long-range gravitational field produces a forward Coulomb singularity,
\(d\sigma/d\Omega\sim16M^2/\theta^4\). The series is distributional at
\(\theta=0\). SchWO retains the full physical Coulomb phase in \(S_\ell\),
uses the explicit free subtraction above, applies series reduction, and
excludes the frozen forward cone. It does not introduce an unsourced
mode-by-mode Coulomb rephasing.

For a Legendre series \(F(x)=\sum_{\ell\ge0}a_\ell^{(0)}P_\ell(x)\), the
Yennie--Ravenhall--Wilson reduced series is

\[
(1-x)^qF(x)=\sum_{\ell\ge0}a_\ell^{(q)}P_\ell(x),
\]

with primary-source recurrence (Yennie et al. 1954, Eqs. (48)--(49))

\[
a_\ell^{(q+1)}=a_\ell^{(q)}
-\frac{\ell+1}{2\ell+3}a_{\ell+1}^{(q)}
-\frac{\ell}{2\ell-1}a_{\ell-1}^{(q)},
\]

and absent coefficients set to zero. It is applied separately to the two
scalar series \(\widetilde f^\pm\), before applying
\(\widehat L_x^\pm\). The adopted production order is \(q=2\), matching
Dolan CQG 25 Sec. 5.3; \(q=1,2,3\) is the mandatory convergence ladder.

## 6. Low-frequency spin-2 benchmark

Dolan PRD 77 Eqs. (19), (20), and (36) give, for \(M\omega\ll1\),

\[
\frac{f(\theta)}{M}=e^{-i\Phi-2iM\omega}
\frac{\Gamma(1-2iM\omega)}{\Gamma(1+2iM\omega)}
\frac{\cos^4(\theta/2)}{[\sin^2(\theta/2)]^{1-2iM\omega}}
+O(M\omega),
\]

\[
\frac{g(\theta)}{M}=e^{-i\Phi}\sin^2(\theta/2)+O(M\omega),
\qquad \Phi=-4M\omega\ln(4M\omega),
\]

and therefore

\[
\frac{1}{M^2}\frac{d\sigma}{d\Omega}=
\frac{\cos^8(\theta/2)+\sin^8(\theta/2)}{\sin^4(\theta/2)}
+O(M\omega)
\]

away from the forward distribution. The common overall phase does not affect
the cross section. The \(\sin^8\) term is the helicity-reversing contribution
from the odd/even relative phase; it makes the exact low-frequency backward
cross section nonzero. V3.3 uses only the frozen low-frequency and angular
domain; no claim is made at \(\theta=0\).

## 7. Backward glory benchmark

Dolan CQG 25 Eq. (5) gives the semiclassical spin-s glory form

\[
\frac{d\sigma}{d\Omega}\simeq
2\pi\omega b_g^2\left|\frac{db}{d\theta}\right|_{\theta=\pi}
J_{2|s|}^2(b_g\omega\sin\theta).
\]

For gravitational waves, \(s=2\) and the Bessel order is exactly four:
\(J_4\). Dolan's exact Schwarzschild geodesic values are

\[
b_g=5.3570M,\qquad
b_g^2|db/d\theta|_{\pi}=4.896M^3,
\]

so \(|db/d\theta|_{\pi}=4.896M^3/b_g^2\). The Darwin approximation values
\(b_g=5.3465M\) and \(b_g^2|db/d\theta|=4.30M^3\) are diagnostic only and
must not replace the exact-geodesic anchor.

Because \(J_4(0)=0\), the spin-2 high-frequency glory is a ring, not an
on-axis maximum. The comparator therefore extracts, inside the frozen
backward window: (i) first ring peak angle, (ii) full width at half maximum of
that ring, and (iii) peak height. It compares these with the same quantities
computed from the formula above on an independently converged angle grid.
No pointwise claim is made at \(\theta=\pi\), and asymptotic-model error is
reported separately from numerical error.

## 8. Master-normalization bridge retained from V2

No V3 normalization is introduced. Martel--Poisson define the
Zerilli--Moncrief field in Eq. (4.23), the Cunningham--Price--Moncrief field
in Eq. (5.13), their vacuum relation to the Regge--Wheeler function in
Eq. (5.18), and the infinity energy flux in Eq. (6.16). The frozen V2 bridge
is retained byte-for-byte in meaning:

- SchWO/Li even master = Martel--Poisson Zerilli--Moncrief master;
- SchWO/Li odd master = Martel--Poisson Regge--Wheeler master;
- in vacuum with \(e^{-i\omega t}\),
  \(\Psi_{\rm CPM}=(2i/\omega)\psi_{\rm odd}^{\rm Li}\);
- the real-peak-amplitude energy-flux coefficient is
  \(\omega^2\sigma_\ell/(128\pi)\) multiplying the squared ZM/CPM
  amplitudes in the established V2 convention.

These facts fix the normalization used by the direct horizon and infinity
flux routes. V3.0 neither rewrites nor revalidates frozen V2 data.

## 9. Stable primary-source records

- Page, *Particle emission rates from a black hole: Massless particles from
  an uncharged, nonrotating hole*, Phys. Rev. D **13**, 198 (1976),
  DOI `10.1103/PhysRevD.13.198`, especially Eq. (19).
- Handler and Matzner, *Gravitational wave scattering*, Phys. Rev. D **22**,
  2331 (1980), DOI `10.1103/PhysRevD.22.2331`, Secs. II, V, VI. Role:
  historical full partial-wave formulation and numerical scattering/glory
  cross-check; not the adopted normalization source where later formulae are
  clearer.
- Dolan, *Scattering of long-wavelength gravitational waves*, Phys. Rev. D
  **77**, 044004 (2008), arXiv:`0710.4252`,
  DOI `10.1103/PhysRevD.77.044004`, Eqs. (3)--(9), (19), (20), (36).
- Dolan, *Scattering and absorption of gravitational plane waves by rotating
  black holes*, Class. Quantum Grav. **25**, 235002 (2008),
  arXiv:`0801.3805`, DOI `10.1088/0264-9381/25/23/235002`, Schwarzschild
  limit of Eqs. (5), (14)--(19), (113)--(121), Sec. 6.1 and Table 1.
- Folacci and Ould El Hadj, *Regge pole description of scattering of
  gravitational waves by a Schwarzschild black hole*, Phys. Rev. D **100**,
  064009 (2019), arXiv:`1906.01441`,
  DOI `10.1103/PhysRevD.100.064009`, Eqs. (1)--(12).
- Yennie, Ravenhall, and Wilson, *Phase-shift calculation of high-energy
  electron scattering*, Phys. Rev. **95**, 500 (1954),
  DOI `10.1103/PhysRev.95.500`, Eqs. (47)--(50).
- Martel and Poisson, *Gravitational perturbations of the Schwarzschild
  spacetime: A practical covariant and gauge-invariant formalism*, Phys. Rev.
  D **71**, 104003 (2005), arXiv:`gr-qc/0502028`,
  DOI `10.1103/PhysRevD.71.104003`, Eqs. (4.23), (5.13), (5.18), (6.16).
- Regge and Wheeler, Phys. Rev. **108**, 1063 (1957),
  DOI `10.1103/PhysRev.108.1063`; Zerilli, Phys. Rev. Lett. **24**, 737
  (1970), DOI `10.1103/PhysRevLett.24.737`, and Phys. Rev. D **2**, 2141
  (1970), DOI `10.1103/PhysRevD.2.2141`; Moncrief, Phys. Rev. D **9**, 2707
  (1974), DOI `10.1103/PhysRevD.9.2707`. Role: foundational RW/Zerilli and
  gauge-invariant normalization chain.
- Ould El Hadj, *Black hole absorption cross sections: Spin and Regge poles*,
  Phys. Rev. D **111**, 124041 (2025), arXiv:`2504.19324`,
  DOI `10.1103/vj91-h7wd`, Eqs. (2)--(6). Role: modern independent statement
  of the total spin-s normalization and Schwarzschild boundary convention.

Sanchez's classic papers are not needed to fix a spin-2 formula here; their
scalar absorption/elastic-scattering results are therefore recorded as
context only, not used as a V3 blocking anchor. Li--Hou--Zhao remains secondary
regression only.
