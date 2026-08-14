# Phase 6 V3.1-U high-precision unitarity-deficit replacement design

Date: 2026-08-11

Gate ID: `phase6_v3_1_hp_unitarity_deficit_replacement_v1`

Display label: `V3.1-U / HIGH-PRECISION UNITARITY-DEFICIT REPLACEMENT GATE`

This document is Root T0's adjudication after formal T7 exhausted the original
V3.1 gate's two bounded repairs.  V3.1-U is a distinct replacement gate with a
fresh liveness counter.  It is not repair cycle 3, an `r3` retry, or V3.2.

## 1. Frozen science boundary

V3.1-U preserves without modification:

- the exact 496-mode V3.1 domain;
- all 16 V3.0 threshold IDs, operators, values and domains;
- all V3.0 formulas and conventions;
- the five V3.1 certificate IDs;
- Route A's 496 modes, 9,920 ordered ladder nodes and protected-call graph;
- Route B's 102 selected AP keys and 458 ordered nodes;
- Route C's 23 fresh odd-sector external records;
- all seven protected radial source bytes.

The failed immutable root
`runs/phase6/classic_scattering/v3_1_mode_greybody_r3_20260811T133458Z_py314`
is failure evidence only.  It may not be resumed, copied, cached, promoted, or
used as a science-record input to V3.1-U.

## 2. Adjudicated numerical defect

Official mode `(kM=0.005, ell=2, odd)` stored

```text
Gamma_flux = 1.836777608324503e-14
Gamma_S_float64 = 1.8096635301389888e-14
abs(log(Gamma_flux)-log(Gamma_S_float64)) = 0.01487180343263006
```

against the unchanged limit `2e-4`.  From the cycle-2 diagnostic's original
80-dps decimal strings, independent reconstruction gives

```text
Gamma_S_AP = 1.8367870337333498168909855594862587860414460956739714e-14
Gamma_flux_AP = 1.8367868805916905830712478346703039465718942407331828e-14
abs(log(Gamma_flux_AP)-log(Gamma_S_AP)) = 8.33747531996819e-8
abs(log(Gamma_flux_RouteA)-log(Gamma_flux_AP)) = 5.0481036691e-6
```

The 80/120-dps results agree to their displayed precision.  At this Gamma,
`Gamma/eps64=82.7211`, whereas the `2e-4` relative budget corresponds to only
`0.01654 eps64` in the subtracted quantity.  The defect is therefore loss of
representability in a binary64 unitarity deficit near `|S|=1`, not evidence of
a physical flux violation.  Reformatting binary64 values cannot restore the
lost information.

This diagnostic is design evidence, not reusable V3.1-U acceptance evidence.
V3.1-U must reproduce the conclusion with fresh pre-execution calculations.

## 3. Deterministic Route-U selector

V3.1-U first computes all fresh Route-A records.  Before any Route-U solve, it
creates and atomically freezes `unitarity_route_map.json` in exact 496-mode
order.  The selector is

```text
use_route_u iff Route-A direct log_Gamma_flux < log(1e-8)
```

The comparison uses the direct horizon `T_H` result and its stored
arbitrary-exponent Gamma representation.  It must not read binary64 `S`,
`Gamma_S`, a route-agreement residual, a threshold outcome, a regime label, or
any external/AP result.  Nonfinite, nonpositive or branch-ambiguous direct
flux fails closed.  The route map records the exact source record identity,
selector operands, decision and ordinal, and is hashed before Route U starts.

The resulting count `N_U` is data-derived and satisfies `0 <= N_U <= 496`.
Earlier V1 bytes suggest about 318 routed modes but are neither a frozen count
nor a V3.1-U science input.

## 4. Independent Route-U oracle

For every routed baseline mode, Route U performs a fresh arbitrary-precision
odd RW or even Zerilli solve.  It independently implements horizon
propagation, outgoing/incoming Jost columns, continuation and exact 2x2
matching.  It may share the analytic equations and frozen conventions with
Route A, and may share implementation bytes with Route B, but it may not import
or call Route-A numerical code or any of the seven protected radial modules.
Route-B records or caches may not substitute for Route-U calls.

The accepted S-route operand is computed only from the Route-U complex S:

```text
log_abs_S_U = 0.5 * log(Re(S_U)^2 + Im(S_U)^2)
Gamma_S_U = -expm1(2 * log_abs_S_U)
```

It must not be inferred from direct horizon flux.  Each record preserves
arbitrary-exponent decimal strings for `S_U`, `log_abs_S_U`, `Gamma_S_U` and
`log_Gamma_S_U`.

### Precision schedule

Let `e10` be the signed base-10 exponent in Route A's direct
`Gamma_flux_decimal`, so `Gamma_flux = mantissa * 10^e10` with a normalized
positive mantissa.  Define

```text
p0 = 20 * ceil(max(80, 30 - e10) / 20)
precision_nodes = [p0, p0 + 40, p0 + 100]
```

This rule is frozen before execution and gives at least 30 decimal guard
digits for the unitarity deficit.  It is not changed after seeing an oracle
result.  Every routed mode must complete all three ordered nodes.  Admission
requires finite positive `Gamma_S_U`, at least 30 recorded guard digits,
adjacent `log_Gamma_S_U` changes no larger than `2e-5`, and adjacent complex-S
symmetric relative changes no larger than `5e-8`.  These are additional,
stricter Route-U numerical-resolution criteria; they do not replace or relax
any V3T threshold.  Failure does not authorize post-hoc extra precision: the
candidate terminates and returns to T0 for a new design decision.

