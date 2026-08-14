# T7 initial package review — V3.1-Y external protocol

Review date: 2026-08-13 UTC

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-Y EXTERNAL PROTOCOL PACKAGE CHANGES REQUIRED
```

This is the initial, archive-only, zero-science review of
`phase6_v3_1_y_external_protocol_v1`.  V3.1-Y is a distinct gate after the
terminal V3.1-U/V3.1-X branches; this review is not X repair cycle 3.  No
Wolfram kernel, BHPT/AP/radial solver, scientific producer, dispatch or run
root was started or created.

The candidate is not executable as frozen.  Three complete current-gate
blockers remain: the predicate registry has two incompatible expansions and
no operation-specific stage profile; the checkpoint/ACK wire schema cannot
represent the claimed prefix/final-stage and parent-only authority chain; and
the fixed Route-U `318/954` graph contradicts the explicit prohibition on
reusing the failed predecessor's data-derived 318-key route map.

## Verdict record

```yaml
review_id: t7_v3_1_y_external_protocol_package_initial_20260813
gate_id: phase6_v3_1_y_external_protocol_v1
attempt: initial
reviewer_task: 019f5ed1-b421-7ec2-9bac-8d134855a1ed

reviewed_candidate:
  root: configs/phase6_v3_1_y_external_protocol_package.json
  identities:
    - path: configs/phase6_v3_1_y_external_protocol_package.json
      sha256: bbb9e97636a8da63d6e29be2a013fb99f09c8667a1608688de03006a9d916203
      mode: "0444"
      nlink: 1
    - path: configs/phase6_v3_1_y_external_protocol_contract.json
      sha256: 8079786b20a8bea7988cb28b10e8c8a5d4fa4dfe2b7fb6459ccdfc72e2c974a7
      mode: "0444"
      nlink: 1
    - path: docs/phase6_v3_1_y_external_protocol_design.md
      sha256: c3b9a6da4a6a06a59b26b4c3e821b2bae55bec19b9d3047bf67b8a5b0fd64c7e
      mode: "0444"
      nlink: 1
    - path: docs/phase6_v3_1_y_external_protocol_redesign_analysis.md
      sha256: 9f04538cb1c42df2eb3ec8779376cf56d7f8769312cd99cc9dd6b59b33099377
      mode: "0444"
      nlink: 1
    - path: docs/handoffs/archive/T4_2026-08-13_v3_1_y_external_protocol_redesign_analysis.md
      sha256: e162a1fc5e396c11234fef09bdeb04f8c1e7496da588da105971a4c8868dbefb
      mode: "0444"
      nlink: 1
    - path: docs/prompts/phase6_t7_v3_1_y_external_protocol_package_review.md
      sha256: 2c4487fb3fab836f297a8b0bb405f0b51acdeb68593f901541a475cb48c8cb01
      mode: "0444"
      nlink: 1

