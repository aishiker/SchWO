# T4bb True Solve-Count Cache Repair Design

Date: 2026-07-28

Status: root-T0 bounded repair candidate. This package repairs one failed
performance gate. It changes no scientific equation, frequency, point, mode,
`lmax`, tolerance, residual gate, equivalence budget, or canonical artifact.

## 1. Trigger And Exact Boundary

T7ch returned:

```text
ACCEPT YELLOW / EQUIVALENCE-PRESERVING METHODS EVIDENCE INCOMPLETE
```

Independent T7ch and root-T0 recomputation agree:

```text
legacy solve count      3668
optimized solve count   3668
frozen limit            floor(0.70 * 3668) = 2567
optimized / legacy      1.0
```

All scientific-equivalence gates passed. The five frequency artifacts and
the full `241x241` artifact remain accepted, immutable equivalence evidence.
They must not be rewritten, promoted, or treated as a performance PASS.

The only objective is to make the already designed read-only radial cache
part of the real optimized execution path and to produce fresh, noncircular
performance evidence whose *actual online* ODE/oracle solve count is at most
`2567`.

## 2. Frozen Inputs

```text
implementation                 45face32f52537ac4b8ab79cb1746d8ac78e9b82
accepted sequence              t4ae_matrix_sequence_t4ba_fa453e3c_20260728T171000p0800
sequence closeout              874614247bd40231abb309b9bc7321a0bdfbdeec5934908497edbca907bc5be1
driver                         fa453e3c399e54e87855603b84d0f37b4206ef23c4420439814cd5f93b56732d
runner                         18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768
runtime manifest               f3ebf3dbf8981500c8d7f714b1740996638f10e32ef17a8377d45ea0b70ab6ca
complete-290                   77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24
fixed identity                 46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48
T4ad oracle validation         runs/phase5/fig5_fig6_another_bounded_local_radial_gate/oracle_validation.json
T4ad oracle record count       12492
```

The T4ad file is immutable historical evidence. For the benchmark cases it
contains exactly:

```text
kM=2.91875   98 exact point records
kM=3.759375  408 exact point records
kM=3.89375   480 exact point records
total        986 exact point records
```

Those records may be admitted only through exact content, schema, snapshot,
origin, mode, point, radius, tolerance, and current-consumer identity
validation. A cache hit is not a solve. A fallback calculation is a solve.

## 3. Pre-Registered Count Closure

After admitting the 986 immutable T4ad records, the remaining online count is
`2682`, which still fails. No count may be relabeled or omitted.

The bounded second cache is the complete low-frequency mode set for the
already frozen `kM=0.86875` case:

```text
sectors                    odd, even
ell                        2..84 inclusive
unique dense mode solves   2 * (84 - 1) = 166
Table-I points             exact frozen eight points
projected point records    166 * 8 = 1328
```

It is generated once, after the final implementation identity is frozen,
with the unchanged solver and exact frozen boundary/tolerance inputs. A
matching independent audit must verify every scalar value and diagnostic
against an ordinary unchanged-solver reconstruction before the cache may be
used.

The registered fresh-online count is then:

```text
0.86875     0
1.58125     286
2.91875     524
3.759375    666
3.89375     682
full image  358
total       2516 <= 2567
```

Any different case selection, missing record, fallback solve, duplicate,
count relabeling, or total above `2567` fails closed. Cache-generation work is
reported separately and may not be hidden inside benchmark accounting.

## 4. Phase A — Zero-Science Implementation

Phase A may modify only the existing methods implementation surfaces needed
to:

1. route real frequency execution through the existing identity-scoped
   `RadialCache` contract;
2. load T4ad records through a strict read-only adapter;
3. load a future low-frequency cache through the same typed admission
   boundary;
4. distinguish `fresh_ode_solve`, `fresh_oracle_solve`, `ordinary_hit`, and
   `oracle_hit` without argument-controlled or boolean-controlled relabeling;
5. preserve the unchanged logical runner, `_compute_frequency`,
   `compute_polarization`, reconstruction, warning, residual, and output
   semantics;
6. bind physical launcher argv separately from logical runner argv and bind
   producer/audit/replay to the same implementation, cache, input, runtime,
   and fixed identities.

Only synthetic/in-memory fixtures, static dataflow checks, focused/full tests,
Ruff, and zero-science preflights are allowed. No solver, producer, official
audit, benchmark, or canonical write is allowed in Phase A.

Phase A ends exactly:

```text
CHECKPOINT / TRUE SOLVE-COUNT CACHE DATAFLOW FROZEN
```

Pre-execution artifact-local defects may be corrected by T4 in fresh
no-overwrite roots. Scientific-source, runner, solver, threshold, tolerance,
frequency, mode, point, `lmax`, runtime, or canonical changes return to T0.

## 5. Phase B — One-Shot Low-Frequency Cache

Phase B requires a separate root-T0 authorization after a full Phase-A audit.
It launches exactly one unchanged-solver producer for the registered 166
modes and exactly one matching audit. It creates no optimized NPZ/JSON result
and writes only a fresh immutable cache evidence root.

The producer and audit must bind:

- final implementation commit and exact path blobs;
- exact source/input/runtime/fixed identity;
- exact `kM=0.86875`, sectors, `ell=2..84`, eight points, boundary and
  tolerances;
- exactly 166 ordinary solves and 1328 point records;
- regular non-symlink `nlink=1`, read-only, no-alias records;
- exact finite scalar payloads, diagnostics, certified radii, record order,
  content index, and terminal manifest;
- exit/signal/wait/reap/process-group closure and empty stderr.

Any launched failure consumes Phase B and cannot be retried under the same
authorization.

## 6. Phase C — Fresh Isolated Six-Case Benchmark

After cache PASS and root-T0 audit, Phase C runs the exact six cases in the
frozen order in a fresh isolated output root. Existing accepted canonical
artifacts are comparison inputs only and remain byte/stat/inode unchanged.

Each case has one producer and one matching official audit. The final matrix
audit must emit and independently verify:

- every existing scientific-equivalence and residual gate;
- exact cache admissions, hits, misses, rejections, and fallback counts;
- fresh online solve count `<=2567`, with no relabeling;
- aggregate wall/CPU, per-case wall, and peak-RSS limits unchanged;
- no canonical write, no old-pair reuse as computed output, no partial
  transaction, and zero residual process.

Only then may T4 return:

```text
GREEN / EQUIVALENCE-PRESERVING METHODS GATE READY
```

and T7ch may be rerun.

## 7. Forbidden

No threshold/tolerance relaxation; no changed frequency/mode/point/`lmax`;
no output-field substitution; no final-result cache; no cross-identity
reuse; no counting cache generation as a cache hit; no hiding fallback
solves; no production/plot/fixture/Kirchhoff/paper/GitHub work; no new task,
subagent, proxy, descendant, max, or ultra.
