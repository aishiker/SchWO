# T7 gate verdict template

Copy this template into the durable review report or T7 handoff.  Do not omit
fields; use `none` or an empty list only when independently verified.

```yaml
review_id: <stable review id>
gate_id: <frozen bounded gate id>
attempt: initial | repair_1 | repair_2
reviewer_task: <formal T7 task identity>
reviewed_candidate:
  root: <absolute or repository-relative path>
  identities:
    - path: <path>
      sha256: <64 hex>

frozen_review_basis:
  review_contract:
    path: <path>
    sha256: <64 hex>
  domain:
    path: <path>
    sha256: <64 hex>
  thresholds:
    - id: <stable threshold id>
      value: <exact value>
      units: <units>
      source_path: <path>
      source_sha256: <64 hex>
  blocking_criteria:
    - <stable criterion id>
  protected_identities:
    - path: <path>
      expected_sha256: <64 hex>
      observed_start_sha256: <64 hex>
      observed_end_sha256: <64 hex>

ADVANCE_DECISION: ADVANCE | REPAIR | ESCALATE
CLAIM_STATUS: PASS | PARTIAL | FAIL | NOT_ASSESSED
GATE_LABEL: <prompt-required bounded label or ESCALATE / T0 ADJUDICATION REQUIRED>

incremental_review_state:
  passed_items:
    - item_id: <stable id>
      evidence_identity: <path/hash or exact invariant>
  failed_items:
    - item_id: <stable id>
      blocker_id: <class-A blocker id>
  partial_allowed_items:
    - item_id: <stable id>
      reason: <why PARTIAL is allowed by the frozen gate>
  not_assessed_items:
    - item_id: <stable id>
      reason: <why outside this gate>

findings:
  - finding_id: <stable id>
    class: BLOCKING_CURRENT_GATE | NONBLOCKING_LIMITATION | CONTROL_PLANE_REPAIR | FOLLOW_UP_DEBT
    summary: <one sentence>
    # The following nine fields are mandatory only for BLOCKING_CURRENT_GATE.
    blocker_id: <stable blocker id>
    violated_contract_item: <exact frozen item>
    exact_evidence: <path/hash/record/test output>
    expected_value: <exact expected value>
    observed_value: <exact observed value>
    bounded_repair: <minimal repair>
    allowed_files:
      - <path or exact glob>
    recheck_command: <exact command>
    unblock_condition: <binary condition>

delta_review:
  reviewed_failed_items:
    - <stable item id>
  passed_invariants_rechecked:
    - <stable item id>
  protected_identities_match: true | false
  unrelated_passed_items_reopened: false

hold_details: null
# When HOLD is used, replace null with:
# exact_reason: <allowed HOLD reason with exact evidence>
# unblock_condition: <binary condition>
# owner: <T0/T6/T7/other exact owner>
# minimum_next_action: <one bounded action>
# independent_downstream_work_may_proceed: true | false

verification:
  commands:
    - <exact command>
  results:
    - <exact pass/fail/skip count or hash result>

non_claims:
  - <domain/observable not established>
  - no global GREEN

repair_cycle:
  completed_bounded_repairs: 0 | 1 | 2
  same_substantive_blocker_remaining: true | false
  t0_adjudication_required: true | false
```

Interpretation rules:

- `CLAIM_STATUS: PARTIAL` may coexist with `ADVANCE_DECISION: ADVANCE`.
- Only a complete `BLOCKING_CURRENT_GATE` finding permits `REPAIR`.
- After repair 2 / delta review 2, a recurring substantive blocker requires
  `ADVANCE_DECISION: ESCALATE` and
  `GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED`.
- HOLD is not shorthand for PARTIAL or future work.
- A legacy GREEN label describes only the bounded gate in `gate_id`.
