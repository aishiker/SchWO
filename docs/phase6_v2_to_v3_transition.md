# Phase 6 transition — V2 selected-domain closeout to bounded V3.0 freeze

Transition time: `2026-08-11T10:48:54Z`

Timezone: `UTC`

Scientific transition: `V2 closed -> V3.0 contract freeze`

Transition artifact revision: `r1`

## Adjudication

The independent V2 closeout verdict remains:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PARTIAL
GATE_LABEL: ACCEPT GREEN / V2 SELECTED-DOMAIN GAUGE-INVARIANT WAVEFORM AND FLUX VALIDATION COMPLETE
```

Root T0 applies the bounded transition authorized by the frozen V3 master
prompt:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PARTIAL
GATE_LABEL: ACCEPT GREEN / V2 SELECTED-DOMAIN VALIDATION SUFFICIENT FOR BOUNDED V3.0 CONTRACT FREEZE
```

This decision authorizes only a zero-science V3.0 literature, formula, phase,
domain and threshold freeze followed by formal T7 review. It does not authorize
V3.1 until that T7 review returns both:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
absorption_branch_authorized: true
```

It does not authorize V3.2–V3.5, a radial solve, a partial-wave sum, an
absorption/glory scan, Li figure regeneration, full-domain V3, or global GREEN.

## Frozen current authority

### V2 selected-domain release

Current root:

`runs/phase6/asymptotic_waveform/v2_selected_release_v2_20260811T083414_py314`

| File | SHA-256 |
|---|---|
| `manifest.json` | `51ddf1580448382be7e182f92cf76bbf53ed39f15418af9e546f357979c743eb` |
| `release_ledger.json` | `8bbc4d098ca64ac256a63a09e4e5744191f314038fe140c131eaf7606f75ba49` |
| `report.json` | `58157a422fabed9be8bb9956c3097296c6dfd30b8d8065d4731edf6fe5a826dc` |
| `source_map.json` | `9011a2cff8a944d68234a32cd754c7b6482b61644464fc512b906e2fbec76fb7` |
| `summary.json` | `25dcc333085e3cd7150bf9e954766ae60a942f3a6e51c20ff36a4081077045cb` |

The root was re-resolved as `0555`; its direct files are immutable regular
files. The accepted predecessor graph was parsed structurally and contains
only:

- V2.1:
  `runs/phase6/asymptotic_waveform/v2_1_mode_amplitudes_v1_20260810T184729_py314`;
- V2.2-r3:
  `runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v3_20260811T113135_py314`;
- V2.3-r2:
  `runs/phase6/asymptotic_waveform/v2_3_flux_closure_v2_20260811T050013_py314`.

The current denylisted/superseded roots are absent from
`accepted_predecessor_roots`. Historical entries explicitly labelled
superseded inside the source map are provenance, not accepted inputs.

### V1 radial authorities

| Authority | Manifest SHA-256 |
|---|---|
| `runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314` | `2ceb769e9f67f0a66f115aba23a82d573e400ea155741b7801cfbfcd501a4728` |
| `runs/phase6/radial_validation/v1_production_state_evidence_v2_20260810_py314` | `7508ec43ba066d97acb00e8745b33ee3f422b2a8819c30874a4a03c22b8616f4` |
| `runs/phase6/radial_validation/v1_radial_selected_acceptance_v1_20260810_py314` | `aa66df4f449372e1af660cee8b0757d23ab494bd631bde1c229eb2ee29a2d78c` |

All three roots were re-resolved as `0555`. The adjudication remains:

- V1 algorithmic radial domain: PASS;
- V1 production radial-state completeness: PASS;
- V1 selected independent numerical validation: PASS;
- V1 full-domain independent scientific certification: PARTIAL.

No full V1 certificate is relabelled GREEN.

### Frozen conventions and protected implementation

| Input | SHA-256 |
|---|---|
| `docs/prompts/phase6_v3_master_prompt.md` | `f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7` |
| `configs/phase6_v2_0_convention_contract_20260810.json` | `1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517` |
| `configs/phase6_v2_0_selected_domain_20260810.json` | `9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818` |
| `docs/handoffs/T7_current.md` at transition | `678ee97d8d4850049d8dd9a2d8f34c931f474408e58d8a360fbd06129dbfee4f` |

The seven protected radial files and D-union plan were rehashed against their
frozen V2 source-map identities with no drift. V3.0 may cite these inputs but
may not change them.

## Frozen V3.0 dispatch package

| Prompt | SHA-256 |
|---|---|
| `docs/prompts/phase6_t1_v3_0_literature_formula_freeze.md` | `03a352b881c97f1f767092340d5dc65f61e800dafde9c28b9f870eaa5ad454cc` |
| `docs/prompts/phase6_t7_v3_0_contract_review.md` | `74a14af6d9876ac5f29431693a27d6279c7838448c93974fc5a0812a8ad50563` |

The T1 prompt requires primary-source literature work and eight exact outputs;
it prohibits all V3 numerical science. The T7 prompt freezes the independent
review criteria before T1 begins and uses the dual-axis liveness protocol.

Required chain:

```text
formal T1 V3.0 freeze
  -> Root T0 identity/checkpoint intake
  -> formal T7 V3.0 independent review
  -> only if ADVANCE/PASS and absorption_branch_authorized=true:
     freeze the V3.1 prompts against accepted V3.0 identities
  -> formal T4 V3.1 execution
  -> formal T7 V3.1 review
```

V3.1 may not be pre-dispatched or run in parallel with V3.0. The
phase-sensitive V3.3/V3.4 branch additionally requires
`phase_sensitive_scattering_branch_authorized=true` and the exact phase
conditions in the V3.0 contract.

## Scope and nonclaims

- V2 remains selected-domain `CLAIM_STATUS=PARTIAL`, with 11 PASS certificates
  and `V2_ABSOLUTE_PHASE_CONVENTION=PARTIAL`.
- Full-domain V1 independent certification remains PARTIAL.
- Full-domain V2 and all V3 science are NOT_ASSESSED at this transition.
- Li figure agreement is not a primary gate.
- Finite-radius observer/detector response is outside this transition.
- No global GREEN is permitted.

The read-only transition preflight found no active Phase-6 solver, Wolfram,
pytest or V3 producer process and no `runs/phase6/classic_scattering` artifact.
