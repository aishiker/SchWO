# Phase 4 T8l Prompt: Resume kM=2.0 Fig.3-Lite After Q018

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8l`。

## 0. 前置条件

只有在 `status.md` 明确记录 T4k 已经解除或足够收窄 Q018，并说明 T8l
可以继续后，才开始本任务。否则停止并更新 `status.md`，不要尝试重跑。

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/architecture.md`
4. `docs/numerics.md`
5. `docs/validation_plan.md`
6. `docs/phase3_closeout.md`
7. `docs/prompts/phase4_t8j_fig3_multifrequency_panel.md`
8. `docs/prompts/phase4_t8k_resume_fig3_multifrequency.md`
9. `docs/prompts/phase4_t4k_q018_high_ell_evanescent_tail.md`
10. `configs/li_fig3_xz_k2p0_hires.yaml`

## 2. Goal

Resume the multi-frequency Fig.3-lite path after Q018:

- keep the accepted existing artifacts:
  - `/tmp/t8j_li_fig3_xz_k0p5_hires.npz`
  - `/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz`
  - `/tmp/t8j_li_fig3_xz_k1p5_hires.npz`
- generate the missing `kM=2.0` saved result:
  - `/tmp/t8j_li_fig3_xz_k2p0_hires.npz`
- generate the read-only four-frequency panel:
  - `/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png`

## 3. Hard limits

- Do not modify radial solver, T2-T6 physics, conventions, or convergence thresholds.
- Do not lower `lmax` unless T4k/T0 explicitly changed the accepted policy in `status.md`.
- Do not generate R60_K2/R60_K4 regression fixtures.
- Do not run `kM=4` stress.
- Do not implement transmission.
- Plotting must remain read-only over saved results.

## 4. Steps

1. Re-check the three existing artifacts for shape `(61,61)`, finite valid
   complex fields, horizon mask, final adjacent-pair pass, cache metadata,
   and warning metadata.
2. Run:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_k2p0_hires.yaml --out /tmp/t8j_li_fig3_xz_k2p0_hires.npz
```

3. Inspect `/tmp/t8j_li_fig3_xz_k2p0_hires.npz`:
   - shape;
   - valid/invalid counts;
   - finite valid fields;
   - invalid fields masked/NaN;
   - convergence history and final pair;
   - run radial cache;
   - radial warnings / evanescent-tail metadata if T4k introduced it;
   - samples per wavelength.
4. If all four saved results pass checks, generate:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel \
  /tmp/t8j_li_fig3_xz_k0p5_hires.npz \
  /tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz \
  /tmp/t8j_li_fig3_xz_k1p5_hires.npz \
  /tmp/t8j_li_fig3_xz_k2p0_hires.npz \
  --quantity real \
  --interpolation nearest \
  --out /tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png
```

## 5. Verification

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run metadata inspection over all four NPZ files and the panel sidecar.

## 6. Stop conditions

Stop and update `status.md` if:

- T4k did not authorize continuation;
- `kM=2.0` still fails;
- single saved run exceeds 60 minutes without output;
- final adjacent pair fails;
- valid fields are non-finite;
- required radial warning/evanescent-tail metadata is missing;
- panel generation calls solver or physics code.

## 7. status.md update requirements

Record changed files, commands, runtimes, artifact paths, metadata summary,
test results, open issues, and whether T7u may proceed.

If T8l completes, next prompt:

```text
你现在是 T7u。请读取并严格执行 docs/prompts/phase4_t7u_fig3_multifrequency_q018_review.md。
```
