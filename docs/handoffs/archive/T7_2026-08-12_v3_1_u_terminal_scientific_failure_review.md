# T7 formal review — V3.1-U terminal scientific failure

Date: 2026-08-12

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-U CHANGES REQUIRED
```

## Verdict record

```yaml
review_id: t7_v3_1_u_terminal_scientific_failure_initial
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
attempt: initial
reviewer_task: formal SchWO T7
reviewed_candidate:
  root: /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/runs/phase6/classic_scattering/v3_1_hp_unitarity_deficit_v1_20260811T143911Z_py314
  terminal_state: FAILED
  identities:
    - path: failure.json
      sha256: 5aef8aec8511e5fa35df6459b7cd520b046e080d43f6c24fd95a8b46379d1779
    - path: failure_manifest.json
      sha256: 6a8ab79495bad03c2d08742a6a6b79f3afc6df658eb7d7dcb20f145efa905b1e
    - path: records.jsonl
      sha256: 04b18189f4baf47ad4ebd94b761635cec5d9eb9c1b591ac0b9e694ddf1e3dea2
    - path: ladder_records.jsonl
      sha256: 599beb3e5598e7d69b5fe3f359e4ad7901bde013cb8363870a5ca88bdd6c6ab5
    - path: unitarity_route_map.json
      sha256: 5eee07ece78204265fe45069ef57a653a61a8ee9d09ff4b4d7e8928bb385c822
    - path: route_u_records.jsonl
      sha256: 645e2e11d95b3e012a8428ee9afd2f282eb252412593168f756065574edf6c2b
    - path: route_u_ladders.jsonl
      sha256: d7c1381f8458efdc98708492e207595be8e6768db9e37f7bd41c2b826e6b5537

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_hp_unitarity_review.md
    sha256: 8822263a09bde6d5b0bd3b2c00117eb5ac1648ae9f804a4e71380b27fa90cb82
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds_source:
    path: configs/phase6_v3_0_thresholds.json
    sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  replacement_package:
    path: configs/phase6_v3_1_hp_unitarity_replacement_package.json
    sha256: decde34bcdc90db0bc69be446357e306cfe942c84a8d575902eddaa7d1ff6877
  replacement_design:
    path: docs/phase6_v3_1_hp_unitarity_replacement_design.md
    sha256: 243f312182528b10a895cef679d195dcedfd97d7a2e02e388449ae3af313dd28
  thresholds:
    - V3T-S-COMPLEX-001: symmetric_relative_error <= 2e-6
    - V3T-LOGGAMMA-001: absolute_difference <= 2e-4
    - V3T-FLUX-BALANCE-001: absolute_value <= 1e-8
    - V3T-GAMMA-ROUTES-001: absolute_difference <= 2e-8
    - V3T-GAMMA-ROUTES-LOG-001: absolute_difference <= 2e-4
    - V3T-GAMMA-PHYSICAL-001: maximum_bound_violation <= 2e-10
    - V3T-PARITY-PROB-001: absolute_difference <= 2e-8
    - V3T-PARITY-PHASE-001: wrapped_phase_absolute_difference <= 2e-6 rad
    - V3T-PRECISION-S-001: maximum_symmetric_relative_change <= 5e-7
    - V3T-PRECISION-LOGGAMMA-001: maximum_absolute_change <= 1e-4
    - V3T-RIN-S-001: maximum_symmetric_relative_change <= 1e-6
    - V3T-RIN-LOGGAMMA-001: maximum_absolute_change <= 2e-4
    - V3T-ROUT-JOST-S-001: maximum_symmetric_relative_change <= 2e-6
    - V3T-ROUT-JOST-LOGGAMMA-001: maximum_absolute_change <= 3e-4
    - V3T-TOLERANCE-S-001: maximum_symmetric_relative_change <= 1e-6
    - V3T-TOLERANCE-LOGGAMMA-001: maximum_absolute_change <= 2e-4
  blocking_criteria:
    - exact 496/9920 Route-A graph
    - frozen 496-entry direct-Gamma route map
    - exact N_U/3N_U Route-U graph and total geometry at every scheduled precision
    - exact 102/458 Route-B graph
    - exact 23 Route-C records
    - all 16 threshold evaluations and five certificates
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

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-U CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31u_terminal_identity_and_immutability
      evidence_identity: failure_manifest.json/6a8ab79495bad03c2d08742a6a6b79f3afc6df658eb7d7dcb20f145efa905b1e; 763 regular files all 0444/nlink1; 83 directories inclusive all 0555; zero links
    - item_id: v31u_route_a_complete_inventory
      evidence_identity: records 496/04b18189f4baf47ad4ebd94b761635cec5d9eb9c1b591ac0b9e694ddf1e3dea2; ladders 9920/599beb3e5598e7d69b5fe3f359e4ad7901bde013cb8363870a5ca88bdd6c6ab5
    - item_id: v31u_route_map_frozen_selector
      evidence_identity: unitarity_route_map.json/5eee07ece78204265fe45069ef57a653a61a8ee9d09ff4b4d7e8928bb385c822; 496 entries and 318 direct-Gamma Route-U selections
    - item_id: v31u_resume_prefix_and_transactions
      evidence_identity: original 435-record prefix 932129a4921cd71b7867bcc2f0e146ed6940eb84403f366b58989e447402b9a0; ladder prefix 8f387abb83115ac76d87170bc5c1220d6effc6f4586c6202bb069fb35cb8d088; 61 Route-A and 16 Route-U committed transactions
    - item_id: v31u_authority_single_use
      evidence_identity: dispatch 52043056146fb4b289b06dee0c2fac80d2f885b43401ea1be97099b92338298f; authority commit 3690d3308e5e7061d63128a88ffcc92c07965abd1645a346e117c82e95a64d27
    - item_id: v31u_protected_source_identity
      evidence_identity: source_start.json/03768ae080e794c7f607b980999a0639c4f2c954e6a2afcc77d1fb8be102f3f4 and all 37 entries rehashed exact
    - item_id: v31u_failure_terminalization
      evidence_identity: failure.json/5aef8aec8511e5fa35df6459b7cd520b046e080d43f6c24fd95a8b46379d1779; resumable=false; scientific_pass=false; no writer/process
  failed_items:
    - item_id: v31u_route_u_auxiliary_geometry_totality
      blocker_id: v31u_auxiliary_radius_closed_boundary_roundoff
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_route_u_complete_graph
      reason: execution stopped at Route-U ordinal 16; only 48/954 precision records and 16/318 ladders exist
    - item_id: v31u_route_b_external_graph
      reason: 0/102 Route-B keys and 0/458 nodes were started
    - item_id: v31u_route_c_graph
      reason: 0/23 Route-C records were started
    - item_id: v31u_thresholds_and_certificates
      reason: all 16 thresholds are NOT_EVALUATED and all five certificates are absent
    - item_id: v31u_gate_scientific_acceptance
      reason: success manifest, summary, report and uncertainty ledger do not exist

