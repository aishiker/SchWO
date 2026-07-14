# T7bl Prompt: Independent Fig.3 dx=0.25M Figure-Quality Review

You are T7bl: validation and independent review.

This is a review-only gate after T10i.  Do not run production computation and do
not mutate accepted artifacts.

## Read First

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/handoffs/T10_current.md`
7. `docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md`
8. `references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md`
9. `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`
10. all ten PNG sidecars under
    `runs/phase5/fig3_four_frequency_dx0p25_production/`

Before reviewing, check whether an installed plugin/skill is relevant.  Use
local data and notes first; no web lookup is needed unless local evidence is
internally inconsistent.

## Scope

Independent review only.  You may inspect image dimensions, PNG metadata,
sidecars, manifest, hashes, and NPZ metadata.  Do not call solver/scattering
APIs and do not generate new plots.

## Review Criteria

Check:

1. T10i did not overclaim final journal-grade readiness.
2. T10i separated numerical saved-data adequacy from rendering/panel polish.
3. The accepted archive still matches the Fig.3 physical content and parameter
   scope.
4. `dx=0.25M` evidence is treated as production evidence, not as a proof of
   pixel-level reproduction.
5. `dx=0.2M` is not authorized unless T10i gives concrete evidence that
   numerical saved-data resolution, not rendering, is the limiting factor.
6. Nearest and bilinear sidecar semantics remain intact.
7. Q018 evidence remains same-domain only and is not generalized to `kM=4`,
   R60/R60_K4, or larger domains.

## Required Decision

Return exactly one of:

```text
ACCEPT GREEN / FIG3 DX0.25 ARCHIVE IS READY FOR READ-ONLY PUBLICATION RENDERING
ACCEPT YELLOW / NEED READ-ONLY RENDER POLISH BEFORE PAPER-QUALITY CLAIM
ACCEPT YELLOW / DX0.2 PLANNING JUSTIFIED
RED / LITERATURE OR SCOPE MISMATCH
```

Interpretation:

- GREEN means no new computation should be run before a T8 read-only
  publication-rendering pass.
- YELLOW render polish means the next task is still T8 read-only rendering,
  followed by another T7 image review.
- YELLOW dx0.2 means T0 should schedule planning and cost/risk review only, not
  immediate production.
- RED means stop Fig.3 promotion and route back to the relevant physics or
  literature thread.

## Required Status/Handoff Updates

Update:

- `status.md`
- `docs/handoffs/T7_current.md`

Record:

- files read;
- commands/checks run;
- changed files;
- decision and rationale;
- whether tests were run or not;
- open issues;
- exact recommended next T0 action.

## Forbidden Actions

- Do not modify `src/`, tests, configs, or accepted artifacts.
- Do not generate new NPZ/HDF5/CSV/PNG/PDF artifacts.
- Do not rerun plotting.
- Do not run `dx=0.2M` or `kM=4`.
- Do not create fixtures.
- Do not change frozen physics conventions, thresholds, `lmax`, or boundary
  policies.
- Do not claim final journal-grade readiness unless the decision explicitly
  supports only the next read-only rendering step.

## Verification Commands

Run read-only checks at minimum:

```bash
test -f references/notes/t10i_fig3_dx0p25_figure_quality_literature_review.md
test -f runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md
rg -n "ACCEPT GREEN|ACCEPT YELLOW|RED|dx=0\\.25|dx=0\\.2|read-only|publication|Fig\\.3|Q018|nearest|bilinear" status.md docs/handoffs/T7_current.md
```

Full pytest is required only if source/tests change, which this review should
not do.

## Definition Of Done

- T7bl records one required decision label.
- `status.md` and `docs/handoffs/T7_current.md` are updated.
- No source/test/config/accepted-artifact mutation occurred.
- T0 has an exact next branch.

