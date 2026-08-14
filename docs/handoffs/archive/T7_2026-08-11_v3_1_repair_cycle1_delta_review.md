# T7 V3.1 repair-cycle-1 bounded delta review

Date: 2026-08-11

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1 CHANGES REQUIRED
```

```yaml
review_id: t7_v3_1_repair_cycle1_delta_review
gate_id: phase6_v3_1_mode_greybody
attempt: repair_1
reviewer_task: formal SchWO T7
reviewed_candidate:
  root: null
  identities:
    - {path: /tmp/schwo_v31_repair_cycle1_route_a_20node_sentinel.json, sha256: 9cfc3f91d722d212a7dfc22ec3746b27d300ce462ca874e0131986e4f39fa892}
    - {path: /tmp/schwo_v31_repair_cycle1_route_a_20node_sentinel.stderr, sha256: 31bdbfa60f243467643d168b6df4e96b7667ab30eff6d1557a17f9e7168e1333}
    - {path: docs/handoffs/archive/T4_2026-08-11_v3_1_repair_cycle1_preexecution_blocker.md, sha256: 12fcdd387c065e0d5f57df6c2b7ae24f7680e6609c7da7f20c685f8fcdf7c30d}
    - {path: docs/handoffs/T4_current.md, sha256: 1c038d6cf04db42b8d1a78a75b5cac7b91e7568da58fa231933c2b5d1ce063bc}
  terminal_state: BLOCKED / V3.1 REPAIR CYCLE 1 MANDATORY ROUTE-A SENTINEL FAILED
  official_r2_root_created: false

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_delta_review_cycle1.md
    sha256: 6b247f5736813d2ba9eb9ea415688a21dd7dc4948659f8bd21d747f90be0498e
  initial_review:
    path: docs/handoffs/archive/T7_2026-08-11_v3_1_initial_failure_review.md
    sha256: d0cb93d0ade94d0376a09e4207d6059558c04c2b45383fcb42039525dad2d7c5
  approved_package:
    path: configs/phase6_v3_1_repair_cycle1_package.json
    sha256: a439c5c0f93c8ae4ce5b01e8e6a1d98c8f55eb150615177ccfb5b2a1ee786255
  package_review:
    path: docs/handoffs/archive/T7_2026-08-11_v3_1_repair_cycle1_package_review.md
    sha256: 1be2473c15a69abdfcd11231d9a393ea7014bdea9ec849990b900a8ba89aa404
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - {id: V3.1 exact 16-field threshold set, value: unchanged, units: individually frozen, source_path: configs/phase6_v3_0_thresholds.json, source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a}
  blocking_criteria:
    - v31_route_a_first_node_native_failure
    - v31_official_runner_incomplete_scope
  protected_identities:
    - {path: src/schwgw/numerics/radial_solver.py, expected_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_start_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_end_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9}
    - {path: src/schwgw/numerics/conditioned_radial.py, expected_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_start_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_end_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2}
    - {path: src/schwgw/numerics/scaled_tortoise_radial.py, expected_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_start_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_end_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df}
    - {path: src/schwgw/numerics/adaptive_jost_radial.py, expected_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_start_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_end_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896}
    - {path: src/schwgw/numerics/matching.py, expected_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_start_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_end_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340}
    - {path: src/schwgw/numerics/physical_boundary_radial.py, expected_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_start_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_end_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f}
    - {path: src/schwgw/numerics/boundary_conditions.py, expected_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_start_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_end_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22}

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1 CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - {item_id: v31_frozen_authorities, evidence_identity: exact-eight V3.0 authorities, V1/V2 current manifests, D-union, approved package and seven protected hashes match at delta-review start/end}
    - {item_id: v31_inventory_contract, evidence_identity: frozen 11-frequency 248-pair/496-mode and 16-threshold inventory unchanged}
    - {item_id: v31_anchor_inventory, evidence_identity: frozen 102 AP and 23 odd-only BHPT anchor inventories unchanged}
    - {item_id: v31_artifact_identity_and_immutability, evidence_identity: both r1 manifests remain f2320d5d...9bb8c and 78ee1b9b...e0e319; no r2 root, writer, link, lock or transient}
    - {item_id: v31_external_runtime_current_identity, evidence_identity: approved package retains exact external-SSD kernel and BHPT source identity; no Route-C execution occurred}
    - {item_id: v31_fail_closed_claim_state, evidence_identity: sentinel records science_evidence=false, scientific_acceptance=false and official_root_created=false; no candidate promotion}
    - {item_id: v31_direct_flux_pure_algebra, evidence_identity: protected amplitude/current/flux formulas and all V3.0 conventions/thresholds unchanged}
    - {item_id: v31_focused_quality_checks, evidence_identity: independent current focused V3 test 4 passed in 0.40 s; no new implementation was accepted}
  failed_items:
    - {item_id: v31_route_a_first_required_node, blocker_id: v31_route_a_first_node_native_failure}
    - {item_id: v31_complete_producer_route_coverage, blocker_id: v31_official_runner_incomplete_scope}
  partial_allowed_items:
    - {item_id: v31_common_absolute_phase, reason: frozen convention-budget PARTIAL/nonclaim remains unchanged}
    - {item_id: v31_full_domain_v1_independent_certification, reason: remains PARTIAL outside V3.1}
  not_assessed_items:
    - {item_id: v31_route_a_mode_observables, reason: mandatory first-key sentinel failed before official execution; no 496-mode r2 records exist}
    - {item_id: v31_route_b_ap, reason: AP gates were not launched after the earlier sentinel failure}
    - {item_id: v31_route_c_external, reason: external gates were not launched after the earlier sentinel failure}
    - {item_id: v31_threshold_extrema, reason: no official raw records exist from which to evaluate the 16 thresholds}
    - {item_id: v31_remaining_certificates, reason: no r2 candidate or five terminal certificates exist}
    - {item_id: v31_class_c_publication_repairs, reason: compact JSONL and complete source-ledger behavior were specified but no synthetic or official publication/reload was executed}
    - {item_id: v31_full_repository_suite, reason: no terminal r2 candidate exists and the implementation remained the initial incomplete runner}
    - {item_id: v31_v3_2_and_full_domain, reason: forbidden and outside scope}

