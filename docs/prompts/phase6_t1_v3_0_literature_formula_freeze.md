# Phase 6 V3.0 — T1 primary-literature, formula, phase, domain and threshold freeze

Date frozen by T0: 2026-08-11

Scientific stage: `Phase 6 / V3.0`

Artifact revision: `r1`

Execution class: literature and control-plane only; zero science computation

You are the existing formal **T1 literature and physical-conventions task** for
SchWO. Work in the shared repository
`/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO`.

This prompt is a bounded V3.0 task. It does not authorize V3.1, a radial solve,
a partial-wave sum, an absorption scan, a glory calculation, or any change to a
frozen V1/V2 convention or science artifact.

## 1. Read and verify before editing

Read in order:

1. `project.md`
2. the YAML current-state header and latest V3 entries in `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T1_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/review_gate_liveness_protocol.md`
7. `docs/templates/t7_gate_verdict_template.md`
8. `docs/prompts/phase6_v3_master_prompt.md`
9. `docs/phase6_v2_to_v3_transition.md`
10. `docs/phase6_independent_physical_validation.md`
11. `docs/phase6_v2_selected_domain_closeout.md`
12. `configs/phase6_v2_0_convention_contract_20260810.json`
13. `configs/phase6_v2_0_selected_domain_20260810.json`
14. `references/manifest.md`
15. `docs/equation_map.md`
16. `docs/physics_spec.md`

At the start and end, rehash these frozen inputs:

- V3 master prompt:
  `f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7`
- V2.0 convention contract:
  `1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`
- V2.0 selected domain:
  `9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`
- current V2 release manifest:
  `51ddf1580448382be7e182f92cf76bbf53ed39f15418af9e546f357979c743eb`
- current V1 radial manifest:
  `2ceb769e9f67f0a66f115aba23a82d573e400ea155741b7801cfbfcd501a4728`
- current V1 production-state manifest:
  `7508ec43ba066d97acb00e8745b33ee3f422b2a8819c30874a4a03c22b8616f4`
- current V1 selected-independent manifest:
  `aa66df4f449372e1af660cee8b0757d23ab494bd631bde1c229eb2ee29a2d78c`

Also rehash the seven protected radial files and the D-union plan using the
identities in the V2.0 convention contract/current V2 source map. If anything
does not match, make no edits and return:

`HOLD / V3 FROZEN INPUT IDENTITY MISMATCH`

Include exact path, expected/observed hash, owner, unblock condition, and
whether independent downstream work may proceed.

## 2. Literature method

Use the available academic/arXiv literature capabilities and primary sources.
Do not freeze an equation from model memory or from Li–Hou–Zhao alone. For each
scientific formula or asymptotic claim, record a primary-source equation/page
locator when available, the source convention, the conversion to the SchWO
convention, units, assumptions and applicability domain. If two sources use
incompatible normalizations, preserve both and derive the conversion rather
than silently choosing one.

At minimum, independently locate and assess:

- Handler & Matzner, *Gravitational wave scattering*, Phys. Rev. D 22 (1980);
- Dolan, *Scattering of long-wavelength gravitational waves*, Phys. Rev. D 77
  (2008);
- Dolan, *Scattering and absorption of gravitational plane waves by rotating
  black holes*, Class. Quantum Grav. 25 (2008), explicitly taking and checking
  its Schwarzschild limit;
- Folacci & Ould El Hadj, gravitational-wave scattering by Schwarzschild,
  Phys. Rev. D 100 (2019);
- the primary source for the adopted series-reduction recurrence;
- Regge–Wheeler, Zerilli, Moncrief and Martel–Poisson normalization sources;
- Sánchez or other classic absorption sources only where needed and with an
  exact role in the evidence matrix.

Prefer DOI/publisher/arXiv records and primary papers. Record stable identifiers
and access URLs. Obey source quotation limits: summarize and derive; do not copy
long passages.

## 3. Required outputs

Create exactly these V3.0 authority candidates:

1. `docs/phase6_v3_0_validation_contract.md`
2. `docs/phase6_v3_0_formula_map.md`
3. `docs/phase6_v3_0_phase_taxonomy.md`
4. `docs/phase6_v3_0_literature_matrix.md`
5. `configs/phase6_v3_0_domain.json`
6. `configs/phase6_v3_0_thresholds.json`
7. `configs/phase6_v3_0_external_anchor_matrix.json`
8. `references/notes/phase6_v3_absorption_scattering_conventions.md`

You may also append V3 primary-source entries to `references/manifest.md`, and
append strictly scoped V3 mappings to `docs/equation_map.md` and
`docs/physics_spec.md`. Do not alter or reinterpret existing frozen V1/V2
mappings. Update `docs/handoffs/T1_current.md` and create a dated T1 archive
handoff. Do not edit another task's current handoff or `status.md`; T0 will
transcribe the checkpoint after independent review.

No other file is writable. In particular, do not modify `src/`, `scripts/`,
`tests/`, `runs/`, V1/V2 configs, immutable artifacts, protected radial files,
Li artifacts, or any frozen V2.0 convention.

All three JSON configs must be canonical, machine-readable and self-describing.
Use UTC timestamps with trailing `Z` and include at least:

- `schema`;
- `scientific_stage: "V3.0"`;
- `artifact_revision: 1`;
- `created_at_utc`;
- `timezone: "UTC"`;
- exact upstream identities;
- `global_green_permitted: false`;
- explicit nonclaims.

## 4. Objects that must be frozen

### 4.1 Mode-level scattering and absorption

Freeze under the SchWO `exp(-i omega t)` convention:

