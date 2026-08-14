# T7 control-plane review — V3.1-X sentinel repair-cycle-1 dispatch namespace

Date: 2026-08-13

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL DISPATCH NAMESPACE CONTROL-PLANE REPAIR READY FOR T6
```

This `ADVANCE` authorizes only the bounded T6 control-plane patch specified
below.  It does not authorize creation of a dispatch or root, a Wolfram or
solver launch, sentinel/official science, V3.2, or global GREEN.

## Verdict record

```yaml
review_id: t7_v3_1_x_sentinel_repair_cycle1_dispatch_namespace_control_plane_review_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
attempt: repair_1_control_plane_fast_repair_authority
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed
reviewed_candidate:
  root: pre-execution live control plane
  identities:
    - path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_implementation_delta_review.md
      sha256: 789f13fe1236a4226606bd61e1c7930d6b9de80b7bcc10df27c95995f7a6c6ce
    - path: src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      sha256: 196d082c28798e2207bfeafd6d37282936b3c74c3e75bce233f8469ddd36737f
    - path: docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0001.json
      sha256: 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9

frozen_review_basis:
  review_contract:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  repair_package:
    path: configs/phase6_v3_1_x_sentinel_repair_cycle1_package.json
    sha256: 5b2da4f0168082996e55a8f4ad27869c8c8e6a27cd207c56696f23134501da75
  repair_design:
    path: docs/phase6_v3_1_x_sentinel_repair_cycle1_design.md
    sha256: b576f96063d3245dd1e37940d4c5b7603983cbf2ef912af6550aa6f1c3274970
  implementation_delta_contract:
    path: docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle1_delta_review.md
    sha256: 8e0aa130a66c16b2deb6d335ff1303375f9e96489843a87aacc5d3bd8decd4b4
  accepted_implementation_delta:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_implementation_delta_review.md
    sha256: 789f13fe1236a4226606bd61e1c7930d6b9de80b7bcc10df27c95995f7a6c6ce
    verdict: ADVANCE / NOT_ASSESSED
    gate_label: ACCEPT GREEN / V3.1-X SENTINEL REPAIR CYCLE 1 IMPLEMENTATION READY FOR ONE-USE T0 DISPATCH
  failed_predecessor:
    dispatch_path: docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0001.json
    dispatch_sha256: 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9
    root: runs/phase6/classic_scattering/v3_1_x_external_direct_sentinel_v1_20260813T055002Z_py314
    root_failure_sha256: c002664933d58913b5793ffc1100a5958cb1dfdd12d0c9b3664ffa9ddfb2f541
    root_manifest_sha256: d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772
    immutable_nonresumable_nonretryable_nonreusable: true
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - id: frozen V3.0 threshold contract
      value: 16 unchanged thresholds
      units: mixed per-observable units defined by the frozen source
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  blocking_criteria:
    - the accepted argv/WLS implementation remains frozen and is not reopened
    - exactly one fresh post-repair sentinel dispatch must be publishable by O_EXCL without replacing or reusing attempt_0001
    - the sentinel dispatch authority must accept one predeclared filename only, not an arbitrary date or attempt number
    - the old attempt_0001 path and one-use identity remain permanently rejected and replay-protected
    - the later implementation-review authority remains non-circular: the future delta-review path is fixed now and its digest is supplied only by the later dispatch
    - official attempt_0001 namespace and all science/domain/threshold/method/precision/convention/protected identities remain unchanged
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
GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL DISPATCH NAMESPACE CONTROL-PLANE REPAIR READY FOR T6

incremental_review_state:
  passed_items:
    - item_id: v31x-repair1-wls-argv-interface
      evidence_identity: accepted implementation archive 789f13fe1236a4226606bd61e1c7930d6b9de80b7bcc10df27c95995f7a6c6ce; WLS 24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6 remains frozen
    - item_id: v31x-repair1-science-and-protected-invariants
      evidence_identity: core 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4, CLI 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768, graph/method/precision/domain/threshold/convention and seven protected hashes remain exact
    - item_id: v31x-repair1-failed-attempt-nonreuse
      evidence_identity: attempt_0001 exists as regular 0444/nlink1 SHA 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9 and its terminal root remains the sole V3.1-X sentinel root
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31x-repair1-control-plane-patch
      reason: the bounded three-file patch and its future T7 delta verification have not yet occurred
    - item_id: v31x-repair1-fresh-sentinel-science
      reason: no attempt_0002 dispatch/root exists and no science was launched
    - item_id: v31x-official-v3-2
      reason: official V3.1-X and V3.2 remain forbidden

