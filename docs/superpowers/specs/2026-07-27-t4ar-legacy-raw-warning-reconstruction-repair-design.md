# T4ar Legacy Raw-Warning Reconstruction Repair Design

## 1. Purpose

Close the `kM=2.91875` warning-provenance gap without changing the
scientific runner, scientific source, runtime dependency bytes, legacy or
golden artifacts, complete-input meaning, benchmark identity, numerical
criteria, or matrix order.

The repair has two logically separate parts:

1. canonicalize one exact SciPy warning source from the frozen hermetic
   overlay to the already accepted repository-relative warning source; and
2. reconstruct the raw-warning record that the immutable legacy v1 driver
   did not capture, using one separately authorized isolated execution of
   the exact legacy implementation.

Missing legacy evidence is not interpreted as an empty warning record. No
warning is suppressed, ignored, reclassified, or accepted by a broader
pattern.

## 2. Consumed Failure Boundary

The consumed attempt is:

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/
  t4ae_matrix_unit_2p91875_t4aq_053ffd06_20260727T181202p0800/
  unit_2p91875
```

Frozen records:

```text
producer request
  5fa369c5825039ccb83f2df4481210bdbe297bda805724b2136350ba803ecc18
prelaunch setup
  cfcb6479f4fac7fab687735abd21c61cd7f3824c793d0e7904592406105efdae
durable prelaunch
  733e202efb2ea0a35298fa471e8c675d8cb8264cfd69ea10a74f415e8050bf41
running
  943ccc0cbd4bd45077f257344177abd00edd25f64b328d37641fe9656891c4d7
launch receipt
  f223d6c3b55299dc384c5e6783d6a5ce14eefc7567cb76c8db6703e1fb4e38f6
final
  09f909759edb464707102e567758faf1c0f4dcdc5dcbb401ac66bcbe60fd49a6
control audit
  56f990a7dc6ea8f0e4d9e9aa73cd2f60384781af653b021a19f29ebf338b39bd
failure checkpoint
  0d485dcd3be9153a41e4183666f98f703dbd4e38c5ddb7a10f5ea0d7706389db
```

Child PID/SID/PGID `76752` exited naturally `1`, without a signal, after
exact `Popen.wait`; it was reaped and its process group is empty. Stdout is
`215` bytes / `c5e45478...a321`; stderr is `2825` bytes /
`3d2070f9...ae62`. The durable audit is valid. Matching official audit and
all later units were not started. The authorization is consumed and cannot
be retried or reinterpreted.

The failed tree is immutable evidence: `3000` regular files, `364`
directories, `607764003` file bytes, no symlink, and no non-one hardlink.
The canonical output still contains only the two accepted frequency pairs;
all eight later matrix files are absent.

## 3. Exact Diagnosed Defects

### 3.1 Hermetic-overlay source spelling

The unchanged runner already accepts these exact warning tuples:

```text
scipy/integrate/_ivp/rk.py : 547 :
  invalid value encountered in dot
  invalid value encountered in multiply
  overflow encountered in dot
```

The frozen overlay file is:

```text
relative path
  scipy/integrate/_ivp/rk.py
SHA-256
  fa5d6300917f4f949e699b116f59ae147159d5c6147d55d940dc9d3303891056
size
  22800
line 547
  F[3:] = h * np.dot(self.D, K)
```

The runner's `_warning_source()` recognizes `/site-packages/` and `/src/`
prefixes. The content-addressed overlay path contains neither, so the exact
allowed warnings are rejected under their absolute overlay pathname.

After exact overlay-relative normalization, the consumed stderr implies
this diagnostic record:

```text
policy
  strict_location_line_message_allowlist_v1
total_count
  624
entries
  208 x invalid value encountered in dot
  208 x invalid value encountered in multiply
  208 x overflow encountered in dot
canonical diagnostic SHA-256
  e9ce10c6ca59c5d2e1eb281c86859528c095b3b75e848ec58c8997aba7015d97
```

This record is evidence about the consumed optimized attempt. It is not by
itself the missing legacy record and cannot authorize a new matrix run.

### 3.2 Missing legacy observation

The immutable legacy artifacts are:

```text
legacy NPZ
  3bf0abfb7abc090918778012560a967ca91b6ec06bb934d529a7a758133402aa
