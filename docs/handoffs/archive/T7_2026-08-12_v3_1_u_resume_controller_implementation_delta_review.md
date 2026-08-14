# T7 V3.1-U resume-controller implementation delta review

Date: 2026-08-12

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-U RESUME CONTROLLER IMPLEMENTATION CHANGES REQUIRED
```

```yaml
review_id: t7_v3_1_u_resume_controller_implementation_delta_review_20260812
gate_id: phase6_v3_1_u_resume_controller_repair_1
attempt: repair_1
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: src/schwgw/validation/phase6_v3_hp_unitarity_resume.py
  identities:
    - path: src/schwgw/validation/phase6_v3_hp_unitarity_resume.py
      sha256: c1ec991481f76fa828e026a397fffb7736118838498fbe4746678cf1196abaf9
    - path: scripts/phase6_v3_1_hp_unitarity_resume.py
      sha256: 49746f878feb16eb98800b5a2dfa949ab1690c2286eb612ebbd7d8e4f68b6291
    - path: tests/unit/test_phase6_v3_hp_unitarity_resume.py
      sha256: 373200067cf5558084a6e60f9a6b7c5fe5f0d43b3e7142afb1ee2cbe258ae5f9
    - path: tests/regression/test_phase6_v3_hp_unitarity_resume_publication.py
      sha256: 95100ac6024e5f8f352ca62c52c175835339406f257e3e9ffdcde45d783241f0

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_u_resume_controller_delta_review.md
    sha256: d61acbb61787746a5442dedbf52caa7815376bff482edd2ba5450e1c278e457a
  package:
    path: configs/phase6_v3_1_u_resume_controller_package.json
    sha256: 2fcd2e4cc57845b32573047fa3989e1bfcd4f520eefcea6f6df6504d164602fe
  package_approval:
    path: docs/handoffs/archive/T7_2026-08-12_v3_1_u_resume_controller_package_delta_review_1.md
    sha256: f2aa03db09dd344462cddcba392ded858663232a5948377b44c673651b9e0326
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
    - stable never-renamed lock and continuous flock through terminal dual validation
    - atomic monotone authority/prepared/checkpoint/commit transaction recovery
    - exact-prefix authenticated append-only JSONL recovery
    - exact one-use implementation approval and Root-T0 dispatch binding
    - non-resumable terminalization of scientific/provenance/threshold/nonfinite failures
    - committed Route-C transaction semantics
    - additive validator rejects duplicate, gap, trailing bytes and every unknown or semantically invalid control artifact
    - observer-safe but writer-sensitive liveness
    - protected/source/current identities and interrupted prefix remain exact
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

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-U RESUME CONTROLLER IMPLEMENTATION CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31ur_four_file_scope_and_identity
      evidence_identity: exact four hashes; no frozen science/formula/selector/threshold/domain/convention edit
    - item_id: v31ur_interrupted_prefix_and_liveness
      evidence_identity: 435 Route-A modes; 8700 ladders; ordinals 0..434; next (8,28,even); checkpoint map 2269f129; active_writer=false; mutations=0; science_calls=0
    - item_id: v31ur_stable_lock_runtime
      evidence_identity: stable_writer_exclusion opens the original O_NOFOLLOW path, verifies inode/link identity, holds nonblocking flock across success/failure terminal sealing and never renames/unlinks it
    - item_id: v31ur_atomic_transaction_runtime
      evidence_identity: complete staging/fsync/renamex_np(RENAME_EXCL)/directory-fsync publication plus authenticated O_APPEND missing-tail recovery and monotone attempts
    - item_id: v31ur_one_use_dispatch_and_science_barrier
      evidence_identity: package/package-approval/implementation-approval/dispatch/root/prefix/lock/prior-chain bindings precede authority_commit and every callback
    - item_id: v31ur_route_order_and_route_c
      evidence_identity: Route-A completes before route-map/U/B/C; Route-C completion is prepared/commit-bound rather than output-existence-bound
    - item_id: v31ur_failure_terminalization
      evidence_identity: ordinary post-authority science/provenance/threshold/validator exceptions seal failure.json plus failure_manifest under held flock and forbid resume
    - item_id: v31ur_liveness_classifier
      evidence_identity: read-only observer and caffeinate wrapper excluded; canonical writer command or writable lsof fd detected
    - item_id: v31ur_quality_checks
      evidence_identity: focused/adjacent 112 passed; Ruff check/format, compile and diff-check PASS
  failed_items:
    - item_id: v31ur_additive_validator_authority_inventory_closure
      blocker_id: v31ur_additive_validator_false_acceptance
  partial_allowed_items:
    - item_id: v31u_common_absolute_phase
      reason: frozen convention limitation remains PARTIAL and is outside this controller implementation gate
  not_assessed_items:
    - item_id: v31u_science
      reason: no real-root resume or Route-A/U/B/C science was run or reviewed
    - item_id: v3_2_and_global_project_state
      reason: outside this gate and unauthorized

