# T4av Scientific-Array Projection Repair Design

## 1. Purpose And Exact Consumed Boundary

T4au Phase A froze:

```text
candidate
  3eb0d28b400e2fe069ec77fcd1d55164bb806b96
checkpoint
  3d03736546cfce81f1d3dda8b9a8b7125377645627a04a9ec594c04cf9fd75b8
driver
  b6e8d7657a2ccb07de7ebd0c44f694325a76611b141d88ec3f39512809ad0c15
launcher
  1db81c64a088ce7dc79a2467ff2338534e2fce302999f04fd3c76fad0e077b3d
zero-science preflight
  bf2a8f1f8e4bda322325f0407ee129d494cdd927a573e747032c67161bd038e8
```

Root T0 independently passed that checkpoint and authorized exactly one
fresh legacy `kM=2.91875` reconstruction producer plus, only after complete
producer PASS, one matching zero-solver reconstruction audit.

The producer launched once and returned:

```text
decision
  RED / LEGACY RAW-WARNING WITNESS PRODUCER FAILED
attempt root
  t4au_phase_b_legacy_warning_witness_b6e8d765_20260728T010500p0800
child PID/SID/PGID
  60188 / 60188 / 60188
terminal
  exit64 / no signal / exact Popen.wait / reaped / PG empty
stdout
  0 bytes / e3b0c442...b855
stderr
  170 bytes / c4aaf029...acf0
exact child detail
  scientific array name/order mismatch
```

The one-shot authorization is consumed. The matching reconstruction audit
did not start, no isolated pair exists, and no Phase C or matrix work
started. The attempt root and every failed prelaunch-only root are
immutable, non-reusable and non-promotable.

T4av repairs only a deterministic post-compute validation projection defect
in the artifact-local reconstruction launcher. It does not reinterpret the
consumed RED as a scientific PASS and does not reuse its in-memory result.

## 2. Immutable Failure Evidence

Freeze the exact durable identities:

```text
setup
  cd9e5f94a00a44259a3acecc12e7bbc5a4da485cdb81b89acf66123058747ba0
producer request
  03c7da9efe867797a03946dd56907640b65e0c974e2778b1c7bade1eccfa77ea
source manifest
  dbab33908f1febf77354088c126bf233b2413b9c664182eb6088cc6966bde080
input manifest
  1a6d97d945dbbec3087a4e5a0bfbac5a6f9200afa6e844b4332c9af9aa3a7651
reference manifest
  b34da74e57a4a76a590b450b47cb2ae985f9dbbc9d1b01ef34b5755945219797
reference content index
  418fa14a5a36deda8279e66cadc87cb7d816bedfa12af37c966fc5ea53e0091a
outer prelaunch
  743641cd29b8b481de1dfceee20f5b224deb4259f25debe22bd822adf2623c72
producer prelaunch
  bb01efbcbcadeddd4f7d5d43cd85b4aa9f26cdc578cf2efbf2c4d68c3b2e90d8
running
  8686a6d7d81b6919238f74d1f8f09a48ecbc2ddf751f6c8aed8e5e482c796c4a
launch receipt
  cd8ae560d0ad362512b5cae4f24cc72bd12fef3a8428131bf80c9665ecbeeef5
supervisor failure
  6c115d3b7086a14d0e80a48c8a5e260e23f7f3927e5d979c0b95ede75150520c
failure audit
  44c6b3096bd3c067c112b8172ac8daaf4a43f3fb7c8e280d0767963038f021eb
failure checkpoint
  099c8341a5af0dbb298b6239c6916964903bf55811b5dac7a603557b3d6d5ee9
```

The frozen driver failure audit is `valid=true`. It independently binds
request, argv, roots, launcher, runtime, source, input, reference view,
canonical guards, exact streams, wait/reap and process-group closure.
Runtime/source/input/reference/canonical post-child checks all PASS.

Root T0 independently rehashed the closed attempt tree:

```text
regular files
  820
directories
  117 inclusive
file bytes
  531568940
symlink / special / non-one-nlink file
  0 / 0 / 0
canonical relative {path,sha256,size} index
  2afbf8e66149c857260dce7497137bc66ffc6bbb79db6590d3e5fde56a7bc4c9
```

The supervisor's generic `missing_path` reason records only that no expected
pair existed after child exit. It must not replace the exact child reason.
No root, lock, manifest, reference view, input copy, process record or
primary artifact from this attempt may be changed, deleted, unlocked,
renamed, repaired, populated or reused.

## 3. Exact Causal Proof

The consumed launcher's `scientific_arrays(path)` loads an NPZ and returns:

