# T7 V3.1-U replacement-package independent review

Date: 2026-08-11

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U REPLACEMENT PACKAGE READY FOR T4
```

```yaml
review_id: t7_v3_1_hp_unitarity_replacement_package_review_20260811
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
attempt: initial
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: configs/phase6_v3_1_hp_unitarity_replacement_package.json
  identities:
    - path: configs/phase6_v3_1_hp_unitarity_replacement_package.json
      sha256: decde34bcdc90db0bc69be446357e306cfe942c84a8d575902eddaa7d1ff6877
    - path: docs/phase6_v3_1_hp_unitarity_replacement_design.md
      sha256: 243f312182528b10a895cef679d195dcedfd97d7a2e02e388449ae3af313dd28
    - path: docs/prompts/phase6_t4_v3_1_hp_unitarity_replacement.md
      sha256: a1bffc42a381489dadd483edf2e6952d97ce236fbad3fe9ca82eb8b0ca862945
    - path: docs/prompts/phase6_t7_v3_1_hp_unitarity_review.md
      sha256: 8822263a09bde6d5b0bd3b2c00117eb5ac1648ae9f804a4e71380b27fa90cb82
frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_hp_unitarity_package_review.md
    sha256: a07d3723a89ea65422df947c7534fa6db0a4dfe2ebef4b35235aa4fc8d0c3b6a
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - id: V3T-S-COMPLEX-001
      value: 2e-6
      units: dimensionless
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
    - id: V3T-LOGGAMMA-001
      value: 2e-4
      units: dimensionless
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
    - id: V3T-GAMMA-ROUTES-ABS-001
      value: 2e-8
      units: dimensionless
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
    - id: V3T-GAMMA-ROUTES-LOG-001
      value: 2e-4
      units: dimensionless
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  blocking_criteria:
    - candidate_identity_and_all_package_bindings_exact
    - distinct_replacement_gate_not_repair_cycle_3_or_r3_retry
    - exact_496_mode_domain_16_thresholds_and_5_certificates_preserved
    - route_selector_non_circular_and_frozen_before_route_u
    - route_u_independent_of_route_a_and_protected_modules
    - precision_schedule_and_admission_fail_closed
    - fresh_root_and_terminal_provenance_complete
    - future_review_cannot_self_dispatch_v3_2_or_global_green
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
GATE_LABEL: ACCEPT GREEN / V3.1-U REPLACEMENT PACKAGE READY FOR T4

incremental_review_state:
  passed_items:
    - item_id: v31u_distinct_gate_governance
      evidence_identity: gate phase6_v3_1_hp_unitarity_deficit_replacement_v1; predecessor remains ESCALATE/FAIL; completed_bounded_repairs=0 for this distinct gate
    - item_id: v31u_identity_and_scope
      evidence_identity: five frozen candidate/review files exact SHA-256, mode 0444, nlink1; all package source bindings exact
    - item_id: v31u_representability_diagnosis
      evidence_identity: /tmp/schwo_v31_repair_cycle2_sentinels_final.json sha256 6c95d795f7911ad08113ca738af6b48af5eb70be236f2ed79f8f5988d03fe55
    - item_id: v31u_domain_threshold_certificate_preservation
      evidence_identity: exact 496 modes; 16 V3.1 threshold IDs/operators/values; five certificate IDs
    - item_id: v31u_selector_non_circularity
      evidence_identity: selector reads only direct Route-A Gamma_flux and freezes all 496 decisions before any Route-U call
    - item_id: v31u_precision_schedule
      evidence_identity: signed-exponent formula and fixed three-node ladders independently checked at boundary and extreme exponents
    - item_id: v31u_route_independence
      evidence_identity: Route-U AP source imports no Route-A or seven protected implementations; Route-B record/cache reuse is forbidden
    - item_id: v31u_graph_budget_and_certificates
      evidence_identity: exact graph 496/9920 + N_U/3N_U + 102/458 + 23; numerical and convention budgets remain separate
    - item_id: v31u_artifact_protocol
      evidence_identity: fresh exclusive root, source start/end maps, success/failure terminal closure, immutable r3 and no-reuse rules
    - item_id: v31u_allowed_scope
      evidence_identity: five allowed implementation/test paths are absent before implementation and exclude all frozen/protected files
    - item_id: v31u_future_review_boundary
      evidence_identity: future T7 review is a new gate; it cannot itself execute or dispatch V3.2 and cannot grant global GREEN
  failed_items: []
  partial_allowed_items:
    - item_id: v31u_common_absolute_phase
      reason: frozen convention limitation remains PARTIAL and is not altered by this package
    - item_id: v1_full_domain_independent_certification
      reason: predecessor project state remains PARTIAL; this package is bounded V3.1-U only
  not_assessed_items:
    - item_id: v31u_scientific_results
      reason: no Route-U or official V3.1-U science has run
    - item_id: v31u_threshold_outcomes_and_certificates
      reason: thresholds and certificate semantics are reviewed, but their future outcomes are not evidence
    - item_id: v31u_runtime_feasibility
      reason: resource stop rules are specified; measured smokes and official runtime remain future T4 evidence
    - item_id: v3_2_and_full_domain_v3
      reason: outside this package gate and unauthorized