findings:
  - finding_id: v31ur_additive_validator_false_acceptance
    class: BLOCKING_CURRENT_GATE
    summary: The additive validator accepts unknown attempt-level control files and accepts semantically invalid authority files when a self-consistent authority_commit merely rebinds their hashes, so it does not independently rebuild every authority/control inventory as frozen.
    blocker_id: v31ur_additive_validator_false_acceptance
    violated_contract_item: Required checks 8-9 and the approved T4 contract requiring the additive validator to independently rebuild every attempt, lock identity, authority, transaction and manifest-bound control artifact, including fail-closed extra-control negatives.
    exact_evidence: src/schwgw/validation/phase6_v3_hp_unitarity_resume.py:1966-2050 validates authority_commit's self-recorded identities and known transaction/recovery directories but neither parses/rebuilds the seven authority-file semantics nor rejects an unknown attempt-level regular file; lines 2085-2144 semantically bind only the latest resume_authority and do not close prior committed authorities or exact attempt inventories. Original build_manifest at src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py:794-813 includes arbitrary files, and its validator at lines 699-722 therefore cannot supply the missing allowed-set check. Independent zero-science temp fixtures returned exactly `extra_control_validator_result=ACCEPTED` and `invalid_authority_semantics_result=ACCEPTED`.
    expected_value: Every unknown/extra control path and every authority payload whose exact schema, root, stable-lock identity, liveness, source ledger, approval, dispatch, implementation hashes or monotone predecessor chain is invalid must raise ResumeContractError even when all self-reported hashes and the terminal manifest are internally recomputed.
    observed_value: `_validate_resume_control_prefix(root, 435)` returned normally for (a) attempt_0001 containing only unexpected_control.json and (b) a committed attempt whose seven required authority files were all `{}` while authority_commit correctly rebound their live identities.
    bounded_repair: Add an exact per-attempt/per-transaction/recovery/staging allowed-path grammar; reject every unclassified path; semantically reconstruct all seven authority files for every committed attempt and the admissible incomplete subset for every abandoned attempt; bind the stable lock identity/continuous-lock declarations, prior chain, dispatch single-use, implementation approval/hashes and source ledger independently rather than trusting authority_commit; extend terminal validation across all attempts. Add adversarial tests that recompute commit/manifest identities after semantic tampering and tests for extra files/directories at each control level.
    allowed_files:
      - src/schwgw/validation/phase6_v3_hp_unitarity_resume.py
      - scripts/phase6_v3_1_hp_unitarity_resume.py
      - tests/unit/test_phase6_v3_hp_unitarity_resume.py
      - tests/regression/test_phase6_v3_hp_unitarity_resume_publication.py
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_hp_unitarity.py tests/regression/test_phase6_v3_hp_unitarity_publication.py tests/unit/test_phase6_v3_hp_unitarity_resume.py tests/regression/test_phase6_v3_hp_unitarity_resume_publication.py
    unblock_condition: Both frozen false-acceptance fixtures and their full terminal-manifest variants raise ResumeContractError; tests explicitly reject extra attempt/transaction/recovery controls and semantically invalid current/prior authorities after recomputed self-hashes; all existing 112 tests plus new negatives pass; exact four-file scope, 26 source bindings, seven protected hashes, three coordination hashes and real 435/8700/435 prefix remain unchanged.
  - finding_id: v31ur_temp_evidence_inventory
    class: CONTROL_PLANE_REPAIR
    summary: T4's temporary real-filesystem evidence inventory independently recomputes exactly, but its passing suite omitted the validator adversaries above.
  - finding_id: v31ur_future_science
    class: FOLLOW_UP_DEBT
    summary: V3.1-U scientific thresholds/certificates and all V3.2 work remain separately gated and NOT_ASSESSED.