findings:
  - finding_id: v31x-sentinel-dispatch-namespace-collision
    class: CONTROL_PLANE_REPAIR
    summary: The accepted producer's sentinel filename matcher admits only attempt_0001 while O_EXCL and immutable nonreuse make that same-day path permanently unavailable; this is a dispatch-authority path defect, not a WLS, method or scientific defect.
    exact_evidence: producer 196d082c28798e2207bfeafd6d37282936b3c74c3e75bce233f8469ddd36737f lines 121-127 accepts any YYYY-MM-DD but only sentinel attempt_0001; the exact 2026-08-13 attempt_0001 file already exists as immutable 0444/nlink1 SHA 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9; exact attempt_0002 is absent and rejected by the matcher; no new dispatch/root/process exists
    expected_value: one different O_EXCL-publishable, one-use, predeclared post-repair sentinel dispatch path exists while attempt_0001 remains immutable and forbidden
    observed_value: the sole admitted same-day path is the consumed immutable attempt_0001; changing date would be an unbound escape and attempt_0002 is currently rejected
    bounded_repair: change only the producer's sentinel dispatch and future review authorities plus the two control-plane test files; accept exactly `T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0002.json`, reject every attempt_0001/0000/0003/arbitrary-number, different-date, wrong-parent, alias, suffix and alternate path; retain replay and fresh-root checks; retain the official attempt_0001 namespace unchanged
    allowed_files:
      - src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      - tests/unit/test_phase6_v3_external_direct.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
    forbidden_files:
      - scripts/phase6_v3_1_x_bhpt_direct.wls
      - src/schwgw/validation/phase6_v3_external_direct.py
      - scripts/phase6_v3_1_x_external_direct.py
      - all package, design, prompt, domain, threshold, convention, protected, status and current-handoff paths
    future_review_path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_dispatch_namespace_delta_review.md
    future_review_required_verdict:
      advance_decision: ADVANCE
      claim_status: NOT_ASSESSED
      gate_label: ACCEPT GREEN / V3.1-X SENTINEL ATTEMPT-0002 AUTHORITY READY FOR ONE-USE T0 DISPATCH
    authority_semantics:
      - producer predeclares the future review path above and never hardcodes its future digest
      - later Root-T0 attempt_0002 dispatch supplies the exact future-review SHA and binds all six then-live implementation hashes
      - producer binds this control-plane review, accepted implementation archive 789f13fe1236a4226606bd61e1c7930d6b9de80b7bcc10df27c95995f7a6c6ce, repair package and predecessor failure/dispatch authorities
      - attempt_0001 is rejected as a namespace mismatch before consumption even with a new payload or one-use id; its existing one-use id remains replay-rejected independently
      - exact_root remains a fresh absent alias-free direct child matching the existing sentinel UTC root grammar and may not equal or alias the failed root
      - official dispatch attempt_0001 matcher is byte-for-byte unchanged and does not conflict with the sentinel attempt_0002 filename
    required_zero_science_tests:
      - exact attempt_0002 positive dispatch validation using a surrogate future review, with no dispatch consumption or root creation
      - attempt_0001 old file and fresh-payload variants both reject before consumption
      - attempt_0000, attempt_0003, arbitrary attempt, different date, wrong parent, symlink/alias and suffix variants reject
      - wrong/missing future-review path, SHA, verdict token or any of the six implementation hashes reject
      - one-use replay and existing failed-root reuse reject
      - official attempt_0001 namespace remains accepted by its isolated matcher and no official dispatch is created
      - WLS/core/CLI/science/protected hashes and all previously passed tests remain unchanged
    recheck_command: >-
      PYTHONDONTWRITEBYTECODE=1
      PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src
      /opt/homebrew/bin/python3.14 -m pytest -q
      tests/unit/test_phase6_v3_external_direct.py
      tests/regression/test_phase6_v3_external_direct_publication.py
    unblock_condition: a formal archive-only T7 delta review at the exact predeclared path independently verifies the exact-three scope, exact attempt_0002-only sentinel namespace, attempt_0001/date/number/alias/replay/root-reuse negatives, non-circular future-review binding, unchanged official namespace and all frozen passed/protected identities; only then may Root T0 O_EXCL-publish one attempt_0002 dispatch and launch one fresh sentinel

delta_review:
  reviewed_failed_items: []
  passed_invariants_rechecked:
    - v31x-repair1-wls-argv-interface
    - v31x-repair1-exact-four-scope
    - v31x-repair1-science-authority-preservation
    - v31x-repair1-failed-attempt-nonreuse
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - read-only source inspection of SENTINEL_DISPATCH_PATTERN, OFFICIAL_DISPATCH_PATTERN, validate_dispatch, implementation-review authority and replay scan
    - independent CPython 3.14 matcher evaluation for attempt_0001, attempt_0002, adjacent dates and arbitrary attempt numbers
    - SHA-256/stat/nlink recheck of old dispatch, accepted implementation archive, producer, package/design/prompt, WLS/core/CLI/tests and seven protected sources
    - read-only dispatch/root/process and future-path absence inventory
  results:
    - current matcher accepts old same-day attempt_0001 and also arbitrary-date attempt_0001 names
    - current matcher rejects exact same-day attempt_0002 and attempt_0003
    - old attempt_0001 is regular 0444/nlink1, exact SHA 5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9 and may not be overwritten or reused
    - exact attempt_0002 dispatch path is absent
    - predeclared future T7 delta-review path is absent
    - only the immutable failed V3.1-X sentinel root exists; no new sentinel/official root or related process exists
    - accepted WLS argv implementation and all frozen science/protected identities remain exact
    - causal classification CONTROL_PLANE_REPAIR PASS; no Class-A blocker established

non_claims:
  - this review does not make the current producer mechanically dispatchable
  - no sentinel dispatch/root may be created until the three-file patch and formal T7 delta verification both pass
  - no WLS argv or scientific item is reopened
  - no repair-cycle-2 consumption
  - no sentinel or official scientific result
  - no threshold, domain, convention, precision, method, graph, environment or protected-source change
  - no V3.2 and no global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 0
  current_bounded_repair: 1
  class_c_fast_repair_pending: true
  class_c_fast_repair_consumes_repair_cycle_2: false
  same_substantive_class_a_blocker_remaining: false
  remaining_bounded_repairs_after_control_plane_closure: 1
  t0_adjudication_required: false
```

## Bounded authorization

Root T0 may authorize T6 to change only the producer and the two listed test
files.  The repair must freeze the exact 2026-08-13 sentinel attempt-0002
dispatch path, the exact future T7 delta-review path and the authority rules
above.  T7 must then perform delta-only verification.

Until that future T7 verdict exists, Root T0 must not create a dispatch or
root.  This Class-C fast repair does not consume repair cycle 2, does not
reopen the accepted argv/WLS implementation, and authorizes no Wolfram,
solver, sentinel/official science, V3.2 or global GREEN.
