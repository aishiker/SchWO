# Phase 6 T6 V2.4 — selected-domain release package

You are the existing formal SchWO T6 task.  Build only the bounded V2.4
release package after Root T0 dispatch.  Add no physics and dispatch no T7.

## Dependency and identity gate

Require immutable accepted V2.1, V2.2 and V2.3 roots and exactly:

```text
ADVANCE_DECISION: ADVANCE
GATE_LABEL: ACCEPT GREEN / V2.3 SELECTED-DOMAIN WAVEFORM AND FLUX CLOSURE READY FOR V2.4
```

An evidence-correct `CLAIM_STATUS: PARTIAL` is compatible with advance.  Read
`docs/review_gate_liveness_protocol.md`.

Read project/status/T6 handoff, V2.0 authorities/material review, all three
accepted roots and T7 decisions, their prompts/source/tests/manifests, this
prompt and existing Phase-6 release patterns.  Rehash every predecessor.

At start/end require contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
domain `9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
plan `de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`
and these protected identities:

```text
9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9  radial_solver.py
91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2  conditioned_radial.py
d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df  scaled_tortoise_radial.py
3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896  adaptive_jost_radial.py
9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340  matching.py
fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f  physical_boundary_radial.py
b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22  boundary_conditions.py
```

Any drift is `HOLD / V2 FROZEN INPUT IDENTITY MISMATCH`.

Any HOLD must include exact reason, unblock condition, owner, minimum next
action and downstream-independence status.  Scientific `PARTIAL`,
`full_domain=PARTIAL` or a future task is not HOLD.

## Release-only task

Do not recompute radial solutions, waveform routes or fluxes and do not add or
change a formula, convention, parameter, threshold or domain.  Build a strict
selected-domain package with at least these separate certificates:

```text
V2_MODE_AMPLITUDE_NORMALIZATION
V2_TOTAL_FREE_SCATTERED_DECOMPOSITION
V2_MASTER_ROUTE_WAVEFORM
V2_CURVATURE_ROUTE_WAVEFORM
V2_EXTERNAL_ROUTE_WAVEFORM
V2_ROUTE_CROSSCHECK
V2_INFINITY_FLUX
V2_HORIZON_FLUX
V2_RADIAL_FLUX_BALANCE
V2_WAVEFORM_CURRENT_FLUX_EQUIVALENCE
V2_ABSOLUTE_PHASE_CONVENTION
V2_SELECTED_DOMAIN_RELEASE_POLICY
```

Each certificate must have the observable, exact parameter/channel domain,
one of `PASS/PARTIAL/FAIL/NOT_ASSESSED`, separate numerical and convention
budgets, evidence roots and hashes, independence boundary, non-claims, all
protected hashes and both V2.0 authority hashes.  Derive state fail-closed
from native accepted evidence; a publisher may never upgrade a source.

The release must set `global_status=null`.  It must not say V2 globally GREEN,
SchWO fully validated, full-domain V2 certified, a complete angular waveform,
finite-radius observer response, or Li-figure equivalence.  It must not
extrapolate 30 radial keys to 17,818 keys.  Absolute phase is `PASS` or
`PARTIAL` only according to the actual accepted evidence; full-domain V2 is
`NOT_ASSESSED` or `PARTIAL`.

Publish once to fresh immutable
`runs/phase6/asymptotic_waveform/v2_selected_release_v1_<timestamp>_py314`
with release ledger, canonical submission/source map as needed, report,
machine summary and manifest.  Write
`docs/phase6_v2_selected_domain_closeout.md`.  Independently reload every
source and release byte.

## Scope and verification

Allowed changes are release/validation logic under
`src/schwgw/validation/phase6_v2*.py`, `scripts/phase6_v2*.py`, matching V2
tests, a new V2 output/release config under `configs/phase6/`, the fresh
release root, closeout doc, status and T6 handoff/archive.  Scientific V2
formula modules should not change in V2.4.

All frozen V2.0 files, protected/numerics, background/potentials/RWZ/
reconstruction, angular/incident, finite observer, legacy NP/pseudoinverse,
thresholds, V1 roots, V2.1--V2.3 roots, paper outputs, Li code and other
prompts are forbidden.  No solver, new measurement, angle scan, angular sum,
figure or V3 work.

Use exact CPython 3.14 overlay-first.  Run targeted release tests, all
Phase-6/V2 tests, full pytest, Ruff format/check, compileall,
`git diff --check`, process/collision checks, immutable full reload and
start/end hashes.  Update status/T6 handoff with exact identities and counts.

On verified success return only:

```text
CHECKPOINT / V2 SELECTED-DOMAIN RELEASE FROZEN
```
