# T4ae Equivalence-Preserving Methods Gate Plan

## Goal

Implement and benchmark only the pre-result methods contract in
`docs/superpowers/specs/2026-07-24-t4ae-equivalence-preserving-methods-prequalification-design.md`.
Do not generate or authorize any new scientific frequency.

## Frozen Start Gate

- Read `project.md`, `status.md`, current T0/T4/T7/T8 handoffs, applicable
  architecture/numerics/validation/extension documents, all five candidate
  files, T7cf evidence, and immutable T4ad/T8as artifacts.
- Verify the exact five-file candidate commit/parent/blob/SHA identity
  supplied by T0 and exact matching
  `REVIEW GREEN / T0 REPAIR PACKAGE APPROVED`.
- Verify legacy implementation `8fb8608...`, all T8as contracts/roots,
  selected legacy NPZ hashes, and image-golden hash.
- Stop before write or compute on any mismatch.

## Task 1 — Clean Legacy Baseline Before Edit

Under exact clean legacy implementation `8fb8608...`:

1. Freeze benchmark config, environment, BLAS thread settings, scientific
   ordering, and full identity hashes.
2. Run the exact five existing frequency cases and the full accepted image
   configuration in an isolated methods directory.
3. Record wall/user/system CPU, peak RSS, solve/reuse counts, stage timings,
   arrays, and contracts atomically.
4. Compare the fresh baseline to each immutable accepted artifact. A baseline
   mismatch is a stop, not an implementation opportunity.

Reuse only an exact complete matching baseline checkpoint.

## Task 2 — Profile And TDD RED

- Produce stage profiles proving where repeated work occurs.
- Add failing tests for typed interfaces, legacy adapter equivalence,
  certified-domain dense reuse, read-only oracle-cache identity, wrong-key
  rejection, deterministic two-worker ordering, and checkpoint faults.
- Preserve radius-specific oracle certification. Do not merge distinct
  required-radius states.

## Task 3 — Typed Interface And Legacy Adapter

- Add typed convention/provenance metadata and protocols for background,
  channel/spin/parity, radial system, boundary/asymptotics, incident source,
  angular/mode coupling, domain driver, backend, projector, and writer.
- Keep the existing Schwarzschild scalar-master/RWZ behavior behind a
  legacy adapter.
- Support scalar and coupled-state contracts without implementing a new
  spin-2, Teukolsky, or coupled-channel theory.
- Update only the four exact architecture/numerics/validation/extension docs.

## Task 4 — Equivalence-Preserving Optimization

- Reuse ordinary radial solutions across certified radii and consumers using
  one solve plus dense/vectorized evaluation.
- Add an immutable read-only cache keyed by complete
  physics/solver/config/source/gate/implementation identity.
- Use independent T4ad oracle values only after full hash/provenance
  validation; fail closed on any mismatch.
- Add fixed at-most-two-worker deterministic execution with stable result
  ordering and one BLAS/OpenMP thread per worker.
- Add atomic checkpoint/resume and fault injection. Never recompute a complete
  matching work unit or reuse across identity.

## Task 5 — Exact Implementation Commit

Run focused tests and Ruff, then create one commit changing exactly the
fourteen paths listed in the design. No benchmark produced after code changes
may precede this implementation identity.

If code must change after the commit, return to `gpt-5.6-sol/ultra`, create a
new identity, and invalidate optimized checkpoints as required. Do not reuse
them across identity.

## Task 6 — Optimized Benchmark And Fresh Verification

- Run the exact same five-frequency and full-image matrix.
- Apply every exact/floating/image/scientific residual condition in the
  predeclared error budget.
- Apply solve-count, wall/CPU, per-case, and peak-RSS performance gates.
- Run serial/two-worker deterministic ordering, cache rejection, and
  checkpoint fault tests.
- Run focused pytest, exact-scope Ruff, fresh full pytest,
  `git diff --check`, exact commit/worktree/source checks, warning
  classification, and forbidden-output searches.
- Write an atomic manifest and methods note; update only allowed coordination
  records; return only to T0.

## Exact Scope

The implementation commit changes exactly:

```text
docs/architecture.md
docs/extension_interface.md
docs/numerics.md
docs/validation_plan.md
scripts/phase5_equivalence_preserving_methods_gate.py
src/schwgw/numerics/radial_cache.py
src/schwgw/scattering/contracts.py
src/schwgw/scattering/legacy_adapter.py
src/schwgw/scattering/partial_wave.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_scalar_adapter_equivalence.py
tests/regression/test_equivalence_preserving_methods_gate.py
tests/unit/test_radial_cache.py
tests/unit/test_scattering_contracts.py
```

Other writes are limited to the exact methods artifact/note and T4
coordination paths in the design.

## Exact Decision

Return exactly one:

```text
GREEN / EQUIVALENCE-PRESERVING METHODS GATE READY
YELLOW / EQUIVALENCE-PRESERVING METHODS EVIDENCE INCOMPLETE
RED / EQUIVALENCE-PRESERVING METHODS GATE INVALID
```

Do not dispatch T7ch, T8, a new frequency, or any later scientific package.
