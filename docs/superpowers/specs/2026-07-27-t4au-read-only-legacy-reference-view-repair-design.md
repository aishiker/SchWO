# T4au Read-Only Legacy Reference-View Repair Design

## 1. Purpose And Exact Failure Boundary

T4at Phase A froze the split-root reconstruction control path:

```text
driver
  efe256d2a0a3493ac321e32b7d69dc607e690a47e28c894b3d089305862e01bd
checkpoint
  d9f9bd5247f4323b7a441557476f9ec691db62fd75932a4c5222a80e754ff2c9
reconstruction launcher
  20bd7e78837b5b78a2258a1cec19baa7fbaff07c500d9c27ce278d099b3b79c6
```

Root T0 independently passed that checkpoint and authorized exactly one
fresh legacy `2.91875` raw-warning reconstruction producer plus, only after
producer PASS, one matching zero-solver reconstruction audit.

The producer was launched once and returned:

```text
decision
  RED / LEGACY RAW-WARNING WITNESS PRODUCER FAILED
attempt root
  t4at_phase_b_legacy_warning_witness_efe256d2_20260727T233000p0800
child PID/SID/PGID
  50124 / 50124 / 50124
terminal
  exit64 / no signal / exact Popen.wait / reaped / PG empty
stdout
  0 bytes / e3b0c442...b855
stderr
  294 bytes / 82f5123f...b5497
exact child detail
  path is writable: .../legacy/frequencies/kM_2p91875.npz.json
```

The authorization is consumed. No matching reconstruction audit, optimized
runner, official audit, solver or matrix unit was started, and no isolated
pair exists.

This is a pre-computation control-provenance failure, not a scientific
result. The launcher intentionally requires JSON inputs to be regular,
non-symlink, nlink-1, non-aliased and read-only. The driver bound the primary
legacy artifacts directly. Their hashes and contents are exact, but the
legacy NPZ, legacy sidecar and golden NPZ are all mode `0644`.
`validate_static_identity()` reaches `load_json(LEGACY_SIDECAR)` before the
sole `_compute_frequency()` call and rejects the writable sidecar.

T4au preserves that read-only gate. It does not chmod, replace or reinterpret
the primary artifacts. It creates a fresh immutable byte-exact read-only
reference view and minimally routes the artifact-local driver and a new
frozen reconstruction launcher through that view.

## 2. Immutable Consumed Failure Evidence

Freeze the exact durable chain:

```text
setup manifest
  b015909deb573e974226426f5bc36b7b04ff4812389289fd0c94192c7644302e
producer request
  df442c6c8b57752094d9d50163f8fdb6bb581a2b5d605a9b16aaeb8c1c8f4d5d
source manifest
  fb149e72882bae0cf8463d6e57229eda94b12a71a7619345c3c2daffec69f23f
input manifest
  ac5c5edcc5c0f070e7625e433e3abd98560d1c5861be404ce31c14e4bc0fd776
producer prelaunch
  5b9d3ee8aa2301046a8601e5f73c41cdc1498c5171dc9ac7403a0cda825af52c
running
  e9ed4661263c5dd6fba0f9bbdb14fa2d9184a2fc163ede1999314dba3fdfda9c
launch receipt
  d55d3a274624862ff0653a628ec7e63bc557de61c520b61dcbaa9e58aa0e256a
supervisor failure
  8e93b6d03aa9ccb9cc123e50481719fed7a6d5107a56b4bbfb6d3a9463774760
failure audit
  4c0f581807e9f2d9d48be46910a58af6649305c5c216e57cf8444e67e7a981b8
failure audit capture
  e8de9828a6922eac241901d1bdbbdd49de636cd8a7004cfe3f46c14ed6f23a08
terminal checkpoint
  93dbc73c3e3dc315e2aab9efceb8630d2ca24cb9222b14ab64a4a2a4b5455f4e
```

