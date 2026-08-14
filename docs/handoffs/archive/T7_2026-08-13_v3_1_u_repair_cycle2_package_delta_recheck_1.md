# T7 formal delta recheck 1 — V3.1-U final bounded repair cycle 2 package

Date: 2026-08-13

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 2 PACKAGE READY FOR T4
```

## Verdict record

```yaml
review_id: t7_v3_1_u_repair_cycle2_package_delta_recheck_1_20260813
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
repair_id: phase6_v3_1_u_route_c_totality_repair_cycle2_v1
attempt: repair_2
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: package-only; no implementation, dispatch, sentinel or official root exists
  identities:
    - path: configs/phase6_v3_1_u_repair_cycle2_package.json
      sha256: 61460a45d4d47ba9247e68969a5d91e2d77aac722c9324014a414ed4126dbfa2
    - path: docs/phase6_v3_1_u_repair_cycle2_design.md
      sha256: ce57d7e8fd6cc4fc61398e448260368662d9aa39da2d53ec4e1342b84d4d0029
    - path: docs/prompts/phase6_t4_v3_1_u_repair_cycle2.md
      sha256: 8287aaff8564554a56bc3cc673c825019f8ead955612eae33ab3543c4b208e80
    - path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_package_review.md
      sha256: 3b1d9083f5de33dee9be5e716ee465edad06050768f621f89993c0f10285959b
    - path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_delta_review.md
      sha256: ca46dac66d322c3953e7a926d62f46ff19be48ec161a97c7b42aa0e83043335f
    - path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_sentinel_review.md
      sha256: 5bbf2996a7af96b282a1c699c74e85a04f7030b9bd5c2bcb33d4c0a99c33e617

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_package_review.md
    sha256: 3b1d9083f5de33dee9be5e716ee465edad06050768f621f89993c0f10285959b
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  predecessor_package_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_package_review.md
    sha256: 08e206d58b178bbed0ae96f7aa395db67f4c2bcb4620a5cd996f00afb028b23f
  predecessor_terminal_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle1_terminal_scientific_review.md
    sha256: 7552b2dbc19269be0eb11b61ae8eb04c55a1225d10db1962d881e0f6ac7925c1
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - id: V3.1 frozen threshold set
      value: exact 16 unchanged IDs/operators/values/domains
      units: mixed dimensionless/logarithmic
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  blocking_criteria:
    - prior failed item v31u_repair2_sentinel_entry_authority_undefined
    - exact executable, four-token argv, cwd and environment allowlist
    - exact fixed-dispatch internal root derivation
    - no -c, direct import, alternate module, extra argv/environment, caller root or fallback
    - correction restricted to package, design and T4 prompt
    - all frozen passed invariants and protected identities preserved
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
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 2 PACKAGE READY FOR T4

