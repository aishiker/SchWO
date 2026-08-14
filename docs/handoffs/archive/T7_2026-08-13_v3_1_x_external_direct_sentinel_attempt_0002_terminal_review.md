# T7 terminal review — V3.1-X attempt-0002 external-direct sentinel

Date: 2026-08-13

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-X SENTINEL CHANGES REQUIRED
```

This is the formal archive-only terminal review of the single authorized
attempt-0002 launch.  The launch, dispatch and immutable root are consumed and
non-reusable.  The review authorizes no implementation, retry, dispatch,
Wolfram execution, solver call, official run, V3.2 or global GREEN.

## Verdict record

```yaml
review_id: t7_v3_1_x_external_direct_sentinel_attempt_0002_terminal_review_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
substage: immutable sentinel review
attempt: post_repair_1_sentinel_terminal_review
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed

reviewed_candidate:
  root: runs/phase6/classic_scattering/v3_1_x_external_direct_sentinel_v1_20260813T085010Z_py314
  root_state:
    mode: "0555"
    directories_inclusive: 9
    directories_all_mode: "0555"
    regular_files: 77
    files_all_mode: "0444"
    files_all_nlink: 1
    total_file_bytes: 720339
    symlinks: 0
    special_files: 0
    relative_tab_ledger_sha256: 1aefc643d6bc8b18218a3d26817a3b5e03f66c2b402c4338b607954cb1a36d08
    active_writer_or_related_process: false
    terminal: true
    overall_state: FAIL
    resumable: false
    retry_permitted: false
    scientific_pass: false
  identities:
    - path: dispatch_consumption.json
      sha256: ae98b5bca3b1ea8604ab93ecb8ac6c9e632b92c8651d0557803ecde71d60c88a
      size: 3124
    - path: failure.json
      sha256: c002664933d58913b5793ffc1100a5958cb1dfdd12d0c9b3664ffa9ddfb2f541
      size: 347
    - path: manifest.json
      sha256: 6e0d2349d998f76ee8d149e4551bf27222c5d93bf4ec9fb7b790adbc9f506109
      size: 15963
    - path: source_start.json
      sha256: 27f704df917dc4702a8e56ded7e64fb1750385a2c6f56504560951ef1b95ea47
    - path: static_contract.json
      sha256: 411d3db83a6490e72a574df49690dc032b3763d21b53fe42bde8debec4c1f227
    - path: writer_exclusion.json
      sha256: 1a2263ef4a5dcfc5748aed8cd896f1fc24e35023ae4807df59629b00f62f6f11
    - path: external_evidence/outcomes.jsonl
      sha256: 9004f01e49923e5fd9449b3c4342aa41e52d3ca2d169bc36e3e111f18693b193
    - path: external_evidence/records.jsonl
      sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      size: 0
    - path: external_evidence/raw_records.jsonl
      sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      size: 0
    - path: external_evidence/node_evidence/call_0000.request.json
      sha256: 8d672144126449c9b3dcbe9fc468ddb46fc6eb29655319d2350e55aa745e85c6
      size: 3325
    - path: external_evidence/node_evidence/call_0000.raw.prelaunch.json
      sha256: e3917ad293c692be27c353ccbf15c23d4f7486b7dd7b974bdf753ce9daf0c4d5
      size: 2462
    - path: external_evidence/node_evidence/call_0000.raw.running.json
      sha256: 9cb37cb0e254e12aaa9f99a67414a839d84903630093a7ed1ca63fbaf0e224b0
      size: 782
    - path: external_evidence/node_evidence/call_0000.raw.receipt.json
      sha256: 4e912324b5e3fdad5bf003292e744f34e7512ace47e5de72378d401ed61e6410
      size: 3248
    - path: external_evidence/node_evidence/call_0000.raw.terminal.json
      sha256: 60623c51838fd135ed945b72f3d111a2bacbead4f0c05340b40b38cb04906920
      size: 3661
    - path: external_evidence/node_evidence/call_0000.raw.stdout.raw
      sha256: df94f3103906db90376690ce3114f5b184c40bb69689273739b74d174fc0e43b
      size: 29
    - path: external_evidence/node_evidence/call_0000.raw.stderr.raw
      sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      size: 0
    - path: external_evidence/node_evidence/call_0000.error.json
      sha256: 3522ae9e71b52209c0ecfbc8a227b9066c6f4b38162c80c96656bd11aec1d7b5
      size: 542

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_x_external_direct_route_science_review.md
    sha256: 339d5d9609e37f263ca3b3c615e5048f4059c80accc03183e02a74df6ffebd7f
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  package:
    path: configs/phase6_v3_1_x_external_direct_route_package.json
    sha256: 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752
  initial_sentinel_terminal_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_sentinel_terminal_review.md
    sha256: cf4ba0a25527f0298bf3f18ba03a19b4a849a592db30bc610c2bb0749015d772
  accepted_repair_1_implementation:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_implementation_delta_review.md
    sha256: 789f13fe1236a4226606bd61e1c7930d6b9de80b7bcc10df27c95995f7a6c6ce
  accepted_attempt_0002_namespace:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_dispatch_namespace_delta_review.md
    sha256: 5a2a3a0f531f777ac0c8299078a645cc0a466158078882dd4e3ad2f38631e498
  one_launch_reauthorization:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_attempt_0002_preconsumption_launch_incident_review.md
    sha256: 7caa3f99e8cc2ff3eadd0b54754cc336aa5ab7fa2748acfdb1eae194cf4f3614
  one_use_dispatch:
    path: docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0002.json
    sha256: 6be8d88226179ed25d4e50dee06cc17a6f38e61e67617edf9751a88e2cea5112
    one_use_id: 92c294a70e73286d998cc47279ec0b1055293c3703441f50b74c8423efba8619
    consumed_exactly_once_before_science: true
    launch_authorization_exhausted: true
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  external_anchor_matrix:
    path: configs/phase6_v3_0_external_anchor_matrix.json
    sha256: 06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485
  thresholds:
    - id: frozen V3.0 threshold contract
      value: byte-identical; 16 thresholds unchanged and not evaluated
      units: mixed per-observable units defined by source
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  convention_contract:
    path: references/notes/phase6_v3_absorption_scattering_conventions.md
    sha256: 82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a
  external_snapshot:
    path: runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json
    sha256: 8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488
    source_files: 25
    source_directories: 5
    content_inventory_sha256: d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2
    identity_inventory_sha256: a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
  runtime:
    wolfram_kernel: /Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel
    wolfram_kernel_sha256: 70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c
  implementation_hashes:
    scripts/phase6_v3_1_x_bhpt_direct.wls: 24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6
    scripts/phase6_v3_1_x_external_direct.py: 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768
    src/schwgw/validation/phase6_v3_external_direct.py: 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4
    src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py: 81a33a4157d6e07b03621bff069c9383914464c16ce4314a9f7a556c7e1cd088
    tests/unit/test_phase6_v3_external_direct.py: 056c7273edbdb612d3fc99c4b493f2fe4c96dc15b8ae7aa3a872587f33f3aaba
    tests/regression/test_phase6_v3_external_direct_publication.py: 24d26a8a9c2e0ad573b97f76b39db7743f2d6639cd57978be93f0c310062f858
  protected_identities:
    - {path: src/schwgw/numerics/radial_solver.py, expected_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_start_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_end_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9}
    - {path: src/schwgw/numerics/conditioned_radial.py, expected_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_start_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_end_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2}
    - {path: src/schwgw/numerics/scaled_tortoise_radial.py, expected_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_start_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_end_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df}
    - {path: src/schwgw/numerics/adaptive_jost_radial.py, expected_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_start_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_end_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896}
    - {path: src/schwgw/numerics/matching.py, expected_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_start_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_end_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340}
    - {path: src/schwgw/numerics/physical_boundary_radial.py, expected_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_start_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_end_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f}
    - {path: src/schwgw/numerics/boundary_conditions.py, expected_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_start_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_end_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22}
  blocking_criteria:
    - exact 35 ordered fresh sentinel calls, 70 independent In/Up solutions and 105 overlap decompositions
    - all 23 selected P1 keys plus P0/I0/I2/O2/O4/O8 for ordinals 3 and 22
    - every node and every mandatory sentinel budget PASS
    - no MST, internal solver, retry, fallback, selection, predecessor reuse or sentinel reuse
    - exact source start/end, child lifecycle, package, domain, threshold, convention and protected identities

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-X SENTINEL CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31x-sentinel-attempt0002-authority-and-consumption
      evidence_identity: dispatch 6be8d88226179ed25d4e50dee06cc17a6f38e61e67617edf9751a88e2cea5112 is bound by consumption ae98b5bca3b1ea8604ab93ecb8ac6c9e632b92c8651d0557803ecde71d60c88a; the one_use_id is consumed exactly once and science_calls_before_consumption=0
    - item_id: v31x-sentinel-attempt0002-terminal-manifest-and-immutability
      evidence_identity: manifest 6e0d2349d998f76ee8d149e4551bf27222c5d93bf4ec9fb7b790adbc9f506109 independently rebuilds exactly over the other 76 files; all 77 files are 0444/nlink1, all nine directories are 0555, and no link/special/writer/process exists
    - item_id: v31x-sentinel-attempt0002-planned-graph-totality
      evidence_identity: outcomes 9004f01e49923e5fd9449b3c4342aa41e52d3ca2d169bc36e3e111f18693b193 has ordinals 0..34, 23 unique P1 keys and the six extra node IDs for each of key ordinals 3 and 22
    - item_id: v31x-sentinel-attempt0002-child-lifecycle-closure
      evidence_identity: receipt 4e912324b5e3fdad5bf003292e744f34e7512ace47e5de72378d401ed61e6410 and terminal 60623c51838fd135ed945b72f3d111a2bacbead4f0c05340b40b38cb04906920 bind PID/SID/PGID 96802, natural rc69, no signal/timeout/wait error, exact wait, reaped=true and process_group_empty=true
    - item_id: v31x-sentinel-attempt0002-source-path-hash-stat-admission
      evidence_identity: all eight requested loaded-source records independently match the materialized overlay in context order by path/SHA-256/size/mode/nlink; the WLS passed overlay identity, context cardinality/schema, Paclet/Needs closure, every FindFile path and the exact NumericalIntegration path before its structural ledger comparison
    - item_id: v31x-sentinel-attempt0002-frozen-authority-preservation
      evidence_identity: package/domain/anchor/threshold/convention/external-snapshot, all six implementation identities and all seven protected radial identities rehash exact; predecessor_science_reused=false and sentinel_science_reused=false
    - item_id: v31x-sentinel-attempt0002-no-retry-or-downstream
      evidence_identity: only attempts 0001 and 0002 roots exist, attempt0002 contains the sole consumption of one_use_id 92c294a7...8619, and no later launch, official dispatch/root, V3.2 root or related process exists
  failed_items:
    - item_id: v31x-sentinel-loaded-source-ledger-structural-comparison
      blocker_id: v31x-sentinel-loaded-source-start-association-order-mismatch
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31x-sentinel-numerical-science
      reason: the WLS exited before the ReggeWheelerRadial NumericalIntegration call; zero boundary solutions, overlaps and scientific records exist
    - item_id: v31x-sentinel-resource-and-numerical-budgets
      reason: no successful node exists from which to evaluate resource projection or numerical admission budgets
    - item_id: v31x-official-science
      reason: the sentinel gate failed; no official dispatch/root is authorized or present
    - item_id: v31x-thresholds-and-certificates
      reason: the 16 thresholds and five certificates were not evaluated or generated
    - item_id: v3-2
      reason: V3.2 is forbidden and was not started

