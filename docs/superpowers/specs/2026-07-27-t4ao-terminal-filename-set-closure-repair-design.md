# T4ao Terminal Filename-Set Closure Repair Design

## 1. Purpose And Scope

T4an reached a durable control-only HOLD after its sole audit child passed.
The child exited `0`, emitted canonical stdout, emitted empty stderr, was
exactly waited and reaped, left its process group empty, preserved complete
pre/post inventories, kept the reserved execution root absent, and invoked
no scientific runner, official audit, solver, witness, or matrix work.

The launcher then rejected its own terminal directory because the computed
`exact_final_filenames` omitted the already-frozen launcher file. This is a
control-record closure defect. It is not scientific failure and it does not
authorize reuse, mutation, repair, or replay of the consumed T4an attempt.

T4ao permits only a fresh reviewed Phase-A0 helper/audit attempt that
preserves all accepted T4an v10-schema, dual-serializer, process-classifier,
runtime, complete-input, provenance, and zero-science semantics while fixing
the terminal filename-set construction.

No production runner, scientific implementation, durable driver, runtime,
complete-290 input, canonical result, threshold, tolerance, resolution,
mode, point, frequency, or `lmax` contract changes.

## 2. Immutable T4an HOLD Boundary

The following roots are immutable, non-executable, non-reusable, and must
not be chmodded, completed, renamed, deleted, or used as replay/execute
inputs:

```text
helper root
  t4an_phase_a0_helper_057bb24b_20260727T091432p0800
  helper t4an_audit_helper.py
  sha256 a0b6e77b59d8c5a207e8810c1365356043b7bc6565a256ed64f7b856edfbdef4
  size 37239

audit root
  t4an_phase_a0_audit_records_057bb24b_20260727T091432p0800
  mode 040700
  exact direct-child count 15
  launcher t4an_audit_launcher.py
  launcher sha256 517f86087818284ccdb8f48d223c7d6e4cee1177e07409336c66fdb5023eda3a
  launcher size 22523

reserved execution root
  t4an_phase_a1_execution_057bb24b_20260727T091432p0800
  absent
```

Exact child facts:

```text
pid/sid/pgid          18329/18329/18329
return/signal         0/null
stdout                16597 bytes
stdout sha256         ce415019fd58ba5f5d62a856f564335d57ad6300ea1adfcfb8b3cb7590136625
stderr                0 bytes
stderr sha256         e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
wait/reap/PG empty    PASS/PASS/PASS
pre/post bytes        equal
pre/post sha256       18758c4c2e0952d3e8007fe6692bc2fe6e0da14e29a9a545dfe0a02e5137d533
execution absent      PASS
science counts        0/0/0
```

Exact failed closure:

```text
manifest expected direct children  14
actual direct children             15
only unexpected name               t4an_audit_launcher.py
records index sha256                05d1131fb55b1fad4b4087575c961e9403d7187c07e284c1f7dfe0001cb1686a
incomplete success manifest sha256  efadb969139a793a17895fdc36190fa8e6b8418d4d525abbf49a21fe13ab5539
failure index/manifest              absent/absent
audit-root close                    not reached
```

The embedded success decision is superseded and invalid because its exact
filename-set claim is false and the audit root never closed.

## 3. Root Cause

The frozen T4an launcher builds:

```python
final_names = sorted(
    [item["name"] for item in publications] + [manifest_name]
)
```

`publications` begins only after the audit child returns and therefore
contains the common records and branch index, but not the launcher that
already existed in the audit root. The subsequent exact-set assertion
correctly fails.

The repair must not merely special-case the observed count. It must freeze
and verify a three-part terminal inventory:

```text
immutable baseline files
+ newly published non-terminal records
+ exactly one terminal manifest
```

## 4. Exact Terminal-Set Model

The fresh T4ao audit root initially contains exactly:

```text
BASELINE_NAMES = ("t4ao_audit_launcher.py",)
```

The launcher freezes exact, disjoint tuples:

```text
BASELINE_NAMES
COMMON_RECORD_NAMES
SUCCESS_INDEX_NAME
SUCCESS_MANIFEST_NAME
FAILURE_INDEX_NAME
FAILURE_MANIFEST_NAME
```

For branch `b`, compute before publication:

```text
branch_index_name(b)
branch_manifest_name(b)
expected_before_manifest(b)
  = sorted(BASELINE_NAMES
           + COMMON_RECORD_NAMES
           + (branch_index_name(b),))
expected_final_names(b)
  = sorted(expected_before_manifest(b)
           + (branch_manifest_name(b),))
```

Required sequencing:

