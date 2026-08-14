# T7 formal package review — V3.1-U final bounded repair cycle 2

Date: 2026-08-13

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: REVIEW YELLOW / V3.1-U REPAIR CYCLE 2 PACKAGE CHANGES REQUIRED
```

## Verdict record

```yaml
review_id: t7_v3_1_u_repair_cycle2_package_review_20260813
gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
repair_id: phase6_v3_1_u_route_c_totality_repair_cycle2_v1
attempt: repair_2
reviewer_task: formal SchWO T7 independent review task
reviewed_candidate:
  root: package-only; no implementation, dispatch, sentinel or official root exists
  identities:
    - path: configs/phase6_v3_1_u_repair_cycle2_package.json
      sha256: d340174b33d166ec4fc35836db932af55a12ea2c7b92bbc5c6b2649cd868f69d
    - path: docs/phase6_v3_1_u_repair_cycle2_design.md
      sha256: ea3bc217298fb10f74dbe10fed091d384cb368514eea02b958ea9a4c6af25551
    - path: docs/prompts/phase6_t4_v3_1_u_repair_cycle2.md
      sha256: a18053878c8da5fcf07ef0abeaf4ca4ae05688b9c2fb6df5b861aeaadef71bbd
    - path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_package_review.md
      sha256: 3b1d9083f5de33dee9be5e716ee465edad06050768f621f89993c0f10285959b
    - path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_delta_review.md
      sha256: ca46dac66d322c3953e7a926d62f46ff19be48ec161a97c7b42aa0e83043335f
    - path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_sentinel_review.md
      sha256: 5bbf2996a7af96b282a1c699c74e85a04f7030b9bd5c2bcb33d4c0a99c33e617
    - path: runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json
      sha256: 8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488

frozen_review_basis:
  review_contract:
    path: docs/prompts/phase6_t7_v3_1_u_repair_cycle2_package_review.md
    sha256: 3b1d9083f5de33dee9be5e716ee465edad06050768f621f89993c0f10285959b
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  predecessor_terminal_review:
    path: docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle1_terminal_scientific_review.md
    sha256: 7552b2dbc19269be0eb11b61ae8eb04c55a1225d10db1962d881e0f6ac7925c1
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    - id: V3.1 frozen threshold set
      value: exact 16 unchanged IDs/operators/values/domains
      units: mixed dimensionless/logarithmic
      source_path: configs/phase6_v3_0_thresholds.json
      source_sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  external_anchor_matrix:
    path: configs/phase6_v3_0_external_anchor_matrix.json
    sha256: 06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485
  blocking_criteria:
    - sole failed item v31u_route_c_external_totality_and_provenance
    - exact six-file implementation boundary
    - exact 23 ordered odd-RW anchors and MST/90/45/45
    - one child and at most one call per anchor
    - source-bound complete success/failure terminal grammar
    - non-circular one-use sentinel then official authority
    - no failed-root or sentinel-science reuse
    - failed sentinel consumes final repair and requires T0 escalation
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
GATE_LABEL: REVIEW YELLOW / V3.1-U REPAIR CYCLE 2 PACKAGE CHANGES REQUIRED

