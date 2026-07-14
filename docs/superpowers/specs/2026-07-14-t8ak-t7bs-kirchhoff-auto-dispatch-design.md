# T8ak–T7bs Kirchhoff Review-Grid Auto-Dispatch Design

Date: 2026-07-14
Owner: T0
Status: user-approved design (option 1)

## 1. Decision

The next Phase-5 slice is a two-gate chain:

1. **T8ak** implements and evaluates a bounded Kirchhoff Eq. (47) scalar
   comparison baseline on the already accepted 18-frequency by 8-point
   Fig.5/Fig.6 conservative review grid.
2. **T7bs** independently reviews the implementation, complex branches,
   numerical values, artifact contract, and separation from the production
   amplification path.

This slice does **not** authorize review-grid plots, 40-frequency production,
fixtures, journal/paper-style figures, or use of the Kirchhoff baseline in any
production denominator, mask, normalization, or polarization-dependent path.

## 2. Scientific Input Boundary

T8ak must use the exact frequency and point arrays in the independently
accepted T8aj review-grid artifact.  It must not reconstruct, reorder, round,
or expand them.

The frozen scalar/eikonal comparison formula is

\[
F_K=\exp(\pi\gamma/2)(-\gamma)^{-i\gamma}
\Gamma(1+i\gamma)\,{}_1F_1(-i\gamma;1;-i\gamma\eta^2),
\]

with

\[
\gamma=-2Mk,
\qquad
\eta=\frac{1}{2}\sqrt{\frac{r}{M}}\tan\theta.
\]

The implementation must follow
`references/notes/kirchhoff_eq47_conventions.md`, including:

- the principal real logarithm of `-gamma = 2 M k > 0`;
- the principal complex Gamma branch;
- Kummer's `M = 1F1` convention;
- principal complex phase for stored phase values;
- no same-positive-`k` complex-conjugation convention;
- polarization independence.

The baseline is comparison-only.  It is not an oracle for the Schwarzschild
solver and must never be used to accept, repair, mask, normalize, or replace
the accepted T8aj values.

## 3. T8ak Design

### 3.1 Isolated API

The preferred implementation location is
`src/schwgw/scattering/kirchhoff.py`.  The module should expose a small pure
API for Eq. (47) and structured metadata describing conventions and backend.
It must not be inserted into the existing pointwise amplification evaluation
or transmission-ratio code path.

Before implementation, T8ak must probe the project-local scientific runtime
for a complex Gamma/log-Gamma and complex Kummer `1F1` backend over the exact
18x8 domain.  A stable log-domain prefactor is preferred.  No global package
installation is authorized.  If no sufficiently stable project-local backend
is available, T8ak must stop YELLOW with a structured diagnostic instead of
adding an unreviewed dependency or silently reducing precision.

### 3.2 Artifact Contract

T8ak should write a separate directory:

`runs/phase5/fig5_fig6_kirchhoff_baseline/`

containing only:

- `tablei_kirchhoff_baseline_values.npz`;
- `tablei_kirchhoff_baseline_values.npz.json`;
- `manifest.md`;
- a structured error record only if the stage stops YELLOW/RED.

The successful artifact must contain at least:

- the exact accepted `kM` and Table-I point arrays and identifiers;
- `F_kirchhoff_complex` with shape `(18, 8)`;
- `abs_F_kirchhoff` with shape `(18, 8)`;
- principal phase, and an explicitly labelled unwrapped phase only if used;
- `eta` for each point;
- formula, branch, units, backend, version, dtype, and comparison-only metadata;
- finite/domain masks that describe the baseline itself but do not alter T8aj;
- source-artifact and output SHA-256 values.

### 3.3 Verification Boundary

Focused tests and artifact checks must cover:

- formula and branch metadata;
- array shapes, point ordering, dtype, and finite values;
- stable evaluation across the exact review grid;
- comparison against independent high-precision spot checks;
- deterministic regeneration within a stated tolerance;
- proof that the production amplification path and accepted T8aj artifact are
  unchanged;
- absence of plot, 40-frequency, fixture, and paper-style outputs.

T8ak is GREEN only after the code/tests, artifact hashes, `status.md`, and
`docs/handoffs/T8_current.md` have been written and freshly re-read.  Otherwise
it must return YELLOW/RED and must not start T7bs.

## 4. T7bs Independent Review

T7bs is read-only with respect to implementation and baseline data generation.
It may update only its review records, `status.md`, and T7 handoff/archive files
allowed by its prompt.

