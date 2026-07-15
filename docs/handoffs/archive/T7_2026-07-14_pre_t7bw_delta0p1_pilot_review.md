# T7 Archived Handoff — Pre-T7bw Delta0p1 Pilot Review

Last updated: 2026-07-15

Thread: T7bv, `Delta(kM)=0.1` risk-pilot radial/Q018 gate independent review.

## Exact Decision

```text
ACCEPT GREEN / DELTA0P1 RISK-PILOT RADIAL GATE ACCEPTED
```

All nine frozen independent checks pass. This GREEN means only that T0 may
dispatch the separately frozen T8an nine-frequency point-only pilot. T7bv did
not start T8an and does not authorize full-grid production, a `0.05` scan,
plots, fixtures, Kirchhoff work, or paper claims.

The pre-T7bv T7bu handoff is archived at:

```text
docs/handoffs/archive/T7_2026-07-14_pre_t7bv_delta0p1_radial_review.md
```

## Nine Independent Checks

1. **PASS — commit/scope.** Implementation commit `ee88351` changes exactly
   the five frozen paths: the radial-gate script, generated literal envelope,
   radial solver, and two physics-test files. No scattering, observable,
   config, accepted artifact, plot, fixture, or unrelated implementation path
   is in the commit.
2. **PASS — contract/cardinality.** The independently derived count is
   `sum_k 2 * 8 * (ell_max(k)-1) = 28,272`. The saved set has exactly 28,272
   unique records with all nine frequencies, both sectors, every integer
   `ell=2..ell_max`, and all eight exact Table-I points; no record is omitted
   or duplicated. Counts are 27,204 default-covered, 1,058 structured
   uncovered, 10 structured solver-failed, and zero default-other.
3. **PASS — default classification.** A fresh 26-record matrix sampled every
   frequency, both sectors, all eight radii, ordinary covered modes, and both
   structured failure classes. Every recomputed classification matched the
   stored record; no unstructured or nonfinite outcome occurred.
4. **PASS — direct oracle.** All 1,068 transition keys are unique and exactly
   equal to the raw structured-transition set. Independent recomputation of
   every saved summary maximum passes. A fresh 12-anchor matrix spans all four
   transition frequencies, both sectors, and multiple near/far radii at
   requested `precision_dps=100`; every complex field matched the saved direct
   oracle exactly and the fresh maximum effective residual was
   `5.237e-16`. Across the full artifact, the maximum effective residual is
   `6.117210310854941e-16` and maximum recorded tolerance sensitivity is
   `1.737627487569545e-7`, below `5e-6`.
5. **PASS — compression identity.** T7bv expanded the saved segments and the
   generated module independently, without calling the T4z compressor. Both
   expansions exactly equal all 1,068 raw `(kM,ell,point_id,sector)`
   transition records. Frequencies, point radii, empty low-frequency segments,
   and literal high-frequency memberships agree; there is no interpolation.
6. **PASS — adapter behavior.** Eight fresh transition anchors invoke the
   exact adapter and carry the required warning, point identity, and
   `T4z/T7bv-pending` review id. Eighteen default-covered modes spanning all
   nine frequencies produced zero mocked direct-oracle calls. Wrong
   `M`, `k`, radius, `r_out`, `r_in_eps`, `rtol`, `atol`, point membership,
   and low/high `ell` membership fail closed with structured reasons.
7. **PASS — checkpoint/provenance.** There are exactly nine checkpoint files;
   all have the frozen schema, `complete=true`, `decision=PASS`, exact
   contract/source hashes, and canonical contract hashes. Their record and
   oracle unions equal the aggregate artifacts exactly. No `.tmp` or
   quarantine file remains. The classification-time radial-solver hash
   `80eb...e186` independently matches the `ee88351` parent blob; the current
   post-integration solver hash is separately `745a...35d4`.
8. **PASS — tests/quality.** Fresh focused pytest is
   `345 passed, 65 warnings, 18 subtests passed in 309.88s`; Ruff is clean;
   fresh full pytest is
   `604 passed, 117 skipped, 1 xfailed, 101 warnings, 81 subtests passed in
   316.09s`. Warnings are the deliberately exercised SciPy fail-closed paths
   and existing Weyl/Wigner warnings.
