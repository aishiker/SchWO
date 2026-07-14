# T10d Li-Hou-Zhao Figure Inventory And Project Mapping

Date: 2026-07-07

Scope: inventory Li-Hou-Zhao paper Figures 1-8 and map each figure to current project artifacts, implemented modules, missing modules, and recommended next-stage work.

Primary source:

- `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`

Project context read:

- `project.md`
- `status.md`
- `references/manifest.md`
- `references/notes/*.md`
- `docs/phase4_production_closeout.md`
- `docs/phase5_m5_four_frequency_closeout.md`
- `docs/q018_r60_k2_angular_production_readiness.md`

PDF status: the Li-Hou-Zhao PDF is present in `references/papers/`, so this note uses its Figure captions, nearby text, Table I, and rendered page inspection of the paper figures. This is not an incomplete notes-only inventory.

## Global paper parameters relevant to figures

The paper's numerical demonstration uses:

- Units: `G = c = M = 1`.
- Fourier convention: `exp(-i k t)`.
- Default incident wave: along `+z`.
- Demonstration amplitudes:

```text
A_plus = 0.9 + 1.1 i
A_cross = 0.4 + 0.6 i
```

- Main figure frequencies:

```text
k = {0.5, 1.0, 1.5, 2.0}/M
```

- The paper also states that computations range over `k = 0.1/M` to `4.0/M`.
- Finite-radius convergence follows empirical `ell_max ~ k r`.
- The main finite-radius observer for angular diffraction/convergence is `r = 60M`.
- The x-z wavefield panels use a `60M x 60M` region, visually `x/M,z/M in [-30,30]`, with event horizon and light ring overlays.
- Transmission-factor fixed points are listed in Table I, all at `z = 30M`:

| region | x/M | theta deg | xi/xi0 |
|---|---:|---:|---:|
| near-axis | 0.00 | 0.00000 | 0.0000 |
| near-axis | 1.00 | 1.90915 | 0.0913 |
| near-axis | 2.00 | 3.81407 | 0.1828 |
| near-axis | 3.00 | 5.71059 | 0.2745 |
| far-axis | 10.0 | 18.4349 | 0.9372 |
| far-axis | 15.0 | 26.5651 | 1.4479 |
| far-axis | 20.0 | 33.6901 | 2.0015 |
| far-axis | 25.0 | 39.8056 | 2.6038 |

## Figure inventory

| Fig. | Category | Physical content | Parameters visible / stated | Required output type | Priority |
|---:|---|---|---|---|---|
| 1 | validation | Validation of asymptotic expansion for normalized radial functions. Exact finite-radius radial solution is compared with asymptotic expansion. | `k=1.0/M`; panels `ell=2,3,4,5,60,61,62,63`; x-axis `r/M`; real/imag exact vs asymptotic. | 1D radial curves for normalized mode functions, exact and asymptotic. | useful |
| 2 | validation / angular convergence | Convergence of the partial-wave series for `Psi4` at fixed observer radius. | `r=60M`; `k={0.5,1.0,1.5,2.0}/M`; angles `theta=0, pi/6, pi/3, pi/2`; x-axis `ell_max`; y-axis log partial-sum error/ratio. | 1D convergence curves vs `ell_max` for strict/paper `Psi4`. | must-have |
| 3 | x-z wavefield | Wave fields of physical `+` and `cross` modes for scattered GWs. | `k={0.5,1.0,1.5,2.0}/M`; `x/M,z/M in [-30,30]`; rows `Re h_plus`, `Re h_cross`; event horizon black, light ring gray. | Saved 2D x-z complex wavefield plus read-only multi-frequency panel. | must-have |
| 4 | angular diffraction | Diffraction patterns, angular distributions of `+` and `cross` amplitudes, exact finite-radius vs conventional asymptotic approach. | `r=60M`; `k={0.5,1.0,1.5,2.0}/M`; x-axis `theta/pi`; y-axis `|h_A(k,r)|`; plus/cross exact and asymptotic curves; insets. | Angular curves from saved finite-radius data; optional asymptotic comparison curves. | must-have for exact curves; useful for asymptotic comparison |
| 5 | amplification/transmission | Transmission factor comparison between BH scattering and Kirchhoff integral in near-axis region. | Table I near-axis points `(x,z)=(0,30),(1,30),(2,30),(3,30)M`; x-axis `Mk` from near 0 to 4; rows `|F|` and phase `theta_F`; plus/cross exact dots; Kirchhoff dashed. | Frequency scan of complex pointwise amplification at fixed points plus Kirchhoff baseline. | must-have for paper-level M5 |
| 6 | amplification/transmission | Transmission factor comparison between BH scattering and Kirchhoff integral in far-axis region. | Table I far-axis points `(x,z)=(10,30),(15,30),(20,30),(25,30)M`; x-axis `Mk` from near 0 to 4; rows `|F|` and phase `theta_F`; plus/cross exact dots; Kirchhoff dashed. | Same as Fig.5 but far-axis fixed points. | must-have for paper-level M5 |
| 7 | x-z wavefield / apparent polarization | Appendix wave fields of apparent `x`, `y`, `b`, and `L` modes induced by the incident-aligned tetrad convention. These are described as apparent/unphysical modes. | `k={0.5,1.0,1.5,2.0}/M`; `x/M,z/M in [-30,30]`; rows `Re h_x`, `Re h_y`, `Re h_b`, `Re h_L`; event horizon/light ring overlays. | Saved 2D x-z fields for apparent modes and read-only panel. | optional |
| 8 | asymptotic validation / other | Differential cross sections from asymptotic Appendix E series-reduction calculation. | `k={0.5,1.0,1.5,2.0}/M`; x-axis `theta/pi`; y-axis `M^-2 d sigma/d Omega`; blue dots unregularized, green first-order reduction, red second-order reduction. | Asymptotic phase-shift/cross-section curves with series reduction. | optional |

