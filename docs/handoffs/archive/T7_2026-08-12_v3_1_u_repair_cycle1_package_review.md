# T7 formal archive-only review — V3.1-U repair cycle 1 package

Date: 2026-08-12

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 1 PACKAGE READY FOR T4
```

## Reviewed package

```yaml
review_id: t7_v3_1_u_repair_cycle1_package_review
gate_id: phase6_v3_1_u_auxiliary_geometry_repair_cycle1_v1
parent_gate_id: phase6_v3_1_hp_unitarity_deficit_replacement_v1
attempt: repair_1_package
reviewer_task: formal SchWO T7 019f5ed1-b421-7ec2-9bac-8d134855a1ed
reviewed_candidate:
  path: configs/phase6_v3_1_u_repair_cycle1_package.json
  sha256: 85bff01def7286ebaf1682d5b5498209dfbbc452e098e1d8633e05fcc1b7554c
  schema: schwo.phase6.v3_1_u.repair_cycle1_package.v1
  canonical_json: true
  mode: '0444'
  nlink: 1
members:
  - path: docs/phase6_v3_1_u_repair_cycle1_design.md
    sha256: efa30a32e46db3e64ced8bfad95b720a0aae003e5361b81526d5801ffa48f1ff
    mode: '0444'
    nlink: 1
  - path: docs/prompts/phase6_t4_v3_1_u_repair_cycle1.md
    sha256: 5a4bf3c05424671b23a95e11ecbffbdd5e65304fbf43f9b1f6e38c910bf48c15
    mode: '0444'
    nlink: 1
  - path: docs/prompts/phase6_t7_v3_1_u_repair_cycle1_package_review.md
    sha256: 4fd5518036df72ac5dac19fe469687b6a1b0484ba7952a22d66d4f9140ebfe23
    mode: '0444'
    nlink: 1
  - path: docs/prompts/phase6_t7_v3_1_u_repair_cycle1_delta_review.md
    sha256: c2be5b0b965868e62225252d1d8eb89444d8b5375d5947139b5829fd7564bd4e
    mode: '0444'
    nlink: 1
frozen_review_basis:
  liveness_protocol:
    path: docs/review_gate_liveness_protocol.md
    sha256: 3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
  verdict_template:
    path: docs/templates/t7_gate_verdict_template.md
    sha256: 3ac1fe9969b253be034aa6a6ccf37d6daa9168c1685554049c143b6d9513179d
  terminal_review:
    path: docs/handoffs/archive/T7_2026-08-12_v3_1_u_terminal_scientific_failure_review.md
    sha256: 7aa90e012e7d079d7c16256647d97db663293cf9ff6f5a4346130aa1d82482f1
  control_plane_clarification:
    path: docs/handoffs/archive/T7_2026-08-12_v3_1_u_terminal_scientific_failure_control_plane_clarification.md
    sha256: 2f661f45dc609f6f92bb475060d5860586df3a916de8acefbab5f539f8850da0
  domain:
    path: configs/phase6_v3_0_domain.json
    sha256: 803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  thresholds:
    path: configs/phase6_v3_0_thresholds.json
    sha256: 91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  original_package:
    path: configs/phase6_v3_1_hp_unitarity_replacement_package.json
    sha256: decde34bcdc90db0bc69be446357e306cfe942c84a8d575902eddaa7d1ff6877
  package_start_coordination:
    status_sha256: 15d29b641b66b061c8865edb72eb811519360bda6a314515fd115cbe1ab96158
    t0_current_sha256: f80779de4990d6d18581d8ee4bccef1393f3a61b6fdb7cdbced272a357ac0ffa
    t7_current_sha256: c41a9a26146d16e1ab3c8c1bf69ea9e4f52cd3d3e853eaa783263cedd7e90e65
    execution_time_live_equality_required: false

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 1 PACKAGE READY FOR T4

