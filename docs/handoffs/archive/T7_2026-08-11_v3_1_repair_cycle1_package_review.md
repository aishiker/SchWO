# T7 V3.1 bounded repair cycle 1 package review

Date: 2026-08-11

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1 REPAIR CYCLE 1 PACKAGE READY FOR T4
```

```yaml
review_id: t7_v3_1_repair_cycle1_package_review
gate_id: phase6_v3_1_repair_cycle1_pre_execution_package
attempt: repair_1
reviewer_task: formal SchWO T7
reviewed_candidate:
  root: configs/phase6_v3_1_repair_cycle1_package.json
  identities:
    - {path: configs/phase6_v3_1_repair_cycle1_package.json, sha256: a439c5c0f93c8ae4ce5b01e8e6a1d98c8f55eb150615177ccfb5b2a1ee786255, mode: "0444", nlink: 1}
    - {path: docs/phase6_v3_1_repair_cycle1_design.md, sha256: 710eecce86e7372c837335ef630cfda94e4e718ac1f7490773e15fa11f349270, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t4_v3_1_repair_cycle1.md, sha256: 40324abfede42f5ce484d34909cd1a20eeaf2e9cc35b290a8f40921af116f0d2, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_delta_review_cycle1.md, sha256: 6b247f5736813d2ba9eb9ea415688a21dd7dc4948659f8bd21d747f90be0498e, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_repair_package_review.md, sha256: 1485857eb0fc9151261031f976daa90234abe4a9b493f1b039cdc5b37e30d1f4, mode: "0444", nlink: 1}

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_repair_package_review.md
    sha256: 1485857eb0fc9151261031f976daa90234abe4a9b493f1b039cdc5b37e30d1f4
  initial_review:
    path: docs/handoffs/archive/T7_2026-08-11_v3_1_initial_failure_review.md
    sha256: d0cb93d0ade94d0376a09e4207d6059558c04c2b45383fcb42039525dad2d7c5
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - {id: V3.1 exact 16-field threshold set, value: unchanged, units: mixed as individually frozen, source_path: configs/phase6_v3_0_thresholds.json, source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a}
  blocking_criteria:
    - v31_route_a_first_node_native_failure
    - v31_official_runner_incomplete_scope
  protected_identities:
    - {path: src/schwgw/numerics/radial_solver.py, expected_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_start_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_end_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9}
    - {path: src/schwgw/numerics/conditioned_radial.py, expected_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_start_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_end_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2}
    - {path: src/schwgw/numerics/scaled_tortoise_radial.py, expected_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_start_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_end_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df}
    - {path: src/schwgw/numerics/adaptive_jost_radial.py, expected_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_start_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_end_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896}
    - {path: src/schwgw/numerics/matching.py, expected_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_start_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_end_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340}
    - {path: src/schwgw/numerics/physical_boundary_radial.py, expected_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_start_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_end_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f}
    - {path: src/schwgw/numerics/boundary_conditions.py, expected_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_start_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_end_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22}

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1 REPAIR CYCLE 1 PACKAGE READY FOR T4

incremental_review_state:
  passed_items:
    - {item_id: v31_package_exact_identity, evidence_identity: five regular 0444/nlink1 files; manifest and four member hashes exact}
    - {item_id: v31_two_blocker_scope_exact, evidence_identity: package names both and only v31_route_a_first_node_native_failure and v31_official_runner_incomplete_scope}
    - {item_id: v31_route_a_repair_contract, evidence_identity: byte-frozen solve_scaled_tortoise_radial_at_radius only; exact 20-node union per 496 keys; 9,920 calls; no result-dependent fallback or favorable baseline}
    - {item_id: v31_route_b_ap_repair_contract, evidence_identity: 102 exact low/turning/evanescent independent odd/even keys; 306 precision nodes plus 152 turning-boundary nodes equals 458; no protected SchWO radial import}
    - {item_id: v31_route_c_external_contract, evidence_identity: 23 fresh odd-only BHPT ReggeWheeler MST records; kernel 70ad9d85...046c; commit 2e012092...981; no internal fallback or independent-even claim}
    - {item_id: v31_complete_orchestration_gate, evidence_identity: same production path must synthetically publish/reload exact 496/9920/102/458/23, all 16 thresholds and five ordered certificates before real science}
    - {item_id: v31_real_sentinel_gate, evidence_identity: exact formerly failed 20-node key plus parity/stratum/AP/external sentinels and runtime/disk projection are mandatory before official root creation}
    - {item_id: v31_publication_and_provenance_repair, evidence_identity: compact one-object-per-line JSONL plus complete start/end accepted/protected/source/runtime ledgers and independent raw-record rebuild}
    - {item_id: v31_fresh_r2_and_failure_isolation, evidence_identity: only fresh no-overwrite UTC-Z r2 root permitted; both r1 roots remain immutable, denylisted and non-resumable}
    - {item_id: v31_liveness_bound, evidence_identity: cycle 1 of maximum 2; delta prompt rechecks only two failed items, passed invariants, protected identities and class-C reload repairs}
  failed_items: []
  partial_allowed_items:
    - {item_id: v31_common_absolute_phase, reason: remains the frozen convention-budget PARTIAL/nonclaim}
    - {item_id: v31_full_domain_v1_independent_certification, reason: remains PARTIAL outside this package gate}
  not_assessed_items:
    - {item_id: v31_route_a_science, reason: no repair-cycle-1 sentinel or official Route-A science has run}
    - {item_id: v31_route_b_ap_science, reason: no repair-cycle-1 AP science has run}
    - {item_id: v31_route_c_external_science, reason: runtime/source contract is bound but no repair-cycle-1 external records exist}
    - {item_id: v31_threshold_and_certificate_outcomes, reason: all 16 outcomes and five certificates await a future complete r2 candidate}
    - {item_id: v31_v3_2_and_full_domain, reason: outside scope and forbidden}

