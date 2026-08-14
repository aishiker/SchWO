# T7 V3.1-U repair-cycle-1 implementation delta review

Date: 2026-08-12

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-U REPAIR CYCLE 1 CONTROL-PLANE CHANGES REQUIRED BEFORE ONE-USE T0 DISPATCH
```

The bounded scientific repair item is closed.  There is no remaining class-A
scientific blocker and bounded scientific repair cycle 1 is consumed.  Two
independently demonstrated class-C defects remain in the producer's authority
enforcement.  Under sections 2, 7 and 9 of the review-gate liveness protocol,
they do not reopen science and do not set `ADVANCE_DECISION: REPAIR`, but Root
T0 must withhold the mechanical one-use dispatch because the prompt-required
bounded GREEN label is absent.  Only the control-plane fast repair and a
delta-only T7 verification are permitted next.

```yaml
review_id: t7_v3_1_u_repair_cycle1_implementation_delta_review_20260812
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
attempt: repair_1
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: source-level repair-cycle-1 implementation; no official artifact root exists
  identities:
    - path: src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py
      before_sha256: 84fe4c299b46042b841a09d92ab7e38af73cfd12428513753e20c8b4b40b3e39
      sha256: a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7
    - path: src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      before_sha256: 81f5ca43480976975fa185ce24ff3f47b83c755dc8b74892b97a93798a914e51
      sha256: 8e531990de3578814ce93352e8f9cca09d33678de1eda2b43e2bafec63c35972
    - path: tests/unit/test_phase6_v3_hp_unitarity.py
      before_sha256: 1a0d1eea3e4d4047b1b8f84b02feb4dade8c3c40c8ba84dbf772b50b96774512
      sha256: a4bf93fc810eaada36d7b408f23b33a4dfaf83a9a1e3c83137e682ed18fafd6e
    - path: tests/regression/test_phase6_v3_hp_unitarity_publication.py
      before_sha256: 5c33f18a4e327f18a7b8e5cdedc02f7ab8fb777e7bc8add645d55c27e93aa007
      sha256: 03558aafa3a7f749062104889c184070cc5374cdb4fb0397bea525ea7674e31b
    - path: scripts/phase6_v3_1_hp_unitarity.py
      sha256: 01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_u_repair_cycle1_delta_review.md
    sha256: c2be5b0b965868e62225252d1d8eb89444d8b5375d5947139b5829fd7564bd4e
  package:
    path: configs/phase6_v3_1_u_repair_cycle1_package.json
    sha256: 85bff01def7286ebaf1682d5b5498209dfbbc452e098e1d8633e05fcc1b7554c
  package_approval:
    path: docs/handoffs/archive/T7_2026-08-12_v3_1_u_repair_cycle1_package_review.md
    sha256: cfaf87f79cf11a9f6c0f8a73dd3faa3517cd15c105afe999cdfa687c2c5160b4
  t4_zero_science_evidence:
    path: /private/tmp/schwo_v31u_repair_cycle1_implementation_preflight.json
    sha256: 0cdf815aad513c900a26ee6cf4be15954c7a96f4f671551114c2b6b28be73084
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - id: V3.1 frozen threshold set
      value: 16 unchanged threshold IDs/operators/values
      units: mixed dimensionless/logarithmic
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  blocking_criteria:
    - exact closed-boundary geometry with no epsilon, tolerance, floor or forced exponent
    - exact 318 routed keys and three scheduled precision nodes per key
    - zero numerical solver calls in implementation preflight
    - exact four-path repair scope and unchanged frozen CLI
    - immutable non-circular authority chain and start/end identity binding
    - fixed-path single-use dispatch bound to an exact fresh root in the frozen UTC namespace
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
GATE_LABEL: REVIEW YELLOW / V3.1-U REPAIR CYCLE 1 CONTROL-PLANE CHANGES REQUIRED BEFORE ONE-USE T0 DISPATCH

