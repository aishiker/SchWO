# Formal T4 prompt — V3.1-U final bounded repair cycle 2

This prompt is inactive until Root T0 supplies a formal T7 package-review
archive containing the exact label:

```text
ACCEPT GREEN / V3.1-U REPAIR CYCLE 2 PACKAGE READY FOR T4
```

Work only in the existing formal T4 task
`019f5fa6-1288-7c01-8a87-4c4370cf5517` and repository
`/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO`.

## Read and rehash first

Read completely: `project.md`; current state header; T0/T4/T7 handoffs;
review-gate liveness protocol/template; V3 master and V3.0 authorities; the
V3.1-U replacement package/design/prompts; repair-cycle-1 package, reviews,
implementation authorities and both failed roots; formal terminal review
`7552b2...25c1`; the repair-cycle-2 package/design/prompts; the stable external
snapshot authority; and the formal package review supplied by T0.

Rehash every named authority, failed root, source snapshot, frozen CLI,
domain/threshold/convention source and protected radial file before editing.
Stop without edits on any mismatch.

## Exact allowed delta

Change exactly these six paths and no others:

```text
scripts/phase6_v3_1_bhpt_mst_cycle2.wls
src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py
src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
tests/unit/test_phase6_v3_cycle2.py
tests/unit/test_phase6_v3_hp_unitarity.py
tests/regression/test_phase6_v3_hp_unitarity_publication.py
```

Preserve the CLI SHA `01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4`,
Route-U oracle, seven protected radial files, V3.0 authorities, exact graph,
16 thresholds, five certificates, anchor set/order, MST/90/45/45, and all
evidence roots.

## Implement the frozen repair

Implement exactly the design's canonical Route-C terminal protocol:

- one exact 23-anchor WLS batch; each anchor called at most once;
- one PASS or ERROR record for every ordinal/key before exit;
- no early `Throw` that discards the failure key;
- raw stdout/stderr, child payload, one wait/reap receipt, exit/signal/timeout,
  source start/end, attempt records and terminal envelope on every branch;
- success only for 23 ordered PASS records, exit0 and empty stderr;
- failure artifacts identify the exact first failed ordinal/key/error and are
  non-resumable/non-retryable;
- no error record may contain a scientific amplitude and no success record
  may contain an error.

Use only the stable 25-file external snapshot bound by the package.  Add a
shared exact source identity builder and fail-closed validation for WLS,
WolframKernel, audit archive/snapshot, 25 files, inherited commit association,
and WLS-loaded source paths.  Preserve the explicit nonclaim that the restored
snapshot has no `.git` directory and inherits its commit association from the
immutable historical ledger plus exact byte equality.

Implement the non-circular two-stage authority chain.  Add a fixed-path
one-use sentinel dispatch and fresh-root validator, a terminal sentinel entry,
and a separate later official dispatch that requires a formal sentinel
review.  Neither dispatch SHA is hardcoded before publication.  No
live-handoff, boolean, alternate hash or fallback authority is allowed.  The
official path must reject any attempt to copy sentinel science and must
recompute all A/U/B/C science.

The only sentinel launch surface is exactly:

```text
executable=/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14
argv=[executable,-m,schwgw.validation.phase6_v3_mode_greybody_hp_replacement,route-c-sentinel]
cwd=/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO
environment_allowlist={PYTHONDONTWRITEBYTECODE=1,PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src}
```

Implement `python -m schwgw.validation.phase6_v3_mode_greybody_hp_replacement
route-c-sentinel` as the module's sole sentinel operation.  It accepts no root
or other argument and rejects every extra token.  It must read the exact root
only from the fixed O_EXCL sentinel dispatch, validate/consume that dispatch,
and then call the internal `run_route_c_sentinel(root)`.  The formal
implementation review and sentinel dispatch must bind the complete invocation
object.  Explicitly reject `python -c`, direct-import expressions, alternate
modules, root/review/source argv, cwd drift, extra environment variables,
environment-selected authority and fallback paths.  Do not change or use the
project CLI as a sentinel entry.

## Mandatory zero-science verification

Run the frozen focused command:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pytest -q -p no:cacheprovider tests/unit/test_phase6_v3_cycle2.py tests/unit/test_phase6_v3_hp_unitarity.py tests/regression/test_phase6_v3_hp_unitarity_publication.py
```

Also run Ruff check/format on the five Python paths, in-memory CPython 3.14
compile, exact six-path diff-check, unchanged CLI preflight, and independent
start/end rehashes.  Tests must cover all success/failure, order/cardinality,
process, source, authority, collision, one-use, terminal grammar and
sentinel-to-official non-reuse adversaries frozen by the package.

Add direct invocation-grammar tests for the exact four-token argv and exact
cwd/environment allowlist, plus negatives for `-c`, direct import, alternate
module, missing/wrong operation, every extra token, caller-supplied root,
cwd drift, extra environment and fallback authority.

The entire implementation/preflight turn must report exactly zero radial,
AP, BHPT, Wolfram, sentinel and science calls.  Temporary synthetic evidence
may exist only below a fresh temporary directory.

Do not run the real sentinel, create/consume a dispatch, create an official
root, edit status/handoffs/package/prompts, or start V3.2.

Return exact before/after hashes, test counts, source snapshot validation,
synthetic artifact inventory, zero-call counters, commands and limitations.
If all gates pass, end with:

```text
CHECKPOINT / V3.1-U REPAIR CYCLE 2 IMPLEMENTATION READY FOR T7 DELTA REVIEW
```

This is implementation readiness only; V3.1-U science remains `FAIL` and no
sentinel, official execution, V3.2 or global GREEN is authorized.
