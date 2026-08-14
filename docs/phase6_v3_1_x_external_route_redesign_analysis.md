# Phase 6 V3.1-X external direct-route redesign analysis

Date: 2026-08-13

Candidate gate ID: `phase6_v3_1_x_external_direct_route_redesign_v1`

Status: `NOT_ASSESSED / ZERO-SCIENCE DESIGN READY FOR T0 PACKAGE FREEZE`

This document is a read-only design analysis. It is not V3.1-U repair cycle
3, a retry of its failed sentinel, an implementation, a numerical result, a
formal T7 acceptance, V3.2, or global GREEN. The failed V3.1-U roots and their
14 successful MST records remain evidence only and are not reusable science.

## 1. Frozen boundary and authority identities

Root T0 selected liveness option 2: replace the failed external algorithm/gate
under a distinct authority. The replacement must retain the exact 496-mode
V3.1 production domain, all V3.0 formulas and conventions, all 16 V3.1
thresholds, all five certificate IDs, the seven protected radial sources, and
the odd-only scope of `V3A-MODE-BHPT-RW-001`.

The principal identities rehashed at the start of this analysis are:

| Authority | SHA-256 |
|---|---|
| `project.md` | `fdba5646eb0d9bb0776ea6148e509d91124871cf371ac08a7229b10e18b63b9a` |
| `status.md` | `3492893eb5a3956a689685f597a3779477e4ed26fbfa83932c1b91df8087507e` |
| `docs/handoffs/T0_current.md` | `65505633a5c97ad581d7458c2b37fe5cf5712440dbba3d09a27830c2f5b7eec5` |
| `docs/handoffs/T4_current.md` | `9aaeb1161549c527dc10c11ab8fc47a7455e467d234248780d30ea6bf1934c7a` |
| `docs/handoffs/T7_current.md` | `51c5315b15a737ae312677cc69f82c0eaed0708d5b8d6725257c36b3e3010de2` |
| liveness protocol | `3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181` |
| V3 master prompt | `f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7` |
| V3.0 domain | `803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b` |
| V3.0 thresholds | `91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a` |
| V3.0 external-anchor matrix | `06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485` |
| V3.0 validation contract | `0f8b8c96e01321231377c857ab40d710aa80ac06dce9084029fe2914b1ef37d3` |
| V3.0 formula map | `e5b556667c28ac8b611430d2dfb4faa5da82b9c7f0c8251251029e3f8c8d0eac` |
| V3.0 phase taxonomy | `fb91f4cf888dd4984174304783875c9f2e591490df8519bafd2e0b0f73053460` |
| V3.0 literature matrix | `088834348e980b81f814340a2a2c460b5bf11239521085c358bed7a90f603328` |
| V3 convention note | `82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a` |
| T7 terminal sentinel review | `e51f32f1f7d633ff78a653d9ab2a0a49d5c1ef0d32c57f84cb9fda63abc80b55` |
| frozen redesign-analysis prompt | `4dfe99653bef581837892eba6daeb9a31bff5f60b734115ea85070cc23c2ca07` |

The seven protected hashes remain:

```text
radial_solver.py             9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
conditioned_radial.py        91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
scaled_tortoise_radial.py    d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
adaptive_jost_radial.py      3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
matching.py                  9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
physical_boundary_radial.py fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
boundary_conditions.py       b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
```

The five certificate IDs remain exactly:

```text
V3_MODE_GREYBODY_NUMERICAL
V3_MODE_GREYBODY_FLUX_VS_S
V3_MODE_GREYBODY_EXTERNAL
V3_MODE_PARITY_PROBABILITY
V3_MODE_DOMAIN_COVERAGE
```

No threshold, formula, convention, certificate, production key, parity claim,
or protected source is changed by this design.

## 2. Failed-sentinel evidence and failure taxonomy