No Figure 1-8 is a pure method schematic. The closest "method" content is Fig.1/Fig.2 as numerical-method validation and Fig.8 as asymptotic-method validation.

## Mapping to current project

### Fig.1 radial asymptotic validation

Current coverage:

- Implemented: T4 radial solver, boundary conditions, Wronskian/flux diagnostics, Q012 high-ell stabilization, Q018 opt-in Riccati oracle for R60 coverage.
- Notes: `references/notes/q012_high_ell_radial_methods.md`, `references/notes/q018_spin2_tail_bound.md`.

Missing:

- A project output for the paper's normalized radial function `u_hat_l^(+/-)`.
- A conventional asymptotic radial expansion evaluator for Eq. (11)-style comparison.
- A read-only radial validation plot/fixture for exact vs asymptotic radial functions.

Route:

- T4: expose or document a validation-only normalized radial diagnostic, if needed.
- T7: define exact-vs-asymptotic tolerances and stop criteria.
- T8: plotting only after T4/T7 freeze saved diagnostic data.
- New physics: no new production physics, but an asymptotic-expansion diagnostic module is needed.

### Fig.2 partial-wave convergence for `Psi4`

Current coverage:

- Implemented: saved `lmax_convergence_history` for production observables, selected/near-axis convergence checks, angular grid support, R60_K2 bounded selected/ angular pilot artifacts.
- Implemented modules: T3 angular, T4 radial, T5 incident coefficients, T6 finite-radius partial-wave assembly, T8 saved results.
- Current readiness: `docs/q018_r60_k2_angular_production_readiness.md` proposes a `65 x 64` angular production candidate at `r=60`, `kM=2`.

Missing:

- Figure-style strict `Psi4` convergence curves at the four paper frequencies and four angles.
- A saved output path exposing strict/paper `Psi4` partial sums separately from Route B packaged `h_plus/h_cross`.
- Lower-frequency R60 angular production artifacts for `kM=0.5,1.0,1.5` if the goal is all four panels.

Route:

- T6/T1: confirm whether the plotted `Psi4` should be strict incident-tetrad `Psi4_NP` or the paper's transformed scalar under the post-Q014 convention. Do not substitute packaged scalars.
- T8: after T8x/T7as, add saved angular/convergence artifacts for the exact requested points.
- T7: independently verify final-pair convergence and strict/package labeling.
- New physics: mostly no, but strict `Psi4` output must not violate Q014 package separation.

