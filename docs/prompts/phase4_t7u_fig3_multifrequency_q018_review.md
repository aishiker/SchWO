# Phase 4 T7u Prompt: Fig.3 Multi-Frequency Review After Q018

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7u`。

## 0. 前置条件

只有在 `status.md` 记录 T4k 和 T8l 均完成、四个 saved results 与
`2x4` panel 都存在后，才做通过态复核。若 artifact 缺失或 T8l 停止，
本任务只能记录 blocker，不得给出 pass。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/phase3_closeout.md`
6. `docs/architecture.md`
7. `docs/numerics.md`
8. `docs/validation_plan.md`
9. `docs/prompts/phase4_t4k_q018_high_ell_evanescent_tail.md`
10. `docs/prompts/phase4_t8l_resume_k2_after_q018.md`
11. T4k/T8l changed files listed in `status.md`

## 2. Goal

Independently review the Fig.3-lite multi-frequency path after Q018:

- Q018 resolution or narrowed policy is scientifically and numerically defensible;
- no frozen convention, T6 Route B, or threshold was changed;
- no high-ell mode was silently skipped;
- all four saved results pass metadata/finiteness/convergence checks;
- the `2x4` panel is read-only over saved results;
- any high-ell evanescent-tail policy is represented in structured metadata.

## 3. Required artifacts

```text
/tmp/t8j_li_fig3_xz_k0p5_hires.npz
/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz
/tmp/t8j_li_fig3_xz_k1p5_hires.npz
/tmp/t8j_li_fig3_xz_k2p0_hires.npz
/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png
/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png.json
```

## 4. Review checklist

### 4.1 Radial Q018 review

Check T4k:

- direct failing mode `sector=odd, ell=153, k=2.0, r_out=300` is addressed or
  bounded explicitly;
- any suppression or high-barrier policy has a documented contribution bound;
- lower-ell Q012/Q017 tests still pass;
- warning metadata is JSON-safe and not hidden in scalar summaries;
- no lmax reduction or threshold relaxation was used as a hidden workaround.

### 4.2 Saved-result checks

For each NPZ:

- `grid.kind == "xz_plane"`;
- matching `x/z` grid over `[-30,30]` with spacing `1`;
- expected shape `(61,61)`;
- horizon mask matches `r <= 2M`;
- valid fields finite;
- invalid fields masked/NaN;
- final adjacent pair passed;
- cache metadata bounded and plausible;
- radial warnings/evanescent metadata are structured.

### 4.3 Panel checks

Check the sidecar:

- exact four source paths in `kM=[0.5,1.0,1.5,2.0]` order;
- components `h_plus/h_cross`;
- quantity real;
- nearest interpolation recorded;
- row-wise symmetric color limits recorded;
- event horizon and light-ring overlays recorded;
- samples per wavelength recorded.

Also confirm `src/schwgw/viz` still has no solver/physics imports.

## 5. Verification commands

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run an independent metadata inspection script over the four NPZ files and the
panel JSON sidecar. Do not rerun solver to create missing artifacts.

## 6. Pass conditions

Pass only if:

- Q018 no longer blocks `kM=2.0`;
- all required artifacts exist;
- per-frequency final adjacent pairs pass;
- valid fields are finite;
- plotting remains read-only;
- full pytest passes;
- no convention/threshold/truncation shortcut was introduced.

## 7. Stop conditions

Stop and update `status.md` if any required artifact is missing, a final pair
fails, valid fields are non-finite, Q018 metadata is missing/unclear, plotting
imports solver code, or T4k changed a frozen physics convention.

## 8. status.md update requirements

Record changed files, commands run, test results, artifact review summary,
Q018 final state, open issues, and next action.