findings:
  - finding_id: v31x-sentinel-loaded-source-start-association-order-mismatch
    class: BLOCKING_CURRENT_GATE
    summary: The controller's sorted-key canonical JSON and the WLS's literal Association constructor encode the same eight exact source records in different per-record key orders, but the WLS compares the two Association lists with order-sensitive structural SameQ and exits 69 before the solver.
    blocker_id: v31x-sentinel-loaded-source-start-association-order-mismatch
    violated_contract_item: Substage B requires an exact source/runtime receipt followed by 35 fresh direct NumericalIntegration calls, 70 In/Up solutions, 105 overlap decompositions and all mandatory sentinel gates PASS; source identity comparison must accept the exact bound source values while failing closed on any actual source drift.
    exact_evidence: >-
      Request 8d672144126449c9b3dcbe9fc468ddb46fc6eb29655319d2350e55aa745e85c6 stores every source item in canonical sorted-key order
      [context,mode,nlink,path,sha256,size]. WLS 24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6 lines 86-113 reconstructs every item in literal order
      [context,path,sha256,size,mode,nlink], lines 115-129 successfully load the package and all contexts, line 130 builds loadedStart, line 131 retains imported expectedLoaded, and line 132 applies `loadedStart =!= expectedLoaded` and emits the exact stdout `loaded source start mismatch\n` (SHA df94f3103906db90376690ce3114f5b184c40bb69689273739b74d174fc0e43b).
      Independent reload proves all eight semantic value maps match the materialized overlay exactly; receipt 4e912324b5e3fdad5bf003292e744f34e7512ace47e5de72378d401ed61e6410 records natural rc69 and complete closure. The ReggeWheelerRadial call is only at WLS line 143 and was not reached. Records and raw_records are both empty SHA e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.
    expected_value: >-
      The imported expected ledger and independently rebuilt actual ledger compare by one explicit canonical six-field semantic projection in the frozen context/list order; all eight exact path/SHA-256/size/mode/nlink identities pass, the solver is reached, and the complete 35/70/105 sentinel may be evaluated without relaxing any source guard.
    observed_value: >-
      All eight source values and paths are exact, but the two Association representations have key orders [context,mode,nlink,path,sha256,size] versus [context,path,sha256,size,mode,nlink]. Structural `=!=` rejects the first node before ReggeWheelerRadial; outcomes are exactly one ERROR plus 34 NOT_STARTED_AFTER_PRIOR_FAILURE, with zero scientific successes, zero boundary solutions and zero overlaps.
    bounded_repair: >-
      In the final bounded repair cycle 2, define one literal six-field source-record normalizer/projection in the WLS and apply it independently to both imported expected records and freshly discovered/rehash-built actual records before exact list comparison. Preserve context/list order and every field; do not sort the record list, use a set, drop a field or accept fallback paths. Add a literal source-load-handshake mode that performs the same request validation, overlay validation, Paclet/context/FindFile closure, exact normalized start/end ledger comparison and durable child lifecycle but exits before ReggeWheelerRadial with external_api_call_count=0 and solver_call_count=0. Bind that mode through a fixed, non-circular, one-use T0 authority and a fresh absent micro-sentinel root. Update only the producer/CLI authority necessary to expose that fixed mode and the two test files; keep the core direct physics module, graph, source snapshot, method, precision, domain, thresholds, conventions and protected radial bytes frozen.
    allowed_files:
      - scripts/phase6_v3_1_x_bhpt_direct.wls
      - src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      - scripts/phase6_v3_1_x_external_direct.py
      - tests/unit/test_phase6_v3_external_direct.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
    recheck_command: >-
      /usr/bin/env -i PYTHONDONTWRITEBYTECODE=1
      PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src
      /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14
      -m pytest -q tests/unit/test_phase6_v3_external_direct.py
      tests/regression/test_phase6_v3_external_direct_publication.py
    unblock_condition: >-
      A formal repair-cycle-2 delta review must independently prove exact five-path-or-smaller scope, one canonical semantic ledger projection used on both sides, rejection of missing/extra/duplicate/reordered-context/wrong-key/wrong-path/hash/size/mode/nlink/alias records, unchanged solve-mode behavior and all frozen passed/protected identities. Root T0 must then separately freeze and consume exactly one source-load micro-sentinel dispatch/root. That real Wolfram handshake must terminal-PASS with exactly one call for V3A-MODE-BHPT-RW-001/P1, eight exact ordered source records at both start and end, one WLS launch, rc0/empty stderr/exact wait-reap-PG closure, and zero ReggeWheelerRadial, boundary-solution, overlap, solver or scientific calls. A formal T7 read-only review of that immutable micro root must ADVANCE before T0 may even consider a different one-use dispatch and fresh 35-call sentinel. Any repair-2 delta or micro failure exhausts the gate and requires ESCALATE; attempt_0002 and its root can never be reused.
  - finding_id: v31x-sentinel-loaded-source-values-not-drifted
    class: NONBLOCKING_LIMITATION
    summary: The failure wording could suggest source drift, but direct reload proves no path/hash/size/mode/nlink or loaded-context drift; the review therefore makes no adverse claim about the external source bytes.
  - finding_id: v31x-sentinel-real-wolfram-ledger-boundary-test-gap
    class: FOLLOW_UP_DEBT
    summary: The accepted regression fake sets loaded_source_start/end directly to request.loaded_source_records and therefore self-confirms the controller representation; final repair 2 must cover the real RawJSON-to-Wolfram Association boundary before any new 35-call attempt.
  - finding_id: v31x-sentinel-no-scientific-result
    class: NONBLOCKING_LIMITATION
    summary: This is an implementation/provenance-admission failure before the external numerical call, not an external-science result, resource failure, threshold failure or evidence that any numerical node would pass after repair.
  - finding_id: v31x-official-v3-2-global-green-forbidden
    class: FOLLOW_UP_DEBT
    summary: This YELLOW authorizes no implementation by itself, no reuse/retry, no official dispatch/root, no V3.2, and no threshold/domain/method/precision/convention change or global GREEN.

