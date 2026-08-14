# Phase 6 V3.0 primary-literature matrix

Scientific stage: `V3.0`

Artifact revision: `r1`

Created at: `2026-08-11T11:27:39Z`

Method: primary paper first; publisher/DOI/arXiv identity; no model-memory formula

## Evidence matrix

| Source ID | Stable identity and access | Primary-source locator | Frozen role | Source convention | SchWO conversion / limitation |
|---|---|---|---|---|---|
| `LIT-PAGE-1976` | D. N. Page, PRD **13**, 198 (1976), DOI [`10.1103/PhysRevD.13.198`](https://doi.org/10.1103/PhysRevD.13.198) | Eq. (19), `s=2`; text immediately below | Exact leading low-frequency graviton absorption cross section and `27 pi M^2` high-frequency statement | General Kerr, angle-averaged; horizon area `A`; natural units | Set `a=0`, `A=16 pi M^2`; Schwarzschild result is polarization independent. Produces `V3-F08` and corroborates `V3-F09`. |
| `LIT-HANDLER-MATZNER-1980` | F. A. Handler and R. A. Matzner, PRD **22**, 2331 (1980), DOI [`10.1103/PhysRevD.22.2331`](https://doi.org/10.1103/PhysRevD.22.2331) | Sec. II, Eqs. (2.4)--(2.14); Secs. V--VI | Required historical gravitational partial-wave, absorption, phase, semiclassical/glory cross-check | Kerr/Teukolsky and metric variables; older notation; circular polarization | Assessed but not adopted for final normalization because later Dolan/Folacci formulae are more explicit and convention-aligned. Its numerical figures are qualitative, not machine-value anchors. |
| `LIT-DOLAN-LONG-2008` | S. R. Dolan, PRD **77**, 044004 (2008), arXiv [`0710.4252`](https://arxiv.org/abs/0710.4252), DOI [`10.1103/PhysRevD.77.044004`](https://doi.org/10.1103/PhysRevD.77.044004) | Eqs. (3)--(9), (11)--(14), (19), (20), (36) | Canonical Schwarzschild S matrix, parity phase relation, low-frequency `f/g`, and spin-2 differential cross section | `exp(-i omega t)`; Schwarzschild; spin-weighted spherical harmonics | Direct match after fixing the existing SchWO tortoise constant. The paper explicitly separates irrelevant common phase from `ell`/parity phase. |
| `LIT-DOLAN-CQG-2008` | S. R. Dolan, CQG **25**, 235002 (2008), arXiv [`0801.3805`](https://arxiv.org/abs/0801.3805), DOI [`10.1088/0264-9381/25/23/235002`](https://doi.org/10.1088/0264-9381/25/23/235002) | Schwarzschild limit of Eqs. (5), (14)--(19), (30), (113)--(121); Table 1; Secs. 5.3, 6.1--6.2 | Absorption normalization, glory formula/parameters, high-frequency capture, and tested GW series reduction | Kerr/Teukolsky/Sasaki--Nakamura; axis incidence; `exp(-i omega t)` | Set `a=0`; spheroidal harmonics become spin-weighted spherical harmonics; `|_-2Y_l2(0)|^2=(2l+1)/(4pi)`. Exact-geodesic glory values are mandatory; Darwin values diagnostic. |
| `LIT-FOLACCI-OEH-2019` | A. Folacci and M. Ould El Hadj, PRD **100**, 064009 (2019), arXiv [`1906.01441`](https://arxiv.org/abs/1906.01441), DOI [`10.1103/PhysRevD.100.064009`](https://doi.org/10.1103/PhysRevD.100.064009) | Eqs. (1)--(12), especially (3), (8)--(12) | Adopted exact Schwarzschild helicity-amplitude representation, `S-1` separation, parity relation, and external Regge-pole context | `exp(-i omega t)`; Schwarzschild; ZM/RW; `p=e,o` | `f+ -> f`, `f- -> g`; their S definition is algebraically SchWO's. Regge-pole plots/approximations are external qualitative/semianalytic checks unless a later numerical table is frozen. |
| `LIT-YRW-1954` | D. R. Yennie, D. G. Ravenhall, R. N. Wilson, Phys. Rev. **95**, 500 (1954), DOI [`10.1103/PhysRev.95.500`](https://doi.org/10.1103/PhysRev.95.500) | Eqs. (47)--(50), publisher page 505 | Primary source for the adopted Legendre series-reduction identity and recurrence | Coulomb electron scattering; scalar Legendre series | The recurrence is mathematical and is applied separately to Folacci's two scalar precursor series. Physics coefficients are not imported. |
| `LIT-MARTEL-POISSON-2005` | K. Martel and E. Poisson, PRD **71**, 104003 (2005), arXiv [`gr-qc/0502028`](https://arxiv.org/abs/gr-qc/0502028), DOI [`10.1103/PhysRevD.71.104003`](https://doi.org/10.1103/PhysRevD.71.104003) | Eqs. (4.23), (5.13), (5.17)--(5.18), (6.13)--(6.16), (7.2)--(7.4) | Modern gauge-invariant ZM/CPM definitions and energy-flux normalization chain | Time-domain covariant formalism; tensor harmonics explicitly normalized | Retain the frozen V2 frequency-domain bridge `Psi_CPM=(2i/omega) psi_Li_odd`; no V3 reinterpretation. |
| `LIT-RW-1957` | T. Regge and J. A. Wheeler, Phys. Rev. **108**, 1063 (1957), DOI [`10.1103/PhysRev.108.1063`](https://doi.org/10.1103/PhysRev.108.1063) | odd-parity decomposition and RW equation | Foundational odd-sector identity | Original RW notation and signature conventions | Used through the already frozen SchWO/V2 potential and master convention; no direct new formula copy. |
| `LIT-ZERILLI-1970` | F. J. Zerilli, PRL **24**, 737 (1970), DOI [`10.1103/PhysRevLett.24.737`](https://doi.org/10.1103/PhysRevLett.24.737); PRD **2**, 2141 (1970), DOI [`10.1103/PhysRevD.2.2141`](https://doi.org/10.1103/PhysRevD.2.2141) | even-parity master equation/potential | Foundational even-sector identity | Original Zerilli normalization | Used through frozen V2 ZM/project conversion; not a new V3 normalization. |
| `LIT-MONCRIEF-1974` | V. Moncrief, PRD **9**, 2707 (1974), DOI [`10.1103/PhysRevD.9.2707`](https://doi.org/10.1103/PhysRevD.9.2707) | gauge-invariant Schwarzschild master variables | Gauge-invariance and normalization chain | Hamiltonian gauge-invariant variables | Cross-check only; Martel--Poisson is the explicit modern bridge. |
| `LIT-OEH-2025` | M. Ould El Hadj, PRD **111**, 124041 (2025), arXiv [`2504.19324`](https://arxiv.org/abs/2504.19324), DOI [`10.1103/vj91-h7wd`](https://doi.org/10.1103/vj91-h7wd) | Eqs. (2)--(6) | Modern independent total spin-s absorption normalization, RW boundary convention, and parity-isospectral statement | `exp(-i omega t)`; explicit Schwarzschild `r_*`; spin-s RW potential | Directly supports `pi/omega^2 sum(2l+1)Gamma_l`; later CAM approximations are diagnostic, not required. |
| `LIT-SANCHEZ-CONTEXT` | N. Sánchez, PRD **18**, 1030 (1978), DOI [`10.1103/PhysRevD.18.1030`](https://doi.org/10.1103/PhysRevD.18.1030); PRD **18**, 1798 (1978), DOI [`10.1103/PhysRevD.18.1798`](https://doi.org/10.1103/PhysRevD.18.1798) | scalar absorption and elastic-scattering analyses | Explicit justified exclusion from blocking spin-2 normalization | Scalar field | Context for classic Schwarzschild absorption/scattering only. No Sánchez scalar coefficient is used as a spin-2 anchor. |
| `LIT-LI-HOU-ZHAO-SECONDARY` | Existing project target paper and local source cache | existing V1/V2 equation maps | Secondary regression only | finite-radius paper conventions | Cannot source or veto any V3 absorption/scattering formula; no figures are regenerated in V3.0. |

## Formula-to-source completeness

| Formula IDs | Primary support | Independent corroboration |
|---|---|---|
| `V3-F01`--`V3-F05` | `LIT-DOLAN-LONG-2008`, `LIT-FOLACCI-OEH-2019` | `LIT-DOLAN-CQG-2008`, `LIT-MARTEL-POISSON-2005` |
| `V3-F06`--`V3-F07` | `LIT-DOLAN-CQG-2008` | `LIT-OEH-2025` |
| `V3-F08` | `LIT-PAGE-1976` | low-frequency scaling discussion in `LIT-DOLAN-CQG-2008` |
| `V3-F09` | `LIT-DOLAN-CQG-2008` | `LIT-PAGE-1976` |
| `V3-F10` | `LIT-FOLACCI-OEH-2019` | `LIT-DOLAN-LONG-2008` |
| `V3-F11` | `LIT-YRW-1954` | gravitational application in `LIT-DOLAN-CQG-2008` |
| `V3-F12` | `LIT-DOLAN-LONG-2008` | Schwarzschild limit of `LIT-DOLAN-CQG-2008` Eq. (2) |
| `V3-F13` | `LIT-DOLAN-CQG-2008` | historical/qualitative `LIT-HANDLER-MATZNER-1980`; Regge-pole context `LIT-FOLACCI-OEH-2019` |
| `V3-F14` | `LIT-MARTEL-POISSON-2005` | `LIT-RW-1957`, `LIT-ZERILLI-1970`, `LIT-MONCRIEF-1974` |

## Locator and evidence policy

- Every blocking scientific formula has a primary-paper equation locator.
- Numerical values from plots are not frozen by eye. Handler--Matzner,
  Dolan, and Folacci figures are qualitative regression unless a later task
  obtains author tables or creates a separately reviewed digitization artifact.
- DOI/publisher and arXiv copies may be used interchangeably for inspection,
  but later artifacts record the exact file hash actually used.
- A changed source role, formula, or conversion requires a new artifact
  revision and T7 review. Bibliographic metadata-only corrections may be
  classified under the liveness protocol without changing science bytes.
