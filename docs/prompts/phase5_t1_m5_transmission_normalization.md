# Phase 5 T1 Prompt: M5 Transmission-Normalization Design

你现在是 `T1：文献与物理约定` 线程，slice 名称为 `M5a/T1`。

## 0. 任务定位

Phase 4 的 finite-radius wave-field production first pass 已经 closeout 并
归档。现在进入 M5 前置设计：冻结 Q005，也就是 transmission / amplification
factor 的 unlensed normalization。此 slice 只做规格冻结和文档，不写 solver、
不写 plotting、不生成新数值 artifacts。

核心风险：项目里可能出现两个不同含义的 "transmission"：

1. wave-optics lensing amplification / transmission factor:
   `F = h_lensed / h_unlensed`，这是 M5 图像和用户可见输出关心的量；
2. radial horizon transmission / absorption coefficient:
   由 RW/Zerilli mode 的 flux、`A_in/A_out`、horizon amplitude 等定义，
   这是径向诊断或未来吸收截面关心的量。

本 slice 必须明确命名和边界，防止两者混用。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/phase3_closeout.md`
8. `docs/phase4_production_closeout.md`
9. `references/manifest.md`
10. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
11. `references/notes/q014_curved_polarization_bridge.md`
12. `references/notes/q012_high_ell_radial_methods.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`. If local notes are insufficient, stop and request a T10 literature
slice instead of guessing.

## 2. Goals

1. Create `docs/m5_transmission_normalization.md`.
2. Freeze Q005 terminology:
   - choose the production name for pointwise wave-optics factor, e.g.
     `F_plus`, `F_cross`, and optionally intensity/amplitude summaries;
   - explicitly reserve or rename radial horizon transmission/absorption so it
     cannot be confused with pointwise lensing amplification.
3. Freeze unlensed baseline convention:
   - same Fourier convention `exp(-ikt)`;
   - same `A_plus`, `A_cross`, `k`, observer coordinates, tetrad/polarization
     convention, and Route B packaged-polarization bridge;
   - no Schwarzschild horizon boundary in the unlensed baseline;
   - baseline should be the existing flat/no-lens production-compatible
     polarization path, not a tiny-`M` Schwarzschild solve.
4. Define denominator/zero policy:
   - what to do when `|h_unlensed|` is near zero;
   - what mask/metadata must be saved;
   - whether separate ratios for `h_plus` and `h_cross` are allowed to be NaN
     independently.
5. Define at least one scalar summary suitable for plots without hiding zeros:
   - e.g. componentwise complex ratio, amplitude ratio, intensity ratio, or
     combined polarization norm ratio;
   - state which are production outputs and which are diagnostics.
6. Update:
   - `docs/physics_spec.md` Sec. 10.3;
   - `docs/equation_map.md` with planned future modules and formulas;
   - `docs/validation_plan.md` with M5 validation tests;
   - `status.md` with changed files, commands, open issues, and next action.

## 3. Required Design Decisions

The new design document must answer these questions explicitly:

1. Is `F_plus = h_plus_lensed / h_plus_unlensed` a complex amplitude ratio,
   an absolute-value ratio, or both?
2. Is `F_cross` defined analogously, and how are cross-polarization zeros
   handled?
3. Is there a combined polarization norm factor, for example
   `sqrt((|h_plus|^2+|h_cross|^2)_lensed /
         (|h_plus|^2+|h_cross|^2)_unlensed)`?
4. What exactly is `h_unlensed` for a plane wave in the same observer/tetrad
   convention?
5. Does the production baseline use `compute_flat_no_lens_polarization(...)`
   or another named path? If another path is needed, specify the required
   interface but do not implement it.
6. Which metadata fields must be saved with M5 outputs?
7. Which future tests are mandatory before any M5 plot can be accepted?

## 4. Hard Limits

- Do not modify `src/`.
- Do not add or regenerate numerical fixtures.
- Do not run expensive grids.
- Do not implement CLI or plotting.
- Do not change frozen Fourier, harmonic, tetrad, RW/Zerilli, Route B, or
  polarization conventions.
- Do not reopen Q014.
- Do not change radial solver thresholds, high-`ell` Q018 policy, or accepted
  M4 artifacts.
- Do not use asymptotic scattering amplitudes as the production finite-radius
  observable unless you explicitly mark them as diagnostics only.

## 5. Verification

Run:

```bash
rg -n "transmission|Transmission|Q005|unlensed|amplification|F_plus|F_cross" docs references/notes status.md
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If you only change documentation, full pytest is still required because the
repository uses docs/status as coordination state.

## 6. Pass Conditions

Pass only if:

- `docs/m5_transmission_normalization.md` exists and cleanly separates
  pointwise wave-optics amplification from radial horizon transmission;
- `docs/physics_spec.md` Sec. 10.3 no longer says normalization is undefined
  without a concrete next action;
- `docs/equation_map.md` maps future implementation modules to the frozen
  formulas and caveats;
- `docs/validation_plan.md` lists concrete M5 validation tests;
- no `src/` files were modified;
- full pytest passes;
- `status.md` recommends the next slice as T7 independent review, not direct
  T6/T8 implementation.

## 7. Stop Conditions

Stop and update `status.md` if:

- local notes/literature are insufficient to distinguish pointwise
  amplification from radial absorption;
- the proposed normalization would require changing frozen Route B or
  polarization conventions;
- the flat/no-lens baseline cannot be specified without new derivation;
- tests fail.

## 8. Handoff

If passed, next prompt:

```text
你现在是 T7aa。请读取并严格执行 docs/prompts/phase5_t7aa_m5_normalization_review.md。
```
