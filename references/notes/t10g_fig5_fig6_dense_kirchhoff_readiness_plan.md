# T10g Fig.5/Fig.6 Dense Scan And Kirchhoff Readiness Plan

Date: 2026-07-08

Thread: T10g, literature / numerical-method planning support.

Status label: **YELLOW / PLAN READY WITH EXPLICIT OPEN RISKS**

Scope: planning only.  No solver was run, no artifacts were created, and no
source/test/config/run files were modified.

## 1. Established Facts

- Li-Hou-Zhao use `G=c=M=1`, Fourier factor `exp(-i k t)`, and a default
  incident plane wave along `+z`.
- The project freezes the same Fourier convention in `docs/physics_spec.md`.
- Production polarization uses packaged plus/cross ratios from Route B:
  `F_plus_complex = h_plus_lensed / h_plus_unlensed` and
  `F_cross_complex = h_cross_lensed / h_cross_unlensed`.
- The accepted M5 archive covers only four frequencies:
  `kM = [0.5, 1.0, 1.5, 2.0]`.
- The accepted Table-I extraction covers eight exact grid points at `z=30M`:
  `x/M = [0, 1, 2, 3, 10, 15, 20, 25]`.
- The accepted T8ad reporting PNG/CSV/Markdown artifacts are explicitly
  four-frequency read-only pilots.  They do not include a dense `Mk` scan,
  do not include `kM=4`, and do not include Kirchhoff Eq. (47).
- Q018 currently gives reviewed protection for the accepted `kM=2` bounded
  cases, including the later opt-in oracle boundary recorded in project docs.
  It does not validate `kM=4`, a dense frequency scan, or a larger requested
  high-ell range.

## 2. Why T8ad Fig.5/Fig.6 Looks Simple

The T8ad plots look simple because the input data are simple by design, not
because the plotting layer failed.

The accepted reporting files contain only four frequency samples per Table-I
point.  A curve made from `kM=[0.5,1.0,1.5,2.0]` cannot reproduce the marker
density, oscillatory structure, or dashed comparison curves of paper Fig.5 and
Fig.6.  The sidecars also intentionally record `no_kM4`, `no_kirchhoff`,
`not_dense`, and read-only provenance flags.

Therefore the current plots are useful smoke/reporting fixtures for the
Table-I extraction schema, but they are not paper-level Fig.5/Fig.6
reproductions.

## 3. Paper Fig.5/Fig.6 Requirements From Local Notes

Established from local notes:

- Fig.5 uses the four near-axis Table-I points:
  `(x,z)/M = (0,30), (1,30), (2,30), (3,30)`.
- Fig.6 uses the four far-axis Table-I points:
  `(x,z)/M = (10,30), (15,30), (20,30), (25,30)`.
- Both figures require frequency-dependent amplification magnitude and phase.
- The paper states a calculation range from roughly `k=0.1/M` to `4.0/M`.
- The paper compares exact wave-optics results with a Kirchhoff approximation
  curve.

Inference from raster figure density, not an established paper parameter:

- Exact markers are plausibly sampled with `Delta(kM) ~ 0.1`, giving about
  40 frequency samples over `[0.1,4.0]`.
- The Kirchhoff dashed curves were probably evaluated on a finer plotting grid
  than the exact markers.
- Fig.6 may need either `Delta(kM)=0.1` plus review, or a denser fallback such
  as `Delta(kM)=0.05`, because the far-axis phase structure can oscillate
  faster than the near-axis curves.

Table-I radii for preflight:

| Label | `(x,z)/M` | `r/M` |
|---|---:|---:|
| near0 | `(0,30)` | `30.000000` |
| near1 | `(1,30)` | `30.016662` |
| near2 | `(2,30)` | `30.066593` |
| near3 | `(3,30)` | `30.149627` |
| far10 | `(10,30)` | `31.622777` |
| far15 | `(15,30)` | `33.541020` |
| far20 | `(20,30)` | `36.055513` |
| far25 | `(25,30)` | `39.051248` |

## 4. Dense Mk Scan Candidate Design

### 4.1 Conservative Review Grid

Use this grid for the first dense-readiness pilot after T7be accepts the plan:

```text
kM_review =
  [0.1, 0.2, 0.3, 0.5,
   0.75, 1.0, 1.25, 1.5, 1.75, 2.0,
   2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0]
```

