# Phase 6 V3.0 analytic/literature validation contract

Scientific stage: `V3.0`

Artifact revision: `r1`

Created at: `2026-08-11T11:27:39Z` (`UTC`)

Owner candidate: T1

Execution class: zero-science literature/formula/phase/domain/threshold freeze

## 1. Bounded claim

The only claim offered for independent review is:

> V3.0 has a scientifically sourced, internally consistent, and executable
> analytic/literature benchmark contract suitable for gated downstream work.

No V3 radial solve, partial-wave sum, absorption scan, glory computation,
benchmark, Li figure, or full test suite was run to create this candidate.
This document is not a V3 science result.

## 2. Authority set and immutable inputs

The eight coequal V3.0 candidate outputs are:

1. this validation contract;
2. `docs/phase6_v3_0_formula_map.md`;
3. `docs/phase6_v3_0_phase_taxonomy.md`;
4. `docs/phase6_v3_0_literature_matrix.md`;
5. `configs/phase6_v3_0_domain.json`;
6. `configs/phase6_v3_0_thresholds.json`;
7. `configs/phase6_v3_0_external_anchor_matrix.json`;
8. `references/notes/phase6_v3_absorption_scattering_conventions.md`.

Their final SHA-256 ledger belongs in the T1 handoff and the T7 verdict. A
later producer must bind all eight hashes, not only this file.

Frozen upstream identities are:

| Authority | SHA-256 |
|---|---|
| V3 master prompt | `f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7` |
| T1 V3.0 prompt | `03a352b881c97f1f767092340d5dc65f61e800dafde9c28b9f870eaa5ad454cc` |
| V2-to-V3 transition | `4493c1359974bf58abcc4b93ebe30a6ebab5edef9bc229654c873846a95bfebb` |
| dispatch-identity addendum | `5a36c7fc72fcf10241a0ae0261cf220d08830c11466660c8259bfbc71b2c16db` |
| V2.0 convention contract | `1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517` |
| V2.0 selected domain | `9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818` |
| current V2 selected-release manifest | `51ddf1580448382be7e182f92cf76bbf53ed39f15418af9e546f357979c743eb` |
| V1 final-radial manifest | `2ceb769e9f67f0a66f115aba23a82d573e400ea155741b7801cfbfcd501a4728` |
| V1 production-state manifest | `7508ec43ba066d97acb00e8745b33ee3f422b2a8819c30874a4a03c22b8616f4` |
| V1 selected-independent manifest | `aa66df4f449372e1af660cee8b0757d23ab494bd631bde1c229eb2ee29a2d78c` |
| authoritative D-union plan | `de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3` |

The seven protected radial source hashes are embedded in every V3.0 JSON
candidate. Any mismatch at a future gate is fail-closed identity drift, not a
threshold failure. Frozen V1/V2 artifacts remain immutable and are not
reinterpreted by V3.

## 3. Formula and observable contract

The binding formula IDs are `V3-F01` through `V3-F14` in the formula map.
The following points are mandatory:

- Fourier convention is `exp(-i omega t)`, with the existing fixed
  Schwarzschild tortoise coordinate.
- `A_in`, `A_out`, and `A_H` are extracted from the exact boundary limits in
  `V3-F01`.
- Complex `S_l^p` is `(-1)^(l+1) A_out/A_in`, including the fixed Jost/free
  phase. Free means `S=1`.
- Signed Wronskian currents and positive physical fluxes are distinct fields.
  `Gamma_flux=F_H/F_in` is the direct route;
  `Gamma_S=1-|S|^2` is an independent consistency route.
- Tiny positive `Gamma` is represented in log domain. A binary64 zero cannot
  pass as an extremely small absorption probability.
- Odd and even radial equations are solved independently. The exact parity
  relation is a check, never an even-sector data generator.
- The partial absorption cross section is
  `pi(2ell+1)(Gamma_odd+Gamma_even)/(2 omega^2)` and the total is the
  gap-free integer sum from `ell=2` with a frozen cutoff ladder and positive
  tail bound.
- The low-frequency absorption law is Page's
  `(256*pi/45) M^2 (M omega)^4`; the high-frequency capture scale is
  `27*pi*M^2`. Pointwise high-frequency oscillations are diagnostic.
- Differential scattering uses the exact Folacci--Ould El Hadj odd/even
  combinations and explicit `S-1` free subtraction. The adopted Yennie
  recurrence is applied to the scalar precursor series.
