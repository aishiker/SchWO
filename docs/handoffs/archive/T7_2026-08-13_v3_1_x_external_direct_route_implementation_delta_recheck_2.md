# T7 V3.1-X Substage-A implementation delta recheck 2

```yaml
review_id: phase6_t7_v3_1_x_external_direct_route_implementation_delta_recheck_2
gate_id: phase6_v3_1_x_external_direct_route_v1
substage: A_zero_science_implementation_review
attempt: repair_2
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed
reviewed_candidate:
  root: repository exact-six final bounded implementation repair
  identities:
    - path: src/schwgw/validation/phase6_v3_external_direct.py
      sha256: 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4
    - path: src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      sha256: 8f6225ce176be25fe17753f4d64c1e41f6ea9d575887940cd9b040fb79740d51
    - path: scripts/phase6_v3_1_x_external_direct.py
      sha256: 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768
    - path: scripts/phase6_v3_1_x_bhpt_direct.wls
      sha256: 652ced5b32983e79df6c36a5e697c5263aa0570f4cf4b20d58a2b3c20e6e1907
    - path: tests/unit/test_phase6_v3_external_direct.py
      sha256: c986b8f298216651d18accf37b5dd4d8c62995a688305c9060c55b039ff09827
    - path: tests/regression/test_phase6_v3_external_direct_publication.py
      sha256: 46bec0847f81a332427686bc66270988d3aa6f9a21aa5892f881ef0669bdf774

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_x_external_direct_route_science_review.md
    sha256: 339d5d9609e37f263ca3b3c615e5048f4059c80accc03183e02a74df6ffebd7f
  package:
    path: configs/phase6_v3_1_x_external_direct_route_package.json
    sha256: 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752
  delta_recheck_1:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_implementation_delta_recheck_1.md
    sha256: e1dde2575e8ad328062ef360a5146bb02d29d2ea3b462ea5e72d566d4d645285
  blocking_criteria:
    - v31x-a-durable-supervision-and-totality-incomplete
    - v31x-a-dispatch-environment-authority-unbounded
    - v31x-a-serialized-precision-unproven
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

ADVANCE_DECISION: ESCALATE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31x_impl_exact_six_identity_scope
      evidence_identity: exact final six hashes above
    - item_id: v31x_impl_package_authority
      evidence_identity: package 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752
    - item_id: v31x_impl_graph_and_no_selection
      evidence_identity: exact 23 keys; sentinel 35/70/105; official 161/322/483; fixed extrema 3 and 22
    - item_id: v31x_impl_frequency_nodes_overlays
      evidence_identity: exact rational frequency construction, frozen 90/45/45 and 120/60/60 nodes, six overlays
    - item_id: v31x_impl_physics_algebra
      evidence_identity: Wronskian decomposition, signed currents, S and Gamma derivations unchanged
    - item_id: v31x_impl_no_internal_science
      evidence_identity: one NumericalIntegration API call per node; no MST/internal fallback
    - item_id: v31x_impl_protected_and_snapshot_identity
      evidence_identity: protected seven exact; snapshot content d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2 and restored identity a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
    - item_id: v31x_impl_sentinel_admission_false_acceptance
      evidence_identity: repair-1 closure preserved; 35 node budgets and two fixed-extrema ladders remain exact and fail closed
    - item_id: v31x_impl_loaded_source_false_acceptance
      evidence_identity: repair-1 exact eight loaded contexts/files closure preserved
    - item_id: v31x_impl_durable_supervision_false_acceptance
      evidence_identity: stream/Popen/running/timeout paths now publish v2 receipt+terminal; terminate-kill-wait-reap/PG-empty and semantic reload adversaries PASS
    - item_id: v31x_impl_precision_serialization_false_acceptance
      evidence_identity: WLS/Python digit algorithms agree for interior-zero/exponent cases; nonzero exact-value escape removed and adversary rejected
  failed_items:
    - item_id: v31x_impl_dispatch_environment_false_acceptance
      blocker_id: v31x-a-dispatch-environment-authority-unbounded
  partial_allowed_items:
    - item_id: v31x_external_odd_only
      reason: frozen external direct branch is odd RW only; even remains separately frozen Route-B/AP evidence
    - item_id: v31x_snapshot_commit_association
      reason: snapshot has no .git; commit association remains inherited provenance, not independently asserted
  not_assessed_items:
    - item_id: v31x_sentinel_science
      reason: no sentinel dispatch/root or Wolfram execution occurred
    - item_id: v31x_official_science
      reason: requires a valid implementation authority and later sentinel ADVANCE
    - item_id: v31x_v3_2
      reason: forbidden outside this gate

findings:
  - finding_id: v31x_impl_final_review_authority_bound_to_yellow_predecessor
    class: BLOCKING_CURRENT_GATE
    summary: The production dispatch validator remains bound to the repair-1 YELLOW archive, so every future sentinel dispatch is deterministically rejected before root creation or science.
    blocker_id: v31x-a-dispatch-environment-authority-unbounded
    violated_contract_item: one non-circular T0-owned identity-bound one-use dispatch authority must bind the final implementation review carrying exact ADVANCE/NOT_ASSESSED/GREEN tokens and all current implementation hashes
    exact_evidence: src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py lines 97-100 set IMPLEMENTATION_REVIEW_PATH to docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_implementation_delta_recheck_1.md. That immutable file has SHA e1dde2575e8ad328062ef360a5146bb02d29d2ea3b462ea5e72d566d4d645285, mode 0444, ADVANCE_DECISION: REPAIR, and no `ADVANCE_DECISION: ADVANCE` token. validate_dispatch lines 459-474 requires that exact path and token before consumption/root/science. Independent token reconstruction returned production_validate_dispatch_would_accept_review_tokens=false.
    expected_value: production validator accepts exactly one future final identity-bound GREEN delta-review authority and rejects predecessor YELLOW, arbitrary path/digest/token/hash, alternate dispatch/argv/cwd/executable/environment and replay
    observed_value: environment requested-two/observed-four semantics and clean env-i positive now pass, but the only accepted implementation-review path is the predecessor YELLOW authority, making the reviewed positive dispatch path impossible
    bounded_repair: none remains inside this gate because this is repair cycle 2/2; Root T0 must adjudicate by narrowing/freezing the branch or defining a distinct control-plane/algorithm gate rather than authorizing a third isomorphic repair
    allowed_files: []
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -c 'from schwgw.validation import phase6_v3_mode_greybody_external_direct_replacement as r; t=r.IMPLEMENTATION_REVIEW_PATH.read_text(); assert "ADVANCE_DECISION: ADVANCE" in t and all(h in t for h in r.implementation_hashes().values())'
    unblock_condition: only a new T0-adjudicated distinct gate may establish a non-circular final implementation authority whose exact path/digest/tokens/current hashes pass production validate_dispatch while all existing environment/namespace/replay negatives remain rejected

delta_review:
  reviewed_failed_items:
    - v31x_impl_durable_supervision_false_acceptance: CLOSED
    - v31x_impl_dispatch_environment_false_acceptance: OPEN
    - v31x_impl_precision_serialization_false_acceptance: CLOSED
  passed_invariants_rechecked:
    - exact-six scope and final hashes
    - package and delta-recheck-1 authorities
    - sentinel-admission and exact-eight-source repair-1 closures
    - exact key/node/overlay graph and no-selection/no-MST/no-reuse rules
    - physics algebra/no-internal-solver path
    - protected seven and complete external snapshot identities
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - shasum -a 256 <prompt/delta-recheck-1/package/exact-six/T4-evidence paths>
    - env -i PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src PATH=/opt/homebrew/bin:/usr/bin:/bin /opt/homebrew/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py
    - env -i PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src PATH=/opt/homebrew/bin:/usr/bin:/bin /opt/homebrew/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_cycle2.py
    - independent CPython3.14 stream-open lifecycle injection in a fresh private temporary directory
    - exact env-i clean-launch readback against requested and observed maps
    - independent interior-zero and forged exact-nonzero precision adversaries
    - verify_start_gate() package/protected/snapshot/graph reload
    - .venv/bin/ruff check and format --check on five Python candidate paths
    - CPython3.14 in-memory compile of five Python candidate paths
    - git diff --check -- <exact six candidate paths>
    - direct production IMPLEMENTATION_REVIEW_PATH token/hash reconstruction
    - process and V3.1-X root-namespace absence checks
  results:
    - exact prompt/delta-recheck-1/package/exact-six/T4 evidence hashes PASS
    - focused zero-science suite 56 passed in 13.35s
    - adjacent frozen suite 49 passed in 3.45s
    - Ruff check PASS; Ruff format PASS; compile PASS; diff-check PASS
    - stream-open injection published bound receipt/terminal, NOT_OPENED streams, PG-empty and rejected the node
    - clean env-i observed exact frozen four-key map and positive validator PASS; missing/changed/extra negatives PASS
    - interior-zero exponent digit count exact; forged exact-nonzero rejected
    - sentinel budget and exact-eight-source closure tests remain PASS
    - production implementation-review authority token check FAIL: predecessor archive lacks ADVANCE_DECISION: ADVANCE
    - protected seven exact; snapshot identities exact; no related process or V3.1-X root

non_claims:
  - V3.1-X implementation is not ready for sentinel dispatch
  - V3.1-X science remains NOT_ASSESSED
  - no Wolfram or numerical solver was run
  - no dispatch, sentinel root or official root was created
  - V3.1 and V3.1-U remain terminal FAIL/ESCALATE and are not reused
  - no independent even-sector external result is established
  - no pristine-upstream BHPT claim
  - no V3.2
  - no full-domain V3 certification
  - no global GREEN

repair_cycle:
  completed_bounded_repairs: 2
  same_substantive_blocker_remaining: true
  final_bounded_repair_available: false
  t0_adjudication_required: true
```

The lifecycle and precision blockers are closed, and the requested/observed
environment maps themselves are now exact. The remaining production review
authority defect is part of the same frozen dispatch-authority blocker and
makes the one-use sentinel path impossible. Because this is delta review 2,
the liveness protocol prohibits repair cycle 3 and requires Root T0
adjudication. No sentinel dispatch, science, V3.2 or global GREEN is authorized.
