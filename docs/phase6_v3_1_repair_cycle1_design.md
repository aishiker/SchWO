# Phase 6 V3.1 bounded repair cycle 1 design

Date: 2026-08-11

Scientific gate: `Phase 6 / V3.1`

Repair artifact revision: `r2`

Liveness count: initial review complete; bounded repair cycle `1 of 2`

This document is a repair candidate, not a scientific result. It changes no
V3.0 formula, convention, domain, threshold or accepted predecessor. It does
not authorize V3.2 or global GREEN.

## 1. Frozen failure basis

The formal T7 initial review is:

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: FAIL
GATE_LABEL: REVIEW YELLOW / V3.1 CHANGES REQUIRED
```

It is frozen in
`docs/handoffs/archive/T7_2026-08-11_v3_1_initial_failure_review.md`,
SHA-256 `d0cb93d0ade94d0376a09e4207d6059558c04c2b45383fcb42039525dad2d7c5`.

Repair cycle 1 addresses exactly two class-A findings:

1. `v31_route_a_first_node_native_failure`;
2. `v31_official_runner_incomplete_scope`.

It also closes two class-C publication defects without changing science:

1. every JSONL record must be one compact canonical JSON object plus one LF;
2. the source map must contain complete start/end ledgers for the eight V3.0
   authorities, current V1/V2 authorities, D-union plan, seven protected
   radial files, implementation, runtime and external source/runtime.

The following immutable roots are evidence of failure only and are forbidden
as resume targets, accepted inputs or publication bases:

```text
runs/phase6/classic_scattering/v3_1_mode_greybody_r1_20260811T120359Z_py314
  manifest f2320d5da8bfebdf3b0542dd6bcbb0cf3b6e855bd363ea0342c8ef697a19bb8c
runs/phase6/classic_scattering/v3_1_mode_greybody_r1_20260811T120717Z_py314
  manifest 78ee1b9b9c9490ddb438639d175a7e9f0ec4b46985c7d35fc604f4a497e0e319
