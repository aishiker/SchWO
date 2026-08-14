# T7 delta review 1 — V3.1-Y external protocol package

Review date: 2026-08-13 UTC

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-Y EXTERNAL PROTOCOL PACKAGE CHANGES REQUIRED
```

This is the archive-only delta review of bounded package repair cycle 1 for
`phase6_v3_1_y_external_protocol_v1`.  It is bound to the immutable initial
T7 review SHA-256
`1cc0da4cdfd7c9aecf7306ba7dd7b10219ce14f93e3a1c8bca37afe12417ac6b`
and the corrected package SHA-256
`7f81d1e92b176cbed9dc8e9a038fed8342c9d05c175c1b633390cf21ba51eee6`.

Two of the three frozen failed items are closed.  The operation-profile
registry expands uniquely to `151/409/14315/65849`, and the Route-U graph is
now generated only from the fresh exact-496 Route-A selector.  The third
failed item is not closed: the corrected contract names eight durable wire
schemas but still does not machine-freeze their per-field types/domains or
the inputs and encodings of their derived chain digests.  It also leaves the
compatibility barrier graph inconsistent and does not cryptographically bind
the stage-16 child-exit authority into stage 17.

The changed package also supplies new exact evidence that reopens one frozen
passed invariant: its sole `future_authority_paths.package_review` is the
already occupied immutable initial YELLOW archive.  The T6 start gate requires
both that initial REPAIR record and a later ADVANCE delta review, but no
distinct delta-review authority path is package-bound.  Therefore T6 cannot
validate an ADVANCE authority without either overwriting historical evidence
or accepting an unlisted path.

No implementation, Wolfram kernel, BHPT/AP/radial solver, scientific call,
dispatch or run root was created or executed by this review.

## Verdict record

```yaml
review_id: t7_v3_1_y_external_protocol_package_delta_1_20260813
gate_id: phase6_v3_1_y_external_protocol_v1
attempt: repair_1
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed

reviewed_candidate:
  root: configs/phase6_v3_1_y_external_protocol_package.json
  identities:
    - {path: configs/phase6_v3_1_y_external_protocol_package.json, sha256: 7f81d1e92b176cbed9dc8e9a038fed8342c9d05c175c1b633390cf21ba51eee6, mode: "0444", nlink: 1}
    - {path: configs/phase6_v3_1_y_external_protocol_contract.json, sha256: 4c59bfb635918e22934d9dcfa82c767fef771be5744059f5294443257e0c2aa4, mode: "0444", nlink: 1}
    - {path: docs/phase6_v3_1_y_external_protocol_design.md, sha256: 353ae27abb82d2484e4f1597782f3cd0618b6411ca67dea623bd47500dc0ddb4, mode: "0444", nlink: 1}
    - {path: docs/phase6_v3_1_y_external_protocol_redesign_analysis.md, sha256: ab0acd114a4ff3c122d1dd590e066988ed8e332fdc1b593fd04f21f5e4181df1, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md, sha256: 5b1d2109dd23954b14ef1c45e4a044c2a0f2a63749c1a5a60ed7831a7d810c2d, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md, sha256: cd11cf3148a1e7b3efba1c726a2790a48479acc7600a2342e74f5309cb8a6696, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_y_wolfram_protocol_compatibility_review.md, sha256: 51404ba66944b08b1785d9a9e58665a728d3b455d8ca771623f1d1f50f1bfd67, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_y_source_load_micro_review.md, sha256: c746e32dfca2bb83a8bbf1a53316b5900ba2852285b078efecc67c6f9d17e18d, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md, sha256: 07a50a946d62abda078959eda8d65414fbf464d5d3cf7fd2a9265c8ab93f5856, mode: "0444", nlink: 1}
    - {path: docs/prompts/phase6_t7_v3_1_y_science_review.md, sha256: ed9dbb0bff0ce524858073e51b434c9b16fe3076bf2d36646a99e738dde0aa44, mode: "0444", nlink: 1}