- The null-infinity incident-plus-scattered total plane wave must not be
  assembled as an ordinary partial-wave sum. The forward distribution is
  excluded by the frozen angle domain.
- The low-frequency spin-2 cross section and the spin-2 `J_4` glory formula
  are asymptotic benchmarks with model uncertainty separate from numerical
  uncertainty.

Primary sources, equation locators, conversions, assumptions, and exclusions
are binding through the literature matrix and convention note. Li--Hou--Zhao
is secondary regression only.

## 4. Frozen domains

`configs/phase6_v3_0_domain.json` is the machine authority. In summary:

- `V3.1` covers low/mid/high `kM`, every integer multipole through a
  photon-sphere-informed margin, both independent parities, and ordinary,
  critical-turning, and evanescent/high-ell strata. It carries precision,
  `r_in`, `r_out`, Jost-order, and tolerance ladders.
- `V3.2` uses the explicit 17-frequency grid from `kM=0.005` to `12`, a
  continuous multipole sequence, three `ell_max` levels, and a positive
  omitted-tail bound. The V2 sparse 30-key set is control only.
- `V3.3` uses blocking low frequencies `0.01, 0.02, 0.05`, angles
  `5--175 deg`, explicit forward exclusion, angle/`ell_max` ladders, and
  reduction orders `q=1,2,3` with `q=2` adopted.
- `V3.4` uses blocking high frequencies `4,6,8,12`, a
  `150--180 deg` backward window, fine angle/`ell_max`/reduction ladders, and
  exact-geodesic Schwarzschild anchors. `kM=2` is onset diagnostic only.

No domain point may be removed after a producer exists. Expansion requires a
new revision; narrowing after seeing results is forbidden.

## 5. Frozen anchors

`configs/phase6_v3_0_external_anchor_matrix.json` binds each anchor's exact
role and independence limit.

- Fresh arbitrary-precision direct RW and Zerilli integrations anchor low,
  turning, and evanescent V3.1 modes. They may not import protected SchWO
  radial code.
- External BHPT ReggeWheeler data anchor selected odd modes only and cannot
  certify an independent even solution.
- Page's formula and a separately summed AP route anchor V3.2; the
  geodesic-capture law anchors only the high-frequency scale.
- Dolan's closed low-frequency formula and a fresh external CAM/MST/direct
  route anchor V3.3.
- A radial-code-independent null-geodesic solve, the closed `J_4` formula,
  and a fresh external CAM/MST route anchor V3.4.
- Published plots are qualitative unless author tables or an independently
  reviewed digitization artifact is later frozen. No visual read-off can
  satisfy a blocking numerical anchor.

Parity-derived even values must always carry a `derived_consistency_only`
role and can never be counted as independent even anchors.

## 6. Frozen thresholds and adjudication

All thresholds predate every V3 producer and are machine-bound in
`configs/phase6_v3_0_thresholds.json`. Each entry has a stable field ID,
observable, operator, value, units, exact domain, rationale/derivation, and
blocking stages.

The threshold groups cover:

- complex S and log Gamma;
- direct flux balance and `Gamma_flux` versus `Gamma_S` in ordinary and log
  domains;
- physical probability bounds and parity probability/relative phase;
- precision, `r_in`, `r_out`/Jost-order, and ODE-tolerance ladders;
- adjacent `ell_max`, omitted tail, low/high absorption asymptotes, and
  external total-absorption routes;
- angle grid, multipole cutoff, series-reduction order, low-frequency
  scattering formula, and external scattering route;
- exact-geodesic `b_g`/derivative plus glory peak angle, FWHM, amplitude,
  numerical stability, and external backend.

Literature asymptotic tolerances are model-error budgets, not numerical
convergence budgets. A result must pass all applicable numerical gates before
an asymptotic comparator is evaluated. A loose asymptotic allowance cannot
hide a failed solver, sum, angle, or route-independence gate.

Acceptance is per observable and per declared domain. No aggregator may turn
a failed blocking field into PASS by averaging across unrelated modes,
frequencies, parities, or angles. Later release manifests must contain

```json
{
  "global_status": null,
  "global_green_permitted": false
}
```

and explicit per-field statuses.

## 7. Phase state and branch predicates

The binding taxonomy is:

| Phase class | State |
|---|---|
| common retarded-time origin | `PASS` |
| frequency-dependent common phase | `PARTIAL` |
| ell-dependent phase | `PASS` |
| odd/even relative phase | `PASS` |
| total/free/scattered reference phase | `PASS` |
| Coulomb/long-range phase subtraction | `PASS` |
| spin-weighted-harmonic phase convention | `PASS` |

