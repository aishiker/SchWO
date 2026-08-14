# T7 package review — V3.1-X final source-ledger repair cycle 2

Date: 2026-08-13

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-X SOURCE-LEDGER REPAIR CYCLE 2 PACKAGE CHANGES REQUIRED
```

This is an archive-only, zero-science package review.  It does not consume
repair cycle 2.  It authorizes no implementation, Wolfram launch, solver,
dispatch, micro/full/official root, V3.2 or global GREEN.

## Verdict record

```yaml
review_id: t7_v3_1_x_source_ledger_repair_cycle2_package_review_20260813
gate_id: phase6_v3_1_x_external_direct_route_v1
repair_id: phase6_v3_1_x_source_ledger_repair_cycle2_v1
attempt: repair_2_package_review
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed

reviewed_candidate:
  root: configs/phase6_v3_1_x_sentinel_repair_cycle2_source_ledger_package.json
  identities:
    - path: configs/phase6_v3_1_x_sentinel_repair_cycle2_source_ledger_package.json
      sha256: 58c4289c6efedde0c48879dcbcdc15064714e493721f79a2d110639eccd9cd43
      size: 9070
      mode: "0644"
      nlink: 1
    - path: docs/phase6_v3_1_x_sentinel_repair_cycle2_source_ledger_design.md
      sha256: 582bc3248a6acf7164485203d317b2cdc0d2a7819a13dcdb584e86e9a90bebdf
      size: 29559
      mode: "0644"
      nlink: 1
    - path: docs/handoffs/archive/T4_2026-08-13_v3_1_x_sentinel_repair_cycle2_source_ledger_design_analysis.md
      sha256: bdbe1c1d05b086cac50d3dd5b99759a5d131b86e73788f92b0788bc9775eba1b
      size: 9645
      mode: "0644"
      nlink: 1
    - path: docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle2_package_review.md
      sha256: 88a1f87d9c1c5bba94ef3c3db83ab5023ddd2b685d9406c0cddc2940bdfb795c
      size: 2297
      mode: "0644"
      nlink: 1
    - path: docs/prompts/phase6_t6_v3_1_x_sentinel_repair_cycle2_source_ledger_implementation.md
      sha256: c0d625896945aa1c5ab09259a458dda90882a499afc5b8fd0b9ff44595a4529c
      size: 3647
      mode: "0644"
      nlink: 1
    - path: docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle2_source_ledger_delta_review.md
      sha256: 6a541ceb99897d65b17449dde13983c1333a630db057c6452d23b60c202e2f66
      size: 2360
      mode: "0644"
      nlink: 1

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle2_package_review.md
    sha256: 88a1f87d9c1c5bba94ef3c3db83ab5023ddd2b685d9406c0cddc2940bdfb795c
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  parent_package:
    path: configs/phase6_v3_1_x_external_direct_route_package.json
    sha256: 6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752
  terminal_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_sentinel_attempt_0002_terminal_review.md
    sha256: 7f002b2e2abb5a80d0836ff4d458a52842af4aad337db0d1e50c8dc1ce8da232
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
  source_snapshot:
    path: runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json
    sha256: 8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488
    files: 25
    directories: 5
    content_inventory_sha256: d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2
    identity_inventory_sha256: a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
  implementation_baseline:
    scripts/phase6_v3_1_x_bhpt_direct.wls: 24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6
    src/schwgw/validation/phase6_v3_external_direct.py: 981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4
    src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py: 81a33a4157d6e07b03621bff069c9383914464c16ce4314a9f7a556c7e1cd088
    scripts/phase6_v3_1_x_external_direct.py: 072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768
    tests/unit/test_phase6_v3_external_direct.py: 056c7273edbdb612d3fc99c4b493f2fe4c96dc15b8ae7aa3a872587f33f3aaba
    tests/regression/test_phase6_v3_external_direct_publication.py: 24d26a8a9c2e0ad573b97f76b39db7743f2d6639cd57978be93f0c310062f858
  protected_identities:
    - {path: src/schwgw/numerics/radial_solver.py, expected_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_start_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9, observed_end_sha256: 9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9}
    - {path: src/schwgw/numerics/conditioned_radial.py, expected_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_start_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2, observed_end_sha256: 91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2}
    - {path: src/schwgw/numerics/scaled_tortoise_radial.py, expected_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_start_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df, observed_end_sha256: d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df}
    - {path: src/schwgw/numerics/adaptive_jost_radial.py, expected_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_start_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896, observed_end_sha256: 3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896}
    - {path: src/schwgw/numerics/matching.py, expected_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_start_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340, observed_end_sha256: 9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340}
    - {path: src/schwgw/numerics/physical_boundary_radial.py, expected_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_start_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f, observed_end_sha256: fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f}
    - {path: src/schwgw/numerics/boundary_conditions.py, expected_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_start_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22, observed_end_sha256: b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22}

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-X SOURCE-LEDGER REPAIR CYCLE 2 PACKAGE CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31x-r2-package-canonical-and-hash-graph
      evidence_identity: package 58c4289c6efedde0c48879dcbcdc15064714e493721f79a2d110639eccd9cd43 is duplicate-free canonical JSON; 5/5 member and 10/10 direct source bindings rehash exact; 40 recursive unique paths are regular nlink1 and exact
    - item_id: v31x-r2-sole-live-science-blocker-reconstruction
      evidence_identity: attempt-0002 request records use object order [context,mode,nlink,path,sha256,size], WLS reconstructs [context,path,sha256,size,mode,nlink], all eight semantic value records match, and rc69 occurs before ReggeWheelerRadial with zero scientific records
    - item_id: v31x-r2-six-field-semantic-projection
      evidence_identity: design freezes one projection [context,path,sha256,size,mode,nlink] for imported expected and independently rebuilt start/end records, exact key/type/value checks and exact positional eight-context list comparison, with no record sorting/set/dedup/drop/fallback
    - item_id: v31x-r2-duplicate-member-preparse-design
      evidence_identity: design requires duplicate-key rejecting raw-byte JSON load and canonical-byte equality in Python before the RawJSON/Wolfram boundary; equal and unequal duplicate members are mandatory negatives
    - item_id: v31x-r2-source-paclet-inode-toctou-closure
      evidence_identity: design requires exact clean pre-load state, Paclet/context/FindFile origin, parent pre/post path/dev/inode/mode/nlink/size/SHA inventories, WLS start/end ledgers, five directory identities and rejection of aliases or same-byte inode replacement
    - item_id: v31x-r2-micro-solver-unreachability-design
      evidence_identity: the authenticated literal source_load_micro_sentinel operation is fixed to V3A-MODE-BHPT-RW-001/P1, requires a second source-ledger check and terminal publication before the first ReggeWheelerRadial expression, and freezes all solver/science counters at zero
    - item_id: v31x-r2-fake-child-nonacceptance
      evidence_identity: synthetic fake_child output is explicitly non-authoritative; only a separately dispatched real Wolfram RawJSON/source-load micro root may satisfy the boundary gate, and micro evidence is forbidden from 35/70/105 or official totals
    - item_id: v31x-r2-distinct-execution-namespaces
      evidence_identity: fixed micro dispatch/root, full attempt-0003 dispatch/repair2 root and unchanged official attempt-0001/root names are unique and absent; attempts 0001/0002 remain explicit nonreuse evidence and global one-use scans are required
    - item_id: v31x-r2-five-path-sufficiency
      evidence_identity: the WLS normalizer/micro branch, producer strict loader/stat/authority/publication, CLI subcommand and two test files fit exactly five unique paths; the direct physics core is excluded and remains SHA 981c2b...8da4
    - item_id: v31x-r2-frozen-graph-and-science-authorities
      evidence_identity: independent zero-science reload yields 23 keys, sentinel 35 calls with P1x23 plus six nodes for ordinals 3/22, and official 161/322/483; method, six overlays, 90/120 ladder, domain, thresholds, convention and seven protected hashes are unchanged
    - item_id: v31x-r2-failed-root-immutability-and-nonreuse
      evidence_identity: attempt0001 is 77 files/9 dirs/720336 bytes, manifest d905500b...1772; attempt0002 is 77/9/720339, manifest 6e0d2349...6109; both are exact 0444/0555 nlink1 terminal FAIL roots with zero scientific records and permanently consumed one-use IDs
    - item_id: v31x-r2-liveness-bound
      evidence_identity: package review does not consume repair2; implementation delta is the final 2/2 repair gate and any delta, real micro or later full-sentinel failure requires ESCALATE with no cycle3
  failed_items:
    - item_id: v31x-r2-micro-terminal-review-machine-authority-unspecified
      blocker_id: v31x-r2-micro-review-authority-contract-missing
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31x-r2-implementation
      reason: no repair-cycle-2 implementation exists or was reviewed
    - item_id: v31x-r2-source-load-micro
      reason: no micro dispatch/root or real RawJSON-to-Wolfram micro result exists
    - item_id: v31x-r2-full-sentinel
      reason: no attempt-0003 dispatch/root exists and 35/70/105 science remains unassessed
    - item_id: v31x-r2-official
      reason: no official dispatch/root is authorized or present
    - item_id: v31x-r2-thresholds-certificates
      reason: all 16 thresholds and five certificates remain unevaluated
    - item_id: v3-2
      reason: V3.2 remains forbidden and was not started

