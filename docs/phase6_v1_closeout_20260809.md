# Phase 6 Independent Physical Validation — full V1 closeout

Date: 2026-08-09

## Post-repair consolidation — 2026-08-10

The canonical 15-certificate release described below remains immutable as the
2026-08-09 pre-repair snapshot.  It was not overwritten.  A fresh repaired
chain has now been published and independently reloaded; the complete account
is in `docs/phase6_v1_radial_repair_v2_20260810.md`.

The repaired radial evidence closes the implementation failures without
claiming full-domain scientific equivalence:

- bounded external direct Regge--Wheeler/Zerilli and the no-fit SchWO
  comparison pass all frozen gates for the selected 30-key domain;
- `24/24` independent 60/80-dps selected ladders pass;
- exact-eight production coverage is `16,048/16,048` modes and `128,384`
  radial master states;
- the generic turning-aware full baseline is `17,818/17,818` algorithmic PASS,
  zero FAIL, maximum flux residual `4.9870720886247e-9 < 1e-8`;
- full-domain V1/V1Q release projections remain PARTIAL because independent
  precision/backend and convention budgets are selected-domain rather than
  `D_union`-complete.

The fresh chain is:

| layer | path | SHA-256 |
|---|---|---|
| map | `configs/phase6_v1_repaired_release_map_20260810.json` | `aef59e5fe9db485b8b5c2b2909befe3777cd9ce6e0e4ecc75200392b52e8fe30` |
| submission | `runs/phase6/v1_release_preparation_repaired_v2_20260810_py314/canonical_submission.json` | `fc0c45db3cff9c7e68219cf26c298e45e162b6cc40d2598729e6266c4920b72f` |
| preparation manifest | `runs/phase6/v1_release_preparation_repaired_v2_20260810_py314/manifest.json` | `6911f209b76965a807be44543674f21c1b225c4736ad3659b97b2b83ea2c970d` |
| release ledger | `runs/phase6/v1_release_repaired_v2_20260810_py314/release_ledger.json` | `7ef62d6b3ff883570510854ff230821a7d3ca89c8596602df2c36d1cff66e0db` |
| release manifest | `runs/phase6/v1_release_repaired_v2_20260810_py314/manifest.json` | `a139e76ac28eba5ae4595aa0bfaad6b7a9814fd2301aa7cdfd3f993fd556e594` |

The repaired release contains 14 per-domain certificates:
`PASS=2`, `PARTIAL=12`, `FAIL=0`, `NOT_ASSESSED=0`, and
`global_status=null`.  PASS remains limited to V0 implementation verification
and V6 policy; there is still no global GREEN.  The remainder of this document
records the historical 2026-08-09 release and must be read as such.

## Verdict

The full Phase-6 V1 implementation and evidence-release package is complete.
The scientific results are not globally accepted.  Acceptance remains per
observable and explicit parameter domain, with separate numerical and
convention uncertainty budgets.  Li--Hou--Zhao figure agreement was not used
as a primary gate, and no full paper figure was recomputed in Phase 6.

The authoritative release contains 15 certificates:

```text
PASS             2
PARTIAL          6
FAIL             6
NOT_ASSESSED     1
global_status    null
```

The two PASS results are implementation/policy results only: V0 stale-metadata
and legacy-path isolation, and V6 release-policy enforcement.  They do not
promote any physical observable.

## Canonical release chain

