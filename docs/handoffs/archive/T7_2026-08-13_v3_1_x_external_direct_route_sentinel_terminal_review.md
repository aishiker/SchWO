# T7 terminal review — V3.1-X one-use external-direct sentinel

Date: 2026-08-13

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-X SENTINEL CHANGES REQUIRED
```

## Verdict record

```yaml
review_id: t7_v3_1_x_external_direct_sentinel_terminal_review_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
attempt: initial_sentinel_terminal_review
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: runs/phase6/classic_scattering/v3_1_x_external_direct_sentinel_v1_20260813T055002Z_py314
  root_state:
    mode: 0555
    directories: 9
    directories_all_mode: 0555
    regular_files: 77
    files_all_mode: 0444
    files_all_nlink: 1
    total_file_bytes: 720336
    symlinks: 0
    special_files: 0
    active_writer_or_related_process: false
    terminal: true
    overall_state: FAIL
    resumable: false
    retry_permitted: false
    scientific_pass: false
  identities:
    - path: failure.json
      sha256: c002664933d58913b5793ffc1100a5958cb1dfdd12d0c9b3664ffa9ddfb2f541
      size: 347
    - path: manifest.json
      sha256: d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772
      size: 15963
    - path: dispatch_consumption.json
      sha256: 50b6f08e17167054a717fc14cc04fb549b927a5a803a5cb6ba06db7a5c62f160
      size: 3099
    - path: source_start.json
      sha256: 020d1ab1027e678dcbbefe1d4ce02b8d371e851e40d969274f9befdc63be00a0
      size: 23076
    - path: static_contract.json
      sha256: 411d3db83a6490e72a574df49690dc032b3763d21b53fe42bde8debec4c1f227
      size: 4109
    - path: writer_exclusion.json
      sha256: a05f1739857e07f3dc4340a4eaa4c902174c44e90b8072daf939c1a6aebc0e03
      size: 501
    - path: external_evidence/outcomes.jsonl
      sha256: f85d11934d180cbf3e65ffe8324857d15dce0cccf504db07835ee64236357230
    - path: external_evidence/records.jsonl
      sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      size: 0
    - path: external_evidence/raw_records.jsonl
      sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      size: 0
    - path: external_evidence/node_evidence/call_0000.raw.prelaunch.json
      sha256: 3a2e406343d55d0db30c6d70b023953f7ad606e4c23baf692981d8ab5cc5d517
    - path: external_evidence/node_evidence/call_0000.raw.receipt.json
      sha256: 8c7b6961570c4aea13c613b26c8a1451b41110f0825c87d709dfec7b677c064e
    - path: external_evidence/node_evidence/call_0000.raw.terminal.json
      sha256: cae9169380ef265c117e25ce49867dbf8cf65758e51ffbc867b13b441e29ea61
    - path: external_evidence/node_evidence/call_0000.raw.stdout.raw
      sha256: 420e61b4fb899771ee2e4b6807d9681fe496f7a7d850aafd7206836f9ff84c0d
      size: 52
    - path: external_evidence/node_evidence/call_0000.error.json
      sha256: 3522ae9e71b52209c0ecfbc8a227b9066c6f4b38162c80c96656bd11aec1d7b5

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
  implementation_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_authority_bridge_delta_review.md
    sha256: f807a6d05eeb577890f544069db1b408120cbe4a1eb9e676a89ac04e06aa9f9c
    verdict: ADVANCE / NOT_ASSESSED / ACCEPT GREEN / V3.1-X AUTHORITY BRIDGE READY FOR ONE-USE SENTINEL DISPATCH
  one_use_dispatch:
    path: docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0001.json
    sha256: 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9
    one_use_id: 069160536d5f248f40cada152e8c4f0695e69f93e953eb99781cb3471b980e6e
    consumed_exactly_once_before_science: true
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
    scripts/phase6_v3_1_x_bhpt_direct.wls: 652ced5b32983e79df6c36a5e697c5263aa0570f4cf4b20d58a2b3c20e6e1907
    scripts/phase6_v3_1_x_external_direct.py: 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768
    src/schwgw/validation/phase6_v3_external_direct.py: 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4
    src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py: e8709bd42d7a2ae037bde40f097568dae62e6f6b0c2a7868fcfee23859231c2b
    tests/unit/test_phase6_v3_external_direct.py: 1e0c96360c652ec6d1c82aa7daf8631df247d8ce43f1ffe2b4ca295227d22604
    tests/regression/test_phase6_v3_external_direct_publication.py: 061ebeeeb276f5cab2a3e3b9acae2a2ac87b68a069f059563113739266bc8623
  blocking_criteria:
    - exactly 35 ordered fresh sentinel calls: 23 P1 calls plus P0/I0/I2/O2/O4/O8 for key ordinals 3 and 22
    - exactly 70 independent boundary solutions and 105 overlap decompositions
    - every node PASS with finite precision witnesses and all sentinel budgets PASS
    - no MST, internal solver, retry, fallback, selection, predecessor reuse or sentinel reuse
    - exact child lifecycle, source closure, package, domain, threshold and convention identities
  protected_identities:
    - {path: src/schwgw/numerics/radial_solver.py, expected_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_start_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_end_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9}
    - {path: src/schwgw/numerics/conditioned_radial.py, expected_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_start_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_end_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2}
    - {path: src/schwgw/numerics/scaled_tortoise_radial.py, expected_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_start_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_end_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df}
    - {path: src/schwgw/numerics/adaptive_jost_radial.py, expected_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_start_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_end_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896}
    - {path: src/schwgw/numerics/matching.py, expected_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_start_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_end_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340}
    - {path: src/schwgw/numerics/physical_boundary_radial.py, expected_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_start_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_end_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f}
    - {path: src/schwgw/numerics/boundary_conditions.py, expected_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_start_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_end_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22}

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-X SENTINEL CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31x-sentinel-authority-and-one-use-consumption
      evidence_identity: dispatch 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9 is bound by consumption 50b6f08e17167054a717fc14cc04fb549b927a5a803a5cb6ba06db7a5c62f160; the one_use_id appears in exactly one run-root consumption and science_calls_before_consumption=0
    - item_id: v31x-sentinel-terminal-manifest-and-immutability
      evidence_identity: manifest d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772 independently binds exactly the other 76 files by path/SHA/size/mode/nlink; all 77 files are 0444/nlink1 and all nine directories are 0555
    - item_id: v31x-sentinel-planned-graph-totality
      evidence_identity: outcomes f85d11934d180cbf3e65ffe8324857d15dce0cccf504db07835ee64236357230 contains 35 ordered call ordinals, 23 unique P1 keys followed by the six remaining nodes for ordinals 3 and 22
    - item_id: v31x-sentinel-child-lifecycle-closure
      evidence_identity: receipt 8c7b6961570c4aea13c613b26c8a1451b41110f0825c87d709dfec7b677c064e and terminal cae9169380ef265c117e25ce49867dbf8cf65758e51ffbc867b13b441e29ea61 record PID/SID/PGID 86741, natural rc64, no signal/timeout/wait error, wait called, reaped=true and process_group_empty=true
    - item_id: v31x-sentinel-source-protected-and-runtime-identities
      evidence_identity: source_start 020d1ab1027e678dcbbefe1d4ce02b8d371e851e40d969274f9befdc63be00a0; all 22 direct authority file identities, the exact 25-file/five-directory snapshot indexes and seven protected source hashes rehash exact
    - item_id: v31x-sentinel-no-reuse-and-no-downstream-execution
      evidence_identity: predecessor_science_reused=false, sentinel_science_reused=false; only the failed sentinel root exists, with no related live process and no official root/dispatch
  failed_items:
    - item_id: v31x-sentinel-wls-scriptcommandline-interface
      blocker_id: v31x-sentinel-wls-scriptcommandline-contract-mismatch
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31x-sentinel-numerical-science
      reason: the WLS exited at its usage guard before request import, source loading or any NumericalIntegration call; 35 calls, 70 solutions, 105 overlaps and all numerical budgets are absent
    - item_id: v31x-official-science
      reason: sentinel gate failed; no official dispatch/root is authorized or present
    - item_id: v31x-thresholds-and-certificates
      reason: the 16 thresholds and five certificates were not evaluated or generated
    - item_id: v3-2
      reason: V3.2 is forbidden and was not started

