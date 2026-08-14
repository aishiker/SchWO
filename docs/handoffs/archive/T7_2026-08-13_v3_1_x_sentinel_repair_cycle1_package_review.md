# T7 package review — V3.1-X sentinel bounded repair cycle 1

Date: 2026-08-13

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL REPAIR CYCLE 1 PACKAGE READY FOR T6
```

## Verdict record

```yaml
review_id: t7_v3_1_x_sentinel_repair_cycle1_package_review_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
repair_id: phase6_v3_1_x_sentinel_argv_repair_cycle1_v1
attempt: repair_1_package_review
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed
reviewed_candidate:
  root: configs/phase6_v3_1_x_sentinel_repair_cycle1_package.json
  identities:
    - path: configs/phase6_v3_1_x_sentinel_repair_cycle1_package.json
      sha256: 5b2da4f0168082996e55a8f4ad27869c8c8e6a27cd207c56696f23134501da75
      size: 10144
      mode: 0444
      nlink: 1
    - path: docs/phase6_v3_1_x_sentinel_repair_cycle1_design.md
      sha256: b576f96063d3245dd1e37940d4c5b7603983cbf2ef912af6550aa6f1c3274970
      size: 4924
      mode: 0444
      nlink: 1
    - path: docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle1_package_review.md
      sha256: 23fdd60c3b67ffb88b1c6e8a764d20c37bf9be5c221af807623021dae084f108
      size: 2428
      mode: 0444
      nlink: 1
    - path: docs/prompts/phase6_t6_v3_1_x_sentinel_repair_cycle1_implementation.md
      sha256: 6f8608c9dee71f17a0b4c8003923be94538a1a93c72c37308d89a08942921bd2
      size: 2011
      mode: 0444
      nlink: 1
    - path: docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle1_delta_review.md
      sha256: 8e0aa130a66c16b2deb6d335ff1303375f9e96489843a87aacc5d3bd8decd4b4
      size: 2131
      mode: 0444
      nlink: 1

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle1_package_review.md
    sha256: 23fdd60c3b67ffb88b1c6e8a764d20c37bf9be5c221af807623021dae084f108
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  parent_package:
    path: configs/phase6_v3_1_x_external_direct_route_package.json
    sha256: 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752
  formal_terminal_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_sentinel_terminal_review.md
    sha256: cf4ba0a25527f0298bf3f18ba03a19b4a849a592db30bc610c2bb0749015d772
    sole_failed_item: v31x-sentinel-wls-scriptcommandline-interface
    sole_blocker_id: v31x-sentinel-wls-scriptcommandline-contract-mismatch
    class_a_nine_fields_complete: true
  failed_sentinel:
    root: runs/phase6/classic_scattering/v3_1_x_external_direct_sentinel_v1_20260813T055002Z_py314
    failure_sha256: c002664933d58913b5793ffc1100a5958cb1dfdd12d0c9b3664ffa9ddfb2f541
    manifest_sha256: d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772
    dispatch_path: docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0001.json
    dispatch_sha256: 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9
    immutable_nonresumable_nonretryable_nonreusable: true
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  external_anchor_matrix:
    path: configs/phase6_v3_0_external_anchor_matrix.json
    sha256: 06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485
  thresholds:
    - id: frozen V3.0 threshold contract
      value: 16 unchanged thresholds
      units: mixed per-observable units defined by the frozen source
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  convention_contract:
    path: references/notes/phase6_v3_absorption_scattering_conventions.md
    sha256: 82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a
  frozen_implementation_baseline:
    scripts/phase6_v3_1_x_bhpt_direct.wls: 652ced5b32983e79df6c36a5e697c5263aa0570f4cf4b20d58a2b3c20e6e1907
    scripts/phase6_v3_1_x_external_direct.py: 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768
    src/schwgw/validation/phase6_v3_external_direct.py: 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4
    src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py: e8709bd42d7a2ae037bde40f097568dae62e6f6b0c2a7868fcfee23859231c2b
    tests/unit/test_phase6_v3_external_direct.py: 1e0c96360c652ec6d1c82aa7daf8631df247d8ce43f1ffe2b4ca295227d22604
    tests/regression/test_phase6_v3_external_direct_publication.py: 061ebeeeb276f5cab2a3e3b9acae2a2ac87b68a069f059563113739266bc8623
  blocking_criteria:
    - change only the WLS argv parser, fixed producer review authority and two tests
    - accept only exact `$CommandLine={absolute_kernel,-script,absolute_WLS,REQUEST,OUTPUT}` and `$ScriptCommandLine={}`
    - reject missing, extra, reordered, alternate executable/mode/script, fallback, slicing and runtime-selected forms before request import
    - positive absent-request handshake returns exact rc73/stdout before Import, Needs, overlay creation, source load or solver activity
    - future implementation review path is singular and predeclared; its digest is supplied only by a later one-use Root-T0 dispatch
    - failed dispatch/root remain immutable and forbidden; any later attempt uses a different one-use dispatch and fresh absent UTC root
    - graph, direct NumericalIntegration method, six overlays, 90/120 precision schedule, thresholds, conventions, environment and protected identities remain unchanged
  protected_identities:
    - {path: src/schwgw/numerics/radial_solver.py, expected_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_start_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_end_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9}
    - {path: src/schwgw/numerics/conditioned_radial.py, expected_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_start_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_end_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2}
    - {path: src/schwgw/numerics/scaled_tortoise_radial.py, expected_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_start_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_end_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df}
    - {path: src/schwgw/numerics/adaptive_jost_radial.py, expected_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_start_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_end_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896}
    - {path: src/schwgw/numerics/matching.py, expected_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_start_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_end_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340}
    - {path: src/schwgw/numerics/physical_boundary_radial.py, expected_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_start_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_end_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f}
    - {path: src/schwgw/numerics/boundary_conditions.py, expected_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_start_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_end_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22}

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL REPAIR CYCLE 1 PACKAGE READY FOR T6