findings:
  - finding_id: v31x-r2-micro-review-authority-contract-missing
    class: BLOCKING_CURRENT_GATE
    summary: The package predeclares a future micro-review archive path but freezes neither a formal micro-terminal review prompt nor the exact machine verdict tokens that the producer must validate before accepting a later full-sentinel dispatch.
    blocker_id: v31x-r2-micro-review-authority-contract-missing
    violated_contract_item: The repair package must define a singular, non-circular, fail-closed authority DAG in which a real zero-science micro root receives formal T7 ADVANCE before any full attempt-0003 dispatch, without T6 inventing an authority mechanism or confusing the micro with the frozen 35-call Substage-B claim.
    exact_evidence: >-
      Package 58c4289c6efedde0c48879dcbcdc15064714e493721f79a2d110639eccd9cd43 names only `future_micro_review=docs/handoffs/archive/T7_2026-08-13_v3_1_x_source_load_micro_sentinel_terminal_review.md`. Its five members contain no micro-terminal review prompt. Design 582bc324...bebdf lines 347-350 says the review must contain exact ADVANCE, claim-status and gate-label tokens, but neither the design, package nor T6 prompt gives their literal values. Repository-wide prompt search finds no V3.1-X source-load micro review prompt or exact label. The only frozen science review 339d5d96...bd7f defines Substage-B GREEN for a completed 35/70/105 scientific sentinel and one-use official dispatch, so using that label for the zero-science micro would be a false authority expansion.
    expected_value: >-
      The package binds one immutable formal micro-terminal review prompt and freezes a literal three-token success envelope: `ADVANCE_DECISION: ADVANCE`, `CLAIM_STATUS: NOT_ASSESSED`, and `GATE_LABEL: ACCEPT GREEN / V3.1-X SOURCE-LOAD MICRO SENTINEL SUFFICIENT FOR ONE-USE FULL SENTINEL DISPATCH`; it also freezes the terminal failure envelope `ADVANCE_DECISION: ESCALATE`, `CLAIM_STATUS: FAIL`, `GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED`. The future full dispatch supplies the review archive's later digest and the producer validates the exact fixed review path, supplied digest, tokens, package/implementation identities and immutable micro root.
    observed_value: >-
      Only the future archive pathname is frozen. Claim status, exact gate label, terminal failure envelope and the micro terminal review procedure are absent. T6 would have to invent those production authority constants or reuse the incompatible 35-call sentinel GREEN label.
    bounded_repair: >-
      Before any T6 dispatch, add one immutable formal micro-terminal review prompt that binds the design/package/implementation review, one-use micro dispatch, exact immutable micro root, one real Wolfram launch, eight start/end source records, rc0/empty-stderr/wait-reap-PG closure, all zero science counters, nonpromotion and no-retry/ESCALATE semantics. Add its path/hash and the literal success/failure tokens to the canonical package. Update only the T6 implementation prompt and future implementation-delta prompt to require the producer's fixed-path plus dispatch-supplied-digest validation of that envelope. Do not change the science design, T4 archive, package-review prompt, source-ledger semantics, five implementation scope, graph or any scientific authority.
    allowed_files:
      - configs/phase6_v3_1_x_sentinel_repair_cycle2_source_ledger_package.json
      - docs/prompts/phase6_t6_v3_1_x_sentinel_repair_cycle2_source_ledger_implementation.md
      - docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle2_source_ledger_delta_review.md
      - docs/prompts/phase6_t7_v3_1_x_source_load_micro_sentinel_terminal_review.md
    recheck_command: >-
      git diff --check --
      configs/phase6_v3_1_x_sentinel_repair_cycle2_source_ledger_package.json
      docs/prompts/phase6_t6_v3_1_x_sentinel_repair_cycle2_source_ledger_implementation.md
      docs/prompts/phase6_t7_v3_1_x_sentinel_repair_cycle2_source_ledger_delta_review.md
      docs/prompts/phase6_t7_v3_1_x_source_load_micro_sentinel_terminal_review.md
    unblock_condition: >-
      A delta-only formal T7 package re-review independently proves exact four-path-or-smaller package correction; duplicate-free canonical package bytes; exact new prompt/member hashes; the literal success and ESCALATE envelopes above; fixed-path/later-dispatch-digest non-circular validation; complete micro raw-root criteria and nonpromotion; unchanged passed items/protected identities; and all corrected package/member authority files sealed regular 0444/nlink1. Only then may T0 dispatch T6 for the still-unconsumed repair cycle 2.
  - finding_id: v31x-r2-package-authority-files-writable
    class: CONTROL_PLANE_REPAIR
    summary: The package and its five members are regular nlink1 and hash-stable but currently mode 0644 rather than the established 0444 frozen-authority mode; the corrected package set must be chmod 0444 without changing bytes before re-review.
  - finding_id: v31x-r2-duplicate-json-boundary
    class: NONBLOCKING_LIMITATION
    summary: Wolfram RawJSON cannot recover duplicate-member history, but the proposed Python raw-byte duplicate-key hook plus canonical-byte equality before child launch is implementable within the producer and is mandatory; no core change is needed.
  - finding_id: v31x-r2-parent-inode-and-wls-source-composition
    class: NONBLOCKING_LIMITATION
    summary: WLS cannot independently establish Darwin inode provenance for every source, but the combined contract is sufficient: WLS binds context/FindFile/path/content at both boundaries while the parent independently binds path/dev/inode/mode/nlink/size/SHA and directory identities before and after the child.
  - finding_id: v31x-r2-no-science-or-downstream-authority
    class: FOLLOW_UP_DEBT
    summary: Package correction or later package GREEN remains readiness only and cannot predict a micro/full sentinel result, authorize official execution, start V3.2 or establish global GREEN.

