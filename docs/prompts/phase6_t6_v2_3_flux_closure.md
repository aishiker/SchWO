# Phase 6 T6 V2.3 — selected infinity/horizon flux closure

You are the existing formal SchWO T6 task.  Execute mode-level V2.3 only after
Root T0 dispatch.  Do not dispatch T7 or V2.4.

## Dependency and frozen gate

Require an accepted immutable V2.2 root and exactly:

```text
ADVANCE_DECISION: ADVANCE
GATE_LABEL: ACCEPT GREEN / V2.2 SELECTED-DOMAIN WAVEFORM ROUTES READY FOR V2.3
```

An evidence-correct `CLAIM_STATUS: PARTIAL`, including partial absolute phase,
is compatible with this dependency.  Read the review-gate liveness protocol.

Read current project/status/T6 handoff; frozen V2.0 contract/domain/equation
map/material review; accepted V2.1 and V2.2 roots/reviews; this prompt; and
the original V1 current/flux evidence.  Rehash all accepted predecessors.

At start and end require contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
domain `9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
plan `de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`
and:

```text
9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9  radial_solver.py
91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2  conditioned_radial.py
d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df  scaled_tortoise_radial.py
3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896  adaptive_jost_radial.py
9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340  matching.py
fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f  physical_boundary_radial.py
b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22  boundary_conditions.py
```

Any mismatch is `HOLD / V2 FROZEN INPUT IDENTITY MISMATCH`.

## Exact flux task

For each exact selected mode/channel, compare:

1. the frozen V1 signed conserved radial current/Wronskian witness;
2. future-null-infinity MP gauge-invariant waveform energy flux;
3. future-horizon ingoing MP absorption flux;
4. an external-direct odd-RW/even-Zerilli flux witness.

Use the real-field-peak convention, time-average factor `1/2`, and frozen
`omega^2 sigma_l/(128 pi)` MP normalization.  Carry the incident
`c_lm/A_in_raw` normalization and the odd RW-to-CPM `2i/omega` factor
explicitly.  Do not compare raw scalar Wronskians to GW flux without the
contract conversion.

The balance gate is the total scattering mode:

```text
F_infinity_in = F_infinity_out_total + F_horizon
```

Never substitute scattered-only outgoing flux in that equation.  Free and
scattered fluxes may be saved only as qualified diagnostics because their
interference does not make them independent positive balance terms.

Each record must store signed radial current; positive physical incoming,
total-outgoing and horizon fluxes; normalization factors; sector/key/channel;
Route-A and Route-B infinity flux; horizon flux; radial-balance,
waveform-vs-current and external-vs-SchWO residuals; positivity,
dimension/scaling and sign checks; source identities; and separate numerical
and convention uncertainty budgets.

Do not call a radial solver.  If frozen evidence does not contain enough
signed-current/amplitude information, return
`HOLD / V2.3 FROZEN FLUX INPUT INSUFFICIENT`.  Every acceptance threshold
must be pre-frozen and identified; otherwise return
`HOLD / V2.3 FROZEN FLUX THRESHOLD ABSENT`.  On a coherent factor discrepancy
of `2`, `4`, `omega`, `omega^2` or a factorial, fail closed with
`HOLD / V2.3 NORMALIZATION FACTOR MISMATCH`; never retune normalization.

Every HOLD must include exact reason, unblock condition, owner, minimum next
action and whether independent downstream work may proceed.  Scientific
`PARTIAL`, wider-domain incompleteness or future work is not HOLD.

## Artifact, scope and checks

Publish once to fresh immutable
`runs/phase6/asymptotic_waveform/v2_3_flux_closure_v1_<timestamp>_py314`
with records, report, summary, source ledger and manifest; independently
reload.  Store `radial_solve_count=0`, `global_status=null`, exact domain and
non-claims.  This is mode-level flux only, not an angular waveform plot.

Allowed changes: V2 asymptotic/validation modules and V2 tests/scripts/docs,
fresh V2.3 root, status, T6 handoff/archive.  Forbidden: frozen V2.0 files,
protected/numerics, backgrounds, potentials/RWZ/reconstruction,
angular/incident, finite observer/tetrad, legacy NP/pseudoinverse, thresholds,
V1 artifacts, paper outputs, Li code and other prompts.  No radial solve,
angle scan, full sum or paper figure.

With exact CPython 3.14 overlay-first, run targeted flux tests, all
Phase-6/V2 tests, full pytest, Ruff format/check, compileall,
`git diff --check`, process/collision checks, immutable reload and start/end
hashes.  Update status/T6 handoff with exact results.

On verified success return only:

```text
CHECKPOINT / V2.3 SELECTED-DOMAIN FLUX CLOSURE EVIDENCE FROZEN
```
