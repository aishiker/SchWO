# T7 Current Handoff

Last updated: 2026-07-14

Thread: T7bs, Fig.5/Fig.6 review-grid Kirchhoff Eq. (47) scalar
comparison-baseline independent review.

## Thread Role And Current Status

T7bs completed an independent read-only review of the T8ak implementation and
18-by-8 Kirchhoff Eq. (47) scalar comparison artifact.

Decision recorded exactly:

```text
ACCEPT YELLOW / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE PARTIAL
```

The formula, numerical values, branches, source-grid integrity, hashes,
isolation, focused tests, Ruff, and full pytest all pass. GREEN is withheld
because the user-approved artifact contract requires explicit `units` and
`dtype` metadata, while neither the NPZ embedded metadata nor JSON sidecar nor
manifest records those fields. The array itself is `complex128`, and the
array names imply dimensionless `kM`, `r/M`, and `eta`, but inference is not a
substitute for the required metadata contract.

This YELLOW does not authorize plots, 40-frequency production, fixtures,
paper-style candidates, artifact mutation, or a later scientific stage.

The pre-T7bs handoff was archived at:

```text
docs/handoffs/archive/T7_2026-07-14_pre_t7bs_kirchhoff_baseline.md
```

## Review Answers

1. **PASS.** Source implements the frozen Eq. (47) with
   `gamma=-2Mk`, coordinate-derived `eta`, positive-real principal
   `log(-gamma)`, principal complex `loggamma`, Kummer M via `hyp1f1`, and no
   conjugation. `gamma`, `eta`, and the special-function arguments are
   dimensionless in the frozen convention.

2. **PASS.** Backend is lazily imported optional project-local `mpmath
   1.4.1`, with `dps=60` recorded. All 144 saved values are finite and the
   validity mask is all true.

3. **PASS.** Source and baseline `kM` and point arrays are bitwise equal.
   The accepted T8aj NPZ/JSON/manifest hashes remain unchanged.

4. **PASS.** Coordinate-derived eta is stored separately from rounded paper
   `xi/xi0`; maximum absolute difference is
   `4.337937456566632e-05 < 5e-5`.

5. **PASS.** Complex value, magnitude, principal phase, display-only
   unwrapped phase, and validity mask are `(18,8)`, finite, and reproduce
   direct NumPy derivations.

6. **PASS.** An independent all-grid 100-dps calculation agrees exactly after
   conversion to saved `complex128`; maximum absolute saved-reference
   difference is `0.0`. Kummer-transformation checks pass at `(k index,
   point index)=(0,0),(0,7),(17,0),(17,7)` using 120 dps.

7. **PARTIAL / BLOCKS GREEN.** NPZ arrays, embedded JSON, external sidecar,
   output hashes, and manifest hashes agree. However, the approved design
   requires formula, branch, **units**, backend, version, **dtype**, and
   comparison-only metadata. `units` and `dtype` are absent from all three
   metadata surfaces. The existing tests also omit these required assertions,
   which explains why the schema gap passed T8ak verification.

8. **PASS.** The API is isolated in new Kirchhoff modules. The two scoped
   implementation commits do not modify production transmission,
   Schwarzschild numerics, Q018, visualization, configs, regression fixtures,
   masks, normalization, or polarization channels. Static searches found no
   new call from those paths into the Kirchhoff API.

9. **PASS.** T8ak produced exactly three files in the bounded baseline
   directory and did not create review-grid plots, dense-production outputs,
   fixtures, configs, visualization changes, or paper-style candidates. T8aj
   artifacts remain byte-identical.

10. **PASS.** Fresh focused tests: `9 passed in 0.26s`. Ruff: clean. Fresh
    full pytest: `558 passed, 117 skipped, 1 xfailed, 85 warnings, 79
    subtests passed in 285.02s`. Warnings are existing Weyl/Wigner/radial
    numerical warnings; no new Kirchhoff warning occurred.

## Artifact Hashes Rechecked

Accepted T8aj inputs:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  runs/phase5/fig5_fig6_dense_review_grid/manifest.md
```

T8ak outputs:

```text
a91f0a5f5eb672ac897ea776f7577d4f33b89c72154dc1b665c8ced06cbec53c  runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz
86670c426ada2284d334a017b6abdfc36443d0fb7ea82606f3d544de17788a19  runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json
53d852b25bd73bb25cecb37518e72a010c5b3882cf5e86799e4b695178586d49  runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md
```

## Completed Work

- Read and followed
  `docs/prompts/phase5_t7bs_fig5_fig6_review_grid_kirchhoff_baseline_review.md`.
- Read the approved design, implementation plan, frozen convention note,
  current project/handoffs, T8ak prompt, artifacts, both implementation
  commits, and every T8ak source/test/script file.
- Inspected commit scope and current mixed worktree independently.
- Recomputed all 144 values at 100 dps without calling the T8ak compute API.
- Checked four independent Kummer-transformation corners at 120 dps.
- Verified exact source arrays, eta derivation, phase/magnitude arrays,
  validity mask, embedded/external metadata relationship, source/output
  hashes, and manifest contents.
- Ran focused pytest, Ruff, mandatory full pytest, scope checks, static
  isolation searches, and forbidden-output checks.
- Updated only `status.md`, this T7 handoff, and its archive.

## Checks Run

```text
T7BS_INDEPENDENT_100DPS_AUDIT=PASS
max_abs_saved_minus_reference 0.0
max_abs_eta_minus_paper 4.337937456566632e-05