The immutable root is
`runs/phase6/classic_scattering/v3_1_u_route_c_sentinel_repair2_v1_20260812T221323Z_py314`.
It contains 17 regular mode-`0444`, nlink-1 files in two mode-`0555`
directories, no symlink, and no live writer. Its compact read-only inventory
digest, including paths, type, hash, size, mode and link count, is
`0e311a51bd2f0e5d1db3ca70068484044275afa606fa0b91190025e1aa4f3e87`.
The terminal failure and failure-manifest hashes are
`c80327f57b56f762fde9df3b215cf94c895e98de8c0d1e48157a31b44a65dc23`
and
`e9ef19b336e1eb9faac34b2f080f2c4956fd2316eb050287e769cbdb401aead4`.

### 2.1 Native child outcomes

The raw payload
`faa904b92e8248f79cc5dabcf6fd72fcbb85721d93a42884227e130c9d8dc0d9`
and attempt ledger
`a111d6dcc7ff937409ce62df73b71e0f0f65881a8d7066d4062d1295fba76399`
agree on 23 ordered, unique, one-call outcomes: 14 `PASS`, nine `ERROR`.
Every native error is exactly
`MST_FAILED / ReggeWheelerRadial returned $Failed`:

| Ordinal | kM | ell | Parity | Classification |
|---:|---:|---:|---|---|
| 0 | 0.1 | 2 | odd | native BHPT MST failure; decimal input was only MachinePrecision |
| 1 | 0.1 | 3 | odd | same demonstrated input-contract defect |
| 2 | 0.1 | 4 | odd | same demonstrated input-contract defect |
| 3 | 0.1 | 8 | odd | same demonstrated input-contract defect |
| 4 | 0.5 | 2 | odd | native BHPT MST failure; decimal input was only MachinePrecision |
| 5 | 0.5 | 3 | odd | same demonstrated input-contract defect |
| 6 | 0.5 | 4 | odd | same demonstrated input-contract defect |
| 7 | 0.5 | 10 | odd | same demonstrated input-contract defect |
| 17 | 2 | 18 | odd | native BHPT MST failure; `cause_not_proven` |

The WLS proves the decimal-precision defect without a new Wolfram evaluation:

- line 60: `k = ToExpression[key["kM"]]` creates an inexact machine number
  for the strings `0.1` and `0.5`;
- line 61 then applies `N[k,100]`; applying `N` to an already machine-precision
  number does not recover the exact decimal rational or 100-digit input;
- lines 61--63 nevertheless request `WorkingPrecision -> 90` and goals 45;
- `ReggeWheelerRadial.m` lines 357--361 checks and warns when the frequency
  precision is below the requested working precision, while the WLS wraps the
  call in `Quiet[Check[...]]` and collapses the diagnostic to `$Failed`.

Established conclusion: all eight failed decimal-frequency calls violated the
intended arbitrary-precision input contract, and the failure pattern is exactly
consistent with that defect. The suppressed native message trace is absent, so
the defect is not overclaimed as a uniquely proven internal MST failure path.
For `kM=2, ell=18`, `ToExpression["2"]` is exact before `N`; the decimal defect
does not apply. Its cause remains `cause_not_proven`.

### 2.2 Separate wrapper parser failure

The child itself completed all 23 calls and returned code 70 because nine raw
outcomes were errors. Separately, the Python wrapper recorded
`V31ContractError: external Route-C amplitude identity mismatch`, leaving its
summary at `pass_count=0` and `first_failure=null`. The validator at
`phase6_v3_mode_greybody_cycle2.py:672-674` requires redundant amplitude and
probability serializations to agree at `1e-40`, whereas the WLS serializes each
quantity independently with `N[...,50]`. Formal T7 reconstructed residuals of
order `1e-21`. This is a downstream serialization/parser defect; it neither
caused nor explains the nine native `$Failed` outcomes.

## 3. Independently rebuilt 23-key inventory

The inventory was rebuilt from the frozen V3.0 frequency/multipole domain and
the exact `V3A-MODE-BHPT-RW-001` selector: odd parity, frequencies
`0.1,0.5,1,2,4`, and the valid set `{2,3,4, nearest critical,
critical+8}` with the frozen smaller-ell tie rule and duplicate removal.

