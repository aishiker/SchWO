# T4z — Delta(kM)=0.1 Risk-Pilot Radial/Q018 Gate

You are the existing T4 task. Execute the frozen radial/Q018 gate for the nine-frequency Fig.5/Fig.6 risk pilot. This task may classify radial modes and add one exact fail-closed adapter, but it must not compute Table-I amplification artifacts or start T8.

## Required Reading And Skills

Read completely:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T4_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/superpowers/specs/2026-07-14-t4z-t8an-delta0p1-risk-pilot-design.md`
7. `docs/superpowers/plans/2026-07-14-t4z-delta0p1-risk-pilot-radial-gate.md`
8. this prompt
9. `docs/prompts/phase5_t7bv_delta0p1_risk_pilot_radial_review.md`
10. `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
11. the three accepted T4y radial-gate JSON files
12. current radial solver, experimental oracle, Table-I points, and named tests

Use `executing-plans`, `test-driven-development`, `systematic-debugging` for any unexpected failure, and `verification-before-completion`. The frozen spec/prompt wins over a skill when scope differs.

## Frozen Contract

```text
kM = [0.4,0.8,0.9,1.6,1.7,2.8,2.9,3.8,3.9]
M=1
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
sectors=odd,even
points=the exact eight src/schwgw/io/tablei.py Table-I radii
```

Frozen initial lmax windows:

```text
0.4 [24,36,60,84]
0.8 [24,36,60,84]
0.9 [24,36,60,84]
1.6 [72,96,120,144]
1.7 [84,108,132,156]
2.8 [180,204,228,252]
2.9 [192,216,240,264]
3.8 [276,300,324,348]
3.9 [288,312,336,360]
```

The existing `q018_tablei_review_grid_transition` adapter is forbidden for new frequencies. Never interpolate its transition segments.

## Authorized Scope

Implementation commit must contain exactly:

```text
scripts/phase5_delta0p1_risk_radial_gate.py
src/schwgw/numerics/q018_delta0p1_risk_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

Additional allowed writes:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/
docs/phase5_delta0p1_risk_pilot_radial_gate.md
status.md
docs/handoffs/T4_current.md
docs/handoffs/archive/T4_2026-07-14_pre_t4z_delta0p1_risk_pilot.md
```

Preserve and exclude unrelated T1/T2/T3/T5/T6 worktree changes. Do not touch accepted T8aj/T8al/T8am artifacts, other adapters, configs, scattering/observable code, plots, fixtures, or other handoffs.

## Required Work

Execute every checkbox in the T4z implementation plan. In particular:

- prove the specified TDD RED;
- classify every requested default radial record;
- require zero unstructured/default-other errors;
- validate every structured transition with the direct oracle;
- write atomic hash-bound checkpoint per frequency;
- generate an immutable literal envelope module;
- add only `q018_tablei_delta0p1_risk_pilot_transition`;
- require exact measured `(kM,ell,point_id)` membership and exact boundary values;
- keep default-covered modes on the ordinary path;
- test positive anchors, direct equality, default paths, and every out-of-envelope axis;
- run focused tests, Ruff, full pytest, scope, artifact, and forbidden-output checks;
- write the scientific note, manifest, status, archive, and handoff.

The user permits long background execution. Four hours is a soft alert, not a failure threshold. Checkpoint progress after every frequency. A healthy solver must not be killed only for elapsed time.

## Stop Conditions

Stop YELLOW/RED and do not dispatch T7 if any record is nonfinite, unstructured, outside scope, not reproducible by the direct oracle, above frozen residual/sensitivity bounds, inconsistent with checkpoint hashes, or if any test/Ruff/scope/provenance check fails. Do not relax thresholds, lower lmax, omit points/modes, or broaden the adapter.

Model-capacity/system interruption is not a scientific failure. On recovery, validate source hashes, process state, checkpoints, and artifacts, then reuse only complete matching checkpoints. Scientific/test failures never qualify for a model switch.

## Exact Decision

Record exactly one:

```text
GREEN / DELTA0P1 RISK-PILOT RADIAL GATE READY
YELLOW / DELTA0P1 RISK-PILOT RADIAL GATE PARTIAL
RED / DELTA0P1 RISK-PILOT RADIAL GATE BLOCKED
```

Exact GREEN requires every frozen check, implementation commit, artifact hash, status, and handoff to pass fresh verification.

## Downstream Dispatch

Only after exact GREEN, send this to existing T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed` with `gpt-5.6-sol`, thinking `high`:

```text
你现在是 T7bv：Delta(kM)=0.1 risk-pilot radial/Q018 gate 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bv_delta0p1_risk_pilot_radial_review.md。请独立核验九频率完整 classification、direct-oracle validation、atomic checkpoints、exact generated envelope、adapter fail-closed scope、focused/Ruff/full tests 和 forbidden observable outputs。不得修复 T4z，不得启动 T8an。
```

Also notify T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` with exact decision, commit, artifact hashes, classification/oracle counts, residual/sensitivity maxima, runtimes, test results, and T7 dispatch status. T4z must not push GitHub or run T8an.