The original Route-B `80/120/180 dps` graph and its frozen precision thresholds
remain unchanged.

## 5. Threshold evaluation

All 16 frozen thresholds are evaluated over their original domains.

- If `Gamma_flux >= 1e-8`, evaluate the original absolute
  `|Gamma_flux-Gamma_S_float64| <= 2e-8` branch.
- If `0 < Gamma_flux < 1e-8`, evaluate the original
  `|log(Gamma_flux_RouteA)-log(Gamma_S_U)| <= 2e-4` branch.
- At exactly `1e-8`, use the first branch.
- For routed modes, binary64 `Gamma_S` remains an explicitly non-acceptance
  diagnostic.  `Gamma_S_U` supplies the S-route physical-bound check.
- Direct flux, Route-A ladders, parity, Route-B/AP, Route-C/external and all
  other threshold operands remain as frozen.

Numerical and convention uncertainty budgets remain separate.  The Route-U
precision envelope and Route-A-versus-U difference are recorded separately.
Common absolute phase remains `PARTIAL` and is irrelevant to this
phase-insensitive gate.

## 6. Graph and provenance

The replacement graph is

```text
Route A: 496 modes / 9,920 nodes
Route U: N_U modes / 3*N_U nodes, 0 <= N_U <= 496
Route B: 102 keys / 458 nodes
Route C: 23 fresh odd external records
thresholds: 16
certificates: 5
```

Route A and Route U share formulas/conventions only.  Route B and Route U may
share the independent mpmath implementation but have distinct logical roles,
fresh calls and record namespaces.  Route C remains external.  Every summary,
report and certificate records these non-independence boundaries explicitly.

## 7. Artifact and terminal protocol

The only official-root namespace is

```text
runs/phase6/classic_scattering/
v3_1_hp_unitarity_deficit_v1_<YYYYMMDDTHHMMSSZ>_py314
```

Required protocol:

1. fresh absent root, `O_EXCL` files and a single-writer lock;
2. no science bytes from any r1/r3 predecessor;
3. contiguous Route-A checkpoints, followed by an immutable route map;
4. only then Route U, Route B and Route C;
5. resume only after a system interruption, with exact package/source/runtime
   identities and a validated contiguous prefix;
6. no resume/retry after scientific, threshold, nonfinite, provenance or
   contract failure;
7. success and failure branches both publish complete source-start/source-end
   maps, terminal manifest and exact artifact hashes;
8. formal files `0444`, directories `0555`, regular files only, `nlink=1`;
9. no global GREEN and no V3.2 authorization before formal T7 review.

## 8. Pre-execution gates

After package approval, T4 must implement but may not create an official root
until all of the following pass:

- fresh first-mode odd/even Route-U three-node ladders reproduce a resolved
  high-precision deficit while the binary64 deficit is rejected as an
  acceptance operand;
- a predeclared highest-barrier set covering every frequency and both parities
  proves the adaptive precision rule and 30-digit margin;
- predeclared modes on both sides of the `1e-8` branch exercise the exact
  selector without reading S-route outcomes;
- synthetic `N_U=0`, `N_U=1` and `N_U=496` route maps rebuild exactly;
- negative tests reject float64 expansion, flux-derived Gamma_S, residual-based
  routing, missing/reordered precision nodes, route-map mutation, cache reuse
  and Route-A numerical imports;
- the original Route-A, Route-B, Route-C, inventory, threshold and certificate
  synthetic paths remain exact;
- low/high-frequency resource smokes measure the highest planned precision;
- projected central runtime, conservative planning upper bound, disk and
  checkpoint cadence are recorded for T0 before official launch;
- all source/protected/runtime identities and success/failure validators pass.

If a pre-execution gate fails, T4 stops without an official root and reports
the exact blocker.  It may not alter this algorithm or add precision post hoc.

## 9. Allowed implementation scope

After formal T7 package approval, T4 may add or modify only:

- `src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py`;
- `src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py`;
- `scripts/phase6_v3_1_hp_unitarity.py`;
- `tests/unit/test_phase6_v3_hp_unitarity.py`;
- `tests/regression/test_phase6_v3_hp_unitarity_publication.py`;
- a fresh official root after all pre-execution gates pass;
- T4 archive/current and `status.md` only after real state changes.

Existing cycle-2 V3-local modules and runners are read-only dependencies.
Frozen V3.0 contract/domain/threshold/convention files, V1/V2 authorities,
all old roots and all seven protected radial files are forbidden.

## 10. Review and non-claims

Formal T7 must review this exact package before T4 receives implementation or
numerical authority.  Package approval means only that V3.1-U is ready for
bounded T4 work.  Scientific acceptance still requires a fresh complete root
with all 496 modes, all 16 thresholds and all five certificates, followed by a
new formal T7 scientific review.

No V3.1 acceptance, V3.2, full-domain V3, Li-figure equivalence, finite-radius
observer claim, common absolute-phase closure or global GREEN is claimed here.
