# Phase 5 T7at Prompt: Review Fig.4/Fig.5/Fig.6 Reproduction Plan

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7at`。

只在 T10e 完成 `references/notes/t10e_fig4_fig5_reproduction_plan.md` 后运行。你的任务是独立复核该计划：
它是否把 accepted R60_K2 `kM=2` angular plot、Fig.4 all-frequency extension、Fig.5/Fig.6 point-frequency
scan、Kirchhoff baseline、Appendix D/E asymptotic comparison、`kM=4` gate 清楚分开。

本 review 通过只允许 T0 后续调度一个 read-only T8y plot slice，从已经接受的 R60_K2 NPZ 画 `kM=2`
exact finite-radius angular curves。不要授权新的 solver runs、fixtures、R60_K4、`kM=4`、larger-domain 或
arbitrary-direction artifacts。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_r60_k2_angular_production_readiness.md`
8. `docs/phase5_m5_four_frequency_closeout.md`
9. `references/manifest.md`
10. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
11. `references/notes/t10e_fig4_fig5_reproduction_plan.md`
12. `docs/prompts/phase5_t10e_fig4_fig5_reproduction_planning.md`
13. Metadata from:
    `runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和 verification-before-completion。
本 review 不需要外部文献检索，除非 T10e 明确报告本地 notes/PDF 冲突。

## 2. Scope Checks

Verify:

- T10e did not modify `src/`, `tests/`, configs, thresholds, physics conventions, Q018 policy, or `lmax` policy;
- T10e did not generate new NPZ/HDF5/PNG/PDF/fixtures;
- T10e updated only allowed documentation/status files;
- the accepted R60_K2 angular production NPZ still exists and has the expected case id;
- the plan does not treat selected-subset convergence as full-grid convergence;
- the plan does not treat `kM=2` as all-frequency Fig.4 readiness;
- the plan does not mix Route B packaged `h_plus/h_cross` with strict `Psi4`;
- the plan does not implement or silently authorize Kirchhoff Eq. (47), Appendix D/E asymptotic curves, apparent modes,
  R60_K4, `kM=4`, larger-domain, or arbitrary incident direction;
- the proposed T8y output is read-only over the accepted NPZ and records source SHA/metadata/provenance.

## 3. Plan Quality Checks

Review `references/notes/t10e_fig4_fig5_reproduction_plan.md` for:

1. Fig.4 `kM=2` exact finite-radius plotting policy:
   - field labels are `|h_plus|` and `|h_cross|`;
   - extraction over `phi` is justified or explicitly marked as a plotting convention;
   - convergence and Q018 caveats are visible in metadata, not hidden in prose only.
2. Fig.4 all-frequency extension:
   - lower-frequency artifacts are planned as separate T8/T7 slices;
   - adaptive `lmax` policy is respected;
   - Q018 expectations are stated without overclaiming.
3. Fig.5/Fig.6 scan schema:
   - Table-I points are listed exactly;
   - complex ratios and phase-unwrapping metadata are specified;
   - dense `Mk` scan to `4.0` and Kirchhoff baseline are explicitly separate future gates.
4. Thread handoff:
   - next action is T8y read-only plotting only if this review is GREEN;
   - no solver run is authorized by implication.

## 4. Optional Metadata Inspection

You may inspect the accepted NPZ metadata to confirm case id, shapes, source fields, and SHA. Do not recompute
polarization and do not run solver.

## 5. Validation Commands

Run at minimum:

```bash
test -f references/notes/t10e_fig4_fig5_reproduction_plan.md
test -f runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz
find runs/phase5/q018_r60_k2_angular_production_first_pass -maxdepth 3 -type f -print
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' \) -print
```

Run targeted/full pytest only if T10e changed code/tests/configs despite the scope. If no code/config changed, record that
pytest was not run because this was a documentation-only review.

## 6. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR FIG.4/FIG.5 PLAN ONLY**:
  T10e plan is scoped and auditable. T0 may schedule T8y read-only Fig.4 exact `kM=2` angular plotting from the
  accepted R60_K2 NPZ only.
- **ACCEPT YELLOW / PLAN REVISION NEEDED**:
  plan is broadly useful but extraction policy, schema, or gate separation needs a T10e revision before T8y.
- **REJECT RED**:
  plan authorizes forbidden solver runs/artifacts, mixes strict/package conventions, hides convergence caveats, or
  changes code/configs/conventions.

## 7. status.md Update

Update `status.md` with:

- changed files;
- files read;
- plugin/skill check;
- scope checks;
- plan-quality checks;
- commands and results;
- decision label;
- open issues;
- exact next action recommendation.

If GREEN, recommend that T0 schedule a separate `T8y` read-only plotting prompt. Do not write that T8y prompt from T7at.

