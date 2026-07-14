# Phase 5 kM=4 Table-I Radial/Q018 Preflight

Date: 2026-07-09

Thread: T4v radial solver and Q018 preflight.

## Decision Label

```text
YELLOW / KM4 TABLE-I PREFLIGHT NEEDS RADIAL METHOD FOLLOWUP
```

The existing radial solver/Q018 policy does not yet support a later
eight-point conservative Table-I review-grid scan up to `kM=4`.

The gate blocker is an uncovered Q018/evanescent-tail branch at `kM=4`:
representative odd/even modes in the continuous high-barrier band
`ell=178..240` fail with
`evanescent_tail_required_radius_uncovered` because their certified
`valid_until_r` is below the largest Table-I radius
`39.051248M`.

No dense production artifact, field map, plot, fixture, Kirchhoff baseline, or
full frequency scan was generated.

## Matrix Covered

Physical Table-I points:

| point | `x/M` | `z/M` | `r/M` |
|---|---:|---:|---:|
| near0 | 0 | 30 | 30.000000 |
| near1 | 1 | 30 | 30.016662 |
| near2 | 2 | 30 | 30.066593 |
| near3 | 3 | 30 | 30.149627 |
| far10 | 10 | 30 | 31.622777 |
| far15 | 15 | 30 | 33.541020 |
| far20 | 20 | 30 | 36.055513 |
| far25 | 25 | 30 | 39.051248 |

Boundary settings actually evaluated:

```text
M=1
r_in_eps=1e-6
r_out=300
rtol=1e-10
atol=1e-12
required_eval_radius=39.051248
experimental_required_radius_oracle=None
```

Q018 oracle setting:

```text
No q018_riccati oracle was requested.
```

Reason: the reviewed `q018_riccati` production envelope remains limited to
`kM=2`, `required_eval_radius=60`, `r_out=300`, and `ell=153..180`.  It is not
a reviewed `kM=4` or Table-I-radius oracle.

Evaluated radial modes:

| frequency | ell probes evaluated | sectors |
|---:|---|---|
| `kM=4.0` | `108,120,132,145,157,169,178,180,204,228,240,241,252,300,336,360` | odd/even |
| `kM=2.0` anchor | `48,60,67,72,79,91,153,156,168,180` | odd/even |

The first large-matrix attempt constructed the full barrier-action-triggered
candidate matrix:

| `kM` | `L_seed` | base ell probes | first `S>=706` ell | continuous candidate band | ell count |
|---:|---:|---|---:|---|---:|
| 2.0 | 180 | `48,60,67,72,79,91,156,180` | 153 | `153..180` | 34 |
| 2.5 | 228 | `63,75,86,87,98,110,204,228` | 161 | `161..228` | 74 |
| 3.0 | 276 | `78,90,102,106,118,130,252,276` | 167 | `167..276` | 116 |
| 3.5 | 324 | `93,105,117,125,137,149,300,324` | 173 | `173..324` | 158 |
| 4.0 | 360 | `108,120,132,145,157,169,336,360` | 178 | `178..360` | 189 |

That full candidate matrix would require 1142 radial solves.  It was ordered
with `kM=4` first and was stopped after the `kM=4` gate showed the uncovered
branch.  The interrupted attempt reached 378 `kM=4` sector-mode records and
showed 126 failures before any broadening to the lower frequencies.

Metadata-only diagnostic JSON:

```text
runs/phase5/km4_tablei_radial_q018_preflight/radial_q018_preflight_metadata.json
```

This JSON contains scalar diagnostics/provenance only.  It does not contain
field arrays, dense scan arrays, plots, NPZ/HDF5 production data, or
Kirchhoff values.

## Diagnostics

Summary over the targeted metadata JSON:

| quantity | value |
|---|---:|
| total records | 52 |
| ok records | 42 |
| error records | 10 |
| `bidirectional_match` records | 24 |
| `evanescent_tail_suppressed` records | 18 |
| warning records | 18 |
| warning code | `evanescent_tail_suppressed` |
| total targeted runtime | `44.52821966699412 s` |

The 10 errors are all structured radial no-go failures:

```text
code = evanescent_tail_required_radius_uncovered
```

They occur only in the sampled `kM=4` high-barrier transition from normal
bidirectional matching to certified evanescent-tail suppression:

