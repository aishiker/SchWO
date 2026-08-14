# T7 V3.1-U repair-cycle-1 control-plane delta review

Date: 2026-08-12

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-U IMPLEMENTATION-REVIEW AUTHORITY BINDING CORRECTION REQUIRED BEFORE ONE-USE T0 DISPATCH
```

This is a delta-only review of the two `CONTROL_PLANE_REPAIR` findings in the
immutable predecessor review
`docs/handoffs/archive/T7_2026-08-12_v3_1_u_repair_cycle1_implementation_delta_review.md`,
SHA-256
`4fa316450553d92b01dedbbcbe9fca120fa4c90384aaaf140e42cbf1a47b0fda`.
The frozen geometry/science repair was not reopened.

```yaml
review_id: t7_v3_1_u_repair_cycle1_control_plane_delta_review_20260812
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
attempt: repair_1_control_plane_delta
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: source-level control-plane fast repair; no official artifact root exists
  identities:
    - path: src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py
      sha256: a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7
    - path: src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      before_sha256: 8e531990de3578814ce93352e8f9cca09d33678de1eda2b43e2bafec63c35972
      sha256: 74d9b2761e41d34cf45f7e126c0cf939832fe5d9ddfbb9b31cd5b2bc94bb8f2b
    - path: tests/unit/test_phase6_v3_hp_unitarity.py
      before_sha256: a4bf93fc810eaada36d7b408f23b33a4dfaf83a9a1e3c83137e682ed18fafd6e
      sha256: e46c7adc94f1a82a794eb035a14e7cb0681f0ee1e9f77149617d5755b4697862
    - path: tests/regression/test_phase6_v3_hp_unitarity_publication.py
      before_sha256: 03558aafa3a7f749062104889c184070cc5374cdb4fb0397bea525ea7674e31b
      sha256: 72b8fdb1e65331ae10f189298573a4aaa426ca3286eeb9f8471c748ab4b1369f
    - path: scripts/phase6_v3_1_hp_unitarity.py
      sha256: 01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4

frozen_review_basis:
  predecessor_review:
    path: docs/handoffs/archive/T7_2026-08-12_v3_1_u_repair_cycle1_implementation_delta_review.md
    sha256: 4fa316450553d92b01dedbbcbe9fca120fa4c90384aaaf140e42cbf1a47b0fda
  package:
    path: configs/phase6_v3_1_u_repair_cycle1_package.json
    sha256: 85bff01def7286ebaf1682d5b5498209dfbbc452e098e1d8633e05fcc1b7554c
  package_approval:
    path: docs/handoffs/archive/T7_2026-08-12_v3_1_u_repair_cycle1_package_review.md
    sha256: cfaf87f79cf11a9f6c0f8a73dd3faa3517cd15c105afe999cdfa687c2c5160b4
  zero_science_evidence:
    path: /private/tmp/schwo_v31u_control_plane_fast_repair_preflight.json
    sha256: 01e9948a5151df4caa91ec07608dc03c2085c7a5f6f17f057ebf39c4fc00d11f
  frozen_geometry:
    key_count: 318
    node_count: 954
    inventory_sha256: 6fada7a7982918b5c9f9504dc62032c521d85b42897c7e357047209a8b7982f4
    science_solver_calls: 0
  protected_identities:
    - all 21 package source bindings rehashed exact at delta-review start/end
    - all seven protected radial identities rehashed exact at delta-review start/end

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-U IMPLEMENTATION-REVIEW AUTHORITY BINDING CORRECTION REQUIRED BEFORE ONE-USE T0 DISPATCH

incremental_review_state:
  passed_items:
    - item_id: v31u_source_end_authority_rehash_gap
      evidence_identity: build_source_ledger independently reopens and compares all 42 cached authority paths on every call; an unchanged cached start_gate plus a mutated temporary authority raises V31ContractError
    - item_id: v31u_dispatch_official_namespace_gap
      evidence_identity: alias-free absolute direct-child path, exact classic_scattering parent, full repair1 basename, UTC timestamp parse and roundtrip are enforced before start gate/root creation/science; canonical positive and wrong-parent/name/timestamp/alias negatives PASS
    - item_id: v31u_exact_three_path_control_plane_scope
      evidence_identity: producer/unit/regression changed only to exact hashes above; oracle and CLI remain frozen; source/protected hashes remain exact
    - item_id: v31u_geometry_science_repair_frozen
      evidence_identity: oracle a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7 and 318x3 inventory 6fada7a7982918b5c9f9504dc62032c521d85b42897c7e357047209a8b7982f4 unchanged; completed_bounded_scientific_repairs=1
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_official_science
      reason: no dispatch, official root or numerical science exists
    - item_id: v31u_thresholds_certificates_and_v3_2
      reason: outside this control-plane delta and unauthorized

