# Phase 6 V3.1 — T4 bounded repair cycle 1 implementation

Date frozen by T0: 2026-08-11

Scientific stage: `Phase 6 / V3.1`

Artifact revision: `r2`

You are the existing formal T4 implementation/numerics task. Work in
`/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO`.

This prompt is inactive until Root T0 supplies a formal T7 package-review
verdict with exact label
`ACCEPT GREEN / V3.1 REPAIR CYCLE 1 PACKAGE READY FOR T4` bound to the
unchanged package manifest. Do not infer approval from this file alone.

## Mandatory reading

Read completely:

1. `project.md`;
2. the YAML header and latest V3.1 entries in `status.md`;
3. T0, T4 and T7 current handoffs;
4. `docs/handoffs/archive/T4_2026-08-11_v3_1_terminal_failure.md`;
5. `docs/handoffs/archive/T7_2026-08-11_v3_1_initial_failure_review.md`;
6. `docs/review_gate_liveness_protocol.md`;
7. the V3 master prompt and original V3.1 T4/T7 prompts;
8. all eight accepted V3.0 authority files;
9. `docs/phase6_v3_1_repair_cycle1_design.md`;
10. the repair package manifest supplied by T0;
11. current V1/V2 authority manifests and the seven protected radial sources;
12. existing V1 pole-safe, AP and external-BHPT modules only as audited
    implementation references.

At start, rehash every identity in the repair package. Require the formal T7
package approval to bind the same package SHA. Any drift is HOLD before
science and no repair-package file may be edited.

## Required implementation

Implement the design exactly:

- Route A uses only the frozen public scaled-tortoise solver and the exact
  20-node per-key graph, giving 496 modes and 9,920 nodes;
- Route B is a V3-local independent AP RW/Zerilli solver with exactly 102 keys
  and 458 nodes, including 80/120/180 digits and turning-boundary variants;
- Route C performs 23 fresh odd-only BHPT ReggeWheeler MST calls through the
  external-SSD WolframKernel;
- all 16 thresholds and exactly five certificates rebuild from raw operands;
- JSONL is one compact canonical object per line;
- source map carries complete accepted/protected start/end ledgers;
- previous `r1` roots remain immutable and denylisted.

Do not modify any protected/frozen file, scientific formula, convention,
domain, selector, threshold or acceptance operator. Do not add a favorable
backend, fit, floor, clipping, missing-data waiver or parity-derived even solve.

Prefer separate V3-local modules for Route A, AP, external, thresholds and
publication when that keeps boundaries auditable. Direct imports from
protected public APIs are permitted only for Route A. Route B and Route C must
remain algorithmically separate from Route A and from each other as frozen in
the design.

## Tests and non-authoritative preflight

Before official science:

1. add injected tests proving the full 496/9,920/102/458/23 orchestration path;
2. test all 16 threshold boundaries, missing/failure propagation, log-domain
   tiny Gamma, parity-derived-even rejection and external internal-fallback
   rejection;
3. test compact JSONL, manifest/source-map tamper, start/end protected drift,
   exact resume rejection and in-place/distinct-copy reload;
4. run focused and all V3 tests, Ruff check/format, compileall and diff-check;
5. under `/tmp`, run the exact failed Route-A key's complete 20 nodes and the
   design's Route-A/AP/external sentinel matrix;
6. publish and reload a synthetic full-route root marked non-scientific;
7. measure runtime/disk and confirm enough resources;
8. freeze implementation/runtime/source/run-contract hashes and rehash the
   protected inputs again.

Within this pre-execution boundary you may correct defects only in the allowed
V3-local files. If a sentinel requires a protected change, if an independent
route is unavailable, or if a frozen requirement is contradictory, stop and
return exact evidence to T0. Do not create an official root.

## Official run

Only after every preflight gate passes, create one fresh no-overwrite root:

`runs/phase6/classic_scattering/v3_1_mode_greybody_r2_<UTC-Z>_py314`.

Use `/opt/homebrew/bin/python3.14`, the frozen project-local dependencies and
the exact external-SSD kernel. Use a single coordinator writer and exact
checkpoint/resume protocol from the design. Do not edit any science source or
restart after a scientific/threshold/nonfinite/provenance failure.

On success, independently rebuild all records, extrema, budgets, summary and
five certificates; seal/reload in place and in a distinct temporary copy; run
the full repository suite; rehash accepted/protected inputs at end; update T4
handoff/archive and `status.md`; return only:

`CHECKPOINT / V3.1 MODE GREYBODY EVIDENCE FROZEN`

Include exact root/file hashes, counts, extrema, runtimes, tests, source-map,
uncertainty budgets and nonclaims. Do not dispatch T7 or start V3.2.

On failure, seal truthful evidence if an official root exists, update T4
handoff/archive and status, and return to T0. Never overwrite, retry for a
science failure, modify a consumed root or claim global GREEN.

