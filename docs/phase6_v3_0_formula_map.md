# Phase 6 V3.0 formula map

Scientific stage: `V3.0`

Artifact revision: `r1`

Created at: `2026-08-11T11:27:39Z`

Status: T1 authority candidate; zero-science freeze

The detailed derivations and convention translations are in
`references/notes/phase6_v3_absorption_scattering_conventions.md`. This map
is the stable ID layer consumed by the validation contract, domains,
thresholds, anchors, and later producer manifests.

| Formula ID | SchWO object | Frozen formula / rule | Primary source and locator | Source-to-SchWO conversion | Units / domain | Downstream |
|---|---|---|---|---|---|---|
| `V3-F01-RADIAL-ASYMPTOTICS` | `A_in`, `A_out`, `A_H` | horizon `A_H exp(-i omega r_*)`; infinity `A_in exp(-i omega r_*) + A_out exp(+i omega r_*)` | Dolan PRD 77 (2008), Eqs. (6)--(8); Folacci--Ould El Hadj (2019), Eqs. (5), (8) | Both sources use `exp(-i omega t)` and Schwarzschild `r_*`; SchWO fixes the integration constant to its existing V2 definition | amplitudes inherit master units; `omega>0`, `ell>=2` | V3.1 |
| `V3-F02-S-MATRIX` | complex `S_l^p` | `S_l^p=(-1)^(l+1) A_out^p/A_in^p` | Dolan PRD 77 Eq. (8); Folacci--Ould El Hadj Eq. (9) | Algebraically identical to frozen SchWO `-A_out/[(-1)^l A_in]`; includes Jost/free phase | dimensionless | V3.1, V3.3, V3.4 |
| `V3-F03-CURRENT-FLUX` | signed current and positive flux | `j=(psi* psi' - psi psi'^*)/(2i)`; `F_in=-j_in`, `F_H=-j_H`, `F_out=+j_out` | real-potential Wronskian consequence; boundary signs fixed by `V3-F01`; Martel--Poisson Eq. (6.16) supplies master flux normalization | Same V2 ZM/RW/CPM conversion; positive flux is never the signed current itself | current/flux share the existing master normalization | V3.1 |
| `V3-F04-GAMMA` | greybody/absorption probability | `Gamma_flux=F_H/F_in`; independent `Gamma_S=1-|S|^2`; `R=|S|^2` | Dolan CQG 25 (2008), Eqs. (18)--(19); Ould El Hadj (2025), Eqs. (2)--(6) | Kerr expression is specialized to `a=0`; no superradiance, so `0<=Gamma<=1` | dimensionless; log representation mandatory for small positive values | V3.1, V3.2 |
| `V3-F05-PARITY` | odd/even relative S phase | `S_l^e=[(sigma_l+12 i M omega)/(sigma_l-12 i M omega)] S_l^o`, `sigma_l=(l-1)l(l+1)(l+2)` | Dolan PRD 77 Eq. (9); Folacci--Ould El Hadj Eqs. (10)--(12) | Source `Lambda(Lambda+2)` equals SchWO `sigma_l` | dimensionless; exact Schwarzschild vacuum relation | V3.1, V3.3 |
| `V3-F06-PARTIAL-ABS` | `sigma_abs_l` | `pi(2l+1)(Gamma_l^o+Gamma_l^e)/(2 omega^2)` | Dolan CQG 25 Eq. (18) plus `|_-2Y_l2(0)|^2=(2l+1)/(4pi)`; Ould El Hadj Eq. (2) | Equal parity weight made explicit; exact isospectral reduction is allowed only after independent odd/even solves | `M^2`; `ell>=2` | V3.2 |
| `V3-F07-TOTAL-ABS` | `sigma_abs` | continuous sum `sum_(l=2)^infinity sigma_abs_l` with frozen `ell_max` ladder and explicit tail bound | same as `V3-F06` | V2 sparse keys are controls only and cannot replace the continuous sum | `M^2` or `sigma/M^2` | V3.2 |
| `V3-F08-LOW-ABS` | low-frequency absorption law | `sigma_abs/M^2 -> (256 pi/45)(M omega)^4`; equivalently `Gamma_2 -> (4/225)(2M omega)^6` | Page PRD 13 (1976), Eq. (19), `s=2`, `a=0`, `A=16pi M^2` | Page angle average becomes helicity-independent in Schwarzschild; no polarization factor added | leading asymptote, `M omega << 1` | V3.2 |
| `V3-F09-CAPTURE` | geometric capture | `b_c=3 sqrt(3) M`, `sigma_geo=pi b_c^2=27 pi M^2` | Dolan CQG 25, Table 1 and Sec. 6.1; Page PRD 13, discussion after Eq. (19) | exact Schwarzschild limit `a=0`; oscillations are diagnostic around the limit | `M`, `M^2`; `M omega >>1` | V3.2, V3.4 |
| `V3-F10-HELICITY-PWS` | `f=f+`, `g=f-`, `d sigma/d Omega` | Folacci scalar-series form: `f^pm=L_x^pm ftilde^pm`; coefficients contain `[ (S_e pm S_o)/2 - (1 pm 1)/2 ]`; `d sigma/dOmega=|f|^2+|g|^2` | Folacci--Ould El Hadj Eqs. (1)--(4) | Their `p=e,o`, `exp(-i omega t)`, and S definition match SchWO; plus/minus maps to helicity-preserving/reversing | amplitudes `M`; cross section `M^2`; `theta>0` | V3.3, V3.4 |
| `V3-F11-SERIES-REDUCTION` | reduced scalar Legendre series | `a_l^(q+1)=a_l^q-(l+1)/(2l+3)a_(l+1)^q-l/(2l-1)a_(l-1)^q` | Yennie--Ravenhall--Wilson (1954), Eqs. (47)--(50); application to GW scattering: Dolan CQG 25 Sec. 5.3 | Apply separately to the two Folacci scalar series before `L_x^pm`; production `q=2`, ladder `q=1,2,3` | dimensionless recurrence; forward cone excluded | V3.3, V3.4 |
| `V3-F12-LOW-SCATTER` | low-frequency spin-2 `f`, `g`, cross section | exact leading amplitudes with common `Phi=-4M omega ln(4M omega)`; `M^-2 d sigma/dOmega=[cos^8(theta/2)+sin^8(theta/2)]/sin^4(theta/2)+O(M omega)` | Dolan PRD 77 Eqs. (19), (20), (36) | Same Fourier convention; overall common phase retained for complex-amplitude comparison and cancels from cross section | `M omega<<1`; outside frozen forward cone | V3.3 |
| `V3-F13-GLORY` | backward spin-2 glory | `2 pi omega b_g^2 |db/dtheta|_pi J_4^2(b_g omega sin theta)`; exact-geodesic `b_g=5.3570M`, `b_g^2|db/dtheta|=4.896M^3` | Dolan CQG 25 Eqs. (5)--(7), text below Eq. (6) | Kerr formula specialized to `a=0`; Bessel order `2|s|=4`; Darwin values are diagnostic only | `M^2`; high frequency and backward window | V3.4 |
| `V3-F14-MASTER-BRIDGE` | ZM/RW/CPM normalization | V2 bridge: Li even = MP ZM; Li odd = MP RW; `Psi_CPM=(2i/omega) psi_Li_odd` in vacuum | Martel--Poisson Eqs. (4.23), (5.13), (5.18), (6.16); Regge--Wheeler, Zerilli, Moncrief foundations | No new V3 normalization; inherits exact V2 convention contract SHA | existing V2 units and real-peak amplitude convention | V3.1, V3.2 |

## Mandatory implementation predicates

1. `V3-F02` and `V3-F04` must be evaluated from independently extracted
   amplitudes/fluxes; `Gamma_S` cannot populate the direct-flux field.
2. Odd and even solutions must both be computed. `V3-F05` is a consistency
   relation, not an even-sector producer.
3. `V3-F07` uses every integer multipole from two through the frozen
   `ell_max`; no sparse interpolation is allowed.
4. `V3-F10` is a scattered-field amplitude. The null-infinity total plane
   wave must not be assembled by an ordinary partial-wave sum.
5. `V3-F11` must preserve the unreduced/reduced identity away from the
   forward cone and pass its reduction-order ladder.
6. `V3-F12` and `V3-F13` carry asymptotic-model uncertainty separately from
   numerical uncertainty; passing a loose asymptotic comparator cannot hide a
   failed numerical convergence gate.

## Source identity policy

Stable DOI/arXiv identifiers and exact source roles are frozen in
`docs/phase6_v3_0_literature_matrix.md`. A later producer must record the
formula IDs used and the SHA-256 of this map. A source or formula change after
producer creation requires a new artifact revision and fresh review; no
in-place reinterpretation is permitted.
