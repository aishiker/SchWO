# T7 delta verification — V3.1-X sentinel attempt-0002 authority

Date: 2026-08-13

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL ATTEMPT-0002 AUTHORITY READY FOR ONE-USE T0 DISPATCH
```

## Verdict record

```yaml
review_id: t7_v3_1_x_sentinel_attempt_0002_namespace_delta_review_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
attempt: repair_1_control_plane_delta_verification
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed
reviewed_candidate:
  root: repository exact-three control-plane delta
  identities:
    - path: src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      before_sha256: 196d082c28798e2207bfeafd6d37282936b3c74c3e75bce233f8469ddd36737f
      sha256: 81a33a4157d6e07b03621bff069c9383914464c16ce4314a9f7a556c7e1cd088
    - path: tests/unit/test_phase6_v3_external_direct.py
      before_sha256: 72209b0cc295df1882cb8fab5b642726095a295baaca1218061ac8e6ef1a6b0a
      sha256: 056c7273edbdb612d3fc99c4b493f2fe4c96dc15b8ae7aa3a872587f33f3aaba
    - path: tests/regression/test_phase6_v3_external_direct_publication.py
      before_sha256: 847819dcdff4df3244c4a44e9c60f05149b332dc0492399447d0f2562c9c13db
      sha256: 24d26a8a9c2e0ad573b97f76b39db7743f2d6639cd57978be93f0c310062f858
  frozen_live_six:
    - path: scripts/phase6_v3_1_x_bhpt_direct.wls
      sha256: 24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6
    - path: scripts/phase6_v3_1_x_external_direct.py
      sha256: 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768
    - path: src/schwgw/validation/phase6_v3_external_direct.py
      sha256: 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4
    - path: src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      sha256: 81a33a4157d6e07b03621bff069c9383914464c16ce4314a9f7a556c7e1cd088
    - path: tests/unit/test_phase6_v3_external_direct.py
      sha256: 056c7273edbdb612d3fc99c4b493f2fe4c96dc15b8ae7aa3a872587f33f3aaba
    - path: tests/regression/test_phase6_v3_external_direct_publication.py
      sha256: 24d26a8a9c2e0ad573b97f76b39db7743f2d6639cd57978be93f0c310062f858

frozen_review_basis:
  review_contract:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  control_plane_authority:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_dispatch_namespace_control_plane_review.md
    sha256: 72c8b1aeb26103b7d9786ba79d57553afa975f65f2d6832c6a8590add35d8edd
  accepted_implementation_delta:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_implementation_delta_review.md
    sha256: 789f13fe1236a4226606bd61e1c7930d6b9de80b7bcc10df27c95995f7a6c6ce
  repair_package:
    path: configs/phase6_v3_1_x_sentinel_repair_cycle1_package.json
    sha256: 5b2da4f0168082996e55a8f4ad27869c8c8e6a27cd207c56696f23134501da75
  formal_terminal_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_sentinel_terminal_review.md
    sha256: cf4ba0a25527f0298bf3f18ba03a19b4a849a592db30bc610c2bb0749015d772
  consumed_predecessor:
    dispatch_path: docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0001.json
    dispatch_sha256: 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9
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
  blocking_criteria:
    - change exactly producer, unit test and regression test; WLS/core/CLI and science bytes remain frozen
    - accept sentinel dispatch basename exactly `T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0002.json`
    - require an absolute, alias-free, non-symlink dispatch path whose direct parent is the exact archive directory
    - reject attempt_0001, 0000, 0003, arbitrary attempts, wrong date, wrong parent, suffix, final symlink and parent alias before consumption
    - retain old attempt_0001 permanent nonreuse and independent one-use replay rejection
    - retain official attempt_0001 matcher and validation behavior unchanged
    - bind this singular predeclared T7 archive path; its digest is supplied only by a later Root-T0 dispatch and is not hardcoded
    - require this archive to contain the exact verdict, seven predecessor authority hashes and all six current implementation hashes
    - preserve root freshness, environment, argv/cwd/executable/launcher, method, graph, precision, domain, threshold, convention, source and protected guards
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
GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL ATTEMPT-0002 AUTHORITY READY FOR ONE-USE T0 DISPATCH

