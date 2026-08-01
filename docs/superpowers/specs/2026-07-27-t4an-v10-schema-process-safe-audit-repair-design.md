# T4an V10-Schema And Process-Safe Audit Repair Design

## 1. Purpose

T4an supersedes the reviewed-but-undispatched T4am package after root T0's
mandatory fresh gate found a blocker that T7cp did not detect.

T4al's only audit-only child exited `1`. Its success-only launcher did not
persist stderr, so the exact historical exception and first thrown cause
remain unrecoverable. T4am correctly repaired the broad process scan and
the missing failure-capture branch, but it did not freeze a correction for
an independently proven deterministic pre-process defect in T4al's v10
manifest validator.

The T4al helper contains:

```python
require(value["raw_records"] == 1041, "v10 raw count mismatch")
```

The immutable v10 manifest actually contains:

```text
raw_records type  list
raw_records len   1041
record schema     {"path": str, "sha256": 64-lowercase-hex, "size": int}
unique paths      1041
path order        Unicode code-point ascending
```

and the generating driver's canonical SHA-256 of that exact list is:

```text
f0d3a4a0b5dbf39019b2daa524cc76b5e808241bf5d8e96e10a756c6d361ad27
```

The faulty comparison is inside `v10_snapshot()` and `collect_before()`
calls `v10_snapshot()` before `process_snapshot()`. Thus an additional
deterministic blocker exists before the broad process scanner. Because the
lost stderr prevents proving which earlier check first raised during the
historical child, T4an does not rewrite the exact historical exception.

T4an closes all three control-plane gaps in one bounded package:

1. generator-exact v10 manifest schema and index binding;
2. structured ancestry-aware, token-aware process validation;
3. durable raw failure capture and mutually exclusive terminal closure.

No scientific runner, implementation, live driver, runtime,
complete-290 input, canonical result, threshold, tolerance, mode, point,
resolution, or `lmax` contract changes.

## 2. Immutable T4al Boundary

The exact failed roots below remain immutable, non-executable, and
non-reusable:

```text
helper root
  t4al_phase_a0_helper_057bb24b_20260727T075721p0800
  dev/inode/nlink/uid/gid/mode/size
  16777244/1233390/3/501/20/040500/96
  mtime_ns 1785110467176422119
  ctime_ns 1785110508880737283

only helper
  t4al_preservation_helper.py
  sha256 ce05879486e703e4f1665552ecf91cdbf5f5bfb5f8fc58b494330efa9a05a7ed
  size 36513
  dev/inode/nlink/uid/gid/mode
  16777244/1233405/1/501/20/100400
  mtime_ns 1785110467177554089
  ctime_ns 1785110508880710782

empty audit root
  t4al_phase_a0_audit_records_057bb24b_20260727T075721p0800
  dev/inode/nlink/uid/gid/mode/size
  16777244/1233391/2/501/20/040700/64
  mtime_ns 1785110249294768176
  ctime_ns 1785110249294821718

reserved execution root
  t4al_phase_a1_execution_057bb24b_20260727T075721p0800
  absent
```

Exact invocation boundary:

```text
audit-only child       1
natural return code    1
pre/post equality      PASS
durable stderr         absent by defective protocol
execute                0
records/manifests      0
driver edit/preflight  0/0
runner/audit/solver    0/0/0
witness/matrix         0/0
```

The empty audit root's mode is not authority to populate, chmod, rename,
delete, repair, or reuse it.

## 3. Independent V10-Schema Finding

The frozen v10 manifest is:

```text
path
  runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/
  t4ah_phase_a_v10_guard_057bb24b_20260726T233134p0800/
  synthetic_preflight_v10_057bb24b_recursive_input_lifecycle_py314_
  20260726T233134p0800/preflight_manifest.json

sha256
  0b2b37c0dbd55810b6f3020d0dd69b4c7026d85134c4c9ef065b06a239b3a577
```

Root T0 independently loaded the exact bytes under CPython 3.14 and
confirmed:

```text
raw_records
  exact list length 1041
  every entry has exactly path/sha256/size
  1041 unique paths
  exact code-point path ordering

canonical raw-record index
  json.dumps(raw_records,
             sort_keys=True,
             separators=(",", ":"),
             allow_nan=False,
             ensure_ascii=False)
  UTF-8, no newline
  f0d3a4a0b5dbf39019b2daa524cc76b5e808241bf5d8e96e10a756c6d361ad27

CLI captures
  cli_capture_inventory is a dict
  capture_count 29
  capture_index_sha256
  8aacda7ef403b8b59a838b8ce1be1df506ad33e2385edf70e0cf4feb2c79a635

tests
  tests_passed is a 23-label list
  test_results is a 23-entry dict
  test_inventory.total_count 23

complete recursive input
  contract_record_count 290
  contract_index_sha256
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24

runtime identity occurrences
  9

scientific runner CLI / official audit / solver
  0 / 0 / 0
```

The T4al helper's list-versus-integer comparison is therefore guaranteed
false if reached. A new helper must never infer a count by comparing a
container to an integer.

