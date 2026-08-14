# T7 formal implementation delta review — V3.1-U final bounded repair cycle 2

Date: 2026-08-13

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-U REPAIR CYCLE 2 IMPLEMENTATION CHANGES REQUIRED
```

## Verdict record

```yaml
review_id: t7_v3_1_u_repair_cycle2_implementation_delta_review_20260813
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
repair_id: phase6_v3_1_u_route_c_totality_repair_cycle2_v1
attempt: repair_2
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: implementation-only; sentinel and official dispatches/roots are absent
  identities:
    - path: scripts/phase6_v3_1_bhpt_mst_cycle2.wls
      sha256: 9b79eca8c205af5d01d6c2f06c2a48aa81ae0babf352e37ee79fe3a4c3cb2d34
    - path: src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py
      sha256: ec1239c3dcf23ed2d7c3752fc131ad25ae2289d48936a0095105a801d06d60a2
    - path: src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      sha256: 94af1455446e8c15cf20fedaa4e09833ed077aa89aef08796558f3e6989cbbfd
    - path: tests/regression/test_phase6_v3_hp_unitarity_publication.py
      sha256: 142e0cdcd0a1e7e079180d9c8323f9e3d1aae0904f96fc457f8bc4642be6feef
    - path: tests/unit/test_phase6_v3_cycle2.py
      sha256: b697adbd4df595f728b636f566cd27c1efba380e5b4f5df9892caa76b9b2797c
    - path: tests/unit/test_phase6_v3_hp_unitarity.py
      sha256: b55be267b08d663b91c294ac0cf27eec63b85c03078ae1ce792fefe891a82982

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
  external_snapshot:
    path: runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json
    sha256: 8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488
    content_inventory_sha256: d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2
    restored_identity_inventory_sha256: a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
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
GATE_LABEL: REVIEW YELLOW / V3.1-U REPAIR CYCLE 2 IMPLEMENTATION CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31u_repair2_exact_six_scope_and_identity
      evidence_identity: package comparison reconstructed exactly 44 unchanged bindings and six changed allowed paths; all six post hashes are exact and git diff-check passes
    - item_id: v31u_repair2_anchor_graph_and_wls_totality
      evidence_identity: 23 unique ordered odd anchors independently reconstructed; WLS has one ReggeWheelerRadial call site inside one MapIndexed traversal and exact MST/90/45/45 method contract; PASS and ERROR outcome schemas cover all anchors
    - item_id: v31u_repair2_durable_child_supervision
      evidence_identity: request/source_start/prelaunch/raw stdout/raw stderr/receipt/wait/reap/process-group/source_end and mutually exclusive terminal records are source-bound; signal, timeout, torn/missing/duplicate payload and child error tests pass
    - item_id: v31u_repair2_sentinel_official_separation
      evidence_identity: fixed-dispatch graph, wrong/missing review/hash/root rejection, official-before-sentinel rejection and official recomputation without sentinel-record reuse are present
    - item_id: v31u_repair2_snapshot_byte_identity
      evidence_identity: 25 regular 0444/nlink1 pairwise-distinct source files and five 0555 directories rebuild exact content and identity indexes; no symlink or .git exists; historical byte chain remains exact
    - item_id: v31u_repair2_zero_science_evidence
      evidence_identity: implementation evidence e22b06f6348f28d063d5e3289f6e39309bc686914c431b7fe727c4f43ddfc5e5, inventory 2f6e6f6e55bf984a9522dd0706a5710608e781797687c3015b4f48a0999ec441 and synthetic manifest a130e48851ded30fdd26aca64afd79cac3902661e2dcd06ca437ee2fe030ada8 report zero Python/Wolfram/sentinel/official/science calls and the exact 496/9920/102/458/23/16/5 graph
    - item_id: v31u_repair2_focused_quality_checks
      evidence_identity: independent CPython 3.14 overlay run 76 passed; unchanged CLI preflight PASS; Ruff check/format, compile and exact-six diff-check PASS
    - item_id: v31u_repair2_protected_invariants
      evidence_identity: CLI, Route-U oracle, package, review authority, seven protected radial sources, frozen domain/threshold/method and failed-root nonreuse identities rehash exact at start/end
  failed_items:
    - item_id: v31u_route_c_external_totality_and_provenance
      blocker_id: v31u_repair2_sentinel_runtime_environment_allowlist_false_acceptance
    - item_id: v31u_route_c_external_totality_and_provenance
      blocker_id: v31u_repair2_loaded_source_snapshot_closure_false_acceptance
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_repair2_sentinel_science
      reason: no sentinel dispatch/root exists and no Wolfram or solver call was run
    - item_id: v31u_repair2_official_science
      reason: no official dispatch/root exists; Route-C and V3.1-U science remain NOT_ASSESSED
    - item_id: v31u_repair2_thresholds_and_certificates
      reason: all 16 thresholds and five certificates require a later successful official candidate and are not evaluated here