Purpose:

- Covers the paper range `[0.1,4.0]`.
- Reuses all accepted anchor frequencies except that `0.5,1.0,1.5,2.0`
  remain comparison anchors, not proof for higher frequencies.
- Explicitly includes `kM=4`.
- Keeps the first high-frequency stress test below the full production count.

This grid is not yet paper-level; it is a review grid for T4/T7/T8 readiness.

### 4.2 Production-Like Grid

Use this grid only after the `kM=4` and Q018 gates are reviewed:

```text
kM_production = [0.1, 0.2, ..., 3.9, 4.0]
```

That is 40 exact frequencies with `Delta(kM)=0.1`.

Optional escalation if T7 finds phase aliasing in Fig.6:

```text
kM_production_fine = [0.10, 0.15, 0.20, ..., 3.95, 4.00]
```

That is 79 exact frequencies with `Delta(kM)=0.05`.  It should not be the
first production attempt unless the review grid shows that `Delta(kM)=0.1`
misses oscillatory structure.

### 4.3 kM=4 Handling

`kM=4` is a gate frequency, not just the last element of a frequency list.
Before any dense production is accepted, T4/T7 should verify:

- odd and even sectors at `kM=4`;
- the Table-I radii up to `r=39.051248M`;
- the final requested `lmax` window, not merely modes near `ell ~= k r`;
- final adjacent-pair convergence in the observable complex ratios;
- Q018 metadata with no unreviewed uncovered high-ell evanescent-tail branch.

### 4.4 Adaptive lmax Policy

Do not set `lmax` only by the scalar rule `ellmax ~= k r`.  The scalar
finite-radius result is a useful prior, but spin-2 observables contain
odd/even master variables, tensor angular factors, reconstruction, and
packaged tidal projections.

Recommended seed rule for Table-I dense planning:

```text
L_seed(kM) = ceil_to_multiple_of_12(max(84, 90*kM))
```

This gives:

- `L_seed(0.5)=84`, matching the accepted low-frequency floor.
- `L_seed(1.0)=96`, then allow an anchor override to include the accepted
  `lmax=108`.
- `L_seed(1.5)=144`, then allow an anchor override to include the accepted
  `lmax=156`.
- `L_seed(2.0)=180`, matching the accepted four-frequency upper anchor.
- `L_seed(4.0)=360`, giving an explicit high-frequency stress target.

For each frequency, compute or reuse partial sums at:

```text
lmax_values =
  sorted unique values among
  [L_seed-72, L_seed-48, L_seed-24, L_seed]
  plus accepted anchors when kM in [0.5,1.0,1.5,2.0]
  with all values clipped to lmax >= 24.
```

Acceptance must depend on final adjacent-pair convergence, not on the seed
rule itself.  A frequency passes only if the last two retained `lmax` values
pass the existing selected-probe thresholds for complex `F_plus` and `F_cross`
at all eight Table-I points, with near-axis cases checked against the stricter
near-axis warning policy already used in project docs.

If the final pair fails, the frequency should extend by `+24` or `+48` in
`lmax` and rerun only after T4/T7 confirm radial/Q018 coverage for the new
band.

### 4.5 Per-Frequency Metadata

Each frequency sidecar should record at minimum:

- requested `kM`;
- exact point list and point labels;
- `lmax_values`, final accepted `lmax`, and final adjacent-pair deltas;
- odd/even sector diagnostics;
- radial cache metadata and any radial warnings;
- Q018 branch used, including oracle name/version if opt-in is used;
- source artifact path/hash if the dense point extraction reads a saved
  polarization artifact;
- invalid-denominator masks for plus/cross separately;
- complex ratios, absolute values, principal phases, unwrapped phases, and
  phase unwrap segment IDs;
- no-interpolation/no-smoothing/no-fill flags;
- Kirchhoff comparison version if present, or an explicit `no_kirchhoff` flag.

### 4.6 Stop Conditions

Stop the dense scan and return to T4/T7 if any of the following occurs:

- nonfinite radial or polarization output at any Table-I point;
- unreviewed `evanescent_tail_required_radius_uncovered` or equivalent Q018
  fail-closed event;