incremental_review_state:
  passed_items:
    - item_id: v31u_route_u_auxiliary_geometry_totality
      evidence_identity: exact 318 keys x 3 scheduled precisions = 954 deterministic geometry nodes; inventory SHA-256 6fada7a7982918b5c9f9504dc62032c521d85b42897c7e357047209a8b7982f4; original failed key gives exponents [2,2,2] at [120,160,220] dps
    - item_id: v31u_auxiliary_radius_closed_boundary_roundoff
      evidence_identity: independent_geometry uses exact Fraction(k_decimal), nonnegative squared comparisons and exact turning-branch integer comparison; no epsilon/tolerance/floor/forced exponent
    - item_id: v31u_exact_four_path_scope
      evidence_identity: exact four repaired SHA-256 values above and unchanged CLI 01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4
    - item_id: v31u_zero_science_preflight
      evidence_identity: T4 evidence 0cdf815aad513c900a26ee6cf4be15954c7a96f4f671551114c2b6b28be73084; official_root_created=false; dispatch_consumed=false; science_solver_calls=0; independent CLI preflight PASS
    - item_id: v31u_live_handoff_alternate_authority_removed
      evidence_identity: verify_start_gate uses the unique immutable archive/package chain; live status/T0_current/T7_current are not runtime equality gates or alternate authorities
    - item_id: v31u_initial_authority_and_dispatch_binding
      evidence_identity: initial verify_start_gate rejects immutable-authority/source/protected drift; fixed dispatch binds exact package/reviews/four hashes/CLI/protected/source/tokens/root and is consumed before science
    - item_id: v31u_terminal_identity_and_immutability
      evidence_identity: preserved from initial terminal review; failure.json 5aef8aec8511e5fa35df6459b7cd520b046e080d43f6c24fd95a8b46379d1779 and failure_manifest 6a8ab79495bad03c2d08742a6a6b79f3afc6df658eb7d7dcb20f145efa905b1e remain exact
    - item_id: v31u_route_a_complete_inventory
      evidence_identity: preserved unchanged from initial review; 496 modes and 9920 nodes remain immutable failed-root evidence only
    - item_id: v31u_route_map_frozen_selector
      evidence_identity: preserved unitarity_route_map.json 5eee07ece78204265fe45069ef57a653a61a8ee9d09ff4b4d7e8928bb385c822 and exact 318 routed keys
    - item_id: v31u_resume_prefix_and_transactions
      evidence_identity: preserved unchanged from initial review
    - item_id: v31u_authority_single_use
      evidence_identity: preserved predecessor terminal-root authority history; no failed-root byte is reusable for a future PASS
    - item_id: v31u_protected_source_identity
      evidence_identity: all 21 package source bindings and seven protected radial identities rehashed exact at this review start/end
    - item_id: v31u_failure_terminalization
      evidence_identity: preserved failure root is immutable/non-resumable; correct exact Route-U JSONL hashes are 645e2e116b13dbc1c70e7be1db06f3827a04ccd723e6093ffac8b06199e56c2b and d7c1381fd0e51f439056350de90022ddc8aaf1808e72ee736b304ef10b2a5537
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_official_repair_science
      reason: no one-use dispatch or official repair root exists and no Route-A/U/B/C science was run
    - item_id: v31u_thresholds_and_certificates
      reason: all 16 thresholds and five certificates require a later separately authorized fresh-root run and review
    - item_id: v3_2_and_global_project_state
      reason: outside this gate and unauthorized

