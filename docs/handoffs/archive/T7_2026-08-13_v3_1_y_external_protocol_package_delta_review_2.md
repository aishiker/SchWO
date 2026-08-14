# T7 delta review 2 — V3.1-Y external protocol package

Review date: 2026-08-13 UTC

```text
ADVANCE_DECISION: ESCALATE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED
```

This is the archive-only delta review of the second and final bounded package
repair for `phase6_v3_1_y_external_protocol_v1`. It is bound to the immutable
initial review SHA-256
`1cc0da4cdfd7c9aecf7306ba7dd7b10219ce14f93e3a1c8bca37afe12417ac6b`,
delta review 1 SHA-256
`63c1ae9286fa5cb7b07ee4c2995a7cf6bb71f9e1bc941399d46861f65f1aa499`,
and current package SHA-256
`5dc0b062c7da463bb3aa4283b38060201c8d6fd7a6902dd0d677273306b9d0b7`.

The future-authority collision from delta review 1 is closed. The candidate
predeclares this distinct archive path, contains no future digest, preserves
the initial and delta-1 YELLOW archives independently, and gives T6 an exact
later-dispatch-supplied digest and token envelope.

The recurring substantive protocol blocker is not closed. The repair adds
eight typed field tables, canonical outer encodings, operation-specific
barriers and a structural stage-16-to-17 chain. However, it still does not
freeze the predicate-instance value semantics or the terminal receipt and
manifest authority needed to instantiate that chain uniquely. A conforming
implementation would have to invent acceptance bytes. Because this is delta
review 2 after bounded repair 2, the liveness protocol forbids a third
isomorphic repair and requires Root T0 adjudication.

No implementation, Wolfram kernel, BHPT/AP/radial solver, scientific call,
dispatch or run root was created or executed by this review.

## Verdict record

