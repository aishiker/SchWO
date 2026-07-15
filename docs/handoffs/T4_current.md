# T4 Current Handoff

Last updated: 2026-07-15

Thread: T4z, Delta(kM)=0.1 risk-pilot radial/Q018 gate.

## Current status

```text
GREEN / DELTA0P1 RISK-PILOT RADIAL GATE READY
```

T4z finished the frozen radial-only nine-frequency gate. The only permitted next action is a frozen independent T7bv review. T4z must not start T8an, produce amplification/observable/Kirchhoff/plot/fixture artifacts, broaden the adapter, run a 40/79-frequency or `0.05` scan, or push GitHub.

## Required context

1. `status.md`
2. `docs/phase5_delta0p1_risk_pilot_radial_gate.md`
3. `runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/manifest.md`
4. The nine JSON files in `runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/checkpoint/`
5. `classification_manifest.json`, `oracle_validation.json`, and `resume_preflight.json` in that run directory
6. `src/schwgw/numerics/q018_delta0p1_risk_envelope.py`
7. `src/schwgw/numerics/radial_solver.py`
8. `tests/physics/test_q018_production_integration_design.py`
9. `tests/physics/test_radial_solver.py`
10. `docs/prompts/phase5_t7bv_delta0p1_risk_pilot_radial_review.md`

## Exact evidence

- Frozen matrix: nine frequencies `0.4,0.8,0.9,1.6,1.7,2.8,2.9,3.8,3.9`, both sectors, exact eight Table-I radii, `M=1`, `r_out=300`, `r_in_eps=1e-6`, `rtol=1e-10`, `atol=1e-12`.
- Classification: 28,272 records; 27,204 default-covered; 1,058 structured uncovered; 10 structured solver-failed; zero default-other.
- Direct oracle: 1,068/1,068 transition records passed; max effective residual `6.117210310854941e-16`; max relative sensitivity `1.737627487569545e-7`.
- Atomic checkpoints: all nine `complete=true` and `decision=PASS`.
- Artifact SHA-256: classification `ee051831e1da7ebb250cab37d7da3a64d8a57298b445577f238d9cefae319d54`; oracle `8f6d23da0894d0abfb42867bf911b9da95090ad5293bc76289daf4522e4067f9`.
- Fresh adapter preflight: 1,068/1,068 passed, zero failures; SHA-256 `59e99ade6993eab6d570f8a2ad18f0778595f7309fbb87fbf1edf32903b80968`.
- Adapter: `q018_tablei_delta0p1_risk_pilot_transition`, literal frequency/ell/point membership only; recovery warning `q018_tablei_delta0p1_risk_pilot_transition_oracle_used`; review id `T4z/T7bv-pending`.
- Implementation commit: `ee88351 feat: add delta0p1 risk-pilot radial gate`.

## Fresh verification

```text
T4Z_CLASSIFICATION_AND_ORACLE_AUDIT=PASS records=28272 transitions=1068 checkpoints=9
T4Z_RESUME_PREFLIGHT=PASS records=1068
Ruff: passed on the five frozen paths
Focused pytest: 345 passed, 65 warnings, 18 subtests passed in 302.50s
Full pytest: 604 passed, 117 skipped, 1 xfailed, 101 warnings, 81 subtests passed in 309.37s
```

Known warnings are deliberately exercised fail-closed SciPy paths and unrelated existing Weyl/Wigner checks. No scientific, test, artifact, scope, or provenance failure occurred.

## Scope boundary

The implementation commit changes exactly `scripts/phase5_delta0p1_risk_radial_gate.py`, `src/schwgw/numerics/q018_delta0p1_risk_envelope.py`, `src/schwgw/numerics/radial_solver.py`, `tests/physics/test_q018_production_integration_design.py`, and `tests/physics/test_radial_solver.py`.

No T8an work was started. No forbidden output directory contains a new file. The predecessor T4y handoff is archived in `docs/handoffs/archive/T4_2026-07-14_pre_t4z_delta0p1_risk_pilot.md`.
