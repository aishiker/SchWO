# Literature Manifest

This directory contains the fixed reference set for the Schwarzschild gravitational-wave wave-optics solver.

## Directory policy

- `references/papers/` stores raw PDF files. Treat them as source material, not as the only implementation context.
- `references/manifest.md` records each reference's role, implementation priority, relevant modules, and key equation ranges.
- `docs/equation_map.md` maps code modules to documented formulas and references.
- `references/notes/` stores Codex-readable formula notes, convention translations, derivation checks, and sign/normalization traps.

Implementation threads should read this manifest first, then the relevant notes, then the PDF only when the notes or `docs/physics_spec.md` are insufficient. When a thread extracts or relies on a new formula from a PDF, it must add a concise note under `references/notes/` or update `docs/physics_spec.md`, and then update `docs/equation_map.md` if code is affected.

Suggested entry fields:

- File
- Role
- Implementation priority
- Relevant modules
- Required equation ranges
- Notes file
- Convention caveats

## Primary implementation target

### Li, Hou, Zhao — Gravitational Lensing of Gravitational Waves: Spin-wave Optics through Black Hole Scattering
File: references/papers/li_hou_zhao_2025_spin_wave_optics.pdf

Role:
- Main implementation specification.
- Defines the finite-radius partial-wave method.
- Provides Schwarzschild background, RW/Zerilli master equations, incident plane GW coefficients, metric reconstruction, Weyl scalar reconstruction, tetrad transformation, and polarization extraction.

Implementation priority:
- Highest.

Relevant modules:
- `docs/physics_spec.md`
- `src/schwgw/backgrounds/`
- `src/schwgw/perturbations/`
- `src/schwgw/waves/`
- `src/schwgw/angular/`
- `src/schwgw/numerics/`
- `src/schwgw/scattering/`

Required equation ranges:
- Background and tensor harmonic expansion: Eq. (1)–(5)
- Master variables and RW/Zerilli equations: Eq. (6)–(13)
- Incident plane GW and boundary coefficients: Eq. (14)–(27)
- Metric reconstruction: Eq. (28)–(29)
- Weyl scalars: Eq. (30)–(40)
- Polarization extraction: Eq. (41)–(42)
- Transmission-factor definition and Kirchhoff scalar comparison baseline:
  Eq. (45)–(47), Table I, Fig. 5/Fig. 6 captions