findings:
  - finding_id: v31u_decimal_diagnostic_is_not_acceptance
    class: NONBLOCKING_LIMITATION
    summary: The recomputed AP diagnostic causally supports a representability repair but remains diagnostic-only and does not convert r3 into PASS.
  - finding_id: v31u_route_b_shared_implementation_disclosed
    class: NONBLOCKING_LIMITATION
    summary: Route U may share analytic equations, conventions and implementation bytes with Route B, but must perform fresh calls and cannot reuse Route-B records or caches.
  - finding_id: v31u_future_science_required
    class: FOLLOW_UP_DEBT
    summary: Implementation, preflight, Route-U evidence, threshold outcomes and certificate closure require future separately authorized T4 execution and T7 review.

delta_review:
  reviewed_failed_items: []
  passed_invariants_rechecked:
    - all package and authority bindings
    - exact 496-mode domain
    - all 16 thresholds and five certificates
    - seven protected source identities
    - immutable r3 failure boundary
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - sha256sum all candidate, package-bound authority, source, r3 and seven protected paths
    - stat -f '%Sp %l %z %N' on the five frozen review-package files and protected/r3 evidence
    - independent Decimal reconstruction from original AP decimal strings at 100 digits
    - independent JSON reconstruction of the V3.1 domain, 16 thresholds, five certificates, graph and precision truth tables
    - static import/call-graph inspection of phase6_v3_mode_greybody_ap.py, phase6_mpmath_radial.py and cycle-2 Route-A sources
    - git diff --check -- configs/phase6_v3_1_hp_unitarity_replacement_package.json docs/phase6_v3_1_hp_unitarity_replacement_design.md docs/prompts/phase6_t4_v3_1_hp_unitarity_replacement.md docs/prompts/phase6_t7_v3_1_hp_unitarity_review.md docs/prompts/phase6_t7_v3_1_hp_unitarity_package_review.md
  results:
    - all frozen candidate hashes, sizes, modes and nlinks PASS
    - all package-bound source identities and seven protected hashes PASS at review start and end
    - independent AP reconstruction PASS: Gamma_flux 1.8367868805916905830712478346703039465718942407331827738995296343085024509877683e-14; Gamma_S 1.83678703373334981689098555948625878604144609567397144681332194860723603399205358334148e-14; abs log difference 8.337475319968190784207174401e-8
    - exact domain 496, Route-A nodes 9920, Route-B 102/458 and Route-C 23 PASS
    - precision schedule boundary/extreme cases retain at least 30 decimal guard digits; no post-hoc extension PASS
    - no V3.1-U root, allowed implementation path, related live process, lock, tmp, partial, quarantine or link drift observed
    - diff-check PASS

non_claims:
  - this is package readiness only; V3.1-U science is NOT_ASSESSED
  - the predecessor r3 failure remains immutable FAIL evidence and is not reused, retried or promoted
  - no threshold, certificate, Route-U result or runtime feasibility has passed scientifically
  - no V3.2 dispatch or execution is authorized by this review
  - no full-domain V3 result, Li equivalence or global GREEN

repair_cycle:
  completed_bounded_repairs: 0
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Independent scientific conclusion

The original decimal strings reproduce a high-precision flux/S deficit mismatch
of only `8.337475319968190784207174401e-8` in log space, while the binary64
predecessor comparison was `0.01487180343263006`.  This supports the package's
representability diagnosis but is not accepted as V3.1-U science.  The proposed
Route U computes a fresh arbitrary-precision complex `S`, derives
`Gamma_S=-expm1(2 log|S|)`, and substitutes that operand only in the already
frozen `Gamma_flux < 1e-8` branch.  The selector cannot inspect its own error or
any Route-U result and is frozen over all 496 modes before execution.

The signed-exponent precision schedule is predeclared, monotone and retains at
least 30 guard digits even for extremely small transmission.  Its admission
limits (`2e-5` in adjacent log-Gamma and `5e-8` in adjacent complex-S symmetric
relative error) are stricter than the relevant frozen V3.1 thresholds.  Route U
is independent of Route A and every protected implementation.  Sharing the
already disclosed AP equations and implementation bytes with Route B does not
constitute an independent oracle, but fresh calls plus the explicit no-record/
no-cache-reuse rule preserve the package's stated route semantics.

The package therefore coherently closes the design-level representability
problem without changing the domain, thresholds, certificates or protected
science.  This verdict authorizes only root-T0 fresh verification and possible
bounded T4 implementation/preflight/conditional execution under the frozen T4
prompt.  It authorizes no science by itself and no V3.2 work.