- incident, reflected and horizon-transmitted master amplitudes;
- complex `S_l^(odd/even)` including the Jost/free reference phase;
- signed Wronskian currents versus positive physical fluxes;
- `Gamma_flux = F_H/F_in`;
- `Gamma_S = 1-|S_l|^2` as an independent consistency route, never as the
  source of the direct horizon route;
- reflection and transmission/absorption probabilities;
- independent odd/even solve requirements and the bounded parity relation;
- log-domain representation for extremely small positive `Gamma`.

State every normalization, degeneracy/helicity/parity weight, sign, dimension,
boundary limit and applicability condition.

### 4.2 Total absorption cross section

Freeze the exact partial and total cross-section normalization, `ell` start,
parity/helicity weights, units (`M^2` and/or `sigma/M^2`), frequency variable,
continuous multipole requirements, `ell_max` ladder, tail bound, low-frequency
law and high-frequency capture limit. State whether oscillatory high-frequency
corrections are mandatory or diagnostic. Any `27*pi*M^2` statement must be
primary-source mapped and unit-qualified.

### 4.3 Differential scattering and helicity amplitudes

Freeze definitions of `f(theta)`, `g(theta)` and `d sigma/d Omega`; the exact
odd/even S-matrix combinations; total/free/scattered separation; the `S_l-1`
structure; Coulomb/long-range phase; forward distributional structure; adopted
series reduction/analytic subtraction and recurrence; forward exclusion;
reduction-order, angle-grid and `ell_max` ladders. The contract must explicitly
forbid an ordinary total-plane-wave sum at null infinity.

### 4.4 Analytic benchmarks

Re-derive/map the spin-2 Schwarzschild low-frequency differential cross section,
including normalization, helicity convention, error order, angle/frequency
domain and forward exclusion. Do not freeze the familiar
`[cos^8(theta/2)+sin^8(theta/2)]/sin^4(theta/2)` expression without a primary
source and explicit conversion.

Freeze the geometric-optics capture cross section and backward-glory benchmark:
critical impact parameter, spin-2 Bessel order, glory impact parameter,
`|db/dtheta|` at `theta=pi`, amplitude/peak/width observables, comparison domain
and asymptotic-error policy.

### 4.5 Phase taxonomy and branch authorization inputs

For each item below, set `PASS`, `PARTIAL` or `NOT_ASSESSED`, attach evidence and
state its effect on V3.1, V3.2, V3.3 and V3.4:

1. common retarded-time origin;
2. frequency-dependent common phase;
3. `ell`-dependent phase;
4. odd/even relative phase;
5. total/free/scattered reference phase;
6. Coulomb/long-range phase subtraction;
7. spin-weighted-harmonic phase convention.

Common overall phase may remain PARTIAL for absorption. V3.3/V3.4 are NO-GO
unless the `ell`-dependent, odd/even-relative and total/free/scattered reference
phases are PASS and the Coulomb/harmonic dependencies required by the chosen
formulae are explicitly closed.

### 4.6 Domain, anchors and thresholds

Freeze separate domains for V3.1, V3.2, V3.3 and V3.4. The V2 sparse 30-key set
is inherited control only and may not stand in for a V3 continuous low/high
frequency or multipole domain. Include ordinary, critical-barrier/turning,
evanescent/high-ell and low/mid/high-`kM` strata as applicable.

Freeze independent external anchors and arbitrary-precision anchors with exact
backend/source roles. Never describe parity-derived even data as an independent
even solve.

Before any producer exists, freeze thresholds for:

- complex S;
- log Gamma;
- direct flux balance and `Gamma_flux` versus `Gamma_S`;
- parity probability;
- precision, `r_in`, `r_out`/Jost-order and tolerance ladders;
- adjacent `ell_max`, tail bound and angle-grid changes;
- analytic-limit and external-backend error;
- series-reduction order;
- glory peak, width and amplitude.

Every threshold entry must include a stable field ID, observable, value and
comparison operator, units, exact domain, rationale, source/derivation and
whether it is blocking for V3.1, V3.2, V3.3 or V3.4. Do not copy a V1/V2 radial
threshold into a new observable merely for convenience.

## 5. Contract governance and nonclaims

The validation contract must freeze:

- exact stage dependencies and branch authorization predicates;
- separate numerical and convention uncertainty budgets per accepted result;
- finding/liveness semantics from `docs/review_gate_liveness_protocol.md`;
- no post-producer threshold or domain changes;
- primary-source identities and equation-map identities;
- protected V1/V2 identities;
- fresh/no-overwrite immutable artifact rules for later producers;
- per-observable/per-domain acceptance only;
- `global_status=null` and `global_green_permitted=false` for later releases.

Mandatory nonclaims include: no full-domain V1/V2/V3 certification; no global
GREEN; no Li figure equivalence; no finite-radius observer/detector response;
no total-plane-wave infinity sum; no V3 science execution in V3.0.

## 6. Verification and handoff

Perform only documentation/config validation:

- JSON parse and canonical serialization checks;
- internal cross-reference and SHA-256 checks;
- equation dimensions/sign/convention audit;
- source-locator completeness audit;
- exact domain/threshold/anchor schema checks;
- `git diff --check` scoped to your files;
- start/end protected identity rehash;
- read-only process check proving no V3 producer was started.

Do not run the radial solver, partial-wave sums, V3 producers, a numerical
benchmark, the full test suite, or Li figure generation.

Return a file/SHA-256 ledger for every changed file and a compact statement of
which phase items are PASS/PARTIAL/NOT_ASSESSED. Do not contact T7 directly;
Root T0 will dispatch the frozen T7 review prompt.

The only successful terminal checkpoint is:

`CHECKPOINT / V3.0 ANALYTIC-LITERATURE BENCHMARK CONTRACT FROZEN`