findings:
  - finding_id: v31x-sentinel-wls-scriptcommandline-contract-mismatch
    class: BLOCKING_CURRENT_GATE
    summary: The exact reviewed Python launcher invokes the exact WolframKernel with `-script WLS REQUEST OUTPUT`, but the WLS assumes `$ScriptCommandLine` has length three and immediately exits 64; this is a WLS argv-interface implementation defect, not a dispatch-construction, resource or numerical-science failure.
    blocker_id: v31x-sentinel-wls-scriptcommandline-contract-mismatch
    violated_contract_item: The one-use sentinel must execute exactly 35 fresh NumericalIntegration calls and publish 35 PASS records, 70 boundary solutions and 105 overlap decompositions before an official dispatch can be considered.
    exact_evidence: WLS SHA-256 652ced5b32983e79df6c36a5e697c5263aa0570f4cf4b20d58a2b3c20e6e1907 lines 7-12 require `Length[$ScriptCommandLine] == 3` and read entries 2/3. Python producer SHA-256 e8709bd42d7a2ae037bde40f097568dae62e6f6b0c2a7868fcfee23859231c2b lines 736-742 constructs the exact five-element child argv. Prelaunch 3a2e406343d55d0db30c6d70b023953f7ad606e4c23baf692981d8ab5cc5d517 and receipt 8c7b6961570c4aea13c613b26c8a1451b41110f0825c87d709dfec7b677c064e record that same argv and rc64. Stdout SHA-256 420e61b4fb899771ee2e4b6807d9681fe496f7a7d850aafd7206836f9ff84c0d is exactly `usage: phase6_v3_1_x_bhpt_direct.wls REQUEST OUTPUT\n`; stderr is empty. Records/raw_records are both empty SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855. Outcome 0 is ERROR and outcomes 1..34 are NOT_STARTED_AFTER_PRIOR_FAILURE.
    expected_value: The exact `WolframKernel -script WLS REQUEST OUTPUT` interface reaches request validation, then each of the 35 frozen nodes produces one PASS record with two boundary solutions and three overlaps; child executions close naturally with rc0.
    observed_value: The first exact child reaches only the WLS usage guard and returns rc64 before request import; no loaded-source runtime record, solver call, boundary solution, overlap or scientific record exists. The root is terminal FAIL/nonresumable and the one-use dispatch is consumed.
    bounded_repair: Freeze the actual `$ScriptCommandLine` vector produced by the exact reviewed kernel/`-script` invocation with a separate zero-science argv probe; change only the WLS parser to accept that one exact executable/mode/script/request/output shape and reject every missing, extra, reordered or alternate form. Because the existing producer hard-binds the pre-repair implementation-review authority and requires it to contain all current implementation hashes, update only its fixed review-authority binding to one predeclared future repair-review archive. Add zero-science unit/regression coverage including an exact external-kernel argv handshake that proceeds only to the missing-request guard, plus negative argv forms. Do not change formulas, source snapshot, graph, precision, domain, thresholds, conventions, environment, radial sources or scientific method.
    allowed_files:
      - scripts/phase6_v3_1_x_bhpt_direct.wls
      - src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      - tests/unit/test_phase6_v3_external_direct.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
    recheck_command: >-
      /usr/bin/env -i PYTHONDONTWRITEBYTECODE=1
      PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src
      /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14
      -m pytest -q tests/unit/test_phase6_v3_external_direct.py
      tests/regression/test_phase6_v3_external_direct_publication.py
    unblock_condition: A formal repair-cycle-1 delta review independently proves the actual exact `$ScriptCommandLine` shape, exact-shape-only parsing, negative-form rejection, unchanged passed/protected identities, zero science during preflight, and a future review authority that binds all repaired implementation hashes. Only then may Root T0 create a different one-use dispatch and a fresh absent sentinel root; the consumed dispatch/root and all its bytes remain permanently non-reusable.
  - finding_id: v31x-sentinel-scriptcommandline-vector-not-persisted
    class: NONBLOCKING_LIMITATION
    summary: The root proves that the real `$ScriptCommandLine` fails the length-three guard, but the internal Wolfram list itself was not persisted; its exact elements must be established by the bounded zero-science probe rather than inferred or invented.
  - finding_id: v31x-sentinel-existing-tests-did-not-exercise-wls-argv-boundary
    class: FOLLOW_UP_DEBT
    summary: Existing tests bind the Python child argv and fake lifecycle but do not run the exact WLS through the real `WolframKernel -script` argv boundary; the bounded repair must add that zero-science handshake.
  - finding_id: v31x-official-v3-2-global-green-forbidden
    class: FOLLOW_UP_DEBT
    summary: This YELLOW authorizes no retry, official dispatch/root, V3.2, threshold/domain/method change or global GREEN.

