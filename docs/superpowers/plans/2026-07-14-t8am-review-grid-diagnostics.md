# T8am Fig.5/Fig.6 Review-Grid Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fail-closed, read-only plotting and sampling-diagnostic path for the accepted 18×8 exact spin-2 and Kirchhoff review-grid artifacts, then generate exactly eight review artifacts without recomputing physics.

**Architecture:** Add a focused `schwgw.viz.tablei_review_grid` module that validates the two accepted artifact triplets, computes deterministic adjacent-sample metrics, renders near/far `2×2` figures, and writes provenance-complete sidecars and a manifest. Expose one CLI command, verify with TDD and full regression, then auto-dispatch T7bu only after exact GREEN.

**Tech Stack:** Python 3.10, NumPy, Matplotlib Agg, JSON, hashlib, pytest, Ruff, existing `schwgw` CLI, project-local `.venv`.

---

## Frozen Boundary

Read `project.md`, `status.md`, T0/T7/T8 handoffs, the approved design at
`docs/superpowers/specs/2026-07-14-t8am-t7bu-review-grid-diagnostics-design.md`,
this plan, existing visualization/CLI code, and relevant tests before editing.

Frozen source hashes:

```text
exact NPZ       a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
exact JSON      2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
exact manifest  86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
Kirchhoff NPZ   66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55
Kirchhoff JSON  0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3
Kirchhoff manifest fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632
```

Allowed implementation paths:

```text
src/schwgw/viz/tablei_review_grid.py
src/schwgw/viz/__init__.py
src/schwgw/cli.py
tests/unit/test_viz_tablei_review_grid.py
tests/regression/test_plot_review_grid_cli.py
```

Allowed generated/document paths:

```text
runs/phase5/fig5_fig6_review_grid_plots/
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-14_pre_t8am_review_grid_diagnostics.md
```

Do not modify `src/schwgw/viz/results.py`, accepted sources, solver,
scattering, IO serializers, radial/Q018 code, configs, fixtures, or unrelated
handoffs. Preserve the user's existing T1/T2/T3/T5/T6 worktree changes.

### Task 1: Establish TDD RED

**Files:**
- Create: `tests/unit/test_viz_tablei_review_grid.py`

- [ ] **Step 1: Add the failing import test**

```python
from schwgw.viz.tablei_review_grid import plot_tablei_review_grid_diagnostics


def test_review_grid_plot_api_is_importable() -> None:
    assert callable(plot_tablei_review_grid_diagnostics)
```

- [ ] **Step 2: Run the intended RED**

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_viz_tablei_review_grid.py -q
```

Expected: collection fails with `ModuleNotFoundError` for
`schwgw.viz.tablei_review_grid`. Diagnose any other failure first.

- [ ] **Step 3: Add deterministic synthetic paired-source helpers**

Use these exact shared arrays in the test file:

```python
KM = np.asarray(
    [0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75,
     2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0],
    dtype=float,
)
POINT_IDS = np.asarray([
    "near_axis_x0_z30", "near_axis_x1_z30",
    "near_axis_x2_z30", "near_axis_x3_z30",
    "far_axis_x10_z30", "far_axis_x15_z30",
    "far_axis_x20_z30", "far_axis_x25_z30",
])
POINT_GROUP = np.asarray(["near_axis"] * 4 + ["far_axis"] * 4)
POINT_X = np.asarray([0, 1, 2, 3, 10, 15, 20, 25], dtype=float)
POINT_Z = np.full(8, 30.0)
POINT_R = np.hypot(POINT_X, POINT_Z)
POINT_THETA = np.arctan2(POINT_X, POINT_Z)
PAPER_XI = 0.5 * np.sqrt(POINT_R) * np.tan(POINT_THETA)
```

Define `write_pair(tmp_path)` to write exact and Kirchhoff NPZ/JSON/manifest
triplets with the two accepted schemas, required flags, finite complex arrays,
all-true masks, and manifests containing current NPZ/JSON hashes. Use
`phase_plus = KM[:, None] * np.linspace(0.4, 2.4, 8)` and
`phase_cross = KM[:, None] * np.linspace(0.6, 2.8, 8)`. Return both NPZ paths
and the six synthetic hashes. Tests patch module `_FROZEN_SOURCE_HASHES` to
that mapping.

- [ ] **Step 4: Add exact contract tests**

Implement these test functions without placeholder assertions:

```text
test_plot_review_grid_writes_exact_eight_artifacts
test_plot_review_grid_rejects_missing_sidecar
test_plot_review_grid_rejects_source_hash_change
test_plot_review_grid_rejects_grid_mismatch
test_plot_review_grid_rejects_metadata_flag_mismatch
test_sampling_metrics_are_deterministic
test_invalid_pair_is_not_connected_or_filled
```

The success test requires exactly the eight design filenames. Failure tests
require `ReviewGridPlotError`. The diagnostics test recomputes
`1.5 * 0.1 * max(abs(diff(phase)) / diff(kM))` independently.

### Task 2: Implement Fail-Closed Loading And Metrics

**Files:**
- Create: `src/schwgw/viz/tablei_review_grid.py`
- Test: `tests/unit/test_viz_tablei_review_grid.py`

- [ ] **Step 1: Add module constants and exception**

```python
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


