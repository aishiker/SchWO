# Phase 6 T6 — bounded V2.3 summary precision-provenance repair

You are the existing formal SchWO T6 task.  Perform one bounded control-plane
repair of the terminal V2.3 root.  Do not dispatch T7 or V2.4, modify science
formulae/thresholds/inputs, or call a radial solver.

## Frozen predecessor and exact defect

Require the predecessor checkpoint:

```text
CHECKPOINT / V2.3 SELECTED-DOMAIN FLUX CLOSURE EVIDENCE V2 FROZEN
```

The immutable predecessor root is:

```text
runs/phase6/asymptotic_waveform/v2_3_flux_closure_v1_20260811T044845_py314
```

with exact identities:

```text
1371e85d80f97c5b3152a5103c3a7bda64a8e0094052cf2e8d3cd8e35d1ceb2b  manifest.json
ba8617224c89c7122e27d0399dafc510d126dd2b4cfd0ca2d8f741ae2a454d39  records.jsonl
d76ed626701f7d40c890a95ee30b32f77ca8314213d36bc6278b9993848afcad  report.json
930e68580dd6d7594349af673b6b436118b34657e2bdad84e551c6c25e69f7ee  source_ledger.json
2b6d334d586b12565a1800ef4edeeea046c2e0151f52bad5adf6ad04447db45e  summary.json
```

Root T0 independently ran the native original-path and temporary-copy reloads,
then recomputed all 120 record-level extrema at 100 dps.  The records are
correct and all frozen acceptance checks pass.  The defect is restricted to
`_summary()` in `src/schwgw/validation/phase6_v2_flux_closure.py`: after
`build_v2_3_flux_closure_records()` exits `mp.workdps(100)`, `_extrema()`
reparses the 100-digit record strings at ambient `mp.dps=15`, then serializes
that quantized value with `precision_digits=100`.

Exact evidence includes:

```text
minimum external horizon fraction
record:  9.373615409990476292528436114160436756813021669668934587236550056169801667903105e-1498
summary: 9.373615409990476240606543253796878289661300356491515003892678180379002016777380090956134044420557438e-1498

maximum SchWO balance residual
record:  2.456693814984740735626905876280748921163992416622833176415819278372141073001165780195065440402033493e-10
summary: 2.45669381498474095621094649810720218774395817717959289439022541046142578125e-10
```

The same ambient-precision quantization affects all stored summary extrema.
It is a `CONTROL_PLANE_REPAIR`: the discrepancies are about `1e-16` relative,
do not affect any threshold, predicate, record, selected-domain conclusion or
nonclaim, but the stated precision provenance is false and must be repaired
before final T7 review.

## Bounded repair

Allowed files:

- `src/schwgw/validation/phase6_v2_flux_closure.py`;
- `tests/unit/test_phase6_v2_3_flux_closure.py`;
- `tests/regression/test_phase6_v2_3_flux_publication.py` only if necessary;
- V2.3 evidence doc, `status.md`, T6 handoff/archive;
- one fresh immutable V2.3-v2 root.

Repair only the summary/extrema precision context.  All mandatory summary
extrema must be parsed, compared and serialized inside explicit
`mp.workdps(WORKING_DPS)`, independent of ambient `mp.dps`.  Do not change a
formula, threshold, comparator, source identity, record construction,
uncertainty vocabulary or claim ceiling.

Add a regression that begins with ambient `mp.dps=15`, builds the 120 records,
constructs summary/report, and proves every stored summary minimum/maximum is
the exact 100-dps extrema of the canonical record strings.  Prove ambient
precision is restored on exit.  Include at least the minimum external horizon
fraction and both SchWO/external balance extrema.  The test must fail on the
predecessor implementation semantics.

Run focused V2.3 tests and all Phase-6/V2 tests with the exact CPython 3.14
overlay-first runtime, plus Ruff format/check, compileall and repository
`git diff --check`.  The already completed full-suite result remains valid;
this bounded metadata repair does not require another full-suite run.

Before publication, rebuild in memory and require:

- all 120 records and all frozen numeric/predicate checks still PASS;
- `radial_solve_count=0`;
- predecessor protected/frozen identities remain exact;
- ambient-dps 15 and 100 produce byte-identical corrected summary/report
  scientific content;
- predecessor `records.jsonl` and candidate `records.jsonl` are byte-identical;
- no V2.3/radial/Li/Wolfram process or target collision exists.

Publish exactly once to a fresh root named

```text
runs/phase6/asymptotic_waveform/v2_3_flux_closure_v2_<timestamp>_py314
```

using the existing immutable protocol.  Reload it in place and from a distinct
temporary path.  Confirm the corrected summary extrema equal record extrema at
100 dps even when reload starts at ambient `mp.dps=15`.  Preserve the v1 root
byte-for-byte, mark it immutable superseded evidence, and forbid it as current
V2.3 authority.

Forbidden changes: V2.3 threshold/rationale/prompts/T7 handoff, V2.0/V2.1/
V2.2/V1/external artifacts, frozen conventions/domain, radial/numerical code,
backgrounds/potentials/RWZ, finite observer/tetrad, angular/incident, V2.4,
Li/paper outputs and every scientific threshold or formula.  Do not run a
radial solve, angular sum, paper figure or Li figure.

On verified success return only:

```text
CHECKPOINT / V2.3 SUMMARY PRECISION-PROVENANCE REPAIR V2 FROZEN
```