| layer | path | SHA-256 |
|---|---|---|
| declarative map | `configs/phase6_v1_release_map_20260809.json` | `c2e388e6a93af227a77f5ad26731357f13ae58236811e80b86457deb12aa4c04` |
| preparation submission | `runs/phase6/v1_release_preparation_v2_20260809_py314/canonical_submission.json` | `6ff1369e7c5e0dc549922a0fed9797e62f9bc9e256253eefd9dbd17b0779dd1e` |
| preparation manifest | `runs/phase6/v1_release_preparation_v2_20260809_py314/manifest.json` | `a00c6df60a194d73bae420eb6023743f6ca26772b26c38bd2fbaf252258e1a53` |
| release ledger | `runs/phase6/v1_release_v1_20260809_py314/release_ledger.json` | `3f289a9f41c2ee0389e12bdf41b8f331274b3504195411dd0a19f01766f6adb4` |
| release manifest | `runs/phase6/v1_release_v1_20260809_py314/manifest.json` | `45339f748e17bdaeb2e2aae2b5cea1988e00c61ca2feca5260e7e54e45df18cf` |

The preparation and release roots are direct mode `0555`; their files are
regular mode `0444`, `nlink=1`.  Independent reload revalidated canonical
bytes, live source identities, predecessor contracts, domain inventories,
certificate derivation, separate uncertainty budgets, and final hashes.

The earlier root
`runs/phase6/v1_release_preparation_v1_20260809_py314` is a preserved failed
publication attempt.  The validator rejected a native Stage-A limitation that
used project/global status wording before writing a canonical submission or
manifest.  No scientific bytes were changed.  The adapter was repaired with
one exact domain-qualified rewrite and a fail-closed test for all other such
wording; publication then used the fresh v2 root.

## Certificate ledger

| gate | observable/domain | coverage | state | interpretation |
|---|---|---:|---|---|
| V0 | final metadata/provenance verification | 1/1 | PASS | Four machine-readable checks passed, including the full repository suite. |
| V1 | BHPT direct vs conditioned, selected 30 | 0/30 | NOT_ASSESSED | No terminal comparison exists because external direct integration timed out. |
| V1 | BHPT direct source/method, selected 30 | 0/30 | FAIL | The real external run reached its 24-hour limit and produced zero records. |
| V1 | external BHPT MST odd, selected 84 | 84/84 | PARTIAL | Odd sector is external and accurate; even remains parity-derived rather than independently solved. |
| V1 | generic conditioning union | 17,818/17,818 | FAIL | Execution inventory is complete; 5,798 keys failed closed numerically. |
| V1 | production eight-radius radial states | 16,048/16,048 | FAIL | 12,666 modes have all eight states; 3,382 modes failed closed. |
| V1 | arbitrary-precision Stage-A | 8/8 | FAIL | Two selected anchors are stable-but-incomplete and six fail closed. |
| V1Q | transition conditioning domain | 158/158 | FAIL | 68 modes are partial and 90 fail closed. |
| V1Q | production generic backend | 16,048/16,048 | FAIL | Native production failures are preserved; no paper-specific envelope is used as acceptance. |
| V2 | master to Martel--Poisson strain/flux | 2/2 | PARTIAL | Selected bridge and finite-radius roundtrip work; large-radius/external-amplitude closure is absent. |
| V2 | metric/Psi4/external cross-check | 2/2 | PARTIAL | Selected-domain evidence only; the external absolute-amplitude route is not closed. |
| V3 | spin-2 scattering benchmarks | 3/3 | PARTIAL | Benchmarks expose unresolved low-frequency, parity, series, and glory discrepancies. |
| V4 | finite-radius tidal/detector response | 2/2 | PARTIAL | Two observer/worldline tests are selected witnesses, not a general finite-arm detector response. |
| V5 | full complex 2x2 transfer | 2/2 | PARTIAL | Selected transfer and phase convention are frozen; production unit-column/independent closure is absent. |
| V6 | release and uncertainty policy | 1/1 | PASS | Per-domain status, two uncertainty budgets, and no-Li-primary/no-paper-rerun policy are enforced. |

## Principal native evidence

### Radial conditioning and production states

The immutable conditioning campaign is
`runs/phase6/radial_validation/v1_conditioning_campaign_v1_20260808_py314`.
It completed 86 shards, 17,818 keys, and 19,240 solver calls without an
execution-integrity failure.  Scientifically, 12,020 keys are PARTIAL and
5,798 are FAIL_CLOSED.  The dominant issues are Riccati step-size collapse,
unresolved incoming Jost coefficients, and complex-exponentiation overflow.

