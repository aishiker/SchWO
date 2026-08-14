# Phase 6 V3.1-X sentinel repair cycle 2: source-ledger boundary design

Date: 2026-08-13
Gate: `phase6_v3_1_x_external_direct_route_v1`
Status: zero-science design only; no implementation or execution authority

## 1. Decision and scope

This is the final bounded V3.1-X repair cycle.  It repairs one exact
pre-solver source-provenance comparison defect and adds a separately reviewed
real RawJSON-to-Wolfram source-load handshake.  It is not repair cycle 3, an
attempt-0001/0002 retry, an official run, V3.2, or a change to numerical
science.

The authoritative terminal review is:

```text
docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_sentinel_attempt_0002_terminal_review.md
SHA-256 7f002b2e2abb5a80d0836ff4d458a52842af4aad337db0d1e50c8dc1ce8da232
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-X SENTINEL CHANGES REQUIRED
```

The sole live blocker is
`v31x-sentinel-loaded-source-ledger-structural-comparison`.  All scientific
results remain `NOT_ASSESSED`.

The implementation delta may touch no more than these five paths:

1. `scripts/phase6_v3_1_x_bhpt_direct.wls`
2. `src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py`
3. `scripts/phase6_v3_1_x_external_direct.py`
4. `tests/unit/test_phase6_v3_external_direct.py`
5. `tests/regression/test_phase6_v3_external_direct_publication.py`

The direct physics module
`src/schwgw/validation/phase6_v3_external_direct.py` is byte-frozen and must
not change.  The package, graph, overlays, numerical method, precisions,
admission criteria, domain, thresholds, conventions, seven protected radial
files, and both failed roots are also frozen.

## 2. Exact causal proof

The request is canonical JSON with sorted object keys.  Each of its eight
loaded-source objects is therefore imported with the insertion order

```text
[context, mode, nlink, path, sha256, size].
```

The WLS currently constructs each fresh `Association` in the literal order

```text
[context, path, sha256, size, mode, nlink].
```

For all eight records, the values of all six fields are identical.  The
ordered contexts, paths, SHA-256 values, sizes, modes and link counts were
independently reloaded from the attempt-0002 overlay and passed.  Nevertheless,
Wolfram `SameQ` on the two `Association` expressions at WLS line 132 is
order-sensitive, so the process emits `loaded source start mismatch` and
returns 69 before the `ReggeWheelerRadial` call at line 143.

This diagnosis is representational, not scientific:

- attempt 0001 failed at the real `$CommandLine` boundary with rc64;
- repair cycle 1 closed that argv defect;
- attempt 0002 passed argv, request, overlay, Paclet, context and every
  `FindFile` gate, then failed only at the order-sensitive ledger comparison;
- attempt 0002 made zero external API, solver, boundary-solution, overlap and
  scientific calls;
- no source byte or semantic ledger value drifted.

Attempts 0001 and 0002, their dispatches and their roots are permanently
consumed.  Neither may be resumed, retried, replayed, repaired in place,
promoted, cached, or used as scientific input.

## 3. Single semantic source-record projection

### 3.1 Fixed schema and field order

The WLS must define exactly one source-record normalizer.  No second key
projection, fallback comparison or structural `Association` comparison is
permitted.

```text
SOURCE_FIELD_ORDER = [context, path, sha256, size, mode, nlink]
SOURCE_FIELD_SET   = the exact six names above
```

The semantic output is a six-element Wolfram `List`, not an `Association`:

```text
{record["context"], record["path"], record["sha256"],
 record["size"], record["mode"], record["nlink"]}
```

The normalizer must, in this order:

1. require `AssociationQ[record]`;
2. require the exact six-key set, with no missing or extra key;
3. require exact types: three strings followed by three integers;
4. require the context supplied by the frozen context position;
5. require lowercase 64-hex SHA-256, nonnegative size, mode `292` (`0444`),
   and `nlink == 1`;