package_members:
  count: 11
  all_hashes_match: true
  all_regular_mode_0444_nlink1: true
  identities:
    - {path: docs/phase6_v3_1_y_external_protocol_redesign_analysis.md, sha256: 9f04538cb1c42df2eb3ec8779376cf56d7f8769312cd99cc9dd6b59b33099377}
    - {path: docs/handoffs/archive/T4_2026-08-13_v3_1_y_external_protocol_redesign_analysis.md, sha256: e162a1fc5e396c11234fef09bdeb04f8c1e7496da588da105971a4c8868dbefb}
    - {path: docs/phase6_v3_1_y_external_protocol_design.md, sha256: c3b9a6da4a6a06a59b26b4c3e821b2bae55bec19b9d3047bf67b8a5b0fd64c7e}
    - {path: configs/phase6_v3_1_y_external_protocol_contract.json, sha256: 8079786b20a8bea7988cb28b10e8c8a5d4fa4dfe2b7fb6459ccdfc72e2c974a7}
    - {path: docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md, sha256: db022d4b0f4ff45ccf4c604a6694d4035001ab7a2ef8b5a4cbb263405379b015}
    - {path: docs/prompts/phase6_t7_v3_1_y_external_protocol_package_review.md, sha256: 2c4487fb3fab836f297a8b0bb405f0b51acdeb68593f901541a475cb48c8cb01}
    - {path: docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md, sha256: bdad02bf8ec6d50af28a86d84095ea92413659d8c957bad53703ba8dd5a0cf42}
    - {path: docs/prompts/phase6_t7_v3_1_y_wolfram_protocol_compatibility_review.md, sha256: 5a73529f57d24fbd4af65cecffbd1322b3a162bfd60acf28bf40cbb1bc8749dd}
    - {path: docs/prompts/phase6_t7_v3_1_y_source_load_micro_review.md, sha256: d5d0ea5eac363d28b87732b4b7092b7190869bcc3978ded39f2366b2409273be}
    - {path: docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md, sha256: 151f5be38a87fc2c78e4edf799a9b07732087561912cfec7f666342e611ad767}
    - {path: docs/prompts/phase6_t7_v3_1_y_science_review.md, sha256: 756aaab79927756d5ec6f93e45398c0cc11b9f0b450d2540057eb18b6e790d6e}

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_y_external_protocol_package_review.md
    sha256: 2c4487fb3fab836f297a8b0bb405f0b51acdeb68593f901541a475cb48c8cb01
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  v3_master:
    path: docs/prompts/phase6_v3_master_prompt.md
    sha256: f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  external_anchor_matrix:
    path: configs/phase6_v3_0_external_anchor_matrix.json
    sha256: 06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485
  convention:
    path: references/notes/phase6_v3_absorption_scattering_conventions.md
    sha256: 82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a
  thresholds:
    source_path: configs/phase6_v3_0_thresholds.json
    source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
    exact_v3_1_count: 16
    entries:
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
  certificate_ids:
    - V3_MODE_GREYBODY_NUMERICAL
    - V3_MODE_GREYBODY_FLUX_VS_S
    - V3_MODE_GREYBODY_EXTERNAL
    - V3_MODE_PARITY_PROBABILITY
    - V3_MODE_DOMAIN_COVERAGE
  external_runtime:
    wolfram_kernel_path: /Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel
    wolfram_kernel_sha256: 70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c
    frozen_version: 14.3.0 for Mac OS X ARM (64-bit) (July 8, 2025)
    snapshot_path: runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json
    snapshot_sha256: 8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488
    snapshot_files: 25
    snapshot_directories_including_root: 5
    content_inventory_sha256: d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2
    restored_identity_inventory_sha256: a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
  blocking_criteria:
    - V3.1-Y must be distinct from U/X and consume no predecessor science, successful subset, request, route map, cache, checkpoint, dispatch or root.
    - Every operation must have one exact, unique predicate/stage expansion and the compatibility operation must remain structurally zero-science.
    - Per-event prefix ACKs, final-stage authority, parent-observer barriers, stage 0 and parent-only terminal closure must be machine-complete and deadlock-free.
    - Route A/U/B/C and sentinel graphs must be generated by their frozen pre-result rules without post-hoc selection.
    - Exact method, precision, source snapshot, transformations, equations, conventions, 16 thresholds, five certificates and seven protected sources must remain unchanged.
    - Future authority paths must be predeclared without future digest self-reference; executable roots must be fresh, one-use and nonreusable.
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
GATE_LABEL: REVIEW YELLOW / V3.1-Y EXTERNAL PROTOCOL PACKAGE CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31y-package-identity-canonical-durability
      evidence_identity: package bbb9e976...6203 and contract 8079786b...974a7 are duplicate-free canonical indent-2 JSON; 11/11 package members and 29/29 unique path/hash bindings rehash exact; package and all members are regular 0444/nlink1.
    - item_id: v31y-distinct-lineage-and-future-authority
      evidence_identity: gate id is phase6_v3_1_y_external_protocol_v1 with completed_bounded_repairs=0; all ten future authority paths and six implementation paths were absent at review start; future review digests are not hardcoded.
    - item_id: v31y-v3-authority-preservation
      evidence_identity: all V3.0 formula/domain/anchor/threshold/convention identities rehash exact; 16 unique V3.1 thresholds and five certificate IDs are unchanged.
    - item_id: v31y-route-a-b-c-and-sentinel-graphs
      evidence_identity: independent reconstruction gives Route A 248 pairs/496 modes/9920 nodes; Route B 102 keys with 38 turning memberships and 458 nodes; exact 23-key compact SHA 5e93fca5...7c76; Route C 161/322/483 and sentinel 23+2*(7-1)=35 calls, 70 boundaries and 105 overlaps.
    - item_id: v31y-external-runtime-and-source-snapshot
      evidence_identity: kernel binary SHA 70ad9d85...046c; snapshot 8d5498ab...e488; 25 regular 0444/nlink1 files, five 0555 directories including root, no links; all eight context/path/hash/size/mode/nlink tuples match actual bytes/stat.
    - item_id: v31y-listed-u-x-deny-roots
      evidence_identity: U sentinel failure/manifest c80327f5...dc23/e9ef19b3...ead4 and X attempts d905500b...1772/6e0d2349...6109 rehash exact; all are terminal 0444/0555 nlink1 link-free roots and remain nonpromotable.
    - item_id: v31y-compatibility-science-code-separation-boundary
      evidence_identity: package freezes a separate compatibility WLS path with BHPT/Paclet/source-load calls=0 and science-capable call-sites=0, distinct from the science-capable WLS; both future paths are absent.
    - item_id: v31y-root-namespaces-resource-and-nonreuse-policy
      evidence_identity: four UTC root grammars are mutually distinct; operation order, one-use dispatch, no retry, failure terminalization, 120-second/16-MiB non-science caps and official 36-hour/free-space bounds are frozen.
    - item_id: v31y-protected-sources-and-no-runtime-drift
      evidence_identity: seven protected hashes match at start/end; no V3.1-Y root, dispatch, implementation path, live Wolfram/Python writer, solver or science process exists.
  failed_items:
    - item_id: v31y-predicate-registry-operation-profile-ambiguous
      blocker_id: v31y-predicate-registry-operation-profile-ambiguous
    - item_id: v31y-checkpoint-ack-parent-edge-wire-undefined
      blocker_id: v31y-checkpoint-ack-parent-edge-wire-undefined
    - item_id: v31y-route-u-graph-authority-contradiction
      blocker_id: v31y-route-u-graph-authority-contradiction
  partial_allowed_items:
    - item_id: v31y-common-absolute-phase-partial
      reason: the inherited frequency-dependent common absolute phase remains PARTIAL; probability, flux, parity-relative phase and the bounded V3.1 gate remain meaningful, but no common absolute complex phase is certified.
    - item_id: v31y-external-even-not-independent
      reason: Route C is intentionally odd-only and cannot certify independent even-sector external evidence; independent AP odd/even routes remain required elsewhere.
  not_assessed_items:
    - item_id: v31y-exact-six-implementation
      reason: all six paths are absent and no implementation is authorized.
    - item_id: v31y-real-kernel-compatibility
      reason: no one-use compatibility dispatch/root or target-kernel result exists.
    - item_id: v31y-source-load-micro
      reason: no source-load micro dispatch/root exists.
    - item_id: v31y-full-sentinel
      reason: no fresh 35/70/105 sentinel exists.
    - item_id: v31y-official-science
      reason: no fresh official A/U/B/C root exists; all 16 threshold outcomes and five certificates are unevaluated.
    - item_id: v31y-v3-2-and-global
      reason: V3.2, full-domain V3 certification and global GREEN remain forbidden/not assessed.

