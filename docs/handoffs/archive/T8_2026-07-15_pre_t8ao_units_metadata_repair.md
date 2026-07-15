# T8 Current Handoff

Last updated: 2026-07-15

## Thread Role And Current Status

T8an completed the frozen Delta(kM)=0.1 nine-frequency, eight-point,
point-only Route-B risk pilot after the T7bv radial/Q018 gate was accepted.
This is a bounded risk pilot, not the 40/79-frequency production grid.

Exact decision:

```text
GREEN / DELTA0P1 NINE-FREQUENCY RISK PILOT GENERATED
```

The predecessor T8am handoff is archived at
`docs/handoffs/archive/T8_2026-07-14_pre_t8an_delta0p1_risk_pilot.md`.

## Completed Work

- Implemented the exact frozen five-path pilot in commit `c068868`:
  `src/schwgw/io/tablei_risk_pilot.py`, `src/schwgw/io/__init__.py`,
  `scripts/phase5_run_delta0p1_risk_pilot.py`,
  `tests/unit/test_tablei_risk_pilot.py`, and
  `tests/regression/test_delta0p1_risk_pilot_script.py`.
- A real 2.8 transaction exposed a runner-only cache-domain bug: a Q018
  point-local solution at a larger radius was incorrectly reused at a smaller
  radius. No solver, adapter, physics threshold, lmax window, or boundary
  policy was changed.
- Commit `47c3d63` adds the regression test and makes cache reuse require the
  full certified radial interval while retaining disjoint point-local
  solutions. The two-commit combined path set remains exactly the frozen five
  paths.
- The five old-contract completed transactions and ledger were preserved under
  `runs/phase5/fig5_fig6_delta0p1_risk_pilot/quarantine/runner_cache_domain_pre_47c3d63/`.
  Because the selected-code hash changed, no old numerical transaction was
  represented as valid under the new contract.
- Generated all nine atomic frequency pairs, the hash-bound checkpoint
  ledger, exact 9x8 aggregate, diagnostic-only sampling audit, and manifest
  under `runs/phase5/fig5_fig6_delta0p1_risk_pilot/`.

## Artifacts, Hashes, And Numerical Summary

Contract SHA256:
`92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9`.

```text
79d4c0f596650dcfb4d63c7e40758ea4afa82d2fe0e0cd3de5aa088bbbfd5ccd  checkpoint_ledger.json
2e0a9fee1b6729466affd4c5f7f6e86c96e696e20882c9f4ad52ae3792d82957  risk_pilot_values.npz
2a9aa472e64747047cb28de90912eecf138b28884d87e8b8219e78d99482772f  risk_pilot_values.npz.json
461d040a180dfa8e5a743967285e67f8b682f8f67607f1c0c7a5c8ab2399d7bd  risk_pilot_sampling_audit.json
120ccd8f11e681bc6d2b3054bd7522ef331a282421f7661dd7888c993b052212  manifest.md
```

- Per-frequency runtimes in increasing order were 15.899, 48.602, 58.995,
  281.801, 314.859, 627.905, 689.144, 1160.762, and 1223.231 seconds;
  total recorded compute time was 4421.198 seconds.
- Adapter-use counts were 0, 0, 0, 0, 0, 62, 92, 434, and 480; total 1068,
  exactly confined to the T7bv-accepted adapter path.
- Maximum final-adjacent-pair relative deltas across all frequencies/points
  were `6.136118112992297e-11` for plus and
  `5.492389935680416e-10` for cross, both below the frozen `1e-4` tolerance.
- The sampling audit contains exactly the five frozen local sequences for
  both components and explicitly emits no acceptance decision; T7bw owns the
  independent scientific review.

## Verification

- Direct independent audit:
  `T8AN_NINE_FREQUENCY_ARTIFACT_AUDIT=PASS`.
- Focused pytest: `11 passed in 0.66s`.
- Ruff: `All checks passed!`.
- Full pytest: `615 passed, 117 skipped, 1 xfailed, 101 warnings, 81 subtests
  passed in 310.43s`.
