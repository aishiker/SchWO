# Phase 6 T6 V2.2 — three asymptotic waveform routes

You are the existing formal SchWO T6 task.  Execute only bounded V2.2 after
Root T0 dispatches this exact frozen prompt.  Do not dispatch T7 or V2.3.

## Dependency and immutable start gate

Require an immutable V2.1 root and the exact formal T7 dual-axis decision:

```text
ADVANCE_DECISION: ADVANCE
GATE_LABEL: ACCEPT GREEN / V2.1 MODE-LEVEL ASYMPTOTIC AMPLITUDES READY FOR V2.2
```

`CLAIM_STATUS` may be `PASS` or an explicitly gate-allowed `PARTIAL`; it is
not itself an advance blocker.  Read `docs/review_gate_liveness_protocol.md`.

Read the current project/status/T6 handoff, the V2.0 contract/domain/material
review, V2.1 prompt/review/root/source/tests, this prompt, the V2.0 equation
map and applicable reference notes.  Rehash the accepted V2.1 identities.

At start and end require the convention contract
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

On any mismatch return `HOLD / V2 FROZEN INPUT IDENTITY MISMATCH` without
repair, replacement or recomputation.

## Three routes on one exact 120-record inventory

Compute the same mode-level future-null-infinity scattered radiation
amplitude, without an observation-angle or angular sum:

- Route A: accepted V2.1 SchWO Li masters mapped to MP ZM/CPM and the frozen
  mode-level complex radiative coefficient.
- Route B: SchWO RW-gauge metric reconstruction followed by a genuine
  large-`r` asymptotic curvature/`Psi4` limit in the frozen symmetric outgoing
  tetrad, or a Kinnersley result multiplied by exactly two with the route
  recorded.  This is an observable-route check sharing the SchWO radial input.
- Route C: immutable V1 external direct odd RW and independently solved even
  Zerilli amplitudes, with no SchWO radial numerical result.  It may share the
  frozen analytic MP/Fourier/angular convention and must say so.

Use the authoritative external root
`runs/phase6/radial_validation/v1_external_bhpt_direct_bounded_selected_v1_20260810_py314`
and cross-check its exact 30-key order and hashes.  Do not call a radial solver
for any route.  If a route cannot be constructed uniquely from frozen bytes,
return `HOLD / V2.2 FROZEN ROUTE INPUT INSUFFICIENT`.

For each of exactly 120 mode/channel/column records store A, B and C complex
amplitudes; A/B, A/C and B/C complex differences; relative magnitude;
wrapped relative phase; a phase-invariant comparator; absolute-phase state;
pairwise shared-source provenance; and separate numerical/convention budgets.
No per-mode phase fit or global complex rescaling is allowed.

Every acceptance threshold must already be explicitly frozen and identified
by path, hash and field before execution.  Radial-S thresholds may not be
silently repurposed as waveform thresholds.  If a mandatory route comparator
has no applicable frozen threshold, return exactly:

```text
HOLD / V2.2 FROZEN WAVEFORM THRESHOLD ABSENT
```

Every HOLD must include the protocol's exact reason, unblock condition, owner,
minimum next action and downstream-independence field.  Scientific `PARTIAL`,
wider-domain incompleteness or an unfinished future task is not HOLD.

Absolute phase may remain `PARTIAL` when honestly unsupported; do not force a
PASS or erase magnitude/relative-phase evidence that is independently valid.

## Output, scope and verification

Publish once to a fresh immutable
`runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v1_<timestamp>_py314`
root with canonical records, report, summary, source/provenance ledger and
manifest, then independently reload it.  Store `radial_solve_count=0`,
`global_status=null` and all selected-domain non-claims.

Allowed changes are only the V2 asymptotic/validation modules and tests,
`scripts/phase6_v2*.py`, a V2 note, the fresh V2.2 root, `status.md`, T6
handoff and necessary archive.  All frozen V2.0 files, protected/numerics,
background, potential/RWZ/reconstruction, angular/incident, finite observer,
legacy NP/pseudoinverse, thresholds, V1 roots, paper figures and other prompts
are forbidden.  Route B must not use `static_orthonormal`,
`li_literal_cartesian`, packaged-NP pseudoinverse or any finite-radius observer
polarization API.  Do not sum a total plane wave at null infinity.

With exact CPython 3.14 and the overlay first, run targeted route tests, all
Phase-6/V2 tests, full pytest, Ruff format/check, compileall,
`git diff --check`, process/collision checks, immutable reload, and start/end
hashes.  Update status and T6 handoff with exact counts and identities.

On success return only:

```text
CHECKPOINT / V2.2 THREE-ROUTE ASYMPTOTIC WAVEFORM EVIDENCE FROZEN
```
