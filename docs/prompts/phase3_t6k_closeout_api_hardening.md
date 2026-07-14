# Phase 3 T6k Prompt: Closeout and API Type Hardening

你现在是 `T6：重构、Weyl、极化` 线程，slice 名称为 `T6k`。

阶段定位：

Phase 3 物理结论保持关闭状态。本 slice 是防返工加固，不是重新打开 Q014，不是改变 Route B，也不是调整任何 convention。目标是把已经通过 T7f 的 strict-NP / packaged-scalar 分离写成文档和 API 边界，降低后续 T8/T5/M5 工作中误用 `Psi0/Psi4` 的风险。

并行性：

- 本 slice 可以与 T7k 并行运行，因为它不应修改 `src/schwgw/io/*`、`src/schwgw/viz/*`、`configs/*` 或 Phase 4 plotting/convergence tests。
- 如果 T7k 同时更新 `status.md`，完成时请先重读最新 `status.md` 再追加自己的记录，避免覆盖 T7k 结果。

先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `references/notes/q014_curved_polarization_bridge.md`
8. `references/notes/q014_weyl_transform_bridge.md`
9. `references/notes/q013_flat_nolens_polarization_convention.md`
10. `src/schwgw/scattering/observables.py`
11. `src/schwgw/scattering/weyl.py`
12. `src/schwgw/scattering/partial_wave.py`
13. `tests/unit/test_polarization_extraction.py`
14. `tests/unit/test_weyl_modes.py`

硬性原则：

- Do not reopen Q014.
- Do not change Route B.
- Do not modify frozen Fourier, harmonic, Wigner-D, tetrad, RW/Zerilli, master-variable, or polarization conventions.
- Do not alter numerical thresholds.
- Do not add plotting code.
- Do not add transmission-factor logic.

目标：

1. 新增 `docs/phase3_closeout.md`，清楚总结 Phase 3 closeout。
2. 用 API/type hardening 防止 strict NP scalars、electric tidal components、packaged polarization scalars 被静默互换。
3. 加 regression tests，证明 production `compute_polarization(...)` 不会把 raw strict `Psi0_NP/Psi4_NP` 直接喂给 packaged extraction。

必须实现：

## 1. `docs/phase3_closeout.md`

创建文档，至少包含以下章节：

- Scope and status
  - Phase 3 is physically closed.
  - Q014 is resolved by T7f independent validation.
  - Q015 remains a separate non-blocking radial diagnostic warning.
  - Q016 high-`ell` Wigner-D overflow is resolved and revalidated.
- Convention boundaries
  - strict NP scalars are tetrad contractions of the Weyl tensor.
  - packaged polarization scalars are project positive-frequency recovery variables.
  - electric tidal components define Route B production packaging.
- Route B production invariant
  - production path: strict NP full quintuple -> incident-frame electric tidal projection / packaged scalars -> polarization extraction.
  - raw strict `Psi0_NP/Psi4_NP` must not be passed directly to packaged extraction.
- Forbidden shortcuts
  - no same-positive-`k`, same-`m` literal conjugation from Li-Hou-Zhao Eq. (35g)-(35h).
  - no strict two-scalar shortcut for curved finite-radius production.
  - no promoting flat type-N/helicity diagnostic to curved production.
  - no plotting-side physics formulas.
  - no threshold relaxation to hide failures.
- Validation evidence
  - Route B active.
  - flat diagnostic genuine.
  - T7f final adjacent-pair convergence values:
    - `k=0.5`, final `24->28`, max change `4.43e-8`.
    - `k=0.2`, final `18->22`, max change `8.61e-11`.
    - near-axis final-pair passed.
- Open issues
  - Q015 structured metadata remains a separate diagnostic hardening task unless already completed by another thread.
  - transmission normalization Q005 remains future M5 scope.

## 2. API/type hardening

Add explicit types so the code cannot silently treat these objects as the same:

- `StrictNPScalars`
  - full strict NP quintuple: `psi0`, `psi1`, `psi2`, `psi3`, `psi4`.
  - optional `frame` string, at least `"incident"` / `"kinnersley"` if useful.
  - constructor/helper from mapping may be allowed, but missing labels must raise clear errors.

- `ElectricTidalComponents`
  - at minimum `E_xx`, `E_xy`.
  - document that Route B finite-radius production uses these components or the equivalent full-Weyl projection.

