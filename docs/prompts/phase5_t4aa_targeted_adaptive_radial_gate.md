# T4aa — Targeted Adaptive Radial/Q018 Gate

You are the existing T4 task. Execute only the frozen thirteen-frequency
radial/Q018 gate needed by the approved targeted adaptive-frequency evidence
slice. This task may measure radial support and add one exact fail-closed
adapter. It must not compute amplification artifacts or start T8ap.

## Required Reading

Read completely before modifying anything:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T4_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/superpowers/specs/2026-07-15-t4aa-t8ap-targeted-adaptive-refinement-design.md`
7. `docs/superpowers/plans/2026-07-15-t4aa-targeted-adaptive-radial-gate.md`
8. this prompt
9. `docs/prompts/phase5_t7by_targeted_adaptive_radial_review.md`
10. the accepted T4z gate note, manifest, thirteen relevant source/contract
    anchors, current radial solver, direct oracle, Table-I points, existing
    Q018 envelopes, and the two authorized test modules

Follow the frozen plan task by task. Use TDD for behavior changes, diagnose any
unexpected failure before modifying code, and verify all claims fresh. Project
scope and stop rules override convenience.

## Start Gate And Immutable Anchors

Begin only after `docs/handoffs/T0_current.md` records the independent package
review:

```text
REVIEW GREEN / T0 REPAIR PACKAGE APPROVED
```

Freshly verify these accepted hashes before classification:

```text
# T8aj
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf

# accepted T8ao package roots
8729ad80043a1837793264b101a776a08e92191c7856cf792ed34683b743859e
69cf9812ddd51d6486f854b77b76d202c281d719041cc07e8e87c1af9bd973f7
b812a4325b9afca91ee360b68dc3e959115f2d992fba21b60cf70a7ad3ce3566
7e1e8646bfa51b09cd96ee301e8847fdc830128d7eca7ac770031bc7b13ce42b
27301b9f300563a5feb654b48d9ef11ca8eb1e10f9c065c805534adfb27bfd78

# T4z/T7bv anchors
ee051831e1da7ebb250cab37d7da3a64d8a57298b445577f238d9cefae319d54
8f6d23da0894d0abfb42867bf911b9da95090ad5293bc76289daf4522e4067f9
59e99ade6993eab6d570f8a2ad18f0778595f7309fbb87fbf1edf32903b80968
```

Any mismatch stops the task. Do not regenerate or repair an anchor.

## Frozen Contract

```text
kM = [0.35,0.45,0.85,0.95,1.55,1.65,1.725,
      2.775,2.85,2.95,3.775,3.85,3.95]
M = 1
r_out = 300
r_in_eps = 1e-6
rtol = 1e-10
atol = 1e-12
sectors = odd, even
points = exact eight TABLEI_POINTS
classification_records = 42224
adapter = q018_tablei_targeted_adaptive_transition
```

Use the exact lmax windows and canonical tokens in the design/plan. Never
round `1.725`, `2.775`, or `3.775`, use nearest-frequency matching, or
interpolate any T4z adapter/envelope.

## Authorized Scope

The implementation commit must contain exactly:

```text
scripts/phase5_targeted_adaptive_radial_gate.py
src/schwgw/numerics/q018_targeted_adaptive_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

Additional allowed writes:

```text
runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/
docs/phase5_targeted_adaptive_radial_gate.md
status.md
docs/handoffs/T4_current.md
docs/handoffs/archive/T4_2026-07-15_pre_t4aa_targeted_adaptive_radial_gate.md
```

Preserve and exclude unrelated T1/T2/T3/T5/T6 changes. Do not modify accepted
artifacts, other envelope modules, configs, IO/scattering/observable/viz code,
fixtures, T0/T7/T8 handoffs, or any later-stage output.

## Required Work

- prove the frozen adapter-support TDD RED;
- classify all `42,224` default records with zero unstructured/default-other
  errors and exactly thirteen atomic hash-bound checkpoints;
- direct-oracle validate every structured transition and record requested vs
  actual backend precision, residuals, normalization and sensitivity;
- generate a literal envelope whose expansion exactly equals the raw
  transition set without frequency/radius/ell interpolation;
- add only the new strict adapter, keep default-covered modes at zero adapter
  calls, and reject every wrong contract field fail-closed;
- run complete adapter preflight, focused tests, Ruff, fresh full pytest,
  source/scope/provenance/cardinality/checkpoint/forbidden-output checks;
- commit exactly the five implementation/test paths and update the permitted
  T4 coordination records.

The user permits long background execution. A `12 h` notice is soft and must
not kill a healthy process. Checkpoint after every frequency. On a genuine
capacity/system interruption, reuse only complete matching checkpoints after
process/source/artifact inspection; a scientific/test/scope failure never
qualifies for model-switch recovery.

## Stop Conditions And Exact Decision

Stop without T7 dispatch on any source mismatch, missing/duplicate record,
unstructured error, nonfinite oracle result, residual/sensitivity failure,
checkpoint/provenance ambiguity, test/Ruff/scope failure, or forbidden output.
Never relax thresholds, omit work, broaden another adapter, or run T8ap.

Record exactly one:

```text
GREEN / TARGETED ADAPTIVE RADIAL GATE READY
YELLOW / TARGETED ADAPTIVE RADIAL GATE PARTIAL
RED / TARGETED ADAPTIVE RADIAL GATE BLOCKED
```

## Downstream Dispatch

Only after exact GREEN and fresh verification, send the following to existing
T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed` with model `5.6 Sol`, thinking
`high`:

```text
你现在是 T7by：targeted adaptive radial/Q018 gate 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7by_targeted_adaptive_radial_review.md。请独立核验十三频率、42,224 条 classification、全部 direct-oracle transition、十三 atomic checkpoints、literal envelope、adapter fail-closed scope、focused/Ruff/full tests 和 forbidden observable outputs。不得修复 T4aa，不得启动 T8ap。
```

Notify T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` with exact decision,
implementation commit, all gate/checkpoint hashes, counts, maxima, backend
precision, runtimes, tests, and T7by dispatch state. Do not push GitHub.