findings:
  - finding_id: v31_package_science_not_yet_executed
    class: NONBLOCKING_LIMITATION
    summary: Package adequacy does not prove that the protected Route-A sentinel, AP route, external route or terminal thresholds will pass; the package correctly fails closed before or during an official run.
  - finding_id: v31_future_v3_2_work
    class: FOLLOW_UP_DEBT
    summary: V3.2 and broader absorption/scattering claims remain separately gated and unauthorized.

delta_review:
  reviewed_failed_items:
    - v31_route_a_first_required_node
    - v31_complete_producer_route_coverage
  passed_invariants_rechecked:
    - v31_frozen_authorities
    - v31_inventory_contract
    - v31_anchor_inventory
    - v31_external_runtime_current_identity
    - v31_fail_closed_claim_state
    - v31_direct_flux_pure_algebra
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - SHA-256/stat/nlink checks for the manifest and all four members
    - direct JSON reload and independent domain/anchor arithmetic from frozen configs
    - source inspection of the protected scaled-tortoise public API and its unit-incoming amplitude/current semantics
    - independent rehash of eight V3.0 authorities, original V3.1 prompts, D-union, V1/V2 manifests, initial T7 archive and seven protected radial sources
    - git diff --check on the five package files
    - read-only failed-root manifest/permission/membership, fresh-r2 absence, process and transient checks
  results:
    - package/member hashes and 0444/nlink1 state exact; diff-check PASS
    - domain reconstructs 248 pairs/496 modes; AP sets are disjoint 40 low + 38 turning + 24 evanescent = 102; AP nodes 102*3 + 38*4 = 458
    - Route-A union is 3 r_in + 16 outer/Jost + 3 tolerance minus two repeated baselines = 20 unique nodes; total 9,920
    - external selector reconstructs 23 unique odd-only anchors
    - all 16 V3.1 frozen threshold records remain byte-bound and unchanged
    - original r1 manifests remain f2320d5d...9bb8c and 78ee1b9b...e0e319; no r2 root, related science process, link, lock, tmp or partial output exists
    - protected and package identities match at review start and end

non_claims:
  - This package GREEN is pre-execution authorization only; V3.1 science remains NOT_ASSESSED.
  - No Route-A/AP/external record, threshold or certificate is accepted by this review.
  - No V3.2 authorization, full-domain V3 certification, Li figure equivalence or global GREEN.

repair_cycle:
  completed_bounded_repairs: 0
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Independent contract conclusions

The Route-A count is not a duplicated-node overcount: its three axes contain
the same baseline, so the exact union is `3 + 16 + 3 - 2 = 20` unique tuples
per mode. The baseline is fixed before results, all 496 keys receive the full
graph, and the original failed key must pass all 20 nodes before an official
root can exist. The public backend's unit-incoming convention is explicit in
the protected source: `A_in=1`, `A_out=A_out/A_in` and
`T_horizon=1/A_in^(horizon-normalized)`. This preserves the frozen S/current/
flux algebra rather than assuming an unavailable raw coefficient.

The AP union independently reconstructs as 40 low, 38 turning and 24
evanescent keys with zero overlap. All 102 receive the 80/120/180-digit
precision ladder; the 38 turning keys additionally receive two horizon,
one outer and one Jost variant at 180 digits. This gives exactly 458 nodes.
The complete Route-A 20-node graph supplies the mandatory all-mode boundary
systematics, while Route B retains independent turning-boundary evidence and
independent low/evanescent AP precision/log-domain evidence. No frozen
threshold, missing-data rule or parity requirement is relaxed.

The synthetic gate is structurally meaningful because it must traverse the
same full orchestration and independently reload raw records, thresholds and
certificates; its three explicit non-science flags prevent promotion. Real
sentinels, protected/source rehashes and resource projection remain separate
mandatory gates. Any inability of the frozen backend, AP route or external
runtime to satisfy them stops before official science.

This decision authorizes Root T0 only to dispatch the exact bounded T4 cycle-1
package. It does not itself authorize or accept V3.1 science and does not
authorize V3.2.
