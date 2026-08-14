# Phase 6 T7 — pre-execution V2.2 waveform-threshold contract review

You are the existing formal SchWO T7 task.  Perform one independent,
read-only pre-execution review of the candidate V2.2 waveform-threshold
contract.  This is a critical scientific gate.  Do not edit the contract,
rationale, test, V2.0/V2.1 bytes, radial evidence, implementation, prompts or
artifacts.  Do not dispatch T6, execute V2.2, run a radial solver, or start
V2.3.

## Governance and exact candidate identities

Read `project.md`, `status.md`, `docs/handoffs/T0_current.md`,
`docs/handoffs/T7_current.md`, `docs/review_gate_liveness_protocol.md` and
`docs/templates/t7_gate_verdict_template.md`.  Apply the dual-axis and finding
classification rules exactly.

Review these stable candidate bytes:

```text
8c2ab9ca254df9c15e3947479bb0af3bb6204f37d326b52c16a0984604ae005e  configs/phase6_v2_2_waveform_threshold_contract_20260811.json
c96a0c640ffb2789c34e8e9ff364d42cc6cfe427b374a7cff1299d196b3c91b6  docs/phase6_v2_2_waveform_threshold_rationale_20260811.md
71918930e4b1384ab66adaf5e7d89bc55c31c30f156fa6f153332542759c611a  tests/unit/test_phase6_v2_2_threshold_contract.py
```

The previous execution prompt
`docs/prompts/phase6_t6_v2_2_waveform_routes.md` is an immutable historical
HOLD predecessor only.  No V2.2 route result exists.  Reject any threshold
derived from an unsealed or future V2.2 result.

At start and end rehash the V2.0 convention contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
selected domain
`9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
V2.1 manifest
`ae39829a3e95169f88aa7ce95639e5e3d473c9b7db23d6301cea24d40109ad90`,
V2.1 records
`eb0e36ae49a1b868f22279d9948e748a69f89d281890df3e6af5ea4356d1bcc5`,
V1 selected report
`3dc46242f171eedd15fcd5f697a728637ce863a9e393994ec611896d275939a1`,
and external direct manifest
`e12c49b00efecc9c65d42699f2a5052ecac1fe2c988312ed21c4da085fe5ee6d`.
Rehash all source identities listed in the candidate contract.

## Independent scientific checks

Independently rebuild the exact 30-key/120-record inventory and the
preexecution diagnostics from the immutable inputs.  Check all of the
following without trusting T0's prose or test:

1. Under the frozen normalization,
   `H_sc=F_sector*c_lm*(-1)^ell*(1-S_l)` and
   `C_record=abs(F_sector*c_lm)` imply
   `abs(H_A-H_C)/C_record=abs(S_A-S_C)`.
2. The fixed scale is independent of every candidate route result and no
   per-mode/global phase or complex scale fit is permitted.
3. The recorded source minima and maximum diagnostic rebuild exactly; the
   observed `1.726826...e-8` is not used as a threshold.
4. The generic conditioning floor `rho>=0.1` is satisfied by all immutable
   SchWO/external source records and does not permit dropping a channel.
5. A/B thresholds are a preexecution route-map/roundoff gate, not a radial
   independence claim.  A/C thresholds are the explicit analytic propagation
   of the already frozen selected `backend_complex_S=2e-6` budget.  B/C adds
   the A/B allocation by triangle inequality.
6. The relative-magnitude and wrapped-phase bounds follow from the stored
   signal floor and
   `|z-w|^2=(|z|-|w|)^2+4|z||w|sin^2(Delta phi/2)`.
7. The phase-invariant comparator remains well conditioned and is not hidden
   inside an aggregate uncertainty scalar.
8. Separate numerical and convention budgets, absolute-phase `PARTIAL`, exact
   selected-domain scope, no-radial/no-frame/no-angular-sum/no-total-plane-wave
   boundaries and all nonclaims are fail-closed.

Run the candidate focused test with exact CPython 3.14 and independently
recompute its substantive assertions.  Run Ruff checks for the test and
`git diff --check` on the candidate files.  Process checks are read-only.

You may update only `status.md`, `docs/handoffs/T7_current.md` and a necessary
T7 archive after the decision.  Do not change candidate identities.

## Exact verdict

If the contract is scientifically and executionally ready, return exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V2.2 WAVEFORM THRESHOLD CONTRACT READY FOR EXECUTION
```

This GREEN is only the bounded pre-execution contract gate.  V2.2 science
remains `NOT_ASSESSED`, full-domain V1 independent scientific certification
remains `PARTIAL`, and no global GREEN is permitted.

If repair is required, use the liveness protocol.  Only a fully specified
`BLOCKING_CURRENT_GATE` finding may return `REPAIR`; otherwise classify the
item as a nonblocking limitation, control-plane repair, or follow-up debt.
Protocol-qualified HOLD uses `ESCALATE` and all five HOLD fields.