| `kM` | sector | ell | `valid_until_r` | required radius | barrier action | local tail action |
|---:|---|---:|---:|---:|---:|---:|
| 4.0 | odd | 178 | 26.055783749097 | 39.051248 | 708.036557877458 | 55.022399352497 |
| 4.0 | even | 178 | 26.055783738640 | 39.051248 | 708.036557883478 | 55.022399349911 |
| 4.0 | odd | 180 | 26.465206738395 | 39.051248 | 718.433054866314 | 55.002962341326 |
| 4.0 | even | 180 | 26.465206728375 | 39.051248 | 718.433054864482 | 55.002962338902 |
| 4.0 | odd | 204 | 31.396533404753 | 39.051248 | 844.759545117400 | 55.000132810381 |
| 4.0 | even | 204 | 31.396533398590 | 39.051248 | 844.759545116209 | 55.000132809017 |
| 4.0 | odd | 228 | 36.417786629630 | 39.051248 | 973.898230264151 | 55.013655552127 |
| 4.0 | even | 228 | 36.417786625625 | 39.051248 | 973.898230266161 | 55.013655551372 |
| 4.0 | odd | 240 | 38.960770674893 | 39.051248 | 1039.424466491339 | 55.005454315185 |
| 4.0 | even | 240 | 38.960770671617 | 39.051248 | 1039.424466490815 | 55.005454314585 |

Representative `kM=4` successful records:

| ell | branch | sectors | Table-I finite | diagnostic scale |
|---:|---|---|---|---|
| 108 | `bidirectional_match` | odd/even | yes | Wronskian and boundary residuals `~1e-16` |
| 120 | `bidirectional_match` | odd/even | yes | Wronskian and boundary residuals `~1e-16` |
| 132 | `bidirectional_match` | odd/even | yes | Wronskian and boundary residuals `~1e-16` |
| 145 | `bidirectional_match` | odd/even | yes | Wronskian and boundary residuals `~1e-16` |
| 157 | `bidirectional_match` | odd/even | yes | Wronskian and boundary residuals `~1e-16` |
| 169 | `bidirectional_match` | odd/even | yes | Wronskian and boundary residuals `~1e-16` |
| 241 | `evanescent_tail_suppressed` | odd/even | yes | `valid_until_r=39.1711277 > 39.051248` |
| 252 | `evanescent_tail_suppressed` | odd/even | yes | `valid_until_r=41.5147452 > 39.051248` |
| 300 | `evanescent_tail_suppressed` | odd/even | yes | `valid_until_r=51.8926904 > 39.051248` |
| 336 | `evanescent_tail_suppressed` | odd/even | yes | `valid_until_r=59.7956187 > 39.051248` |
| 360 | `evanescent_tail_suppressed` | odd/even | yes | `valid_until_r=65.1155562 > 39.051248` |

The sampled `kM=2` anchor comparison is consistent with the accepted
same-domain behavior:

| branch | records | notes |
|---|---:|---|
| `bidirectional_match` | 12 | finite at all Table-I radii |
| `evanescent_tail_suppressed` | 8 | sampled `ell=153,156,168,180`; all finite at Table-I radii because `required_eval_radius=39.051248` is covered |

## kM=4 Gate

The `kM=4` gate does not pass.

The preflight found no nonfinite radial values in successful records, but it
found a structured uncovered radial branch before all required high-ell modes
could be certified:

```text
evanescent_tail_required_radius_uncovered
```

This appears for odd/even `ell=178,180,204,228,240` in the targeted
representative sample.  The first large-matrix attempt also showed 126
`kM=4` failures while sweeping the continuous high-barrier candidate band,
before the suppression policy became valid again near `ell=241`.

Therefore `kM=4` does have an uncovered Q018/evanescent-tail branch at the
required Table-I radii.

## T8 Readiness Recommendation

T8 should not run the conservative eight-point review-grid scan yet.

T4 followup is required first.  The existing solver needs one of:

- a reviewed target-radius-aware radial method for the uncovered `kM=4`
  transition band;
- a reviewed spin-2 observable-level tail bound that covers this band at the
  Table-I radii;
- or a revised, reviewed production policy that can represent the finite
  transition contribution without hiding it behind `ell_max` truncation or
  threshold relaxation.

The current result is suitable for T7bn batch gate review together with the
already completed T1j Kirchhoff convention freeze.  It is not sufficient to
authorize dense Fig.5/Fig.6 production.

## Non-Claims

This preflight does not claim or authorize:

- dense Fig.5/Fig.6 production;
- a 40-frequency `Mk` scan;
- `dx=0.2M`;
- R60_K4;
- full `kM=4` production readiness;
- dense field maps;
- plots or fixtures;
- Kirchhoff values or Kirchhoff dashed curves;
- Appendix D/E curves;
- paper-level Fig.5/Fig.6 reproduction;
- threshold, `lmax`, boundary, Q018, or physics-convention changes.

The T1j Kirchhoff convention freeze is independent and still required for any
future Kirchhoff implementation.  T1j has already frozen the convention, but
T4v does not implement or validate Kirchhoff numerics.

## Verification Commands

Relevant radial/Q018 test required by the prompt:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py
```

Additional required file/static checks are recorded in `status.md` and the T4
handoff for this thread.
