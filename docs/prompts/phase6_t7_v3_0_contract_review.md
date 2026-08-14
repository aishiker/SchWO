# Phase 6 V3.0 — formal T7 independent contract review

Date frozen by T0: 2026-08-11

Scientific stage: `Phase 6 / V3.0`

Artifact revision: `r1`

Review class: independent read-only scientific/control-plane review

You are the existing formal **T7 independent review task** for SchWO. Work in
the shared repository
`/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO`.

This is a review of a zero-science V3.0 literature/formula/domain/threshold
freeze. It is not a review of V3 numerical results. Do not implement repairs,
run a radial solve or partial-wave sum, change a threshold, or start V3.1.

## 1. Frozen review contract

Read in order:

1. `project.md`
2. the YAML current-state header and latest V3 entries in `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T1_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/review_gate_liveness_protocol.md`
7. `docs/templates/t7_gate_verdict_template.md`
8. `docs/prompts/phase6_v3_master_prompt.md`
9. `docs/phase6_v2_to_v3_transition.md`
10. `docs/prompts/phase6_t1_v3_0_literature_formula_freeze.md`
11. all eight T1 V3.0 outputs named in that prompt
12. `references/manifest.md`, `docs/equation_map.md`, `docs/physics_spec.md`
13. V2.0 convention/domain contracts and current immutable V1/V2 authorities

The blocking criteria in this prompt are frozen before T1 work. Review only
against them. New suggestions that do not directly invalidate the bounded
V3.0 contract-readiness claim are `D. FOLLOW_UP_DEBT`, not retrospective
blockers.

At review start and end, independently rehash:

- master prompt
  `f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7`;
- V2.0 convention contract
  `1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`;
- V2.0 selected domain
  `9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`;
- current V2 release five-file identity ledger from
  `docs/phase6_v2_to_v3_transition.md`;
- current V1 radial, production-state and selected-independent manifests;
- seven protected radial sources and the D-union plan;
- the frozen T1 and T7 prompts;
- every T1 V3.0 output and all source files T1 changed.

If evidence or identity is missing/inconsistent, use HOLD only under the
strict conditions in `docs/review_gate_liveness_protocol.md`, and state exact
reason, unblock condition, owner, minimum next action and whether independent
downstream work may proceed.

## 2. Independent checks

Do not accept a candidate validator as the scientific proof. Independently
inspect and, where useful, rederive the following.

### 2.1 Primary-source traceability

- Each mandatory absorption/scattering/glory formula has a primary-source
  record and an equation/page locator or a transparent independent derivation.
- Source conventions and their conversion to SchWO are explicit.
- Handler–Matzner, both relevant Dolan works, Folacci–Ould El Hadj, the adopted
  series-reduction primary source, and the RW/Zerilli/Moncrief/Martel–Poisson
  normalization chain have an exact role or an explicit justified exclusion.
- Li–Hou–Zhao is secondary regression only.
- No formula is frozen from unreferenced model memory.

### 2.2 Mode and flux definitions

Verify under `exp(-i omega t)`:

- incident/reflected/horizon amplitudes and complex odd/even S matrices;
- Jost/free reference phase and tortoise convention inheritance;
- signed currents versus positive physical fluxes;
- direct `Gamma_flux=F_H/F_in` and independent
  `Gamma_S=1-|S_l|^2` routes;
- reflection/transmission probability, extremely small-Gamma log-domain
  representation and no binary64-zero acceptance;
- odd/even independent-solve and parity limitations.

### 2.3 Absorption and scattering formulae

Independently check dimensions, degeneracy/parity/helicity weights, `ell` start,
units and boundary assumptions for partial/total absorption. Check the sourced
low-frequency law and high-frequency capture limit.

Independently check the `f(theta)`, `g(theta)`, `d sigma/d Omega`, odd/even
combinations, `S_l-1`, total/free/scattered separation, Coulomb/long-range
phase, forward distribution, series-reduction recurrence and angle exclusion.
Check the low-frequency spin-2 expression in the adopted convention rather
than merely recognizing its shape.

Independently check the glory formula, critical impact parameter, spin-2 Bessel
order, `b_g`, `|db/dtheta|`, units and peak/width/amplitude comparator
definitions.

### 2.4 Phase taxonomy and branch booleans

Verify evidence and downstream dependence for all seven frozen phase classes.

Set `absorption_branch_authorized: true` only if the V3.1 mode greybody and
V3.2 total-absorption definitions, domains, anchors, thresholds, direct-flux
route, log-domain policy and uncertainty schema are complete and executable.
A PARTIAL common overall/time-origin phase does not by itself block this
branch.