6. require a normalized relative path with no empty component, `.` or `..`,
   no absolute form and no alternate Unicode/case spelling;
7. return the six values in `SOURCE_FIELD_ORDER`.

Object member order is deliberately non-semantic after the exact-key-set
check.  Record-list order remains semantic.

### 3.2 Exact ledger normalization

The eight frozen contexts remain in this literal order:

1. `ReggeWheeler\``
2. `ReggeWheeler\`MST\`MST\``
3. `ReggeWheeler\`MST\`RenormalizedAngularMomentum\``
4. `ReggeWheeler\`NumericalIntegration\``
5. `ReggeWheeler\`Hyperboloidal\``
6. `ReggeWheeler\`ReggeWheelerRadial\``
7. `ReggeWheeler\`ReggeWheelerSource\``
8. `ReggeWheeler\`ReggeWheelerMode\``

`normalizeLedger` must require a list of exactly eight records and use
position-wise mapping against this context list.  It must reject duplicate
contexts, duplicate normalized paths, wrong context position, and any
cardinality mismatch.  It must not sort the record list, convert it to a set,
deduplicate it, normalize case/Unicode, or drop a field.

The comparison is exactly:

```text
expectedProjection = normalizeLedger[request["loaded_source_records"]]
actualStartProjection = normalizeLedger[freshSourceRecords[]]
SameQ[actualStartProjection, expectedProjection]
```

and, immediately before output publication:

```text
actualEndProjection = normalizeLedger[freshSourceRecords[]]
SameQ[actualEndProjection, expectedProjection]
SameQ[actualEndProjection, actualStartProjection]
```

`freshSourceRecords[]` must independently obtain the actual source path from
`FindFile`, compute SHA-256 and byte size from that file, and use the frozen
literal mode/link contract only after exact `FindFile` path equality.  The
Python parent independently reloads regular-file type, path, device/inode,
mode, nlink, size and SHA-256 before and after the child.  Thus a wrong
mode/nlink cannot pass by being copied from the request: WLS requires the
literal `0444/nlink1` contract, while the parent verifies the actual stat.

The request writer and Python loader must reject duplicate JSON object members
before launching Wolfram.  RawJSON import cannot reliably recover duplicate
member history after parsing; therefore a last-member-wins document is not an
accepted input to the WLS boundary.

### 3.3 Alias and time-of-check closure

Every source file and each of the five snapshot directories must be a regular,
non-symlink, non-hardlinked object under the exact snapshot/overlay root.
Resolved paths must be direct descendants at their frozen relative paths.  A
fresh pre-child and post-child inventory must bind path, device, inode, mode,
nlink, size and SHA-256.  The WLS start/end ledgers additionally bind actual
`FindFile` resolution.  Any atomic replacement, alias, source mutation,
context relocation or parent-directory drift fails the current stage.

The frozen 25-file/five-directory snapshot indexes remain:

```text
content_inventory_sha256  d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2
identity_inventory_sha256 a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
```

## 4. Distinct source-load micro-sentinel

### 4.1 Purpose and exact workload

The micro-sentinel is a control/provenance handshake, not science.  It uses
the exact frozen key `V3A-MODE-BHPT-RW-001` and node `P1` only to validate the
same request schema and frozen route metadata that the full sentinel will use.
It launches exactly one fresh Wolfram process and performs:

1. exact executable/argv/cwd/environment validation;
2. canonical request import and exact request schema validation;
3. overlay and 25-file/five-directory snapshot validation;
4. `PacletDirectoryLoad`, exact context closure and eight `FindFile` checks;
5. normalized loaded-source start ledger;
6. normalized loaded-source end ledger;
7. canonical result publication and complete child closure;
8. exit before any evaluation of `ReggeWheelerRadial`.

Its exact counters are:

```text
wolfram_launch_count             = 1
request_count                    = 1
source_record_count_start        = 8
source_record_count_end          = 8
external_api_call_count          = 0
regge_wheeler_radial_call_count  = 0
solver_call_count                = 0
boundary_solution_count          = 0
overlap_record_count             = 0
scientific_call_count            = 0
```