incremental_review_state:
  passed_items:
    - item_id: v31u_repair2_sentinel_entry_authority_closed
      evidence_identity: package 61460a45d4d47ba9247e68969a5d91e2d77aac722c9324014a414ed4126dbfa2 sentinel_invocation plus design ce57d7e8fd6cc4fc61398e448260368662d9aa39da2d53ec4e1342b84d4d0029 sections 7-8 and T4 prompt 8287aaff8564554a56bc3cc673c825019f8ead955612eae33ab3543c4b208e80 exact module-entry contract
    - item_id: v31u_repair2_package_identity_and_scope
      evidence_identity: corrected pretty canonical package with one terminal newline; five members exact; 50/50 repository path bindings plus external WolframKernel binding rehash exact; all seven package/snapshot files regular 0444/nlink1
    - item_id: v31u_repair2_correction_scope_exact_three
      evidence_identity: package package_correction.allowed_paths is exactly configs/phase6_v3_1_u_repair_cycle2_package.json, docs/phase6_v3_1_u_repair_cycle2_design.md and docs/prompts/phase6_t4_v3_1_u_repair_cycle2.md; the other three prompts and all implementation/science identities are unchanged
    - item_id: v31u_repair2_exact_six_file_boundary
      evidence_identity: baselines a7a53b9fee2e2001132b0b437b233f4fafff1362a113d21105913e2263dcdf6a/a3990e9dc3bc5480478c037a77c0661e805508df49007848185e7178380da29e/168c8771fbe7cba8983b51d0ae58294169c2e901a75593953a91ad0c401fc146/acdb1e30f69c2a5972af7394c08d360f8dfef32f3fc5f0a69c7401ca4d5167cc/d86fc31af71a2e3815cf063989918994495c05b1f8655bb8973bb8362c2dca39/e4e3cfb939cb7ccd2f267cbddfe52c4064873cddbc481fd26dc727ec08ea29aa
    - item_id: v31u_repair2_science_invariants_frozen
      evidence_identity: CLI 01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4; Route-U oracle a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7; exact 496/9920/318/954/102/458/23 graph, 16 thresholds, five certificates, odd RW MST/90/45/45 and all seven protected hashes unchanged
    - item_id: v31u_repair2_external_snapshot_byte_chain
      evidence_identity: snapshot 8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488; 25 exact source bytes; content inventory d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2; restored identity inventory a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
    - item_id: v31u_repair2_external_historical_chain
      evidence_identity: historical ledger c73c1c585af9bbfeed8d50a2b28c9c2f94e08b38214b3db716fe1c7e501e2d16, historical inventory 512685e2860d784cf3152b96ba71fac76d4cdc8fd23e74825ebb519ac7ddb57c, audit ZIP 715e27a45b15ec2ab78f92c77506de4317f5a26af79bb665de5a16d30557d162 and SHA256SUMS ea5e8d103323a1e8b5faefd951022f1d88cfbd05660820a18055c765492b0b92
    - item_id: v31u_repair2_snapshot_commit_nonclaim
      evidence_identity: restored snapshot has no .git; commit association remains explicitly inherited from immutable historical evidence and is not independently asserted by the snapshot
    - item_id: v31u_repair2_terminal_protocol
      evidence_identity: complete ordered 23-attempt PASS/ERROR records, raw streams, receipt/wait/reap, source start/end, exclusive terminal closure and fail-closed adversaries remain frozen
    - item_id: v31u_repair2_no_reuse_and_loop_limit
      evidence_identity: failed roots and sentinel records remain forbidden official inputs; sentinel dispatch consumes repair 2; failure requires ESCALATE; no retry/resume/repair cycle 3
    - item_id: v31u_repair2_future_review_hash_non_circularity
      evidence_identity: future paths and tokens are frozen without future SHA; fixed T0 dispatch later supplies one exact published path/SHA; live handoffs, alternate hashes and fallback remain forbidden
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_repair2_implementation
      reason: no six-file implementation delta or zero-science T4 evidence exists
    - item_id: v31u_repair2_sentinel_science
      reason: sentinel dispatch/root are absent; repair cycle 2 is not consumed
    - item_id: v31u_repair2_official_science
      reason: official dispatch/root are absent; V3.1-U science remains NOT_ASSESSED at this package gate

findings:
  - finding_id: v31u_repair2_sentinel_entry_authority_closed
    class: CONTROL_PLANE_REPAIR
    summary: The prior package-level authority ambiguity is closed by one exact package-bound no-root-argument module invocation and exhaustive rejection of alternate launch/authority surfaces; no science byte or criterion changed.
  - finding_id: v31u_snapshot_commit_association_inherited_only
    class: NONBLOCKING_LIMITATION
    summary: The restored source snapshot has no .git; its commit association remains honestly inherited from exact historical byte/provenance evidence rather than independently asserted.
  - finding_id: v31u_repair2_science_not_yet_assessed
    class: NONBLOCKING_LIMITATION
    summary: This package gate does not assess implementation, sentinel science, official science, any threshold or certificate.
  - finding_id: v31u_v3_2_and_global_state_out_of_scope
    class: FOLLOW_UP_DEBT
    summary: V3.2, broader V3 claims and global GREEN remain outside and forbidden by this gate.