1. prove initial audit-root names equal `BASELINE_NAMES`;
2. freeze and verify the launcher identity as the sole baseline record;
3. publish all common records;
4. publish exactly the selected branch index;
5. require the actual names equal `expected_before_manifest(branch)`;
6. create the terminal manifest in memory with
   `exact_final_filenames == expected_final_names(branch)`;
7. require the manifest contains the exact launcher identity and baseline
   tuple;
8. publish the terminal manifest once;
9. require actual names equal `expected_final_names(branch)`;
10. independently reload every direct child, require regular non-symlink
    nlink-1 mode-0400 identity, then close the audit root to mode `0500`;
11. fsync audit and control parents and report post-close root identity.

The records index must describe only newly published non-index records and
must explicitly bind the immutable baseline launcher separately. It must
not claim to contain itself or the terminal manifest. The terminal manifest
must not claim its own hash/stat or a post-close timestamp.

## 5. Mandatory Pre-Child Closure Fixtures

Before the one real audit child may start, pure in-memory zero-science
fixtures must exercise both success and failure branches:

- exact success baseline/common/index/manifest set accepted;
- exact failure baseline/common/index/manifest set accepted;
- missing launcher rejected;
- launcher duplicated rejected;
- wrong launcher name/hash/path rejected;
- missing common record rejected;
- extra unexpected file rejected;
- success/failure index cross-use rejected;
- success/failure manifest cross-use rejected;
- index self-inclusion rejected;
- terminal-manifest inclusion in the index rejected;
- terminal self-hash/stat/post-close-timestamp claims rejected;
- pre-manifest actual-set mismatch rejected;
- final actual-set mismatch rejected;
- raw substring/count-only validation rejected;
- set-only comparison without duplicate detection rejected.

Static AST/dataflow review must prove the live closure path calls the same
pure functions used by these fixtures. Reimplementing the terminal formula
after fixtures is forbidden.

## 6. Preserved T4an Contracts

The new helper/launcher must preserve, without weakening:

- direct full exact root and executable `ast.Constant` assignments;
- no root inference, `Path.parents`, aliases, shell evaluation, stdin
  scripts, heredocs, `python -c`, destructive surfaces, or agents;
- dedicated v10 raw-index serializer with explicit
  `ensure_ascii=False`;
- separate helper canonical stdout/replay serializer using omitted/default
  `ensure_ascii=True`;
- the exact non-ASCII discriminator and all v10 positive/negative cases;
- exact v10 list type, length `1041`, record schema, path order, current
  index, capture count/index, test count, runtime occurrences, complete-290
  index, and science counts;
- structured PID/PPID/PGID/SID/state/command ancestry and token-aware
  classifier with variable PIDs excluded from canonical payload;
- immutable file-based launcher, one child, raw stdout/stderr,
  return/signal/wait/reap/PG-empty, complete pre/post inventories, and
  execution-root absence;
- mutually exclusive success/failure terminal branches;
- exact driver, runner, runtime, complete-290, consumed-witness, canonical,
  later-unit absence, external-object, link, bytecode, quarantine, and
  transient guards.

## 7. One-Shot Phase A0

After root-T0 accepts an independent T7 review, T4 may choose one fresh
pairwise-distinct helper root, audit root, and reserved absent execution
root. It creates only helper/audit roots, freezes one helper and one
launcher, completes static review and all zero-science fixtures, then
launches at most one `--first-attempt` audit-only child.

Any pre-child static or fixture failure freezes the fresh roots and stops
without child launch. Any child or post-child failure closes the appropriate
durable evidence if possible, consumes the authorization, and stops.
No retry, second roots, alternate helper, replay, execute, driver edit,
preflight, scientific runner, official audit, solver, witness, or matrix.

Only complete PASS returns:

```text
CHECKPOINT / T4AO TERMINAL FILENAME-SET AUDIT HELPER FROZEN
```

Root T0 must then independently audit all source/records and run one
identical frozen-file no-write replay before any separate execute authority.

## 8. Downstream Boundary

T4ao does not authorize preservation execute or resumption of T4ai. A
separate root-T0 decision after checkpoint/replay PASS may authorize one
digest-bound preservation execute and the already-reviewed T4ai Phase A.
Only a later T4ai checkpoint PASS may authorize a new full one-shot
existing-`kM=1.58125` producer plus matching official audit. The old
successful pair remains non-reusable.

Matrix order remains:

```text
2.91875 -> 3.759375 -> 3.89375 -> full 241x241
```

T7ch, new frequencies, production, plots, fixtures, Kirchhoff, paper work,
GitHub, standard relaxation, and all downstream claims remain forbidden.
