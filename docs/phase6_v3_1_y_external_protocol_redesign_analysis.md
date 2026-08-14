# Phase 6 V3.1-Y external protocol redesign analysis

Date: 2026-08-13
Gate: `phase6_v3_1_y_external_protocol_redesign_analysis_v1`
State: `NOT_ASSESSED / ZERO-SCIENCE DESIGN ONLY`

Repair-cycle-1 normative clarification: this original analysis remains the
historical causal record, while corrected contract revision 2 is controlling.
Every former fixed Route-U `318/954` reference is superseded by fresh
`N_U/3*N_U`, `0 <= N_U <= 496`, obtained only from the exact complete
496-entry Route-A order with `direct log_Gamma_flux < log(1e-8)`. The failed
predecessor root and historical route map are denylisted inputs. No numerical
method, threshold, domain, convention, precision, source, or protected byte
changes.

Repair-cycle-2 normative clarification: the historical causal analysis above
and below remains unchanged, but final contract revision 3 is now the sole
machine protocol authority. It supplies exact per-field type, domain,
nullability and value rules for the eight schemas; exact `C_OBJ`/`C_WIRE` and
`F`/`A`/`L` digest inputs; operation-specific barrier traversals; an unbroken
event/prefix chain; a noncircular stage-0 seed; and a cryptographic
stage-16-exit/lifecycle-receipt/P17 chain. The only future package authority
for the final bounded review is the predeclared, initially absent
`docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_delta_review_2.md`.
No future digest is embedded. The already-passed registry/profile and fresh
Route-U subtrees remain byte-semantically frozen, and no scientific boundary
is changed.

## 0. Decision and scope

This analysis recommends a **parent-acknowledged, predicate-event protocol**
(`Protocol A` below) for the Wolfram boundary.  Every semantic assertion is a
separate typed event; the Python parent durably publishes and reloads that
event before acknowledging it; the Wolfram child may not enter the next stage
without the exact acknowledgement.  A one-launch real-kernel compatibility
matrix and a different one-launch source-load micro sentinel are mandatory
before any BHPT public API call.

This is a distinct V3.1-Y authority.  It is not V3.1-X repair cycle 3, an
attempt-0003 retry, implementation, a package, a dispatch, science, V3.2, an
independent review, or global GREEN.  No failed V3.1/V3.1-U/V3.1-X scientific
value, successful subset, cache, request, dispatch, root, transcript or
checkpoint is reusable.

No WolframKernel, BHPT, AP, Route A/U/B/C or other numerical solver was run in
this analysis.  The only repository writes authorized by the governing prompt
are this file and its T4 archive.

## 1. What V3.1-X established, and what it did not

The final formal V3.1-X review is
`ESCALATE / NOT_ASSESSED`.  Its sole review-authorized real-Wolfram,
zero-science preflight used the exact WolframKernel and terminated naturally
with return code 69 and exact stdout:

```text
loaded-source record semantic mismatch
```

The preserved review root is
`/private/tmp/schwo_t7_v31x_r2_review_preflight.ptN6p0`, tree identity
`64602b35aec85f8facac412b90eb8e8a329fe5300e493d76fc1afd1d1f31a534`.
It contains 36 regular mode-`0444`, nlink-1 files and six mode-`0555`
directories, and records PID/SID/PGID `7185/7185/7185`, natural rc69, exact
wait, reap and empty process group.  The request SHA-256 is
`503eb41d144a041fbda65a0934002c09b680bd8fa7f92ea8195348869ec1a8bb`;
stdout SHA-256 is
`37272a68ab5eb4dcb6d46815d08608b26c5c3cca457fcd2d601c5cd6ac15cc03`.
There was no WLS result, source-end, Paclet result, runtime result or counter
record, and the static call graph puts the only `ReggeWheelerRadial` call after
the failed branch.  External API, solver, boundary, overlap and scientific
call counts are therefore exactly zero.

Python independently reconstructed all eight request records and found the
six semantic values valid.  This proves that byte-valid producer evidence can
still be rejected by a mismatched target-language predicate.  It does not
make the Python reconstruction an observation of the failed Wolfram leaf.

### 1.1 Evidence classification for the failed leaf

Two statements must remain separate:

1. **Persisted V3.1-X runtime evidence:** the precise failed leaf is
   `UNKNOWN`, because the WLS collapsed all semantic leaves into one message
   and persisted no predicate ID, ordinal, expected value or observed value.
2. **Static causal reconstruction from the frozen WLS and Wolfram 14.3
   semantics:** the first record deterministically fails the path-normalization
   leaf, for the reason below.  This is a source-level deduction, not a new
   runtime observation.  V3.1-Y must confirm it in its one-use real-kernel
   compatibility matrix before treating it as a verified runtime fact.

### 1.2 Exact static causal reconstruction

The frozen WLS has SHA-256
`7a8277b6996fccbd3d0b515ebba8a0fae17a9c6a9efa7a0d3116a9055bbc041f`.
Its path predicate contains:

```wl
normalizedRelativePathQ[path_] := StringQ[path] && path =!= "" &&
  StringNormalize[path] === path &&
  StringMatchQ[path, RegularExpression["[A-Za-z0-9._/-]+"]] && ...
```

and the compound semantic gate contains:

```wl
!normalizedRelativePathQ[values[[2]]]
```