The immutable 1,041 paths are all ASCII, so `ensure_ascii=True` happens to
produce the same stored digest. That accidental equality is not the v10
serialization contract. The live generating driver
`durable_control_driver_v2.py` SHA
`057bb24beeb0ea90c6a2524b8ca43df05b611ffe252a1f0b631fab149d1259a9`
defines `_canonical_json()` with explicit `ensure_ascii=False`, and
`_canonical_sha256(raw_records)` produced the stored index.

T4an therefore freezes two deliberately separate canonical surfaces:

```text
v10 raw-list index
  json.dumps(value,
             allow_nan=False,
             ensure_ascii=False,
             separators=(",", ":"),
             sort_keys=True)
  UTF-8, no newline

helper replay payload
  json.dumps(value,
             allow_nan=False,
             separators=(",", ":"),
             sort_keys=True)
  ensure_ascii omitted/default True
  UTF-8, no newline
```

Neither implementation may reuse the other serializer implicitly.

## 4. Exact V10 Validator Contract

T4an freezes one pure `validate_v10_manifest()` used by both audit-only and
future execute collection. It must:

1. bind the full manifest file hash and regular/non-symlink/nlink-1
   identity;
2. require `raw_records` to be a list, never a scalar or mapping;
3. require length exactly `1041`;
4. require every record to have exactly `path`, `sha256`, and `size`;
5. require path to be a normalized nonempty repository-relative string
   with no absolute form, dot escape, duplicate, case/Unicode alias, or
   noncanonical separator;
6. require the list already be in Python Unicode code-point path order;
7. require exactly `1041` unique paths;
8. require every hash to be lowercase 64-hex and every size to be a
   nonnegative integer but not boolean;
9. recompute the exact generating-driver canonical raw-list bytes with
   explicit `ensure_ascii=False` and require index
   `f0d3a4a0b5dbf39019b2daa524cc76b5e808241bf5d8e96e10a756c6d361ad27`;
10. require the stored `raw_record_index_sha256` to equal that recomputed
    index;
11. bind the exact CLI-capture, test, complete-290, runtime, and zero
    scientific-invocation fields above;
12. reject missing, extra, mistyped, duplicate, reordered, or drifted
    fields instead of coercing them.

The helper's canonical payload may contain only stable v10 facts:

```json
{
  "manifest_sha256": "0b2b37c0...",
  "raw_record_count": 1041,
  "raw_record_index_sha256": "f0d3a4a0...",
  "cli_capture_count": 29,
  "cli_capture_index_sha256": "8aacda7e...",
  "test_count": 23,
  "complete_290": "77927103...",
  "runtime_identity": "811d3840...",
  "runtime_occurrences": 9,
  "science_counts": [0, 0, 0]
}
```

It must not embed the full 6.6-MB manifest or timing/inode values in the
replay digest unless already part of a separately frozen stable identity.
The helper payload itself uses the separate replay serializer with
omitted/default `ensure_ascii=True`; the already-computed v10 index is a
string field in that payload and is never recomputed with the replay
serializer.

## 5. Mandatory Zero-Science V10 Fixtures

Before the real Phase-A0 child, T4 runs pure validator fixtures that never
launch the runner, official audit, or solver:

- exact frozen manifest PASS;
- scalar `raw_records = 1041` reject;
- mapping `raw_records` reject;
- missing/extra record reject;
- 1040 and 1042 list lengths reject;
- duplicate path reject;
- reordered path reject;
- absolute/path-escape/noncanonical path reject;
- case/Unicode alias reject;
- extra/missing/wrong key reject;
- uppercase/short/nonhex hash reject;
- negative/bool/noninteger size reject;
- raw-list content tamper reject;
- stored index tamper reject;
- non-ASCII serializer discriminator PASS using exactly:

  ```json
  [{"path":"含中文/δ.json","sha256":"0000000000000000000000000000000000000000000000000000000000000000","size":0}]
  ```

  The generator-exact `ensure_ascii=False` bytes must hash to
  `b4e06758295001d25a50dff9bf13f54ebf45a8036c30c2626a5c10eb341a3eee`;
  the otherwise-identical `ensure_ascii=True` bytes must hash to
  `fd74c5506b8b4dc8af160d6ad41b46c84fb877a27689703753316b84d6c46343`,
  the byte strings and hashes must differ, and the true-mode alternative
  must be rejected as a v10-index implementation;
- capture count/index tamper reject;
- test label/count/result mismatch reject;
- complete-290/runtime/science-count drift reject.

Fixture assembly may use in-memory copies only. It may not alter the frozen
v10 manifest or any evidence file.

## 6. Process-Safe File-Based Launch

T4an retains T4am's reviewed three-root geometry:

```text
fresh immutable helper root
fresh audit-record root containing immutable launcher
fresh reserved execution root absent throughout Phase A0/replay
```