incremental_review_state:
  passed_items:
    - item_id: v31u_repair2_package_identity_and_scope
      evidence_identity: canonical package d340174b33d166ec4fc35836db932af55a12ea2c7b92bbc5c6b2649cd868f69d; five exact members; package plus 48 unique bound dependency paths rehash exact; seven package/snapshot files all 0444/nlink1
    - item_id: v31u_repair2_exact_six_file_boundary
      evidence_identity: exact six baselines a7a53b9fee2e2001132b0b437b233f4fafff1362a113d21105913e2263dcdf6a/a3990e9dc3bc5480478c037a77c0661e805508df49007848185e7178380da29e/168c8771fbe7cba8983b51d0ae58294169c2e901a75593953a91ad0c401fc146/acdb1e30f69c2a5972af7394c08d360f8dfef32f3fc5f0a69c7401ca4d5167cc/d86fc31af71a2e3815cf063989918994495c05b1f8655bb8973bb8362c2dca39/e4e3cfb939cb7ccd2f267cbddfe52c4064873cddbc481fd26dc727ec08ea29aa
    - item_id: v31u_repair2_science_invariants_frozen
      evidence_identity: CLI 01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4; Route-U oracle a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7; exact 496/9920/318/954/102/458/23 graph, 16 thresholds, five certificates, odd RW MST/90/45/45 and all seven protected hashes unchanged
    - item_id: v31u_repair2_external_snapshot_byte_chain
      evidence_identity: snapshot 8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488; 25 exact files; content inventory d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2; restored identity inventory a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
    - item_id: v31u_repair2_external_historical_chain
      evidence_identity: historical ledger c73c1c585af9bbfeed8d50a2b28c9c2f94e08b38214b3db716fe1c7e501e2d16 and its 512685e2860d784cf3152b96ba71fac76d4cdc8fd23e74825ebb519ac7ddb57c inventory; audit ZIP 715e27a45b15ec2ab78f92c77506de4317f5a26af79bb665de5a16d30557d162 and SHA256SUMS ea5e8d103323a1e8b5faefd951022f1d88cfbd05660820a18055c765492b0b92; all 25 bytes agree
    - item_id: v31u_repair2_snapshot_commit_nonclaim
      evidence_identity: restored snapshot has no .git; association with 2e01209271fb3d0d92705d5c27bd9e00a6140981 is explicitly inherited from the immutable historical clean ledger and is not asserted as independently proven by the snapshot
    - item_id: v31u_repair2_terminal_protocol
      evidence_identity: design sections 5-6 require complete 23-attempt PASS/ERROR inventory, raw streams, child payload, receipt/wait/reap, first error, source start/end and mutually exclusive immutable success/failure closure
    - item_id: v31u_repair2_no_reuse_and_loop_limit
      evidence_identity: both failed roots and sentinel records forbidden as official inputs; sentinel dispatch consumes repair 2; any sentinel failure requires ESCALATE; no retry/resume/repair cycle 3
    - item_id: v31u_repair2_future_review_hash_non_circularity
      evidence_identity: future review paths and verdict tokens are frozen without a future SHA; each later fixed T0 dispatch must supply exactly one path/SHA after that review exists; alternate hashes and live handoffs are forbidden
  failed_items:
    - item_id: v31u_route_c_external_totality_and_provenance
      blocker_id: v31u_repair2_sentinel_entry_authority_undefined
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31u_repair2_implementation
      reason: no six-file implementation delta or zero-science T4 evidence exists
    - item_id: v31u_repair2_sentinel_science
      reason: sentinel dispatch/root are absent and the final scientific repair has not been consumed
    - item_id: v31u_repair2_official_science
      reason: official dispatch/root are absent; V3.1-U remains FAIL

