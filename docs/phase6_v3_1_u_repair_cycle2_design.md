# Phase 6 V3.1-U final bounded repair cycle 2 design

Date frozen by Root T0: 2026-08-13

Scientific gate: `phase6_v3_1_hp_unitarity_deficit_replacement_v1`

Repair identity: `phase6_v3_1_u_route_c_totality_repair_cycle2_v1`

This is bounded scientific repair 2 of 2 for the distinct V3.1-U replacement
gate.  It is not a retry or resume of either failed science root, and it is
not V3.2.  It changes no frozen domain, anchor, method, precision, threshold,
formula, convention, Route-A/U/B result, or protected radial implementation.

## 1. Frozen verdict and liveness state

The formal terminal verdict is:

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-U CHANGES REQUIRED
```

It is recorded in
`docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle1_terminal_scientific_review.md`,
SHA-256 `7552b2dbc19269be0eb11b61ae8eb04c55a1225d10db1962d881e0f6ac7925c1`.

The sole class-A blocker is
`v31u_route_c_external_totality_and_provenance`.  The repair-1 candidate
completed Route A (`496/9920`), Route U (`318/954`, all ladders PASS), and
Route B (`102/458`), then its external Route-C child returned exit `70` before
publishing any of the exact 23 records.  The immutable root does not identify
the failed anchor or bind the executed WLS, WolframKernel, and BHPT source at
both ends.  The specific lower-level cause is therefore `UNKNOWN`.

Completed bounded scientific repairs are `1`.  This package freezes the
last permitted bounded repair.  Package review and zero-science
implementation review do not consume it.  The one-shot 23-anchor sentinel
does consume it once dispatched, whether it passes or fails.  A failed
sentinel requires `ESCALATE / T0 ADJUDICATION REQUIRED`; there is no retry or
repair cycle 3.

## 2. Immutable failed evidence and no-reuse rule

The repair-1 failed root is:

```text
runs/phase6/classic_scattering/v3_1_hp_unitarity_deficit_repair1_v1_20260812T064653Z_py314
failure.json          e3874e7565dc35498513af8112577810dd9059035f43a9d4573d633c2ae752aa
failure_manifest.json f977a0d555652d028b3b73d18990b902f37a55c3dd9305c6e6da55f66593050d
records.jsonl         04b18189f4baf47ad4ebd94b761635cec5d9eb9c1b591ac0b9e694ddf1e3dea2
ladder_records.jsonl  a8cb91d0fd9374003ad63fa2a6ddd2c57fa3bf4f287c5f44aa287878746e7f7c
route_u_records.jsonl 99fc2dd34ebcd029a86b22c0dd04a20ba2423711b0879c481e39d597bc5489d9
route_u_ladders.jsonl 38b377f61e9da1cd1dfe4aebb68642ed6e00ab25a434ffa4556878f5118da2c4
ap_records.jsonl      3de519e8e9e55be8f4908a6715f5730f2f039bb5eed76b90acac8aa004e6b527
external request      6094323a056d7e1396affccd87ef15851612ac404ab84d29b7cbae7c7415bf82
```

The original V3.1-U failed root remains forbidden as well.  Both roots and
all partial records are immutable diagnostic evidence only.  They may supply
authenticated identities and already reviewed passed-item evidence, but no
science record, checkpoint, cache, amplitude, route output, or manifest byte
may populate the sentinel or a future official candidate.

The sentinel must compute Route C afresh.  A future official candidate must
compute Route A, U, B, and C afresh and record
`predecessor_science_reused=false` and `sentinel_science_reused=false`.

## 3. Exact six-file implementation boundary

Formal T4 may modify exactly these six paths:

```text
scripts/phase6_v3_1_bhpt_mst_cycle2.wls
src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py
src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
tests/unit/test_phase6_v3_cycle2.py
tests/unit/test_phase6_v3_hp_unitarity.py
tests/regression/test_phase6_v3_hp_unitarity_publication.py
```

Their package-start hashes are frozen in the package.  The unchanged CLI
`scripts/phase6_v3_1_hp_unitarity.py` remains SHA-256
`01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4`.
No seventh implementation or test path is permitted.

All V3.0 authorities, 16 threshold bytes, five certificate IDs, exact graph,
Route-U selector and precision schedule, Route-U oracle, seven protected
radial files, status/handoffs, Li figures, and finite-radius observer paths
are frozen.

## 4. Stable external source snapshot

The historical `/private/tmp/SchWO_ReggeWheeler_phase6_v1_20260808` checkout
was a volatile runtime path and was cleared by the operating system after the
repair-1 terminal.  It is forbidden as a future source.

Root T0 restored the same 25 source-file bytes offline from the immutable
third-audit archive into:

```text
runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813/source
```

The snapshot authority is:

```text
runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json
```

It binds the audit ZIP SHA-256 `715e27a45b15ec2ab78f92c77506de4317f5a26af79bb665de5a16d30557d162`,
the embedded `SHA256SUMS.txt`, all 25 relative path/hash/size records, the
historical immutable source ledger, and the historical clean commit assertion
`2e01209271fb3d0d92705d5c27bd9e00a6140981`.  Every restored file is
regular, direct, `0444`, nlink1; every source directory is `0555`.

The snapshot contains no `.git` directory and does not independently prove a
commit.  Its commit association is valid only through the exact 25-file byte
equality to the immutable historical ledger, which recorded that commit and
clean status, plus the audit ZIP identity.  The implementation must preserve
this distinction.  It may not claim a new checkout, synthesize git metadata,
use another local probe, or fetch a replacement from the network.

## 5. Canonical Route-C terminal protocol

The Python external runner and WLS must publish a complete process/evidence
chain on every terminal branch.  The exact artifact names may be namespaced
under a sentinel or official root, but must include:

```text
external_request.json
external_source_start.json
external_prelaunch.json
external_stdout.raw
external_stderr.raw
external_receipt.json
external_child_payload.raw.json
external_attempt_records.jsonl
external_source_end.json
external_terminal.json
```

On success it additionally publishes exactly 23 ordered scientific records
as `external_records.jsonl` and a success result.  On failure it publishes a
failure record and failure manifest; success result/manifest are forbidden.

The request freezes the exact 23 ordered anchors and exactly:

```text
Method = MST
WorkingPrecision = 90
PrecisionGoal = 45
AccuracyGoal = 45
Potential = ReggeWheeler
BoundaryConditions = In
odd Regge-Wheeler independent external route
```

The WLS must execute each anchor at most once.  It must return one canonical
PASS or ERROR record for every requested ordinal/key and write its terminal
envelope before exit.  `Throw` or another early exit that loses the key is
forbidden.  An error record contains no scientific amplitude.  The batch may
continue after an anchor error only to make the complete 23-record diagnostic
inventory durable; any error makes the batch fail with exit `70`.

The parent must persist raw stdout and stderr, one exact wait/reap receipt,
return code/signal/timeout state, output identities, elapsed time, and the
first failing ordinal/key/error.  Missing, torn, noncanonical, reordered,
duplicate, extra, or mixed success/error data fail closed.

## 6. Start/end provenance closure

One shared external-source identity builder must be used by both sentinel and
official execution.  At start and end it binds:

- the repaired WLS absolute path, SHA-256, size, mode and nlink;
- the external runner and producer identities;
- the fixed WolframKernel absolute path, SHA-256
  `70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c`,
  size, mode and nlink;
- the snapshot authority and audit ZIP identities;
- the exact 25 restored relative path/hash/size/mode/nlink records;
- the inherited historical commit/clean assertion with its nonclaim;
- the WLS-observed `$Version`, `$SystemID`, loaded package path, and loaded
  `ReggeWheeler` numerical-source paths, all inside the authenticated snapshot.

Failure branches must also attempt and persist source-end.  Start/end drift,
missing/extra source files, symlink/hardlink, loaded path escape, kernel drift,
or audit/snapshot mismatch makes the terminal fail.

## 7. Non-circular two-stage authority graph

The only authority graph is:

```text
repair-2 package
  -> formal T7 package review
  -> formal T4 six-file zero-science implementation
  -> formal T7 implementation delta review
  -> one-use Root-T0 sentinel dispatch
  -> one terminal 23-anchor sentinel root
  -> formal T7 sentinel review
  -> separate one-use Root-T0 official dispatch
  -> fresh official A/U/B/C root
  -> formal T7 terminal scientific review
