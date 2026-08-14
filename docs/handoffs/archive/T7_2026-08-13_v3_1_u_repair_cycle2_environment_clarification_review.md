# T7 formal package review — V3.1-U repair-cycle-2 sentinel environment clarification

Date: 2026-08-13

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 2 ENVIRONMENT CLARIFICATION READY FOR T4
```

## Verdict record

```yaml
review_id: t7_v3_1_u_repair_cycle2_environment_clarification_review_20260813
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
repair_id: phase6_v3_1_u_route_c_totality_repair_cycle2_v1
attempt: repair_2_pre_sentinel_control_plane_clarification
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: authority-only; no implementation delta, dispatch, sentinel or official root is authorized by this file alone
  identities:
    - path: configs/phase6_v3_1_u_repair_cycle2_sentinel_environment_authority.json
      sha256: 936e4a403030d96ce4575e35fbefdff7d6eb29acaad564c137488a27aabec581
      mode: 0444
      nlink: 1

frozen_review_basis:
  predecessor_initial_implementation_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_implementation_delta_review.md
    sha256: 4c4f048eb909f5f714f76d7f6c55c3429da6f80396bd2683976ca4a826df7499
  predecessor_delta_recheck:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_implementation_delta_recheck_1.md
    sha256: c5f827cbbc61c413d269c611e34cf72c72433a63752e71dcace21f670cec4210
  corrected_package:
    path: configs/phase6_v3_1_u_repair_cycle2_package.json
    sha256: 61460a45d4d47ba9247e68969a5d91e2d77aac722c9324014a414ed4126dbfa2
  package_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_package_delta_recheck_1.md
    sha256: f67ce9fa3f0b3f65a7ad34c736c06236f1b0c87674a0e943e8b749f1ca9387e5
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  blocked_item:
    item_id: v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable
    predecessor_evidence: exact two-key requested exec environment becomes exact four-key observed environment after CPython 3.14 startup on the frozen macOS host
  environment_authorities:
    launcher:
      path: /usr/bin/env
      sha256: 6e506aec3c0cff703ac1e66cedc6f1945354ad41339a38db4425c7c88227128f
      size: 102368
    python:
      path: /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14
      sha256: b502cb4c5b46b8d4192ec6bcb600ce8922f1afc396fcf646e8765c6eba74a0bf
      size: 52448
      version: 3.14.6
    platform:
      architecture: arm64
      darwin_kernel_release: 25.5.0
      macos_version: 26.5.2
      macos_build: 25F84
      uid_decimal: 501
    requested_execve_environment:
      PYTHONDONTWRITEBYTECODE: "1"
      PYTHONPATH: runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src
    observed_post_startup_environment:
      LC_CTYPE: C.UTF-8
      PYTHONDONTWRITEBYTECODE: "1"
      PYTHONPATH: runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src
      __CF_USER_TEXT_ENCODING: "0x1F5:0x19:0x34"
    observed_compact_sorted_json_with_terminal_newline_sha256: 275a7c96a039be3a15a61d6ff5f2dd4c5285be0b60759775123c5215289f10bb
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
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 2 ENVIRONMENT CLARIFICATION READY FOR T4

incremental_review_state:
  passed_items:
    - item_id: v31u_repair2_requested_observed_environment_contract_ready
      evidence_identity: authority 936e4a403030d96ce4575e35fbefdff7d6eb29acaad564c137488a27aabec581 binds exact requested two-key map, exact observed four-key map, launcher, CPython, host, cwd and argv without wildcard, prefix, subset, projection or ignored keys
    - item_id: v31u_repair2_environment_probe_reproducible
      evidence_identity: three env-i and three direct-execve probes independently reproduced the same four-key compact canonical map SHA 275a7c96a039be3a15a61d6ff5f2dd4c5285be0b60759775123c5215289f10bb with science_calls=0
    - item_id: v31u_repair2_environment_authority_non_circular
      evidence_identity: requested environment is an exact T0-dispatch/launcher authority and is explicitly not inferred from observed os.environ; observed environment is independently checked as exact full map; dispatch must bind this immutable authority and root consumption must persist both forms
    - item_id: v31u_repair2_environment_extra_authority_rejected_by_contract
      evidence_identity: missing, changed or extra requested/observed key is forbidden before dispatch consumption; arbitrary, prefix and environment-derived root/dispatch/source/method/fallback selection are all false
    - item_id: v31u_repair2_future_scope_exact_three
      evidence_identity: allowed future implementation scope is exactly HP producer, HP unit test and HP regression test; WLS, cycle2 module, cycle2 unit, CLI, oracle, science and protected sources are excluded
    - item_id: v31u_repair2_loaded_source_closure_pass_frozen
      evidence_identity: WLS 894bb2ebe6bd9637e3e449e7785241085de0f673ad93ebbf7865c4a5023b888f, cycle2 module 60fdc7c3f46ab21eafbe2b319f0c7b15b3ab64d6633d360f79ada078dcbd36b1 and cycle2 unit 47e29bf2ee0c900aaff1153ebee31848916b8c94b5de7e488220ef0f457b5323 remain exact; loaded-source closure is PASS_FROZEN
    - item_id: v31u_repair2_predecessor_and_protected_bindings
      evidence_identity: all six predecessor authorities, three unchanged passed paths and seven protected radial identities rehash exact at start/end
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_repair2_environment_implementation
      reason: the exact three-path implementation delta has not yet been made or reviewed
    - item_id: v31u_repair2_sentinel_science
      reason: no sentinel dispatch/root exists and repair cycle 2 remains unconsumed
    - item_id: v31u_repair2_official_science
      reason: no official dispatch/root exists; V3.1-U science remains NOT_ASSESSED

