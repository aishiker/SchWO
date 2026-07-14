# Phase 5 T7bd Prompt: Table-I Reporting Pilot Closeout

You are T7bd: closeout writer for the accepted Table-I four-frequency read-only plotting/reporting pilot.

This is a documentation/coordination slice only. Do not modify `src`, tests, configs, references, accepted NPZ/JSON artifacts, generated PNG/CSV/Markdown artifacts, or any `runs/` files.

## Required Reads

Read, in order:

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T0_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T8_current.md`
7. `docs/phase5_tablei_extraction_closeout.md`
8. `docs/prompts/phase5_t8ad_tablei_readonly_plotting_reporting_goal.md`
9. `docs/prompts/phase5_t7bc_tablei_plotting_reporting_review.md`
10. `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png.json`
11. `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png.json`

Also inspect the reporting directory listing and hashes.

## Task

Create:

- `docs/phase5_tablei_reporting_closeout.md`

Update:

- `status.md`
- `docs/handoffs/T7_current.md`

## Closeout Content Requirements

The closeout must state:

- Decision label:
  `CLOSED / ACCEPTED FOR TABLE-I FOUR-FREQUENCY READ-ONLY PLOTTING/REPORTING ONLY`
- Accepted artifacts:
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/tablei_four_frequency_values.csv`
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/tablei_four_frequency_values.md`
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png`
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png.json`
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png`
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png.json`
- The exact SHA-256 of all six artifacts, copied from fresh `shasum -a 256`.
- Source extraction NPZ/JSON hashes:
  - `69b2e449ba24bdc17fb6f85f0450d38daae6ce16f551381f19b13717c836ad2d`
  - `8a64c50ae96f75dc9a9ed4db2191098fe6d92418e4877b8752f87c7ca434f3f8`
- T7bc verification evidence:
  - CSV has 32 data rows.
  - Values were independently checked against accepted extraction arrays.
  - PNGs are nonblank.
  - Sidecars contain no-solver/no-recompute/no-interpolation/no-Kirchhoff/no-`kM=4`/not-paper-level flags.
  - Focused tests and full pytest passed under T7bc.
- Scope limitation:
  - The PNGs are sparse reporting pilots, not paper-level Fig.5/Fig.6 reproductions.
  - The apparent visual simplicity is expected because the data contain only four frequency samples, no dense `Mk` scan to about `4`, no `kM=4`, and no Kirchhoff dashed comparison curves.
- Remaining gates:
  - dense `Mk` scan planning;
  - explicit `kM=4` gate;
  - Kirchhoff Eq. (47) convention freeze;
  - production dense scan;
  - paper-level Fig.5/Fig.6 plotting after accepted dense artifacts.

## Required Commands

Run:

```bash
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/*
```

Do not run full pytest unless you change code/tests, which this prompt forbids.

## Stop Conditions

Stop and report RED if:

- any expected reporting artifact is missing;
- hashes differ from `status.md`/T7bc records;
- sidecars do not point to the accepted extraction NPZ/JSON;
- you would need to modify `src`, tests, configs, references, artifacts, or `runs/`;
- you find any claim that these PNGs are paper-level Fig.5/Fig.6 reproduction.

## Final Status Label

Use one of:

- `CLOSED GREEN / TABLE-I REPORTING PILOT CLOSED`
- `RED / TABLE-I REPORTING CLOSEOUT BLOCKED`

If GREEN, recommend that T0 may proceed to T10g dense Fig.5/Fig.6 + Kirchhoff readiness planning.
