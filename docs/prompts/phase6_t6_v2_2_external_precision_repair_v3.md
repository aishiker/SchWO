# Phase 6 T6 V2.2 v3 — bounded external-wp60 precision repair

You are the existing formal SchWO T6 task. Perform exactly the first bounded
repair of the formal T7 V2.2 v2 science-gate finding
`v22_external_wp60_precision_scope`. Do not dispatch T7 and do not start V2.3.

This prompt supersedes the execution role of
`docs/prompts/phase6_t6_v2_2_waveform_routes_v2.md` only for this repair. The
v2 prompt, implementation history, and immutable v2 evidence root remain
preserved. Do not reinterpret or overwrite them.

## Frozen review state

Require the exact initial T7 verdict:

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: PARTIAL
GATE_LABEL: REVIEW YELLOW / V2.2 CHANGES REQUIRED
```

Read `docs/handoffs/T7_current.md` and bind this repair to its exact
`incremental_review_state`, blocker fields, protected identities, and unblock
condition. This is repair cycle 1 under
`docs/review_gate_liveness_protocol.md`.

The sole class-A blocker is:

```text
blocker_id: v22_external_wp60_precision_scope
violated item: original-immutable-input reconstruction and truthful separate
               numerical arithmetic-precision provenance
expected: all 120 external S_l values, Route-C coefficients, and comparators
          are parsed/evaluated from the original wp60 decimal strings inside
          mp.workdps(80)
observed: all 120 external S_l values were parsed first at default mp.dps=15,
          then promoted and labeled precision_dps=80
bounded repair: move/delay external phase_factor conversion into the frozen
                80-dps context; add source-anchored default-dps regression;
                publish one fresh immutable v3 root
```

Preserve the v2 root byte-for-byte:

```text
runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v2_20260811T104500_py314
7b1fd01983dc03e8c3c027b74e3d01aac2962a129614248d6a2e96284cf5093f  manifest.json
9ae79a006fdbd9f86a385b085bc1cb4d9fcdea52b2debccf7a0b16bfb970ec74  records.jsonl
6e9ce7cfb18390e21fbe5385d57ff77acfc3aed7929c294c54cee7b9b1ea5a0a  report.json
18ca221fa2b221bffdc22cd1bcb4f24b91485dce70817ae8003b4b50e81de66d  source_ledger.json
76e289f748490b77a6266d7ae6723f7e6f4498cc9660a2a78d402aea31b3966e  summary.json
```

At start and end require exact matches for the frozen convention contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
selected domain
`9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
D_union plan
`de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`,
threshold contract
`8c2ab9ca254df9c15e3947479bb0af3bb6204f37d326b52c16a0984604ae005e`,
threshold rationale
`c96a0c640ffb2789c34e8e9ff364d42cc6cfe427b374a7cff1299d196b3c91b6`,
threshold test
`71918930e4b1384ab66adaf5e7d89bc55c31c30f156fa6f153332542759c611a`,
and the seven protected radial source hashes recorded in the current T7
handoff. Any drift is a protocol HOLD, not permission to repair it.

## Required bounded repair

1. Ensure the original external `__wp60.json` `phase_factor` decimal strings
   are retained without numeric conversion until inside
   `mp.workdps(WORKING_DPS)`, or enter that context before conversion.
2. Ensure publication validation independently reloads the original immutable
   external wp60 source nodes and reconstructs all 120 external inputs,
   Route-C amplitudes, and comparator values at 80 dps. It must not validate
   precision by parsing only the already-published `external_S_l` field.
3. Add a regression that deliberately starts with `mp.dps=15`, loads the
   original 40-digit wp60 strings, and proves 120/120 published external
   inputs and derived Route-C coefficients match the direct 80-dps
   source-anchored reconstruction. The old v2 root should fail this new
   precision-provenance check or otherwise be explicitly recognized as the
   superseded defective predecessor; the new v3 root must pass.
4. Preserve all nine `passed_items` frozen in the T7 handoff. In particular:
   exact 15 parity pairs / 30 radial keys / 120 records; Route A and Route B
   bytes and algebra; odd direct RW / independently solved even Zerilli
   provenance; fixed scale and no fit; all 1440 frozen comparator gates;
   signal floor; no radial solve/frame/angular/total-plane-wave/Li expansion;
   separate uncertainty budgets; root immutability and canonical manifests.
5. Do not change any formula, convention, domain, threshold, input identity,
   radial backend, Route-B implementation, scientific acceptance semantics,
   or scope. `absolute_phase=PARTIAL`, full-domain V2 `NOT_ASSESSED`,
   full-domain V1 independent certification `PARTIAL`, `global_status=null`,
   and no-global-GREEN remain mandatory.

Only these implementation/review-owned paths may change in the bounded
repair:

```text
src/schwgw/validation/phase6_v2_waveform_routes.py
tests/unit/test_phase6_v2_2_waveform_routes.py
tests/regression/test_phase6_v2_2_waveform_publication.py
status.md
docs/handoffs/T6_current.md
runs/phase6/asymptotic_waveform/<one-fresh-v2_2-waveform-routes-v3-root>/*
```

Do not edit this prompt, T7 handoff, threshold package, V2.0/V2.1 files,
publisher CLI, scattering formulas, protected radial files, or the v2 root.

## Verification and publication

Use exact CPython 3.14 with the mpmath 1.4.1 overlay first. Before publication,
run the exact T7 recheck command:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/bin/python3.14 -m pytest -q -p no:cacheprovider tests/unit/test_phase6_v2_2_threshold_contract.py tests/unit/test_phase6_v2_2_waveform_routes.py tests/regression/test_phase6_v2_2_waveform_publication.py
```

Also run all Phase-6/V2 tests, full pytest, focused Ruff format/check,
compileall, scoped `git diff --check`, fresh-root collision/process checks,
old-v2-root identity checks, independent source-string reconstruction, and
start/end protected hashes. Record preexisting unrelated failures separately
without modifying them.

Publish exactly once to a fresh immutable root named
`runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v3_<timestamp>_py314`.
Independently reload it after sealing. Mark the v2 root as immutable
superseded evidence and forbidden as V2.2 authority; never overwrite it.

The unblock condition is exact: from an independent process beginning at
default `mp.dps=15`, the fresh root has 120/120 `external_S_l` values and
Route-C coefficients exactly reconstructed from the original wp60 decimal
strings at 80 dps; all candidate comparators exactly match the source-anchored
reconstruction and pass frozen thresholds; the old root remains unchanged;
and every frozen passed invariant/protected identity remains exact.

On terminal publication return only:

```text
CHECKPOINT / V2.2 EXTERNAL WP60 PRECISION REPAIR V3 FROZEN
```

Do not dispatch T7 and do not start V2.3.