delta_review: null
hold_details: null

verification:
  commands:
    - SHA-256 and complete reads of the package, all five members, ten source bindings, original package recursion, terminal review and both failed roots
    - independent CPython 3.14 duplicate-key-rejecting package load and canonical UTF-8/sorted-key/indent-2/terminal-newline byte comparison
    - independent recursive unique path/hash/stat/mode/nlink reconstruction over 40 bound authority/source/implementation paths
    - independent manifest/path/SHA/size/mode/nlink rebuild of both failed roots and reload of all 35 outcomes and empty scientific JSONL streams
    - exact CPython 3.14 zero-science graph reconstruction under the frozen mpmath overlay
    - static dataflow review of current overlay materialization, parent file/directory identity functions, WLS Paclet/context/FindFile/sourceRecords/SameQ/ReggeWheelerRadial ordering and proposed design
    - repository-wide search for a frozen source-load micro-terminal prompt and exact micro verdict label
    - authority-path uniqueness/absence, failed one-use/root nonreuse, process absence and targeted git diff-check
  results:
    - package SHA/canonical/duplicate-free parse PASS
    - member hashes 5/5 PASS and direct source bindings 10/10 PASS
    - recursive unique path/hash bindings 40/40 PASS; all regular nlink1
    - new package/member permissions FAIL frozen-authority hardening: six files are 0644, not 0444
    - original package/member/review-basis/snapshot/protected recursion PASS
    - attempt0001 root rebuild PASS: 77 files, nine dirs, 720336 bytes, manifest d905500b...1772, zero scientific records
    - attempt0002 root rebuild PASS: 77 files, nine dirs, 720339 bytes, ledger 1aefc643...6d08, manifest 6e0d2349...6109, zero scientific records
    - graph PASS: 23 keys, sentinel 35/70/105 topology, official 161/322/483 topology
    - six-field projection, duplicate preparse, source/inode/Paclet closure, micro solver-unreachability, fake-child rejection and five-path sufficiency design PASS
    - execution namespace path uniqueness/absence PASS
    - micro terminal machine-authority completeness FAIL: no frozen prompt or exact verdict token envelope
    - no Wolfram/solver/science/dispatch/root process or new execution artifact