findings:
  - finding_id: v31_cycle1_route_a_native_failure_remaining
    class: BLOCKING_CURRENT_GATE
    summary: The mandatory cycle-1 sentinel re-executed the exact first Route-A key through the approved protected API, but the frozen baseline and 11 additional required nodes failed; the first failed item is not closed.
    blocker_id: v31_route_a_first_node_native_failure
    violated_contract_item: Every frozen Route-A ladder node must complete; the exact baseline r_in=1e-10, multiplier=1, Jost=160, rtol=1e-10, atol=1e-12 is mandatory and post-hoc selection of a farther passing boundary is forbidden.
    exact_evidence: /tmp/schwo_v31_repair_cycle1_route_a_20node_sentinel.json SHA-256 9cfc3f91d722d212a7dfc22ec3746b27d300ce462ca874e0131986e4f39fa892; stderr SHA-256 31bdbfa60f243467643d168b6df4e96b7667ab30eff6d1557a17f9e7168e1333; T4 archive 12fcdd387c065e0d5f57df6c2b7ae24f7680e6609c7da7f20c685f8fcdf7c30d.
    expected_value: Exactly 20/20 finite PASS records for kM=0.005, odd, ell=2, including the frozen baseline, before any official r2 root.
    observed_value: Exactly 8 PASS and 12 FAIL; only multiplier 4/8 pass. The baseline, every multiplier-1 node, all four multiplier-2 nodes and two non-baseline tolerance nodes fail; errors are seven invalid Jost matching inputs and five unresolved incoming Jost coefficients.
    bounded_repair: No repair is authorized by this review. Root T0 may, under the liveness limit, freeze and independently review one final cycle-2 package; any protected-backend or node-policy change must be explicit, identity-bound and must not select a favorable node from these observed results.
    allowed_files:
      - none under this read-only delta review
      - only exact paths explicitly authorized by a future Root-T0 cycle-2 package; never either r1 root or this diagnostic
    recheck_command: 'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 scripts/phase6_v3_1_mode_greybody.py validate --root "$FRESH_V31_R2_ROOT"'
    unblock_condition: A separately approved cycle-2 pre-execution sentinel proves the exact frozen required graph, including its predeclared baseline, complete and finite without result-dependent selection, and a fresh terminal r2 candidate independently validates every mandatory Route-A node/mode.
  - finding_id: v31_cycle1_complete_runner_coverage_remaining
    class: BLOCKING_CURRENT_GATE
    summary: Cycle 1 stopped before synthetic publication and made no accepted implementation change; the current official runner remains the initial one-node failure capturer, so complete Route-A/AP/external/threshold/certificate coverage is still unproven and structurally absent.
    blocker_id: v31_official_runner_incomplete_scope
    violated_contract_item: The production implementation and pre-science synthetic gate must exercise exact 496/9920/102/458/23 coverage, all 16 thresholds and five ordered certificates through the same reloadable orchestration.
    exact_evidence: src/schwgw/validation/phase6_v3_mode_greybody.py SHA-256 ad013357187c98f1da039cffde85f75d7613b0fbc00decc52bbee36af3ac0119; AST of run_official_candidate lines 412-535 has zero loops, one solve_radial_mode call, build_mode_inventory()[0], and OFFICIAL_RUNNER_INCOMPLETE_AFTER_UNEXPECTED_FIRST_NODE_PASS; no r2 or synthetic root exists; T4 archive 12fcdd38...7c30d states AP/external/synthetic were not launched.
    expected_value: Static dataflow plus a non-scientific synthetic publish/reload prove exact 496 Route-A modes, 9,920 Route-A nodes, 102 AP keys, 458 AP nodes, 23 external records, 16 threshold families and five certificates before official science.
    observed_value: The initial runner bytes remain; there is no complete loop or accepted AP/external production path and no synthetic evidence. Route B, Route C, publication/reload and runtime/disk gates were not launched.
    bounded_repair: No implementation repair is authorized here. Root T0 may include this unchanged failed item in one separately frozen final cycle-2 package, which must require full static/dataflow and injected synthetic closure before any official root.
    allowed_files:
      - none under this read-only delta review
      - only exact V3-local implementation/test/publication paths enumerated by a future Root-T0 cycle-2 package; never accepted/protected inputs or consumed roots
    recheck_command: 'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 -m pytest -q -p no:cacheprovider tests/unit/test_phase6_v3_mode_greybody.py tests/physics/test_phase6_v3_mode_greybody.py tests/regression/test_phase6_v3_mode_greybody.py && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 scripts/phase6_v3_1_mode_greybody.py validate --root "$FRESH_V31_R2_ROOT"'
    unblock_condition: A separately approved cycle-2 implementation has a complete fail-closed production call graph and its same-path synthetic evidence independently reloads exact 496/9920/102/458/23, 16 thresholds and five certificates before a fresh r2 run.
  - finding_id: v31_jsonl_linewise_reload_repair_not_assessed
    class: CONTROL_PLANE_REPAIR
    summary: The compact-JSONL repair was specified but no synthetic or r2 artifact was published, so its execution-level closure remains NOT_ASSESSED and cannot mitigate either class-A blocker.
  - finding_id: v31_source_ledger_repair_not_assessed
    class: CONTROL_PLANE_REPAIR
    summary: The complete start/end source-ledger repair was specified but no synthetic or r2 source map exists for reload verification.
  - finding_id: v31_common_phase_nonclaim
    class: NONBLOCKING_LIMITATION
    summary: Common absolute phase remains PARTIAL and does not cause this failure.
  - finding_id: v31_future_v3_2_work
    class: FOLLOW_UP_DEBT
    summary: V3.2 and broader absorption/scattering work remain separately gated and unauthorized.