delta_review:
  reviewed_failed_items:
    - v31ur_controller_implementation
  passed_invariants_rechecked:
    - v31ur_identity_and_archive_governance
    - v31ur_interrupted_prefix
    - v31ur_stable_lock_runtime
    - v31ur_atomic_transaction_runtime
    - v31ur_one_use_dispatch_and_science_barrier
    - v31ur_route_order_and_route_c
    - v31ur_failure_terminalization
    - v31ur_liveness_classifier
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - sha256 rehash of the review prompt, approved package archive, four implementation files, package source bindings, seven protected paths and three frozen coordination files
    - independent CPython 3.14 inspect_interrupted_root on the real root with exact overlay and no lock acquisition
    - independent reconstruction of the T4 temporary evidence inventory as the compact path -> {sha256,size,mode,nlink} mapping
    - focused/adjacent CPython 3.14 pytest on the original and resume controller unit/regression files
    - Ruff check and format --check on the four implementation files
    - CPython 3.14 in-memory compile of the four implementation files and git diff --check
    - two zero-science TemporaryDirectory adversarial calls to _validate_resume_control_prefix
  results:
    - candidate hashes, package approval and review prompt exact
    - all 26 package source bindings and seven protected hashes exact
    - real root remains exactly 435 modes, 8700 ladders, next ordinal 435 at kM=8 ell=28 even, checkpoint map 2269f129814c26d609cf3fdd0a451a5fd35661a576cf4d030f4f7b9516366d11, active_writer=false, mutations=0 and science_calls=0
    - T4 temp evidence root contains 8925 regular files and its compact inventory SHA-256 is 85585320ffa52f5d957c64f49118751c6d78d5f26bc946ead6c02297ebc711f4
    - T0 inspect record SHA-256 is 0e426d17365ef7da352cd3d835d7a6bfbae91e821bc350297fb03c2f4df9bef0
    - focused/adjacent tests 112 passed in 18.37s
    - Ruff check PASS; four files already formatted; in-memory compile PASS; diff-check PASS
    - extra control adversary was accepted instead of rejected
    - semantically invalid but self-consistently rehashed authority set was accepted instead of rejected
    - no solver, science callback, real lock acquisition, real-root mutation or V3.2 action occurred

non_claims:
  - controller implementation is not ready for one-use real-root dispatch
  - V3.1-U science remains NOT_ASSESSED
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

## Review conclusion

The controller's stable lock, atomic publication, exact-prefix append recovery,
Route ordering, Route-C commit semantics, one-use dispatch barrier and ordinary
failure terminalization are sufficient and remain frozen passed invariants.
The real interrupted root was inspected read-only and was unchanged.

The current implementation nevertheless cannot be authorized for a real-root
resume because the additive validator does not yet provide the exact authority
and control-inventory closure promised by the approved package.  A terminal
manifest can bind extra bytes without establishing that they are allowed, and
an authority commit can bind invalid authority payloads without independently
establishing their semantics.  The bounded repair is limited to the same four
controller/test paths and must preserve all passed invariants.  This decision
does not assess V3.1-U science and does not authorize V3.2 or global GREEN.
