# Kirchhoff Eq. (47) Convention Freeze

> **Superseding 2026-08-02 audit addendum.** This file records the historical
> T1j decision to transcribe Eq. (47) literally.  A later independent analytic
> check found that the printed `exp(+pi gamma/2)` sign is inconsistent with
> both the paper's own Figs. 5--6 and
> `|F(eta=0)|^2=4*pi*Mk/(1-exp(-4*pi*Mk))`.  Current code therefore defaults
> to `standard_point_mass`, using `exp(-pi gamma/2)`, and retains the frozen
> formula below only as `literal_paper_v1` for forensic reproduction.  The
> branch, no-conjugation, comparison-only and non-denominator decisions remain
> in force.

Date: 2026-07-09

Thread: T1j

Decision Label: GREEN / EQ47 COMPARISON BASELINE CONVENTIONS FROZEN

## 1. Decision Label

GREEN. Li-Hou-Zhao Eq. (47) can be used as a frozen scalar Kirchhoff
comparison baseline for later Fig. 5/Fig. 6 review-grid work, provided it is
kept separate from the project's production pointwise wave-optics
amplification denominator and from spin-2 production observables.

This decision does not authorize dense Fig. 5/Fig. 6 production, solver runs,
new plots, or source-code changes. It only freezes the conventions needed by
future implementation/review threads.

## 2. Source Basis

Primary source:

- Li, Hou, Zhao, "Gravitational Lensing of Gravitational Waves: Spin-wave
  Optics through Black Hole Scattering", local PDF
  `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`.
- Sec. V.D, Eq. (45)-(47), Table I, and Fig. 5/Fig. 6 captions.

Project sources used for compatibility:

- `docs/physics_spec.md`: Fourier convention `exp(-i k t)`, flat/no-lens
  pointwise amplification denominator, and production polarization policy.
- `docs/equation_map.md`: current mapping for pointwise amplification and
  saved plotting.
- `references/notes/t10d_li_hou_zhao_figure_inventory.md`
- `references/notes/t10e_fig4_fig5_reproduction_plan.md`
- `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
- `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`

## 3. Formula Map

Li-Hou-Zhao define the frequency-domain transmission factor by

```text
h_tilde_{+,\times} = F_{+,\times} h_tilde^{(0)}_{+,\times},
h_tilde^{(0)}_{+,\times} = A_tilde_{+,\times} exp(i k r cos(theta)).
```

With the project Fourier convention `exp(-i k t)`, the factor
`exp(i k r cos(theta)) = exp(i k z)` is the same positive-frequency flat
incident plane wave used by the project for a `+z` incident wave. No
conjugation or sign flip is introduced when comparing Eq. (47) to the project
positive-`k` API.

The frozen Kirchhoff baseline is

```text
F_K(k, r, theta; M)
  = exp(pi gamma / 2)
    * (-gamma)^(-i gamma)
    * Gamma(1 + i gamma)
    * 1F1(-i gamma, 1; -i gamma * eta^2),