Compact canonical JSON SHA-256:
`5e93fca57b6d4fb82762043fedea4631de92111164c8c4a991d76925e3867c76`.
Compact canonical JSONL SHA-256:
`fae654aeda6e7e1984c944e837f56d9280a2bc8af1d4f3dde29a619fd9f18046`.

```text
00 (0.1,  2, odd)   01 (0.1,  3, odd)   02 (0.1,  4, odd)
03 (0.1,  8, odd)
04 (0.5,  2, odd)   05 (0.5,  3, odd)   06 (0.5,  4, odd)
07 (0.5, 10, odd)
08 (1,    2, odd)   09 (1,    3, odd)   10 (1,    4, odd)
11 (1,    5, odd)   12 (1,   13, odd)
13 (2,    2, odd)   14 (2,    3, odd)   15 (2,    4, odd)
16 (2,   10, odd)   17 (2,   18, odd)
18 (4,    2, odd)   19 (4,    3, odd)   20 (4,    4, odd)
21 (4,   20, odd)   22 (4,   28, odd)
```

The domain cannot be narrowed to the 14 prior successes, and no prior value is
eligible for promotion or cache reuse.

## 4. Proposed independent direct algorithm

### 4.1 Equation, potential and boundary conventions

Use the stable BHPT `ReggeWheelerRadial` public API with
`Method -> {"NumericalIntegration", "Domain" -> ...}`, spin argument `s=2`,
`Potential -> "ReggeWheeler"`, and both
`"BoundaryConditions" -> {"In","Up"}` in one call per node.

The external source writes `x=r/M`, `omega=M omega`, `f=1-2/x`, and solves

\[
 f^2\psi''(x)+\frac{2f}{x^2}\psi'(x)
 +[\omega^2-V_{\rm RW}(x)]\psi(x)=0,
\]

with

\[
 V_{\rm RW}(x)=\frac{f}{x^3}
 [2(1-s^2)+\ell(\ell+1)x]
 =f\left[\frac{\ell(\ell+1)}{x^2}-\frac6{x^3}\right]
\]

for `s=2`. These are `NumericalIntegration.m:67-76,292`. The frozen
tortoise coordinate is
`r_star=r+2 log(r/2-1)` with `M=1`, and the Fourier convention is
`exp(-i omega t)`.

The independent `In` solution starts from the near-horizon expansion
`exp(-i omega r_star) sum_n a_n f^n`, with unit horizon transmission. The
independent `Up` solution starts from the outgoing infinity expansion
`exp(+i omega r_star) sum_n a_n/(omega r)^n`, with unit outgoing amplitude.
The public numerical implementation sets the two transmission normalizations
to one (`ReggeWheelerRadial.m:117-125`) and integrates them independently with
Wolfram `NDSolveValue`, stiffness switching, unlimited steps, and all-order
interpolation. No SchWO radial/Jost/matching function is imported or called.

Frequency construction must never pass through machine precision. The future
WLS must map the five literal labels to exact rationals first:

```text
"0.1" -> 1/10, "0.5" -> 1/2, "1" -> 1, "2" -> 2, "4" -> 4
```

and only then apply `N[exact, workingPrecision+guardDigits]`; it must assert
the resulting input precision before each API call.

### 4.2 Controlled overlap decomposition

At every predeclared overlap radius, define dot as `d/dr_star=f d/dr` and
read independently integrated values

```text
H, Hdot = In solution
U, Udot = Up solution
Jin, Jindot = Conjugate[U], Conjugate[Udot]
D = Jin*Udot - U*Jindot
```

The real RW equation makes `Conjugate[U]` the incoming infinity basis. Extract
the horizon-normalized coefficients only through the two-solution Wronskian
system:

\[
 A_{\rm in}=\frac{H\dot U-U\dot H}{D},\qquad
 A_{\rm out}=\frac{J_{\rm in}\dot H-H\dot J_{\rm in}}{D},\qquad A_H=1.
\]

Then compute without phase or normalization fitting

