# T4ai Relocated Benchmark-Identity Binding Repair Design

## 1. Purpose

T4ai repairs one bounded control-provenance defect exposed by the consumed
T4ah complete-input witness:

- the scientific producer ran once in a clean detached exact-`45face32`
  project with the frozen hermetic runtime and complete 290-input contract;
- the producer exited `0`, emitted empty stderr, was exactly waited and
  reaped, left an empty process group, and atomically published an isolated
  NPZ/JSON pair;
- every one of the 22 scientific arrays is bitwise identical to canonical,
  legacy, and golden references;
- the matching official audit did not start because the durable driver
  required the primary-workspace benchmark identity
  `46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48`,
  while the detached runner correctly emitted
  `db7937fad5e95123f079c9a54142ddd22b4025b70fd8ee2fef86d7f8a1a269b8`.

The mismatch is not scientific drift. The frozen runner's `_gate_identity()`
includes absolute `path` strings for five frozen gate files in the hashed
gate manifest. Relocating byte-identical files below the detached project
therefore changes the gate manifest, the derived `gate_sha256`, and the
final benchmark identity.

T4ai must bind the exact path-relocated identity before launch without
accepting arbitrary identities and without editing the scientific runner,
implementation, runtime, inputs, configs, thresholds, canonical data, or
scientific semantics.

## 2. Immutable T4ah HOLD Evidence

The consumed witness root is immutable:

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/
    witness_kM_1p58125_complete_input_20260727T001212p0800
```

Exact records:

```text
preparation helper
  369ad2ae7c6bd6af8cacf6de37fde819ea1956905dcea8043684d18c6291a1c2

prelaunch setup
  99d71f6759d1bf97c0de6fb387f8435f3446958b11c7a4805dffffc72b8c2fb3

producer request
  e513e75fb250438c9f0c0660b4192b314e1bb23e50d082533a639b42fa246873

producer final
  247790537ff120c7dbabe7a80016a5f3db26d969639af9cedeb5a1e152e8a8da

producer stdout
  0b689aea1bd9b3f3cfff95e8140ba2b9a5f22e82903207247babad9ef2492a88

producer stderr
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

durable control audit
  b20e481dbd070ea63e9999f43f90e0df99dde2d6e9b756a5a0d77706467d800c

independent pair audit
  854df348a67bd32e377420e7239dbcacfefb94281eecd1f91b025f2fb98b1792

official-audit start-gate failure
  ab3741aba87b30be2272c5dde0a793c1e4a838ec0652ecbe31e3dcf11d44c35f
```

The producer supervisor PID was `62272`; the scientific child
PID/SID/PGID was `62285`. The child exited `0` with no signal and was
exactly waited and reaped. Its process group is empty. The matching official
audit request, prelaunch record, and run directory are absent, and the
official-audit scientific invocation count is zero.

The isolated pair is immutable:

```text
NPZ
  c2134d4fe41701fa0f22f39db4a317518b4b4126a540dac0c8fdd19cb0154cf2

JSON
  2e0b659c779feb2183cf662aa17169277e0664d7fafb430e9ff711caed1944c9

terminal stdout record
  8a6c7e8eef25bf85ce096714392fdf4ba314e4ea9ed9b1115a2e1b2e6896d5ca
```

This pair is evidence of a scientifically successful producer only. It is
not a completed witness because no matching official audit ran. It must not
be reused, promoted into performance/cache/downstream evidence, or audited
under a changed driver. The T4ah one-shot authorization is consumed.

## 3. Frozen Identities And Guards

T4ai inherits:

```text
primary implementation
  45face32f52537ac4b8ab79cb1746d8ac78e9b82

T4ah package candidate
  7d84746a96184a250acddb044502d2506263b9b9

scientific runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768

T4ah driver
  057bb24beeb0ea90c6a2524b8ca43df05b611ffe252a1f0b631fab149d1259a9

T4ah Phase-A manifest
  0b2b37c0dbd55810b6f3020d0dd69b4c7026d85134c4c9ef065b06a239b3a577

complete input contract
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24

T4ah runtime environment
  811d3840e858c1ad0a92c665e54dbf99662d884575871ade6ab45c6b40c4db30