gamma = -2 M k,
eta = xi / xi0 = (1/2) * sqrt(r / M) * tan(theta).
```

Here `1F1(a,b;z)` is the Kummer confluent hypergeometric function
`M(a,b,z)`. For Table-I observer points in the paper, `theta` is the polar
angle relative to the `+z` incident direction and `r` is the observer radius.
For an x-z plotting plane with `phi=0` and `z>0`, this gives

```text
r = sqrt(x^2 + z^2),
theta = atan(x / z),
eta = (1/2) * sqrt(r / M) * tan(theta).
```

This reproduces the Table-I values, e.g. for `z=30M`, `x=25M`,
`eta = 2.6038` after rounding.

## 4. Branch And Phase Decisions

The project uses positive real `M` and positive real `k` for the Fig. 5/Fig. 6
comparison baseline. Therefore

```text
gamma = -2 M k < 0,
-gamma = 2 M k > 0.
```

Branch decisions:

- `(-gamma)^(-i gamma)` uses the real positive principal logarithm of
  `-gamma`:

  ```text
  (-gamma)^(-i gamma) = exp((-i gamma) * log(-gamma)),
  log(-gamma) = log(2 M k) with zero imaginary part.
  ```

- `Gamma(1 + i gamma)` uses the principal analytic continuation of the
  Euler gamma function. Numerically, use a stable complex gamma/log-gamma
  implementation, e.g. `loggamma(1 + 1j*gamma)` followed by exponentiation if
  overflow/underflow control is needed.

- `1F1(-i gamma, 1; -i gamma eta^2)` is Kummer's regular confluent
  hypergeometric function `M(a,b,z)`. Since `b=1`, there is no pole in `b`;
  the function is entire in `z`. Use a standard complex implementation such
  as SciPy/mpmath `hyp1f1` and record the backend in output metadata.

- Do not apply a same-positive-`k` complex conjugation to Eq. (47). A
  conjugated expression would correspond to a different Fourier/sign
  convention or to a reality-condition relation involving the negative
  frequency partner, not to the project positive-frequency API.

Phase convention:

```text
theta_F = Arg(F_K)
```

where `Arg` is the principal complex argument in `(-pi, pi]` for stored
single-point metadata. Plotting code may additionally store an unwrapped
phase along an explicitly declared scan coordinate, but unwrapping is a
display operation and must not replace the principal stored value.

## 5. Comparison Policy

Eq. (47) is a scalar/eikonal point-mass Kirchhoff baseline. It is
polarization independent and neglects the spin-2 polarization evolution,
long-range Schwarzschild scattering effects beyond the weak-field lensing
approximation, and strong-field partial-wave structure.

Project policy:

- Eq. (47) may be plotted as a dashed comparison baseline against
  `F_plus_complex` and/or `F_cross_complex`.
- The same scalar `F_K` curve is used for plus and cross unless a future
  reviewed note defines a different baseline. Labels must say
  "Kirchhoff scalar comparison baseline" or equivalent.
- Eq. (47) must not be used as the denominator for project pointwise
  amplification. The denominator remains the flat/no-lens
  production-compatible polarization field defined in `docs/physics_spec.md`.
- Eq. (47) must not mask, normalize, correct, or calibrate exact spin-2
  partial-wave results.
- Eq. (47) must not be presented as a production spin-2 prediction. It is
  only a comparison curve for literature-style Fig. 5/Fig. 6 diagnostics.

## 6. Implementation Guardrails

Future implementation should keep the Kirchhoff baseline in a separate API and
saved-result group from production pointwise amplification. Suggested
metadata:

```text
baseline.kind = "kirchhoff_eq47_scalar_comparison"
baseline.source = "Li-Hou-Zhao Eq. (47)"
baseline.fourier = "exp(-i k t)"
baseline.gamma_definition = "gamma = -2 M k"
baseline.power_branch = "principal real log for -gamma=2Mk>0"
baseline.gamma_function_branch = "principal complex Gamma(1+i gamma)"
baseline.kummer = "1F1(a,b;z)=Kummer M(a,b,z)"
baseline.argument = "-i gamma (xi/xi0)^2"
baseline.theta_F = "principal Arg(F_K), optional display unwrap separately"
baseline.comparison_only = true
baseline.not_denominator = true
baseline.polarization_independent = true
```

Do not silently recompute `eta` if a Table-I reproduction explicitly supplies
the paper's tabulated `xi/xi0`. If both coordinates and tabulated `eta` are
available, store both and report any mismatch beyond rounding tolerance.

Do not run radial solvers, scattering solvers, dense scans, or plotting from
this convention note. T8 dense review-grid scanning remains gated until both
T1j and T4v have been reviewed together by T7bn.

## 7. Open Items

No convention blocker remains for implementing the Eq. (47) comparison
baseline.

Non-blocking future checks:

- Choose and test the numerical backend for complex `Gamma` and `1F1` at the
  planned Fig. 5/Fig. 6 frequency and `eta` ranges.
- Decide saved-file naming and plotting labels in the T8 implementation.
- Let T7bn review this T1j decision together with the T4v `kM=4` preflight
  before authorizing any dense Fig. 5/Fig. 6 scan.
