# Phase 6 T7 V2.2 v3 — repair-cycle-1 precision delta review

You are the existing formal SchWO T7 task. Perform only delta review 1 for
the frozen V2.2 gate under `docs/review_gate_liveness_protocol.md`. Do not
repeat the full initial science review, modify science/artifact bytes, dispatch
T6, or start V2.3.

## 1. Review identity and exact scope

Bind this review to the initial verdict already recorded at the top of the
pre-delta `docs/handoffs/T7_current.md`, whose start identity must be:

```text
91a0c06ba4e23c77b221c5d67f0202c0664ab9e07e75f506337de272d7d0a4ee
```

The frozen initial verdict is:

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: PARTIAL
GATE_LABEL: REVIEW YELLOW / V2.2 CHANGES REQUIRED
```

Review only the failed item
`v22v2_external_wp60_precision_provenance` and blocker
`v22_external_wp60_precision_scope`; check whether repair cycle 1 damaged the
nine already-passed invariants; and rehash protected identities. Do not reopen
an unrelated passed item without exact evidence that the bounded repair
changed its bytes, dependency, or invariant.

The repair prompt is:

```text
docs/prompts/phase6_t6_v2_2_external_precision_repair_v3.md
8e1c589ff7381b89d76f23e242d2497c2bab73ffcf7823fd998799a3d3cd97a4
```

The formal T6 terminal checkpoint is:

```text
CHECKPOINT / V2.2 EXTERNAL WP60 PRECISION REPAIR V3 FROZEN
```

Require the pre-review T6 handoff identity
`43d9e5e8c43658b36e53819fe0da11e2f36124482deed086db5c017330bf34dd`.

## 2. Candidate and predecessor identities

Review exactly this fresh immutable candidate root:

```text
runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v3_20260811T113135_py314
3981aeb5424cbac4e7774fc84b5f03d5764561ea21a7338a60f19bf5f0d46660  manifest.json
2f7b466036d1481766794aa13581dd9824c851a7e405117f94e192d849f526c9  records.jsonl
fc66bb1a66f10257b80827ee292d180b0582587c3291332471971731dc352f9b  report.json
9fdbd6302fdc0eea93cc1ced1db76f2355343b3538dfee35f5145ac8e5b518a1  source_ledger.json
fdd314e760c4fa71c555f9eadb13eeb8389d0b24c0f6e8822eb1005afc9b8b19  summary.json
```

Require root `0555`, exactly five direct regular files, each `0444`/nlink1,
canonical serialization, exact manifest membership, no symlink/staging/lock/
partial/transient, and no concurrent V2.2 writer.

The superseded v2 predecessor must remain byte-for-byte unchanged and is
forbidden as current authority:

```text
runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v2_20260811T104500_py314
7b1fd01983dc03e8c3c027b74e3d01aac2962a129614248d6a2e96284cf5093f  manifest.json
9ae79a006fdbd9f86a385b085bc1cb4d9fcdea52b2debccf7a0b16bfb970ec74  records.jsonl
6e9ce7cfb18390e21fbe5385d57ff77acfc3aed7929c294c54cee7b9b1ea5a0a  report.json
18ca221fa2b221bffdc22cd1bcb4f24b91485dce70817ae8003b4b50e81de66d  source_ledger.json
76e289f748490b77a6266d7ae6723f7e6f4498cc9660a2a78d402aea31b3966e  summary.json
```

Repair-owned source identities are:

```text
2e996d5070f6db370523dbd3c9f620a6b2dcca6c9d37c79c9c9ed2b8860b4fe4  src/schwgw/validation/phase6_v2_waveform_routes.py
da88978565b7587e421f8692fe993a046a1246659caa8e7e41fd31e5978dde27  tests/unit/test_phase6_v2_2_waveform_routes.py
a5a7f1879b1d153d31c2a5c6d765d28c4002512bf11e94fca9893a31d88c77d6  tests/regression/test_phase6_v2_2_waveform_publication.py
```

The Route-B science implementation and publisher were not repair-owned and
must remain:

```text
d7a8ca0c711ec5082145556116447f045e73c453b40fa480ec647d178637b515  src/schwgw/scattering/phase6_v2_2_waveform_routes.py
879925a6ea428ba0ccf4e2acadae3a87648ab9b9613771b4af6923b7a803fb47  scripts/phase6_v2_2_publish_waveform_routes.py
```

## 3. Exact failed-item recheck

Start a fresh CPython 3.14 process with the mpmath 1.4.1 overlay first and
explicit ambient `mp.dps=15`. Independently reopen all original immutable
external `__wp60.json` nodes. For every one of the 120 records:

1. parse the original `phase_factor.real/imag` decimal strings only inside
   `mp.workdps(80)`;
2. require exact equality with published `route_inputs.external_S_l` and its
   stored original decimal mapping;
3. reconstruct Route C from the source `S_l`, frozen V2.1 `c_lm`, sector,
   `omega`, and `ell`, and require exact equality with the published Route-C
   coefficient;
4. independently reconstruct A/C and B/C, as well as A/B, comparators from
   source amplitudes and the frozen fixed scale; require exact equality with
   all candidate comparator fields and all frozen threshold outcomes;
5. confirm ambient precision returns to 15 after reload.

Binary unblock requires exactly 120/120 external inputs, 120/120 Route-C
coefficients and 360/360 route-pair records source-anchored at 80 dps, with
all 1440 comparator gates and every signal floor passing. A self-referential
reload based only on candidate `external_S_l` is not evidence.

## 4. Passed invariants and protected identities

Recheck, without reopening their full science derivation, the nine frozen
passed items from the initial review:

```text
v22v2_identity_and_immutability
v22v2_inventory_and_serialization
v22v2_route_a_and_b_algebra
v22v2_external_provenance
v22v2_threshold_outcome_from_exact_sources
v22v2_signal_floor_no_fit_scope
v22v2_route_b_not_final_output_copy
v22v2_tests_and_quality
v22v2_process_and_transient_isolation
```

In particular, compare v2/v3 records and require Route A and Route B objects
to be field-equal for 120/120 records; preserve 15 parity pairs, 30 radial
keys, 120 records, odd direct RW / independently solved even Zerilli, fixed
scale/no fit, no radial solve/frame/angular/total-plane-wave/Li scope,
separate uncertainty budgets, and all nonclaims.

At start and end rehash the frozen convention contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
selected domain
`9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
D_union plan
`de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`,
threshold contract
`8c2ab9ca254df9c15e3947479bb0af3bb6204f37d326b52c16a0984604ae005e`,
threshold rationale/test, V2.1/external source identities, and the seven
protected radial source hashes in the initial T7 record. No drift is allowed.

