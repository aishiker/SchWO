# Phase 4 T4k Delta Prompt: Q018 Scalar Cutoff Reference

你已经在运行 `T4k` 时使用本补充提示词。不要重启任务，除非你已经开始实现
一个与本文献结论冲突的方案。

请在当前 T4k 任务中补读：

1. `references/notes/q018_scalar_partial_wave_cutoff.md`
2. `arxiv-reading/2508.17253.memory.md`
3. 更新后的 `docs/prompts/phase4_t4k_q018_high_ell_evanescent_tail.md`
4. `status.md` 中 2026-07-06 关于 arXiv:2508.17253 的记录

补充要求：

- 将 arXiv:2508.17253 的 scalar finite-radius cutoff 结论作为 Q018 的
  strong prior：finite-radius scalar PWS naturally truncates around
  `ell_max ~ k r`。
- 不要把 scalar 结论直接当作 spin-2 RW/Zerilli 的完成证明。
- 需要明确分析该结论如何映射到 RW/Zerilli 大 `ell` 势、
  tensor/spin-weighted angular factors、metric/Weyl/polarization extraction。
- 若采用 high-ell cutoff/tail policy，必须给出 contribution bound 或
  conservative diagnostic criterion，并写入 result metadata；禁止 silent
  `lmax` reduction。
- 如果你已经完成了与此不冲突的诊断，可以继续；如果已经开始实现“强行积分
  到 `ell=180`”或 arbitrary precision 方案，请暂停并先重新评估 scalar
  cutoff 路线。

完成或停止时仍按主 T4k prompt 更新 `status.md`。
