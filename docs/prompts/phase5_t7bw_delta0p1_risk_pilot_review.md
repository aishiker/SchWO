# T7bw — Delta(kM)=0.1 Risk Pilot Independent Review

You are the existing T7 review task. Independently review T8an's nine-frequency point-only risk pilot and decide whether it supports T0 designing later full-grid completion. You are not a repair task.

## Start Gate

Begin only after T8an reports exactly:

```text
GREEN / DELTA0P1 NINE-FREQUENCY RISK PILOT GENERATED
```

If the decision, implementation commit, nine frequency pairs, ledger, aggregate/audit/manifest, or fresh T8 verification is absent/ambiguous, stop and notify T0.

## Required Reading

Read completely:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T4_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T8_current.md`
7. `docs/superpowers/specs/2026-07-14-t4z-t8an-delta0p1-risk-pilot-design.md`
8. `docs/superpowers/plans/2026-07-14-t8an-delta0p1-nine-frequency-risk-pilot.md`
9. `docs/prompts/phase5_t8an_delta0p1_nine_frequency_risk_pilot.md`
10. this prompt
11. all five T8an implementation paths
12. accepted T8aj source triplet and all T8an artifacts

Use `receiving-code-review` and `verification-before-completion` as helpful; frozen criteria control.

## Allowed Writes

```text
status.md
docs/handoffs/T7_current.md
docs/handoffs/archive/T7_2026-07-14_pre_t7bw_delta0p1_pilot_review.md
```

Do not modify implementation/tests/scripts/configs/artifacts, T4/T8 handoffs, or unrelated handoffs.

## Independent Checks

1. **Commit/scope:** exact five T8an implementation paths; no radial, scattering formula, viz, config, fixture, source, or unrelated diff.
2. **Gate/source hashes:** independently verify T4z/T7bv gate and accepted T8aj triplet hashes.
3. **Nine transactions:** direct-load every NPZ/JSON without T8an helpers; require exact frequency/point order, shapes, dtypes, units, masks, finiteness, lmax windows/final pairs/deltas, warnings, and adapter counts.
4. **Checkpoint/provenance:** verify ledger hashes, contract hash, atomic completion, no quarantine item treated complete, git/source/config/gate hashes, and exact output cardinality.
5. **Aggregate identity:** independently stack per-frequency arrays and require byte/numeric identity with aggregate; audit JSON must be derivable but is not trusted.
6. **Five local sequences:** independently combine accepted T8aj endpoints and pilot rows into exactly:

```text
[0.3,0.4,0.5]
[0.75,0.8,0.9,1.0]
[1.5,1.6,1.7,1.75]
[2.75,2.8,2.9,3.0]
[3.75,3.8,3.9,4.0]
```

7. **Observed phase criterion:** every adjacent unwrapped phase step for every point/component is finite and `<pi/2`; spacings are `<=0.1`.
8. **Magnitude dominance:** for magnitudes use `|a-b|/max(1,|a|,|b|)`. Every refined step inside a selected coarse interval must be no larger than the same point/component's accepted coarse endpoint step plus `2e-15`. Also report total variation, largest attribution, and interior extrema without inventing another threshold.
9. **Tests/isolation:** run focused tests, Ruff, full pytest, and require no production/0.05/plot/fixture/paper artifacts.

Required commands include:

```bash
shasum -a 256 runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json runs/phase5/fig5_fig6_dense_review_grid/manifest.md
PYTHONPATH=src .venv/bin/python -m pytest -q tests/unit/test_tablei_risk_pilot.py tests/regression/test_delta0p1_risk_pilot_script.py
.venv/bin/python -m ruff check src/schwgw/io/tablei_risk_pilot.py src/schwgw/io/__init__.py scripts/phase5_run_delta0p1_risk_pilot.py tests/unit/test_tablei_risk_pilot.py tests/regression/test_delta0p1_risk_pilot_script.py
PYTHONPATH=src .venv/bin/python -m pytest -q
find runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_delta0p05_targeted runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
```

The final command must be empty. Also run an independent direct-NPZ audit script; do not call T8an metric/aggregation APIs.

## Exact Decision

Record exactly one:

```text
ACCEPT GREEN / DELTA0P1 RISK PILOT SUPPORTS FULL GRID DESIGN
ACCEPT YELLOW / DELTA0P1 RISK PILOT REQUIRES TARGETED 0P05 EVIDENCE
REJECT RED / DELTA0P1 RISK PILOT INVALID
```

GREEN requires all nine checks and means only that T0 may design later full-grid completion. YELLOW must name exact intervals, points, components, and proposed `0.05` frequencies. RED identifies invalid science, computation, provenance, artifact, test, or scope.

Update status/archive/handoff and notify T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636`. Do not repair T8an, push GitHub, dispatch another task, or start full production, `0.05`, plots, fixtures, or paper-style work.