findings:
  - finding_id: v31u_repair2_sentinel_runtime_environment_allowlist_false_acceptance
    class: BLOCKING_CURRENT_GATE
    summary: The actual module-entry runtime validator projects os.environ onto two reviewed keys before comparison, so an arbitrary extra environment variable survives the real launch surface and is invisible to the fail-closed invocation check.
    blocker_id: v31u_repair2_sentinel_runtime_environment_allowlist_false_acceptance
    violated_contract_item: The approved corrected package and implementation delta prompt require the exact fixed environment allowlist, reject extra environment and prohibit environment-selected authority or fallback for the one-use sentinel.
    exact_evidence: src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py lines 847-860 constructs relevant_environment using only PYTHONDONTWRITEBYTECODE and PYTHONPATH, rejects only SCHWO_V31_* names, then sends the filtered mapping to validate_sentinel_invocation. An independent CPython 3.14 overlay probe added EXTRA_UNREVIEWED_SENTINEL_AUTHORITY=1 and called the real _validate_current_sentinel_runtime with exact argv; it returned successfully (OBSERVED_ACCEPTED_EXTRA_ENV 1). The existing extra-environment unit test calls the lower-level validator directly and therefore does not exercise this reachable projection bypass.
    expected_value: The actual module entry must fail closed on every environment entry outside the explicitly frozen runtime policy and must not discard an unreviewed entry before validation. The enforceable policy, including any unavoidable interpreter/platform-injected keys, must be explicit and identity-bound rather than inferred after launch.
    observed_value: Any non-SCHWO_V31_* extra key is silently omitted from relevant_environment and the exact sentinel runtime validator accepts the otherwise exact invocation.
    bounded_repair: Correct the actual runtime validation path so it validates the unprojected relevant process environment against one explicit frozen allowlist and cannot hide caller-supplied entries. Add a test that launches/calls the actual module-entry runtime surface with one unrelated extra key and proves rejection before dispatch consumption/root creation. If unavoidable platform-injected keys make the current two-key literal contract impossible, Root T0 must first freeze a bounded control-plane clarification; T4 must not invent or silently broaden the allowlist.
    allowed_files:
      - src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      - tests/unit/test_phase6_v3_hp_unitarity.py
      - tests/regression/test_phase6_v3_hp_unitarity_publication.py
    fresh_root_rule: No sentinel dispatch or root may exist during the correction or recheck; no failed or synthetic scientific output may be promoted. Repair cycle 2 remains unconsumed until a later one-use dispatch/launch.
    required_tests_preflight: Exact CPython 3.14 focused suite plus actual-module-entry positive exact-environment test and negatives for arbitrary extra key, SCHWO authority key, missing key, changed value, extra argv and alternate invocation; all must complete with zero science calls and no dispatch/root.
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/schwo_mpmath_cp314_overlay_20260806:/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_cycle2.py tests/unit/test_phase6_v3_hp_unitarity.py tests/regression/test_phase6_v3_hp_unitarity_publication.py
    unblock_condition: The real _validate_current_sentinel_runtime path rejects every unreviewed environment entry without pre-validation projection, the exact reviewed invocation still passes, all authority/dispatch/root negatives remain fail-closed, all tests pass with zero science, and package/protected/exact-six-unrelated identities remain exact.

  - finding_id: v31u_repair2_loaded_source_snapshot_closure_false_acceptance
    class: BLOCKING_CURRENT_GATE
    summary: Loaded-source provenance accepts an arbitrary nonempty subset and duplicates of authenticated snapshot paths, while snapshot directory permissions are not revalidated; it therefore cannot prove the required complete unique loaded numerical-source closure at source_start/source_end.
    blocker_id: v31u_repair2_loaded_source_snapshot_closure_false_acceptance
    violated_contract_item: The approved design and implementation delta prompt require WLS/kernel/snapshot/audit/25-file/loaded-path start-end provenance and fail-closed missing, extra, alias, permission and drift adversaries for the 23-anchor Route-C child.
    exact_evidence: src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py lines 1925-1950 checks only that loaded_source_paths is a nonempty list and that each resolved path is a member of the authenticated snapshot. Independent direct probes showed that a single top-level ReggeWheeler source is accepted (OBSERVED_ACCEPTED_SINGLE_LOADED_SOURCE 1) and the same path repeated twice is accepted (OBSERVED_ACCEPTED_DUPLICATE_LOADED_SOURCE 2). The positive unit fixture likewise supplies only one loaded path. The snapshot identity validator checks the 25 file identities but does not include the five required 0555 directory modes, so directory-permission drift is also outside the observed source identity.
    expected_value: The WLS child must publish one exact, ordered, duplicate-free set of all frozen ReggeWheeler numerical source files actually loaded for the MST call, and Python must require exact equality against a package/source-derived authenticated list at both source boundaries. Missing, duplicate, extra, reordered, aliased, escaped, changed or permission-drifted source state must fail closed. The restored five directories must remain exact 0555 as part of the source identity.
    observed_value: One authenticated file, or duplicate repetitions of it, satisfies runtime validation; completeness and uniqueness are not established, and directory-mode drift is not represented by the source identity validator.
    bounded_repair: Freeze the exact required loaded-source inventory from the authenticated 25-file snapshot and the package entry graph; make WLS publish stable records for that inventory and make Python require exact cardinality/order/uniqueness/path/hash/stat identity at source_start and source_end. Extend snapshot validation to the five exact directories and reject permission, symlink, hardlink, missing, extra and alias drift. Add direct positive and adversarial tests; do not change MST/90/45/45, anchors, amplitudes, domain, thresholds or protected radial code.
    allowed_files:
      - scripts/phase6_v3_1_bhpt_mst_cycle2.wls
      - src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py
      - tests/unit/test_phase6_v3_cycle2.py
      - tests/unit/test_phase6_v3_hp_unitarity.py
      - tests/regression/test_phase6_v3_hp_unitarity_publication.py
    fresh_root_rule: No sentinel dispatch/root or official dispatch/root may be created. Only temp, zero-science fixtures may be used; no source snapshot byte or permission may be mutated in place.
    required_tests_preflight: Exact CPython 3.14 focused suite plus direct missing/duplicate/reordered/extra/alias/outside/hash/stat/file-mode/directory-mode/symlink/hardlink adversaries, WLS first/middle/last success/error schema checks and unchanged CLI preflight, all with zero Wolfram/solver/science calls.
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/schwo_mpmath_cp314_overlay_20260806:/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_cycle2.py tests/unit/test_phase6_v3_hp_unitarity.py tests/regression/test_phase6_v3_hp_unitarity_publication.py
    unblock_condition: Runtime loaded-source evidence is exact, complete, ordered and unique; every required source and directory identity is revalidated at start/end; all listed adversaries fail before terminal acceptance; exact 23 anchors and WLS method/outcome/supervision contracts remain unchanged; tests and quality checks pass with zero science and no dispatch/root.

  - finding_id: v31u_repair2_snapshot_commit_association_inherited_only
    class: NONBLOCKING_LIMITATION
    summary: The restored 25-file snapshot has no .git; commit association remains honestly inherited from the immutable historical ledger and audit ZIP, not independently asserted by this review.
  - finding_id: v31u_repair2_science_not_assessed
    class: NONBLOCKING_LIMITATION
    summary: This implementation review does not assess Route-C numerical results, the 16 thresholds, five certificates or V3.1-U science.
  - finding_id: v31u_repair2_v3_2_forbidden
    class: FOLLOW_UP_DEBT
    summary: V3.2, broader V3 claims and global GREEN remain outside this gate and forbidden.

