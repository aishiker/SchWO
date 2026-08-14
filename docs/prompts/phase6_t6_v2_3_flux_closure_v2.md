# Phase 6 T6 V2.3 v2 — threshold-bound selected infinity/horizon flux closure

You are the existing formal SchWO T6 task.  Execute bounded V2.3 only after
Root T0 dispatch.  Do not dispatch T7 or V2.4.

## Accepted dependencies and frozen gate

Require the authoritative V2.2-v3 verdict exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PARTIAL
GATE_LABEL: ACCEPT GREEN / V2.2 SELECTED-DOMAIN WAVEFORM ROUTES READY FOR V2.3
```

Require the V2.3 pre-execution threshold verdict exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V2.3 FLUX THRESHOLD CONTRACT READY FOR BOUNDED EXECUTION
```

Read `project.md`, `status.md`, current T0/T6/T7 handoffs, the review-gate
liveness protocol, frozen V2.0 convention/domain authorities, accepted V2.1,
authoritative V2.2-v3, V1 selected radial acceptance, external bounded direct
RW/Zerilli evidence, and the complete V2.3 threshold package and T7 review.

The execution threshold package is exactly:

```text
6cc64b32534c0211da90a7fbec7fb783b91a3b852cfda2991640a37e9de88808  configs/phase6_v2_3_flux_threshold_contract_20260811.json
ce0da14d565bd1db9a63d848f8c7f68078c144899da7911861ad590494586ee8  docs/phase6_v2_3_flux_threshold_rationale_20260811.md
ba85493073d653de1ee5847f05668e0eaeb418a3697827df2c2e2b2afe2ea5e4  tests/unit/test_phase6_v2_3_threshold_contract.py
128803a461cb82717580959f85d84c55d91278e752b9025391e2336b08ecbafc  docs/prompts/phase6_t7_v2_3_threshold_contract_review.md
```

The accepted V2.2-v3 root is
`runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v3_20260811T113135_py314`
with:

```text
3981aeb5424cbac4e7774fc84b5f03d5764561ea21a7338a60f19bf5f0d46660  manifest.json
2f7b466036d1481766794aa13581dd9824c851a7e405117f94e192d849f526c9  records.jsonl
fc66bb1a66f10257b80827ee292d180b0582587c3291332471971731dc352f9b  report.json
9fdbd6302fdc0eea93cc1ced1db76f2355343b3538dfee35f5145ac8e5b518a1  source_ledger.json
fdd314e760c4fa71c555f9eadb13eeb8389d0b24c0f6e8822eb1005afc9b8b19  summary.json
```

At start and end require V2.0 contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
domain
`9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
D_union plan
`de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`,
every source identity in the V2.3 contract, and:

```text
9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9  src/schwgw/numerics/radial_solver.py
91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2  src/schwgw/numerics/conditioned_radial.py
d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df  src/schwgw/numerics/scaled_tortoise_radial.py
3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896  src/schwgw/numerics/adaptive_jost_radial.py
9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340  src/schwgw/numerics/matching.py
fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f  src/schwgw/numerics/physical_boundary_radial.py
b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22  src/schwgw/numerics/boundary_conditions.py
```

Any mismatch is a protocol-complete
`HOLD / V2 FROZEN INPUT IDENTITY MISMATCH`.

## Exact implementation task

Implement a narrow V2.3 arbitrary-precision validation/publisher slice.  It
must consume only immutable predecessor bytes and must never import, call or
mock a radial solve.  Validate the accepted V2.1 and V2.2 roots through their
native reloaders before constructing records.

For every exact selected `(radial key, m, incident column)` item, produce one
record: 30 keys x two `m` values x two columns = exactly 120 unique records.
Use at least 80 decimal digits for all mandatory flux arithmetic; 100 digits is
preferred.  Decimal strings from original external wp60 nodes must be parsed
inside the explicit precision context.  Restore ambient precision on exit.

For both SchWO and the independent external direct witness, reconstruct:

```text
J_in  = -omega |A_in_MP|^2
J_out = +omega |A_out_total_MP|^2
J_h   = -omega |T_horizon_MP|^2

F = sigma_l * omega * |J| / (128*pi)
  = sigma_l * omega^2 * |Psi_MP|^2 / (128*pi)
