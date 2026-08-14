# T7 V3.1-X Substage-A implementation review

```yaml
review_id: t7_v3_1_x_external_direct_route_implementation_review_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
substage: A_zero_science_implementation_review
attempt: initial
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed
reviewed_candidate:
  root: exact-six V3.1-X implementation set
  identities:
    - path: src/schwgw/validation/phase6_v3_external_direct.py
      sha256: f4001bf181d8704ac2a286dfda8af6919fa2112c620acc8440f8bc521c414802
    - path: src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      sha256: 843871d89ab08c31cf28edc3cccc4b32aa02d5b36f9501c125c6eddc67c6a901
    - path: scripts/phase6_v3_1_x_external_direct.py
      sha256: 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768
    - path: scripts/phase6_v3_1_x_bhpt_direct.wls
      sha256: 86f6374b0f917e1ea300df0ee40787fdaf01455b611c598d9a43e7bcf79a6672
    - path: tests/unit/test_phase6_v3_external_direct.py
      sha256: cf8e0de93e0c29fec09bb710528bff3488a0a6bc0e94c96193451d0a4fdb6f69
    - path: tests/regression/test_phase6_v3_external_direct_publication.py
      sha256: 23d41e51c275b3c3424bea34c0ec0798b19d5bd98d67c57652e360584b1e04a4
    - path: /private/tmp/schwo_v31x_external_direct_final_cMtlRO/preflight_evidence.json
      sha256: b69af6cea53e60807ecd965024bace047907e548409d2669fca3eb3dd613bd3a
    - path: /private/tmp/schwo_v31x_external_direct_final_cMtlRO/junit.xml
      sha256: e5d569585a54583e1bc61f10f49129095d18bf9fffe5ea9d737838296769a6b5

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_x_external_direct_route_science_review.md
    sha256: 339d5d9609e37f263ca3b3c615e5048f4059c80accc03183e02a74df6ffebd7f
  package:
    path: configs/phase6_v3_1_x_external_direct_route_package.json
    sha256: 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752
  prior_package_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_package_review.md
    sha256: 4ecfdbbf0df84657fb4a24d0ebb8143c4bb0b01cdc3d925b4eca4bf4df0bad50
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - id: V3.1-frozen-threshold-set
      value: 16 unchanged V3.1 blocking thresholds
      units: exact per-field units in source artifact
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  blocking_criteria:
    - exact source/protected/runtime start-end closure including actual loaded contexts/files
    - exact argv/environment and T0-owned one-use dispatch authority
    - exclusive stable writer lock and durable request/prelaunch/running/raw-stream/receipt/terminal chain
    - per-node success-or-error records and exact batch totality on scientific error
    - O_EXCL/no-follow/atomic/fsynced/nlink1 publication
    - precision-honest WLS serialization and fail-closed Python reload
    - every mandatory sentinel numerical, provenance, publication and resource gate PASS
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
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-X IMPLEMENTATION CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31x_impl_exact_six_identity_and_scope
      evidence_identity: all six requested SHA-256 values exact; no seventh V3.1-X implementation path
    - item_id: v31x_impl_package_prior_review_and_authorities
      evidence_identity: package 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752 and prior review 4ecfdbbf0df84657fb4a24d0ebb8143c4bb0b01cdc3d925b4eca4bf4df0bad50 exact
    - item_id: v31x_impl_graphs_and_no_selection
      evidence_identity: exact 23 keys; sentinel 35/70/105; official 161/322/483; fixed extrema 3/22; no 14-key subset
    - item_id: v31x_impl_frequency_nodes_and_overlays
      evidence_identity: exact rational frequency map, P0/P1 90/120 schedule and all six transformed hashes independently rebuilt
    - item_id: v31x_impl_physics_algebra
      evidence_identity: RW odd equation, In/Up basis, Wronskian signs, V3-F02, direct Gamma_flux and Gamma_S separation pass source and synthetic checks
    - item_id: v31x_impl_no_internal_science_path
      evidence_identity: core imports no protected SchWO solver; WLS contains one public NumericalIntegration In/Up call and no Method->MST; preflight science/Wolfram counts zero
    - item_id: v31x_impl_protected_and_snapshot_identity
      evidence_identity: seven protected sources exact; 25-file/five-directory external snapshot and six overlays exact; source start=end in reported preflight
    - item_id: v31x_impl_existing_zero_science_suite
      evidence_identity: independent CPython3.14 runs 35/35 candidate plus 49/49 adjacent PASS; Ruff, compile and diff-check PASS
  failed_items:
    - item_id: v31x_impl_sentinel_admission_false_acceptance
      blocker_id: v31x-a-sentinel-admission-gates-omitted
    - item_id: v31x_impl_loaded_source_false_acceptance
      blocker_id: v31x-a-loaded-source-closure-incomplete
    - item_id: v31x_impl_durable_supervision_false_acceptance
      blocker_id: v31x-a-durable-supervision-and-totality-incomplete
    - item_id: v31x_impl_dispatch_environment_false_acceptance
      blocker_id: v31x-a-dispatch-environment-authority-unbounded
    - item_id: v31x_impl_precision_serialization_false_acceptance
      blocker_id: v31x-a-serialized-precision-unproven
  partial_allowed_items:
    - item_id: v31x_impl_odd_only_external_scope
      reason: independent even external evidence is explicitly outside this gate and remains a required nonclaim
    - item_id: v31x_impl_snapshot_commit_inherited_only
      reason: byte/inventory snapshot authority is exact; upstream commit association remains an explicit inherited-only nonclaim
  not_assessed_items:
    - item_id: v31x_sentinel_science
      reason: no sentinel dispatch/root or Wolfram execution occurred and implementation is not ready
    - item_id: v31x_official_science
      reason: requires a later sentinel ADVANCE and distinct one-use official dispatch
    - item_id: v32_and_global_status
      reason: forbidden outside this gate

findings:
  - finding_id: v31x_impl_sentinel_admission_false_acceptance
    class: BLOCKING_CURRENT_GATE
    summary: The sentinel success path applies only structural/resource checks and can publish PASS with a frozen per-node numerical criterion violated.
    blocker_id: v31x-a-sentinel-admission-gates-omitted
    violated_contract_item: every mandatory sentinel gate PASS, including per-node current/overlap and applicable fixed-extrema ladder budgets
    exact_evidence: resource_projection validates only record structure and timing; a direct zero-science adversary with max_abs_signed_current_balance=8.0, versus frozen limit 1e-8, returned runtime_gate_passed=true and disk_gate_passed=true
    expected_value: every one of 35 nodes passes all applicable numerical admission gates and both fixed-extrema full ladders have explicit PASS budgets before sentinel_result PASS
    observed_value: run_sentinel calls resource_projection then emits PASS_NOT_REUSABLE without evaluating current/overlap gates or fixed-extrema ladder budgets
    bounded_repair: add exact source-bound sentinel budget construction and validation for all applicable criteria; persist it; reject any failed/missing/nonfinite gate before PASS; add direct negative fixtures including the reproduced current-balance case
    allowed_files:
      - src/schwgw/validation/phase6_v3_external_direct.py
      - src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      - tests/unit/test_phase6_v3_external_direct.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py
    unblock_condition: a synthetic 35-record sentinel with any one admission metric over its unchanged package limit must terminalize FAIL, while an exact all-PASS fixture publishes and independently reloads a complete explicit sentinel budget

  - finding_id: v31x_impl_loaded_source_false_acceptance
    class: BLOCKING_CURRENT_GATE
    summary: The claimed loaded-source closure omits two files that the frozen package entry graph actually loads and does not bind actual contexts/files.
    blocker_id: v31x-a-loaded-source-closure-incomplete
    violated_contract_item: exact source/protected/runtime start-end ledgers and exact Wolfram loaded contexts/files
    exact_evidence: producer LOADED_SOURCE_PATHS has six entries at lines 91-98; immutable Kernel/ReggeWheeler.m loads seven subordinate contexts in addition to itself, yielding exact eight files; omitted are Kernel/MST/MST.m and Kernel/MST/RenormalizedAngularMomentum.m; WLS lines 65-93 merely rehash the request list and checks FindFile only for NumericalIntegration
    expected_value: exact ordered duplicate-free eight-file actual entry graph plus actual loaded-context/file identities, alias-free and equal at start/end and to the overlay request
    observed_value: six-file declared list; the two top-level loaded MST source files are absent, actual context/file totality is not observed, and Python accepts any identical start/end list
    bounded_repair: bind and validate the exact eight actually loaded source paths and contexts before/after every child; compare raw records to the request/overlay identity rather than equality to themselves; add missing/extra/reordered/alias/hash/size/mode/link/cross-overlay adversaries
    allowed_files:
      - scripts/phase6_v3_1_x_bhpt_direct.wls
      - src/schwgw/validation/phase6_v3_external_direct.py
      - src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      - tests/unit/test_phase6_v3_external_direct.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py
    unblock_condition: independent static reconstruction and zero-science fixtures prove exact eight actual loaded sources/contexts and reject every incomplete, self-consistent-but-wrong, aliased or drifted record at both source boundaries

  - finding_id: v31x_impl_durable_supervision_false_acceptance
    class: BLOCKING_CURRENT_GATE
    summary: The controller lacks the frozen stable lock and durable per-child state chain, and its failure branch stops without per-node/batch totality.
    blocker_id: v31x-a-durable-supervision-and-totality-incomplete
    violated_contract_item: exclusive stable writer lock; canonical request/prelaunch/running/raw streams/receipt/terminal; per-node success-or-error and exact batch totality on scientific failure; O_EXCL/no-follow/atomic/fsynced publication
    exact_evidence: synthetic third-call failure produced three requests, only two raw/success records, no prelaunch/running/receipt, no failed-node error record, no records.jsonl totality and only an unflocked .writer.authority; WLS lines 201-207 use Export plus RenameFile without exclusive/no-follow/fsync proof
    expected_value: continuously held stable lock through terminal dual validation; durable prelaunch and running before child; exact wait/reap/streams/receipt/terminal afterward; complete 35-entry outcome index even on scientific error; all publication primitives meet frozen durability semantics
    observed_value: plain authority file without flock; terminal-only child supervision; stop at call 3; incomplete batch; raw WLS publication does not establish the frozen atomic durability contract
    bounded_repair: implement a stable never-replaced lock held through terminal closure, explicit durable child lifecycle records, per-node error records and exact batch outcome totality, and controller-owned exclusive/fsynced raw publication; add second-writer, prelaunch interruption, timeout/signal/orphan, third-node error and publication-race adversaries
    allowed_files:
      - scripts/phase6_v3_1_x_bhpt_direct.wls
      - src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
      - tests/unit/test_phase6_v3_external_direct.py
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py
    unblock_condition: every injected lifecycle failure produces a complete immutable fail-closed terminal with exact plan/outcome totality, continuous lock proof and no live child/group/writer, while success proves the full durable record chain and manifest

  - finding_id: v31x_impl_dispatch_environment_false_acceptance
    class: BLOCKING_CURRENT_GATE
    summary: Dispatch validation treats caller-supplied current environment and arbitrary review/dispatch paths as authority, so an unreviewed extra environment key and forged temporary authority are accepted.
    blocker_id: v31x-a-dispatch-environment-authority-unbounded
    violated_contract_item: exact argv/environment and T0-owned identity-bound one-use dispatch authority before root/science
    exact_evidence: zero-science adversary created a temporary 0444 review and dispatch, added SCHWO_UNREVIEWED_EXTRA=arbitrary to both live and recorded observed_environment, and validate_dispatch returned accepted=true; lines 415-425 compare observed_environment only to dict(os.environ), while lines 426-438 accept any path containing three verdict tokens
    expected_value: one frozen caller environment/observed startup contract with no extra/missing/changed key and one T0-owned dispatch/review authority surface bound to this implementation and review identity
    observed_value: arbitrary caller extras pass when echoed by the dispatch; arbitrary temporary dispatch/review paths with matching tokens pass; no T0-owned namespace/identity closure distinguishes them
    bounded_repair: freeze a non-circular exact dispatch/review authority path and identity grammar for the delta review, require the exact allowed requested/observed environment maps and launcher, persist both before science, and reject arbitrary/extra/missing/changed/alternate authority surfaces
    allowed_files:
      - src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      - scripts/phase6_v3_1_x_external_direct.py
      - tests/unit/test_phase6_v3_external_direct.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py
    unblock_condition: canonical positive authority passes, while arbitrary path/review, predecessor YELLOW, wrong digest/hash/token, extra field, replay, alternate argv/cwd/executable/launcher and every missing/changed/extra environment key fail before consumption/root/science

  - finding_id: v31x_impl_precision_serialization_false_acceptance
    class: BLOCKING_CURRENT_GATE
    summary: The raw schema records only frequency precision and the Python validator accepts basis values with no proof of the node's requested numerical precision.
    blocker_id: v31x-a-serialized-precision-unproven
    violated_contract_item: minimal WLS amplitude/current serialization with serialization-digit consistency for frozen 90/120-digit nodes
    exact_evidence: _mp_real at lines 580-589 checks parseability/finiteness only; a P1 wp=120/pg=60 fixture declaring input_precision_digits=140 but containing short basis strings such as U={real:1,imag:0} and five-character radius was accepted; no per-value Wolfram Precision/Accuracy metadata is serialized or enforced
    expected_value: each nonexact numerical basis/radius/derivative component carries source precision/accuracy sufficient for its node and round-trips without silent truncation, with exact-zero handling explicit
    observed_value: any finite decimal string up to length 1000 is accepted independently of node wp/pg/ag; existing positive fixtures do not prove meaningful serialized precision
    bounded_repair: serialize explicit Wolfram precision/accuracy or an equally fail-closed per-value precision witness, enforce it against the frozen node contract in Python, and add short/truncated/padded/fake-metadata/cross-node adversaries
    allowed_files:
      - scripts/phase6_v3_1_x_bhpt_direct.wls
      - src/schwgw/validation/phase6_v3_external_direct.py
      - tests/unit/test_phase6_v3_external_direct.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py
    unblock_condition: every serialized nonexact value independently proves the frozen node precision/accuracy and round-trip integrity, and all short/truncated/padded/forged/cross-node records fail closed

delta_review:
  reviewed_failed_items: []
  passed_invariants_rechecked:
    - package identities and initial package ADVANCE
    - exact-six scope and hashes
    - exact 23-key and node graphs
    - exact rational frequencies and six overlays
    - physics algebra and no internal solver path
    - protected radial and external snapshot identities
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - shasum -a 256 docs/prompts/phase6_t7_v3_1_x_external_direct_route_science_review.md configs/phase6_v3_1_x_external_direct_route_package.json docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_package_review.md
    - shasum -a 256 <exact six candidate paths> /private/tmp/schwo_v31x_external_direct_final_cMtlRO/preflight_evidence.json /private/tmp/schwo_v31x_external_direct_final_cMtlRO/junit.xml
    - PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py
    - PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_cycle2.py
    - .venv/bin/ruff check src/schwgw/validation/phase6_v3_external_direct.py src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py scripts/phase6_v3_1_x_external_direct.py tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py
    - CPython3.14 in-memory compile of five Python candidate files
    - git diff --check -- <exact six candidate paths>
    - CPython3.14 zero-science loaded-source, third-call failure, sentinel-current, dispatch/environment and precision-record adversaries
    - ps -axo pid=,command=
  results:
    - exact prompt/package/prior-review and exact-six hashes PASS
    - focused V3.1-X tests 35 passed in 6.30s
    - adjacent cycle-2 tests 49 passed in 3.31s
    - combined zero-science run 84 passed in 9.77s
    - Ruff PASS; compile PASS; git diff-check PASS
    - T4 preflight/JUnit hashes exact and report zero science/Wolfram/dispatch/root
    - independent source graph reconstruction found six declared versus eight actual entry-graph files
    - synthetic third-call failure reproduced missing lifecycle/totality evidence
    - current-balance 8.0 greater than 1e-8 was accepted by sentinel resource path
    - arbitrary extra environment and temporary dispatch/review authority accepted
    - wp120 node accepted without per-value precision proof
    - seven protected identities exact at start/end; no V3.1-X root or related live process

non_claims:
  - V3.1-X implementation is not ready for sentinel dispatch
  - V3.1-X science remains NOT_ASSESSED
  - no Wolfram or solver was run by this review
  - no dispatch, sentinel root or official root was created
  - V3.1 and V3.1-U remain FAIL
  - no predecessor or sentinel science reuse
  - no independent even-sector external evidence
  - no pristine-upstream BHPT claim
  - no V3.2
  - no full-domain V3 certification
  - no global GREEN

repair_cycle:
  completed_bounded_repairs: 0
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

This verdict authorizes no sentinel dispatch or science. Root T0 may authorize
one bounded implementation repair limited to the allowed exact-six paths and
the five frozen failed items above. A delta review must check only those failed
items, preservation of the frozen passed items, and protected/source identities.
