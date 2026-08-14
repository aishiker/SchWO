# T7 implementation delta review — V3.1-X sentinel repair cycle 1

Date: 2026-08-13

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL REPAIR CYCLE 1 IMPLEMENTATION READY FOR ONE-USE T0 DISPATCH
```

## Verdict record

```yaml
review_id: t7_v3_1_x_sentinel_repair_cycle1_implementation_delta_review_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
repair_id: phase6_v3_1_x_sentinel_argv_repair_cycle1_v1
attempt: repair_1_delta_review
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed
reviewed_candidate:
  root: repository exact-four implementation delta
  identities:
    - path: scripts/phase6_v3_1_x_bhpt_direct.wls
      sha256: 24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6
    - path: src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      sha256: 196d082c28798e2207bfeafd6d37282936b3c74c3e75bce233f8469ddd36737f
    - path: tests/unit/test_phase6_v3_external_direct.py
      sha256: 72209b0cc295df1882cb8fab5b642726095a295baaca1218061ac8e6ef1a6b0a
    - path: tests/regression/test_phase6_v3_external_direct_publication.py
      sha256: 847819dcdff4df3244c4a44e9c60f05149b332dc0492399447d0f2562c9c13db
  frozen_unchanged:
    - path: scripts/phase6_v3_1_x_external_direct.py
      sha256: 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768
    - path: src/schwgw/validation/phase6_v3_external_direct.py
      sha256: 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle1_delta_review.md
    sha256: 8e0aa130a66c16b2deb6d335ff1303375f9e96489843a87aacc5d3bd8decd4b4
  repair_package:
    path: configs/phase6_v3_1_x_sentinel_repair_cycle1_package.json
    sha256: 5b2da4f0168082996e55a8f4ad27869c8c8e6a27cd207c56696f23134501da75
  package_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_package_review.md
    sha256: 94bbce737b26d80149f19b5b15c8dcf56a29371f55cb5fad21ddb3c8ac61d9bd
  parent_package:
    path: configs/phase6_v3_1_x_external_direct_route_package.json
    sha256: 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752
  accepted_authority_bridge:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_authority_bridge_delta_review.md
    sha256: f807a6d05eeb577890f544069db1b408120cbe4a1eb9e676a89ac04e06aa9f9c
  formal_terminal_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_sentinel_terminal_review.md
    sha256: cf4ba0a25527f0298bf3f18ba03a19b4a849a592db30bc610c2bb0749015d772
  consumed_dispatch:
    path: docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0001.json
    sha256: 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9
  failed_sentinel:
    root: runs/phase6/classic_scattering/v3_1_x_external_direct_sentinel_v1_20260813T055002Z_py314
    failure_sha256: c002664933d58913b5793ffc1100a5958cb1dfdd12d0c9b3664ffa9ddfb2f541
    manifest_sha256: d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772
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
  t6_zero_science_preflight:
    path: /private/tmp/schwo_v31x_sentinel_repair1_preflight_nzda_c2o/zero_science_preflight.json
    sha256: f2c5191b3a457d664c25f255284823586aa9bdab77ef8424ea1e30463eb193b6
  blocking_criteria:
    - close only failed item v31x-sentinel-wls-scriptcommandline-interface
    - accept only exact WolframKernel/-script/WLS/REQUEST/OUTPUT command shape and empty ScriptCommandLine
    - reject missing, extra, reordered, alternate executable/mode/script, fallback and slicing forms before request import
    - exact absent-request handshake must return rc73 and exact stdout with empty stderr before Import, source loading or solver execution
    - producer must bind the singular predeclared review path, exact verdict, frozen authorities and all six current implementation hashes; only a later one-use Root-T0 dispatch supplies this archive digest
    - stale/alternate review, environment, argv/cwd/executable/launcher, replay and root-reuse surfaces fail closed
    - failed dispatch/root remain permanently forbidden and any future sentinel uses a different one-use dispatch and fresh absent UTC root
    - graph, NumericalIntegration method, six overlays, 90/120 ladder, threshold, domain, convention, protected and source identities remain unchanged
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
GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL REPAIR CYCLE 1 IMPLEMENTATION READY FOR ONE-USE T0 DISPATCH

