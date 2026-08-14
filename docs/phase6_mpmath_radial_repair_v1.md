# Phase-6 independent arbitrary-precision radial repair V1

## Scope and scientific boundary

This campaign is a new, isolated diagnostic of selected fail-closed radial
keys.  It does not rerun a paper figure and does not use agreement with Li et
al. as an acceptance gate.  It is not a detector-response, finite-radius
observer, or full-domain validation.  A successful 24-anchor campaign can
support only the explicitly selected radial domain; it cannot promote the
remaining 5,774 source failures or the project as a whole to `GREEN`.

The selection source is the immutable conditioning campaign

`runs/phase6/radial_validation/v1_conditioning_campaign_v1_20260808_py314`

whose `conditioning_campaign_index.json` SHA-256 is
`e26b53ecb7997808a52da4dae5420fa7c4ebf5e1e46df88519fa8903e1956de6`.
The planner reopens all 86 immutable shards and derives exactly 5,798 native
`FAIL` keys.  Float64 values from those artifacts are used only to choose the
diagnostic keys; no stored radial amplitude or state enters the mpmath solve.

## Frozen selection

For every failed key, define the dimensionless turning-severity proxy

\[
  q_{\rm turn}=\frac{\sqrt{\ell(\ell+1)}}{(kM)(r_{\rm out}/M)},
  \qquad r_{\rm out}/M=300.
\]

The 24-anchor selection contains one deterministic representative from every
cell in

- four frequency bands: `0.3--1`, `1.1--2`, `2.1--3`, and `3.1--8`;
- both `odd` and `even` sectors;
- three severity bands: `q_turn < 0.06`, `0.06 <= q_turn < 0.1`, and
  `q_turn >= 0.1`.

Within a cell, the frozen ordering minimizes distance from its severity
target, frequency target, and severity-specific ell-quantile target, followed
by exact `kM` and ell tie-breakers.  The two-key timing subset is also frozen:

- ordinary/low odd: `kM=0.9`, `ell=21`;
- severe/high even: `kM=8`, `ell=315`.

## Independent numerical construction

The dedicated implementation is
`src/schwgw/validation/phase6_mpmath_radial_repair.py`.  It evaluates the
Regge--Wheeler and Zerilli potentials directly with `mpmath` and propagates the
full complex state by explicit RK4 in Schwarzschild tortoise coordinate.  It
does not import NumPy, SciPy, the production radial solver, the conditioning
backend, or the older Phase-6 mpmath backend.  An AST call-graph check is bound
into every plan.

The frozen conventions are:

- `M=1`, `r_star = r + 2 log(r/2 - 1)`;
- Fourier convention `exp(-i k t)`;
- unit ingoing horizon normalization at `r=2(1+10^-6)`;
- independent local outer bases
  `exp(+-i k r_star) sum_n a_n/r^n` at `r_out=300M`;
- Jost order cap 160 and bidirectional logarithmic-derivative matching at
  `60M`;
- direct Zerilli evolution for every even mode; parity-derived even data are
  prohibited;
- scattering convention `S=-A_out/[(-1)^ell A_in]`.

The production ladder is the Cartesian product of 60/80 decimal digits and
RK4 maximum steps `0.0016/0.0008` in `r_star/M`.  The fine steps were chosen
only after a coarse two-key smoke showed that `0.2/0.1` was not converged.  The
worst timing key gave an 80-dps adjacent-step relative S difference of
`6.7176610912047816207e-7` for the final fine pair.

Numerical closure requires every frozen component to pass:

- arithmetic precision relative S delta `<= 1e-20`;
- step-size relative S delta `<= 2e-6`;
- flux-fraction residual `<= 1e-8`;
- Jost tail ratio `<= 1e-15`;
- matching log-derivative residual `<= 1e-20/M`;
- match-condition estimate `<= 1e50`.

The numerical budget and convention budget are separate objects.  Frozen
conventions are not represented as zero numerical error and remain
`FROZEN_NOT_EXTERNALLY_CROSSCHECKED` in V1.

## Runtime and evidence protocol

Execution requires CPython 3.14, the immutable mpmath 1.4.1 overlay first on
`PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1`, and the project root as the working
directory.  The runner rejects output outside the direct children of
`runs/phase6/radial_validation`.

The campaign is append-only and single-writer:

- a nonblocking `fcntl` lock guards the partial mode-0700 root;
- plan, per-anchor result, and per-anchor checkpoint files use `O_EXCL`;
- each file and parent directory are flushed before the next anchor;
- `--resume` requires the same canonical plan and revalidates every existing
  mode-0444/nlink-1 artifact;
- a completed root is sealed mode 0555 with all JSON files mode 0444.

An interrupted partial root is resumable.  A timing benchmark never carries
scientific acceptance even if both ladders close.  A full selected campaign is
accepted only if all 24 exact anchor ladders close; `global_green_permitted`
remains false in every case.

## Two-key timing result (2026-08-09)

The reviewed fine-ladder timing root is

`runs/phase6/radial_validation/ap_radial_repair_timing_benchmark_v2_20260809_py314`.

Both selected ladders closed, while the campaign-level
`scientific_acceptance` remained false because this is only a timing subset.
The low/odd and worst/high/even anchors took 230.09 s and 288.01 s,
respectively.  The linear 24-anchor projection is 6,217.13 s (about 1 h 44
min), below the frozen 10 h scheduling bound.  This is a timing extrapolation,
not a guarantee that all 24 numerical ladders will close.

The limiting observed numerical component was the worst/high/even adjacent
step S difference, `6.7176610912047816207e-7`, below the `2e-6` threshold.  All
arithmetic-precision, flux, Jost-tail, match-residual, and condition components
also passed for both timing anchors.  The sealed root is mode 0555; every JSON
artifact is mode 0444 with link count one.  Key identities are:

- campaign plan SHA-256:
  `bd958ccb82aadd9023adb5072d4fe02e1120264a900a6999eeb1207c31fd3fe6`;
- summary SHA-256:
  `b4a32ef9e1b955dc595afc14fb60dc4b918672b021b0a41da36ff463cc216e31`;
- manifest SHA-256:
  `438eac3a1f6a0d81d1681d4c6bd7050896146314a1710c32133a585860204333`.

The earlier `v1` timing root used the deliberately coarse `0.2/0.1` probe and
failed closed on step size.  It is preserved as diagnostic provenance and is
not the production-ladder timing evidence.

## Commands

Set the exact runtime prefix once:

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD/runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:$PWD/src"
```

Read-only plan validation:

```bash
/opt/homebrew/bin/python3.14 scripts/phase6_run_mpmath_radial_repair.py \
  --benchmark-two \
  --run-id ap_radial_repair_fine_timing_20260809 \
  --plan-only
```

Two-key timing benchmark:

```bash
/opt/homebrew/bin/python3.14 scripts/phase6_run_mpmath_radial_repair.py \
  --benchmark-two \
  --run-id ap_radial_repair_fine_timing_20260809 \
  --output-root runs/phase6/radial_validation/ap_radial_repair_timing_benchmark_v2_20260809_py314
```

The 24-key command is intentionally not run by the implementation thread.  It
must use a fresh output root and explicit `--full-selected-repair` only after
T0 reviews the two-key timing and closure budgets.  A partial run is continued
with the identical arguments plus `--resume`; it is never restarted into the
same root without that flag.
