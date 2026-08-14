# T7 independent repaired-V1 to bounded-V2 transition review

Review date: 2026-08-10

Review task: `/root/t7_transition_review`

Review mode: read-only, static identity/domain/threshold reconstruction.  The
reviewer did not invoke a project validator, radial/BHPT/arbitrary-precision
solver, or write to the repository.  This file is T0's durable transcription
of the independent review result; it is not a replacement evidence root.

## Exact decision

```text
ACCEPT GREEN / V1 RADIAL REPAIR SUFFICIENT FOR BOUNDED V2 ENTRY
```

```text
full-domain V1 independent scientific certification remains PARTIAL
```

The review explicitly limited GREEN to the repaired-radial bounded transition
gate.  It did not emit Phase-6 global GREEN or convert selected external/AP
calibrations into full-domain independent coverage.

## Identity reconstruction

The reviewer recomputed 298 identity objects representing 227 unique files.
There were no SHA-256, size, mode, link-count, or path mismatches.  Seven
specified roots were mode `0555`; all contained files were regular,
`0444/nlink1`.  The release map was byte-identical to its preparation snapshot.

```text
release map
  aef59e5fe9db485b8b5c2b2909befe3777cd9ce6e0e4ecc75200392b52e8fe30
preparation canonical submission
  fc0c45db3cff9c7e68219cf26c298e45e162b6cc40d2598729e6266c4920b72f
preparation manifest
  6911f209b76965a807be44543674f21c1b225c4736ad3659b97b2b83ea2c970d
release ledger
  7ef62d6b3ff883570510854ff230821a7d3ca89c8596602df2c36d1cff66e0db
release manifest
  a139e76ac28eba5ae4595aa0bfaad6b7a9814fd2301aa7cdfd3f993fd556e594
```

The reviewer independently reconstructed 14 release certificates:
`PASS=2 / PARTIAL=12 / FAIL=0 / NOT_ASSESSED=0`.  PASS remained limited to
V0 and V6.  All V1/V1Q release certificates remained PARTIAL and
`global_green_permitted=false`.

## Algorithmic and production domains

Frozen domain hashes:

```text
D_union    a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b
D_prod     54f13ea2473fb0a04ca5e16277edae31335c03b11753973d83a934cce2f0872b
D_external d572c88259ef4b42b490af263d012a8de880458902dcf5a4d303c9f587cd466b
```

- Algorithmic radial evidence projected to the exact 17,818-key `D_union` in
  frozen order.  All eight invariants passed for every key.  Maximum radial
  flux residual was `4.9870720886247e-9 < 1e-8`; maximum Jost-series residual
  was `9.9822e-11`.  No legacy, NP, pseudoinverse, or paper-envelope path was
  present.
- Production evidence projected to exact `D_prod`: 12,666 original complete
  modes and 3,382 repaired modes were disjoint and their union was exactly
  16,048.  Every mode had the same eight-site signature, yielding 128,384
  stored radial master states.  The reviewer checked 35,478 associated
  identity objects without error.

## External 30-key coverage

Each `(kM,ell)` below contains both odd and independently solved even sectors:

```text
0.5 : 2
1   : 20, 39, 40, 41
2   : 60, 79, 80, 81, 153
4   : 120, 159, 160, 161, 360
```

Counts were odd/even `15/15`, selected low/mid/high `10/10/10`, low-ell
absorption `2`, operational turning/barrier proxy `18`, high-ell tail `4`, and
control `6`.  The turning category is the frozen `r=40M` proxy
`ell=40kM+{-1,0,+1}`, not a new analytic photon-sphere critical-ell claim.

All 30 results and 60 40/60-digit nodes were manifest-bound and passed.  Each
node independently solved In and Up solutions at three matching radii.  Even
used an independent Zerilli solve, not parity derivation; no fit or fallback
was used.  All ten frozen comparisons passed for each key.  The closest
threshold was the `r_in` phase difference
`1.7545e-6 < 2e-6`; maximum flux residual was
`2.4567e-10 < 1e-8`.

## Selected arbitrary precision

The 24 anchors formed the exact Cartesian strata
`4 k-bands x 2 parity x 3 severity`.  All 96 nodes
(`60/80 dps x two RK4 steps`) and all 24 ladders closed.  The largest
step-size complex-S difference was `6.7177e-7 < 2e-6`; the largest arithmetic
precision difference was approximately `4.70e-34`.  This remained selected
evidence and was not extrapolated to the full V1 domain.

## Scoped adjudication

```text
V1 ALGORITHMIC RADIAL DOMAIN                         PASS
V1 PRODUCTION RADIAL-STATE COMPLETENESS              PASS
V1 SELECTED INDEPENDENT NUMERICAL VALIDATION         PASS
V1 FULL-DOMAIN INDEPENDENT SCIENTIFIC CERTIFICATION  PARTIAL
```

The transition review authorizes V2.0 convention freezing only under the
prohibitions and non-claims in
`docs/phase6_v1_to_v2_transition_gate_20260810.md`.

