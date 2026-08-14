# T7 formal review — V3.1-U repair-cycle-1 terminal scientific failure

Date: 2026-08-13

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-U CHANGES REQUIRED
```

## Verdict record

```yaml
review_id: t7_v3_1_u_repair_cycle1_terminal_scientific_review_20260813
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
attempt: repair_1
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/runs/phase6/classic_scattering/v3_1_hp_unitarity_deficit_repair1_v1_20260812T064653Z_py314
  terminal_state: FAILED
  identities:
    - path: failure.json
      sha256: e3874e7565dc35498513af8112577810dd9059035f43a9d4573d633c2ae752aa
    - path: failure_manifest.json
      sha256: f977a0d555652d028b3b73d18990b902f37a55c3dd9305c6e6da55f66593050d
    - path: dispatch_consumption.json
      sha256: 91598bf9233134a8e32f04d48b029f27e39bcbb938ddc606dddd272a573c9c7e
    - path: records.jsonl
      sha256: 04b18189f4baf47ad4ebd94b761635cec5d9eb9c1b591ac0b9e694ddf1e3dea2
    - path: ladder_records.jsonl
      sha256: a8cb91d0fd9374003ad63fa2a6ddd2c57fa3bf4f287c5f44aa287878746e7f7c
    - path: unitarity_route_map.json
      sha256: 5eee07ece78204265fe45069ef57a653a61a8ee9d09ff4b4d7e8928bb385c822
    - path: route_u_records.jsonl
      sha256: 99fc2dd34ebcd029a86b22c0dd04a20ba2423711b0879c481e39d597bc5489d9
    - path: route_u_ladders.jsonl
      sha256: 38b377f61e9da1cd1dfe4aebb68642ed6e00ab25a434ffa4556878f5118da2c4
    - path: ap_records.jsonl
      sha256: 3de519e8e9e55be8f4908a6715f5730f2f039bb5eed76b90acac8aa004e6b527
    - path: external_raw.request.json
      sha256: 6094323a056d7e1396affccd87ef15851612ac404ab84d29b7cbae7c7415bf82

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_hp_unitarity_review.md
    sha256: 8822263a09bde6d5b0bd3b2c00117eb5ac1648ae9f804a4e71380b27fa90cb82
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds_source:
    path: configs/phase6_v3_0_thresholds.json
    sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  external_anchor_matrix:
    path: configs/phase6_v3_0_external_anchor_matrix.json
    sha256: 06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485
  replacement_package:
    path: configs/phase6_v3_1_hp_unitarity_replacement_package.json
    sha256: decde34bcdc90db0bc69be446357e306cfe942c84a8d575902eddaa7d1ff6877
  repair_cycle1_package:
    path: configs/phase6_v3_1_u_repair_cycle1_package.json
    sha256: 85bff01def7286ebaf1682d5b5498209dfbbc452e098e1d8633e05fcc1b7554c
  blocking_criteria:
    - exact 496/9920 Route-A graph
    - frozen 496-entry direct-Gamma route map
    - exact 318/954 Route-U graph
    - exact 102/458 Route-B graph
    - exact 23 ordered Route-C records from a source-bound external runtime
    - all 16 threshold evaluations and five certificates
    - start/end identity closure for every scientific source and runtime
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
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-U CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31u_repair1_terminal_identity_and_immutability
      evidence_identity: failure_manifest.json/f977a0d555652d028b3b73d18990b902f37a55c3dd9305c6e6da55f66593050d; 827 regular files all 0444/nlink1; two directories inclusive both 0555; zero links
    - item_id: v31u_route_a_complete_inventory
      evidence_identity: 496 records/04b18189f4baf47ad4ebd94b761635cec5d9eb9c1b591ac0b9e694ddf1e3dea2 and 9920 ladders/a8cb91d0fd9374003ad63fa2a6ddd2c57fa3bf4f287c5f44aa287878746e7f7c
    - item_id: v31u_route_map_frozen_selector
      evidence_identity: unitarity_route_map.json/5eee07ece78204265fe45069ef57a653a61a8ee9d09ff4b4d7e8928bb385c822; 496 entries and exact 318 small-Gamma Route-U selections
    - item_id: v31u_route_u_geometry_repair_and_complete_graph
      evidence_identity: 954 ordered precision records/99fc2dd34ebcd029a86b22c0dd04a20ba2423711b0879c481e39d597bc5489d9 and 318 PASS ladders/38b377f61e9da1cd1dfe4aebb68642ed6e00ab25a434ffa4556878f5118da2c4; minimum guard digits 30
    - item_id: v31u_route_b_complete_graph
      evidence_identity: 102 exact keys and 458 ordered AP records/3de519e8e9e55be8f4908a6715f5730f2f039bb5eed76b90acac8aa004e6b527
    - item_id: v31u_one_use_dispatch_and_fresh_root
      evidence_identity: dispatch 4abb301c7bd1f0389ab0341e6936306254b99b3396b19a7a119ab4aa5f7ad176; consumption 91598bf9233134a8e32f04d48b029f27e39bcbb938ddc606dddd272a573c9c7e; exact fresh root; science_calls_before_consumption=0
    - item_id: v31u_failed_predecessor_nonreuse
      evidence_identity: run_contract predecessor_science_reused=false; new records/ladders are fresh files with inode identities distinct from the failed predecessor; official source path recomputes Route A/U/B and reads the predecessor only for frozen authority/geometry preflight
    - item_id: v31u_protected_radial_identity
      evidence_identity: all seven protected SHA-256 values above rehashed exact at review start/end
    - item_id: v31u_failure_terminalization
      evidence_identity: failure.json/e3874e7565dc35498513af8112577810dd9059035f43a9d4573d633c2ae752aa; resumable=false; scientific_pass=false; no live writer/process/lock/transient in the reviewed root
  failed_items:
    - item_id: v31u_route_c_external_totality_and_provenance
      blocker_id: v31u_route_c_external_totality_and_provenance
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_route_c_records
      reason: the exact 23-anchor request exists but external_raw.json and external_records.jsonl are absent, so 0/23 Route-C records are assessable
    - item_id: v31u_thresholds_and_certificates
      reason: the run stopped before evaluation; all 16 thresholds and all five certificates are absent and NOT_ASSESSED
    - item_id: v31u_gate_scientific_acceptance
      reason: source_map, uncertainty_budget, summary, report and success manifest do not exist

