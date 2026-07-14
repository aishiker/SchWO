# Phase 5 kM=4 Table-I Adapter Closeout

Date: 2026-07-09

Thread: T12 Fig.5/Fig.6 autonomous gated pipeline, Stage 1.

## Decision Label

```text
YELLOW / PIPELINE PARTIAL - NEXT GATE IDENTIFIED
```

Stage 1 did not pass.  No `q018_tablei_km4_transition` production adapter was
implemented, and the pipeline did not continue to Stage 2.

## Required Pre-Implementation Scan

The Stage 1 prompt required measuring the continuous default fail-closed set
before implementing any adapter, using:

```text
BoundaryConfig(required_eval_radius=39.051248, r_out=300,
               r_in_eps=1e-6, rtol=1e-10, atol=1e-12)
```

for `kM=4`, `ell=2..360`, odd/even sectors.

The scan was started with default no-oracle production behavior.  It reached
the printed progress checkpoint:

```text
ell=160
summary={
  default_covered: 318,
  default_fail_closed_uncovered: 0,
  default_error_other: 0,
  evanescent_tail_suppressed_radius_covered: 0
}
```

Before the next checkpoint, the scan aborted in the transition region with a
non-structured numerical exception:

```text
numpy.linalg.LinAlgError: SVD did not converge
```

The reproduced first blocker is:

```text
kM=4
required_eval_radius=39.051248
ell=177
sector=odd/even
default error type=LinAlgError
location=bidirectional fallback condition-number SVD
barrier_action ~= 702.798961
```

This is not the allowed fail-closed code:

```text
evanescent_tail_required_radius_uncovered
```

Therefore Stage 1 hit the prompt stop condition:

```text
Stop YELLOW if any non-uncovered default error appears.
```

## Focused Diagnostics

The direct experimental oracle was also probed for the reproduced blocker
modes, only to diagnose the stop.  It was not used to bypass the default-path
error.

| sector | ell | direct oracle status | finite fields | max residual scale |
|---|---:|---|---|---:|
| odd | 177 | ok | yes | `1.783242004625387e-16` |
| even | 177 | ok | yes | `1.145901331977054e-16` |

This suggests the Riccati/log-derivative method can probably cover the
`ell=177` transition mode, but the Stage 1 adapter gate requires the default
scan to classify all required modes without non-uncovered errors.  The
unstructured default error must be handled in a separate radial-method or
error-structuring slice before a production adapter can be reviewed.

Metadata-only blocker record:

```text
runs/phase5/km4_tablei_adapter_validation/stage1_yellow_blocker_metadata.json
```

## Non-Claims

This closeout does not claim or authorize:

- `kM=4` production adapter support;
- `q018_tablei_km4_transition` implementation;
- T8 conservative review-grid scan;
- dense Fig.5/Fig.6 production;
- 40-frequency scan;
- field maps, plots, fixtures, NPZ/HDF5 production artifacts, or Kirchhoff values;
- threshold, `lmax`, boundary, Q018, or physics-convention changes.

## Recommendation

Stop the autonomous Fig.5/Fig.6 pipeline here.  The next gate should be a
focused T4 radial slice that either:

- makes the `ell=177` bidirectional fallback failure a structured no-go
  without weakening the Q018 policy; or
- extends the reviewed Riccati/log-derivative adapter design to a precisely
  measured continuous transition envelope that includes all default failures
  and is then independently reviewed.

Only after that radial gate passes should the Stage 1 adapter implementation
be retried.