legacy sidecar
  d5c839cdf2e2a8b0cb1c5b87754a87898684bf0e433ef2bcc1d06f2529bb9788
legacy golden NPZ
  d6b81923284142dfe5faf13e8932b4e5c12aed1cd253c459ab10641ab0949b8b
legacy implementation commit
  8fb8608c187280dc39fd56a78b976e6cf75a6ada
baseline driver
  t4ae_legacy_case_driver_v1
baseline driver SHA-256
  f5ac6a830e1ab8fb052eebb4ca7b7f99f2776d80a1d1a2315d0b383e439d08e7
```

The v1 sidecar has no `raw_runtime_warning_record` key. By contrast, the
v3 sidecars for `3.759375` and `3.89375` contain exact records. The
unchanged runner currently substitutes an empty record whenever the key is
absent. That fallback is useful for genuinely warning-free old cases, but
it cannot establish that `2.91875` emitted no raw warning.

The `2.91875` structured record is non-empty:

```text
radial_warning_codes
  evanescent_tail_suppressed
  q018_tablei_another_bounded_local_transition_oracle_used
radial_warning_count
  296
adapter_use_count
  98
```

Consequently, source normalization alone would merely advance the failure
to the unchanged exact optimized/legacy warning comparison. The missing
field must be reconstructed rather than assumed.

## 4. Frozen Identities And Non-Changes

The repair preserves:

```text
primary HEAD
  45face32f52537ac4b8ab79cb1746d8ac78e9b82
scientific runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768
T4aq driver
  053ffd06d746fa8b49172a170f41f0e653da9b3fcc0f515cc634f9cfb92c6edd
T4aq launcher
  07270d1559626ad60465a7dcc52a91151683f1e26080106d50bb6af3baa637df
complete-290 contract
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24
fixed benchmark identity
  46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48
runtime overlay manifest
  f3ebf3dbf8981500c8d7f714b1740996638f10e32ef17a8377d45ea0b70ab6ca
T4ai witness checkpoint
  2c448a70ed9dc47399c9bb1f148add60315670d4e66c886e5e7895abb5e8cde9