### Fig.3 physical plus/cross x-z wavefield

Current coverage:

- Achieved as M4-production first pass:
  - `runs/phase4/m4_production_first_pass/`
  - `kM=[0.5,1.0,1.5,2.0]`
  - `x/M,z/M in [-30,30]`
  - `dx=dz=0.5M`, shape `(121,121)`
  - saved complex `h_plus/h_cross`
  - read-only PNG/PDF multi-frequency Fig.3-style panel.
- Closeout: `docs/phase4_production_closeout.md`.

Remaining differences:

- The project has accepted "Fig.3-style" artifacts, not a pixel-for-pixel paper reproduction.
- `kM=4` is not included.
- Color normalization/layout may differ from the paper.

Route:

- T8 only, if final paper-like cosmetics are desired, using saved results read-only.
- T7 review if artifact is promoted to a benchmark fixture.
- New physics: no.

### Fig.4 angular diffraction pattern

Current coverage:

- Implemented: angular saved-output support and selected R60_K2 pilot/readiness.
- Current `r=60,kM=2` angular production config is drafted but, at the time of this note, production NPZ is scheduled separately and not accepted yet.

Missing:

- Full exact angular curves for `kM=0.5,1.0,1.5,2.0`.
- Read-only Fig.4 plotting from saved angular data.
- Conventional asymptotic approach curves from Appendix D.
- Series-reduction regularization used by the conventional approach.

Route:

- T8: generate exact finite-radius angular data only after T0 authorization, starting from the scheduled R60_K2 path and extending lower frequencies.
- T10/T1: write a short Appendix D/E convention note before implementing asymptotic comparison.
- T4/T6: if asymptotic comparison is desired, add phase-shift/asymptotic-amplitude diagnostic support.
- T7: review exact finite-radius curves separately from asymptotic comparison.
- New physics: exact curves use existing finite-radius pipeline; asymptotic comparison requires a new diagnostic module.

### Fig.5 and Fig.6 transmission factors

Current coverage:

- Achieved partially as M5 four-frequency pointwise wave-optics amplification archive:
  - `runs/phase5/m5_four_frequency_amplification_artifacts/`
  - source M4 x-z grid `[-30,30]^2`
  - `kM=[0.5,1.0,1.5,2.0]`
  - complex component ratios `F_plus_complex`, `F_cross_complex`
  - derived plots for amplification summaries.
- Closeout: `docs/phase5_m5_four_frequency_closeout.md`.

Missing:

- Dense frequency scan in `Mk` from near 0 to 4 at Table I points.
- `kM=4` support remains gated.
- Kirchhoff integral baseline Eq. (47) is not implemented.
- Figure-style phase unwrapping and panel layout for `|F|` and `theta_F`.
- Exact use of paper Table I positions as a first-class scan config.

Route:

- T1/T10: freeze the Kirchhoff comparison formula, branch convention for `(-gamma)^(-i gamma)`, `Gamma(1+i gamma)`, Kummer `1F1`, and phase unwrapping policy.
- T8: implement or configure pointwise frequency scans only after `kM=4` gate is decided.
- T6: ensure `compute_pointwise_amplification(...)` remains the production M5 denominator and does not drift into radial horizon transmission.
- T7: review complex ratios, masks, phase wrapping, and Kirchhoff baseline metadata.
- New physics: Kirchhoff baseline and dense frequency-scan workflow are new; current M5 pointwise amplification core exists.

### Fig.7 apparent polarization x/y/b/L wavefields

Current coverage:

- Implemented core ingredients: T6 finite-radius Weyl/tidal pipeline and Route B physical `h_plus/h_cross`.
- Q014 notes explicitly warn that finite-radius apparent modes depend on incident-frame convention and strict/package separation.

Missing:

- Definitions and API outputs for apparent `x`, `y`, `b`, `L` modes as used in the paper's Eq. (42)-style decomposition.
- Saved x-z artifacts and read-only panel for these four apparent modes.
- T1 convention freeze for whether these are diagnostic-only unphysical apparent polarizations.

Route:

