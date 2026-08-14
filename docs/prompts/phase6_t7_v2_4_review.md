# Phase 6 T7 V2.4 — final selected-domain release review

You are the existing formal SchWO T7 task.  Independently review the V2.4
selected-domain release read-only.  Do not edit science/artifacts, dispatch
another task, enter V3, run figures or start observer validation.

Require exactly:

```text
CHECKPOINT / V2 SELECTED-DOMAIN RELEASE FROZEN
```

Read project/status/T7 handoff, frozen V2.0 authorities/material review, the
review-gate liveness protocol and verdict template,
accepted V2.1--V2.3 roots and formal T7 decisions, V2.4 prompt/source/tests/T6
handoff, `docs/phase6_v2_selected_domain_closeout.md`, and every release byte.
Do not trust the T6 ledger or summary without rebuilding from native sources.

At review start/end rehash contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
domain `9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
plan `de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`
and:

```text
radial_solver.py             9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
conditioned_radial.py        91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
scaled_tortoise_radial.py    d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
adaptive_jost_radial.py      3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
matching.py                  9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
physical_boundary_radial.py fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
boundary_conditions.py       b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
```

Any drift is `HOLD / V2 FROZEN INPUT IDENTITY MISMATCH`.

Independently rebuild the release from the immutable native V2.1--V2.3 roots.
Verify exact 30-key/120-record selected scope, every hash and permission,
native-to-certificate state propagation, all 12 named certificates, separate
uncertainty budgets, method-independence boundaries, protected identities and
non-claims.  Confirm `global_status=null`, no state upgrade, no full-domain or
angular/observer/Li extrapolation and an evidence-correct absolute-phase
state.  Confirm no radial solve or new physics occurred in V2.4.

Run targeted, all Phase-6/V2 and full tests with exact CPython 3.14, plus
Ruff, compileall and diff checks.  Update only status, T7 handoff and a
necessary T7 archive.  Do not change source science, roots or closeout claims.

Freeze the four incremental item inventories and classify every finding as
exactly one of `BLOCKING_CURRENT_GATE`, `NONBLOCKING_LIMITATION`,
`CONTROL_PLANE_REPAIR` or `FOLLOW_UP_DEBT`.  Only a complete blocker that
invalidates the honest selected-domain release may set REPAIR.
`global_status=null`, `full_domain=PARTIAL`, an evidence-based absolute-phase
PARTIAL and explicit non-claims are permitted and do not alone block advance.
Delta reviews inspect only failed items, passed invariants and protected
identities, with at most two repair/review cycles.

Return the verdict template with one valid combination:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS | PARTIAL
GATE_LABEL: ACCEPT GREEN / V2 SELECTED-DOMAIN GAUGE-INVARIANT WAVEFORM AND FLUX VALIDATION COMPLETE

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL | PARTIAL
GATE_LABEL: REVIEW YELLOW / V2.4 CHANGES REQUIRED

ADVANCE_DECISION: ESCALATE
CLAIM_STATUS: FAIL | NOT_ASSESSED | PARTIAL
GATE_LABEL: REVIEW RED / V2.4 INVALID
```

After delta review 2, a recurring blocker uses
`GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED`.  HOLD is exceptional and
must include all five protocol fields; scientific `PARTIAL` alone is not
HOLD.  Bind the decision to all exact release identities.  GREEN is only the frozen
selected-domain V2 release gate; it is not global GREEN, full-domain V2,
complete angular waveform, finite-radius observer validation, Li equivalence
or V3 authorization.  Return the decision to Root T0 and stop.