The target Wolfram Language 14.3 Unicode-normalization function is
`CharacterNormalize[text, "NFC"]`; the official system documentation and
the installed System usage/symbol inventories contain `CharacterNormalize`,
not `StringNormalize`.  The exact 25-file BHPT snapshot also defines no
`StringNormalize`.  A repository- and runtime-file read-only search found no
definition that could resolve the bare symbol in this script.  Under Wolfram
symbol-resolution and evaluation semantics the call consequently remains an
undefined expression such as
`Global`StringNormalize["Kernel/ReggeWheeler.m"]`.  `SameQ` tests expression
identity, so that expression is not identical to the string on its right and
the leaf evaluates to `False`.  Negation in the outer semantic branch makes
the failure condition `True`; the first otherwise valid record exits through
the generic rc69 branch.

This is sufficient to explain the observed rc69 before solver entry.  It also
explains why Python validation of all eight records can pass: Python never
evaluated the target-language undefined symbol.  The current source has other
unverified cross-language assumptions (notably `RegularExpression` dialect,
Unicode normalization and integer/type behavior); they are latent until the
first failure is removed and must not be guessed as the observed leaf.

The relevant official semantics are documented by Wolfram Research for
[`CharacterNormalize`](https://reference.wolfram.com/language/ref/CharacterNormalize.html),
[`SameQ`](https://reference.wolfram.com/language/ref/SameQ.html), and
[`If`](https://reference.wolfram.com/language/ref/If.html).  In particular,
`If` takes a branch only for an explicit `True` or `False`; a condition that
remains symbolic is not a safe Boolean gate.  V3.1-Y therefore requires every
leaf to be reduced with an explicit Boolean contract and records
`INDETERMINATE` as a blocking outcome.

## 2. Frozen scientific boundary

V3.1-Y changes only the cross-runtime protocol and its control/evidence
plane.  It does not change any numerical method, formula, domain, precision,
source, convention, threshold or certificate.

### 2.1 Exact production and anchor domain

- Production frequencies, in ordinal order:
  `0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 4, 8`.
- For each frequency, every integer
  `ell=2..max(12,ceil(3 sqrt(3) kM - 0.5)+16)` and both independently solved
  parities, giving 248 `(kM,ell)` pairs and 496 modes.
- Exact external odd-only anchors, in frozen order:

```text
0.1: ell 2,3,4,8
0.5: ell 2,3,4,10
1:   ell 2,3,4,5,13
2:   ell 2,3,4,10,18
4:   ell 2,3,4,20,28
```

The compact 23-key inventory digest independently reconstructed in the
predecessor analysis is
`5e93fca57b6d4fb82762043fedea4631de92111164c8c4a991d76925e3867c76`.
It is a diagnostic derivation, not a substitute for the frozen anchor matrix.
All 23 anchors are blocking as one declared set; no favorable subset may be
selected after execution.

### 2.2 Exact graph, method and precision

The external route remains odd-only BHPT Regge-Wheeler direct integration:

```text
method                   NumericalIntegration
potential                ReggeWheeler
spin                     2
boundary solutions       In and Up, independently constructed
node order               P0,P1,I0,I2,O2,O4,O8
P0 precision             90/45/45 (working/precision/accuracy goals)
P1 and boundary nodes    120/60/60
selected node            P1
MST calls                0
```

The sentinel remains exactly 35 public calls, 70 boundary solutions and 105
overlap records.  The official external route remains exactly 23 keys, 161
public calls, 322 boundary solutions and 483 overlap records.  The complete
fresh candidate graph remains Route A `496/9920`, Route U `N_U/3*N_U`
(`0 <= N_U <= 496`), Route B
`102/458`, and Route C `23/161`, with five certificates.  Sentinel science is
never reused by the official candidate, and predecessor Route A/U/B/C bytes
are never reused by V3.1-Y.

The direct horizon route and the independent unitarity-deficit route remain
separate:

```text
Gamma_flux = F_H/F_in                         (direct signed-current route)
Gamma_S    = 1-|S|^2                         (independent S route)
```

Neither may populate the other.  Frequency is constructed from an exact
rational before arbitrary-precision evaluation; no MachinePrecision upgrade
is accepted.  The boundary-geometry overlays, equations, overlap
decomposition, `exp(-i omega t)` convention and phase convention are frozen
as in V3.0/V3.1-X.

### 2.3 Exact 16 threshold IDs

| ID | Frozen value |
|---|---:|
| `V3T-S-COMPLEX-001` | `2e-6` |
| `V3T-LOGGAMMA-001` | `2e-4` |
| `V3T-FLUX-BALANCE-001` | `1e-8` |
| `V3T-GAMMA-ROUTES-001` | `2e-8` |
| `V3T-GAMMA-ROUTES-LOG-001` | `2e-4` |
| `V3T-GAMMA-PHYSICAL-001` | `2e-10` |
| `V3T-PARITY-PROB-001` | `2e-8` |
| `V3T-PARITY-PHASE-001` | `2e-6` rad |
| `V3T-PRECISION-S-001` | `5e-7` |
| `V3T-PRECISION-LOGGAMMA-001` | `1e-4` |
| `V3T-RIN-S-001` | `1e-6` |
| `V3T-RIN-LOGGAMMA-001` | `2e-4` |
| `V3T-ROUT-JOST-S-001` | `2e-6` |
| `V3T-ROUT-JOST-LOGGAMMA-001` | `3e-4` |
| `V3T-TOLERANCE-S-001` | `1e-6` |
| `V3T-TOLERANCE-LOGGAMMA-001` | `2e-4` |

The frozen operators and applicability domains in
`configs/phase6_v3_0_thresholds.json` remain controlling; this table does not
replace them.

### 2.4 Exact five certificate IDs

```text
V3_MODE_GREYBODY_NUMERICAL
V3_MODE_GREYBODY_FLUX_VS_S
V3_MODE_GREYBODY_EXTERNAL
V3_MODE_PARITY_PROBABILITY
V3_MODE_DOMAIN_COVERAGE
```

Missing blocking evidence is failure or `NOT_ASSESSED`, never a partial PASS.
Odd-only external evidence cannot become independent even-sector evidence.
The frequency-common absolute scattering phase remains a nonclaim.

## 3. Candidate protocols

### 3.1 Protocol A — parent-ACK typed predicate dialogue (recommended)

The child and parent use a strictly framed, ordered dialogue over dedicated
stdin/stdout pipes.  The exact pipe behavior itself is admitted only after the
real-kernel compatibility matrix passes.

The request remains canonical JSON, but the parent performs a lexical
duplicate-member check before Wolfram import.  Inside Wolfram, objects are
used only for named lookup.  Cross-language source records are projected to
ordered arrays in the exact field sequence:

```text
[context,path,sha256,size,mode,nlink]
```

No Association insertion order is an identity.  No entire Association is
compared with `SameQ`.  No production path/hash predicate depends on
`RegularExpression`; ASCII membership and length are checked by explicit
character/code-point predicates, and required source paths are additionally
compared to the eight exact frozen literals.

Each child predicate emits one wire frame:

```text
[
  "schwo.phase6.v3_1_y.predicate_frame.v1",
  session_id,
  event_sequence,
  stage_ordinal,
  stage_id,
  predicate_id,
  record_ordinal_or_null,
  field_id,
  observer_id,
  value_type,
  expected_value,
  observed_value,
  outcome,
  previous_frame_sha256
]
```

`outcome` is exactly `PASS`, `FAIL` or `INDETERMINATE`.  A predicate helper
must evaluate its comparison once, require its head/value to be an explicit
Boolean, and convert non-Boolean results to `INDETERMINATE`; it may not embed
multiple leaves in one `If` or rely on symbolic truthiness.

For each received frame the Python parent:

1. preserves the exact raw frame bytes;
2. strictly parses schema, types, session, monotone sequence and hash chain;
3. independently recomputes the predicate where it owns the observation;
4. atomically O_EXCL/no-follow publishes the raw frame and canonical event;
5. fsyncs files and parent directories, reloads, rehashes and restats them;
6. publishes a stage checkpoint when every declared predicate for that stage
   is present, ordered, unique and passing;
7. only then sends this exact acknowledgement:

```text
[
  "schwo.phase6.v3_1_y.predicate_ack.v1",
  session_id,
  event_sequence,
  frame_sha256,
  durable_checkpoint_sha256
]
```

The child validates the exact ACK and cannot emit the next stage or enter a
science branch without it.  An absent, duplicate, replayed, out-of-order or
wrong-session ACK is terminal.  Unknown stdout data is not ignored: it is
captured as raw stream evidence and blocks protocol acceptance.

This design gives durability to the parent, not to a self-confirming child,
and gives every failure a stable leaf identity.  Its cost is a more demanding
bidirectional state machine.  That complexity is acceptable because it is
precisely the boundary that failed twice under opaque one-shot output.

### 3.2 Protocol B — child filesystem checkpoint FSM

An alternative is a file-mailbox state machine.  Wolfram performs named
lookups and explicit tuple projection, writes one typed file per predicate to
a fresh temporary name, renames it to a stage checkpoint and reloads it before
continuing.  Python validates all checkpoints after child termination.

This removes Association-order dependence and can expose predicate IDs, but
it is not recommended:

- Wolfram-side `RenameFile` does not by itself establish the parent-required
  O_EXCL/no-follow/file-fsync/parent-fsync boundary;
- the child can still self-assert that its own checkpoint is durable;
- parent discovery can race with partial publication;
- the mailbox expands the writable/alias surface and complicates timeout
  ownership;
- failure before the parent sees a file again loses the stage boundary.

Protocol B is useful as an adversarial reference implementation but not as the
authority boundary.

### 3.3 Protocol C — terminal monolithic result (rejected)

A single result object emitted after all checks is operationally simple, but
it recreates the V3.1-X defect: a crash or generic exception before terminal
publication erases predicate provenance, request/Paclet/source stages are not
durable before solver entry, and a child can self-confirm an invented ledger.
Protocol C is rejected even if it uses ordered tuples.

### 3.4 Comparison

| Property | Protocol A | Protocol B | Protocol C |
|---|---|---|---|
| Leaf predicate observable | yes | yes if file exists | no after early exit |
| Parent-controlled durability before next stage | yes | no | no |
| Association-order independent | yes | yes | possible |
| Child self-confirmation resistance | strong | weak | weak |
| Partial-publication surface | per-frame, parent-owned | broad shared FS | terminal-only loss |
| Process complexity | highest | medium | lowest |
| Recommendation | **adopt** | reject as authority | reject |

## 4. Protocol A stage machine

The exact stage order is frozen before implementation.  A stage may start only
after the parent has durably committed and acknowledged the preceding stage.

| Ordinal | Stage ID | Blocking output before next stage |
|---:|---|---|
| 0 | `Y_REQUEST_RAW_PARENT` | raw bytes, duplicate-member scan, canonical-byte identity, request/dispatch/root equality |
| 1 | `Y_RUNTIME_ENTRY` | exact kernel/script/argv/cwd/environment/session identities |
| 2 | `Y_REQUEST_RAWJSON` | RawJSON head and typed top-level named fields |
| 3 | `Y_LEDGER_SCHEMA` | exact 8-record cardinality/order; exact six-key set per record |
| 4 | `Y_LEDGER_PROJECTION` | six typed leaves per ordinal; exact context/path literals; explicit character/hash/integer leaves |
| 5 | `Y_PRELOAD_STATE` | no preloaded ReggeWheeler context/Paclet/source contamination |
| 6 | `Y_PACLET_LOAD` | exact Paclet directory, candidate count and loaded root |
| 7 | `Y_CONTEXT_LOAD` | exact eight contexts in frozen order |
| 8 | `Y_FIND_FILE` | one event per context/path plus resolved-path equality |
| 9 | `Y_SOURCE_START_CHILD` | child-observed path/hash/size for all eight loaded files |
| 10 | `Y_SOURCE_START_PARENT` | parent-observed regular/no-follow/hash/size/mode/nlink/inode/no-alias plus 25-file/5-dir snapshot closure |
| 11 | `Y_PRE_SCIENCE_COMMIT` | exact zero counters and an explicit `science_branch_authorized` bit from the stage FSM |
| 12 | `Y_OPERATION` | compatibility or micro zero-science exit; otherwise exactly one reviewed public API call |
| 13 | `Y_SOURCE_END_CHILD` | child re-observation of all eight loaded files |
| 14 | `Y_SOURCE_END_PARENT` | full parent rehash/restat and start/end equality |
| 15 | `Y_COUNTERS` | exact route-specific counts and no undeclared call |
| 16 | `Y_RESULT` | typed operation result or typed failure |
| 17 | `Y_CHILD_TERMINAL` | return/signal/timeout/wait/reap/PG-empty/raw streams |

For the compatibility operation, stages 5--10 are replaced by isolated test
fixtures as declared in the matrix; all scientific branches are statically
and dynamically unreachable.  For the source-load micro, stages 0--11 and
13--17 execute, while stage 12 is the explicit pre-solver exit.  Its counters
must say one kernel launch and zero BHPT public API, `ReggeWheelerRadial`,
solver, boundary, overlap and scientific calls.

`mode` and `nlink` are parent POSIX observations.  The child must not pretend
to observe them; it only binds their expected values in the request and
identifies the parent predicate that supplied the actual value.  This
observer-role separation prevents a second self-confirming ledger.

## 5. Persistent transcript and terminal artifacts

Every executable stage uses a fresh direct-child root.  Its immutable
transcript is a directory of independently closed records, not a vulnerable
append-only summary:

```text
request/request.raw
request/request.canonical.json
authority/dispatch_consumption.json
authority/run_contract.json
authority/source_start.json
process/prelaunch.json
process/running.json
transcript/raw/000000.child.frame
transcript/events/000000.event.json
transcript/acks/000000.ack.json
transcript/stages/0000-Y_RUNTIME_ENTRY.checkpoint.json
...
process/stdout.raw
process/stderr.raw
process/receipt.json
process/terminal.json
authority/source_end.json
result.json | failure.json
manifest.json | failure_manifest.json
```

Each event binds schema, gate/stage/session IDs, dispatch, operation, sequence,
predicate registry identity, ordinal, expected/observed typed values, observer,
raw-frame identity, preceding event identity and source/runtime identities.
Each stage checkpoint binds the exact ordered event set and preceding stage
checkpoint.  Each ACK binds the committed checkpoint rather than an in-memory
Boolean.  Aggregated JSONL views may be produced only after terminal closure;
they are derived indexes and never the authority for a missing per-event file.

All files are exclusive, regular, non-symlink, nlink1, atomically published,
file+parent fsynced, reloaded and finally mode `0444`; directories close mode
`0555`.  The manifest has an exact allowed-path grammar and is
non-self-referential.  Unknown paths, extra frames, missing frames, duplicate
sequence/predicate IDs, noncanonical values, uncommitted tails and aliases
fail closed even if a recomputed manifest claims otherwise.

## 6. Real-kernel zero-science compatibility matrix

The compatibility matrix is a persistent one-use root, not a temporary unit
test and not a scientific input.  It launches the exact WolframKernel once,
exercises only protocol primitives, and is reviewed by formal T7 before the
separate source-load micro may be dispatched.

Suggested exact namespace:

```text
runs/phase6/classic_scattering/
  v3_1_y_wolfram_protocol_compatibility_v1_<YYYYMMDDTHHMMSSZ>_py314
