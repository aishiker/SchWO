# T4as Legacy Reconstruction Durable-Supervision Repair Design

## 1. Purpose

Close one control-plane gap discovered before the authorized legacy
`kM=2.91875` reconstruction started: the frozen T4ar driver does not expose
phases capable of supervising the separately frozen reconstruction launcher's
`run` and `audit` modes.

This repair changes no scientific runner, legacy implementation, scientific
source, runtime dependency, complete-input meaning, warning rule, legacy or
golden artifact, canonical output, benchmark identity, numerical criterion, or
matrix order. It adds an exact phase-specific durable-supervision surface and
tests it without executing reconstruction science.

## 2. Immutable Prelaunch HOLD

The attempted T4ar Phase B stopped before any child, detached source, output
pair, or scientific request existed:

```text
decision
  HOLD / LEGACY RAW-WARNING WITNESS PRELAUNCH DRIVER PHASE-SURFACE BLOCKED
evidence root
  runs/phase5/equivalence_preserving_methods_gate/
    control_provenance_witness/
    t4ar_phase_b_prelaunch_hold_ee2b2960_20260727T204500p0800
manifest
  241584cc23907c0b97f63b5d1042272e99900edb99fcd38015fd1166ec31ec20
audit helper
  0b57be2b08da0ae905b5b8d831ad8002e61618ad5d7a28209d0edce9addf479e
```

The root contains exactly the helper and manifest and is closed
`0500/0400/0400`. The manifest is canonical UTF-8 JSON with explicit
`ensure_ascii=False`, sorted keys, compact separators, and no newline.

It records:

```text
authorization_consumed=false
child_launch_count=0
producer_invocation_count=0
matching_audit_invocation_count=0
scientific_solver_invocation_count=0
matrix_invocation_count=0
detached_root_created=false
output_pair_created=false
process_matches=[]
transient_paths=[]
```

The prior authorization cannot be treated as an executable authorization for
a different driver identity. After this Phase-A repair, root T0 must audit the
new checkpoint and issue one new exact one-shot authorization.

## 3. Exact Diagnosed Gap

The frozen driver is:

```text
path
  runs/phase5/equivalence_preserving_methods_gate/
    control_provenance_witness/durable_control_driver_v2.py
SHA-256
  ee2b2960205383fdd6e946abfaf2ae91e540f9657b2b10c440f141a349b67ed5
size
  838910
```

Its phase surface contains exactly six old phases:

```text
t4af_phase_a_synthetic_preflight
t4af_phase_a_synthetic_scientific_audit_control
t4af_phase_b_control_provenance_witness
t4af_phase_b_control_provenance_witness_scientific_audit
t4af_original_matrix_continuation
t4af_original_matrix_continuation_scientific_audit
```

The non-synthetic path:

1. requires a T4aq/T4ar matrix-adapter launcher binding;
2. requires a logical argv whose second token is the unchanged optimized
   scientific runner;
3. calls `_match_scientific_command()` against only witness or matrix
   `run/audit` commands;
4. derives output geometry from that optimized runner; and
5. parses optimized-runner start/terminal records and optimized artifact
   paths.

The frozen reconstruction launcher is:

```text
path
  runs/phase5/equivalence_preserving_methods_gate/
    control_provenance_witness/
    t4ar_phase_a_053ffd06_20260727T191954p0800/
    t4ar_legacy_warning_reconstruction_launcher.py
SHA-256
  20bd7e78837b5b78a2258a1cec19baa7fbaff07c500d9c27ce278d099b3b79c6
size
  15917
modes
  run, audit
```

It is not the optimized runner and emits a distinct terminal schema. Reusing
an old phase, bypassing the driver, or editing the driver after a request is
frozen would all violate the accepted provenance contract.

## 4. Frozen Scientific And Evidence Identities

T4as preserves:

```text
primary compute HEAD
  45face32f52537ac4b8ab79cb1746d8ac78e9b82
T4ar candidate
  132d98750a57ceea8f59423b0f8f5d66ad8facbd
T4ar Phase-A checkpoint
  2c6be479f0cbff850addc9b519160242d1cf202211803b73a9e4129166612f26
matrix adapter
  b38739fbc4af3d923d884f42c868f34ab76407bb89a5551cd3feb9fbf9b5cc8a
scientific runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768
legacy implementation commit
  8fb8608c187280dc39fd56a78b976e6cf75a6ada
complete-290 contract
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24
runtime overlay manifest
  f3ebf3dbf8981500c8d7f714b1740996638f10e32ef17a8377d45ea0b70ab6ca
overlay content index
  1803e0f763cac682442b22af8986b240e5830a1a42849c77ae2c7aa96fc39371
fixed optimized benchmark identity
  46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48
relocated witness checkpoint
  2c448a70ed9dc47399c9bb1f148add60315670d4e66c886e5e7895abb5e8cde9
legacy NPZ
  3bf0abfb7abc090918778012560a967ca91b6ec06bb934d529a7a758133402aa
legacy sidecar
  d5c839cdf2e2a8b0cb1c5b87754a87898684bf0e433ef2bcc1d06f2529bb9788
legacy golden
  d6b81923284142dfe5faf13e8932b4e5c12aed1cd253c459ab10641ab0949b8b
legacy v1 driver
  f5ac6a830e1ab8fb052eebb4ca7b7f99f2776d80a1d1a2315d0b383e439d08e7
raw-warning record
  624 / e9ce10c6ca59c5d2e1eb281c86859528c095b3b75e848ec58c8997aba7015d97
```

The four accepted optimized files retain exact hash/stat/inode identities.
The `2.91875`, `3.759375`, `3.89375`, and full-image pairs remain absent.

## 5. New Phase Model

The driver shall add two exact, non-interchangeable phases:

```text
t4as_legacy_raw_warning_reconstruction_producer
t4as_legacy_raw_warning_reconstruction_audit
```

They may be named by constants, but their literal values are frozen above.
They must enter `_ALLOWED_PHASES` without changing the existing six phase
values or their behavior.

The new phases must not be inserted blindly into the existing optimized
runner phase sets. The driver shall use phase-specific sets or an equally
explicit dispatch that keeps these surfaces distinct:

```text
optimized scientific run/audit
  unchanged runner, optimized command and optimized terminal schema
legacy reconstruction producer/audit
  reconstruction launcher, reconstruction command and reconstruction schema
synthetic control
  internal zero-science children only
```

The producer markers are exact:

```text
scientific_runner_invoked=false
scientific_solver_invoked=true
reconstruction_launcher_invoked=true
reconstruction_mode=run
```

The matching audit markers are exact:

```text
scientific_runner_invoked=false
scientific_solver_invoked=false
reconstruction_launcher_invoked=true
reconstruction_mode=audit
```

The current optimized runner SHA remains an immutable guard, not a false claim
that the optimized runner was invoked.

## 6. Exact Reconstruction Command Surface

The producer command is exactly:

```text
<exact Python 3.14.6>
<exact reconstruction launcher>
--mode run
--expected-launcher-sha256 20bd7e78...79c6
--detached-root <fresh exact legacy root>
--overlay-root <frozen content-addressed overlay>
--output-root <fresh isolated output root>
```

The audit command differs only by `--mode audit`. No `-c`, stdin script,
sitecustomize, import hook, alternate launcher, wrapper, prefix/glob command,
extra argument, or argument-controlled phase is permitted.

The driver must bind the full argv and canonical argv digest; executable,
launcher, detached root, overlay root, and output root exact path identities;
launcher hash/stat/inode/nlink/mode; cwd and allowed cwd root; environment and
environment digest; source and input manifests; exact legacy commit; Phase-A
checkpoint; immutable legacy/golden artifacts; and canonical guards.

The detached root, output root, producer run directory, and matching-audit run
directory must be pairwise distinct, non-aliased, same-filesystem where atomic
publication requires it, direct descendants of one fresh T4as attempt root,
and disjoint from canonical, legacy, golden, driver, launcher, runtime overlay,
and every older evidence root.

## 7. Reconstruction Binding Schema

Each new request shall contain one exact `legacy_reconstruction` binding.
The driver may choose field names only if the frozen semantics remain exact.
The binding must include:

- schema/version and exact `2p91875` scope;
- exact phase and mode;
- reconstruction launcher path/hash/stat identity;
- full argv and canonical digest;
- detached root, output root, cwd, and allowed-root identities;
- exact legacy commit and clean tracked scientific implementation;
- complete-290 source/input manifest paths, hashes, counts, roles, and final
  contract;
