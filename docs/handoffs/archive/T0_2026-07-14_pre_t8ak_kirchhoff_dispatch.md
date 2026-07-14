# T0 Current Handoff

Date: 2026-07-14

Thread: T0, project coordination and gate scheduling.

## Current Status

The last locally verifiable Fig.5/Fig.6 gate remains:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW-GRID RADIAL GATE PASSED
```

The user reports that T8aj and T7br have completed.  T0 checked the active
checkout, Codex worktree storage, visible Codex task records, and GitHub
`origin/main`, but the completion evidence is not present in any of them.

Missing required T8aj outputs:

```text
runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
runs/phase5/fig5_fig6_dense_review_grid/manifest.md
```

The directory currently contains only the preserved T12b blocker:

```text
runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json
```

`docs/handoffs/T7_current.md`, `docs/handoffs/T8_current.md`, and the current
`status.md` timeline also contain no T8aj/T7br completion record.  Local
`HEAD`, the local `origin/main` tracking ref, and the live remote `main` all
resolve to `bf710bc86a288cf272b3f720aa89e7c7f49b22e8`.

Decision:

```text
YELLOW / T8AJ-T7BR COMPLETION EVIDENCE NOT SYNCED
```

Do not start Kirchhoff implementation, review-grid plots, 40-frequency
production, or paper-style candidates until the missing artifact and T7br
decision are visible and independently checked in the active project tree.

## GitHub Milestone Sync Rule

`project.md` now requires T0 to synchronize verified major project nodes to
the configured private GitHub repository after `status.md` and the T0 handoff
are updated and fresh verification passes.

Before every such sync T0 must inspect the complete diff, exclude secrets,
private raw data, unintended large files, unrelated changes, and unreviewed
artifacts, then make a scoped commit and non-force push.  If the tree contains
unrelated changes or any sync boundary is unclear, record `GitHub sync
pending` instead of staging or pushing blindly.

Current GitHub sync status:

```text
GitHub sync pending
```

Reason: this T0 slice is not a verified major project closeout, and the active
working tree already contains unrelated handoff/status changes that must not
be bundled into an automatic push.

## Exact Next Tasks

First return to the completed T8aj task and send:

```text
你现在是 T8aj 结果同步恢复线程。不要重跑 solver。请检查你已完成任务所使用的 checkout/worktree，定位 tablei_dense_review_values.npz、对应 JSON sidecar、manifest.md，以及你对 status.md 和 docs/handoffs/T8_current.md 的更新；把这些已完成结果安全同步到当前主项目目录 /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO。不得覆盖 runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json，不得生成 Kirchhoff、plots、40-frequency production、fixtures 或 paper-style artifacts。同步后重新运行 docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md 中的 artifact checks，并报告文件路径、SHA256、检查结果和所有实际变更。如果已完成结果已丢失或从未落盘，停止并明确报告，不要无提示重算。
```

After the T8aj files are visible, return to the completed T7br task and send:

```text
你现在是 T7br 结果同步与复核恢复线程。不要生成数据、Kirchhoff、plots 或 dense production。请把你已完成的 T7br decision、status.md 更新和 docs/handoffs/T7_current.md 更新安全同步到当前主项目目录 /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO；然后对当前目录中的 T8aj NPZ/JSON/manifest 重新执行 docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md 的只读 fresh checks。若结果仍满足 GREEN，原样记录 `ACCEPT GREEN / FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA ACCEPTED`；若 artifact 缺失、hash 不符或检查失败，记录实际 YELLOW/RED，停止且不得开启 Kirchhoff 阶段。
```

T0 must then independently inspect the synchronized artifacts and decision.

## Conditional Next Stage After Reconciliation

Only if T7br's exact GREEN decision is present and fresh checks pass, the next
bounded implementation stage is a separate T8 Kirchhoff Eq. (47) scalar
comparison-baseline artifact for the same 18-by-8 review grid, followed by a
separate T7 independent review.  Review-grid plotting remains gated until
that baseline review passes.  No 40-frequency production or paper-style
candidate is authorized by T7br GREEN alone.

## Must-Read Files

1. `status.md`
2. `project.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md`
7. `docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md`
8. `references/notes/kirchhoff_eq47_conventions.md`
9. `docs/physics_spec.md`
10. `docs/equation_map.md`

## Frozen Decisions

- Fourier convention remains `exp(-i k t)`.
- Route B packaged polarization remains the production path.
- Strict NP scalars and packaged polarization scalars remain separated.
- Pointwise amplification denominator remains the flat/no-lens packaged
  polarization field.
- Kirchhoff Eq. (47) remains a scalar comparison baseline only.
- Q018 `required_eval_radius` remains fail-closed.
- Existing Wronskian/flux/lmax/near-axis thresholds remain unchanged.
- `q018_tablei_review_grid_transition` must not be broadened beyond its
  reviewed envelope.

## Forbidden Actions

- Do not infer T8aj/T7br acceptance from the user's completion report alone.
- Do not rerun the expensive T8aj solver scan during result reconciliation
  without an explicit new authorization.
- Do not start Kirchhoff implementation or plotting before synchronized T7br
  GREEN evidence is checked.
- Do not run 40-frequency production, fixtures, Appendix D/E, R60_K4,
  Fig.2 strict `Psi4`, `dx=0.2M`, or paper-style candidates.
- Do not stage, commit, or push unrelated/unreviewed working-tree changes.
- Do not force push or rewrite Git history.

## Verification Commands

```bash
test -f runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
test -f runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
test -f runs/phase5/fig5_fig6_dense_review_grid/manifest.md
rg -n "T8aj|T7br|FIG5-FIG6 CONSERVATIVE REVIEW-GRID DATA" status.md docs/handoffs/T7_current.md docs/handoffs/T8_current.md
git status --short
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

After artifact synchronization, also run the exact artifact checks in both
the T8aj and T7br prompts.

## Definition Of Done For Reconciliation

- T8aj NPZ/JSON/manifest are present in the required project path.
- Artifact hashes and schema checks pass.
- `status.md` and T8/T7 handoffs contain the actual completion and review
  records.
- T7br's fresh independent decision is recorded without artifact mutation.
- Forbidden downstream artifacts remain absent.
- T0 has enough evidence to issue a new bounded Kirchhoff-baseline prompt.
