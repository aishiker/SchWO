# T7 V3.1 initial identity-bound failure review

Review date: 2026-08-11

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1 CHANGES REQUIRED
```

```yaml
review_id: phase6_t7_v3_1_initial_failure_20260811
gate_id: phase6_v3_1_mode_greybody_evidence
attempt: initial
reviewer_task: formal T7 task 019f5ed1-b421-7ec2-9bac-8d134855a1ed
reviewed_candidate:
  root: runs/phase6/classic_scattering/v3_1_mode_greybody_r1_20260811T120717Z_py314
  identities:
    - {path: manifest.json, sha256: 78ee1b9b9c9490ddb438639d175a7e9f0ec4b46985c7d35fc604f4a497e0e319}
    - {path: inventory.json, sha256: c7d09f3e72c31f93d62491c859794b7c1b7fe9cc232e84e2560aa61e8f1b2133}
    - {path: ladder_records.jsonl, sha256: 7cfcb4615f41ae9af27d09a008dd6f2f3af3798cefeaba9e1b17a745736cbe58}
    - {path: summary.json, sha256: 3241cecd93c04fbb6ec1a2cdd1f46d81f90313d5d47ff91d2fbb67ebe5a23e1f}
    - {path: report.json, sha256: 8bcb55a5c16630e2c7b422feb2e60c657efb21ef577b3b2c5f589747e923a5d5}
  superseded_denylisted_diagnostic:
    root: runs/phase6/classic_scattering/v3_1_mode_greybody_r1_20260811T120359Z_py314
    manifest_sha256: f2320d5da8bfebdf3b0542dd6bcbb0cf3b6e855bd363ea0342c8ef697a19bb8c
    disposition: immutable preflight diagnostic only; incomplete Wolfram executable search; forbidden for resume, repair-in-place, promotion, or accepted input

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_review.md
    sha256: 058cea918e0c41537b4af8b3973dbe9d378cd3b612aad884ac986d14733d3899
  implementation_contract:
    path: docs/prompts/phase6_t4_v3_1_mode_greybody.md
    sha256: 7e377f64782b8311e111469f53eeb182190d30347ffe0d9853a41b96deeafab6
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - {id: V3T-S-COMPLEX-001, value: 2e-6, units: dimensionless}
    - {id: V3T-LOGGAMMA-001, value: 2e-4, units: natural-log units}
    - {id: V3T-FLUX-BALANCE-001, value: 1e-8, units: dimensionless}
    - {id: V3T-GAMMA-ROUTES-001, value: 2e-8, units: probability}
    - {id: V3T-GAMMA-ROUTES-LOG-001, value: 2e-4, units: natural-log units}
    - {id: V3T-GAMMA-PHYSICAL-001, value: 2e-10, units: probability}
    - {id: V3T-PARITY-PROB-001, value: 2e-8, units: probability}
    - {id: V3T-PARITY-PHASE-001, value: 2e-6, units: radian}
    - {id: V3T-PRECISION-S-001, value: 5e-7, units: dimensionless}
    - {id: V3T-PRECISION-LOGGAMMA-001, value: 1e-4, units: natural-log units}
    - {id: V3T-RIN-S-001, value: 1e-6, units: dimensionless}
    - {id: V3T-RIN-LOGGAMMA-001, value: 2e-4, units: natural-log units}
    - {id: V3T-ROUT-JOST-S-001, value: 2e-6, units: dimensionless}
    - {id: V3T-ROUT-JOST-LOGGAMMA-001, value: 3e-4, units: natural-log units}
    - {id: V3T-TOLERANCE-S-001, value: 1e-6, units: dimensionless}
    - {id: V3T-TOLERANCE-LOGGAMMA-001, value: 2e-4, units: natural-log units}
    source_path: configs/phase6_v3_0_thresholds.json
    source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  blocking_criteria:
    - exact 11-frequency, 248-pair, 496-independent-parity Route-A domain
    - complete frozen r_in, r_out/Jost, tolerance and AP precision ladders
    - 102 independent AP modes and 23 fresh external odd BHPT anchors
    - all 16 pre-producer thresholds and exactly five certificates
    - direct horizon-current Gamma independent of Gamma_S
    - immutable canonical publication and linewise JSONL reload
  protected_identities:
    - {path: docs/prompts/phase6_v3_master_prompt.md, expected_sha256: f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7, observed_start_sha256: f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7, observed_end_sha256: f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7}
    - {path: docs/handoffs/archive/T7_2026-08-11_v3_0_contract_review.md, expected_sha256: b672c7f33d2f3cc891f455c6d8123ed846309a07244696da34236f8e254c0126, observed_start_sha256: b672c7f33d2f3cc891f455c6d8123ed846309a07244696da34236f8e254c0126, observed_end_sha256: b672c7f33d2f3cc891f455c6d8123ed846309a07244696da34236f8e254c0126}
    - {path: runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314/plan.json, expected_sha256: de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3, observed_start_sha256: de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3, observed_end_sha256: de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3}
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
    - {item_id: v31_frozen_authority_identity, evidence_identity: exact V3 master/T4/T7 prompts, exact-eight V3.0 authorities, V1/V2 current manifests, D-union and seven protected hashes all match at start/end}
    - {item_id: v31_inventory_contract, evidence_identity: 11 frequencies; ellmax 16/16/16/16/17/17/19/21/26/37/58; 248 unique pairs; 496 ordered odd/even keys; strata pairs 62 transmitted, 21 critical, 66 reflected, 99 evanescent}
    - {item_id: v31_anchor_inventory, evidence_identity: 102 unique AP modes with retained memberships and 23 unique odd-only BHPT keys}
    - {item_id: v31_artifact_identity_and_immutability, evidence_identity: both roots 0555; each has 11 direct entries, 10 non-self manifest records; all direct artifacts 0444 regular nlink1; hashes/sizes exact; no links/transients/writer}
    - {item_id: v31_external_runtime_current_identity, evidence_identity: exact external SSD WolframKernel SHA 70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c bound in main root; prior incomplete-search root explicitly denylisted}
    - {item_id: v31_fail_closed_claim_state, evidence_identity: overall FAILED_SCIENTIFIC; candidate_success false; numerical certificate FAIL; four certificates NOT_ASSESSED; global_status null; global GREEN false; independent review NOT_ASSESSED}
    - {item_id: v31_direct_flux_pure_algebra, evidence_identity: absorption module keeps supplied horizon flux separate from S route; focused injected test demonstrates gamma_flux 0.5 versus gamma_s 0.75}
    - {item_id: v31_focused_quality_checks, evidence_identity: independent focused/all-V3 test 4 passed; scoped Ruff check/format PASS; source compile 3/3 PASS; scoped diff-check PASS}
  failed_items:
    - {item_id: v31_route_a_first_required_node, blocker_id: v31_route_a_first_node_native_failure}
    - {item_id: v31_complete_producer_route_coverage, blocker_id: v31_official_runner_incomplete_scope}
  partial_allowed_items:
    - {item_id: v31_common_absolute_phase, reason: frozen convention budget permits only a common absolute-phase PARTIAL/nonclaim; it cannot excuse missing mode probabilities}
    - {item_id: v31_full_domain_v1_independent_certification, reason: remains PARTIAL outside this selected V3.1 gate}
  not_assessed_items:
    - {item_id: v31_route_a_mode_observables, reason: zero of 496 modes completed; no A_in/A_out/A_H, currents, fluxes, S, Gamma or log-Gamma mode records exist}
    - {item_id: v31_route_b_ap, reason: 0 of 102 AP modes and no 80/120/180-digit records}
    - {item_id: v31_route_c_external, reason: runtime is available but 0 of 23 required external anchors executed in the consumed candidate}
    - {item_id: v31_threshold_extrema, reason: all 16 threshold evaluations have zero applicable completed records; no extrema can be scientifically reported}
    - {item_id: v31_remaining_certificates, reason: flux-vs-S, external, parity and domain-coverage certificates are explicitly NOT_ASSESSED}
    - {item_id: v31_full_repository_suite, reason: not repeated because this initial gate already has complete class-A scientific/implementation blockers; a fresh passing full suite remains mandatory before acceptance}
    - {item_id: v31_v3_2_and_full_domain, reason: downstream absorption sums/full-domain V3 are outside scope and forbidden}