```yaml
review_id: t7_v3_1_y_external_protocol_package_delta_2_20260813
gate_id: phase6_v3_1_y_external_protocol_v1
attempt: repair_2
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed

reviewed_candidate:
  root: configs/phase6_v3_1_y_external_protocol_package.json
  identities:
    - {path: configs/phase6_v3_1_y_external_protocol_package.json, sha256: 5dc0b062c7da463bb3aa4283b38060201c8d6fd7a6902dd0d677273306b9d0b7, mode: "0444", nlink: 1}
    - {path: configs/phase6_v3_1_y_external_protocol_contract.json, sha256: c3d601940b8f297eb23cccad404c8ec5c326ffc6fb9a1dfa005ec6f5db3ef45c, mode: "0444", nlink: 1}
    - {path: docs/phase6_v3_1_y_external_protocol_design.md, sha256: 78fc6d2d62549ebb907c80685f41222d0e5be5f85329e071cd0510c5da20bb44, mode: "0444", nlink: 1}
    - {path: docs/phase6_v3_1_y_external_protocol_redesign_analysis.md, sha256: 4e4f6eff3b22c170bf9502d86c3d5af70d5221a5aa746ac266f77e5065c60cd0, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md, sha256: 32ec19023973a4f49801efaa9dade8fd47d97e5919befd5f7634191f50a576a5, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md, sha256: 9bd7f90e1615e82db053461a60de23389d18fbe61171f6ee7253741dc87665f0, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_y_wolfram_protocol_compatibility_review.md, sha256: 1571a13fe7e88bd03012a375dcd8abfc7c913db85c00db36f053a33f0cf0cafb, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_y_source_load_micro_review.md, sha256: 157b0e943d170c60779d4eef1a28c3086f8c89b2a88795849c32f95b4d8051d0, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md, sha256: 9a40e2334989235bfc50690046b870318678ea7e7b64e31f155582a82d0f80c4, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_y_science_review.md, sha256: c5d30024c7418888d267b9de044ae3336acbf709894d89dbf89b44d5b23e112b, mode: "0444", nlink: 1}

frozen_review_basis:
  initial_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_review.md
    sha256: 1cc0da4cdfd7c9aecf7306ba7dd7b10219ce14f93e3a1c8bca37afe12417ac6b
  delta_review_1:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_delta_review_1.md
    sha256: 63c1ae9286fa5cb7b07ee4c2995a7cf6bb71f9e1bc941399d46861f65f1aa499
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_y_external_protocol_package_review.md
    sha256: 2c4487fb3fab836f297a8b0bb405f0b51acdeb68593f901541a475cb48c8cb01
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    path: configs/phase6_v3_0_thresholds.json
    sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
    exact_v3_1_count: 16
  convention:
    path: references/notes/phase6_v3_absorption_scattering_conventions.md
    sha256: 82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a
  blocking_criteria:
    - the two delta-1 blockers must both meet their binary unblock conditions
    - the nine initial passed invariants and closed delta-1 failed items must remain frozen
    - all eight wire artifacts, every derived digest and all four operation DAGs must be uniquely reconstructible from candidate bytes
    - every field mutation must have one machine-decidable expected result before implementation
    - no implementation, runtime, dispatch, root, science or V3.2 is authorized at this package gate
  frozen_pass_subtree_sha256s:
    operation_profiles: e5022a948c909ed8dd8a1fe9f143cb2c7ba5d2b0156b08b9c20918a9283a33a3
    predicate_registry: 510858c86bc1884b4177e6b271975a312bf8e544caedbb433a1355540e6e80c0
    route_u_selector_authority: 46b22623f367d12291862b78feab25cf579c3a0a51179dba55c3b90f2a8c10ba
    exact496_inventory: e4d09740c032c3c48ae43be56c1dd11512527b6266f5974f444302bb4afc45d8
  protected_identities:
    - {path: src/schwgw/numerics/radial_solver.py, expected_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_start_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_end_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9}
    - {path: src/schwgw/numerics/conditioned_radial.py, expected_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_start_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_end_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2}
    - {path: src/schwgw/numerics/scaled_tortoise_radial.py, expected_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_start_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_end_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df}
    - {path: src/schwgw/numerics/adaptive_jost_radial.py, expected_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_start_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_end_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896}
    - {path: src/schwgw/numerics/matching.py, expected_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_start_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_end_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340}
    - {path: src/schwgw/numerics/physical_boundary_radial.py, expected_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_start_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_end_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f}
    - {path: src/schwgw/numerics/boundary_conditions.py, expected_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_start_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_end_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22}

ADVANCE_DECISION: ESCALATE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31y-package-identity-canonical-durability
      evidence_identity: package and contract are duplicate-free canonical JSON; 11/11 members and 18/18 review-basis identities rehash exact; all candidate members are regular 0444/nlink1.
    - item_id: v31y-package-delta-review-authority-path-collision
      evidence_identity: exact distinct delta-2 path was absent before review, its candidate digest is null, initial and delta-1 YELLOW archives are independently immutable, and T6 requires the later T0-supplied delta-2 digest plus exact GREEN tokens.
    - item_id: v31y-predicate-registry-operation-profile-ambiguous
      evidence_identity: compatibility/source_load_micro/full_sentinel/official expand uniquely to 151/409/14315/65849; global count is 80724 with frozen profile and registry hashes.
    - item_id: v31y-route-u-graph-authority-contradiction
      evidence_identity: exact-496 compact SHA e4d09740...45d8, fresh direct log_Gamma_flux < log(1e-8), dynamic N_U/3N_U and explicit failed-U root/map denylist remain exact.
    - item_id: v31y-v3-authority-preservation
      evidence_identity: V3.0 domain/formula/anchor/threshold/convention authorities, all 16 V3.1 thresholds and five certificate IDs remain exact.
    - item_id: v31y-route-a-b-c-and-sentinel-graphs
      evidence_identity: Route A 496/9920, Route B 102/458, Route C exact-23 and 161/322/483, and sentinel 35/70/105 remain frozen.
    - item_id: v31y-external-runtime-and-source-snapshot
      evidence_identity: kernel 70ad9d85...046c; snapshot 8d5498ab...e488; 25 files/five directories; content d849db67...e6e2; identity a1d2842d...2f27; eight loaded tuples exact.
    - item_id: v31y-listed-u-x-deny-roots
      evidence_identity: failed U/X roots and authorities remain immutable and nonpromotable; failed-U failure/manifest/map e3874e75...52aa/f977a0d5...3050d/5eee07ec...c822 remain denied.
    - item_id: v31y-compatibility-science-code-separation-boundary
      evidence_identity: compatibility remains a separate zero-science WLS path; all future implementation paths remain absent.
    - item_id: v31y-root-namespaces-resource-and-nonreuse-policy
      evidence_identity: root grammars, one-use/no-retry rules, resource limits, terminalization and U/X nonreuse remain unchanged.
    - item_id: v31y-protected-sources-and-no-runtime-drift
      evidence_identity: seven protected hashes match at review start/end; no Y dispatch/root or related process exists.
  failed_items:
    - item_id: v31y-checkpoint-ack-parent-edge-wire-undefined
      blocker_id: v31y-checkpoint-ack-parent-edge-wire-undefined
  partial_allowed_items:
    - item_id: v31y-common-absolute-phase-partial
      reason: inherited common absolute phase remains PARTIAL and is not certified by this package.
    - item_id: v31y-external-even-not-independent
      reason: Route C remains odd-only and supplies no independent external even-sector evidence.
  not_assessed_items:
    - item_id: v31y-exact-six-implementation
      reason: six implementation paths remain absent and T6 is not authorized.
    - item_id: v31y-real-kernel-compatibility
      reason: no compatibility dispatch/root/result exists.
    - item_id: v31y-source-load-micro
      reason: no source-load-micro dispatch/root/result exists.
    - item_id: v31y-full-sentinel
      reason: no 35/70/105 sentinel dispatch/root/result exists.
    - item_id: v31y-official-science
      reason: no official A/U/B/C root exists; all thresholds and certificates remain unevaluated.
    - item_id: v31y-v3-2-and-global
      reason: V3.2, full-domain V3 certification and global GREEN remain forbidden/not assessed.

findings:
  - finding_id: v31y-checkpoint-ack-parent-edge-wire-undefined
    class: BLOCKING_CURRENT_GATE
    summary: Repair cycle 2 makes the structural DAG countable but still does not make predicate values and terminal authority uniquely machine-derivable.
    blocker_id: v31y-checkpoint-ack-parent-edge-wire-undefined
    violated_contract_item: >-
      The initial failed item and delta-1 unblock condition require one unambiguous canonical authority chain for every event and all 18 stage edges of compatibility, source-load micro, full-sentinel and official operations, including machine-decidable per-field values, typed lifecycle/terminal evidence and fail-closed single-field mutation handling.
    exact_evidence: >-
      Contract c3d60194...ef45c now defines eight schemas with exact field counts child_frame/parent_event/prefix/final/ACK/open/seed/exit = 27/29/18/24/21/29/25/19, exact field/spec keysets, C_OBJ/C_WIRE/F/A/L, operation barriers and the stage16-to-17 structural order. Nevertheless, all 24 production predicate templates have exactly seven keys: template_id, id_format, applicable_operations, stage_id, observer_id, axis_order and axis_values. None supplies field_id, ownership, value_type, comparison_id, expected_value or evidence-input plan, while child_frame and parent_event require those to be exact predicate literals/schemas. Across the 192 schema fields, 101 value rules are only `derived from exact profile and preceding immutable authority`; the frozen profiles do not contain those missing values. P00 has no stage-open artifact, yet its event/prefix schemas require non-null stage_open_authority_sha256 and the only digest rule says `A(stage_open) or A(stage0_seed)` without a machine null/mapping matrix. LR is only a 14-item tuple type and no lifecycle-receipt artifact schema/canonical/self-hash rule exists. No terminal_manifest schema, field order or hash formula exists; it appears only in prose/path grammar. The eight P17 templates contain no exact evidence-input plan, so candidate bytes cannot prove that every P17 event binds both child-exit authority and lifecycle receipt. The eight field-order hashes are reproducible from their ordered field-name arrays, but they do not supply the absent predicate value semantics.
    expected_value: >-
      Every expanded predicate instance has one frozen field_id, ownership, value_type, comparison_id, expected-value schema/value and ordered evidence-input plan; P00 maps stage_open_authority_sha256 exactly to A(stage0_seed); the lifecycle receipt and terminal manifest have complete canonical schemas/hash inputs/path binding; and every P17 event and final manifest transitively binds child exit, EOF/wait/reap/process-group closure and the exact receipt. From those bytes an independent validator can construct one typed four-operation DAG and reject every missing/extra/type/null/domain/order/hash/sequence/barrier/replay/oversize/extra-output mutation.
    observed_value: >-
      Candidate bytes determine counts, IDs and structural sequencing but permit multiple incompatible value/comparison/evidence rows and multiple P00/receipt/terminal encodings. A T6 implementation would have to invent authority semantics, so its later tests could self-certify an implementation choice not frozen by this package.
    bounded_repair: >-
      None is authorized within this gate. Bounded repairs 1 and 2 are exhausted and the same substantive blocker remains. Root T0 must adjudicate under liveness protocol section 5 by narrowing the claim/domain, freezing a distinctly redesigned gate with complete machine semantics, or freezing this blocked branch while advancing only work that does not depend on it. Renaming or patching the same package as repair cycle 3 is forbidden.
    allowed_files:
      - none in phase6_v3_1_y_external_protocol_v1 after repair cycle 2
    recheck_command: >-
      NOT AUTHORIZED IN THIS GATE: no delta-review-3 command or implementation dispatch exists; any further check must be defined by a new Root-T0-frozen distinct gate after adjudication.
    unblock_condition: >-
      Root T0 records one of the three liveness adjudications. Advancement to T6 requires a distinct, newly frozen gate whose own initial T7 review independently reconstructs the complete predicate-value, P00, receipt, P17 and terminal-manifest authority without implementation discretion. The present candidate cannot unblock.

  - finding_id: v31y-common-absolute-phase-limitation
    class: NONBLOCKING_LIMITATION
    summary: The inherited common absolute complex phase remains PARTIAL and is not promoted by this package review.

  - finding_id: v31y-future-runtime-and-science
    class: FOLLOW_UP_DEBT
    summary: Compatibility, source-load micro, full sentinel and official science remain outside this failed package gate and cannot start without a future valid authority.

delta_review:
  reviewed_failed_items:
    - v31y-checkpoint-ack-parent-edge-wire-undefined
    - v31y-package-delta-review-authority-path-collision
  closed_failed_items:
    - v31y-package-delta-review-authority-path-collision
  remaining_failed_items:
    - v31y-checkpoint-ack-parent-edge-wire-undefined
  passed_invariants_rechecked:
    - v31y-package-identity-canonical-durability
    - v31y-predicate-registry-operation-profile-ambiguous
    - v31y-route-u-graph-authority-contradiction
    - v31y-v3-authority-preservation
    - v31y-route-a-b-c-and-sentinel-graphs
    - v31y-external-runtime-and-source-snapshot
    - v31y-listed-u-x-deny-roots
    - v31y-compatibility-science-code-separation-boundary
    - v31y-root-namespaces-resource-and-nonreuse-policy
    - v31y-protected-sources-and-no-runtime-drift
  protected_identities_match: true
  passed_invariant_regression: none
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - SHA-256/stat/nlink/no-symlink verification of the initial review, delta review 1, package, contract and all 11 members
    - duplicate-key-rejecting JSON reload and exact sorted indent-2 UTF-8 canonical-byte comparison for package and contract
    - recursive member/review-basis binding verification and exact ten-path repair-scope comparison
    - compact sorted-key semantic hashing of operation_profiles, predicate_registry and route_u_selector_authority
    - independent exact-496 domain/inventory reconstruction and failed-U denylist reload
    - independent enumeration of all eight schema field/spec tables, 24 production-template keysets, canonical functions, derived-digest declarations, operation barrier profiles and FSM edges
    - independent future-authority absence/null-digest/noncircularity and T6 start-gate token reconstruction
    - start/end rehash of V3.0 authorities, 25-file source snapshot, eight loaded-source tuples and seven protected radial files
    - six implementation-path, Y dispatch/root and related-process absence checks
    - scoped git diff --check over the exact ten-path repair-cycle-2 allowed union
  results:
    - package/contract canonical identity PASS; members 11/11 PASS; review-basis identities 18/18 PASS; allowed scope 10/10 PASS; diff-check PASS
    - delta-2 authority path fresh-absent before publication, candidate digest null and historical authority separation PASS
    - frozen semantic subtree hashes PASS: operation profiles e5022a94...a33a3, predicate registry 510858c8...80c0, Route-U selector 46b22623...10ba
    - operation profiles PASS: 151/409/14315/65849, global 80724; Route-U exact-496/dynamic N_U authority PASS
    - schema field/spec cardinality PASS: 27/29/18/24/21/29/25/19, total 192
    - structural finite-barrier and stage16-to-17 DAG count/order PASS
    - exact predicate-instance value/comparison/evidence semantics FAIL
    - exact P00 seed-to-event authority mapping FAIL
    - typed lifecycle receipt/P17 evidence plan/terminal-manifest authority FAIL
    - V3.0/science/threshold/convention/precision/source/protected identities PASS at start/end
    - six implementation paths and all Y runtime authorities absent; no Wolfram/BHPT/AP/radial/solver/science execution

non_claims:
  - no V3.1-Y implementation acceptance and no T6 dispatch
  - no target-kernel compatibility observation
  - no source-load micro or full-sentinel authority/result
  - no official V3.1-Y science, threshold PASS or certificate
  - no reuse or promotion of U/X values, subsets, requests, route maps, caches, checkpoints, dispatches or roots
  - no independent external even-sector result
  - no common absolute scattering-phase validation
  - no Li-figure equivalence
  - no finite-radius observer claim
  - no full-domain V3 certification
  - no V3.2 and no global GREEN

repair_cycle:
  completed_bounded_repairs: 2
  package_delta_review_consumes_additional_repair: false
  bounded_repair_3_available: false
  same_substantive_blocker_remaining: true
  t0_adjudication_required: true
```

## Independent conclusion

Repair cycle 2 closes the future-authority path collision and preserves every
frozen scientific, source, threshold, convention and protected identity. It
also makes the protocol's event counts and high-level DAG substantially more
explicit.

It does not close the original machine-authority blocker. Predicate values,
the stage-zero seed edge, lifecycle receipt, P17 evidence plan and terminal
manifest cannot be uniquely reconstructed from the candidate bytes. This is
not a style preference or a request for a stronger future test: it directly
prevents T6 from implementing the frozen package literally and prevents a
later independent validator from distinguishing a valid artifact from an
implementation-defined one.

The second bounded repair cycle is exhausted. Root T0 adjudication is now
required. T6 implementation, Wolfram compatibility, source-load micro, full
sentinel, official science and V3.2 are not authorized.
