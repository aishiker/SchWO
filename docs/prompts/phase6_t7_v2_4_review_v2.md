# Phase 6 T7 V2.4-v2 — final selected-domain release review

You are the existing formal SchWO T7 task. Independently review the current
V2.4-v2 selected-domain release read-only. Do not edit science or artifacts,
dispatch another task, enter V3, run figures, or start observer validation.

This prompt supersedes `docs/prompts/phase6_t7_v2_4_review.md` only for the
current v2 review. The old prompt and v1 release remain immutable historical
predecessors and are forbidden as current authority.

## Exact start gate

Require exactly:

```text
CHECKPOINT / V2 SELECTED-DOMAIN RELEASE CONTROL-PLANE REPAIR V2 FROZEN
```

The only current candidate is:

```text
runs/phase6/asymptotic_waveform/v2_selected_release_v2_20260811T083414_py314
  manifest.json        51ddf1580448382be7e182f92cf76bbf53ed39f15418af9e546f357979c743eb
  release_ledger.json  8bbc4d098ca64ac256a63a09e4e5744191f314038fe140c131eaf7606f75ba49
  report.json          58157a422fabed9be8bb9956c3097296c6dfd30b8d8065d4731edf6fe5a826dc
  source_map.json      9011a2cff8a944d68234a32cd754c7b6482b61644464fc512b906e2fbec76fb7
  summary.json         25dcc333085e3cd7150bf9e954766ae60a942f3a6e51c20ff36a4081077045cb
```

The root must be `0555`; all five direct files must be regular
`0444`/nlink1. The v1 predecessor
`runs/phase6/asymptotic_waveform/v2_selected_release_v1_20260811T081608_py314`
must remain immutable, must be marked superseded/forbidden current authority,
and must retain hashes `1500c198...27d3f`, `8bbc4d09...ba49`,
`44b6e503...fc0c`, `bc459ba0...08c7`, `25dcc333...45cb` in manifest,
ledger, report, source-map, summary order.

Read project/status/T7 handoff, `docs/review_gate_liveness_protocol.md`, the
verdict template, frozen V2.0 authorities/material review, accepted
V2.1--V2.3 roots and formal T7 decisions, the V2.4 T6 prompt, both V2.4
release roots, current V2.4 source/tests/T6 handoff, and
`docs/phase6_v2_selected_domain_closeout.md`. Do not trust a T6 ledger,
summary, report, or source map without rebuilding it from native sources.

## Frozen identities

At review start and end rehash:

```text
1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517  configs/phase6_v2_0_convention_contract_20260810.json
9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818  configs/phase6_v2_0_selected_domain_20260810.json
de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3  runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314/plan.json
9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9  src/schwgw/numerics/radial_solver.py
91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2  src/schwgw/numerics/conditioned_radial.py
d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df  src/schwgw/numerics/scaled_tortoise_radial.py
3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896  src/schwgw/numerics/adaptive_jost_radial.py
9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340  src/schwgw/numerics/matching.py
fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f  src/schwgw/numerics/physical_boundary_radial.py
b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22  src/schwgw/numerics/boundary_conditions.py
```

Any drift is `HOLD / V2 FROZEN INPUT IDENTITY MISMATCH` with all five HOLD
fields required by the liveness protocol.

## Independent release rebuild

Independently reload the immutable native V2.1, V2.2-v3, and V2.3-v2 roots
and rebuild the release without trusting V2.4 helper summaries. Verify:

- exact 30-key, 15 parity-pair, 120 ordered-record selected scope;
- exactly the twelve certificate IDs frozen by the V2.4 T6 prompt;
- native-to-certificate fail-closed state propagation, expected aggregate
  `11 PASS / 1 PARTIAL / 0 FAIL / 0 NOT_ASSESSED`, with only
  `V2_ABSOLUTE_PHASE_CONVENTION=PARTIAL`;
- every certificate's exact parameter/channel domain, separate numerical and
  convention budgets, evidence roots/file hashes, independence boundary,
  V2.0 authorities, protected identities, and nonclaims;
- `global_status=null`, `global_green_permitted=false`,
  `claim_status=PARTIAL`, `absolute_phase=PARTIAL`,
  `full_domain_v2=NOT_ASSESSED`, `radial_solve_count=0`, and no state upgrade;
- no extrapolation to 17,818 keys, complete angular waveform, finite-radius
  observer, total plane wave at null infinity, Li-figure, or global-GREEN
  claim;
- manifest, permissions, canonical serialization, in-place reload, and a
  distinct temporary-copy reload;
- v1/v2 `release_ledger.json` and `summary.json` are byte-identical; only
  report/source-map/manifest provenance changed.

## Control-plane delta review

Verify the bounded V2.4 live-handoff repair directly:

- historical `check-only` and reconstruction tests explicitly use
  `require_dispatch_review_identity=False`;
- actual publication still applies the default strict `True` gate at both
  start and end, before creating an output root;
- regressions prove an advanced live handoff permits historical read-only
  reconstruction but is rejected by strict publication;
- `DISPATCH_T7_SHA256`, certificate/science derivation, thresholds,
  conventions, domain, V2.1--V2.3 artifacts, v1 release bytes, and protected
  radial sources were not relaxed or changed.

This is a control-plane delta plus final release review, not a new scientific
review. Do not reopen accepted V2.1--V2.3 science without exact evidence that
the current release claim is invalid.

## Verification and verdict

Before modifying T7 coordination text, run targeted V2.4 tests, all
Phase-6/V2 tests, and the full suite using exact CPython 3.14 overlay-first,
plus Ruff, compileall, scoped diff checks, process/collision checks, and
start/end rehashes. Update only `status.md`, `docs/handoffs/T7_current.md`,
and a necessary T7 archive. Do not change source, tests, prompts, closeout,
roots, thresholds, or science.

Freeze `passed_items`, `failed_items`, `partial_allowed_items`, and
`not_assessed_items`. Classify every finding as exactly one of
`BLOCKING_CURRENT_GATE`, `NONBLOCKING_LIMITATION`, `CONTROL_PLANE_REPAIR`, or
`FOLLOW_UP_DEBT`. A scientific `PARTIAL`, `global_status=null`, or explicit
full-domain nonclaim is not a blocker.

Return one valid dual-axis verdict. On acceptance use exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PARTIAL
GATE_LABEL: ACCEPT GREEN / V2 SELECTED-DOMAIN GAUGE-INVARIANT WAVEFORM AND FLUX VALIDATION COMPLETE
```

If and only if a complete class-A finding invalidates the honest selected
release, use `REPAIR` with all required blocker fields. Use `ESCALATE` only as
required by the liveness protocol. Bind the verdict to every exact v2 release
identity and stop. GREEN is bounded to the frozen selected-domain V2 release;
it is not global GREEN, full-domain V2, complete angular waveform,
finite-radius observer validation, Li equivalence, or V3 authorization.
