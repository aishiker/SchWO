# T4aw Historical-JSON Reference-Surface Repair Design

## 1. Decision Scope

T4av Phase B launched exactly one authorized legacy `kM=2.91875`
reconstruction producer. The scientific child returned naturally with exit
zero and empty stderr, but the durable driver failed during post-child
validation before accepting the pair or launching the matching audit.

This package repairs only the artifact-local JSON reader surface that caused
that failure. It does not change the reconstruction launcher, scientific
source, runtime, complete-input contract, legacy/reference bytes, scientific
criteria, warning criteria, canonical optimized artifacts, matrix order or
one-shot semantics.

T4aw Phase A is zero-science and stops at:

```text
CHECKPOINT / HISTORICAL JSON REFERENCE SURFACE FROZEN
```

## 2. Consumed T4av Phase-B Boundary

The complete immutable evidence root is:

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/
  t4av_phase_b_legacy_warning_witness_v2_e70aab91_20260728T062417p0800/
```

Root T0 independently reconstructed:

```text
files
  823
directories inclusive of root
  117
total file bytes
  531851545
final relative {path,sha256,size} index
  1c1f88da368b0107d441e87b35602d75794584b036147dd96b957bf3a2fe74d1
pre-terminal records
  821
pre-terminal records file SHA
  6a8a956c64d6f696996c837098b2b6935463a8b9decb6e4856a23b92cd13930a
```

Every file is regular, non-symlink, `nlink=1`, mode `0400`; every directory
is mode `0500`; there is no special file, bytecode, mutable child or live
process.

Exact durable identities:

```text
checkpoint
  c8794b03eacf9e0e0482a8a4cac602fa4822c63bb811c594e7b6f663243151e9
setup
  b32368a022df3073241bfa2e864a0e32ee1de95d60b78105b55d0100ec669dc6
producer request
  595df7172910eaa6d091240fe182d9ea9e02901a15b3462bd6f8b9a6bf8eb5c6
source manifest
  f573dd2f0d6e210df9564944663639f1a4904d7ac3ec9c8af39cf6a8523e1782
input manifest
  96cdbb758e5927217a6a895ae864a666701d3f60135906c92929c376a64353ae
reference manifest
  bd8929edf13453ca4468cbd63ac68a8fe20a00c0ca7515c0b0e834286f21ec80
reference index
  418fa14a5a36deda8279e66cadc87cb7d816bedfa12af37c966fc5ea53e0091a
prelaunch / running / receipt
  00de626b232d4b47fb5170c10371a39fd620252a5bd9cdf3a41c2fce57f5defa
  2817eeebcc6fdd723e6193dd382cfe4c30b699f898b6dd0411db6cf4bbed14aa
  48883109f5d531bc621256d2c2af962a0669b7da7ee8a42906ad1422d92447c9
producer stdout / stderr
  1543b1250500dc9e7835129ae19615171d25c2aeb7f0377550f671d3b35aed4a
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
supervisor failure
  78e44bb35bd978cad3587236a52b14d3c339ed6e08a6fe9aba6feaf193f0ba71
```

The child terminal record is exact:

```text
PID / SID / PGID
  2090 / 2090 / 2090
raw return / exit
  0 / 0
signal
  null
wait
  subprocess.Popen.wait / exact / reaped
process group
  empty
wait errors
  0
elapsed ns
  636250283250
```

The producer published an isolated mode-`0400` pair:

```text
NPZ
  a0cf2ac4669d9d7abf9cd9448864c812fb14b1b48f9c135345a10e007bfdecaa
sidecar
  10675ce9e6b50246c9e4d676cb07f785481d4e3f120c6edf71d7cedba889ac46
```

That pair was never accepted by the durable post-child snapshot. It is
permanently non-reusable and may not be audited, promoted, copied into a new
attempt, used as a positive scientific fixture or treated as evidence that
the 23-to-22 projection and `296/98/624` gates passed.

The matching reconstruction audit invocation count is zero. Producer and
solver counts are one. Optimized runner, official audit and matrix counts
are zero. The authorization is consumed.

The separate `audit-failure` attempt returned code `2`, empty stdout and
exact 244-byte stderr because the producer phase now had a non-empty output
pair:

```text
reason
  reconstruction_output_collision
detail
  producer requires no producer binding and an empty pair
stderr SHA
  22f9d6eea11bc8c19ffa53e2fb36671f8b11453c0a0bf9b4dd777e26f2b11011
