# Q018 Larger-Domain Readiness Audit

Date: 2026-07-06

Thread: T4l radial ODE and matching

## 1. Scope

This audit answers one question: whether the current `kM=2`
high-`ell` `evanescent_tail_suppressed` policy is sufficient for R60_K2 or
larger observer domains than the accepted M4/M5 production domain.

It is read-only with respect to the solver.  It does not generate new
wave-field artifacts, plots, `kM=4` stress runs, R60 fixtures, or larger
domain production outputs.  It does not modify Fourier, harmonic, tetrad,
RW/Zerilli, Route B, Q005, Q014, radial threshold, or `lmax` conventions.

## 2. Source Artifact And Checksum

Source artifact:

```text
runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz
```

Manifest:

```text
runs/phase4/m4_production_first_pass/manifest.md
```

Checksum result:

```text
Expected SHA-256: a06c2e8d7f26773c790214630d3eab5f6cd09c5013ac12151ec0992b09160762
Observed SHA-256: a06c2e8d7f26773c790214630d3eab5f6cd09c5013ac12151ec0992b09160762
Result: match
```

## 3. Accepted-Domain Metadata Summary

The accepted source metadata records:

| Field | Value |
|---|---:|
| case id | `LI_FIG3_XZ_K2P0_DX0P5_PRODUCTION` |
| grid kind | `xz_plane` |
| x range | `[-30.0, 30.0]` |
| z range | `[-30.0, 30.0]` |
| spacing | `dx=dz=0.5M` |
| shape | `(121, 121)` |
| valid / invalid points | `14592 / 49` |
| `lmax` | `180` |
| `lmax_values` | `[108, 132, 156, 180]` |
| final adjacent pair | `[156, 180]`, passed |
| boundary config | `r_out=300`, `r_in_eps=1e-6`, `rtol=1e-10`, `atol=1e-12` |

The accepted production maximum radius is:

```text
r_max = sqrt(30^2 + 30^2) = 42.42640687119285 M
```

The saved Q018 warning metadata records:

| Field | Value |
|---|---:|
| warning count | `56` |
| warning code | `evanescent_tail_suppressed` |
| warning solver | `evanescent_tail_suppressed` |
| sectors | `odd`, `even` |
| `ell` range | `153..180` |
| minimum `valid_until_r` | `42.472089355131786 M` |
| maximum `valid_until_r` | `53.33351865570635 M` |
| minimum barrier action | `706.3028355047636` |
| maximum barrier action | `863.2243480839638` |
| maximum suppression bound | `1.2994970680433635e-24` |
| accepted-domain margin | `0.045682483938932705 M` |

The warning metadata has enough fields for this audit:
`sector`, `ell`, `k`, `code`, `solver`, `barrier_action`,
`valid_until_r`, `suppression_bound`, boundary/effective Wronskian/flux
residuals, raw Wronskian residual, expected flux scale, and match condition
number.

## 4. Candidate-Domain Coverage

Criterion:

```text
covered iff every relevant suppressed-mode valid_until_r > required radius
```

For the accepted `kM=2,lmax=180` source, the limiting saved value is
`min(valid_until_r)=42.472089355131786`.

| candidate | required radius | covered by current Q018 metadata? | margin |
|---|---:|---|---:|
| accepted `[-30,30]^2` | `42.42640687119285` | yes | `+0.045682483938932705` |
| x-z `[-40,40]^2` | `56.568542494923804` | no | `-14.096453139792018` |
| angular R60_K2 | `60.0` | no | `-17.527910644868214` |
| x-z `[-60,60]^2` | `84.8528137423857` | no | `-42.38072438725391` |

The current accepted-domain pass must not be extrapolated to R60_K2 or larger
x-z domains.

## 5. Targeted Radial Probe

Parameters:

```text
M=1
k=2.0
r_out=300.0
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
ell in [144, 150, 152, 153, 156, 168, 180]
sector in [odd, even]
observer radii = [42.42640687119285, 56.568542494923804, 60.0, 84.8528137423857]
```

The probe completed in `12.16 s` with no unstructured radial exceptions.

Coverage columns are ordered as:

```text
A = accepted [-30,30]^2, required r=42.42640687119285
B = x-z [-40,40]^2, required r=56.568542494923804
C = angular R60_K2, required r=60.0
D = x-z [-60,60]^2, required r=84.8528137423857
```

