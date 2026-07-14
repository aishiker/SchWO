# Phase 3 Blocker Prompt: T7 Revalidation After T4/T6 Fixes

你现在是 `T7：验证与基准` 线程。只有在 T4 完成 Q012 high-`ell` radial stability 修复/诊断，并且 T6 完成 Q013 flat-space no-lens adapter / Q011 convention 判断后，才启动本 prompt。

任务是重新执行 Phase 3 final physics validation，并给出是否可以进入 M4 visualization/benchmark 的判断。

## 必读文件

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `references/notes/phase3_formula_audit.md`
9. `docs/prompts/phase3_blocker_t4_high_ell_radial_diagnostics.md`
10. `docs/prompts/phase3_blocker_t6_flat_space_nolens_adapter.md`
11. T4/T6 changed source and tests
12. `tests/physics/test_phase3_validation.py`

## 启动前置条件

Do not start final revalidation unless `status.md` records:

- Q012 status: fixed, or explicitly bounded with justified remaining limitations.
- Q013 status: flat-space no-lens oracle implemented or clearly rejected with reason.
- Q011 status: current convention validated, or a documented T6 convention change with tests.

If these are absent, stop and ask T4/T6 to complete their blocker tasks.

## 目标

Re-run Phase 3 acceptance:

- `compute_polarization` outputs finite `h_plus/h_cross`.
- Selected-probe `lmax` convergence reaches `<1e-4` first pass or has a documented physically justified revised target.
- Near-axis values remain finite and near-axis lmax-refinement reaches `<1e-3` first pass.
- Flat no-lens / polarization recovery passes.
- Q011 is no longer unresolved.
- No regression fixtures are generated unless all above are stable.

## 允许修改

- `tests/physics/test_phase3_validation.py`
- `docs/validation_plan.md` only to record justified thresholds or command boundaries.
- `tests/regression/fixtures/*.json` only if the user explicitly approves fixture generation after validation passes.
- `status.md`

Do not modify `src/` except for tiny import/export wiring discovered during revalidation. Formula or solver failures must go back to T4/T6.

## Required Commands

Run targeted tests:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_metric_reconstruction.py tests/unit/test_tetrads.py tests/unit/test_weyl_modes.py tests/unit/test_polarization_extraction.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_incident_flat_space.py tests/physics/test_partial_wave_observables.py tests/physics/test_phase3_validation.py
```

Run aggregate tests:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## Required Diagnostic Sweeps

Radial high-`ell` sweep:

```text
M=1, k=0.5, r=20, lmax values including at least 6,8,10,12
```

Low-`k` sweep:

```text
M=1, k=0.2, r=20, lmax values including at least 3,4,5,6
```

Flat no-lens sweep:

```text
Use the T6 flat-space adapter, not tiny-M horizon solve.
Pure plus, pure cross, and generic complex amplitudes.
```

Record:

- max adjacent-lmax relative change.
- max Wronskian residual for radial-backed runs.
- near-axis finite status and near-axis refinement change.
- flat no-lens relative polarization error.
- whether skipped/xfail validation entrypoints can be converted to active passing tests.

## Stop Conditions

Stop and update `status.md` if:

- Any default full pytest fails.
- `lmax` convergence still fails after 3 documented parameter/root-cause attempts.
- Flat no-lens adapter fails and Q011 cannot be resolved.
- High-`ell` radial Wronskian residual still blows up in the accepted lmax range.
- Passing would require relaxing thresholds without numerical or physical justification.
- Numeric fixtures are requested before validation is stable.

## Completion Conditions

- Phase 3 validation entrypoints are active where possible; remaining skips/xfails are explicitly justified and not part of exit criteria.
- `status.md` records changed files, commands, results, diagnostics, open issues, and a clear go/no-go decision for M4.
- If go: specify whether fixture generation is now safe.
- If no-go: identify whether blocker returns to T4, T6, or T1 convention review.