incremental_review_state:
  passed_items:
    - item_id: v31x-attempt0002-exact-three-scope
      evidence_identity: producer 196d082c28798e2207bfeafd6d37282936b3c74c3e75bce233f8469ddd36737f -> 81a33a4157d6e07b03621bff069c9383914464c16ce4314a9f7a556c7e1cd088; unit 72209b0cc295df1882cb8fab5b642726095a295baaca1218061ac8e6ef1a6b0a -> 056c7273edbdb612d3fc99c4b493f2fe4c96dc15b8ae7aa3a872587f33f3aaba; regression 847819dcdff4df3244c4a44e9c60f05149b332dc0492399447d0f2562c9c13db -> 24d26a8a9c2e0ad573b97f76b39db7743f2d6639cd57978be93f0c310062f858; WLS/core/CLI hashes remain exact
    - item_id: v31x-attempt0002-namespace-closed
      evidence_identity: exact sentinel regex accepts only the frozen 2026-08-13 attempt_0002 basename; validate_dispatch additionally requires absolute/no-final-symlink/no-parent-alias resolution and exact archive parent before payload/review processing
    - item_id: v31x-attempt0002-negative-grammar-closed
      evidence_identity: fresh attempt_0001, 0000, 0003, 0042, adjacent dates, suffix, prefixed alias, wrong parent, final symlink and parent-directory alias adversaries all fail with zero consumption/root creation
    - item_id: v31x-attempt0002-review-authority-noncircular
      evidence_identity: producer binds exactly this archive path and exact ADVANCE/NOT_ASSESSED/GREEN tokens plus authorities 72c8b1aeb26103b7d9786ba79d57553afa975f65f2d6832c6a8590add35d8edd, 789f13fe1236a4226606bd61e1c7930d6b9de80b7bcc10df27c95995f7a6c6ce, 5b2da4f0168082996e55a8f4ad27869c8c8e6a27cd207c56696f23134501da75, cf4ba0a25527f0298bf3f18ba03a19b4a849a592db30bc610c2bb0749015d772, 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9, c002664933d58913b5793ffc1100a5958cb1dfdd12d0c9b3664ffa9ddfb2f541 and d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772; no future digest is embedded and the later dispatch must supply it
    - item_id: v31x-attempt0002-six-live-hash-binding
      evidence_identity: producer requires every live implementation hash and the regression adversary removes each of the six in turn; all six omissions fail closed
    - item_id: v31x-attempt0002-old-attempt-nonreuse
      evidence_identity: old attempt_0001 remains regular 0444/nlink1 SHA 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9 and is rejected by the sentinel namespace before payload/review; failed root manifest independently rebuilds 76 bound artifacts and root reuse remains rejected
    - item_id: v31x-attempt0002-official-namespace-preserved
      evidence_identity: official regex remains `T0_\d{4}-\d{2}-\d{2}_v3_1_x_external_direct_official_dispatch_attempt_0001\.json`; sentinel-only unresolved-path check is guarded by stage==sentinel and adjacent 49/49 tests pass
    - item_id: v31x-attempt0002-science-and-protected-preserved
      evidence_identity: WLS 24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6, core 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4, CLI 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768, graph/method/precision/domain/threshold/convention and all seven protected hashes remain exact
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31x-attempt0002-sentinel-science
      reason: this Class-C delta review creates no dispatch/root and invokes no Wolfram, BHPT source or solver; fresh sentinel science remains NOT_ASSESSED
    - item_id: v31x-official-science
      reason: no official dispatch/root is authorized or present
    - item_id: v31x-thresholds-and-certificates
      reason: the frozen 16 thresholds and five certificates are not evaluated by this control-plane review
    - item_id: v3-2
      reason: V3.2 remains forbidden and was not started

findings:
  - finding_id: v31x-sentinel-dispatch-namespace-collision
    class: CONTROL_PLANE_REPAIR
    summary: CLOSED — the singular attempt_0002 namespace, alias-safe path grammar, non-circular review authority and permanent attempt_0001 rejection satisfy every frozen Class-C unblock condition without changing science.
  - finding_id: v31x-attempt0002-science-not-assessed
    class: NONBLOCKING_LIMITATION
    summary: This GREEN establishes only one-use dispatch authority; it predicts no numerical sentinel outcome.
  - finding_id: v31x-official-v3-2-global-green-forbidden
    class: FOLLOW_UP_DEBT
    summary: Official V3.1-X, V3.2 and any broader scientific claim remain outside this gate.