findings:
  - finding_id: v31y-predicate-registry-operation-profile-ambiguous
    class: BLOCKING_CURRENT_GATE
    summary: The frozen predicate expansion rule is nonunique and the single global stage registry cannot be reconciled with the operation-specific compatibility and micro paths.
    blocker_id: v31y-predicate-registry-operation-profile-ambiguous
    violated_contract_item: >-
      Package-review items 5, 7 and 8 require a literal, complete predicate registry, exact operation behavior, zero-science compatibility path and mutually executable future prompts; the contract's exact expansion rule must produce one unique ordered predicate inventory for each operation.
    exact_evidence: >-
      `configs/phase6_v3_1_y_external_protocol_contract.json` declares 108 templates and instructs substitution of every declared operation, record ordinal and field. Its domains are 4 operations x 8 record ordinals x 6 fields, but zero templates contain `{operation}`, zero contain `{field}`, and only 43 contain `{record_ordinal}`. Literal Cartesian expansion produces 20,736 entries but only 409 unique IDs (20,327 duplicates); placeholder-only expansion produces 409 unique IDs only by silently discarding two declared domains. The same contract has one 18-stage order, while T4 analysis lines 372-377 says compatibility replaces stages 5-10 with fixtures and source-load micro replaces stage 12 with a pre-solver exit. No operation-specific stage/predicate/fixture map exists.
    expected_value: >-
      One machine-readable operation profile for each of compatibility, source_load_micro, full_sentinel and official, with exact applicable stage order, fixture stages, template domains, unique predicate IDs, total count and order. Literal expansion must yield zero duplicate, missing, extra or unknown IDs and must reconcile compatibility's zero Paclet/source/science calls and micro's pre-solver exit.
    observed_value: >-
      Two incompatible expansions (20,736/409 unique versus selectively expanded 409) and no operation-specific profile. T6 would have to invent whether compatibility executes forbidden Paclet/source stages or omits registry-required stages.
    bounded_repair: >-
      Freeze a corrected contract/package revision with explicit per-operation stage profiles and explicit per-template applicable expansion domains/counts/order; freeze the exact compatibility fixture-to-stage/predicate map and micro stage-12 terminal behavior. Align the design, T6 prompt and all affected future review prompts. Add canonical expansion adversaries for duplicate/missing/extra IDs, wrong operation profile and incompatible fixture/stage use.
    allowed_files:
      - configs/phase6_v3_1_y_external_protocol_package.json
      - configs/phase6_v3_1_y_external_protocol_contract.json
      - docs/phase6_v3_1_y_external_protocol_design.md
      - docs/phase6_v3_1_y_external_protocol_redesign_analysis.md
      - docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md
      - docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md
      - docs/prompts/phase6_t7_v3_1_y_wolfram_protocol_compatibility_review.md
      - docs/prompts/phase6_t7_v3_1_y_source_load_micro_review.md
      - docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md
      - docs/prompts/phase6_t7_v3_1_y_science_review.md
    recheck_command: >-
      PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.14 -c 'load the corrected duplicate-rejecting canonical contract; expand each explicit operation profile exactly in declared order; assert four profiles, zero duplicate/unknown IDs, exact declared counts, compatibility zero-source profile, micro pre-solver profile and full/official profiles' && git diff --check -- configs/phase6_v3_1_y_external_protocol_package.json configs/phase6_v3_1_y_external_protocol_contract.json docs/phase6_v3_1_y_external_protocol_design.md docs/phase6_v3_1_y_external_protocol_redesign_analysis.md docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md docs/prompts/phase6_t7_v3_1_y_wolfram_protocol_compatibility_review.md docs/prompts/phase6_t7_v3_1_y_source_load_micro_review.md docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md docs/prompts/phase6_t7_v3_1_y_science_review.md
    unblock_condition: >-
      A delta-only T7 package review independently obtains exactly one duplicate-free ordered predicate inventory and executable stage profile for each of all four operations, with every compatibility fixture and source/micro stage accounted for and no implementation discretion.

  - finding_id: v31y-checkpoint-ack-parent-edge-wire-undefined
    class: BLOCKING_CURRENT_GATE
    summary: The frozen wire schemas cannot encode the claimed per-event prefix checkpoint, final-stage checkpoint, parent barrier, stage-zero seed and parent-only terminal authority chain.
    blocker_id: v31y-checkpoint-ack-parent-edge-wire-undefined
    violated_contract_item: >-
      Package-review item 5 requires parent-owned durability, per-event prefix ACKs without multi-event deadlock, exact parent-barrier/stage-edge semantics and parent-only terminal closure; the design says all schemas and barrier IDs are machine-frozen.
    exact_evidence: >-
      The ACK has only `[schema,session_id,event_sequence,frame_sha256,durable_checkpoint_sha256]`. The design requires every last event to create two distinct immutable files, its per-event prefix checkpoint and an additional final-stage checkpoint, but does not define which digest the one ACK field carries. The first frame of the next stage must bind the previous final-stage digest, yet child frames contain only `previous_frame_sha256` and no prior-stage checkpoint field. Only a barrier schema ID is named; there is no barrier field order, barrier ID/stage map, observer literal registry, parent-event schema, prefix-checkpoint schema, final-stage-checkpoint schema or parent-event sequencing. Stage 0 and stage 17 are prose-only parent edges. ACK compatibility cases omit WRONG_SCHEMA, WRONG_SEQUENCE and WRONG_DURABLE_CHECKPOINT_DIGEST, even though those fields control progression.
    expected_value: >-
      Exact canonical field orders/hash inputs/path grammar for child frames, parent events, per-event prefix checkpoints, final-stage checkpoints and ACKs; an unambiguous last-event ACK binding; an explicit prior-stage digest or stage-open token in the next-stage first frame; exact observer literals and predicate-to-observer mapping; exact barrier IDs and parent predicate sequence; explicit stage-zero seed and parent-only terminal rules. All wrong schema/sequence/checkpoint/barrier/stage-transition cases must fail closed.
    observed_value: >-
      The high-level prefix idea avoids the old whole-stage deadlock, but the machine contract cannot represent both checkpoint chains or the parent-only edges. Multiple incompatible implementations satisfy the prose, so replay/deadlock/false-ACK exclusion is unproven.
    bounded_repair: >-
      Machine-freeze separate prefix and final checkpoint schemas and hashes; make the last-event ACK carry or otherwise bind both authorities; add the prior-stage digest/stage-open authority to the next-stage first frame; freeze parent-event/barrier/observer/stage-zero/terminal schemas and path/state rules. Expand the compatibility matrix with wrong ACK schema, sequence, checkpoint, barrier and stage-edge cases, and require an exhaustive zero-science four-operation FSM model including crash/failure transitions.
    allowed_files:
      - configs/phase6_v3_1_y_external_protocol_package.json
      - configs/phase6_v3_1_y_external_protocol_contract.json
      - docs/phase6_v3_1_y_external_protocol_design.md
      - docs/phase6_v3_1_y_external_protocol_redesign_analysis.md
      - docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md
      - docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md
      - docs/prompts/phase6_t7_v3_1_y_wolfram_protocol_compatibility_review.md
      - docs/prompts/phase6_t7_v3_1_y_source_load_micro_review.md
      - docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md
      - docs/prompts/phase6_t7_v3_1_y_science_review.md
    recheck_command: >-
      PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.14 -c 'load the corrected canonical contract; construct the declared four-operation FSM; exhaustively advance every event/stage with valid authorities; assert no deadlock; mutate ACK schema, sequence, frame digest, prefix digest, final-stage digest, barrier, observer, stage-zero seed and terminal state one at a time and assert fail-closed rejection' && git diff --check -- configs/phase6_v3_1_y_external_protocol_package.json configs/phase6_v3_1_y_external_protocol_contract.json docs/phase6_v3_1_y_external_protocol_design.md docs/phase6_v3_1_y_external_protocol_redesign_analysis.md docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md docs/prompts/phase6_t7_v3_1_y_wolfram_protocol_compatibility_review.md docs/prompts/phase6_t7_v3_1_y_source_load_micro_review.md docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md docs/prompts/phase6_t7_v3_1_y_science_review.md
    unblock_condition: >-
      A delta-only T7 package review reconstructs one unambiguous canonical authority chain for all events and all 18 stage edges of each operation; valid multi-event runs terminate without deadlock, and every single-field checkpoint/sequence/barrier/observer/replay mutation fails before progression.

  - finding_id: v31y-route-u-graph-authority-contradiction
    class: BLOCKING_CURRENT_GATE
    summary: The package hardcodes Route U as 318/954 while explicitly forbidding the only evidenced 318-key map, which was data-derived in a failed predecessor.
    blocker_id: v31y-route-u-graph-authority-contradiction
    violated_contract_item: >-
      Package-review items 1-4 require a genuinely distinct Y gate, no U/X science or route-map reuse, no post-hoc selection, and an exact fresh Route-U graph under unchanged V3.1 method/domain/threshold authority.
    exact_evidence: >-
      The original Route-U design freezes `use_route_u iff fresh Route-A direct log_Gamma_flux < log(1e-8)` and states `N_U` is data-derived in `[0,496]`; approximately 318 is explicitly not a frozen count or science input. Y design, contract, T4 analysis and future science prompt instead require exactly `318/954` without a selector, 318-key ordered inventory or inventory hash. Y analysis lines 721-726 simultaneously says the observed 318-route map from a failed predecessor is never reusable. The actual failed official U root `runs/phase6/classic_scattering/v3_1_hp_unitarity_deficit_repair1_v1_20260812T064653Z_py314` is terminal `scientific_pass=false`, with failure e3874e75...52aa, manifest f977a0d5...3050d and `unitarity_route_map.json` SHA 5eee07ec...c822 containing 496 ordered entries and `route_u_count=318`; that root/map is absent from the package machine denylist.
    expected_value: >-
      Route-U membership is rebuilt only from fresh Y Route-A records in exact 496-mode order using the frozen direct-log-Gamma selector. The graph is `N_U` keys and `3*N_U` precision records with `0<=N_U<=496`; the failed U root/map/count is explicitly denylisted and cannot set expected cardinality.
    observed_value: >-
      A fixed 318/954 acceptance count with no machine selector or membership authority. Any 318-key subset can satisfy cardinality, while the only evidenced reason for the number 318 is forbidden failed-predecessor science.
    bounded_repair: >-
      Restore the fresh selector and data-derived `N_U/3*N_U` graph in the package, design, machine contract, T6 prompt and future reviews; bind the exact 496-mode input order and selector operands/source identities; add the full failed U root, failure manifest and route-map identity to the denylist. Do not change domain, thresholds, method, precision, equations, certificate meanings or protected sources.
    allowed_files:
      - configs/phase6_v3_1_y_external_protocol_package.json
      - configs/phase6_v3_1_y_external_protocol_contract.json
      - docs/phase6_v3_1_y_external_protocol_design.md
      - docs/phase6_v3_1_y_external_protocol_redesign_analysis.md
      - docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md
      - docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md
      - docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md
      - docs/prompts/phase6_t7_v3_1_y_science_review.md
    recheck_command: >-
      PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.14 -c 'load the corrected duplicate-rejecting canonical package and contract; assert exact fresh selector `direct log_Gamma_flux < log(1e-8)`, exact 496-mode source order, route_u keys=data-derived, nodes_per_key=3, 0<=N_U<=496, no fixed 318/954 acceptance, and explicit denylist hashes e3874e7565dc35498513af8112577810dd9059035f43a9d4573d633c2ae752aa/f977a0d555652d028b3b73d18990b902f37a55c3dd9305c6e6da55f66593050d/5eee07ece78204265fe45069ef57a653a61a8ee9d09ff4b4d7e8928bb385c822' && git diff --check -- configs/phase6_v3_1_y_external_protocol_package.json configs/phase6_v3_1_y_external_protocol_contract.json docs/phase6_v3_1_y_external_protocol_design.md docs/phase6_v3_1_y_external_protocol_redesign_analysis.md docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md docs/prompts/phase6_t7_v3_1_y_science_review.md
    unblock_condition: >-
      A delta-only T7 package review proves that no predecessor Route-U membership/count/map enters Y; every fresh 496-entry Route-A map is evaluated in frozen order by the exact selector, Route-U totality is reconstructed as `N_U/3*N_U`, and the failed predecessor root/map is machine-denylisted.

  - finding_id: v31y-common-absolute-phase-limitation
    class: NONBLOCKING_LIMITATION
    summary: The inherited common absolute complex phase remains PARTIAL; it does not invalidate this package gate but must remain a nonclaim.
  - finding_id: v31y-stringnormalize-historical-boundary
    class: NONBLOCKING_LIMITATION
    summary: The static `StringNormalize` diagnosis may motivate the fresh compatibility matrix but cannot rewrite the historical X runtime leaf, which remains UNKNOWN.
  - finding_id: v31y-future-runtime-and-science
    class: FOLLOW_UP_DEBT
    summary: Even after a corrected package is accepted, exact-six implementation, real compatibility, source-load micro, 35-call sentinel and fresh official science each require their own one-use authority and formal T7 review.

