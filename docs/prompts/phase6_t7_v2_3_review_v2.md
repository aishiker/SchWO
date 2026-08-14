# Phase 6 T7 V2.3 v2 — independent selected-domain flux-closure review

You are the existing formal SchWO T7 task.  Perform the initial independent
science review of the terminal V2.3-v2 authority, read-only.  Do not edit
implementation/science/artifact/threshold/prompt bytes, dispatch V2.4, call a
radial solver or expand the domain.

## Terminal candidate and dependencies

Require both T6 checkpoints exactly:

```text
CHECKPOINT / V2.3 SELECTED-DOMAIN FLUX CLOSURE EVIDENCE V2 FROZEN
CHECKPOINT / V2.3 SUMMARY PRECISION-PROVENANCE REPAIR V2 FROZEN
```

The only current candidate authority is:

```text
runs/phase6/asymptotic_waveform/v2_3_flux_closure_v2_20260811T050013_py314
```

with exact identities:

```text
a0fc62a4e8fc47176832d8b749285e7f0be9cad46e69911900230f591028694b  manifest.json
ba8617224c89c7122e27d0399dafc510d126dd2b4cfd0ca2d8f741ae2a454d39  records.jsonl
3d8fa27847887f4cb9605f18b1241f948a87362f6a2f3f4e056d678061cd6166  report.json
2c91e4b4f1567b5911e3fda2611b64d303e8dba16484be9d450403225677ac2a  source_ledger.json
336379cf0e20e14af898f4e4dee04523fb851d4c70c23efedfed3d49d935c29f  summary.json
```

The predecessor
`runs/phase6/asymptotic_waveform/v2_3_flux_closure_v1_20260811T044845_py314`
is immutable superseded evidence and forbidden as current authority.  Its
`records.jsonl` must remain byte-identical to v2 at
`ba8617224c89c7122e27d0399dafc510d126dd2b4cfd0ca2d8f741ae2a454d39`;
its other bytes must remain unchanged.

Read `project.md`, `status.md`, current T0/T6/T7 handoffs, review-gate
liveness protocol and verdict template; V2.0 authorities; accepted V2.1;
authoritative V2.2-v3 and its T7 verdict; the accepted V2.3 threshold package
and pre-execution T7 verdict; both V2.3 T6 prompts; current source, tests and
evidence doc; every v2 artifact byte; original V1 comparison records and
external wp60 nodes.  Do not trust T6/T0 summaries as proof.

At start and end require:

```text
6cc64b32534c0211da90a7fbec7fb783b91a3b852cfda2991640a37e9de88808  configs/phase6_v2_3_flux_threshold_contract_20260811.json
ce0da14d565bd1db9a63d848f8c7f68078c144899da7911861ad590494586ee8  docs/phase6_v2_3_flux_threshold_rationale_20260811.md
ba85493073d653de1ee5847f05668e0eaeb418a3697827df2c2e2b2afe2ea5e4  tests/unit/test_phase6_v2_3_threshold_contract.py
25f2f42febaaec9c6eb8ebe621ff1d095648c5aca4f0154c4b3c8b9acd959ba0  docs/prompts/phase6_t6_v2_3_flux_closure_v2.md
531cc709a766693d925adb9ff82163648b155adf538540872563d63abdde23c9  docs/prompts/phase6_t6_v2_3_summary_precision_repair_v2.md
dd14b7910890ff752c34e9fae55147a2ad08e33777b07a13919737342f1eaa8a  src/schwgw/validation/phase6_v2_flux_closure.py
f42241e1e49f2a10b8192a0d8071813580ca66f4803058ceed7ab8d43fbe1406  scripts/phase6_v2_3_publish_flux_closure.py
170a9d4391294e5c3c3f4e0f8f3a1045f0277553cd0ea6a1d6fe6b31f653c213  tests/unit/test_phase6_v2_3_flux_closure.py
c8bb426d6a4281029744ac27c424042902af8c2f7379c0da3faadf14b49a93c8  tests/regression/test_phase6_v2_3_flux_publication.py
aa483b8309d56cbfc96c163f00c87f75b19d2bfe019a4cea9f42270cb6a1b670  docs/phase6_v2_3_flux_closure_20260811.md
```