```

It is retained as durable evidence but is not represented as a successful
failure audit and does not replace the complete raw supervisor-failure
record.

The first T4av Phase-B setup root
`t4av_phase_b_legacy_warning_witness_e70aab91_20260728T062128p0800`
failed before source/input materialization or any child because its
attempt-local lock filename violated the frozen driver contract. It is also
immutable and non-reusable.

## 3. Independently Proven Root Cause

The live driver SHA is:

```text
e70aab9136d99d8791a9d55f10b2559652a0e10d3e4f136adcca795ac9c721b4
```

Its generic `_read_json()` is intentionally a protocol/control-record
reader. It:

1. decodes UTF-8 JSON;
2. requires one object;
3. reserializes with the driver's compact, sorted, explicit
   `ensure_ascii=False` canonical JSON;
4. requires the raw file to equal those bytes plus one newline.

That rule is correct for driver-created request, manifest, durable record
and checkpoint surfaces.

During the reconstruction producer post-child snapshot, the driver calls:

```text
_post_scientific_audit_snapshot()
  -> _reconstruction_pair_snapshot()
  -> _read_json(legacy_sidecar_path)
```

The `legacy_sidecar_path` is not a driver-created control record. It is an
immutable historical scientific-reference sidecar copied byte-for-byte from:

```text
runs/phase5/equivalence_preserving_methods_gate/
  legacy/frequencies/kM_2p91875.npz.json
```

Its source and attempt-local target are exactly:

```text
SHA-256
  d5c839cdf2e2a8b0cb1c5b87754a87898684bf0e433ef2bcc1d06f2529bb9788
size
  57925
source/target bytes equal
  true
source/target inode distinct
  true
target mode / nlink
  0400 / 1
```

Strict UTF-8 JSON parsing returns one object with 40 top-level keys and no
non-finite constant. The raw historical file is pretty-printed. Its compact
semantic canonicalization is 37,178 bytes with SHA:

```text
a91bf5aa687e2dedb18e0136e28b61cce8d4d1620e67786bea57d99abc290be1
```

Therefore raw-byte inequality to the control-record serializer is expected.
It is a serialization-surface mismatch, not reference-content drift and not
a scientific failure.

## 4. Two Non-Interchangeable JSON Surfaces

T4aw must preserve two explicit reader surfaces.

### 4.1 Canonical control JSON

The existing `_read_json()` semantics remain byte-identical and mandatory
for every driver-created protocol/control record:

- requests;
- source/input/reference manifests and indexes;
- prelaunch/running/receipt/final/failure records;
- control and pair audit records;
- checkpoints and preflight records.

No canonical-control caller may be moved to the historical reader. No
formatting tolerance, duplicate-key tolerance or non-finite value may be
introduced on this surface.

### 4.2 Immutable historical reference JSON

Add one dedicated, non-argument-controlled reader used only at the literal
legacy-sidecar call site in `_reconstruction_pair_snapshot()`.

Before parsing, it must require all existing reference-view gates:

- exact derived role/path under the validated reference root;
- exact source and target SHA, size, stat, realpath and inode-disjoint
  binding;
- exact immutable legacy sidecar SHA
  `d5c839cd...9788` and size `57925`;
- target regular, non-symlink, `nlink=1`, exact mode `0400`;
- source/target raw bytes exact and reference index
  `418fa14a...091a` unchanged.

Parsing must:

- decode strict UTF-8;
- reject invalid JSON;
- reject every duplicate object key at every nesting level;
- reject `NaN`, `Infinity` and `-Infinity` through an explicit
  `parse_constant` rejection;
- require the top-level value to be exactly one object;
- return the parsed value without rewriting or publishing any bytes.

It must not:

- require raw bytes to equal any reserialization;
- normalize whitespace, key order, Unicode spelling or number spelling;
- rewrite, replace, chmod, copy back or update the historical source or
  target;
- accept a fallback path, basename search, prefix, glob, regex,
  case-folding, Unicode normalization, environment variable or arbitrary
  argument;
- serve any request/manifest/durable-control or produced-pair JSON.

The parsed historical object remains subject to the existing exact semantic
gate:

```text
raw_runtime_warning_record is absent
```

and all existing exact legacy/reference provenance checks.

## 5. Required Driver Dataflow

The only production dataflow change is:

```text
before
  _reconstruction_pair_snapshot()
    -> _read_json(legacy_sidecar_path)

after
  _reconstruction_pair_snapshot()
    -> _read_immutable_historical_legacy_sidecar(legacy_sidecar_path)
