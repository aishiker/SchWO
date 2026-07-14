# T8 Current Handoff

Last updated: 2026-07-14

## Thread Role And Current Status

T8ak implemented and freshly verified the bounded Li–Hou–Zhao Eq. (47)
scalar Kirchhoff comparison baseline on the T7br-accepted 18×8 review grid.

Decision:

```text
GREEN / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE GENERATED
```

T7bs automatic dispatch succeeded to existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` with `gpt-5.6-sol`, thinking `high`.
T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` was notified. This baseline
is comparison-only and is not a polarization prediction, production
denominator, mask, normalization, calibration, or solver result.

## Completed Work

- Executed
  `docs/superpowers/plans/2026-07-14-t8ak-kirchhoff-review-grid.md` using the
  `executing-plans` workflow and TDD.
- Installed the already-declared `[dev,oracle]` extras only inside `.venv`;
  backend is `mpmath 1.4.1`, `dps=60`.
- Added an isolated pure Eq. (47) API and accepted-grid artifact writer.
- Used the frozen formula/branches: `gamma=-2Mk`, coordinate-derived `eta`,
  principal positive-real log, principal complex Gamma, Kummer M, and no
  conjugation.
- Generated exactly three baseline artifacts under
  `runs/phase5/fig5_fig6_kirchhoff_baseline/`.
- Verified all 144 values finite, validity mask all true, exact source grid
  ordering, and maximum eta mismatch `4.337937456566632e-05 < 5e-5`.

## Artifacts And Hashes

Accepted T8aj source hashes remained unchanged:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  runs/phase5/fig5_fig6_dense_review_grid/manifest.md
```

T8ak outputs:

```text
a91f0a5f5eb672ac897ea776f7577d4f33b89c72154dc1b665c8ced06cbec53c  runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz
86670c426ada2284d334a017b6abdfc36443d0fb7ea82606f3d544de17788a19  runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json
53d852b25bd73bb25cecb37518e72a010c5b3882cf5e86799e4b695178586d49  runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md
```

## Tests And Verification

- API TDD RED: missing-module collection failure; GREEN: `7 passed`.
- Artifact TDD RED: missing-module collection failure; combined GREEN:
  `9 passed`.
- Ruff: all specified T8ak paths passed.
- Full pytest: `558 passed, 117 skipped, 1 xfailed, 85 warnings, 79 subtests`
  in 278.39s.
- Fresh artifact assertions passed with NPZ-sidecar hash agreement.
- Forbidden-output search and forbidden-source diff were empty.
- T8aj source NPZ SHA256 remained
  `a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb`.
- Scoped commits:
  - `70ef022 feat: add isolated Kirchhoff Eq47 baseline`
  - `c09bbf9 feat: write Kirchhoff review-grid artifact`

## Incomplete Work

- T7bs independent review was dispatched and remains pending its own decision.
- No review-grid plots, 40-frequency scan, fixtures, paper-style candidates,
  or later production stage are authorized.

## Blocking Issues And Non-Blocking Warnings

- No T8ak scientific or verification blocker remains.
- Existing full-suite Weyl/Wigner/radial numerical warnings remain; no new
  Kirchhoff warning or non-finite value occurred.
- T7bs independent acceptance remains the next gate.

## Files The Next Thread Must Read

1. `status.md`
2. `docs/prompts/phase5_t7bs_fig5_fig6_review_grid_kirchhoff_baseline_review.md`
3. `docs/handoffs/T8_current.md`
4. `docs/handoffs/T7_current.md`
5. `docs/superpowers/plans/2026-07-14-t8ak-kirchhoff-review-grid.md`
6. `references/notes/kirchhoff_eq47_conventions.md`
7. `src/schwgw/scattering/kirchhoff.py`
8. `src/schwgw/io/kirchhoff.py`
9. `tests/unit/test_kirchhoff.py`
10. `tests/unit/test_kirchhoff_artifact.py`
11. `scripts/phase5_generate_kirchhoff_baseline.py`
12. `runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md`
13. `runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json`
14. `runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz`

## Frozen Decisions

- Eq. (47) uses the T1j-frozen branches and no positive-`k` conjugation.
- Kirchhoff remains scalar and polarization-independent.
- Coordinate-derived eta and rounded paper `xi/xi0` are stored separately;
  neither may silently replace the other.
- The accepted T8aj 18×8 source arrays and hashes are immutable.
- The production solver, pointwise amplification denominator, masks,
  normalization, Q018, boundary policy, and polarization channels remain
  untouched.

## Forbidden Actions

- Do not repair or regenerate T8ak implementation/artifacts in T7bs.
- Do not call or modify the Schwarzschild solver, Q018, production
  amplification, denominator, masks, normalization, or polarization paths.
- Do not create plots, 40-frequency data, fixtures, interpolation, smoothing,
  paper-style candidates, Appendix D/E curves, or later-stage artifacts.
- Do not mutate T8aj inputs or push GitHub from T7/T8.
- Scientific failures must not be bypassed by changing model.

## Superseded Prompts

- T12/T12b autonomous pipeline prompts are superseded for this gate.
- The T8ak implementation prompt is complete and must not be reused by T7bs
  to repair or regenerate outputs.

## Exact Next Task

The frozen T7bs prompt has been sent to the existing T7 task:

```text
你现在是 T7bs：Fig.5/Fig.6 review-grid Kirchhoff Eq. (47) scalar comparison-baseline 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bs_fig5_fig6_review_grid_kirchhoff_baseline_review.md。T8ak 已报告 exact GREEN；请先独立核验当前文件、hash、公式分支和 fresh tests，不得依赖 T8 的结论，不得修改实现或生成新 baseline/plots/dense-production。完成后按 prompt 更新 status/T7 handoff，并把 exact decision 发送给 T0 task 019f5ec5-84ba-79e2-8c77-1160b150a636。默认使用当前 5.6 Sol High；科学失败不得通过更换模型绕过。
```

## Allowed Files, Verification Commands, And Definition Of Done

- T7bs may modify only its authorized review status/T7 handoff/archive files.
- T7bs must independently recompute all 144 values at higher precision, check
  Kummer-transformation corners, verify hashes/isolation, and rerun focused,
  Ruff, and full pytest checks.
- T8ak verification commands include:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_kirchhoff.py tests/unit/test_kirchhoff_artifact.py -q
.venv/bin/python -m ruff check src/schwgw/scattering/kirchhoff.py src/schwgw/io/kirchhoff.py scripts/phase5_generate_kirchhoff_baseline.py tests/unit/test_kirchhoff.py tests/unit/test_kirchhoff_artifact.py src/schwgw/scattering/__init__.py src/schwgw/io/__init__.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

- T8ak definition of done requires code/artifact/tests/docs fresh checks and
  exact GREEN, followed by authorized dispatch to existing T7 and notification
  to T0. Scientific work, documentation, T7bs dispatch, and T0 notification
  are complete.
