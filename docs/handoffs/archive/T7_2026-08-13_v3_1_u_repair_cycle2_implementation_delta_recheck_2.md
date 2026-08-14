# T7 formal implementation delta recheck 2 — V3.1-U repair cycle 2

Date: 2026-08-13

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 2 IMPLEMENTATION READY FOR ONE-SHOT ROUTE-C SENTINEL
```

## Verdict record

```yaml
review_id: t7_v3_1_u_repair_cycle2_implementation_delta_recheck_2_20260813
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
repair_id: phase6_v3_1_u_route_c_totality_repair_cycle2_v1
attempt: repair_2_delta_recheck_2
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: implementation-only; no sentinel or official dispatch/root exists
  identities:
    - path: scripts/phase6_v3_1_bhpt_mst_cycle2.wls
      sha256: 894bb2ebe6bd9637e3e449e7785241085de0f673ad93ebbf7865c4a5023b888f
      state: PASS_FROZEN
    - path: src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py
      sha256: 60fdc7c3f46ab21eafbe2b319f0c7b15b3ab64d6633d360f79ada078dcbd36b1
      state: PASS_FROZEN
    - path: src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      sha256: 3292aea5074ae42b68cdb475bf86364b3aecc6ab08c37bf5ca51718f2834d730
      state: reviewed_delta
    - path: tests/regression/test_phase6_v3_hp_unitarity_publication.py
      sha256: c5f07055a79d99b1f03cf6954dc9d51a5832cd7eaa6fcd6a58875bb708b5356c
      state: reviewed_delta
    - path: tests/unit/test_phase6_v3_cycle2.py
      sha256: 47e29bf2ee0c900aaff1153ebee31848916b8c94b5de7e488220ef0f457b5323
      state: PASS_FROZEN
    - path: tests/unit/test_phase6_v3_hp_unitarity.py
      sha256: a61b53e84ab2aeab5f66639cb6a11d7c593803ac7067ddb437ca6811e554a2c3
      state: reviewed_delta

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_delta_review.md
    sha256: ca46dac66d322c3953e7a926d62f46ff19be48ec161a97c7b42aa0e83043335f
  package:
    path: configs/phase6_v3_1_u_repair_cycle2_package.json
    sha256: 61460a45d4d47ba9247e68969a5d91e2d77aac722c9324014a414ed4126dbfa2
  package_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_package_delta_recheck_1.md
    sha256: f67ce9fa3f0b3f65a7ad34c736c06236f1b0c87674a0e943e8b749f1ca9387e5
  initial_implementation_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_implementation_delta_review.md
    sha256: 4c4f048eb909f5f714f76d7f6c55c3429da6f80396bd2683976ca4a826df7499
  predecessor_delta_recheck:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_implementation_delta_recheck_1.md
    sha256: c5f827cbbc61c413d269c611e34cf72c72433a63752e71dcace21f670cec4210
  environment_authority:
    path: configs/phase6_v3_1_u_repair_cycle2_sentinel_environment_authority.json
    sha256: 936e4a403030d96ce4575e35fbefdff7d6eb29acaad564c137488a27aabec581
    mode: 0444
    nlink: 1
  environment_clarification_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_environment_clarification_review.md
    sha256: f30bff27a4e39d9959cc5b50fd3abe790490c0180f278a583832ca6e2d4016f6
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  unchanged_cli:
    path: scripts/phase6_v3_1_hp_unitarity.py
    sha256: 01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4
  unchanged_route_u_oracle:
    path: src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py
    sha256: a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7
  blocking_criteria:
    - v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable
    - exact requested execve environment equals the frozen two-key map
    - exact post-startup environment equals the frozen four-key map
    - dispatch binds the immutable environment authority
    - root-local consumption persists requested and observed maps before science
    - every missing, changed or extra key and invocation drift fails before authority consumption
  protected_identities:
    - path: src/schwgw/numerics/radial_solver.py
      expected_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
      observed_start_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
      observed_end_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
    - path: src/schwgw/numerics/conditioned_radial.py
      expected_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
      observed_start_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
      observed_end_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
    - path: src/schwgw/numerics/scaled_tortoise_radial.py
      expected_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
      observed_start_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
      observed_end_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
    - path: src/schwgw/numerics/adaptive_jost_radial.py
      expected_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
      observed_start_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
      observed_end_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
    - path: src/schwgw/numerics/matching.py
      expected_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
      observed_start_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
      observed_end_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
    - path: src/schwgw/numerics/physical_boundary_radial.py
      expected_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
      observed_start_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
      observed_end_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
    - path: src/schwgw/numerics/boundary_conditions.py
      expected_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
      observed_start_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
      observed_end_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 2 IMPLEMENTATION READY FOR ONE-SHOT ROUTE-C SENTINEL