The WLS operation is a literal authenticated operation, for example
`source_load_micro_sentinel`; it is not selected by an environment variable,
free boolean, filename inference or arbitrary fallback.  The micro branch
must be statically and dynamically proven to exit after the second ledger
check and before the first `ReggeWheelerRadial` expression.

### 4.2 Micro result and nonpromotion

The canonical micro result must contain exactly:

- schema and operation;
- exact key/node identity;
- request, dispatch, implementation-review and source identities;
- runtime, argv, cwd, requested and observed clean environments;
- overlay, Paclet, contexts and `FindFile` identities;
- both exact eight-record ledgers and their projection digest;
- all zero counters above;
- `scientific_evidence = false`;
- `reusable_as_science = false`;
- `reusable_as_full_sentinel_record = false`;
- child PID/SID/PGID and complete lifecycle closure;
- terminal state `PASS_PENDING_FORMAL_T7_REVIEW` or a truthful failure state.

Neither the raw result nor any micro artifact may satisfy a full-sentinel
record, contribute to the 35/70/105 totals, seed a later request, cache a
source load, or be promoted into official evidence.  The full sentinel must
rehash and reload every source again.

### 4.3 Durable micro artifact set

The micro root uses exclusive/no-follow creation and canonical serialization.
At minimum it contains immutable, independently reloadable records for:

```text
dispatch_consumption.json
source_start.json
static_contract.json
writer_exclusion.json
micro_request.json
child.prelaunch.json
child.running.json
child.stdout.raw
child.stderr.raw
child.receipt.json
child.terminal.json
source_load_result.json
source_end.json
micro_result.json              # success only
failure.json                   # failure only
manifest.json
```

All files are regular non-symlink `0444/nlink1`; completed directories and the
root are `0555`.  File publication is O_EXCL/no-follow, temp-file + fsync +
exclusive atomic rename, reload/hash/stat verified, followed by parent fsync.
The manifest is non-self-referential and exactly binds every other artifact.

## 5. Non-circular authority graph

### 5.1 Predeclared names

The future package must freeze these unique names; it must not freeze the
future archive digests inside the implementations that the archives review.
The subsequent T0 dispatch supplies exactly one digest for each fixed path.

Implementation review authority:

```text
docs/handoffs/archive/
T7_2026-08-13_v3_1_x_sentinel_repair_cycle2_source_ledger_implementation_delta_review.md
```

Micro one-use dispatch basename:

```text
T0_2026-08-13_v3_1_x_source_load_micro_sentinel_dispatch_attempt_0001.json
```

Micro root namespace, direct child of
`runs/phase6/classic_scattering`:

```text
v3_1_x_source_load_micro_sentinel_v1_<YYYYMMDDTHHMMSSZ>_py314
```

Micro terminal review authority:

```text
docs/handoffs/archive/
T7_2026-08-13_v3_1_x_source_load_micro_sentinel_terminal_review.md
```

Later full sentinel dispatch basename:

```text
T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0003.json
```

Later full sentinel root namespace:

```text
v3_1_x_external_direct_sentinel_repair2_v1_<YYYYMMDDTHHMMSSZ>_py314
```

Later full sentinel terminal review authority:

```text
docs/handoffs/archive/
T7_2026-08-13_v3_1_x_external_direct_sentinel_attempt_0003_terminal_review.md
```

The official dispatch remains attempt 0001 and the official root namespace
remains `v3_1_x_external_direct_v1_<UTC>_py314`; this design does not create,
change or authorize either.

### 5.2 Authority DAG

```text
repair-2 package + formal package review
  -> exact five-path implementation + zero-science tests
  -> formal T7 implementation delta ADVANCE
  -> one-use T0 micro dispatch
  -> one fresh micro root, one Wolfram launch, zero science
  -> formal T7 micro terminal ADVANCE
  -> distinct one-use T0 full-sentinel attempt-0003 dispatch
  -> one fresh repair2 full-sentinel root, exact 35/70/105 science
  -> formal T7 full-sentinel terminal ADVANCE
  -> unchanged future official attempt-0001 eligibility
```

