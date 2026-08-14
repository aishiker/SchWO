# Phase 6 V3.1-Y external protocol frozen design

Date: 2026-08-13 (UTC material identity date)  
Gate: `phase6_v3_1_y_external_protocol_v1`  
State: `FINAL REPAIR-CYCLE-2 CORRECTED CANDIDATE / T7 DELTA-2 REVIEW REQUIRED`

Repair authority: predecessor package SHA-256
`bbb9e97636a8da63d6e29be2a013fb99f09c8667a1608688de03006a9d916203`;
initial T7 review SHA-256
`1cc0da4cdfd7c9aecf7306ba7dd7b10219ce14f93e3a1c8bca37afe12417ac6b`.
Repair-cycle-1 delta review SHA-256
`63c1ae9286fa5cb7b07ee4c2995a7cf6bb71f9e1bc941399d46861f65f1aa499`.
This final bounded revision addresses only the two remaining package
blockers; it is not implementation or scientific evidence. There is no
repair cycle 3.

## 1. Purpose and non-circular lineage

V3.1-Y is a distinct protocol redesign after V3.1-X exhausted both bounded
repairs and formal T7 returned `ESCALATE / NOT_ASSESSED`.  It is not V3.1-X
repair cycle 3.  The X implementation, two failed sentinel roots and the
review-only preflight are immutable diagnostics and permanent denylist items.
No computed X/U value, successful subset, request, cache, checkpoint,
dispatch, root or timing datum can enter Y science.

The only permitted reuse is immutable scientific authority and reviewed
implementation knowledge: V3.0 formula/domain/threshold/convention bytes, the
25-file BHPT source snapshot, the direct `NumericalIntegration` method, exact
boundary transformations, and pure algebra whose identities are explicitly
bound.  Every Y runtime observation is fresh.

The package does not authorize implementation or execution.  Formal T7 must
first accept the package.  Later review digests are never hardcoded before the
review exists: each later one-use T0 dispatch supplies the one exact digest of
the predeclared prior review path.

## 2. Frozen scientific boundary

The V3.0 domain, external-anchor matrix, formulas, phase taxonomy,
conventions, 16 thresholds and five certificate IDs are unchanged.

All package, dispatch, evidence and review timestamps use UTC.  Root names
must contain an RFC-3339-basic UTC stamp of the form `YYYYMMDDTHHMMSSZ`, and
every run contract and manifest must also carry `timezone="UTC"` plus the
full `created_at_utc` value.  Local wall-clock labels are never ordering
authority; hashes and the explicit predecessor graph are.

- production Route A: `496` modes and `9920` ladder nodes;
- independent AP Route U: `N_U` modes and `3*N_U` precision nodes, where
  `0 <= N_U <= 496` is freshly derived only after all `496/9920` Route-A
  records/ladders are immutably complete;
- Route B: `102` keys and `458` nodes;
- external odd Route C: exact 23 predeclared anchors, seven nodes each,
  `161` public API calls, `322` In/Up boundary solutions and `483` overlap
  records;
- fixed full-sentinel graph: `35` public API calls, `70` boundary solutions
  and `105` overlap records;
- direct external method: BHPT Regge-Wheeler `NumericalIntegration`, spin 2,
  independent `In` and `Up`, zero MST/internal-SchWO-radial fallback;
- precision: P0 `90/45/45`; P1 and boundary nodes `120/60/60`; selected P1;
- exact rational frequency construction before arbitrary-precision
  evaluation.

All 23 external anchors form one blocking set.  No post-result 14-key subset,
per-key fallback, parity-derived independent-even claim, method selection or
threshold relaxation is permitted.

## 3. Frozen Protocol A

Protocol A is an ordered child-frame/parent-ACK state machine.  The
WolframKernel child emits one typed predicate frame at a time.  The Python
parent preserves the raw bytes, validates and independently recomputes the
owned observation, O_EXCL-publishes the event, fsyncs file and directory,
reloads and rehashes it, publishes a monotone per-event prefix checkpoint,
and only then sends an ACK containing that committed prefix-checkpoint
digest.  The final declared event of a stage additionally closes the final
stage checkpoint.  Thus a multi-event stage cannot deadlock waiting for a
checkpoint that itself requires later unacknowledged frames.  The child
cannot emit the next event without the exact
session/sequence/frame/prefix-checkpoint-bound ACK, and it cannot enter the
next stage without the prior final-stage checkpoint digest.

Parent-owned observations are not self-asserted by the child.  At a
parent-observer boundary the child emits only the frozen barrier/request
frame; the parent performs, persists and independently evaluates the
declared parent predicates before acknowledging the barrier.  Stage 0 is
committed before launch and its digest is an input to the first child frame;
the terminal lifecycle stage is committed by the parent after EOF/wait/reap
and has no child-advance ACK.  These two edge cases and the barrier IDs are
machine-frozen in the protocol contract.