- inconsistent odd/even sector convention metadata;
- final adjacent-pair convergence fails after one reviewed `lmax` extension;
- `kM=4` requires a radial method not already reviewed for production;
- Kirchhoff Eq. (47) branch conventions remain unfrozen but a plotting/reporting
  task tries to include dashed Kirchhoff curves;
- sidecar provenance cannot identify source data and code/config hashes.

## 5. Radial/Q018 And kM=4 Gate

The four-frequency acceptance does not validate `kM=4`.  It only establishes
that the existing four archived frequencies are internally consistent for the
accepted M5/Table-I reporting scope.

Minimal T4/T7 preflight matrix before dense production:

| Axis | Required values |
|---|---|
| Frequencies | `kM = 2.0` anchor, plus `2.5, 3.0, 3.5, 4.0`; optionally `0.1, 0.5, 1.0` for low-frequency metadata coverage |
| Sectors | odd RW and even Zerilli |
| Radii | all eight Table-I radii listed above |
| Ell bands | `ell_turn = ceil(k*r)` at `r=30M` and `r=39.051248M`; `ell_turn-12`, `ell_turn`, `ell_turn+12`; `L_seed-24`; `L_seed`; plus any Q018 continuous band triggered by the solver |
| Observables | packaged `F_plus_complex`, `F_cross_complex`, masks, final adjacent-pair deltas |
| Diagnostics | Wronskian/matching residuals where available, radial warning codes, Q018 branch/oracle metadata, nonfinite checks |

Evidence labels:

- **GREEN**: all matrix entries finite; no uncovered Q018 branch; odd/even
  sectors pass; final adjacent-pair convergence passes for the review grid;
  `kM=4` has reviewed radial metadata and no new convention change.
- **YELLOW**: one or more entries require an explicitly reviewed opt-in oracle
  or higher-precision radial route, but T4/T7 can bound the risk and sidecars
  identify the branch.  Dense production should wait until T7 accepts the
  mitigation.
- **RED**: nonfinite outputs, uncovered Q018 fail-closed events, unreviewed
  radial method changes, or final adjacent-pair failure at `kM=4`.

## 6. Kirchhoff Eq. (47) Convention Freeze Requirements

Kirchhoff must be introduced as a comparison baseline, not as the denominator
or normalization of the project amplification.  The project denominator remains
the unlensed packaged polarization field.

Before T8 implements or plots Kirchhoff Eq. (47), T1/T10/T7 should freeze:

- Fourier sign compatibility with project `exp(-i k t)`;
- sign of `gamma`, especially whether Eq. (47) uses `gamma=-2Mk` under the
  project convention;
- complex branch of `(-gamma)^(-i gamma)`;
- branch and argument convention of `Gamma(1+i gamma)`;
- Kummer confluent hypergeometric convention and branch for `1F1`;
- exact argument of `1F1`, including signs and the relation to
  `xi/xi0` or the paper's equivalent impact-parameter variable;
- global phase convention `theta_F`;
- whether the comparison is scalar/eikonal only or directly comparable to
  packaged plus/cross `F_plus_complex` and `F_cross_complex`;
- whether the same Kirchhoff curve is used for plus/cross, or whether the
  comparison must be labeled polarization-independent.

Recommended policy:

- Store Kirchhoff values in a separate baseline file or separate NPZ group.
- Plot Kirchhoff only after a sidecar records the frozen convention name,
  formula version, branch choices, and input parameters.
- Label Kirchhoff as "comparison baseline" in metadata.  Do not use it to
  normalize, mask, or correct the exact spin-2 outputs.

## 7. Artifact Schema And Output Layout

Do not create these paths in T10g.  Proposed future layout:

```text
runs/phase5/fig5_fig6_dense_scan_review/
  tablei_dense_review_values.npz
  tablei_dense_review_values.npz.json

runs/phase5/fig5_fig6_dense_scan_production/
  tablei_dense_production_values.npz
  tablei_dense_production_values.npz.json

runs/phase5/fig5_fig6_kirchhoff_baseline/
  tablei_kirchhoff_baseline_values.npz
  tablei_kirchhoff_baseline_values.npz.json
```

Suggested NPZ arrays:

```text
kM_values                      shape (n_frequency,)
point_x, point_z, point_r       shape (8,)
F_plus_complex                  shape (n_frequency, 8)
F_cross_complex                 shape (n_frequency, 8)
abs_F_plus, abs_F_cross         shape (n_frequency, 8)
phase_plus_principal            shape (n_frequency, 8)
phase_cross_principal           shape (n_frequency, 8)
phase_plus_unwrapped            shape (n_frequency, 8)
phase_cross_unwrapped           shape (n_frequency, 8)
phase_plus_unwrap_segment       shape (n_frequency, 8)
phase_cross_unwrap_segment      shape (n_frequency, 8)
valid_plus_mask                 shape (n_frequency, 8)
valid_cross_mask                shape (n_frequency, 8)
lmax_final                      shape (n_frequency,)
lmax_values_padded              shape (n_frequency, n_lmax_slots)
final_pair_delta_plus           shape (n_frequency, 8)
final_pair_delta_cross          shape (n_frequency, 8)
```

Suggested JSON sidecar keys:

```text
schema_version
scope_label
paper_figure_target
frequency_grid_name
point_table_source
source_artifacts
source_artifact_sha256
config_sha256
source_code_hash_policy
selected_source_file_hashes
git_available
git_commit
git_dirty
radial_preflight_status
q018_policy
per_frequency_metadata
kirchhoff_convention
no_interpolation
no_smoothing
no_fill
not_denominator_normalized_by_kirchhoff
```

Source-code hash policy for a non-git workspace:

- If a git commit is available, record commit and dirty status.
- If git is unavailable or the workspace is not a git worktree, record
  `git_available=false` and hash the selected source/config files that control
  the computation.  At minimum include `src/schwgw/scattering/partial_wave.py`,
  `src/schwgw/scattering/observables.py`, `src/schwgw/scattering/weyl.py`,
  radial modules, and the exact run config.
- Record the hash list in the sidecar rather than only in `status.md`.

## 8. Runtime And Storage Estimate

Known local archive sizes:

- Each accepted full M4 source x-z artifact is about `14.6-15.1 MB`.
- Each accepted M5 amplification x-z artifact is about `1.607 MB`.
- The accepted four-frequency Table-I extraction NPZ is `57 KB`.
- The accepted four-frequency reporting PNGs are about `228 KB` and `296 KB`.

Grid-count implications:

- Full x-z M4 artifacts use the `[-30,30]^2`, `dx=dz=0.5M` grid:
  `121 x 121 = 14641` points per frequency.
- Table-I dense curves need only eight points per frequency.
- A point-only dense scan should therefore be far smaller than a full x-z
  dense wavefield archive.  The dominant cost is radial mode generation and
  convergence history, not the eight point values.

Rough radial solve count under the proposed `L_seed=max(84,90*kM)` policy:

- Four accepted anchor frequencies used about `2*(lmax-1)` odd/even radial
  sectors per frequency, roughly `1048` sector solves total for
  `lmax=[84,108,156,180]`.
- A 40-frequency `Delta(kM)=0.1` dense point scan to `kM=4` would request
  roughly `1.5e4` odd/even sector solves before any failed convergence
  extension.
- A 79-frequency `Delta(kM)=0.05` scan would be roughly twice that.

Storage estimate:

- Point-only review grid: likely `<10 MB` for final NPZ/JSON if it stores only
  values and metadata.
- Point-only 40-frequency production grid: likely `<50 MB`, dominated by
  sidecar/convergence metadata if verbose.
- Full x-z dense production at 40 frequencies would be order
  `40 * (15 MB + 1.6 MB) ~= 660 MB` before plots and duplicates.  This is not
  recommended for Fig.5/Fig.6, which only need Table-I points.

Wall-clock estimate:

- Highly uncertain because runtime depends on radial cache reuse, high-ell
  Q018 branch behavior, and whether `kM=4` needs a stronger radial method.
- Expect the review grid to be hours-scale rather than seconds-scale on the
  current machine if it computes fresh radial data.
- Expect the 40-frequency production-like grid to be several times the review
  grid and plausibly hours to tens of hours if high-ell radial solves dominate.
- Treat any estimate before the T4 `kM=4` preflight as a planning estimate, not
  a scheduling commitment.

Recommended staged run plan:

1. T1 freezes Kirchhoff Eq. (47) conventions, without implementation.
2. T4 performs the `kM=4`/Q018 radial preflight matrix.
3. T7 reviews the T10g plan and T4 preflight result.
4. T8 runs only the conservative review grid at eight Table-I points.
5. T7 reviews convergence, masks, and sidecars.
6. T8 runs the 40-frequency production-like point scan only if the review grid
   is accepted.
7. T8 plots paper-level Fig.5/Fig.6 only from accepted dense artifacts.

## 9. Rejected Options

- **Use T8ad four-frequency plots as paper-level Fig.5/Fig.6.**
  Rejected because they are sparse reporting pilots with no dense `Mk`, no
  `kM=4`, and no Kirchhoff comparison.
- **Adopt `ellmax ~= k r` as the sole lmax rule.**
  Rejected because scalar finite-radius convergence is not a complete spin-2
  proof, and final adjacent-pair convergence is already the project acceptance
  standard.
- **Run full x-z dense grids for Fig.5/Fig.6 first.**
  Rejected because Fig.5/Fig.6 only need eight Table-I points; full grids would
  spend storage and runtime on unused points.
- **Use Kirchhoff as normalization.**
  Rejected because the project's M5 quantity is pointwise lensed/unlensed
  packaged polarization amplification.  Kirchhoff is a comparison baseline.
- **Implement Kirchhoff before freezing branches.**
  Rejected because `Gamma`, Kummer `1F1`, `(-gamma)^(-i gamma)`, `theta_F`,
  and Fourier-sign choices can move phases by convention-dependent amounts.

## 10. Open Items

- T1 has not frozen Kirchhoff Eq. (47) branches and phase convention.
- T4 has not validated `kM=4` radial/Q018 behavior for the Table-I dense scan.
- The exact paper frequency step is not stated; `Delta(kM)=0.1` is an inference
  from figure density and the paper's `0.1/M` to `4.0/M` statement.
- Runtime remains uncertain until the `kM=4` preflight reports high-ell radial
  behavior and cache reuse.
- A future T8 task must confirm whether the existing run machinery can compute
  the eight Table-I points directly without producing full x-z grids.

## 11. Recommended Next Thread Sequence

Send T7 next:

```text
你现在是 T7be。请读取并严格执行 docs/prompts/phase5_t7be_fig5_fig6_dense_kirchhoff_plan_review.md。
```

If T7be accepts this plan, suggested downstream prompts are:

```text
你现在是 T1。请冻结 Li-Hou-Zhao Eq. (47) Kirchhoff comparison baseline 的 Fourier sign、gamma sign、Gamma/Kummer/1F1 branch、theta_F phase 和 packaged plus/cross comparison convention；只更新 docs/physics_spec.md 或指定 convention note，不运行 solver。
```

```text
你现在是 T4。请基于 T10g/T7be 接受的 plan，执行 kM=4 Table-I dense scan radial/Q018 preflight；覆盖 odd/even sectors、Table-I radii、ell_turn bands 和 L_seed=360 附近 high-ell bands；只输出 preflight note/metadata，不生成 dense production artifacts。
```

```text
你现在是 T8。请在 T7 接受 T10g plan、T1 Kirchhoff convention freeze、T4 kM=4/Q018 preflight 后，只对八个 Table-I 点运行 conservative review grid dense scan；不要生成 paper-level plots，先输出 NPZ/JSON sidecar 供 T7 review。
```

## 12. Minimal Formulas / Rules For Later Implementation

These are planning formulas only; T10g did not implement them.

Frequency grids:

```text
kM_review =
  [0.1,0.2,0.3,0.5,0.75,1.0,1.25,1.5,1.75,2.0,
   2.25,2.5,2.75,3.0,3.25,3.5,3.75,4.0]

kM_production = 0.1,0.2,...,4.0
```

Adaptive lmax seed:

```text
L_seed(kM) = ceil_to_multiple_of_12(max(84, 90*kM))
```

Acceptance condition:

```text
accept frequency only if final adjacent lmax pair passes
for complex F_plus and F_cross at all eight Table-I points,
with plus/cross masks handled independently and no fill/interpolation.
```

Kirchhoff policy:

```text
exact spin-2 F = h_lensed / h_unlensed
Kirchhoff Eq. (47) = comparison baseline only
```