```

Every row has a stable case ID, predicate ID, expected typed value, observed
typed value, exact Boolean outcome and raw transcript.  The blocking matrix is:

| Case family | Positive and adversarial observations |
|---|---|
| `Y-COMP-JSON-*` | RawJSON object→Association, array→List, String/Integer heads; duplicate raw members rejected by parent before launch; missing/extra/noncanonical/torn JSON |
| `Y-COMP-PROJECT-*` | every permutation of Association insertion order gives the same named six-field projection; missing/extra/duplicate record and reordered context are rejected |
| `Y-COMP-EQUALITY-*` | ordered tuple identity, String identity, exact Integer identity, `0` versus `0.`, explicit `TrueQ`; symbolic/indeterminate predicate blocks |
| `Y-COMP-UNICODE-*` | `CharacterNormalize[...,"NFC"]` on ASCII, NFC and NFD; composed/decomposed, confusable and invisible characters; the obsolete/undefined `StringNormalize` expression is observed and must not appear in production |
| `Y-COMP-STRING-*` | explicit ASCII code-point allowlist; slash, colon, backslash, repeated slash, leading/trailing slash, `.`/`..`; whole-string semantics |
| `Y-COMP-REGEX-*` | target-kernel `RegularExpression` behavior for the two predecessor patterns is recorded; production regex call count remains zero regardless of observation |
| `Y-COMP-HASH-*` | exactly 64 lowercase ASCII hex characters, uppercase/short/long/nonhex/Unicode lookalike negatives; exact file hash and size |
| `Y-COMP-INTEGER-*` | `size>=0`, `mode=292`, `nlink=1` as exact Integers; Real/string/negative/large/missing forms reject |
| `Y-COMP-FRAME-*` | Unicode escaping, LF framing, maximum length, Flush visibility, exact raw bytes, wrong schema/session/sequence/previous-hash/type/outcome |
| `Y-COMP-ACK-*` | correct ACK progresses; missing, delayed, replayed, duplicate, wrong-frame and wrong-session ACK do not progress |
| `Y-COMP-LIFECYCLE-*` | rc0, native failure, malformed frame, exception, EOF, timeout, signal, terminate→wait, kill→wait, exact reap and PG-empty |
| `Y-COMP-FS-*` | regular file, directory, symlink, hardlink, same-byte new inode, no-follow and alias observations are parent-owned and exact |
| `Y-COMP-PACLET-*` | clean preload state; contaminated context/Paclet/`FindFile`/search path negatives; exact source replacement between start/end |
| `Y-COMP-FAKE-*` | a fake child reproducing every expected JSON value still fails exact executable/runtime/process/source and real-kernel transcript authority |
| `Y-COMP-PUBLISH-*` | collision, partial file, missing fsync attestation, extra path, post-close write, wrong mode/link, manifest self-report tamper |

The matrix itself must prove
`external_api_calls=regge_wheeler_radial_calls=solver_calls=boundary_calls=overlap_calls=scientific_calls=0`.
No compatibility output is admissible as later numerical input.

### 6.1 At least three additional failure modes closed proactively

Beyond the known `StringNormalize`, ordering and generic-message defects, the
design explicitly closes these latent modes:

1. **Protocol-channel contamination:** package messages or localized kernel
   text on stdout could be mistaken for a valid event.  Unknown bytes are
   preserved and blocking; only exact framed events on the reviewed channel
   can be acknowledged.
2. **ACK/session replay:** a delayed ACK from an earlier stage or process
   could authorize the wrong stage.  Session, sequence, frame digest and
   durable checkpoint digest are all required, monotone and one-use.
3. **TOCTOU source replacement:** a correct `FindFile` result could be
   replaced between source-start and the API call.  Parent and child each
   close start/end observations; parent also binds inode, mode, nlink and the
   complete 25-file/5-directory snapshot.  Any drift terminalizes the run.
4. **Approximate-number type drift:** JSON `292.0` or Wolfram `Real` could
   compare numerically equal to an integer.  Type and value are separate
   predicates, and production uses exact Integer identity.
5. **Unicode/confusable path drift:** NFC-equivalent or visually similar paths
   cannot be silently normalized into authority.  Required loaded paths are
   exact ASCII literals; normalization is diagnostic and any nonidentical raw
   string rejects.
6. **Child self-confirmation after parent death:** the child cannot proceed
   without a parent ACK that contains an already-fsynced checkpoint digest;
   EOF or timeout is terminal and cannot be converted to PASS by a child file.

## 7. Source-load micro sentinel

Only a formally T7-accepted compatibility root permits a distinct one-use
micro dispatch.  Suggested namespace:

```text
runs/phase6/classic_scattering/
  v3_1_y_external_source_load_micro_v1_<YYYYMMDDTHHMMSSZ>_py314
