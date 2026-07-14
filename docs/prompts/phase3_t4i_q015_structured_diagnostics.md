# Phase 3 T4i Prompt: Q015 Structured Diagnostic Metadata

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4i`。

阶段定位：

Q015 已经 triage 为 non-blocking low-`k` transition-regime radial diagnostic warning。本 slice 不重新打开 Q014，不改变 radial solver physics，不放宽阈值。目标是把 Q015 从聊天/status 里的文字结论固化为结构化 diagnostic metadata，供后续 fixtures、Phase 4 result metadata 和 benchmark reports 记录。

启动建议：

- 建议等 T7k 完成后启动，避免与 T7k 对 T8c convergence metadata 的复核同时改动 diagnostics schema。
- 如果必须并行运行，不要修改 `src/schwgw/io/*`、`src/schwgw/viz/*`、`configs/*` 或 T8c/T7k tests；只做 radial diagnostics 内部结构和 targeted tests。

先读：

1. `project.md`
2. `status.md`
3. `docs/numerics.md`
4. `docs/validation_plan.md`
5. `docs/equation_map.md`
6. `references/notes/q012_high_ell_radial_methods.md`
7. `src/schwgw/numerics/radial_solver.py`
8. `src/schwgw/numerics/__init__.py`
9. `src/schwgw/scattering/partial_wave.py`
10. `tests/physics/test_radial_solver.py`
11. `tests/physics/test_phase3_validation.py`

硬性原则：

- Do not reopen Q014.
- Do not change Route B.
- Do not alter radial equations, boundary conditions, matching formulas, or numerical thresholds.
- Do not hide failures by truncating `ell` or relaxing residual thresholds.
- Do not add plotting code.

目标：

Convert Q015 into structured diagnostic metadata rather than a blocking issue.

必须实现：

## 1. Structured radial warning type

Add a small structured warning representation, preferably in `src/schwgw/numerics/radial_solver.py` or a focused diagnostics module if cleaner.

Suggested dataclass:

```python
@dataclass(frozen=True)
class RadialDiagnosticWarning:
    code: str
    severity: str
    message: str
    sector: str
    ell: int
    k: float
    solver: str
    barrier_action: float
    raw_wronskian_residual: float
    effective_wronskian_residual: float
    flux_residual: float
    boundary_residual: float
    expected_flux_scale: float
    match_condition_number: float
```

Use a code like:

```text
transition_raw_wronskian_warning
```

Do not use a boolean-only warning; the metadata must carry enough numerical context to diagnose the mode later.

## 2. Extend `RadialDiagnostics`

Add fields without breaking existing users:

- `raw_wronskian_residual`
- `expected_flux_scale`
- `warnings` as a tuple of `RadialDiagnosticWarning` or JSON-safe dictionaries

For outward shooting, set:

- `raw_wronskian_residual = wronskian_residual`
- `expected_flux_scale = 0.0` or a documented value if available
- `warnings = ()`

For BVP branch:

- store both raw and effective Wronskian residual.
- store `expected_flux_scale`.
- emit `transition_raw_wronskian_warning` only when:
  - raw Wronskian residual is above the first-pass target,
  - boundary residual remains healthy,
  - flux/collocation diagnostic remains healthy,
  - solution is finite,
  - condition number is not pathological,
  - mode lies in the transition regime near the BVP threshold.

Use the existing Q015 evidence as a guide, but do not hard-code only `k=0.2, ell=3`.

## 3. Metadata plumbing

If touching `src/schwgw/scattering/partial_wave.py`, keep it minimal:

- Existing scalar diagnostics such as `max_wronskian_residual` must remain numeric.
- Add separate structured metadata only if it does not break `PolarizationResult.diagnostics` consumers.
- If `PolarizationResult.diagnostics` is still numeric-only, add a helper such as `collect_radial_diagnostic_warnings(radial_cache)` and document how T8/fixture generation can call it later.

Do not modify `src/schwgw/io/results.py` in this slice unless T7k is complete and the change is strictly required.

## 4. Tests

Add targeted tests in `tests/physics/test_radial_solver.py`.

Required coverage:

1. Existing high-`ell` stabilized tests still pass without threshold relaxation.
2. A Q015-like transition mode records structured warning metadata if the raw Wronskian residual is high but boundary/collocation/condition diagnostics are healthy.
3. Healthy high-barrier modes do not produce warning metadata.
4. Warning metadata is JSON-safe or has a clear `to_metadata()` method returning JSON-safe fields.

If the exact Q015 mode is too slow for fast tests:

- Use a focused physics test with the existing Q015 parameters but keep it marked `@pytest.mark.physics`.
- Do not fake the warning in production code just to make a fast unit test pass.

Allowed modifications:

- `src/schwgw/numerics/radial_solver.py`
- `src/schwgw/numerics/__init__.py`
- `src/schwgw/scattering/partial_wave.py` only for diagnostic collection, not physics formulas
- `tests/physics/test_radial_solver.py`
- `tests/unit/*` only if a pure metadata helper needs unit coverage
- `docs/numerics.md`
- `docs/validation_plan.md`
- `docs/equation_map.md` only if new public diagnostic helper is added
- `status.md`

Forbidden modifications:

- Do not modify T6 production polarization bridge.
- Do not modify angular/Wigner-D code.
- Do not modify plotting code.
- Do not generate plots or large fixtures.
- Do not change residual thresholds.
- Do not mark Q015 as resolved unless a separate T7 review verifies it.

Stop conditions:

- The Q015-like mode shows large boundary residual, non-finite radial data, condition number pathology, or field-convergence failure.
- Structured metadata requires changing result-file schema while T7k is still reviewing T8c.
- Implementing warning classification requires new physics assumptions not documented in `docs/numerics.md`.
- Any change would make Q012 high-`ell` tests fail.

Must run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_phase3_validation.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Completion update in `status.md`:

- changed files
- commands run
- test results
- structured warning schema
- Q015 warning classification behavior
- confirmation thresholds were not relaxed
- open issues
- next action: T7l hardening review