```python
order = [name for name in loaded.files if name != "metadata_json"]
arrays = {name: np.asarray(loaded[name]) for name in order}
```

Direct read-only loading independently proves both immutable legacy and
golden NPZs have the same exact 23-entry full order:

```text
kM
point_ids
point_group
point_x
point_y
point_z
point_r
point_theta
point_phi
lmax_values
F_plus_history
F_cross_history
F_plus_complex
F_cross_complex
abs_F_plus
abs_F_cross
arg_F_plus_principal
arg_F_cross_principal
valid_ratio_plus_mask
valid_ratio_cross_mask
final_pair_delta_plus
final_pair_delta_cross
metadata_json
```

Therefore `scientific_arrays()` returns the first exact 22 names.

The unchanged exact-legacy `_compute_frequency()` constructs the same 22
scientific arrays in that order, validates them, then always executes:

```python
arrays["metadata_json"] = np.asarray(
    json.dumps(_json_safe(metadata), sort_keys=True)
)
return arrays, metadata
```

Thus every successful return from the one unchanged scientific call has the
exact 23-key full mapping above.

The consumed launcher next calls:

```python
exact_array_comparison(arrays, legacy_npz, legacy_golden)
```

Its current gate requires simultaneously:

```python
legacy_order == golden_order
list(computed) == legacy_order
len(legacy_order) == 22
```

For the producer, `list(computed)` has 23 entries while `legacy_order` has
22. The predicate is deterministically false regardless of scientific
array values. The exact observed child stderr is therefore fully explained
by this reachable post-compute comparison. Output temporary-file creation
occurs later, so no pair was written.

This proof establishes the exact control defect. It does not establish the
unpersisted array values, warning record or scientific equality. Those
claims require a new separately authorized full producer.

## 4. Frozen Scientific And Provenance Boundary

Preserve exactly:

```text
primary HEAD
  45face32f52537ac4b8ab79cb1746d8ac78e9b82
legacy scientific commit
  8fb8608c187280dc39fd56a78b976e6cf75a6ada
optimized runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768
complete-290 contract
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24
runtime manifest
  f3ebf3dbf8981500c8d7f714b1740996638f10e32ef17a8377d45ea0b70ab6ca
runtime content
  1803e0f763cac682442b22af8986b240e5830a1a42849c77ae2c7aa96fc39371
fixed benchmark identity
  46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48
relocated witness
  2c448a70ed9dc47399c9bb1f148add60315670d4e66c886e5e7895abb5e8cde9
legacy NPZ / sidecar / golden
  3bf0abfb7abc090918778012560a967ca91b6ec06bb934d529a7a758133402aa
  d5c839cdf2e2a8b0cb1c5b87754a87898684bf0e433ef2bcc1d06f2529bb9788
  d6b81923284142dfe5faf13e8932b4e5c12aed1cd253c459ab10641ab0949b8b
raw warning
  624 / e9ce10c6ca59c5d2e1eb281c86859528c095b3b75e848ec58c8997aba7015d97
structured warning
  296 / adapter use 98
```

The single `_compute_frequency(2.91875, ...)` call, all arguments and
callables, warning capture, 22 scientific arrays, exact dtype/shape/order/
C-byte equality, finite-mask requirements, warning counts, mode0400 atomic
pair lifecycle and matching audit remain unchanged.

No scientific source, optimized runner, dependency, runtime, complete-input
meaning, reference content, fixed identity, canonical artifact, threshold,
tolerance, mode, point, resolution, `lmax`, frequency or matrix order
changes.

## 5. Exact Two-Surface Projection Contract

Publish a new artifact-local reconstruction launcher derived from
`1db81c64...77b3d`. Leave that consumed launcher immutable.

The new comparison code must distinguish two explicit non-interchangeable
surfaces:

1. `producer_full_mapping`: the direct result of `_compute_frequency()`;
2. `audit_scientific_mapping`: the result of loading the published NPZ
   through the scientific-only loader.

### 5.1 Producer full mapping

The producer surface must require:

- exact full key order is the frozen 22-name scientific order followed by
  exactly one final `metadata_json`;
- no missing, extra, duplicate, reordered, aliased, case-folded or
  Unicode-normalized name;
- `metadata_json` is a scalar NumPy Unicode string and parses as one JSON
  object;
- removing only that exact final metadata entry yields the exact 22-name
  scientific projection;
- only those 22 arrays enter bitwise legacy/golden comparison.