findings:
  - finding_id: v31u_repair2_sentinel_entry_authority_undefined
    class: BLOCKING_CURRENT_GATE
    summary: The package claims a package-frozen no-CLI module entry but does not contain the exact CPython invocation, argv grammar or unique fixed-dispatch-to-root derivation, so T4 would have to invent the sentinel launch authority channel.
    blocker_id: v31u_repair2_sentinel_entry_authority_undefined
    violated_contract_item: Required check 7 and design section 7 require a unique, non-circular sentinel authority with no live-handoff, environment, argv, boolean or fallback authority escape; the review prompt explicitly requires any no-CLI sentinel ambiguity to be classified before T4.
    exact_evidence: configs/phase6_v3_1_u_repair_cycle2_package.json freezes sentinel/official dispatch paths and forbids environment/argument authority selection but contains no sentinel invocation object, exact argv or module-entry bytes. docs/phase6_v3_1_u_repair_cycle2_design.md lines 214-218 say the sentinel uses one package-frozen CPython 3.14 module entry expression, yet no literal expression follows. docs/prompts/phase6_t4_v3_1_u_repair_cycle2.md lines 67-72 only instruct T4 to add run_route_c_sentinel(root). The unchanged CLI has no sentinel command. Therefore the package leaves T4 to choose -m versus -c/direct import, the operation token, how root is passed, and whether the invocation is dispatch-bound.
    expected_value: One exact package member must freeze the CPython 3.14 executable, complete argv, project cwd, fixed runtime environment, module/operation token, prohibition of extra argv, and the rule that the sentinel root is read only from and validated against the one fixed O_EXCL dispatch. The sentinel dispatch must bind that exact invocation and six implementation hashes. No root path, review path/hash, source root, WLS or kernel may be selected through argv/environment.
    observed_value: No exact invocation is frozen. Multiple materially different launch surfaces satisfy the prose, including an unaudited python -c expression or caller-supplied root argument. The current package cannot prove that argv merely selects an operation rather than an authority, so the sentinel chain is not uniquely closed.
    bounded_repair: Correct only the package/design/T4 prompt to freeze one literal no-CLI invocation. The recommended minimal contract is exact argv [/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14, -m, schwgw.validation.phase6_v3_mode_greybody_hp_replacement, route-c-sentinel], exact project cwd, PYTHONDONTWRITEBYTECODE=1 and exact overlay-first PYTHONPATH. It takes no root/review/source argument and rejects every extra token. The module operation must load the exact fixed sentinel-dispatch path internally, derive its sole root from that canonical dispatch, then validate/consume it before launch. The dispatch and implementation review must bind the exact invocation object. Explicitly reject python -c, direct-import expressions, alternate modules, root argv, environment-selected authority and fallback. Preserve the unchanged project CLI and every already passed package invariant.
    allowed_files:
      - configs/phase6_v3_1_u_repair_cycle2_package.json
      - docs/phase6_v3_1_u_repair_cycle2_design.md
      - docs/prompts/phase6_t4_v3_1_u_repair_cycle2.md
    recheck_command: shasum -a 256 configs/phase6_v3_1_u_repair_cycle2_package.json docs/phase6_v3_1_u_repair_cycle2_design.md docs/prompts/phase6_t4_v3_1_u_repair_cycle2.md && PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m json.tool configs/phase6_v3_1_u_repair_cycle2_package.json >/dev/null
    unblock_condition: A corrected immutable package/design/T4 prompt freeze exactly one no-root-argument module invocation and require both implementation review and one-use sentinel dispatch to bind it; all alternate -c/direct-import/module/extra-argv/root/environment/fallback surfaces are explicitly rejected; all member/source/snapshot/protected hashes and repair-cycle semantics remain exact; a delta-only package re-review finds no other class-A item.
  - finding_id: v31u_snapshot_commit_association_inherited_only
    class: NONBLOCKING_LIMITATION
    summary: The restored 25-file snapshot does not contain .git and cannot independently prove commit 2e012092; the package states this honestly and uses exact byte equality plus the immutable historical clean ledger and audit ZIP as the bounded association.
  - finding_id: v31u_repair2_science_not_yet_assessed
    class: NONBLOCKING_LIMITATION
    summary: Package readiness cannot assess Route-C or V3.1-U science; even a future sentinel PASS would assess only the 23-anchor prerequisite.
  - finding_id: v31u_v3_2_and_global_state_out_of_scope
    class: FOLLOW_UP_DEBT
    summary: V3.2, full-domain V3, Li-figure equivalence, finite-radius observer claims and global GREEN remain forbidden.

delta_review:
  reviewed_failed_items:
    - v31u_route_c_external_totality_and_provenance
  passed_invariants_rechecked:
    - v31u_route_a_complete_inventory
    - v31u_route_map_frozen_selector
    - v31u_route_u_geometry_repair_and_complete_graph
    - v31u_route_b_complete_graph
    - v31u_one_use_dispatch_and_fresh_root
    - v31u_failed_predecessor_nonreuse
    - v31u_protected_radial_identity
  protected_identities_match: true
  unrelated_passed_items_reopened: false

