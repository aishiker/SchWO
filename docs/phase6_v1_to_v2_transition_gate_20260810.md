# Phase 6 repaired V1/V1Q to bounded V2 transition gate

Date: 2026-08-10

## Decision

An independent T7 read-only review returned the exact decision

```text
ACCEPT GREEN / V1 RADIAL REPAIR SUFFICIENT FOR BOUNDED V2 ENTRY
```

with the mandatory non-claim

```text
full-domain V1 independent scientific certification remains PARTIAL
```

`GREEN` in this document names only the bounded transition gate.  It is not a
Phase-6 global status, is not a full-domain V1 certificate, and does not turn
selected external or arbitrary-precision checks into full-domain independent
coverage.

The durable review transcription is
`docs/handoffs/archive/T7_2026-08-10_phase6_v1_to_v2_transition_review.md`.

## Scoped adjudication

| Observable/domain | Native adjudication | Scope qualification |
|---|---:|---|
| V1 algorithmic radial domain | PASS | Exact frozen `D_union`, 17,818/17,818 keys |
| V1 production radial-state completeness | PASS | Exact frozen `D_prod`, 16,048/16,048 modes and eight stored states per mode |
| V1 selected independent numerical validation | PASS | External direct 30/30 plus arbitrary-precision 24/24 selected anchors |
| V1 full-domain independent scientific certification | PARTIAL | No full-domain external or arbitrary-precision comparison and convention budget remains open |

The repaired formal release deliberately remains more conservative: its 14
certificates are `PASS=2 / PARTIAL=12 / FAIL=0 / NOT_ASSESSED=0`, with PASS
limited to V0 implementation verification and V6 release policy.  Its
`global_status` is null and `global_green_permitted=false`.

## Authoritative repaired identities

```text
release map
  configs/phase6_v1_repaired_release_map_20260810.json
  aef59e5fe9db485b8b5c2b2909befe3777cd9ce6e0e4ecc75200392b52e8fe30
preparation canonical submission
  runs/phase6/v1_release_preparation_repaired_v2_20260810_py314/canonical_submission.json
  fc0c45db3cff9c7e68219cf26c298e45e162b6cc40d2598729e6266c4920b72f
preparation manifest
  6911f209b76965a807be44543674f21c1b225c4736ad3659b97b2b83ea2c970d
release ledger
  runs/phase6/v1_release_repaired_v2_20260810_py314/release_ledger.json
  7ef62d6b3ff883570510854ff230821a7d3ca89c8596602df2c36d1cff66e0db
release manifest
  a139e76ac28eba5ae4595aa0bfaad6b7a9814fd2301aa7cdfd3f993fd556e594
```

Native radial evidence:

```text
algorithmic D_union
  runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314
  manifest 2ceb769e9f67f0a66f115aba23a82d573e400ea155741b7801cfbfcd501a4728
production exact-eight states
  runs/phase6/radial_validation/v1_production_state_evidence_v2_20260810_py314
  manifest 7508ec43ba066d97acb00e8745b33ee3f422b2a8819c30874a4a03c22b8616f4
external direct RW/Zerilli
  runs/phase6/radial_validation/v1_external_bhpt_direct_bounded_selected_v1_20260810_py314
  manifest e12c49b00efecc9c65d42699f2a5052ecac1fe2c988312ed21c4da085fe5ee6d
external-to-SchWO selected acceptance
  runs/phase6/radial_validation/v1_radial_selected_acceptance_v1_20260810_py314
  manifest aa66df4f449372e1af660cee8b0757d23ab494bd631bde1c229eb2ee29a2d78c
selected arbitrary precision
  runs/phase6/radial_validation/v1_ap_selected_evidence_v1_20260810_py314
  manifest c755b93c490ff836c60ec436e320ee45adc5118186a45294bfc9f608839349d9
```

Frozen domain hashes are `a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b`
for `D_union`, `54f13ea2473fb0a04ca5e16277edae31335c03b11753973d83a934cce2f0872b`
for `D_prod`, and `d572c88259ef4b42b490af263d012a8de880458902dcf5a4d303c9f587cd466b`
for the external direct inventory.

## Independent T7 checks

The review was static and read-only.  It independently rehashed 298 identity
objects representing 227 unique files, checked root/file modes and link
counts, rebuilt all three frozen domains, and did not invoke a project
validator or numerical solver.

- `D_union` contains 17,818 unique keys in exact frozen order.  All pass the
  eight required invariants; the maximum radial flux residual is
  `4.9870720886247e-9 < 1e-8`.
- `D_prod` contains 16,048 unique modes.  The original 12,666 complete modes
  and the 3,382 repaired modes are disjoint and form the exact domain; every
  mode has the same eight-site signature, for 128,384 stored states.
- The external direct domain contains 30 results and 60 independent
  40/60-digit nodes.  Each node solves both In and Up solutions at three
  matching radii.  Odd uses RW and even uses an independently integrated
  Zerilli equation; there is no parity-derived even result, fit, or fallback.
- The selected arbitrary-precision domain contains 24 anchors arranged as
  `4 k-bands x 2 parities x 3 severity levels`; all 24 ladders close.

## Exact external-30 coverage

Every listed `(kM,ell)` has both odd and even sectors:

```text
0.5 : 2
1   : 20, 39, 40, 41
2   : 60, 79, 80, 81, 153
4   : 120, 159, 160, 161, 360
```

This gives odd/even `15/15`, selected low/mid/high-frequency counts
`10/10/10`, two low-ell absorption keys, 18 turning/barrier-proxy keys, four
high-ell-tail keys, and six subcritical/control keys.  The critical category
is the frozen operational `r=40M` turning proxy
`ell=40 kM+{-1,0,+1}`.  It is not an additional photon-sphere analytic
critical-ell result.

The machine-readable V2.0 lift is
`configs/phase6_v2_0_selected_domain_20260810.json`, SHA-256
`9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`.
It freezes 15 exact odd/even `(kM,ell)` pairs, `m=-2,+2`, and two unit
plus/cross input columns: 60 mode channels per column and 120 structural
route-mode-column records per future route.  Observation angles and a full
partial-wave sum remain deferred, so this inventory is not itself a complete
angular waveform or transfer matrix.

## Superseded inputs forbidden for current work

The following remain preserved as history but must not be used as current
V1/V1Q authorities or V2.0 inputs:

- `runs/phase6/radial_validation/v1_production_state_evidence_v1_20260810_py314`;
- `runs/phase6/radial_validation/v1_final_radial_baseline_v1_20260810_py314`;
- `configs/phase6_v1_release_map_20260809.json` and its 2026-08-09 preparation/release roots;
- timed-out `v1_external_bhpt_direct_selected_v3_20260808_py314`;
- `v1_v0_verification_v1_20260808_py314`;
- every aborted duplicate-writer root or stale-manifest diagnostic described in `status.md`.

No historical root is overwritten or deleted.

## Bounded V2 entry

This gate authorizes V2.0 convention freezing only.  It does not authorize a
radial-backend change, finite-radius observer waveform, total incident plane
wave at future null infinity, paper-figure recomputation, or any V2 scientific
PASS.  The V2.0 contract, equation map, selected domain, and executable T6/T7
prompts must pass independent review before V2.1 numerical work is proposed.