- `PackagedPolarizationScalars`
  - packaged positive-frequency pair: `psi0_pack`, `psi4_pack`.
  - must be a distinct dataclass from `StrictNPScalars`.
  - do not make it a plain alias for `dict[str, complex]`.

Implementation location:

- Prefer `src/schwgw/scattering/observables.py` for observable-facing packaged/electric types.
- If `StrictNPScalars` fits better in `src/schwgw/scattering/weyl.py`, that is acceptable, but keep imports acyclic.

Function API requirements:

- Add `polarization_from_packaged_scalars(k, packaged_scalars)` and use it in production.
- Add `polarization_acceleration_from_packaged_scalars(packaged_scalars)` or equivalent if needed.
- Keep legacy `polarization_from_weyl(k, psi0_hat, psi4_hat)` only as a backward-compatible packaged-scalar wrapper; update its docstring to say it consumes packaged scalars, not raw strict NP scalars.
- Update `compute_packaged_polarization_scalars(...)` so its return type is typed. If preserving a mapping-like compatibility helper is necessary, name it explicitly, e.g. `packaged_scalars_to_mapping(...)`.
- Update `compute_polarization(...)` so production flow is visibly typed:

```text
assembled strict NP mapping
  -> transform_strict_np_weyl_to_incident_tetrad(...)
  -> StrictNPScalars.from_mapping(...)
  -> compute_packaged_polarization_scalars(...)
  -> polarization_from_packaged_scalars(...)
```

Do not change the numerical formulas or signs.

## 3. Regression tests

Update or add tests in `tests/unit/test_polarization_extraction.py` and, if needed, `tests/unit/test_weyl_modes.py`.

Required tests:

1. `PackagedPolarizationScalars` and `StrictNPScalars` are distinct types and not silently interchangeable.
   - Passing `StrictNPScalars` into `polarization_from_packaged_scalars(...)` must raise `TypeError` or otherwise fail clearly.

2. `compute_packaged_polarization_scalars(...)` returns a typed packaged object.
   - It must still produce the same numeric packaged values as before.

3. Production `compute_polarization(...)` never uses raw strict two-scalar shortcut.
   - Patch `transform_strict_np_weyl_to_incident_tetrad(...)` to return a strict quintuple where raw `Psi0/Psi4` differ from the expected packaged pair.
   - Patch `polarization_from_packaged_scalars(...)` and assert it receives a `PackagedPolarizationScalars`.
   - Patch legacy `polarization_from_weyl(...)` to raise if called; production should not call it.
   - Assert returned `PolarizationResult.psi0_hat/psi4_hat` equal packaged values, not raw strict values.

4. Existing flat no-lens and linearity tests still pass.

Allowed modifications:

- `docs/phase3_closeout.md`
- `src/schwgw/scattering/observables.py`
- `src/schwgw/scattering/weyl.py`
- `src/schwgw/scattering/partial_wave.py`
- `src/schwgw/scattering/__init__.py`
- `tests/unit/test_polarization_extraction.py`
- `tests/unit/test_weyl_modes.py`
- `docs/equation_map.md` only if public API names change
- `docs/physics_spec.md` only to clarify type/API wording without changing convention
- `status.md`

Forbidden modifications:

- Do not modify `src/schwgw/io/*`.
- Do not modify `src/schwgw/viz/*`.
- Do not modify `configs/*`.
- Do not modify `src/schwgw/angular/*`.
- Do not modify `src/schwgw/numerics/*`.
- Do not modify `src/schwgw/perturbations/*`.
- Do not change thresholds or test tolerances to force a pass.
- Do not generate fixtures or plots.

Stop conditions:

- The change requires a new derivation of the finite-radius strict-NP to packaged bridge.
- The change would alter numerical outputs for existing validated Phase 3 tests.
- The change would force reopening Q014.
- Existing Route B tests fail unless convention or formulas are changed.
- Type hardening requires breaking T8a/T8b/T8c public result schemas.

Must run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_polarization_extraction.py tests/unit/test_weyl_modes.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_phase3_validation.py tests/physics/test_partial_wave_observables.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Completion update in `status.md`:

- changed files
- commands run
- test results
- whether `docs/phase3_closeout.md` was created
- type/API hardening summary
- confirmation Q014 remains closed and Route B unchanged
- open issues
- next action, usually T7l hardening review after T4i or after this slice if T4i is deferred
