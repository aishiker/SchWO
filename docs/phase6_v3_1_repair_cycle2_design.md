# Phase 6 V3.1 bounded repair cycle 2 design

Date: 2026-08-11

Scientific gate: `Phase 6 / V3.1`

Repair artifact revision: `r3` (`artifact_rev=3`; this is not scientific
stage V3)

Liveness count: initial review and bounded repair cycle 1 complete; this is
the final bounded repair cycle `2 of 2`

This document is a pre-science repair contract. It changes no V3.0 formula,
convention, domain, threshold, selector, accepted predecessor, or protected
radial byte. It does not authorize numerical execution until formal T7
approves the exact frozen package. It never authorizes V3.2 or global GREEN.

## 1. Frozen failure basis and liveness boundary

Formal T7 delta review 1 is frozen in
`docs/handoffs/archive/T7_2026-08-11_v3_1_repair_cycle1_delta_review.md`,
SHA-256
`cbd04d5bba74fef2daffca62f9e80c5c0a6589f89b35812aa8ce10a60592f55b`:

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1 CHANGES REQUIRED
```

Cycle 2 addresses exactly the two still-frozen class-A blockers:

1. `v31_route_a_first_node_native_failure`;
2. `v31_official_runner_incomplete_scope`.

It also closes the already classified compact-JSONL and complete source-ledger
class-C defects. It may not create a new acceptance item or reopen any passed
item.

If either substantive blocker remains after delta review 2, formal T7 must
return:

```text
ADVANCE_DECISION: ESCALATE
GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED
```

There is no cycle 3. A failed pre-execution prototype may be corrected only
inside the V3-local implementation paths and only while the algorithm below
is unchanged. Requiring a different algorithm, protected edit, domain change,
threshold change, or result-dependent rule stops T4 and returns to T0.

## 2. Diagnosis and bounded repair principle

The cycle-1 first-key sentinel (`kM=0.005`, odd, `ell=2`) gave exactly
`8 PASS / 12 FAIL`. Every requested node at outer multiplier 4 or 8 passed and
gave mutually stable complex `A_out` and `log|T|`; multipliers 1 and 2 failed
inside the finite-radius asymptotic Jost initialization. This establishes a
local basis-initialization defect, not permission to select a farther science
node.

Cycle 2 therefore keeps every requested match radius and every frozen ladder
node. It initializes the same `a_0=1` incoming/outgoing Jost solutions at a
deterministic auxiliary radius where the asymptotic expansion is geometrically
outside the centrifugal turning scale, transports those exact RW/Zerilli
solutions inward, and performs the coefficient match at the original requested
radius. The auxiliary choice uses no observed amplitude, residual, comparator,
or threshold outcome.

This is a V3-local numerically continued Jost adapter. It is part of Route A's
same-equation production path and is not an independent scientific route.
Route B remains a separately implemented arbitrary-precision solver and Route
C remains external BHPT.

## 3. Exact Route-A continuation algorithm

For each of the exact 9,920 logical Route-A nodes, define

```text
r_turn  = sqrt(ell*(ell+1))/omega
r_base  = max(300M, r_turn)
r_match = r_base * frozen_r_out_multiplier
n_aux   = min { n in [0,1,2] : omega*(2^n*r_match) >= 4*sqrt(ell*(ell+1)) }
r_aux   = 2^n_aux * r_match
```

Because `r_match >= r_turn`, the set is always nonempty. `n_aux` is a pure
function of the frozen key and requested node. No alternative auxiliary
radius may be tried after seeing a science value. The first failed baseline
has `n_aux=2`; its multiplier-2 nodes have `n_aux=1`; multiplier-4/8 nodes
have `n_aux=0`.

### 3.1 Direct branch (`n_aux=0`)

Call the protected public
`solve_scaled_tortoise_radial_at_radius` once with the exact frozen request and
`r_out=r_match`. Preserve its raw operands, logs, phases, diagnostics, runtime,
and protected source identity. There is no fallback.

### 3.2 Continued branch (`n_aux>0`)

1. Call the same protected public solver exactly once with the frozen
   `r_in_eps`, Jost order, tolerance and sector, with
   `required_radius=40M`, `evaluation_radii=(r_match,)`, and `r_out=r_aux`.
   This supplies the horizon-normalized/unit-incoming physical state at the
   requested match radius while using a valid auxiliary asymptotic start.
2. At `r_aux`, construct incoming and outgoing `jost_1_over_r` columns with
   the protected `outer_asymptotic_basis`, the requested Jost order, and
   leading coefficient `a_0=1`. Convert `dpsi/dr` to `dpsi/dr_star=f dpsi/dr`.
3. In a new V3-local implementation, integrate both complex Jost columns
   inward from `r_aux` to the exact `r_match` through their sector's exact
   RW or Zerilli equation in `r_star`, using DOP853, the node's frozen
   `rtol/atol`, deterministic segments no longer than `4M`, and independent
   positive-real column rescaling. Store every accumulated log scale.
4. Reconstruct a scaled two-component physical state at `r_match` from its
   stored log-amplitudes and phases, so a compatibility complex underflow is
   never treated as zero science. Match it to the two inward-continued Jost
   columns by an exact column-scaled 2-by-2 solve. Least squares,
   pseudoinverse, NP, legacy, fitted, clipped, or result-dependent fallback is
   forbidden.
5. If scaled match coefficients are `c_-`, `c_+`, physical-state log scale is
   `L_h`, and the continued-column log scales are `L_-`, `L_+`, retain

   ```text
   log|a_in|  = log|c_-| + L_h - L_-
   arg(a_in)  = arg(c_-)
   log|a_out| = log|c_+| + L_h - L_+
   arg(a_out) = arg(c_+)
   S_raw      = a_out/a_in
   log|T|     = log|T_aux| - log|a_in|
   arg(T)     = arg(T_aux) - arg(a_in)
   ```

   and then expose the final unit-incoming convention `A_in=1`,
   `A_out=S_raw` before applying the frozen `(-1)^(ell+1)` S-matrix factor.
   Positive rescalings cannot alter phase.
6. Require finite scaled states, finite coefficients, nonzero incoming
   coefficient, exact requested-radius identity, correct source identities,
   and successful ODE termination. Any failure fails the logical node. Basis
   residual, tail ratio, determinant, column Wronskian, conjugacy, current
   drift, match residual, condition number, auxiliary radius and `n_aux` are
   recorded as diagnostics; none may be used to select a different node or
   auxiliary radius.

The node record must distinguish `requested_match_radius` from
`jost_initialization_radius`. The frozen `r_out/Jost` ladder compares results
at the requested match radii exactly as before. The auxiliary radius is an
algorithmic initialization coordinate, not a replacement science node.

### 3.3 Route-A physical operands

For every completed logical node, preserve separately:

- raw continued match coefficients and all log/phase operands;
- `A_in=1`, `A_out`, and `T_horizon` after final normalization;
- `S=(-1)^(ell+1) A_out`;
- `j_in=-omega`, `j_out=+omega*|A_out|^2`, and
  `j_H=-omega*|T_horizon|^2` under `exp(-i omega t)`;
- positive `F_in=-j_in`, `F_out=j_out`, `F_H=-j_H`;
- direct `log_Gamma_flux=2*log|T_horizon|` and arbitrary-exponent decimal
  Gamma representation;
- cancellation-aware `log|S|` and
  `Gamma_S=-expm1(2*log|S|)`, independently evaluated from the S route;
- `Gamma_flux` and `Gamma_S` as separate fields, with no clipping.

An underflowed binary64 probability is compatibility metadata only and cannot
satisfy a comparator. The log/arbitrary-exponent representation is primary.

## 4. Independent Route-B continuation

Route B remains a fresh V3-local `mpmath` RW/Zerilli solver that imports no
protected SchWO radial implementation. It implements its own potential,
tortoise/background formulae, horizon integration, Jost recurrence,
inward-Jost continuation, exact matching, currents and serialization.

It uses the same predeclared geometric `n_aux/r_aux` policy because that policy
is part of this frozen repair contract, but shares no Route-A numerical code.
Odd and even equations are independently integrated; parity-derived even is
forbidden as an independent record.

The exact inventory remains 102 keys and 458 AP node records:

- all 102 keys at 80, 120 and 180 decimal digits;
- the 38 frozen turning keys receive the four additional 180-digit boundary/
  Jost variants already frozen in cycle 1.

All arbitrary-precision amplitudes, coefficients, currents, S, direct/S Gamma
and log Gamma use arbitrary-exponent decimal strings. Precision and boundary
comparisons remain the exact frozen comparisons. Route-B code must not call
Route A or import a protected implementation.

## 5. External Route C

Execute exactly the frozen 23 odd-only BHPT ReggeWheeler MST anchors through

```text
/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel
```

with SHA-256
`70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c`
and version
`14.3.0 for Mac OS X ARM (64-bit) (July 8, 2025)`.

Every record is a fresh external call and binds the exact BHPT
ReggeWheeler source-tree inventory/commit. No internal fallback, Phase-5/V1
value reuse, or parity-derived independent-even claim is allowed.

## 6. Exact graph, thresholds and certificates

The complete production orchestration remains exactly:

```text
Route A modes             496
Route A logical nodes     9,920 = 496*20
protected Route-A calls   9,920 (one per logical node)
Route B AP keys           102
Route B AP nodes          458
Route C external records  23
frozen V3.1 thresholds    16
ordered certificates      5
```

The 20 logical Route-A nodes and their membership/deduplication are unchanged
from cycle 1. No cross-node cached science result may replace a call. Every
threshold is loaded by exact field ID from
`configs/phase6_v3_0_thresholds.json`; values, operators and domains are
unchanged.

The five ordered certificates remain:

1. `V3_MODE_GREYBODY_NUMERICAL`;
2. `V3_MODE_GREYBODY_FLUX_VS_S`;
3. `V3_MODE_GREYBODY_EXTERNAL`;
4. `V3_MODE_PARITY_PROBABILITY`;
5. `V3_MODE_DOMAIN_COVERAGE`.

Any missing/failed/nonfinite/provenance-mismatched required record or failed
blocking threshold fails the relevant certificate and candidate. No averaging
may hide a failed mode.

## 7. Complete runner and control-plane repair

Before official science, injected synthetic execution through the same
production orchestration must publish and independently reload exact
`496/9920/102/458/23`, all 16 thresholds and five certificates. Synthetic
records are marked
`scientific_evidence=false`, `science_executed=false`, and
`kernel_unit_test_only=true` and can never become science evidence.

The runner must provide complete deterministic loops, validators and terminal
success/failure publication for Routes A/B/C. It must emit one compact sorted
JSON object plus one LF per JSONL record, and the source map must contain start
and end identities for every V3.0 authority, current V1/V2 authority,
D-union plan, seven protected files, V3-local implementation/runtime, Wolfram
binary and BHPT source tree.

Official checkpoint/resume uses one coordinator writer, `O_EXCL`, per-record
flush+fsync, a nonblocking single-writer lock and exact contract/source hash
revalidation. Resume is permitted only after an operating-system/process
interruption with no scientific failure and a byte-valid contiguous prefix.
Scientific, threshold, nonfinite, provenance or validator failure is terminal
and may not be retried in the same or a new root as part of cycle 2.

## 8. Pre-execution gates

T4 may iteratively correct V3-local implementation defects before an official
root, provided this frozen algorithm and all protected/scientific identities
remain unchanged. It must complete all gates below:

1. static/dataflow and injected tests prove the complete
   `496/9920/102/458/23` runner and both terminal paths;
2. exact threshold-boundary, missing-data, log-underflow, parity-derived-even,
   external-fallback, manifest/source tamper, JSONL and resume tests pass;
3. a non-scientific first-key 20-node sentinel gives `20/20` finite completed
   nodes, includes the original baseline, and passes every applicable frozen
   ladder threshold without favorable selection;
4. for the first key's multiplier-4/Jost-160 baseline-tolerance node, a
   non-scientific shadow continuation initialized at twice that radius agrees
   with the direct `n_aux=0` result under the already frozen
   `V3T-S-COMPLEX-001` and `V3T-ROUT-JOST-LOGGAMMA-001` budgets; the shadow is
   diagnostic only and never replaces a node;
5. fixed Route-A stratum sentinels complete independently for
   `(0.005,2,odd/even)`, `(0.01,12,odd/even)`, `(2,10,odd/even)`, and
   `(8,49,odd/even)` at the frozen baseline plus their required continuation
   diagnostics;
6. fixed independent AP sentinels complete for `(0.005,2,odd/even)` and
   `(2,10,odd/even)` at 80/120 digits and agree with Route A under applicable
   frozen thresholds;
7. one fresh external `(0.1,2,odd)` BHPT MST sentinel completes and converts
   under frozen conventions;
8. the synthetic full-route root publishes/reloads, focused/all-V3 tests,
   Ruff, compileall and diff-check pass, and runtime/disk projection is
   recorded;
9. all inputs/protected/package/implementation identities rehash immediately
   before official-root creation.

The fixed sentinels were chosen from frozen strata before cycle-2 execution.
They are not a narrowed production domain and do not replace any official
record.

## 9. Allowed and forbidden files

Before package freeze, T0 may create only this design, the cycle-2 package
manifest and T4/T7 prompts. After formal T7 package approval, T4 may edit or
create only:

- `src/schwgw/validation/phase6_v3_continued_jost.py`;
- `src/schwgw/validation/phase6_v3_mode_greybody*.py`;
- `scripts/phase6_v3_1_*.py` and V3.1-specific `.wls` helpers;
- `tests/unit/test_phase6_v3*.py`;
- `tests/physics/test_phase6_v3*.py`;
- `tests/regression/test_phase6_v3*.py`;
- `docs/phase6_v3_1_mode_greybody.md`;
- one T4 archive plus `docs/handoffs/T4_current.md` and `status.md` after an
  actual state change;
- `/tmp` for non-authoritative sentinels/synthetic roots;
- one fresh official `r3` root.

T4 must not modify:

- the seven protected radial files;
- any V1/V2/V3.0 authority, config, formula, threshold, prompt or immutable
  evidence root;
- this design, package manifest, T4 execution prompt, or either T7 prompt;
- either failed `r1` root or any cycle-1 diagnostic;
- V2 waveform/flux, finite-radius observer, legacy/NP/pseudoinverse or Li
  code/artifacts;
- global environments, PATH, Wolfram installation or BHPT source snapshot.

## 10. Official artifact and independent delta review

Only after every pre-execution gate passes may T4 create once:

```text
runs/phase6/classic_scattering/v3_1_mode_greybody_r3_<UTC-Z>_py314
```

The manifest must state `artifact_rev=3`, `timezone=UTC`, and distinguish this
artifact revision from scientific stage `V3.1`. It must be no-overwrite,
terminal, immutable (`0555`; files `0444`, direct regular nlink1), reloadable
in place and from a distinct copy, and bind all raw records, source identities,
uncertainty budgets, extrema, summaries and certificates.

T0 then performs a read-only identity/count/process verification and dispatches
formal T7 delta review 2. Only the exact verdict below authorizes V3.2:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V3.1 MODE GREYBODY EVIDENCE READY FOR V3.2
```

Common absolute phase remains a permitted `PARTIAL` nonclaim. The verdict is
bounded to the frozen V3.1 domain and never means full-domain or global GREEN.

## 11. Mandatory nonclaims

- no modification or new acceptance of the protected radial backend;
- no claim that Route A and Route B are independent if they share code;
- no independent external even-sector BHPT claim;
- no V3.2, angular scattering, glory, finite-radius observer or Li-figure
  result;
- no full-domain V3 certification;
- no global GREEN.