package_integrity:
  package_canonical_duplicate_free_indent2_sorted_one_lf: true
  contract_canonical_duplicate_free_indent2_sorted_one_lf: true
  member_count: 11
  member_hash_mode_nlink_pass: 11
  recursive_unique_path_hash_bindings: 30
  recursive_binding_failures: 0
  exact_allowed_path_union_count: 10
  exact_allowed_path_union_unique_count: 10
  actual_corrected_scope: package plus nine allowed members
  unchanged_members:
    - {path: docs/handoffs/archive/T4_2026-08-13_v3_1_y_external_protocol_redesign_analysis.md, sha256: e162a1fc5e396c11234fef09bdeb04f8c1e7496da588da105971a4c8868dbefb}
    - {path: docs/prompts/phase6_t7_v3_1_y_external_protocol_package_review.md, sha256: 2c4487fb3fab836f297a8b0bb405f0b51acdeb68593f901541a475cb48c8cb01}

frozen_review_basis:
  initial_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_review.md
    sha256: 1cc0da4cdfd7c9aecf7306ba7dd7b10219ce14f93e3a1c8bca37afe12417ac6b
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
  external_anchor_matrix:
    path: configs/phase6_v3_0_external_anchor_matrix.json
    sha256: 06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485
  convention:
    path: references/notes/phase6_v3_absorption_scattering_conventions.md
    sha256: 82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a
  thresholds:
    path: configs/phase6_v3_0_thresholds.json
    sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
    exact_v3_1_count: 16
  blocking_criteria:
    - each corrected failed item must meet the exact initial unblock condition
    - all nine frozen passed invariants and protected/source identities must remain exact
    - the package and T6 start gate must provide a noncircular executable authority chain
    - no implementation, runtime, science, dispatch, root or V3.2 is authorized at this gate
  protected_identities:
    - {path: src/schwgw/numerics/radial_solver.py, expected_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_start_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_end_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9}
    - {path: src/schwgw/numerics/conditioned_radial.py, expected_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_start_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_end_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2}
    - {path: src/schwgw/numerics/scaled_tortoise_radial.py, expected_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_start_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_end_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df}
    - {path: src/schwgw/numerics/adaptive_jost_radial.py, expected_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_start_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_end_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896}
    - {path: src/schwgw/numerics/matching.py, expected_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_start_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_end_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340}
    - {path: src/schwgw/numerics/physical_boundary_radial.py, expected_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_start_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_end_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f}
    - {path: src/schwgw/numerics/boundary_conditions.py, expected_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_start_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_end_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22}

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-Y EXTERNAL PROTOCOL PACKAGE CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31y-package-identity-canonical-durability
      evidence_identity: corrected package/contract are duplicate-free canonical JSON; 11/11 members and 30/30 unique recursive bindings rehash exact; all candidate files are regular 0444/nlink1.
    - item_id: v31y-v3-authority-preservation
      evidence_identity: V3.0 formula/domain/anchor/threshold/convention authorities, 16 V3.1 thresholds and five certificate IDs remain exact.
    - item_id: v31y-route-a-b-c-and-sentinel-graphs
      evidence_identity: frozen Route A 496/9920, Route B 102/458, exact-23 Route C 161/322/483 and full-sentinel 35/70/105 graphs are unchanged.
    - item_id: v31y-external-runtime-and-source-snapshot
      evidence_identity: kernel 70ad9d85...046c, snapshot 8d5498ab...e488, 25 files/five dirs and eight loaded-source tuples rehash exact.
    - item_id: v31y-listed-u-x-deny-roots
      evidence_identity: all predecessor U/X authorities remain terminal and nonpromotable; the failed official U root/failure/manifest/map e3874e75...52aa/f977a0d5...3050d/5eee07ec...c822 are now explicitly bound and denied.
    - item_id: v31y-compatibility-science-code-separation-boundary
      evidence_identity: separate compatibility/science-capable WLS paths remain frozen and absent; compatibility science-capable call sites and counters remain required zero.
    - item_id: v31y-root-namespaces-resource-and-nonreuse-policy
      evidence_identity: operation root namespaces, one-use/no-retry policy and resource/terminal rules are unchanged; no Y root or dispatch exists.
    - item_id: v31y-protected-sources-and-no-runtime-drift
      evidence_identity: seven protected hashes match at start/end; six implementation paths and all post-package runtime roots are absent; no related process exists.
    - item_id: v31y-predicate-registry-operation-profile-ambiguous
      evidence_identity: independently expanded compatibility/source_load_micro/full_sentinel/official profiles are exactly 151/409/14315/65849 and global 80724/80724 unique, with exact ordered-ID, call-plan, profile and registry hashes.
    - item_id: v31y-route-u-graph-authority-contradiction
      evidence_identity: exact 496-mode inventory SHA e4d09740...45d8 and fresh direct log_Gamma_flux < log(1e-8) stable-order selector produce dynamic N_U/3N_U; fixed 318/954 and predecessor map/count reuse are forbidden.
  failed_items:
    - item_id: v31y-checkpoint-ack-parent-edge-wire-undefined
      blocker_id: v31y-checkpoint-ack-parent-edge-wire-undefined
    - item_id: v31y-distinct-lineage-and-future-authority
      blocker_id: v31y-package-delta-review-authority-path-collision
  partial_allowed_items:
    - item_id: v31y-common-absolute-phase-partial
      reason: inherited common absolute complex phase remains PARTIAL and is not certified by this package.
    - item_id: v31y-external-even-not-independent
      reason: Route C remains odd-only and supplies no independent external even-sector result.
  not_assessed_items:
    - item_id: v31y-exact-six-implementation
      reason: all six implementation paths are absent; T6 is not authorized.
    - item_id: v31y-real-kernel-compatibility
      reason: no compatibility dispatch/root/result exists.
    - item_id: v31y-source-load-micro
      reason: no source-load-micro dispatch/root/result exists.
    - item_id: v31y-full-sentinel
      reason: no fresh 35/70/105 sentinel exists.
    - item_id: v31y-official-science
      reason: no official A/U/B/C root exists; 16 threshold outcomes and five certificates remain unevaluated.
    - item_id: v31y-v3-2-and-global
      reason: V3.2, full-domain V3 certification and global GREEN remain forbidden/not assessed.