incremental_review_state:
  passed_items:
    - item_id: v31ur1_package_identity
      evidence_identity: package 85bff01def7286ebaf1682d5b5498209dfbbc452e098e1d8633e05fcc1b7554c and four exact members; canonical JSON; all five regular 0444/nlink1
    - item_id: v31ur1_all_bound_identity_closure
      evidence_identity: 44 unique external bound paths plus package and four members, 49 unique regular paths total; every SHA-256/size/type/nlink reload exact
    - item_id: v31ur1_liveness_scope
      evidence_identity: sole blocker v31u_auxiliary_radius_closed_boundary_roundoff; completed bounded scientific repairs=0; package review consumes none; repair 1 of 2
    - item_id: v31ur1_exact_four_path_scope
      evidence_identity: oracle, producer and two shared tests only; expected changed path count=4
    - item_id: v31ur1_frozen_cli
      evidence_identity: scripts/phase6_v3_1_hp_unitarity.py/01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4
    - item_id: v31ur1_geometry_equivalence
      evidence_identity: exact nonnegative squared-ratio construction; q order [0,1,2], closed inequality and actual radii unchanged
    - item_id: v31ur1_geometry_proof_contract
      evidence_identity: exact 318 routed keys x three frozen precision nodes = 954; explicit zero-solver and ambient-precision-invariance requirements
    - item_id: v31ur1_non_circular_authority_chain
      evidence_identity: immutable predecessor/package/package-review/implementation-review chain; mutable live handoffs are predecessor records, not execution equality gates
    - item_id: v31ur1_fixed_path_one_use_dispatch
      evidence_identity: docs/handoffs/archive/T0_2026-08-12_v3_1_u_repair_cycle1_dispatch_attempt_0001.json fixed path; O_EXCL canonical 0444/nlink1; exact-root/single-use/four-hash/review binding; pre-science consumption
    - item_id: v31ur1_failed_root_no_reuse
      evidence_identity: failure 5aef8aec8511e5fa35df6459b7cd520b046e080d43f6c24fd95a8b46379d1779; manifest 6a8ab79495bad03c2d08742a6a6b79f3afc6df658eb7d7dcb20f145efa905b1e; fresh absent UTC root required
    - item_id: v31ur1_v3_and_protected_identity
      evidence_identity: V3.0 formula/domain/threshold/convention identities and seven protected radial SHA-256 values rehashed exact at review start/end
  failed_items: []
  partial_allowed_items: []
  not_assessed_items:
    - item_id: v31ur1_implementation_delta
      reason: four repaired implementation/test bytes do not yet exist
    - item_id: v31ur1_zero_solve_preflight_evidence
      reason: 954-node proof, adversarial tests and CLI preflight are T4 implementation outputs
    - item_id: v31ur1_one_use_dispatch
      reason: dispatch must remain absent until an accepted implementation delta review
    - item_id: v31ur1_science
      reason: Route A/U/B/C, all thresholds and certificates are not executed or assessed by this package review
    - item_id: v31ur1_v3_2
      reason: downstream V3.2 remains forbidden

findings: []
hold_details: null
repair_cycle:
  completed_bounded_scientific_repairs: 0
  current_bounded_scientific_repair: 1
  maximum_bounded_scientific_repairs: 2
  package_review_consumes_scientific_repair: false
  t0_adjudication_required: false
