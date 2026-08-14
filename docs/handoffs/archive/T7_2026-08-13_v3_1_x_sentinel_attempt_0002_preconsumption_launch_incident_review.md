# T7 incident review — V3.1-X attempt-0002 pre-consumption launch

Date: 2026-08-13

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X ATTEMPT-0002 PRECONSUMPTION INVOCATION READY FOR ONE-USE T0 LAUNCH
```

This is an archive-only `CONTROL_PLANE_REPAIR` incident classification.  It
does not accept sentinel science.  It supersedes the operational launch
permission in the predecessor namespace review only to the extent necessary
to authorize the single exact invocation frozen below.  It does not replace,
rewrite or mint a dispatch.

## Verdict record

```yaml
review_id: t7_v3_1_x_attempt_0002_preconsumption_launch_incident_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed
review_scope: archive-only pre-execution incident classification

frozen_review_basis:
  review_contract:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  accepted_namespace_authority:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_dispatch_namespace_delta_review.md
    sha256: 5a2a3a0f531f777ac0c8299078a645cc0a466158078882dd4e3ad2f38631e498
  accepted_implementation_delta:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_implementation_delta_review.md
    sha256: 789f13fe1236a4226606bd61e1c7930d6b9de80b7bcc10df27c95995f7a6c6ce
  namespace_control_plane_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_dispatch_namespace_control_plane_review.md
    sha256: 72c8b1aeb26103b7d9786ba79d57553afa975f65f2d6832c6a8590add35d8edd
  repair_package:
    path: configs/phase6_v3_1_x_sentinel_repair_cycle1_package.json
    sha256: 5b2da4f0168082996e55a8f4ad27869c8c8e6a27cd207c56696f23134501da75
  external_direct_package:
    path: configs/phase6_v3_1_x_external_direct_route_package.json
    sha256: 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752

incident_dispatch:
  path: docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0002.json
  sha256: 6be8d88226179ed25d4e50dee06cc17a6f38e61e67617edf9751a88e2cea5112
  size: 2722
  mode: "0444"
  nlink: 1
  inode: 2096863
  canonical_reload: PASS
  immutable_bytes_unchanged_start_end: true
  one_use_id: 92c294a70e73286d998cc47279ec0b1055293c3703441f50b74c8423efba8619
  exact_root: /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/runs/phase6/classic_scattering/v3_1_x_external_direct_sentinel_v1_20260813T085010Z_py314
  exact_root_absent_start_end: true
  dispatch_consumption_absent: true
  one_use_id_absent_from_all_existing_consumption_records: true

incident_boundary:
  reported_operator_exit_code: 1
  reproduced_exception_type: ExternalDirectContractError
  reproduced_exception_message: live executable/argv/cwd mismatch
  causal_call_chain:
    - run_sentinel calls verify_start_gate
    - run_sentinel calls validate_dispatch
    - validate_dispatch validates the absent root namespace and immutable dispatch
    - validate_dispatch calls _validate_runtime_invocation
    - relative CLI argv[0] fails exact sys.argv equality
    - validate_dispatch does not return
    - _begin_root is never entered
    - _consume_dispatch and all external/scientific execution are unreachable
  root_creation_count: 0
  dispatch_consumption_count: 0
  wolfram_launch_count: 0
  bhpt_source_load_count: 0
  solver_call_count: 0
  science_call_count: 0
  related_live_process_count: 0
  retry_or_second_launch_count: 0

causal_precision:
  operator_executable_lexeme: /opt/homebrew/bin/python3.14
  executable_symlink_target: ../Cellar/python@3.14/3.14.6/bin/python3.14
  executable_resolved_identity: /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14
  executable_sha256: b502cb4c5b46b8d4192ec6bcb600ce8922f1afc396fcf646e8765c6eba74a0bf
  dispatch_expected_executable: /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14
  validator_executable_semantics: resolved-path equality
  executable_identity_result: PASS
  decisive_mismatch: relative `scripts/phase6_v3_1_x_external_direct.py` versus the required absolute CLI argv[0]
  note: the Homebrew symlink is not independently causal under the frozen resolved-path validator; the corrected command nevertheless uses the exact dispatch-declared Cellar path