findings:
  - finding_id: v31y-checkpoint-ack-parent-edge-wire-undefined
    class: BLOCKING_CURRENT_GATE
    summary: The corrected protocol adds the named artifacts but still does not define one literal, type-complete and cryptographically closed four-operation FSM.
    blocker_id: v31y-checkpoint-ack-parent-edge-wire-undefined
    violated_contract_item: >-
      Initial failed item `v31y-checkpoint-ack-parent-edge-wire-undefined` and its unblock condition require one unambiguous canonical authority chain for every event and all 18 stage edges of all four operations, a deadlock-free valid traversal, and fail-closed rejection of every single-field schema/checkpoint/sequence/barrier/observer/replay mutation.
    exact_evidence: >-
      Corrected contract lines 1487-1735 list eight field orders with 26 child-frame, 28 parent-event, 17 prefix-checkpoint, 23 final-checkpoint, 16 ACK, 26 stage-open, 22 stage0-seed and 18 child-exit fields, while lines 5879-5956 provide prose DAGs. No per-field type, nullability, allowed-value or value-derivation table exists; `single_field_mutation_rule` only commands rejection. The fields `prefix_chain_sha256`, `zero_event_chain_seed_sha256`, `ordered_event_hashes_sha256`, checkpoint `ordered_predicate_ids_sha256`, `observer_plan_sha256`, `path_grammar_sha256` and `evidence_inputs` have no frozen canonical input list or encoding formula beyond the outer artifact hash. Stage0 has no exact seed-to-first-event/prefix rule and event/prefix cross-stage reset versus global chaining is unspecified. Global FSM lines 5940/5944 require child barriers at stages 10/14 with 67/68 parent predicates, but compatibility declares only 7/16 cases at those stages and contains no `WL_BARRIER_REQUEST` event or operation-specific exemption. Stage16 ACK binds a child-exit authority, while the stage17 open schema has no child-exit/receipt/terminal digest and stage17 events use unconstrained `evidence_inputs`.
    expected_value: >-
      For each of all eight schemas, an exact field-type/nullability/domain/value table and canonical hash-input formula; exact event/prefix chain reset rules; an explicit stage0 seed-to-event/prefix binding; operation-specific barrier IDs, event counts and actor plans consistent with every operation profile; and an open17/terminal chain that explicitly binds child-exit authority, receipt, wait/reap and process-group closure. One literal model must traverse all declared counts and reject every single-field mutation.
    observed_value: >-
      Multiple incompatible encodings, chain formulas and barrier traversals satisfy the prose. Compatibility cannot literally reconcile its 7/16 stage counts with the global 67/68 child-barrier plan, and stage17 is not cryptographically anchored to child exit. T6 would have to invent acceptance semantics.
    bounded_repair: >-
      In repair cycle 2, machine-freeze the per-field type/nullability/domain/value rules and every derived-digest formula/input order; freeze stage0 and event/prefix chain semantics; add exact operation-specific barrier plans or explicit zero-science compatibility exemptions consistent with profile counts; and bind stage17 open/events/final to the stage16 child-exit authority and durable lifecycle receipt. Align the design, T6 prompt and affected future review prompts without changing science, domain, thresholds, conventions, precision, source snapshot or protected bytes.
    allowed_files:
      - configs/phase6_v3_1_y_external_protocol_package.json
      - configs/phase6_v3_1_y_external_protocol_contract.json
      - docs/phase6_v3_1_y_external_protocol_design.md
      - docs/phase6_v3_1_y_external_protocol_redesign_analysis.md
      - docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md
      - docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md
      - docs/prompts/phase6_t7_v3_1_y_wolfram_protocol_compatibility_review.md
      - docs/prompts/phase6_t7_v3_1_y_source_load_micro_review.md
      - docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md
      - docs/prompts/phase6_t7_v3_1_y_science_review.md
    recheck_command: >-
      PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.14 -c 'duplicate-reject and canonical-reload the corrected package/contract; construct all eight typed schemas and exact derived digests; traverse all four operation DAGs through stages 0..17 with declared profile/barrier counts; then mutate each field one at a time across missing/extra/type/value/order/hash, chain reset, barrier, stage0, child-exit and stage17 bindings and require rejection before progression' && git diff --check -- configs/phase6_v3_1_y_external_protocol_package.json configs/phase6_v3_1_y_external_protocol_contract.json docs/phase6_v3_1_y_external_protocol_design.md docs/phase6_v3_1_y_external_protocol_redesign_analysis.md docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md docs/prompts/phase6_t7_v3_1_y_wolfram_protocol_compatibility_review.md docs/prompts/phase6_t7_v3_1_y_source_load_micro_review.md docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md docs/prompts/phase6_t7_v3_1_y_science_review.md
    unblock_condition: >-
      A repair-cycle-2 delta review independently constructs exactly one type-complete canonical FSM for every declared event and stage of compatibility, micro, sentinel and official operations; valid executions match all frozen profile and barrier counts without deadlock, stage17 is transitively bound to child exit and lifecycle closure, and every schema-field/chain/barrier/replay mutation fails before progression.

  - finding_id: v31y-package-delta-review-authority-path-collision
    class: BLOCKING_CURRENT_GATE
    summary: The repaired package has no distinct package-bound archive path capable of carrying this delta review's required ADVANCE authority into T6.
    blocker_id: v31y-package-delta-review-authority-path-collision
    violated_contract_item: >-
      Frozen passed item `v31y-distinct-lineage-and-future-authority`, initial package-review items 8-9, and the corrected T6 start gate require executable, noncircular predeclared future authority paths: the immutable initial REPAIR review must remain historical while a later immutable ADVANCE delta review is separately identity-bound.
    exact_evidence: >-
      Corrected package lines 45-57 define only `future_authority_paths.package_review = docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_review.md`. Package lines 199-204 simultaneously bind that same path and SHA `1cc0da4cdfd7c9aecf7306ba7dd7b10219ce14f93e3a1c8bca37afe12417ac6b` as the initial `REPAIR / NOT_ASSESSED` review. The file exists immutable 0444/nlink1 and contains `REVIEW YELLOW`. Corrected T6 prompt lines 7-15 requires the predecessor package, initial REPAIR archive, later delta-review archive and a fixed future package-review archive carrying `ADVANCE / NOT_ASSESSED`. No package-bound delta-review path exists; plausible delta paths were absent before this review. The unchanged initial package-review prompt still names only the already occupied initial path.
    expected_value: >-
      A distinct predeclared O_EXCL delta-review archive path, absent before its review and with no future digest hardcoded. After publication, T6 must bind the exact initial YELLOW path/SHA and the exact distinct delta path/SHA plus its `ADVANCE / NOT_ASSESSED / package-ready` tokens independently.
    observed_value: >-
      The sole configured package-review authority is permanently occupied by the initial YELLOW. Overwrite is forbidden, while this delta archive's distinct path is not package-authorized; accepting it would require an unlisted-path escape.
    bounded_repair: >-
      In repair cycle 2, add one distinct package-bound package-delta-review path and align the T6 start gate to require both the immutable initial YELLOW identity and the later delta identity. Preserve the initial archive unchanged and keep the future delta digest absent from candidate bytes. This is authority metadata only and must not alter contract science, domain, thresholds, convention, precision, source or protected bytes beyond changes independently required by the first blocker.
    allowed_files:
      - configs/phase6_v3_1_y_external_protocol_package.json
      - docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md
    recheck_command: >-
      PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.14 -c 'duplicate-reject and canonical-reload the corrected package; assert the initial package-review path is immutable REPAIR SHA 1cc0da4cdfd7c9aecf7306ba7dd7b10219ce14f93e3a1c8bca37afe12417ac6b; assert a different package-bound delta path was absent before review; after T7 publication rehash that path and require ADVANCE/NOT_ASSESSED/package-ready tokens; reject missing, alias, wrong-path, wrong-digest, YELLOW, replay, overwrite and extra-authority variants; verify T6 requires both exact authorities' && git diff --check -- configs/phase6_v3_1_y_external_protocol_package.json docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md
    unblock_condition: >-
      A repair-cycle-2 T7 delta review writes one immutable ADVANCE authority only at the newly predeclared distinct path, and an independent reload proves T6 can validate the initial YELLOW and later ADVANCE identities separately with no overwrite, self-reference, alias or unlisted path.

