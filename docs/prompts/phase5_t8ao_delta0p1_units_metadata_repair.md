# T8ao — Delta(kM)=0.1 Risk-Pilot Units Metadata Repair

You are the existing T8 task. Repair only the active T8an artifact metadata
contract. Do not rerun any scientific calculation.

## Start Gate

Begin only after T0 confirms all of the following:

```text
REJECT RED / DELTA0P1 RISK PILOT INVALID
design commit 529ee60
user reviewed the T8ao/T7bx design and authorized execution
```

The RED cause is missing explicit units metadata. Numerical convergence,
finiteness, checkpoint consistency, and phase-step safety passed. The existing
38 magnitude-dominance failures and 51 extrema remain scientific evidence and
must not be altered or reinterpreted.

## Required Reading And Skills

Read completely:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/superpowers/specs/2026-07-15-t8ao-t7bx-delta0p1-units-metadata-repair-design.md`
7. `docs/superpowers/plans/2026-07-15-t8ao-delta0p1-units-metadata-repair.md`
8. `docs/prompts/phase5_t7bx_delta0p1_units_metadata_repair_review.md`
9. this prompt
10. `src/schwgw/io/tablei_risk_pilot.py`
11. both existing T8an focused test files
12. all 23 active risk-pilot files and existing quarantine provenance

Use `executing-plans`, `test-driven-development`, `systematic-debugging` for
unexpected failures, and `verification-before-completion`.

## Frozen Inputs

Generation contract:

```text
92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9
```

Repaired metadata schema:

```text
phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering
```

Root artifact hashes:

```text
79d4c0f596650dcfb4d63c7e40758ea4afa82d2fe0e0cd3de5aa088bbbfd5ccd  checkpoint_ledger.json
2e0a9fee1b6729466affd4c5f7f6e86c96e696e20882c9f4ad52ae3792d82957  risk_pilot_values.npz
2a9aa472e64747047cb28de90912eecf138b28884d87e8b8219e78d99482772f  risk_pilot_values.npz.json
461d040a180dfa8e5a743967285e67f8b682f8f67607f1c0c7a5c8ab2399d7bd  risk_pilot_sampling_audit.json
120ccd8f11e681bc6d2b3054bd7522ef331a282421f7661dd7888c993b052212  manifest.md
```

Accepted T8aj/T4z anchors:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
ee051831e1da7ebb250cab37d7da3a64d8a57298b445577f238d9cefae319d54
8f6d23da0894d0abfb42867bf911b9da95090ad5293bc76289daf4522e4067f9
59e99ade6993eab6d570f8a2ad18f0778595f7309fbb87fbf1edf32903b80968
```

Any mismatch is a stop condition. Never repair or regenerate these sources.

## Authorized Implementation Scope

The implementation commit may contain exactly:

```text
src/schwgw/io/tablei_risk_pilot.py
scripts/phase5_repair_delta0p1_risk_pilot_metadata.py
tests/unit/test_tablei_risk_pilot.py
tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
```

Additional allowed writes:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot/
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-15_pre_t8ao_units_metadata_repair.md
```

Preserve and exclude unrelated T0/T1/T2/T3/T4/T5/T6/T7 changes. Do not
modify `src/schwgw/io/__init__.py` or the existing scientific runner script.

## Required Work

Execute every checkbox in the T8ao plan:

- first establish the exact TDD RED;
- retain the v1 `SCHEMA_VERSION` and immutable generation-contract hash;
- add exactly
  `phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering`, the frozen units
  registry, ordering registry, and independently reproducible
  metadata-contract hash;
- validate exactly 23 active files and 22 non-self manifest records;
- preserve all 23 original active files byte-for-byte under
  `quarantine/t8ao_pre_units_metadata/source/`;
- compute canonical `.npy` SHA-256 for every non-`metadata_json` array using
  exactly `np.save(BytesIO(), array, allow_pickle=False)` bytes;
- build and validate a complete candidate tree before replacement;
- perform journaled, atomic, resumable replacement;
- retain a complete candidate tree and repair ledger for T7bx;
- prove no solver, polarization, radial cache, scientific runner, or metric
  recomputation path was called;
- independently prove old/new key, shape, dtype, `np.array_equal`, and
  canonical fingerprint identity for every non-metadata array;
- verify units/ordering/schema/provenance on all required surfaces;
- run focused tests, Ruff, full pytest, scope, source-hash, cardinality, and
  forbidden-output checks;
- archive/update T8 handoff and update `status.md`.

## Immutable Scientific Boundary

Do not change or recompute any frequency, point, lmax, branch, mask, complex
field, magnitude, phase, final-pair delta, runtime, cache count, warning,
adapter count, threshold, source/config/code hash, or selected generation Git
state. Only schema/units/ordering/repair provenance and hashes/sizes/timestamps
that necessarily change because metadata bytes changed may change.

No full grid, `0.05`, `0.025`, plot, PDF/PNG, fixture, Kirchhoff, smoothing,
interpolation, fill, or paper-style output is allowed.

## Required Fresh Verification

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
```

Also run direct standalone audits that do not call the migration helper and
emit:

```text
T8AO_NUMERICAL_ARRAY_IDENTITY=PASS
T8AO_METADATA_SURFACES_AND_PROVENANCE=PASS
```

The implementation commit must list exactly the four authorized paths.
Forbidden code/config/fixture diff and downstream-output searches must be
empty.

## Stop Conditions

Stop on any source/manifest/root hash mismatch, unexpected active file,
tampered or ambiguous backup, third-state mixed active file, array-key/shape/
dtype/value/fingerprint change, metadata coverage mismatch, provenance drift,
test/Ruff/scope failure, or forbidden output. Do not solve a contract failure
by rerunning scientific code, regenerating arrays, weakening equality, or
switching models.

A clear model-capacity/system interruption may resume this same T8 task only
after inspecting the repair ledger, source/candidate/active hashes, tests, and
process state. Reuse the safe journaled state and do not restart from scratch.

## Exact Decision

Record exactly one:

```text
GREEN / DELTA0P1 RISK-PILOT UNITS METADATA HARDENED
YELLOW / DELTA0P1 RISK-PILOT UNITS METADATA PARTIAL
RED / DELTA0P1 RISK-PILOT UNITS METADATA BLOCKED
```

## Downstream Dispatch

Only after exact GREEN, complete artifacts, fresh tests, status, archive, and
handoff, send this to existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` with `gpt-5.6-sol`, thinking `high`:

```text
你现在是 T7bx：Delta(kM)=0.1 risk-pilot units/ordering metadata repair 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bx_delta0p1_units_metadata_repair_review.md。请从 durable pre-repair backup 与 active artifacts 直接重建 array fingerprints 和 metadata contract，独立核验全部 units/ordering surfaces、23/22 cardinality、legacy provenance、tests 与 scope。不得调用 T8ao migration helper，不得修复 artifact，不得启动 0.05/0.025/full-grid/plot/paper work。
```

On YELLOW/RED/incomplete/ambiguous state, do not start T7bx; notify T0 only.
Notify T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` with exact decision,
implementation commit, metadata-contract hash, all new root hashes, identity
audit, tests, scope, and dispatch status. Do not push GitHub or start any later
scientific stage.
