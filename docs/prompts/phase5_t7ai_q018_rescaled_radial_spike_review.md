# Phase 5 T7ai Prompt: Review Q018 Rescaled Radial Architecture Spike

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ai`。

只在 T4n 完成后运行。你的任务是独立复核 T4n 的 rescaled/log/high-precision
radial architecture spike，判断它是否足以支持下一步 implementation slice，
而不是判断 R60_K2 production artifact 是否通过。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_larger_domain_readiness.md`
8. `docs/q018_r60_method_hardening.md`
9. `docs/q018_rescaled_radial_architecture_spike.md`
10. `references/notes/q018_spin2_tail_bound.md`
11. `docs/prompts/phase5_t4n_q018_rescaled_radial_architecture_spike.md`
12. relevant files changed by T4n

按项目规则先检查已安装 plugin/skill。这个 slice 是验证/review，使用
verification/systematic debugging 相关 skill（如可用）并记录。

## 2. Review Scope

确认 T4n：

- 没有生成 R60_K2 wave-field artifact；
- 没有绘图；
- 没有运行或验证 `kM=4`；
- 没有修改 frozen physics conventions；
- 没有降低 `lmax` 或放宽 thresholds；
- 没有绕过 T4m `required_eval_radius` fail-closed guard；
- 如果有 prototype，它没有被默认为 production solver path。

## 3. Independent Checks

Re-run or inspect enough targeted diagnostics for:

```text
k=2
r=60
r_out=300
ell=[153,156,180]
sector=[odd, even]
```

Check:

- current production path remains fail-closed for `required_eval_radius=60`;
- any prototype result is finite only if T4n claims finite;
- precision/tolerance sensitivity is reported;
- no unsupported scalar-cutoff-to-spin-2 GREEN claim is made。

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## 4. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR IMPLEMENTATION SLICE**:
  T4n identifies a plausible, bounded-scope method with finite/stable selected
  diagnostics and clear tests; next step may be a T4 implementation slice.
  This still does not authorize T8 R60_K2 production.
- **ACCEPT YELLOW / DESIGN ONLY**:
  T4n clarifies architecture or no-go, but no stable implementation path is
  ready.
- **REJECT RED**:
  unsupported claims, hidden production changes, threshold/convention drift,
  failing tests, or unstable diagnostics.

## 5. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- independent diagnostics;
- test results;
- decision label;
- open issues;
- exact next action prompt recommendation.
