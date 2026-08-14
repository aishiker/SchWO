# T7 V3.1-X external direct-route package review

```yaml
review_id: t7_v3_1_x_external_direct_route_package_review_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
attempt: initial
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed
reviewed_candidate:
  root: configs/phase6_v3_1_x_external_direct_route_package.json
  identities:
    - path: configs/phase6_v3_1_x_external_direct_route_package.json
      sha256: 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752
    - path: docs/phase6_v3_1_x_external_route_redesign_analysis.md
      sha256: b937011e9ee932cbe41aa58d2fbd3cb849e503c083d09570ce281c3f15331661
    - path: docs/handoffs/archive/T4_2026-08-13_v3_1_x_external_route_redesign_analysis.md
      sha256: 0cec21f4e279199f69cef7b8b5df68ec8347a2cf2f066543b7188c12f1d581e7
    - path: docs/phase6_v3_1_x_external_direct_route_design.md
      sha256: 9a75c6f80cd8360438d395caf887a13b8c88e97faef94139c6ed4dfeba4fdb8d
    - path: docs/prompts/phase6_t4_v3_1_x_external_direct_route.md
      sha256: 3c65164bcad33e7f86e993c2ec9536643cc5f2ec5c179020c923902e8caf4c4f
    - path: docs/prompts/phase6_t7_v3_1_x_external_direct_route_package_review.md
      sha256: 7faaab2183328b83dc5c85c82bfb5c6695ca5d028fdab7180538afa7c2c3ce5b
    - path: docs/prompts/phase6_t7_v3_1_x_external_direct_route_science_review.md
      sha256: 339d5d9609e37f263ca3b3c615e5048f4059c80accc03183e02a74df6ffebd7f

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_x_external_direct_route_package_review.md
    sha256: 7faaab2183328b83dc5c85c82bfb5c6695ca5d028fdab7180538afa7c2c3ce5b
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - id: V3.1-frozen-threshold-set
      value: 16 unchanged blocking thresholds
      units: mixed, exactly as frozen per field
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  blocking_criteria:
    - exact_23_key_order_and_totality
    - direct_numericalintegration_only_no_mst_fallback_or_prior_value_reuse
    - exact_rational_frequency_and_frozen_90_120_digit_ladder
    - equation_boundary_wronskian_current_and_v3_f02_correctness
    - exact_six_reviewed_odd_sector_overlay_hashes
    - official_23_161_322_483_and_sentinel_35_70_105_graphs
    - unchanged_16_thresholds_and_five_certificates
    - one_use_nonretry_source_closed_publication
    - exact_six_new_path_implementation_scope_and_executable_future_authority
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

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X EXTERNAL DIRECT-ROUTE PACKAGE READY FOR T4

incremental_review_state:
  passed_items:
    - item_id: v31x_liveness_lineage
      evidence_identity: V3.1-U repairs=2 exhausted; immutable failed sentinel; V3.1-X distinct gate; completed_bounded_repairs=0
    - item_id: v31x_exact_23_key_domain
      evidence_identity: V3A-MODE-BHPT-RW-001 canonical anchor SHA256 5e93fca57b6d4fb82762043fedea4631de92111164c8c4a991d76925e3867c76; canonical JSONL SHA256 fae654a7cd1ef8b99f06422bd2a4ca203c5a5ce5de7d9039c5d339fa818046
    - item_id: v31x_direct_method_no_selection
      evidence_identity: one predeclared odd RW NumericalIntegration In/Up method for all 23 keys; MST/fallback/prior reuse counts all zero
    - item_id: v31x_physics_algebra
      evidence_identity: source-bound RW equation, e^-iomega t convention, In/Up normalization, Wronskian decomposition, S=(-1)^(ell+1)Aout/Ain, signed currents and direct Gamma_flux independently rederived
    - item_id: v31x_frequency_and_precision_ladder
      evidence_identity: exact rational frequencies; P0=90/45/45 and P1/boundary=120/60/60; selected P1; unknown (2,18) cause remains unclaimed
    - item_id: v31x_overlay_identity
      evidence_identity: six odd-first-occurrence-only transformed hashes independently reproduced exactly
    - item_id: v31x_exact_graphs
      evidence_identity: official 23/161/322/483; sentinel 23 anchors plus fixed extrema at ordinals 3 and 22 = 35/70/105
    - item_id: v31x_threshold_certificate_budget_freeze
      evidence_identity: 16 unchanged V3.1 thresholds; five unchanged certificate IDs; numerical and convention budgets remain separate
    - item_id: v31x_publication_dispatch_resource_protocol
      evidence_identity: source-closed sentinel-before-official, distinct one-use dispatches, no retry, immutable terminal success/failure roots
    - item_id: v31x_scope_and_future_executability
      evidence_identity: exactly six currently absent new implementation/test paths; future T4/T7 prompts fix authority and require separate implementation review before sentinel
    - item_id: v31x_package_and_source_identity
      evidence_identity: canonical package; 13/13 unique recursive path bindings exact; six members 0444/nlink1; external snapshot 25 files/five dirs and protected 7/7 exact
    - item_id: v31x_bounded_direct_feasibility
      evidence_identity: immutable 30-key bounded direct evidence manifest e12c49b00efecc9c65d42699f2a5052ecac1fe2c988312ed21c4da085fe5ee6 verifies callable independent In/Up direct route without serving as V3.1-X acceptance evidence
  failed_items: []
  partial_allowed_items:
    - item_id: v31x_odd_only_external_claim
      reason: package explicitly excludes independent even-sector external evidence; this is a frozen nonclaim and does not block odd Route C package readiness
    - item_id: v31x_snapshot_commit_association
      reason: restored snapshot has no .git; association with upstream commit is inherited provenance only and is explicitly not independently asserted
  not_assessed_items:
    - item_id: v31x_implementation
      reason: the exact six implementation paths do not yet exist and implementation review is a later gate
    - item_id: v31x_sentinel_science
      reason: no dispatch/root exists and no sentinel science was authorized or run
    - item_id: v31x_official_science
      reason: official V3.1-X science requires later sentinel ADVANCE and separate one-use dispatch
    - item_id: v32_or_global_status
      reason: outside this gate; no V3.2 or global GREEN is authorized

findings:
  - finding_id: v31x_snapshot_commit_inherited_only
    class: NONBLOCKING_LIMITATION
    summary: The source snapshot is byte- and inventory-bound but its upstream commit association is inherited because the restored snapshot intentionally contains no .git metadata.
  - finding_id: v31x_runtime_resource_outcome_unassessed
    class: NONBLOCKING_LIMITATION
    summary: Direct-route runtime and resource success across the exact sentinel and official graphs remains future empirical evidence and cannot be inferred from package readiness or the bounded 30-key feasibility root.

delta_review:
  reviewed_failed_items: []
  passed_invariants_rechecked:
    - package_and_member_identities
    - v3_authorities_and_protected_sources
    - failed_sentinel_immutability_and_nonreuse
    - external_snapshot_identity
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - shasum -a 256 docs/prompts/phase6_t7_v3_1_x_external_direct_route_package_review.md configs/phase6_v3_1_x_external_direct_route_package.json docs/phase6_v3_1_x_external_direct_route_design.md
    - python3 independent package/path/hash/mode/nlink/canonical/source-snapshot/protected-identity reconstruction
    - python3 independent 23-key derivation, canonical anchor/JSONL hash, graph and threshold/certificate reconstruction
    - python3 independent odd-sector overlay first-occurrence transformation and six SHA-256 reconstruction
    - python3 independent failed-sentinel inventory/outcome/process reconstruction
    - python3 independent bounded-direct manifest/result/source inspection
    - ps -axo pid=,command=
    - git diff --check -- configs/phase6_v3_1_x_external_direct_route_package.json docs/phase6_v3_1_x_external_direct_route_design.md docs/prompts/phase6_t7_v3_1_x_external_direct_route_package_review.md
  results:
    - prompt/package/design SHA-256 exact at start and end
    - package canonical JSON PASS; 13/13 recursive unique bindings PASS
    - six package members regular 0444/nlink1 and exact
    - exact 23-key V3-derived order PASS; observed 14-key success subset rejected
    - equation/boundary/Wronskian/V3-F02/current/Gamma separation PASS
    - six overlay hashes PASS
    - official and sentinel graph arithmetic PASS
    - 16 thresholds and five certificate IDs unchanged
    - external snapshot content and restored-identity indexes PASS
    - seven protected radial identities PASS at start/end
    - exact six implementation paths absent; no V3.1-X root or related process
    - git diff-check PASS

non_claims:
  - V3.1 and V3.1-U remain FAIL
  - V3.1-X science remains NOT_ASSESSED
  - package GREEN is readiness only
  - no independent even-sector external evidence
  - no pristine-upstream BHPT claim
  - no accepted reuse of failed V3.1/V3.1-U/sentinel science
  - no V3.2 before an official V3.1-X ADVANCE
  - no Li-figure equivalence
  - no finite-radius observer claim
  - no full-domain V3 certification
  - no global GREEN

repair_cycle:
  completed_bounded_repairs: 0
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

The six allowed future paths are exactly:

1. `scripts/phase6_v3_1_x_bhpt_direct.wls`
2. `src/schwgw/validation/phase6_v3_external_direct.py`
3. `src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py`
4. `scripts/phase6_v3_1_x_external_direct.py`
5. `tests/unit/test_phase6_v3_external_direct.py`
6. `tests/regression/test_phase6_v3_external_direct_publication.py`

This review authorizes Root T0 to dispatch only the frozen zero-science T4
implementation package. It does not authorize a sentinel dispatch, Wolfram or
Python science, an official V3.1-X root, V3.2, or global GREEN.