No edge may be inferred from filenames or environment.  Each child authority
record binds the fixed parent path plus the digest supplied by the later T0
dispatch.  A predecessor YELLOW/FAIL archive, live handoff, alternate archive,
glob result or multiple-choice hash is never accepted.

The micro T7 review must verify the actual immutable micro root and contain
exact `ADVANCE`, claim status and gate-label tokens.  The full-sentinel
dispatch must bind that review and the implementation review independently.
The micro review cannot approve itself because its digest is absent until
after the micro root closes; it is used only by the later full dispatch.

Attempts 0001 and 0002 remain explicitly forbidden in dispatch validation,
one-use scans and manifest nonreuse records.  Attempt 0003 must bind a fresh
exact root whose resolved path differs from both failed roots and the official
namespace.

## 6. One-use launch and terminal protocol

For both micro and full sentinel:

1. Rehash all frozen package, review, implementation, snapshot, V3.0 and
   protected identities.
2. Require exact absolute executable, script, dispatch and root paths; exact
   command order; exact project cwd; and exact clean requested/observed
   environments.
3. Require the target root absent and its parent non-aliased; reject symlink,
   hardlink, alternate parent, Unicode/case variant and preexisting path.
4. Require no live writer or related process and acquire the stable writer
   exclusion before mutation.
5. Create the root and O_EXCL-publish `dispatch_consumption.json` before the
   first child call.  Its one-use ID is globally searched and must be absent.
6. Publish source start, static contract and process records durably.
7. Launch once.  No retry, resume, fallback executable, cache or second child
   is permitted.
8. On timeout or exception: terminate the process group, bounded wait, kill if
   still alive, final wait/reap, prove PG empty, close both streams, publish
   receipt/terminal/failure/manifest while writer exclusion remains held.
9. On success: require natural rc0, no signal/timeout/wait error, empty stderr,
   exact expected stdout/result, wait called, child reaped and PG empty.
10. Rehash sources and authorities at end, publish result/manifest, chmod files
    `0444`, directories/root `0555`, fsync, and never reopen for writing.

Any launched micro or full-sentinel failure is terminal `ESCALATE / T0
ADJUDICATION REQUIRED`.  There is no retry, repair cycle 3 or alternate
dispatch.  A repair-2 implementation delta failure or real micro failure also
exhausts this gate.

## 7. Test and review matrix

### 7.1 Semantic projection tests

Required positives:

- canonical JSON key order and WLS literal Association order normalize to the
  same six-element vector;
- all permutations of Association member order normalize identically when
  the exact six names and values are present;
- exact eight records in frozen context/list order pass at both start and end;
- a real Python canonical RawJSON request reaches the real WLS normalizer in
  the micro-sentinel and returns the same projection.

Required negatives, independently at start and end where applicable:

- missing or extra field;
- duplicate JSON member rejected before WLS launch;
- missing, extra or duplicate record;
- reordered context/record list;
- duplicate context or duplicate path;
- wrong context, relative path, SHA-256, size, mode or nlink;
- absolute path, `..`, case/Unicode variant, symlink, hardlink, inode alias or
  outside-root resolution;
- WLS `FindFile` path differs from the frozen overlay path;
- source mutation or replacement between start and end.

Restoring `SameQ[Association, Association]` without normalization must make a
discriminator test fail.

### 7.2 Micro-sentinel tests

- synthetic tests may validate schemas and lifecycle, but a fake child that
  echoes request ledgers must carry `fake_child=true` and can never satisfy the
  formal micro acceptance validator;
- the only valid RawJSON-to-Wolfram boundary acceptance is the separately
  authorized real one-launch micro root;
- static AST/text/dataflow inspection proves the micro branch exits before
  `ReggeWheelerRadial` and cannot reach boundary/overlap code;