delta_review:
  reviewed_failed_items:
    - v31y-predicate-registry-operation-profile-ambiguous
    - v31y-checkpoint-ack-parent-edge-wire-undefined
    - v31y-route-u-graph-authority-contradiction
  closed_failed_items:
    - v31y-predicate-registry-operation-profile-ambiguous
    - v31y-route-u-graph-authority-contradiction
  remaining_failed_items:
    - v31y-checkpoint-ack-parent-edge-wire-undefined
  passed_invariants_rechecked:
    - v31y-package-identity-canonical-durability
    - v31y-distinct-lineage-and-future-authority
    - v31y-v3-authority-preservation
    - v31y-route-a-b-c-and-sentinel-graphs
    - v31y-external-runtime-and-source-snapshot
    - v31y-listed-u-x-deny-roots
    - v31y-compatibility-science-code-separation-boundary
    - v31y-root-namespaces-resource-and-nonreuse-policy
    - v31y-protected-sources-and-no-runtime-drift
  passed_invariant_regression:
    item_id: v31y-distinct-lineage-and-future-authority
    blocker_id: v31y-package-delta-review-authority-path-collision
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - complete read, SHA-256, mode and nlink checks for the initial review, corrected package/contract/design/analysis, all 11 members and every recursively bound path
    - duplicate-key-rejecting JSON reload and exact canonical-byte comparison for package and contract
    - exact comparison of repair scope against the ten-path allowed union and scoped `git diff --check`
    - independent four-profile template/case expansion, ordered-ID/call-plan/profile/registry hashing and hostile duplicate/axis/collision/replay reconstruction
    - independent exact-496 domain rebuild, compact inventory hash, fresh Route-U selector and N_U/3N_U boundary/adversarial reconstruction
    - independent enumeration of all eight wire schemas, field orders, FSM stage actors, compatibility stage counts, barrier roles and derived-digest definitions
    - direct future-authority path and T6 start-gate cross-read, including initial archive mode/nlink and pre-write absence of delta paths
    - start/end rehash of V3.0 authorities, source snapshot and seven protected radial files; six implementation/future runtime path and related-process absence checks
  results:
    - corrected package/contract canonical identity PASS; members 11/11 PASS; recursive bindings 30/30 PASS; exact allowed union 10/10 PASS; diff-check PASS
    - operation profiles PASS: compatibility 151, source-load micro 409, full sentinel 14315, official 65849, global 80724 unique
    - ordered-ID SHA values PASS: e3e9ecd008051d9f085ca9f28785884276eb5c22fadd9ab2770331c26506200f / 4ac7bce24e17ee7eb3b39ad5596409b912007bd6b8a0e1367f941592f2d046de / dd4fe0ea816e0d92a39d0f866b77e30bb7b423fa5a554a7060c909c97fcd48bf / 3666f6287a2887b4d3277042a617579685d82192816e20252037d135c28b623e; global 1212271ce988975018a4e464f24815d645d36debcf8b0fdd54f5ac5bc44f8616; registry 9eb5f8d9d7e8b829c8323b64bb089b5e77d664f4b6f79945cf04ee3a9d786a60
    - exact-496 Route-U authority PASS: compact inventory e4d09740c032c3c48ae43be56c1dd11512527b6266f5974f444302bb4afc45d8; dynamic N_U/3N_U and failed-root denylist exact
    - checkpoint/ACK/parent-edge machine completeness FAIL
    - package delta-review future-authority executability FAIL
    - V3.0/science/threshold/convention/precision/source identities and seven protected hashes PASS at start/end
    - six implementation paths, all compatibility/micro/sentinel/official dispatches and roots absent; zero related Wolfram/Python/science processes
    - no Wolfram/BHPT/AP/radial/solver/science execution

