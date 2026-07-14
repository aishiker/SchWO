# Phase 5 T6m Prompt: M5 Pointwise Amplification API

你现在是 `T6：metric/Weyl/polarization/observable extraction` 线程，slice 名称为
`T6m`。

## 0. 任务定位

T1/M5a 已冻结 Q005，T7aa 已独立复核通过。现在可以实现 M5 的核心
pointwise wave-optics amplification API，但本 slice 只做纯计算层：

- 不改 CLI；
- 不改 plotting；
- 不生成 benchmark artifacts；
- 不实现 radial horizon transmission / absorption。

M5 production `F` 是有限半径逐点比值 `h_lensed / h_unlensed`。它不是
`A_in/A_out`、phase shift、horizon flux 或 absorption coefficient。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/m5_transmission_normalization.md`
5. `docs/equation_map.md`
6. `docs/validation_plan.md`
7. `docs/phase3_closeout.md`
8. `docs/phase4_production_closeout.md`
9. `references/notes/q014_curved_polarization_bridge.md`
10. `references/notes/q012_high_ell_radial_methods.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Implementation Scope

Create the core API in:

```text
src/schwgw/scattering/transmission.py
```

Export it from:

```text
src/schwgw/scattering/__init__.py
```

Add tests in:

```text
tests/unit/test_transmission.py
```

Use test-driven development: write failing tests first, then implement.

## 3. Required API

Implement a small, typed/vectorized API. Suggested names:

```python
@dataclass(frozen=True)
class PointwiseAmplificationResult:
    F_plus_complex: np.ndarray
    F_cross_complex: np.ndarray
    amplification_plus: np.ndarray
    amplification_cross: np.ndarray
    intensity_plus_ratio: np.ndarray
    intensity_cross_ratio: np.ndarray
    F_pol_norm: np.ndarray
    I_pol_ratio: np.ndarray
    valid_ratio_plus_mask: np.ndarray
    valid_ratio_cross_mask: np.ndarray
    valid_ratio_norm_mask: np.ndarray
    metadata: dict[str, object]
```

Core function:

```python
def compute_pointwise_amplification(
    *,
    h_plus_lensed: np.ndarray,
    h_cross_lensed: np.ndarray,
    h_plus_unlensed: np.ndarray,
    h_cross_unlensed: np.ndarray,
    valid_lensed_mask: np.ndarray | None,
    A_plus: complex,
    A_cross: complex,
    denominator_atol_factor: float = 1.0e-14,
    denominator_rtol_factor: float = 1.0e-12,
) -> PointwiseAmplificationResult:
    ...
```

Optional scalar helper, if useful for T8p:

```python
def flat_no_lens_baseline_at_point(
    *,
    k: float,
    r: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    lmax: int = 2,
) -> tuple[complex, complex]:
    ...
```

The helper must call `compute_flat_no_lens_polarization(...)` or exactly match
its documented contract. It must not call `solve_radial_mode`, construct a
Schwarzschild background, or use tiny-`M`.

## 4. Required Behavior

Implement exactly the M5a/T1 policy:

- `F_plus_complex = h_plus_lensed / h_plus_unlensed` on valid plus mask.
- `F_cross_complex = h_cross_lensed / h_cross_unlensed` on valid cross mask.
- Invalid complex ratios are `nan + 1j*nan`.
- Component masks are independent.
- `F_pol_norm = H_norm_lensed / H_norm_unlensed`.
- `I_pol_ratio = H_norm_lensed**2 / H_norm_unlensed**2`.
- Invalid scalar ratios are real `nan`.
- Do not clip, floor, zero-fill, or one-fill invalid denominators.
- Save denominator thresholds and convention fields in `metadata`.
- Reject shape mismatches clearly.
- Reject non-positive denominator factors clearly.
- If `A_plus=A_cross=0`, all masks should be false and all ratios NaN; this
  is a diagnostic zero-input case, not a physical amplification map.

Metadata must include at least:

```text
normalization.kind = "pointwise_wave_optics_amplification"
normalization.version = "m5a_t1_v1"
normalization.baseline = "flat_no_lens"
normalization.baseline_api = "compute_flat_no_lens_polarization"
normalization.fourier = "exp(-i k t)"
normalization.polarization_bridge = "Route B incident-frame electric tidal packaged scalars"
normalization.no_schwarzschild_horizon_boundary_in_baseline = true
normalization.no_tiny_M_baseline = true
normalization.excludes_radial_horizon_transmission = true
normalization.denominator_policy = "independent masks, NaN where denominator mask is false"
normalization.denominator_atol_factor = ...
normalization.denominator_rtol_factor = ...
normalization.eps_plus = ...
normalization.eps_cross = ...
normalization.eps_norm = ...
```

## 5. Required Tests

At minimum, add unit tests for:

1. No-lens identity:
   - lensed arrays equal unlensed arrays;
   - valid ratios equal `1+0j`;
   - `F_pol_norm` and `I_pol_ratio` equal `1`.
2. Complex ratio phase:
   - use nontrivial complex lensed/unlensed values;
   - verify exact complex division, absolute ratio, and intensity ratio.
3. Pure plus input:
   - `A_cross=0`;
   - cross denominator mask false and `F_cross_complex` complex NaN;
   - plus ratio remains finite.
4. Pure cross input:
   - symmetric to pure plus.
5. Combined norm:
   - finite if at least one polarization denominator is finite;
   - NaN only where norm mask is false.
6. Shape mismatch and invalid denominator-factor errors.
7. Baseline helper guard:
   - monkeypatch/inspect enough to prove the helper uses
     `compute_flat_no_lens_polarization` or equivalent direct flat contract;
   - prove it does not call `solve_radial_mode`.
8. Terminology guard:
   - metadata includes `excludes_radial_horizon_transmission=True`;
   - no public field is named bare `transmission`.

## 6. Hard Limits

- Do not modify frozen conventions.
- Do not reopen Q014 or Q005.
- Do not alter `compute_polarization(...)`.
- Do not modify radial solver behavior or thresholds.
- Do not implement saved-result schema, CLI, plotting, or benchmark configs in
  this slice.
- Do not add large dependencies.
- Do not generate `/tmp` artifacts except ephemeral test temp files.

## 7. Verification Commands

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_transmission.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "radial_horizon_transmission|radial_absorption|A_in|A_out|solve_radial_mode" src/schwgw/scattering/transmission.py tests/unit/test_transmission.py
```

The `rg` command may find only negative/guard references in tests or metadata;
it must not reveal a production dependency on radial matching.

## 8. Stop Conditions

Stop and update `status.md` if:

- denominator-zero behavior conflicts with `docs/m5_transmission_normalization.md`;
- implementing the helper requires changing Route B or flat/no-lens APIs;
- tests require radial solver calls for the baseline;
- full pytest fails.

## 9. Handoff

If passed, update `status.md` and recommend:

```text
T8p should implement saved-output schema/CLI for M5 amplification using the T6m API.
```
