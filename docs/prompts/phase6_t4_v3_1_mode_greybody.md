# Phase 6 V3.1 — formal T4 mode-greybody implementation and evidence

Date frozen by T0: 2026-08-11

Scientific stage: `Phase 6 / V3.1`

Artifact revision: `r1`

Execution class: bounded numerical science on the frozen V3.1 mode domain

You are the existing formal **T4 implementation/numerics task** for SchWO.
Work only in the shared repository
`/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO`.

V3.0 has received the formal independent verdict:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V3.0 ANALYTIC-LITERATURE BENCHMARK CONTRACT READY
absorption_branch_authorized: true
phase_sensitive_scattering_branch_authorized: true
```

This prompt authorizes **V3.1 only**. It does not authorize V3.2, angular
partial-wave scattering, glory, Li figures, finite-radius observers, a radial
backend modification, or global GREEN.

## 1. Mandatory reading and start gate

Read completely, in order:

1. `project.md`
2. the YAML current-state header and latest V3 entries in `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T4_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/archive/T7_2026-08-11_v3_0_contract_review.md`
7. `docs/review_gate_liveness_protocol.md`
8. `docs/prompts/phase6_v3_master_prompt.md`
9. all eight accepted V3.0 authority files
10. the current V1/V2 authorities and protected implementation identities
11. existing Phase-6 radial, AP and external-BHPT validation modules/evidence
   only as implementation/provenance inputs, never as a substitute for the
   V3.1 domain or thresholds.

At start and end, rehash these accepted V3.0 authorities:

| File | SHA-256 |
|---|---|
| `docs/phase6_v3_0_validation_contract.md` | `0f8b8c96e01321231377c857ab40d710aa80ac06dce9084029fe2914b1ef37d3` |
| `docs/phase6_v3_0_formula_map.md` | `e5b556667c28ac8b611430d2dfb4faa5da82b9c7f0c8251251029e3f8c8d0eac` |
| `docs/phase6_v3_0_phase_taxonomy.md` | `fb91f4cf888dd4984174304783875c9f2e591490df8519bafd2e0b0f73053460` |
| `docs/phase6_v3_0_literature_matrix.md` | `088834348e980b81f814340a2a2c460b5bf11239521085c358bed7a90f603328` |
| `configs/phase6_v3_0_domain.json` | `803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b` |
| `configs/phase6_v3_0_thresholds.json` | `91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a` |
| `configs/phase6_v3_0_external_anchor_matrix.json` | `06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485` |
| `references/notes/phase6_v3_absorption_scattering_conventions.md` | `82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a` |

Also bind:

- V3.0 T7 archive SHA-256
  `b672c7f33d2f3cc891f455c6d8123ed846309a07244696da34236f8e254c0126`;
- V3.0 T7 current handoff at dispatch SHA-256
  `1c58d8b8b8a563cf81edac68bb5a0c56675cfa626bdf5af6a2d0ba3a77d04cfa`;
- D-union plan SHA-256
  `de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`;
- seven protected radial source identities from the V3.0 JSON configs;
- current V1/V2 manifest identities from the `status.md` authority header.

If any identity differs, make no science write and return the exact frozen
identity HOLD. Do not repair or replace an accepted input.

Use `/opt/homebrew/bin/python3.14` and the exact project-local dependency paths
already used by accepted Phase-6 evidence. Record Python, NumPy, SciPy, mpmath,
Wolfram/BHPT and OS/runtime identities. Do not modify a global environment.

## 2. Exact domain and deterministic inventory

The only production domain is `configs/phase6_v3_0_domain.json["domains"]["V3.1"]`:

- 11 exact `kM` values: `0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 4, 8`;
- for each frequency every integer
  `ell=2..max(12, ceil(3*sqrt(3)*kM-0.5)+16)`;
- odd and even are independent radial solves.

The expected inventory is exactly 248 `(kM,ell)` pairs and 496 mode keys.
Rebuild this count from the config; do not hard-code only the count. Use exact
decimal-string frequency IDs and a deterministic sort by frequency ordinal,
`ell`, then parity `odd,even`.

For a selector saying “nearest critical”, choose the in-domain integer `ell`
that minimizes `abs((ell+0.5)-3*sqrt(3)*kM)`; an exact tie chooses the smaller
`ell`. For “critical+N”, minimize distance to
`3*sqrt(3)*kM-0.5+N`, then clip to the V3.1 domain and deduplicate keys while
retaining every anchor membership label.

Before any official producer starts, publish a machine-readable, hash-bound
inventory/route plan in the staging area. It must enumerate:

- all 496 Route-A keys;
- the exact union and membership of AP low/turning/evanescent anchors from
  `V3A-MODE-AP-LOW-001`, `V3A-MODE-AP-TURNING-001` and
  `V3A-MODE-AP-EVANESCENT-001`;
- the exact odd-only external keys from `V3A-MODE-BHPT-RW-001`;
- all ladder nodes and deduplication rules.

V2's sparse 30-key set is diagnostic provenance only. It cannot supply missing
V3.1 records, interpolate the V3.1 domain, or reduce its inventory.

## 3. Required independent routes

### Route A — SchWO production radial backend

For every one of the 496 keys, independently solve the odd or even equation
with the existing accepted production backend. Do not modify any protected
radial source. Extract and preserve raw complex `A_in`, `A_out`, and `A_H`,
signed Wronskian currents, positive incident/outgoing/horizon fluxes, complex
`S=(-1)^(ell+1) A_out/A_in`, `R=|S|^2`, direct
`Gamma_flux=F_H/F_in`, independent `Gamma_S=1-|S|^2`, and log Gamma.

`Gamma_flux` must not be populated from `S` or `1-|S|^2`. The horizon route
must be traceable to its own boundary amplitude/current. Keep signed currents
separate from positive physical fluxes.

Run the complete frozen ladders for every Route-A key, deduplicating identical
nodes without omitting a comparison:

- `r_in_eps/M = 1e-8, 1e-10, 1e-12`;
- effective base `r_out/M=max(300,sqrt(ell(ell+1))/omega)` multiplied by
  `1,2,4,8`;
- Jost orders `80,120,160,200`, with the full required outer/Jost comparison
  graph recorded explicitly;
- tolerance pairs exactly as frozen in the domain config.

Use the frozen baseline node (`r_in=1e-10`, multiplier 1 or the first node
passing the already frozen Jost-quality policy, Jost order 160,
`rtol=1e-10`, `atol=1e-12`) only through a deterministic pre-declared
selection rule. Do not choose a favorable node after seeing comparator values.

### Route B — independent arbitrary-precision direct solver

Implement/use a fresh arbitrary-precision RW and Zerilli direct integration
that does not import or call a protected SchWO radial implementation. Shared
analytic potentials/background formulae must be declared in the source map;
the integration, boundary, matching, amplitude and current extraction
algorithms must be independent.

Execute the exact AP anchor union at 80/120/180 decimal digits. Odd and even
are separate integrations. Preserve arbitrary-exponent decimal strings for
all raw amplitudes, currents, Gamma and log Gamma. Underflowed binary64 zero is
never an accepted representation. The turning anchors must also carry
independent boundary-ladder evidence as required by the anchor matrix; low and
evanescent anchors must preserve the applicable frozen boundary systematics.

The AP route must compute a direct horizon-current Gamma and an independent
S-route Gamma. It may not derive even data from the parity relation.

### Route C — external BHPT ReggeWheeler

Run fresh external Black Hole Perturbation Toolkit `ReggeWheeler` MST or
`Numerical` output for the exact odd-only anchor set. Capture package source
identity, method, runtime, raw amplitudes and convention translation to
`V3-F02`/`V3-F04`. Do not fall back to a SchWO/internal implementation.

This route certifies odd anchors only. A parity-derived even value may appear
only as `derived_consistency_only` and must never count as an independent even
solve. If the external runtime or package is unavailable, freeze a truthful
failed/NOT_ASSESSED candidate and return to T0; do not fabricate or substitute
the old Phase-5 comparison.

## 4. Frozen threshold evaluation

Evaluate all 16 V3.1 blocking thresholds from
`configs/phase6_v3_0_thresholds.json` exactly as written:

- complex S route comparison;
- log-Gamma AP comparison;
- normalized direct flux balance;
- Gamma flux/S agreement in ordinary and log domains;
- probability bounds;
- parity probability and relative phase;
- AP precision ladders;
- `r_in`, outer/Jost and tolerance ladders for S and log Gamma.

Threshold values, operators, domains and missing-data semantics are immutable.
Do not add a signal floor, fit phase, average failures away, clip Gamma into
`[0,1]`, replace a nonfinite number, or relax a gate. Every comparison records
raw operands, stable threshold field ID, value, result and numerical context.

For very small Gamma, retain finite arbitrary-exponent decimal and log-domain
values. If binary64 Route A cannot represent a mandatory direct Gamma, the
corresponding log-domain observable requires a justified scaled/log current
extraction from the same production solve; zero-by-underflow is FAIL, not
physical zero.

## 5. Evidence schema and certificates

Create one fresh official candidate root only after code/tests/smoke preflight:

`runs/phase6/classic_scattering/v3_1_mode_greybody_r1_<YYYYMMDDTHHMMSSZ>_py314`

The timestamp is UTC with trailing `Z`. Never reuse or overwrite a prior root.
The root must contain at least:

- `run_contract.json`;
- `inventory.json`;
- `records.jsonl` — exact 496 Route-A terminal mode records;
- `ladder_records.jsonl`;
- `ap_records.jsonl`;
- `external_records.jsonl`;
- `uncertainty_budget.json`;
- `source_map.json`;
- `summary.json`;
- `report.json`;
- `manifest.json`.

Each mode record must include exact key/ordinal, parity, raw amplitude/current
and flux routes, S/R/Gamma/log Gamma, all applicable threshold outcomes,
failure state, route/source identities, separate numerical and convention
budgets, and nonclaims. Pair records must be reconstructible from the two raw
independent parity records.

Publish exactly these candidate certificates:

1. `V3_MODE_GREYBODY_NUMERICAL`
2. `V3_MODE_GREYBODY_FLUX_VS_S`
3. `V3_MODE_GREYBODY_EXTERNAL`
4. `V3_MODE_PARITY_PROBABILITY`
5. `V3_MODE_DOMAIN_COVERAGE`

A certificate may be candidate PASS only if every applicable blocking item in
its exact scope passes. Missing blocking evidence is FAIL or NOT_ASSESSED, not
PARTIAL-by-default. Preserve native failures and all raw evidence.

The common absolute phase limitation is a convention-budget PARTIAL/nonclaim;
it does not prevent mode-probability candidate PASS. The candidate must still
state:

```json
{
  "global_status": null,
  "global_green_permitted": false,
  "independent_review_state": "NOT_ASSESSED"
}
```

T4 may report candidate threshold states but cannot self-issue the independent
V3.1 GREEN.

## 6. Uncertainty and independence ledger

Every accepted-key candidate record has two non-combined budgets.

Numerical budget includes every applicable precision, `r_in`, outer/Jost,
tolerance, route, flux, log-domain and matching term. Preserve assessed,
unassessed and failed components separately; do not use a max-float sentinel as
zero convention uncertainty.

Convention/observable budget includes master/parity normalization, Jost/free
reference, direct-flux versus S role, common absolute phase nonclaim, AP/shared
potential boundary, external BHPT translation and finite/infinity
applicability. State pairwise route independence explicitly:

- A/B share analytic equations/potentials and frozen conventions but not the
  integration/matching/amplitude algorithm;
- A/C share physical equations and convention translation, not code/runtime;
- B/C share physical equations and frozen observables, not numerical code;
- no pair is called fully independent without this qualification.

## 7. Implementation, execution and sealing protocol

Use new V3 files only, for example:

- `src/schwgw/scattering/absorption.py`;
- `src/schwgw/validation/phase6_v3_mode_greybody*.py`;
- `scripts/phase6_v3_1_*.py` and a bounded external `.wls` helper if needed;
- `tests/unit|physics|regression/test_phase6_v3*.py`;
- `docs/phase6_v3_1_mode_greybody.md`;
- T4 current/archive, `status.md`, and the fresh V3.1 run root.

Do not modify the seven protected radial files, existing V1/V2/V3.0 authority
bytes, V2 asymptotic modules, finite-radius observer modules, legacy/NP/
pseudoinverse paths, existing immutable evidence or Li artifacts. Avoid edits
to generic `__init__.py` unless importability truly requires it and it is not a
protected/frozen source; prefer direct module imports.

Before official execution:

1. build deterministic inventories and pure validators;
2. add unit/physics/regression tests, including injected failure, underflow,
   parity-derived-even rejection, source drift, duplicate/missing key,
   threshold-boundary and immutable-reload cases;
3. run focused tests, all `test_phase6_v3*.py`, Ruff check/format, compileall and
   scoped diff-check;
4. run only small non-authoritative smoke/timing probes in `/tmp`;
5. estimate official runtime and verify enough local disk/process isolation;
6. freeze implementation/runtime/source hashes into `run_contract.json`.

Once the official producer starts, its science sources, runtime, inventory,
thresholds and contract are frozen. Do not edit code and restart around failed
keys. Use a single-writer lock, exact resume contract, per-key atomic writes and
fsync. Resume is allowed only after a genuine system interruption and exact
contract/source/checkpoint validation; scientific/finite/threshold failure is
terminal evidence, not a resume reason.

Seal with no-overwrite publication, canonical serialization, root `0555`, all
direct files regular `0444`/nlink1, no symlink/staging residue, full manifest
rehash, in-place reload and distinct-temporary-copy reload. Rebuild the summary
and all certificates independently from raw records after sealing.

Do not run paper figures. Run the full repository suite only after the official
candidate is terminal and before handing it to T7, as required by the V3 master
prompt. Existing Ruff baseline debt is allowed only under zero-new-delta.

## 8. Stop conditions and terminal checkpoint

Stop and return to T0 without dispatching T7 if:

- any accepted V3.0/protected identity drifts;
- exact 496-key inventory cannot be constructed;
- a frozen domain/threshold/formula is contradictory or requires a change;
- independent AP or external BHPT requirements cannot be met;
- official execution has a scientific/threshold/nonfinite failure;
- an immutable publication/reload/provenance check fails;
- a needed fix would modify a protected radial or frozen V1/V2/V3.0 file.

Freeze truthful failure evidence; do not relax standards. Do not start V3.2.
Do not message T7 directly; Root T0 will verify and dispatch the already frozen
review prompt.

On successful candidate completion return only:

`CHECKPOINT / V3.1 MODE GREYBODY EVIDENCE FROZEN`

Include the exact root, every file SHA-256, inventory/route/threshold/certificate
counts, extrema, runtime, tests, protected start/end identities, limitations and
mandatory nonclaims.
