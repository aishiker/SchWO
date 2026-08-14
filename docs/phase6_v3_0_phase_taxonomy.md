# Phase 6 V3.0 phase taxonomy

Scientific stage: `V3.0`

Artifact revision: `r1`

Created at: `2026-08-11T11:27:39Z`

Assessment scope: convention/evidence readiness, not V3 numerical validation

`PASS` means the phase class has an explicit, internally consistent contract
and source bridge. It does not mean a V3 producer has numerically passed.
`PARTIAL` means the bounded observables are still usable but an absolute phase
claim remains prohibited. `NOT_ASSESSED` would mean no executable contract.

## Frozen assessments

| ID | Phase class | Status | Evidence and exact convention | V3.1 effect | V3.2 effect | V3.3 effect | V3.4 effect |
|---|---|---|---|---|---|---|---|
| `PHASE-01` | common retarded-time origin | `PASS` | Existing V2 contract fixes `u=t-r_*`, `exp(-i omega t)`, and `r_*=r+2M ln(r/(2M)-1)` with no new additive constant. Radial asymptotics are `V3-F01`. | no block | no block | fixes the common phase used in analytic `f/g` mapping | fixes the partial-wave/geodesic phase reference |
| `PHASE-02` | frequency-dependent common phase | `PARTIAL` | V2 absolute phase remains `PARTIAL`. Dolan PRD 77 Eqs. (11)--(20) exposes the common `Phi=-4M omega ln(4M omega)` and notes its cross-section irrelevance. SchWO records but does not claim an independently certified absolute common phase at every frequency. | no block: `|S|`, flux, Gamma are invariant | no block: absorption is phase invariant | absolute complex `f`/`g` phase claim prohibited; cross section and relative/helicity phase remain eligible | no block for intensity/peak/width; absolute complex glory phase prohibited |
| `PHASE-03` | `ell`-dependent phase | `PASS` | `S_l=(-1)^(l+1)A_out/A_in` with fixed leading Jost coefficient and fixed `r_*`; no `ell`-dependent rephasing. Dolan PRD 77 Eqs. (8), (13)--(14), and Folacci Eq. (9). | complex-S comparison eligible | not required for total absorption but retained | mandatory condition satisfied | mandatory condition satisfied |
| `PHASE-04` | odd/even relative phase | `PASS` | Independent odd/even solves plus `S_l^e/S_l^o=(sigma_l+12iMomega)/(sigma_l-12iMomega)` from Dolan Eq. (9) and Folacci Eq. (12). Parity-derived even is forbidden as independent evidence. | parity phase/probability check eligible | equal-probability reduction allowed only after independent solve | helicity-preserving/reversing combination is defined | spin-2 helicity/glory channel is defined |
| `PHASE-05` | total/free/scattered reference phase | `PASS` | Free reference is exactly `S_l=1`; Folacci Eqs. (1)--(4) give plus coefficient `(S_e+S_o)/2-1` and minus coefficient `(S_e-S_o)/2`. Ordinary total-plane-wave summation at null infinity is forbidden. | S reference fixed | no block | mandatory `S-1` identity closed | mandatory `S-1` identity closed |
| `PHASE-06` | Coulomb/long-range phase subtraction | `PASS` | The physical long-range phase remains inside `S_l`; free subtraction is explicit, and Yennie reduction acts on the resulting scalar series. No unsourced modewise Coulomb rephasing is introduced. The forward distribution is excluded by domain. Evidence: Dolan CQG Sec. 5.3; Folacci Eqs. (1)--(4); Yennie Eqs. (47)--(50). | no block | no block | required dependency closed for the frozen `theta>=5 deg` domain | required dependency closed for the frozen backward window |
| `PHASE-07` | spin-weighted-harmonic phase convention | `PASS` | Existing V2 Condon--Shortley/spin-harmonic convention is retained. Axis value `|_-2Y_l2(0)|^2=(2l+1)/(4pi)` fixes absorption degeneracy; the adopted Folacci differential-operator representation fixes the helicity channel without a new arbitrary harmonic phase. | mode/helicity weight fixed | degeneracy fixed | required dependency closed | Bessel/helicity channel fixed |

## Branch predicate inputs

These are T1 contract-readiness inputs, not self-authorization. Formal branch
authorization belongs to the independent T7 V3.0 verdict.

```text
absorption_contract_complete_candidate: true
phase_sensitive_scattering_contract_complete_candidate: true
common_absolute_phase_certified: false
```

The absorption candidate is complete because mode amplitudes, direct positive
flux, `Gamma_flux`, independent `Gamma_S`, total weights, domains, anchors,
log policy, and thresholds are frozen. `PHASE-02=PARTIAL` does not affect any
absorption observable.

The phase-sensitive scattering candidate is eligible because `PHASE-03`,
`PHASE-04`, `PHASE-05`, `PHASE-06`, and `PHASE-07` are all `PASS`. The
remaining common-phase limitation forbids only an absolute complex-amplitude
phase claim. It does not block `d sigma/d Omega`, odd/even relative phase,
helicity composition, or glory peak/width/amplitude.

## Failure semantics for later stages

- Drift in `PHASE-03`, `PHASE-04`, or `PHASE-05` is a V3.3/V3.4 blocker.
- An unreviewed Coulomb subtraction or harmonic convention change is a
  V3.3/V3.4 blocker.
- `PHASE-02=PARTIAL` must be carried as convention uncertainty and a nonclaim;
  it cannot be silently promoted by choosing a fitted overall phase.
- A phase failure in V3.3/V3.4 does not retroactively invalidate a truthful
  V3.1/V3.2 absorption result.
- Findings and repair cycles follow
  `docs/review_gate_liveness_protocol.md`; out-of-claim suggestions are not
  retrospective current-gate blockers.