The frame and ACK schemas, exact stage order, predicate registry,
compatibility cases and namespaces are machine-frozen in
`configs/phase6_v3_1_y_external_protocol_contract.json`.

### 3.1 Operation profiles and durable FSM

The registry is operation-specific; a blind global Cartesian product is
forbidden. Expansion order is exactly call plan, stage ordinal, template
declaration, then declared axis order. Every template freezes its ID format,
operations, stage, observer, axes, and values; placeholders equal the axis
list. Exact profile sizes are compatibility `1/151`, source-load micro
`1/409`, sentinel `35/14315`, and official `161/65849`, for a global ordered
total of `80724`. Compatibility contains 118 direct fixture cases and 33
common predicates. Production per-session P00..P17 counts are
`[5,9,5,10,120,4,3,16,24,24,67,7,4,24,68,7,4,8]`.

Contract revision 3 is the sole machine authority for the wire protocol. It
freezes the ordered field lists and a type/domain/nullability/value rule for
all eight artifacts: child frame `27`, parent event `29`, prefix checkpoint
`18`, final checkpoint `24`, ACK `21`, stage-open authority `29`, stage-0 seed
`25`, and child-exit authority `19` fields. Child frames and ACKs use compact
ordered `C_WIRE`; durable objects use sorted `C_OBJ`; `F`, `A`, and every
labelled `L` digest have exact domain separators and ordered input lists.
Hashes include their single terminal LF. Missing, extra, reordered, mistyped,
nullable-domain, invalid-enum, sequence, digest, barrier, replay, oversize and
extra-output mutations fail before progression.

Every event durably closes one prefix checkpoint and the event/prefix chains
continue across stage boundaries. A last event also closes the final-stage
checkpoint and next-stage-open authority before its ACK. The exact stage-0
seed binds the first event and prefix without a circular predecessor.
Compatibility uses its own seven barriers P08--P14 and totals exactly 151
events / 82 frames / 82 ACKs; source-load micro uses the two declared P10/P14
barriers and totals 409 / 263 / 263. Sentinel and official are exact 35- and
161-call products of the micro profile. At stage 16 the final and last-prefix
identities enter the child-exit authority; after child flush, EOF, wait, reap
and process-group-empty closure, a typed lifecycle receipt and that exit
authority enter the P17 open. All eight P17 events and the terminal manifest
transitively bind both. P17 has no child frame, ACK or next open.

Every predicate has one stable ID and exactly one logical comparison.
Expected and observed values are separately typed.  The outcome is exactly
`PASS`, `FAIL` or `INDETERMINATE`; symbolic/non-Boolean evaluation becomes
blocking `INDETERMINATE`.  Compound semantic `If` gates, Association-wide
identity, Association insertion-order identity, production regex path/hash
validation and `StringNormalize` are prohibited.

Source records are named-looked-up and projected in the exact order:

```text
[context,path,sha256,size,mode,nlink]
```

The required contexts and paths remain exact frozen literals.  Path and hash
syntax use explicit ASCII code-point predicates.  `CharacterNormalize` is a
compatibility diagnostic only; production authority requires raw exact ASCII
literal equality and never normalizes an untrusted path into acceptance.
`mode`, `nlink`, inode and no-follow/link observations are parent-owned POSIX
facts and cannot be self-confirmed by the child.

## 4. Structural separation of zero-science and science-capable code

The compatibility WLS is a separate file and has no BHPT/Paclet/source-load or
science-capable call site.  It exercises only target-kernel language,
serialization, framing, Boolean, string, Unicode, integer and ACK semantics.

The science-capable WLS contains a source-load-micro operation and a direct
node operation.  The source-load micro exits at the pre-science commit before
the sole reviewed BHPT public API call site.  Static call-graph tests and
runtime counters must both establish zero external API, radial, solver,
boundary, overlap and scientific calls for compatibility and micro.

### 4.1 Fresh Route-U selector

The only selector input is the exact ordered fresh 496-entry Route-A view
`[ordinal, mode, Gamma_flux_decimal, log_Gamma_flux,
source_record_sha256]`. The rule is exactly
`direct log_Gamma_flux < log(1e-8)`; equality is non-U and invalid operands
fail closed. Stable filtering yields `N_U` keys and `3*N_U` nodes. Fixed
`318/954` membership or count acceptance is forbidden; a fresh 318 is allowed
only if the fresh selector independently returns it.

The failed predecessor root
`runs/phase6/classic_scattering/v3_1_hp_unitarity_deficit_repair1_v1_20260812T064653Z_py314`
and its failure `e3874e7565dc35498513af8112577810dd9059035f43a9d4573d633c2ae752aa`,
manifest `f977a0d555652d028b3b73d18990b902f37a55c3dd9305c6e6da55f66593050d`,
and route map `5eee07ece78204265fe45069ef57a653a61a8ee9d09ff4b4d7e8928bb385c822`
are explicit denylisted inputs.

