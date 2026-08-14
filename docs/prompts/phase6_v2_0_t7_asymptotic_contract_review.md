# T7 executable prompt — Phase 6 V2.0 convention-contract review

## Role

Perform an independent, read-only review of the exact T6 V2.0 handoff.  Do
not edit files, run science, repair code, or accept a result from prose alone.

Read completely:

1. `AGENTS.md` and applicable parent instructions;
2. `docs/phase6_v1_to_v2_transition_gate_20260810.md`;
3. `configs/phase6_v2_0_convention_contract_20260810.json`;
4. `configs/phase6_v2_0_selected_domain_20260810.json`;
5. the V2.0 section of `docs/equation_map.md`;
6. `docs/phase6_v2_0_convention_freeze_20260810.md`;
7. the exact T6 handoff and every changed source/test file it names.

Require the frozen input hashes:

```text
convention contract 1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517
selected domain    9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818
```

## Independent review requirements

Without calling any radial or external solver:

1. Rehash all frozen inputs and T6 outputs and verify the claimed diff scope.
   Independently require exact start/end equality for the authoritative
   D_union plan and all seven `protected_radial_backend_identities`; do not
   infer this from git status in the pre-existing dirty worktree.
2. Independently reconstruct the source 30-key inventory and its odd/even,
   selected low/mid/high, low-ell absorption, operational turning/barrier,
   high-tail, and control categories.  Verify 15 exact odd/even pairs, two
   incident unit columns, and that the `m=-2,+2` lift gives exactly 60 unique
   channels per column and 120 structural records per route.  Confirm that
   observation angles and a complete angular sum remain deferred.
3. Derive the Li-to-Martel--Poisson even/odd map from the stated harmonic and
   Fourier assumptions.  In particular, check
   `Psi_RW=(1/2)partial_t Psi_CPM` and
   `Psi_CPM=(2i/omega)psi_Li_odd` under `exp(-i omega t)`.
4. Independently derive `A_L/A_R`, `A_lm^(plus/minus)`, and
   `c_lm^(plus/minus)` from the frozen `+z` unit-column convention.  Require
   physical scaling `c_lm/A_in_raw`.  Then derive the free/scattered split
   from `S_l=-A_out_raw/[(-1)^ell A_in_raw]`; verify that only
   `(-1)^ell c_lm(1-S_l)` enters the null-infinity mode.
5. Check the spin-weighted-harmonic, plus/cross, horizon odd-sign,
   polarization-rotation, explicit Riemann sign, normalized asymptotic null
   tetrad, the exact Kinnersley-to-symmetric Psi4 factor, and peak/RMS flux
   factors against the frozen project conventions and algebraic tests.  Check
   all Jost leading coefficients are fixed to one and cannot be
   complex-rescaled.
6. Verify that route independence is qualified, numerical and convention
   uncertainty remain separate per result, and no finite-radius observer frame
   or total plane-wave null-infinity sum is admitted.  A finite
   `areal_scale` precursor call must not count as the explicit infinity
   coefficients `H_plus/H_cross`.
7. Verify no radial-backend or evidence-root byte changed and no V2 science,
   Li figure, or external computation was run.

Do not run `tests/unit/test_phase6_asymptotic.py` wholesale because one test
calls the radial solver.  Tests are only supporting implementation evidence;
independently inspect
the equations, contract fields, and negative cases.  Any ambiguity in a sign,
factor of two, phase origin, boundary, amplitude meaning, or source identity
is a blocker.

## Decision vocabulary

If every V2.0 convention and scope requirement is exact, return

```text
ACCEPT GREEN / V2.0 CONVENTION CONTRACT READY FOR BOUNDED V2.1 IMPLEMENTATION
```

and also state

```text
V2 scientific validation remains NOT_ASSESSED by V2.0
full-domain V1 independent scientific certification remains PARTIAL
```

Otherwise return

```text
REVIEW YELLOW / V2.0 CONVENTION CONTRACT REQUIRES REPAIR
```

or, for an identity/scope/scientific violation,

```text
REVIEW RED / V2.0 START GATE VIOLATED
```

List exact blockers.  Do not authorize V2.1 in a YELLOW/RED review and do not
emit a global GREEN claim.
