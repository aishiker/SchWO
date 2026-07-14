# Phase 5 T10b Prompt: Literature Support For Q018 Spin-2 Tail Bound

你现在是 `T10：文献与数值方法支援` 线程，slice 名称为 `T10b`。

T7ag 已经把 Q018 larger-domain readiness 复核为 **ACCEPT YELLOW**：
当前 `kM=2` evanescent-tail suppression 只覆盖 accepted `[-30,30]^2`，不覆盖
R60_K2。你的任务是给 T4m 提供文献和公式层面的判断：能否用 finite-radius
WKB/high-ell tail bound 支持 spin-2 RW/Zerilli R60_K2，或者必须记录 no-go。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/q018_larger_domain_readiness.md`
7. `docs/prompts/phase5_t4m_q018_r60_method_hardening.md`
8. `references/manifest.md`
9. existing relevant notes under `references/notes/`

按项目规则先检查是否有已安装且适用的 plugin/skill。涉及文献时，优先使用已安装
的 arXiv / academic-search / paper-reading / Zotero 相关能力（如果可用），并记录。

## 2. Scope

允许：

- 阅读 `references/manifest.md`、`references/notes/`、必要 PDF/论文条目。
- 使用已安装的文献检索/阅读插件或 skills。
- 创建：

```text
references/notes/q018_spin2_tail_bound.md
```

- 更新 `references/manifest.md` 中相关条目的用途说明（如需要）。
- 更新 `status.md`。

禁止：

- 不要修改 `src/`。
- 不要生成 artifacts 或 plots。
- 不要修改 physics conventions。
- 不要把 scalar-field `ell_max~kr` 结论直接当作 spin-2 RW/Zerilli 定理。

## 3. Required Questions

请回答：

1. Zhao Li scalar scattering / partial-wave convergence paper 中的
   `ell_max ~ k r` 或自然截断结论的适用前提是什么？
2. 这些前提哪些可以迁移到 spin-2 RW/Zerilli master equation？
3. 哪些地方不能直接迁移？
   - parity odd/even potentials；
   - metric reconstruction factors；
   - tensor harmonics；
   - finite-radius polarization extraction；
   - possible polynomial `ell` prefactors。
4. 对 `k=2, r=60, ell>=153`，使用 local WKB tail action/bound 是否可能给出
   足够保守的 spin-2 negligible-tail criterion？
5. 如果可以，建议 T4m metadata 至少记录哪些量？
6. 如果不可以，建议 T4m 采用怎样的 no-go wording 和未来 method requirements？

## 4. Output Note Requirements

创建：

```text
references/notes/q018_spin2_tail_bound.md
```

内容包括：

- source list and priority；
- established claims；
- assumptions；
- what transfers from scalar to spin-2；
- what does not transfer；
- recommended conservative bound form, or no-go recommendation；
- exact warning about not validating `kM=4`；
- how this note should be used by T4/T7。

避免长篇原文摘抄；引用只保留短句或公式编号，并用 paraphrase 说明。

## 5. status.md Update

更新 `status.md`：

- changed files；
- files read；
- plugin/skill used；
- literature conclusion；
- whether T4m Route B is supportable, not supportable, or needs stronger derivation；
- open issues；
- next action。
