# T7 formal implementation delta recheck 1 — V3.1-U repair cycle 2

Date: 2026-08-13

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-U REPAIR CYCLE 2 IMPLEMENTATION CHANGES REQUIRED
```

## Verdict record

```yaml
review_id: t7_v3_1_u_repair_cycle2_implementation_delta_recheck_1_20260813
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
repair_id: phase6_v3_1_u_route_c_totality_repair_cycle2_v1
attempt: repair_2_delta_recheck_1
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: implementation-only; no sentinel or official dispatch/root exists
  identities:
    - path: scripts/phase6_v3_1_bhpt_mst_cycle2.wls
      sha256: 894bb2ebe6bd9637e3e449e7785241085de0f673ad93ebbf7865c4a5023b888f
    - path: src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py
      sha256: 60fdc7c3f46ab21eafbe2b319f0c7b15b3ab64d6633d360f79ada078dcbd36b1
    - path: src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      sha256: 73a85e4cc072afa55135a1ef528994b3296f7373fcd15360f03e7bdfd334f49a
    - path: tests/regression/test_phase6_v3_hp_unitarity_publication.py
      sha256: 142e0cdcd0a1e7e079180d9c8323f9e3d1aae0904f96fc457f8bc4642be6feef
    - path: tests/unit/test_phase6_v3_cycle2.py
      sha256: 47e29bf2ee0c900aaff1153ebee31848916b8c94b5de7e488220ef0f457b5323
    - path: tests/unit/test_phase6_v3_hp_unitarity.py
      sha256: dda2478a811c32c3008b7d4435c5622a524989b3f05ada855fe1dcf0e30efbd9

frozen_review_basis:
  predecessor_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_implementation_delta_review.md
    sha256: 4c4f048eb909f5f714f76d7f6c55c3429da6f80396bd2683976ca4a826df7499
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_delta_review.md
    sha256: ca46dac66d322c3953e7a926d62f46ff19be48ec161a97c7b42aa0e83043335f
  package:
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
  unchanged_cli:
    path: scripts/phase6_v3_1_hp_unitarity.py
    sha256: 01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4
  unchanged_route_u_oracle:
    path: src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py
    sha256: a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7
  t4_zero_science_evidence:
    evidence_sha256: 4fd6ed8c3e6fdaaf487ee2d3d08793a6eaad66ba3f62bd30eaa09cebb11304a6
    inventory_sha256: 14d83f6cf935d463981f298e1bdc3eb752a2d5131c08c635fa23460c3683e65f
    junit_sha256: 76a3b59061d2197bd2329f5adbf0f68715358a88d64dcfb71c4007a2b8d10526
    synthetic_manifest_sha256: a130e48851ded30fdd26aca64afd79cac3902661e2dcd06ca437ee2fe030ada8
  protected_identities:
    - path: src/schwgw/numerics/radial_solver.py
      sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
    - path: src/schwgw/numerics/conditioned_radial.py
      sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
    - path: src/schwgw/numerics/scaled_tortoise_radial.py
      sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
    - path: src/schwgw/numerics/adaptive_jost_radial.py
      sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
    - path: src/schwgw/numerics/matching.py
      sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
    - path: src/schwgw/numerics/physical_boundary_radial.py
      sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
    - path: src/schwgw/numerics/boundary_conditions.py
      sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-U REPAIR CYCLE 2 IMPLEMENTATION CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31u_repair2_loaded_source_snapshot_closure_closed
      evidence_identity: exact eight ordered unique loaded-source records with path/sha256/size; complete 25-file and five-directory source closure at start/end; WLS and Python inventories agree; all requested missing/duplicate/reordered/extra/outside/alias/hash/size/mode/symlink/hardlink adversaries pass fail-closed tests
    - item_id: v31u_repair2_exact_six_scope_and_identity_preserved
      evidence_identity: current six hashes exactly match the dispatched delta set; comparison to package baselines changes only the six allowed paths
    - item_id: v31u_repair2_anchor_graph_and_wls_totality_preserved
      evidence_identity: exact ordered 23 odd anchors, one MapIndexed traversal, one ReggeWheelerRadial call site, and unchanged MST/90/45/45 plus PASS/ERROR outcome grammar
    - item_id: v31u_repair2_durable_child_supervision_preserved
      evidence_identity: source start/end, request/prelaunch/raw streams/receipt/wait/reap/process-group and exclusive terminal branch tests remain PASS
    - item_id: v31u_repair2_sentinel_official_separation_preserved
      evidence_identity: fixed dispatch, no-reuse, wrong-root/review/hash rejection and official-before-sentinel guards remain unchanged
    - item_id: v31u_repair2_snapshot_byte_identity_preserved
      evidence_identity: 25 regular 0444/nlink1 files, five 0555 directories, no link/.git drift, content index d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2 and restored identity index a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
    - item_id: v31u_repair2_focused_quality_checks_preserved
      evidence_identity: exact CPython 3.14 overlay focused suite 101 passed; JUnit 76a3b59061d2197bd2329f5adbf0f68715358a88d64dcfb71c4007a2b8d10526; CLI preflight PASS; Python Ruff/format/compile and exact-six diff-check PASS
    - item_id: v31u_repair2_zero_science_and_protected_invariants_preserved
      evidence_identity: zero Wolfram/sentinel/official/solver/science; dispatch and repair2 roots absent; CLI, oracle, package authorities and all seven protected radial hashes exact at start/end
  failed_items:
    - item_id: v31u_route_c_external_totality_and_provenance
      blocker_id: v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_repair2_sentinel_science
      reason: sentinel dispatch/root are absent; repair cycle 2 is not consumed
    - item_id: v31u_repair2_official_science
      reason: official dispatch/root are absent; V3.1-U science remains NOT_ASSESSED
    - item_id: v31u_repair2_thresholds_and_certificates
      reason: no official candidate exists; 16 thresholds and five certificates are not evaluated