- exact Python, NumPy, SciPy, overlay manifest/content index, environment, and
  isolated-HOME identities;
- immutable legacy NPZ/sidecar/golden/v1-driver identities;
- T4ar Phase-A checkpoint, driver-before identity, and raw-warning expected
  record;
- expected isolated filenames
  `legacy_raw_warning_2p91875.npz` and
  `legacy_raw_warning_2p91875.npz.json`;
- canonical four before identities and exact eight-path absence;
- explicit no-canonical-write and no-promotion claims.

Every source/target input must be regular, non-symlink, nlink-1, read-only,
hash/size/realpath exact, distinct-inode where required, and contained under
the bound roots. Case, Unicode, prefix, basename, glob, regex, symlink,
hardlink, writable, missing, duplicate-role, duplicate-path, shared-inode,
wrong-root, wrong-commit, wrong-manifest, wrong-overlay, and wrong-environment
variants fail closed.

## 8. Durable Producer Closure

The existing request/prelaunch/running/receipt/streams/final/control-audit
durability remains mandatory:

- child PID=SID=PGID;
- natural exit `0`, no signal;
- exact `Popen.wait`, child reaped, process group empty, zero wait errors;
- empty stderr;
- exact argv/cwd/env/request/bindings cross-record equality;
- runtime/source/input/legacy/golden/canonical pre/post equality;
- no unexpected process, lock, tmp, partial, quarantine, link, alias, or
  output;
- one isolated same-filesystem atomic pair only.

The reconstruction `run` stdout is exactly one UTF-8 canonical JSON line and
no other byte. After parsing, it must have the exact launcher result schema:

```text
schema_version=t4ar_legacy_reconstruction_run_result_v1
npz_path=<exact isolated NPZ>
npz_sha256=<direct file hash>
witness_path=<exact isolated JSON>
witness_sha256=<direct file hash>
```

The driver shall not parse this as an optimized runner start/terminal pair.
Its control audit independently reloads the pair and requires:

- exactly 22 scientific arrays;
- exact name/order/dtype/shape/C-order bytes against legacy and golden;
- exact structured warnings `296/98`;
- exact three-tuple raw warning record `624 / e9ce10c6...15d97`;
- exact witness schema and all source/runtime/input identities;
- legacy sidecar field still truly absent;
- canonical and all old evidence unchanged.

No output copy, promotion, post-hoc edit, sidecar rewrite, or canonical path is
reachable.

## 9. Matching Reconstruction Audit

Only a producer durable/control/pair PASS may construct one matching audit
request. The audit binding must include exact producer run id, request/final
paths and hashes, parsed producer result and digest, pair path/hash/stat/inode,
launcher/roots/argv/cwd/env/runtime/source/input identities, and producer
terminal process records.

The audit uses the same exact launcher, detached root, overlay, isolated pair,
Python, environment, and provenance; only mode and run directory differ.
It is zero-solver.

Audit stdout is exactly one canonical JSON line:

```text
schema_version=t4ar_legacy_reconstruction_audit_result_v1
valid=true
npz_sha256=<producer pair hash>
witness_sha256=<producer pair hash>
```

It must exit `0` with no signal and empty stderr, exact wait/reap/PG-empty,
and no output mutation. Pre/post pair stat/hash/inode and complete global
guards must be equal. The driver must not route this child through optimized
official-audit parsing.

Any producer or audit launch failure consumes the new future authorization and
forbids retry.

## 10. Process And Replay Semantics

The process guard must recognize the exact driver, reconstruction launcher,
optimized runner, and matrix adapter by parsed argv/path identity and ancestry.
It must reject duplicate/parallel producer or audit, unrelated launcher,
wrong parent/session/group, zombie, alias, and ambiguous rows. It must not use
broad command-substring matching that can match an observer's prose or shell.

Variable PIDs and timestamps may be recorded but must not enter identities
that are expected to replay byte-for-byte. Static request/argv/root/launcher
bindings, runtime/input identities, and parsed reconstruction terminal records
must be identical across producer, audit, final control audit, and any
read-only replay.

## 11. Phase A: Zero-Science Repair