The metadata payload is not a scientific array and is not bitwise compared
to legacy/golden metadata because runtime duration and provenance are
attempt-specific. It remains in the produced NPZ exactly as returned by the
unchanged `_compute_frequency()`.

### 5.2 Audit scientific mapping

The audit surface must require:

- exact key order is the frozen 22-name scientific order;
- `metadata_json` is absent because the loader intentionally filtered it;
- no missing, extra, duplicate, reordered or aliased name;
- all 22 arrays are compared bitwise against both legacy and golden.

### 5.3 Common comparison

The two surfaces may share one pure projection helper only if the caller
passes a frozen literal surface name and the helper rejects every other
value. The producer call site must use the producer literal and the audit
call site the audit literal. Boolean, environment-controlled,
argument-controlled, heuristic, prefix, glob, regex, set-only, sorted-key
or fallback selection is forbidden.

The final comparison record remains exactly:

```text
array_count = 22
bitwise_equal_golden = true
bitwise_equal_legacy = true
dtype_shape_order_exact = true
finite_mask_contract = true
```

No metadata content may substitute for or weaken any of those 22-array
checks.

## 6. Driver Binding And Phase-A Scope

T4av Phase A may modify only:

- a new launcher published in a fresh unique evidence root;
- the artifact-local durable driver so all reconstruction commands,
  request/prelaunch/running/final/control/pair/audit/replay identities bind
  that exact launcher and its projection contract;
- solver-free tests and evidence.

The consumed T4au launcher and driver snapshots remain immutable.
Every existing source/input/reference/runtime/process/canonical/external
guard remains mandatory.

Phase A must run exact Python 3.14 and science counts must remain zero:

```text
launcher main
  0
_compute_frequency
  0
reconstruction producer
  0
reconstruction audit
  0
optimized runner
  0
official audit
  0
solver
  0
matrix
  0
```

## 7. Mandatory Zero-Science Tests

Before checkpoint, run positive fixtures using only in-memory/read-only
legacy/golden arrays:

- exact 23-entry producer full mapping passes;
- exact 22-entry audit scientific mapping passes;
- all 22 arrays remain dtype/shape/C-byte exact;
- scalar Unicode `metadata_json` parses as a JSON object;
- producer and audit return the same exact scientific comparison record.

Run negative fixtures for:

- producer metadata missing, duplicated by sequence input, non-final,
  renamed, wrong case, wrong Unicode spelling, non-scalar, non-Unicode or
  malformed JSON;
- audit mapping containing metadata;
- one missing, extra, duplicated or reordered scientific name;
- sorting or set-only logic that would hide order drift;
- one dtype, shape, C-byte or finite-mask drift;
- producer call using audit surface and audit call using producer surface;
- environment/argv-controlled surface;
- launcher path/hash, driver path/hash, source/input/reference/runtime/
  fixed-identity/canonical/external/process drift.

Static AST/dataflow tests must prove:

- one unchanged `_compute_frequency()` call;
- producer full result flows to the producer surface;
- audit loader result flows to the audit surface;
- metadata is excluded only by exact-name/final-position contract;
- the 22 scientific comparisons are unchanged;
- output permission and atomic publication logic is unchanged.

## 8. Checkpoint And Later One-Shot Boundary

Only complete Phase-A PASS returns:

```text
CHECKPOINT / SCIENTIFIC ARRAY PROJECTION CONTRACT FROZEN
```

The checkpoint freezes old/new launcher and driver hashes/diffs, exact
projection functions/call sites, all tests/rejections, prospective fresh
producer/audit requests, consumed RED evidence, runtime/source/input/
reference/legacy/golden/warning/canonical/absence/process/transient/external
guards and all science counts zero.

Only a separate root-T0 audit and authorization may launch one new producer
and, after its full PASS, one matching audit. A launched failure consumes
that authorization and forbids retry. No prior in-memory result, request,
root, reference view, pair or process evidence may be reused.

Standing self-remediation applies only before any scientific child and only
to diagnosed artifact-local helper/fixture/manifest/path/serialization/
bookkeeping/ordinary-test defects in fresh immutable roots. It never permits
scientific child retry or scientific/provenance boundary changes.

## 9. Non-Goals

T4av does not authorize:

- T4ar Phase C;
- optimized matrix execution or official matrix audit;
- canonical write or promotion;
- new frequency or alternate order;
- scientific source, runner, runtime, dependency, input or reference change;
- threshold, tolerance, mode, point, resolution or `lmax` change;
- production, plotting, fixtures, Kirchhoff, paper or GitHub work;
- task, subagent, proxy or descendant creation;
- model `max` or `ultra`;
- destructive or global environment action.