delta_review:
  reviewed_failed_items:
    - v31x-sentinel-dispatch-namespace-collision
  passed_invariants_rechecked:
    - v31x-repair1-wls-argv-interface
    - v31x-repair1-science-and-protected-invariants
    - v31x-repair1-failed-attempt-nonreuse
    - v31x-repair1-review-authority-noncircular
    - v31x-repair1-adversarial-control-closure
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - exact SHA-256 recheck of the three delta files, frozen WLS/core/CLI, package, predecessor reviews, old dispatch/failure/manifest and seven protected sources
    - independent CPython 3.14 package declared-canonical reload and 30/30 recursive member/source/protected path/hash/nlink verification
    - independent CPython 3.14 matcher matrix for exact attempt_0002 and eight invalid basename/date/attempt/suffix forms
    - independent static/dataflow inspection of sentinel absolute/no-symlink/no-parent-alias/direct-parent gate, future review authority, six-hash binding, replay scan and official stage isolation
    - PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py
    - PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_cycle2.py
    - in-memory compile of exact three Python files; .venv/bin/ruff check and format --check; exact-three git diff --check
    - read-only future-review/attempt_0002/official-root/process inventory
  results:
    - exact-three terminal hashes 3/3 PASS
    - live implementation hashes 6/6 PASS
    - package declared canonical serialization PASS; recursive bound identities 30/30 PASS
    - exact attempt_0002 positive basename 1/1 PASS; invalid basename/date/attempt/suffix matrix 8/8 rejected
    - wrong parent, final symlink and parent alias adversaries rejected before consumption
    - old immutable attempt_0001 and fresh attempt_0001 variants rejected; replay and failed-root reuse rejected
    - missing/wrong review path, digest, verdict token, predecessor authority and each of six implementation hashes rejected
    - exact future review surrogate validates without dispatch consumption or root creation
    - official attempt_0001 matcher identity/behavior preserved
    - focused tests 103/103 PASS; adjacent tests 49/49 PASS
    - in-memory compile 3/3 PASS; Ruff check PASS; Ruff format check PASS; diff-check PASS
    - future archive was absent at review start; exact attempt_0002 dispatch/root and official dispatch/root were absent
    - old failure root manifest equality PASS with 76 bound artifacts; old dispatch/failure/manifest identities unchanged
    - related process, Wolfram launch, BHPT/source load, solver/science call, dispatch creation and root creation counts are all zero

non_claims:
  - this authority does not constitute V3.1-X sentinel scientific acceptance
  - no numerical node, threshold or certificate is predicted or established to pass
  - no reuse, retry, resume, overwrite or reinterpretation of attempt_0001 or its failed root
  - no arbitrary attempt number or alternate date/path is authorized
  - no official V3.1-X dispatch/root or evidence
  - no WLS argv, method, graph, precision, threshold, domain, convention, environment, source or protected-radial change
  - no finite-radius observer, Li-figure, independent even-sector or full-domain claim
  - no V3.2 and no global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 0
  class_c_fast_repair_closed: true
  class_c_fast_repair_consumed_repair_cycle_2: false
  same_substantive_class_a_blocker_remaining: false
  remaining_bounded_repairs_if_fresh_sentinel_fails: 1
  t0_adjudication_required: false
```

## Bounded authorization

Root T0 may O_EXCL-publish exactly one dispatch at
`docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0002.json`
and launch exactly one fresh absent UTC sentinel root under the already frozen
implementation, invocation, environment, graph, method, source, precision,
threshold, domain, convention and protected identities.  The dispatch must
bind this archive's exact path and later-computed SHA-256 plus all six live
implementation hashes.

This Class-C closure does not consume science repair cycle 2.  It authorizes
no attempt_0001 reuse, arbitrary dispatch name, official run, V3.2, science
change or global GREEN.
