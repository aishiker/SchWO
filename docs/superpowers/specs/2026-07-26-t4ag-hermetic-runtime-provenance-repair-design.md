# T4ag Hermetic Runtime-Provenance Repair Design

## 1. Purpose

T4af ended correctly with:

```text
RED / EQUIVALENCE-PRESERVING METHODS GATE INVALID
```

The only prospective `kM=1.58125` witness authorized by T4af reached the
frozen scientific runner but stopped at its import boundary:

```text
ModuleNotFoundError: No module named 'scipy'
```

The durable final record is valid and immutable. The child exited `1`,
produced 370 bytes of stderr, was reaped, left an empty process group, and
created no scientific output pair. The solver was never reached. T4ag does
not reinterpret that RED result and does not reuse the consumed
authorization.

T4ag repairs only the missing hermetic runtime-dependency provenance. It
adds a content-addressed, read-only Python runtime overlay and binds that
overlay into the existing durable driver. It does not change the scientific
runner, implementation, configuration, inputs, frequencies, tolerances,
thresholds, modes, points, lmax values, or acceptance rules.

## 2. Frozen Starting Identity

T4ag starts from the exact accepted T4af and implementation identities:

```text
repair candidate               78b80129515d5c5ae60de9ec3367d6e3d12925d5
candidate parent / primary     45face32f52537ac4b8ab79cb1746d8ac78e9b82
candidate ref                  refs/heads/codex/t4af-control-provenance-repair-candidate
runner SHA-256                 18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768
benchmark identity             46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48
benchmark environment          04b4a8c8964716ae0ee46b2a4736cbe47cd1212f60a08a212c2366fbbc387615
CPython 3.14 binary            b502cb4c5b46b8d4192ec6bcb600ce8922f1afc396fcf646e8765c6eba74a0bf
last frozen driver             573c784b15d670e324ab56b602aa558344abadefae07b05ec613fa8b8178d083
last preflight manifest        1ee3423ffe052006fc053eb804293ea3a7ce4f54eb57abfd9506011dcb034abf
last raw index                 80630f3d274d9033e7e8b032aeb4d3bb558c7bfe29f0554d09560beae994f49a
last capture index             04fed92020f3362d60ff1c104b9dfe1a10a983920070f1f054078077f293d667
```

The T4af exact-four design/plan/prompts, the exact-fourteen implementation,
all legacy/golden/canonical data, all successful and failed preflights, and
the failed witness tree remain immutable.

The failed witness evidence is fixed:

```text
root
  runs/phase5/equivalence_preserving_methods_gate/control_provenance_witness/
  witness_kM_1p58125_20260726T114847p0800/
request
  546d184155e75ee93a6cbc08f3fd2b2385f289fd0c94a3054bc4307c3a575750
durable final
  f40cc69756ccc07ea11a6d1006aa39a0e4b2f62a5c12aedc804d871788c480d8
stderr
  370 bytes
  effc003d8acea8d9869cfc1c9aadaec9e307308471124b615ad7909d0ab81786
```

## 3. Established Runtime Diagnosis

Root T0 reproduced the failure without invoking the scientific runner:

- exact CPython is 3.14.6;
- NumPy 2.4.6 is visible from
  `/opt/homebrew/lib/python3.14/site-packages`;
- SciPy 1.17.1 is installed only under
  `/Users/aishiker/Library/Python/3.14/lib/python/site-packages`;
- PyYAML 6.0.3 is installed under the same user site and is required by
  `schwgw.io.config`;
- the isolated witness `HOME` correctly hides that mutable user site;
- with the user site explicitly placed on `PYTHONPATH`, an import-only probe
  loads NumPy, SciPy, PyYAML, the exact required `schwgw` modules, and the
  frozen runner module without starting a solver.

Directly exposing the mutable user site to a new witness is not accepted.
The repair must snapshot the required distributions into immutable control
evidence.

## 4. Runtime Overlay Contract

### 4.1 Exact source distributions

The overlay may source only these already-installed local distributions:

```text
SciPy   1.17.1
  scipy/**
  scipy-1.17.1.dist-info/**

PyYAML  6.0.3
  yaml/**
  _yaml/**
  pyyaml-6.0.3.dist-info/**
```

No network access, `pip`, `conda`, `brew`, package installation, dependency
upgrade, or global/user environment modification is permitted.

NumPy 2.4.6 remains part of the already accepted exact CPython/Homebrew
runtime. Its resolved origin, version, configuration identity, and imported
binary-module origins must be recorded and checked, but its Homebrew
symlink-farm is not copied into the overlay.

### 4.2 Copy and publication rules

