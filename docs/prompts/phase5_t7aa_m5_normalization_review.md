# Phase 5 T7aa Prompt: M5 Transmission-Normalization Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7aa`。

## 0. 任务定位

T1/M5a 应已冻结 Q005 transmission / unlensed normalization。你的任务是独立
复核这个规格是否足够让后续 T6/T8 实现，且没有混淆 pointwise wave-optics
amplification 与 radial horizon transmission/absorption。

本 slice 只做 review、测试和状态更新；不写 solver、不写 plotting、不生成
数值 artifacts。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/phase3_closeout.md`
8. `docs/phase4_production_closeout.md`
9. `docs/m5_transmission_normalization.md`
10. `docs/prompts/phase5_t1_m5_transmission_normalization.md`
11. `references/manifest.md`
12. `references/notes/q014_curved_polarization_bridge.md`
13. `references/notes/q012_high_ell_radial_methods.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Review Checklist

Independently verify:

1. Q005 is either closed or clearly remains blocked with a precise missing
   derivation.
2. The production "transmission" output is named and defined unambiguously.
3. Radial horizon transmission/absorption is explicitly separated from
   pointwise wave-optics amplification.
4. The unlensed baseline is compatible with:
   - `exp(-ikt)`;
   - default `+z` incident direction;
   - existing `A_plus/A_cross`;
   - Route B packaged-polarization bridge;
   - no tiny-`M` Schwarzschild horizon solve.
5. Denominator-zero masking is concrete and testable.
6. Required metadata is concrete enough for future result files.
7. M5 validation tests in `docs/validation_plan.md` are concrete enough for T7
   to implement after T6/T8 code exists.
8. No frozen physics convention, radial threshold, Q018 policy, M4 artifact, or
   Route B decision was changed.
9. No `src/` files were modified in the T1/M5a design slice.

## 3. Verification Commands

Run:

```bash
rg -n "Q005|transmission|Transmission|unlensed|amplification|F_plus|F_cross|radial horizon|absorption" docs references/notes status.md
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If useful, run a lightweight import-only check of the existing flat/no-lens
public path, but do not compute new benchmark grids.

## 4. Pass Conditions

Pass only if:

- T1/M5a design gives enough information for the next implementation slice to
  write tests first;
- the review finds no convention drift or hidden dependency on asymptotic
  scattering formulas as production finite-radius output;
- full pytest passes;
- `status.md` records changed files, commands, test results, open issues, and
  next action.

If passed, recommend the next implementation slice as:

```text
T6m/T8p M5 transmission API and saved-output schema, followed by T7ab tests.
```

Do not write the T6/T8 implementation prompt unless T0 asks or the project
status already requires it.

## 5. Stop Conditions

Stop and update `status.md` if:

- Q005 remains ambiguous;
- T1/M5a mixes radial absorption with pointwise amplification;
- the unlensed baseline conflicts with Route B or Q014 closeout;
- denominator-zero policy is missing;
- tests fail.