delta_review:
  reviewed_failed_items:
    - v31u_route_c_external_totality_and_provenance
  passed_invariants_rechecked:
    - v31u_repair2_exact_six_scope_and_identity
    - v31u_repair2_anchor_graph_and_wls_totality
    - v31u_repair2_durable_child_supervision
    - v31u_repair2_sentinel_official_separation
    - v31u_repair2_snapshot_byte_identity
    - v31u_repair2_zero_science_evidence
    - v31u_repair2_focused_quality_checks
    - v31u_repair2_protected_invariants
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - complete source read and static/dataflow inspection of the six changed paths, approved package/design/prompts, liveness protocol/template and package authority archive
    - independent SHA-256 comparison of 50 package-bound repository paths, exact six changed-path inventory, CLI, oracle, seven protected radial sources and external-source chain at start/end
    - direct reconstruction of 23 ordered unique anchors and WLS call/outcome/method constants
    - direct 25-file/five-directory snapshot inventory, content/identity-index, link/mode and historical ZIP/ledger comparison
    - exact CPython 3.14 overlay focused pytest; unchanged CLI preflight; Ruff check/format, compile and exact-six diff-check
    - independent in-memory adversarial calls through the actual sentinel runtime validator and loaded-source validator; no producer, WolframKernel, radial solver or science invocation
    - read-only absence/process/transient checks for fixed dispatches and repair-2 sentinel/official roots
  results:
    - exact-six hashes and the 44 unchanged package bindings match; no unrelated implementation path changed
    - 76 focused tests passed in 2.98 seconds; CLI preflight PASS; Ruff, format, compile and diff-check PASS
    - implementation evidence e22b06f6348f28d063d5e3289f6e39309bc686914c431b7fe727c4f43ddfc5e5, inventory 2f6e6f6e55bf984a9522dd0706a5710608e781797687c3015b4f48a0999ec441, JUnit fbcb30c771dd311b21a75cd269473734642d6b9dcf81c76158e512b00a5871a3 and synthetic manifest a130e48851ded30fdd26aca64afd79cac3902661e2dcd06ca437ee2fe030ada8 rehash exact
    - snapshot contains 25 regular 0444/nlink1 files and five 0555 directories, with exact content index d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2 and identity index a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
    - arbitrary unrelated extra environment was accepted by the real sentinel runtime path after projection; one loaded source and a duplicate loaded source list were accepted by runtime provenance validation
    - sentinel/official dispatches and repair-2 roots remain absent; no relevant producer/Wolfram/science process was found; zero science call was made