```

Carry explicitly the real-field-peak time-average `1/2`,
`sigma_l=(ell+2)!/(ell-2)!`, `N_lm^p=c_lm^p/A_in_raw`, and in the odd sector
`Psi_CPM=(2i/omega)Psi_RW`.  The external odd witness is direct Regge--Wheeler;
the external even witness is independently solved Zerilli.  Use the same
frozen physical incident normalization for SchWO and external coefficients;
never compare unqualified raw-master energy fluxes.

For Route A and Route B, reconstruct total outgoing MP coefficients as the
frozen free coefficient plus each route's accepted scattered coefficient.
Do not use a scattered-only square in the balance.  Save free/scattered
squares only as explicitly nonadditive interference diagnostics.

Each record must include at least:

- exact domain key, `m`, incident column, sector, `omega`, `sigma_l` and
  arbitrary-precision context;
- all physical normalization/MP bridge factors and original source identities;
- SchWO and external signed incoming, total-outgoing and horizon currents;
- positive current-derived and amplitude-derived incoming, total-outgoing and
  horizon energy fluxes;
- Route-A and Route-B total-outgoing infinity fluxes;
- normalized SchWO and external balance residuals;
- all mandatory waveform/current, A/B, SchWO/external outgoing and
  SchWO/external horizon comparators;
- threshold references by contract path, SHA-256 and exact field;
- positivity, current-sign, inventory, normalization-factor, finite-value,
  total-outgoing and no-fit predicates;
- distinct numerical and convention uncertainty budgets, with missing items
  represented as `PARTIAL` or `NOT_ASSESSED`, never zero;
- `radial_solve_count=0`, selected-domain claim ceiling and all nonclaims.

Every one of the six frozen numeric bounds and every exact predicate in the
contract is mandatory and fail-closed.  There is no signal floor or omission
policy.  In particular, retain the approximately `9.37e-1498` high-ell horizon
fraction.  Never cast a mandatory horizon current, flux, fraction or residual
to binary64.

If frozen bytes do not contain enough information, return a protocol-complete
`HOLD / V2.3 FROZEN FLUX INPUT INSUFFICIENT`.  If any coherent factor mismatch
of `2`, `4`, `omega`, `omega^2`, `sigma_l` or an odd MP bridge appears, return
`HOLD / V2.3 NORMALIZATION FACTOR MISMATCH`; do not retune a factor or
threshold.  Scientific PARTIAL or wider-domain incompleteness alone is not
HOLD.

## Evidence and validation

Provide a check-only path, a publish-once path and a strict independent reload
path.  The reload must rebuild all 120 records from original immutable V2.1,
V2.2 and external wp60 source bytes rather than trusting the published report.

After check-only passes, publish exactly once to a fresh immutable root named

```text
runs/phase6/asymptotic_waveform/v2_3_flux_closure_v1_<timestamp>_py314
```

with canonical `records.jsonl`, `source_ledger.json`, `summary.json`,
`report.json` and `manifest.json`.  Use exclusive creation, single-writer
locking, fsync, direct regular files, file mode `0444`, root mode `0555`, no
symlink/hardlink/staging residue, and an exact manifest.  Independently reload
after sealing.  Store `global_status=null`, `global_green_permitted=false`,
`full_domain_v2=NOT_ASSESSED`, `absolute_phase=PARTIAL`, and the exact accepted
V2.3 threshold-review verdict and its T7 handoff identity at build time.

Add focused unit and publication tests that include fail-closed tamper,
binary64-underflow/record-omission, scattered-only-balance and ambient-mpmath
precision-restoration cases.  With exact project CPython 3.14 overlay-first,
run:

1. focused V2.3 and adjacent V2.2/V2.1 tests;
2. all `tests/unit/test_phase6*.py` and V2 regression tests;
3. full `pytest`;
4. Ruff format/check on owned Python files, compileall, scoped and repository
   `git diff --check`;
5. pre/post process, collision, immutable permission, manifest and protected
   identity checks.

Allowed changes are one narrow V2.3 validation module, one CLI publisher,
focused V2.3 tests, one V2.3 evidence document, a fresh V2.3 root, `status.md`
and T6 handoff/archive.  Do not modify the threshold package, either V2.3 T7
prompt, T7 handoff, frozen V2.0 files, V2.1/V2.2/V1/external artifacts,
protected radial/numerical code, backgrounds, potentials/RWZ/reconstruction,
finite observer/tetrad code, angular/incident code, legacy NP/pseudoinverse,
paper outputs, Li code or V2.4 files.  Do not run radial solves, angle scans,
angular sums, full paper figures or Li figures.

On verified success return only:

```text
CHECKPOINT / V2.3 SELECTED-DOMAIN FLUX CLOSURE EVIDENCE V2 FROZEN
```
