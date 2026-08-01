# T8 Current Handoff

Last updated: 2026-07-16

## Thread Role And Current Status

T8ap completed the frozen targeted adaptive refinement point-only execution
for exactly thirteen frequencies. Every frequency was written as one atomic
NPZ/JSON transaction with a hash-bound checkpoint-ledger entry, followed by a
directly stacked `(13, 8)` aggregate and read-only sampling audit.

Exact decision:

```text
GREEN / TARGETED ADAPTIVE FREQUENCY EVIDENCE GENERATED
```

The predecessor T8ao handoff is archived byte-for-byte at
`docs/handoffs/archive/T8_2026-07-15_pre_t8ap_targeted_adaptive_refinement.md`.

## Completed Work

- Implementation commit
  `575c275fcb4ab9263786e7e5ee7f3425f20b7ce6` changes exactly the five frozen
  paths:
  `src/schwgw/io/tablei_adaptive_refinement.py`,
  `src/schwgw/io/__init__.py`,
  `scripts/phase5_run_targeted_adaptive_refinement.py`,
  `tests/unit/test_tablei_adaptive_refinement.py`, and
  `tests/regression/test_targeted_adaptive_refinement_script.py`.
- The thirteen frequencies are exactly
  `0.35, 0.45, 0.85, 0.95, 1.55, 1.65, 1.725, 2.775, 2.85, 2.95,
  3.775, 3.85, 3.95`. No automatic midpoint or lmax extension occurred.
- The implementation generation contract is
  `74cb3aafa63e12609d7f6b7f1efef10b539ebec1f1a91f2990356d9e56a51c94`;
  the independently reconstructed metadata contract is
  `5bf94f5bd0ac5ad8678fe9e561012c53ff4e9c1cff14bd401f3feadba6fd2865`.
- All seven frozen design/plan/prompt hashes, eight accepted T8aj/T8ao source
  hashes, four T4aa gate hashes, classification/final-adapter snapshots, and
  selected scientific-code hashes freshly match.
- All 13 T4aa checkpoints are `PASS`. Per-frequency adapter use exactly equals
  the corresponding gate `transition_record_count`; it is zero outside the
  reviewed transition envelope.

## Active Artifact Package

Directory:
`runs/phase5/fig5_fig6_targeted_adaptive_refinement/`

The package has exactly 31 active files and the manifest has exactly 30
non-self records. There is no `.tmp`, quarantine, plot, PDF/PNG/SVG,
Kirchhoff, fixture, paper-style, 40/79-frequency, full/uniform-grid, or
`0.025` artifact.

Root hashes:

```text
ec6328ad5b9acfdd341a00877a7aaf355d49a0d39db1569f3e488b34b9980f17  adaptive_refinement_values.npz
9d9c821ab8c7f5af1ceb5136451e859a41bccd5456fe3beee834b876ffdc38cc  adaptive_refinement_values.npz.json
4606960110b658b74894c1b82a604c333481290ca0c451f3013574906eea5d67  adaptive_sampling_audit.json
2dfcaa7802ed8c7e3b3225429bb8b312d651441f378719331d023a5adb1e1caf  checkpoint_ledger.json
b728b1f5b4d45e622d5bebc32e710ac2be786556ab1ee7b7d9f26ca545223e5c  manifest.md
```

All 26 per-frequency NPZ/JSON hashes are recorded and independently verified
by `manifest.md` and `checkpoint_ledger.json`.

## Per-Frequency Execution Evidence

Columns are `kM | runtime_s | radial_solve | radial_reuse | adapter_use |
warning_count`:

```text
0.35  | 12.891246   | 166  | 3034  | 0   | 2
0.45  | 17.826778   | 166  | 3034  | 0   | 0
0.85  | 54.106291   | 166  | 3034  | 0   | 0
0.95  | 67.692761   | 190  | 3586  | 0   | 0
1.55  | 265.811520  | 286  | 6562  | 0   | 0
1.65  | 301.922816  | 310  | 7306  | 0   | 0
1.725 | 321.361152  | 310  | 7306  | 0   | 0
2.775 | 653.525772  | 572  | 13188 | 72  | 250
2.85  | 689.059327  | 610  | 13918 | 86  | 286
2.95  | 697.138624  | 640  | 14656 | 90  | 312
3.775 | 1123.017214 | 1084 | 18820 | 418 | 738
3.85  | 1161.578958 | 1112 | 18792 | 450 | 764
3.95  | 1234.534026 | 1180 | 19492 | 500 | 830
```

