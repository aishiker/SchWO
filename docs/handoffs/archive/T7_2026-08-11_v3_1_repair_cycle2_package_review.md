# T7 V3.1 final bounded repair cycle 2 package review

Date: 2026-08-11

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1 REPAIR CYCLE 2 PACKAGE READY FOR T4
```

```yaml
review_id: t7_v3_1_repair_cycle2_package_review
gate_id: phase6_v3_1_repair_cycle2_pre_execution_package
attempt: repair_2
reviewer_task: formal SchWO T7
reviewed_candidate:
  root: configs/phase6_v3_1_repair_cycle2_package.json
  identities:
    - {path: configs/phase6_v3_1_repair_cycle2_package.json, sha256: 5bce1966b76c85b49c79cb7d98c481403a4b5006bb48bd2d4d47ea67f879b2c4, mode: "0444", nlink: 1}
    - {path: docs/phase6_v3_1_repair_cycle2_design.md, sha256: 746d8753408bdb74cd1a9597108a63cf3c67842dc6cbedcbbb56fb68c0f967a7, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_repair_cycle2_package_review.md, sha256: 27022e735bd61ce7aa41eee26c77f52de77df5aa69ee56d5a41b99b7ec420b19, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t4_v3_1_repair_cycle2.md, sha256: f2d0b45613ca8c10c5b36715379f215644dce31079e577ff11279b478ec81ed9, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_delta_review_cycle2.md, sha256: 8bab4d149876e3876559db021340be1a6151bf6c9c1cd6bcfc29ec653ae29724, mode: "0444", nlink: 1}

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_repair_cycle2_package_review.md
    sha256: 27022e735bd61ce7aa41eee26c77f52de77df5aa69ee56d5a41b99b7ec420b19
  initial_review:
    path: docs/handoffs/archive/T7_2026-08-11_v3_1_initial_failure_review.md
    sha256: d0cb93d0ade94d0376a09e4207d6059558c04c2b45383fcb42039525dad2d7c5
  cycle1_delta_review:
    path: docs/handoffs/archive/T7_2026-08-11_v3_1_repair_cycle1_delta_review.md
    sha256: cbd04d5bba74fef2daffca62f9e80c5c0a6589f89b35812aa8ce10a60592f55b
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
GATE_LABEL: ACCEPT GREEN / V3.1 REPAIR CYCLE 2 PACKAGE READY FOR T4

incremental_review_state:
  passed_items:
    - {item_id: v31_cycle2_package_exact_identity, evidence_identity: five regular 0444/nlink1 files; package and four member hashes exact}
    - {item_id: v31_two_blocker_scope_exact, evidence_identity: package addresses both and only v31_route_a_first_node_native_failure and v31_official_runner_incomplete_scope}
    - {item_id: v31_frozen_authorities, evidence_identity: exact-eight V3.0 authorities, current V1/V2 manifests, D-union plan, cycle-1 chain, both r1 manifests and seven protected hashes unchanged}
    - {item_id: v31_inventory_contract, evidence_identity: independent reconstruction gives 11 frequencies, ellmax 16/16/16/16/17/17/19/21/26/37/58, 248 pairs and 496 odd/even modes}
    - {item_id: v31_continued_jost_geometry_policy, evidence_identity: n_aux is the first member of fixed [0,1,2] satisfying omega*2^n*r_match >= 4*sqrt(ell*(ell+1)); r_aux is fixed before results and final matching remains at r_match}
    - {item_id: v31_continued_jost_normalization, evidence_identity: exact positive-column-rescaling algebra gives log|a_i|=log|c_i|+L_h-L_i, S_raw=a_out/a_in and T=T_aux/a_in; frozen S/current/direct-Gamma/S-route-Gamma formulae preserved without clipping}
    - {item_id: v31_route_a_repair_contract, evidence_identity: exact unchanged 20-node union for every 496 keys, one protected call per logical node, 9,920 total, no cached-node substitution, fallback or favorable replacement}
    - {item_id: v31_route_b_ap_repair_contract, evidence_identity: separately implemented mpmath RW/Zerilli/Jost continuation; disjoint 40 low + 38 turning + 24 evanescent keys = 102 and 102*3+38*4=458 nodes; odd/even independently integrated}
    - {item_id: v31_route_c_external_contract, evidence_identity: 23 independently reconstructed odd-only fresh BHPT MST anchors; kernel SHA 70ad9d85...046c and clean source commit 2e012092...981; no internal fallback or independent-even claim}
    - {item_id: v31_complete_orchestration_gate, evidence_identity: same production path must synthetically publish/reload exact 496/9920/102/458/23, all 16 frozen thresholds and five ordered certificates before official science}
    - {item_id: v31_publication_and_provenance_repair, evidence_identity: compact one-object-per-line JSONL, complete source start/end ledger, raw-record rebuild, O_EXCL/single-writer/fsync and fail-closed resume/terminal rules are mandatory}
    - {item_id: v31_preexecution_and_failure_isolation, evidence_identity: exact first-key 20/20, shadow/direct, fixed Route-A/AP/external sentinels, synthetic reload, runtime/disk and quality gates precede one fresh r3 root; either r1 and cycle-1 diagnostic remain immutable}
    - {item_id: v31_liveness_bound, evidence_identity: final cycle 2 of maximum 2; same blocker after delta review 2 requires ESCALATE / T0 ADJUDICATION REQUIRED and cycle 3 is forbidden}
  failed_items: []
  partial_allowed_items:
    - {item_id: v31_common_absolute_phase, reason: remains the frozen convention-budget PARTIAL/nonclaim}
    - {item_id: v31_full_domain_v1_independent_certification, reason: remains PARTIAL outside this package gate}
  not_assessed_items:
    - {item_id: v31_route_a_science, reason: cycle-2 implementation and sentinels have not run; no r3 Route-A evidence exists}
    - {item_id: v31_route_b_ap_science, reason: no cycle-2 AP computation exists}
    - {item_id: v31_route_c_external_science, reason: runtime/source identity is bound but no cycle-2 external record exists}
    - {item_id: v31_threshold_and_certificate_outcomes, reason: all 16 outcomes and five certificates await a future complete r3 candidate}
    - {item_id: v31_class_c_publication_repairs, reason: compact JSONL and complete source-ledger execution await synthetic and official reload evidence}
    - {item_id: v31_v3_2_and_full_domain, reason: outside scope and forbidden}