classification:
  class_a_blocking_current_gate: true
  class_c_control_plane_repair: false
  external_scientific_result: false
  hold: false
  escalate: false
  rationale: Evidence is complete and immutable, the causal branch is deterministic and precedes the solver, and one final bounded repair cycle remains; the executable source-provenance comparator is part of the current scientific gate rather than metadata-only control plane.

delta_review:
  reviewed_failed_items:
    - v31x-sentinel-wls-scriptcommandline-interface
  passed_invariants_rechecked:
    - v31x-repair1-exact-command-vector-and-argv-handshake
    - v31x-attempt0002-dispatch-namespace-and-one-use-authority
    - v31x-sentinel-planned-graph-totality
    - v31x-sentinel-child-lifecycle-closure
    - v31x-package-domain-threshold-convention-preservation
    - v31x-seven-protected-radial-identities
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - SHA-256/stat/nlink recheck of the review contract, liveness/template, package, predecessor reviews, incident authority, dispatch, domain, anchor matrix, thresholds, convention, snapshot, six implementation files and seven protected sources
    - independent CPython 3.14 recursive inventory and manifest rebuild over every terminal-root byte, excluding only manifest.json from the self-excluding artifact map
    - independent CPython 3.14 reload of every JSON and every non-empty JSONL line, all 35 outcomes and both empty scientific streams
    - independent rehash/stat comparison of all eight request source records against the materialized call_0000 overlay
    - static line/dataflow reconstruction of Python canonical request serialization, WLS sourceRecords/load/compare order and the later ReggeWheelerRadial call
    - read-only one_use_id, dispatch/root, official/V3.2 and process inventory checks
  results:
    - frozen authorities and protected identities PASS at review start/end
    - root inventory PASS: 77 files, nine directories inclusive, 720339 bytes, all 0444/0555 and nlink1, zero symlink/special
    - manifest rebuild PASS: exact 76-artifact object and exact canonical indent-2 newline bytes
    - JSON/JSONL reload PASS: 46 JSON files, three JSONL files, 35 non-empty JSONL records, zero parse failures
    - one-use dispatch binding and exactly-one pre-science consumption PASS
    - graph totality PASS: 35 ordered outcomes, 23 P1 plus two each of P0/I0/I2/O2/O4/O8
    - child closure PASS: PID/SID/PGID 96802, rc69, no signal/timeout/wait error, reaped and process group empty
    - source semantic identities PASS: eight of eight context/path/SHA/size/mode/nlink records equal the overlay
    - sentinel acceptance FAIL: one ERROR, 34 NOT_STARTED_AFTER_PRIOR_FAILURE, zero raw/scientific records, zero solutions and zero overlaps
    - exact causal classification PASS: order-sensitive structural Association comparison at WLS line 132 before solver line 143
    - no retry, later launch, official root/dispatch, V3.2 or related live process

