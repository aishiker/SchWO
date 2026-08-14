# T7 final implementation delta review — V3.1-X source-ledger repair cycle 2

Timestamp: `2026-08-13T11:54:27Z`  
Review kind: `incremental implementation delta / final bounded cycle 2`  
Reviewer task: `019f5ed1-b421-7ec2-9bac-8d134855a1ed`

```text
ADVANCE_DECISION: ESCALATE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED
```

The exact-five implementation is **not** ready for a one-use formal source-load
micro dispatch.  The one and only review-authorized real-Wolfram zero-science
preflight exited `69` with exact stdout
`loaded-source record semantic mismatch\n`.  It produced no WLS result and
therefore no observed start/end projection, Paclet record, preload record,
runtime record, or WLS counter record.  The launch was not retried.  The child
was fully waited/reaped and its process group is empty.

This is the final bounded repair cycle (`2/2`).  No `REPAIR`, cycle 3, formal
micro dispatch, 35-call sentinel, official V3.1-X run, V3.2, or global GREEN is
authorized by this review.

## Identity-bound review record

```yaml
review_id: t7_v3_1_x_source_ledger_repair_cycle2_implementation_delta_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
repair_id: phase6_v3_1_x_source_ledger_repair_cycle2_v1
attempt: repair_2
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed

frozen_review_basis:
  package:
    path: configs/phase6_v3_1_x_sentinel_repair_cycle2_source_ledger_package.json
    sha256: 2f4f2304b4e9507a3627ee26d3aadd9d7632152d7367653746bedf1ec591673c
    size: 9700
    mode: "0444"
    nlink: 1
  package_approval:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle2_source_ledger_package_delta_review_1.md
    sha256: 4acf5aa7e09874576da100a3b9c7c6acee2ea033d7da798dde689f1611da5685
    size: 9918
    mode: "0444"
    nlink: 1
  implementation_delta_contract:
    path: docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle2_source_ledger_delta_review.md
    sha256: 52096dc832fed2bc64153273e3d5d69ac446ac96ccf63bf468d12e7b25162aa1
    size: 2671
    mode: "0444"
    nlink: 1
  root_t0_adjudication:
    path: docs/handoffs/archive/T0_2026-08-13_v3_1_x_repair_cycle2_preflight_provenance_adjudication.md
    sha256: 47638b68b540fa4ef35f40c32fe4b7774e932768587a2fbf7597913bc546bb8a
    size: 4109
    mode: "0444"
    nlink: 1

reviewed_exact_five:
  scripts/phase6_v3_1_x_bhpt_direct.wls: 7a8277b6996fccbd3d0b515ebba8a0fae17a9c6a9efa7a0d3116a9055bbc041f
  src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py: fa0c9c2cdadead19dd1051c45fb0ac22932641a7266d9717dfd2188377945af8
  scripts/phase6_v3_1_x_external_direct.py: b85a8cff88b1cab5c01b50fbd047b403d56c37952ca920bde55668cf7affa574
  tests/unit/test_phase6_v3_external_direct.py: e0ad4e08c84921cb1eaaf1a91e351e189e474938678b56d033c3494cbb7574c3
  tests/regression/test_phase6_v3_external_direct_publication.py: ee79b8c276cc9eee369e97de83a3008714f090a1c735b7872f05e901cb3a862d

unchanged_direct_core:
  path: src/schwgw/validation/phase6_v3_external_direct.py
  sha256: 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4

protected_radial_identities:
  src/schwgw/numerics/radial_solver.py: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
  src/schwgw/numerics/conditioned_radial.py: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
  src/schwgw/numerics/scaled_tortoise_radial.py: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
  src/schwgw/numerics/adaptive_jost_radial.py: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
  src/schwgw/numerics/matching.py: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
  src/schwgw/numerics/physical_boundary_radial.py: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
  src/schwgw/numerics/boundary_conditions.py: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
```

