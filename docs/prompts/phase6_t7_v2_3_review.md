# Phase 6 T7 V2.3 — independent flux-closure review

You are the existing formal SchWO T7 task.  Review V2.3 independently and
read-only.  Do not edit science/artifacts, dispatch V2.4 or expand scope.

Require exactly:

```text
CHECKPOINT / V2.3 SELECTED-DOMAIN FLUX CLOSURE EVIDENCE FROZEN
```

Read project/status/T7 handoff; V2.0 authorities; the review-gate liveness
protocol and verdict template; accepted V2.1/V2.2
roots/reviews; the V2.3 prompt, source, tests, T6 handoff and all candidate
artifact bytes; and original V1 current/amplitude sources.  Do not trust the
T6 report as proof.

At review start/end rehash contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
domain `9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
plan `de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`
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

Any drift is `HOLD / V2 FROZEN INPUT IDENTITY MISMATCH`.

Independently recompute signed currents, physical incoming/total-outgoing/
horizon fluxes, MP infinity/horizon fluxes, Route-B waveform flux and external
witnesses for every record.  Verify even/odd normalization, `omega` and
RW/CPM factors, `1/(128 pi)`, time averaging, dimensions, positivity and
horizon/infinity signs.  Recompute the total-mode balance and prove that no
scattered-only flux replaced total outgoing.  Check every threshold was
already frozen; reject fitted factors or retuned constants.

Verify exact domain/cardinality, source/provenance hashes, separate numerical
and convention budgets, immutable root, `radial_solve_count=0`, and absence of
observers, angular sums, Li figures and global/full-domain claims.

Use CPython 3.14 for targeted, all Phase-6/V2 and full tests plus Ruff,
compileall and diff checks.  Update only status/T7 handoff/archive.

Freeze the four incremental item inventories and classify every finding as
exactly one of `BLOCKING_CURRENT_GATE`, `NONBLOCKING_LIMITATION`,
`CONTROL_PLANE_REPAIR` or `FOLLOW_UP_DEBT`.  Only a complete blocker directly
invalidating selected-domain flux closure may set REPAIR.  Wider-domain or
waveform limitations are nonblocking here.  A delta review checks failed
items, passed invariants and protected identities only, with at most two
repair/review cycles.

Return the template with one valid combination:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS | PARTIAL
GATE_LABEL: ACCEPT GREEN / V2.3 SELECTED-DOMAIN WAVEFORM AND FLUX CLOSURE READY FOR V2.4

ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL | PARTIAL
GATE_LABEL: REVIEW YELLOW / V2.3 CHANGES REQUIRED

ADVANCE_DECISION: ESCALATE
CLAIM_STATUS: FAIL | NOT_ASSESSED | PARTIAL
GATE_LABEL: REVIEW RED / V2.3 INVALID
```

After delta review 2, a recurring blocker uses
`GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED`.  HOLD must satisfy the
protocol and include all five fields; scientific `PARTIAL` is not HOLD.  Bind
the result to exact identities and retain all selected-domain,
absolute-phase, full-domain and no-global-GREEN non-claims.  Do not dispatch
V2.4.
