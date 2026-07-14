# Phase 5 Fig.3 dx=0.25M Publication-Readiness Long Task Chain

Date: 2026-07-09

Coordinator: T0

## Purpose

This chain follows the T7bk closeout of the accepted Fig.3 four-frequency
`dx=0.25M` production archive.

It does not authorize new production computation.  Its purpose is to decide
whether the accepted archive is ready for read-only publication-style rendering,
or whether a further numerical-resolution plan such as `dx=0.2M` is justified.

Accepted archive:

```text
runs/phase5/fig3_four_frequency_dx0p25_production/
```

Closeout:

```text
docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md
```

## Chain

1. T10i literature / figure-quality audit in Goal mode.
2. T7bl independent review of T10i and the accepted archive.
3. T0 decides the next execution branch from the T7bl decision.

## Do Not Skip T10i/T7bl

Do not start a `dx=0.2M` run only because the current image looks less smooth
than a published figure.  First separate:

- saved-data numerical resolution;
- interpolation / rendering smoothness;
- panel layout, color normalization, labels, and DPI;
- physical/literature comparability with Li-Hou-Zhao Fig.3.

## Allowed Branches After T7bl

If T7bl returns:

```text
ACCEPT GREEN / FIG3 DX0.25 ARCHIVE IS READY FOR READ-ONLY PUBLICATION RENDERING
```

then T0 may schedule a T8 read-only publication-rendering task.  That task may
only read the accepted NPZ files and create a new publication-style rendering
directory.  It must not rerun the solver.

If T7bl returns:

```text
ACCEPT YELLOW / NEED READ-ONLY RENDER POLISH BEFORE PAPER-QUALITY CLAIM
```

then T0 should schedule T8 read-only rendering polish first, then a T7 image
review.  No new production computation is authorized.

If T7bl returns:

```text
ACCEPT YELLOW / DX0.2 PLANNING JUSTIFIED
```

then T0 should schedule a planning-only `dx=0.2M` feasibility and cost prompt,
not immediate production.

If T7bl returns:

```text
RED / LITERATURE OR SCOPE MISMATCH
```

then T0 must stop Fig.3 promotion and send the issue back to T10/T1/T6 as
appropriate.

## Hard Stop Conditions

Stop and return to T0 if any thread finds:

- the accepted archive does not match the Li-Hou-Zhao Fig.3 physical content;
- Fig.3 requires a different observable than saved `h_plus/h_cross`;
- a paper-level claim would require changing frozen physics conventions;
- Q018 metadata is insufficient for the accepted domain;
- an attempted review needs solver reruns, new configs, new artifacts, or
  plotting mutation outside the explicitly authorized scope.

## Concrete Prompts

Run T10i first:

```text
你现在是 T10i。请使用 Goal 模式，读取并严格执行 docs/prompts/phase5_t10i_fig3_dx0p25_figure_quality_literature_goal.md。
```

After T10i completes, run T7bl:

```text
你现在是 T7bl。请读取并严格执行 docs/prompts/phase5_t7bl_fig3_dx0p25_figure_quality_review.md。
```

