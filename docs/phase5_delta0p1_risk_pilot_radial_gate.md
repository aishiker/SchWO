# Delta(kM)=0.1 Risk-Pilot Radial/Q018 Gate

## Decision

```text
GREEN / DELTA0P1 RISK-PILOT RADIAL GATE READY
```

T4z completed the frozen radial-only gate for `kM=[0.4,0.8,0.9,1.6,1.7,2.8,2.9,3.8,3.9]`.
This authorizes only the independent T7bv review. It does not authorize T8an, a production grid, a `0.05` scan, amplification/observable/Kirchhoff artifacts, plots, fixtures, or paper-style work.

## Measured envelope

Both sectors, every frozen integer ell, and all eight exact Table-I radii were classified with `M=1`, `r_out=300`, `r_in_eps=1e-6`, `rtol=1e-10`, and `atol=1e-12`.

| classification | count |
|---|---:|
| default covered | 27,204 |
| structured fail-closed uncovered | 1,058 |
| structured fail-closed solver-failed | 10 |
| unstructured/default-other | 0 |

All 1,068 structured transitions passed direct experimental Q018-oracle validation. The maximum effective residual was `6.117210310854941e-16`; the maximum 70/80/100-dps relative sensitivity was `1.737627487569545e-7`, below the frozen `5e-6` bound.

`src/schwgw/numerics/q018_delta0p1_risk_envelope.py` is literal data only: exact frequency, consecutive-ell, and point-ID membership, with no artifact loading, interpolation, or frequency broadening.

## Production adapter

The only new opt-in name is `q018_tablei_delta0p1_risk_pilot_transition`.

It is limited to Schwarzschild `M=1`, the nine frozen frequencies, one of the eight exact Table-I radii, both sectors, literal measured `(kM, ell, point_id)` membership, and the frozen boundary/tolerance tuple. Global configuration is prevalidated while ordinary covered modes stay on the normal solver path. A structured recoverable default failure invokes the oracle only after exact mode-membership validation. All other requests fail closed with `q018_experimental_oracle_out_of_envelope`.

Recovery emits `q018_tablei_delta0p1_risk_pilot_transition_oracle_used`, review id `T4z/T7bv-pending`, and evidence `T4z complete measured Delta0p1 risk-pilot transition set`.

## Integrity and verification

- Classification SHA-256: `ee051831e1da7ebb250cab37d7da3a64d8a57298b445577f238d9cefae319d54`.
- Oracle SHA-256: `8f6d23da0894d0abfb42867bf911b9da95090ad5293bc76289daf4522e4067f9`.
- All nine atomic checkpoints are complete/PASS; their hashes are in the run manifest.
- Fresh adapter preflight: 1,068/1,068 passed, zero failures; SHA-256 `59e99ade6993eab6d570f8a2ad18f0778595f7309fbb87fbf1edf32903b80968`.
- Focused tests: `345 passed, 65 warnings, 18 subtests passed`.
- Full suite: `604 passed, 117 skipped, 1 xfailed, 101 warnings, 81 subtests passed`.
- Ruff passed on all five frozen implementation paths.
- Implementation commit: `ee88351 feat: add delta0p1 risk-pilot radial gate`.

Known warnings are deliberately exercised fail-closed radial paths and unrelated existing Weyl/Wigner numerical checks; no test, scope, artifact, residual, sensitivity, or provenance failure occurred.

## Next owner

T7bv must independently review the checkpoint/artifact envelope, adapter fail-closed scope, tests, and forbidden-output boundary. T4z does not start T8an or perform additional scientific computation.