delta_review:
  reviewed_failed_items:
    - v31u_repair2_sentinel_entry_authority_undefined
  passed_invariants_rechecked:
    - v31u_repair2_package_identity_and_scope
    - v31u_repair2_exact_six_file_boundary
    - v31u_repair2_science_invariants_frozen
    - v31u_repair2_external_snapshot_byte_chain
    - v31u_repair2_external_historical_chain
    - v31u_repair2_snapshot_commit_nonclaim
    - v31u_repair2_terminal_protocol
    - v31u_repair2_no_reuse_and_loop_limit
    - v31u_repair2_future_review_hash_non_circularity
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - SHA-256, mode and nlink reload of corrected package, five members, prior review, snapshot, 31 source bindings, seven protected paths, six implementation baselines, frozen CLI and external WolframKernel
    - independent pretty-canonical JSON reconstruction with sorted keys, two-space indentation and one terminal newline
    - static exact-field and dataflow review of package sentinel_invocation, corrected design sections 7-8 and corrected T4 prompt
    - exact check for four-token argv, executable, cwd, two-key environment allowlist, fixed dispatch and internal exact_root derivation
    - negative-surface audit for -c, direct import, alternate module, missing/wrong operation, fifth token, caller root, extra environment, environment authority and fallback
    - exact three-path correction-scope comparison and diff-check
    - read-only absence checks for fixed dispatches and repair-2 sentinel/official roots; process check excluding the review commands themselves
  results:
    - corrected package hash is 61460a45d4d47ba9247e68969a5d91e2d77aac722c9324014a414ed4126dbfa2 and equals its specified pretty canonical serialization byte-for-byte
    - design/T4 hashes are ce57d7e8fd6cc4fc61398e448260368662d9aa39da2d53ec4e1342b84d4d0029 and 8287aaff8564554a56bc3cc673c825019f8ead955612eae33ab3543c4b208e80
    - all five member hashes rehash exact; 50/50 repository bindings rehash exact; external WolframKernel path rehashes 70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c
    - corrected package/design/T4 prompt and all unchanged members/snapshot are regular 0444/nlink1; corrected three-path diff-check PASS
    - exact sentinel argv is [python3.14,-m,schwgw.validation.phase6_v3_mode_greybody_hp_replacement,route-c-sentinel], with exact absolute executable, project cwd and only PYTHONDONTWRITEBYTECODE=1 plus overlay-first PYTHONPATH
    - no root/review/source/dispatch/WLS/kernel/method/precision/authority argument exists; exact_root is derived only by internally loading and validating the fixed canonical O_EXCL dispatch
    - package, design and T4 prompt all explicitly reject -c, direct import, alternate module, extra argv/environment, cwd drift, caller root, environment authority and fallback; implementation review and sentinel dispatch must bind the complete invocation object
    - fixed sentinel/official dispatches and repair-2 roots are absent; no related live producer or Wolfram process was found
    - zero Python radial/AP/BHPT/Wolfram/sentinel/official/science solve was run

non_claims:
  - this GREEN establishes package readiness only
  - V3.1-U implementation and science are NOT_ASSESSED
  - repair cycle 2 is not consumed by package review or this delta recheck
  - no sentinel dispatch, sentinel execution, official dispatch, official execution or artifact reuse is authorized
  - no V3.2, broader V3 scientific claim or global GREEN is authorized

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 1
  current_bounded_scientific_repair: 2
  repair_cycle2_consumed: false
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Independent delta conclusion

The exact prior blocker is closed.  The corrected package now owns a single
auditable launch surface: the fixed CPython 3.14 executable, exactly four argv
tokens, exact project cwd, and exactly two environment entries.  The operation
accepts no caller-selected root or authority; it obtains `exact_root` only from
the one canonical fixed-path dispatch after internal validation and consumes
that dispatch before the child launch.  All materially different surfaces are
explicitly forbidden in the package, design and T4 prompt.

The correction is confined to the three previously allowed package-control
files.  It does not modify implementation, equations, method, precision,
domain, thresholds, protected radial bytes, external source bytes, evidence or
repair-cycle accounting.  No Class-A finding remains.

## Downstream boundary

Root T0 may separately dispatch the formal zero-science T4 implementation
task bound to this corrected package and this review archive.  This review does
not itself dispatch T4 and does not authorize a sentinel, an official run,
reuse of any failed/sentinel result, V3.2 or global GREEN.