non_claims:
  - no V3.1-X sentinel scientific PASS
  - no claim that any missing numerical node would pass after the ledger repair
  - no scientific reuse, retry or resume of attempt_0001 or attempt_0002
  - no official V3.1-X dispatch/root or evidence
  - no threshold, domain, convention, precision, method, graph, source-snapshot or protected-radial change
  - no finite-radius observer, Li-figure, full-domain or broader independent-certification claim
  - no V3.2 and no global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 0
  attempt_0002_one_use_launch_consumed: true
  repair_cycle_2_consumed_by_this_review: false
  next_permitted_cycle: final bounded repair 2 followed by delta review 2 and the separately gated one-call source-load micro-sentinel
  remaining_bounded_repairs: 1
  cycle_3_permitted: false
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Exact causal reconstruction

The request's eight records have exact semantic values.  For clarity, the
independently reloaded values are:

| ordinal | context | path | SHA-256 | size | mode | nlink |
|---:|---|---|---|---:|---:|---:|
| 0 | `ReggeWheeler\`` | `Kernel/ReggeWheeler.m` | `24fb778a9e09d2a933f133d571e948f8efcb6442e766f40963bdd248718506da` | 405 | 292 | 1 |
| 1 | `ReggeWheeler\`MST\`MST\`` | `Kernel/MST/MST.m` | `868b8e4b0bdbf1a6b56033168f00a4251e42122600235d0370ea0926376814b7` | 35438 | 292 | 1 |
| 2 | `ReggeWheeler\`MST\`RenormalizedAngularMomentum\`` | `Kernel/MST/RenormalizedAngularMomentum.m` | `402ec64abb706c984cc6db44e91343dac5d5b5cf350d429ad6c13ab784a85528` | 12298 | 292 | 1 |
| 3 | `ReggeWheeler\`NumericalIntegration\`` | `Kernel/NumericalIntegration.m` | `a8601cd1b377bf4741035a03bec98590ebffbec0004a63af498a260f1d05c5fc` | 9478 | 292 | 1 |
| 4 | `ReggeWheeler\`Hyperboloidal\`` | `Kernel/Hyperboloidal.wl` | `0e7aebc51595e538b42618c2b37e36f1e518e89cb3b8235e720e2dc96fe05887` | 25998 | 292 | 1 |
| 5 | `ReggeWheeler\`ReggeWheelerRadial\`` | `Kernel/ReggeWheelerRadial.m` | `2af593f527b39d2b7ece71f99e50ecb6b84399342251985004d6d2e2c3fed41f` | 19584 | 292 | 1 |
| 6 | `ReggeWheeler\`ReggeWheelerSource\`` | `Kernel/ReggeWheelerSource.m` | `3a1794cc09293067c804e60ea916bc59d7118468100d2a7c6e6bd73ea8532406` | 3288 | 292 | 1 |
| 7 | `ReggeWheeler\`ReggeWheelerMode\`` | `Kernel/ReggeWheelerMode.m` | `f8fa3882aecc927b885024cb6ec471dd0b7644a929c35eed5903beb0c55322c7` | 8940 | 292 | 1 |

