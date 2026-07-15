# T7 Archived Handoff

Last updated: 2026-07-14

Thread: T7bu, Fig.5/Fig.6 review-grid diagnostics and production-spacing
independent review.

## Thread Role And Current Status

T7bu completed an independent read-only review of T8am's diagnostics generated
from the accepted T8aj exact spin-2 review grid and T8al scalar Kirchhoff
baseline.

Exact decision:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW GRID SUPPORTS DELTA KM 0.1 PRODUCTION PILOT
```

All nine frozen checks pass. This GREEN means only that the current evidence
supports T0 designing a separate bounded `Delta(kM)=0.1` production pilot. It
does not authorize that pilot, approve production data, prove band limitation,
or permit T7 to dispatch another task.

The pre-T7bu T7bt handoff is archived at:

```text
docs/handoffs/archive/T7_2026-07-14_pre_t7bu_review_grid_diagnostics.md
```

## Nine Required Checks

1. **PASS — commit and scope.** `f6d32b1` plus layout-only `1542f5e` change
   exactly the five frozen implementation/test paths. No solver, scattering,
   numerics, IO, config, fixture, source-artifact, or unrelated-handoff path is
   in the combined commit range.
2. **PASS — no recomputation.** The plotting module imports only stdlib and
   NumPy at module load, plus Matplotlib inside rendering. It contains no
   solver/scattering/radial/Q018/compute/solve import or call. The CLI branch
   passes only the two accepted NPZ paths, output directory, DPI, and CLI flag
   to the plotting API.
3. **PASS — paired source contract.** Both schemas, embedded/sidecar metadata,
   frozen flags, exact ordered 18-frequency/eight-point arrays, `(18,8)`
   shapes, Boolean masks, valid-value finiteness, exact polarization meaning,
   and scalar comparison-only Kirchhoff contract pass. Kirchhoff units/dtypes
   cover every non-metadata array and match actual dtypes. All three masks are
   `144/144` true.
4. **PASS — independent sampling metrics.** T7bu loaded the two NPZ files
   directly and did not call T8am's loader or metric API. Every one of the 272
   saved adjacent records was independently recomputed and matched within an
   absolute serialization tolerance of `2e-15`; maxima, point/interval
   attribution, `0.1` projection, factor `1.5`, and `< pi/2` flags all agree.
   The recommendation is exactly `DELTA_0P1_PROVISIONAL_REVIEW`, explicitly
   diagnostic and not a theorem or production authorization.
5. **PASS — eight-file contract.** The directory contains exactly the eight
   frozen names. PNG/PDF/JSON headers and readability, all current output
   hashes, manifest entries, two source triplets, source sizes/hashes, and all
   frozen no-recompute/no-interpolation/no-smoothing/no-fill/non-production
   flags pass.
6. **PASS — visual review.** Both native 2100x1620 PNGs and independently
   rendered one-page PDFs contain four readable nonblank panels, correct
   near/far points, four color/marker encodings, exact markers with thin saved-
   sample guides, dashed `Kirchhoff scalar comparison` lines, correct magnitude
   and phase units, legible labels/legends, and the exact diagnostic-only
   subtitle. No clipping or paper-style claim was found. Both PDF text bounding
   boxes are inside the 504x388.8-point page box.
7. **PASS — focused tests.** Fresh focused pytest is `10 passed in 1.76s`.
8. **PASS — static quality/full regression.** Ruff is clean. Fresh full pytest
   is `568 passed, 117 skipped, 1 xfailed, 85 warnings, 79 subtests passed in
   282.63s (0:04:42)`. Warnings remain the known Weyl/Wigner/radial warnings;
   no T8am diagnostics warning or non-finite failure occurred.
9. **PASS — isolation/non-claims.** Forbidden production diff and downstream-
   output commands are empty. No source mutation, solver rerun, physics
   recomputation, interpolation, smoothing, fill, altered mask, 40/79-point
   production, fixture, paper-style candidate, or automatic later dispatch
   occurred.

## Accepted Source SHA256

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  exact NPZ
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  exact JSON
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  exact manifest
66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55  Kirchhoff NPZ
0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3  Kirchhoff JSON
fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632  Kirchhoff manifest
```

## Eight Output SHA256

```text
f8ffcee55ce2a4d07e9a2ff91320baa0122bd37f43701cfde8d5eab5e963c386  fig5_near_axis_review_grid.png
e19c28ca4a6532adc079f99137853115b9f90e0764bed84957d133d3b9167c11  fig5_near_axis_review_grid.pdf
627903f91de69edf3d4e527419511a6a898979e8ae8c6dd57e6cee70ee93cb98  fig5_near_axis_review_grid.json
e949bd7436617bf8cadb59515a3861e8bc8503e17337347a81be7598ef061855  fig6_far_axis_review_grid.png
02b05bbe092f0c5934bcc389ca16d305208202637182c88038eeb5ff511a77ec  fig6_far_axis_review_grid.pdf
06142d333dabba5dd17f76642a4a792dfa6603beee6a73ce8cc712c07073f534  fig6_far_axis_review_grid.json
cb40d6cae967699b86f0ef3d863e8cbe9ce2555f56dcd3427f8f5d64d44190a4  sampling_diagnostics.json
f09c24abb30c1ec64abcd3cd9dd2679061dfa23d746c2c96c49ffdd4e04c327b  manifest.md
```