findings:
  - finding_id: v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable
    class: BLOCKING_CURRENT_GATE
    summary: The projection false acceptance is removed, but exact comparison of complete post-startup os.environ to the two-key package map rejects the legitimate frozen CPython 3.14 process because macOS/Python inject two deterministic runtime keys before module validation.
    blocker_id: v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable
    violated_contract_item: The predecessor Class-A unblock condition required both rejection of every unreviewed caller-supplied environment entry and successful passage of the exact reviewed real invocation. It explicitly required Root T0 to freeze a bounded clarification if unavoidable platform-injected keys made the literal two-key contract impossible.
    exact_evidence: src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py now passes dict(os.environ) directly, closing the prior projection bypass. Unit tests pass only by monkeypatching os.environ to the two-key map. Independent zero-science process probes used both /usr/bin/env -i and direct os.execve with exactly PYTHONDONTWRITEBYTECODE=1 and the frozen PYTHONPATH. In both cases CPython 3.14 observed four keys: the frozen two plus LC_CTYPE=C.UTF-8 and __CF_USER_TEXT_ENCODING=0x1F5:0x19:0x34. Calling _validate_current_sentinel_runtime with the exact frozen argv then failed with Route-C sentinel invocation mismatch before any authority consumption. Thus a real exact launch cannot satisfy the implemented two-key equality on this frozen host.
    expected_value: A package-bound, non-circular environment contract must distinguish the exact two-key requested execve environment from a separately frozen and validated post-startup observed environment containing only explicitly allowed deterministic platform/interpreter additions. It must continue to reject every caller-supplied extra, missing/changed frozen key and every environment authority/fallback surface, while the actual reviewed CPython 3.14 module entry passes.
    observed_value: In-memory exact-two tests pass and arbitrary-extra tests fail, but the legitimate real CPython process always contains LC_CTYPE and __CF_USER_TEXT_ENCODING and is rejected. No sentinel can reach dispatch validation under the frozen invocation.
    bounded_repair: Root T0 must first freeze a minimal control-plane clarification for requested-versus-observed environment semantics. Bind the requested execve environment exactly to the existing two keys; bind an exact, finite set and values/derivation for unavoidable CPython/macOS additions; persist both requested and observed forms; reject all other keys and all drift. Then update only the sentinel producer and its unit/regression tests. Do not silently ignore arbitrary keys, broaden to prefixes, read authority from environment, modify science, or create a dispatch/root.
    allowed_files:
      - a new immutable bounded control-plane clarification authority selected by Root T0
      - src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
      - tests/unit/test_phase6_v3_hp_unitarity.py
      - tests/regression/test_phase6_v3_hp_unitarity_publication.py
    fresh_root_rule: Sentinel and official dispatches/roots must remain absent. Only zero-science subprocess/in-memory tests may be used. No failed, synthetic or future sentinel science may be promoted; repair cycle 2 remains unconsumed.
    required_tests_preflight: Use direct subprocess/execve tests under exact CPython 3.14, not only monkeypatched os.environ. Prove the frozen requested environment leads to the exact accepted observed environment; arbitrary extra, SCHWO key, missing/changed frozen key, changed platform key, omitted required observed key, extra argv and alternate invocation all fail before dispatch consumption. Re-run the focused 101-test set, CLI preflight, Ruff/format/compile/diff and zero-call/root-absence checks.
    recheck_command: /usr/bin/env -i PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -c 'import os; print(sorted(os.environ.items()))' && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_cycle2.py tests/unit/test_phase6_v3_hp_unitarity.py tests/regression/test_phase6_v3_hp_unitarity_publication.py
    unblock_condition: A frozen requested/observed environment authority exists; the actual exact CPython 3.14 module-entry path passes from a clean requested environment; every caller-added or drifted key fails before authority consumption; exact loaded-source closure remains PASS; all focused/quality/identity/zero-science checks pass; dispatch and repair2 roots remain absent.

  - finding_id: v31u_repair2_loaded_source_snapshot_closure_closed
    class: CONTROL_PLANE_REPAIR
    summary: The prior loaded-source/snapshot false acceptance is closed by an exact eight-record runtime inventory, complete source-tree closure including directory modes, and direct adversarial tests; no scientific method or source byte changed.
  - finding_id: v31u_repair2_snapshot_commit_association_inherited_only
    class: NONBLOCKING_LIMITATION
    summary: The restored snapshot has no .git; commit association remains inherited from the immutable historical ledger and byte-identical audit archive rather than independently asserted.
  - finding_id: v31u_repair2_science_not_assessed
    class: NONBLOCKING_LIMITATION
    summary: No sentinel or official run occurred; Route-C, thresholds, certificates and V3.1-U science remain NOT_ASSESSED.
  - finding_id: v31u_repair2_v3_2_forbidden
    class: FOLLOW_UP_DEBT
    summary: V3.2, broader V3 claims and global GREEN remain outside and forbidden.

