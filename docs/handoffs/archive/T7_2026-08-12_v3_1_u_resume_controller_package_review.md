# T7 V3.1-U resume-controller package review

Date: 2026-08-12

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-U RESUME-CONTROLLER REPAIR PACKAGE CHANGES REQUIRED
```

```yaml
review_id: t7_v3_1_u_resume_controller_package_review_20260812
gate_id: phase6_v3_1_u_resume_controller_repair_1
attempt: repair_1
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: configs/phase6_v3_1_u_resume_controller_package.json
  identities:
    - path: configs/phase6_v3_1_u_resume_controller_package.json
      sha256: 5dce56e5848af09f3b618332927eb90d44feaf6b6db78eaa54f59dc5ba827388
    - path: docs/phase6_v3_1_u_resume_controller_design.md
      sha256: 9660dc5d061c3224f04192bd18e21c1eb547705ca04fa87564bb04f04049b812
    - path: docs/prompts/phase6_t4_v3_1_u_resume_controller.md
      sha256: 605ea95019b9fcfb31a26036d033ef12913dd7f3aabe3ac961a7d023fe99765d
    - path: docs/prompts/phase6_t7_v3_1_u_resume_controller_delta_review.md
      sha256: c5c681d6f7d5a3fdf6c532f9867357726f797fb78cac66087e5ecff458ed9651

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_u_resume_controller_package_review.md
    sha256: 412521ae7976a626f61122790aab85fe7435c345fa59bcc4016e54204ff89f04
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - id: V3.1 frozen threshold set
      value: 16 unchanged threshold IDs/operators/values
      units: mixed dimensionless/logarithmic
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  blocking_criteria:
    - exact interrupted prefix and no live writer
    - exclusive stale-lock takeover with no unowned path window
    - authority publication before science and crash-safe monotone attempt chain
    - prepared/append/checkpoint/commit crash consistency without truncation or rewrite
    - second system interruption safely resumable
    - scientific/provenance/threshold/nonfinite failures terminal and non-resumable
    - original live-source validation plus additive resume validation
    - archive-only coordination identity preservation
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
GATE_LABEL: REVIEW YELLOW / V3.1-U RESUME-CONTROLLER REPAIR PACKAGE CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31ur_identity_and_archive_governance
      evidence_identity: all frozen package/source/protected hashes exact; status/T0_current/T7_current exact at start and end
    - item_id: v31ur_interrupted_prefix
      evidence_identity: records 435/943913/932129a4; ladders 8700/16898419/8f387abb; checkpoints 435/map 2269f129; next key (8,28,even)
    - item_id: v31ur_interruption_classification
      evidence_identity: all JSONL/checkpoint bytes parse as a finite contiguous COMPUTED_NOT_ACCEPTED prefix; no failure/threshold/terminal/U/B/C artifact, live process or open writer fd
    - item_id: v31ur_scope_and_science_preservation
      evidence_identity: exactly four allowed new implementation/test paths, all absent; original five science paths and seven protected paths excluded and unchanged
    - item_id: v31ur_source_and_terminal_validation
      evidence_identity: original source_start byte identity and validate_live_sources=True remain mandatory; additive validator and manifest binding are required
    - item_id: v31ur_real_root_prohibition
      evidence_identity: T4 prompt forbids real-root mutation before implementation delta review and requires actual-prefix temp-copy testing
  failed_items:
    - item_id: v31ur_lock_authority_crash_chain
      blocker_id: v31ur_lock_authority_publication_not_interruption_atomic
    - item_id: v31ur_transaction_partial_suffix_recovery
      blocker_id: v31ur_prepared_append_protocol_not_second_interrupt_resumable
  partial_allowed_items:
    - item_id: v31u_common_absolute_phase
      reason: remains the frozen PARTIAL convention limitation and is not changed by this controller package
  not_assessed_items:
    - item_id: v31u_science
      reason: no resumed Route-A, Route-U, Route-B, Route-C, threshold or certificate result has been produced or reviewed
    - item_id: v31ur_controller_implementation
      reason: the four allowed implementation/test files do not yet exist
    - item_id: v3_2_and_global_project_state
      reason: outside this controller package and unauthorized