## Independent Metric Evidence

```text
T7BU_SOURCE_AND_PAIRED_CONTRACT=PASS
T7BU_ALL_ADJACENT_METRICS=PASS records=272
T7BU_EIGHT_FILE_HASH_PROVENANCE=PASS
```

Maximum phase slopes and factor-1.5 safety projections at candidate spacing
`0.1`:

- near `F_plus`: slope `2.796164802757737` at `near_axis_x1_z30`,
  `[3.75,4.0]`; safety projection `0.4194247204136605` rad.
- near `F_cross`: slope `3.625714958231235` at `near_axis_x2_z30`,
  `[2.75,3.0]`; safety projection `0.5438572437346854` rad.
- far `F_plus`: slope `8.763007426859136` at `far_axis_x20_z30`,
  `[0.3,0.5]`; safety projection `1.3144511140288706` rad.
- far `F_cross`: slope `7.5544095996424385` at `far_axis_x10_z30`,
  `[1.5,1.75]`; safety projection `1.1331614399463659` rad.

All four are below `pi/2`. The most rapid magnitude evidence remains visible
and is not hidden by an invented threshold: far `F_cross` has maximum absolute
step `1.7643213800514306` and maximum relative step `0.8039700767407513` at
`far_axis_x15_z30`, `[0.75,1.0]`. This is a limitation of sparse-grid evidence,
but it does not contradict the frozen meaning of GREEN: support for a bounded
finer-spacing pilot rather than acceptance of its eventual production output.

## Visual Review Notes

- Native PNGs are opaque white-background RGBA images with nonzero color
  variance and dimensions `2100x1620`.
- Both PDFs are valid unencrypted one-page PDF 1.4 files with page size
  `504x388.8 pt`; they were rendered independently at 180 DPI and inspected.
- A first simultaneous two-image viewer call displayed the far-axis margins
  incorrectly. Direct alpha/RGB inspection showed fully opaque white pixels,
  and separate PNG loading plus an independent PDF-to-JPEG render displayed
  the complete figure. This was a reviewer-tool display anomaly, not an
  artifact defect.
- The accepted masks are all true, so the real figures contain no invalid gap.
  Source inspection plus `test_invalid_pair_is_not_connected_or_filled`
  confirms invalid samples split guides rather than being filled or connected.

## Review-Only Changed Paths

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-14_pre_t7bu_review_grid_diagnostics.md`

T7bu modified no implementation, test, config, source, artifact, plot,
fixture, or unrelated handoff.

## Limitations And Next Owner

- The phase proxy with factor `1.5` is a conservative diagnostic, not a
  band-limit theorem and not proof that no unobserved extrema exist.
- Magnitude evidence has no frozen automatic threshold. The far-axis curves
  require evaluation in the future bounded pilot rather than being treated as
  already converged production evidence.
- T0 alone may interpret this GREEN and design a separate bounded
  `Delta(kM)=0.1` pilot. T7bu starts and authorizes nothing downstream.

## Frozen Decisions And Forbidden Actions

- Exact spin-2 plus/cross and scalar polarization-independent Kirchhoff remain
  distinct quantities; Kirchhoff never enters masks, normalization, solver,
  Q018, or polarization channels.
- Do not modify or regenerate accepted sources, diagnostics, implementation,
  tests, or artifacts from T7.
- Do not start 40/79-frequency production, midpoint probes,
  `Delta(kM)=0.05`, fixtures, interpolation/smoothing, or paper-style work.
- Do not push GitHub or dispatch a later task from T7.

## Files The Next Thread Must Read

1. `status.md`
2. `docs/handoffs/T7_current.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T8_current.md`
5. `docs/superpowers/specs/2026-07-14-t8am-t7bu-review-grid-diagnostics-design.md`
6. `docs/superpowers/plans/2026-07-14-t8am-review-grid-diagnostics.md`
7. `docs/prompts/phase5_t7bu_fig5_fig6_review_grid_diagnostics_review.md`
8. the five T8am implementation/test paths
9. both accepted source triplets and all eight diagnostics outputs

## Exact Next Task And Definition Of Done

Send the exact GREEN, six source hashes, eight output hashes, metric maxima,
visual evidence, focused/Ruff/full-test results, scope results, review-only
changed files, and limitations to T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636`.

T7bu is complete only after fresh document/hash/scope verification and a
successful T0 message. No later task is dispatched by T7.
