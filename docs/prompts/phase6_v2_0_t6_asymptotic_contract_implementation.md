# T6 executable prompt — Phase 6 V2.0 convention-contract implementation

## Start gate

Read completely before acting:

1. `AGENTS.md` and any applicable parent instructions;
2. `docs/phase6_v1_to_v2_transition_gate_20260810.md`;
3. `configs/phase6_v2_0_convention_contract_20260810.json`;
4. `configs/phase6_v2_0_selected_domain_20260810.json`;
5. the V2.0 section of `docs/equation_map.md`;
6. `docs/phase6_v2_0_convention_freeze_20260810.md`;
7. `src/schwgw/validation/phase6_asymptotic.py` and its focused tests.

Before editing, rehash both configuration files and require

```text
convention contract 1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517
selected domain    9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818
```

Stop fail-closed if either identity differs or if the repaired V1 transition
decision is not exactly

```text
ACCEPT GREEN / V1 RADIAL REPAIR SUFFICIENT FOR BOUNDED V2 ENTRY
```

with the non-claim that full-domain V1 independent scientific certification
remains PARTIAL.

Before editing, also rehash the authoritative D_union plan and every entry in
`protected_radial_backend_identities`.  Require exact equality.  Repeat the
same checks immediately before handoff.  A pre-existing dirty git worktree is
not evidence that a protected byte is unchanged; the contract hashes are the
start/end gate.

## Task

Implement only the typed, zero-science V2.0 convention boundary and algebraic
validation needed for a future bounded V2.1 run.  Prefer a small new module
under `src/schwgw/validation/` and focused unit tests.  The implementation
must load/validate the frozen contract and selected-domain records and expose
explicit typed operations for:

- Li even/odd to Zerilli--Moncrief/RW/CPM conversion;
- the RW-to-CPM frequency-domain factor under `exp(-i omega t)`;
- the `+z` incident phase, Cartesian unit plus/cross columns, helicity map,
  exact `c_lm^(plus/minus)` phases, and `c_lm/A_in_raw` physical scaling;
- the frozen tortoise constant, retarded/advanced time, Jost/Fourier phase,
  and exact unit leading coefficients of all three Jost factors;
- raw versus physical total, free, scattered-outgoing, and horizon
  coefficient separation;
- the frozen spin-weighted harmonic, plus/cross, explicit Riemann-sign and
  normalized no-boost/no-spin null-tetrad conventions, including the exact
  factor-two conversion from an asymptotic Kinnersley Psi4;
- real-field peak versus complex-RMS flux normalization;
- pairwise role-qualified A/B/C provenance and mandatory separate
  numerical/convention uncertainty ledgers;
- exact loading of 15 odd/even pairs, 30 radial keys, two unit input columns,
  and their 60-channel-per-column/120-record structural lift;
- canonical `future_event_horizon` publication with the explicit
  `event_horizon` precursor-API alias.

Add fail-closed algebraic tests for wrong Fourier sign, odd factor/sign,
tortoise offset, total-versus-scattered coefficient, harmonic convention,
Kinnersley boost factor, flux factor of two, duplicate/missing domain keys,
and unqualified route
independence.  Explicitly test that a finite-radius observer frame and a total
plane-wave null-infinity sum are rejected.  A V2 infinity record must expose
`H_plus/H_cross=lim_(r->infinity) r h_plus/cross`; reject any attempt to label
a finite `areal_scale` precursor call as that limit.  Also reject an
observation-angle or summed-transfer claim because the V2.0 angular domain is
explicitly deferred.

## Hard prohibitions

- Do not modify `radial_solver.py`, `conditioned_radial.py`,
  `scaled_tortoise_radial.py`, `adaptive_jost_radial.py`, any Jost recurrence,
  or any V1 evidence root.
- Do not call a radial solver, BHPT/Wolfram kernel, arbitrary-precision
  integrator, paper-figure runner, renderer, or external network service.
- Do not use finite-radius observer frames.
- Do not sum a total plane wave at null infinity.
- Do not fit or tune any amplitude, phase, sign, tortoise constant, or
  normalization.
- Do not publish V2 science evidence or claim V2 PASS/global GREEN.
- Do not silently reuse the 2026-08-08 selected V2 witness as V2.0 acceptance.

The existing `tests/unit/test_phase6_asymptotic.py` contains a real radial
solve in its metric-roundtrip test.  Do not run that file wholesale.  Run only
new pure-algebraic tests and explicitly selected existing node IDs that have
been inspected and shown not to call a radial or external solver.

## Required handoff

Report exact changed-file hashes, the exact pure-algebraic test node IDs and
results, and a field-by-field comparison against the frozen contract.  State explicitly
that `science_executed=false`, the radial backend was untouched, and no
finite-radius or total-plane-wave waveform was produced.  Stop for T7
read-only review; do not proceed to V2.1.
