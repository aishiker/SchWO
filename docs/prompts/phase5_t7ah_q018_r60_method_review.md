# Phase 5 T7ah Prompt: Review Q018 R60 Method Hardening

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ah`。

T7ag 已经接受 T4l 为 **YELLOW**。本 slice 只在 T4m 完成后运行；如果 T10b
也完成了，请同时纳入复核。你的任务是判断 T4m 是否真正解除 R60_K2 的 Q018
gate，还是仍应保持 YELLOW/RED。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_larger_domain_readiness.md`
8. `docs/q018_r60_method_hardening.md` if present
9. `references/notes/q018_spin2_tail_bound.md` if present
10. `docs/prompts/phase5_t4m_q018_r60_method_hardening.md`
11. `src/schwgw/numerics/radial_solver.py`
12. `src/schwgw/numerics/boundary_conditions.py`
13. `tests/physics/test_radial_solver.py`

按项目规则先检查是否有已安装且适用的 plugin/skill；本 slice 是验证/review，
使用 verification / systematic debugging 相关 skill（如可用）并记录。

## 2. Review Scope

确认：

- T4m 没有生成 R60_K2 wave-field artifact。
- T4m 没有绘图。
- T4m 没有运行或声称通过 `kM=4`。
- T4m 没有改变 Fourier/harmonic/tetrad/RWZ/Route B/Q005/Q014 convention。
- T4m 没有降低 `lmax` 或放宽 residual/convergence thresholds。
- T4m 没有仅通过降低 suppression thresholds 来制造 R60 pass。

## 3. Independent Technical Checks

### 3.1 Behavior checks

Independently test:

```text
M=1
k=2.0
r_out=300.0
ell in [153,156,168,180]
sector in [odd, even]
required_eval_radius=60.0 if implemented
```

Check:

- no unstructured exception unless T4m intentionally chose documented no-go；
- old `valid_until_r≈42.47` is not silently treated as covering R60；
- warning metadata is JSON-safe；
- if R60 is claimed covered, metadata contains target-radius evidence；
- if no-go is chosen, error/report is clear and T8 remains gated。

### 3.2 Tests

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

### 3.3 Literature consistency

If `references/notes/q018_spin2_tail_bound.md` exists, verify T4m does not
claim more than that note supports. In particular, scalar `ell_max~kr` cannot
alone justify a spin-2 production truncation or suppression pass.

## 4. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR R60_K2 METHOD ONLY**:
  T4m provides target-radius-aware solver/bound evidence for `r=60`,
  tests pass, metadata is reviewable, and no forbidden shortcut occurred.
  This allows a future T8 R60_K2 artifact prompt, but does not itself accept
  any R60_K2 artifact.
- **ACCEPT YELLOW**:
  T4m improved diagnostics/API/no-go clarity but R60_K2 production remains
  gated.
- **REJECT RED**:
  hidden threshold/convention/lmax changes, unsupported spin-2 extrapolation,
  failing tests, missing metadata, or unstructured failures.

Do not validate `kM=4` in this review.

## 5. status.md Update

Update `status.md` with:

- changed files；
- files read；
- skill/plugin check；
- independent behavior/probe results；
- test results；
- literature consistency result if applicable；
- decision label；
- open issues；
- exact next action prompt recommendation。
