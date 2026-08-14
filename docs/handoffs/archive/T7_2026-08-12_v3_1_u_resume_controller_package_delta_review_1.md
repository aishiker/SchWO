# T7 V3.1-U resume-controller package repair-1 delta review

Date: 2026-08-12

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U RESUME-CONTROLLER REPAIR PACKAGE READY FOR T4
```

```yaml
review_id: t7_v3_1_u_resume_controller_package_delta_review_1_20260812
gate_id: phase6_v3_1_u_resume_controller_repair_1
attempt: repair_1
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: configs/phase6_v3_1_u_resume_controller_package.json
  identities:
    - path: configs/phase6_v3_1_u_resume_controller_package.json
      sha256: 2fcd2e4cc57845b32573047fa3989e1bfcd4f520eefcea6f6df6504d164602fe
    - path: docs/phase6_v3_1_u_resume_controller_design.md
      sha256: 094235c0ce0158521da81ec0587899dc6dc942ab92866e8afe8f3102487fa9d7
    - path: docs/prompts/phase6_t4_v3_1_u_resume_controller.md
      sha256: 72e40f540d3f406c6d1af79931d425b9efc8e5517f21d6e91ba9b1c8b0333b05
    - path: docs/prompts/phase6_t7_v3_1_u_resume_controller_delta_review.md
      sha256: d61acbb61787746a5442dedbf52caa7815376bff482edd2ba5450e1c278e457a

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_u_resume_controller_package_review.md
    sha256: 05edd09266673bc0edb3428d25c33d7b3ea209019ed3ca8ca5424499bc6a1952
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - id: V3.1 frozen threshold set
      value: 16 unchanged threshold IDs/operators/values
      units: mixed dimensionless/logarithmic
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  blocking_criteria:
    - close v31ur_lock_authority_crash_chain
    - close v31ur_transaction_partial_suffix_recovery
    - preserve all frozen passed invariants and protected/current identities
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
GATE_LABEL: ACCEPT GREEN / V3.1-U RESUME-CONTROLLER REPAIR PACKAGE READY FOR T4

incremental_review_state:
  passed_items:
    - item_id: v31ur_lock_authority_crash_chain
      evidence_identity: stable never-renamed .writer.lock plus complete-staging/fsync/renamex_np(RENAME_EXCL)/dir-fsync authority chain and last authority_commit
    - item_id: v31ur_transaction_partial_suffix_recovery
      evidence_identity: atomic prepared record authenticates target preappend identity and exact blocks; exact byte-prefix recovery appends only missing tail
    - item_id: v31ur_identity_and_archive_governance
      evidence_identity: repaired candidate/source bindings exact; status/T0_current/T7_current unchanged at both endpoints
    - item_id: v31ur_interrupted_prefix
      evidence_identity: records 435/932129a4; ladders 8700/8f387abb; checkpoints 435/map 2269f129; next key (8,28,even)
    - item_id: v31ur_interruption_classification
      evidence_identity: no failure/threshold/nonfinite/U/B/C/terminal artifact or live writer; exact finite contiguous prefix
    - item_id: v31ur_scope_and_science_preservation
      evidence_identity: only four future controller/test paths allowed; original science and seven protected paths unchanged
    - item_id: v31ur_source_and_terminal_validation
      evidence_identity: original validate_live_sources=True and additive resume validator both mandatory before terminal PASS
    - item_id: v31ur_real_root_prohibition
      evidence_identity: implementation phase remains temp-copy/zero-solver only until formal implementation delta review and one-use T0 dispatch
  failed_items: []
  partial_allowed_items:
    - item_id: v31u_common_absolute_phase
      reason: remains the frozen PARTIAL convention limitation and is untouched by this control-plane package
  not_assessed_items:
    - item_id: v31u_science
      reason: no resumed Route-A/U/B/C, threshold or certificate result has been generated or reviewed
    - item_id: v31ur_controller_implementation
      reason: final controller implementation and real-filesystem fault-injection evidence are future T4 outputs
    - item_id: v3_2_and_global_project_state
      reason: outside this gate and unauthorized

