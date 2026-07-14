# Codex instructions

版本：v0.1-design

## 1. 启动顺序

Codex 每次开始工作时必须按顺序阅读：

1. `project.md`
2. `status.md`
3. 本次任务对应的 `docs/*.md`
4. 若任务涉及物理公式、文献依据、normalization、gauge、tetrad、boundary condition 或 validation benchmark，阅读 `references/manifest.md` 和相关 `references/notes/*.md`
5. 相关源码和测试

不要仅根据聊天上下文修改代码。

M0/Phase 0 任务还必须额外检查：

- `docs/architecture.md`
- `docs/workstreams.md`
- `docs/validation_plan.md`
- `docs/equation_map.md`

## 2. 修改规则

- 小步提交；一次提交只表达一个可审查意图。
- 每个 PR/patch 只服务一个线程；跨线程变更必须先在 `status.md` 写 decision/open issue。
- 新增或修改公式时，同步更新 `docs/physics_spec.md`。
- 修改接口时，同步更新 `docs/architecture.md` 和 `status.md` decision log。
- 修改数值策略时，同步更新 `docs/numerics.md`。
- 修改测试阈值时，同步更新 `docs/validation_plan.md` 和 `status.md`。
- 新增或使用文献依据时，同步更新 `references/manifest.md`、`docs/equation_map.md` 或 `references/notes/`。
- 从 PDF 提取公式后，先写入 `references/notes/` 中的公式笔记，再进入代码实现；不要只依赖 PDF 原文作为后续线程上下文。
- 每次修改后必须更新 `status.md`：changed files、commands run、results、open issues、next action。
- T7 审查应按风险分级：新 production 数据、physics/convention/API 变更、
  benchmark/fixture 晋级、阈值或数值策略变更必须审查；低风险 read-only
  plotting、layout/caption、sidecar/manifest polish 应由 T8 批量完成并自检，
  再交给 T7 做一次 batch review 或 paper-quality 晋级审查。

## 2.1 分支、测试、提交粒度

- 分支命名建议：`phase0/t0-coordination`, `phase0/t1-physics-conventions`, `phase0/t7-validation-skeleton`；后续阶段使用 `mN/tX-short-topic`。
- 一个分支只对应一个线程和一个 milestone slice。
- 提交粒度：文档冻结、测试骨架、公式实现、数值算法、可视化分别提交；不要把 convention 变更和代码实现混在同一个提交。
- 提交前至少运行本线程相关命令；Phase 0 默认命令是 `PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q`。
- 若测试无法运行，必须在 `status.md` 写明解释器、缺失依赖、失败命令和替代验证。
- 本目录当前可能不是 Git 仓库；若无 Git，仍按提交粒度组织 patch，并在 `status.md` 记录无法提交的原因。

## 3. 禁止事项

- 禁止在 plotting code 中重新实现 physics formula。
- 禁止为通过图像比较而调整 normalization。
- 禁止无记录地改变 Fourier convention、tetrad convention 或 harmonic convention。
- 禁止把 Schwarzschild-specific formula 写进 generic interface。
- 禁止只凭视觉结果声明物理正确。
- 禁止未登记来源地引入文献公式。
- 禁止只引用 PDF 文件而不整理 Codex 可读的公式笔记；关键 convention 差异必须在 `references/notes/` 或 `docs/physics_spec.md` 中说明。

## 4. 推荐任务提示模板

### 4.1 实现模块

```text
Read project.md, status.md, docs/physics_spec.md, and docs/numerics.md.
Implement T4 radial solver only. Do not modify angular or Weyl modules.
Add unit tests for horizon boundary data, outer matching residual, and Wronskian conservation.
Update status.md with what changed, commands run, diagnostics, and open issues.
```

### 4.2 修复 bug

```text
Read status.md latest run log and failing test output.
Locate the failure without changing conventions.
If the fix requires a convention change, stop and update docs/physics_spec.md first.
Add a regression test reproducing the failure.
Update status.md.
```

### 4.3 增加新黑洞 backend

```text
Read docs/extension_interface.md.
Implement only the background and sector interfaces for the new model.
Do not reuse Schwarzschild RW/Zerilli reconstruction unless justified in documentation.
Add a minimal benchmark and update status.md.
```

## 5. 状态更新模板

```markdown
## YYYY-MM-DD HH:MM - Tn - short title

Changed:
- ...

Commands run:
```bash
...
```

Results:
- ...

Diagnostics:
- boundary residual: ...
- Wronskian residual: ...
- lmax convergence: ...

Open issues:
- ...

Next:
- ...
```

## 6. Done definition per patch

- [ ] Code runs locally.
- [ ] Relevant tests added/updated.
- [ ] Relevant docs updated.
- [ ] `status.md` updated.
- [ ] No unrelated files changed.