non_claims:
  - V3.1-U science remains NOT_ASSESSED
  - no Route-C result, threshold or certificate is accepted
  - repair cycle 2 is not consumed because no sentinel dispatch or launch occurred
  - no sentinel dispatch, sentinel launch, official dispatch/run, failed-root reuse or artifact promotion is authorized
  - no V3.2, broader V3 claim or global GREEN is authorized

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 1
  current_bounded_scientific_repair: 2
  repair_cycle2_consumed: false
  same_substantive_blocker_remaining: true
  bounded_pre_sentinel_implementation_correction_available: true
  t0_adjudication_required: false
```

## Independent assessment

The exact-six implementation is substantially bounded: anchor cardinality,
WLS total outcome grammar, durable child closure, sentinel/official separation,
source bytes, protected radial identities and zero-science evidence all pass.
The focused suite also passes.  Those facts do not close the frozen Route-C
provenance item, because two reachable acceptance paths remain broader than
the reviewed contract.

First, the real sentinel module entry filters the current environment before
validating it, so a caller-supplied unrelated variable is not observed.
Second, the external-runtime validator proves only that each reported loaded
path belongs to the snapshot; it does not prove a complete unique loaded
source set, and the snapshot validator omits directory-permission closure.
Both false acceptances were reproduced without science.  They are current-gate
Class-A blockers rather than style hardening because the next action would be
the final one-use Route-C sentinel.

## Downstream boundary

Root T0 may freeze a bounded pre-sentinel implementation correction within
the already approved exact-six scope and request a delta-only recheck.  Root
T0 may not create or consume the sentinel dispatch yet.  Repair cycle 2 remains
unconsumed until that later one-use dispatch/launch.  This review does not
authorize WolframKernel, sentinel or official science, V3.2, or global GREEN.