class ReviewGridPlotError(RuntimeError):
    """Raised when plotting cannot preserve the frozen review-grid contract."""


_EXPECTED_KM = np.asarray(
    [0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75,
     2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0],
    dtype=float,
)
_FROZEN_SOURCE_HASHES = {
    "exact_npz": "a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb",
    "exact_json": "2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537",
    "exact_manifest": "86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf",
    "kirchhoff_npz": "66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55",
    "kirchhoff_json": "0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3",
    "kirchhoff_manifest": "fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632",
}
_OUTPUT_NAMES = {
    "fig5_png": "fig5_near_axis_review_grid.png",
    "fig5_pdf": "fig5_near_axis_review_grid.pdf",
    "fig5_json": "fig5_near_axis_review_grid.json",
    "fig6_png": "fig6_far_axis_review_grid.png",
    "fig6_pdf": "fig6_far_axis_review_grid.pdf",
    "fig6_json": "fig6_far_axis_review_grid.json",
    "diagnostics": "sampling_diagnostics.json",
    "manifest": "manifest.md",
}
```

- [ ] **Step 2: Add exact hash and metadata helpers**

```python
def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _triplet(npz_path: Path) -> tuple[Path, Path, Path]:
    return (
        npz_path,
        npz_path.with_suffix(npz_path.suffix + ".json"),
        npz_path.parent / "manifest.md",
    )


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewGridPlotError(f"Cannot read JSON metadata {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReviewGridPlotError(f"Metadata must be an object: {path}")
    return value
```

- [ ] **Step 3: Implement `_load_and_validate_sources`**

Require both triplets, all six frozen hashes, exact schemas/flags, exact
frequency and point-array equality, `(18, 8)` matrix shapes, and Boolean masks.
Load embedded metadata with
`json.loads(str(data["metadata_json"].item()))`. Compare Kirchhoff embedded
metadata with a sidecar copy after removing only `output_npz_path` and
`output_npz_sha256`. Use `np.array_equal`, never tolerance comparison, for the
paired grids.

- [ ] **Step 4: Implement adjacent metrics**

```python
def _pair_metrics(values: np.ndarray, mask: np.ndarray, kM: np.ndarray) -> dict[str, Any]:
    valid = (
        mask[:-1]
        & mask[1:]
        & np.isfinite(values[:-1])
        & np.isfinite(values[1:])
    )
    absolute = np.where(valid, np.abs(np.diff(values, axis=0)), np.nan)
    scale = np.maximum(1.0, np.maximum(np.abs(values[:-1]), np.abs(values[1:])))
    relative = np.where(valid, absolute / scale, np.nan)
    slope = np.where(valid, absolute / np.diff(kM)[:, None], np.nan)
    return {
        "valid_pair": valid,
        "absolute_step": absolute,
        "relative_step": relative,
        "absolute_slope": slope,
    }
```

Build JSON-serializable maxima for each group/component with point ID and
interval. Compute `projected = 0.1 * max_slope`,
`safety_projected = 1.5 * projected`, and
`phase_proxy_pass = safety_projected < np.pi / 2`. Return
`DELTA_0P1_PROVISIONAL_REVIEW` only when all four phase proxies pass and the
source/mask/finite contract passes. Do not invent an automatic magnitude
threshold.

- [ ] **Step 5: Run metric-focused tests**

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_viz_tablei_review_grid.py -q
```

Loader/metric tests must pass before rendering is implemented.

### Task 3: Render And Write Exactly Eight Outputs

**Files:**
- Modify: `src/schwgw/viz/tablei_review_grid.py`
- Test: `tests/unit/test_viz_tablei_review_grid.py`

- [ ] **Step 1: Implement the public API**

```python
def plot_tablei_review_grid_diagnostics(
    exact_npz: str | Path,
    kirchhoff_npz: str | Path,
    *,
    output_dir: str | Path,
    dpi: int = 300,
    created_by_cli: bool = False,
) -> dict[str, Path]:
    if int(dpi) <= 0:
        raise ReviewGridPlotError("dpi must be positive")
    sources = _load_and_validate_sources(Path(exact_npz), Path(kirchhoff_npz))
    diagnostics = _sampling_diagnostics(sources)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    unexpected = sorted(p.name for p in out.iterdir() if p.name not in _OUTPUT_NAMES.values())
    if unexpected:
        raise ReviewGridPlotError(f"Output directory contains unexpected files: {unexpected}")
    paths = {key: out / name for key, name in _OUTPUT_NAMES.items()}
    _render_group(sources, "near_axis", paths["fig5_png"], paths["fig5_pdf"], int(dpi))
    _render_group(sources, "far_axis", paths["fig6_png"], paths["fig6_pdf"], int(dpi))
    paths["diagnostics"].write_text(json.dumps(diagnostics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_figure_sidecar(sources, diagnostics, "near_axis", paths, created_by_cli)
    _write_figure_sidecar(sources, diagnostics, "far_axis", paths, created_by_cli)
    paths["manifest"].write_text(_manifest_text(paths), encoding="utf-8")
    if {p.name for p in out.iterdir()} != set(_OUTPUT_NAMES.values()):
        raise ReviewGridPlotError("Review-grid output cardinality is not exactly eight")
    return paths
```

The manifest is written last and lists hashes for the other seven files.

- [ ] **Step 2: Implement the shared `2×2` renderer**

Use Matplotlib Agg, `figsize=(7.0, 5.4)`, `dpi=dpi`, and
`constrained_layout=True`. Use:

```python
colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
markers = ["o", "s", "^", "D"]
```

Panels are `|F_plus|`, `|F_cross|`, unwrapped `arg F_plus`, and unwrapped
`arg F_cross`. Exact data use markers plus a `0.8`-width solid guide through
adjacent valid saved samples. Kirchhoff uses same-point color, dashed
`1.1`-width line, and no spin marker. Split lines into contiguous valid
segments so invalid endpoints are never connected. Add `(A)`–`(D)`, `kM`,
dimensionless/radian labels, point legend, line-style key, and the subtitle
`18-point nonuniform review grid — diagnostic only`. Save one PDF and one PNG
from the same figure and close it.

- [ ] **Step 3: Implement sidecars and manifest**

Each figure JSON records both source triplets, schemas, ordered grids,
plotted arrays, masks, phase policy, palette/markers/styles, PNG/PDF hashes,
sampling recommendation, and these exact flags:

```python
{
    "read_only": True,
    "no_solver_rerun": True,
    "no_physics_recomputation": True,
    "no_interpolation": True,
    "no_smoothing": True,
    "no_fill": True,
    "review_grid_only": True,
    "not_40_frequency_production": True,
    "not_paper_style": True,
    "kirchhoff_comparison_only": True,
    "kirchhoff_polarization_independent": True,
    "exact_line_policy": "thin guide through adjacent valid saved samples only",
}
```

The manifest title is `Fig.5/Fig.6 Review-Grid Diagnostics Manifest`, states
`diagnostic-only; pending T7bu sampling review`, records six source hashes,
and lists current hashes for the seven companion files.

- [ ] **Step 4: Run unit tests and Ruff**

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_viz_tablei_review_grid.py -q
.venv/bin/python -m ruff check src/schwgw/viz/tablei_review_grid.py tests/unit/test_viz_tablei_review_grid.py
```

### Task 4: Expose API And CLI

**Files:**
- Modify: `src/schwgw/viz/__init__.py`
- Modify: `src/schwgw/cli.py`
- Create: `tests/regression/test_plot_review_grid_cli.py`

- [ ] **Step 1: Export the API**

```python
from .tablei_review_grid import (
    ReviewGridPlotError,
    plot_tablei_review_grid_diagnostics,
)
```

Add both names to `__all__`.

- [ ] **Step 2: Add CLI dispatch, handler, and parser**

Dispatch:

```python
if args.command == "plot-tablei-review-grid":
    return _plot_tablei_review_grid(args)
```

Handler:

```python
def _plot_tablei_review_grid(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import plot_tablei_review_grid_diagnostics
        plot_tablei_review_grid_diagnostics(
            args.exact_result,
            args.kirchhoff_result,
            output_dir=args.out_dir,
            dpi=args.dpi,
            created_by_cli=True,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"schwgw plot-tablei-review-grid: {exc}", file=sys.stderr)
        return 2
    return 0
```

Parser:

```python
review = subparsers.add_parser(
    "plot-tablei-review-grid",
    help="plot accepted exact and Kirchhoff Table-I review-grid diagnostics",
)
review.add_argument("exact_result", help="accepted exact review-grid NPZ")
review.add_argument("kirchhoff_result", help="accepted Kirchhoff review-grid NPZ")
review.add_argument("--out-dir", required=True, help="diagnostic output directory")
review.add_argument("--dpi", type=_positive_int, default=300)
```

- [ ] **Step 3: Add CLI regression tests**

Create a self-contained synthetic pair, patch `_FROZEN_SOURCE_HASHES`, call
`main([...])`, and require exit `0` plus exact eight filenames. A missing
Kirchhoff JSON must return exit `2` and a fail-closed stderr message.

- [ ] **Step 4: Run combined checks**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/unit/test_viz_tablei_review_grid.py tests/regression/test_plot_review_grid_cli.py
.venv/bin/python -m ruff check src/schwgw/viz/tablei_review_grid.py src/schwgw/viz/__init__.py src/schwgw/cli.py tests/unit/test_viz_tablei_review_grid.py tests/regression/test_plot_review_grid_cli.py
```

- [ ] **Step 5: Commit exactly five implementation/test paths**

```bash
git add src/schwgw/viz/tablei_review_grid.py src/schwgw/viz/__init__.py src/schwgw/cli.py tests/unit/test_viz_tablei_review_grid.py tests/regression/test_plot_review_grid_cli.py
git diff --cached --check
git diff --cached --name-status
git commit -m "feat: add Fig5 Fig6 review-grid diagnostics"
```

### Task 5: Generate And Audit Real Diagnostics

**Files:**
- Create exactly eight files under `runs/phase5/fig5_fig6_review_grid_plots/`

- [ ] **Step 1: Recheck the six frozen source hashes**

Use `shasum -a 256` on both NPZ/JSON/manifest triplets. Stop unless all six
match the Frozen Boundary section.

- [ ] **Step 2: Generate through the CLI**

```bash
PYTHONPATH=src .venv/bin/python -m schwgw.cli plot-tablei-review-grid runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz --out-dir runs/phase5/fig5_fig6_review_grid_plots --dpi 300
```

- [ ] **Step 3: Run artifact checks**

Require exactly eight files, nonblank PNGs, `%PDF-` headers, matching sidecar
and manifest hashes, frozen source hashes, finite four-proxy maxima, Boolean
proxy pass flags, one frozen recommendation label, and every no-* flag. Print:

```text
T8AM_OUTPUT_CARDINALITY_AND_HASHES=PASS
T8AM_SAMPLING_DIAGNOSTICS=PASS
```

- [ ] **Step 4: Visually inspect both PNGs**

Use the local image inspection tool. Require readable labels/legends, four
nonblank panels, distinct point colors/markers, dashed scalar Kirchhoff lines,
correct near/far points, and no invalid-gap connections. Record dimensions and
hashes.

- [ ] **Step 5: Run fresh focused, Ruff, and full pytest**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/unit/test_viz_tablei_review_grid.py tests/regression/test_plot_review_grid_cli.py
.venv/bin/python -m ruff check src/schwgw/viz/tablei_review_grid.py src/schwgw/viz/__init__.py src/schwgw/cli.py tests/unit/test_viz_tablei_review_grid.py tests/regression/test_plot_review_grid_cli.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

- [ ] **Step 6: Run forbidden checks**

```bash
git diff -- src/schwgw/scattering src/schwgw/numerics src/schwgw/io configs tests/regression/fixtures
find runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_kirchhoff_baseline_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
rg -n "schwgw\.(scattering|numerics|io)|compute_|solve_|q018|radial" src/schwgw/viz/tablei_review_grid.py
```

The first two outputs must be empty. The final scan may match only literal
no-recompute metadata text, never imports or calls.

### Task 6: Record T8am And Dispatch T7bu

**Files:**
- Modify: `status.md`
- Modify/archive: `docs/handoffs/T8_current.md`
- Create: `docs/handoffs/archive/T8_2026-07-14_pre_t8am_review_grid_diagnostics.md`

- [ ] **Step 1: Record one exact decision**

```text
GREEN / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS GENERATED
YELLOW / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS PARTIAL
RED / FIG5-FIG6 REVIEW-GRID DIAGNOSTICS BLOCKED
```

GREEN requires all source contracts, exact eight outputs, visual inspection,
sampling metrics, focused/Ruff/full pytest, scope, status, and handoff checks.

- [ ] **Step 2: Dispatch T7bu only after exact GREEN**

Send to existing T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed` with
`gpt-5.6-sol`, thinking `high`:

```text
你现在是 T7bu：Fig.5/Fig.6 review-grid diagnostics 与 production-spacing 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bu_fig5_fig6_review_grid_diagnostics_review.md。T8am 只能从已接受 T8aj/T8al artifacts 只读生成诊断图和 sampling metrics；请独立重算 metrics、核验八文件 hashes/provenance、检查 PNG/PDF 可读性与 Kirchhoff scalar 标签、运行 fresh tests，并给 T0 exact decision。不得修改实现或 artifacts，不得启动 40/79-frequency production。
```

Also notify T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636`. On any
YELLOW/RED/incomplete/ambiguous state, do not start T7bu; notify T0 only.

## T7bu Frozen Review

T7bu independently rechecks six source hashes, five-path commit scope,
no-recompute imports, all metrics/proxies, eight output hashes/provenance,
PNG/PDF legibility, exact-vs-scalar labels, focused/Ruff/full pytest, and
forbidden production scope. It modifies only `status.md`, T7 handoff, and its
archive.

Allowed decisions:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW GRID SUPPORTS DELTA KM 0.1 PRODUCTION PILOT
ACCEPT YELLOW / FIG5-FIG6 REVIEW GRID SAMPLING REMAINS UNRESOLVED
REJECT RED / FIG5-FIG6 REVIEW GRID DIAGNOSTICS INVALID
```

T7bu never repairs T8am, starts production, or pushes GitHub.

## Execution Route

The user approved direct execution in the existing T8 task. T8am uses
`executing-plans`, TDD, `scientific-visualization`, and
`verification-before-completion`. Do not ask an execution-choice question.