findings:
  - finding_id: v31ur_lock_authority_crash_chain_finding
    class: BLOCKING_CURRENT_GATE
    summary: The specified stale-lock rename followed by new-lock creation and in-place authority publication has interruption windows with no defined reconstructable monotone-attempt recovery.
    blocker_id: v31ur_lock_authority_publication_not_interruption_atomic
    violated_contract_item: Required checks 5, 7 and 8 require real atomic exclusion, authority before science, and safe second-system-interruption resume through a monotone attempt chain.
    exact_evidence: docs/phase6_v3_1_u_resume_controller_design.md lines 118-142 rename .writer.lock before creating its replacement and publish final authority files with O_EXCL/fsync; no stable never-renamed exclusion object, atomic swap, authority prepare/commit marker, or recovery rule exists for interruption after rename or during authority publication.
    expected_value: At every lock-takeover and authority-publication boundary there is exactly one discoverable held/stale exclusion identity, and after owner death the next attempt can deterministically validate the prior state and publish a monotone successor before any science call.
    observed_value: A crash after stale-lock rename but before replacement creation leaves .writer.lock absent; a crash during an O_EXCL authority write can leave a partial final-name authority. The next attempt is simultaneously required to validate a full prior authority chain, but the package defines no legal recovery for either state.
    bounded_repair: Freeze a stable exclusion mechanism that is never absent during handoff (for example a separately bound controller lock or an atomic old/new lock swap), and freeze atomic prepared-to-committed publication plus explicit recovery for every authority file and every interruption point before science. Preserve all incomplete attempts as evidence and reject live/concurrent/aliased states.
    allowed_files:
      - configs/phase6_v3_1_u_resume_controller_package.json
      - docs/phase6_v3_1_u_resume_controller_design.md
      - docs/prompts/phase6_t4_v3_1_u_resume_controller.md
      - docs/prompts/phase6_t7_v3_1_u_resume_controller_delta_review.md
      - docs/prompts/phase6_t7_v3_1_u_resume_controller_package_review.md
    recheck_command: PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_hp_unitarity_resume.py tests/regression/test_phase6_v3_hp_unitarity_resume_publication.py -k 'lock or authority or interruption'
    unblock_condition: A corrected frozen package and real-filesystem zero-solver tests demonstrate exclusive single-controller ownership and successful next-attempt reconstruction after forced process death at every stale-lock handoff and authority publication boundary, with no missing-lock gap, partial final authority, manual deletion or science call.

  - finding_id: v31ur_transaction_partial_suffix_recovery_finding
    class: BLOCKING_CURRENT_GATE
    summary: The prepared/append protocol declares every torn line terminal even when it is an exact prefix of a frozen prepared payload, contradicting the package's unconditional second-system-interruption resume claim.
    blocker_id: v31ur_prepared_append_protocol_not_second_interrupt_resumable
    violated_contract_item: Required checks 6 and 8 require crash-consistent intent/prepared/append/checkpoint/commit handling and safe resume after a second system interruption without truncation, rewrite or re-solving committed/prepared science.
    exact_evidence: docs/phase6_v3_1_u_resume_controller_design.md lines 151-168 use in-place O_EXCL prepared publication and O_APPEND data writes, but enumerate only absent suffix, complete suffix, missing checkpoint and committed recovery; line 167 classifies every torn line as terminal. The package does not distinguish an exact existing prefix of the authenticated prepared bytes from an unknown suffix.
    expected_value: After forced death at every prepared/data/checkpoint/commit write boundary, an exact prepared-prefix suffix can be completed byte-for-byte without truncate/rewrite/re-solve, while any byte mismatch or unauthenticated suffix fails closed.
    observed_value: A system interruption can leave a partial prepared final file or a partial canonical JSONL block. Both are reachable before fsync/commit, but neither has a resumable rule; the blanket torn-line rule consumes the root despite the package's second-interruption-resumable claim.
    bounded_repair: Atomically publish prepared/checkpoint/commit records, define byte-prefix recovery for only the exact authenticated prepared payload, append only its missing suffix under the stable lock, and retain terminal fail-closed behavior for any mismatch, unknown bytes, duplicate or gap. Add forced-death tests at every byte/publication boundary for Route A/U/B and staged Route C.
    allowed_files:
      - configs/phase6_v3_1_u_resume_controller_package.json
      - docs/phase6_v3_1_u_resume_controller_design.md
      - docs/prompts/phase6_t4_v3_1_u_resume_controller.md
      - docs/prompts/phase6_t7_v3_1_u_resume_controller_delta_review.md
      - docs/prompts/phase6_t7_v3_1_u_resume_controller_package_review.md
    recheck_command: PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q tests/unit/test_phase6_v3_hp_unitarity_resume.py tests/regression/test_phase6_v3_hp_unitarity_resume_publication.py -k 'prepared or append or checkpoint or commit or interruption'
    unblock_condition: A corrected frozen contract and real-filesystem zero-solver tests prove deterministic byte-identical continuation after process death at every prepared/append/checkpoint/commit boundary, including exact partial prepared payloads and JSONL suffixes, while unknown/tampered suffixes remain terminal and no existing byte is truncated or rewritten.

  - finding_id: v31ur_historical_cause_scope
    class: NONBLOCKING_LIMITATION
    summary: The root proves an exact unfinished finite prefix with no failure surface or live writer; it does not by itself encode the external lifecycle event that terminated the original process, so the review does not infer a more specific historical signal or host cause.
  - finding_id: v31ur_future_science
    class: FOLLOW_UP_DEBT
    summary: V3.1-U science, thresholds, certificates and any V3.2 decision remain future separately gated work.