```

The micro uses only frozen anchor ordinal 0 `(kM=0.1,ell=2,odd)` and node
`P1` as an authority label.  It launches the exact kernel once, authenticates
the request, exact overlay, Paclet, eight contexts, eight loaded source files
and complete external snapshot at start/end, executes the full Protocol A
dialogue, and exits at `Y_PRE_SCIENCE_COMMIT` before the
`ReggeWheelerRadial` symbol is called.  Its static call graph and runtime
counters must independently establish:

```text
kernel launches                 1
BHPT public API calls           0
ReggeWheelerRadial calls        0
solver calls                    0
boundary solutions              0
overlap records                 0
scientific calls                0
```

The micro result is protocol/source-load evidence only.  It cannot satisfy an
anchor, seed a request, supply a cache, update a resource estimate or be
copied into the sentinel/official root.

## 8. Typed authority and execution graph

Every arrow below is a hash-bound `requires` relation, not permission implied
by temporal order:

```text
V3.0 authorities + T0 X final adjudication + this analysis
  -> fresh V3.1-Y package/design/T4/T7 prompts
  -> formal T7 package ADVANCE
  -> zero-science implementation in exact allowed paths
  -> formal T7 implementation ADVANCE
  -> one-use T0 compatibility dispatch
  -> immutable compatibility PASS/FAIL root
  -> formal T7 compatibility terminal ADVANCE
  -> different one-use T0 source-load-micro dispatch
  -> immutable micro PASS/FAIL root
  -> formal T7 micro terminal ADVANCE
  -> different one-use T0 35-call sentinel dispatch
  -> immutable sentinel PASS/FAIL root
  -> formal T7 sentinel terminal ADVANCE
  -> different one-use T0 official attempt_0001 dispatch
  -> fresh full Route A/U/B/C candidate root
  -> formal T7 scientific review
