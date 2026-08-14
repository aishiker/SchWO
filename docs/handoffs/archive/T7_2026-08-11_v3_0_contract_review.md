# T7 V3.0 independent contract review

Review date: 2026-08-11

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V3.0 ANALYTIC-LITERATURE BENCHMARK CONTRACT READY
absorption_branch_authorized: true
phase_sensitive_scattering_branch_authorized: true
```

```yaml
review_id: phase6_t7_v3_0_contract_initial_20260811
gate_id: phase6_v3_0_analytic_literature_benchmark_contract
attempt: initial
reviewer_task: T7
reviewed_candidate:
  root: repository V3.0 exact-eight candidate
  identities:
    - {path: docs/phase6_v3_0_validation_contract.md, sha256: 0f8b8c96e01321231377c857ab40d710aa80ac06dce9084029fe2914b1ef37d3}
    - {path: docs/phase6_v3_0_formula_map.md, sha256: e5b556667c28ac8b611430d2dfb4faa5da82b9c7f0c8251251029e3f8c8d0eac}
    - {path: docs/phase6_v3_0_phase_taxonomy.md, sha256: fb91f4cf888dd4984174304783875c9f2e591490df8519bafd2e0b0f73053460}
    - {path: docs/phase6_v3_0_literature_matrix.md, sha256: 088834348e980b81f814340a2a2c460b5bf11239521085c358bed7a90f603328}
    - {path: configs/phase6_v3_0_domain.json, sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b}
    - {path: configs/phase6_v3_0_thresholds.json, sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a}
    - {path: configs/phase6_v3_0_external_anchor_matrix.json, sha256: 06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485}
    - {path: references/notes/phase6_v3_absorption_scattering_conventions.md, sha256: 82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a}

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_0_contract_review.md
    sha256: 74a14af6d9876ac5f29431693a27d6279c7838448c93974fc5a0812a8ad50563
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - id: v3_0_exact_35_field_threshold_ledger
      value: 35 unique pre-producer thresholds; 16 V3.1, 6 V3.2, 6 V3.3 and 8 V3.4 stage associations, including one shared V3.3/V3.4 reduction threshold
      units: field-qualified
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  blocking_criteria:
    - exact primary-source traceability and SchWO convention conversion for V3-F01 through V3-F14
    - direct signed-current/horizon-flux route remains independent of Gamma_S=1-|S|^2
    - independent odd/even solves; parity relation is consistency only
    - gap-free ell>=2 absorption sum, Page low-frequency law and 27*pi*M^2 capture scale
    - exact Folacci f/g and S-1 structure, Yennie recurrence, forward exclusion and no ordinary total-plane-wave infinity sum
    - exact spin-2 J4 glory structure and source-bound geodesic anchors
    - seven-class phase taxonomy and explicit branch predicates
    - distinct V3.1--V3.4 domains, honest external/AP roles and pre-producer observable thresholds
    - immutable upstream identities, separate uncertainty budgets and mandatory nonclaims
  protected_identities:
    - {path: docs/prompts/phase6_v3_master_prompt.md, expected_sha256: f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7, observed_start_sha256: f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7, observed_end_sha256: f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7}
    - {path: configs/phase6_v2_0_convention_contract_20260810.json, expected_sha256: 1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517, observed_start_sha256: 1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517, observed_end_sha256: 1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517}
    - {path: configs/phase6_v2_0_selected_domain_20260810.json, expected_sha256: 9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818, observed_start_sha256: 9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818, observed_end_sha256: 9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818}
    - {path: runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314/plan.json, expected_sha256: de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3, observed_start_sha256: de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3, observed_end_sha256: de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3}
    - {path: src/schwgw/numerics/radial_solver.py, expected_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_start_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_end_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9}
    - {path: src/schwgw/numerics/conditioned_radial.py, expected_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_start_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_end_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2}
    - {path: src/schwgw/numerics/scaled_tortoise_radial.py, expected_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_start_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_end_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df}
    - {path: src/schwgw/numerics/adaptive_jost_radial.py, expected_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_start_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_end_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896}
    - {path: src/schwgw/numerics/matching.py, expected_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_start_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_end_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340}
    - {path: src/schwgw/numerics/physical_boundary_radial.py, expected_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_start_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_end_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f}
    - {path: src/schwgw/numerics/boundary_conditions.py, expected_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_start_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_end_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22}

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V3.0 ANALYTIC-LITERATURE BENCHMARK CONTRACT READY
absorption_branch_authorized: true
phase_sensitive_scattering_branch_authorized: true