All four frozen authorities, all exact-five paths, the unchanged direct core,
all ten package source bindings, and all seven protected radial sources were
rehash-exact at the end of review.  The two consumed failed-root manifests
remain exactly `d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772`
and `6e0d2349d998f76ee8d149e4551bf27222c5d93bf4ec9fb7b790adbc9f506109`.

## Incremental item inventories

```yaml
incremental_review_state:
  passed_items:
    - item_id: v31x-r2-exact-five-scope-and-identities
      evidence_identity: five hashes listed above; maximum changed paths 5
    - item_id: v31x-r2-package-source-and-protected-bindings
      evidence_identity: package 2f4f2304...1673c; source bindings 10/10; protected 7/7
    - item_id: v31x-r2-canonical-duplicate-json-preparse
      evidence_identity: focused unit/regression adversaries PASS
    - item_id: v31x-r2-six-field-static-dataflow
      evidence_identity: one SOURCE_FIELD_ORDER and one normalizer/ledger path in WLS
    - item_id: v31x-r2-fixed-micro-key-and-solver-unreachability
      evidence_identity: V3A-MODE-BHPT-RW-001/P1 and micro Exit[0] precede sole ReggeWheelerRadial call
    - item_id: v31x-r2-lifecycle-fail-closed
      evidence_identity: focused lifecycle/stream/timeout/duplicate-raw tests PASS; real child reaped
    - item_id: v31x-r2-fake-child-and-cross-use-rejection
      evidence_identity: focused negative tests PASS
    - item_id: v31x-r2-fixed-noncircular-authority-namespaces
      evidence_identity: implementation/micro/full/official paths fixed; future paths absent
    - item_id: v31x-r2-failed-root-immutability-and-nonreuse
      evidence_identity: both package-bound manifests rehash exact
    - item_id: v31x-r2-no-science-and-no-formal-artifact
      evidence_identity: no dispatch/root; failure before micro result and before sole solver branch
  failed_items:
    - item_id: v31x-r2-real-wolfram-semantic-ledger-preflight
      blocker_id: v31x-r2-wls-semantic-normalizer-runtime-failure
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31x-r2-formal-source-load-micro
      reason: no formal dispatch/root; review-only preflight failed
    - item_id: v31x-r2-full-35-call-sentinel
      reason: not authorized and not executed
    - item_id: v31x-r2-official-v31x
      reason: not authorized and not executed
    - item_id: v31x-r2-thresholds-and-five-certificates
      reason: no scientific records exist in this review
    - item_id: v3-2
      reason: forbidden downstream stage
```

## Independent six-field reconstruction

The raw canonical request stores each object in alphabetical member order
`context, mode, nlink, path, sha256, size`; the frozen semantic projection is
`context, path, sha256, size, mode, nlink`.  Independent strict parsing found
no duplicate member.  For all eight ordered records:

- exact six-key set: `8/8 PASS`;
- exact Python types `str,str,str,int,int,int`: `8/8 PASS`;
- exact context and frozen position: `8/8 PASS`;
- normalized relative path and exact frozen path: `8/8 PASS`;
- lowercase 64-hex SHA-256: `8/8 PASS`;
- nonnegative exact size, mode `292`, nlink `1`: `8/8 PASS`;
- independently rehashed overlay six-field projection equality: `8/8 PASS`;
- duplicate context/path: `0/0`.

The exact expected/actual projections were:

```text
ReggeWheeler` | Kernel/ReggeWheeler.m | 24fb778a9e09d2a933f133d571e948f8efcb6442e766f40963bdd248718506da | 405 | 292 | 1
ReggeWheeler`MST`MST` | Kernel/MST/MST.m | 868b8e4b0bdbf1a6b56033168f00a4251e42122600235d0370ea0926376814b7 | 35438 | 292 | 1
ReggeWheeler`MST`RenormalizedAngularMomentum` | Kernel/MST/RenormalizedAngularMomentum.m | 402ec64abb706c984cc6db44e91343dac5d5b5cf350d429ad6c13ab784a85528 | 12298 | 292 | 1
ReggeWheeler`NumericalIntegration` | Kernel/NumericalIntegration.m | a8601cd1b377bf4741035a03bec98590ebffbec0004a63af498a260f1d05c5fc | 9478 | 292 | 1
ReggeWheeler`Hyperboloidal` | Kernel/Hyperboloidal.wl | 0e7aebc51595e538b42618c2b37e36f1e518e89cb3b8235e720e2dc96fe05887 | 25998 | 292 | 1
ReggeWheeler`ReggeWheelerRadial` | Kernel/ReggeWheelerRadial.m | 2af593f527b39d2b7ece71f99e50ecb6b84399342251985004d6d2e2c3fed41f | 19584 | 292 | 1
ReggeWheeler`ReggeWheelerSource` | Kernel/ReggeWheelerSource.m | 3a1794cc09293067c804e60ea916bc59d7118468100d2a7c6e6bd73ea8532406 | 3288 | 292 | 1
ReggeWheeler`ReggeWheelerMode` | Kernel/ReggeWheelerMode.m | f8fa3882aecc927b885024cb6ec471dd0b7644a929c35eed5903beb0c55322c7 | 8940 | 292 | 1
```

Thus the observed failure is not source-byte, list-order, context, path,
hash, size, mode, or nlink drift in the request/overlay data.  It is localized
to the current WLS semantic-normalizer/runtime boundary.  The WLS uses one
generic `loaded-source record semantic mismatch` branch for all leaf
predicates and does not persist the record ordinal or failed predicate.
Because the single permitted launch is consumed, the exact leaf predicate is
**UNKNOWN** and must not be retroactively guessed.

## Sole review-only real-Wolfram launch

The Root-T0 adjudication permitted at most one review-only, zero-science real
Wolfram launch.  Exactly one was executed and its evidence was written to a
persistent, subsequently sealed directory rather than an auto-deleting
temporary context.

```yaml
review_evidence_root: /private/tmp/schwo_t7_v31x_r2_review_preflight.ptN6p0
root_mode: "0555"
regular_files: 36
directories_inclusive: 6
regular_file_mode_nlink: all_0444_nlink1
directory_modes: all_0555
symlink_or_special_count: 0
regular_file_bytes: 719947
tree_identity_sha256: 64602b35aec85f8facac412b90eb8e8a329fe5300e493d76fc1afd1d1f31a534
tree_identity_serialization: explicit-false compact sorted-key JSON over root/files/directories/other records including path,size,dev,inode,mode,nlink and file sha256

operation: source_load_micro_sentinel
formal_dispatch: false
formal_execution_root: false
attempt_limit: 1
attempts_executed: 1
retry_count: 0
reusable_as_micro_or_science: false

kernel_path: /Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel
kernel_sha256: 70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c
wls_sha256: 7a8277b6996fccbd3d0b515ebba8a0fae17a9c6a9efa7a0d3116a9055bbc041f

request_sha256: 503eb41d144a041fbda65a0934002c09b680bd8fa7f92ea8195348869ec1a8bb
preflight_plan_sha256: 06271b4f3fc7e522d2792555d25b5e60ab0fc6e09a65baf59f0a3bd5822a79de
source_start_sha256: 1ff879e1c431d5a9d26d5fb96b1166a9dacb624a542f000011a3bca6071960e1
overlay_identity_start_sha256: 8703f68d1b40d0f8f50eab3061ed20aa64bec3bc1c0021e86b8f132c61730c19

child_prelaunch_sha256: d2a0bef0a5a7a881f53761b11d9b256cf5b13279406060e17dba7f03008cb818
child_running_sha256: fa22b6775830e9883526a0e4cabe2d9acb122dca8c962a9f9fb55b2c38f98c07
child_receipt_sha256: afaaf492f028c6936bc69cc833b1045747566b39cc4177f54c11d2ba3761500c
child_terminal_sha256: b88f69235523a6603edf47885072cda00a1b15bcb3147ab1ccaa9e8de97f2e88
summary_sha256: 935b65239a10e12b9cf160eae9d64ca5e9a368c14364e65352d1adaab57563fb