\[
 S_\ell=(-1)^{\ell+1}\frac{A_{\rm out}}{A_{\rm in}},\qquad
 \Gamma_{\rm flux}=\frac{|A_H|^2}{|A_{\rm in}|^2},\qquad
 \Gamma_S=1-|S_\ell|^2.
\]

`Gamma_flux` is therefore the direct horizon/incoming-current ratio under the
unit-transmission normalization, never inferred from `1-|S|^2`.
`Gamma_S` remains a separate consistency route. The evidence must retain raw
`H,Hdot,U,Udot,D,A_in,A_out,A_H`, signed currents, positive fluxes, flux
balance, and all three overlap projections. `D=0`, nonfinite values, unhealthy
conditioning, loss of conjugacy, or an unresolved positive `Gamma` is a
fail-closed node error.

To avoid the cycle-2 parser defect, WLS should serialize only an independent
minimal amplitude/current basis at a declared digit count. Python must derive
all redundant ratios, `S`, `Gamma_flux`, `Gamma_S`, and logs from those same
canonical decimal strings. If redundant producer fields are retained, their
tolerance must be tied to emitted digits rather than an impossible fixed
`1e-40` equality.

## 5. Snapshot sufficiency and exact overlay boundary

The pristine 25-file snapshot is sufficient as the external algorithm source:
it contains the odd RW equation, independent `In/Up` boundary expansions, the
public numerical dispatcher, and overlap-evaluable solution objects. Its
content and restored-identity indexes are
`d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2`
and
`a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27`;
the snapshot authority is
`8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488`.

The pristine bytes are **not sufficient for a blocking boundary-convergence
gate**, because `NumericalIntegration.m` hardcodes odd `rin=2+10^-5` at line
126 and `rout=100/Abs[omega]` at line 157. The public `Domain` option changes
integration coverage, not those boundary-series construction points. No
immutable evidence establishes the default outer point as converged for all
23 anchors.

The minimal future overlay must therefore change exactly one file:
`Kernel/NumericalIntegration.m`. For the odd branch only, each predeclared
node-local copy changes exactly these two literal source sites:

1. the `ReggeWheelerInBC` local `rin=2+10^-5` literal to one frozen literal
   from `2+10^-8`, `2+10^-10`, `2+10^-12`;
2. the `ReggeWheelerUpBC` literal
   `rout =100*Abs[omega]^-1;` to that node's frozen literal expression
   `rout = m Max[300,8 Sqrt[l(l+1)]/Abs[omega]];`, for
   `m in {1,2,4,8}`.

All other bytes, including the equation, potential, recurrences, NDSolve
method, even branch, dispatcher and package entry graph, remain identical to
the stable snapshot. A future package must freeze the exact source bytes and
SHA for every node overlay and prove exactly one old occurrence and one new
occurrence. There is no run-time arbitrary boundary, environment-selected
formula, per-key patch, or fallback.

This remains an external BHPT numerical algorithm with a disclosed,
source-hashed boundary-location overlay; it is not a pristine-upstream claim.
It does not become a SchWO internal solver because SchWO supplies no equation,
integrator, basis solution, or matching data. Nevertheless, independence must
be reported precisely as `BHPT NumericalIntegration + reviewed boundary
geometry overlay`, not as byte-unmodified upstream BHPT.

Existing immutable bounded evidence supports this design but is not acceptance
evidence for V3.1-X. It used the same two-solution Wronskian method and a
two-line outer-radius overlay (transformed hash
`5fed25a141ea274592610dff4dabc1eef789f04fe8282ab16d37d7c058bdadc3`),
and completed 30 harder odd/even calibration keys at 40/60 digits. Its root
has 93 files, 368,927 logical bytes, inventory digest
`839f7ee4a858be8479f36aaa186e1e9936df5626deb7cf8d14a6da2bfeb2ab2a`,
and summary elapsed 1647.185409 s. It does not prove the new 23 anchors or the
new inner/outer ladder.

## 6. Predeclared ladder and uncertainty separation

The recommended minimum external ladder is one-factor-at-a-time around a
selected node; no node may be selected after results are seen.

