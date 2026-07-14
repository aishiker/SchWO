# schw-gw-waveoptics design package

这是一个面向 Codex 的 Schwarzschild 引力波波光学求解器项目设计包。

入口文件：

- `project.md`：总项目架构、模块边界、线程分工、里程碑。
- `status.md`：长期维护的进度记录模板。
- `docs/physics_spec.md`：物理约定和公式地图。
- `docs/architecture.md`：代码架构和数据流。
- `docs/workstreams.md`：Codex 并行线程分工。
- `docs/numerics.md`：径向求解、partial-wave sum 和稳定性策略。
- `docs/validation_plan.md`：验证矩阵。
- `docs/extension_interface.md`：新静态球对称黑洞接入接口。
- `docs/codex_instructions.md`：给 Codex 的执行规则。

推荐使用方式：先让 Codex 读取 `project.md` 和 `status.md`，再按线程读取对应 `docs/*.md`。
