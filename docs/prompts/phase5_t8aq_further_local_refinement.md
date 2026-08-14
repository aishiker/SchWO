# T8aq — Further-Local Frequency Evidence

You are the existing T8 task. Execute only the frozen point-only 24-frequency
further-local repair after T0 confirms T7ca exact GREEN. This is not a full
grid, uniform scan, or recursive refinement.

## Start Gate

Begin only after T0 sends:

```text
ACCEPT GREEN / FURTHER LOCAL RADIAL GATE ACCEPTED
```

with exact T4ab commit/gate/snapshot hashes and T7ca records. Verify it
independently; T7ca itself cannot start T8aq.

## Required Reading

Read completely: `project.md`, `status.md`, T0/T4/T7/T8 handoffs, frozen
further-local design, T8aq plan, T7cb prompt, this prompt, accepted
T8aj/T8ao/T8ap artifacts/contracts, archived T7bz evidence, all accepted
T4ab/T7ca gate files, adapter source, and focused tests.

Follow the plan task by task. Use TDD and fresh verification.

## Immutable Sources

Require all exact hashes in design Section 2, including the T8ap roots:

```text
ec6328ad5b9acfdd341a00877a7aaf355d49a0d39db1569f3e488b34b9980f17
9d9c821ab8c7f5af1ceb5136451e859a41bccd5456fe3beee834b876ffdc38cc
4606960110b658b74894c1b82a604c333481290ca0c451f3013574906eea5d67
2dfcaa7802ed8c7e3b3225429bb8b312d651441f378719331d023a5adb1e1caf
b728b1f5b4d45e622d5bebc32e710ac2be786556ab1ee7b7d9f26ca545223e5c
```

Require T8ap generation contract
`74cb3aafa63e12609d7f6b7f1efef10b539ebec1f1a91f2990356d9e56a51c94`,
metadata contract
`5bf94f5bd0ac5ad8678fe9e561012c53ff4e9c1cff14bd401f3feadba6fd2865`,
schema `phase5_t8ap_targeted_adaptive_refinement_v1_units_dtype_ordering`,
and archived T7bz evidence hash
`8edd808e543460f943eb217af248b2edd52d7ea7d1827e99315b4f49f6521d9e`.
T0 supplies future T4ab/T7ca gate hashes. Any mismatch stops; never repair or
regenerate an input.

## Frozen Contract

```text
kM = [0.325,0.375,0.825,0.875,0.925,0.975,
      1.525,1.575,1.625,1.675,1.7125,1.7375,
      2.7625,2.7875,2.825,2.875,2.925,2.975,
      3.7625,3.7875,3.825,3.875,3.925,3.975]
M = 1
A_plus = 0.9+1.1j
A_cross = 0.4+0.6j
incident_direction = +z
r_out = 300
r_in_eps = 1e-6
rtol = 1e-10
atol = 1e-12
convergence_tolerance = 1e-4
adapter = q018_tablei_further_local_transition
schema = phase5_t8aq_further_local_refinement_v1_units_dtype_ordering
```

Use exact Table-I points, tokens, lmax, sequences, and literal parent map from
the design. Denominators are flat/no-lens Route-B, never Kirchhoff. No nearest
matching, interpolation, smoothing, fill, or lmax extension.

## Authorized Scope

Implementation commit exactly:

```text
src/schwgw/io/tablei_further_local_refinement.py
src/schwgw/io/__init__.py
scripts/phase5_run_further_local_refinement.py
tests/unit/test_tablei_further_local_refinement.py
tests/regression/test_further_local_refinement_script.py
```

Additional writes only:

```text
runs/phase5/fig5_fig6_further_local_refinement/
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-16_pre_t8aq_further_local_refinement.md
```

Preserve unrelated changes. Do not modify radial solver/envelopes, accepted
modules/artifacts, configs, viz, fixtures, Kirchhoff, or other handoffs.

## Required Work

- establish TDD RED and separate generation/metadata contracts with explicit
  units, dtypes, ordering, and provenance;
- implement atomic pairs/ledger, strict resume validation, and quarantine;
- complete fake-compute tests/Ruff and commit exactly five paths before the
  first real frequency; bind the commit/blobs in the contract;
- use frequency-local certified-domain cache reuse and preserve disjoint
  local solutions;
- compute exactly 24 frequencies at eight points with frozen Route-B ratios,
  masks, histories, and final-pair test; no extension;
- reload and validate each pair/ledger before starting the next; never
  recompute a valid complete transaction;
- produce exactly 53 active files, 52 manifest records, `(24,8)` aggregate,
  and diagnostic audit with exactly 816 phase, 768 hierarchy, and 80 summary
  records using the literal mapping;
- if implementation changes after execution begins, freeze a new five-path
  identity and quarantine all old-contract transactions;
- run standalone no-helper audit, focused tests, Ruff, fresh full pytest, and
  source/gate/scope/cardinality/provenance/forbidden-output checks;
- update only permitted T8 coordination records.

Elapsed `12 h` is soft. Never kill a healthy process for time alone. Genuine
system/capacity recovery first inspects process, pairs, ledger, contracts,
hashes, tests, and scope, then reuses safe state. Scientific/test/scope
failure never qualifies.

## Output Contract

Only under `runs/phase5/fig5_fig6_further_local_refinement/`:

```text
frequencies/kM_<token>.npz and matching JSON for 24 frequencies
checkpoint_ledger.json
further_local_values.npz
further_local_values.npz.json
further_local_sampling_audit.json
manifest.md
```

No `.tmp`, extra active file, plot, full/uniform artifact, fixture, Kirchhoff,
paper candidate, or automatically proposed next midpoint.

## Stop Conditions And Decision

Stop on any source/gate/code mismatch, missing/extra pair, unsafe cache,
nonfinite value, false mask, final-pair failure, schema/units/dtype/ordering
mismatch, ledger/aggregate/manifest ambiguity, test/Ruff/scope failure, or
forbidden output. Do not omit work or relax a rule.

Record exactly one:

```text
GREEN / FURTHER LOCAL FREQUENCY EVIDENCE GENERATED
YELLOW / FURTHER LOCAL FREQUENCY EVIDENCE PARTIAL
RED / FURTHER LOCAL FREQUENCY EVIDENCE BLOCKED
```

## Downstream Dispatch

Only after exact GREEN and fresh verification, send to existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` with `5.6 Sol High`:

```text
你现在是 T7cb：further-local frequency evidence 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7cb_further_local_refinement_review.md。请直接读取 24 个 per-frequency artifacts 与 immutable T8aj/T8ao/T8ap rows，独立重建五个序列、816 个 phase records、768 个 hierarchical magnitude records，并核验 53/52 artifact contract、contracts/hashes/provenance、focused/Ruff/full tests 与 forbidden outputs。不得修复 T8aq，不得启动下一 midpoint 或 production。
```

Notify T0 with exact decision, commit, contracts/source/gate/output hashes,
runtimes, solve/reuse/adapter counts, final-pair maxima, audits/tests, and T7cb
dispatch state. Do not push GitHub or start another stage.