incremental_review_state:
  passed_items:
    - item_id: v31u_repair2_sentinel_runtime_environment_allowlist_launchable
      evidence_identity: two independent zero-science launches, one through exact /usr/bin/env -i and one direct execve, produced the exact four-key observed map with canonical SHA-256 275a7c96a039be3a15a61d6ff5f2dd4c5285be0b60759775123c5215289f10bb and passed the live validator
    - item_id: v31u_repair2_environment_dispatch_and_consumption_binding
      evidence_identity: dispatch schema requires environment_authority path/SHA 936e4a403030d96ce4575e35fbefdff7d6eb29acaad564c137488a27aabec581 and the exact requested invocation; root-local dispatch_consumption persists authority, requested map, observed map and full runtime boundary with science_calls_before_consumption=0
    - item_id: v31u_repair2_environment_adversaries_fail_closed
      evidence_identity: missing/changed/extra requested and observed maps plus argv/module/executable/cwd/launcher drift all raise V31ContractError; dispatch authority and consumption tamper tests PASS
    - item_id: v31u_repair2_loaded_source_snapshot_closure_closed
      evidence_identity: exact eight ordered loaded-source records and complete 25-file/five-directory source closure remain PASS_FROZEN; WLS, cycle2 module and cycle2 unit hashes are unchanged
    - item_id: v31u_repair2_exact_three_delta_scope
      evidence_identity: only HP producer, HP unit test and HP regression test changed from delta-recheck-1; the three loaded-source paths, CLI, oracle, package and protected radial bytes are unchanged
    - item_id: v31u_repair2_anchor_graph_and_wls_totality_preserved
      evidence_identity: exact ordered 23 odd anchors, MST/90/45/45 method contract, total outcome grammar and source closure are frozen by unchanged WLS/module identities
    - item_id: v31u_repair2_durable_child_supervision_preserved
      evidence_identity: request/prelaunch/raw streams/receipt/wait/reap/process-group, source start/end and mutually exclusive terminal tests remain PASS in the focused suite
    - item_id: v31u_repair2_sentinel_official_separation_preserved
      evidence_identity: fixed one-use dispatch, exact sentinel namespace, official-before-sentinel rejection, no-reuse and wrong authority/root/review/hash rejection remain fail-closed
    - item_id: v31u_repair2_snapshot_byte_identity_preserved
      evidence_identity: stable source snapshot closure and its inherited-only commit association limitation are unchanged; no source or scientific byte is changed by this delta
    - item_id: v31u_repair2_focused_quality_checks_pass
      evidence_identity: exact CPython 3.14 overlay suite 118 passed; JUnit c8e6e289a73c6b9a6e749b8b4d6221a185d7ca88f1a9922cf9c89d39c960d7b9; Ruff, format, compile and scoped diff checks PASS
    - item_id: v31u_repair2_zero_science_and_protected_invariants_preserved
      evidence_identity: no Wolfram/sentinel/official/solver/science process or call; sentinel and official dispatches/roots are absent; all frozen and protected hashes match at start/end
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_repair2_sentinel_science
      reason: the one-use sentinel dispatch and fresh sentinel root do not yet exist; repair cycle 2 remains unconsumed
    - item_id: v31u_repair2_official_science
      reason: no formal sentinel result, official dispatch or official root exists; V3.1-U science remains NOT_ASSESSED
    - item_id: v31u_repair2_thresholds_and_certificates
      reason: no official candidate exists; 16 thresholds and five certificates are not evaluated

findings:
  - finding_id: v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable_closed
    class: CONTROL_PLANE_REPAIR
    summary: The exact host-bound requested/observed environment authority is now executable under both reviewed clean-launch paths, remains exact rather than projected, and is bound through dispatch and pre-science consumption.
  - finding_id: v31u_repair2_host_specific_environment_authority
    class: NONBLOCKING_LIMITATION
    summary: The authority is deliberately limited to the frozen macOS/arm64/UID/launcher/CPython identities; any host, binary, key or value drift requires a new reviewed authority and fails closed.
  - finding_id: v31u_repair2_snapshot_commit_association_inherited_only
    class: NONBLOCKING_LIMITATION
    summary: The restored external snapshot has no .git; its commit association remains inherited from byte-identical historical ledger and audit evidence, not independently asserted.
  - finding_id: v31u_repair2_science_not_assessed
    class: NONBLOCKING_LIMITATION
    summary: Implementation readiness does not execute or accept Route-C, the official candidate, thresholds or certificates.
  - finding_id: v31u_repair2_v3_2_forbidden
    class: FOLLOW_UP_DEBT
    summary: V3.2, broader V3 claims and global GREEN remain outside and forbidden.