Selected node:

```text
WorkingPrecision=60, PrecisionGoal=30, AccuracyGoal=30
r_in-2 = 1e-10
B(k,ell) = Max[300, 8*Sqrt[ell*(ell+1)]/k]
r_out = B
overlap fractions = [0.80, 0.88, 0.96], selected fraction = 0.88
for each node, r_match(f) = f*r_out, Domain["In"] = 0.96*r_out,
and Domain["Up"] = 0.80*r_out
```

Exact seven API nodes per anchor:

| Axis | Mandatory nodes | Other fields |
|---|---|---|
| precision | `(40,20,20)`, `(60,30,30)` | selected boundaries |
| inner boundary | `1e-8`, `1e-10`, `1e-12` | selected precision and outer boundary |
| outer boundary | multipliers `1,2,4,8` of `B` | selected precision and inner boundary |
| overlap | fractions `0.80,0.88,0.96` | all extracted from each In/Up pair |

After deduplicating the selected node this is exactly `23*7=161` fresh public
API calls, `322` independently integrated boundary solutions, and `483`
overlap records. These external precision nodes are additional Route-C
controls; they do not replace the unchanged Route-B 80/120/180 AP ladder or
any Route-A ladder.

Numerical uncertainty is a structured budget, not one fitted number. It must
store and gate separately:

- adjacent precision-node changes in complex `S` and `log Gamma`;
- adjacent `r_in` changes;
- adjacent `r_out` changes;
- three-radius overlap spread and Wronskian/determinant conditioning;
- signed-current balance and direct `Gamma_flux` versus independent
  `Gamma_S`;
- per-node NDSolve warnings, boundary-series termination and failure state.

The corresponding unchanged V3.1 limits are applied where their domains
match: `5e-7/1e-4` precision, `1e-6/2e-4` inner boundary,
`2e-6/3e-4` outer boundary, `1e-8` flux balance, `2e-8` or `2e-4`
flux-versus-S by Gamma regime, `2e-6` independent complex-S comparison, and
`2e-4` independent small-Gamma log comparison. No missing node can close a
ladder, and the conservative numerical uncertainty is the maximum applicable
measured axis difference.

Convention uncertainty remains separate and cannot absorb numerical drift.
It records exact Fourier sign, tortoise additive constant, RW master-function
normalization, `In/Up` unit-transmission definitions, current orientation,
and V3-F02 conversion. A convention mismatch is `OPEN/FAIL`, not a phase fit
or an enlarged tolerance.

## 7. Independence accounting

| Route | Relationship to proposed V3.1-X Route C |
|---|---|
| Route A | Independent algorithm/runtime: protected SchWO float64 scaled-tortoise/Jost path versus Wolfram NDSolve/BHPT sources. Shared physics conventions only. |
| Route U | Independent implementation/runtime: SchWO's mpmath HP unitarity-deficit oracle versus BHPT/Wolfram direct integration. No U bytes or results feed Route C. |
| Route B/AP | Independent implementation/runtime and separate fresh solves. The RW equation and V3 conventions are necessarily shared. No AP result initializes, normalizes, selects or repairs Route C. |
| failed MST route | Same BHPT distribution, public dispatcher and Wolfram runtime, but a distinct MST algorithm. It is not an independent source ecosystem. It is replaced, not combined; any future exact-input MST output is diagnostic only. |

The external claim remains odd-only. It cannot certify an independent even
solve. The exact odd/even parity certificate continues to depend on fresh
Route-A/Route-B odd and even solves, not parity-derived external data.

## 8. No-selection acceptance and call accounting

The future gate must require:

1. the exact ordered 23-key inventory and seven mandatory nodes per key;
2. exactly 161 official public API calls and 322 `In/Up` boundary solutions;
3. all 161 node records present, canonical, ordered and unique;
4. exact three-radius overlap records for every node;
5. zero MST call, internal-solver call, fallback, retry, cache hit, prior-root
   reuse, per-key method choice, dropped error, reordered node, or post-hoc
   selected result;