The failure audit is `valid=true`. Runtime pre/post, source/input bindings,
canonical guards, streams, exact wait/reap and process-group closure all
PASS. The supervisor's generic durable failure reason is `missing_path`
because the expected pair was absent after child exit. That generic
supervisor label must not replace the child stderr's exact launcher reason.

The closed tree has:

```text
787 regular nlink-1 files
96 directories inclusive
529261027 file bytes
0 symlink / 0 special / 0 non-one-nlink file
root-T0 canonical relative content index
  87fd6cceb3b03f0fbbd0199f0aff541a17ca1930cbfbd9b015a24305a00c667e
T4 reported boundary ledger
  488bd3966dcf0d5945aef2a085c32bc79b071716a4d78509835d31c8610b77c7
```

The three earlier T4at prelaunch-only setup roots are also immutable. They
contain no producer child and did not consume the scientific authorization.
Neither they nor the consumed producer root may be repaired, chmodded,
renamed, deleted, populated, reused or promoted.

## 3. Frozen Scientific, Runtime And Input Boundary

Preserve exactly:

```text
primary HEAD
  45face32f52537ac4b8ab79cb1746d8ac78e9b82
legacy scientific commit
  8fb8608c187280dc39fd56a78b976e6cf75a6ada
old launcher
  20bd7e78837b5b78a2258a1cec19baa7fbaff07c500d9c27ce278d099b3b79c6
optimized runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768
complete-290 contract
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24
runtime manifest
  f3ebf3dbf8981500c8d7f714b1740996638f10e32ef17a8377d45ea0b70ab6ca
runtime content index
  1803e0f763cac682442b22af8986b240e5830a1a42849c77ae2c7aa96fc39371
relocated witness
  2c448a70ed9dc47399c9bb1f148add60315670d4e66c886e5e7895abb5e8cde9
fixed optimized benchmark identity
  46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48
legacy NPZ
  3bf0abfb7abc090918778012560a967ca91b6ec06bb934d529a7a758133402aa
legacy sidecar
  d5c839cdf2e2a8b0cb1c5b87754a87898684bf0e433ef2bcc1d06f2529bb9788
legacy golden
  d6b81923284142dfe5faf13e8932b4e5c12aed1cd253c459ab10641ab0949b8b
raw warning
  624 / e9ce10c6ca59c5d2e1eb281c86859528c095b3b75e848ec58c8997aba7015d97
structured warning
  296 / adapter use 98
```

The old launcher remains immutable. T4au publishes a new launcher in the
fresh Phase-A evidence root; it does not edit the old closed T4ar launcher.
The new launcher's scientific body must preserve byte-equivalent behavior:

- the same exact legacy commit and module origins;
- one unchanged `_compute_frequency(2.91875, ...)` call with the same
  arguments and callables;
- the same `warnings.simplefilter("always")` capture and exact warning
  allowlist;
- the same 22-array names/order/dtypes/shapes/C-order bytes comparison;
- the same structured warning `296/98` requirements;
- the same atomic isolated pair and matching audit semantics.

Static inspection also proves a second reachable permission closure in the
same launcher: `run()` creates the NPZ temporary with ordinary `xb`, which
would normally retain mode `0644`, while `audit()` calls the unchanged
read-only `regular_file()` on the final NPZ. A successful producer would
therefore make a later matching audit fail before loading the pair. T4au
must close this artifact-local lifecycle without changing bytes: create both
temporary pair files exclusively, fsync them, set both to exact mode `0400`,
reopen/reload their identities, then atomically replace and parent-fsync.
The final NPZ and JSON must both be regular, non-symlink, nlink-1 and
read-only before producer PASS. This is not a warning/array/science change.

No scientific source, runner, dependency, complete-input meaning, warning
rule, array criterion, threshold, tolerance, frequency, point, mode,
resolution, `lmax`, legacy/golden/canonical artifact or matrix order changes.

## 4. Fresh Read-Only Reference View

Every prospective or later authorized attempt creates one fresh direct child
of its attempt root:

```text
legacy_reference_root/
  legacy/frequencies/kM_2p91875.npz
  legacy/frequencies/kM_2p91875.npz.json
  golden/frequencies/kM_2p91875.npz
```

