# Formal T4 prompt — V3.1-U high-precision unitarity-deficit replacement

You are the existing formal SchWO T4 task.  This prompt is dormant until Root
T0 supplies an exact formal-T7 package-approval archive and hash for gate
`phase6_v3_1_hp_unitarity_deficit_replacement_v1`.

## Authority and scope

Read fully: `project.md`, the YAML header of `status.md`, T0/T4/T7 current
handoffs, `docs/review_gate_liveness_protocol.md`, the frozen V3.0 contract,
domain, thresholds, formula map and convention note, the final T7 ESCALATE
archive, and
`docs/phase6_v3_1_hp_unitarity_replacement_design.md` with SHA-256
`243f312182528b10a895cef679d195dcedfd97d7a2e02e388449ae3af313dd28`.

This is `V3.1-U`, a distinct replacement gate after T0 adjudication.  It is not
repair cycle 3, an r3 retry or V3.2.  Do not start unless the supplied formal
T7 verdict is exactly package `ADVANCE/NOT_ASSESSED` with the reviewed package
identity unchanged.

## Hard prohibitions

- Do not change any V3.0 formula, convention, 496-mode domain, 16 threshold or
  five certificate ID.
- Do not change/import through a new path any of the seven protected radial
  files.
- Do not modify existing cycle-2 implementation/runner/test bytes.
- Do not use Li figures, finite-radius observer frames or angular sums.
- Do not resume/reuse/copy science bytes from any r1/r3 root.
- Do not expand binary64 S into arbitrary precision, infer Gamma_S from direct
  flux, select Route U from an S-route mismatch, or reuse Route-B results as
  Route-U production calls.
- Do not launch an official root before every pre-execution gate passes.
- Do not claim V3.1 or global GREEN.  V3.2 remains unauthorized.

## Allowed files

Only these implementation paths may change:

```text
src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py
src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py
scripts/phase6_v3_1_hp_unitarity.py
tests/unit/test_phase6_v3_hp_unitarity.py
tests/regression/test_phase6_v3_hp_unitarity_publication.py
```

After real state changes, update only T4 archive/current and `status.md`.

## Required implementation

1. Rebuild the exact Route-A/Route-B/Route-C inventories from frozen inputs.
2. Compute Route A fresh: 496 modes, 9,920 nodes and one protected public call
   per node, with the cycle-2 geometry/continuation bytes only as read-only
   dependencies.
3. After all Route-A mode records exist and before any Route-U call, atomically
   freeze a 496-entry `unitarity_route_map.json`.  Its only selector is direct
   Route-A `log_Gamma_flux < log(1e-8)`.  Store source identity, operands,
   branch and ordinal.  Reject any selector access to S, Gamma_S, residual,
   PASS/FAIL, AP/external data or regime label.
4. For each routed mode, make three fresh independent mpmath calls using the
   exact precision schedule in the design.  Odd RW and even Zerilli are
   independently solved.  Route U may share analytic formulas and Route-B AP
   implementation bytes, but it may not import/call Route-A numerical code.
5. Derive `Gamma_S_U` only as
   `-expm1(2*log_abs_S_U)` from fresh complex `S_U`; preserve decimal strings,
   precision/cancellation margins and exact call identities.
6. Enforce the two Route-U numerical-admission bounds in the design.  A
   missing/nonfinite/nonpositive/unresolved node fails closed; do not add dps
   post hoc.
7. Evaluate all 16 frozen thresholds exactly as designed.  For small Gamma,
   use Route-A direct log Gamma versus highest-precision Route-U log Gamma_S.
   For large Gamma, retain the frozen float64 absolute branch.  Keep the
   original Route-B 102/458 and Route-C 23 graphs fresh and distinct.
8. Publish separate numerical/convention budgets and all five original
   certificates only if the complete graph passes.

## Pre-execution gates

Before an official root, complete and hash non-authoritative sentinels for:

- first low-frequency odd/even modes;
- a predeclared highest-barrier mode for every frequency and both parities;
- both sides of the `1e-8` selector boundary;
- exact synthetic `N_U=0,1,496` graphs;
- every negative/provenance/route-map/resume case in the design;
- unchanged Route-A/B/C and full synthetic publication/reload cardinalities;
- low/high-frequency highest-planned-dps runtime and disk projection;
- source/protected/import isolation and success/failure terminal validators.

Focused tests, adjacent V3 tests, Ruff format/check, py_compile and diff-check
must pass.  Rehash all protected and frozen inputs at start and end.

Report the exact preflight identities and projected lower/central/conservative
runtime to T0.  If any gate fails, if the conservative projection exceeds 36
hours, or if projected bytes exceed one quarter of measured free space, stop
without an official root.  Do not alter the reviewed algorithm.

## Official execution

If and only if all reviewed pre-execution and resource gates pass, create one
fresh root named

```text
runs/phase6/classic_scattering/
v3_1_hp_unitarity_deficit_v1_<YYYYMMDDTHHMMSSZ>_py314
```

using UTC metadata, `artifact_rev: 1`, `O_EXCL`, single-writer and the exact
terminal protocol in the design.  A scientific/threshold/provenance failure is
terminal and non-resumable.  Resume is allowed only for a proven system
interruption with an exact validated contiguous prefix and unchanged
identities.  Success and failure both require complete source-start/source-end
maps and terminal manifests.

After terminalization, independently reload every artifact/hash/count and run
the frozen validators.  Update T4 handoff/status honestly and return all exact
identities to T0.  Do not message T7 or start V3.2; T0 owns dispatch.