Set `phase_sensitive_scattering_branch_authorized: true` only if the
`ell`-dependent phase, odd/even relative phase, total/free/scattered reference
phase, required Coulomb subtraction and spin-harmonic convention are PASS, and
the V3.3/V3.4 formula/domain/threshold contracts are complete. Otherwise set it
false and classify the limitation precisely; that alone does not block the
absorption branch or V3.0 contract readiness.

### 2.5 Domain, anchors and thresholds

- V3.1–V3.4 have distinct, explicit domains.
- V3.1 covers the declared ordinary, critical-barrier/turning,
  evanescent/high-ell and low/mid/high-frequency strata.
- V3.2 uses a continuous multipole sequence and frozen frequency ladder, not
  the sparse V2 30-key controls.
- V3.3 freezes low-frequency/angle/forward-exclusion/reduction ladders.
- V3.4 freezes high-frequency/backward-angle/glory ladders.
- External and arbitrary-precision anchors have honest independence roles;
  parity-derived even data are not called independent even solutions.
- Every threshold predates producers and has field ID, operator, value, units,
  domain, rationale/source and stage-blocking role.
- Observable thresholds are not silently inherited from V1/V2 radial gates.

### 2.6 Governance and protected boundaries

Verify canonical JSON, UTC/revision metadata, exact upstream identities,
separate numerical/convention budgets, per-observable/per-domain adjudication,
fresh immutable later-artifact rules, and mandatory nonclaims.

Verify no V3 producer/root/process exists, no radial or partial-wave science ran,
no protected radial/V2 convention byte changed, and no superseded root entered
the accepted predecessor graph. Full-domain incompleteness, future V3.2–V3.5
work, Li disagreement and global-GREEN absence are not blockers for this gate.

## 3. Frozen acceptance and finding rules

The bounded claim is only:

`V3.0 has a scientifically sourced, internally consistent and executable
analytic/literature benchmark contract suitable for gated downstream work.`

The gate passes only when all mandatory checks above are satisfied and at least
the absorption branch can be evaluated under frozen inputs. The phase-sensitive
branch may remain unauthorized without converting a truthful absorption-ready
V3.0 gate into REPAIR.

Use the dual-axis/finding protocol exactly:

- `A. BLOCKING_CURRENT_GATE` is the only class that permits `REPAIR`;
- every A finding must include `blocker_id`, `violated_contract_item`, exact
  evidence, expected/observed values, bounded repair, allowed files, recheck
  command and unblock condition;
- metadata/path/wording-only issues are `C. CONTROL_PLANE_REPAIR` when science,
  formulas, thresholds, input identities and solver behavior are unchanged;
- limitations outside the bounded claim are B or D;
- freeze `passed_items`, `failed_items`, `partial_allowed_items` and
  `not_assessed_items` in the verdict for incremental recheck;
- do not reopen passed items without exact evidence of invariant drift;
- obey the two-repair-cycle limit.

## 4. Allowed writes and verification

The scientific review is read-only. You may write only:

- `docs/handoffs/T7_current.md`;
- a new dated `docs/handoffs/archive/T7_*v3_0*.md` review record.

Do not edit T1 outputs, prompts, configs, source maps, source code, tests,
thresholds, contracts, status, immutable roots or another handoff. T0 will
transcribe an accepted verdict into project state.

Run read-only/config checks only: source retrieval/inspection, independent
algebra/dimension checks, JSON canonicality, SHA-256 and permission/identity
checks, scoped `git diff --check`, and process/transient checks. Do not run V3
science or the full numerical suite.

## 5. Required terminal verdict

Return a complete verdict with:

```text
ADVANCE_DECISION: ADVANCE|REPAIR|ESCALATE
CLAIM_STATUS: PASS|PARTIAL|FAIL|NOT_ASSESSED
GATE_LABEL: <exact bounded label>
absorption_branch_authorized: true|false
phase_sensitive_scattering_branch_authorized: true|false
```

If accepted, the exact gate label is:

`ACCEPT GREEN / V3.0 ANALYTIC-LITERATURE BENCHMARK CONTRACT READY`

The accepted verdict must be `ADVANCE_DECISION: ADVANCE` and
`CLAIM_STATUS: PASS`. Include findings by class, frozen incremental-review sets,
exact reviewed identities, commands/checks, uncertainty/convention limitations
and mandatory nonclaims.

This GREEN means only the bounded V3.0 contract may advance according to the two
branch booleans. It is not V3 science PASS, full-domain certification, Li figure
equivalence or global GREEN. Do not dispatch T4; return the verdict to Root T0.