findings:
  - finding_id: v31u_route_c_external_totality_and_provenance
    class: BLOCKING_CURRENT_GATE
    summary: The exact 23-anchor Route-C batch terminated with child exit 70 before publishing any record, while the failed key/error and the external WLS/kernel/BHPT execution identities were not durably bound by this root.
    blocker_id: v31u_route_c_external_totality_and_provenance
    violated_contract_item: Frozen review items 4, 10 and 11 require exactly 23 ordered independent Route-C records, all external threshold/certificate operands, and exact start/end scientific-source/runtime identities.
    exact_evidence: failure.json/e3874e7565dc35498513af8112577810dd9059035f43a9d4573d633c2ae752aa records stage=route_c and external Route-C failed exit=70 with empty stderr; external_raw.request.json/6094323a056d7e1396affccd87ef15851612ac404ab84d29b7cbae7c7415bf82 is the exact canonical 23-anchor inventory; external_raw.json and external_records.jsonl are absent; current scripts/phase6_v3_1_bhpt_mst_cycle2.wls SHA a7a53b9fee2e2001132b0b437b233f4fafff1362a113d21105913e2263dcdf6a exits 70 when the batch is not a 23-list or at least one record contains MST_FAILED/AMPLITUDE_INVALID, but it publishes neither the failed record nor stdout before Exit[70]; src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py run_external_records captures stdout/stderr in memory and persists neither failure stream; source_start.json/754be2875cddfa691b19f5fd17edb1c85b0087c789e810789f709a834a9c0c0e has 49 exact live entries but omits that WLS path, WolframKernel and bhpt_source.
    expected_value: A source-bound, ordered 23-record external batch with exit 0, empty stderr, exact request/output identities, per-anchor independent odd-RW provenance, and durable start/end identities for the WLS, WolframKernel and BHPT commit/clean source inventory; on failure the exact key, error class, stdout/stderr, exit/wait and source identities must remain independently recoverable.
    observed_value: The child returned 70 and the gate has 0/23 Route-C records. Conditional on the current WLS bytes, exit 70 means at least one anchor yielded MST_FAILED or AMPLITUDE_INVALID (or the returned object was not the exact 23-list), but the exact key and lower-level cause are UNKNOWN because no error record/stdout was published and the executed WLS identity was not included in source_start. The evidence does not support classifying this as a resource failure, a particular mode failure, a frozen-domain inconsistency or a physics-threshold failure.
    bounded_repair: Freeze at most repair cycle 2 as a two-stage fail-closed external-route closure. Phase A may only bind/re-hash the exact WLS, WolframKernel and complete clean BHPT source identity at both start and end; publish canonical per-anchor result/error records plus raw stdout/stderr/exit/wait on every terminal branch; and add zero-science adversarial fixtures. A separately Root-T0-authorized one-shot 23-anchor sentinel must then either complete all 23 exact frozen anchors under unchanged Method=MST, WorkingPrecision=90, PrecisionGoal=45 and AccuracyGoal=45, or terminalize with the exact failing key/error and consume repair cycle 2 without launching an official root. Only after a 23/23 sentinel PASS may a new official candidate use a fresh absent root. Do not change the anchor set, domain, threshold, convention, protected radial bytes or accept/drop/retry individual anchors; do not reuse any science byte from either failed root.
    allowed_files:
      - scripts/phase6_v3_1_bhpt_mst_cycle2.wls
      - src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py
      - src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      - tests/unit/test_phase6_v3_cycle2.py
      - tests/unit/test_phase6_v3_hp_unitarity.py
      - tests/regression/test_phase6_v3_hp_unitarity_publication.py
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q -p no:cacheprovider tests/unit/test_phase6_v3_cycle2.py tests/unit/test_phase6_v3_hp_unitarity.py tests/regression/test_phase6_v3_hp_unitarity_publication.py
    unblock_condition: A frozen repair-cycle-2 package and T7 delta review prove exact external source/runtime start-end binding and durable success/failure publication; a separately authorized one-shot sentinel returns exactly 23 ordered records with exit0/empty stderr and no omitted anchor; then a fresh official root independently recomputes Route A/U/B/C and passes all 16 frozen thresholds and all five certificates with protected/domain/threshold/convention identities unchanged.
  - finding_id: v31u_completed_a_u_b_are_not_gate_acceptance
    class: NONBLOCKING_LIMITATION
    summary: Complete Route A, repaired Route U and Route B are immutable failed-root evidence, but they cannot be promoted to V3.1-U PASS or reused in a future accepted root.
  - finding_id: v31u_full_domain_and_downstream_out_of_scope
    class: FOLLOW_UP_DEBT
    summary: Full-domain V3, V3.2, Li-equivalence and finite-radius observer claims remain outside this bounded gate.

