# Phase 6 V2.1 mode-level asymptotic amplitudes

## Scope

This bounded slice constructs route-A gauge-invariant mode amplitudes for the
30 frozen SchWO radial keys, the two unit incident columns (`plus`, `cross`),
and `m=-2,+2`.  The canonical record order is radial-key ordinal, incident
column in the frozen order, then `m=(-2,+2)`, giving exactly 120 records and
60 records per incident column.  No radial solver is imported or called.

The implementation is split between the filesystem-free formula layer
`src/schwgw/scattering/gauge_invariant_asymptotics.py` and the immutable V1
loader/publisher in
`src/schwgw/validation/phase6_v2_mode_amplitudes.py`.  The command interface
is `scripts/phase6_publish_v2_1_mode_amplitudes.py`.

## Frozen coefficient reconstruction

The authoritative radial bytes are read only from
`runs/phase6/radial_validation/v1_radial_selected_acceptance_v1_20260810_py314`.
For every key, the stored baseline `A_out`, `S`, `log_abs_T_horizon`, and
`phase_T_horizon` are used.  The two unstored complex coefficients are
reconstructed only as

```text
A_in_raw = -A_out_raw/[(-1)^ell S_l]
T_horizon_raw = exp(log_abs_T_horizon) exp(i phase_T_horizon).
```

Both source fields, derived values, formulas, and the complex `S_l` closure
residual are retained per record.  The formula layer evaluates at 80 decimal
digits through the frozen project-local `mpmath 1.4.1` overlay, so the
`ell=360` horizon coefficients remain nonzero rather than underflowing in
binary64.

## Physical and master normalization

The implementation applies the V2.0 formulas literally:

```text
N_lm^p                   = c_lm^p/A_in_raw
A_out,total,physical     = c_lm^p A_out_raw/A_in_raw
A_out,free,physical      = -(-1)^ell c_lm^p
A_out,scattered,physical = c_lm^p[A_out_raw/A_in_raw+(-1)^ell]
T_horizon,physical       = c_lm^p T_horizon_raw/A_in_raw.
```

Even records identify `psi_Li_even=Psi_ZM`.  Odd records separately retain
the SchWO/Li master `psi_Li_odd`, the Martel--Poisson `Psi_RW`, and `Psi_CPM`,
with

```text
Psi_RW = psi_Li_odd
Psi_RW = (1/2) partial_t Psi_CPM
Psi_CPM = (2 i/omega) psi_Li_odd       [exp(-i omega t)].
```

Thus RW is never relabelled as CPM.  Raw and physical incoming, outgoing,
and horizon coefficients are recorded in Li, RW/ZM, and CPM normalization as
applicable, including magnitude and complex phase.

## Evidence policy

Every record independently evaluates

```text
A_out,total,physical
  - A_out,free,physical
  - A_out,scattered,physical
```

and stores the full complex residual.  No threshold is introduced for this
algebraic-definition check.  Numerical and convention uncertainty budgets
use exactly the V2.0 component vocabulary; deferred quantities remain
`PARTIAL` or `NOT_ASSESSED`.

This slice assesses no angle, angular or `m` sum, finite-radius observer
response, Li figure, physical flux, three-route comparison, or full-domain
V2 result.  Full-domain V1 independent scientific certification remains
`PARTIAL`, and global GREEN is not permitted.