```

No package hardcodes the digest of a future review file.  It freezes exactly
one future archive path; the later T0 dispatch supplies that file's one exact
digest and the then-current implementation hashes.  Each dispatch binds one
absolute direct-child root, one operation, exact argv/cwd/requested and
observed clean environments, kernel, package, implementation, predecessor
review and prior-chain digest.  Dispatch consumption is O_EXCL and durable
before the child launch or first science call.

Suggested mutually exclusive root namespaces are:

```text
v3_1_y_wolfram_protocol_compatibility_v1_<UTC>_py314
v3_1_y_external_source_load_micro_v1_<UTC>_py314
v3_1_y_external_direct_sentinel_v1_<UTC>_py314
v3_1_y_external_direct_v1_<UTC>_py314
```

Each namespace starts at `attempt_0001`; no V3.1-X attempt number, dispatch,
root or review-only preflight becomes a V3.1-Y authority.

### 8.1 Artifact types and promotion rules

| Artifact type | Producer | May authorize | Never supplies |
|---|---|---|---|
| `Y_PACKAGE` | T0 | implementation review | runtime fact or science |
| `Y_COMPAT_TRANSCRIPT` | real kernel + parent | compatibility review | source-load or numerical evidence |
| `Y_MICRO_TRANSCRIPT` | real kernel + parent | micro review | anchor value, cache, timing model |
| `Y_SENTINEL_NODE` | reviewed external route | sentinel review/resource projection | official value |
| `Y_OFFICIAL_NODE` | fresh official route | certificate review | even-sector external evidence |
| `Y_FAILURE` | any executable stage | adjudication only | PASS, retry seed, cache |

## 9. Exact allowed future implementation paths

A future package should permit exactly these six **new** paths and no others:

```text
scripts/phase6_v3_1_y_wolfram_protocol_compatibility.wls
scripts/phase6_v3_1_y_bhpt_direct.wls
src/schwgw/validation/phase6_v3_mode_greybody_external_protocol.py
scripts/phase6_v3_1_y_external_protocol.py
tests/unit/test_phase6_v3_external_protocol.py
tests/regression/test_phase6_v3_external_protocol_publication.py
```

Separating the compatibility WLS from the science-capable WLS makes the
zero-science call graph structural rather than argument-selected.  The second
WLS contains the source-load-micro pre-solver branch and the direct node
branch; their exact operation authority is supplied by distinct dispatches.

The new producer may re-express reviewed graph and validation knowledge from
V3.1-X, but it must not import the X control plane as authority.  The frozen
external BHPT snapshot and reviewed boundary-geometry transformations may be
freshly materialized from their canonical source identities; this is source
reuse, not failed result reuse.  Any need to change a seventh path, external
method, graph, precision, threshold, convention, snapshot or protected source
stops package freeze and requires a new T0 adjudication.

## 10. Adversarial tests and pre-execution gates

### 10.1 Static and fake-process tests before any real kernel

- exact predicate registry: stable unique IDs, exact stage membership, every
  leaf has a generated one-variable negative;
- WLS AST/text gate: no compound semantic `If`, no production
  `StringNormalize`, no production regex, no Association-wide equality, one
  reviewed public API call site after `Y_PRE_SCIENCE_COMMIT` only;
- strict duplicate-key RawJSON lexical parser, canonical request bytes, exact
  six-field named extraction and tuple order;
- event/ACK schemas, hash chain, wrong session/sequence/replay/extra/missing,
  frame truncation and channel contamination;
- full lifecycle injection at before/after request, frame, event, fsync,
  checkpoint, ACK, Popen, PGID/SID, wait, timeout, terminate, kill, reap and
  terminal publication;
- exact attempt path grammar and manifest grammar; collision, symlink,
  hardlink, alias, inode/content/mode/nlink drift;
- fake child with perfect values still rejected for wrong runtime/process
  identity;
- source/Paclet/context/start/end replacement and contamination;
- full 23/35/161 plan cardinality/order and no favorable selection;
- exact clean environment, absolute executable/argv/cwd and kernel SHA;
- compatibility and micro call graphs prove zero science.

### 10.2 Gates before the compatibility launch

1. all authorities rehash exact, target absent and no writer/process;
2. exact six paths and T7 implementation ADVANCE;
3. exact kernel path/hash/version, snapshot 25/5 identity, overlays and seven
   protected files;
4. all static/fake tests and canonical publication checks pass;
5. one-use compatibility dispatch is valid, fresh and unconsumed;
6. disk and process/liveness guards pass.

### 10.3 Gates before micro, sentinel and official

- micro additionally requires the immutable compatibility root and formal T7
  compatibility ADVANCE;
- sentinel additionally requires the immutable micro root and formal T7 micro
  ADVANCE;
- official additionally requires all 35 sentinel calls/70 boundaries/105
  overlap records, all numerical/source/protocol/resource gates and formal T7
  sentinel ADVANCE;
- every later stage rehashes source/runtime/protocol identities anew; it does
  not trust an earlier stage's source snapshot as a current observation.

## 11. Resource and storage bounds

Stored zero-science X child lifetimes were approximately 3.24 s and 4.87 s;
the latter loaded the full Paclet/context closure before rc69.  These support
only an operational zero-science projection:

| Stage | Lower | Central | Hard upper | Launches | Root cap |
|---|---:|---:|---:|---:|---:|
| compatibility matrix | 3 s | 10 s | 120 s | 1 | 16 MiB |
| source-load micro | 3 s | 5 s | 120 s | 1 | 16 MiB |

The wider central value for compatibility covers the full predicate dialogue
but is not a performance claim.  Either hard timeout is terminal and
nonretryable under that dispatch.

No V3.1-X direct numerical call completed, so its pre-solver failures cannot
predict the 90/120-digit 35-call sentinel.  Older 40/60-digit direct evidence
suggested about 74 minutes centrally and 7.7 hours under an observed-max
envelope, but it does not bound the frozen high-precision/multiplier-8 graph.
The sentinel must measure every geometry class.  The unchanged official
resource gate uses at least safety factor 2, projects 23 instances of each
seven-node class maximum, requires projected wall time `<=36 h`, and requires
the frozen projected output `20,000,000` bytes to be no more than one quarter
of freshly measured free workspace space.  CPU concurrency remains one.

Compatibility/micro timings may not relax, replace or seed the sentinel
resource projection.

## 12. Failure and resume semantics

- A pre-dispatch source/package/authority/test/root/environment mismatch
  creates no dispatch consumption and no executable root; it blocks.
- Once a compatibility or micro child launches, any protocol, timeout,
  process, source, publication or counter failure consumes that dispatch and
  terminalizes an immutable failure root.  No retry or resume is permitted.
- Once sentinel/official science starts, any scientific, numerical,
  provenance, protocol or resource failure is terminal, nonresumable and
  nonretryable.  No code or threshold edit may surround a retry.
- A genuine system interruption is not a scientific failure.  Resume is
  permitted only if a separately reviewed controller was frozen before the
  run, validates a complete immutable committed prefix, uses the same root
  and exact sources, obtains a new T0 one-use resume dispatch, and starts at
  the exact next uncomputed node.  Otherwise the root remains incomplete and
  no restart is authorized.
- Missing leaf events, unacknowledged frames, torn output, unauthenticated
  trailing bytes, source drift, unknown paths or inability to prove PG-empty
  always fail closed.
- Any failure of the compatibility matrix, micro or full sentinel returns to
  formal T7/T0 adjudication.  V3.1-Y does not silently create a bounded repair
  or a new attempt.

## 13. What may be shared, and what may not

### May be shared as immutable authority or implementation knowledge

- V3.0 domain, formulas, phase taxonomy, literature matrix, thresholds,
  convention note, exact anchor selector and certificate IDs;
- the exact BHPT 25-file/5-directory source snapshot, freshly revalidated and
  freshly materialized under the new root;
- the reviewed NumericalIntegration method, boundary geometry, In/Up
  decomposition, node graph, precision schedule and pure algebra;
- generic lessons and test ideas from X: strict JSON parsing, atomic
  publication, durable Popen lifecycle and source start/end closure;
- X source bytes as read-only historical inputs to a T7 delta review.

### Never reusable as V3.1-Y scientific or authority evidence

- any V3.1, V3.1-U or V3.1-X computed value, successful subset, raw outcome,
  cache, checkpoint, root-local overlay, request or timing promotion;
- X attempt-0001/0002 dispatches or roots, the review-only preflight, its
  transcript, or any planned X micro/full/official authority;
- the 14 MST successes, the observed 318-route map from a failed predecessor,
  or any post-hoc subset;
- a Python reconstruction as a substitute for a target-kernel observation;
- a compatibility or micro result as source-load or numerical science;
- sentinel values in the official candidate.

## 14. Authority identity audit

The following files were read and freshly hashed in this turn.  The hashes
match the frozen chain supplied to T4.

The mutable coordination documents were read for context only and were not
edited.  Their analysis-start identities were:

```text
project.md                 fdba5646eb0d9bb0776ea6148e509d91124871cf371ac08a7229b10e18b63b9a
status.md                  15e2b4fb1578d47de2848eb7c52ca02803e5076706bda38f700428482db8abbe
docs/handoffs/T0_current.md 18e0f3ba900db4906fb38bcb2ea51b1ce2682a404312d4dc3e5fb2ac95f2c85a
docs/handoffs/T4_current.md 6ff654c3a5feae15f56d4d01e5e733134979980d2e8f18b61823a8685399a134
docs/handoffs/T7_current.md 03c04e335568d5b1c08a0f038138ab9149c730b40bf3becd231ee9f52f9efb6b
```

### 14.1 Governing and V3.0 authorities

| Path/role | SHA-256 |
|---|---|
| Y analysis prompt | `653cd1e8a20fdb6085c5bf1c3081ca19f1632176a3a915bf20798a885a903fb6` |
| T0 final X adjudication | `7fd2012a57e86a8b085114c3b68243db616e8437983bf150ee85b2474775cee5` |
| T7 final X review | `e5f9b9503e16b053525dfba7dacb661abc433211d49dcccb2c5c9dc442af1dee` |
| liveness protocol | `3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181` |
| V3 master prompt | `f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7` |
| V3.0 validation contract | `0f8b8c96e01321231377c857ab40d710aa80ac06dce9084029fe2914b1ef37d3` |
| V3.0 formula map | `e5b556667c28ac8b611430d2dfb4faa5da82b9c7f0c8251251029e3f8c8d0eac` |
| V3.0 phase taxonomy | `fb91f4cf888dd4984174304783875c9f2e591490df8519bafd2e0b0f73053460` |
| V3.0 literature matrix | `088834348e980b81f814340a2a2c460b5bf11239521085c358bed7a90f603328` |
| V3.0 domain | `803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b` |
| V3.0 thresholds | `91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a` |
| V3.0 external anchors | `06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485` |
| V3 convention note | `82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a` |
| formal V3.0 T7 review | `b672c7f33d2f3cc891f455c6d8123ed846309a07244696da34236f8e254c0126` |

### 14.2 V3.1-U/X boundary and current X sources

| Path/role | SHA-256 |
|---|---|
| V3.1-U replacement package | `decde34bcdc90db0bc69be446357e306cfe942c84a8d575902eddaa7d1ff6877` |
| V3.1-U replacement design | `243f312182528b10a895cef679d195dcedfd97d7a2e02e388449ae3af313dd28` |
| U repair2 sentinel terminal review | `e51f32f1f7d633ff78a653d9ab2a0a49d5c1ef0d32c57f84cb9fda63abc80b55` |
| X route package | `6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752` |
| X route design | `9a75c6f80cd8360438d395caf887a13b8c88e97faef94139c6ed4dfeba4fdb8d` |
| X source-ledger repair2 package | `2f4f2304b4e9507a3627ee26d3aadd9d7632152d7367653746bedf1ec591673c` |
| X source-ledger repair2 design | `582bc3248a6acf7164485203d317b2cdc0d2a7819a13dcdb584e86e9a90bebdf` |
| current X WLS | `7a8277b6996fccbd3d0b515ebba8a0fae17a9c6a9efa7a0d3116a9055bbc041f` |
| current X direct core | `981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4` |
| current X producer | `fa0c9c2cdadead19dd1051c45fb0ac22932641a7266d9717dfd2188377945af8` |
| current X CLI | `b85a8cff88b1cab5c01b50fbd047b403d56c37952ca920bde55668cf7affa574` |
| current X unit test | `e0ad4e08c84921cb1eaaf1a91e351e189e474938678b56d033c3494cbb7574c3` |
| current X regression test | `ee79b8c276cc9eee369e97de83a3008714f090a1c735b7872f05e901cb3a862d` |

The preceding V3.1/V3.1-U governance chain was also read in full.  Compact
start identities for the bounded-repair authorities are:

```text
V3.1 T4 prompt / T7 prompt
  7e377f64782b8311e111469f53eeb182190d30347ffe0d9853a41b96deeafab6
  058cea918e0c41537b4af8b3973dbe9d378cd3b612aad884ac986d14733d3899