delta_review: null
hold_details: null

verification:
  commands:
    - complete reads and SHA-256/stat/nlink verification of the package, contract, design, T4 analysis/archive, all eleven members, all V3.0 authorities, T0 final X adjudication, T7 final X review, liveness protocol/template, source snapshot and denylisted roots
    - duplicate-key-rejecting JSON load and exact indent-2/sorted-key/LF/terminal-newline canonical-byte comparison for package and contract
    - recursive package path/hash verification over 29 unique bindings and exact absence checks over ten future authorities and six implementation paths
    - independent predicate-registry Cartesian and placeholder-sensitive expansion
    - independent V3.1 domain, Route-A, Route-B, exact-23 Route-C, sentinel and official graph reconstruction
    - independent V3.1 threshold/certificate enumeration and seven protected-source start/end rehash
    - independent 25-file/five-directory source snapshot and eight loaded-source tuple byte/stat reconstruction
    - immutable mode/nlink/link/failure/manifest checks on U/X denylisted roots and direct readback of the failed 318-key U route map
    - read-only process/root/transient checks and scoped git diff-check
  results:
    - package and contract identity/canonical/durability PASS
    - package members 11/11 PASS; recursive unique bindings 29/29 PASS
    - future paths absent/noncircular at review start PASS; only this package-review archive is created by this review
    - seven protected source hashes PASS at start/end
    - source snapshot 25 files/five dirs/eight loaded tuples PASS; no symlink/hardlink drift
    - Route A 496/9920 PASS; Route B 102/458 PASS; Route C exact-23 digest and 161/322/483 PASS; sentinel 35/70/105 PASS
    - 16 V3.1 thresholds, five certificates, method/precision/convention identities PASS
    - listed U/X deny roots and nonreuse PASS; full failed U 318-route-map denylist completeness FAIL
    - predicate registry determinism/operation profiles FAIL
    - checkpoint/ACK/parent-stage machine completeness FAIL
    - Route-U fresh graph/nonreuse consistency FAIL
    - no Wolfram/BHPT/AP/radial/solver/science execution; no Y dispatch/root/process

