# Phase 6 V1/V1Q radial repair and repaired release

Date: 2026-08-10

## Scope and verdict

This work repairs and consolidates the Phase-6 **V1/V1Q radial-validation**
slice.  It does not advance V2--V5, use Li--Hou--Zhao raster agreement as an
acceptance gate, or rerun a full paper figure.

The exact frozen `D_union` now has an algorithmically successful generic
turning-aware solve for all `17,818/17,818` keys.  The exact production domain
has all eight requested radial master states for `16,048/16,048` modes.  A
bounded external direct Regge--Wheeler/Zerilli campaign and the no-fit SchWO
comparison pass all frozen thresholds on the selected 30-key domain.

These results do **not** establish a global or full-domain scientific GREEN.
The full-domain release certificates remain `PARTIAL`: arbitrary-precision and
external-backend comparisons cover selected domains, and the absolute phase/
convention budget is not independently closed over all `D_union` keys.

## Terminal radial evidence

### Selected independent validation

- External bounded direct root:
  `runs/phase6/radial_validation/v1_external_bhpt_direct_bounded_selected_v1_20260810_py314`.
  Odd modes are independent Regge--Wheeler solves and even modes are independent
  Zerilli solves; no parity-derived even value is used.  All `30/30` keys pass
  the 40/60-digit precision and three-matching-radius ladders.  Summary and
  manifest SHA-256 values are
  `50f448455ddf978591bf210ec103a1475ea0ccc0c3efd477dda77962081c644b`
  and `e12c49b00efecc9c65d42699f2a5052ecac1fe2c988312ed21c4da085fe5ee6d`.
- SchWO versus external no-fit acceptance root:
  `runs/phase6/radial_validation/v1_radial_selected_acceptance_v1_20260810_py314`.
  All `30/30` keys pass.  Maximum external differences are
  `1.7268260316599918e-8` for complex `S`,
  `6.110507953220471e-8` for `log|T|`, and
  `7.817655042208216e-7 rad` for transmission phase, below the frozen
  `2e-6` gates.  Report/summary/manifest SHA-256 values are
  `3dc46242f171eedd15fcd5f697a728637ce863a9e393994ec611896d275939a1`,
  `ae2480c9989e9a7eaf0056ae39aefb7594ddbb3ad840c0b0bdd70c4203900695`,
  and `aa66df4f449372e1af660cee8b0757d23ab494bd631bde1c229eb2ee29a2d78c`.
- Independent arbitrary-precision wrapper:
  `runs/phase6/radial_validation/v1_ap_selected_evidence_v1_20260810_py314`.
  All `24/24` selected 60/80-dps and fine-step ladders pass; this is selected
  coverage only.  Report/manifest SHA-256 values are
  `c3ee315bb96e139297e7663a7519f06df1259d374c2079bc577a4392351a7039`
  and `c755b93c490ff836c60ec436e320ee45adc5118186a45294bfc9f608839349d9`.

### Production exact-eight radial states

The valid composed root is
`runs/phase6/radial_validation/v1_production_state_evidence_v2_20260810_py314`.
It combines the original `12,666` complete modes with the fresh `3,382`-mode
repair, giving `16,048/16,048` modes and `128,384` exact radial states.  Its V1
and V1Q projections are both `PARTIAL 16048/16048`, because a second
algorithmically independent backend and convention budget are not full-domain.
Report/manifest/source-ledger SHA-256 values are
`34701bbf930817dd37ba183cea273d6130cc6fa907b8e8fecb8a43687438954f`,
`7508ec43ba066d97acb00e8745b33ee3f422b2a8819c30874a4a03c22b8616f4`,
and `3886f002774fd5db7b9af471b1f3a1a6e0ab39acc6a283b337da99f793c832e3`.
The earlier v1 wrapper is immutable but invalid/superseded because its
provenance hash list contained dictionary keys; it must not be cited.

### Full generic `D_union` baseline

The authoritative root is
`runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314`.
It uses one paper-independent policy:

```text
r_in_eps = 1e-10
base r_out = max(300M, sqrt(ell(ell+1))/k)
candidate ladder = base r_out * (1,2,4,8)
selection = frozen Jost residual/tail/condition/determinant gates
```