delta_review: null
hold_details: null

verification:
  commands:
    - sha256sum of the frozen review prompt, package, bridge review, one-use dispatch, domain, thresholds, anchor matrix, convention note and snapshot authority
    - independent CPython 3.14 manifest/inventory rebuild over every candidate-root path, including canonical JSON/JSONL and path/SHA/size/mode/nlink equality
    - independent CPython 3.14 reload of dispatch consumption and all 35 outcomes, including one-use search over every classic-scattering dispatch consumption
    - independent CPython 3.14 rebuild of the 25-file/five-directory snapshot content and identity indexes and rehash of all seven protected radial sources
    - static line/dataflow inspection of WLS argv parsing and Python child command/Popen lifecycle
    - read-only process and V3.1-X root inventory checks
  results:
    - frozen identities PASS
    - root/manifest/canonical serialization/permissions/link inventory PASS
    - one-use dispatch binding and exactly-one consumption PASS
    - 35-outcome fail-closed totality PASS: one ERROR plus 34 NOT_STARTED_AFTER_PRIOR_FAILURE
    - child process closure PASS: rc64, no signal/timeout, reaped, process group empty
    - source snapshot/protected identity/nonreuse guards PASS
    - sentinel acceptance FAIL: zero scientific records, zero boundary solutions and zero overlaps
    - exact causal classification PASS: WLS `$ScriptCommandLine` contract mismatch before request import

non_claims:
  - no V3.1-X sentinel scientific PASS
  - no statement that any missing numerical node would pass after the interface repair
  - no official V3.1-X execution or evidence
  - no reuse, retry or resume of the consumed dispatch or failed root
  - no threshold, domain, convention, precision, method or protected-radial change
  - no finite-radius observer, Li-figure or broader full-domain claim
  - no V3.2 and no global GREEN

repair_cycle:
  completed_bounded_repairs: 0
  completed_bounded_scientific_repairs: 0
  next_permitted_cycle: bounded repair 1 followed by delta review 1
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Independent conclusion

The immutable sentinel evidence is internally complete and correctly sealed,
but the bounded sentinel claim is false.  The dispatch and supervisor launched
the reviewed command exactly; the WLS rejected the real `-script` command-line
shape at its own usage guard.  This is a newly evidenced, bounded
implementation-interface blocker.  It does not establish any numerical or
physical failure, and it does not permit reuse of this consumed attempt.

Root T0 may freeze one bounded repair-cycle-1 package limited to the four
listed files and the binary unblock condition above.  This review does not
authorize implementation, a Wolfram run, a new dispatch/root, official
science, V3.2, or global GREEN.