- exact P1 key and zero counters are required; any other key/node or nonzero
  counter fails;
- micro data cannot validate as a full sentinel record and cannot be read as
  a later scientific input.

### 7.3 Lifecycle/publication tests

Inject failures after each boundary: consumption, request, prelaunch, Popen,
running record, stdout/stderr creation, timeout, terminate, kill, wait, receipt,
terminal, source end, result, manifest and chmod.  Every path must leave either
a complete immutable success root or a complete immutable failure root, never
an accepted partial root.  Tests must cover nonzero exit, signal, unreadable
stream, unreaped child, nonempty PG, wait error, preexisting file, torn JSON,
noncanonical JSON, wrong mode/link, extra/missing manifest entry and manifest
self-reference.

### 7.4 Authority tests

- exact future implementation-review path positive, with digest supplied only
  by the later dispatch;
- predecessor YELLOW/FAIL path, live handoff, alternate path/digest/verdict,
  missing future file and stale implementation hashes negative;
- exact micro dispatch/root namespace positive; wrong parent, alias, malformed
  UTC, reused one-use ID and attempt-0001/0002 identity negative;
- full attempt-0003 dispatch fails without a formal micro `ADVANCE` review;
- micro dispatch cannot authorize full sentinel or official;
- full sentinel dispatch/root cannot alias the micro or failed roots;
- official attempt-0001 rules and root namespace remain unchanged.

### 7.5 Frozen-science regression tests

Static and hash checks must prove no change to the core direct physics module,
node graph, formulas, precisions, overlay bytes, 23 anchors, 35/70/105
sentinel totals, 161/322/483 official totals, 16 thresholds, five certificate
IDs, conventions, seven protected radial files, or official nonreuse rules.

## 8. Additional failure modes found by this analysis

These were not the literal rc69 cause but must be closed now to avoid another
false acceptance cycle.

### FM-1: duplicate JSON member collapse

Many JSON parsers retain only the final value of a duplicate member.  An exact
post-parse key-set check alone could therefore accept a document whose raw
object repeated `sha256` or `path`.  The producer must use a duplicate-key
rejecting loader and canonical-byte check before any dispatch consumption or
Wolfram launch.  Tests inject equal and unequal duplicate members.

### FM-2: preloaded context or Paclet search contamination

A fresh kernel could still resolve a context from an unreviewed `$Path` or
preloaded Paclet if the environment/search path is not exact.  The WLS must
record the pre-load `$Packages`/Paclet state, require the reviewed loading
sequence, and prove every post-load `FindFile` path is under the exact overlay.
Tests inject a competing context/Paclet and altered search path; both fail.

### FM-3: source TOCTOU with semantically equal replacement

Replacing a file between parent preflight and WLS load could preserve path,
size and even content while changing inode/link provenance.  Parent start/end
inventories must bind device/inode/mode/nlink as well as content; WLS start/end
must bind the loaded path/content.  Tests atomically replace one file with
same bytes and require failure.

### FM-4: micro-mode branch confusion

If operation selection is inferred from an output filename, environment value
or optional boolean, an attacker could turn the zero-science micro into a
solver call or suppress a full call.  The operation must be a literal field in
an authenticated stage-specific request and dispatch, with an exact CLI
subcommand/argv.  Cross-stage requests and extra options fail before launch.

### FM-5: self-confirming fake boundary

The existing regression fake copies `request.loaded_source_records` into both
result ledgers.  This tests Python plumbing but cannot test RawJSON import or
Wolfram expression semantics.  Formal acceptance must explicitly reject
`fake_child`, require the exact Wolfram runtime/source identities and bind the
real one-launch micro terminal record.

### FM-6: source changes after micro acceptance

A passed micro review is permission to attempt the full sentinel, not a source
cache.  Full attempt 0003 must rehash the five implementation files, core,
snapshot and every loaded source at its own start/end.  Any drift after the
micro review blocks before dispatch consumption/science.

## 9. Resource and time bounds

