# Phase 6 T7 — pre-execution review of the V2.3 flux-threshold contract

You are the existing formal SchWO T7 task.  Perform an independent read-only
scientific and control-plane review of the proposed V2.3 threshold package.
Do not execute V2.3, edit science/config/prompt bytes, call a radial solver,
dispatch T6/V2.4, or create a V2.3 science root.

## Frozen candidate package

Require these exact identities:

```text
6cc64b32534c0211da90a7fbec7fb783b91a3b852cfda2991640a37e9de88808  configs/phase6_v2_3_flux_threshold_contract_20260811.json
ce0da14d565bd1db9a63d848f8c7f68078c144899da7911861ad590494586ee8  docs/phase6_v2_3_flux_threshold_rationale_20260811.md
ba85493073d653de1ee5847f05668e0eaeb418a3697827df2c2e2b2afe2ea5e4  tests/unit/test_phase6_v2_3_threshold_contract.py
```

Read `project.md`, `status.md`, current T0/T6/T7 handoffs, the review-gate
liveness protocol and verdict template, V2.0 convention/domain authorities,
the accepted V2.1 and authoritative V2.2-v3 artifacts, the V2.2 threshold
contract and delta verdict, V1 selected radial acceptance artifacts, external
direct bounded RW/Zerilli artifacts, and every source identity named by the
candidate contract.  Rehash them independently; do not trust the candidate's
own ledger as proof.

At start and end also require:

```text
1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517  configs/phase6_v2_0_convention_contract_20260810.json
9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818  configs/phase6_v2_0_selected_domain_20260810.json
de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3  D_union plan identity
```

and the seven protected radial files:

```text
radial_solver.py             9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
conditioned_radial.py        91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
scaled_tortoise_radial.py    d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
adaptive_jost_radial.py      3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
matching.py                  9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
physical_boundary_radial.py fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
boundary_conditions.py       b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
```

Identity drift is a protocol-complete HOLD, not a scientific repair finding.

## Independent review requirements

Independently derive and verify all of the following before accepting the
package:

1. Under `exp(-i omega t)`, the signed radial-current orientations are
   `J_in<0`, `J_out>0`, `J_h<0`, and the MP energy-flux conversion is
   `sigma_l*omega*abs(J)/(128*pi)` for the frozen real-field-peak convention.
2. The energy-flux formula contains the explicit time-average `1/2`,
   `sigma_l=(ell+2)!/(ell-2)!`, `omega^2`, `1/(128*pi)`, `c_lm/A_in_raw`, and
   odd `Psi_CPM=(2i/omega)Psi_RW` factors.
3. The balance uses total outgoing flux only.  Free and scattered pieces are
   interference diagnostics and are never independent positive balance terms.
4. The domain is exactly 30 radial keys x two `m` values x two incident
   columns = 120 records, with odd/even 15/15 and no angle or angular sum.
5. The SchWO `1e-8` and external `1e-15` balance thresholds are byte-for-byte
   inherited from preexisting accepted policies.
6. `2.1e-11` is a valid upward-rounded quadratic propagation of the frozen
   V2.2 A/B amplitude-map allowance, not a fit to V2.3 data.
7. `4.1e-6` is a valid upward-rounded image of the frozen V1 selected
   `2e-6` complex-S and log-absolute-transmission bounds for, respectively,
   outgoing and horizon flux fractions.
8. Rebuild every preexecution diagnostic independently from immutable source
   bytes at arbitrary precision.  Confirm that diagnostics are not acceptance
   thresholds and that the approximately `9.37e-1498` minimum horizon fraction
   forces arbitrary precision rather than record omission.
9. The exact predicates, separate numerical/convention budgets, no-fit policy,
   no-radial rule, no-frame/no-angular-sum boundary and nonclaims are complete.
10. No V2.3 science artifact or active V2.3 process exists, and no threshold
    was calibrated from a V2.3 result.

Run the focused V2.3/V2.2 contract tests with exact project CPython 3.14, JSON
validation, Ruff on the new test, and `git diff --check` on the candidate
package.  Do not run a radial or paper-figure test.

## Governance and result

This is a pre-execution material-readiness gate.  Freeze passed, failed,
partial-allowed and not-assessed items.  Classify every finding under the
liveness protocol.  Only a complete class-A finding that directly invalidates
the bounded flux gate may return REPAIR.  V2.2 absolute phase `PARTIAL`, wider
domain incompleteness, or future V2.4 work are nonblocking limitations.

Return one template-complete verdict:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V2.3 FLUX THRESHOLD CONTRACT READY FOR BOUNDED EXECUTION
```

or, with complete class-A fields:

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL | PARTIAL
GATE_LABEL: REVIEW YELLOW / V2.3 THRESHOLD CONTRACT CHANGES REQUIRED
```

Use `ESCALATE` only as defined by governance.  Bind the verdict to all exact
candidate and predecessor identities.  State explicitly:

```text
V2.3 scientific validation remains NOT_ASSESSED before execution.
V2.2 absolute phase remains PARTIAL and is not promoted by this gate.
Full-domain V2 remains NOT_ASSESSED; no global GREEN is permitted.
```

Do not dispatch T6 or V2.4.  Update only T7 handoff/archive if needed for a
durable verdict; do not modify status or any candidate/science byte.
