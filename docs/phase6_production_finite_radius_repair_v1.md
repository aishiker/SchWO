# Phase 6 V1 production eight-radius repair diagnostic

## Scope

This isolated diagnostic consumes, read-only, the immutable production
finite-radius campaign at
`runs/phase6/radial_validation/v1_production_finite_radius_campaign_v1_20260808_py314`.
It validates that campaign and enumerates exactly its 3,382 missing-state modes.
The predecessor result and manifest SHA-256 values are respectively
`eb089da8bf1ac947dc56c3f44fc5eef7856c6b7d21a7f63e676801b24d952a3f`
and
`f214d97d792bb90e51ecf914c4ddb4d77f209472e66768c03a6cdef68bef3cfe`.
The repair inventory SHA-256 is
`e39a6b9ab94514d7ac3dd7f3e7f341b8222e4b725834701d3d690dd12a9d0e02`.

Each selected production key is evaluated exactly once with
`scaled_tortoise_radial.py`.  The single request contains the minimum Table-I
radius as `required_radius` and the other seven exact radii as
`evaluation_radii`.  It therefore produces one radial trajectory, not eight
separate integrations.  The predecessor's generic supported `r_out` is reused;
no paper-specific Q018 envelope, Riccati variable, Newman-Penrose path, or
pseudoinverse is permitted.

## Evidence boundary

The records contain the complex radial state, derivative, log amplitudes,
phase/status fields, radial S quantity, transmission quantity, and internal
signed-current/flux diagnostics at the exact production radii.  They are
production radial-state diagnostics only.  They do not establish an
observer-qualified tidal response, detector response, infinity waveform,
tetrad/polarization convention, independent-solver agreement, or closed
numerical uncertainty budget.

Accordingly every record and run summary has
`scientific_acceptance=false` and `global_green_permitted=false`.  Numerical
and convention uncertainties are separate and remain unclosed or
`NOT_ASSESSED`.  A structurally complete run is at most `PARTIAL`; a backend
failure makes the run `FAIL` and remains in the failure ledger.

## Protocol

The runner uses one nonblocking filesystem writer lock, an O_EXCL publication
path, canonical JSON, per-key fsync, strict no-overwrite resume, implementation
source SHA-256 bindings, immutable 0444 files, and a terminal 0555 root.  A
partial root may be resumed only with the identical selection, source bytes,
Python identity, and predecessor campaign.  Completed roots are reloaded and
validated rather than republished.

For a smoke diagnostic:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_run_production_finite_radius_repair.py \
  --output-root runs/phase6/radial_validation/<fresh-smoke-root> \
  --limit 2
```

For the full inventory, omit `--limit` and use a fresh root.  A limited root is
contractually distinct and cannot later be expanded into a full run.  The full
3,382-mode run requires explicit T0 authorization after smoke review.