- Accepted T8aj and T7bv source/gate hashes were freshly rechecked and match
  all six frozen SHA256 values.
- Active output cardinality, per-frequency hashes, point arrays, shapes,
  dtypes, finiteness, masks, final pairs, metadata, ledger, aggregate equality,
  sampling records, and manifest hashes all passed.
- Required forbidden-output searches were empty. No full-grid, 0.05 scan,
  plot/PDF/PNG, fixture, Kirchhoff, paper-style, or GitHub artifact was made.

## Incomplete Work

- T7bw must independently review the saved nine-frequency pilot and accepted
  T8aj endpoints. T8an does not issue a production-grid sampling decision.
- Full 40/79-frequency production and any 0.05 refinement remain unstarted and
  separately gated.

## Blocking Issues And Non-Blocking Warnings

- No T8an blocker remains.
- Known Weyl/SciPy intermediate RuntimeWarnings occurred in accepted
  fail-closed numerical paths. Final arrays are finite, all masks are true,
  final-pair checks pass, and the full test suite passes.
- The quarantine directory is intentional provenance for the resolved
  runner cache-domain diagnosis; it is excluded from active aggregate and
  manifest content.

## Must-Read Files For The Next Thread

1. `docs/prompts/phase5_t7bw_delta0p1_risk_pilot_review.md`
2. `docs/prompts/phase5_t8an_delta0p1_nine_frequency_risk_pilot.md`
3. `runs/phase5/fig5_fig6_delta0p1_risk_pilot/manifest.md`
4. `runs/phase5/fig5_fig6_delta0p1_risk_pilot/checkpoint_ledger.json`
5. `runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_sampling_audit.json`
6. `docs/phase5_delta0p1_risk_pilot_radial_gate.md`
7. `status.md` under the 2026-07-15 T8an entry.

## Frozen Decisions

- Frequencies, Table-I points, lmax windows, amplitudes, boundary values,
  adapter name, tolerance `1e-4`, source hashes, and gate hashes are frozen.
- Transactions are valid only under the exact contract/code hash and must be
  atomic, independently hash-bound, finite, mask-valid, and final-pair valid.
- Q018 solutions are point-local unless their certified interval proves wider
  coverage; radius ordering alone never authorizes reuse.
- This output is diagnostic/risk-directed and not production approval.

## Forbidden Actions

- Do not rerun or modify T8an artifacts during T7bw review.
- Do not change physics, thresholds, lmax, radial/Q018 policy, accepted T8aj
  artifacts, or gate artifacts.
- Do not start the full 40/79-frequency grid, a 0.05 scan, plots, PDF/PNG,
  fixtures, Kirchhoff, paper-style work, or GitHub push.
- Do not treat the sampling audit as an acceptance decision.

## Superseded Prompts

- `docs/prompts/phase5_t8an_delta0p1_nine_frequency_risk_pilot.md` is complete
  and must not be rerun as a new production task.
- Earlier T8aj/T8ak/T8al/T8am prompts remain historical and must not be used
  to regenerate accepted artifacts.

## Exact Next Task

Run T7bw in the existing T7 task:

```text
你现在是 T7bw：Delta(kM)=0.1 nine-frequency risk pilot 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bw_delta0p1_risk_pilot_review.md。请直接读取九个 per-frequency artifacts 与 accepted T8aj endpoints，独立重建五个局部序列，核验 observed phase-step 与 magnitude-dominance criteria、checkpoint/provenance、tests 和 scope。不得修复 T8an，不得启动 full grid 或 0.05 scan。
```

## Allowed/Forbidden Files And Definition Of Done

- T7bw is read-only except for its own T7 coordination records explicitly
  authorized by its prompt. T8an artifacts and implementation are frozen.
- Verification commands are the direct artifact audit, focused T8an pytest,
  Ruff on the frozen five paths, full pytest, source/gate SHA256 checks, commit
  path-set checks, and forbidden-output searches recorded above.
- T8an is done only because all nine transactions, aggregate/audit/manifest,
  fresh tests, provenance, scope checks, this handoff/archive, and `status.md`
  are complete with the exact GREEN decision.