non_claims:
  - no repair-cycle-2 implementation acceptance
  - no source-load micro acceptance or evidence
  - no 35-call sentinel numerical PASS and no prediction that its nodes will pass
  - no reuse, retry, resume, promotion or cache use of attempts 0001/0002 or their roots
  - no official V3.1-X execution or evidence
  - no threshold, domain, convention, precision, method, graph, source-snapshot, direct-core or protected-radial change
  - no independent even-sector external evidence
  - no finite-radius observer, Li-figure, full-domain or broader certification claim
  - no V3.2 and no global GREEN

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_science_repairs: 1
  current_bounded_repair: 2
  package_review_consumes_repair_cycle_2: false
  repair_cycle_2_consumed: false
  remaining_bounded_repairs_after_package_correction: 1
  repair_cycle_3_permitted: false
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Independent conclusion

The scientific repair design is bounded and technically adequate: its single
semantic projection removes only Association insertion-order sensitivity,
while exact names/types/values and the frozen eight-record order remain
fail-closed.  Duplicate-member rejection, parent inode/stat closure, exact
Paclet/`FindFile` origin, a pre-solver real micro operation, fake-child
rejection and the five-path implementation scope are all implementable without
changing the direct physics core.

The package is nevertheless not ready for T6.  It asks production code to
authenticate a future micro T7 verdict without freezing the formal prompt or
the exact claim/gate tokens that distinguish a zero-science micro ADVANCE from
the incompatible 35-call sentinel GREEN.  That omission would require T6 to
invent a machine authority and is therefore a current package-level Class-A
blocker.

Root T0 may freeze the four-path bounded package correction specified above
and request only a delta package re-review.  This review does not consume the
final repair cycle.  Until that delta review returns identity-bound ADVANCE,
T6 may not be dispatched.
