# T0 Current Handoff

Date: 2026-07-14

Thread: T0, project coordination and gate scheduling.

## Current Status

The T8am/T7bu diagnostic spacing gate is closed, and the user has reviewed and
approved the next bounded `Delta(kM)=0.1` risk-pilot design for direct start.

Current exact state:

```text
AUTHORIZED / T4Z DELTA0P1 RISK-PILOT RADIAL GATE
```

Only T4z is authorized now. T8an remains blocked until T4z exact GREEN is
independently accepted by T7bv and T0 dispatches the frozen T8an prompt.

T8am exact decision:

```text
GREEN / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS GENERATED
```

T7bu exact decision:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW GRID SUPPORTS DELTA KM 0.1 PRODUCTION PILOT
```

T0 exact decision:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW-GRID DIAGNOSTIC SPACING GATE CLOSED
DESIGN AUTHORIZED / BOUNDED DELTA KM 0.1 PILOT ONLY
```

The approved pilot remains narrow: nine new point-only frequencies, not full
production. No 40/79-frequency production, `Delta(kM)=0.05` scan, fixture,
plot, interpolation/smoothing/fill, or paper-style stage is authorized.

## T0 Independent Verification

- `git diff --name-only f6d32b1^..1542f5e` contains exactly:
  - `src/schwgw/cli.py`
  - `src/schwgw/viz/__init__.py`
  - `src/schwgw/viz/tablei_review_grid.py`
  - `tests/regression/test_plot_review_grid_cli.py`
  - `tests/unit/test_viz_tablei_review_grid.py`
- All six frozen T8aj/T8al source SHA256 values match.
- All eight diagnostic-output SHA256 values match and the output directory
  contains exactly eight files.
- Independent direct-NPZ recomputation passed:

```text
T0_T7BU_PHASE_AND_RECOMMENDATION_AUDIT=PASS
DELTA_0P1_PROVISIONAL_REVIEW
```

- Focused pytest: `10 passed in 1.81s`.
- Ruff: `All checks passed!`.
- Full pytest:
  `568 passed, 117 skipped, 1 xfailed, 85 warnings, 79 subtests passed in
  277.82s (0:04:37)`.
- Forbidden production diff and downstream-output checks are empty.
- Warnings remain the known Weyl/Wigner/radial warnings.

## Visualization Check And Recorded Qualification

- Both PNGs are native `2100x1620` RGBA images.
- Both PDFs are unencrypted one-page `504x388.8 pt` documents; both were
  independently rasterized at 180 DPI and inspected with the PNGs.
- Titles, diagnostic-only subtitles, four panels, saved-sample guides,
  legends, axes, units, and bottom captions are visibly present and unclipped.
- Actual rasters have nonzero white margins, no non-white edge pixels, and
  first non-white content 13 pixels inside the left edge.
- `pdftotext -bbox` nevertheless reports two rotated y-axis font boxes per PDF
  with `xMin=-1.727017`. T0 records this as a nonblocking font-bbox extraction
  discrepancy, not visible clipping. The stronger literal statement that
  every extracted font bbox lies inside the page box is therefore not adopted
  by T0, while the frozen visual gate itself still passes.

## Scientific Interpretation

All four independently recomputed phase-safety projections are below `pi/2`:

- near `F_plus`: `0.4194247204136605` rad;
- near `F_cross`: `0.5438572437346854` rad;
- far `F_plus`: `1.3144511140288706` rad;
- far `F_cross`: `1.1331614399463659` rad.

This supports a bounded finer-spacing pilot. It does not prove band limitation
or production convergence. In particular, far `F_cross` has maximum absolute
magnitude step `1.7643213800514306` and maximum relative step
`0.8039700767407513` at `far_axis_x15_z30` over `[0.75,1.0]`; the frozen gate
has no automatic magnitude threshold, so this remains an explicit pilot risk.

## Accepted Hashes

