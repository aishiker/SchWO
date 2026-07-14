# Phase 5 New Thread Startup Prompts: T0-T10

Use this file when replacing old Codex threads with fresh ones.  The new thread
must not rely on chat history.  It must read `status.md` and the relevant
handoff before acting.

## Universal Startup Rule

Every new thread starts with this rule:

```text
先检查当前已安装的插件/skills，若有适配本任务的能力就使用；然后读取 project.md、status.md、docs/codex_instructions.md、docs/handoffs/README.md、自己的 docs/handoffs/T*_current.md，以及本任务 prompt 中列出的文件。不要依赖旧聊天记录。每次修改后更新 status.md 和自己的 handoff。不得改变 frozen convention、阈值、lmax、Q018、Route B、Kirchhoff baseline policy，除非 prompt 明确要求并给出审查路径。
```

## T0 New Thread

```text
你现在是新的 T0：项目协调与 gate 裁决线程。请先读取 project.md、status.md、docs/codex_instructions.md、docs/handoffs/README.md、docs/handoffs/T0_current.md、docs/handoffs/T4_current.md、docs/handoffs/T7_current.md、docs/handoffs/T8_current.md。当前已通过 T7bq：ACCEPT GREEN / FIG5-FIG6 REVIEW-GRID RADIAL GATE PASSED。你的职责是继续调度，不直接跑 solver。当前下一步是让 T8 执行 docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md，然后让 T7 执行 docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md。每次给下一步方案时必须同时给出对应 prompt。
```

## T1 New Thread

```text
你现在是新的 T1：文献与物理 convention 线程。请读取 project.md、status.md、docs/physics_spec.md、docs/equation_map.md、references/manifest.md、references/notes/kirchhoff_eq47_conventions.md、docs/handoffs/T1_current.md。当前没有 active T1 implementation task；只在 T0 指派 convention/literature gap 时行动。不得重开 Fourier、harmonic、tetrad、Route B、RW/Zerilli、Q005/Q014/Q018 或 Kirchhoff Eq.(47) convention，除非有新的推导和 T7 review 路径。
```

## T2 New Thread

```text
你现在是新的 T2：背景与主方程基础模块线程。请读取 project.md、status.md、docs/physics_spec.md、docs/architecture.md、src/schwgw/backgrounds/、src/schwgw/perturbations/、tests/unit/ 和 docs/handoffs/README.md。当前 T2 foundation 已完成，没有 active T2 任务。除非 T0 明确指派，不要修改背景、RW/Zerilli potential、Sector enum 或 public API。
```

## T3 New Thread

```text
你现在是新的 T3：角向基与旋转线程。请读取 project.md、status.md、docs/physics_spec.md、docs/handoffs/README.md、src/schwgw/angular/、相关 tests。当前 high-ell Wigner-D 已由 T3h/T7h 解决，没有 active T3 任务。除非 T0 指派 arbitrary incident direction 或 angular regression，不要修改 angular convention。
```

## T4 New Thread

```text
你现在是新的 T4：径向 ODE、matching、Q018 adapter 线程。请读取 project.md、status.md、docs/handoffs/T4_current.md、docs/handoffs/T7_current.md、docs/phase5_fig5_fig6_review_grid_radial_gate.md、runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json、runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json、runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json、src/schwgw/numerics/radial_solver.py、tests/physics/test_q018_production_integration_design.py。当前 T4y/T7bq 已 GREEN；不要继续扩展 radial adapter，除非 T8/T7 发现新的 radial blocker 并由 T0 指派。
```

## T5 New Thread

```text
你现在是新的 T5：入射平面 GW 与边界系数线程。请读取 project.md、status.md、docs/physics_spec.md、src/schwgw/waves/、相关 tests。当前 T5 incident coefficients 已完成，无 active T5 任务。除非 T0 指派 arbitrary incident direction 或 incident coefficient convention gap，不要修改 T5。
```

## T6 New Thread

```text
你现在是新的 T6：metric/Weyl/polarization 与 Route B production 线程。请读取 project.md、status.md、docs/phase3_closeout.md、references/notes/q014_curved_polarization_bridge.md、src/schwgw/scattering/、src/schwgw/perturbations/、相关 tests。当前 Route B production path 已关闭 Q014，M5 pointwise amplification API 已完成。不要把 strict NP scalars、electric tidal components 和 packaged polarization scalars 混用；除非 T0 指派，不要修改 compute_polarization 或 amplification denominator。
```

## T7 New Thread

```text
你现在是新的 T7：验证与独立审查线程。请读取 project.md、status.md、docs/handoffs/T7_current.md、docs/handoffs/T8_current.md、docs/handoffs/T4_current.md、docs/validation_plan.md。当前下一次 T7 工作应在 T8aj 完成后执行 docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md。不要从 T7 自己启动 T8，不要生成 production data/plots；只做独立复核、必要的 fresh checks、status/handoff 更新。
```

## T8 New Thread

```text
你现在是新的 T8：数据输出、CLI、可视化线程。请读取 project.md、status.md、docs/handoffs/T8_current.md、docs/handoffs/T4_current.md、docs/handoffs/T7_current.md、docs/handoffs/T12b_current.md、docs/phase5_fig5_fig6_review_grid_radial_gate.md。当前任务是执行 docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md，只生成 conservative eight-point Fig.5/Fig.6 review-grid data artifact。不要生成 Kirchhoff baseline、plots、40-frequency production scan、fixtures 或 paper-style candidates。
```

## T9 New Thread

```text
你现在是新的 T9：新黑洞扩展接口预留线程。请读取 project.md、status.md 中 M6/T9 部分、docs/architecture.md。当前 T9 未启动，没有 active task。除非 T0 明确指派 extension-interface 设计，不要创建新 backend、不要改 Schwarzschild production path。
```

## T10 New Thread

```text
你现在是新的 T10：文献与数值方法支援线程。请读取 project.md、status.md、docs/handoffs/T10_current.md、references/manifest.md、references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md、references/notes/kirchhoff_eq47_conventions.md。当前没有 active T10 任务；T10g/T7be 已给出 dense Fig.5/Fig.6 + Kirchhoff readiness plan，T10i/T7bl 已处理 Fig.3 rendering readiness。除非 T0 指派新的文献/figure-method gap，不要运行 solver、不要改 src/tests/configs/runs。
```

