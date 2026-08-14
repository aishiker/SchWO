# Phase 6 T7 V2.1 — independent mode-amplitude review

You are the existing formal SchWO T7 task.  Perform a read-only independent
review of V2.1 only.  Do not trust the T6 summary, edit scientific code or
artifacts, dispatch another task, or begin V2.2.

## Start gate and dependencies

Read `project.md`, current `status.md`, `docs/handoffs/T7_current.md`, the
V2.0 material review, frozen convention contract and selected domain,
`docs/review_gate_liveness_protocol.md`,
`docs/templates/t7_gate_verdict_template.md`,
`docs/prompts/phase6_t6_v2_1_mode_amplitudes.md`, this prompt, the T6 handoff,
all V2.1 source/tests, and every file in the candidate V2.1 root.

Require the predecessor checkpoint exactly:

```text
CHECKPOINT / V2.1 MODE-LEVEL ASYMPTOTIC AMPLITUDES FROZEN
```

At review start and end, rehash the convention contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
selected domain
`9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
D_union plan
`de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`,
and the seven protected files:

```text
radial_solver.py             9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
conditioned_radial.py        91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
scaled_tortoise_radial.py    d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
adaptive_jost_radial.py      3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
matching.py                  9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
physical_boundary_radial.py fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
boundary_conditions.py       b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
```

Any drift, missing current authority, non-immutable root or domain mismatch is:

```text
HOLD / V2 FROZEN INPUT IDENTITY MISMATCH
```

## Independent checks

Independently rebuild the selected inventory as 15 parity pairs, 30 radial
keys, 60 channels per incident column and exactly 120 records.  Rehash every
source and artifact.  From original V1 selected bytes independently recover
`A_in_raw`, `A_out_raw` and complex `T_horizon_raw`; reject an assumed unit
incoming coefficient or a source not sufficient to determine it.

Re-derive and recompute `c_lm`, `c_lm/A_in_raw`, even ZM, odd RW-to-CPM
`2i/omega`, total/free/scattered/horizon coefficients and the full complex
total-equals-free-plus-scattered identity.  Check both incident columns,
`m=-2,+2`, all phases, formula/source identities and separate numerical and
convention budgets.  Confirm `radial_solve_count=0` by artifact, static source
inspection and process evidence.

Reject any observer frame, finite-radius waveform claim, angular or `m` sum,
total-plane-wave infinity sum, Li figure dependency, threshold/convention
change, hidden fit, forbidden file modification, full-domain extrapolation or
global GREEN.

Use CPython 3.14 and independently run targeted tests, all Phase-6/V2 tests,
the full suite, Ruff, compileall and `git diff --check`.  Record exact commands
and results.  You may update only `status.md`, `docs/handoffs/T7_current.md`
and a necessary T7 archive handoff; do not modify V2.1 science or its root.

## Finding classes, incremental state and terminal envelope

Freeze `passed_items`, `failed_items`, `partial_allowed_items` and
`not_assessed_items` on the initial review.  Classify every finding as
`BLOCKING_CURRENT_GATE`, `NONBLOCKING_LIMITATION`, `CONTROL_PLANE_REPAIR` or
`FOLLOW_UP_DEBT`.  Only a complete class-A finding with all nine mandatory
blocker fields from the liveness protocol may set `REPAIR`.  A delta review
checks only failed items, passed-invariant preservation and protected hashes;
do not reopen passed items without new causal evidence.  Enforce the initial
review plus at most two bounded repair/delta-review cycles.

Return the template with exactly one `ADVANCE_DECISION`, one `CLAIM_STATUS`
and one compatible label:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V2.1 MODE-LEVEL ASYMPTOTIC AMPLITUDES READY FOR V2.2

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL | PARTIAL
GATE_LABEL: REVIEW YELLOW / V2.1 CHANGES REQUIRED

ADVANCE_DECISION: ESCALATE
CLAIM_STATUS: FAIL | NOT_ASSESSED | PARTIAL
GATE_LABEL: REVIEW RED / V2.1 INVALID
```

After the second delta review, a recurring substantive blocker instead uses
`GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED`.  HOLD is permitted only for
the protocol's exceptional evidence states and must include all five HOLD
fields; it uses `ADVANCE_DECISION: ESCALATE`.  Scientific `PARTIAL` alone is
not HOLD or a blocker.

Every outcome must name the reviewed root and hashes and retain the non-claims
that V2 is selected-domain only, full-domain V1 independent certification is
`PARTIAL`, and no global GREEN exists.  Do not dispatch V2.2.