delta_review:
  reviewed_failed_items:
    - v31u_missing_resume_controller_control_plane
  passed_invariants_rechecked:
    - exact 435-mode and 8700-node original prefix
    - 435-checkpoint identity map
    - original five science-source identities
    - seven protected radial identities
    - frozen coordination identities
    - no U/B/C/terminal/live-writer state
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - sha256sum all four candidate files, review prompt, all package source bindings, seven protected files and three frozen coordination files
    - independent CPython 3.14 JSON/JSONL reload of inventory, 435 records, 8700 ladders and 435 checkpoints without importing or calling a project solver
    - independent compact checkpoint identity-map reconstruction using sort_keys=true, separators=(',',':') and no newline
    - stat inspection of root/data/checkpoint/lock device, inode, mode and nlink
    - lsof on .writer.lock, records.jsonl and ladder_records.jsonl plus exact-root process scan
    - git diff --check on the five review-package files
  results:
    - candidate and package bindings exact; diff-check PASS
    - exact contiguous Route-A ordinals 0..434 and 20 ladder nodes per mode PASS
    - checkpoint map digest 2269f129814c26d609cf3fdd0a451a5fd35661a576cf4d030f4f7b9516366d11 PASS
    - next key is exactly kM=8, ell=28, even; remaining Route A count 61
    - records and ladders hashes/sizes/devices/inodes/modes/nlinks match package; last checkpoint c61e44e027d05d65a5c8a39868cc138fb4b72df7e6efb6d014d9e03c666ce986
    - all loaded numeric values finite; no U/B/C/failure/threshold/terminal/resume artifact exists
    - no live exact-root writer or writable open fd observed; no link/hardlink drift
    - all four allowed implementation/test paths absent
    - no radial, AP or Wolfram solve executed
    - status.md, T0_current.md and T7_current.md remained byte-identical

non_claims:
  - V3.1-U science remains NOT_ASSESSED
  - no threshold or certificate result is accepted
  - no reuse or promotion of predecessor r3
  - common absolute phase remains PARTIAL
  - no V3.2 authorization
  - no full-domain V3 or Li-figure equivalence
  - no global GREEN

repair_cycle:
  completed_bounded_repairs: 0
  same_substantive_blocker_remaining: true
  t0_adjudication_required: false
```

## Review conclusion

The interrupted scientific prefix itself is exact and suitable as a frozen
input to a resume-controller design.  The package also correctly separates
control-plane readiness from scientific acceptance and excludes every science,
threshold, protected and current-handoff edit.

The package is not yet sufficient for T4, however, because its own required
second-interruption guarantee is not closed by the specified state machine.
The lock handoff can be interrupted after the stale pathname is removed and
before the replacement/authority chain is durably complete.  Independently,
an exact partial write of a prepared payload or its authenticated JSONL suffix
has no resumable state even though it is distinguishable from unknown data.
These are reachable control-plane states, not hypothetical scientific
failures.  They can be repaired without changing any frozen science byte,
formula, domain, threshold or evidence prefix, but they must be frozen and
reviewed before implementation or real-root authority.