delta_review:
  reviewed_failed_items:
    - v31u_route_u_auxiliary_geometry_totality
    - v31u_auxiliary_radius_closed_boundary_roundoff
  passed_invariants_rechecked:
    - v31u_terminal_identity_and_immutability
    - v31u_route_a_complete_inventory
    - v31u_route_map_frozen_selector
    - v31u_one_use_dispatch_and_fresh_root
    - v31u_failed_predecessor_nonreuse
    - v31u_protected_radial_identity
    - v31u_failure_terminalization
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - exact SHA-256/stat/nlink/mode inventory of the root, frozen prompt, domain, thresholds, anchor matrix, packages, dispatch and protected sources
    - independent build_manifest(root, overall_state=FAILED) object and canonical-byte comparison
    - exact CPython 3.14 canonical JSONL reload plus validate_route_map and validate_oracle_ladder over all Route-A/Route-U/AP records
    - independent exact external-anchor reconstruction and request comparison
    - read-only source/dataflow inspection of run_external_records and phase6_v3_1_bhpt_mst_cycle2.wls
    - read-only dispatch/predecessor inode/source-ledger/process/transient checks
  results:
    - root inventory: 827 regular files, two directories inclusive, 29,013,094 file bytes; all files 0444/nlink1; both directories 0555; zero symlink
    - independent canonical tree index: 4a23c86a56e0d244b78b195d42aec6f4314aa6a8cb6710c0d3ae1e8f8578c698
    - failure manifest: 826 non-self artifacts; rebuilt object equality PASS and canonical byte equality PASS
    - exact inventories: Route A 496/9920; route map 496 with N_U=318; Route U 954 records/318 PASS ladders; Route B 102/458; Route C 0/23
    - all 318 Route-U ladders independently revalidated PASS; route-map ordinals and original 496-mode order exact
    - exact one-use dispatch/consumption/root binding PASS; previous and current science files have distinct inodes and the current run contract says predecessor_science_reused=false
    - 49 recorded source_start identities rehash exact now, but WLS/Wolfram/BHPT are absent from that ledger and source_end is absent after failure
    - current external environment read-only identities: WLS a7a53b9fee2e2001132b0b437b233f4fafff1362a113d21105913e2263dcdf6a; WolframKernel 70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c; BHPT commit 2e01209271fb3d0d92705d5c27bd9e00a6140981 with clean status. These current values are not retroactive proof of the execution-time WLS/BHPT bytes.
    - no related WolframKernel/official producer process, new-root lock, tmp, partial or quarantine path found