```

The hermetic overlay, exact Python 3.14 binary, complete 290 inputs, exact
fourteen implementation paths, canonical four files, old evidence, and
external zero-byte object remain frozen.

Canonical hashes remain:

```text
e95d28f4b3d0f35a770430ec074dc47f24b93dc7a2e1785e9646ff4581955f91
3a24f316c9c78c72d382fd68c3409f8833fd10c073e942a56d7e8509c4f595d6
36ff7902d86762ad3f93bf1b386275cc7b5ca89c50c4f8b448a99592089e5bd9
d60277384e6edb1d2192d8a6e0a111cfd21a9be20ddbf976f05d7ec30a712c28
```

Only those two canonical frequency pairs may exist. The three later
frequency pairs and full-image pair remain absent.

## 4. Exact Root Cause

The runner computes:

```python
gate_manifest_sha256 = canonical_sha256(gate_records)
gate_sha256 = canonical_sha256(
    {
        "frozen_gate_manifest_sha256": gate_manifest_sha256,
        "tablei_input_manifest_sha256": tablei_input_manifest_sha256,
    }
)
benchmark_identity_sha256 = canonical_sha256(
    {
        "implementation_sha256": ...,
        "physics_sha256": ...,
        "solver_sha256": ...,
        "config_sha256": ...,
        "source_sha256": ...,
        "gate_sha256": gate_sha256,
        "environment_sha256": ...,
    }
)
```

`gate_records` is keyed by exactly:

```text
design
plan
t4ae_prompt
t7cg_prompt
t7ch_prompt
```

Each value contains exactly:

```text
path
sha256
size
```

The five SHA-256 values and sizes are identical between the primary and
detached projects. Only `path` changes from the primary absolute root to the
detached absolute root.

Primary values:

```text
gate manifest
  101823bb86227192bdeb120dff36dd84b979e45f6e237cfda2c385e021084eb4

table-I manifest
  6c20e1d54ee09d5e5207361348161c69cbc7c3ca2f5b811acbb20f71840d4010

gate identity component
  e1fb15b91d8cbd59a1f4e4a1d71ee59122361870da3ed52a605cf0e16dcd4626

benchmark identity
  46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48
```

Consumed detached-witness values:

```text
gate manifest
  b0c9b5210c1a08cb0629f7796e18d6085400096ead1912408cc7715fe1fc8a09

table-I manifest
  6c20e1d54ee09d5e5207361348161c69cbc7c3ca2f5b811acbb20f71840d4010

gate identity component
  be6375212b8bb9b9baafef498dcf6adadd1122bbac2103a6ac27bbe6b6c43f25

benchmark identity
  db7937fad5e95123f079c9a54142ddd22b4025b70fd8ee2fef86d7f8a1a269b8
