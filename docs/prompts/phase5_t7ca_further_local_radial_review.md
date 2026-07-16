# T7ca — Further-Local Radial Gate Independent Review

You are the existing T7 task. Independently review T4ab's 24-frequency radial
gate and exact adapter. You are review-only: do not repair T4ab or start T8aq.

## Start Gate

Begin only after T4ab reports exactly:

```text
GREEN / FURTHER LOCAL RADIAL GATE READY
```

Before changing T7 current handoff, archive its exact T7bz bytes to:

```text
docs/handoffs/archive/T7_2026-07-16_pre_t7ca_further_local_radial_review.md
```

and require SHA-256
`8edd808e543460f943eb217af248b2edd52d7ea7d1827e99315b4f49f6521d9e`.
If commit, 24 checkpoints, artifacts, status, handoff, or fresh T4 verification
is missing or ambiguous, stop and notify T0.

## Required Reading

Read completely: `project.md`, `status.md`, T0/T4/T7/T8 current handoffs,
the frozen further-local design, T4ab plan, T4ab prompt, this prompt, all five
authorized implementation paths, all gate artifacts, and immutable T7bz
evidence. Review from raw records and independent recomputation.

## Allowed Writes

```text
status.md
docs/handoffs/T7_current.md
docs/handoffs/archive/T7_2026-07-16_pre_t7ca_further_local_radial_review.md
```

Do not modify implementation, tests, scripts, configs, artifacts, accepted
sources, T0/T4/T8 handoffs, or unrelated changes.

## Independent Checks

1. **Commit/scope:** exact five frozen paths and no IO/scattering/observable/
   config/fixture/source diff.
2. **Contract/cardinality:** independently derive 81,792 rows from exact
   lmax maxima, both sectors and eight points; require unique complete keys and
   24 complete/PASS checkpoints.
3. **Fresh classification:** deterministic sample spanning all frequencies,
   sectors, points, and structured classes; zero default-other.
4. **Direct oracle:** exact key equality across raw/oracle/preflight without
   symmetry assumptions. Recompute maxima and producer anchors. For a fresh
   complementary matrix select each nonempty group's lexicographic median,
   then last transition for every uncovered point; run fresh precision and
   tolerance variants. Verify empty groups explicitly.
5. **Envelope:** independent literal expansion equals every raw transition;
   reject interpolation, inferred membership, IO-loaded envelope, or extra
   frequency.
6. **Adapter:** direct anchors equal oracle; default-covered calls stay zero;
   wrong M/k/token/radius/point/ell/sector/boundary/tolerance fails closed.
7. **Provenance:** independently reconstruct classification and final-adapter
   snapshots, exact five-path commit/blobs, atomic hashes, quarantine
   exclusion, requested/actual precision, manifest, preflight, and hash bridge.
8. **Tests:** focused, Ruff on exact five paths, fresh full pytest; classify
   known warnings and allow no new failure.
9. **Isolation:** no T8aq, full/uniform scan, plot, fixture, Kirchhoff, paper,
   or unrelated implementation output.

Required commands include:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/physics/test_q018_production_integration_design.py \
  tests/physics/test_radial_solver.py
.venv/bin/python -m ruff check \
  scripts/phase5_further_local_radial_gate.py \
  src/schwgw/numerics/q018_further_local_envelope.py \
  src/schwgw/numerics/radial_solver.py \
  tests/physics/test_q018_production_integration_design.py \
  tests/physics/test_radial_solver.py
PYTHONPATH=src .venv/bin/python -m pytest -q
find runs/phase5/fig5_fig6_further_local_refinement \
     runs/phase5/fig5_fig6_dense_scan_production \
     runs/phase5/fig5_fig6_delta0p025_uniform \
     runs/phase5/fig5_fig6_delta0p0125_uniform \
     runs/phase5/fig5_fig6_paper_style_candidates \
     -maxdepth 2 -type f -print 2>/dev/null | sort
```

The final command must be empty.

## Exact Decision

Record exactly one:

```text
ACCEPT GREEN / FURTHER LOCAL RADIAL GATE ACCEPTED
ACCEPT YELLOW / FURTHER LOCAL RADIAL EVIDENCE INCOMPLETE
REJECT RED / FURTHER LOCAL RADIAL GATE INVALID
```

GREEN authorizes only T0 to dispatch the separately frozen T8aq package. It
does not authorize T7 to dispatch, add frequencies, start production/plots/
fixtures/paper/Kirchhoff, or push GitHub.

Update only review records and notify T0 with exact decision, reviewed commit
and hashes, independent counts/maxima, tests, scope, and non-claims. Do not
repair or start downstream work.