delta_review:
  reviewed_failed_items:
    - v31_route_a_first_required_node
    - v31_complete_producer_route_coverage
  passed_invariants_rechecked:
    - v31_frozen_authorities
    - v31_inventory_contract
    - v31_anchor_inventory
    - v31_artifact_identity_and_immutability
    - v31_external_runtime_current_identity
    - v31_fail_closed_claim_state
    - v31_direct_flux_pure_algebra
    - v31_focused_quality_checks
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - exact SHA-256 reload of delta prompt, package, package approval, T4 archive/current, sentinel and stderr
    - direct JSON reconstruction of all 20 sentinel records, ordinals, memberships, baseline, status and native exception counts
    - Python AST/dataflow inspection of current run_official_candidate without executing science
    - PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 -m pytest -q -p no:cacheprovider tests/unit/test_phase6_v3_mode_greybody.py
    - fresh accepted/protected/package/r1 manifest rehashes and read-only r2/process/link/lock/tmp/partial checks
  results:
    - supplied identities all exact; sentinel is valid JSON with exact package binding and false science/acceptance/official-root flags
    - sentinel exact 20 ordered records: 8 PASS, 12 FAIL; baseline FAIL; pass multipliers only 4 and 8; native errors 7/5 exactly
    - current runner unchanged at ad013357...ac0119 and independently remains first-key-only with no complete route loop
    - focused V3 tests 4 passed in 0.40 s, but test success does not close either missing scientific/coverage item
    - seven protected files, five package files, accepted authorities and both r1 manifests match; no official r2, related process or transient exists

non_claims:
  - No V3.1 mode, AP, external, threshold, parity or certificate evidence is accepted.
  - No successful multiplier may replace the frozen baseline by post-hoc selection.
  - No cycle-2 implementation or science is authorized by this review; only Root T0 may design and freeze the final package.
  - No V3.2, full-domain V3, Li equivalence, finite-radius result or global GREEN.

repair_cycle:
  completed_bounded_repairs: 1
  same_substantive_blocker_remaining: true
  t0_adjudication_required: false
```

Cycle 1 is consumed. Under the frozen liveness protocol, Root T0 may design
and separately freeze at most one final bounded cycle 2. That allowance is
governance permission to prepare a package only; it is not authorization to
edit protected science, change a node policy, execute a sentinel or create an
official root. If the same substantive blocker remains after delta review 2,
the required outcome is `ESCALATE / T0 ADJUDICATION REQUIRED` rather than a
third repair.