T7bs must independently verify:

- the Eq. (47) transcription, signs, dimensions, and all frozen branches;
- exact identity and ordering of the 18x8 T8aj input grid;
- complex values against an independent high-precision calculation or a
  justified equivalent reference route;
- finite/domain/phase behavior and declared numerical tolerances;
- NPZ/JSON/manifest agreement and SHA-256 values;
- lack of mutation or coupling to the production solver, ratios, masks,
  normalization, or polarization channels;
- lack of unauthorized plots or dense-production artifacts.

Only an exact T7bs GREEN accepts the baseline and permits T0 to design a later,
separate read-only diagnostic-plot gate.

## 5. Cross-Task Auto-Dispatch State Machine

T0 owns scheduling.  The current runtime bindings are:

- T8 task: `019f5ece-f578-7b91-8f61-df882c656591`;
- T7 task: `019f5ed1-b421-7ec2-9bac-8d134855a1ed`;
- T0 task: `019f5ec5-84ba-79e2-8c77-1160b150a636`.

The dispatch state machine is:

1. T0 freezes separate reusable T8ak and T7bs prompt files, records their paths
   in `status.md` and the T0 handoff, and verifies the scheduling diff.
2. In the same user-facing turn in which T0 reports the final plan, T0 sends
   the frozen T8ak prompt to the existing T8 task with **5.6 Sol High**.
3. T8 completes T8ak without starting any later scientific stage.  After an
   exact GREEN and fresh verification, T8 sends the already frozen T7bs prompt
   to the existing T7 task with **5.6 Sol High**.
4. A T8ak YELLOW, RED, incomplete run, missing artifact, failed check, or
   ambiguous completion must not start T7bs.  T8 reports the stop state to T0.
5. T7 reports its exact decision to T0.  T7 must not start a later
   implementation or plotting task.
6. If a bound task is absent, archived, or otherwise unavailable, orchestration
   stops and returns to the user; it does not silently create a replacement.

To prevent document races, downstream dispatch occurs only after the upstream
task has finished all artifact and documentation writes and freshly verified
them.  At most one task may write a shared status/handoff file at a time.

## 6. Model-Capacity Recovery Policy

The default for every dispatched task is **5.6 Sol High**.

If and only if the app reports an explicit model-capacity or equivalent system
interruption, the same existing task may be resumed with **5.6 Terra High**.
The recovery message must instruct the task to inspect existing process and
artifact state, reuse safe checkpoints, and avoid recomputation when possible.
The fallback does not relax scientific checks, change prompt scope, reinterpret
YELLOW/RED as GREEN, or authorize a new stage.

Ordinary scientific errors, failed tests, non-finite values, backend
instability, timeouts with ambiguous process state, and missing artifacts are
not model-capacity failures.  They return to T0 instead of triggering an
automatic model fallback.

## 7. Status, Handoff, And GitHub Boundaries

T8ak completion alone is not a verified major project node because T7bs is
still pending.  T7bs exact GREEN is an independent acceptance of a high-risk
comparison baseline and therefore is a major node under `project.md`.

After T7bs GREEN, T0 must:

1. independently inspect the decision and fresh evidence;
2. update and verify `status.md` and `docs/handoffs/T0_current.md`;
3. inspect the complete working-tree diff and exclude secrets, private raw
   data, unintended large files, and unrelated/unreviewed changes;
4. create a scope-explicit non-force commit and push the authorized branch to
   the configured private GitHub repository;
5. record `GitHub sync pending` with the exact blocker instead of performing a
   blind sync if the safe commit boundary is unclear.

The automatic T8-to-T7 handoff does not grant either task authority to push to
GitHub.  GitHub milestone synchronization remains T0-only.

## 8. Rejected Alternatives

The following alternatives are rejected for this slice:

- combining baseline implementation and plotting in one review gate, because
  special-function/branch failures and plotting failures would become mixed;
- resuming the older broad T12/T12b autonomous pipeline, because it could
  cross unapproved review-grid, 40-frequency, and paper-style boundaries;
- allowing T7 to repair the implementation or start later stages, because that
  would break independent review and T0 scheduling ownership.

## 9. Definition Of Done For Scheduling

This design is ready to become an executable plan when:

- the user has approved option 1, including the bounded Sol-to-Terra capacity
  fallback;
- this design document is committed separately from the existing mixed
  working-tree changes;
- the user has reviewed this durable design;
- T0 then uses the `writing-plans` workflow to create the implementation and
  dispatch plan before generating and sending the two prompts.
