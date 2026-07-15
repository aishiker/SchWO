# T8ap — Targeted Adaptive Frequency Evidence Pilot

You are the existing T8 task. Execute only the frozen point-only thirteen-
frequency targeted adaptive pilot after T0 independently confirms T7by exact
GREEN. This is not a full grid or an automatically recursive refinement.

## Start Gate

Begin only after T0 sends this exact upstream decision with unambiguous T4aa
commit/gate hashes and T7by records:

```text
ACCEPT GREEN / TARGETED ADAPTIVE RADIAL GATE ACCEPTED
```

Verify it independently. T7by itself is not authorized to start this task.

## Required Reading

Read completely:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T4_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T8_current.md`
7. `docs/superpowers/specs/2026-07-15-t4aa-t8ap-targeted-adaptive-refinement-design.md`
8. `docs/superpowers/plans/2026-07-15-t8ap-targeted-adaptive-refinement.md`
9. `docs/prompts/phase5_t7bz_targeted_adaptive_refinement_review.md`
10. this prompt
11. accepted T8aj and T8ao/T7bx artifacts/contracts and all accepted T4aa/T7by
    gate files, adapter source and focused tests

Follow the plan task by task. Use TDD for behavior changes, diagnose unexpected
failures before changing implementation, and verify all claims fresh.

## Immutable Sources

Freshly require the accepted T8aj hashes:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
```

Freshly require the accepted T8ao root hashes:

```text
8729ad80043a1837793264b101a776a08e92191c7856cf792ed34683b743859e
69cf9812ddd51d6486f854b77b76d202c281d719041cc07e8e87c1af9bd973f7
b812a4325b9afca91ee360b68dc3e959115f2d992fba21b60cf70a7ad3ce3566
7e1e8646bfa51b09cd96ee301e8847fdc830128d7eca7ac770031bc7b13ce42b
27301b9f300563a5feb654b48d9ef11ca8eb1e10f9c065c805534adfb27bfd78
```

Require generation contract
`92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9`,
metadata contract
`1bd32a3e2988ef786c3777859f76f8d38a276cdacd12cdadba7f79e843ca0161`,
schema `phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering`, and the exact
future T4aa/T7by gate hashes reported by T0. Any mismatch stops; never repair
or regenerate an input.

## Frozen Contract

```text
kM = [0.35,0.45,0.85,0.95,1.55,1.65,1.725,
      2.775,2.85,2.95,3.775,3.85,3.95]
M = 1
A_plus = 0.9+1.1j
A_cross = 0.4+0.6j
incident_direction = +z
r_out = 300
r_in_eps = 1e-6
rtol = 1e-10
atol = 1e-12
convergence_tolerance = 1e-4
adapter = q018_tablei_targeted_adaptive_transition
schema = phase5_t8ap_targeted_adaptive_refinement_v1_units_dtype_ordering
```

Use exact Table-I points, canonical tokens and lmax windows from the design.
The denominator is flat/no-lens Route-B packaged polarization, never
Kirchhoff. No nearest-frequency matching, interpolation, smoothing or fill.

## Authorized Scope

Implementation commit exactly:

```text
src/schwgw/io/tablei_adaptive_refinement.py
src/schwgw/io/__init__.py
scripts/phase5_run_targeted_adaptive_refinement.py
tests/unit/test_tablei_adaptive_refinement.py
tests/regression/test_targeted_adaptive_refinement_script.py
```

Additional allowed writes:

```text
runs/phase5/fig5_fig6_targeted_adaptive_refinement/
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-15_pre_t8ap_targeted_adaptive_refinement.md
```

Preserve/exclude unrelated T1/T2/T3/T5/T6 changes. Do not modify radial solver
or envelopes, `tablei_risk_pilot.py`, accepted artifacts, configs, viz,
fixtures, Kirchhoff, T0/T4/T7 handoffs, or unrelated files.

## Required Work

- establish the frozen TDD RED and implement separate generation/metadata
  contracts with explicit units, dtype, ordering and source/gate provenance;
- implement atomic frequency pairs/ledger, exact resume validation and
  quarantine; never reuse a filename without all hashes/contracts matching;
- use only frequency-local, certified-domain-aware radial reuse, processing
  points in decreasing radius and preserving disjoint local solutions;
- compute exactly thirteen frequencies at exactly eight points with frozen
  Route-B plus/cross ratios, masks, histories and final-pair test;
- allow one `+24`/`+48` extension only wholly inside T7by's accepted envelope;
- after every frequency, reload and validate its NPZ/JSON/ledger before the
  next transaction; resume must not recompute a valid complete transaction;
- produce exactly 31 active files and 30 manifest records, a `(13,8)`
  aggregate, and an audit containing exactly 432 phase and 416 hierarchical
  child/parent magnitude records without emitting scientific acceptance;
- run standalone no-helper artifact reconstruction, focused tests, Ruff,
  fresh full pytest, scope/provenance/cardinality/source/forbidden-output checks;
- commit exactly the five implementation/test paths and update the permitted
  T8 coordination records.

The user permits long background execution. A `6 h` notice is soft. Do not
kill a healthy process for elapsed time. For a genuine capacity/system
interruption, first inspect process, transaction pairs, ledger, contracts,
hashes, tests and scope, then reuse safe state. Scientific/test/scope failure
never qualifies for model-switch recovery.

## Output Contract

Only under `runs/phase5/fig5_fig6_targeted_adaptive_refinement/`:

```text
frequencies/kM_<token>.npz and matching JSON for thirteen frequencies
checkpoint_ledger.json
adaptive_refinement_values.npz
adaptive_refinement_values.npz.json
adaptive_sampling_audit.json
manifest.md
```

No active `.tmp`, extra active file, plot/PDF/PNG, full-grid artifact, fixture,
Kirchhoff result, paper candidate, or automatically proposed next midpoint.

## Stop Conditions And Exact Decision

Stop on any source/gate/code hash mismatch, missing/extra/duplicate transaction,
unsafe cache reuse, nonfinite value, false mask, final-pair failure outside the
accepted envelope, units/dtype/ordering/schema mismatch, ledger/aggregate/
manifest ambiguity, test/Ruff/scope failure, or forbidden output. Do not omit
work or relax any physical/numerical/scientific rule.

Record exactly one:

```text
GREEN / TARGETED ADAPTIVE FREQUENCY EVIDENCE GENERATED
YELLOW / TARGETED ADAPTIVE FREQUENCY EVIDENCE PARTIAL
RED / TARGETED ADAPTIVE FREQUENCY EVIDENCE BLOCKED
```

## Downstream Dispatch

Only after exact GREEN and fresh verification, send this to existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` with model `5.6 Sol`, thinking `high`:

```text
你现在是 T7bz：targeted adaptive frequency evidence 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bz_targeted_adaptive_refinement_review.md。请直接读取十三个 per-frequency artifacts、accepted T8aj endpoints 和 T8ao/T7bx rows，独立重建五个序列、432 个 phase records、416 个 hierarchical magnitude records，并核验 31/30 artifact contract、contracts/hashes/provenance、focused/Ruff/full tests 与 forbidden outputs。不得修复 T8ap，不得启动下一 midpoint 或 production。
```

Notify T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` with exact decision,
commit, all contract/source/gate/output hashes, per-frequency runtimes,
solve/reuse/adapter counts, final-pair maxima, audit/test results, and T7bz
dispatch state. Do not push GitHub or start another stage.
