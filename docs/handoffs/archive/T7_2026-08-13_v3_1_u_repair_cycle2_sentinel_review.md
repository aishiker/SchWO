# T7 terminal scientific review — V3.1-U repair-cycle-2 Route-C sentinel

Date: 2026-08-13

```text
ADVANCE_DECISION: ESCALATE
CLAIM_STATUS: FAIL
GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED
```

## Verdict record

```yaml
review_id: t7_v3_1_u_repair_cycle2_route_c_sentinel_terminal_review_20260813
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
repair_id: phase6_v3_1_u_route_c_totality_repair_cycle2_v1
attempt: repair_2_terminal_sentinel_review
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: runs/phase6/classic_scattering/v3_1_u_route_c_sentinel_repair2_v1_20260812T221323Z_py314
  root_state:
    mode: 0555
    directories: 2
    directories_all_mode: 0555
    regular_files: 17
    files_all_mode: 0444
    files_all_nlink: 1
    symlinks: 0
    active_writer_or_related_process: false
    terminal: true
    overall_state: FAILED
    resumable: false
    scientific_pass: false
  identities:
    - path: dispatch_consumption.json
      sha256: 6b5deeff2a22c009da07631b76faa5c300dbe0ba57282f429fc6130dc8b79dda
      size: 5198
    - path: external_evidence/external_attempt_records.jsonl
      sha256: a111d6dcc7ff937409ce62df73b71e0f0f65881a8d7066d4062d1295fba76399
      size: 17330
    - path: external_evidence/external_child_payload.raw.json
      sha256: faa904b92e8248f79cc5dabcf6fd72fcbb85721d93a42884227e130c9d8dc0d9
      size: 23468
    - path: external_evidence/external_failure.json
      sha256: 31313cb56e352af5e087e4562e134594d74350265b885d29f24259dd6244e3c2
      size: 326
    - path: external_evidence/external_failure_manifest.json
      sha256: ffb40274831b4662d9d71c281bead2e6bb96c20c32f502886fceee13ff506f0e
      size: 2089
    - path: external_evidence/external_prelaunch.json
      sha256: e010eae5870d62df725eef211cfac62edfd8a2ffbd31b1b5b807152034206f2f
      size: 1090
    - path: external_evidence/external_receipt.json
      sha256: 46f06d8ce3665bac5dfb175d98cdbab6e6ea72a0a51d213d83907745e3477364
      size: 606
    - path: external_evidence/external_request.json
      sha256: 54fe975cce7d6128b6ef21145fbe31600403370bc1c97a16a644061c9125467c
      size: 3053
    - path: external_evidence/external_source_end.json
      sha256: 8d02265d945771ec1bc05fc5292f9eb1b69176a72b26b58e6b636c4cc69407ae
      size: 12638
    - path: external_evidence/external_source_start.json
      sha256: d704108329d3340e3649d3f6e638e9a951920dd3011d2f0647804ee725dc1b63
      size: 10055
    - path: external_evidence/external_stderr.raw
      sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      size: 0
    - path: external_evidence/external_stdout.raw
      sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      size: 0
    - path: external_evidence/external_terminal.json
      sha256: 552670ed5a752ee3397d0837d3cdfa2ba55704547e6e299a1290885cd4dbd795
      size: 802
    - path: failure.json
      sha256: c80327f57b56f762fde9df3b215cf94c895e98de8c0d1e48157a31b44a65dc23
      size: 294
    - path: failure_manifest.json
      sha256: e9ef19b336e1eb9faac34b2f080f2c4956fd2316eb050287e769cbdb401aead4
      size: 3450
    - path: sentinel_contract.json
      sha256: 6eb9401c210b4d441859f45bcbdec93c9e60b41da4dbd647459a2aa66ab8f7b3
      size: 3072
    - path: source_start.json
      sha256: eea1d97869d2a40471bbbc0295792a953e8c66f6977c2a7de6b95455cdbb08b5
      size: 33890

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_sentinel_review.md
    sha256: 5bbf2996a7af96b282a1c699c74e85a04f7030b9bd5c2bcb33d4c0a99c33e617
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  repair_package:
    path: configs/phase6_v3_1_u_repair_cycle2_package.json
    sha256: 61460a45d4d47ba9247e68969a5d91e2d77aac722c9324014a414ed4126dbfa2
  package_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_package_delta_recheck_1.md
    sha256: f67ce9fa3f0b3f65a7ad34c736c06236f1b0c87674a0e943e8b749f1ca9387e5
  implementation_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_implementation_delta_recheck_2.md
    sha256: a0556466626efb2215cd9d9bcb5739668e7ab7b81b1420a4c1409937ce9cb7e9
  environment_authority:
    path: configs/phase6_v3_1_u_repair_cycle2_sentinel_environment_authority.json
    sha256: 936e4a403030d96ce4575e35fbefdff7d6eb29acaad564c137488a27aabec581
  one_use_dispatch:
    path: docs/handoffs/archive/T0_2026-08-13_v3_1_u_repair_cycle2_sentinel_dispatch_attempt_0001.json
    sha256: 6aaf17508333d8b965e13daf348ec368e8d2582fa6ea1c9f76ace62e61659112
    mode: 0444
    nlink: 1
    consumed_once_before_science: true
  external_snapshot_authority:
    path: runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json
    sha256: 8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488
    content_inventory_sha256: d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2
    restored_identity_inventory_sha256: a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
    file_count: 25
    directory_count: 5
    commit_association: inherited-only; snapshot contains no .git
  audit_archive:
    path: SchWO_third_audit_package_20260806.zip
    sha256: 715e27a45b15ec2ab78f92c77506de4317f5a26af79bb665de5a16d30557d162
  implementation:
    wls_sha256: 894bb2ebe6bd9637e3e449e7785241085de0f673ad93ebbf7865c4a5023b888f
    python_cycle2_sha256: 60fdc7c3f46ab21eafbe2b319f0c7b15b3ab64d6633d360f79ada078dcbd36b1
    hp_producer_sha256: 3292aea5074ae42b68cdb475bf86364b3aecc6ab08c37bf5ca51718f2834d730
  external_runtime:
    wolfram_kernel_path: /Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel
    wolfram_kernel_sha256: 70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c
    wolfram_version: 14.3.0 for Mac OS X ARM (64-bit) (July 8, 2025)
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  external_anchor_matrix:
    path: configs/phase6_v3_0_external_anchor_matrix.json
    sha256: 06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485
  thresholds:
    - id: frozen V3.0 threshold contract
      value: byte-identical
      units: mixed per-observable units as defined by source
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  convention_contract:
    path: references/notes/phase6_v3_absorption_scattering_conventions.md
    sha256: 82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a
  blocking_criteria:
    - exactly 23 ordered frozen odd Regge-Wheeler anchors
    - exactly one fresh MST call per ordinal with WorkingPrecision 90, PrecisionGoal 45 and AccuracyGoal 45
    - exactly 23 PASS outcomes and zero ERROR outcomes
    - child natural exit 0 with empty stderr, exact wait/reap and empty process group
    - no retry, drop, duplicate, reorder, selection or prior-artifact reuse
    - exact source/snapshot/kernel/protected/domain/threshold/convention identities
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

ADVANCE_DECISION: ESCALATE
CLAIM_STATUS: FAIL
GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31u_repair2_sentinel_dispatch_single_use_and_pre_science_consumption
      evidence_identity: dispatch 6aaf17508333d8b965e13daf348ec368e8d2582fa6ea1c9f76ace62e61659112 is bound by dispatch_consumption 6b5deeff2a22c009da07631b76faa5c300dbe0ba57282f429fc6130dc8b79dda with single_use=true and science_calls_before_consumption=0
    - item_id: v31u_repair2_sentinel_anchor_order_and_call_totality
      evidence_identity: request 54fe975cce7d6128b6ef21145fbe31600403370bc1c97a16a644061c9125467c, contract 6eb9401c210b4d441859f45bcbdec93c9e60b41da4dbd647459a2aa66ab8f7b3 and raw payload faa904b92e8248f79cc5dabcf6fd72fcbb85721d93a42884227e130c9d8dc0d9 contain the same 23 ordered unique keys, ordinals 0..22 and exactly one fresh call each
    - item_id: v31u_repair2_sentinel_method_identity
      evidence_identity: raw request/payload and WLS bind odd ReggeWheeler, BoundaryConditions=In, Method=MST, WorkingPrecision=90, PrecisionGoal=45, AccuracyGoal=45; WLS/kernel hashes are exact
    - item_id: v31u_repair2_sentinel_process_closure
      evidence_identity: PID/SID/PGID 58385, elapsed 9187271667 ns, timeout=false, signal=null, wait_calls=1, wait_error_count=0, reaped=true, process_group_empty=true; stdout and stderr are exact empty SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    - item_id: v31u_repair2_sentinel_source_and_loaded_module_closure
      evidence_identity: source start/end are equal after removing the documented end-only runtime_observed block; runtime loaded-source records equal the frozen exact ordered eight; live 25-file/five-directory snapshot rehashes the frozen content and restored-identity indexes
    - item_id: v31u_repair2_sentinel_manifest_and_immutability
      evidence_identity: all 17 files and two directories have exact immutable permissions/link counts; failure_manifest independently binds exactly the other 16 files and external_failure_manifest binds exactly the other 11 external files by path/SHA/size/mode/nlink
    - item_id: v31u_repair2_sentinel_frozen_inputs_and_nonreuse
      evidence_identity: 80 absolute source-start identities, seven protected radial sources, domain, threshold, convention, package, review, environment, snapshot and failed-predecessor bindings rehash exact; predecessor_science_reused=false, sentinel_science_reused=false, retry_permitted=false
  failed_items:
    - item_id: v31u_route_c_external_totality_and_provenance
      blocker_id: v31u_repair2_route_c_sentinel_totality_failure
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_repair2_official_science
      reason: sentinel is terminal FAILED; official dispatch/root do not exist and are forbidden
    - item_id: v31u_repair2_thresholds_and_certificates
      reason: no official candidate exists; all 16 thresholds and five certificates remain NOT_ASSESSED
    - item_id: v31u_v3_2
      reason: V3.2 is forbidden and was not started

findings:
  - finding_id: v31u_repair2_route_c_sentinel_totality_failure
    class: BLOCKING_CURRENT_GATE
    summary: The consumed one-shot sentinel completed the frozen 23-call traversal but only 14 anchors passed; nine exact frozen anchors returned native MST_FAILED outcomes, so the required all-23 PASS totality and child-exit-0 contract is false.
    blocker_id: v31u_repair2_route_c_sentinel_totality_failure
    violated_contract_item: The frozen sentinel gate requires each ordinal/key to have exactly one fresh call and exactly one PASS record with no ERROR, retry, drop, duplicate, reorder or selection; the child must naturally exit 0 before a one-use official dispatch may be authorized.
    exact_evidence: external_attempt_records.jsonl SHA-256 a111d6dcc7ff937409ce62df73b71e0f0f65881a8d7066d4062d1295fba76399 and raw child payload SHA-256 faa904b92e8248f79cc5dabcf6fd72fcbb85721d93a42884227e130c9d8dc0d9 independently reload as 23 ordered outcomes with 14 PASS and 9 ERROR. ERROR ordinals are 0,1,2,3,4,5,6,7,17, each code MST_FAILED and detail `ReggeWheelerRadial returned $Failed`. Receipt 46f06d8ce3665bac5dfb175d98cdbab6e6ea72a0a51d213d83907745e3477364 records returncode 70. Outer failure c80327f57b56f762fde9df3b215cf94c895e98de8c0d1e48157a31b44a65dc23 records terminal nonresumable scientific_pass=false.
    expected_value: 23 PASS, 0 ERROR, first_failure=null, overall_status=PASS, child returncode=0, and an exact validated 23-record Route-C result sufficient only for a separate official dispatch.
    observed_value: 14 PASS and 9 ERROR. Failures are kM=0.1 with ell=2,3,4,8; kM=0.5 with ell=2,3,4,10; and kM=2 with ell=18, all odd. First failure is ordinal 0 at kM=0.1, ell=2, odd. The child reports overall_status=ERROR and exits 70. No timeout, signal, package-load failure, source drift or process/resource failure is evidenced.
    bounded_repair: none exists inside the frozen gate. Repair cycle 2 has been consumed by this one-shot dispatch/launch, the sentinel is explicitly non-resumable/non-reusable, and no repair cycle 3 is permitted. Root T0 must adjudicate by freezing this branch, narrowing the claim/domain under a new authority, or designing a distinct new algorithm/gate; it may not reinterpret or repair this sentinel as PASS.
    allowed_files: []
    fresh_root_rule: this sentinel root and all 14 PASS/9 ERROR records remain immutable scientific failure evidence and are forbidden as a future PASS source; any T0-authorized distinct gate must use a new authority and fresh root and must not retry or reuse an anchor from this sentinel as acceptance evidence.
    required_tests_preflight: no current-gate repair or execution is authorized. Any distinct future gate requires its own frozen package, thresholds/domain/method/precision authority, zero-science preflight and formal T7 review before any new science.
    recheck_command: PYTHONDONTWRITEBYTECODE=1 python3.14 -c 'import json,pathlib,collections; p=pathlib.Path("runs/phase6/classic_scattering/v3_1_u_route_c_sentinel_repair2_v1_20260812T221323Z_py314/external_evidence/external_attempt_records.jsonl"); x=[json.loads(s) for s in p.read_text().splitlines()]; print(len(x),collections.Counter(r["status"] for r in x),[r["ordinal"] for r in x if r["status"]=="ERROR"],[r["error"] for r in x if r["status"]=="ERROR"]); assert len(x)==23 and collections.Counter(r["status"] for r in x)=={"PASS":14,"ERROR":9}'
    unblock_condition: no unblock condition exists within V3.1-U repair cycle 2. The current gate remains escalated until Root T0 records an explicit adjudication selecting branch freeze, claim/domain narrowing, or a distinct newly frozen algorithm/gate; none may promote this failed sentinel or authorize an official run from it.
  - finding_id: v31u_repair2_wrapper_parse_detail_separate
    class: CONTROL_PLANE_REPAIR
    summary: The wrapper additionally reports `external Route-C amplitude identity mismatch`, causing wrapper pass_count=0 and first_failure=null; direct raw reconstruction locates this at separately serialized PASS-amplitude precision checks, but it is downstream of and non-causal to the decisive nine native MST_FAILED outcomes.
  - finding_id: v31u_repair2_fourteen_pass_records_nonpromotable
    class: NONBLOCKING_LIMITATION
    summary: The 14 PASS records are internally reconstructible from incidence/reflection/transmission with the frozen S convention, but the frozen gate is all-or-nothing; no individual PASS or partial subset may be reused, promoted or treated as sentinel acceptance.
  - finding_id: v31u_repair2_snapshot_commit_association_inherited_only
    class: NONBLOCKING_LIMITATION
    summary: The restored snapshot has no .git; commit association remains inherited from the immutable historical ledger and exact 25-file byte equality rather than independently asserted by the snapshot.
  - finding_id: v31u_repair2_official_and_v3_2_forbidden
    class: FOLLOW_UP_DEBT
    summary: No official dispatch/run, V3.2, broader V3 claim or global GREEN may proceed from this failed sentinel.

delta_review:
  reviewed_failed_items:
    - v31u_route_c_external_totality_and_provenance
  passed_invariants_rechecked:
    - v31u_repair2_sentinel_dispatch_single_use_and_pre_science_consumption
    - v31u_repair2_sentinel_anchor_order_and_call_totality
    - v31u_repair2_sentinel_method_identity
    - v31u_repair2_sentinel_process_closure
    - v31u_repair2_sentinel_source_and_loaded_module_closure
    - v31u_repair2_sentinel_manifest_and_immutability
    - v31u_repair2_sentinel_frozen_inputs_and_nonreuse
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - complete frozen prompt, liveness protocol, verdict template, repair package/reviews, implementation authority, environment authority, one-use dispatch, snapshot authority and all 17 sentinel files read/reload
    - independent SHA-256/stat/mode/nlink enumeration of the terminal root and both directories
    - strict duplicate-free finite JSON reload; independent canonical-byte rebuild of 13 project JSON files and compact canonical rebuild of the 23-line attempt ledger; the Wolfram RawJSON payload is preserved and hash-bound as raw rather than falsely claimed to use project canonical formatting
    - independent failure_manifest and external_failure_manifest artifact-set/path/SHA/size/mode/nlink reconstruction
    - independent request/contract/dispatch/payload/attempt comparison for exact 23 keys, ordinals 0..22, uniqueness, order, one call each, method and terminal status
    - 100-dps algebraic reconstruction of reflection_ratio=Reflection/Incidence, S=(-1)^(ell+1) reflection_ratio, T_horizon=Transmission/Incidence and Gamma_flux for every raw PASS outcome
    - independent source-start/end comparison, live 25-file/five-directory snapshot inventory rebuild, exact eight loaded-source rehash and 80 absolute source-start identity rehashes
    - read-only PID/PGID/process, official-dispatch/root and V3.2 absence checks; no WolframKernel, solver, sentinel retry or new science was executed
  results:
    - exact root inventory is 17 regular 0444/nlink1 files and two 0555 directories with zero symlink; failure manifest binds the other 16 files and external failure manifest binds the other 11 external files exactly
    - request, dispatch, sentinel contract, attempt ledger and raw child payload agree on 23 ordered unique odd anchors and 23 total fresh calls; no duplicate, reorder, omission or retry exists
    - method is exact MST/WorkingPrecision 90/PrecisionGoal 45/AccuracyGoal 45/ReggeWheeler/In; WLS, Python runner, WolframKernel and snapshot identities are exact
    - status count is 14 PASS / 9 ERROR, error ordinals 0,1,2,3,4,5,6,7,17; every error is exact MST_FAILED / `ReggeWheelerRadial returned $Failed`
    - the 14 PASS records independently reproduce reflection_ratio to maximum residual 5.18517343977e-22, S convention exactly, T_horizon to 1.98533206311e-22 and flux relations to 1.76380645608e-21; these checks do not cure all-23 totality
    - wrapper parse detail is independently distinct: the raw nine ERROR outcomes already force child overall ERROR/exit 70; the wrapper amplitude-identity exception does not replace or explain them
    - receipt is PID/SID/PGID 58385, returncode 70, signal null, timeout false, one exact wait, reaped true, process group empty, elapsed 9187271667 ns; stdout/stderr are both exact empty files
    - external source start/end static records are equal; end adds only runtime_observed. The eight loaded sources are exact. Snapshot inventory independently rebuilds 25 files, five directories, content index d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2 and restored identity index a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
    - all 80 absolute source-start records, seven protected sources, domain, threshold, convention, package/review/environment/dispatch/snapshot/audit identities rehash exact at start/end
    - sentinel is terminal FAILED, non-resumable and scientific_pass=false; no live writer/process, official dispatch/root or V3.2 process exists

non_claims:
  - the nine MST failures do not establish that the underlying physical quantities fail; they establish that the frozen external Route-C method did not produce the mandatory total evidence
  - the 14 raw PASS outcomes are not a partial sentinel acceptance and are not reusable for an official candidate
  - the wrapper parse detail is not asserted as the cause of the nine native MST failures
  - no threshold, domain, convention, method or precision is changed or relaxed
  - no official V3.1-U dispatch/run, retry, repair cycle 3, V3.2, broader V3 claim or global GREEN is authorized

repair_cycle:
  completed_bounded_repairs: 2
  completed_bounded_scientific_repairs: 2
  current_bounded_scientific_repair: none
  repair_cycle2_consumed: true
  repair_cycles_exhausted: true
  same_substantive_blocker_remaining: false
  t0_adjudication_required: true
```

## Independent scientific conclusion

The one-shot Route-C sentinel is complete as failure evidence but does not
satisfy its scientific acceptance condition. All 23 frozen calls were made in
the exact order and under the exact external method, yet nine calls returned
native `MST_FAILED` outcomes. The failures are not attributable to timeout,
signal, process loss, missing package, source drift or incomplete traversal.
They are therefore a method/totality failure against this frozen gate, without
being promoted to a claim that the underlying physics itself is false.

The wrapper's additional amplitude-identity parse error is separately
recorded and does not obscure the decisive raw evidence. Even if that parser
detail were absent, 14 PASS plus 9 ERROR cannot satisfy the exact all-23 PASS
criterion.

## Downstream boundary

Repair cycle 2 was consumed by the one-use dispatch and launch. This sentinel
is immutable, non-resumable and non-reusable. No retry, repair cycle 3,
official dispatch/root, threshold/domain/method/precision change, V3.2 or
global GREEN is authorized. Root T0 must adjudicate whether to freeze the
branch, narrow the claim/domain under a new authority, or design a distinct
new algorithm/gate.