delta_review:
  reviewed_failed_items:
    - v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable
  closed_failed_items:
    - v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable
  remaining_failed_items: []
  passed_invariants_rechecked:
    - v31u_repair2_loaded_source_snapshot_closure_closed
    - v31u_repair2_exact_six_scope_and_identity_preserved
    - v31u_repair2_anchor_graph_and_wls_totality_preserved
    - v31u_repair2_durable_child_supervision_preserved
    - v31u_repair2_sentinel_official_separation_preserved
    - v31u_repair2_snapshot_byte_identity_preserved
    - v31u_repair2_focused_quality_checks_preserved
    - v31u_repair2_zero_science_and_protected_invariants_preserved
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - start/end SHA-256 reload of authority, clarification review, predecessor delta recheck, package, governance, exact-six, CLI, oracle and seven protected radial paths
    - exact CPython 3.14 overlay focused pytest for cycle2, HP unitarity and publication regression tests
    - Ruff check and format check on the exact three changed Python paths; py_compile and exact-six git diff --check
    - independent /usr/bin/env -i and direct-execve CPython 3.14 probes with exactly the frozen requested map, followed by direct validate_sentinel_runtime_boundary calls
    - independent in-memory missing/changed/extra requested and observed environment, argv, module, executable, cwd and launcher adversaries
    - static/dataflow inspection of start-gate authority rehash, fixed-dispatch authority schema, runtime validation, root creation order, dispatch-consumption publication and source-ledger binding
    - read-only dispatch/root/process absence checks; no WolframKernel, Route-C sentinel, official producer, radial or AP solve
  results:
    - exact two clean launches both produced the literal four-key observed map and passed validation; canonical compact sorted JSON plus terminal-newline SHA-256 is 275a7c96a039be3a15a61d6ff5f2dd4c5285be0b60759775123c5215289f10bb
    - all 11 independent adversaries were rejected: requested missing/changed/extra, observed missing/changed/extra, argv, module, executable, cwd and launcher
    - dispatch requires exact environment-authority binding and requested invocation; consumption persists authority, requested and observed maps plus runtime boundary before science; authority/dispatch/consumption mutations are covered by focused fail-closed tests
    - 118 focused tests passed in 4.28 seconds under exact CPython 3.14 overlay
    - JUnit SHA-256 c8e6e289a73c6b9a6e749b8b4d6221a185d7ca88f1a9922cf9c89d39c960d7b9 rehashes exact; T4 inventory 129b04cc133c9a4fb753e2e1dfa6b686d28befbf22039bd1bbb7a4f915a51ade, verification aae6417735fd4002a3722cf9c98fe94e5ef61cb0f829f8f6ca6e2d001016ee84 and checkpoint cd9deafb00a69b37e0c05a9002ed86e41f6bfe3d1dc9a5f4982eca4a07c1641a rehash exact
    - Ruff and format checks PASS; three changed Python paths compile; scoped exact-six diff-check PASS
    - WLS, cycle2 module, cycle2 unit, CLI, oracle, package, environment authority, predecessor reviews and seven protected radial identities match at start/end
    - sentinel/official dispatches and roots are absent; no related process was found; zero Wolfram, sentinel, official, solver or science call was made

non_claims:
  - this bounded GREEN establishes only implementation readiness for one one-shot Route-C sentinel under the exact reviewed launcher and environment authority
  - V3.1-U science remains NOT_ASSESSED
  - no Route-C scientific record, threshold, certificate or official candidate is accepted
  - repair cycle 2 remains unconsumed until Root T0 creates/consumes the one-use sentinel dispatch and the fresh sentinel launch occurs
  - no official dispatch or official V3.1-U run is authorized by this review
  - no failed-root reuse, retry, artifact promotion, method/domain/threshold/convention change or protected-source modification is authorized
  - no V3.2, broader V3 claim or global GREEN is authorized

repair_cycle:
  completed_bounded_repairs: 2
  completed_bounded_scientific_repairs: 1
  current_bounded_scientific_repair: 2
  repair_cycle2_consumed: false
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Independent delta conclusion

The sole remaining failed item is closed. The implementation now keeps the
caller authority at the exact two-key `execve` map, validates the complete
literal four-key post-startup map, and accepts both reviewed clean-launch
paths on the frozen host. It does not use a subset, prefix, wildcard,
projection or ignored-key rule. Every independently tested missing, changed,
extra or invocation-drift case fails before dispatch consumption.

The one-use dispatch must bind authority SHA-256
`936e4a403030d96ce4575e35fbefdff7d6eb29acaad564c137488a27aabec581`.
Before any science, the fresh root must durably persist the authority identity,
the exact requested two-key map, the exact observed four-key map and the full
runtime boundary. The exact loaded-source closure, external method, domain,
thresholds, conventions and protected radial implementation remain frozen.

## Downstream boundary

Root T0 may create and consume exactly one sentinel dispatch and launch one
fresh Route-C sentinel using the exact `/usr/bin/env -i` launcher, executable,
argv, cwd and environment authority. Repair cycle 2 is consumed only when that
dispatch/launch occurs. This review does not authorize the official V3.1-U
run, V3.2, artifact reuse, or global GREEN.