incremental_review_state:
  passed_items:
    - {item_id: v30_identity_and_authority, evidence_identity: exact eight candidate hashes; T1 handoff 2b4894ed...84fff; T1 archive 6b8013ff...5918f; all upstream/protected hashes exact at start/end}
    - {item_id: v30_primary_source_traceability, evidence_identity: Page 1976 Eq.19; Dolan PRD77 Eqs.6-9/19/20/36; Dolan CQG25 Eqs.5/18/19 and Sec.5.3/6.1; Folacci Eqs.1-12; Yennie Eqs.47-50; MP normalization chain; Handler-Matzner role/exclusion}
    - {item_id: v30_mode_flux_contract, evidence_identity: e^-iwt currents, S=(-1)^(ell+1)Aout/Ain, direct Gamma_flux and independent Gamma_S, positive-flux signs, log-domain tiny Gamma, independent parities}
    - {item_id: v30_absorption_formula, evidence_identity: sigma_l=pi(2ell+1)(Gamma_o+Gamma_e)/(2omega^2); Page equivalence and 27piM2 dimensions independently rebuilt}
    - {item_id: v30_scattering_formula, evidence_identity: Folacci f+/f- operators and S-1 coefficients, dσ/dΩ=|f|²+|g|², Yennie recurrence, forward exclusion and low-frequency formula independently rebuilt}
    - {item_id: v30_glory_formula, evidence_identity: 2pi omega bg²|db/dtheta| J4² with bg=5.3570M and bg²|db/dtheta|=4.896M³; ring rather than on-axis peak}
    - {item_id: v30_phase_taxonomy, evidence_identity: PHASE-01/03/04/05/06/07 PASS; PHASE-02 PARTIAL with exact bounded effects}
    - {item_id: v30_domain_contract, evidence_identity: four distinct domains; V3.1 11 frequencies/248 ell values/496 parity modes with all strata; V3.2 17 frequencies and gap-free sums; V3.3/V3.4 explicit ladders/windows}
    - {item_id: v30_threshold_anchor_contract, evidence_identity: 35 unique finite threshold fields and 14 unique role-qualified anchors covering V3.1-V3.4; external even limitations explicit}
    - {item_id: v30_governance_isolation, evidence_identity: JSON parse/sorted-key/LF/terminal-newline PASS; no V3 root/process/science; scoped diff PASS}
    - {item_id: v30_absorption_branch, evidence_identity: V3.1/V3.2 formula/domain/anchor/direct-flux/log/uncertainty requirements complete}
    - {item_id: v30_phase_sensitive_branch, evidence_identity: five required phase classes PASS and V3.3/V3.4 formula/domain/threshold contracts complete; any analytic alignment is one common phase shared across f/g, never independent channel fits}
  failed_items: []
  partial_allowed_items:
    - {item_id: v30_frequency_dependent_common_phase, reason: absolute complex f/g phase remains PARTIAL; intensity, common-phase-quotiented complex comparison, relative helicity phase and glory features remain eligible}
    - {item_id: v30_full_domain_v1_independent_certification, reason: remains PARTIAL outside this bounded zero-science contract gate}
  not_assessed_items:
    - {item_id: v30_v3_science, reason: V3.0 ran no radial solve, partial-wave sum, absorption scan or glory computation}
    - {item_id: v30_full_domain_v3, reason: only downstream selected domains are frozen}
    - {item_id: v30_finite_radius_li_global, reason: finite-radius observer, Li equivalence and global project validation are outside scope}

findings:
  - {finding_id: v30_common_absolute_phase_partial, class: NONBLOCKING_LIMITATION, summary: Frequency-dependent common absolute phase is not independently certified; absolute complex f/g phase claims remain forbidden.}
  - {finding_id: v30_future_backend_instantiation, class: FOLLOW_UP_DEBT, summary: Later stage prompts and source maps must bind the fresh AP/BHPT/CAM/geodesic implementations and exact outputs before any numerical claim; this does not invalidate the pre-producer role contract.}
  - {finding_id: v30_source_file_durability, class: FOLLOW_UP_DEBT, summary: Later producer source maps should retain exact inspected primary-source file hashes in addition to stable DOI/arXiv identities; V3.0 formula locators and conversions are already independently verified.}

delta_review:
  reviewed_failed_items: []
  passed_invariants_rechecked: []
  protected_identities_match: true
  unrelated_passed_items_reopened: false
hold_details: null

verification:
  commands:
    - shasum -a 256 on frozen prompts, exact-eight candidate, T1 handoffs, V1/V2 authorities, V2 release five-file ledger, D-union plan and seven protected radial sources at start/end
    - direct primary-source inspection of Page 1976, Handler-Matzner 1980, Dolan 0710.4252 and 0801.3805, Folacci-Ould El Hadj 1906.01441, Yennie-Ravenhall-Wilson 1954, Ould El Hadj 2504.19324, Martel-Poisson, RW and Moncrief bytes/locators
    - python3.14 independent algebra/domain/config audit without importing or invoking SchWO numerical producers
    - jq empty configs/phase6_v3_0_domain.json configs/phase6_v3_0_thresholds.json configs/phase6_v3_0_external_anchor_matrix.json
    - git diff --check -- <exact T1 V3.0 candidate and handoff paths>
    - read-only find/ps checks for runs/phase6/classic_scattering, V3 transients and related numerical processes
  results:
    - all frozen and candidate identities exact at start/end; three JSON candidates parse with recursively sorted keys, LF and one terminal newline
    - 14 formula IDs, 35 unique thresholds, 14 unique anchors and V3.1-V3.4 cross-file stage coverage PASS
    - V3.1 independently expands to 11 frequencies, 248 gap-free ell values and 496 odd/even modes; every declared stratum occurs in the frozen aggregate domain
    - primary-source signs, parity ratio, absorption weights/units, low/high asymptotes, f/g operators, Yennie recurrence and glory dimensions/order PASS
    - no class-A finding, no HOLD condition, no V3 producer/root/process and no scoped whitespace error

non_claims:
  - This GREEN is only the bounded zero-science V3.0 analytic/literature benchmark contract gate.
  - No V3 numerical science result is PASS or authorized by this record alone.
  - Absolute common complex phase remains PARTIAL; no absolute complex f/g phase claim is certified.
  - Full-domain V1 independent certification remains PARTIAL; full-domain V2/V3 are not certified.
  - No Li figure equivalence, finite-radius observer/detector response or ordinary total-plane-wave infinity sum is claimed.
  - No parity-derived even value is an independent even solve, and no published raster is a blocking numerical anchor.
  - No global GREEN.

repair_cycle:
  completed_bounded_repairs: 0
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

Only this review archive and `docs/handoffs/T7_current.md` were changed. No
candidate, prompt, config, source, test, status, T0/T1 handoff, artifact or
numerical process was modified or started. T7 did not dispatch V3.1.