findings:
  - finding_id: v31u_auxiliary_radius_closed_boundary_roundoff
    class: BLOCKING_CURRENT_GATE
    summary: Route-U's auxiliary-radius admissibility test is not total at its own exact closed boundary and fails at one frozen precision node.
    blocker_id: v31u_auxiliary_radius_closed_boundary_roundoff
    violated_contract_item: Exact N_U/3N_U fresh Route-U graph with a non-post-hoc geometry rule that is defined for every routed key and every frozen precision node.
    exact_evidence: failure.json/5aef8aec8511e5fa35df6459b7cd520b046e080d43f6c24fd95a8b46379d1779; resume_control/attempt_0001/transactions/route_u_0016/intent.json; src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py SHA 84fe4c299b46042b841a09d92ab7e38af73cfd12428513753e20c8b4b40b3e39 lines 89-101 and 121-147.
    expected_value: For kM=0.005, ell=10, odd and the frozen dps schedule [120,160,220], a geometry-only auxiliary radius in the allowed exponent set {0,1,2} must exist at every node; the exponent-2 boundary is admissible because k*(4*sqrt(ell*(ell+1))/k) >= 4*sqrt(ell*(ell+1)) by exact algebra.
    observed_value: At 220 dps the independently repeated literal computation gives k*(4*match_radius)-4*sqrt(110) approximately -7.082e-220, so the rounded `>=` test rejects exponent 2 and raises `HPUnitarityOracleError: independent oracle auxiliary-radius domain empty`; at 120 and 160 dps the same expression rounds to exact zero and passes. Route-U ordinal 16 therefore has an authenticated intent but no prepared/commit record.
    bounded_repair: Replace only the precision-sensitive auxiliary-geometry membership construction with an algebraically stable, geometry-only implementation of the already frozen closed-boundary rule. It must not change the exponent set, domain, precision schedule, equations, thresholds, conventions, protected radial code or use any post-solve observable. Add adversarial exact-boundary and just-below/just-above tests, plus an all-318-route/all-three-dps no-solve geometry preflight. Do not use the failed root or any of its scientific values as a new PASS.
    allowed_files:
      - src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py
      - tests/unit/test_phase6_v3_hp_unitarity.py
      - tests/regression/test_phase6_v3_hp_unitarity_publication.py
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_hp_unitarity.py tests/regression/test_phase6_v3_hp_unitarity_publication.py
    unblock_condition: A frozen repair package and zero-science delta review prove the exact closed-boundary semantics and all 318 routed keys x 3 scheduled precision nodes admit a deterministic geometry without post-hoc selection; protected/domain/threshold/convention hashes remain exact; a later separately authorized run uses a fresh absent root and completes Route U, Route B, Route C, all 16 thresholds and all five certificates before scientific acceptance is reconsidered.
  - finding_id: v31u_completed_route_a_is_not_gate_acceptance
    class: NONBLOCKING_LIMITATION
    summary: The complete Route-A graph is durable and internally exact but cannot be promoted to V3.1-U PASS while the replacement gate terminated before independent routes and certificates.
  - finding_id: v31u_full_domain_and_downstream_out_of_scope
    class: FOLLOW_UP_DEBT
    summary: Full-domain V3, V3.2, Li-equivalence and finite-radius observer claims remain outside this bounded gate.

