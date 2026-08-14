# T7 V3.1-U repair-cycle-1 final control-plane delta recheck

Date: 2026-08-12

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 1 IMPLEMENTATION READY FOR ONE-USE T0 DISPATCH
```

This is the sole predeclared immutable implementation-review authority for the
later fixed-path Root-T0 dispatch.  Its SHA-256 is intentionally not
self-recorded: the later dispatch must supply exactly this path and the fresh
SHA-256 of these bytes, and the producer independently rehashes it before any
root creation or science.

```yaml
review_id: t7_v3_1_u_repair_cycle1_control_plane_delta_recheck_20260812
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
attempt: repair_1_control_plane_delta_recheck
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: source-level implementation; no official artifact root exists
  identities:
    - path: src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py
      sha256: a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7
    - path: src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      sha256: 168c8771fbe7cba8983b51d0ae58294169c2e901a75593953a91ad0c401fc146
    - path: tests/unit/test_phase6_v3_hp_unitarity.py
      sha256: e4e3cfb939cb7ccd2f267cbddfe52c4064873cddbc481fd26dc727ec08ea29aa
    - path: tests/regression/test_phase6_v3_hp_unitarity_publication.py
      sha256: acdb1e30f69c2a5972af7394c08d360f8dfef32f3fc5f0a69c7401ca4d5167cc
    - path: scripts/phase6_v3_1_hp_unitarity.py
      sha256: 01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4

frozen_review_basis:
  package:
    path: configs/phase6_v3_1_u_repair_cycle1_package.json
    sha256: 85bff01def7286ebaf1682d5b5498209dfbbc452e098e1d8633e05fcc1b7554c
  package_approval:
    path: docs/handoffs/archive/T7_2026-08-12_v3_1_u_repair_cycle1_package_review.md
    sha256: cfaf87f79cf11a9f6c0f8a73dd3faa3517cd15c105afe999cdfa687c2c5160b4
  implementation_delta_review:
    path: docs/handoffs/archive/T7_2026-08-12_v3_1_u_repair_cycle1_implementation_delta_review.md
    sha256: 4fa316450553d92b01dedbbcbe9fca120fa4c90384aaaf140e42cbf1a47b0fda
  control_plane_delta_review:
    path: docs/handoffs/archive/T7_2026-08-12_v3_1_u_repair_cycle1_control_plane_delta_review.md
    sha256: 1837e9f94a4a379080646fdd2ccebbd2720a2cf4798b3ee9dfce7090bc521d9e
  zero_science_evidence:
    path: /private/tmp/schwo_v31u_final_authority_wiring_preflight.json
    sha256: db5e85c8ffd5f6dfb79920628d7e2d6c3e7bfb438754342886bda60d87a997cd
  frozen_geometry:
    oracle_sha256: a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7
    key_count: 318
    node_count: 954
    node_inventory_sha256: 6fada7a7982918b5c9f9504dc62032c521d85b42897c7e357047209a8b7982f4
    science_solver_calls: 0

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 1 IMPLEMENTATION READY FOR ONE-USE T0 DISPATCH

incremental_review_state:
  passed_items:
    - item_id: v31u_implementation_review_delta_authority_unbound
      evidence_identity: producer accepts only this exact predeclared path; later dispatch must provide exactly path+sha256; producer rehashes these bytes and requires exact ADVANCE/NOT_ASSESSED/GREEN tokens plus all four current implementation hashes
    - item_id: v31u_predecessor_and_alternate_authority_rejection
      evidence_identity: predecessor YELLOW path, mutable live handoff, missing file, wrong digest, wrong token, wrong implementation hash, extra implementation-review field and alternate path all fail closed
    - item_id: v31u_source_end_authority_rehash
      evidence_identity: all 42 cached authority paths are freshly reopened and compared on each ledger construction; mid-run mutation fails closed
    - item_id: v31u_official_root_namespace
      evidence_identity: exact alias-free direct child of classic_scattering, full repair1 UTC basename and timestamp roundtrip required before start gate/root creation/science
    - item_id: v31u_scientific_repair_frozen
      evidence_identity: oracle and 318x3 geometry inventory unchanged; completed_bounded_scientific_repairs=1
    - item_id: v31u_no_execution
      evidence_identity: dispatch absent, official root absent and all science-call counters zero
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_official_science
      reason: this is implementation/control-plane readiness only; no Route-A/U/B/C science, threshold or certificate is assessed
    - item_id: v3_2_and_global_project_state
      reason: outside this gate and unauthorized

findings:
  - finding_id: v31u_implementation_review_delta_authority_unbound
    class: CONTROL_PLANE_REPAIR
    status: CLOSED
    summary: The future implementation-review authority is now one fixed non-circular path whose digest comes only from the later fixed dispatch and whose bytes bind the exact verdict and implementation identities.
  - finding_id: v31u_future_science
    class: FOLLOW_UP_DEBT
    summary: V3.1-U terminal science and all downstream V3.2 work remain separately gated.

delta_review:
  reviewed_failed_items:
    - v31u_implementation_review_delta_authority_unbound
  passed_invariants_rechecked:
    - v31u_source_end_authority_rehash
    - v31u_official_root_namespace
    - v31u_scientific_repair_frozen
    - v31u_exact_implementation_scope
    - v31u_source_and_protected_identity
    - v31u_no_dispatch_no_root_no_science
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - SHA-256/stat/nlink reload of predecessor reviews, package, package approval, zero-science evidence, four current implementation files and frozen CLI
    - exact CPython 3.14 focused pytest on the two frozen test files
    - exact CPython 3.14 CLI preflight under the frozen mpmath overlay while this future authority path was absent
    - Ruff check and format --check plus git diff --check
    - source/dataflow inspection and temporary dispatch adversaries for exact future path/digest/tokens/hashes/schema
    - start/end source/protected identity and dispatch/root/process absence checks
  results:
    - 39 passed in 1.14s
    - CLI preflight PASS with future authority absent; all science calls zero
    - Ruff check PASS; four files already formatted; diff-check PASS
    - geometry remains 318 keys / 954 nodes / 6fada7a7982918b5c9f9504dc62032c521d85b42897c7e357047209a8b7982f4
    - fixed dispatch and official repair root absent

non_claims:
  - V3.1-U science remains NOT_ASSESSED
  - this GREEN authorizes only Root T0 to create one exact fixed-path dispatch for one fresh namespace-valid root
  - the dispatch itself does not establish a scientific PASS
  - no failed-root science reuse, V3.2, full-domain V3, Li-figure equivalence, finite-radius observer claim or global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
  scientific_repair_cycle_2_consumed: false
  control_plane_fast_repair_required: false
```

## Exact authority boundary

The producer does not hardcode this archive's digest.  A later Root-T0
dispatch must bind this exact path and its freshly measured SHA-256, the four
implementation hashes above, the frozen CLI, package/review/source/protected
identities, one namespace-valid absent root and `single_use=true`.  The
producer then rehashes and validates this archive and consumes that dispatch
before the first science call.  No alternate path, predecessor review, live
handoff, runtime argument, environment selector or fallback authority is
accepted.