6. every external numerical ladder and applicable unchanged threshold PASS;
7. all 23 selected records compare to their fresh Route-A counterpart under
   unchanged `V3T-S-COMPLEX-001` and `V3T-LOGGAMMA-001` domains;
8. a fresh whole-gate official root that also recomputes Route A, Route U and
   Route B and closes exact `496/9920`, `318/954`, `102/458`, Route C counts,
   all 16 thresholds and all five certificate IDs.

An error at any mandatory key/node terminalizes the attempt. Passing MST data,
a lower-precision value, the nearest successful key, or `Gamma_S` reconstructed
from `Gamma_flux` cannot replace it.

## 9. Bounded sentinel and control-plane design

The predeclared sentinel is deliberately not a favorable subset:

- run the selected direct node freshly for **all 23 keys**;
- additionally run the six non-selected ladder nodes for the two fixed
  geometry extrema, ordinal 3 `(0.1,8,odd)` and ordinal 22 `(4,28,odd)`;
- deduplicate their selected nodes, for exactly `23+2*6=35` API calls,
  70 boundary solutions and 105 overlap records;
- require all 35 nodes and the complete source/runtime/publication gates to
  PASS; none of its numerical values may be copied into the official root.

The two extra keys are fixed by input geometry before results, not selected by
success. Sentinel and official execution each require a distinct one-use T0
dispatch, absent fresh UTC root, exact argv/environment, exclusive stable
writer lock, request/authority publication before science, one child process,
exact wait/reap/process-group-empty closure, and source/runtime start/end
equality.

Each node publishes a raw receipt and either a success record or an error
record. A batch publishes exact totality even on scientific error. Files are
O_EXCL/no-follow, atomic, fsynced, nlink-1 and terminal mode `0444`; directories
close `0555`. Failure publishes `failure.json` and a non-self-referential
failure manifest, marks the root non-resumable, and forbids retry. A genuine
system interruption may be resumed only by a separately frozen, formally
reviewed contract-bound protocol; it is never inferred from an absent terminal
file.

Required provenance includes:

- full 25-file/five-directory BHPT base snapshot identity;
- every generated overlay's base hash, exact two transformations, final hash,
  node binding, and loaded-source start/end record;
- exact WolframKernel path/hash/version and loaded contexts/files;
- Python executable/runtime, producer/controller/test/package/review/dispatch
  identities;
- V3.0 authorities, seven protected files, predecessor denylist and
  `predecessor_science_reused=false`;
- canonical request, prelaunch, running, raw streams, receipt, terminal,
  source end, result/certificate and manifest identities.

## 10. Runtime and storage projection

Only immutable timing evidence is used. The bounded direct run completed 60
API calls (each an `In/Up` pair) with 40/60-digit nodes:

```text
solver sum       1519.291646 s
wall summary     1647.185409 s
per-call min     1.704413 s
per-call median 15.417895 s
per-call max   159.058995 s
```

Its modes extend to `(kM=4,ell=360)`, substantially higher ell than this
23-key set, but its outer-boundary geometries are not identical to the proposed
multiplier-8 ladder. Straight count scaling gives:

- 35-call sentinel central wall estimate: about 16.0 minutes;
- 161-call official Route-C central wall estimate: about 73.7 minutes;
- applying the observed per-call maximum to all official calls: 7.11 solver
  hours, about 7.7 hours with the observed wall/solver overhead.

These are estimates, not guarantees. The multiplier-8 and `kM=0.1` geometries
are outside the stored timing envelope, so a defensible hard upper below the
existing 36-hour governance ceiling is currently unknowable. The frozen
package should require the predeclared 35-call sentinel to produce classed
timings and then compute an upper official projection using the maximum
observed time in each fixed geometry class, inflated by the exact radial-domain
length ratio and a fixed safety factor of at least 2. Official dispatch is
forbidden unless that projection is `<=36 h` and disk projection is below the
frozen free-space fraction. This resource calculation may stop a run but may
not select scientific keys or methods.

