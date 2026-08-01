# T4ba Full-Image Cache-Accounting Projection Repair Design

## 1. Decision Scope

The first authorized full `241x241` producer completed the expensive
numerical call path and then failed before comparison or publication because
the unchanged runner contains one wrong cache-hit accounting literal.

This package repairs only that full-image control-accounting surface through
one artifact-local, full-image-only in-memory projection. It does not change
the runner file, scientific source, grid, mask, `lmax`, convergence probes,
runtime, complete-input contract, fixed identity, legacy/golden artifacts,
comparison budgets, canonical outputs, accepted frequency pairs or matrix
order.

T4ba Phase A is exact-Python3.14 zero-science and stops at:

```text
CHECKPOINT / FULL-IMAGE CACHE ACCOUNTING PROJECTION FROZEN
```

## 2. Consumed Full-Image Boundary

The immutable unit is:

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/
  t4ae_matrix_sequence_bdaeeda3_20260728T122000p0800/
  unit_full_241x241/
```

Exact durable identities:

```text
request
  14e02533ca6a356a2d87c40b65e0131112cbef38edeaea7db805fd9a17dfb4f1
prelaunch
  ee203d96950fa648b1b200e0a8fe3f13899c3ee526f6d80ce108904363579c1f
running
  4ea51ea6676799c037d8bcf0dd0014bc75ed0ca68b392396136c73d596dc9404
launch receipt
  be9add3658ef6e39b29500e318dc6bd5de8f40fcad702f37cc3bee9557171c65
final
  4454f6d716d2f8294735fe4d0e0834b977555fda345018cd34e768192a00ced7
stdout
  d8667b6fa65a8437e6834380f19d8d9091067d2b60b202fd15766ed56dd5a2fd
stderr
  294f894264ca4e10eb202580775627306ad2a6d2788269bee8d95d0fbb7058ff
```

The child terminal record is:

```text
supervisor PID
  34980
child PID / SID / PGID
  34989 / 34989 / 34989
exit / signal
  1 / null
wait
  subprocess.Popen.wait / exact / reaped
process group
  empty
wait errors
  0
elapsed ns
  5176352829541
```

Stdout contains only the correct 216-byte `optimized_case_start` record.
Stderr ends exactly at runner line 3977 with:

```text
GateContractError: full-image call/cache/true-solve contract mismatch
```

Both supervisor streams are empty. The matching official audit, unit
checkpoint and full canonical pair are absent. The unit is consumed and may
never be rerun, repaired, populated, audited, copied, promoted or reused.

Independent whole-root reconstruction gives:

```text
regular files
  3234
directories inclusive
  363
file bytes
  627046494
symlinks / non-one-link regular files
  0 / 0
path<TAB>sha256<TAB>size<LF> ledger
  330dfdcf6c56254363c923a5e5acbe2485dba3c4fc11df66bfed676a9d7d520b
```

## 3. Deterministic Accounting Proof

The unchanged runner SHA is:

```text
18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768
```

It and the regression test freeze:

```python
FULL_IMAGE_OPTIMIZED_CACHE_HIT_COUNT = 10_367_742
```

The exact frozen full-image configuration has:

- `241x241` inclusive x-z grid from `-30` to `30` with step `0.25`;
- Schwarzschild `M=1` and masked invalid radii `r<=2`;
- final `lmax=180`;
- convergence `lmax=[108,132,156,180]`;
- six theta and two phi probes, hence 12 probes per convergence level.

Direct integer lattice enumeration gives exactly 197 masked points and
57,884 valid grid calls. Convergence adds 48 polarization calls, so the
total is 57,932, exactly as required by the runner and immutable legacy
record.

Each final-grid call requests two sectors for every `ell=2..180`, or 358
run-cache keys. The first grid call has 358 misses and every later final-grid
request is a hit. Each convergence probe requests:

```text
lmax 108 -> 214 keys
lmax 132 -> 262 keys
lmax 156 -> 310 keys
lmax 180 -> 358 keys
```

All are already present after the grid. Therefore:

```text
(57884 - 1) * 358 + 12 * (214 + 262 + 310 + 358)
  = 20735842
```

The immutable legacy full-image sidecar:

```text
runs/phase5/equivalence_preserving_methods_gate/legacy/full_image/
  t8ah_li_fig3_xz_k1p0_dx0p25.npz.json
SHA-256
  08f7a8e3e4ae508265b4f6480ebcb528289f3827202beff3cb12a22d67821b7a