focused pytest: 9 passed in 0.26s
Ruff: All checks passed!
full pytest: 558 passed, 117 skipped, 1 xfailed, 85 warnings,
             79 subtests passed in 285.02s
```

Scope results:

- Commit `70ef022` contains exactly the isolated API and its unit test.
- Commit `c09bbf9` contains exactly the serializer, IO export, script, and
  artifact test.
- Forbidden production-source diff is empty.
- Forbidden downstream artifact search is empty.
- Baseline directory contains exactly NPZ, JSON sidecar, and manifest.

The first independent-audit command completed all scientific assertions and
printed PASS but then exited nonzero because a reviewer-added diagnostic tried
to access an `NpzFile` after its context had closed. `systematic-debugging`
traced this to the review script lifetime, not the artifact. The complete
audit was rerun with the scalar copied before context exit and returned exit
zero with the results above.

## Incomplete Work

- The accepted artifact metadata contract is not complete until explicit
  units and dtype metadata are added and independently re-reviewed.
- T0 has not yet inspected this YELLOW or designed a bounded metadata-only
  hardening/review gate.
- No diagnostic plot or later production stage is authorized.

## Blocking Issues And Non-Blocking Warnings

- **Blocking GREEN:** explicit `units` and `dtype` metadata required by
  `docs/superpowers/specs/2026-07-14-t8ak-t7bs-kirchhoff-auto-dispatch-design.md`
  are absent from the embedded metadata, sidecar, and manifest.
- The missing metadata does not invalidate the independently reproduced
  numerical values, formula branches, or isolation result.
- The working tree contains unrelated accumulated handoff/status changes.
  They were inspected and excluded from the scientific decision.
- Full-suite warnings are pre-existing and non-blocking for this gate.

## Files The Next Thread Must Read

1. `status.md`
2. `docs/handoffs/T7_current.md`
3. `docs/handoffs/T8_current.md`
4. `docs/superpowers/specs/2026-07-14-t8ak-t7bs-kirchhoff-auto-dispatch-design.md`
5. `docs/prompts/phase5_t7bs_fig5_fig6_review_grid_kirchhoff_baseline_review.md`
6. `src/schwgw/io/kirchhoff.py`
7. `tests/unit/test_kirchhoff_artifact.py`
8. `runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json`
9. `runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md`
10. `references/notes/kirchhoff_eq47_conventions.md`

## Frozen Decisions

- Eq. (47) formula and the T1j principal branches remain unchanged.
- No positive-frequency conjugation is permitted.
- Coordinate-derived eta and rounded paper values remain distinct.
- Kirchhoff remains scalar, polarization-independent, and comparison-only.
- It must not enter the solver, denominator, masks, normalization,
  calibration, Q018, or polarization channels.
- Accepted T8aj inputs and current T8ak artifacts are read-only until T0
  explicitly authorizes a bounded repair/regeneration slice.

## Forbidden Actions

- T7 must not repair source, tests, scripts, metadata, or artifacts.
- Do not generate or regenerate the baseline from T7.
- Do not create plots, 40-frequency data, fixtures, configs, Appendix D/E,
  interpolation, smoothing, or paper-style candidates.
- Do not change models to reinterpret this schema failure as GREEN.
- Do not start a later task or push GitHub from T7.

## Superseded Prompts

- The T8ak implementation prompt is complete and cannot be reused by T7 to
  repair this issue.
- T7br and earlier T7 radial/data prompts remain completed historical gates.
- T12/T12b autonomous pipeline prompts remain superseded.

## Exact Next Task

Return this exact YELLOW decision to T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636`. T0 must decide whether to create a
bounded T8 metadata-contract hardening prompt that adds explicit units and
dtype metadata, updates the relevant artifact-contract tests, regenerates the
three baseline files without changing numerical values/formula branches, and
then requests a separate T7 rereview. T7bs starts no such task itself.

## Allowed Files, Verification Commands, And Definition Of Done

The only T7bs writes are:

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-14_pre_t7bs_kirchhoff_baseline.md`

T8ak source, tests, scripts, all T8ak artifacts, T8aj artifacts, configs, and
other handoffs remain untouched.

Definition of done for T7bs is satisfied when all ten questions have evidence,
the exact YELLOW is recorded, the schema blocker is stated without artifact
repair, review documents are freshly verified, artifacts remain byte-identical,
and the decision/evidence are sent to T0.
