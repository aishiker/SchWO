# T7cb — Further-Local Frequency Evidence Independent Review

You are the existing T7 review task. Independently review T8aq's 24-frequency
point-only evidence. You are not a repair task and must not start another
midpoint, production grid, plot, fixture, Kirchhoff, or paper stage.

## Start Gate

Begin only after T8aq reports exactly:

```text
GREEN / FURTHER LOCAL FREQUENCY EVIDENCE GENERATED
```

If implementation commit, 24 transaction pairs, ledger, aggregate, audit,
manifest, source/gate hashes, status, handoff, or fresh verification is absent
or ambiguous, stop and notify T0.

## Required Reading

Read completely: `project.md`, `status.md`, T0/T4/T7/T8 handoffs, frozen
further-local design, T8aq plan/prompt, this prompt, all five implementation
paths and active artifacts, accepted T8aj/T8ao/T8ap sources, archived T7bz
evidence, and accepted T4ab/T7ca gate.

Review by direct loading and independent reconstruction. Do not call T8aq
loader, aggregation, sampling, migration, or acceptance helpers.

## Allowed Writes

```text
status.md
docs/handoffs/T7_current.md
docs/handoffs/archive/T7_2026-07-16_pre_t7cb_further_local_review.md
```

Do not modify implementation, tests, scripts, configs, artifacts, sources, or
T0/T4/T8 handoffs.

## Independent Checks

1. **Commit/scope:** exact five paths, predates first transaction, contract
   binds commit/blobs, and no radial/source/config/viz/fixture/Kirchhoff diff.
2. **Sources/gate:** independently verify every T8aj/T8ao/T8ap/T7bz and
   T4ab/T7ca hash, contract, schema, adapter, snapshot, and provenance field.
3. **Transactions/cardinality:** direct-load 24 NPZ/JSON pairs; exact tokens,
   order, points, arrays, shapes, actual dtypes, units, lmax, histories/final
   pairs, masks, finiteness, warnings, counts; exact 53/52 and no active temp.
4. **Contracts/provenance:** independently reconstruct generation/metadata
   hashes, registries, fingerprints, ledger, atomic completion, resume,
   quarantine exclusion, Git/code/source/gate hashes, and manifest.
5. **Aggregate:** independently stack all 24 transactions and require exact
   key/order/shape/dtype/value identity. Do not trust the audit as proof.
6. **Sequences:** direct-load immutable rows and build only the five literal
   sequences in design Section 6.
7. **Phase:** for all `51*8*2=816` records apply frequency-axis
   `np.unwrap(np.angle(F))`; every step finite and strictly `<pi/2`. Report
   complete maxima and attribution.
8. **Hierarchy:** for exactly `24*2*8*2=768` grandchild records use
   `abs(a-b)/max(1,a,b)` and require each `<=` its exact T7bz parent-child step
   `+2e-15`. Reconstruct the literal 24-row map, never infer float adjacency,
   and report complete failures, parent/child complex/magnitude/phase values,
   total variation, cancellation, largest steps, all extrema, and diagnostic
   next midpoint only for YELLOW. Invent no threshold.
9. **Tests/isolation:** focused tests, Ruff, fresh full pytest, scope/source
   checks, known-warning classification, and empty forbidden outputs.

Required commands include:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_tablei_further_local_refinement.py \
  tests/regression/test_further_local_refinement_script.py
.venv/bin/python -m ruff check \
  src/schwgw/io/tablei_further_local_refinement.py \
  src/schwgw/io/__init__.py \
  scripts/phase5_run_further_local_refinement.py \
  tests/unit/test_tablei_further_local_refinement.py \
  tests/regression/test_further_local_refinement_script.py
PYTHONPATH=src .venv/bin/python -m pytest -q
find runs/phase5/fig5_fig6_dense_scan_production \
     runs/phase5/fig5_fig6_delta0p025_uniform \
     runs/phase5/fig5_fig6_delta0p0125_uniform \
     runs/phase5/fig5_fig6_paper_style_candidates \
     -maxdepth 2 -type f -print 2>/dev/null | sort
find runs/phase5/fig5_fig6_further_local_refinement \
     -type f \( -name '*.png' -o -name '*.pdf' -o -name '*.svg' \) \
     -print 2>/dev/null | sort
```

Both forbidden-output commands must be empty.

## Exact Decision

Record exactly one:

```text
ACCEPT GREEN / FURTHER LOCAL FREQUENCY EVIDENCE ACCEPTED
ACCEPT YELLOW / FURTHER LOCAL FREQUENCY REFINEMENT REQUIRED
REJECT RED / FURTHER LOCAL FREQUENCY ARTIFACT INVALID
```

GREEN requires the full artifact gate and all 816 phase plus 768 hierarchy
records to pass. It permits only T0 to interpret whether a later nonuniform
production completion is justified; it proves no global convergence.

YELLOW requires a valid artifact but failed scientific records. Record every
exact failure and diagnostic next midpoint without authorization. RED is for
invalid computation/artifact/source/provenance/test/scope and may not be
downgraded by favorable metrics.

Update only review records and notify T0 with exact decision, reviewed hashes,
independent 816/768 evidence, tests, scope, and non-claims. Do not repair,
dispatch another task, push GitHub, or start later work.
