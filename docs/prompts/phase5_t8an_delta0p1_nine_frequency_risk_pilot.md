# T8an — Delta(kM)=0.1 Nine-Frequency Risk Pilot

You are the existing T8 task. Execute the frozen point-only, resumable nine-frequency Table-I risk pilot only after T0 confirms T7bv exact GREEN. This is not the 40-frequency production grid.

## Start Gate

Begin only after T0 supplies and you independently verify:

```text
ACCEPT GREEN / DELTA0P1 RISK-PILOT RADIAL GATE ACCEPTED
```

The T4z implementation commit, T7bv record, adapter envelope, and gate artifact hashes must be present and unambiguous.

## Required Reading And Skills

Read completely:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T4_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T8_current.md`
7. `docs/superpowers/specs/2026-07-14-t4z-t8an-delta0p1-risk-pilot-design.md`
8. `docs/superpowers/plans/2026-07-14-t8an-delta0p1-nine-frequency-risk-pilot.md`
9. `docs/prompts/phase5_t7bw_delta0p1_risk_pilot_review.md`
10. this prompt
11. accepted T8aj NPZ/JSON/manifest
12. T4z/T7bv gate files and accepted adapter source/tests

Use `executing-plans`, `test-driven-development`, `systematic-debugging` for unexpected failures, and `verification-before-completion`.

## Immutable Reference Inputs

```text
runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
runs/phase5/fig5_fig6_dense_review_grid/manifest.md
```

Hashes:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
```

Any mismatch is a stop condition. Never repair/regenerate the accepted source.

## Frozen Pilot Contract

```text
kM=[0.4,0.8,0.9,1.6,1.7,2.8,2.9,3.8,3.9]
M=1
A_plus=0.9+1.1j
A_cross=0.4+0.6j
incident_direction=+z
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
convergence_tolerance=1e-4
adapter=q018_tablei_delta0p1_risk_pilot_transition
```

Use the exact eight Table-I coordinates and frozen lmax windows in the design/plan. The denominator is flat/no-lens Route-B packaged polarization, never Kirchhoff.

## Authorized Scope

Implementation commit exactly:

```text
src/schwgw/io/tablei_risk_pilot.py
src/schwgw/io/__init__.py
scripts/phase5_run_delta0p1_risk_pilot.py
tests/unit/test_tablei_risk_pilot.py
tests/regression/test_delta0p1_risk_pilot_script.py
```

Additional allowed writes:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot/
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-14_pre_t8an_delta0p1_risk_pilot.md
```

Preserve/exclude unrelated T1/T2/T3/T5/T6 changes. Do not modify radial solver/adapter, accepted artifacts, configs, visualization, Kirchhoff code, fixtures, or other handoffs.

## Required Work

Execute every checkbox in the T8an plan:

- establish TDD RED;
- implement exact contract hashing and atomic JSON/NPZ transactions;
- implement frequency-local domain-aware cache with certified-radius reuse only;
- compute Route-B plus/cross ratios at nine frequencies and eight points;
- check the final adjacent lmax pair for both components/all points;
- allow one lmax extension only inside T7bv's accepted envelope;
- checkpoint each completed frequency and hash-bind the ledger;
- resume without recomputing complete valid transactions;
- write exact nine-row aggregate, sampling audit, and manifest;
- run direct artifact audit, focused tests, Ruff, full pytest, scope, hash, and forbidden-output checks;
- update status/archive/handoff and commit exactly the five paths.

The user permits long background work. Four hours is a soft alert only. Do not kill a healthy process because of elapsed time. On a clear capacity/system interruption, validate process/checkpoint/artifact state, then reuse safe transactions. Scientific/test/nonfinite/scope failures are not recoverable by model switching.

## Output Contract

Only under:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot/
```

Required:

```text
frequencies/kM_<token>.npz and matching JSON for nine frequencies
checkpoint_ledger.json
risk_pilot_values.npz
risk_pilot_values.npz.json
risk_pilot_sampling_audit.json
manifest.md
```

No plot/PDF/PNG, Kirchhoff output, full production artifact, fixture, or paper candidate.

## Stop Conditions

Stop on any source/gate hash mismatch, checkpoint mismatch, unexpected file, invalid mask, nonfinite value, final-pair failure outside allowed extension, unreviewed radial mode, scope drift, test/Ruff failure, or ambiguous provenance. Do not lower lmax, relax `1e-4`, omit points/frequencies, fill/interpolate/smooth, or broaden the adapter.

## Exact Decision

Record exactly one:

```text
GREEN / DELTA0P1 NINE-FREQUENCY RISK PILOT GENERATED
YELLOW / DELTA0P1 NINE-FREQUENCY RISK PILOT PARTIAL
RED / DELTA0P1 NINE-FREQUENCY RISK PILOT BLOCKED
```

## Downstream Dispatch

Only after exact GREEN and fresh verification, send this to existing T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed` with `gpt-5.6-sol`, thinking `high`:

```text
你现在是 T7bw：Delta(kM)=0.1 nine-frequency risk pilot 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bw_delta0p1_risk_pilot_review.md。请直接读取九个 per-frequency artifacts 与 accepted T8aj endpoints，独立重建五个局部序列，核验 observed phase-step 与 magnitude-dominance criteria、checkpoint/provenance、tests 和 scope。不得修复 T8an，不得启动 full grid 或 0.05 scan。
```

Notify T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` with exact decision, commit, hashes, runtimes, cache/oracle counts, final-pair maxima, audit result, tests, and T7 dispatch status. Do not push GitHub or start any later stage.