The common absolute phase limitation forbids an absolute complex `f/g` phase
claim. It does not block absorption, differential intensity, relative
odd/even/helicity phase, or glory features.

Formal authorization belongs only to T7. T7 may set
`absorption_branch_authorized: true` only if V3.1/V3.2 formulae, domains,
anchors, direct flux, log policy, thresholds, and uncertainty schema are
complete and identity-bound. T7 may set
`phase_sensitive_scattering_branch_authorized: true` only if the five
required phase dependencies remain PASS and V3.3/V3.4 contracts are complete.
T1 records both as complete candidates but does not authorize either branch.

## 8. Uncertainty contract

Every accepted later record must report two independent budgets:

### Numerical uncertainty

At minimum, a structured maximum/envelope from every applicable convergence
field: precision, horizon start, outer boundary/Jost order, ODE tolerance,
route comparison, `ell_max`, tail, angle grid, reduction order, and feature
extraction. The method for combining correlated terms must be stated; default
is a conservative maximum for alternative estimates and a sum for demonstrably
independent bounded contributions. Missing applicable terms produce
`NOT_ASSESSED`, not zero uncertainty.

### Convention/observable uncertainty

At minimum:

- phase-taxonomy states and common-phase nonclaim;
- master-variable and parity/helicity conversion identity;
- direct-flux versus S-route role;
- asymptotic-model error for Page/Dolan/glory comparisons;
- source/backend independence limitations;
- forward exclusion and finite/infinite-radius applicability.

Numerical and convention budgets must never be collapsed into a single number.
An observable may be numerically precise but convention-limited, or
convention-closed but numerically failed.

## 9. Stage dependencies

```text
V3.0 T1 freeze
  -> independent T7 contract review
     -> V3.1 only if ADVANCE + PASS + absorption_branch_authorized=true
        -> fresh independent T7 V3.1 review
           -> V3.2 only under a separately frozen prompt/authorization

V3.3/V3.4
  -> only if the V3.0 T7 verdict additionally sets
     phase_sensitive_scattering_branch_authorized=true
  -> each still requires its own later frozen prompt and upstream gate
```

V3.5/full-domain closure is outside this contract. V3.0 does not dispatch T4,
T7, V3.1, or any producer.

## 10. Artifact and provenance governance

Later producers must:

1. use a fresh UTC-stamped, unique, no-overwrite root;
2. bind runtime, runner, all eight V3.0 hashes, upstream V1/V2 identities,
   domain and threshold hashes, and exact formula/source IDs;
3. write a source map, manifest, structured records, summary, and report;
4. keep failed and partial evidence immutable;
5. never reuse or enter a superseded root into the accepted predecessor graph;
6. preserve raw route values so validators are not the scientific proof;
7. report `global_status=null` and `global_green_permitted=false`;
8. undergo an independent, identity-bound T7 review before downstream use.

Post-producer threshold, domain, formula, or source-role changes are forbidden.
A necessary change creates a fresh artifact revision, new hashes, and a new
review. Metadata-only repairs must still preserve before/after identity and
follow the liveness protocol.

## 11. Review and liveness semantics

`docs/review_gate_liveness_protocol.md` and the T7 verdict template are
incorporated by reference. Reviews use the dual axes
`ADVANCE_DECISION` and `CLAIM_STATUS`. Only an
`A. BLOCKING_CURRENT_GATE` finding permits `REPAIR`; B limitations, C
control-plane repairs, and D follow-up debt do not retrospectively redefine
the frozen bounded claim. Repair cycles and HOLD conditions are exactly those
of the protocol.

For the V3.0 review, full-domain incompleteness, future V3.2--V3.5 work, Li
disagreement, and absence of global GREEN are expected nonclaims, not blockers.
Identity/evidence absence or inconsistency remains fail closed.

## 12. Mandatory nonclaims

- no full-domain V1, V2, or V3 certification;
- no global GREEN;
- no Li figure equivalence;
- no finite-radius observer or detector response;
- no total-plane-wave infinity sum;
- no V3 science execution in V3.0;
- no independently certified absolute common complex phase;
- no authorization of V3.1, V3.2, V3.3, V3.4, or V3.5 by T1;
- no claim that a parity-derived even value is an independent even solve;
- no claim that a published raster supplies a blocking numerical anchor.

This candidate becomes an accepted V3.0 contract only after an independent T7
verdict returns the exact bounded GREEN required by the frozen T7 prompt.