findings:
  - finding_id: v31u_source_end_authority_rehash_gap
    class: CONTROL_PLANE_REPAIR
    summary: build_source_ledger rehashes six live implementation/science paths but shallow-copies the start-gate authority identities, so source_end cannot detect mid-run package/review/dispatch/implementation-review drift as frozen.
    exact_evidence: src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py build_source_ledger at lines 1065-1078 starts with dict(start_gate["identities"]); an independent call probe found 42 cached start identities, six dynamic paths, only two overlap/rehashed and 40 cached identities copied unchanged. run_official adds dispatch, implementation-review and dispatch-consumption identities to the same cached map before both source_start and source_end. The frozen design section 6 and T4 prompt lines 93-95 require package/reviews/CLI/all authorities at start/end.
    bounded_control_plane_repair: In build_source_ledger, independently reopen and _file_identity every path represented by the immutable start-gate/dispatch identity map on each start and end invocation, compare the freshly rebuilt identity to the frozen expected identity, and retain the six explicit dynamic source identities. Add a zero-science test that changes a temporary authority after source_start and proves source_end fails closed even when the cached start_gate object is unchanged.
    allowed_files:
      - src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      - tests/unit/test_phase6_v3_hp_unitarity.py
      - tests/regression/test_phase6_v3_hp_unitarity_publication.py
    unblock_condition: every package/review/dispatch/implementation-review/dispatch-consumption and frozen source identity is freshly rebuilt at both source_start and source_end; any temporary mid-run identity drift raises V31ContractError before acceptance; oracle, CLI, domain, thresholds, conventions, failed root and protected hashes remain exact.
  - finding_id: v31u_dispatch_official_namespace_gap
    class: CONTROL_PLANE_REPAIR
    summary: _validate_dispatch binds the argument and payload to one exact absent root but does not enforce the package's frozen direct-child UTC official-root namespace.
    exact_evidence: configs/phase6_v3_1_u_repair_cycle1_package.json freezes official_root_namespace=runs/phase6/classic_scattering/v3_1_hp_unitarity_deficit_repair1_v1_<YYYYMMDDTHHMMSSZ>_py314 and timezone=UTC. src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py _validate_dispatch at lines 429-508 checks root absence and payload["exact_root"] == str(root), but no parent/basename namespace predicate exists. The focused positive dispatch fixture uses tmp_path/future_absent_root outside that namespace and _validate_dispatch accepts it.
    bounded_control_plane_repair: Before root creation, require the resolved target to be a direct child of the exact frozen classic_scattering parent and its basename to full-match v3_1_hp_unitarity_deficit_repair1_v1_<YYYYMMDDTHHMMSSZ>_py314 with a valid UTC timestamp; preserve exact payload-root equality and all existing one-use bindings. Add nonnamespace, wrong-parent, malformed timestamp and alias negatives plus one canonical namespace positive.
    allowed_files:
      - src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      - tests/unit/test_phase6_v3_hp_unitarity.py
      - tests/regression/test_phase6_v3_hp_unitarity_publication.py
    unblock_condition: exact-root dispatches outside the frozen parent/basename/UTC namespace fail before root creation and science, while exactly one canonical fresh absent namespace root passes all pre-science authority checks.
  - finding_id: v31u_science_repair_closed
    class: NONBLOCKING_LIMITATION
    summary: The exact geometry repair closes the initial scientific blocker, but this implementation delta is not itself V3.1-U scientific acceptance.
  - finding_id: v31u_future_science_and_v3_2
    class: FOLLOW_UP_DEBT
    summary: A future fresh-root science run, terminal review and all V3.2 work remain separately gated.

delta_review:
  reviewed_failed_items:
    - v31u_route_u_auxiliary_geometry_totality
    - v31u_auxiliary_radius_closed_boundary_roundoff
    - v31u_live_handoff_start_gate_recursion
  passed_invariants_rechecked:
    - v31u_terminal_identity_and_immutability
    - v31u_route_a_complete_inventory
    - v31u_route_map_frozen_selector
    - v31u_resume_prefix_and_transactions
    - v31u_authority_single_use
    - v31u_protected_source_identity
    - v31u_failure_terminalization
    - v31u_exact_graph_threshold_and_certificate_cardinality
  protected_identities_match: true
  unrelated_passed_items_reopened: false
  class_c_delta_required_before_dispatch: true