findings:
  - finding_id: v31_route_a_native_failure
    class: BLOCKING_CURRENT_GATE
    summary: The first mandatory frozen Route-A ladder node fails in both the stabilized BVP and protected bidirectional fallback, leaving zero completed modes.
    blocker_id: v31_route_a_first_node_native_failure
    violated_contract_item: Every Route-A key and every frozen ladder node must complete with raw amplitudes/currents/fluxes; a failed blocking Route-A node cannot be excused.
    exact_evidence: main manifest 78ee1b9b...e0e319; ladder_records.jsonl 7cfcb461...cbe58; sole record kM=0.005/odd/ell=2/r_in=1e-8/r_out=489.8979485566356/Jost160/rtol1e-10/atol1e-12; summary 3241cecd...23e1f; radial_solver.py lines 688-699 and 920-932.
    expected_value: A finite PASS node followed by the complete predeclared Route-A ladder and 496 terminal independent-parity modes.
    observed_value: RuntimeError; BVP singular Jacobian at barrier_action=14.716089382, then bidirectional fallback non-monotonic grid; elapsed 0.06759266601875424 s; attempts/completed 1/0; records.jsonl empty.
    bounded_repair: No repair is authorized here. Root T0 must freeze a separate identity-bound generic radial/V3.1 repair scope; the first node must pass without changing domain, node, formula, threshold or convention, and all evidence must be regenerated in a fresh no-overwrite revision. If a protected radial file must change, its upstream authority and hashes require a new contract/review before rerun.
    allowed_files:
      - none under this read-only review
      - only files explicitly named by a future Root-T0 frozen repair prompt; never either consumed root
    recheck_command: 'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 scripts/phase6_v3_1_mode_greybody.py validate --root "$FRESH_V31_ROOT"'
    unblock_condition: A fresh identity-bound root contains a PASS record for the exact failed node and complete fail-closed evidence for every required Route-A node/mode, with unchanged frozen domain/threshold/convention identities.
  - finding_id: v31_official_runner_scope_incomplete
    class: BLOCKING_CURRENT_GATE
    summary: The frozen official runner is structurally a first-node failure capturer, not an implementation capable of producing the required complete V3.1 evidence.
    blocker_id: v31_official_runner_incomplete_scope
    violated_contract_item: The official implementation must execute 496 Route-A modes with complete ladders, 102 AP modes, 23 fresh external anchors, 16 threshold families and five reconstructible certificates.
    exact_evidence: phase6_v3_mode_greybody.py SHA ad013357...ac0119 lines 462-506 selects build_mode_inventory()[0], has one solve_radial_mode call, zero loops, and hard-codes OFFICIAL_RUNNER_INCOMPLETE_AFTER_UNEXPECTED_FIRST_NODE_PASS; AST finds no AP solver and only an external smoke function; source_map SHA 312b3704...734d05.
    expected_value: Deterministic full-domain loops and independent Route A/B/C implementations with raw records, threshold evaluation, resume/checkpoint, summary/report and certificate reconstruction.
    observed_value: One hard-coded Route-A call; no loop; no AP implementation; external code is smoke-only; even an unexpected first-node PASS is forced to terminal FAILED_SCIENTIFIC; 0 mode/AP/external records and 0 threshold evaluations.
    bounded_repair: Under a separately frozen T0 package, complete the V3-specific producer/validator and independent AP/external routes without editing protected radial/V1/V2/V3.0 bytes or changing scientific criteria; then run one fresh revision from scratch.
    allowed_files:
      - src/schwgw/scattering/absorption*.py
      - src/schwgw/validation/phase6_v3*.py
      - scripts/phase6_v3*.py
      - tests/unit/test_phase6_v3*.py
      - tests/physics/test_phase6_v3*.py
      - tests/regression/test_phase6_v3*.py
      - runs/phase6/classic_scattering/v3_1_mode_greybody_r2_<fresh-UTCZ>_py314/**
    recheck_command: 'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 -m pytest -q -p no:cacheprovider tests/unit/test_phase6_v3_mode_greybody.py tests/physics/test_phase6_v3_mode_greybody.py tests/regression/test_phase6_v3_mode_greybody.py && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 scripts/phase6_v3_1_mode_greybody.py validate --root "$FRESH_V31_ROOT"'
    unblock_condition: Static dataflow and fresh raw artifacts prove exact counts 496/102/23, complete frozen ladders, all 16 thresholds independently reconstructible, and exactly five scope-complete certificates with no first-node-only terminal path.
  - finding_id: v31_jsonl_linewise_reload_defect
    class: CONTROL_PLANE_REPAIR
    summary: ladder_records.jsonl is one valid pretty-printed JSON object across 17 lines, so every line fails JSON parsing in-place and in a distinct temporary copy.
  - finding_id: v31_embedded_protected_identity_ledger_incomplete
    class: CONTROL_PLANE_REPAIR
    summary: source_map records only three V3 configs and two prompts plus protected_files_unchanged=true, rather than embedding all eight V3.0 authorities, V1/V2 identities, D-union and seven protected start/end hashes; independent T7 rehashes show no drift, so this is a future publication/provenance repair, not a new scientific failure.
  - finding_id: v31_common_phase_nonclaim
    class: NONBLOCKING_LIMITATION
    summary: Frequency-dependent common absolute phase remains PARTIAL and forbids absolute complex phase claims, but it would not block mode probabilities if the missing evidence passed.
  - finding_id: v31_future_scattering_work
    class: FOLLOW_UP_DEBT
    summary: V3.2-V3.5, total absorption, angular scattering, glory, Li comparison and finite-radius response remain separate downstream gates and cannot mitigate or enlarge this failure review.

delta_review:
  reviewed_failed_items: []
  passed_invariants_rechecked: []
  protected_identities_match: true
  unrelated_passed_items_reopened: false
hold_details: null

verification:
  commands:
    - fresh SHA-256/start-end stat checks over prompts, exact-eight V3.0 authorities, current V1/V2 manifests, D-union, seven protected sources, T4 handoffs, two candidate manifests, four V3.1 sources and external WolframKernel
    - direct Python-3.14 reconstruction of frequency/ell/parity inventory, strata, AP/external anchors, manifest membership and JSONL linewise behavior without invoking a radial solver
    - in-place and distinct-temporary-copy validate_terminal_candidate calls
    - Python-3.14 AST/dataflow inspection of run_official_candidate and run_external_smoke
    - PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 -m pytest -q -p no:cacheprovider tests/unit/test_phase6_v3_mode_greybody.py
    - .venv/bin/ruff check plus .venv/bin/ruff format --check on four V3.1 implementation/test paths
    - read-only source compile for three Python paths and scoped git diff --check
    - read-only process/transient/link checks
  results:
    - exact current and protected identities match at start/end; T4 current/archive are 10a44da0...d94e and 0dbdeddc...71d4
    - both roots have exact manifest membership and immutable 0555/0444/nlink1 regular-file state; no related process, link or transient
    - exact domain reconstruction PASS: 11 frequencies, 248 pairs, 496 ordered modes, 102 AP modes, 23 odd-only external keys
    - main native failure independently recovered; Route A attempts/completions 1/0, Route B 0, Route C 0
    - JSONL strict reload FAIL reproduced in place and temporary copy with JSONDecodeError at line 1 column 2; whole-file JSON is valid and status FAILED
    - focused/all existing Phase-6 V3 tests 4 passed in 0.29 s; Ruff check PASS; four files formatted; source compile 3/3 PASS; scoped diff-check PASS
    - /opt/homebrew Python 3.14 environment does not expose ruff as a module; project .venv Ruff binary supplied the successful read-only checks
    - full repository suite not run because no acceptance is possible with the two complete class-A blockers

non_claims:
  - No V3.1 mode greybody probability, flux closure, parity relation, AP agreement or external agreement is accepted.
  - No threshold extremum is reported as PASS; all 16 have zero completed applicable records.
  - The superseded 120359Z preflight diagnostic is not current evidence and its no-Wolfram conclusion is denied.
  - No V3.2, total absorption, full-domain V3, angular scattering, glory, Li equivalence or finite-radius observer result is authorized.
  - Full-domain V1 independent certification remains PARTIAL; common absolute phase remains PARTIAL.
  - No global GREEN.

repair_cycle:
  completed_bounded_repairs: 0
  same_substantive_blocker_remaining: true
  t0_adjudication_required: false
```

The candidate and both consumed roots were not modified, resumed or executed.
T7 did not design or dispatch a repair and did not start V3.2.
