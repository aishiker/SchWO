# Phase 5 T7bh Prompt: Fig.3 kM=2 dx=0.25 Sidecar Hardening Review

你现在是 **T7bh：Fig.3 kM=2 dx=0.25 pilot sidecar provenance review**。

## Must Read First

1. `project.md`
2. `status.md`
3. `docs/handoffs/T7_current.md`
4. `docs/handoffs/T8_current.md`
5. `docs/prompts/phase5_t8af_fig3_k2_dx0p25_sidecar_hardening.md`
6. `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.run.json`
7. `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_manifest.md`
8. If present: `docs/phase5_fig3_k2_dx0p25_hires_pilot_closeout.md`

Before doing task work, check whether installed plugins/skills are relevant. Use only those that help with local artifact review.

## Goal

Independently verify whether T8af closed the T7bg sidecar provenance gap without changing numerical artifacts or expanding scope.

This is a review-only task. Do not rerun the solver and do not generate new plots.

## Review Requirements

Verify:

1. The source NPZ is unchanged:
   - path: `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.npz`
   - SHA-256: `5edddc1326a9f756c2507d3c3ac2285b067ca81333d300de7f2bca1c023bbbe2`
   - size: `59539269`
2. The two PNG files are unchanged from T8ae/T7bg:
   - nearest SHA-256: `b52cfc1a58dcfa5f06c3edd55781f520f2ad5a3aaa0d4d61a45896d140da3ce1`
   - bilinear SHA-256: `c8c93b391f15f768c9817f8d8ec2a11045c889abef20d9e03ad798161db2f286`
3. Both PNG sidecar JSON files now include, by explicit keys:
   - source NPZ path;
   - source NPZ SHA-256;
   - source NPZ size;
   - run JSON path;
   - Q018 warning summary;
   - `not_paper_level_claim: true`;
   - `not_final_journal_grade: true`;
   - `single_frequency_resolution_evidence_only: true`;
   - false flags for four-frequency `dx=0.25M`, `dx=0.2M`, `kM=4`, R60, and Fig.2 strict `Psi4`.
4. Q018 sidecar summary matches the run JSON:
   - warning count `56`;
   - code `evanescent_tail_suppressed`;
   - ell range `153..180`;
   - sectors odd/even;
   - `rmax=42.42640687119285`;
   - `valid_until_r_min=42.472089355131786`;
   - `coverage_margin_min_minus_rmax=0.045682483938932705`;
   - `suppression_bound_max=1.2994970680433635e-24`;
   - `covers_rmax=true`.
5. Interpolation policy is not ambiguous:
   - nearest is the audit plot and exposes the saved grid;
   - bilinear is display-only and not numerical evidence.
6. The task did not modify `src/`, tests, configs, NPZ, or PNGs.
7. `status.md` and `docs/handoffs/T8_current.md` record changed files, commands, test results, and next action.

## Commands / Checks

Run:

```bash
shasum -a 256 runs/phase5/fig3_k2_dx0p25_hires_pilot/*
```

Run a small independent Python inspection over the run JSON and both sidecars. It must not import solver/scattering/project physics APIs.

Run focused tests:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
```

Do not run full pytest unless source/tests were modified. If source/tests were modified, treat that as a scope issue and record it.

## Decision Labels

Use one of these:

- **ACCEPT GREEN / SIDECAR PROVENANCE GAP CLOSED**:
  all required sidecar metadata is present, NPZ/PNG hashes are unchanged, and focused tests pass.
- **ACCEPT YELLOW / NUMERICS STILL ACCEPTED BUT SIDECAR GAP PARTIAL**:
  numerical artifacts are unchanged, but a nonfatal sidecar/status/handoff metadata gap remains. Say exactly what blocks four-frequency `dx=0.25M`.
- **RED / SCOPE OR ARTIFACT INTEGRITY FAILURE**:
  NPZ or PNG artifacts changed unexpectedly, source/tests/configs were modified without authorization, or sidecar facts conflict with run JSON.

## Required Updates

Update only:

- `status.md`
- `docs/handoffs/T7_current.md`

Record:

- files inspected;
- commands/checks run;
- decision label;
- whether four-frequency `dx=0.25M` production can now be scheduled;
- open issues and forbidden actions.

## Next-Step Guidance

If GREEN:

- Recommend T0 schedule a separate four-frequency `dx=0.25M` production planning prompt.
- Do **not** directly run production from T7.

If YELLOW:

- Provide the exact narrow T8 follow-up prompt needed to close the remaining metadata gap.

If RED:

- Stop and recommend artifact integrity triage before any new computation.