live_implementation_identities:
  scripts/phase6_v3_1_x_bhpt_direct.wls: 24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6
  scripts/phase6_v3_1_x_external_direct.py: 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768
  src/schwgw/validation/phase6_v3_external_direct.py: 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4
  src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py: 81a33a4157d6e07b03621bff069c9383914464c16ce4314a9f7a556c7e1cd088
  tests/unit/test_phase6_v3_external_direct.py: 056c7273edbdb612d3fc99c4b493f2fe4c96dc15b8ae7aa3a872587f33f3aaba
  tests/regression/test_phase6_v3_external_direct_publication.py: 24d26a8a9c2e0ad573b97f76b39db7743f2d6639cd57978be93f0c310062f858

frozen_scientific_authorities:
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  external_anchor_matrix:
    path: configs/phase6_v3_0_external_anchor_matrix.json
    sha256: 06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485
  thresholds:
    path: configs/phase6_v3_0_thresholds.json
    sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  convention:
    path: references/notes/phase6_v3_absorption_scattering_conventions.md
    sha256: 82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a

protected_identities:
  src/schwgw/numerics/radial_solver.py: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
  src/schwgw/numerics/conditioned_radial.py: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
  src/schwgw/numerics/scaled_tortoise_radial.py: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
  src/schwgw/numerics/adaptive_jost_radial.py: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
  src/schwgw/numerics/matching.py: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
  src/schwgw/numerics/physical_boundary_radial.py: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
  src/schwgw/numerics/boundary_conditions.py: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X ATTEMPT-0002 PRECONSUMPTION INVOCATION READY FOR ONE-USE T0 LAUNCH

incremental_review_state:
  passed_items:
    - item_id: v31x-attempt0002-dispatch-identity
      evidence_identity: immutable canonical dispatch SHA 6be8d88226179ed25d4e50dee06cc17a6f38e61e67617edf9751a88e2cea5112, mode0444, nlink1, size2722, unchanged at review end
    - item_id: v31x-attempt0002-preconsumption-boundary
      evidence_identity: _validate_runtime_invocation precedes _begin_root and _consume_dispatch; target root and consumption remain absent and science is unreachable on the observed branch
    - item_id: v31x-attempt0002-cause-reconstructed
      evidence_identity: exact clean-environment negative reconstruction with relative CLI argv[0] returned ExternalDirectContractError/live executable/argv/cwd mismatch; executable symlink resolved to the frozen b502cb4c... binary
    - item_id: v31x-attempt0002-authority-still-valid
      evidence_identity: exact clean-environment positive reconstruction with absolute CLI argv passed verify_start_gate and validate_dispatch against the real immutable dispatch without creating a root or consumption
    - item_id: v31x-attempt0002-one-use-unconsumed
      evidence_identity: one_use_id 92c294a7...8619 is absent from every existing dispatch_consumption.json; the only V3.1-X consumption has different one_use_id 06916053...0e6e
    - item_id: v31x-attempt0002-source-and-protected-closure
      evidence_identity: all six implementation, package, domain, anchor, threshold, convention, external-source snapshot and seven protected identities revalidated by verify_start_gate and direct SHA checks
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31x-attempt0002-sentinel-science
      reason: no root, Wolfram child, BHPT load, solver or scientific record exists
    - item_id: v31x-official-science
      reason: no official dispatch/root is authorized or present
    - item_id: v31x-thresholds-and-certificates
      reason: the 16 thresholds and five certificates remain frozen and unevaluated
    - item_id: v3-2
      reason: V3.2 remains forbidden and was not started

findings:
  - finding_id: v31x-attempt0002-operator-command-shape
    class: CONTROL_PLANE_REPAIR
    summary: CLOSED by this identity-bound one-invocation reauthorization; the incorrect relative CLI failed closed before durable consumption, root creation or science and does not consume scientific repair cycle 2.
  - finding_id: v31x-attempt0002-ephemeral-operator-exit-record
    class: NONBLOCKING_LIMITATION
    summary: the reported historical shell exit was not persisted as a repository artifact, but the exact exception is independently reproduced and the only acceptance-relevant durable facts—unchanged dispatch, absent root/consumption, unconsumed one_use_id and zero live process—are directly verified.
  - finding_id: v31x-operator-command-preflight-coverage
    class: FOLLOW_UP_DEBT
    summary: current tests monkeypatch sys.argv and therefore do not execute an operator-facing validation-only command envelope; a future zero-science test should derive executable/absolute CLI/argv/cwd/environment from a real dispatch, run verify_start_gate plus validate_dispatch only, assert no root/consumption before and after, and prove the relative-CLI negative fails identically.
  - finding_id: v31x-attempt0002-no-class-a
    class: NONBLOCKING_LIMITATION
    summary: no scientific byte, formula, threshold, domain, convention, protected identity or solver behavior is changed or invalidated, so no BLOCKING_CURRENT_GATE finding and no nine-field Class-A repair exists.

