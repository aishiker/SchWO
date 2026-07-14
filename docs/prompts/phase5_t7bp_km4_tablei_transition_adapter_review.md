# Phase 5 T7bp Prompt: Review kM=4 Table-I Transition Adapter Gate

You are T7bp: independent validation for the T4x kM=4 Table-I transition
error-structuring and adapter gate.

Do not modify source, tests, configs, or run artifacts unless the review itself
requires a tiny metadata/status correction.  Prefer read-only inspection and
fresh verification commands.

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T0_current.md`
6. `docs/handoffs/T4_current.md`
7. `docs/handoffs/T7_current.md`
8. `docs/handoffs/T12_current.md`
9. `docs/prompts/phase5_t4x_km4_tablei_transition_error_structuring_adapter.md`
10. `docs/phase5_km4_tablei_adapter_closeout.md`
11. `docs/phase5_km4_tablei_transition_error_structuring_adapter.md`
12. `runs/phase5/km4_tablei_adapter_validation/stage1_yellow_blocker_metadata.json`
13. `runs/phase5/km4_tablei_adapter_validation/t4x_default_classification_metadata.json`
14. `runs/phase5/km4_tablei_adapter_validation/t4x_oracle_validation_metadata.json`
15. `src/schwgw/numerics/radial_solver.py`
16. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
17. relevant tests under `tests/physics/`, `tests/unit/`, and `tests/regression/`.

Use `systematic-debugging` if any verification fails and
`verification-before-completion` before the final decision.

## Review Questions

Answer each explicitly:

1. Did T4x reproduce and localize the original `ell=177` raw SVD blocker?
2. Does the default no-oracle path avoid leaking raw `LinAlgError` while
   preserving Q018 fail-closed behavior?
3. Did the continuous `kM=4`, `ell=2..360`, odd/even default classification
   finish with `default_error_other=0`?
4. Is the complete measured transition set recorded, not guessed from the old
   selected probes?
5. Did the direct Riccati/log-derivative oracle validate every in-envelope
   transition mode with finite fields and existing residual/stability
   thresholds?
6. If a new adapter was implemented, is it a separate exact opt-in envelope
   such as `q018_tablei_km4_transition`, and does it reject all out-of-envelope
   calls?
7. Is the old R60_K2 `q018_riccati` behavior unchanged?
8. Were frozen Fourier/harmonic/tetrad/RW/Zerilli/Route-B/Kirchhoff/Q018
   conventions preserved?
9. Were thresholds, `lmax`, boundary settings, and convergence policy left
   unchanged?
10. Did T4x avoid T8, dense scans, plots, fixtures, Kirchhoff values, and
    Fig.5/Fig.6 artifact generation?

## Required Fresh Checks

Run at least:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also parse the two T4x metadata files and independently confirm:

- `default_error_other == 0`;
- transition sets in classification and oracle validation agree;
- no non-finite oracle fields;
- residual/stability maxima meet the stated thresholds;
- metadata records exact parameters and provenance.

Check that no forbidden downstream artifacts were generated:

```bash
find runs/phase5/fig5_fig6_dense_review_grid runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
```

## Required Outputs

Update:

- `status.md`
- `docs/handoffs/T7_current.md`

If GREEN, say that T0 may schedule a new continuation of the autonomous
Fig.5/Fig.6 pipeline starting after the accepted T4x adapter gate.  Do not
start T8 yourself.

## Decision Labels

Use exactly one:

```text
ACCEPT GREEN / KM4 TABLE-I TRANSITION ADAPTER GATE PASSED
ACCEPT YELLOW / KM4 TABLE-I TRANSITION ADAPTER GATE PARTIAL
REJECT RED / KM4 TABLE-I TRANSITION ADAPTER GATE FAILED
```

GREEN requires all review questions to pass and no forbidden downstream work.