Notes file:
- `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
- `references/notes/kirchhoff_eq47_conventions.md`

Convention caveats:
- Eq. (47) uses `gamma = -2 M k` and is frozen in this project only as a
  scalar/eikonal Kirchhoff comparison baseline. It is not the denominator for
  pointwise wave-optics amplification and not a production spin-2 observable.

Do not mix conventions from other papers unless explicitly mapped.

## Foundational references

### Regge & Wheeler — Stability of a Schwarzschild Singularity
File: references/papers/regge1957.pdf

Role:
- Foundational odd-parity Schwarzschild perturbation reference.
- Supports Regge-Wheeler potential, parity decomposition, and historical convention checks.

Implementation priority:
- High for `src/schwgw/perturbations/` and validation of odd-sector conventions.

Relevant modules:
- `docs/physics_spec.md`
- `src/schwgw/perturbations/potentials.py`
- future `src/schwgw/perturbations/rwz.py`

Notes file:
- `references/notes/regge1957.md`

### Moncrief — Gravitational perturbations of spherically symmetric systems
File: references/papers/moncrief1974.pdf

Role:
- Gauge-invariant perturbation variables and Hamiltonian structure.
- Useful for checking master-variable normalization and constraint consistency.

Implementation priority:
- Medium-high for perturbation conventions and future reconstruction checks.

Relevant modules:
- `docs/physics_spec.md`
- `src/schwgw/perturbations/`
- future `src/schwgw/scattering/reconstruction.py`

Notes file:
- `references/notes/moncrief1974.md`

### Gravitational perturbations of the Schwarzschild spacetime
File: references/papers/Gravitational perturbations of the Schwarzschild spacetime.pdf

Role:
- Modern review/reference for Schwarzschild perturbation notation and gauge-invariant formalism.
- Use to cross-check RW/Zerilli conventions, tensor-harmonic definitions, and reconstruction formulas.

Implementation priority:
- Medium-high as a convention cross-check, not the primary target-paper specification.

Relevant modules:
- `docs/physics_spec.md`
- `src/schwgw/perturbations/`
- `src/schwgw/angular/`
- future `src/schwgw/scattering/`

Notes file:
- `references/notes/schwarzschild_perturbations_review.md`

## Numerical methods and Q012 radial-stability references

### Li & Zhao — Rigorous calculation of scalar scattering in Schwarzschild background: the convergence of partial-wave series and Poisson spot
File: `references/papers/li_zhao_2025_scalar_schwarzschild_convergence_poisson_spot.pdf`; local HTML cache at `arxiv-reading/2508.17253.html`

Role:
- Key reference for Q018 finite-radius partial-wave cutoff and high-`ell`
  evanescent-tail policy.
- Shows for scalar finite-radius Schwarzschild scattering that the partial-wave
  series naturally truncates around `ell_max ~ k r`, and that asymptotic radial
  expansions fail for `ell ~ k r`.
- Provides the scalar baseline for T10b's spin-2 tail-bound audit.  Use it as
  leading-potential intuition only; it does not certify R60_K2 spin-2
  observables without reconstruction-aware tail bounds.

Implementation priority:
- High for Q018 and Phase 4 wave-field numerics.
- Medium as a direct gravitational-wave implementation source, because the
  paper treats scalar waves and only discusses full GW scattering as future
  work.

Relevant modules:
- `docs/numerics.md`
- `docs/validation_plan.md`
- `src/schwgw/numerics/radial_solver.py`
- `src/schwgw/io/results.py` metadata for any high-ell tail policy
- Phase 4 T4/T7 validation prompts

Required equation ranges:
- Sec. II, Eq. (4)-(8): finite-radius plane-wave PWS and asymptotic-expansion
  failure for `ell ~ k r`
- Sec. IV.1, Eq. (40)-(51): spin-0 RW Schwarzschild scalar scattering
- Sec. IV.2, Fig. 9-11 discussion: finite-radius convergence and turning-point
  interpretation
- Sec. V: procedure summary and `ell_max ~ k r` / `k min(r,r_s)` scaling
- Appendix B: high-frequency GW as scalar-amplitude/eikonal approximation

Notes file:
- `references/notes/q018_scalar_partial_wave_cutoff.md`
- `references/notes/q018_spin2_tail_bound.md`
- `arxiv-reading/2508.17253.memory.md`

Convention caveats:
- Scalar spin-0 result is a strong prior for large-`ell` RW/Zerilli behavior,
  but it is not a proof of the full spin-2 finite-radius observable.  Do not
  silently truncate gravitational partial waves without a T4/T7-reviewed tail
  bound and metadata policy.
- For R60_K2 specifically, T10b found that target-radius local WKB action for
  the first suppressed spin-2 modes is too small to support a conservative
  negligible-tail GREEN claim once polynomial reconstruction/tensor/Weyl
  prefactors are allowed.

### Mano, Suzuki, Takasugi — Analytic Solutions of the Regge-Wheeler Equation and the Post-Minkowskian Expansion
File: references/papers/mano_suzuki_takasugi_1996_rw_mst.pdf

Role:
- Core reference for analytic homogeneous Regge-Wheeler solutions using horizon-side hypergeometric series and infinity-side Coulomb-wave series.
- Provides the MST-style two-basis structure, continued-fraction determination of the renormalized angular momentum, and asymptotic incoming/outgoing amplitudes.
- Use as a future high-accuracy radial oracle/backend candidate for Q012-like high-barrier modes.

Implementation priority:
- High for future radial-solver validation; medium for immediate implementation because full MST is too large for the v0.1 blocker fix.

Relevant modules:
- `src/schwgw/numerics/radial_solver.py`
- `src/schwgw/numerics/matching.py`
- future transmission/phase-shift extraction modules
- `docs/numerics.md`
- `docs/validation_plan.md`

Required equation ranges:
- RW equation and variables: Sec. I, Eq. (1.1)
- Continued fractions and renormalized angular momentum: Sec. II, Eq. (2.6)-(2.11)
- Coulomb-wave expansion: Sec. III, Eq. (3.1)-(3.7)
- Infinity amplitudes and absorption coefficient: Sec. IV, Eq. (4.3)-(4.7)

Notes file:
- `references/notes/q012_high_ell_radial_methods.md`

Convention caveats:
- Uses `epsilon = 2M omega`, `z = omega r`, and Coulomb asymptotic factors. Convert to the project `exp(± i k r_star)` normalization before comparing `A_in`, `A_out`, phase factors, or Wronskians.

### Sasaki and Tagoshi — Analytic black hole perturbation approach to gravitational radiation
File: references/papers/sasaki_tagoshi_2003_analytic_bhpt.pdf

Role:
- Review of analytic black-hole perturbation methods, including RW/Sasaki-Nakamura wave-equation forms and MST horizon/infinity series matching.
- Useful for deciding whether MST or Sasaki-Nakamura-style methods are worth introducing.

Implementation priority:
- Medium-high as a method-selection and convention cross-check reference; not the primary finite-radius implementation target.

Relevant modules:
- `src/schwgw/numerics/radial_solver.py`
- future high-precision radial backend
- future transmission/phase-shift extraction modules

Required equation ranges:
- Chandrasekhar-Sasaki-Nakamura motivation: Sec. 2.2
- RW-based Schwarzschild PN method: Sec. 3
- MST formalism overview: Sec. 4
- Hypergeometric and Coulomb series matching: Sec. 4.2-4.3

Notes file:
- `references/notes/q012_high_ell_radial_methods.md`

Convention caveats:
- Much of the review is Teukolsky/Kerr-oriented. Do not copy Teukolsky or Sasaki-Nakamura radial normalizations into the Schwarzschild RW/Zerilli finite-radius solver without an explicit transformation.

### Dolan — Scattering and absorption of gravitational plane waves by rotating black holes
File: references/papers/dolan_2008_gravitational_plane_wave_scattering.pdf

Role:
- Practical partial-wave scattering reference for gravitational waves, phase-shift extraction, and large-`l` convergence hazards.
- Shows how numerical phase shifts and partial-wave sums are handled in cross-section calculations, and why large-`l` phase errors can be amplified.

Implementation priority:
- Medium for future phase-shift/transmission/cross-section validation; low as a direct solver recipe for current finite-radius observables.

Relevant modules:
- future transmission/phase-shift extraction modules
- `src/schwgw/numerics/radial_solver.py`
- `docs/validation_plan.md`

Required equation ranges:
- Phase-shift and absorption relation: Sec. 3-4
- Numerical method: Sec. 5
- Large-`l` sensitivity and convergence discussion: Sec. 6-7

Notes file:
- `references/notes/q012_high_ell_radial_methods.md`

Convention caveats:
- Primarily Kerr/Teukolsky/Sasaki-Nakamura and asymptotic cross-section focused. Do not replace Li-Hou-Zhao finite-radius partial-wave observables with Dolan-style asymptotic cross sections.

### Johnson — Multichannel log-derivative method for scattering calculations
File: no open PDF stored; official metadata at https://www.osti.gov/biblio/4376059

Role:
- General scattering reference for log-derivative/Riccati propagation, useful for understanding amplitude-growth stabilization.

Implementation priority:
- Low-medium. Relevant as a future optional stabilization method, but not a direct BHPT or finite-radius radial-function prescription.

Relevant modules:
- future radial-solver experimental backend

Required equation ranges:
- Not extracted locally; official abstract identifies the method as numerical propagation of the matrix Riccati equation for the logarithmic derivative of the wave function.

Notes file:
- `references/notes/q012_high_ell_radial_methods.md`

Convention caveats:
- Not Schwarzschild/RW/Zerilli-specific. A log-derivative solver would still need a separate normalization and reconstruction step to recover `psi(r)` and `dpsi/dr` for finite-radius observables.

### Black Hole Perturbation Toolkit — ReggeWheeler package documentation
File: online documentation only, https://bhptoolkit.org/ReggeWheeler/

Role:
- External-practice reference: homogeneous Regge-Wheeler radial solutions are computed with either MST or direct numerical integration.
- Useful as a possible future external benchmark if Mathematica/BHPT Toolkit is available.

Implementation priority:
- Medium for validation planning; no dependency should be added for v0.1.

Relevant modules:
- `src/schwgw/numerics/radial_solver.py`
- future benchmark/oracle tooling

Required equation ranges:
- Documentation sections "Homogeneous solutions", "MST", and "Numerical integration".

Notes file:
- `references/notes/q012_high_ell_radial_methods.md`

Convention caveats:
- Toolkit interfaces and Mathematica precision behavior are external to this Python project. Any comparison must translate radial-function and boundary-condition normalizations to `docs/physics_spec.md`.
