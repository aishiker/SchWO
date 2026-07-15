# T7bx — Delta(kM)=0.1 Units Metadata Repair Independent Review

You are the existing T7 review task. Independently review T8ao's metadata-only
repair. You are not a repair or scientific-computation task.

## Start Gate

Begin only after T8ao reports exactly:

```text
GREEN / DELTA0P1 RISK-PILOT UNITS METADATA HARDENED
```

If the implementation commit, durable source backup, complete candidate tree,
repair ledger, 23 active files, status, or T8 handoff is missing or ambiguous,
stop and notify T0.

The durable review root is exactly:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot/quarantine/t8ao_pre_units_metadata/
```

## Required Reading

Read completely:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/superpowers/specs/2026-07-15-t8ao-t7bx-delta0p1-units-metadata-repair-design.md`
7. `docs/superpowers/plans/2026-07-15-t8ao-delta0p1-units-metadata-repair.md`
8. `docs/prompts/phase5_t8ao_delta0p1_units_metadata_repair.md`
9. this prompt
10. the four T8ao implementation/test paths
11. all active, source-backup, candidate, ledger, and existing quarantine
    files under the risk-pilot run directory

Use `receiving-code-review` and `verification-before-completion` as helpful;
the frozen design and this prompt control the decision.

## Frozen Pre-Repair Identity

```text
92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9  generation contract
79d4c0f596650dcfb4d63c7e40758ea4afa82d2fe0e0cd3de5aa088bbbfd5ccd  checkpoint_ledger.json
2e0a9fee1b6729466affd4c5f7f6e86c96e696e20882c9f4ad52ae3792d82957  risk_pilot_values.npz
2a9aa472e64747047cb28de90912eecf138b28884d87e8b8219e78d99482772f  risk_pilot_values.npz.json
461d040a180dfa8e5a743967285e67f8b682f8f67607f1c0c7a5c8ab2399d7bd  risk_pilot_sampling_audit.json
120ccd8f11e681bc6d2b3054bd7522ef331a282421f7661dd7888c993b052212  manifest.md
```

The six accepted T8aj/T4z anchor hashes are the exact values frozen in the
design and implementation plan. Any pre-repair identity mismatch is RED, not
an invitation to regenerate artifacts.

## Allowed Review Writes

```text
status.md
docs/handoffs/T7_current.md
docs/handoffs/archive/T7_2026-07-15_pre_t7bx_units_metadata_repair.md
```

Do not modify implementation, tests, scripts, configs, artifacts, T0/T4/T8
handoffs, accepted inputs, or unrelated handoffs.

## Required Independent Checks

The only accepted repaired schema is:

```text
phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering
```

1. **Implementation scope:** the T8ao implementation commit changes exactly
   the four frozen paths. No solver, adapter, runner, IO export, config,
   fixture, visualization, or unrelated path is included.
2. **Frozen sources:** independently verify the five pre-repair root hashes,
   all 22 old manifest entries, exact 23-file source backup, generation
   contract, and all six T8aj/T4z source anchors.
3. **Direct numerical identity:** without importing or calling T8ao migration
   or fingerprint helpers, load all ten source-backup/active NPZ pairs. Require
   identical non-metadata key sets, shapes, dtypes, `np.array_equal`, and
   SHA-256 of `np.save(BytesIO(), array, allow_pickle=False)` bytes.
4. **Metadata contract reconstruction:** independently reconstruct the exact
   v2 units registry, ordering registry, source fingerprint map, and canonical
   metadata-contract hash. Require equality with every declared hash.
5. **Required surfaces:** directly inspect nine per-frequency embedded
   metadata objects, nine sidecars, aggregate embedded/sidecar, checkpoint
   ledger, sampling audit, and manifest. Require exact schema, units,
   ordering, generation/metadata hash split, repair identity, source anchors,
   and pre-repair provenance.
6. **Coverage and actual arrays:** units keys must cover all and only the
   declared per-frequency and aggregate non-metadata arrays. Exact frequency,
   point, lmax, and axis ordering must match actual arrays. Coordinate values
   are expressed in `M`, angles/phases in radians, complex amplification and
   deltas dimensionless, masks Boolean.
7. **Journal/cardinality/provenance:** require a complete repair ledger,
   candidate hashes, exact 23 active files, exact 22 non-self manifest
   records, no active `.tmp`, no candidate/source ambiguity, and no existing
   runner-cache quarantine item treated as active.
8. **Legacy/scientific preservation:** except for the frozen metadata mutation
   allowlist, legacy metadata values must be unchanged. Independently verify
   all masks true, exact final-pair maxima, 224 phase steps and their maximum,
   38 magnitude-dominance failures, and 51 strict interior extrema. The
   scientific state remains YELLOW for later targeted refinement.
9. **Tests and isolation:** run focused tests, Ruff, full pytest, source-hash,
   commit-scope, forbidden code/config/fixture diff, and forbidden downstream-
   output checks freshly.

## Required Commands

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_tablei_risk_pilot.py \
  tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
.venv/bin/python -m ruff check \
  src/schwgw/io/tablei_risk_pilot.py \
  scripts/phase5_repair_delta0p1_risk_pilot_metadata.py \
  tests/unit/test_tablei_risk_pilot.py \
  tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
PYTHONPATH=src .venv/bin/python -m pytest -q
find \
  runs/phase5/fig5_fig6_dense_scan_production \
  runs/phase5/fig5_fig6_delta0p05_targeted \
  runs/phase5/fig5_fig6_paper_style_candidates \
  -maxdepth 2 -type f -print 2>/dev/null | sort
```

The last command must be empty. Run a separate direct-NPZ Python audit that
does not import `schwgw.io.tablei_risk_pilot` and report the full independently
reconstructed fingerprint/metadata-contract result.

## Exact Decision

Record exactly one:

```text
ACCEPT GREEN / DELTA0P1 RISK-PILOT ARTIFACT CONTRACT REPAIRED
ACCEPT YELLOW / DELTA0P1 RISK-PILOT METADATA EVIDENCE INCOMPLETE
REJECT RED / DELTA0P1 RISK-PILOT METADATA REPAIR INVALID
```

GREEN requires all nine checks. An artifact-contract GREEN must separately
retain:

```text
YELLOW / TARGETED ADAPTIVE FREQUENCY REFINEMENT REQUIRED
```

This does not authorize any new frequency or production calculation.

Update status/archive/handoff and notify T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636` with the exact decision,
implementation commit, independently reconstructed metadata-contract hash,
new root hashes, array count/fingerprint result, scientific preservation
result, fresh tests, and review-only changed paths.

Do not repair T8ao, push GitHub, dispatch another task, or start `0.05`,
`0.025`, full-grid, plot, fixture, Kirchhoff, or paper-style work. Only T0 may
close the gate, apply the project major-node GitHub rule, and design the next
scientific stage.
