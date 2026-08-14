# T7 archive-only governance clarification — V3.1-U bounded scientific repair 1

Date: 2026-08-12

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1-U CHANGES REQUIRED
```

This is a `CONTROL_PLANE_REPAIR` clarification of the formal terminal review
at:

```text
docs/handoffs/archive/T7_2026-08-12_v3_1_u_terminal_scientific_failure_review.md
SHA-256 7aa90e012e7d079d7c16256647d97db663293cf9ff6f5a4346130aa1d82482f1
```

It does not reopen that scientific review, change its verdict, add another
class-A finding or consume a bounded scientific repair.  The sole class-A
blocker remains `v31u_auxiliary_radius_closed_boundary_roundoff`, and
`completed_bounded_scientific_repairs=0`.

## Independently confirmed control-plane defect

The current producer
`src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py`, SHA-256
`81f5ca43480976975fa185ce24ff3f47b83c755dc8b74892b97a93798a914e51`,
hard-codes in `verify_start_gate()`:

- the pre-review `docs/handoffs/T7_current.md` identity
  `61e25ccb891b992cc82426a135dca1bccdaafa3f84ccb9bfa338a6d3e8a4c383`;
- the original package/design/T4-prompt/package-review identities;
- the then-current `status.md` and `docs/handoffs/T0_current.md` identities.

The formal terminal review necessarily updated live `T7_current.md` to
`c41a9a26146d16e1ab3c8c1bf69ea9e4f52cd3d3e853eaa783263cedd7e90e65`.
Consequently the unchanged producer now fails before science.  Reverting the
handoff, accepting multiple historical hashes, bypassing the check or
monkeypatching it is forbidden.

Merely changing the producer's `T7_CURRENT_SHA256` constant is also
insufficient: the formal package review and implementation delta review may
advance live handoffs again.  The bounded repair must replace the live-handoff
equality with a non-circular immutable authority chain.  This is a class-C
control-plane defect because it changes no equation, solver, route selection,
domain, threshold, convention or scientific acceptance rule, but T0 must
withhold execution until it is closed.

## Corrected Route-U evidence identities

Fresh direct readback of the actual terminal-root files gives:

```text
645e2e116b13dbc1c70e7be1db06f3827a04ccd723e6093ffac8b06199e56c2b  route_u_records.jsonl
d7c1381fd0e51f439056350de90022ddc8aaf1808e72ee736b304ef10b2a5537  route_u_ladders.jsonl
```

The terminal root does not contain a file named
`route_u_precision_ladders.jsonl`; the on-disk filename is
`route_u_ladders.jsonl`.  These full hashes supersede only the two transcribed
Route-U JSONL hashes in the earlier review archive.  All counts, causal
analysis, verdict and other identities in that archive remain unchanged.

## Frozen allowed-file sets

### Scientific repair paths — unchanged

Exactly these three paths may change for the sole class-A science repair:

```text
src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py
tests/unit/test_phase6_v3_hp_unitarity.py
tests/regression/test_phase6_v3_hp_unitarity_publication.py
```

The tests are shared verification surfaces; their science assertions may cover
the exact closed-boundary, just-below/just-above cases and the full 318-key by
three-precision no-solve geometry matrix.

### Minimum control-plane/start-gate paths

Exactly one additional implementation path may change:

```text
src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
```

Within that file the change is confined to start-gate constants and the
`verify_start_gate()` authority-chain logic, plus the corresponding source
ledger binding needed to record the repaired bytes.  The two already allowed
test paths may add positive and adversarial start-gate tests.

The CLI remains frozen and must not change:

```text
scripts/phase6_v3_1_hp_unitarity.py
SHA-256 01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4
```

It already delegates preflight, official execution and validation to the
producer.  No CLI logic, argv surface or new bypass is required.  Thus the
combined implementation/test delta has exactly four unique paths: the oracle,
the producer and the two tests.  New package/design/prompts/review archives are
coordination records owned by T0/T7, not additional T4 implementation scope.

## Exact replacement start-gate semantics

The repair-1 package must require the producer to fail closed on one exact,
non-circular authority chain:

1. Preserve the original replacement package, design, T4 prompt and package
   approval as immutable predecessor identities:
   `decde34bcdc90db0bc69be446357e306cfe942c84a8d575902eddaa7d1ff6877`,
   `243f312182528b10a895cef679d195dcedfd97d7a2e02e388449ae3af313dd28`,
   `a1bffc42a381489dadd483edf2e6952d97ce236fbad3fe9ca82eb8b0ca862945`
   and
   `9616b3fb4d0999e782e164740f5815f6bcdf46a955910cd2bcfcae032bde75cf`.
2. Bind the immutable terminal failure identities
   `5aef8aec8511e5fa35df6459b7cd520b046e080d43f6c24fd95a8b46379d1779`
   and
   `6a8ab79495bad03c2d08742a6a6b79f3afc6df658eb7d7dcb20f145efa905b1e`.
3. Bind the formal terminal-review archive
   `7aa90e012e7d079d7c16256647d97db663293cf9ff6f5a4346130aa1d82482f1`
   and require its exact `REPAIR`, `FAIL`, class-A blocker ID and fresh-root
   unblock semantics.
4. Bind this clarification archive by its eventual exact SHA-256 and require
   its `CONTROL_PLANE_REPAIR`, exact four-path implementation/test scope and
   corrected Route-U evidence identities.
5. Record the current T7 authority predecessor
   `docs/handoffs/T7_current.md` at
   `c41a9a26146d16e1ab3c8c1bf69ea9e4f52cd3d3e853eaa783263cedd7e90e65`
   in the repair package and immutable package-review archive.  Do not require
   the mutable live handoff to retain that hash at execution time.  The final
   execution authority is the later immutable T7 repair-package approval and
   implementation delta-review archive, each of which must hash-bind this
   predecessor, the package, the repaired four source/test hashes and the
   exact gate label/tokens.
6. Likewise, do not make mutable live `status.md` or `T0_current.md` a
   circular execution identity.  Freeze their package-start predecessor
   hashes in the package/approval chain, and bind execution to a one-use
   immutable T0 dispatch that names the approved package, T7 archives, exact
   repaired source/test hashes and fresh absent root.
7. Continue to rehash the V3.0 domain, all 16 thresholds, formula/convention
   authorities, seven protected radial files, runtime and every original
   scientific source.  No alternative hash, fallback authority, environment
   selection, boolean escape or argument-selected gate is allowed.
8. `build_source_ledger()` must record the exact repaired producer and oracle,
   the unchanged CLI and every frozen source at start and end.  Any drift is a
   terminal failure.

This semantics retains current T7 authority without making a mutable handoff
an impossible post-review execution prerequisite.

## Required recheck and unblock conditions

Before any science authorization, T4 must provide zero-science evidence for:

```text
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src \
/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 \
-m pytest -q \
tests/unit/test_phase6_v3_hp_unitarity.py \
tests/regression/test_phase6_v3_hp_unitarity_publication.py

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src \
/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 \
scripts/phase6_v3_1_hp_unitarity.py preflight