hold_details: null

verification:
  commands:
    - SHA-256/mode/nlink reload of package, five members, snapshot, 30 source bindings, seven protected paths and six implementation baselines
    - canonical JSON reload of package and snapshot; whitespace/diff-check of all seven package/snapshot files
    - direct 25-file restored-root inventory, content/identity index reconstruction and symlink/hardlink/directory-mode audit
    - direct historical source_start bhpt_source record/commit/clean-status reconstruction
    - direct ZIP SHA, embedded SHA256SUMS and 25 source-member byte comparison without extraction
    - static authority/dataflow review of package, design and all four prompts; absence checks for future reviews, dispatches and roots
    - read-only process check for WolframKernel and repair-2 sentinel/official producers
  results:
    - package is canonical JSON d340174b33d166ec4fc35836db932af55a12ea2c7b92bbc5c6b2649cd868f69d; package plus 48 unique bound dependencies rehash exact
    - package, five members and snapshot are regular 0444/nlink1; diff-check/terminal-newline/trailing-whitespace checks PASS
    - restored source has 25 regular 0444/nlink1 pairwise-distinct files, five inclusive 0555 directories, zero symlink and no .git
    - three-field pretty canonical content index with terminal newline is d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2
    - five-field path/sha256/size/mode/nlink identity index is a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
    - historical 25-record identity index is 512685e2860d784cf3152b96ba71fac76d4cdc8fd23e74825ebb519ac7ddb57c and records exact commit association 2e01209271fb3d0d92705d5c27bd9e00a6140981 with empty status_porcelain
    - audit ZIP 715e27a45b15ec2ab78f92c77506de4317f5a26af79bb665de5a16d30557d162; SHA256SUMS ea5e8d103323a1e8b5faefd951022f1d88cfbd05660820a18055c765492b0b92; all 25 member bytes/hashes exact
    - implementation review, sentinel review, both fixed dispatches and both repair-2 roots are absent; no related live process was found
    - zero Python radial/AP/BHPT/Wolfram/science solve was run in this review

non_claims:
  - package readiness is NOT_ASSESSED because its unique sentinel invocation authority is incomplete
  - V3.1-U remains FAIL; Route-C, all 16 thresholds and five certificates are not accepted
  - the snapshot commit association is inherited, not independently established by a .git checkout
  - no failed-root or future sentinel scientific byte is reusable in an official candidate
  - repair cycle 2 is not consumed by this package review
  - no implementation, sentinel dispatch, sentinel science, official dispatch/run, V3.2 or global GREEN is authorized

repair_cycle:
  completed_bounded_repairs: 1
  completed_bounded_scientific_repairs: 1
  current_bounded_scientific_repair: 2
  repair_cycle2_consumed: false
  same_substantive_blocker_remaining: true
  t0_adjudication_required: false
```

## Independent package assessment

The scientific and provenance portions of the package are otherwise bounded
and coherent.  The 25 restored source bytes exactly match both the immutable
historical ledger and the audit ZIP.  The snapshot correctly avoids claiming
that a directory without `.git` independently proves a commit.  The
success/failure process envelope, one-call-per-anchor rule, non-reuse rule,
two one-use dispatches and final repair-cycle limit are all appropriate.

The remaining defect is an authority-channel ambiguity, not a style
preference.  The design calls the module entry “package-frozen”, but no such
literal entry is present.  Because the CLI is frozen and T4 may change only
six paths, leaving the invocation open would require T4 to invent a seventh
control surface in prose or at dispatch time.  Freezing one exact no-root-arg
`-m` entry closes the cycle without changing any science, domain, method,
precision, threshold or protected source.

## Downstream boundary

Root T0 must not dispatch T4 from this package identity.  A corrected package
may receive one delta-only package re-review; that correction does not consume
repair cycle 2.  No sentinel or official execution, V3.2 or global GREEN is
authorized.
