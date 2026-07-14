# Phase 3 T7l Prompt: Hardening Regression Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7l`。

启动条件：

- Run after T6k completes.
- If T4i is also executed, run this after T4i as well.
- If T4i is deferred, review T6k and explicitly record that Q015 structured metadata remains deferred.
- Do not run this while T7k is still modifying status/tests unless you first re-read latest `status.md`.

先读：

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `references/notes/q014_curved_polarization_bridge.md`
9. T6k modified `src/schwgw/scattering/*`
10. T6k modified tests
11. If T4i ran: T4i modified `src/schwgw/numerics/*`, `src/schwgw/scattering/partial_wave.py`, and tests

目标：

Independently verify Phase 3 hardening without changing Phase 3 physics. This is a regression review, not a new convention review.

必须验证：

## 1. Phase 3 closeout document

Check `docs/phase3_closeout.md` exists and states:

- Q014 closed by T7f independent validation.
- Route B production invariant.
- strict NP scalars are not packaged polarization scalars.
- Q015 remains separate and non-blocking unless T4i has only added metadata.
- Q016 high-`ell` Wigner-D overflow resolved.
- forbidden shortcuts are documented.

If the document implies Q014 is reopened, stop and return to T0/T1.

## 2. API/type boundary

Verify:

- `StrictNPScalars`, `ElectricTidalComponents`, and `PackagedPolarizationScalars` or equivalent distinct typed objects exist.
- Production `compute_polarization(...)` routes through typed packaged scalars before polarization extraction.
- Raw strict `Psi0_NP/Psi4_NP` are not passed directly to packaged extraction.
- Legacy API names, if retained, clearly say they consume packaged scalars.

Use source scan and tests. A useful scan:

```bash
rg -n "polarization_from_weyl|polarization_from_packaged|compute_packaged|StrictNP|Packaged|ElectricTidal|Psi0|Psi4" src/schwgw/scattering tests/unit/test_polarization_extraction.py
```

## 3. Regression tests

Confirm tests prove:

- strict/package types are not silently interchangeable.
- `compute_polarization(...)` does not call the legacy raw two-scalar extraction path.
- Route B numerical outputs did not change beyond roundoff.
- flat no-lens diagnostic remains genuine.

## 4. Q015 metadata

If T4i ran:

- Verify structured warning metadata includes mode parameters and residual context.
- Verify thresholds were not relaxed.
- Verify Q015 remains non-blocking unless paired with boundary/finite/condition/field-convergence failures.

If T4i did not run:

- Record that Q015 metadata hardening remains open and should be run with `docs/prompts/phase3_t4i_q015_structured_diagnostics.md`.

## 5. Q016 permanent regression

Verify high-`ell` Wigner-D and spin-weighted harmonic checks are permanent tests:

- `tests/unit/test_wigner.py` covers finite high-`ell` values.
- `tests/unit/test_spin_weighted_harmonics.py` covers finite high-`ell` spin-weighted values and high-`ell` conjugation stability.

If these tests are missing, add the smallest regression tests. Do not modify angular implementation unless tests reveal a real failure.

## 6. Phase 4 convergence metadata boundary

Do not redo T7k, but check status after T7k:

- T8c/T7k should ensure convergence history is saved at run time for convergence-enabled Phase 4 results.
- Plotting must still be read-only.
- If no-convergence smoke configs remain allowed, they must not be represented as benchmark-quality outputs.

Allowed modifications:

- `tests/unit/*`
- `tests/physics/*`
- `docs/validation_plan.md`
- `docs/phase3_closeout.md` only for minor review fixes
- `status.md`

Principally avoid modifying:

- `src/schwgw/scattering/*`
- `src/schwgw/numerics/*`
- `src/schwgw/angular/*`

Only do tiny fixes if they are obvious review/test wiring issues. If implementation or convention changes are needed, stop and return to T6/T4/T1/T0.

Forbidden modifications:

- Do not reopen Q014.
- Do not change Route B.
- Do not change frozen conventions.
- Do not change numerical thresholds.
- Do not add plotting code.
- Do not generate R60_K2/R60_K4.
- Do not implement transmission factor.

Stop conditions:

- Production path can still feed raw strict `Psi0_NP/Psi4_NP` into packaged extraction.
- Type hardening changes validated Phase 3 numerical outputs.
- Q015 metadata hides a real radial failure.
- High-`ell` Wigner-D permanent tests are absent and cannot be added without changing convention.
- T8c/T7k convergence metadata contradicts `docs/numerics.md`.

Must run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_polarization_extraction.py tests/unit/test_weyl_modes.py tests/unit/test_wigner.py tests/unit/test_spin_weighted_harmonics.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_phase3_validation.py tests/physics/test_partial_wave_observables.py tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Completion update in `status.md`:

- changed files
- commands run
- test results
- closeout document review result
- strict/package type-boundary result
- Q015 metadata review result or deferred status
- Q016 permanent regression result
- Phase 4 convergence-metadata boundary result
- open issues
- next action: if all pass, proceed to T8d Li Fig.3/Fig.4-lite saved benchmark grid; otherwise return to the responsible thread