findings:
  - finding_id: v31_cycle2_package_science_not_yet_executed
    class: NONBLOCKING_LIMITATION
    summary: Package adequacy does not establish that the continued-Jost, AP, external, threshold or certificate gates will pass. The contract correctly stops before an official root on any failed pre-execution gate and makes a post-launch scientific failure terminal.
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
    - v31_artifact_identity_and_immutability
    - v31_external_runtime_current_identity
    - v31_fail_closed_claim_state
    - v31_direct_flux_pure_algebra
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - SHA-256/stat/mode/nlink checks for the package manifest and all four members
    - independent JSON/domain/anchor/threshold arithmetic from frozen configs without importing the producer
    - direct source inspection of protected scaled-tortoise propagation, Jost basis, unit-incoming normalization and signed-current conventions
    - independent rehash of eight V3.0 authorities, current V1/V2 manifests, D-union, initial/cycle-1 T7 archives, cycle-1 T4 blocker/sentinel, both r1 manifests, seven protected sources and external kernel/commit
    - git diff --check on the five package files
    - read-only r2/r3 absence, process, link, lock, tmp, partial and quarantine checks
  results:
    - supplied status and T0 hashes match c2adf8cb...302ab and ebd829e4...48ff6; pre-review T7 current is 760d42a2...cbce7
    - package/member hashes, sizes and 0444/nlink1 state exact; scoped and repository diff-check PASS
    - domain reconstructs 248 pairs/496 modes; Route-A union is 3+16+3-2=20 unique nodes and 9,920 protected calls
    - AP sets are disjoint 40+38+24=102; AP node total is 102*3+38*4=458; external selector gives 23 unique odd-only anchors
    - the first 16 frozen threshold records are the exact V3.1 set; values/operators/domains remain bound to SHA-256 91fbe1a7...ac4a
    - coefficient/transmission normalization, signed currents, direct log-Gamma and independent S-route Gamma are algebraically consistent with the protected public solver and V3-F01--F04
    - original r1 manifests remain f2320d5d...9bb8c and 78ee1b9b...e0e319; no r2/r3 root, related science process, link, lock, tmp, partial or quarantine output exists
    - protected, package, predecessor and current authority identities match at review start and end

non_claims:
  - This package GREEN accepts only the final bounded pre-execution repair plan; V3.1 science remains NOT_ASSESSED.
  - No Route-A, AP or external record, threshold outcome or certificate is accepted by this review.
  - No protected radial backend is modified or newly accepted.
  - Route A and Route B are independent only if the future implementation shares no numerical code; Route C remains odd-only and supplies no independent even solve.
  - No V3.2, full-domain V3 certification, angular scattering, glory, finite-radius observer, Li equivalence or global GREEN is authorized.

repair_cycle:
  completed_bounded_repairs: 1
  current_cycle: 2
  maximum_bounded_repairs: 2
  same_substantive_blocker_remaining: true
  t0_adjudication_required: false
  terminal_rule: if either substantive blocker remains after delta review 2, return ESCALATE / T0 ADJUDICATION REQUIRED; no cycle 3
```

## Independent contract conclusions

The continued-Jost repair does not replace a failed requested node by a farther
passing node.  It fixes the coefficient-extraction basis: the physical state
is produced once with the protected solver using a deterministic auxiliary
initialization radius, while the same `a_0=1` Jost columns are propagated back
and matched at the original frozen radius.  For a common physical-state scale
`L_h` and independent column scales `L_-`, `L_+`, the coefficient rule
`log|a_i|=log|c_i|+L_h-L_i` is exact.  Re-normalizing by `a_in` therefore gives
`A_out=a_out/a_in` and `T=T_aux/a_in`; positive-real rescaling preserves phase.

The geometry rule is fixed before cycle-2 execution and depends only on
`omega`, `ell` and the requested ladder node.  For the original failed key it
maps multipliers `1/2/4/8` to `n_aux=2/1/0/0`, but all four requested match
radii and the complete 20-node graph remain mandatory.  The fixed first-key,
shadow/direct, stratum, AP and external sentinels prevent this algorithmic
choice from becoming favorable result selection.

This decision authorizes Root T0 only to dispatch the exact frozen cycle-2 T4
package.  It does not authorize T7 to run the implementation, create an
official root, accept V3.1 science or start V3.2.