incremental_review_state:
  passed_items:
    - item_id: v31x-sentinel-wls-scriptcommandline-interface
      evidence_identity: WLS 24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6 requires exact five-element CommandLine with exact kernel, -script and WLS at positions 1..3, empty ScriptCommandLine, and consumes request/output only at positions 4/5; independent real-kernel absent-request handshake returned rc73 before line-23 Import, line-115 Needs and line-143 ReggeWheelerRadial
    - item_id: v31x-repair1-exact-four-scope
      evidence_identity: only the package-authorized WLS, producer, unit and regression identities changed from their frozen baselines; CLI 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768 and core 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4 remain exact
    - item_id: v31x-repair1-review-authority-noncircular
      evidence_identity: producer 196d082c28798e2207bfeafd6d37282936b3c74c3e75bce233f8469ddd36737f binds exactly this predeclared path and the exact ADVANCE/NOT_ASSESSED/GREEN tokens, nine frozen authority hashes and all six live implementation hashes; it hardcodes no future digest and accepts only the digest supplied by a later valid dispatch
    - item_id: v31x-repair1-adversarial-control-closure
      evidence_identity: 84/84 focused tests include missing/extra/reordered/alternate argv model checks and stale/alternate review, digest/token/hash, environment, argv/cwd/executable/launcher, dispatch replay and root-reuse negatives; all fail closed
    - item_id: v31x-repair1-frozen-adjacent-invariants
      evidence_identity: 49/49 adjacent Cycle-2 tests pass; graphs remain sentinel 35/70/105 and official 161/322/483; method, six overlays, precision, threshold, domain and convention records are unchanged
    - item_id: v31x-repair1-source-and-protected-identities
      evidence_identity: package members/source/protected traversal resolves 30 unique regular nlink1 paths and every hash matches; all seven protected hashes match at review start/end
    - item_id: v31x-repair1-failed-attempt-nonreuse
      evidence_identity: failed root manifest independently rebuilds 76 bound artifacts, root inventory remains 77 files all 0444/nlink1 and nine directories all 0555, failure/manifest identities remain exact, and no additional V3.1-X root or related process exists
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31x-repair1-sentinel-science
      reason: this implementation delta review runs no request import, BHPT source load or solver; the prior sentinel remains terminal FAIL and a future fresh sentinel remains NOT_ASSESSED
    - item_id: v31x-repair1-official-science
      reason: no official dispatch/root is authorized or present
    - item_id: v31x-repair1-thresholds-and-certificates
      reason: the 16 thresholds and five certificates remain frozen but were not evaluated by this zero-science review
    - item_id: v3-2
      reason: V3.2 remains forbidden and was not started

findings:
  - finding_id: v31x-repair1-interface-blocker-closed
    class: NONBLOCKING_LIMITATION
    summary: The sole frozen interface blocker is closed at the zero-science implementation level; numerical sentinel acceptance is deliberately not assessed and requires a separately authorized fresh one-use attempt.
  - finding_id: v31x-repair1-no-science-claim
    class: FOLLOW_UP_DEBT
    summary: A future Root-T0 dispatch may test the repaired interface, but no node, threshold, certificate or official route is claimed to pass by this review.

delta_review:
  reviewed_failed_items:
    - v31x-sentinel-wls-scriptcommandline-interface
  passed_invariants_rechecked:
    - v31x-repair1-exact-four-scope
    - v31x-repair1-commandline-mathematics
    - v31x-repair1-zero-science-handshake-order
    - v31x-repair1-noncircular-authority-chain
    - v31x-repair1-failed-attempt-nonreuse
    - v31x-repair1-science-authority-preservation
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - exact SHA-256/stat recheck of package, four members, package review, terminal review, parent/bridge authorities, current six implementation files, 19 source bindings and seven protected identities
    - independent CPython 3.14 package canonical reload and recursive unique path/hash validation
    - independent failed-root manifest/path/SHA/size/mode/nlink rebuild and V3.1-X root/process inventory
    - PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py
    - PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_cycle2.py
    - /usr/bin/env -i PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel -script /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/scripts/phase6_v3_1_x_bhpt_direct.wls ABSENT_REQUEST ABSENT_OUTPUT
    - in-memory compile of five Python source/test files; .venv/bin/ruff check and format --check; git diff --check on exact four delta paths
  results:
    - package SHA 5b2da4f0168082996e55a8f4ad27869c8c8e6a27cd207c56696f23134501da75 and declared sorted/two-space/terminal-newline canonical serialization PASS
    - package members/source/protected records 30/30 unique identities PASS
    - current repaired four and frozen CLI/core identities 6/6 PASS
    - focused tests 84/84 PASS; adjacent tests 49/49 PASS
    - real WolframKernel SHA 70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c; exact handshake rc=73
    - handshake stdout size 45 SHA b5ad39ecb432487c0b1bae3248ba1a3c8d307bd89077de39aa9bbbc5420792d and exact text `request must exist and output must be absent\n`
    - handshake stderr size 0 SHA e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; request/output remained absent; temporary directory removed
    - WLS static ordering PASS: exact argv guard lines 9-15, absent-request guard lines 17-21, Import line 23, Needs line 115 and ReggeWheelerRadial line 143
    - failed root raw manifest equality PASS; 77 files/9 directories/zero links and immutable permissions PASS
    - in-memory compile 5/5 PASS; Ruff check PASS; Ruff format check PASS; diff-check PASS
    - related live process, science import/call, dispatch creation, root creation and artifact reuse counts are all zero

non_claims:
  - implementation readiness is not V3.1-X sentinel scientific acceptance
  - no missing numerical node is predicted or established to pass
  - no failed dispatch/root byte is reusable and no retry/resume of it is permitted
  - no official V3.1-X dispatch/root or evidence
  - no threshold, domain, convention, precision, method, graph, environment or protected-radial change
  - no finite-radius observer, Li-figure, independent even-sector or broader full-domain claim
  - no V3.2 and no global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 0
  current_bounded_repair: 1
  package_review_consumed_repair: false
  implementation_delta_review_consumes_repair: true
  same_substantive_blocker_remaining: false
  remaining_bounded_repairs_if_future_fresh_attempt_fails: 1
  t0_adjudication_required: false
```

## Bounded authorization

Root T0 may create one different one-use sentinel dispatch and one fresh absent
UTC sentinel root bound to this archive's exact path and SHA-256.  That future
attempt must retain the exact executable, command shape, clean environment,
graph, method, source, precision, threshold, domain, convention and protected
identities reviewed here.

This verdict consumes bounded repair cycle 1.  It does not authorize reuse,
retry or resume of the failed sentinel; an official dispatch/root; V3.2; any
science, threshold, domain, convention, precision, method or protected-source
change; or global GREEN.