V3.1 initial terminal review
  d0cb93d0ade94d0376a09e4207d6059558c04c2b45383fcb42039525dad2d7c5
V3.1 repair1 package / design / T4 prompt / package review / delta review
  a439c5c0f93c8ae4ce5b01e8e6a1d98c8f55eb150615177ccfb5b2a1ee786255
  710eecce86e7372c837335ef630cfda94e4e718ac1f7490773e15fa11f349270
  40324abfede42f5ce484d34909cd1a20eeaf2e9cc35b290a8f40921af116f0d2
  1be2473c15a69abdfcd11231d9a393ea7014bdea9ec849990b900a8ba89aa404
  cbd04d5bba74fef2daffca62f9e80c5c0a6589f89b35812aa8ce10a60592f55b
V3.1 repair2 package / design / T4 prompt / package review / terminal delta
  5bce1966b76c85b49c79cb7d98c481403a4b5006bb48bd2d4d47ea67f879b2c4
  746d8753408bdb74cd1a9597108a63cf3c67842dc6cbedcbbb56fb68c0f967a7
  f2d0b45613ca8c10c5b36715379f215644dce31079e577ff11279b478ec81ed9
  6c3d9371ec2d191f4b6ee10076ad264127bc858142c0972225e2a18638431cc1
  fe2b1c351fb02e8f67af7cd5e22547d305fe5d4ead2edf681a85f19f1e61c0f3
