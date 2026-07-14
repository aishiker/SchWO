# Phase 5 T10e Prompt: Li-Hou-Zhao Fig.4/Fig.5/Fig.6 Reproduction Planning

你现在是 `T10：文献与数值方法支援` 线程，slice 名称为 `T10e`。

T8x 已生成 R60_K2 angular production NPZ，T7as 已独立接受该 NPZ。你的任务不是运行 solver，也不是画图，
而是把 Li-Hou-Zhao Fig.4 exact angular curves 与 Fig.5/Fig.6 Table-I point-frequency scan 的最小可复现
artifact/schema/plotting 计划写清楚，防止 T8 后续把数据、图像、Kirchhoff baseline、asymptotic comparison 混在一起。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_r60_k2_angular_production_readiness.md`
8. `docs/phase4_production_closeout.md`
9. `docs/phase5_m5_four_frequency_closeout.md`
10. `references/manifest.md`
11. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
12. `references/notes/q014_curved_polarization_bridge.md`
13. `references/notes/q018_spin2_tail_bound.md`
14. `configs/r60_k2_q018_angular_production_first_pass.yaml`
15. Metadata from:
    `runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz`

按项目规则，先检查已安装 plugin/skill。使用适合本任务的文献/计划 skill；如果使用 PDF 工具，只允许读本地
`references/papers/` 文件，不上传任何私有文件。本 slice 不需要 web lookup，除非发现本地 notes 与 PDF 明显冲突。

## 2. 严格范围

允许：

- 读取本地 docs、notes、configs、accepted NPZ metadata；
- 必要时读取 `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf` 的 caption/Table I/相关段落；
- 新增：
  `references/notes/t10e_fig4_fig5_reproduction_plan.md`；
- 更新 `status.md`。

禁止：

- 不运行 solver；
- 不生成新的 NPZ/HDF5/PNG/PDF/fixture；
- 不修改 `src/`、`tests/`、configs、physics convention、thresholds、`lmax` policy 或 Q018 policy；
- 不把 R60_K2 的 GREEN 扩张为 R60_K4、`kM=4`、arbitrary incident direction、larger-domain 或 all-frequency
  readiness；
- 不实现 Kirchhoff Eq. (47)、Appendix D/E asymptotic comparison、phase-shift extraction 或 apparent modes。

## 3. 必须回答的问题

在 `references/notes/t10e_fig4_fig5_reproduction_plan.md` 中给出以下内容。

### A. Fig.4 exact angular curves

1. 明确当前已经可以从 accepted R60_K2 NPZ 得到什么：
   - `r=60M`;
   - `kM=2`;
   - finite-radius production `h_plus/h_cross`;
   - angular grid `theta.shape=(65,)`, `phi.shape=(64,)`;
   - selected final-pair convergence, not full-grid convergence。
2. 明确当前还不能声称什么：
   - all-frequency Fig.4 is not available until `kM=0.5,1.0,1.5` angular artifacts are generated and reviewed;
   - conventional asymptotic comparison curves are not available without a separate Appendix D/E diagnostic path;
   - `kM=4` is not authorized.
3. 给出 read-only Fig.4 exact-curve plotting policy for the accepted `kM=2` data:
   - state whether curves should be extracted at a fixed `phi`, averaged over `phi`, or plotted as a small set of
     representative `phi` cuts;
   - if the paper caption/text does not justify a `phi` average, say so and choose the least misleading policy;
   - plot quantities must be labeled as exact finite-radius `|h_plus|` and `|h_cross|`, not strict `Psi4` and not
     asymptotic amplitudes.
4. Define the minimal output names for a future T8 read-only plot slice, for example under:
   `runs/phase5/q018_r60_k2_angular_production_first_pass/plots/`.
5. Define the metadata sidecar fields needed for the plot:
   - source NPZ path and SHA-256;
   - case id;
   - plotted field names;
   - curve extraction policy;
   - theta/phi selection;
   - convergence caveat;
   - Q018 oracle provenance summary;
   - no solver rerun flag.

### B. Fig.4 all-frequency extension

Give a separate plan for later exact finite-radius angular datasets at `r=60M`, `kM=0.5,1.0,1.5`.

For each frequency, list:

- proposed case id;
- expected output path;
- initial `lmax`/final-pair strategy based on the adaptive policy in `docs/numerics.md`;
- whether Q018 oracle is expected to be needed;
- T4/T7 checks required before T8 production;
- stop conditions if convergence or radial coverage fails.

Do not authorize these runs from T10e. This is a plan only.

### C. Fig.5/Fig.6 Table-I point-frequency scans

Use the Table I point set from T10d:

- near-axis: `(x,z)=(0,30),(1,30),(2,30),(3,30)M`;
- far-axis: `(x,z)=(10,30),(15,30),(20,30),(25,30)M`.

Define the minimal scan artifact schema for exact project finite-radius ratios:

- point coordinates and derived `r,theta,phi`;
- frequency grid;
- complex `F_plus`, `F_cross`;
- `abs(F_plus)`, `abs(F_cross)`;
- unwrapped phase policy for `arg(F_plus)`, `arg(F_cross)`;
- source denominator/baseline metadata from the accepted M5 normalization;
- masks/NaN policy;
- solver/convergence metadata per point/frequency;
- source-code/config SHA metadata.

Also separate three scopes:

1. currently available four-frequency archive scope: `kM=0.5,1.0,1.5,2.0` only;
2. dense `Mk` scan up to `4.0`, which requires a separate `kM=4` gate;
3. Kirchhoff Eq. (47) baseline, which requires T1/T10 convention freeze before any implementation.

### D. Thread handoff plan

End the note with a concrete staged handoff:

1. T7at review of this plan;
2. if T7at GREEN, T8y read-only Fig.4 exact `kM=2` plot from the accepted NPZ only;
3. T7au review of the T8y plot sidecars and source-boundary checks;
4. only after that, T0 decides whether to open lower-frequency Fig.4 data generation or Fig.5/Fig.6 scan planning.

## 4. Decision Labels

Use exactly one:

- **GREEN / PLAN READY FOR T7at REVIEW**:
  the note cleanly separates accepted `kM=2` plotting, all-frequency Fig.4 data generation, Fig.5/Fig.6 scans,
  Kirchhoff baseline, asymptotic comparison, and gated `kM=4` work.
- **YELLOW / PLAN NEEDS T1 OR T4 INPUT**:
  the note is useful but cannot define a safe T8y plotting policy or scan schema without a convention/radial decision.
- **RED / DO NOT PROCEED**:
  local sources conflict in a way that would make the next plot misleading, or the accepted NPZ metadata is missing/failing.

## 5. status.md Update

Update `status.md` with:

- changed files;
- files read;
- plugin/skill check;
- whether the accepted R60_K2 NPZ metadata was found;
- decision label;
- commands run;
- tests run or explicitly not run with reason;
- open issues;
- exact next action:

```text
你现在是 T7at。请读取并严格执行 docs/prompts/phase5_t7at_fig4_fig5_plan_review.md。
```

