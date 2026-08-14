# Phase 6 V3.1-U bounded repair cycle 1 design

Date frozen by Root T0: 2026-08-12

Scientific gate: `phase6_v3_1_hp_unitarity_deficit_replacement_v1`

Repair identity: `phase6_v3_1_u_auxiliary_geometry_repair_cycle1_v1`

This is bounded scientific repair 1 of the distinct V3.1-U replacement gate.
It is not a retry of the failed root, a third repair of predecessor V3.1, or
V3.2.  It changes no frozen formula, domain, threshold, convention, route
selection, precision schedule, protected radial implementation, or claim.

## 1. Frozen failure and governance basis

The formal terminal scientific verdict is:

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-U CHANGES REQUIRED
```

It is recorded in
`docs/handoffs/archive/T7_2026-08-12_v3_1_u_terminal_scientific_failure_review.md`,
SHA-256 `7aa90e012e7d079d7c16256647d97db663293cf9ff6f5a4346130aa1d82482f1`.
The archive-only control-plane clarification is
`docs/handoffs/archive/T7_2026-08-12_v3_1_u_terminal_scientific_failure_control_plane_clarification.md`,
SHA-256 `2f661f45dc609f6f92bb475060d5860586df3a916de8acefbab5f539f8850da0`.

The sole class-A blocker is
`v31u_auxiliary_radius_closed_boundary_roundoff`.  The existing Route-U
membership predicate rejects an algebraically admissible exponent-2 closed
boundary at one 220-decimal-digit node because a mathematically zero residual
rounds to approximately `-7.082e-220`.  This is a deterministic geometry
construction defect, not a threshold failure or physical inconsistency.

The separate class-C item is
`v31u_live_handoff_start_gate_recursion`.  The producer currently requires an
obsolete live `T7_current.md` hash, although every formal review necessarily
advances that mutable handoff.  This must be replaced by a non-circular
immutable authority chain before any later official execution.

Completed bounded scientific repairs remain `0`; this package freezes repair
cycle `1 of 2`.  Package review and control-plane correction do not consume a
scientific repair cycle.

## 2. Immutable failed evidence and no-reuse rule

The failed root is:

```text
runs/phase6/classic_scattering/v3_1_hp_unitarity_deficit_v1_20260811T143911Z_py314
failure.json          5aef8aec8511e5fa35df6459b7cd520b046e080d43f6c24fd95a8b46379d1779
failure_manifest.json 6a8ab79495bad03c2d08742a6a6b79f3afc6df658eb7d7dcb20f145efa905b1e
route_u_records.jsonl 645e2e116b13dbc1c70e7be1db06f3827a04ccd723e6093ffac8b06199e56c2b
route_u_ladders.jsonl d7c1381fd0e51f439056350de90022ddc8aaf1808e72ee736b304ef10b2a5537
```

The root and every partial Route-A/Route-U value are immutable failure
evidence.  They may be read to reconstruct the frozen 318-key geometry test
inventory, but no record, checkpoint, cache, amplitude, flux, ladder, route
result, or manifest byte may populate a later candidate.  Any authorized
science execution must start in a fresh absent UTC-named root and recompute
Route A before Route U/B/C.

## 3. Exact implementation boundary

The scientific repair may change exactly:

```text
src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py
tests/unit/test_phase6_v3_hp_unitarity.py
tests/regression/test_phase6_v3_hp_unitarity_publication.py
```

The control-plane repair may additionally change exactly:

```text
src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
```

The combined T4 implementation/test delta is therefore exactly four unique
paths.  The two tests are shared verification surfaces.  No other source,
script, test, status, handoff, config, prompt, package, or evidence path may be
changed by T4 during implementation.

The CLI is frozen byte-for-byte:

```text
scripts/phase6_v3_1_hp_unitarity.py
01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4
```

All seven protected radial files, the V3.0 domain/formula/convention
authorities, the 16 thresholds, the 496/9920/102/458/23 graph, the 318-key
Route-U selector result, and the three-node precision schedule remain frozen.

## 4. Algebraically stable closed-boundary construction

Let

```text
L2 = ell(ell+1)
R_turn = sqrt(L2)/k
R_match = max(300, R_turn)
R_q = 2^q R_match, q in {0,1,2}
```

The frozen admissibility rule remains the closed inequality

```text
k R_q >= 4 sqrt(L2).
```

The repair changes only how membership in this already frozen set is decided.
It must not decide membership by subtracting two independently rounded
`mpmath` square-root expressions.  It must use an algebraically equivalent
nonnegative squared comparison or an exact rational/dimensionless ratio whose
closed-boundary value is represented exactly.  A suitable invariant is

```text
rho2 = (k R_match)^2 / L2
admissible(q) iff 4^q rho2 >= 16.
```

For the turning-radius branch `rho2=1` by construction, so exponent `2` is
admissible exactly.  For the `R_match=300` branch, the comparison must be
formed from the canonical decimal `kM`, integer `ell`, and exact nonnegative
algebra rather than from a precision-dependent cancellation.  Exponents are
still tested in the fixed order `(0,1,2)`, and the first admissible exponent is
returned.  The actual `mpmath` radii supplied to the unchanged oracle solve
remain `R_match` and `2^q R_match` at the requested node precision.

Forbidden substitutes include an epsilon tolerance, `almosteq`, clipping,
rounding a residual to zero, always forcing exponent 2, expanding the exponent
set, using a solved amplitude/residual, or changing a failed key's precision.

## 5. Mandatory zero-solve geometry proof

Before any scientific solve, T4 must run a geometry-only proof that:

1. exact-boundary, just-below, and just-above dimensionless cases select the
   correct first exponent under the closed inequality;
2. the original failing key `(kM=0.005, ell=10, odd)` admits exponent 2 at
   every frozen scheduled precision `120/160/220`;
3. all exact 318 routed keys admit exactly one deterministic first exponent at
   all three scheduled precisions, giving `954` successful geometry nodes;
4. repeated evaluation is independent of ambient `mp.mp.dps` and produces
   identical exponent decisions;
5. any invalid, negative, nonfinite, out-of-domain, or altered exponent-set
   input fails closed;
6. the proof executes zero `_fresh_match`, radial, AP, external BHPT, or other
   numerical solver calls.

The failed root's frozen route map may supply only ordered mode identities and
the already reviewed Route-U selector decisions for this proof.  It is not a
science input to a future root.

## 6. Non-circular start-gate authority chain

The repaired producer must preserve and rehash the original V3.1-U package,
design, T4 prompt and package approval; the failed terminal identities; the
formal terminal review; this control-plane clarification; the new combined
repair package; and the formal package-review archive.  It must also preserve
all original scientific source bindings and seven protected identities.

Live `docs/handoffs/T7_current.md`, `status.md`, and
`docs/handoffs/T0_current.md` are recorded as package-start predecessors, but
their mutable live hashes must not be execution-time equality requirements.
There is one immutable authority chain, not a list of acceptable historical
hashes and not an environment-, argument-, or boolean-selected bypass.

The implementation-stage `verify_start_gate()` must validate the immutable
predecessor/package/package-review chain and reject missing, extra, malformed,
wrong-verdict, wrong-scope, wrong-terminal-root, protected-drift, or source-
drift authorities.  The producer source ledger must record the repaired
producer and oracle, unchanged CLI, package/reviews, and every frozen source at
start and end.

Official execution is a separate later authorization.  After formal T7
implementation delta review, Root T0 must publish one fixed-path, O_EXCL,
regular `0444`/nlink1, canonical-JSON dispatch for one exact fresh absent root.
The dispatch must bind the package, package review, implementation review,
exact repaired four hashes, unchanged CLI, frozen source/protected identities,
target root, `single_use=true`, UTC timestamp, and all required verdict tokens.
The producer must semantically validate that fixed dispatch and publish its
identity/consumption before the first science call.  A second root, reused
dispatch, missing implementation review, mutable-authority substitution, or
changed source must fail before science.

Because the CLI is frozen and carries no authority arguments, the formal T7
package review must explicitly confirm that the proposed fixed-path dispatch
and producer validation form a sufficient single non-circular chain.  If not,
it must return a complete package-level blocker before T4 is dispatched; T4
may not invent another authority channel.

## 7. T4 implementation and preflight stop boundary

Formal T4 may start only after formal T7 returns the exact package-ready gate
label bound to this package.  T4 then implements only the four-path delta and
runs:

- the two focused test files under exact CPython 3.14 and the mpmath overlay;
- the exact 954-node no-solve geometry proof;
- start-gate positive and adversarial tests for every authority class;
- the frozen CLI `preflight` command;
- Ruff check/format, in-memory compilation, and four-path diff-check;
- independent SHA-256 rechecks of the CLI, domain, thresholds, conventions,
  original sources, failed evidence, and protected files.

T4 must not run sentinels, Route A/U/B/C science, create an official root,
write a T4/status handoff, or consume a dispatch in this implementation turn.
It returns exact before/after hashes, test counts, geometry counts and a
machine-readable temporary evidence inventory to Root T0.

## 8. Incremental T7 implementation review

Formal T7 then reviews only:

- the failed geometry-totality item and its exact-boundary unblock condition;
- the class-C start-gate recursion repair;
- preservation of frozen passed invariants and protected/source identities;
- exact four-path implementation scope and frozen CLI;
- the zero-solve nature and exact `318*3=954` geometry coverage;
- fail-closed authority adversaries and one-use dispatch semantics.

If accepted, the bounded label is
`ACCEPT GREEN / V3.1-U REPAIR CYCLE 1 IMPLEMENTATION READY FOR ONE-USE T0 DISPATCH`.
This is implementation readiness only.  V3.1-U science remains
`NOT_ASSESSED` until a fresh terminal root is independently reviewed.

## 9. Scientific execution and downstream boundary

Only after the implementation review returns `ADVANCE` may Root T0 create the
one-use dispatch and send formal T4 a separate execution instruction.  The
fresh run must recompute all `496/9920`, then `N_U=318/954`, `102/458`, `23`,
all 16 thresholds and all five certificates.  No predecessor bytes may be
copied.  Any failure is sealed honestly and returns to T7 under the liveness
protocol.

V3.2 starts automatically only after a complete immutable V3.1-U candidate is
independently reviewed by formal T7 with `ADVANCE`.  This package does not
authorize V3.2, Li-figure recomputation, finite-radius observer claims,
threshold relaxation, full-domain V3, or global GREEN.