The request binds overlay content index
`abc17a59659b21b984c080f042faaefce71a1216328e6a9cc0ee5d02b0321c1d`,
identity index
`357d8b57be7c13869ac29c082dd14046f1e71b8aea29a579e66a5bbd03d780bd`
and the modified `rin10_m1` NumericalIntegration source shown above.  Those
identities pass.  Because the exact stdout is emitted only after every earlier
overlay, context and `FindFile` guard, and every semantic value independently
rehashes equal, the remaining deterministic mismatch is the Association
representation order: canonical JSON imported
`context,mode,nlink,path,sha256,size`, while `sourceRecords[]` constructs
`context,path,sha256,size,mode,nlink`.  The direct numerical call follows
eleven source lines later and is unreachable on this branch.

## Bounded next action

Root T0 may freeze one final repair-cycle-2 package limited to the five
allowed paths and binary unblock condition above.  The package must predeclare
the exact future repair-2 review authority, the exact one-use micro-sentinel
dispatch/root and a separate later 35-call sentinel namespace; no path or hash
may be selected through environment, arbitrary argv, fallback or globbing.

After an implementation delta review, the first executable check must be one
real external source-load micro-sentinel for exact key
`V3A-MODE-BHPT-RW-001`, node `P1`.  It must load and independently rehash the
eight sources at both boundaries but must stop before `ReggeWheelerRadial`.
Only a formal T7 GREEN on that immutable micro root can permit T0 to consider
a fresh, different 35-call sentinel.  Failure of the repair-2 delta or micro
sentinel, or recurrence of this substantive source-ledger blocker after
delta-review 2, requires `ESCALATE / T0 ADJUDICATION REQUIRED`; no cycle 3
exists.

The consumed attempt-0002 dispatch and root are permanent failure evidence.
They may not be retried, resumed, repaired, replayed, promoted or used as
scientific input.