delta_review:
  reviewed_failed_items:
    - v31u_repair2_sentinel_runtime_environment_allowlist_false_acceptance
    - v31u_repair2_loaded_source_snapshot_closure_false_acceptance
  closed_failed_items:
    - v31u_repair2_loaded_source_snapshot_closure_false_acceptance
  remaining_failed_items:
    - v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable
  passed_invariants_rechecked:
    - v31u_repair2_exact_six_scope_and_identity_preserved
    - v31u_repair2_anchor_graph_and_wls_totality_preserved
    - v31u_repair2_durable_child_supervision_preserved
    - v31u_repair2_sentinel_official_separation_preserved
    - v31u_repair2_snapshot_byte_identity_preserved
    - v31u_repair2_focused_quality_checks_preserved
    - v31u_repair2_zero_science_and_protected_invariants_preserved
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - start/end SHA-256 reload of predecessor review, frozen prompt/package/package-review, exact-six, CLI, oracle and seven protected radial files
    - static/dataflow delta inspection limited to complete os.environ validation, eight loaded-source WLS/Python closure, source-tree directory/file identity and affected adversarial tests
    - exact CPython 3.14 overlay focused pytest, Python-only Ruff/format/compile, exact-six diff-check and unchanged CLI preflight
    - independent in-memory exact/extra-environment and exact/single/duplicate-loaded-source adversaries
    - independent /usr/bin/env -i and direct os.execve CPython 3.14 probes with only the frozen requested environment
    - read-only dispatch/root/process absence checks; no WolframKernel, sentinel, official, radial or AP solve
  results:
    - exact-six, CLI, oracle, package, predecessor-review and protected identities are exact at start/end
    - 101 focused tests passed in 4.56 seconds; JUnit SHA-256 is 76a3b59061d2197bd2329f5adbf0f68715358a88d64dcfb71c4007a2b8d10526
    - Python Ruff and format checks PASS; five Python files compile; exact-six diff-check PASS; CLI preflight reports v3_1_u_preflight=PASS
    - exact two-key in-memory environment passes and arbitrary extra is rejected, but real clean CPython startup adds LC_CTYPE and __CF_USER_TEXT_ENCODING and the actual runtime validator rejects that legitimate process
    - exact eight loaded sources pass; single and duplicate inventories fail; full missing/duplicate/reordered/extra/path/hash/size/schema and snapshot tree adversaries pass fail-closed tests
    - WLS freezes the exact eight loaded contexts/paths, checks uniqueness/order against FindFile, and publishes ordered path/hash/size records; method and 23-outcome logic remain unchanged
    - sentinel/official dispatches and repair2 roots are absent; no relevant science process exists; science call count is zero

non_claims:
  - V3.1-U science is NOT_ASSESSED
  - no Route-C record, threshold or certificate is accepted
  - repair cycle 2 is not consumed because no sentinel dispatch or launch occurred
  - no one-use sentinel dispatch, sentinel execution, official dispatch/run, failed-root reuse or artifact promotion is authorized
  - no V3.2, broader V3 claim or global GREEN is authorized

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 1
  current_bounded_scientific_repair: 2
  repair_cycle2_consumed: false
  same_substantive_blocker_remaining: true
  bounded_pre_sentinel_control_plane_correction_available: true
  t0_adjudication_required: false
```

## Independent delta conclusion

The loaded-source and snapshot-closure blocker is closed without changing the
external method or any scientific source byte. The implementation now requires
the exact eight actually loaded numerical sources, rejects incomplete and
duplicate reports, and revalidates the complete 25-file/five-directory tree.

The environment blocker is not closed. The new code correctly stops hiding
arbitrary extra entries, but it equates the requested two-key exec environment
with the post-startup Python environment. On the frozen macOS host, both a
clean `env -i` launch and direct `execve` add `LC_CTYPE` and
`__CF_USER_TEXT_ENCODING` before validation. The exact legitimate invocation
therefore fails before reading or consuming its dispatch. Monkeypatched tests
cannot establish real launchability.

## Downstream boundary

Root T0 may freeze one bounded, pre-sentinel control-plane clarification and
request a delta-only recheck. Root T0 may not yet create or consume the
sentinel dispatch. Repair cycle 2 remains unconsumed. This review authorizes no
WolframKernel/sentinel/official science, V3.2 or global GREEN.
