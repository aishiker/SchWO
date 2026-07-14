# Phase 4 T4k Prompt: Q018 High-Ell Evanescent-Tail Radial Failure

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4k`。

## 0. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/phase3_closeout.md`
8. `src/schwgw/numerics/radial_solver.py`
9. `tests/unit/test_radial_solver.py`
10. `tests/physics/test_radial_solver.py`
11. `configs/li_fig3_xz_k2p0_hires.yaml`
12. `docs/prompts/phase4_t4j_radial_bvp_mesh_failure.md`
13. `references/notes/q018_scalar_partial_wave_cutoff.md`
14. `arxiv-reading/2508.17253.memory.md`
15. T4j/T8k records in `status.md`

## 1. 背景

T4j resolved Q017: the original `kM=1.5,r_out=300,ell=10`
BVP mesh-node failure now completes via structured bidirectional matching.
T8k then successfully generated:

```text
/tmp/t8j_li_fig3_xz_k1p5_hires.npz
```

but stopped on the missing `kM=2.0` saved result:

```text
Stabilized radial BVP solve failed
(sector=odd, ell=153, k=2.0, r_out=300.0,
 barrier_action=706.302835508, solver=bvp_unit_infinity,
 initial_mesh=1200, max_nodes=50000):
The maximum number of mesh nodes is exceeded.;
bidirectional fallback failed:
Radial basis integration failed: Required step size is less than spacing between numbers.
```

T0 quick diagnostic:

```text
k=2.0
grid rmax = sqrt(30^2+30^2) = 42.4264
k*rmax = 84.8528
ell=153 is far above k*rmax
barrier_action S(ell=153) ~= 706.303
exp(-S) ~= 1.8e-307, close to double-precision normal underflow scale
ell=156 has exp(-S) ~= 6.2e-315
ell=180 underflows to 0.0 in double precision
```

This is a new Q018 high-ell evanescent-tail/double-precision radial issue,
not a T8 plotting failure.

The scalar finite-radius reference arXiv:2508.17253 argues that scalar
Schwarzschild partial-wave sums naturally truncate around `ell_max ~ k r`
because modes far above `k r` are behind the centrifugal barrier at the
observer.  Treat this as a strong physical prior for Q018, but not as a
complete spin-2 proof: T4k must still validate or bound the gravitational
RW/Zerilli contribution and record any cutoff/tail policy explicitly.

## 2. Goal

Adjudicate and, if justified, implement a numerically sound policy for
`kM=2.0` high-`ell` modes whose WKB barrier action is near or beyond
double-precision dynamic range.

The immediate target is the first failing mode:

```text
sector=odd, ell=153, k=2.0, M=1, r_out=300, r_in_eps=1e-6,
rtol=1e-10, atol=1e-12
```

The broader target is to let T8 resume the `kM=2.0` Fig.3-lite saved run
without lowering `lmax`, relaxing convergence thresholds, or hiding mode
failures.

## 3. Non-goals and hard limits

- Do not change frozen Fourier, harmonic, tetrad, RW/Zerilli, or polarization conventions.
- Do not change T6 Route B production bridge.
- Do not edit plotting code.
- Do not generate Fig.3 panel or saved benchmark artifacts.
- Do not reduce `lmax` in `configs/li_fig3_xz_k2p0_hires.yaml`.
- Do not relax convergence thresholds.
- Do not silently skip high-`ell` modes.
- Do not use arbitrary smoothing/interpolation as a numerical fix.
- Do not introduce arbitrary-precision dependencies unless T0 approves after a no-go report.

## 4. Required investigation

### 4.1 Reproduce and bracket Q018

Run targeted direct radial diagnostics around the failure:

```text
k=2.0, r_out=300, ell in [132, 144, 150, 153, 156, 168, 180],
sector=odd/even
```

For each mode record:

- selected solver branch;
- `barrier_action`;
- approximate `exp(-S)` or log attenuation;
- turning-point / match-radius information;
- `A_in`, `A_out`, `phase_factor` if returned;
- max finite field amplitude over the solved grid;
- boundary residual, flux residual, raw/effective Wronskian;
- match condition number;
- warning metadata;
- exact failure message if it fails.

### 4.2 Diagnose the numerical regime

Answer explicitly in `status.md`:

1. Is the failure caused by BVP mesh refinement alone, or by dynamic-range
   loss in the evanescent tail?
2. Does bidirectional matching fail because basis amplitudes overflow/underflow
   before reaching the match radius?
3. Are `ell >= 153` modes physically negligible on the saved `61x61`
   x-z grid, or do they need a rescaled/log-domain representation?
4. Can a mathematically bounded high-`ell` tail policy be defined without
   changing the physics convention?
5. How does the scalar `ell_max ~ k r` argument from arXiv:2508.17253 map
   onto the project RW/Zerilli spin-2 potentials and final `h_plus/h_cross`
   observables?

### 4.3 Possible implementation directions

Only implement after the diagnostics support the choice. Acceptable directions:

- A rescaled/log-amplitude radial basis integration for evanescent high-`ell`
  modes, preserving the public `RadialSolution` contract.
- A structured evanescent-tail suppression policy with a conservative upper
  bound on omitted field contribution, explicit diagnostics/warnings, and
  T7-reviewable metadata. This must not be a silent truncation.
- A narrower no-go record proving that current double precision cannot
  support the requested `ell` range without a larger architectural change.

If adopting a suppression/bounding policy, add clear docs in `docs/numerics.md`
and tests proving:

- the policy is triggered only in extreme high-barrier regimes;
- it records structured diagnostics;
- it does not change lower-`ell` Q012/Q017 behavior;
- it does not silently alter convergence thresholds.

## 5. Required tests and checks

At minimum run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run a direct radial scan for `k=2.0,r_out=300` across the high-ell
bracket listed above. If full `ell=2..180` is feasible, run it and record
runtime; if not, explain the bounded subset and why it is sufficient for T8l
to attempt the real saved run.

## 6. Stop conditions

Stop and update `status.md` if:

- the only apparent solution is lowering `lmax` without a convergence or
  contribution-bound argument;
- the solution requires changing physics conventions or T6 Route B;
- three independent numerical strategies fail;
- a single targeted mode exceeds 10 minutes without diagnostic progress;
- implementing a stable high-ell policy requires arbitrary precision,
  complex WKB connection formulas, or a larger radial-solver redesign.

## 7. status.md update requirements

Record:

- changed files;
- commands run;
- direct radial diagnostics;
- whether Q018 is resolved, narrowed, or still open;
- whether T8l may proceed;
- any new warning/metadata policy;
- tests and results;
- open issues and next action.

If Q018 is resolved or adequately narrowed, next T8 prompt is:

```text
你现在是 T8l。请读取并严格执行 docs/prompts/phase4_t8l_resume_k2_after_q018.md。
```