The bounded root stores 368,927 logical bytes for 60 nodes (652 KiB allocated).
Linear scaling gives roughly 1.0 MB logical for 161 nodes. Including raw
streams, source ledgers, overlays, supervision, manifests and failure reserve,
use conservative caps of 5 MB for the sentinel and 20 MB for the Route-C
official subroot. The complete fresh V3.1-X root additionally includes fresh
Route A/U/B evidence and must use the separately frozen whole-run disk gate.

## 11. Exact future implementation scope

No implementation is authorized now. The recommended future T4 implementation
scope is exactly these six new paths:

```text
scripts/phase6_v3_1_x_bhpt_direct.wls
src/schwgw/validation/phase6_v3_external_direct.py
src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
scripts/phase6_v3_1_x_external_direct.py
tests/unit/test_phase6_v3_external_direct.py
tests/regression/test_phase6_v3_external_direct_publication.py
```

The first two own exact-input BHPT direct nodes and their validation. The third
is a new whole-gate orchestrator that calls the byte-frozen Route A/U/B
implementations for fresh science and substitutes only the newly reviewed
Route C; it must not read predecessor science. The fourth is the sole CLI. The
last two cover pure contracts and temp-copy publication/fault paths. No seven
protected radial file, V3.0 authority, predecessor implementation or immutable
root is editable.

Root T0 should freeze a separate package graph, for example:

```text
configs/phase6_v3_1_x_external_direct_route_package.json
docs/phase6_v3_1_x_external_direct_route_design.md
docs/prompts/phase6_t4_v3_1_x_external_direct_route.md
docs/prompts/phase6_t7_v3_1_x_external_direct_route_package_review.md
docs/prompts/phase6_t7_v3_1_x_external_direct_route_science_review.md
```

The package must hash-bind this analysis, all V3.0 authorities, base snapshot,
overlay transformation table and resulting hashes, exact 23/35/161 call
graphs, source roles, runtime cap, expected artifacts, tests and future review
prompts. Formal T7 package acceptance is mandatory before any sentinel.
Sentinel terminal review is mandatory before a separate official dispatch.
The official root then requires a separate formal T7 scientific review before
any V3.2 action.

Minimum package-review acceptance items are:

- exact decimal-to-rational frequency construction and precision assertion;
- exact 23-key and seven-node derivation, no selection/fallback/reuse;
- only the declared `NumericalIntegration.m` odd-boundary bytes differ;
- AST/source gates prove public BHPT direct `In/Up` calls and zero MST/internal
  solver calls;
- exact Wronskian signs, amplitude normalization, V3-F02 conversion and
  direct-flux versus S-route separation;
- complete positive/adversarial tests for key/node totality, duplicate/gap,
  noncanonical/torn output, frequency precision, overlay drift, loaded-source
  drift, boundary/match/conditioning failure, parser digit consistency,
  source start/end, process closure, immutable publication, one-use dispatch,
  predecessor nonreuse and terminal failure;
- exact 35-call sentinel and 161-call official resource projections;
- explicit nonclaims: odd-only external, no pristine-upstream claim, no
  V3.1/V3.2/global GREEN before independent review.

## 12. Recommendation and nonclaims

**Recommendation:** freeze a distinct V3.1-X package implementing the single
BHPT NumericalIntegration route above for all 23 anchors, with the exact
node-local boundary overlay and no MST fallback. This is scientifically
defensible because it uses independent `In/Up` integrations and controlled
Wronskian matching, retains direct horizon flux separately from `1-|S|^2`,
preserves every frozen V3 authority, and eliminates result-conditioned method
selection. It is operationally conditional on formal package review and the
predeclared sentinel/resource gates.

Established evidence does **not** prove that the proposed route will pass all
23 keys or finish within the hard runtime cap. The nine MST failures are
method-totality failures, not failures of the physical quantities. The 14 MST
successes are nonpromotable. V3.1 and V3.1-U remain FAIL, V3.1-X remains
NOT_ASSESSED, V3.2 remains blocked, and no global GREEN is claimed.