T4as Phase A may modify only the artifact-local durable driver and
artifact-local control/test/helper files. The exact reconstruction launcher
should remain byte-identical. If a newly demonstrated pre-child
artifact-local launcher-control defect makes the reviewed command impossible,
T4 may minimally repair only CLI/provenance/atomic-control code in a fresh
root; it must preserve the exact single `_compute_frequency()` call, warning
capture, scientific imports/arguments/constants, 22-array comparison, and
scientific dataflow. Any such change must be separately visible in the
checkpoint for root-T0 audit.

Required zero-science tests include:

1. both new literal phases are allowed and distinct;
2. all six existing phase values and accepted requests remain unchanged;
3. exact producer and exact audit requests validate;
4. producer markers are `false/true/true/run`;
5. audit markers are `false/false/true/audit`;
6. reconstruction argv cannot be accepted as witness/matrix argv and vice
   versa;
7. wrong mode, launcher, hash, Python, argv order, extra arg, cwd, roots,
   overlay, commit, input, environment, pair name, legacy/golden, checkpoint,
   warning digest, or canonical guard rejects;
8. output/canonical/root overlap and every alias/link/writeability case rejects;
9. producer stdout schema positive plus malformed/extra/missing/multiline/
   wrong-path/wrong-hash/optimized-terminal negatives;
10. audit stdout schema positive plus producer/audit mismatch and pair
    mutation negatives;
11. producer failure/nonzero/signal/stderr/wait/PG/runtime/input/source/
    canonical/post-child drift closes durably and forbids audit;
12. audit failure/nonzero/signal/stderr/wait/PG/pair/global drift closes
    durably;
13. exact process ancestry/token positives and harmless marker-prose negative;
14. failure audit, control audit, runtime snapshot, source files, canonical
    guards, and replay understand both new phases;
15. static AST/dataflow proves optimized terminal parsers are unreachable from
    reconstruction phases and reconstruction parsers are unreachable from old
    phases;
16. static AST proves no Phase-A path reaches the reconstruction launcher,
    optimized runner, `_compute_frequency`, solver, or official audit.

Run exact Python 3.14 static/AST/dataflow checks, Ruff, diff-check, targeted
tests, and one full synthetic preflight. Then build one fresh prospective
exact-legacy detached/input/output geometry and validate a complete producer
request plus matching-audit template without launching either child. It must
record:

```text
reconstruction launcher invocation=0
optimized scientific runner CLI invocation=0
matching reconstruction audit invocation=0
official matrix audit invocation=0
solver invocation=0
```

The prospective roots remain immutable evidence and are never reused for
Phase B.

Only complete PASS returns:

```text
CHECKPOINT / LEGACY RECONSTRUCTION DURABLE SUPERVISION FROZEN
```

## 12. Later Gates

After root T0 independently audits Phase A, it may issue one new:

```text
AUTHORIZED / LEGACY 2P91875 RAW-WARNING RECONSTRUCTION WITNESS
```

The old prelaunch authorization is not reused. Producer plus matching audit
PASS returns the existing T4ar checkpoint:

```text
CHECKPOINT / LEGACY RAW-WARNING WITNESS PASSED
```

Root T0 must then independently audit every durable and scientific record
before Phase C. T4ar Phase C remains zero-science and separately gated. Only
its full audit may authorize a new matrix `2.91875` one-shot.

## 13. Local Self-Remediation And Prohibitions

Within T4as Phase A, diagnosed pre-execution zero-science artifact-local
driver/helper/fixture/manifest/path/serialization/bookkeeping/ordinary-test
defects must be preserved in immutable failed roots, minimally corrected in
fresh no-overwrite roots, and continued to the exact checkpoint. There is no
fixed correction count and no blind unchanged retry.

Return to root T0 only if a correction would change the scientific runner,
scientific source, runtime dependency, complete-input meaning, exact legacy
computation, fixed benchmark identity, canonical artifacts, warning count or
allowlist, numerical criteria, matrix order, or require destructive/global
action.

Forbidden: old-root mutation; reuse of prospective roots; launched-child
retry; warning suppression/filter/count adjustment; missing-as-zero;
legacy/golden/canonical rewrite; output promotion; runner/source/runtime/input/
identity/criteria/order changes; alternate/parallel/duplicate execution; new
frequency; production; plot; scientific fixture; Kirchhoff; paper; GitHub;
network/install/global mutation; destructive cleanup; new task/subagent/proxy/
descendant; `max`; or `ultra`.