hold_details: null

verification:
  commands:
    - SHA-256/stat/nlink reload of the review prompt, package, package approval, T4 evidence, four changed files, frozen CLI, 21 source bindings, seven protected paths and failed-root critical identities
    - exact CPython 3.14 focused pytest on tests/unit/test_phase6_v3_hp_unitarity.py and tests/regression/test_phase6_v3_hp_unitarity_publication.py
    - exact CPython 3.14 CLI preflight under the frozen mpmath overlay with PYTHONDONTWRITEBYTECODE=1
    - Ruff check and format --check on the four implementation paths
    - CPython 3.14 in-memory compile of the four implementation paths and git diff --check
    - read-only build_source_ledger call-path probe after verify_start_gate
    - source/dataflow review of independent_geometry, verify_start_gate, _validate_dispatch, run_official and build_source_ledger plus dispatch adversary fixtures
  results:
    - all review/package/evidence/four-file/CLI/source/protected/failure identities exact
    - focused tests 31 passed in 1.15s
    - CLI preflight v3_1_u_preflight=PASS
    - 318 geometry keys, 954 nodes, inventory SHA-256 6fada7a7982918b5c9f9504dc62032c521d85b42897c7e357047209a8b7982f4, original failed-key exponents [2,2,2], science_solver_calls=0
    - Ruff check PASS; four files already formatted; in-memory compile PASS; git diff --check PASS
    - fixed dispatch and official repair root remain absent; no related live science process was found
    - start/end status.md, T0_current.md and T7_current.md hashes remain respectively 15d29b641b66b061c8865edb72eb811519360bda6a314515fd115cbe1ab96158, f80779de4990d6d18581d8ee4bccef1393f3a61b6fdb7cdbced272a357ac0ffa and c41a9a26146d16e1ab3c8c1bf69ea9e4f52cd3d3e853eaa783263cedd7e90e65

non_claims:
  - V3.1-U science remains NOT_ASSESSED; no threshold or certificate result exists for a fresh repair root
  - completed Route-A and partial Route-U failure evidence are immutable and non-reusable as accepted science
  - no one-use T0 dispatch is authorized until both class-C items receive bounded correction and delta verification
  - no V3.2, full-domain V3, Li-figure equivalence or finite-radius observer claim
  - no global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
  control_plane_fast_repair_required: true
```

## Independent decision rationale

The closed-boundary defect is repaired by exact nonnegative algebra.  For the
fixed-radius branch the admissibility decision uses
`4**q * (300*k)^2 >= 16*ell*(ell+1)` with exact rational `k`; for the turning
branch it reduces to the exact integer predicate `4**q >= 16`.  The original
failed key therefore selects `q=2` independently at 120, 160 and 220 dps.
The full frozen route map gives 318 keys and 954 successful decisions with an
ambient-dps invariant inventory and a hard zero-solver guard.  No radius,
exponent set/order, precision schedule, equation, threshold, convention,
protected radial source or failed-root science value changed.

The live-handoff recursion itself is also removed: mutable live coordination
records are preserved only as package-start history, not runtime alternatives
or equality gates.  Initial immutable-authority validation, exact-root
dispatch binding, implementation-review binding and pre-science consumption
are present.  They are not yet the complete frozen control plane, however.
`source_end` cannot observe a mid-run authority replacement because most
authority identities are copied from the start object, and an otherwise valid
dispatch can select an exact absent root outside the reviewed UTC namespace.
Both faults are metadata/path/provenance enforcement defects confined to the
producer and tests.  Correcting them changes no scientific computation and
does not consume bounded scientific repair cycle 2.

Root T0 may authorize only that bounded class-C fast repair and a delta-only
T7 verification.  Root T0 may not publish or use the one-use dispatch until a
later archive carries the exact frozen GREEN implementation-ready label.