findings:
  - finding_id: v31ur_lock_authority_crash_chain_closed
    class: CONTROL_PLANE_REPAIR
    summary: The corrected contract closes the missing-lock and partial-authority windows without changing any science byte or acceptance criterion.
  - finding_id: v31ur_transaction_partial_suffix_recovery_closed
    class: CONTROL_PLANE_REPAIR
    summary: Atomic prepared metadata plus authenticated byte-prefix completion closes the second-interruption append window while preserving fail-closed mismatch handling and the no-truncate/no-rewrite rule.
  - finding_id: v31ur_darwin_primitive_implementation_evidence
    class: FOLLOW_UP_DEBT
    summary: Current SDK/runtime expose renamex_np with RENAME_EXCL=0x4; exact same-volume behavior and every forced-death boundary remain mandatory T4 zero-solver temp-copy evidence before any real-root dispatch.
  - finding_id: v31ur_future_science
    class: FOLLOW_UP_DEBT
    summary: V3.1-U science, thresholds, certificates and V3.2 remain separately gated future work.

delta_review:
  reviewed_failed_items:
    - v31ur_lock_authority_crash_chain
    - v31ur_transaction_partial_suffix_recovery
  passed_invariants_rechecked:
    - v31ur_identity_and_archive_governance
    - v31ur_interrupted_prefix
    - v31ur_interruption_classification
    - v31ur_scope_and_science_preservation
    - v31ur_source_and_terminal_validation
    - v31ur_real_root_prohibition
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - sha256sum repaired candidate, prior archive, every package source binding, seven protected paths and frozen coordination surfaces
    - independent CPython 3.14 reload of the 435/8700/435 interrupted prefix and compact checkpoint-map reconstruction
    - xcrun --show-sdk-path plus read-only SDK lookup of renamex_np and RENAME_EXCL
    - CPython ctypes read-only symbol probe for renamex_np
    - git diff --check on the five repaired package/review files
  results:
    - repaired candidate hashes exact and all 26 source bindings plus seven protected bindings PASS
    - prior formal archive hash daba09ea92781596d54e9eefee729cfa0a1c117862443fa6445f4ab0d20f2c76 PASS
    - interrupted prefix remains exact 435 records, 8700 ladders and 435 checkpoints; map digest 2269f129814c26d609cf3fdd0a451a5fd35661a576cf4d030f4f7b9516366d11
    - SDK defines RENAME_EXCL as 0x00000004 and declares renamex_np; runtime symbol is present
    - no solver, lock acquisition, real-root append, permission change or terminal publication occurred
    - diff-check PASS
    - status.md, T0_current.md and T7_current.md remained byte-identical

non_claims:
  - package readiness only; V3.1-U science remains NOT_ASSESSED
  - no threshold or certificate outcome is accepted
  - no predecessor r3 reuse or promotion
  - common absolute phase remains PARTIAL
  - no V3.2 authorization
  - no full-domain V3 or Li-figure equivalence
  - no global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Delta conclusion

Both frozen failed items are closed at the package-contract level.  The stable
original lock pathname is continuously discoverable and never renamed,
unlinked, replaced or rewritten; its flock is retained through terminal 0555
and dual validation.  Complete staging plus fsync, Darwin no-replace atomic
publication and directory fsync prevent partial final-name authority,
prepared, checkpoint and commit files.  `authority_commit.json` is the final
pre-science publication, and incomplete attempts remain evidence in a
deterministic monotone chain.

After a complete atomic prepared record exists, each target's exact preappend
identity and canonical byte block are authenticated.  Recovery accepts only an
exact suffix prefix and appends its missing tail; mismatch, unknown bytes,
duplicate or gap remains terminal.  An unauthenticated staging fragment is
correctly distinguished from prepared science.  These semantics cover Route
A/U/B and staged Route C without changing or reusing a scientific result.

No previously passed invariant was damaged.  This bounded GREEN permits only
Root-T0 fresh verification and possible T4 implementation plus zero-solver
temporary-copy validation under the corrected frozen prompt.  It does not
authorize acquisition of the real lock, real-root resume, scientific
acceptance, V3.2 or global GREEN.