Run the exact focused recheck command from the initial blocker. Under delta
governance, do not rerun an unrelated full scientific review; instead verify
the T6-recorded Phase-6 and full-suite counts against the immutable report and
run only additional checks causally needed by this repair.

## 5. Verdict and durable record

If and only if the failed-item unblock condition and all preserved invariants
hold, return exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PARTIAL
GATE_LABEL: ACCEPT GREEN / V2.2 SELECTED-DOMAIN WAVEFORM ROUTES READY FOR V2.3
```

This bounded GREEN authorizes only later Root-T0 dispatch of V2.3. It does not
start V2.3 and does not make V2.2 absolute phase or full-domain science PASS.
The required nonclaims remain: `absolute_phase=PARTIAL`, full-domain V2
`NOT_ASSESSED`, full-domain V1 independent certification `PARTIAL`,
`global_status=null`, and no global GREEN.

If the same substantive blocker remains, return a complete class-A `REPAIR`
record for repair cycle 2. Any new blocker is allowed only with exact evidence
that repair cycle 1 changed a passed dependency and thereby invalidated the
current frozen claim. Other advice is B/C/D and cannot block advance.

Write the durable delta-review record using
`docs/templates/t7_gate_verdict_template.md`, with `attempt: repair_1`,
`completed_bounded_repairs: 1`, `same_substantive_blocker_remaining` and all
delta fields explicit. You may update only `status.md`,
`docs/handoffs/T7_current.md`, and a necessary T7 archive/review document.
Prepend or append the delta decision while retaining the complete initial
review text in `T7_current.md`; the v3 validator deliberately requires that
initial decision/blocker record to remain readable. Do not modify candidate,
implementation, tests, thresholds, conventions, prompts, T6 handoff, or any
evidence root. Do not dispatch T6 and do not start V2.3.