findings:
  - finding_id: v31u_source_end_authority_rehash_closed
    class: CONTROL_PLANE_REPAIR
    status: CLOSED
    summary: All cached authority identities are now freshly reopened and compared at each source-ledger construction.
  - finding_id: v31u_dispatch_official_namespace_closed
    class: CONTROL_PLANE_REPAIR
    status: CLOSED
    summary: Official target validation is alias-free, exact-parent, exact-pattern and canonical UTC before any publication or science.
  - finding_id: v31u_implementation_review_delta_authority_unbound
    class: CONTROL_PLANE_REPAIR
    status: OPEN
    summary: The producer still fixes IMPLEMENTATION_REVIEW_PATH to the immutable predecessor YELLOW review rather than this later delta authority, so the required exact GREEN token cannot be validated without impermissibly rewriting the predecessor archive.
    exact_evidence: src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py defines IMPLEMENTATION_REVIEW_PATH as docs/handoffs/archive/T7_2026-08-12_v3_1_u_repair_cycle1_implementation_delta_review.md and _validate_dispatch requires every IMPLEMENTATION_REVIEW_TOKENS string in that file. Direct search of immutable predecessor SHA 4fa316450553d92b01dedbbcbe9fca120fa4c90384aaaf140e42cbf1a47b0fda finds no exact `ACCEPT GREEN / V3.1-U REPAIR CYCLE 1 IMPLEMENTATION READY FOR ONE-USE T0 DISPATCH` token. A newly created delta archive is not an accepted implementation-review path.
    bounded_control_plane_repair: Freeze one immutable post-delta authority path and exact SHA/token binding in the producer and dispatch contract, without rewriting the predecessor archive or adding environment/argv/fallback authority selection. Update only the producer and focused authority tests; rehash all cached authorities at start/end and retain the official-root namespace checks.
    allowed_files:
      - src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      - tests/unit/test_phase6_v3_hp_unitarity.py
      - tests/regression/test_phase6_v3_hp_unitarity_publication.py
    unblock_condition: A future fixed immutable authority path containing the exact ADVANCE/NOT_ASSESSED/GREEN tokens and all four current implementation hashes is the sole path accepted by _validate_dispatch; the predecessor YELLOW archive remains byte-identical; missing/wrong/alternate/live authority paths fail before root creation/science; all 34 tests and existing identity guards pass.

delta_review:
  reviewed_failed_items:
    - v31u_source_end_authority_rehash_gap
    - v31u_dispatch_official_namespace_gap
  passed_invariants_rechecked:
    - v31u_geometry_science_repair_frozen
    - v31u_exact_three_path_control_plane_scope
    - v31u_source_and_protected_identity
    - v31u_no_dispatch_no_root_no_science
  protected_identities_match: true
  unrelated_passed_items_reopened: false
  newly_observed_control_plane_dependency: v31u_implementation_review_delta_authority_unbound

hold_details: null

verification:
  commands:
    - exact SHA-256/stat/nlink reload of predecessor review, package, package review, T4 evidence, four current implementation files and frozen CLI
    - exact CPython 3.14 focused pytest on the two frozen files
    - exact CPython 3.14 CLI preflight under the frozen mpmath overlay
    - Ruff check and format --check plus git diff --check
    - independent TemporaryDirectory authority-mutation and canonical/wrong-parent/wrong-name/wrong-timestamp/alias probes
    - read-only instrumented build_source_ledger call-count/identity probe
    - start/end rehash of all 21 source bindings, seven protected paths and coordination records
  results:
    - 34 passed in 1.08s
    - CLI preflight PASS; science calls all zero
    - Ruff check PASS; four files already formatted; diff-check PASS
    - cached authority paths 42, freshly rehashed 42; ledger entries 46
    - independent control-plane adversaries PASS
    - status/T0_current/T7_current remain 15d29b641b66b061c8865edb72eb811519360bda6a314515fd115cbe1ab96158 / f80779de4990d6d18581d8ee4bccef1393f3a61b6fdb7cdbced272a357ac0ffa / c41a9a26146d16e1ab3c8c1bf69ea9e4f52cd3d3e853eaa783263cedd7e90e65
    - fixed dispatch and official repair root absent

non_claims:
  - V3.1-U science remains NOT_ASSESSED
  - no one-use dispatch is authorized by this YELLOW delta record
  - no failed-root science reuse, V3.2, full-domain V3 or global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
  scientific_repair_cycle_2_consumed: false
  control_plane_fast_repair_required: true
```

## Decision boundary

The two requested control-plane defects are closed and the frozen scientific
repair is unchanged.  Nevertheless, the exact producer dataflow cannot use a
new durable delta decision as its implementation-review authority: it accepts
only the prior immutable YELLOW archive and requires the exact GREEN token in
that same file.  Rewriting that predecessor would destroy the identity-bound
review history.  Therefore the bounded GREEN label is not emitted and Root T0
must not create the one-use dispatch.  One further class-C-only authority-path
correction and delta verification are sufficient; no science or scientific
repair cycle is implicated.
