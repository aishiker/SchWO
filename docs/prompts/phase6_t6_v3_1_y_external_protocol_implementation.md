# Formal T6 prompt — V3.1-Y external protocol implementation

Gate: `phase6_v3_1_y_external_protocol_v1`  
Mode: exact-six zero-science implementation  
Task: formal T6 `019f5faf-bfdd-7aa3-80a9-1c9829daecac`

This prompt activates only after formal T7 accepts the exact V3.1-Y final
repair-cycle-2 package revision. Bind separately: the immutable initial
REPAIR archive, repair-cycle-1 delta REPAIR archive SHA-256
`63c1ae9286fa5cb7b07ee4c2995a7cf6bb71f9e1bc941399d46861f65f1aa499`,
and the newly predeclared delta-2 archive
`docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_delta_review_2.md`.
At execution time the latter must exist 0444/nlink1, rehash to the dispatch
supplied identity, and contain exact `ADVANCE / NOT_ASSESSED / ACCEPT GREEN /
V3.1-Y EXTERNAL PROTOCOL PACKAGE READY FOR T6` tokens. The candidate package
must contain no delta-2 digest. Any alias, missing authority or identity drift
stops before a write.
Read and rehash the package, protocol contract, design, T4 analysis/archive,
T0 X-final adjudication, T7 X-final review, this prompt, all future review
prompts, V3.0 authorities, BHPT snapshot/runtime and seven protected radial
sources.  Verify the fixed future package-review archive and its exact
`ADVANCE / NOT_ASSESSED` package-ready envelope.  Any mismatch stops before a
write.

Create exactly the six new implementation paths frozen by the package and no
others.  Do not modify X/U code, V3.0 authorities, source snapshot, protected
sources, package/design/prompts, status/current handoffs or evidence roots.

Implement the machine contract literally:

- separate compatibility WLS with structurally zero science call sites;
- science-capable WLS with one micro pre-solver exit and one reviewed direct
  BHPT public API call site after pre-science commit;
- exact typed frame/parent durable-ACK FSM, stage/predicate registry, explicit
  Boolean/`INDETERMINATE`, named projection and exact ASCII literal policy;
- per-event durable prefix checkpoint before each ACK, final-stage checkpoint
  on the last declared event, parent-observer barrier semantics, prelaunch
  stage-0 seed and parent-only terminal stage, with no multi-event deadlock;
- strict raw duplicate-member rejection before RawJSON import;
- exact source/Paclet/context/start/end observer separation and TOCTOU closure;
- persistent per-frame/event/ACK/checkpoint evidence and strict manifests;
- exact one-use namespaces for compatibility, micro, sentinel and official;
- UTC-only root timestamps and explicit timezone/created-at fields in every
  run contract and manifest;
- exact 23/35/161 graph, source/method/precision/threshold/certificate and
  protected identities; no MST/fallback/cache/predecessor/sentinel reuse;
- independently expand the four profiles to exactly
  `151/409/14315/65849` predicates and global `80724`, including exact call
  ordinals, ordered IDs, and profile/registry hashes;
- implement contract revision 3 literally: exact 27/29/18/24/21/29/25/19
  ordered fields, per-field type/domain/nullability/value rules,
  `C_OBJ`/`C_WIRE`, domain-separated `F`/`A`/labelled `L` inputs, continuing
  event/prefix chains, last-event prefix+final binding, operation-specific
  barrier plans, stage-0 seed, and the stage16 final+prefix -> child-exit ->
  lifecycle receipt -> open17 -> P17 events/final/terminal chain;
- require compatibility totals 151 events/82 frames/82 ACKs and micro totals
  409/263/263, with exact sentinel/official products; P17 is parent-only and
  has no frame/ACK/next-open;
- exhaustively reject each single-field missing/extra/type/null/domain/order/
  digest/sequence/barrier/replay/oversize/extra-output mutation before
  progression, plus crash/recovery variants;
- derive Route U only after fresh complete Route A using
  `direct log_Gamma_flux < log(1e-8)`, publish dynamic `N_U/3*N_U`, and reject
  fixed-318 acceptance or any explicitly denylisted predecessor provenance;
- full process lifecycle, clean environment, absolute argv/cwd, timeout,
  wait/reap/PG-empty and immutable PASS/FAIL terminalization.

Tests must generate a direct positive and at least one negative for every
predicate template and every compatibility case ID.  Include compound-gate,
undefined-symbol, symbolic Boolean, Association order, Unicode, regex,
integer, path/hash/stat/inode/link, Paclet/context/source drift, frame/ACK,
fake-child, partial-publication, timeout/signal/orphan and authority replay
attacks.  Reconstruct exact graph/cardinality and separate numerical and
convention budgets.

Run CPython 3.14 focused and adjacent tests, Ruff check/format, in-memory
compile and `git diff --check`.  Use only fake children and temporary synthetic
roots.  Hard stop for this turn:

```text
real Wolfram launches = 0
BHPT/AP/radial/solver/science calls = 0
formal dispatch/root created = 0
```

Do not contact T7.  Return exact six hashes, tests, temporary evidence
identities, source/protected start/end hashes and:

```text
CHECKPOINT / V3.1-Y EXTERNAL PROTOCOL IMPLEMENTATION READY FOR T7 REVIEW
```