The two failed first-child lifetimes were approximately 3.24 s and 4.87 s.
Attempt 0002 loaded the complete Paclet/context closure before rc69.  Based on
those stored timings, the source-load-only micro central expectation is 5 s;
the predeclared operational band is:

```text
lower  3 s
central 5 s
upper/hard timeout 120 s
Wolfram launches 1
CPU concurrency 1
scientific calls 0
root size hard cap 16 MiB
```

The upper limits are fail-closed operational caps, not performance claims.
The micro timing must not update or relax any full-sentinel resource budget.
The full 35-call sentinel retains its existing frozen timeout, graph and
resource/admission gates; no runtime can be predicted from the pre-solver
failures because no numerical call completed.  This unknowability must remain
explicit until the separately reviewed full sentinel runs.

## 10. Future package and executable prompt requirements

This turn creates no package or prompt.  Root T0 should freeze a package with:

- a distinct repair ID, e.g.
  `phase6_v3_1_x_sentinel_source_ledger_repair_cycle2_v1`;
- this design and its archive identities;
- the exact five allowed paths and their preimplementation hashes;
- the current core, package, domain, anchor, threshold, convention, snapshot,
  runtime and seven protected hashes;
- both consumed dispatch/root terminal identities and explicit nonreuse;
- `completed_bounded_repairs=1`, `current_bounded_repair=2`,
  `maximum_bounded_repairs=2`, `cycle_3_permitted=false`;
- all fixed future authority paths/namespaces from section 5, without
  circular future SHA hardcoding;
- exact zero-science implementation tests and formal micro/full review gates;
- micro resource caps and nonpromotion fields;
- passed/failed/not-assessed freeze lists from section 11.

The future formal T6 implementation prompt must:

- permit exactly the five paths in section 1;
- require one normalizer, the exact WLS/Python dataflow and all adversarial
  tests above;
- permit only fake/temporary zero-science tests during implementation;
- forbid the real micro, dispatch/root creation, Wolfram science, official,
  V3.2 and handoff/status edits;
- return exact hashes and zero-call evidence for formal T7 delta review.

The formal T7 implementation-delta prompt must independently reconstruct the
RawJSON/WLS mismatch, audit exact five-path scope, run the zero-science test
suite, inspect the micro branch before the solver, attack every schema/alias/
authority/lifecycle surface, and return `ADVANCE` before T0 can issue the
micro dispatch.

The formal T7 micro-terminal prompt must review the immutable real micro root,
one-use consumption, exact single Wolfram launch, eight start/end records,
rc0/empty stderr/wait-reap-PG closure, zero scientific calls and nonpromotion.
Only its `ADVANCE` axis permits T0 to publish attempt 0003.

The formal T7 full-sentinel prompt must review a separate immutable attempt
0003 root for exact 35/70/105 totals and all existing budgets.  It must not
reuse the micro result as science.  Only its `ADVANCE` axis can make the
unchanged official attempt-0001 dispatch eligible.

## 11. Frozen review-state inventory

Passed/frozen and not to be reopened except for drift checking:

- repair-1 exact `$CommandLine`/argv handshake;
- attempt-0002 dispatch namespace and one-use consumption;
- exact 35-call planned graph totality;
- child lifecycle closure;
- package/domain/threshold/convention preservation;
- seven protected radial identities;
- exact eight semantic source values and overlay/context/FindFile closure;
- no predecessor/sentinel science reuse and no downstream execution.

Failed and in scope:

- only the order-sensitive loaded-source ledger comparison and the missing
  real RawJSON-to-Wolfram source-load acceptance boundary.

Not assessed and still not claimable:

- 35-call sentinel numerical science;
- 70 boundary solutions and 105 overlaps;
- official V3.1-X science;
- 16 threshold evaluations and five certificates;
- V3.2 or any global GREEN.

## 12. Start identity ledger

These identities were independently rehashed at design start.  They must be
identical at design end; the archive records the end comparison.

