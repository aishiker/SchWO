# T7 review-gate liveness protocol

Effective date: 2026-08-10

This protocol governs future T7 gate reviews.  Its purpose is to prevent a
bounded scientific gate from entering a YELLOW/HOLD live-lock while preserving
every frozen scientific convention, domain, threshold, input identity and
blocking criterion.  It changes review governance only.  It does not upgrade
a scientific claim, weaken a test, authorize a solver run, or create global
GREEN.

Historical verdicts remain historical evidence.  A future review that starts
after this protocol takes effect must use the verdict envelope and finding
schema below, including when an older prompt also requires a legacy exact
GREEN/YELLOW/RED label.

## 1. Mandatory dual-axis verdict

Every T7 verdict must report these independent fields:

```text
ADVANCE_DECISION: ADVANCE | REPAIR | ESCALATE
CLAIM_STATUS: PASS | PARTIAL | FAIL | NOT_ASSESSED
```

- `ADVANCE` means the frozen bounded gate permits its declared downstream
  dependency to start.
- `REPAIR` means at least one fully specified
  `BLOCKING_CURRENT_GATE` finding prevents that bounded advance.
- `ESCALATE` means T7 cannot close the gate within the frozen scope or the
  repair-cycle limit and Root T0 must adjudicate.
- `CLAIM_STATUS` describes the scientific claim, not workflow liveness.
  `PARTIAL` does not by itself prevent `ADVANCE`.
- A legacy prompt-required exact line remains as `GATE_LABEL`.  It is a
  compatibility label, not a substitute for the two axes.
- `GREEN` always means the current bounded gate may advance.  It never means
  project-wide, full-domain, all-observable or global GREEN.

## 2. Finding classes and blocker completeness

Every finding must be assigned exactly one class:

```text
A. BLOCKING_CURRENT_GATE
B. NONBLOCKING_LIMITATION
C. CONTROL_PLANE_REPAIR
D. FOLLOW_UP_DEBT
```

Only class A may set `ADVANCE_DECISION: REPAIR`.  Every class-A finding must
contain all fields below:

```text
blocker_id
violated_contract_item
exact_evidence
expected_value
observed_value
bounded_repair
allowed_files
recheck_command
unblock_condition
```

An incomplete finding cannot be a blocker.  It must be reclassified as B, C
or D until the missing proof is supplied.  A new critical defect may become A
only when T7 demonstrates a direct causal chain from the defect to invalidity
of the current frozen claim.  Severity, general scientific interest or value
to a future full-domain claim is not enough.

- B records an honest limitation compatible with advancing the bounded gate.
- C records a metadata/manifest/path/permission/wording/handoff or read-only
  observer defect whose repair does not change science bytes, formulas,
  thresholds, input identities or solver behavior.
- D records a useful task outside the current frozen acceptance boundary.

A class-C finding does not set `REPAIR`.  T0 may withhold mechanical dispatch
under the existing artifact/tests/status/handoff completion gate, authorize the
bounded control-plane fix, and request only T7 delta verification before
dispatch.

## 3. Frozen acceptance basis

At review start T7 must record the exact hashes/identities of the review
contract, domain, thresholds and blocking criteria.  T7 may evaluate only that
frozen basis.  It may not retroactively enlarge the gate because a stronger
test, broader domain or additional desirable witness becomes apparent during
review.

New advice that does not directly invalidate the current claim is
`FOLLOW_UP_DEBT`.  Changing a frozen acceptance item requires a new T0/user
gate; it cannot be smuggled into a repair review.

## 4. Incremental review state

The initial review freezes four item inventories with stable item IDs and
evidence identities:

```text
passed_items
failed_items
partial_allowed_items
not_assessed_items
```

A repair review checks only:

1. the frozen `failed_items` and their unblock conditions;
2. whether the bounded repair damaged any frozen passed invariant;
3. protected and source identities.

T7 must not reopen a passed item without new exact evidence that the repair
changed its bytes, dependency or invariant.  Any such reopening must itself be
a fully specified class-A finding.

## 5. Repair-cycle limit

One gate permits at most this sequence:

```text
initial review
bounded repair 1 -> delta review 1
bounded repair 2 -> delta review 2
```

After delta review 2, if the same substantive blocker remains, T7 must return:

```text
ADVANCE_DECISION: ESCALATE
GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED
```

No third isomorphic repair is allowed.  Root T0 must choose one of:

1. narrow the claim or domain;
2. redesign the gate or algorithm;
3. freeze the blocked branch and advance work that does not depend on it.

Renaming a blocker does not reset the counter when violated item, evidence and
unblock condition are substantively the same.

## 6. HOLD is an exceptional evidence state

HOLD is allowed only for:

- missing or inconsistent evidence/identity;
- an active or concurrent writer;
- an internally contradictory contract;
- a necessary unreadable input;
- unrecoverable required provenance needing a policy decision.

Every HOLD must include:

```text
exact_reason
unblock_condition
owner
minimum_next_action
independent_downstream_work_may_proceed: true | false
```

A HOLD uses `ADVANCE_DECISION: ESCALATE` unless the frozen prompt defines a
strictly local, already authorized control-plane recovery.  Its
`CLAIM_STATUS` is the evidence-supported value, commonly `NOT_ASSESSED`.

Scientific `PARTIAL`, absence of full-domain coverage, an unfinished future
task or disagreement with a Li figure cannot alone justify HOLD.

## 7. Control-plane fast repair

T0 or the authorized implementation owner may perform a bounded class-C
repair when it changes only metadata, manifest, path, permission, wording,
handoff or a read-only observer false positive.  It must preserve science
bytes, formulas, thresholds, input identity and solver behavior and record
before/after hashes plus the exact delta.

T7 then performs delta verification only: the class-C defect, protected
identities and passed-invariant preservation.  A complete scientific re-review
is prohibited unless the delta touched a scientific dependency.

## 8. V2 gate-specific advance semantics

- V2.1 may advance when normalization, exact 120-record cardinality,
  total/free/scattered complex identity and the no-radial/no-frame/
  no-angular-sum boundary pass.  Broader waveform science is not a V2.1 gate.
- V2.2 may advance with `CLAIM_STATUS: PARTIAL` and
  `absolute_phase=PARTIAL` when the frozen phase-invariant, magnitude and
  relative-phase criteria pass.  Absolute-phase follow-up is a limitation,
  not an automatic blocker.  This rule does not create a missing threshold or
  permit a threshold to be inferred, repurposed or weakened.
- V2.3 GREEN concerns only selected-domain infinity/horizon/radial flux
  closure.
- V2.4 GREEN means the selected-domain release is internally honest and
  closed.  `global_status=null`, `full_domain=PARTIAL` and explicit non-claims
  are allowed and required when supported by the evidence.

## 9. Required durable record

Use `docs/templates/t7_gate_verdict_template.md`.  Store the dual-axis verdict,
legacy label, frozen basis, attempt number, item inventories, classified
findings, HOLD details if any, exact hashes, tests and non-claims in the T7
handoff or an immutable review report.  Root T0 may dispatch a dependent task
only when `ADVANCE_DECISION: ADVANCE` and the prompt-required bounded
`GATE_LABEL` are both present and identity-bound.
