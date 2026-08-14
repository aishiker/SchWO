# T7 V3.1-X Substage-A implementation delta recheck 1

```yaml
review_id: phase6_t7_v3_1_x_external_direct_route_implementation_delta_recheck_1
gate_id: phase6_v3_1_x_external_direct_route_v1
substage: A_zero_science_implementation_review
attempt: repair_1
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed
reviewed_candidate:
  root: repository exact-six repair-cycle-1 implementation
  identities:
    - path: src/schwgw/validation/phase6_v3_external_direct.py
      sha256: 4d3cbb37ec36526acb8b648675e28994e4b5c78e34e3fd95bceac5de92bed05e
    - path: src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      sha256: 6b043a4f8cdcab3a513eb2bca05538fdecdbb0eb5ba60608dd55ab10ed7791c7
    - path: scripts/phase6_v3_1_x_external_direct.py
      sha256: 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768
    - path: scripts/phase6_v3_1_x_bhpt_direct.wls
      sha256: 0f68dcdff3d91ea3a48df1b2a12ca8de6825c69f905d966be6572c7160e074b3
    - path: tests/unit/test_phase6_v3_external_direct.py
      sha256: a9d00a3361613fc7135c5e9982900e85b746f4ea9aff7b18f3a4b0bcc617ce0c
    - path: tests/regression/test_phase6_v3_external_direct_publication.py
      sha256: 5f08f4ae263d59ddda3fb1e7d30b478ba042641e97d726f6a6ba97ae230eade1

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_x_external_direct_route_science_review.md
    sha256: 339d5d9609e37f263ca3b3c615e5048f4059c80accc03183e02a74df6ffebd7f
  package:
    path: configs/phase6_v3_1_x_external_direct_route_package.json
    sha256: 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752
  initial_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_implementation_review.md
    sha256: 43227b575af051b7beee0c1e568c7842b6724bbb12bb85aebc8389d6b7d2c393
  package_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_package_review.md
    sha256: 4ecfdbbf0df84657fb4a24d0ebb8143c4bb0b01cdc3d925b4eca4bf4df0bad50
  route_admission_thresholds:
    - external precision complex-S symmetric relative change <= 5e-7
    - external precision absolute log-Gamma change <= 1e-4
    - external r_in complex-S symmetric relative change <= 1e-6
    - external r_in absolute log-Gamma change <= 2e-4
    - external r_out complex-S symmetric relative change <= 2e-6
    - external r_out absolute log-Gamma change <= 3e-4
    - three-overlap complex-S symmetric relative spread <= 2e-6
    - three-overlap absolute log-Gamma spread <= 2e-4
    - per-node signed-current balance absolute value <= 1e-8
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
    - item_id: v31x_impl_exact_six_identity_scope
      evidence_identity: exact repair-1 six hashes above; no seventh implementation path
    - item_id: v31x_impl_package_authority
      evidence_identity: package 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752 and package review 4ecfdbbf0df84657fb4a24d0ebb8143c4bb0b01cdc3d925b4eca4bf4df0bad50
    - item_id: v31x_impl_graph_and_no_selection
      evidence_identity: exact 23 keys; sentinel 35/70/105; official 161/322/483; fixed extrema ordinals 3 and 22
    - item_id: v31x_impl_frequency_nodes_overlays
      evidence_identity: exact rational frequencies; 90/45/45 and 120/60/60 nodes; six frozen overlay hashes
    - item_id: v31x_impl_physics_algebra
      evidence_identity: independent In/Up Wronskian decomposition, signed currents, S and Gamma redundant derivations unchanged
    - item_id: v31x_impl_no_internal_science
      evidence_identity: core AST and WLS static source retain one NumericalIntegration public call per node, no MST/internal solver fallback
    - item_id: v31x_impl_protected_and_snapshot_identity
      evidence_identity: protected seven exact; BHPT content d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2 and restored identity a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
    - item_id: v31x_impl_sentinel_admission_false_acceptance
      evidence_identity: all 35 node budgets plus exact two fixed-extrema seven-node ladders are built, persisted, reloaded and reject signed-current balance 8.0 against 1e-8
    - item_id: v31x_impl_loaded_source_false_acceptance
      evidence_identity: exact eight ordered contexts/files reconstructed from Kernel/ReggeWheeler.m and bound to request plus start/end FindFile identities
  failed_items:
    - item_id: v31x_impl_durable_supervision_false_acceptance
      blocker_id: v31x-a-durable-supervision-and-totality-incomplete
    - item_id: v31x_impl_dispatch_environment_false_acceptance
      blocker_id: v31x-a-dispatch-environment-authority-unbounded
    - item_id: v31x_impl_precision_serialization_false_acceptance
      blocker_id: v31x-a-serialized-precision-unproven
  partial_allowed_items:
    - item_id: v31x_external_odd_only
      reason: the frozen bounded external branch is odd RW only; even evidence remains the separately frozen Route-B/AP branch
    - item_id: v31x_snapshot_commit_association
      reason: restored bytes are exact but the snapshot contains no .git; commit association remains inherited provenance, not independently asserted
  not_assessed_items:
    - item_id: v31x_sentinel_science
      reason: no sentinel dispatch/root or Wolfram execution occurred
    - item_id: v31x_official_science
      reason: requires later sentinel ADVANCE and a different one-use official dispatch
    - item_id: v31x_v3_2
      reason: forbidden outside this gate

findings:
  - finding_id: v31x_impl_durable_supervision_failure_window_remains
    class: BLOCKING_CURRENT_GATE
    summary: Repair 1 adds the stable lock and batch outcome index, but stream-open and early child-start failure windows still escape the mandatory durable child terminal/reap envelope.
    blocker_id: v31x-a-durable-supervision-and-totality-incomplete
    violated_contract_item: canonical request/prelaunch/running/raw streams/receipt/terminal for every launched or attempted node, exact argv/environment/start/end/wait/reap/process-group-empty evidence, and no live child after any lifecycle failure
    exact_evidence: src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py lines 603-605 open stdout/stderr before the protected try; an independent zero-science injected first stream-open failure left only request.json and out.raw.prelaunch.json with receipt_exists=false and terminal_exists=false. Lines 649-655 wait only ten seconds after a running/publication exception and neither terminate nor kill a still-live process group. Prelaunch/terminal records omit the exact child environment and absolute start/end timestamps.
    expected_value: every prelaunch interruption, stream-open error, Popen/running-record error, timeout, signal and publication race closes all opened streams, terminates and exactly waits/reaps any child/group, and publishes a semantically validated receipt/terminal plus a complete 35-entry outcome index
    observed_value: third-call abstract failure now gives 35 outcome entries, but an earlier stream-open failure has no receipt/terminal and the early post-Popen exception path can leave a live group after its bounded wait; lifecycle reload validates file identities rather than the full receipt relationships
    bounded_repair: move all stream/process acquisition into one exception-safe state machine; record requested/observed child environment and absolute start/end; on every error close streams, terminate/kill as required, exact-wait/reap and prove PG empty before terminal publication; semantically reload lifecycle records; add direct stream-open, running-publication, hanging-child, timeout/signal/orphan and tampered-receipt adversaries
    allowed_files:
      - scripts/phase6_v3_1_x_bhpt_direct.wls
      - src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
      - tests/unit/test_phase6_v3_external_direct.py
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py tests/unit/test_phase6_v3_cycle2.py
    unblock_condition: all named lifecycle injections produce exact immutable terminal evidence, no open stream/live child/process group/writer remains, lifecycle semantic reload passes only for the exact chain, and the success/failure batch outcome index remains complete and ordered

  - finding_id: v31x_impl_dispatch_environment_positive_unlaunchable
    class: BLOCKING_CURRENT_GATE
    summary: Repair 1 rejects arbitrary caller extras but defines the reviewed positive environment as a two-key live map that the frozen macOS clean-launch path does not produce.
    blocker_id: v31x-a-dispatch-environment-authority-unbounded
    violated_contract_item: one non-circular exact argv/environment and T0-owned one-use dispatch authority with both an executable positive path and rejection of every missing/changed/extra caller surface
    exact_evidence: under `/usr/bin/env -i PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=...` and exact CPython3.14, direct readback is four keys: LC_CTYPE=C.UTF-8, PYTHONDONTWRITEBYTECODE=1, PYTHONPATH=..., and __CF_USER_TEXT_ENCODING=0x1F5:0x19:0x34. The validator requires requested_environment==observed_environment==EXACT_EXECUTION_ENVIRONMENT and dict(os.environ)==that two-key map, yielding equal=false before dispatch consumption/root/science.
    expected_value: exact caller-requested two-key environment and exact host-observed startup environment are separately frozen, internally derived and both persisted, while any deviation from either map or authority path fails before science
    observed_value: arbitrary extras are now rejected and review/dispatch namespaces are fixed, but the canonical intended clean launch is rejected because observed macOS startup state is not the same map as requested execve state
    bounded_repair: separate requested and observed environment authorities using the exact host-bounded launcher semantics; retain exact-map equality with no wildcard/subset/ignored keys; bind both in dispatch and consumption; add a real zero-science clean-launch positive plus missing/changed/extra/alternate-launcher negatives
    allowed_files:
      - src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
      - scripts/phase6_v3_1_x_external_direct.py
      - tests/unit/test_phase6_v3_external_direct.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
    recheck_command: /usr/bin/env -i PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -c 'import os; from schwgw.validation import phase6_v3_mode_greybody_external_direct_replacement as r; assert r.validate_clean_launch_environment(dict(os.environ))'
    unblock_condition: the exact clean-launch positive reaches dispatch validation with separately exact requested and observed maps, while every missing/changed/extra key, wrong launcher/argv/cwd/executable/review/dispatch identity and replay still fails before consumption/root/science

  - finding_id: v31x_impl_precision_witness_internally_inconsistent_and_forgeable
    class: BLOCKING_CURRENT_GATE
    summary: Repair 1 adds scalar witnesses, but the WLS and Python significant-digit algorithms disagree and the Python reload still accepts forged nonzero exact-value metadata.
    blocker_id: v31x-a-serialized-precision-unproven
    violated_contract_item: each nonexact radius/basis/derivative scalar must carry source precision/accuracy sufficient for its 90/120-digit node and must round-trip without silent truncation; exact-zero handling must be explicit and forged metadata fail closed
    exact_evidence: WLS lines 180-185 delete every character `0` before counting, whereas Python `_decimal_significant_digits` counts interior zeros. For synthetic canonical decimal 1.2034 the Python count is 5 and the WLS literal algorithm count is 4, so a legitimate WLS witness containing an interior zero fails reload. Separately, an independent P1 adversary changed H.real to decimal=1, exact_value=true, exact_zero=false, null precision/accuracy and serialized_significant_digits=1; derive_node_record accepted it.
    expected_value: producer and independent reload implement one exact canonical significant-digit definition, prove source precision/accuracy and serialized digits for every nonexact scalar, and admit only explicitly justified exact zeros without a metadata escape hatch
    observed_value: current positive producer/reload algorithms are incompatible for decimals containing zero, while arbitrary short nonzero scalars can bypass wp/pg/ag through exact_value=true; the existing 96 tests omit both cases
    bounded_repair: align the WLS and Python canonical digit algorithm including interior zeros/exponents; restrict exact-value handling to the explicitly permitted exact-zero case or prove an equally strict source-bound exact-value grammar; add interior-zero/exponent/trailing-zero and forged exact-nonzero adversaries plus producer-to-reloader fixture parity
    allowed_files:
      - scripts/phase6_v3_1_x_bhpt_direct.wls
      - src/schwgw/validation/phase6_v3_external_direct.py
      - tests/unit/test_phase6_v3_external_direct.py
      - tests/regression/test_phase6_v3_external_direct_publication.py
    recheck_command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py -k 'precision or serialization'
    unblock_condition: WLS-produced canonical decimals and Python reload agree for interior-zero/exponent edge cases; all nonexact values meet exact node wp/pg/ag and digit requirements; short/truncated/padded/forged/cross-node/exact-nonzero attacks fail closed

delta_review:
  reviewed_failed_items:
    - v31x_impl_sentinel_admission_false_acceptance: CLOSED
    - v31x_impl_loaded_source_false_acceptance: CLOSED
    - v31x_impl_durable_supervision_false_acceptance: OPEN
    - v31x_impl_dispatch_environment_false_acceptance: OPEN
    - v31x_impl_precision_serialization_false_acceptance: OPEN
  passed_invariants_rechecked:
    - exact-six scope and repair-1 hashes
    - package and initial/package review authorities
    - exact key/node/overlay graph and no-selection/no-MST/no-reuse rules
    - Wronskian/current/S/Gamma algebra and no internal solver path
    - protected seven and complete 25-file external snapshot identities
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - shasum -a 256 <prompt/package/initial-review/exact-six/T4-evidence paths>
    - env -i PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src PATH=/opt/homebrew/bin:/usr/bin:/bin /opt/homebrew/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_external_direct.py tests/regression/test_phase6_v3_external_direct_publication.py tests/unit/test_phase6_v3_cycle2.py
    - CPython3.14 zero-science stream-open lifecycle injection in a fresh private temporary directory
    - /usr/bin/env -i PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src <exact CPython3.14> -c <read-only environment dump>
    - CPython3.14 synthetic interior-zero significant-digit comparison and forged exact-nonzero raw-record adversary
    - .venv/bin/ruff check <five Python candidate paths>
    - .venv/bin/ruff format --check <five Python candidate paths>
    - CPython3.14 in-memory compile of five Python candidate files
    - git diff --check -- <exact six candidate paths>
    - verify_start_gate() independent package/protected/snapshot reload
    - ps -axo pid=,command= and root-namespace absence check
  results:
    - exact prompt/package/initial-review/exact-six/T4 evidence hashes PASS
    - 96 passed in 17.02s under CPython3.14 exact overlay; zero Wolfram/solver/dispatch/root
    - Ruff check PASS; Ruff format PASS; compile PASS; diff-check PASS
    - sentinel signed-current and missing-ladder adversaries reject; exact explicit sentinel budget reload PASS
    - exact eight loaded contexts/files and missing/extra/reordered/alias/mode/link adversaries PASS
    - stream-open injection reproduced receipt=false and terminal=false
    - exact clean-launch environment observed four keys and differs from frozen two-key live validator map
    - interior-zero significant-digit algorithms disagree 5 versus 4
    - forged nonzero exact-value P1 scalar accepted
    - protected seven exact; snapshot content/identity exact; no related V3.1-X root or live process

non_claims:
  - V3.1-X implementation is not ready for sentinel dispatch
  - V3.1-X science remains NOT_ASSESSED
  - no Wolfram or numerical solver was run by this review
  - no dispatch, sentinel root or official root was created
  - V3.1 and V3.1-U remain terminal FAIL/ESCALATE and are not reused
  - no independent even-sector external result is established here
  - no pristine-upstream BHPT claim
  - no V3.2
  - no full-domain V3 certification
  - no global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  same_substantive_blocker_remaining: true
  final_bounded_repair_available: true
  t0_adjudication_required: false
```

Repair cycle 1 closes the sentinel numerical-admission and exact loaded-source
items, but does not satisfy the other three frozen unblock conditions. This
verdict authorizes no dispatch or science. Root T0 may freeze at most one final
bounded repair restricted to the allowed files and the three open items above,
followed by delta review 2. A recurring substantive blocker after that review
requires `ESCALATE / T0 ADJUDICATION REQUIRED`.
