# T4ab — Further-Local Radial/Q018 Gate

You are the existing T4 task. Execute only the frozen 24-frequency radial/Q018
gate for the T7bz YELLOW repair. You may measure radial support and add one
exact fail-closed adapter. Do not compute amplification or start T8aq.

## Required Reading

Read completely before modifying anything:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T4_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T8_current.md`
7. `docs/superpowers/specs/2026-07-16-t4ab-t8aq-further-local-refinement-design.md`
8. `docs/superpowers/plans/2026-07-16-t4ab-further-local-radial-gate.md`
9. this prompt
10. `docs/prompts/phase5_t7ca_further_local_radial_review.md`
11. all accepted T8aj/T8ao/T4aa/T8ap artifacts named in the design, current
    radial solver/direct oracle/Table-I source/envelopes, and authorized tests

Follow the frozen plan task by task. Use TDD, diagnose unexpected failures,
and verify every claim fresh.

## Start Gate And Immutable Anchors

Begin only when T0 handoff records the exact reviewed seven-file candidate
identity and:

```text
REVIEW GREEN / T0 REPAIR PACKAGE APPROVED
```

Freshly verify the exact design Section-2 path/hash mapping, including:

```text
8edd808e543460f943eb217af248b2edd52d7ea7d1827e99315b4f49f6521d9e  docs/handoffs/T7_current.md
ec6328ad5b9acfdd341a00877a7aaf355d49a0d39db1569f3e488b34b9980f17  runs/phase5/fig5_fig6_targeted_adaptive_refinement/adaptive_refinement_values.npz
9d9c821ab8c7f5af1ceb5136451e859a41bccd5456fe3beee834b876ffdc38cc  runs/phase5/fig5_fig6_targeted_adaptive_refinement/adaptive_refinement_values.npz.json
4606960110b658b74894c1b82a604c333481290ca0c451f3013574906eea5d67  runs/phase5/fig5_fig6_targeted_adaptive_refinement/adaptive_sampling_audit.json
2dfcaa7802ed8c7e3b3225429bb8b312d651441f378719331d023a5adb1e1caf  runs/phase5/fig5_fig6_targeted_adaptive_refinement/checkpoint_ledger.json
b728b1f5b4d45e622d5bebc32e710ac2be786556ab1ee7b7d9f26ca545223e5c  runs/phase5/fig5_fig6_targeted_adaptive_refinement/manifest.md
```

Also verify all earlier hashes in the design and the exact seven reviewed
package hashes supplied by T0. Bind path and hash; never discover, regenerate,
repair, or substitute an input.

## Frozen Contract

```text
kM = [0.325,0.375,0.825,0.875,0.925,0.975,
      1.525,1.575,1.625,1.675,1.7125,1.7375,
      2.7625,2.7875,2.825,2.875,2.925,2.975,
      3.7625,3.7875,3.825,3.875,3.925,3.975]
M = 1
r_out = 300
r_in_eps = 1e-6
rtol = 1e-10
atol = 1e-12
sectors = odd, even
points = exact eight TABLEI_POINTS
classification_records = 81792
adapter = q018_tablei_further_local_transition
```

Use exact tokens/lmax windows from the design. Never use nearest-frequency
matching or interpolate any earlier adapter.

## Authorized Scope

Implementation commit exactly:

```text
scripts/phase5_further_local_radial_gate.py
src/schwgw/numerics/q018_further_local_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

Additional writes only:

```text
runs/phase5/fig5_fig6_further_local_radial_gate/
docs/phase5_further_local_radial_gate.md
status.md
docs/handoffs/T4_current.md
docs/handoffs/archive/T4_2026-07-16_pre_t4ab_further_local_radial_gate.md
```

Preserve unrelated changes. Do not modify accepted artifacts, other envelope
modules, configs, IO/scattering/observable/viz code, fixtures, T0/T7/T8
handoffs, or later outputs.

## Required Work

- prove adapter-support TDD RED;
- classify all 81,792 records with zero default-other and exactly 24 atomic
  hash-bound PASS checkpoints;
- keep the pre-adapter classification snapshot separate from the final-
  adapter snapshot and bind their bridge;
- validate every exact sector-aware transition with the direct oracle,
  requested/actual precision, residual, normalization, boundary, and
  sensitivity evidence;
- use frozen deterministic anchors and explicit empty groups;
- generate a literal sector-aware envelope whose expansion equals raw keys;
- add only the new strict adapter, preserve zero adapter calls on default-
  covered modes, and reject every wrong contract field;
- after focused tests/Ruff, commit exactly five paths and freeze the final
  snapshot before integrated resume preflight;
- run focused tests, Ruff, fresh full pytest, and source/scope/provenance/
  cardinality/checkpoint/forbidden-output checks;
- update only permitted T4 coordination records.

Elapsed `30 h` is a soft notice. Checkpoint each frequency and never kill a
healthy process for time alone. Genuine system/capacity recovery reuses only
complete matching checkpoints after safety inspection; scientific/test/scope
failure never qualifies.

## Stop Conditions And Decision

Stop without T7 dispatch on any source mismatch, missing/duplicate record,
default-other, nonfinite oracle field, residual/sensitivity failure,
checkpoint/provenance ambiguity, test/Ruff/scope failure, or forbidden output.
Do not relax thresholds, omit work, broaden an adapter, or run T8aq.

Record exactly one:

```text
GREEN / FURTHER LOCAL RADIAL GATE READY
YELLOW / FURTHER LOCAL RADIAL GATE PARTIAL
RED / FURTHER LOCAL RADIAL GATE BLOCKED
```

## Downstream Dispatch

Only after exact GREEN and fresh verification, send to existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` with `5.6 Sol High`:

```text
你现在是 T7ca：further-local radial/Q018 gate 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7ca_further_local_radial_review.md。请独立核验 24 个频率、81,792 条 classification、全部 sector-aware direct-oracle transitions、24 个 atomic checkpoints、literal envelope、adapter fail-closed scope、双层 provenance、focused/Ruff/full tests 与 forbidden outputs。不得修复 T4ab，不得启动 T8aq。
```

Notify T0 with exact decision, commit, all gate/checkpoint hashes, counts,
maxima, precision, runtimes, tests, and T7ca dispatch state. Do not push
GitHub.