9. **PASS — isolation.** The required forbidden-output command is empty.
   No Table-I amplification pilot, dense production, plot, fixture,
   paper-style output, implementation repair, artifact regeneration, or T8an
   execution occurred during T7bv.

## Per-Frequency Classification

```text
kM=0.4  total=1328  covered=1328  transitions=0
kM=0.8  total=1328  covered=1328  transitions=0
kM=0.9  total=1328  covered=1328  transitions=0
kM=1.6  total=2288  covered=2288  transitions=0
kM=1.7  total=2480  covered=2480  transitions=0
kM=2.8  total=4016  covered=3954  uncovered=62
kM=2.9  total=4208  covered=4116  uncovered=82  solver-failed=10
kM=3.8  total=5552  covered=5118  uncovered=434
kM=3.9  total=5744  covered=5264  uncovered=480
```

## Accepted Artifact SHA-256

```text
ee051831e1da7ebb250cab37d7da3a64d8a57298b445577f238d9cefae319d54  classification_manifest.json
8f6d23da0894d0abfb42867bf911b9da95090ad5293bc76289daf4522e4067f9  oracle_validation.json
59e99ade6993eab6d570f8a2ad18f0778595f7309fbb87fbf1edf32903b80968  resume_preflight.json
823a3553efd951cf9ba1f5deefdad8e349813756c97f47b7a5d9388854de8a11  checkpoint/kM_0p4.json
70681191d586eb9b7e821690742e29b89f9fef0301cdb7734e64e7413fc64836  checkpoint/kM_0p8.json
7f9f58f688fa7efafc6effdce849d96af778b6629b847212d5b3c167d8fad0e9  checkpoint/kM_0p9.json
24b2006a8f46f88084c1fe7a13b8ba6c346275848339917e7515f907c3515522  checkpoint/kM_1p6.json
e2835c1d83b38fae3dd271e6040873e889d330e72a0da655cc2ad6287eb8bb28  checkpoint/kM_1p7.json
ccbbaedf4ba7f7021e553610547c8fa5b091c7a4583cf867316a6b3efc6847e4  checkpoint/kM_2p8.json
3692cc6a0e08daaad803a28ab616b8b345ba23bf372fa0484629525753503361  checkpoint/kM_2p9.json
d02b863866c84ac83f20d258fe956bc4c85c7958e526ed0f8984b9380eed3d55  checkpoint/kM_3p8.json
80606dfefa9115f340733d216c4186f99a96e9d94b04bbcadaa6c0280d148b36  checkpoint/kM_3p9.json
```

Generated envelope evidence:

```text
2d4e20e76f78396fcc540e2743b4444a7f40751873f7a6a308b6cd3aba387ac0  q018_delta0p1_risk_envelope.py
```

## Precision Qualification

The oracle API received the frozen `precision_dps=80` requests and fresh
review anchors used `precision_dps=100`, but its current SciPy backend reports
actual precision `53` bits and `precision_note=double_precision_scipy`.
Artifacts expose this rather than claiming arbitrary precision. The nonzero
sensitivity evidence comes from frozen loose/tight tolerance perturbations;
70/80/100 requests are deterministic and identical on this backend. This is a
recorded limitation, not a failure of the frozen gate thresholds.

## Review-Only Changed Paths

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-14_pre_t7bv_delta0p1_radial_review.md`

T7bv modified no implementation, tests, scripts, configs, T4/T8 handoffs, or
artifacts.

## Frozen Boundary And Next Owner

- T0 alone may interpret this exact GREEN and dispatch the separately frozen
  T8an prompt.
- T7bv must not start T8an, full 40/79-frequency production, a `0.05` scan,
  interpolation, plotting, fixture promotion, or paper-style work.
- The accepted adapter remains exact, opt-in, point-only, and fail closed; it
  is not a general frequency/radius/ell extension.
- T7bv is complete only after fresh document/scope/hash verification and a
  successful exact-decision message to T0 task
  `019f5ec5-84ba-79e2-8c77-1160b150a636`.
