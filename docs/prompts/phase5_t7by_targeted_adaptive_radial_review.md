# T7by — Targeted Adaptive Radial Gate Independent Review

You are the existing T7 task. Independently review the T4aa thirteen-frequency
radial/Q018 classification and exact adapter. You are review-only: do not
repair T4aa and do not start T8ap.

## Start Gate

Begin only after T4aa reports exactly:

```text
GREEN / TARGETED ADAPTIVE RADIAL GATE READY
```

If the decision, five-path implementation commit, thirteen checkpoints, gate
artifacts, status, handoff, or fresh T4 verification is missing or ambiguous,
stop and notify T0.

## Required Reading

Read completely:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T4_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/superpowers/specs/2026-07-15-t4aa-t8ap-targeted-adaptive-refinement-design.md`
7. `docs/superpowers/plans/2026-07-15-t4aa-targeted-adaptive-radial-gate.md`
8. `docs/prompts/phase5_t4aa_targeted_adaptive_radial_gate.md`
9. this prompt
10. all five authorized implementation paths and every T4aa gate artifact

The frozen design and prompt control. Review from raw records and independent
recomputation; do not treat T4aa summaries as proof.

## Allowed Writes

```text
status.md
docs/handoffs/T7_current.md
docs/handoffs/archive/T7_2026-07-15_pre_t7by_targeted_adaptive_radial_review.md
```

Do not modify implementation, tests, scripts, configs, artifacts, T0/T4/T8
handoffs, accepted sources, or unrelated handoffs. Preserve unrelated changes.

## Independent Nine Checks

1. **Commit and scope:** the T4aa implementation commit changes exactly the
   five frozen paths and no IO/scattering/observable/config/fixture/source path.
2. **Contract and cardinality:** independently derive `42,224` records from
   thirteen frequencies, exact lmax maxima, both sectors and eight points;
   require unique complete keys and thirteen exact complete/PASS checkpoints.
3. **Fresh default classification:** recompute a deterministic sample spanning
   every frequency, both sectors, all points and every structured class;
   require zero unstructured/default-other records and no omission.
4. **Direct oracle:** require exact `(kM, sector, ell, point_id)` key equality
   across raw records, oracle validation and resume preflight without assuming
   odd/even symmetry. Recompute producer maxima and its frozen first/last plus
   point-coverage anchor rule. For a fresh complementary matrix, independently
   select the lexicographic median key in every nonempty `(kM,sector)` group,
   then add the lexicographically last transition for each exact point ID not
   already represented. Run the deduplicated union at fresh precision and
   tolerance settings. Verify explicit zero-transition groups and never invent
   an oracle anchor for them.
5. **Envelope identity:** expand the literal module independently and require
   exact equality with all raw transitions; reject interpolation, inferred
   membership, import-time run-file loading, or an unstated frequency.
6. **Adapter behavior:** direct-match anchors equal oracle evidence;
   default-covered modes make zero adapter calls; wrong M/k/token/radius/point/
   ell/sector/boundary/tolerance fails closed with exact reasons.
7. **Checkpoint and provenance:** independently reconstruct the classification
   snapshot (final gate script, pre-adapter radial blob, oracle, Table-I and
   frozen docs) and separately the final-adapter snapshot (literal envelope,
   final radial blob, exact five-path commit/blobs). Verify their hash bridge,
   atomic filenames, output hashes, quarantine exclusion, backend requested/
   actual precision, manifest and resume. A checkpoint must compare against
   the classification snapshot, not the later radial blob.
8. **Tests and quality:** run focused tests, Ruff on the five paths, and fresh
   full pytest. Known warnings must be classified; no new failure is allowed.
9. **Isolation:** require no T8ap artifact, full/uniform scan, plot, fixture,
   Kirchhoff, paper output, or unrelated implementation change.

At minimum run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/physics/test_q018_production_integration_design.py \
  tests/physics/test_radial_solver.py
.venv/bin/python -m ruff check \
  scripts/phase5_targeted_adaptive_radial_gate.py \
  src/schwgw/numerics/q018_targeted_adaptive_envelope.py \
  src/schwgw/numerics/radial_solver.py \
  tests/physics/test_q018_production_integration_design.py \
  tests/physics/test_radial_solver.py
PYTHONPATH=src .venv/bin/python -m pytest -q
find runs/phase5/fig5_fig6_targeted_adaptive_refinement \
     runs/phase5/fig5_fig6_dense_scan_production \
     runs/phase5/fig5_fig6_paper_style_candidates \
     -maxdepth 2 -type f -print 2>/dev/null | sort
```

The final command must be empty.

## Exact Decision

Record exactly one:

```text
ACCEPT GREEN / TARGETED ADAPTIVE RADIAL GATE ACCEPTED
ACCEPT YELLOW / TARGETED ADAPTIVE RADIAL EVIDENCE INCOMPLETE
REJECT RED / TARGETED ADAPTIVE RADIAL GATE INVALID
```

GREEN means only that T0 may dispatch the separately frozen T8ap package. It
does not authorize T7 to dispatch T8ap or authorize new frequencies, full
production, plots, fixtures, paper work, or GitHub action.

Update only the allowed review records and notify T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636` with exact decision, reviewed commit
and artifact hashes, independent counts/maxima, tests, and scope evidence. Do
not repair T4aa, push GitHub, or start downstream work.