The immutable production finite-radius campaign is
`runs/phase6/radial_validation/v1_production_finite_radius_campaign_v1_20260808_py314`.
It completed 80 shards and all 16,048 production terminals.  Exactly 12,666
modes produced all eight requested Cartesian/radial states (101,328 state
records); 3,382 modes failed closed with the Riccati step-size spacing error.
These are radial master-field states.  They are not infinity waveforms,
observer responses, or detector outputs.

### Independent and external solvers

The arbitrary-precision Stage-A root is
`runs/phase6/radial_validation/v1_stage_a_mpmath_selected_anchors_v10_20260808_py314`.
It is a bounded eight-anchor diagnostic, not production-domain coverage.

The legacy external MST root remains a useful selected odd-sector calibration:
84 records have maximum complex error about `9.2112e-15`.  Even-sector values
in that root are derived by the exact parity relation, so they are not an
independent even solve.

The external direct RW/Zerilli attempt is preserved at
`runs/phase6/radial_validation/v1_external_bhpt_direct_selected_v3_20260808_py314`.
It ran for the configured 86,400 seconds with 800-digit working precision and
terminated `FAIL/EXTERNAL_DIRECT_TIMEOUT`, `science_executed=true`, and zero
external records.  The workload requested 60 high-precision boundary solves;
the upstream horizon expansion targets `10^-800` and the numerical integrator
allows unbounded step counts.  No fallback, precision reduction, restart, or
fabricated comparison was used.  Consequently the direct-versus-conditioned
comparator remains NOT_ASSESSED.

### Observable witnesses

The selected V2--V5 evidence root is
`runs/phase6/v1_observable_evidence_selected_v1_20260808_py314`.  All five
certificates are PARTIAL.  It establishes implemented, auditable selected
witnesses for the Li-to-Martel--Poisson bridge, asymptotic/flux primitives,
spin-2 benchmark machinery, two observer/worldline transport checks, and a
complex 2x2 polarization transfer matrix with frozen phase ledger.  It does
not establish production-domain convergence, an external absolute-amplitude
cross-check, a general detector response, or a production transfer matrix.

## Verification

- V0 formal evidence records `1474 passed, 119 skipped, 1 xfailed, 104 subtests`;
  the JUnit accounting is 1,474 PASS, 120 SKIP, zero FAIL.
- After the release-language repair, the focused release/preparation suite
  passed under CPython 3.14.6: `58 passed, 2 skipped`.
- The complete Phase-6 plus legacy-isolation unit suite then passed under the
  frozen runtime contract: `311 passed, 2 skipped`.
- A final post-publication full-repository run, including the three new
  release-language tests, passed with `1477 passed, 119 skipped, 1 xfailed,
  104 subtests` and 149 expected numerical warnings.
- Release-map no-write preflight, immutable preparation reload, release
  no-write preflight, and immutable final-release reload all passed.
- No Phase-6 numerical or Wolfram process remained at closeout.

## Remaining scientific work

The next scientific version must target the failures rather than rerun paper
figures:

1. consolidate the post-release full-state/adaptive-Jost repair overlays into
   a fresh release chain, and obtain exact-key arbitrary-precision or external
   validation before promoting any repaired radial slice beyond PARTIAL;
2. redesign the independent direct RW/Zerilli calculation with a bounded,
   validated asymptotic series and staged precision ladder before attempting
   the 30-key external comparison again;
3. independently solve the even sector rather than infer it by parity;
4. close large-radius metric/Psi4/external-amplitude agreement, spin-2
   low-frequency/glory benchmarks, general worldline/tetrad detector response,
   and production 2x2 transfer columns on explicit domains.

Any future result must retain separate numerical and convention uncertainty
budgets and remain scoped to its observable and parameter domain.