```

All other `_read_json()` call sites remain on the canonical-control surface.
The dedicated reader must either close over the frozen literal identity or
receive an already validated exact role/path while independently rechecking
the fixed identity. It must not expose a boolean, mode, surface name or
arbitrary expected hash that lets callers select weaker parsing.

The existing produced reconstruction witness JSON remains exact compact
canonical no-newline JSON through `_reconstruction_json_file()`. The repair
must not weaken that surface.

## 6. Mandatory Zero-Science Tests

Run exact Python 3.14 tests without invoking launcher `main`,
`_compute_frequency()`, reconstruction producer/audit, optimized runner,
official audit, solver or matrix.

Positive fixtures:

1. the exact immutable historical sidecar bytes parse on the dedicated
   historical surface;
2. the parsed value is one 40-key object and lacks
   `raw_runtime_warning_record`;
3. exact source/target hash/stat/inode/reference-index binding passes;
4. existing canonical request/manifest/durable-record fixtures continue to
   pass the unchanged canonical reader;
5. exact canonical produced reconstruction witness continues to pass the
   unchanged produced-pair reader;
6. a synthetic post-child reconstruction snapshot with a fresh synthetic
   pair reaches the pair-validation surface without science and accepts the
   historical sidecar formatting.

Negative fixtures:

- invalid UTF-8;
- malformed JSON;
- top-level list, scalar or null;
- duplicate key at top level or nested level;
- `NaN`, `Infinity` or `-Infinity`;
- one-byte content drift;
- hash, size, stat, mode, link, inode, path, role or reference-index drift;
- writable, symlinked, hardlinked or source-aliased target;
- basename/prefix/case/Unicode/path-alias substitution;
- historical reader used for request, manifest, durable record or produced
  witness JSON;
- canonical reader weakened to accept pretty-printed/noncanonical control
  JSON;
- control/historical reader cross-use;
- argument-, environment- or fallback-controlled surface selection;
- any mutation or publication attempt against the historical sidecar.

Static AST/dataflow tests must prove:

- exactly one production call site uses the dedicated historical reader;
- that call site is the literal legacy-sidecar check inside
  `_reconstruction_pair_snapshot()`;
- all canonical-control readers retain exact raw-byte canonical equality;
- `_reconstruction_json_file()` remains canonical no-newline;
- no scientific launcher or scientific source changes;
- no producer/audit child is invoked in Phase A.

## 7. Phase-A Durability And Self-Remediation

T4aw Phase A may modify only:

- the artifact-local durable driver;
- solver-free tests/helpers/evidence in fresh unique no-overwrite roots.

Before editing, preserve the exact old driver and complete consumed T4av
roots. Every failed local Phase-A helper/preflight root is immutable.

Diagnosed pre-execution zero-science artifact-local helper, fixture,
manifest, path, serialization, bookkeeping or ordinary-test defect must be
minimally corrected in a fresh root and continued until the exact
checkpoint. There is no fixed correction count and no blind retry.

Any required change to scientific source, reconstruction launcher, runtime,
complete-input meaning, fixed identity, reference content, canonical
artifact, scientific criterion or matrix order must return fail-closed to
root T0.

## 8. Checkpoint And Later One-Shot Boundary

The checkpoint freezes:

- old/final driver hashes and exact diff;
- dedicated historical reader source/AST/dataflow;
- unchanged canonical-control and produced-witness readers;
- every positive/negative/static test and rejection;
- a fresh prospective producer and matching-audit request validation with
  zero child;
- consumed T4av roots, non-reusable pair and full durable identities;
- source/input/reference/runtime/fixed-identity/warning/witness/canonical/
  absence/external/process/transient/link guards;
- all science counts zero.

Only a later separate root-T0 full audit may authorize one completely new
producer and, after full producer PASS, one matching reconstruction audit.
No request, root, reference view, output pair or result from the consumed
attempt may be reused. Any newly launched failure consumes that new
authorization and forbids retry.

## 9. Non-Goals

T4aw does not authorize:

- use, audit, promotion or reinterpretation of the consumed pair;
- a reconstruction producer or matching audit;
- T4ar Phase C or optimized matrix work;
- canonical write or promotion;
- scientific source, launcher, runtime, dependency, complete-input,
  reference-content, fixed-identity or criterion change;
- threshold, tolerance, mode, point, resolution, `lmax`, frequency or order
  change;
- production, plotting, fixture, Kirchhoff, paper or GitHub work;
- task, subagent, proxy or descendant creation;
- model `max` or `ultra`;
- destructive or global environment action.
