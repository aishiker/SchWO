# Phase 5 T8af Prompt: Fig.3 kM=2 dx=0.25 Sidecar Provenance Hardening

你现在是 **T8af：Fig.3 kM=2 dx=0.25 pilot read-only closeout / sidecar provenance hardening**。

## Mode

Use Goal mode if available. Continue until the Definition of Done is met or a stop condition is reached.

## Must Read First

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/prompts/phase5_t8ae_fig3_k2_dx0p25_hires_goal.md`
7. `docs/prompts/phase5_t7bg_fig3_k2_dx0p25_hires_review.md`
8. `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.run.json`
9. `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_manifest.md`

Before doing task work, check whether installed plugins/skills are relevant. Use only those that are actually helpful for this local metadata hardening task.

## Goal

Close the T7bg YELLOW provenance gap for the already-generated single-frequency Fig.3 pilot.

This task is **metadata-only**. Do not rerun the solver. Do not regenerate the NPZ. Do not change physics/source formulas.

## Background

T7bg accepted the T8ae numerical pilot as:

```text
ACCEPT YELLOW / FIG3 K2 DX0.25 HIRES PILOT ACCEPTED WITH NAMED RISKS
```

The remaining YELLOW reason is that the two PNG sidecars do not independently record enough provenance:

- `source_result_sha256`
- `source_result_size_bytes`
- `q018_warning_summary`
- `not_final_journal_grade`
- `not_paper_level_claim`

These facts exist in the run JSON, manifest, and status. This task must copy the essential provenance into each PNG sidecar and update closeout documentation.

## Strict Scope

Allowed:

- Update these existing sidecar JSON files in place:
  - `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png.json`
  - `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png.json`
- Update:
  - `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_manifest.md`
  - `status.md`
  - `docs/handoffs/T8_current.md`
- Optionally create:
  - `docs/phase5_fig3_k2_dx0p25_hires_pilot_closeout.md`

Forbidden:

- Do not rerun `schwgw.cli run`.
- Do not rerun the solver through any Python API.
- Do not modify `src/`.
- Do not modify tests.
- Do not modify configs.
- Do not change the NPZ file.
- Do not modify the PNG image files unless a sidecar cannot be updated without doing so; if that happens, stop and report RED/YELLOW.
- Do not generate four-frequency `dx=0.25M`.
- Do not run `dx=0.2M`.
- Do not run `kM=4`.
- Do not run R60/R60_K4.
- Do not generate Fig.2 strict `Psi4`.
- Do not create fixtures.
- Do not make paper-level or final journal-grade claims.

## Required Sidecar Fields

Each of the two PNG sidecar JSON files must preserve existing fields and add or verify these fields:

```json
{
  "source_result_path": "runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.npz",
  "source_result_sha256": "5edddc1326a9f756c2507d3c3ac2285b067ca81333d300de7f2bca1c023bbbe2",
  "source_result_size_bytes": 59539269,
  "run_json_path": "runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.run.json",
  "q018_warning_summary": {
    "warning_count": 56,
    "codes": ["evanescent_tail_suppressed"],
    "ell_min": 153,
    "ell_max": 180,
    "sectors": ["even", "odd"],
    "rmax": 42.42640687119285,
    "valid_until_r_min": 42.472089355131786,
    "coverage_margin_min_minus_rmax": 0.045682483938932705,
    "suppression_bound_max": 1.2994970680433635e-24,
    "covers_rmax": true
  },
  "not_paper_level_claim": true,
  "not_final_journal_grade": true,
  "single_frequency_resolution_evidence_only": true,
  "four_frequency_dx025_production": false,
  "dx02_production": false,
  "kM4_production": false,
  "R60_production": false,
  "fig2_strict_psi4_artifact": false
}
```

Also ensure each sidecar clearly records:

- interpolation policy:
  - nearest: audit plot; exposes saved grid; numerical/provenance inspection plot.
  - bilinear: display-only smoothing; not numerical evidence.
- `grid_spacing`
- `final_lmax_pair`
- `final_pair_passed`
- `valid_point_count`
- `invalid_point_count`
- `requested_dpi`
- Fourier/gauge/polarization convention fields already present.

It is acceptable for exact JSON key names to be slightly more structured, but T7 must be able to find the facts unambiguously by key, not only in prose.

## Optional Closeout Doc

If you create `docs/phase5_fig3_k2_dx0p25_hires_pilot_closeout.md`, keep it concise and include:

- decision state: T7bg numerical pilot accepted YELLOW, sidecar hardening pending T7bh review;
- artifact list;
- NPZ hash/size;
- unchanged PNG hashes if PNGs were not touched;
- updated sidecar hashes;
- Q018 summary;
- explicit non-claims:
  - not four-frequency `dx=0.25M`;
  - not `dx=0.2M`;
  - not `kM=4`;
  - not R60/R60_K4;
  - not Fig.2 strict `Psi4`;
  - not paper-level/final journal-grade.

## Verification Commands

Run:

```bash
shasum -a 256 runs/phase5/fig3_k2_dx0p25_hires_pilot/*
```

Run a small read-only Python inspection that:

- loads the run JSON;
- loads both PNG sidecar JSON files;
- verifies the source NPZ path/SHA/size match the run JSON;
- verifies the required Q018 fields match the run JSON;
- verifies the non-claim flags are present;
- verifies interpolation policy is distinguishable for nearest vs bilinear;
- verifies NPZ and PNG hashes did not change from the T8ae/T7bg accepted values.

Run focused tests:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
```

Do **not** run full pytest unless you accidentally modify source or tests. If source or tests are modified, stop and explain why that happened before proceeding.

## Stop Conditions

Stop and report YELLOW/RED if any of these occur:

- the NPZ hash differs from `5edddc1326a9f756c2507d3c3ac2285b067ca81333d300de7f2bca1c023bbbe2`;
- either PNG hash differs from the T8ae/T7bg accepted hash;
- run JSON is missing or inconsistent with the sidecar facts;
- Q018 summary cannot be represented without ambiguity;
- sidecars cannot be updated without touching source, tests, configs, NPZ, or PNGs;
- focused tests fail for reasons that look related to this task.

## Required Updates

Update `status.md` with:

- changed files;
- commands run;
- sidecar hardening result;
- updated sidecar hashes;
- test results;
- open issues;
- exact next action for T7bh.

Update `docs/handoffs/T8_current.md` with:

- current state after T8af;
- changed files;
- forbidden actions;
- required next T7 review prompt;
- definition of done for T7bh.

## Definition of Done

- Both PNG sidecars independently contain source NPZ path/SHA/size, Q018 warning summary, non-claim flags, interpolation policy, final pair, and grid spacing.
- NPZ and PNG hashes are unchanged.
- Manifest/status/T8 handoff are updated.
- Focused tests pass or a clear stop reason is recorded.
- T7 can review with:

```text
你现在是 T7bh。请读取并严格执行 docs/prompts/phase5_t7bh_fig3_k2_dx0p25_sidecar_review.md。
```