non_claims:
  - V3.1-U scientific acceptance is FAIL; Route-C science, all 16 thresholds and all five certificates are NOT_ASSESSED
  - no exact failing Route-C key or lower-level MST/amplitude cause is established by the immutable root
  - completed Route-A, Route-U and Route-B records are failure evidence and are not reusable as accepted science
  - no threshold, domain, convention, precision, anchor or protected-radial change is authorized
  - no V3.2, full-domain V3, Li-figure equivalence, finite-radius observer claim or global GREEN
  - only Root T0 may freeze a final bounded repair-cycle-2 package; this review does not dispatch T4 or authorize science

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 1
  same_substantive_blocker_remaining: false
  new_substantive_blocker: v31u_route_c_external_totality_and_provenance
  final_bounded_repair_cycle_available: true
  t0_adjudication_required: false
```

## Exact causal classification

The old `v31u_auxiliary_radius_closed_boundary_roundoff` blocker is closed:
the repaired candidate contains all 318 Route-U ladders and 954 precision
records, and independent validation returns `PASS` for every ladder.  The
present failure is therefore not the same substantive blocker.

The durable immediate cause is a Route-C child exit 70 before output
publication.  In the currently readable WLS, exit 70 is the script's own
fail-closed branch for a non-23 batch or an error record generated by
`MST_FAILED`/`AMPLITUDE_INVALID`; it is not an operating-system resource exit
code.  However, the immutable root does not bind the executed WLS/BHPT bytes
and does not retain the failed record or captured stdout.  Consequently the
specific anchor and lower-level cause are formally `UNKNOWN`.  Assigning a
specific mode, resource exhaustion, implementation bug or physical
inconsistency would overstate the evidence.

This is nevertheless a complete current-gate blocker: the frozen claim
requires 23 Route-C records and has zero.  One final bounded repair cycle is
available because the completed repair addressed a different Route-U geometry
defect.  That final cycle must first make external provenance and failure
diagnostics durable and must fail closed before any fresh official run if its
one-shot sentinel does not produce all 23 frozen anchors.

## Downstream boundary

This verdict authorizes no implementation, no new external call, no solver,
no official candidate, no V3.2 and no global GREEN.  Only Root T0 may freeze a
final repair-cycle-2 package, followed by the required package and delta
reviews and a separately authorized one-shot execution.