| Role | Path | SHA-256 |
|---|---|---|
| WLS | `scripts/phase6_v3_1_x_bhpt_direct.wls` | `24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6` |
| direct core | `src/schwgw/validation/phase6_v3_external_direct.py` | `981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4` |
| producer | `src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py` | `81a33a4157d6e07b03621bff069c9383914464c16ce4314a9f7a556c7e1cd088` |
| CLI | `scripts/phase6_v3_1_x_external_direct.py` | `072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768` |
| unit test | `tests/unit/test_phase6_v3_external_direct.py` | `056c7273edbdb612d3fc99c4b493f2fe4c96dc15b8ae7aa3a872587f33f3aaba` |
| regression test | `tests/regression/test_phase6_v3_external_direct_publication.py` | `24d26a8a9c2e0ad573b97f76b39db7743f2d6639cd57978be93f0c310062f858` |
| V3.1-X package | `configs/phase6_v3_1_x_external_direct_route_package.json` | `6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752` |
| V3.1-X design | `docs/phase6_v3_1_x_external_direct_route_design.md` | `9a75c6f80cd8360438d395caf887a13b8c88e97faef94139c6ed4dfeba4fdb8d` |
| domain | `configs/phase6_v3_0_domain.json` | `803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b` |
| external anchors | `configs/phase6_v3_0_external_anchor_matrix.json` | `06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485` |
| thresholds | `configs/phase6_v3_0_thresholds.json` | `91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a` |
| convention | `references/notes/phase6_v3_absorption_scattering_conventions.md` | `82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a` |

Protected radial identities:

| Path | SHA-256 |
|---|---|
| `src/schwgw/numerics/radial_solver.py` | `9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9` |
| `src/schwgw/numerics/conditioned_radial.py` | `91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2` |
| `src/schwgw/numerics/scaled_tortoise_radial.py` | `d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df` |
| `src/schwgw/numerics/adaptive_jost_radial.py` | `3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896` |
| `src/schwgw/numerics/matching.py` | `9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340` |
| `src/schwgw/numerics/physical_boundary_radial.py` | `fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f` |
| `src/schwgw/numerics/boundary_conditions.py` | `b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22` |

Consumed failed roots:

| Attempt | Immutable root | Terminal identity |
|---|---|---|
| 0001 | `runs/phase6/classic_scattering/v3_1_x_external_direct_sentinel_v1_20260813T055002Z_py314` | 77 files, 9 dirs, 720336 bytes, all `0444/0555`, nlink1; manifest `d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772`; failure `c002664933d58913b5793ffc1100a5958cb1dfdd12d0c9b3664ffa9ddfb2f541` |
| 0002 | `runs/phase6/classic_scattering/v3_1_x_external_direct_sentinel_v1_20260813T085010Z_py314` | 77 files, 9 dirs, 720339 bytes, all `0444/0555`, nlink1; relative ledger `1aefc643d6bc8b18218a3d26817a3b5e03f66c2b402c4338b607954cb1a36d08`; manifest `6e0d2349d998f76ee8d149e4551bf27222c5d93bf4ec9fb7b790adbc9f506109`; failure `c002664933d58913b5793ffc1100a5958cb1dfdd12d0c9b3664ffa9ddfb2f541` |

Their dispatches are respectively
`5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9`
and
`6be8d88226179ed25d4e50dee06cc17a6f38e61e67617edf9751a88e2cea5112`.

## 13. Recommendation

Freeze this as the repair-cycle-2 design, then require the formal sequence:
package review -> exact five-path zero-science implementation -> T7 delta
`ADVANCE` -> one real source-load micro-sentinel -> T7 micro `ADVANCE` -> one
fresh attempt-0003 full sentinel.  Do not collapse the micro and full stages.
The real micro is the smallest experiment that tests the boundary that both
prior synthetic tests missed, while retaining every scientific contract byte.

If the implementation delta, micro launch or full sentinel fails, stop with
`ESCALATE / T0 ADJUDICATION REQUIRED`.  No third repair cycle exists.