incremental_review_state:
  passed_items:
    - item_id: v31x-repair1-package-canonical-and-recursive-identity
      evidence_identity: canonical package 5b2da4f0168082996e55a8f4ad27869c8c8e6a27cd207c56696f23134501da75; five package/member files are 0444/nlink1; 37 unique recursive path/hash bindings rehash exact and are regular nlink1
    - item_id: v31x-repair1-single-class-a-lineage
      evidence_identity: terminal review cf4ba0a25527f0298bf3f18ba03a19b4a849a592db30bc610c2bb0749015d772 freezes exactly failed item v31x-sentinel-wls-scriptcommandline-interface and blocker v31x-sentinel-wls-scriptcommandline-contract-mismatch with all nine mandatory fields
    - item_id: v31x-repair1-liveness-lineage
      evidence_identity: V3.1-X sentinel initial terminal review completed repairs=0/2; this package is bounded repair 1 and explicitly not V3.1-U repair cycle 3; package review consumes no repair
    - item_id: v31x-repair1-exact-four-scope
      evidence_identity: package implementation_scope and repair.allowed_files are the same four unique paths and exactly equal the formal terminal-review allowed set
    - item_id: v31x-repair1-commandline-mathematics
      evidence_identity: the frozen launch is five elements; `$ScriptCommandLine={}` cannot supply request/output, while exact length-five `$CommandLine` plus exact first-three literal comparison uniquely selects request/output at positions 4/5 and rejects missing/extra/reordered/alternate executable/mode/script forms without fallback or slicing
    - item_id: v31x-repair1-zero-science-handshake-order
      evidence_identity: existing WLS control flow places the absent-request/output guard before RawJSON Import at line 17, package/source overlay inspection, Needs at line 113 and ReggeWheelerRadial at line 137; exact rc73/stdout therefore proves argv parsing without science
    - item_id: v31x-repair1-noncircular-authority-chain
      evidence_identity: future package review and implementation-delta review paths are singular/predeclared and absent at review start; no future digest is hardcoded, and only a later Root-T0 dispatch may bind the implementation review's fresh digest and repaired six hashes
    - item_id: v31x-repair1-failed-attempt-nonreuse
      evidence_identity: failed root is 0555 with 77 regular 0444/nlink1 files, nine 0555 directories, zero links, canonical manifest exact; one-use id has one consumption only, failure is nonresumable/nonretryable, and no other V3.1-X root exists
    - item_id: v31x-repair1-science-authority-preservation
      evidence_identity: parent package, graph 35/70/105 and 161/322/483, NumericalIntegration/In-Up method, six overlays, 90/120 precision ladder, domain, anchor matrix, 16 thresholds, five certificates, convention and seven protected hashes remain unchanged
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31x-repair1-implementation
      reason: exact-four implementation bytes and formal zero-science preflight are future T6 work
    - item_id: v31x-repair1-real-kernel-handshake
      reason: T0's temporary diagnostic established the shape but is not a durable acceptance artifact; formal T6 and the future T7 delta review must independently reproduce the exact rc73 zero-science handshake
    - item_id: v31x-repair1-sentinel-science
      reason: package review runs no solver and creates no dispatch/root; V3.1-X sentinel science remains NOT_ASSESSED after the immutable failed attempt
    - item_id: v31x-repair1-official-v3-2
      reason: official V3.1-X and V3.2 remain forbidden