delta_review:
  reviewed_failed_items: []
  passed_invariants_rechecked: []
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

repair_cycle:
  completed_bounded_repairs: 0
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Independent reconstruction

The terminal manifest lists 762 non-self artifacts.  Independent reload of
every file and directory gives 763 regular files and 83 directories inclusive;
every file is `0444/nlink1`, every directory is `0555`, and there is no
symlink, special file, active writer, related Wolfram/Python process or screen
session.  Rebuilding the manifest object with `overall_state="FAILED"` and
canonical serialization reproduces its object and bytes exactly.

Route A contains all 496 ordered modes and 9,920 ladder nodes.  The original
interrupted 435-mode prefix is byte-identical through offsets 943,913 and
16,898,419; its checkpoint inventory is
`2269f129814c26d609cf3fdd0a451a5fd35661a576cf4d030f4f7b9516366d11`.
The full 496 checkpoint inventory is
`16b78dcbeea698554cc37ddc227d4bacbe74fabd628d25c58cb349e3602a54fa`.
All 61 resumed Route-A modes have intent/prepared/commit transactions.

The route map has 496 entries and selects exactly 318 Route-U keys.  Independent
reconstruction from only direct Route-A `Gamma_flux < 1e-8` agrees entry by
entry.  Route U contains 48 precision records and 16 completed ladders, with
17 intents but only 16 prepared/commit pairs.  The failed intent is ordinal 16,
`kM=0.005`, `ell=10`, odd, `small_gamma_route_u`, with Route-A
`Gamma_flux=1.377057120629454e-74` and frozen precision schedule
`[120,160,220]`.

The exact cause is deterministic and pre-publication.  The oracle defines
`match_radius=max(300,sqrt(ell(ell+1))/k)` and admits the three candidates
`2^q*match_radius`, `q=0,1,2`, by comparing
`k*candidate >= 4*sqrt(ell(ell+1))`.  For this key the final candidate is the
closed boundary by exact algebra.  Re-evaluation with the same mpmath operations
passes at 120 and 160 dps, but at 220 dps the left-minus-right value is a
negative rounding residual of approximately `-7.082e-220`; the loop therefore
falls through.  This is an implementation/domain-construction bug in the
independent Route-U oracle, not a resource failure, physical inconsistency,
threshold failure or evidence that the frozen domain must change.

The authoritative dispatch
`52043056146fb4b289b06dee0c2fac80d2f885b43401ea1be97099b92338298f`
was consumed once and binds the corrected T7 controller authority archive
`8c7388c0cf4991f4c47f4ca87c7612efd02fdb4b14a7147be8d426554f3b1e77`.
No old dispatch was used, no retry or lower precision occurred, and the stable
writer lock was retained.  Controller package/implementation corrections are
control-plane history and do not consume a scientific bounded-repair cycle of
the distinct V3.1-U replacement gate.  This initial terminal science failure
therefore permits at most bounded repair 1 under the liveness protocol.

## Verification commands and results

- exact SHA-256/stat reload of the frozen prompt, package, design, domain,
  thresholds, source ledger, root and all artifacts: PASS;
- independent failure-manifest object and canonical-byte reconstruction: PASS;
- direct JSONL reload/order/count/hash reconstruction for Route A, Route U and
  all transactions/checkpoints: PASS;
- independent selector reconstruction for all 496 route-map entries: PASS,
  `N_U=318`;
- mpmath pure-algebra boundary probe at 80/120/160/220/300 dps: reproduced the
  precision-dependent equality failure; no radial or scientific solve run;
- read-only process/screen scan: no active writer, solver, Wolfram kernel or
  related screen session;
- start/end hashes of the seven protected radial sources: exact.

## Non-claims and downstream boundary

- V3.1-U scientific acceptance is `FAIL`; the 16 thresholds and five
  certificates are not evaluated.
- Completed Route-A and partial Route-U records are immutable failure evidence,
  not reusable science for a new PASS.
- This verdict authorizes no repair implementation, T4 execution, V3.2,
  full-domain V3, Li-figure equivalence, finite-radius observer claim or global
  GREEN.
- Only Root T0 may freeze a bounded repair package.  Any later science run
  requires a separate authorization and a fresh absent output root.