The builder is artifact-local and may write only under a fresh unique
directory below:

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/hermetic_runtime/
```

It must:

1. lstat and hash every source file before copying;
2. reject source or target path escape, symlink, hardlink/shared inode,
   device/socket/FIFO, duplicate target, `.pth`, bytecode, `__pycache__`,
   and pre-existing destination;
3. copy regular files without following links into a fresh unpublished
   staging directory, using exclusive creation;
4. fsync every file and every created directory;
5. verify exact source and target size/SHA-256 after each copy;
6. re-lstat and re-hash every source after the complete copy to reject
   source drift;
7. verify every target is regular, single-link, non-symlink, and confined to
   the overlay;
8. make files read-only and directories non-writable;
9. compute a canonical file index and content identity;
10. atomically publish the completed directory under a content-addressed
    name and fsync its parent;
11. atomically publish a final manifest binding source and target
    identities, versions, wheel metadata, RECORD hashes, file modes,
    compiled-extension inventory, Mach-O dependency inventory, Python
    identity, and package index.

An interrupted or failed build remains failed evidence and cannot be used by
a runner. It must never be silently cleaned, resumed, overwritten, or
treated as a valid overlay.

### 4.3 Exact runtime environment

Every import probe, new witness producer, matching official audit, and later
matrix process must use:

```text
PYTHONNOUSERSITE=1
PYTHONDONTWRITEBYTECODE=1
PYTHONHASHSEED=0
PYTHONPATH=<published-overlay>:<exact-project-root>/src
HOME=<fresh-isolated-home>
```

The existing controlled thread variables remain exact. No mutable user-site
fallback is allowed.

Before and after every child, the driver must verify:

- overlay manifest path and SHA-256;
- overlay canonical file index and every file SHA/size/mode/inode/device;
- read-only, non-symlink, single-link status;
- no overlap or alias with canonical, output, control-run, source, legacy,
  golden, configuration, or detached-input paths;
- exact `PYTHONPATH` ordering and `PYTHONNOUSERSITE=1`;
- exact module origins: SciPy and PyYAML inside the overlay, NumPy inside the
  accepted Homebrew runtime, and `schwgw` inside the exact project root;
- unchanged CPython binary, NumPy/SciPy versions, benchmark environment
  identity, and controlled thread environment;
- no bytecode/cache creation.

## 5. Bounded Driver Change

The existing artifact-local durable driver may be changed only to add:

- a closed runtime-overlay manifest schema;
- request bindings for the exact overlay root, final manifest, canonical
  index, and environment;
- validation of the runtime overlay before launch and after child
  completion;
- the same runtime binding for producer and matching official audit;
- witness and matrix phase-specific project-root checks;
- positive and negative solver-free tests for these new bindings.

The existing process supervision, post-Popen fault behavior, atomic
records, scientific-audit producer binding, exhaustive 48-input contract,
source manifests, phase-specific witness/matrix roots, canonical guards,
and all scientific acceptance semantics must remain unchanged.

No implementation file, runner, config, input, legacy/golden/canonical
artifact, frozen package, threshold, or scientific record may be modified.

## 6. Phase A — Zero-Science Runtime Freeze

Phase A may:

1. preserve the old driver and all old evidence immutably;
2. build exactly one successful overlay after local static validation;
3. modify only the artifact-local driver and its synthetic tests;
4. run import-only probes that import the exact required SciPy, PyYAML, and
   `schwgw` modules but never execute the runner CLI or a solver;
5. run one fresh full exact-Python-3.14 zero-science preflight.

The import probe must cover at least:

```text
numpy
scipy
scipy.integrate
scipy.interpolate
scipy.special
yaml
schwgw.io.config
schwgw.io.results
schwgw.numerics
schwgw.scattering.partial_wave
schwgw.io.tablei_another_bounded_local_refinement
```

It must record exact module origins and loaded compiled extensions. Scientific
runner CLI invocation and solver invocation must both remain exactly zero.

The new preflight must rerun every prior T4af positive/negative/fault/lock/
audit/path/identity test plus runtime-overlay positive and negative cases.
It must also pass AST, Ruff, `git diff --check`, raw/capture index,
environment, canonical, old-evidence, absent-unit, process, transient,
symlink, and hardlink checks.

Phase A returns exactly:

```text
CHECKPOINT / HERMETIC RUNTIME ENVIRONMENT FROZEN
```

and pauses. It must report the new driver SHA, builder SHA, runtime manifest
SHA, overlay index, preflight manifest/raw/capture indexes, tests, import
origins, zero-science counts, process state, and subagent counts.

## 7. Independent Gates And New Prospective Witness

T7 must independently review this exact four-file package before T4ag
starts. T4ag requires exact:

```text
REVIEW GREEN / T0 RUNTIME REPAIR PACKAGE APPROVED
```

After Phase A, root T0 independently audits every builder, overlay, driver,
manifest, raw record, capture, test, package origin, canonical guard, and
process state.

Only root T0 may then issue:

```text
AUTHORIZED / HERMETIC-RUNTIME CONTROL-PROVENANCE WITNESS COMPUTE
```

That authorization permits one new prospective isolated witness for the
existing `kM=1.58125` case. It is a new reviewed attempt under a new frozen
runtime identity, not a reuse or reinterpretation of the failed T4af
attempt.

The witness and its matching official audit retain every T4af acceptance
condition. Canonical data remain read-only. The witness remains excluded
from performance, cache/checkpoint, matrix, and downstream evidence. Any
failure consumes the new authorization and stops without retry.

## 8. Conditional Matrix And Final Gate

Only after the new witness and matching official audit pass and root T0
freshly verifies them may T0 issue the original matrix continuation.

The remaining work order stays fixed:

```text
kM=2.91875
kM=3.759375
kM=3.89375
full accepted 241x241 image configuration
```

Each producer and official audit uses the same frozen runtime overlay and
durable driver and must pass before the next unit starts.

Only final T4 GREEN plus root-T0 full T4ae verification permits the frozen
T7ch review. T4ag does not authorize a new frequency, production expansion,
plotting, fixtures, Kirchhoff work, paper claims, or GitHub action.

## 9. Orchestration Policy

Use only:

- the existing T4 task `019f5fa6-1288-7c01-8a87-4c4370cf5517`;
- the existing T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed`;
- the single existing local proxy
  `019f9be5-2deb-7c52-b740-a0db8fa387ca`.

Do not create another task, proxy, subagent, or descendant. The proxy may
review low-complexity control-plane details but cannot approve the package,
authorize a witness, decide scientific acceptance, continue the matrix, or
dispatch T7ch.