.venv/bin/python -m ruff check \
src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py \
src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py \
tests/unit/test_phase6_v3_hp_unitarity.py \
tests/regression/test_phase6_v3_hp_unitarity_publication.py

git diff --check -- \
src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py \
src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py \
tests/unit/test_phase6_v3_hp_unitarity.py \
tests/regression/test_phase6_v3_hp_unitarity_publication.py
```

Mandatory negative tests must independently alter each immutable authority,
required verdict token, repaired source hash, terminal failure identity and
protected identity and obtain fail-closed rejection.  They must also prove
that the old `61e25ccb...`, current `c41a9a...` or any future live handoff hash
cannot be selected as an alternative at runtime; the authority comes only
through the single immutable reviewed chain.

The control-plane item is unblocked only when:

- a formal combined repair-1 package freezes the exact four unique
  implementation/test paths and this authority-chain semantics;
- T7 package review returns the package-specific bounded approval;
- the four repaired hashes pass a T7 implementation delta review;
- all zero-science positive/negative tests, preflight, Ruff and diff checks
  pass with the domain, thresholds, conventions and protected bytes exact;
- Root T0 creates a new one-use dispatch bound to those immutable approvals
  and a fresh absent output root.

Only after those conditions may Root T0 separately decide whether to authorize
a fresh official run.  The failed root and all of its Route-A/Route-U science
remain immutable evidence and may not be copied, resumed, cached or promoted
into a new PASS.

## Finding classification and liveness

```yaml
findings:
  - finding_id: v31u_auxiliary_radius_closed_boundary_roundoff
    class: BLOCKING_CURRENT_GATE
    status: unchanged
    completed_bounded_scientific_repairs: 0
  - finding_id: v31u_live_handoff_start_gate_recursion
    class: CONTROL_PLANE_REPAIR
    status: package repair required before execution
    scientific_bytes_changed: false
    blocks_package_freeze: false
    blocks_unrepaired_execution: true
incremental_review_state:
  passed_items: unchanged from archive 7aa90e012e7d079d7c16256647d97db663293cf9ff6f5a4346130aa1d82482f1
  failed_items:
    - v31u_route_u_auxiliary_geometry_totality
  partial_allowed_items: unchanged
  not_assessed_items: unchanged
repair_cycle:
  completed_bounded_scientific_repairs: 0
  same_substantive_blocker_remaining: true
  t0_adjudication_required: false
hold_details: null
```

## Authorization boundary

Root T0 may now freeze one combined bounded scientific-repair-1 package for
formal T7 package review and possible later T4 implementation.  This archive
does not itself dispatch or authorize T4, a producer, solver or artifact
execution.  It does not change the domain, any threshold, formula, convention,
seven protected radial bytes or science claim.  V3.1-U remains `FAIL`; V3.2,
artifact reuse and global GREEN remain forbidden.

This clarification is archive-only.  `status.md`, `T0_current.md`,
`T4_current.md`, `T7_current.md`, the terminal root and all implementation
files were not modified.