findings:
  - finding_id: v31x-repair1-probe-is-diagnostic-only
    class: NONBLOCKING_LIMITATION
    summary: The independent T0 `$CommandLine` probe was temporary and is not durable scientific evidence; package readiness is nevertheless non-circular because formal T6 must reproduce the exact zero-science handshake and formal T7 must independently verify it before any fresh dispatch.
  - finding_id: v31x-repair1-no-science-claim
    class: FOLLOW_UP_DEBT
    summary: Package GREEN establishes only bounded implementation readiness; no repaired implementation, numerical node, sentinel acceptance, official route or downstream V3 claim exists yet.

delta_review: null
hold_details: null

verification:
  commands:
    - SHA-256/stat recheck of package, four members, formal terminal review, parent chain, domain/threshold/convention and protected sources
    - independent CPython 3.14 canonical JSON reload and enumeration of every member/source/baseline/failed-root/protected recursive path binding
    - independent exact-four set comparison among package implementation_scope, repair.allowed_files and terminal Class-A allowed_files
    - independent failed-root manifest/path/SHA/size/mode/nlink rebuild and repository-wide one-use-id consumption search
    - static WLS control-flow and exact `$CommandLine` predicate analysis; no Wolfram invocation
    - read-only V3.1-X root and process inventory
  results:
    - package canonical serialization PASS
    - frozen package/member identities 5/5 PASS; all 0444/nlink1
    - recursive unique path/hash bindings 37/37 PASS; all regular nlink1
    - exact-four repair scope PASS
    - sole Class-A lineage and liveness count PASS
    - exact-shape/no-fallback argv design PASS
    - rc73 pre-import/pre-source/pre-solver handshake ordering PASS
    - non-circular future authority graph PASS; both future paths absent at review start
    - failed dispatch/root immutability, single consumption and nonreuse PASS
    - graph/method/precision/domain/threshold/convention/protected preservation PASS
    - Wolfram launches, solver calls, dispatch creations and new roots by this review: 0

non_claims:
  - package readiness is not repaired implementation acceptance
  - no numerical node is predicted or established to pass
  - no failed dispatch/root record is reusable
  - no fresh sentinel or official execution is authorized by this package review
  - no method, graph, precision, threshold, domain, convention, environment or protected-radial change
  - no independent even-sector external result or pristine-upstream claim
  - no V3.2, full-domain V3 certification or global GREEN

repair_cycle:
  completed_bounded_repairs: 0
  current_bounded_repair: 1
  package_review_consumes_repair: false
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Bounded authorization

Root T0 may dispatch only the frozen formal T6 zero-science exact-four
implementation task.  T6 must reproduce the exact WolframKernel argv probe
and absent-request rc73 handshake without importing the request, loading BHPT
sources or calling a solver.  A later formal T7 delta review is mandatory
before Root T0 may create any different one-use sentinel dispatch and fresh
root.

This review does not consume repair cycle 1 and authorizes no implementation
outside the four paths, science, dispatch, sentinel, official execution,
V3.2 or global GREEN.