Also rehash V2.0 contract
`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`,
domain
`9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`,
D_union plan
`de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`,
every contract-listed source, accepted V2.1/V2.2-v3 artifact, original V1 and
external source, and the seven protected radial files frozen in the execution
prompt.  Identity drift is a protocol-complete HOLD.

## Independent scientific reconstruction

Start a fresh CPython 3.14/mpmath process with ambient `mp.dps=15`.  Parse
original source decimal strings only inside explicit 100-dps contexts and
restore ambient precision afterward.  Independently reconstruct all 120
unique `(30 radial keys, m=-2/+2, plus/cross)` records and verify odd/even
60/60 record coverage.

For every record independently verify:

1. `exp(-i omega t)` signed currents have `J_in<0`, `J_out,total>0`, `J_h<0`.
2. The real-field-peak MP flux is
   `sigma_l*omega^2*abs(Psi_MP)^2/(128*pi)` and equals the current route
   `sigma_l*omega*abs(J)/(128*pi)`.
3. `sigma_l=(ell+2)!/(ell-2)!`, `N=c_lm/A_in_raw`, the explicit `1/2`
   time average and odd `Psi_CPM=(2i/omega)Psi_RW` are present with no fitted
   factor.
4. Route A and Route B total outgoing amplitudes are frozen free plus their
   accepted scattered amplitudes.  Free/scattered squares are diagnostic only;
   prove that the balance uses total outgoing, never scattered-only.
5. External odd is direct Regge--Wheeler and even is independently solved
   Zerilli; reparse original selected wp60 incidence/reflection/transmission
   rather than trusting candidate fields.
6. Recompute SchWO and external balances, six waveform/current checks, Route
   A/B outgoing fraction, SchWO/external outgoing fraction and horizon
   symmetric-relative fraction.  Bind each to the pre-execution threshold
   field/hash and verify all 120 pass without a signal floor or omission.
7. Retain the positive approximately `9.37e-1498` horizon fraction in
   arbitrary precision; any binary64 substitution or dropped item fails.
8. Rebuild every exact predicate, source/provenance identity, distinct
   numerical/convention budget and nonclaim; `radial_solve_count` must be zero.

Independently reload the v2 root in place and from a distinct temporary path.
Check `0555`/`0444`, nlink1 regular files, canonical JSON/JSONL, exact manifest,
no symlink/hardlink/staging/writer residue and source rebuild equality.

The v2 control-plane repair is part of this initial review, not a reason to
reopen or alter science.  Beginning at ambient `mp.dps=15`, prove that every
stored summary/report extremum equals the exact 100-dps extremum of canonical
record strings and that ambient precision is restored.  Prove v2 and v1
records are byte-identical while v1 remains forbidden current authority.

Run focused threshold/flux/publication tests and all Phase-6/V2 tests with the
exact overlay-first runtime, plus Ruff format/check on owned files, compileall
and repository `git diff --check`.  Verify the already frozen full-suite result
and do not rerun it unless a focused failure requires escalation.  Do not run
radial, angular or paper-figure workflows.

## Governance and verdict

Freeze `passed_items`, `failed_items`, `partial_allowed_items` and
`not_assessed_items`; classify every finding.  Only a complete class-A finding
that directly invalidates selected-domain flux closure may return REPAIR.
Absolute phase `PARTIAL`, full-domain incompleteness, absence of angles or
future V2.4 work are nonblocking here.  A pure metadata/path/wording issue is
`CONTROL_PLANE_REPAIR`, not a reopened full science review.

If all frozen V2.3 selected-domain criteria pass, return exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PARTIAL
GATE_LABEL: ACCEPT GREEN / V2.3 SELECTED-DOMAIN WAVEFORM AND FLUX CLOSURE READY FOR V2.4
```

If repair is required, use the template and complete all class-A fields.  Use
ESCALATE/HOLD only under the liveness protocol.  Bind the verdict to every
candidate/review/protected identity and state explicitly:

```text
V2.3 GREEN is bounded to the exact selected-domain infinity/horizon/radial flux observable.
Absolute phase remains PARTIAL; full-domain V2 remains NOT_ASSESSED.
No global GREEN is permitted.
```

You may update only `status.md`, T7 handoff and a necessary T7 archive after
the decision.  Do not dispatch V2.4.