non_claims:
  - no V3.1-Y implementation acceptance
  - no target-kernel compatibility observation
  - no source-load micro acceptance
  - no 35-call sentinel result or permission
  - no official V3.1-Y science, threshold PASS or certificate
  - no reuse or promotion of U/X values, subsets, requests, route maps, caches, checkpoints, dispatches or roots
  - no independent external even-sector result
  - no common absolute scattering-phase validation
  - no Li-figure equivalence
  - no finite-radius observer claim
  - no full-domain V3 certification
  - no V3.2 and no global GREEN

repair_cycle:
  completed_bounded_repairs: 0
  package_review_consumes_repair: false
  bounded_repair_1_available: true
  bounded_repair_2_available: true
  same_substantive_blocker_remaining: false
  t0_adjudication_required: false
```

## Independent conclusion

The package has a strong and largely coherent scientific boundary: all frozen
V3.0 authorities, Route A/B/C graphs, external direct method, precision ladder,
source snapshot, thresholds, certificates, protected code and nonreuse policy
remain intact.  Its per-event prefix-checkpoint idea is also the right remedy
for the old whole-stage deadlock.

Those concepts are not yet a complete machine contract.  T6 would have to
choose among incompatible registry expansions, invent checkpoint/barrier wire
fields and silently decide whether the predecessor-derived number 318 is an
authority or a forbidden diagnostic.  Any one of those choices could change
what later evidence means.  Formal T6 implementation is therefore not
authorized.

Root T0 may freeze one bounded repair-1 package limited to the exact files and
unblock conditions above, then request a delta-only T7 package review.  No
science, compatibility launch, micro, sentinel, official run or V3.2 is
authorized by this record.