```

## Independent package analysis

### Identity and scope

The package canonical bytes equal UTF-8, sorted-key, two-space-indented JSON
with one terminal newline.  Independent recursive extraction produces 49
unique concrete path/hash bindings when the package and its four members are
included.  Removing those five package files leaves the package-declared 44
unique external bound paths.  Every path is a regular non-symlink `nlink1`
file and every digest matches.  Both package diff checks pass.

The science repair remains exactly the oracle plus the two shared tests.  The
producer is the only additional control-plane implementation path, so the
combined T4 delta is exactly four unique paths.  The CLI is byte-frozen at
`01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4`.
No package member authorizes a source, config, evidence, handoff, threshold,
domain, convention or protected-radial change outside this boundary.

### Closed-boundary mathematics

For positive `k` and `L2=ell(ell+1)`, squaring the frozen nonnegative closed
inequality is equivalent:

```text
k (2^q R_match) >= 4 sqrt(L2)
iff 4^q (k R_match)^2 >= 16 L2.
```

The branch decision itself can be made without a rounded square-root
subtraction:

```text
R_match=300 branch iff (300 k)^2 >= L2;
turning branch otherwise, with (k R_match)^2/L2 = 1 by construction.
```

Thus the turning branch selects exponent 2 exactly, while the fixed-300 branch
uses canonical decimal `k`, integer `ell` and exact nonnegative algebra.  This
preserves the closed boundary, the first-admissible order `(0,1,2)`, actual
mpmath radii and just-below/just-above behavior without an epsilon.  The design
explicitly rejects tolerance, `almosteq`, clipping, forced exponent 2,
expanded exponents and post-solve selection.

The mandatory no-solve proof is complete as a preimplementation contract: it
requires all 318 already frozen selector keys at all three per-key scheduled
precisions, exactly 954 successful decisions, ambient-dps invariance and a
hard zero-call guard on `_fresh_match`, radial, AP and external backends.  The
failed root supplies only reviewed ordered key identities; none of its science
may populate a later result.

### Fixed-path dispatch under the frozen CLI

The authority design is sufficient and non-circular.  The CLI has one ordinary
`--output-root` argument but no authority argument.  That argument may propose
only the target root; it cannot select an authority.  The producer must always
read the single frozen path:

```text
docs/handoffs/archive/T0_2026-08-12_v3_1_u_repair_cycle1_dispatch_attempt_0001.json
```

and fail unless the dispatch's exact target equals the proposed root.  The
dispatch must be published by Root T0 after implementation review using
O_EXCL canonical JSON as a regular `0444/nlink1` file and bind the package,
this package review, the future fixed-path implementation review, all four
repaired hashes, the unchanged CLI, protected/source identities,
`single_use=true`, required verdict tokens and one exact fresh absent root.

The unchanged producer creates that exact root with exclusive absent-root
semantics.  It must then durably publish dispatch identity/consumption inside
the bound root before its first science call.  Competing or repeated use of the
same dispatch cannot select another root because the dispatch target is exact;
it cannot reuse the same root because the first creation makes it non-absent.
A crash after root creation also consumes the root and forbids retry.  Thus
fixed-path dispatch plus exact-root binding and exclusive root creation closes
one-use without an environment, boolean, alternative-hash or argv-selected
authority channel.  The implementation details may choose only an
artifact-local consumption record consistent with these already frozen
semantics; they may not invent a second authority mechanism.

The future implementation review identity is non-circular: its fixed path and
digest are carried by the later T0 dispatch, which is created only after that
review.  The producer validates the dispatch at its fixed path, then rehashes
the fixed implementation-review path and exact tokens named by that dispatch.
Package-stage preflight validates the package/package-review chain without a
dispatch; official execution requires the dispatch.  Mutable live
`T7_current`, `status` and `T0_current` are preserved as package-start
predecessor identities but are not runtime equality gates.

No package-level ambiguity or blocker remains for item 9.

## Verification

Read-only commands performed:

- SHA-256/stat/nlink checks of the package and all four members: PASS;
- canonical JSON byte reconstruction: PASS;
- independent extraction and reload of 44 unique external bindings and all
  49 concrete paths including package/members: PASS, zero conflicts/missing;
- direct rehash of the failed terminal Route-U files:
  `route_u_records.jsonl = 645e2e116b13dbc1c70e7be1db06f3827a04ccd723e6093ffac8b06199e56c2b`,
  `route_u_ladders.jsonl = d7c1381fd0e51f439056350de90022ddc8aaf1808e72ee736b304ef10b2a5537`;
- independent algebraic review of exact/squared branch equivalence: PASS;
- static producer/CLI dataflow review for fixed dispatch and fresh-root
  exclusivity: PASS;
- `git diff --check` on the five package files: PASS;
- start/end V3.0/source/seven-protected rehash: PASS;
- read-only process check: no repair producer, solver or writer started.

No tests or numerical solver were run because this is a package-readiness
review; the focused tests and 954-node zero-solve proof are mandatory T4
implementation evidence and remain `NOT_ASSESSED` here.

## Authorization and nonclaims

Root T0 may separately dispatch this exact unchanged package to formal T4 for
the zero-science, exact-four-path implementation/preflight turn.  This archive
does not itself dispatch T4 or authorize a one-use dispatch, official root,
Route A/U/B/C science, threshold evaluation, certificate generation or failed
root reuse.

V3.1-U science remains `NOT_ASSESSED` for the repaired implementation.  This
GREEN is package readiness only.  It is not V3.1-U scientific acceptance,
V3.2 authorization, full-domain V3 certification, Li-figure equivalence,
finite-radius observer evidence or global GREEN.

This review is archive-only.  `status.md`, `T0_current.md`, `T4_current.md`,
`T7_current.md`, package/source/test/implementation bytes and all evidence
roots were not modified.