V3.1-U replacement package / design / T4 prompt / package review
  decde34bcdc90db0bc69be446357e306cfe942c84a8d575902eddaa7d1ff6877
  243f312182528b10a895cef679d195dcedfd97d7a2e02e388449ae3af313dd28
  a1bffc42a381489dadd483edf2e6952d97ce236fbad3fe9ca82eb8b0ca862945
  9616b3fb4d0999e782e164740f5815f6bcdf46a955910cd2bcfcae032bde75cf
V3.1-U repair1 package / design / T4 prompt / terminal review
  85bff01def7286ebaf1682d5b5498209dfbbc452e098e1d8633e05fcc1b7554c
  efa30a32e46db3e64ced8bfad95b720a0aae003e5361b81526d5801ffa48f1ff
  5a4bf3c05424671b23a95e11ecbffbdd5e65304fbf43f9b1f6e38c910bf48c15
  7552b2dbc19269be0eb11b61ae8eb04c55a1225d10db1962d881e0f6ac7925c1
V3.1-U repair2 package / design / T4 prompt / terminal review
  61460a45d4d47ba9247e68969a5d91e2d77aac722c9324014a414ed4126dbfa2
  ce57d7e8fd6cc4fc61398e448260368662d9aa39da2d53ec4e1342b84d4d0029
  8287aaff8564554a56bc3cc673c825019f8ead955612eae33ab3543c4b208e80
  e51f32f1f7d633ff78a653d9ab2a0a49d5c1ef0d32c57f84cb9fda63abc80b55
