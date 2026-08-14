# Formal T4 prompt — V3.1-U bounded repair cycle 1

Date frozen by Root T0: 2026-08-12

This prompt is inactive until Root T0 supplies a formal T7 package-review
archive with the exact identity-bound label:

```text
ACCEPT GREEN / V3.1-U REPAIR CYCLE 1 PACKAGE READY FOR T4
```

Work in `/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO` as the
existing formal T4 task `019f5fa6-1288-7c01-8a87-4c4370cf5517`.

## Read first

Read completely: `project.md`; the current-state header and latest V3.1-U
entries in `status.md`; T0/T4/T7 current handoffs; the V3 master prompt; the
original V3.1-U package/design/T4/T7 prompts; the terminal failure root's
`failure.json` and `failure_manifest.json`; the formal terminal review; the
control-plane clarification; `docs/review_gate_liveness_protocol.md`; the new
repair package and `docs/phase6_v3_1_u_repair_cycle1_design.md`; and the
formal T7 package-review archive supplied by T0.

Rehash every package member, predecessor authority, frozen CLI, failed-root
identity, V3.0 authority, original scientific source and protected radial file
before editing.  Stop without edits if any identity differs.

## Exact implementation scope

You may change exactly four unique paths:

```text
src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py
src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
tests/unit/test_phase6_v3_hp_unitarity.py
tests/regression/test_phase6_v3_hp_unitarity_publication.py
```

The oracle change is limited to the algebraically stable implementation of the
already frozen closed auxiliary-radius membership rule.  The producer change
is limited to non-circular immutable start-gate constants/logic and the
corresponding source-ledger binding.  The two tests cover both changes.

Do not modify the frozen CLI
`scripts/phase6_v3_1_hp_unitarity.py` (SHA-256
`01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4`),
any package/design/prompt/status/handoff, original producer dependency, seven
protected radial files, formula/domain/threshold/convention authority, route
selector, precision schedule, graph, or evidence root.

## Required science repair

Preserve exactly:

```text
R_match=max(300,sqrt(ell(ell+1))/k)
R_q=2^q R_match, q=(0,1,2) in that order
admissible iff k R_q >= 4 sqrt(ell(ell+1))
```

Replace only the precision-sensitive membership construction by an
algebraically equivalent exact/nonnegative squared or exact-ratio comparison
as frozen in the design.  Preserve actual mpmath radii and solver inputs.
Epsilon tolerances, `almosteq`, clipping, forced exponent 2, extra exponents,
post-solve selection and precision changes are forbidden.

Add direct tests for exact boundary, just below, just above, invalid inputs,
ambient-precision invariance and the original `(0.005,10,odd)` failure.  Build
the exact 318-key Route-U inventory from the reviewed route map and prove all
three scheduled precision nodes per key, exactly 954 geometry nodes, with a
hard zero-solver-call assertion.

## Required control-plane repair

Remove execution-time equality against mutable live `T7_current.md`,
`status.md` and `T0_current.md`.  Do not replace it with multiple acceptable
hashes, a live-handoff fallback, an environment/argv/boolean-selected gate or
a monkeypatch.

Implement the single immutable chain frozen in the design:

- original package/design/T4 prompt/package approval;
- terminal failure and corrected Route-U identities;
- terminal T7 review and control-plane clarification;
- this combined package and formal package review;
- all original/V3.0/protected scientific identities;
- a later fixed-path one-use T0 dispatch that binds the formal implementation
  review, exact four repaired hashes and exact fresh root.

At implementation preflight the package/package-review chain must validate.
Official execution must additionally require and consume the later dispatch
before a science call.  The source ledger must bind the repaired producer and
oracle, unchanged CLI and all authorities at start/end.  Add adversarial tests
for missing/extra/wrong-token/wrong-hash/wrong-root/reused-dispatch/live-
handoff-substitution cases.

## Mandatory zero-science verification

Run exactly the focused command from the clarification under CPython 3.14 and
the frozen mpmath overlay.  Also run the frozen CLI `preflight`, Ruff
check/format on the four paths, in-memory compile, and four-path `git diff
--check`.  Rehash all protected/source/authority inputs after tests.

The complete preflight must demonstrate:

- exact-boundary semantics and `318*3=954` deterministic geometry nodes;
- zero radial/AP/BHPT/science solver calls;
- fail-closed authority adversaries;
- unchanged CLI, thresholds, domain, conventions and protected sources;
- only the four permitted files changed.

Use only `/tmp` for non-authoritative test evidence.  Do not create or resume
an official root, do not run Route A/U/B/C science or sentinels, do not consume
a dispatch, and do not edit status/T4 handoff in this turn.

Return to Root T0 with exact before/after SHA-256 values, test counts, commands,
the 954-node inventory identity, zero science-call count, and any limitation.
If every gate passes, end with:

```text
CHECKPOINT / V3.1-U REPAIR CYCLE 1 IMPLEMENTATION READY FOR T7 DELTA REVIEW
```

This does not accept V3.1-U science and does not authorize official execution,
V3.2 or global GREEN.