Helper and launcher freeze project/control/helper/audit/execution as direct
full exact `ast.Constant` strings. The launcher also freezes exact helper
path/hash and Python-3.14 executable. Root inference, `Path.parents`,
environment expansion, aliases, stdin scripts, heredocs, `python -c`,
dynamic launcher generation, and shell evaluation are forbidden.

Static dataflow review must prove the v10 raw-index validator calls only
the explicit-false serializer, while helper stdout/replay digest calls
only the default-true serializer. A shared ambiguous canonical helper or
argument-controlled mode is forbidden.

The launcher is invoked from its frozen file with `--first-attempt`.
Root-T0 later uses the same file with `--replay-only`.

The helper receives an explicit expected launcher PID only as validation
input. That PID and every PID/PPID/PGID/SID/raw command are excluded from
the canonical payload and replay digest.

One structured process snapshot contains:

```text
pid ppid pgid sid state command
```

The parser requires unique self and exact direct launcher ancestry, exempts
only those two rows, and checks all other rows with normalized
executable/script/argument-token semantics. Missing, duplicate, malformed,
wrong-parent, cyclic, alias, ambiguous, sibling, unrelated-runner, or
forbidden-script cases fail closed. Broad whole-command substring matching
is forbidden.

Zero-science process fixtures cover valid ancestry, marker text in the
exact launcher, harmless marker prose, and every rejection branch.

## 7. Durable Success And Failure Closure

The launcher captures complete prelaunch inventories, launches exactly one
audit-only child, captures raw stdout/stderr/return/signal/wait/reap, and
captures complete post inventories before publication.

If no-write pre/post equality, helper/launcher identities, or execution
absence fails, it publishes nothing because safe attribution is lost.

If equality passes, it durably publishes common attempt records regardless
of child success:

```text
attempt_request.json
source_static_review.json
v10_validator_fixtures.json
process_classifier_fixtures.json
argv_cwd_environment.json
pre_inventory.json
post_inventory.json
stdout.bin
stderr.bin
child_terminal.json
wait_reap_process_group.json
attempt_guards.json
```

All publications are exclusive/no-follow, atomic, file-fsynced,
parent-fsynced, reloaded, and hashed.

Success requires exit0/no signal/empty stderr/exact canonical stdout and
all guards. It closes with:

```text
records_index.json
phase_a0_final_manifest.json
```

Any nonzero, signal, nonempty stderr, malformed stdout, v10/process/payload
failure, or post-child semantic failure closes with:

```text
failure_records_index.json
phase_a0_failure_manifest.json
```

Success and failure terminal sets are mutually exclusive. Each terminal
manifest binds its branch, records index, exact filename set including
itself, publication order, fsync/reload proofs, and intended modes, but not
its own hash/stat or post-close timestamp. T4 reports those after close.

Failure consumes authorization, forbids execute, returns HOLD, and permits
no local retry.

## 8. Root-T0 Replay And Later Boundaries

Only success returns:

```text
CHECKPOINT / T4AN V10-SCHEMA PROCESS-SAFE AUDIT HELPER FROZEN
```

Root T0 must fully read and independently validate sources, AST/dataflow,
v10/process fixtures, records, indexes, terminal manifest, and all frozen
guards. It then invokes the frozen launcher once in no-write
`--replay-only` mode and requires byte-identical helper stdout/digest,
empty stderr, exit0, unchanged helper/audit roots, execution absent, and
zero science.

Only complete replay PASS can support a separate digest-bound one-shot
preservation execute authorization. Preservation PASS may resume only the
already reviewed T4ai artifact-local driver/tests and one fresh
exact-Python-3.14 zero-science preflight.

## 9. Frozen Upstream Guards And Safety

```text
T4am candidate
  c1adcbd5233a6aefa55a8343c33438eabecbe4d6

T4al candidate
  6b27fe58a3946429493a0a69365a6146b4144f49

primary compute HEAD
  45face32f52537ac4b8ab79cb1746d8ac78e9b82

driver
  057bb24beeb0ea90c6a2524b8ca43df05b611ffe252a1f0b631fab149d1259a9

runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768

runtime manifest
  f3ebf3dbf8981500c8d7f714b1740996638f10e32ef17a8377d45ea0b70ab6ca

runtime identity
  811d3840e858c1ad0a92c665e54dbf99662d884575871ade6ab45c6b40c4db30

complete-290
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24

consumed witness
  2566 files / 582625016 bytes
  c21828703400ae65b52d516fe7d41e52f2d7255de1f3a6bdd22f5c3cdb13bb97
```

Canonical four hash/stat/inodes remain exact; all eight later-unit files
remain absent; external zero-byte object remains exact; control has zero
unexpected symlink/hardlink/lock/tmp/partial/process state.

Phase A0 authorizes no execute, driver edit/preflight, scientific runner,
official audit, solver, witness, matrix, pair reuse, canonical/external
write, cleanup, destructive action, network/install/global mutation, new
frequency, production, plot, fixture, Kirchhoff, paper, or GitHub action.

Use existing T4/T7 tasks only. T4 uses `gpt-5.6-sol/high`; `max` and
`ultra` are forbidden. No task, subagent, proxy, or descendant.
