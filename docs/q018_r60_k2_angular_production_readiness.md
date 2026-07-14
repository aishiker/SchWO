# Q018 R60_K2 Angular Production Readiness

Date: 2026-07-07

Thread: T8w visualization and CLI schema/readiness

Status: readiness only. This document does not authorize a production run.

## 1. Accepted Evidence And Limits

T7aq independently accepted the bounded T8v angular-grid pilot as:

```text
ACCEPT GREEN FOR BOUNDED R60_K2 ANGULAR-GRID PILOT ONLY
```

The accepted artifact was:

```text
runs/phase5/q018_r60_k2_angular_pilot/r60_k2_q018_angular_pilot.npz
```

It covered `r=60`, `kM=2`, `lmax=180`, Q018 explicit opt-in
`experimental_required_radius_oracle=q018_riccati`, and a bounded
`17 x 8 = 136` angular grid. T7aq verified finite saved complex fields,
final adjacent pair `[156,180]` passing the selected and near-axis thresholds,
default fail-closed behavior without the oracle, direct selected-point
recomputation, and serialized oracle provenance for the continuous
`ell=153..180`, odd/even suppressed band.

This evidence does not validate full R60 production, `R60_K4`, `kM=4`,
larger domains, arbitrary incident direction, plotting, fixtures, scalar-only
tail arguments, or any threshold/`lmax` policy change.

## 2. Proposed Production Candidate

Draft config:

```text
configs/r60_k2_q018_angular_production_first_pass.yaml
```

Proposed output path if a later authorized slice runs it:

```text
runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz
```

This T8w slice creates the config draft only. It does not run it and does not
create the production NPZ.

## 3. Grid Definition

The proposed observer grid is angular at fixed radius:

| field | value |
|---|---:|
| `r` | `60.0` |
| `theta_range` | `0..pi`, step `pi/64`, `endpoint=true` |
| `theta` count | `65` |
| `phi_range` | `0..2pi`, step `2pi/64`, `endpoint=false` |
| `phi` count | `64` |
| total points | `4160` |

The `theta` endpoint policy includes both poles. The `phi` endpoint policy
excludes `2pi`, suitable for periodic azimuthal sampling without duplicating
`phi=0`.

The production draft uses an explicit selected convergence subset matching
the accepted T8v `17 x 8` angular pilot probes. That is not full-grid
convergence acceptance. A later production authorization must decide whether
the selected subset is sufficient or whether full `65 x 64` convergence
probes are required.

## 4. Runtime And Storage Estimate

T8v observed runtime:

```text
136 points, about 425.48 s
```

The production candidate has:

```text
4160 points
4160 / 136 = 30.58823529411765
```

Linear point-count scaling gives:

```text
425.48 s * 30.58823529411765 = 13016.452941176472 s ~= 3.6 h
```

This is a rough estimate before reruns, review probes, filesystem overhead,
or any additional convergence expansion. The radial cache expectation is that
the unique radial solves remain `358` for the same `k`, `lmax`, boundary, and
Q018 opt-in settings, while cache hits scale with angular point count.

The accepted T8v pilot NPZ size was about `482638 bytes` for 136 points.
Direct point scaling suggests roughly `15 MB` for 4160 points, but metadata,
diagnostic histories, compression behavior, and provenance records can move
that number. Budget at least tens of MB plus logs and any later review
sidecars.

## 5. Acceptance Gates Before Production

Before any production run is allowed:

- T7ar must independently review this readiness slice.
- T0 must explicitly authorize the production run.
- The production run must remain project-local.
- The final adjacent pair must pass the selected-probe threshold `<1e-4` and
  near-axis threshold `<1e-3`.
- Q018 provenance must serialize every used oracle mode for `ell=153..180`,
  odd/even, with `required_eval_radius=60.0`,
  `experimental_required_radius_oracle=q018_riccati`,
  `valid_at_required_radius=True`, and
  `unit_incoming_at_infinity=True`.
- Default fail-closed behavior without the oracle must remain tested.
- Unknown opt-in and out-of-envelope opt-in requests must remain fail-closed.
- No `kM=4`, `R60_K4`, larger-domain, arbitrary-direction, plotting, or
  fixture expansion may be bundled into the production authorization.
- The production artifact must not be described as accepted until independent
  review verifies schema, metadata, convergence, finite fields, provenance,
  static import boundaries, and output scope.

## 6. T8w Readiness Slice Boundary

T8w only adds angular range schema support, a small runnable range-schema
smoke config, this production config draft, and this readiness document. It
does not authorize or perform full R60 production.