The source origins remain the three exact primary paths. Their frozen
hash/size pairs are:

```text
legacy NPZ
  3bf0abfb...02aa / 167094
legacy sidecar
  d5c839cd...9788 / 57925
golden NPZ
  d6b81923...9b8b / 117970
```

Before copying, bind each source's full `lstat` identity, realpath, hash and
size. Each target is created by no-follow exclusive create, streamed from
its one source, fsynced, closed, chmodded to `0400`, parent-fsynced, reopened
and fully rehashed. Require:

- exact fixed relative path and exactly three final files;
- regular, non-symlink, nlink-1 target;
- mode exactly `0400`, no writable bit;
- target bytes/hash/size equal its one frozen source;
- three distinct target `(device,inode)` pairs;
- every target inode distinct from all three source inodes and from every
  complete-input/source/output/launcher/driver inode;
- reference root distinct, non-aliased and non-overlapping with clean
  source, complete input, output, HOME, producer/audit run roots, runtime
  overlay, primary legacy/golden, canonical and every old attempt;
- no cache, bytecode, lock, tmp, partial, quarantine, extra file or special
  entry.

After publication, close the reference root read-only and never mutate it.
The three primary source records must remain byte/stat/inode exact before
and after materialization, Phase-A probes, producer and matching audit.

### 4.1 Reference manifest and canonical index

Publish a manifest outside the reference root. It binds:

- the reference-root full directory identity;
- all three primary source full records;
- all three target full records;
- fixed source-to-target mapping;
- exact source/target inode non-alias proofs;
- exact final directory and file set;
- a three-field target content index.

The target index payload is a list in ordinary Python Unicode code-point
order by `relative_path`, each record containing exactly
`relative_path,sha256,size`. Serialize it using the driver's dedicated
canonical function:

```python
json.dumps(
    value,
    allow_nan=False,
    ensure_ascii=False,
    separators=(",", ":"),
    sort_keys=True,
).encode("utf-8")
```

with no newline before SHA-256. The manifest file itself uses the same
canonical bytes and no newline. The reconstruction launcher keeps its
separate existing default-`ensure_ascii=True` stdout serializer. These two
surfaces are not interchangeable.

## 5. New Artifact-Local Launcher Contract

Publish a new frozen launcher derived from old launcher
`20bd7e78...79c6`. Its only behavioral input change is one required CLI
argument:

```text
--legacy-reference-root <absolute fresh reference root>
```

The launcher derives the exact three fixed relative paths itself. It must
not accept individual arbitrary artifact paths, environment-controlled
fallbacks, primary-path fallback, basename search, glob, prefix, regex,
case-fold, Unicode alias, symlink, import hook, `sitecustomize`, stdin or
`-c` routing.

Thread the derived three `Path` objects explicitly through
`validate_static_identity`, `compute_once`, `exact_array_comparison`,
`run` and `audit`. All legacy sidecar loads and legacy/golden NPZ loads must
flow only from these objects. Preserve `regular_file(..., read_only=True)`
unchanged and call it for all three reference objects before scientific
execution or audit.

Preserve the existing atomic output filenames and bytes, but make the
producer's NPZ and JSON permission lifecycle satisfy the same unchanged
read-only audit gate. Both final files must be exact mode0400 before the
producer reports success; partial/failure cleanup remains fail-closed and no
canonical promotion is added.

Static AST/dataflow tests must prove:

- no primary absolute legacy/golden path is reachable for payload reads;
- no module-level mutable path substitution;
- the one `_compute_frequency()` call and all its arguments are unchanged;
- run and audit both validate the same reference-view schema;
- launcher self-hash and exact logical/physical argv remain bound;
- return/SystemExit propagation and one-main-call behavior remain exact.

## 6. Durable Driver Contract

Change only the artifact-local durable driver and Phase-A evidence/tests.
Keep all old phase values and the two T4as reconstruction phases unchanged.

For reconstruction requests:

