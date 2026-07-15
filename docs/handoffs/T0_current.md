# T0 Current Handoff

Date: 2026-07-15

Thread: T0, project coordination and gate scheduling.

## Current Status

The previous bounded risk-pilot chain closed at:

```text
T4z GREEN -> T7bv ACCEPT GREEN -> T8an GREEN -> T7bw REJECT RED
```

The user has reviewed and approved a separately bounded repair design. T0 is
freezing and dispatching:

```text
T8ao metadata-only repair -> exact GREEN only -> T7bx independent review
```

No new scientific frequency, full-grid production, plot, fixture, Kirchhoff,
or paper-style work is authorized.

## Approved Design And Frozen Documents

- Design:
  `docs/superpowers/specs/2026-07-15-t8ao-t7bx-delta0p1-units-metadata-repair-design.md`
  at commit `529ee60`.
- Implementation plan:
  `docs/superpowers/plans/2026-07-15-t8ao-delta0p1-units-metadata-repair.md`.
- T8ao prompt:
  `docs/prompts/phase5_t8ao_delta0p1_units_metadata_repair.md`.
- T7bx prompt:
  `docs/prompts/phase5_t7bx_delta0p1_units_metadata_repair_review.md`.

The plan/prompts are frozen only after their T0 coordination commit is
recorded in `status.md`. The predecessor handoff is archived at:

```text
docs/handoffs/archive/T0_2026-07-15_pre_t8ao_units_metadata_repair_dispatch.md
```

## Exact Repair Scope

T8ao implementation commit may contain exactly:

```text
src/schwgw/io/tablei_risk_pilot.py
scripts/phase5_repair_delta0p1_risk_pilot_metadata.py
tests/unit/test_tablei_risk_pilot.py
tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
```

Additional T8ao writes are restricted to the existing risk-pilot run tree,
`status.md`, T8 current handoff, and the exact T8 archive named in the prompt.

## Frozen Identity

- Generation contract:
  `92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9`.
- Pre-repair root hashes:
  - ledger `79d4c0f596650dcfb4d63c7e40758ea4afa82d2fe0e0cd3de5aa088bbbfd5ccd`;
  - aggregate NPZ `2e0a9fee1b6729466affd4c5f7f6e86c96e696e20882c9f4ad52ae3792d82957`;
  - aggregate JSON `2a9aa472e64747047cb28de90912eecf138b28884d87e8b8219e78d99482772f`;
  - audit `461d040a180dfa8e5a743967285e67f8b682f8f67607f1c0c7a5c8ab2399d7bd`;
  - manifest `120ccd8f11e681bc6d2b3054bd7522ef331a282421f7661dd7888c993b052212`.
- Active cardinality is exactly 23 physical files; the manifest has exactly
  22 non-self records.
- Repaired schema is exactly
  `phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering`.

## Scientific Interpretation That Must Not Change

- The T7bw RED is an artifact-contract failure caused by absent explicit
  units, not a numerical-convergence failure.
- Every non-`metadata_json` NPZ array must remain identical by key, shape,
  dtype, `np.array_equal`, and canonical `.npy` SHA-256.
- All 224 adjacent phase steps remain finite and below `pi/2`; frozen maximum
  is `1.4363184904108022 rad`.
- The 38 magnitude-dominance failures and 51 strict interior extrema remain
  scientific evidence requiring a later, separately designed adaptive stage.
- T8ao must not recompute scientific values. T7bx independently reconstructs
  the preservation evidence after an exact T8ao GREEN.

## Automatic Chain

- Target T8 task: `019f5ece-f578-7b91-8f61-df882c656591`.
- Target T7 task: `019f5ed1-b421-7ec2-9bac-8d134855a1ed`.
- T8ao uses `gpt-5.6-sol`, reasoning `high`.
- Only exact
  `GREEN / DELTA0P1 RISK-PILOT UNITS METADATA HARDENED` may dispatch T7bx.
- T7bx is read-only except its own status/handoff/archive records and returns
  only to T0.
- YELLOW, RED, incomplete, missing artifact, failed test, scope drift, or
  ambiguous state stops the chain.
- A clear capacity/system interruption may resume the same task with
  `gpt-5.6-terra/high` only after ledger/source/candidate/active hashes and
  process state prove it is not a scientific, test, scope, or provenance
  failure.

## Forbidden Actions

- Do not run the T8an scientific runner or any solver/polarization/radial path.
- Do not change numerical arrays, frequencies, points, lmax, masks, branches,
  tolerances, warnings, cache counts, adapter counts, or selected generation
  provenance.
- Do not start `0.05`, `0.025`, full-grid, plotting, fixture, Kirchhoff,
  interpolation, smoothing, fill, or paper-style work.
- Do not create a new T7/T8 task if the existing target is unavailable.
- T8ao/T7bx must not push GitHub.

## Exact Next Task

After the coordination commit is frozen, send the T8ao prompt to the existing
T8 task and create a monitor for exact-GREEN-only T7bx dispatch and T0
closeout. No user action is required unless dispatch or verification fails.

## Definition Of Done

- T8ao produces one exact decision after array-identity, metadata, provenance,
  focused/Ruff/full tests, scope, and forbidden-output checks.
- Exact T8ao GREEN is independently reviewed by T7bx.
- T0 verifies the final exact decision, updates this handoff and `status.md`,
  applies the project major-node GitHub rule only for an independently
  accepted GREEN, and stops the monitor.
- No later scientific stage is started automatically.