T8aj exact review-grid source:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  NPZ
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  JSON
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  manifest
```

T8al Kirchhoff comparison source:

```text
66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55  NPZ
0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3  JSON
fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632  manifest
```

T8am diagnostics:

```text
f8ffcee55ce2a4d07e9a2ff91320baa0122bd37f43701cfde8d5eab5e963c386  fig5 PNG
e19c28ca4a6532adc079f99137853115b9f90e0764bed84957d133d3b9167c11  fig5 PDF
627903f91de69edf3d4e527419511a6a898979e8ae8c6dd57e6cee70ee93cb98  fig5 JSON
e949bd7436617bf8cadb59515a3861e8bc8503e17337347a81be7598ef061855  fig6 PNG
02b05bbe092f0c5934bcc389ca16d305208202637182c88038eeb5ff511a77ec  fig6 PDF
06142d333dabba5dd17f76642a4a792dfa6603beee6a73ce8cc712c07073f534  fig6 JSON
cb40d6cae967699b86f0ef3d863e8cbe9ce2555f56dcd3427f8f5d64d44190a4  sampling JSON
f09c24abb30c1ec64abcd3cd9dd2679061dfa23d746c2c96c49ffdd4e04c327b  manifest
```

## GitHub Milestone Synchronization

This independent GREEN closes a high-risk gate and is a major node under
`project.md`.

Authorized synchronization scope:

- the four committed design/plan/implementation commits from `259a020`
  through `1542f5e`;
- `status.md`;
- current T0/T7/T8 handoffs;
- T7/T8 archives belonging to the T8am/T7bu chain.

Explicitly excluded:

- unrelated T1/T2/T3/T5/T6 handoff changes;
- ignored `runs/` artifacts;
- secrets/credentials, raw/private data, unexpected large files, and any
  unrelated or unreviewed path.

Synchronization result:

```text
GitHub sync completed
```

- The configured repository is private and its default/current branch is
  `main`; authentication was available.
- Fresh preflight showed `origin/main...HEAD = 0 4` before closeout, and the
  outgoing scope/secret/binary checks passed.
- `status.md` is a known tracked text ledger: it grew from `1,177,642` to
  `1,192,689` bytes. No newly added file exceeds 1 MiB and no binary file is
  included.
- Primary scoped closeout commit:
  `96d8aac docs: close review-grid diagnostic gate`.
- Non-force `main -> origin/main` push succeeded. Fresh fetch reported
  divergence `0 0` and exact object equality:
  `FIRST_GITHUB_SYNC=PASS`.
- The final durable sync-record commit changes only `status.md` and this T0
  handoff and is followed by a second non-force push/equality check.
- No PR, force push, history rewrite, branch deletion, visibility change, or
  unrelated handoff upload occurred.

## Runtime Tasks And Monitor

- T0 task: `019f5ec5-84ba-79e2-8c77-1160b150a636`.
- T4 task: `019f5fa6-1288-7c01-8a87-4c4370cf5517`.
- T8 task: `019f5ece-f578-7b91-8f61-df882c656591`.
- T7 task: `019f5ed1-b421-7ec2-9bac-8d134855a1ed`.
- T8am and T7bu are complete; their old monitor is deleted.
- A new T4z→T7bv→T8an→T7bw monitor is created only after T4z dispatch.

## Exact Next Action

Frozen design:

- `docs/superpowers/specs/2026-07-14-t4z-t8an-delta0p1-risk-pilot-design.md`
  (`cb9bbfc`).

Frozen plans/prompts (`55b843f`):

- `docs/superpowers/plans/2026-07-14-t4z-delta0p1-risk-pilot-radial-gate.md`;
- `docs/superpowers/plans/2026-07-14-t8an-delta0p1-nine-frequency-risk-pilot.md`;
- `docs/prompts/phase5_t4z_delta0p1_risk_pilot_radial_gate.md`;
- `docs/prompts/phase5_t7bv_delta0p1_risk_pilot_radial_review.md`;
- `docs/prompts/phase5_t8an_delta0p1_nine_frequency_risk_pilot.md`;
- `docs/prompts/phase5_t7bw_delta0p1_risk_pilot_review.md`.

Exact next action: send the frozen T4z prompt to existing T4 task with
`gpt-5.6-sol/high`. Only exact T4z GREEN dispatches T7bv. T7bv never starts
T8an; it returns to T0, which alone may dispatch T8an after independently
checking exact GREEN. T8an exact GREEN may dispatch T7bw. Every other state
stops and returns to T0.