1. Add the reference root and immutable reference manifest as required
   request fields.
2. Add `--legacy-reference-root` to the exact reconstruction argv.
3. Replace direct primary payload reads in reconstruction scientific
   comparison/audit helpers with the validated target paths.
4. Retain the primary three records separately as immutable source origins;
   never treat targets as replacements for historical identity.
5. Bind target root/files in request, prelaunch, running, receipt,
   terminal/failure, control audit, pair audit and checkpoint.
6. Require clean source, complete input, reference view, output, HOME,
   producer run and audit run as pairwise-distinct direct children of the
   fresh attempt and reject any overlap or inode alias.
7. Require producer and matching audit to use the exact same reference
   root, manifest, file identities, launcher, roots, runtime and pair.
8. Recheck both primary source records and target view records before and
   after each child.
9. Require producer terminal evidence to bind final pair mode0400 and
   matching audit to observe those exact same file identities.

The driver must not chmod or write any primary source. It may create only
fresh attempt-local targets and evidence. A post-launch failure still
consumes the one-shot and cannot self-remediate or retry.

## 7. Phase-A Zero-Science Test Contract

Under exact CPython 3.14 and the frozen runtime, exercise:

- one exact positive three-file reference view;
- one prospective producer request and one matching-audit request;
- launcher source/AST/dataflow and exact single scientific call;
- primary-source pre/post identity equality;
- exact target path/order/index/manifest derivation;
- missing/extra/duplicate/wrong-relative-path target;
- writable target or writable directory after closure;
- symlink, hardlink, shared inode, source-target alias and cross-target alias;
- wrong hash, size, mode, source mapping, source drift or post-copy drift;
- root equality/containment/overlap/realpath/case/Unicode alias;
- manifest schema/index/serialization/newline/order drift;
- launcher path/hash/argv/reference-root drift;
- producer/audit reference mismatch;
- writable producer NPZ or JSON, pre-chmod publication, post-chmod drift,
  pair alias/link, or audit-visible pair identity mismatch;
- reference root under source/input/output/HOME/run/runtime/canonical/old
  roots;
- attempted primary chmod/write/replacement;
- unchanged T4at split-root and all older phase behavior.

Use import/named-load and pure-function fixtures only. Phase A must not call
launcher `main`, `_compute_frequency()`, optimized runner, official audit or
solver. Diagnosed pre-execution artifact-local fixture/helper/manifest/path/
serialization/bookkeeping/ordinary-test defects must be preserved in fresh
immutable roots and minimally corrected until checkpoint; blind retry is
forbidden.

## 8. Phase-A Checkpoint

Freeze:

- old/final driver SHA and exact diff;
- old launcher unchanged and new launcher SHA/diff;
- reference source/target manifest and target index;
- all positive/negative/static/dataflow test results;
- prospective producer and matching-audit request bindings;
- zero-science pure-function proof that producer pair publication closes
  both files mode0400 before success and audit requires the same identities;
- exact primary pre/post records;
- runtime/source/input/canonical/absence/process/transient/external guards;
- science invocation counts all zero.

Only complete PASS returns:

```text
CHECKPOINT / READ-ONLY LEGACY REFERENCE VIEW FROZEN
```

and stops for root-T0 independent audit.

## 9. Later One-Shot And Downstream Gates

Only root-T0 Phase-A PASS may authorize a new reconstruction producer plus,
only after producer durable/scientific PASS, one matching zero-solver audit.
The consumed PID-50124 attempt and every earlier pair/root are non-reusable.

Any launched producer or audit failure consumes that new authorization and
forbids retry. A successful pair remains isolated. Root T0 must audit it
before separately authorizing the already reviewed T4ar Phase C. Only
Phase-C PASS and root audit may authorize the next original matrix item
`2.91875`.

No old-root mutation, primary chmod, read-only relaxation, scientific
change, canonical write, pair promotion, matrix execution, new frequency,
production, plot, fixture, Kirchhoff, paper, GitHub, T7ch or downstream work
is authorized by this package.