findings:
  - finding_id: v31u_repair2_environment_clarification_authority_ready
    class: CONTROL_PLANE_REPAIR
    summary: The authority non-circularly separates the exact requested execve environment from the exact deterministic post-startup environment while keeping all caller extras and authority surfaces fail-closed; it changes no science.
  - finding_id: v31u_repair2_host_specific_environment_authority
    class: NONBLOCKING_LIMITATION
    summary: The observed environment is deliberately bounded to the exact frozen macOS/arm64/UID/CPython/launcher identities; platform, user, binary or injected-value drift requires a new authority rather than fallback or normalization.
  - finding_id: v31u_repair2_science_not_assessed
    class: NONBLOCKING_LIMITATION
    summary: Authority readiness neither executes nor accepts Route-C or any V3.1-U scientific result.
  - finding_id: v31u_repair2_v3_2_forbidden
    class: FOLLOW_UP_DEBT
    summary: V3.2, broader V3 claims and global GREEN remain outside and forbidden.

delta_review:
  reviewed_failed_items:
    - v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable
  passed_invariants_rechecked:
    - v31u_repair2_loaded_source_snapshot_closure_closed
    - v31u_repair2_exact_six_scope_and_identity_preserved
    - v31u_repair2_anchor_graph_and_wls_totality_preserved
    - v31u_repair2_durable_child_supervision_preserved
    - v31u_repair2_sentinel_official_separation_preserved
    - v31u_repair2_snapshot_byte_identity_preserved
    - v31u_repair2_zero_science_and_protected_invariants_preserved
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - complete authority/predecessor/liveness/template read and start/end SHA-256, mode, nlink and canonical JSON verification
    - independent rehash/stat/version of /usr/bin/env and exact CPython 3.14.6 executable; uname, sw_vers and uid verification
    - three zero-science /usr/bin/env -i probes with the exact requested environment and exact CPython command
    - three zero-science direct os.execve probes with exactly the two requested entries
    - independent compact sorted JSON plus terminal-newline SHA rebuild of every observed map
    - in-memory exact-map adversaries for extra, missing and changed requested and observed keys
    - read-only absence/process checks for sentinel/official dispatches, repair2 roots, Wolfram and science processes
  results:
    - authority is regular 0444/nlink1 canonical pretty JSON with exact SHA-256 936e4a403030d96ce4575e35fbefdff7d6eb29acaad564c137488a27aabec581
    - /usr/bin/env rehashes 6e506aec3c0cff703ac1e66cedc6f1945354ad41339a38db4425c7c88227128f at 102368 bytes; CPython rehashes b502cb4c5b46b8d4192ec6bcb600ce8922f1afc396fcf646e8765c6eba74a0bf at 52448 bytes and reports 3.14.6
    - host identities are arm64, Darwin 25.5.0, macOS 26.5.2 build 25F84 and uid 501
    - all six probes returned exactly LC_CTYPE=C.UTF-8, the two requested entries and __CF_USER_TEXT_ENCODING=0x1F5:0x19:0x34, with map SHA 275a7c96a039be3a15a61d6ff5f2dd4c5285be0b60759775123c5215289f10bb
    - requested/observed extra, missing and changed variants are unequal to their literal authorities; no subset/prefix/projection/normalization surface exists in the frozen contract
    - all predecessor, loaded-source-passed and protected identities are exact; dispatches/roots are absent; no science process exists and zero science call was made

non_claims:
  - this GREEN approves only the bounded environment clarification contract
  - V3.1-U science and the future three-path implementation remain NOT_ASSESSED
  - repair cycle 2 remains unconsumed
  - no dispatch, sentinel, official run, WolframKernel, solver or artifact reuse is authorized
  - no V3.2, broader V3 claim or global GREEN is authorized

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 1
  current_bounded_scientific_repair: 2
  repair_cycle2_consumed: false
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Independent assessment

The clarification is scientifically inert and control-plane complete. It does
not reinterpret the four observed keys as four caller-authority keys. Instead,
the caller boundary remains exactly the original two-key `execve` map under an
exact hashed `/usr/bin/env -i` launcher, while the module boundary validates
the complete literal four-key post-startup map. The requested state is bound
by the later T0 dispatch and cannot be inferred from the observation; the
observation accepts no wildcard, prefix, subset, projection or ignored entry.
Both forms must be persisted in root-local dispatch consumption evidence.

This closes the contract ambiguity without weakening rejection of caller
extras or permitting environment-selected root, dispatch, source, method or
fallback behavior. Any host, UID, OS, binary, key or value drift fails closed.

## Downstream boundary

Root T0 may dispatch only a zero-science T4 edit of these exact paths:

1. `src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py`
2. `tests/regression/test_phase6_v3_hp_unitarity_publication.py`
3. `tests/unit/test_phase6_v3_hp_unitarity.py`

The implementation must bind authority SHA-256
`936e4a403030d96ce4575e35fbefdff7d6eb29acaad564c137488a27aabec581`,
validate and persist both environment forms, and return for a delta-only T7
recheck. This review does not authorize creation of a sentinel dispatch/root,
sentinel or official execution, V3.2, or global GREEN.