pid_sid_pgid: 7185/7185/7185
returncode: 69
signal: null
timed_out: false
popen_wait_called: true
child_reaped: true
process_group_empty: true
wait_error: null
cleanup_actions: [wait]

stdout_size: 39
stdout_sha256: 37272a68ab5eb4dcb6d46815d08608b26c5c3cca457fcd2d601c5cd6ac15cc03
stdout_exact: "loaded-source record semantic mismatch\\n"
stderr_size: 0
stderr_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

wls_result: absent
projection: null
source_end: null
wls_preload_state: null
wls_paclet: null
wls_runtime: null
wls_counters: null
```

The source-start record binds the full package/source authority graph, the
25-file/5-directory overlay identity, external snapshot metadata, exact-five,
direct core, and protected sources.  However, the WLS failed before result
publication.  Therefore observed WLS source-end/Paclet/preload/runtime/counter
evidence is absent.  This fails the adjudication's requirement that the sole
preflight close those provenance surfaces; the absence cannot be repaired by
inference from Python-side source-start bytes.

Static control flow and the exact failure point place the only
`ReggeWheelerRadial[` call after the micro branch and after the failing
normalizer.  No formal dispatch/root exists, and no Wolfram/Python process
remained after reaping.  Accordingly:

```yaml
real_wolfram_review_launches: 1
formal_micro_launches: 0
full_sentinel_launches: 0
official_launches: 0
regge_wheeler_radial_calls: 0
external_api_calls: 0
solver_calls: 0
boundary_solution_calls: 0
overlap_calls: 0
scientific_calls: 0
```

## Finding and governance disposition

```yaml
findings:
  - finding_id: v31x-r2-real-wolfram-semantic-ledger-preflight
    class: BLOCKING_CURRENT_GATE
    blocker_id: v31x-r2-wls-semantic-normalizer-runtime-failure
    summary: >-
      The final exact-five WLS rejects an independently valid and byte-exact
      eight-record semantic ledger in the sole real-Wolfram zero-science
      preflight and publishes no required source/Paclet closure evidence.
    violated_contract_item: >-
      The implementation-delta contract requires imported expected and
      independently rebuilt start/end records to pass the one exact six-field
      projection in real Wolfram, with a complete zero-science transcript and
      source/Paclet identities, before a formal micro dispatch is authorized.
    exact_evidence: >-
      /private/tmp/schwo_t7_v31x_r2_review_preflight.ptN6p0;
      summary 935b65239a10e12b9cf160eae9d64ca5e9a368c14364e65352d1adaab57563fb;
      request 503eb41d144a041fbda65a0934002c09b680bd8fa7f92ea8195348869ec1a8bb;
      terminal b88f69235523a6603edf47885072cda00a1b15bcb3147ab1ccaa9e8de97f2e88;
      stdout 37272a68ab5eb4dcb6d46815d08608b26c5c3cca457fcd2d601c5cd6ac15cc03.
    expected_value: >-
      Exactly one rc0 real-Wolfram source-load preflight; eight expected,
      start and end projections equal in frozen order; complete non-null
      preload/Paclet/runtime/source-end records; counters proving zero external
      API/ReggeWheelerRadial/solver/boundary/overlap/scientific calls.
    observed_value: >-
      rc69; exact stdout "loaded-source record semantic mismatch\n"; empty
      stderr; no WLS result; projection/source_end/wls_preload_state/wls_paclet/
      wls_runtime/wls_counters all null. Independent request/overlay
      reconstruction nevertheless passes every intended six-field rule 8/8.
    bounded_repair: >-
      None remains within this gate. Repair cycle 2 is exhausted. Root T0 must
      adjudicate under the liveness protocol by narrowing/freezing the blocked
      branch or freezing a distinct, newly reviewed gate/algorithm; T7 does
      not authorize an isomorphic cycle 3.
    allowed_files: []
    recheck_command: >-
      none — another Wolfram preflight, implementation patch, formal micro
      dispatch or science launch is prohibited by this terminal review
    unblock_condition: >-
      Not satisfiable inside phase6_v3_1_x_source_ledger_repair_cycle2_v1.
      Only a new Root-T0 adjudication with a distinct frozen authority and
      independent review can create a future unblock condition.
```

The exact leaf predicate inside the WLS semantic `If` is not observable from
the persisted failure branch.  It is therefore deliberately recorded as
`UNKNOWN`, not misreported as a source/path/hash/stat mismatch.

## Verification commands and results

```yaml
verification:
  commands:
    - >-
      /usr/bin/env -i PYTHONDONTWRITEBYTECODE=1
      PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src
      LC_CTYPE=C.UTF-8 __CF_USER_TEXT_ENCODING=0x1F5:0x19:0x34
      /opt/homebrew/opt/python@3.14/bin/python3.14 -m pytest -q
      tests/unit/test_phase6_v3_external_direct.py
      tests/regression/test_phase6_v3_external_direct_publication.py
    - >-
      same frozen CPython 3.14 environment, pytest -q
      tests/unit/test_phase6_v3_cycle2.py
    - >-
      ruff check and ruff format --check over the four exact Python paths
    - >-
      CPython 3.14 py_compile over the four exact Python paths using
      /private/tmp/schwo_t7_v31x_compilecheck
    - >-
      git diff --check -- scripts/phase6_v3_1_x_bhpt_direct.wls
      src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      scripts/phase6_v3_1_x_external_direct.py
      tests/unit/test_phase6_v3_external_direct.py
      tests/regression/test_phase6_v3_external_direct_publication.py
    - one review-only real-Wolfram source_load_micro_sentinel preflight
  results:
    - focused exact unit+regression: 154 passed in 17.51s
    - adjacent frozen cycle2 suite: 49 passed in 3.51s
    - Ruff check: PASS
    - Ruff format: 4 files already formatted
    - CPython 3.14 compile: PASS 4/4
    - targeted git diff --check: PASS
    - canonical duplicate/key/type/value/path/stat/inode/alias adversaries: PASS
    - package source bindings: PASS 10/10
    - protected identities: PASS 7/7
    - future micro/full/official authority paths and roots: ABSENT
    - related live process after child reap: 0
    - real-Wolfram preflight: FAIL rc69; no retry
```

## Delta and liveness state

```yaml
delta_review:
  reviewed_failed_items:
    - v31x-r2-source-ledger-semantic-comparison
    - v31x-r2-real-wolfram-zero-science-provenance
  passed_invariants_rechecked:
    - exact-five scope and hashes
    - direct-core and seven protected hashes
    - package and ten source bindings
    - fixed graph/method/precision/domain/threshold/convention
    - duplicate-member raw preparse
    - micro solver unreachability
    - fake-child/cross-use/replay rejection
    - fixed non-circular future authorities
    - failed-root immutability/nonreuse
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

repair_cycle:
  completed_bounded_repairs: 2
  completed_bounded_scientific_repairs: 2
  current_cycle: 2
  maximum_cycles: 2
  same_substantive_blocker_remaining: true
  repair_cycle_2_consumed: true
  repair_cycle_3_permitted: false
  t0_adjudication_required: true
```

## Nonclaims and authorization boundary

- V3.1-X source-ledger implementation readiness is not established.
- V3.1-X source-load micro science is `NOT_ASSESSED`.
- No formal micro, 35-call sentinel, or official V3.1-X execution is
  authorized.
- The review-only launch and its copied overlay are not a dispatch, formal
  evidence root, scientific record, cache, retry authority, or reusable input.
- Neither failed sentinel root nor either failed dispatch is reusable.
- No method, graph, precision ladder, domain, threshold, convention, external
  source, direct core, or protected radial byte was changed or relaxed.
- V3.2 is not authorized.
- No global GREEN exists.

Root T0 adjudication is required.  T7 does not authorize another preflight,
repair cycle 3, formal micro dispatch, full sentinel, official run, or science.