All complex arrays are finite, both valid-ratio masks are true, and all final
lmax pairs pass without extension. Global final-pair maxima are
`3.5676700242976008e-12` for plus and
`3.2385769900639225e-11` for cross, below the frozen `1e-4` threshold.

## Verification

- `T8AP_IMPLEMENTATION_AND_METADATA_CONTRACT=PASS` for the exact five-path
  commit, live file/blob hashes, and reconstructed metadata contract.
- `T8AP_GENERATION_CONTRACT_RECONSTRUCTION=PASS` for the complete generation
  contract, including frozen package, source/gate, implementation, and selected
  scientific-code identity.
- `T8AP_TRANSACTION_AGGREGATE_MANIFEST_AUDIT=PASS 31/30/13`: direct NPZ loads
  verified exact keys, shapes, dtypes, finite values, masks, final-pair deltas,
  canonical `.npy` fingerprints, embedded/sidecar equality, ledger hashes,
  gate-envelope adapter counts, direct aggregate stacking, unwrap, and every
  manifest size/hash record without importing a T8ap helper.
- `T8AP_DIRECT_SAMPLING_RECONSTRUCTION=PASS phase=432 hierarchy=416`: direct
  reconstruction from accepted T8aj endpoints, T8ao/T7bx rows, and T8ap
  midpoint rows exactly equals every saved phase and hierarchical record.
- Focused pytest: `12 passed in 0.71s`.
- Ruff: `All checks passed!` on the exact five implementation/test paths.
- Mandatory full pytest: `639 passed, 117 skipped, 1 xfailed, 101 warnings,
  81 subtests passed in 311.30s`.
- The first standalone audit used an unnecessarily order-sensitive assertion
  for `git diff-tree`; inspection confirmed the required five-path set exactly
  matched, and the corrected set-exact audit passed. No artifact or code was
  changed for that audit correction.

## Incomplete Work

- T7bz must independently review the thirteen transaction pairs, accepted
  endpoint/risk rows, contracts, `31/30` cardinality, and `432/416` sampling
  reconstruction. T8ap does not independently accept its own evidence.
- This GREEN generates bounded point-only evidence. It does not authorize an
  additional midpoint, full/uniform grid, 40/79-frequency production, plot,
  fixture, Kirchhoff, or paper-style artifact.

## Frozen Decisions And Forbidden Actions

- Frequencies, lmax windows, Table-I points, amplitudes, boundary values,
  tolerance, source/gate hashes, Q018 adapter policy, transaction schema,
  contracts, and sampling checks are immutable.
- Do not rerun T8ap, extend lmax, add a midpoint, interpolate, smooth, fill, or
  start production.
- Do not modify radial solver/adapter, accepted T8aj/T8ao/T4aa artifacts,
  configs, visualization, fixtures, Kirchhoff, paper-style outputs, or GitHub.

## Exact Next Task

Dispatch T7bz in the existing T7 task with `gpt-5.6-sol/high`:

```text
你现在是 T7bz：targeted adaptive frequency evidence 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bz_targeted_adaptive_refinement_review.md。请直接读取十三个 per-frequency artifacts、accepted T8aj endpoints 和 T8ao/T7bx rows，独立重建五个序列、432 个 phase records、416 个 hierarchical magnitude records，并核验 31/30 artifact contract、contracts/hashes/provenance、focused/Ruff/full tests 与 forbidden outputs。不得修复 T8ap，不得启动下一 midpoint 或 production。
```

## Definition Of Done

T8ap is complete because the exact five-path implementation commit, thirteen
atomic transactions, ledger, `(13, 8)` aggregate, diagnostic-only sampling
audit, `31/30` package, contract/hash/source/gate/adapter checks, independent
`432/416` reconstruction, focused/Ruff/full tests, archive, this handoff, and
`status.md` are fresh and GREEN. Scientific interpretation remains with T7bz.
