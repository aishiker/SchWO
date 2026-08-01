# T4aq Lazy-Oracle Loaded-Module Closure Repair Design

## 1. Purpose

Repair one exact provenance defect exposed by the consumed
`frequency:2p91875` matrix producer without changing the scientific runner
bytes, scientific source, runtime dependencies, complete-input meaning,
fixed benchmark identity, canonical data, scientific criteria, or matrix
order.

The repair is control-plane only. It introduces one frozen, transparent
launcher adapter that executes the unchanged primary runner while
normalizing one reviewed lazy-import pair out of the runner's
loaded-module *set* digest. The original loaded-module verifier must still
validate the path and content identity of every loaded module, including
the two normalized records.

## 2. Immutable Failure Boundary

The consumed matrix attempt is:

```text
sequence
  runs/phase5/equivalence_preserving_methods_gate/
    control_provenance_witness/
    t4ae_matrix_sequence_61c23880_20260727T162000p0800
unit
  unit_2p91875_attempt2
producer run
  control_runs/t4ae_matrix_2p91875_producer
```

Frozen records:

```text
producer request
  0c98d160abc01f60ad18190472c9d8e6e36f05cd35f9a0219dd9f8ae609f7b32
prelaunch
  eacce8055ef6c21d1be835623597883aae9ad75ba3a0662b9d4923ad8486bcd4
running
  847d07a3a09debde79c1528762272958a8354ed63e04dc21929b198fb6d025d5
final
  e6afab6ffed105218b5d7b436ed42ecb8dbd4efea1a36b87acd76823ca583a24
launch receipt
  1c81db603ec9fb63f182883270aa61389eb2c2fe443580f40139a9adcf327966
stdout
  215 bytes /
  c5e45478b42a85f4e6997e9e24aaa732480961c5474639125899d3008cb3a321
stderr
  1314 bytes /
  81ff8c1a43030bbc899be256e2d4abe6188473db88473394605ba21b600a8c2e
failure checkpoint
  bbd8ae0645b8b9c07de6b6c96df456e194b38619fd57cbcd8c69ead52f51ecaf
```

The exact child PID/SID/PGID was `59291`. It exited naturally with code
`1`, no signal, exact wait/reap, zero wait errors, and an empty process
group. The traceback terminates at:

```text
GateContractError:
  frozen identity changed during frequency:2p91875:post_compute
```

The normal durable audit is `valid=true`; source bindings, canonical
guards, runtime overlay, stream hashes, wait/reap records, and semantic
cross-checks pass. Official audit and every later matrix unit were not
started. The attempt and its authorization are consumed and non-reusable.

The complete failed unit tree is immutable evidence: `2957` regular files,
`362` directories, `604815842` file bytes, no symlink, no non-one hardlink,
and canonical file-ledger SHA-256
`16051aa1fcfe986c2743d39afe1d10933a4d74e9f4c8cb4342ee4d42af690895`.

## 3. Exact Root Cause

The unchanged runner freezes loaded `schwgw` modules before science:

```text
initial module count
  44
initial loaded-module manifest
  190176ee7707a7579f8f504168d310f1ea5a34cf1c98c493f63e121a16db81f5
```

The frozen legacy `kM=2.91875` sidecar has:

```text
adapter
  q018_tablei_another_bounded_local_transition
adapter_use_count
  98
warning code
  q018_tablei_another_bounded_local_transition_oracle_used
```

The reviewed adapter path in
`src/schwgw/numerics/radial_solver.py` performs this import inside the
solver path:

```python
from schwgw.numerics.experimental.q018_rescaled_oracle import (
    RescaledOracleRequest,
    solve_q018_rescaled_oracle,
)
```

An exact Python-3.14, exact-environment, import-only reconstruction from the
accepted detached input view proves that this import changes only the
loaded-module set:

```text
added modules
  schwgw.numerics.experimental
  schwgw.numerics.experimental.q018_rescaled_oracle
post-import module count
  46
post-import raw loaded-module manifest
  9dc258e57a7e103f23809f418124ed75ff6e4a5a95eaeb33a84c17d4ebaa2fde
```

The same reconstruction independently recomputes implementation, source,
gates, config, environment, selected-code hashes, Table-I inputs, and the
seven-field benchmark identity after the import. Every one remains exactly
equal; only the loaded-module manifest differs.

This is sufficient to cause the exact observed `_recheck_identity()` error.
It is a deterministic provenance-set defect, not a scientific-value
failure and not an environmental or filesystem drift.

## 4. Frozen Scientific And Runtime Identity

The repair must retain exactly:

```text
primary HEAD
  45face32f52537ac4b8ab79cb1746d8ac78e9b82
runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768
driver before repair
  61c2388080e402586c2a2ef7be12f99400c35be4d9f2603c2d5bcf91b051d0bb
complete-290 contract
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24
fixed benchmark identity
  46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48
T4ai witness checkpoint
  2c448a70ed9dc47399c9bb1f148add60315670d4e66c886e5e7895abb5e8cde9
T4ap v14
  8d3a9594d5a818979c698d53106156049ed384ae25ee89d4998f75d398bb98f7
```

The exact oracle source identities are:

```text
schwgw/numerics/experimental/__init__.py
  b4592c0c4788757a4fb726772cc25ce1a418c14ee2d92313e4388b6e5aaef260
schwgw/numerics/experimental/q018_rescaled_oracle.py
  cbaf3bcdb8000ff0965997b59e1be4c62e1112c3a35162e2aca52758db45589d
```

The repair may not modify either file.

## 5. Stable Loaded-Module Projection

The scientific runner remains byte-for-byte unchanged. One immutable
artifact-local launcher shall:

1. verify its own frozen digest and exact file identity;
2. verify exact Python, runner path/SHA, primary source root, cwd/input root,
   environment, and runtime overlay;
3. load the unchanged runner as a named module without invoking `main`;
4. retain the runner's original `_loaded_module_identity`;
5. install one exact wrapper around that function;
6. set logical `sys.argv` to the unchanged primary-runner command;
7. call the unchanged runner's `main()` exactly once and propagate its
   natural `SystemExit`/return code.

The wrapper must first call the original verifier. Therefore every loaded
module, including the lazy oracle pair, is still required to:

- have a source path under the primary `src/schwgw` tree;
- exist in the frozen source manifest;
- match exact SHA-256 and Git blob identity;
- satisfy all original required-module checks.

Only after those checks may the wrapper remove these exact module names
from the manifest-set projection:

```text
schwgw.numerics.experimental
schwgw.numerics.experimental.q018_rescaled_oracle
```

No prefix, glob, regex, argument-controlled list, basename match, or
additional module is allowed. The normalized records must remain in exact
canonical order and must reproduce:

```text
count
  44
manifest_sha256
  190176ee7707a7579f8f504168d310f1ea5a34cf1c98c493f63e121a16db81f5
```

Both allowed states are:

- neither reviewed lazy module is loaded;
- both reviewed lazy modules are loaded and validated, then excluded only
  from the set digest.

A one-of-two partial state is invalid. Any other added, removed, aliased,
wrong-origin, wrong-content, or duplicate module must fail closed.

This projection preserves the existing complete-pair sidecars, whose
post-compute loaded-module manifest is the exact 44-module value, and makes
the legitimate `2.91875` lazy import stable without changing the fixed
benchmark identity.

## 6. Transparent Launcher Provenance

The launcher is not hidden scientific source. The artifact-local durable
driver must bind it explicitly with:

- path, realpath, SHA-256, size, device, inode, nlink, mode;
- exact launcher schema/version;
- exact primary runner path/SHA;
- exact two-name normalization allowlist;
- exact raw 44/46 and normalized 44 manifest identities;
- exact logical runner argv and physical launcher argv;
- exact environment, cwd/input root, source/input manifests, and output
  root.

The launcher must be regular, non-symlink, nlink-1, read-only, and outside
the detached input and canonical output roots. Producer and matching
official audit must use the same launcher bytes and bindings.

The runner-visible `sys.argv` and embedded `source_command` remain the
unchanged primary runner command. The durable control records separately
store the physical launcher command. Process guards must track the exact
launcher child and must still reject any unrelated runner, launcher,
duplicate, alias, or descendant.

No `-c`, stdin program, `sitecustomize`, user-site exposure, import-hook
package, overlay mutation, source copy, runner copy, output copy, or
post-hoc sidecar rewrite is allowed.

## 7. Phase-A Tests

All Phase-A tests are exact Python-3.14 and solver-free.

Required positive cases:

- initial raw 44 modules normalize to exact 44/`190176...`;
- exact oracle import produces raw 46/`9dc258...` and normalized
  44/`190176...`;
- all other identity components remain exact after the import;
- existing `0.86875` and `1.58125` complete-pair audits pass through the
  launcher;
- split-root matrix preflight passes through the launcher with
  `solver_started=false`;
- producer and official-audit request validation bind identical launcher,
  logical runner, roots, manifests, runtime, and identity;
- logical source command remains byte-for-byte the primary runner command;
- final and replay validation consume the same launcher binding.

Required negative cases:

- missing or partial allowlisted pair;
- extra `schwgw` module such as `schwgw.cli`;
- prefix/basename/Unicode/case alias;
- wrong module source, content, blob, origin, or symlink;
- wrong launcher hash/path/mode/inode/nlink or writable launcher;
- launcher inside input/output root or aliased to runner/driver/input;
- physical/logical argv mismatch;
- producer/audit launcher mismatch;
- direct unadapted `2.91875` provenance simulation remains rejected;
- default-true/false serialization cross-use;
- changing the normalized baseline count or digest;
- changing runner/source/runtime/input/fixed identity/canonical paths,
  thresholds, tolerances, modes, points, resolution, `lmax`, or order.

## 8. Phase-A Checkpoint

T4 may modify only artifact-local control driver/helper/launcher/tests and
fresh durable evidence. It must preserve the failed matrix sequence and all
earlier evidence roots unchanged.

After static/AST/dataflow/Ruff/diff checks, exact import-only regressions,
full zero-science synthetic preflight, and one fresh real split-root
`preflight/matrix` through the frozen launcher all pass, T4 returns:

```text
CHECKPOINT / STABLE LAZY-ORACLE MODULE CLOSURE FROZEN
```

The real preflight must exit naturally `0`, emit empty stderr, be exactly
waited/reaped with an empty process group, preserve fixed identity
`46403a...`, audit both existing pairs, report `solver_started=false`, and
leave all eight later output files absent.

The checkpoint authorizes no producer, official audit, solver, canonical
write, or retry. Root T0 must independently audit it before issuing a new
one-shot matrix authorization.

## 9. Downstream Boundary

Only after T4aq checkpoint and root-T0 full PASS may a new authorization
restart the still-fixed sequence:

```text
2.91875 -> 3.759375 -> 3.89375 -> full 241x241
```

The consumed failed `2.91875` attempt is never reused, repaired, promoted,
or reinterpreted. Any future producer or official-audit child failure
again consumes that unit and forbids retry.

T7ch, T8, new frequencies, production, plots, fixtures, Kirchhoff, paper,
GitHub, threshold relaxation, canonical overwrite, destructive cleanup,
global environment changes, and new tasks/agents remain forbidden.