hold_details: null

classification:
  class_c_control_plane_repair: true
  class_a_blocking_current_gate: false
  hold: false
  escalate: false
  rationale: complete readable identities, no active writer, no contradictory authority, deterministic fail-closed cause, and an unconsumed exact dispatch admit one bounded control-plane action within frozen scope

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 0
  preconsumption_operator_incident_consumes_repair_cycle_2: false
  preconsumption_operator_incident_is_science_retry: false
  remaining_bounded_repairs_if_sentinel_science_later_fails: 1
  t0_adjudication_required: false

verification:
  results:
    - dispatch/review/package/live-six/domain/threshold/anchor/convention/protected hashes PASS
    - verify_start_gate PASS with exact six implementation hashes and complete external-source/protected identity closure
    - wrong relative CLI argv negative PASS with exact expected exception
    - corrected absolute CLI argv positive validate_dispatch PASS
    - requested environment exact two keys and clean-launch observed environment exact four keys PASS
    - exact target root absent before and after every read-only probe
    - exact one_use_id absent from all existing consumption records
    - dispatch SHA/mode/nlink/size unchanged after probes
    - no related Python writer, WolframKernel, sentinel root, lock or science process
    - no implementation, science, test, status or current-handoff file modified

non_claims:
  - no sentinel node or scientific observable has been evaluated or accepted
  - no official V3.1-X dispatch/root or evidence is authorized
  - no reuse, retry, resume or reinterpretation of the consumed attempt_0001 dispatch/root
  - no second launch is authorized by the predecessor namespace archive
  - no arbitrary dispatch, one_use_id, root, date, executable, argv, cwd or environment substitution
  - no threshold, domain, convention, method, precision, graph, source or protected-radial change
  - no finite-radius observer, Li-figure, full-domain or broader independent-certification claim
  - no V3.2 and no global GREEN
```

## Exact one-use reauthorization

The immutable attempt-0002 dispatch is still mechanically and semantically
unconsumed.  Reusing its bytes is therefore permitted only under this new
archive's explicit authority; absence of `dispatch_consumption.json` by itself
is not permission to invoke it again.

Root T0 may perform exactly one process launch, from the exact working
directory

```text
/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO
```

using exactly:

```text
/usr/bin/env -i \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src \
  /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 \
  /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/scripts/phase6_v3_1_x_external_direct.py \
  sentinel \
  --dispatch /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0002.json \
  --dispatch-sha256 6be8d88226179ed25d4e50dee06cc17a6f38e61e67617edf9751a88e2cea5112
```

The launcher identity is `/usr/bin/env` SHA-256
`6e506aec3c0cff703ac1e66cedc6f1945354ad41339a38db4425c7c88227128f`;
the resolved Python identity is SHA-256
`b502cb4c5b46b8d4192ec6bcb600ce8922f1afc396fcf646e8765c6eba74a0bf`.
The requested environment must contain exactly the two keys shown above and
the observed clean-launch environment must be exactly those two plus
`LC_CTYPE=C.UTF-8` and
`__CF_USER_TEXT_ENCODING=0x1F5:0x19:0x34`.

Immediately before that launch, Root T0 must recheck this archive's exact
path/SHA, the dispatch SHA/mode/nlink, all six live implementation hashes,
the exact absent root, absence of the one-use ID from consumption records and
absence of a related writer/process.  Root T0's operator record must bind this
archive path and SHA; the immutable dispatch itself is not rewritten.

This archive authorizes one `exec` attempt, not an open-ended retry.  Once the
command is started, this reauthorization is spent regardless of whether the
process later creates the root or exits before consumption.  Any created root
or consumption is governed by the frozen terminal/nonretryable rules.  A
second process launch, another dispatch, a different root, official science,
V3.2 or global GREEN requires new Root-T0 adjudication and is not authorized
here.