non_claims:
  - no V3.1-Y implementation acceptance or T6 dispatch
  - no target-kernel compatibility observation
  - no source-load-micro or full-sentinel authority/result
  - no official V3.1-Y science, threshold PASS or certificate
  - no reuse or promotion of U/X values, subsets, requests, route maps, caches, checkpoints, dispatches or roots
  - no independent external even-sector result
  - no common absolute scattering-phase validation
  - no Li-figure equivalence
  - no finite-radius observer claim
  - no full-domain V3 certification
  - no V3.2 and no global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  package_delta_review_consumes_additional_repair: false
  bounded_repair_2_available: true
  same_substantive_blocker_remaining: true
  t0_adjudication_required: false
```

## Independent conclusion

The corrected registry and Route-U authority are materially stronger and pass
their frozen unblock conditions.  They do not make the package executable.
The durable protocol still leaves core wire values and chain hashes to an
implementer's discretion, and its compatibility barrier and child-exit-to-
terminal edges cannot be reconstructed as one exact FSM.  Separately, the
package has no noncircular path for this delta review to become the T6 start
authority.

Root T0 may freeze the final bounded repair cycle 2, limited to the exact
allowed files and binary unblock conditions above.  Until a delta-2 review
closes both blockers, formal T6 implementation is not authorized.  No runtime,
science, dispatch, root or V3.2 is authorized by this record.
