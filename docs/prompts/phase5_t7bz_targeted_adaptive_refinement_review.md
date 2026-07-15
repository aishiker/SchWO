# T7bz — Targeted Adaptive Frequency Evidence Independent Review

You are the existing T7 review task. Independently review T8ap's thirteen-
frequency point-only adaptive evidence. You are not a repair task and must not
start another midpoint, production grid, plot, fixture, or paper stage.

## Start Gate

Begin only after T8ap reports exactly:

```text
GREEN / TARGETED ADAPTIVE FREQUENCY EVIDENCE GENERATED
```

If the implementation commit, thirteen transaction pairs, ledger, aggregate,
audit, manifest, source/gate hashes, status, handoff or fresh T8 verification
is absent or ambiguous, stop and notify T0.

## Required Reading

Read completely:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T4_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T8_current.md`
7. `docs/superpowers/specs/2026-07-15-t4aa-t8ap-targeted-adaptive-refinement-design.md`
8. `docs/superpowers/plans/2026-07-15-t8ap-targeted-adaptive-refinement.md`
9. `docs/prompts/phase5_t8ap_targeted_adaptive_refinement.md`
10. this prompt
11. all five T8ap implementation paths, all active artifacts, accepted T8aj
    source triplet, accepted T8ao/T7bx package, and accepted T4aa/T7by gate

Review by direct loading and independent reconstruction. Do not call T8ap
loader, aggregation, sampling metric, migration, or acceptance helpers.

## Allowed Writes

```text
status.md
docs/handoffs/T7_current.md
docs/handoffs/archive/T7_2026-07-15_pre_t7bz_targeted_adaptive_review.md
```

Do not modify implementation, tests, scripts, configs, artifacts, accepted
sources, T0/T4/T8 handoffs, or unrelated handoffs.

## Independent Checks

1. **Commit/scope:** the T8ap implementation commit contains exactly the five
   frozen paths and no radial solver/envelope, source, config, viz, fixture,
   Kirchhoff or unrelated diff.
2. **Immutable sources and gate:** independently verify all T8aj, T8ao/T7bx,
   T4aa/T7by hashes/contracts/schema, adapter identity and source provenance.
3. **Transactions and cardinality:** direct-load thirteen NPZ/JSON pairs;
   require exact tokens/order, points, arrays, shapes, actual dtypes, units,
   lmax windows, histories/final pairs, masks, finiteness, warnings and counts.
   Require exactly 31 active files and 30 manifest records with no active temp.
4. **Contracts/provenance:** independently reconstruct generation and metadata
   hashes, units/dtype/ordering registries and canonical array fingerprints;
   verify ledger, atomic completion, resume, quarantine exclusion, Git/code/
   config/source/gate hashes and every manifest hash.
5. **Aggregate identity:** independently stack the thirteen transactions and
   require exact key/order/shape/dtype/value identity with the aggregate. Do
   not trust the saved sampling audit as proof.
6. **Exact sequences:** direct-load immutable source rows and construct only:

```text
[0.3,0.35,0.4,0.45,0.5]
[0.75,0.8,0.85,0.9,0.95,1.0]
[1.5,1.55,1.6,1.65,1.7,1.725,1.75]
[2.75,2.775,2.8,2.85,2.9,2.95,3.0]
[3.75,3.775,3.8,3.85,3.9,3.95,4.0]
```

7. **Observed phase:** for all `27*8*2 = 432` adjacent records, independently
   apply frequency-axis `np.unwrap(np.angle(F))`; every step must be finite and
   strictly `<pi/2`. Report global and per-sequence maxima with attribution.
8. **Hierarchical magnitude:** for exactly `13*2*8*2 = 416` child records use
   `abs(a-b)/max(1,a,b)` on magnitudes and require each child step
   `<= exact_parent_step + 2e-15`. A `0.05` child uses only its exact `0.1`
   parent; a `0.025` child uses only its exact `0.05` parent. Report complete
   failure membership, parent/child values, total variation, cancellation,
   largest-step attribution, all strict extrema, and next midpoint only for a
   scientific YELLOW. Never invent another threshold.
9. **Tests/isolation:** run focused tests, Ruff on the exact five paths, fresh
   full pytest, source/scope checks and forbidden-output searches. Classify
   known warnings and reject any new failure or downstream product.

Required commands include:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_tablei_adaptive_refinement.py \
  tests/regression/test_targeted_adaptive_refinement_script.py
.venv/bin/python -m ruff check \
  src/schwgw/io/tablei_adaptive_refinement.py \
  src/schwgw/io/__init__.py \
  scripts/phase5_run_targeted_adaptive_refinement.py \
  tests/unit/test_tablei_adaptive_refinement.py \
  tests/regression/test_targeted_adaptive_refinement_script.py
PYTHONPATH=src .venv/bin/python -m pytest -q
find runs/phase5/fig5_fig6_dense_scan_production \
     runs/phase5/fig5_fig6_delta0p025_uniform \
     runs/phase5/fig5_fig6_paper_style_candidates \
     -maxdepth 2 -type f -print 2>/dev/null | sort
find runs/phase5/fig5_fig6_targeted_adaptive_refinement \
     -type f \( -name '*.png' -o -name '*.pdf' -o -name '*.svg' \) \
     -print 2>/dev/null | sort
```

Both forbidden-output commands must be empty. Pre-existing accepted
review-grid plots are historical inputs outside these searches and must not be
mistaken for new T8ap output.

## Exact Decision

Record exactly one:

```text
ACCEPT GREEN / TARGETED ADAPTIVE FREQUENCY EVIDENCE ACCEPTED
ACCEPT YELLOW / FURTHER LOCAL FREQUENCY REFINEMENT REQUIRED
REJECT RED / TARGETED ADAPTIVE FREQUENCY ARTIFACT INVALID
```

GREEN requires the full artifact gate, all 432 phase records and all 416
hierarchical magnitude records to pass. It permits only T0 to design a later
nonuniform production-grid completion and does not prove global convergence.

YELLOW requires a valid artifact but failed scientific child records. Record
every exact failing parent/child interval, point, component, complex/magnitude/
phase values and candidate next midpoint; do not authorize it.

RED is reserved for invalid computation, artifact, source, provenance, test or
scope. Never downgrade RED because metrics look favorable.

Update only the allowed review records and notify T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636` with exact decision, reviewed hashes,
independent 432/416 evidence, tests, scope and non-claims. Do not repair T8ap,
dispatch another task, push GitHub, or start later work.
