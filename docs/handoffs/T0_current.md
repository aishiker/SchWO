# T0 Current Handoff

Date: 2026-07-15

Thread: T0, project coordination and gate scheduling.

## Current Status

The bounded metadata-only repair chain is closed:

```text
T8ao GREEN -> T7bx ACCEPT GREEN -> T0 ACCEPT GREEN
```

T0 exact artifact-contract decision:

```text
ACCEPT GREEN / DELTA0P1 RISK-PILOT METADATA REPAIR GATE CLOSED
```

The independent scientific state remains deliberately separate:

```text
YELLOW / TARGETED ADAPTIVE FREQUENCY REFINEMENT REQUIRED
```

This closeout accepts the repaired artifact contract only. It does not
authorize a new frequency, `0.05`/`0.025` scan, full grid, plot, fixture,
Kirchhoff, interpolation, smoothing, fill, or paper-style stage.

## Accepted Implementation And Contracts

- T8ao implementation commit:
  `689c0759e790ccdc614f4b5a4ddbd48585d914fa`.
- Its path set is exactly:

```text
scripts/phase5_repair_delta0p1_risk_pilot_metadata.py
src/schwgw/io/tablei_risk_pilot.py
tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
tests/unit/test_tablei_risk_pilot.py
```

- Generation contract remains:
  `92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9`.
- Metadata contract is:
  `1bd32a3e2988ef786c3777859f76f8d38a276cdacd12cdadba7f79e843ca0161`.
- Accepted schema is:
  `phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering`.
- Repair ledger SHA-256 is:
  `ec4c6784a26e53b583c032fe360f51b940f5dfe6d58e705b2c3412fbeb9c717c`.

## Independent Acceptance Evidence

- T7bx exact decision:
  `ACCEPT GREEN / DELTA0P1 RISK-PILOT ARTIFACT CONTRACT REPAIRED`.
- T7bx did not import/call the T8ao migration or fingerprint helpers.
- Ten source-backup/active NPZ pairs and all 219 non-metadata arrays match by
  key order/set, shape, dtype, `np.array_equal`, and canonical
  `np.save(..., allow_pickle=False)` SHA-256. Candidate fingerprints match too.
- Source, candidate, and active packages each contain 23 files. Each manifest
  contains 22 non-self records. The complete journal contains 23 copied-source
  and 23 replaced paths; no active `.tmp` or third state exists.
- Units cover all and only the 22 per-frequency and 21 aggregate arrays.
  Actual frequency, point, lmax, history/final/aggregate axes, coordinates,
  phases, complex amplitudes, and Boolean masks match the frozen ordering and
  units registries.
- Legacy metadata outside the mutation allowlist and all scientific values are
  unchanged. The historical runner-cache quarantine remains excluded.

## T0 Fresh Verification

- Direct no-helper NPZ audit:
  `T0_DIRECT_NPZ_IDENTITY=PASS pairs=10 arrays=219 fingerprints=219`.
- Cardinality/journal audit:
  `T0_CARDINALITY_AND_LEDGER=PASS source=23 candidate=23 active=23 manifest=22 copied=23 replaced=23`.
- Schema/hash surfaces, commit scope, forbidden commit diff, and forbidden
  downstream-output checks: PASS.
- Focused pytest: `18 passed in 2.23s`.
- Ruff: `All checks passed!`.
- Full pytest: `624 passed, 117 skipped, 1 xfailed, 101 warnings, 81 subtests
  passed in 333.70s`.
- The first T0 read-only ledger audit used a nonexistent `copied_paths` key;
  inspection confirmed the frozen key is `copied_source_paths`. The corrected
  audit passed. No artifact, implementation, or migration state changed.

## Scientific State Retained

- All masks remain true.
- Final-pair maxima remain `6.136118112992297e-11` plus and
  `5.492389935680416e-10` cross.
- All 224 adjacent phase steps remain finite with maximum
  `1.4363184904108022 < pi/2`.
- Exactly 38 magnitude-dominance failures and 51 strict interior extrema
  remain. These are scientific evidence for a later, separately designed
  adaptive-frequency stage, not defects that metadata repair can remove.

## Coordination And Archive

- T7 current review: `docs/handoffs/T7_current.md`.
- T8 current implementation record: `docs/handoffs/T8_current.md`.
- Pre-closeout T0 handoff:
  `docs/handoffs/archive/T0_2026-07-15_pre_t8ao_t7bx_metadata_repair_closeout.md`.
- The obsolete heartbeat
  `monitor-t8ao-t7bx-units-metadata-repair` must be deleted after the GitHub
  synchronization record is complete.

## GitHub Major-Node Handling

This independently accepted high-risk artifact-contract repair is a major
node under `project.md`. GitHub synchronization is pending the scope-explicit
closeout commit and non-force push. Only this chain's committed implementation,
frozen design/plan/prompts, the T4 radial-gate note/handoff, and reviewed
T0/T7/T8/status coordination records may be included. Unrelated
T1/T2/T3/T5/T6 working-tree changes and ignored `runs/` products remain
excluded.

## Exact Next Task

Complete the scope-explicit non-force GitHub synchronization and record its
remote verification, then stop the heartbeat monitor. Do not dispatch a later
scientific task.

No next-stage prompt is provided because adaptive-frequency refinement has not
yet been designed, reviewed, frozen, or authorized. The release condition is a
new T0 design that preserves the accepted v2 artifact contract and explicitly
defines frequencies, radial/Q018 support, checkpoints, scientific stop rules,
scope, and an independent T7 review.

## Definition Of Done

- `status.md` and this handoff record the exact artifact GREEN and retained
  scientific YELLOW.
- Scope-explicit closeout commits are pushed non-force to private `origin/main`
  and remote equality is freshly verified.
- The obsolete monitor is deleted.
- No adaptive, production, plotting, fixture, Kirchhoff, or paper task starts
  automatically.
