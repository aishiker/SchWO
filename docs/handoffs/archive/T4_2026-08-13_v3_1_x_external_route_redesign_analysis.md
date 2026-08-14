# T4 archive — V3.1-X external direct-route redesign analysis

Date: 2026-08-13

Task: formal T4, zero-science/read-only design analysis

Gate candidate: `phase6_v3_1_x_external_direct_route_redesign_v1`

## Outcome

T4 completed the frozen redesign-analysis prompt without launching Wolfram,
BHPT, AP, Route A/U/B/C, or any solver. No dispatch, evidence, sentinel,
official or staging root was created. Only the analysis, this archive and the
authorized `T4_current` prepend were written.

The complete design is:

`docs/phase6_v3_1_x_external_route_redesign_analysis.md`

Key conclusions:

1. The failed sentinel has 23 one-call outcomes, 14 PASS and nine native
   `MST_FAILED` errors at ordinals `0..7,17`.
2. The eight errors at `kM=0.1/0.5` were supplied MachinePrecision frequency
   inputs despite the nominal 90-digit request. The remaining `(2,18,odd)`
   error is `cause_not_proven`.
3. The wrapper's separate `amplitude identity mismatch` is a downstream
   redundant-serialization tolerance defect and is noncausal to the nine raw
   errors.
4. The exact 23-key compact inventory hash is
   `5e93fca57b6d4fb82762043fedea4631de92111164c8c4a991d76925e3867c76`.
5. The recommended distinct route uses fresh BHPT
   `Method -> {"NumericalIntegration",...}` for every key, independently
   integrates `In/Up`, extracts amplitudes by a three-radius Wronskian
   decomposition, and keeps direct `Gamma_flux` separate from `Gamma_S`.
6. A node-local, source-hashed boundary-location overlay is required because
   pristine BHPT hardcodes `rin` and `rout`. Only the odd boundary literals in
   `Kernel/NumericalIntegration.m` may differ; equations, integrator and all
   other source bytes remain external BHPT.
7. The official design is no-selection: seven nodes per key, exactly 161 API
   calls/322 boundary solves/483 match records. The predeclared sentinel is all
   23 selected nodes plus full ladders at two fixed geometry extrema, exactly
   35 calls; sentinel values are never reused officially.
8. Existing immutable timing yields a central Route-C estimate near 74
   minutes and an observed-max envelope near 7.7 wall hours, but the extended
   boundary geometry is outside stored timing evidence. A separately reviewed
   sentinel-derived projection must remain within the 36-hour cap.

## Governance boundary

This is not repair cycle 3, a retry, implementation, science, T7 acceptance,
V3.2 or global GREEN. The failed sentinel and all predecessor science remain
immutable, non-resumable and non-reusable. Root T0 must freeze a distinct
package and obtain formal T7 package review before any implementation or
numerical execution.

The start authority hashes, exact source/evidence identities, equations,
ladder, publication protocol, future six-file implementation scope and formal
package graph are recorded in the main analysis. Final non-circular output
hashes are reported in the T4 checkpoint returned to Root T0.

