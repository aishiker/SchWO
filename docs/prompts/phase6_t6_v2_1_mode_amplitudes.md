# Phase 6 T6 V2.1 — mode-level asymptotic amplitudes

You are the existing formal SchWO T6 task.  Execute only this bounded V2.1
slice in the shared repository.  Use `gpt-5.6-sol` with `high` reasoning.
Do not dispatch T7 or V2.2; return the terminal decision to Root T0.

## 1. Authorized start gate

Read, in order, `project.md`, the top current sections of `status.md`,
`docs/handoffs/T6_current.md`,
`docs/phase6_v2_0_material_reviews_20260810.md`,
`docs/review_gate_liveness_protocol.md`, this prompt,
`configs/phase6_v2_0_convention_contract_20260810.json`,
`configs/phase6_v2_0_selected_domain_20260810.json`, the frozen V2.0 section
of `docs/equation_map.md`, the applicable sections of `docs/physics_spec.md`,
and every V1 root listed by the convention contract.

The predecessor decision must be exactly:

```text
ACCEPT GREEN / V2.0 CONVENTION CONTRACT READY FOR BOUNDED V2.1 IMPLEMENTATION
```

At both start and end, independently rehash these immutable inputs:

```text
configs/phase6_v2_0_convention_contract_20260810.json
  1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517
configs/phase6_v2_0_selected_domain_20260810.json
  9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818
runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314/plan.json
  de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3
src/schwgw/numerics/radial_solver.py
  9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
src/schwgw/numerics/conditioned_radial.py
  91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
src/schwgw/numerics/scaled_tortoise_radial.py
  d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
src/schwgw/numerics/adaptive_jost_radial.py
  3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
src/schwgw/numerics/matching.py
  9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
src/schwgw/numerics/physical_boundary_radial.py
  fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
src/schwgw/numerics/boundary_conditions.py
  b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
```

The selected domain must rebuild exactly as 15 odd/even pairs, 30 radial
keys, 60 `(radial key,m)` channels per unit incident column, and 120 total
route-mode-column records.  If any identity, root, permission, cardinality or
ordering differs, stop without repair or replacement and return exactly:

```text
HOLD / V2 FROZEN INPUT IDENTITY MISMATCH
```

## 2. Implementation scope

Implement a typed, pure-function mode-amplitude layer, concentrating all new
V2 formulas in a small module such as
`src/schwgw/scattering/gauge_invariant_asymptotics.py`, with evidence and
publication logic under `src/schwgw/validation/phase6_v2*.py` and
`scripts/phase6_v2*.py`.

Consume only immutable V1 evidence.  The authoritative SchWO selected source
is
`runs/phase6/radial_validation/v1_radial_selected_acceptance_v1_20260810_py314`.
For every baseline key, load the frozen incoming, total-outgoing and horizon
information.  If `A_in_raw` is not stored directly, it may be reconstructed
only by the frozen identity
`A_in_raw=-A_out_raw/[(-1)^ell S_l]`; record both source fields, the derived
value and its complex closure residual.  Likewise a complex horizon
coefficient may be reconstructed only from the stored `log_abs_T_horizon`
and `phase_T_horizon`, with the exact formula recorded.  Do not assume a unit
coefficient without proving it from the stored bytes.  If these frozen bytes
do not uniquely determine every required coefficient, stop exactly with:

```text
HOLD / V2.1 FROZEN RADIAL INPUT INSUFFICIENT
```

Every HOLD must also state `exact_reason`, `unblock_condition`, `owner`,
`minimum_next_action`, and whether independent downstream work may proceed.
Scientific `PARTIAL`, wider-domain incompleteness or future work is not HOLD.

For the two incident columns `(A_plus,A_cross)=(1,0),(0,1)` and both
`m=-2,+2`, apply only the V2.0 formulas:

```text
N_lm^p                         = c_lm^p/A_in_raw
Psi_ZM                         = psi_Li_even
Psi_CPM                        = (2 i/omega) psi_Li_odd
A_out,total,physical           = c_lm^p A_out_raw/A_in_raw
A_out,free,physical            = -(-1)^ell c_lm^p
A_out,scattered,physical       = c_lm^p[A_out_raw/A_in_raw+(-1)^ell]
T_horizon,physical             = c_lm^p T_horizon_raw/A_in_raw
```

The odd record must separately identify the SchWO/Li master, the
Martel--Poisson RW function, the CPM function and
`Psi_RW=(1/2) partial_t Psi_CPM` under `exp(-i omega t)`.  Never relabel RW as
CPM.

Each of exactly 120 records must include the radial key and ordinal, sector,
`ell`, `m`, incident column, raw and physical coefficients, total/free/
scattered/horizon amplitudes in Li and MP normalization, complex phase,
formula identities, source paths and SHA-256 identities, and separate
numerical and convention uncertainty budgets using the component vocabulary
of the V2.0 contract.  Missing components remain `NOT_ASSESSED` or `PARTIAL`,
never zero-filled.

Construct and independently evaluate the complex identity

```text
A_out,total,physical
  = A_out,free,physical + A_out,scattered,physical
```

for every record.  Store the complex residual, not only magnitudes.  This is
an algebraic-definition check; do not invent or change a numerical threshold.

## 3. Artifact and claims

Publish once to a fresh no-overwrite root matching
`runs/phase6/asymptotic_waveform/v2_1_mode_amplitudes_v1_<timestamp>_py314`.
Use an exclusive writer, canonical machine-readable records, report, summary,
source ledger and manifest.  Seal files read-only and the root immutable, then
perform a full independent reload.  The summary must state
`radial_solve_count=0`, `global_status=null`, `global_green_permitted=false`,
and that angles, an angular sum, finite-radius observer responses, Li figures
and full-domain V2 are not assessed.

No scientific result outside the frozen 120-record structural domain may be
accepted.  V1 full-domain independent scientific certification remains
`PARTIAL`.

## 4. Allowed and forbidden changes

Allowed: new V2 modules under `src/schwgw/scattering/`,
`src/schwgw/validation/phase6_v2*.py`, `scripts/phase6_v2*.py`, matching
`tests/unit|physics|regression/test_phase6_v2*.py`, a V2 implementation note,
the fresh V2.1 root, `status.md`, `docs/handoffs/T6_current.md`, and a necessary
T6 archive handoff.

Forbidden: both frozen V2.0 JSON files; all `src/schwgw/numerics/**`,
`backgrounds/**`, `perturbations/potentials.py`, `perturbations/rwz.py`,
`perturbations/reconstruction.py`, `angular/**`, `waves/incident.py`, finite
observer/tetrad production modules, legacy NP/pseudoinverse modules,
`docs/physics_spec.md`, the frozen V2.0 mapping in `docs/equation_map.md`, all
V1 artifacts, thresholds, Phase-4/5 outputs, Li plotting code, and every other
prompt in this chain.  Do not call any radial solver, add an observation
angle, perform an `m`/angular sum, sum a total plane wave at null infinity, or
run a paper figure.

## 5. Required verification and terminal response

Use exact CPython 3.14 with the project overlay first and
`PYTHONDONTWRITEBYTECODE=1`.  Run targeted V2.1 tests, all Phase-6/V2 tests,
the complete pytest suite, Ruff format/check, compileall, `git diff --check`,
process checks, fresh-root collision checks, immutable reload, and start/end
input hashes.  Preserve exact pass/fail/skip counts and commands in the report
and T6 handoff.  Confirm no residual numerical process.

On verified success, return only:

```text
CHECKPOINT / V2.1 MODE-LEVEL ASYMPTOTIC AMPLITUDES FROZEN
```

Do not start or message T7 yourself.