```

Implementation may freeze the unique future archive/dispatch paths and exact
required verdict tokens, but not a not-yet-created review SHA.  Each T0
dispatch supplies and binds the one exact review SHA at its fixed path.
Mutable live handoffs, environment/argv-selected authority, alternate hashes,
fallback paths, booleans, or predecessor YELLOW reviews are forbidden.

The unchanged CLI has no Route-C sentinel command.  The only sentinel entry is
the following exact invocation object; it is part of the package authority:

```text
executable=/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14
argv=[
  /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14,
  -m,
  schwgw.validation.phase6_v3_mode_greybody_hp_replacement,
  route-c-sentinel
]
cwd=/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO
environment_allowlist={
  PYTHONDONTWRITEBYTECODE=1,
  PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src
}
```

No fifth argv token is permitted.  In particular there is no root, review,
dispatch, source, WLS, kernel, method, precision, or authority argument.  The
module token `route-c-sentinel` selects only the frozen operation.  The module
must read the single fixed sentinel-dispatch path internally, parse its
canonical `exact_root`, validate that root and all authorities, durably
consume the dispatch, and only then launch the child.

`python -c`, a direct-import expression, another `-m` module, extra argv,
caller-supplied root, current-working-directory drift, extra environment
variables, environment-selected authority, and any fallback path are
forbidden.  The sentinel dispatch and formal implementation review must bind
this complete invocation object byte-for-byte.  The unchanged project CLI is
not an alternate sentinel entry.

## 8. One-use sentinel

The sentinel root namespace is exactly:

```text
runs/phase6/classic_scattering/v3_1_u_route_c_sentinel_repair2_v1_<UTC-Z>_py314
```

The fixed sentinel dispatch is O_EXCL, canonical JSON, regular `0444`, nlink1
and binds the package, package review, implementation review, six repaired
hashes, exact fresh root, exact 23 anchors, method/precision, snapshot,
WolframKernel, source/protected identities, `single_use=true`, and the exact
verdict tokens.  It is durably consumed before the child launch.

The sentinel performs one Wolfram child launch containing 23 MST calls.  No
anchor retry, drop, reorder, alternate method, precision change, result
selection, or second child is permitted.  Any post-dispatch failure,
interruption, timeout, signal, torn output, or source drift terminalizes the
root and consumes the sentinel.  It is non-resumable and non-retryable.

Only `23 PASS / exit 0 / empty stderr / exact order / start=end provenance`
is sentinel PASS.  Formal T7 must review that immutable root.  Sentinel PASS
does not accept V3.1-U and its records are forbidden as official inputs.

## 9. Official execution after sentinel review

Only a formal sentinel verdict with exact bounded label

```text
ACCEPT GREEN / V3.1-U ROUTE-C SENTINEL SUFFICIENT FOR ONE-USE OFFICIAL DISPATCH
```

permits Root T0 to publish the separate official dispatch.  The official
root namespace is exactly:

```text
runs/phase6/classic_scattering/v3_1_hp_unitarity_deficit_repair2_v1_<UTC-Z>_py314
```

The official dispatch binds the sentinel dispatch/consumption/result/manifest
and formal review, but the official candidate recomputes Route C and all other
routes.  A terminal official failure after this final repair is adjudicated
under the loop limit; it cannot trigger repair cycle 3.

## 10. T4 implementation stop boundary

After package approval, T4 may implement only the six-file delta and run the
three frozen focused test files under exact CPython 3.14 plus the mpmath
overlay, Ruff check/format, in-memory compile, six-path diff-check, synthetic
success/failure publication, source/adversarial fixtures, and the unchanged
CLI preflight.  It must prove zero radial/AP/BHPT/Wolfram/science calls.

T4 must not create a sentinel or official dispatch/root, launch
WolframKernel, edit status/handoffs, or start V3.2 in the implementation turn.
Formal T7 then performs an incremental implementation review.  Root T0 alone
may subsequently create the one-use sentinel dispatch.

## 11. Nonclaims

- V3.1-U remains `FAIL` until a fresh official candidate passes formal T7.
- The sentinel assesses only the exact 23-anchor Route-C prerequisite.
- Route A/U/B from failed roots are not accepted or reusable science.
- Full-domain V3, Li-figure equivalence, common absolute phase closure, and
  finite-radius observer claims remain out of scope.
- V3.2 is forbidden before formal V3.1-U `ADVANCE`.
- No project-wide or global GREEN is permitted.