```

## 2. Immutable scientific inputs

The repair must rehash at start, immediately before official execution, and
after terminal publication:

- the eight accepted V3.0 authority identities already frozen in
  `docs/prompts/phase6_t4_v3_1_mode_greybody.md`;
- the V3.0 T7 archive `b672c7f3...c0126`;
- the V3.1 initial T7 archive `d0cb93d0...d2d7c5`;
- D-union plan `de266846...067e3`;
- all seven protected radial source hashes from the V3.0 domain config;
- current V1 radial, V1 production-state, V1 selected-independent and V2
  release manifests from the `status.md` authority header;
- external SSD WolframKernel path
  `/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel`,
  SHA-256 `70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c`,
  and its version output;
- the exact BHPT ReggeWheeler source-tree inventory used by the fresh Route C.

Any drift is a pre-science HOLD. No accepted input may be repaired or replaced.

## 3. Allowed and forbidden changes

Allowed implementation scope is limited to:

- `src/schwgw/scattering/absorption.py` only if a V3-specific raw-current or
  log-Gamma helper cannot be cleanly kept under validation;
- `src/schwgw/validation/phase6_v3_mode_greybody*.py`;
- `scripts/phase6_v3_1_*.py` and V3.1-specific `.wls` helpers;
- `tests/unit/test_phase6_v3*.py`;
- `tests/physics/test_phase6_v3*.py`;
- `tests/regression/test_phase6_v3*.py`;
- `docs/phase6_v3_1_mode_greybody.md`;
- T4 current/archive and `status.md` after an actual state change;
- `/tmp` for non-authoritative smoke artifacts;
- one fresh no-overwrite official `r2` root.

The repair must not modify:

- any of the seven protected radial files;
- V1/V2/V3.0 authorities, configs, thresholds, prompts or immutable roots;
- either failed `r1` root;
- V2 waveform/flux modules, finite-radius observer code, legacy/NP/
  pseudoinverse paths or Li artifacts;
- any global environment, PATH or Wolfram installation.

## 4. Route A repair and exact node graph

Route A must call the accepted, byte-frozen public function
`solve_scaled_tortoise_radial_at_radius` from
`src/schwgw/numerics/scaled_tortoise_radial.py`. It must not call the failed
generic `solve_radial_mode` path, and it must not add a result-dependent
backend fallback.

For every one of the exact 496 ordered keys, construct
`ConditionedRadialRequest` with:

- `required_radius=40M`;
- `outer_basis="jost_1_over_r"`;
- exact parity/ell/omega from the frozen inventory;
- `r_out_base=max(300M,sqrt(ell(ell+1))/omega)`;
- all other fields from the frozen node tuple.

The exact unique per-key node graph is 20 calls:

1. `r_in` axis: three nodes at `1e-8,1e-10,1e-12`, with
   `(r_out_multiplier,Jost,rtol,atol)=(1,160,1e-10,1e-12)`;
2. outer/Jost grid: all 16 Cartesian nodes
   `r_out_multiplier=(1,2,4,8)` by `Jost=(80,120,160,200)`, with
   `(r_in,rtol,atol)=(1e-10,1e-10,1e-12)`;
3. tolerance axis: three frozen tolerance pairs, with
   `(r_in,r_out_multiplier,Jost)=(1e-10,1,160)`;
4. exact duplicate tuples are executed once and carry every membership label.

Therefore the complete Route-A ladder inventory is exactly `496*20=9,920`
solver calls. The sole mode baseline is the exact tuple
`(r_in=1e-10,r_out_multiplier=1,Jost=160,rtol=1e-10,atol=1e-12)`.
There is no favorable post-hoc baseline selection. A missing, failed,
nonfinite or provenance-mismatched node makes the key and official candidate
fail closed.

For the unit-incoming result, preserve independently traceable operands:

- `A_in=1`, `A_out` from the Jost ratio and `A_H=T_horizon`;
- signed currents under `exp(-i omega t)`:
  `j_in=-omega|A_in|^2`, `j_out=+omega|A_out|^2`,
  `j_H=-omega|A_H|^2`;
- positive fluxes `F_in=-j_in`, `F_out=j_out`, `F_H=-j_H`;
- `S=(-1)^(ell+1) A_out/A_in`;
- direct `log_Gamma_flux=2*log_abs_T_horizon` and a nonzero
  arbitrary-exponent decimal representation when binary64 Gamma underflows;
- independent `Gamma_S=1-|S|^2`, evaluated with cancellation-aware arithmetic
  from stored raw `S`, never copied from the direct horizon route.

No probability may be clipped. Signed currents and positive fluxes must remain
different fields.

## 5. Route B independent AP repair

Route B must be a V3-specific arbitrary-precision direct RW/Zerilli solver
that imports no protected SchWO radial implementation. It may reuse the
audited mathematical design of `phase6_mpmath_radial_repair.py`, but its V3
integration, potential, Jost, matching, amplitude, current and serialization
call graph must be explicit and independently hash-bound.

Use the frozen project-local `mpmath 1.4.1` overlay. Odd and even are separate
integrations. Parity-derived even data are forbidden.

For all 102 exact AP keys, execute the precision baseline at 80, 120 and 180
decimal digits with `r_in=1e-10`, `r_out_multiplier=1` and Jost order 160.
For the 38 turning-anchor keys, additionally execute at 180 digits:

- `r_in=1e-8` and `1e-12` at base outer/Jost;
- `r_out_multiplier=2`, `r_in=1e-10`, Jost 160;
- `r_out_multiplier=1`, `r_in=1e-10`, Jost 200.

This is exactly `102*3 + 38*4 = 458` AP node records. Low and evanescent AP
keys retain the full three-precision ladder while their complete boundary
systematics are supplied independently by the mandatory Route-A 20-node
graph. This allocation changes no frozen threshold; it makes the extra
turning-boundary requirement explicit before execution.

Every AP record preserves arbitrary-exponent decimal strings for all complex
amplitudes, signed currents, positive fluxes, S, direct Gamma, S-route Gamma
and log Gamma. The 80/120/180 adjacent comparisons are evaluated exactly.
Underflowed binary64 zero is never accepted.

## 6. Route C fresh external repair

Execute all 23 frozen odd-only anchors through fresh Black Hole Perturbation
Toolkit `ReggeWheeler` MST output using the exact external-SSD WolframKernel.
The official Route C must not reuse the smoke output or any Phase-5/V1 value.

Freeze per record:

- package source-tree identities and license/commit provenance where present;
- exact WolframKernel path/hash/version;
- method `MST`;
- raw incidence/reflection/transmission operands returned by the package;
- explicit conversion to frozen `V3-F02`/`V3-F04`;
- odd-only scope and `external_even_independently_solved=false`.

No internal fallback or parity-derived independent-even claim is allowed.

## 7. Complete runner, thresholds and certificates

Before real science, a fully injected synthetic end-to-end run must prove that
the same production orchestration path can publish and independently reload:

- 496 Route-A mode records;
- 9,920 Route-A ladder records;
- 102 AP terminal keys and 458 AP node records;
- 23 external records;
- all 16 frozen threshold fields with raw operands and extrema;
- exactly five ordered certificates.

The synthetic fixture must not be usable as scientific evidence and must state
`scientific_evidence=false`, `science_executed=false` and
`kernel_unit_test_only=true`.

The real validator must rebuild inventories, threshold outcomes, budgets,
summary and certificates only from raw records. It must reject missing/extra/
duplicate keys, incomplete node membership, parity-derived even, internal
external fallback, protected identity drift, nonfinite or underflow-zero
substitution, summary-only promotion and manifest/source-map drift.

All JSONL writers use compact sorted JSON with no internal LF followed by one
record-terminating LF. Canonical pretty JSON remains allowed only for `.json`.

## 8. Mandatory pre-execution gates

No official root may be created until all of these pass:

1. focused unit/physics/regression tests and all `test_phase6_v3*.py`;
2. Ruff check/format, compileall and scoped diff-check;
3. synthetic full-route publication plus in-place and distinct-copy reload;
4. the exact formerly failed Route-A key's complete 20-node graph;
5. Route-A sentinels covering both parities and low, turning, transmitted and
   evanescent/high-ell strata, including the largest frozen `r_out` node;
6. AP sentinels covering low odd/even, turning odd/even and evanescent odd/even
   at all 80/120/180 precisions, plus the turning boundary variants;
7. fresh external sentinels spanning low/mid/high selected kM;
8. a measured runtime/disk projection for the complete 9,920/458/23 workload;
9. source/runtime/run-contract freeze and a second protected-identity rehash.

Smoke outputs live only under `/tmp`, carry `scientific_acceptance=false` and
cannot populate the official root. A smoke failure allows further edits only
inside this already approved pre-execution repair scope. If no protected
backend can pass the exact first node without modifying protected bytes, stop
and return to T0; do not start official science.

## 9. Official execution and terminal protocol

The only official target pattern is:

```text
runs/phase6/classic_scattering/v3_1_mode_greybody_r2_<YYYYMMDDTHHMMSSZ>_py314
```

The manifest must record `scientific_stage="V3.1"`, `artifact_rev=2`,
`created_at_utc` and `timezone="UTC"`.

Use one coordinator/single writer, a nonblocking process lock, deterministic
ordered checkpoints, per-record atomic replacement plus fsync, and exact
source/runtime/contract-bound resume only after a genuine system interruption.
Workers may compute independent keys, but only the coordinator writes and the
published order is frozen. A scientific, threshold, nonfinite or provenance
failure is terminal and is not a resume reason.

After completion, build the formal files, reload from raw records, write the
manifest last, make every direct file regular `0444`/nlink1 and root `0555`,
then validate in place and from a distinct temporary copy. No staging residue,
writer, lock, symlink or hardlink may remain.

The candidate retains:

```json
{
  "global_status": null,
  "global_green_permitted": false,
  "independent_review_state": "NOT_ASSESSED"
}
```

Run the full repository suite only after the root is terminal. T4 may issue
only `CHECKPOINT / V3.1 MODE GREYBODY EVIDENCE FROZEN` on a complete candidate;
formal T7 delta review alone may accept the bounded gate.

## 10. Stop and escalation boundaries

Stop without an official run if a frozen input drifts, the complete production
path cannot be proven synthetically, any mandatory sentinel fails, runtime/
disk is unsafe, or a protected change is required.

After official start, preserve any science failure exactly and return to T0;
do not edit and rerun. This is repair cycle 1. If formal T7 delta review still
returns REPAIR, T0 may design at most repair cycle 2. A repeated substantive
blocker after cycle 2 requires
`ESCALATE / T0 ADJUDICATION REQUIRED`.

