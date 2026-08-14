# Formal T4 prompt — V3.1-Y external protocol redesign analysis

Gate: `phase6_v3_1_y_external_protocol_redesign_analysis_v1`  
Task: existing formal T4 task `019f5fa6-1288-7c01-8a87-4c4370cf5517`  
Mode: read-only analysis and design; zero science

## Authority

Read completely and rehash:

- `project.md`, the current-state header of `status.md`, and
  `docs/review_gate_liveness_protocol.md`;
- `docs/prompts/phase6_v3_master_prompt.md` and all V3.0 frozen authorities;
- the complete V3.1, V3.1-U and V3.1-X package/review/failure chain;
- the final V3.1-X T7 review
  `docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle2_source_ledger_implementation_delta_review.md`
  with SHA-256
  `e5f9b9503e16b053525dfba7dacb661abc433211d49dcccb2c5c9dc442af1dee`;
- the Root-T0 final adjudication
  `docs/handoffs/archive/T0_2026-08-13_v3_1_x_final_escalation_adjudication.md`.

## Task

Design a distinct V3.1-Y external protocol that can validate all exact 23
predeclared odd anchors without MST fallback, post-hoc key selection, threshold
relaxation or reuse of V3.1-U/V3.1-X science.

The analysis must identify the exact reason V3.1-X's Wolfram semantic
normalizer can reject an independently valid eight-record ledger.  Do this by
reasoning from Wolfram Language evaluation semantics and by designing a
**zero-science compatibility matrix**; do not run Wolfram or any solver in
this turn.

The proposed protocol must, at minimum:

1. eliminate opaque compound predicates: every check has a stable predicate
   ID, record ordinal, expected value and observed value;
2. publish request-parse, schema, semantic-projection, Paclet, `FindFile`,
   source-start and source-end checkpoints atomically before the next stage;
3. use a representation whose equality semantics are explicit and tested in
   the real target WolframKernel (for example exact named-field projections or
   ordered tuples with per-field predicates), without relying on Association
   insertion order or an unverified regex dialect;
4. preserve duplicate raw-JSON-member rejection before Wolfram import;
5. predeclare a persistent zero-science compatibility root and a one-call
   source-load micro sentinel, both terminating before every BHPT/external
   API/solver/science branch;
6. include fault injection for every leaf predicate, Unicode/path semantics,
   regex/string behavior, integer representation, inode/symlink/hardlink,
   Paclet contamination, source replacement, fake-child self-confirmation,
   partial publication, timeout and process reaping;
7. define fresh, non-circular, one-use authority namespaces with no V3.1-X
   dispatch/root reuse;
8. retain the exact 23 anchors, graph, precision, source snapshot, V3.0
   conventions, 16 thresholds, five certificate IDs and seven protected radial
   identities;
9. include conservative runtime/storage projections and explicit stop rules;
10. state exactly what may be shared with V3.1-X as implementation knowledge
    and what may never be reused as scientific evidence.

Compare at least two protocol designs and recommend one.  Provide a typed
artifact graph, exact allowed future implementation paths, exact
pre-execution gates, adversarial test inventory, persistent transcript schema,
formal T7 review points and bounded failure semantics.  No package is approved
by this analysis alone.

## Allowed writes

Write only:

- `docs/phase6_v3_1_y_external_protocol_redesign_analysis.md`
- `docs/handoffs/archive/T4_2026-08-13_v3_1_y_external_protocol_redesign_analysis.md`

Do not modify code, tests, configs, prompts, status/current handoffs, protected
sources, evidence or dispatch roots.  Do not invoke Wolfram, BHPT, AP, Route A,
Route U, Route B, Route C or any numerical solver.  Do not contact T7, create a
package, start V3.2 or claim global GREEN.

End with:

```text
CHECKPOINT / V3.1-Y EXTERNAL PROTOCOL REDESIGN ANALYSIS READY FOR T0 PACKAGE FREEZE
```