- T1/T10: first write a convention note for apparent modes, explicitly marking them non-production diagnostics.
- T6: add diagnostic-only observable extraction if T1 freezes formulas.
- T8: save and plot read-only x-z apparent-mode panels.
- T7: ensure apparent modes are not treated as new physical polarizations or as tests of modified gravity.
- New physics: no new physical theory, but new diagnostic observables and strong convention labels are required.

### Fig.8 differential cross sections

Current coverage:

- No production coverage.
- Related method notes exist for phase shifts/MST/high-ell hazards, but current project intentionally avoids asymptotic scattering amplitudes as the main output.

Missing:

- Asymptotic reflected-wave amplitudes from Appendix D.
- Even/odd phase-shift extraction compatible with project radial normalization.
- Series-reduction method from Appendix E.
- Differential cross-section output `d sigma / d Omega`.

Route:

- T10/T1: write Appendix D/E convention and phase-shift note before any implementation.
- T4: add phase-shift/Jost/asymptotic amplitude diagnostics if approved.
- T8: plotting only after saved asymptotic data exist.
- T7: validate against known asymptotic scattering references and ensure no finite-radius production path is replaced.
- New physics/module: yes, a separate asymptotic scattering diagnostic module is required.

## Priority summary

Must-have:

- Fig.2 exact finite-radius convergence curves, but only after strict `Psi4` output is clearly labeled.
- Fig.3 physical plus/cross wavefield; already achieved as a first-pass Fig.3-style artifact.
- Fig.4 exact finite-radius angular diffraction curves.
- Fig.5/Fig.6 pointwise amplification/transmission scans if the project wants paper-level M5 reproduction.

Useful:

- Fig.1 radial exact-vs-asymptotic validation, because it supports Q012/Q018 explanations.
- Fig.4 conventional asymptotic comparison curves, because they explain near-axis asymptotic failure.

Optional:

- Fig.7 apparent polarizations, because the paper itself describes them as apparent/unphysical and beyond its main scope.
- Fig.8 asymptotic differential cross sections, because it belongs to Appendix D/E diagnostics rather than the finite-radius production pipeline.

## Recommended next-stage order

Do not interrupt the current scheduled T8x/T7as R60_K2 angular production/review sequence.

After T8x/T7as:

1. T7/T0: decide whether the accepted R60_K2 angular production artifact is enough to start Fig.4 exact-curve plotting for `kM=2`.
2. T8: add read-only angular-curve plotting from saved angular data, no solver calls.
3. T8/T4/T7: extend exact angular datasets to `kM=0.5,1.0,1.5` at `r=60` if Fig.4 all-frequency reproduction is desired.
4. T1/T10: freeze Kirchhoff Eq. (47) and phase convention before any Fig.5/Fig.6 reproduction.
5. T8/T7: build a Table-I point-frequency scan fixture for exact `F_plus/F_cross`, initially limited to existing safe frequencies.
6. T0: open `kM=4` only as a separate gate if Fig.5/Fig.6 full paper range is required.
7. Optional later: T10/T1/T4 define asymptotic Appendix D/E diagnostics for Fig.8 and conventional Fig.4 curves.

Suggested next prompt after the current scheduled T8x/T7as path completes:

```text
你现在是 T10e：Li-Hou-Zhao Fig.4/Fig.5 reproduction planning.
请读取 references/notes/t10d_li_hou_zhao_figure_inventory.md、status.md、docs/q018_r60_k2_angular_production_readiness.md、docs/phase5_m5_four_frequency_closeout.md。
任务：在不运行 solver、不改 src 的前提下，给出 Fig.4 exact angular curves 与 Fig.5/6 Table-I point-frequency scan 的最小 artifact/schema/plotting 计划，并明确哪些步骤需要 T1/T4/T7/T8。
```

## Open issues

- The paper's Fig.2 plotted `Psi4` must be separated from project packaged polarization scalars after Q014. A strict output label is required before implementation.
- The scheduled R60_K2 angular production NPZ is not yet accepted at the time of this inventory.
- Kirchhoff baseline branch conventions and phase unwrapping are not frozen.
- `kM=4` remains gated.
- Apparent polarization modes require a diagnostic-only convention freeze before implementation.
- Asymptotic differential cross-section reproduction requires a new phase-shift/series-reduction diagnostic path.