```

independently records `benchmark_record.cache_metrics.cache_hit_count =
20735842`, together with polarization calls 57,932 and radial solves 358.
No accepted specification freezes a hit-count reduction. The wrong literal
is therefore an arithmetic/control-accounting defect, not a scientific or
performance criterion.

The failed in-memory arrays and metadata were discarded before comparison
and publication. They are not scientific PASS evidence and cannot be
recovered or reused.

## 4. Full-Image-Only Projection

Phase A must freeze one fresh immutable wrapper above the exact current
physical shim:

```text
t4az_matrix_warning_adapter_launcher.py
SHA-256
  9e424fab261e207822958c365709c9a324975a19ba56c1193d428c68fbf10d21
```

The wrapper must load that exact shim and preserve its existing
T4ax/T4ar warning and loaded-module projections. It may intercept only the
exact T4ar adapter load in order to wrap `adapter._load_runner`.

The wrapped loader must:

1. call the unchanged original `_load_runner()` exactly once;
2. thereby named-load and fully verify the unchanged primary runner first;
3. require the runner path/SHA and implementation identity to remain exact;
4. require the runner's current literal to be exactly `10367742`;
5. require exact config path/SHA
   `4b714db46cc92488db95417d7211ec2f05d0ffc383867d680f5b403e13904971`;
6. require exact legacy sidecar path/SHA
   `08f7a8e3e4ae508265b4f6480ebcb528289f3827202beff3cb12a22d67821b7a`;
7. recompute the frozen grid/mask/probe/key formula as exactly `20735842`;
8. require the legacy raw record to contain the same exact value and exact
   `57932/358` call/solve counts;
9. set only the loaded module's in-memory
   `FULL_IMAGE_OPTIMIZED_CACHE_HIT_COUNT` to `20735842`;
10. return the same module and allow the unchanged adapter and runner
    `main()` flow to continue.

No runner or test file is edited. No module other than the exact named runner
may be patched. The wrapper may not alter functions, source command,
scientific arrays, metadata, comparison logic, budgets, performance gates,
runtime state, config, legacy/golden files or canonical outputs.

## 5. Route and Provenance Boundary

The projection is legal only when the exact logical runner argv selects:

```text
--mode run   --case full-image
--mode audit --case full-image
```

It must reject frequency, matrix preflight, arbitrary case, missing or
duplicate mode/case, `-c`, stdin, argument/environment-controlled paths,
fallback, prefix/glob/regex/case/Unicode matching and any non-exact physical
launcher/runner/config/legacy identity.

The new physical wrapper path/SHA must be bound by the artifact-local durable
driver. The logical argv must still bind the unchanged primary runner. The
same wrapper, formula digest, physical/logical argv, roots, runtime,
complete290 and fixed identity must match across prospective producer,
matching official audit, replay and final checkpoint.

All five accepted frequency pairs and checkpoints continue to bind their
already accepted runner/driver evidence. The new wrapper is forbidden on
every frequency route and does not rewrite their provenance.

## 6. Phase-A Zero-Science Verification

Exact Python3.14 tests must prove:

- original loader called once before the single constant assignment;
- only the exact runner module and exact attribute can change;
- correct old literal/config/legacy/formula accepts;
- wrong old literal, new literal, grid, mask, resolution, range, step,
  `M`, lmax list, probe count, sidecar call count, solve count or cache count
  rejects;
- runner/shim/wrapper/config/legacy path/hash/stat/link/alias drift rejects;
- run and audit full-image routes accept;
- every frequency/preflight/cross-case route rejects;
- physical/logical argv and producer/audit/replay mismatch rejects;
- in-memory patching cannot write runner/test/config/legacy/canonical bytes;
- wrapper calls unchanged shim/adapter/runner main exactly once and
  propagates return/SystemExit;
- old runner/test bytes, driver-except-launcher binding, runtime,
  complete290, fixed identity, canonical ten files and full-pair absence are
  unchanged.

One full synthetic zero-science preflight may exercise the wrapper with a
fake exact-shape module. A real split-root preflight may only validate
imports, roots, identities and route/dataflow with `solver_started=false`.
Phase A must execute zero optimized producer, official audit, solver or
full-image numerical call.

Diagnosed pre-execution artifact-local helper/fixture/manifest/path/hash/
bookkeeping defects may be minimally corrected in fresh roots. Any need to
change runner/science/runtime/input/fixed identity/config/legacy/canonical/
criteria/order returns fail-closed to root T0.

## 7. Later One-Shot Boundary

Only after T7da GREEN, T4ba checkpoint and root-T0 full audit may root T0
authorize one completely fresh full-image producer. Only its complete PASS
may authorize one matching unchanged official audit and atomic checkpoint.

Any launched producer or audit failure consumes the new unit and forbids
retry. The consumed first full unit is never reusable.