| ell | sector | solver | structured warning | valid_until_r | boundary residual | raw W residual | effective W residual | flux residual | expected flux scale | coverage A/B/C/D |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 144 | odd | `bidirectional_match` | no | none | `1.23e-16` | `1.08e+01` | `1.59e-16` | `1.59e-16` | `0.0` | yes/yes/yes/yes |
| 144 | even | `bidirectional_match` | no | none | `1.50e-16` | `2.57e+01` | `1.50e-16` | `1.50e-16` | `0.0` | yes/yes/yes/yes |
| 150 | odd | `bidirectional_match` | no | none | `1.72e-16` | `1.01e+01` | `2.39e-16` | `2.39e-16` | `0.0` | yes/yes/yes/yes |
| 150 | even | `bidirectional_match` | no | none | `1.20e-16` | `1.14e+01` | `3.67e-16` | `3.67e-16` | `0.0` | yes/yes/yes/yes |
| 152 | odd | `bidirectional_match` | no | none | `2.11e-16` | `8.06e+00` | `4.42e-16` | `4.42e-16` | `0.0` | yes/yes/yes/yes |
| 152 | even | `bidirectional_match` | no | none | `1.00e-16` | `1.29e+01` | `1.48e-16` | `1.48e-16` | `0.0` | yes/yes/yes/yes |
| 153 | odd | `evanescent_tail_suppressed` | yes | `42.47208937473273` | `1.30e-24` | `0.0` | `1.30e-24` | `1.30e-24` | `0.0` | yes/no/no/no |
| 153 | even | `evanescent_tail_suppressed` | yes | `42.472089355131786` | `1.30e-24` | `0.0` | `1.30e-24` | `1.30e-24` | `0.0` | yes/no/no/no |
| 156 | odd | `evanescent_tail_suppressed` | yes | `43.65426908502512` | `1.26e-24` | `0.0` | `1.26e-24` | `1.26e-24` | `0.0` | yes/no/no/no |
| 156 | even | `evanescent_tail_suppressed` | yes | `43.65426906687423` | `1.26e-24` | `0.0` | `1.26e-24` | `1.26e-24` | `0.0` | yes/no/no/no |
| 168 | odd | `evanescent_tail_suppressed` | yes | `48.46415897852191` | `1.27e-24` | `0.0` | `1.27e-24` | `1.27e-24` | `0.0` | yes/no/no/no |
| 168 | even | `evanescent_tail_suppressed` | yes | `48.46415896491557` | `1.27e-24` | `0.0` | `1.27e-24` | `1.27e-24` | `0.0` | yes/no/no/no |
| 180 | odd | `evanescent_tail_suppressed` | yes | `53.33351865570635` | `1.25e-24` | `0.0` | `1.25e-24` | `1.25e-24` | `0.0` | yes/no/no/no |
| 180 | even | `evanescent_tail_suppressed` | yes | `53.33351864532575` | `1.25e-24` | `0.0` | `1.25e-24` | `1.25e-24` | `0.0` | yes/no/no/no |

The regular `bidirectional_match` modes cover the candidate radii because the
radial solution is defined out to `r_out=300`.  The limiting factor for
larger-domain readiness is the structured suppression domain of `ell>=153`.

## 6. Classification

Classification: **YELLOW**.

Reason:

- The accepted `[-30,30]^2` production domain remains covered.
- The accepted source checksum matches the manifest.
- Q018 warning metadata is present and structured.
- The targeted probe has no unstructured radial failure.
- R60_K2 and larger domains are not covered because at least one relevant
  suppressed mode has `valid_until_r < 60.0`.  The first suppressed even mode
  has `valid_until_r=42.472089355131786`, and even the `ell=180` modes only
  reach about `53.3335`, still below R60.

This is not a RED result because current accepted-domain metadata is
consistent.  It is not GREEN because the current Q018 policy does not certify
R60_K2 or any larger candidate domain.

## 7. Next Recommendation

Before any R60_K2 production run or larger-domain T8 run, open a new T4 method
hardening slice.  The next slice should make the Q018 policy
evaluation-radius aware and should choose one of these defensible methods:

1. Rescaled/log-domain radial propagation through the requested observer
   radius for modes whose current `valid_until_r` is too small.
2. A conservative WKB tail-bound policy evaluated at the requested observer
   radius, with explicit spin-2 RW/Zerilli and reconstruction prefactor
   accounting.
3. A no-go record showing that R60_K2 needs a larger radial architecture
   before production artifacts are allowed.

For R60_K2 specifically, the next T4 slice must require every suppressed mode
needed by the selected `k=2,lmax` policy to satisfy `valid_until_r > 60.0`, or
must replace the current zero-field suppression by a reviewed bound/solver
that is valid at `r=60`.

Suggested review handoff after this audit:

```text
你现在是 T7ag。请读取并严格执行 docs/prompts/phase5_t7ag_q018_larger_domain_readiness_review.md。
```

Do not open R60_K2, larger-domain production, or `kM=4` from this report
without T7ag review.

## 8. Explicit kM=4 Non-Validation

This report does not validate `kM=4`.  The diagnostics here are only for
`kM=2`, the accepted M4 source artifact, and targeted `k=2,r_out=300` radial
probes.  No conclusion about `kM=4` stress, its required `lmax`, its
centrifugal barrier structure, or its observer-domain coverage follows from
this audit.

## 9. Commands

```bash
shasum -a 256 runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz

PYTHONPATH=src /opt/homebrew/bin/python3 - <<'PY'
# Load accepted kM=2 NPZ, parse metadata_json, extract grid/lmax/warning
# metadata, and compute min(valid_until_r)-rmax.
PY

PYTHONPATH=src /opt/homebrew/bin/python3 - <<'PY'
# Run targeted radial probes for ell=[144,150,152,153,156,168,180],
# sector=[odd,even], k=2, r_out=300, and assess candidate coverage.
PY
```

The full pytest command required by the prompt should be recorded in
`status.md` with its final result.