```

No legacy, golden, optimized canonical, source, runner, runtime, input,
threshold, tolerance, mode, point, resolution, `lmax`, or ordering byte
may change.

## 5. Exact Legacy Reconstruction

### 5.1 Geometry

T4 shall freeze one artifact-local reconstruction launcher and one
artifact-local matrix adapter launcher during Phase A. Phase A executes no
solver.

The later reconstruction attempt must use:

- one fresh unique, no-overwrite evidence root;
- one fresh detached local clone at exact commit
  `8fb8608c187280dc39fd56a78b976e6cf75a6ada`;
- the accepted recursive inputs materialized as regular, read-only,
  non-symlink, nlink-1 files under that detached root;
- exact Python `3.14.6`, NumPy `2.4.6`, SciPy `1.17.1`, thread variables,
  and the frozen hermetic overlay;
- isolated `HOME`, `PYTHONDONTWRITEBYTECODE=1`, no user site, no network,
  no install, and no global mutation;
- one isolated output pair and no canonical output path.

The detached commit must have the exact five-path implementation diff. All
five implementation blobs and all selected scientific code hashes must
match the immutable legacy sidecar. Materialized data may not replace or
alter any scientific source path. Existing exact tracked bytes may be
retained; every newly materialized path must be separately bound by
source/target hash, size, realpath, device, inode, nlink, mode, and
non-alias checks.

### 5.2 Computation

The reconstruction launcher shall import the exact legacy module and call
its unchanged `_compute_frequency()` exactly once for existing
`kM=2.91875`, with:

- the sidecar's exact generation and metadata hashes;
- exact source/gate path and hash mappings;
- exact implementation and selected-code identities;
- the legacy `compute_polarization`,
  `compute_flat_no_lens_polarization`, and `solve_radial_mode`;
- unchanged amplitudes, points, boundary conditions, tolerances, adapter,
  and lmax sequence `[192,216,240,264]`.

The launcher may contain control and validation code only. It may not
modify, monkey-patch, wrap, substitute, or filter any scientific solver,
polarization, radial, oracle, NumPy, or SciPy computation.

All Python warnings are captured with `warnings.simplefilter("always")`.
Only one exact source mapping is allowed: the exact frozen overlay file
above maps to `scipy/integrate/_ivp/rk.py` after its root, content, stat,
and manifest record pass. No prefix/glob/regex/basename/argument-controlled
mapping is allowed. Every warning tuple must then pass the unchanged
runner's existing strict allowlist.

### 5.3 Required comparisons

The isolated NPZ contains the exact 22 scientific arrays, excluding only
`metadata_json`. For every array:

- name and order are exact;
- dtype and shape are exact;
- finite/mask contracts pass;
- C-order bytes are bitwise equal to the immutable legacy NPZ;
- C-order bytes are bitwise equal to the immutable golden NPZ.

The reconstruction metadata must also match the immutable legacy sidecar
for structured warning codes/count, adapter count, lmax values, contracts,
source/gate hashes, implementation, selected-code hashes, units, dtypes,
ordering, flags, and scientific array fingerprints. Only execution-local
duration/path/stat/provenance fields are new.

The supplemental witness JSON contains:

- schema/version and exact `2p91875` scope;
- legacy NPZ/sidecar/golden identities;
- detached commit/source/input identities;
- Python/runtime/overlay identities;
- immutable reconstruction launcher identity and argv/cwd/env;
- exact scientific-array comparison;
- exact structured warning comparison;
- the canonical raw-warning record and its digest;
- producer process and stream terminal records;
- explicit statements that legacy/canonical files were read-only and
  unchanged.

NPZ and JSON are published as one isolated same-filesystem atomic pair.

## 6. Durable One-Shot Supervision

The legacy reconstruction is science and therefore requires a separate
root-T0 one-shot authorization after Phase-A audit.

The existing durable driver must supervise it with the same standards as a
matrix producer:

- exact immutable request, prelaunch, running, receipt, streams, final, and
  control audit;
- child PID=SID=PGID, exact wait, natural exit `0`, no signal, empty
  stderr, reaped child, empty process group, and zero wait errors;
- exact runtime/source/input/canonical pre/post equality;
- atomic isolated pair;
- no retry after launch.

Only after producer PASS may the same frozen reconstruction launcher run
one matching `--mode audit`. The audit performs no solver call. It reloads
the isolated pair, legacy and golden artifacts, all manifests, hashes,
array bytes, warning schema, and terminal provenance. Its exit must be `0`
with empty stderr, exact wait/reap, and an empty process group.

Any producer or audit failure consumes the authorization and forbids retry.

## 7. Bound Matrix Adapter

The Phase-A matrix launcher extends the already accepted T4aq launcher. It
must retain:

- original loaded-module verification before the exact two-module stable
  projection;
- exact physical/logical argv separation;
- one unchanged-runner `main()` call;
- all source/runtime/input/fixed-identity/process guards.

It adds only two exact wrappers.

### 7.1 Warning-source wrapper

The wrapper first calls the unchanged runner's original
`_warning_source()`. It changes the result only when the original filename
is the exact frozen overlay `scipy/integrate/_ivp/rk.py`, its manifest
record/content/stat identity passes, and the original result remains the
same absolute path. The replacement is exactly
`scipy/integrate/_ivp/rk.py`.

Every other path and warning remains subject to original behavior.

### 7.2 Legacy-audit wrapper

The wrapper first calls the unchanged runner's original
`_audit_legacy_frequency()`. Therefore the immutable NPZ, sidecar, golden,
embedded metadata, fingerprints, arrays, commit, and comparison must pass
before supplementation.

For every token other than `2p91875`, the exact original result is
returned. For `2p91875` only, supplementation requires:

- the immutable sidecar key is truly absent;
- the original audit produced only its documented fallback empty record;
- one root-T0-bound supplemental witness path and SHA-256;
- exact witness schema, scope, legacy/golden/source/runtime identities;
- bitwise 22-array equality and exact structured warning equality;
- canonical raw-warning record validation through the unchanged runner's
  `_warning_signature()`;
- equality between the witness raw record and the normalized diagnostic
  record independently derived from the consumed optimized stderr.

The wrapper returns a fresh copy of the original audit result with only
`raw_warning_record` replaced. It does not mutate the legacy sidecar,
embedded metadata, NPZ, golden, runner globals, or scientific arrays.

The witness path/hash must be explicit in durable request, prelaunch,
producer, official-audit, final, and replay records. Missing, extra,
mutable, aliased, wrong-token, wrong-hash, wrong-runtime, wrong-array, or
wrong-warning evidence fails closed.

## 8. Phase A: Zero-Science Control Freeze

T4 may change only artifact-local driver/helper/launcher/test files and
fresh durable evidence.

Required solver-free tests include:

- exact overlay path maps to the accepted relative source;
- same basename outside the overlay, wrong overlay root, wrong hash,
  wrong manifest record, symlink, hardlink, writable file, Unicode/case
  alias, prefix, and partial path all reject;
- consumed stderr normalizes to exact diagnostic digest
  `e9ce10c6...15d97`;
- v1 field absence is distinguished from explicit empty/null/malformed;
- original legacy audit runs before supplementation;
- exact synthetic supplemental witness passes only for `2p91875`;
- wrong legacy/sidecar/golden/commit/runtime/input/array/structured-warning/
  raw-warning identity rejects;
- all other frequency tokens return original audits unchanged;
- T4aq 44/46 lazy-module projection remains exact;
- producer/audit/final/replay witness bindings are identical;
- reconstruction launcher calls exact legacy `_compute_frequency` once;
- no scientific callable is reachable in Phase-A tests or preflight;
- no legacy/canonical write path is reachable from either launcher.

After static/AST/dataflow/Ruff/diff checks, the full synthetic preflight,
and one real split-root matrix preflight with a synthetic non-scientific
witness all pass with science counts `0/0/0`, T4 returns:

```text
CHECKPOINT / LEGACY RAW-WARNING RECONSTRUCTION CONTROL FROZEN
```

Root T0 must independently audit Phase A before authorizing reconstruction.

## 9. Phase B And Phase C Gates

After exact Phase-A PASS, root T0 may issue one:

```text
AUTHORIZED / LEGACY 2P91875 RAW-WARNING RECONSTRUCTION WITNESS
```

Only complete producer plus matching audit PASS returns:

```text
CHECKPOINT / LEGACY RAW-WARNING WITNESS PASSED
```

Root T0 then independently audits every array, warning, manifest, stream,
process, runtime, source, input, legacy/golden, canonical, and absence
record. If and only if all pass, root T0 may authorize Phase C:

```text
AUTHORIZED / BIND LEGACY RAW-WARNING WITNESS TO MATRIX ADAPTER
```

Phase C is zero-science. It binds the exact witness path/hash in a fresh
driver checkpoint, reruns all positive/negative tests, and runs one real
split-root matrix preflight through the final launcher. It must audit the
two existing canonical pairs, report `solver_started=false`, preserve
fixed identity `46403a...`, and leave all eight later files absent. Success
returns:

```text
CHECKPOINT / BOUND RAW-WARNING MATRIX ADAPTER FROZEN
```

Only a full root-T0 audit of that checkpoint may authorize a new one-shot
`2.91875` matrix producer and matching official audit.

## 10. Local Self-Remediation And Prohibitions

Within Phase A or Phase C, diagnosed pre-execution zero-science
artifact-local helper/launcher/test/manifest/path/serialization/bookkeeping
defects must be corrected in fresh immutable roots without blind retry.

Any reconstruction producer/audit or matrix producer/audit launch failure
consumes its one-shot and must return to root T0. Local self-remediation
does not apply after a scientific child starts.

Forbidden throughout:

- mutation/reuse/repair of any consumed evidence root;
- mutation or rewriting of legacy, golden, or canonical sidecars/NPZs;
- warning suppression, filtering, count adjustment, relaxed allowlist, or
  reinterpretation of missing evidence as zero;
- runner/scientific source/runtime/complete-input/identity/criteria/order
  changes;
- output copy, promotion, or post-hoc sidecar editing;
- parallel/duplicate execution or alternate matrix order;
- new frequency, production, plot, scientific fixture, Kirchhoff, paper,
  GitHub, global install, network, destructive cleanup, task, subagent,
  proxy, descendant, `max`, or `ultra`.