All `17,818/17,818` keys pass the finite-value, signed-flux, Jost-quality and
legacy-path-isolation invariants; there are zero numerical failures.  The
maximum flux residual is `4.9870720886247e-9 < 1e-8`; maximum Jost series
residual and tail ratio are `9.982220826659957e-11` and
`8.874806913995545e-9`.  Exactly `15,768` keys retain `300M`; `2,050` use an
expanded or turning-anchored radius.  The maximum selected radius is
`8449.852069711043M` for the low-frequency high-ell part of the frozen domain.

The native algorithmic summary is PASS, while the typed V1 and V1Q release
projections are both `PARTIAL 17818/17818`.  Summary/report/manifest/records
SHA-256 values are
`22afce89c31b6c606c3140ae31f2c9d6ef2f1b1c36e65d553be052afbcf332a3`,
`22883fdced4a1b8a93845dbe11179238220075de49548ee8149ba471df8c101d`,
`2ceb769e9f67f0a66f115aba23a82d573e400ea155741b7801cfbfcd501a4728`,
and `03f56dd7f8c4e41a9983b6ab1d919a7880aaf80573ded65dcacf48e57a5e80a7`.
The root is direct `0555`; every file is `0444`, `nlink=1`, and the strict
native validator recomputes the live implementation/runtime plan.

The predecessor fixed-radius diagnostic
`v1_final_radial_baseline_v1_20260810_py314` remains immutable at
`17,715 PASS / 103 FAIL`.  Its failures diagnose a ladder that stayed inside
the low-frequency high-ell turning region; it was not overwritten or relabelled.

## Repaired release chain

The 2026-08-09 release remains immutable as a historical pre-repair snapshot.
The fresh repaired chain is:

| layer | path | SHA-256 |
|---|---|---|
| V0 verification | `runs/phase6/v1_v0_verification_v2_20260810_py314/verification.json` | `0795a35f0c3a3156dcc1788554996c6019a4d1de2704956b473d20f2376e4819` |
| release map | `configs/phase6_v1_repaired_release_map_20260810.json` | `aef59e5fe9db485b8b5c2b2909befe3777cd9ce6e0e4ecc75200392b52e8fe30` |
| preparation submission | `runs/phase6/v1_release_preparation_repaired_v2_20260810_py314/canonical_submission.json` | `fc0c45db3cff9c7e68219cf26c298e45e162b6cc40d2598729e6266c4920b72f` |
| preparation manifest | `runs/phase6/v1_release_preparation_repaired_v2_20260810_py314/manifest.json` | `6911f209b76965a807be44543674f21c1b225c4736ad3659b97b2b83ea2c970d` |
| release ledger | `runs/phase6/v1_release_repaired_v2_20260810_py314/release_ledger.json` | `7ef62d6b3ff883570510854ff230821a7d3ca89c8596602df2c36d1cff66e0db` |
| release manifest | `runs/phase6/v1_release_repaired_v2_20260810_py314/manifest.json` | `a139e76ac28eba5ae4595aa0bfaad6b7a9814fd2301aa7cdfd3f993fd556e594` |

The release has 14 certificates:

```text
PASS             2   (V0 implementation verification, V6 policy)
PARTIAL         12
FAIL             0
NOT_ASSESSED     0
global_status    null
```

The selected 30-key native comparison is a scoped numerical PASS, but its
release certificate remains PARTIAL because the normalized source is a single
composite evidence role; the release layer does not split it into invented
primary and independent envelopes.  This is intentional conservatism, not a
failed numerical gate.

## Verification and remaining boundary

- Formal V0 full-suite root: `1533 passed`, `120 skipped`, zero failed.
- Post-release full repository run with the repaired map-builder tests:
  `1535 passed`, `119 skipped`, `1 xfailed`, `151 warnings`, `104 subtests`.
- Release/preparation focused regression before publication:
  `62 passed`, `2 skipped`; map-builder serialization tests: `2 passed`.
- Native full-domain, preparation and release post-publication reloads all
  pass.  No numerical or paper-figure process remains active.

Remaining work is scientific closure, not another solver-crash cleanup:
full-domain arbitrary-precision/external comparison, full-domain boundary and
order ladders where required, and independent convention/absolute-phase
validation.  V2--V5 retain their prior selected-domain PARTIAL states.
