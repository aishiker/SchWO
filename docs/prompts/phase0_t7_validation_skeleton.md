# Phase 0 T7 Prompt: 验证框架骨架

你现在是 `T7：验证与基准` 线程。当前阶段是 Phase 0 / M0：项目启动与规格冻结。目标不是写完整物理测试或生成 benchmark 数据，而是建立后续测试工作的骨架和规则。

请先按顺序阅读：

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/validation_plan.md`
5. `docs/physics_spec.md`
6. `docs/equation_map.md`
7. `pyproject.toml`
8. `tests/` 现有结构

你的任务：

1. 检查并完善 pytest 配置：
   - `pyproject.toml` 中 `testpaths = ["tests"]`。
   - 本地命令采用 `PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q`，或记录更合适的项目本地环境命令。
2. 检查测试目录骨架：
   - `tests/unit/`
   - `tests/physics/`
   - `tests/regression/`
   - `tests/data/`
   - `tests/regression/fixtures/`
3. 在 `docs/validation_plan.md` 中冻结 Phase 0 测试规则：
   - test tiers。
   - 数值容差策略。
   - regression fixture schema。
   - fast/local/physics/full regression 命令边界。
4. 如需要，添加最小 smoke test 或保留现有 unit tests，确保 `tests/` 可以运行通过。
5. 更新 `status.md`：
   - pytest 命令。
   - 测试结果。
   - 目前哪些测试只是 skeleton。
   - 后续 T1/T2/T3/T4/T6 需要提供哪些 fixtures 或 oracle。

边界：

- 不生成大型 regression data。
- 不实现 solver。
- 不改变物理 convention。
- 不为尚未冻结的公式写硬编码 expected physics values；可以只写 schema/smoke/import tests。

退出条件：

- pytest 本地命令可运行。
- `tests/` 空跑或最小测试通过。
- `docs/validation_plan.md` 明确记录容差策略和 fixture schema。
- `status.md` 有 T7 更新记录。