```

All other seven-field benchmark-identity components are equal. The
configuration's absolute `path` and the runner's absolute `path` also
relocate in the emitted provenance payload, but the benchmark digest uses
the config SHA-256 and runner self SHA-256, not those path strings.

## 5. Closed Relocation-Binding Contract

The driver must retain the fixed primary/canonical benchmark identity and
add a phase-specific detached-witness identity binding. It must never
replace exact equality with a set-membership or arbitrary-observed-value
acceptance.

### 5.1 Canonical serialization

Every derived digest uses the frozen runner's exact canonicalization:

```python
json.dumps(
    _json_safe(value),
    allow_nan=False,
    separators=(",", ":"),
    sort_keys=True,
).encode("utf-8")
```

The `ensure_ascii` argument is intentionally omitted, exactly as in the
runner, so the Python default `ensure_ascii=True` is mandatory.  Non-ASCII
code points are therefore serialized as JSON `\uXXXX` escape sequences
(including surrogate pairs when applicable) before the resulting ASCII
bytes are encoded as UTF-8.  The driver must reuse the runner-equivalent
`_json_safe` behavior for the supported payload values: recursively sorted
string-key mappings, lists/tuples converted recursively to lists, `Path`
converted to `str`, NumPy scalars converted with `.item()`, and complex
values converted to `{"real": float, "imag": float}`.  Unsupported values,
non-string mapping keys, non-finite floats, or any serialization error fail
closed.  There is no trailing newline; SHA-256 is taken over exactly these
bytes.

The Phase-A fixture set must include a detached root containing non-ASCII
path components (for example `/tmp/含中文/项目`).  A positive fixture must
show byte-for-byte and digest equality between the frozen runner
canonicalization and the driver derivation.  A paired negative regression
must show that an otherwise identical `ensure_ascii=False` derivation
produces different bytes/digest and is rejected.  An implementation may
not restrict detached roots to ASCII merely to avoid this test.

### 5.2 Prelaunch derivation

Before a detached witness request is published, the driver must:

1. bind one exact detached project root by lstat, realpath, device/inode,
   no-symlink/no-alias, and containment checks;
2. bind the five exact gate repository-relative paths, SHA-256 values, and
   sizes;
3. construct each runner gate `path` as the exact absolute resolved path
   below that bound detached root;
4. require each path to be regular, read-only, non-symlink, `nlink=1`,
   content-identical, and inside the detached project;
5. reconstruct the gate manifest, gate identity component, seven-field
   benchmark-identity payload, and final digest using section 5.1;
6. prove that the reconstructed payload differs from the primary payload
   only in `gate_sha256`, and that the gate difference is explained only by
   the five path prefixes while all five content hashes and sizes match;
7. publish the full derived payload and digest into the durable request and
   prelaunch records before any scientific process starts.

The derivation must reproduce both:

- primary root -> `46403a00663fc331...06c48`;
- the consumed detached root -> `db7937fad5e95123...a269b8`.

### 5.3 Producer and official-audit validation

For detached witness phases:

- start and terminal stdout records must equal the prelaunch-derived digest;
- NPZ embedded metadata and JSON sidecar must contain the same full
  benchmark payload and digest;
- the producer durable final must bind the same request/prelaunch/run
  identity;
- the official-audit request may be published only after producer exit `0`,
  empty stderr, exact wait/reap, PG-empty, runtime pre/post equality, atomic
  pair, and canonical/source/input guards pass;
- the official audit must run in the same detached project/root/runtime and
  must independently derive and emit the identical benchmark payload;
- any producer/audit payload or digest mismatch fails closed.

For original matrix phases, the driver must continue to require the fixed
primary/canonical benchmark identity
`46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48`.
No detached-witness identity is admissible for matrix work.

## 6. Driver And Test Scope

Only the artifact-local durable driver and solver-free tests may change.
The minimum implementation may:

- add a versioned benchmark-identity binding record;
- add exact deterministic relocation derivation;
- thread the phase-specific expected identity through producer terminal,
  sidecar, producer-audit, official-audit, and request validators;
- preserve the primary constant for matrix/canonical context;
- add positive and negative synthetic fixtures.

Required negative cases include:

- arbitrary observed identity;
- wrong detached root or path prefix;
- missing/extra/wrong-role gate file;
- gate byte/hash/size drift;
- table-I manifest drift;
- any non-gate benchmark component drift;
- config or runner self-hash drift;
- producer start/terminal mismatch;
- sidecar/embedded/terminal mismatch;
- producer/official-audit mismatch;
- detached identity admitted in matrix context;
- primary identity admitted for a differently rooted detached witness;
- Unicode detached-root serialization drift, including an
  `ensure_ascii=False` implementation;
- path escape, symlink, hardlink/shared inode, writable gate, alias, and
  post-prelaunch mutation.

Phase A must be exact Python 3.14 and zero-science. It must run every prior
T4ah test/capture/rejection/fault/lock/runtime/input-contract guard plus the
new identity-binding cases. Scientific runner CLI, official audit, and
solver invocation counts must all be zero.

## 7. Phase And Authorization Boundaries

T4ai Phase A ends only at:

```text
CHECKPOINT / RELOCATED BENCHMARK IDENTITY CONTRACT FROZEN
```

Root T0 must independently review the driver diff, derivation, fixtures,
all Phase-A evidence, old HOLD evidence, runtime, canonical, absence,
process, and transient guards.

Only a fresh root-T0 authorization may permit a new full one-shot
`kM=1.58125` detached producer plus matching official audit. The consumed
producer pair may not be reused. Any new failure consumes that authorization
and forbids implicit retry.

Only a completely audited witness PASS may authorize the original matrix in
fixed order:

```text
2.91875 -> 3.759375 -> 3.89375 -> full 241x241
```

No threshold, tolerance, resolution, mode, point, `lmax`, frequency,
scientific source, canonical pair, legacy/golden data, performance/cache
rule, or downstream claim may change.

## 8. Orchestration And Safety

- Use only the existing T7 and T4 tasks.
- Create no task, subagent, proxy, or descendant.
- T7 review is read-only.
- T4 code work uses `gpt-5.6-sol/high`; `max` and `ultra` are forbidden for
  this bounded repair.
- No network, install, global environment mutation, destructive cleanup,
  production, plot, fixture, Kirchhoff, paper, or GitHub action is
  authorized.
