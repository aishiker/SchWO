# Phase 5 T7bk Prompt: Fig.3 Four-Frequency dx=0.25M Production Closeout

你现在是 **T7bk：Fig.3 four-frequency dx=0.25M accepted production archive closeout**。

## Must Read First

1. `project.md`
2. `status.md`
3. `docs/handoffs/T7_current.md`
4. `docs/handoffs/T8_current.md`
5. `docs/phase5_fig3_four_frequency_dx0p25_production_plan.md`
6. `docs/prompts/phase5_t8ah_fig3_four_frequency_dx0p25_production_goal.md`
7. `docs/prompts/phase5_t7bj_fig3_four_frequency_dx0p25_production_review.md`
8. `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`

Before doing task work, check whether installed plugins/skills are relevant. Use only those that help with local documentation/closeout review.

## Goal

Create a formal closeout document for the T7bj-accepted Fig.3 four-frequency `dx=0.25M` production archive.

This is documentation/status closeout only. Do not rerun production, do not regenerate plots, and do not modify artifacts.

## Accepted Decision To Record

Record this decision exactly:

```text
ACCEPT GREEN / FOUR-FREQUENCY DX0.25 PRODUCTION ARCHIVE ACCEPTED
```

Archive:

```text
runs/phase5/fig3_four_frequency_dx0p25_production/
```

Scope:

- Option A fresh four-frequency archive;
- `kM=[0.5,1.0,1.5,2.0]`;
- `dx=dz=0.25M`;
- `x/M,z/M in [-30,30]`;
- Route B/M4 saved-result path;
- not by-reference reuse of the T8ae/T8af `kM=2` pilot.

## Allowed Files

Create:

- `docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md`

Optional, if consistent with the handoff archive practice:

- `docs/handoffs/archive/T7_2026-07-09_fig3_dx0p25_production_review_pre_closeout.md`

Update:

- `status.md`
- `docs/handoffs/T7_current.md`

## Forbidden Actions

- Do not rerun `schwgw.cli run`.
- Do not rerun plotting commands.
- Do not modify `src/`.
- Do not modify tests.
- Do not modify configs.
- Do not modify files under `runs/phase5/fig3_four_frequency_dx0p25_production/`.
- Do not modify the accepted `kM=2` pilot directory.
- Do not create fixtures.
- Do not run `dx=0.2M`.
- Do not run `kM=4`.
- Do not run R60/R60_K4.
- Do not generate Fig.2 strict `Psi4`.
- Do not implement Kirchhoff or Appendix D/E curves.
- Do not claim paper-level or final journal-grade Fig.3 readiness.
- Do not change physics conventions, thresholds, `lmax`, or boundary tolerances.

## Closeout Document Requirements

`docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md` must include:

1. Decision:
   - T7bj GREEN label;
   - date;
   - archive path;
   - accepted scope.
2. Artifact inventory:
   - four NPZ files;
   - four run JSON files;
   - per-frequency nearest/bilinear PNGs and sidecars;
   - archive-level nearest/bilinear PNGs and sidecars;
   - manifest.
3. Key hashes:
   - manifest;
   - four NPZs;
   - archive-level nearest PNG;
   - archive-level bilinear PNG.
4. Numerical evidence:
   - shape `(241,241)`;
   - valid/invalid `57884/197`;
   - mask policy `valid_mask == (r > 2M)`;
   - valid fields finite;
   - invalid fields complex NaN;
   - final adjacent pair `[156,180]` passed for all four frequencies;
   - radial cache metadata present.
5. Q018 evidence:
   - zero-warning structured metadata for `kM=0.5,1.0,1.5`;
   - `kM=2.0` warning count `56`, code `evanescent_tail_suppressed`, ell `153..180`, sectors `even/odd`, `valid_until_r_min=42.472089355131786`, margin `0.045682483938932705`, covers `rmax=42.42640687119285`.
6. Plot/sidecar policy:
   - nearest is audit/numerical provenance;
   - bilinear is display-only smoothing;
   - sidecars contain source NPZ SHA/size, run JSON provenance, Q018 summary, interpolation policy, final-pair status, grid/DPI/counts, convention metadata, and non-claim flags.
7. Verification evidence:
   - T7bj focused pytest result `58 passed in 6.20s`;
   - static viz dependency check no output;
   - source/test/config timestamp checks no output;
   - independent Python inspection PASS.
8. Explicit non-claims:
   - not paper-level;
   - not final journal-grade;
   - not `dx=0.2M`;
   - not `kM=4`;
   - not R60/R60_K4;
   - not Fig.2 strict `Psi4`;
   - not fixtures;
   - not dense Fig.5/Fig.6;
   - not Kirchhoff/Appendix D/E.
9. Remaining gates:
   - figure-quality/literature comparison review before any paper-level Fig.3 claim;
   - `dx=0.2M` only if later review decides `dx=0.25M` remains insufficient;
   - `kM=4`, R60/R60_K4, Fig.2 strict `Psi4`, Kirchhoff, Appendix D/E remain separate gates.
10. Exact next-step options:
   - T0 may schedule a T10/T7 figure-quality comparison/reproduction-readiness review;
   - or pause Fig.3 and return to Fig.2 strict `Psi4`/other gated work.

## Required Checks

Run read-only checks:

```bash
test -f docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md
test -f runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md
find runs/phase5/fig3_four_frequency_dx0p25_production -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md
rg -n "FOUR-FREQUENCY DX0.25 PRODUCTION ARCHIVE ACCEPTED|paper-level|final journal|dx=0\\.2|kM=4|R60|Fig\\.2|Q018|58 passed" docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md
```

Pytest is not required because this closeout must not change source/tests. If source/tests are modified, stop and run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## Required Updates

Update `status.md` with:

- changed files;
- files read;
- commands/checks run;
- closeout result;
- open issues;
- next action options.

Update `docs/handoffs/T7_current.md` with:

- current state after closeout;
- closeout document path;
- accepted archive scope;
- remaining gates;
- exact next task options for T0.

## Definition of Done

- Closeout document exists and records the T7bj accepted archive without overstating it.
- No production artifact, source, test, config, convention, threshold, or `lmax` change occurred.
- `status.md` and T7 handoff are updated.
- The next T0 step is clear: either schedule a figure-quality/literature comparison review or choose another gated track.