## 5. Durable evidence protocol

Every executable stage creates one fresh direct-child root.  Predicate frames,
events, ACKs, per-event prefix checkpoints and final stage checkpoints are
individual immutable files.  Aggregate
JSONL is a derived index and cannot replace a missing event.  Required paths
include raw/canonical request, dispatch consumption, run contract, source
start/end, process prelaunch/running/receipt/terminal, raw stdout/stderr,
per-frame raw/event/ACK files, per-stage checkpoints, result or failure, and a
non-self-referential manifest.

Files are regular O_EXCL/no-follow/nlink1, atomically published, file+parent
fsynced, reloaded and sealed `0444`; directories close `0555`.  The manifest
enforces an exact allowed-path grammar.  Missing/extra/duplicate/reordered
events, unknown bytes, replayed ACKs, partial publication, aliases, source
drift, failure to reap or inability to prove process-group empty fail closed.

## 6. Ordered gates

The only authority order is:

```text
package -> formal T7 package ADVANCE
        -> T6 exact-six zero-science implementation
        -> formal T7 implementation ADVANCE
        -> one-use T0 real-kernel compatibility dispatch/root
        -> formal T7 compatibility ADVANCE
        -> one-use T0 source-load-micro dispatch/root
        -> formal T7 micro ADVANCE
        -> one-use T0 35-call sentinel dispatch/root
        -> formal T7 sentinel ADVANCE
        -> one-use T0 official attempt-0001 dispatch/root
        -> formal T7 scientific review
```

Compatibility and micro roots are non-scientific and non-reusable.  Sentinel
values are not official values.  Each executable dispatch is one-use and has
no retry.  Any failure terminalizes an immutable failure root and returns to
formal T7/T0 adjudication.  A repair, if permitted by the liveness protocol,
requires a separately frozen package revision and fresh namespace; no code
edit may surround a retry.

## 7. Exact implementation scope

Only these six new paths may be created after package approval:

```text
scripts/phase6_v3_1_y_wolfram_protocol_compatibility.wls
scripts/phase6_v3_1_y_bhpt_direct.wls
src/schwgw/validation/phase6_v3_mode_greybody_external_protocol.py
scripts/phase6_v3_1_y_external_protocol.py
tests/unit/test_phase6_v3_external_protocol.py
tests/regression/test_phase6_v3_external_protocol_publication.py
```

The producer may import the frozen pure direct-route core at SHA-256
`981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4`
but may not import the V3.1-X producer, CLI or evidence control plane.  Any
seventh implementation path or protected/scientific authority change stops
the gate.

## 8. Pre-execution verification

Implementation review is zero-science and fake-process/static only.  It must
cover every machine-contract predicate and compatibility case, plus lifecycle
faults before/after frame, fsync, checkpoint, ACK, launch, timeout, wait, reap
and terminal publication.  A fake child with perfect values must still fail
real-runtime authority.

Only after formal implementation ADVANCE may the real compatibility matrix
run once.  It must confirm the static `StringNormalize` diagnosis as a new
target-kernel observation without changing the historical X leaf from
`UNKNOWN`; verify `CharacterNormalize`, `SameQ`, explicit Boolean semantics,
RawJSON heads, integer types, Unicode/path/string behavior, frame/ACK behavior
and process closure; and report all science counters as zero.

The different one-use source-load micro then authenticates Paclet, eight
contexts, eight loaded files and the complete source snapshot start/end.  It
exits before the public API call and reports all science counters as zero.

## 9. Resource and stop contracts

- compatibility: one kernel launch, hard timeout 120 s, root cap 16 MiB;
- source-load micro: one kernel launch, hard timeout 120 s, root cap 16 MiB;
- CPU concurrency: one;
- full sentinel: all 35 calls, with fresh measured runtime/storage projection;
- official: safety factor at least 2, projected wall time at most 36 h,
  projected bytes at most one quarter of current free workspace space.

Timeout, signal, malformed frame, missing ACK, source drift, counter mismatch,
protocol failure, threshold failure or resource-gate failure is terminal.

## 10. Acceptance and nonclaims

Corrected-package GREEN means only that implementation may begin.  Implementation GREEN
means only that a one-use compatibility dispatch may be created.  Compatibility
GREEN permits only the source-load micro.  Micro GREEN permits only the
35-call sentinel.  Sentinel GREEN permits only a fresh official run.  Final
V3.1-Y GREEN means the frozen bounded V3.1 gate may enter V3.2; it does not
mean full-domain, independent-even, V3-wide or global GREEN.

No Li-figure agreement, finite-radius observer response, common absolute
scattering phase, independent external even-sector result or full V3 closure
is claimed here.
