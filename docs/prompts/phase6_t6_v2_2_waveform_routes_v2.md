# Phase 6 T6 V2.2 v2 — threshold-bound three asymptotic waveform routes

You are the existing formal SchWO T6 task.  Execute only bounded V2.2 after
Root T0 dispatches this exact superseding prompt and only after formal T7 has
accepted the threshold contract.  Do not dispatch T7 or V2.3.

The earlier `docs/prompts/phase6_t6_v2_2_waveform_routes.md` is an immutable
historical HOLD predecessor and is forbidden for execution.  It is not edited
or reinterpreted.

## Dependency and immutable start gate

Require both exact formal T7 decisions:

```text
ADVANCE_DECISION: ADVANCE
GATE_LABEL: ACCEPT GREEN / V2.1 MODE-LEVEL ASYMPTOTIC AMPLITUDES READY FOR V2.2
```

and

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V2.2 WAVEFORM THRESHOLD CONTRACT READY FOR EXECUTION
```

Read the current project/status/T6 handoff, review-gate liveness protocol,
V2.0 contract/domain/material review, accepted V2.1 prompt/review/root/source,
the threshold rationale, this prompt and the V2.0 equation map.

Require these exact threshold-package identities at start and end:

```text
8c2ab9ca254df9c15e3947479bb0af3bb6204f37d326b52c16a0984604ae005e  configs/phase6_v2_2_waveform_threshold_contract_20260811.json
c96a0c640ffb2789c34e8e9ff364d42cc6cfe427b374a7cff1299d196b3c91b6  docs/phase6_v2_2_waveform_threshold_rationale_20260811.md
71918930e4b1384ab66adaf5e7d89bc55c31c30f156fa6f153332542759c611a  tests/unit/test_phase6_v2_2_threshold_contract.py
```

At start and end also require the convention contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
domain `9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
D_union plan `de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`
and protected radial hashes:

```text
9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9  radial_solver.py
91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2  conditioned_radial.py
d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df  scaled_tortoise_radial.py
3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896  adaptive_jost_radial.py
9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340  matching.py
fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f  physical_boundary_radial.py
b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22  boundary_conditions.py
```

Any mismatch is `HOLD / V2 FROZEN INPUT IDENTITY MISMATCH` with all liveness
protocol HOLD fields.  Do not repair, replace or recompute a frozen input.

## Exact three-route observable

For exactly the accepted 120 mode/channel/incident-column records, construct
the future-null-infinity scattered Martel--Poisson master coefficient

```text
H_sc = F_sector * c_lm * (-1)^ell * (1-S_l)
F_even = 1
F_odd  = 2 i / omega
C_record = abs(F_sector*c_lm)
```

without an observation angle or angular sum:

- Route A: accepted V2.1 SchWO Li masters mapped to MP ZM/CPM.
- Route B: the same SchWO radial/master input passed through an independently
  coded RW-gauge metric leading coefficient, direct asymptotic
  curvature/`Psi4` coefficient and frozen symmetric outgoing tetrad; a
  Kinnersley coefficient is allowed only with the exact factor two recorded.
  Route B may not copy Route A's final coefficient or call a finite-radius
  waveform/observer API.
- Route C: immutable external direct odd RW and independently solved even
  Zerilli amplitudes, with no SchWO radial numerical output.  Shared frozen
  analytic MP/Fourier/angular conventions must be recorded.

Use exactly the external root
`runs/phase6/radial_validation/v1_external_bhpt_direct_bounded_selected_v1_20260810_py314`
and verify its manifest
`e12c49b00efecc9c65d42699f2a5052ecac1fe2c988312ed21c4da085fe5ee6d`.
Do not call any radial solver.  If a route cannot be reconstructed uniquely
from frozen bytes, return `HOLD / V2.2 FROZEN ROUTE INPUT INSUFFICIENT` with
all protocol fields.

For each record store A/B/C complex amplitudes, fixed `C_record`, normalized
signal, A/B, A/C and B/C complex differences, all four comparator values,
absolute-phase state, exact threshold field/path/hash, pass/fail state,
pairwise shared-source provenance, and separate numerical/convention budgets.
No phase or complex rescaling is allowed.

Apply the contract fields literally:

```text
common_applicability.phase_and_relative_magnitude_signal_floor
route_pair_thresholds.A_B.*
route_pair_thresholds.A_C.*
route_pair_thresholds.B_C.*
acceptance_logic.*
separate_uncertainty_budget_policy.*
```

All 120 records and all three pairs are mandatory.  A failed signal-floor or
comparator is a scientific FAIL, not a missing/omitted record.  Absolute phase
must remain `PARTIAL` as frozen; that limitation does not erase independently
passing magnitude, phase-invariant and no-fit relative-phase evidence.

## Output and verification

Publish once to a fresh immutable
`runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v2_<timestamp>_py314`
root with canonical records, report, summary, source/provenance ledger and
manifest, then independently reload and reconstruct it.  Store
`radial_solve_count=0`, `global_status=null`, threshold identities, start/end
protected hashes and all selected-domain nonclaims.

Allowed changes are only new V2.2 asymptotic/validation modules and tests,
`scripts/phase6_v2_2*.py`, one V2.2 note, the fresh V2.2 root, `status.md`, T6
handoff and necessary archive.  Frozen V2.0/V2.1 files, the threshold package,
protected/numerics, background, potential/RWZ/reconstruction inputs, angular
or incident conventions, finite observer, legacy NP/pseudoinverse, V1 roots,
paper figures and all prompts are forbidden.

Route B must not use `static_orthonormal`, `li_literal_cartesian`, packaged-NP
pseudoinverse or finite-radius observer polarization.  Do not sum a total
plane wave at null infinity, perform an angular sum, rerun Li figures, or
modify a threshold after seeing results.

With exact CPython 3.14 and overlay first, run the threshold-contract test,
targeted route/publication tests, all Phase-6/V2 tests, full pytest, focused
Ruff format/check, compileall, `git diff --check`, process/collision checks,
immutable reload and start/end hashes.  Record preexisting out-of-scope lint
separately without modifying it.  Update status and T6 handoff with exact
counts and identities.

On terminal publication return only:

```text
CHECKPOINT / V2.2 THREE-ROUTE ASYMPTOTIC WAVEFORM EVIDENCE V2 FROZEN
```

Do not dispatch T7 or V2.3.