```

The two consumed X manifests remain exact and denylisted:

```text
attempt-0001 d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772
attempt-0002 6e0d2349d998f76ee8d149e4551bf27222c5d93bf4ec9fb7b790adbc9f506109
```

The external runtime remains the exact executable
`/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel`,
mode `0755`, size `167488`, nlink1, SHA-256
`70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c`,
version authority `14.3.0 for Mac OS X ARM (64-bit) (July 8, 2025)`.

The external source snapshot remains 25 files/five directories with metadata
`8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488`,
content inventory
`d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2`
and restored identity
`a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27`.

### 14.3 Seven protected radial source identities

```text
radial_solver.py             9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
conditioned_radial.py        91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
scaled_tortoise_radial.py    d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
adaptive_jost_radial.py      3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
matching.py                  9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
physical_boundary_radial.py fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
boundary_conditions.py       b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
```

## 15. Formal T7 review points for a future package

Formal package and implementation review should independently require:

1. distinct V3.1-Y liveness ID and exact-six path boundary;
2. a static proof of the `StringNormalize` failure and a real-kernel matrix
   event that confirms the target semantics without treating old rc69 as a
   leaf observation;
3. exact predicate registry, no compound semantic gate, explicit Boolean and
   typed expected/observed parity across WLS/Python;
4. real one-launch compatibility transcript with every matrix row and zero
   science counters;
5. parent-owned ACK/durability and fake-child rejection;
6. exact one-launch source micro, Paclet/FindFile/source start/end closure and
   zero science counters;
7. exact 23/35/161 graph and source/method/precision invariants;
8. complete fault injection, lifecycle closure and immutable manifests;
9. noncircular one-use authority paths and permanent X denylist;
10. unchanged 16 thresholds, five certificates, conventions, snapshot and
    seven protected identities;
11. sentinel-derived resource projection before official dispatch;
12. explicit nonclaims and `global_green_permitted=false`.

No package is approved by this analysis alone.

## 16. Nonclaims

- V3.1, V3.1-U and V3.1-X remain failed or not assessed as formally recorded.
- V3.1-Y implementation, compatibility, micro, sentinel and science are all
  `NOT_ASSESSED`.
- The static cause reconstruction is not a new real-kernel observation; old
  runtime evidence still has `failed_leaf=UNKNOWN`.
- There is no independent even-sector external result.
- There is no pristine-upstream claim for the reviewed boundary overlay.
- There is no common absolute scattering-phase validation.
- There is no V3.2 authorization, Li-figure claim, finite-radius observer
  claim, full-domain V3 certificate or global GREEN.
- This document creates no package, dispatch, executable root or review
  authority.

CHECKPOINT / V3.1-Y EXTERNAL PROTOCOL REDESIGN ANALYSIS READY FOR T0 PACKAGE FREEZE
