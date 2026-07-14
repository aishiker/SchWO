# T7bv — Delta(kM)=0.1 Risk-Pilot Radial Gate Independent Review

You are the existing T7 review task. Independently review T4z's nine-frequency radial/Q018 classification and exact adapter. You are not a repair task and must not start T8an.

## Start Gate

Begin only after T4z reports exactly:

```text
GREEN / DELTA0P1 RISK-PILOT RADIAL GATE READY
```

If the exact decision, implementation commit, gate artifacts, or fresh T4 verification is missing/ambiguous, stop and notify T0.

## Required Reading

Read completely:

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T4_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/superpowers/specs/2026-07-14-t4z-t8an-delta0p1-risk-pilot-design.md`
7. `docs/superpowers/plans/2026-07-14-t4z-delta0p1-risk-pilot-radial-gate.md`
8. `docs/prompts/phase5_t4z_delta0p1_risk_pilot_radial_gate.md`
9. this prompt
10. all five authorized implementation paths
11. all T4z gate artifacts and checkpoints

Use `receiving-code-review` and `verification-before-completion` as helpful. The frozen scientific contract controls.

## Allowed Writes

```text
status.md
docs/handoffs/T7_current.md
docs/handoffs/archive/T7_2026-07-14_pre_t7bv_delta0p1_radial_review.md
```

Do not modify implementation, tests, scripts, configs, artifacts, T4/T8 handoffs, or unrelated handoffs. Preserve unrelated worktree changes.

## Independent Nine Checks

1. **Commit/scope:** the implementation commit changes exactly the five frozen paths; no scattering/observable/config/accepted-artifact diff.
2. **Contract/cardinality:** independently derive the expected record count from nine frequencies, both sectors, ell ranges, and eight exact points; require all records and nine valid checkpoints.
3. **Default classification:** independently sample and recompute records across every frequency; require zero unstructured/default-other errors and no omitted modes.
4. **Oracle evidence:** load direct-oracle records without the T4z compressor; recompute all summary maxima and a representative cross-frequency/cross-sector/cross-radius anchor matrix at fresh precision.
5. **Compression identity:** expand generated segments and require exact set identity with raw structured transition records; no k/radius/ell interpolation.
6. **Adapter behavior:** direct-match anchors pass; default-covered modes never invoke it; wrong M/k/radius/ell/point/tolerance/r_out fail closed with structured reasons.
7. **Checkpoint/provenance:** validate atomic filenames, contract/source hashes, quarantine policy, artifact hashes, and generated-module evidence hashes.
8. **Tests/quality:** run focused radial/Q018 tests, Ruff on five paths, and full pytest fresh.
9. **Isolation:** require no Table-I amplification pilot, dense production, plotting, fixture, paper-style, or unrelated output.

At minimum run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/physics/test_q018_production_integration_design.py tests/physics/test_radial_solver.py
.venv/bin/python -m ruff check scripts/phase5_delta0p1_risk_radial_gate.py src/schwgw/numerics/q018_delta0p1_risk_envelope.py src/schwgw/numerics/radial_solver.py tests/physics/test_q018_production_integration_design.py tests/physics/test_radial_solver.py
PYTHONPATH=src .venv/bin/python -m pytest -q
find runs/phase5/fig5_fig6_delta0p1_risk_pilot runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
```

The final command must be empty.

## Exact Decision

Record exactly one:

```text
ACCEPT GREEN / DELTA0P1 RISK-PILOT RADIAL GATE ACCEPTED
ACCEPT YELLOW / DELTA0P1 RISK-PILOT RADIAL EVIDENCE INCOMPLETE
REJECT RED / DELTA0P1 RISK-PILOT RADIAL GATE INVALID
```

GREEN means only that T0 may dispatch the separately frozen T8an nine-frequency pilot. It does not authorize full-grid production, `0.05` scans, plots, fixtures, or paper claims.

Update status/archive/handoff and notify T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` with exact decision and evidence. Do not repair T4z, push GitHub, dispatch T8an, or start any later work.
