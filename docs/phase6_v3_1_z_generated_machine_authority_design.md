# Phase 6 V3.1-Z generated machine-authority package design

Date: 2026-08-14 (Asia/Shanghai)  
Gate: `phase6_v3_1_z_generated_machine_authority_redesign_v1`  
Architecture: `GMA-Z1`  
Package status: candidate for formal source-distinct T7 package review  
Scientific status: `NOT_ASSESSED`

## 1. Package decision and boundary

This package realizes the accepted GMA-Z1 design as one declarative typed
canonical-JSON source, one package-time compiler, and one closed generated
authority bundle.  It is a control-plane package.  It does not implement or
execute the future runtime and it does not run Wolfram Language, BHPT,
arbitrary-precision radial code, a solver, Route A/U/B/C, a compatibility
root, a source-load micro, a sentinel, or official science.

The package-time compiler expands all behavior-bearing identifiers before T6:

1. complete 26-field predicate instances;
2. the 13 primary and 17 nested artifact schemas;
3. the domain-separated digest DAG and four operation state graphs;
4. canonical positive conformance vectors;
5. the exhaustive mutation recipe stream and exact expansion index;
6. package-frozen Python and Wolfram validators; and
7. a zero-science Wolfram compatibility observer.

The Wolfram child remains observation-only.  Parent authority owns every
expected value, comparison, evidence resolution, digest, transition, ACK,
stage-open decision, terminal decision, and future-authority check.  No
runtime callback or function name, dict/Association insertion order, glob,
`latest`, current handoff, prose-only behavior, or future review digest is an
authority input.

The package is distinct from V3.1-Y and is not Y repair cycle 3.  Every U/X/Y
runtime, value, cache, route map, checkpoint, request, dispatch, root,
transcript, timing, partial success, and failure remains threat-model evidence
only and is nonpromotable.

## 2. Frozen formal and scientific authorities

The declarative spec binds the following accepted design authorities:

| Role | Path | SHA-256 |
|---|---|---|
| accepted analysis | `docs/phase6_v3_1_z_generated_machine_authority_redesign_analysis.md` | `4d300bb9891763f7efa12d1f67bf993a98c39c93a49672618af6f1255472cd13` |
| accepted T4 archive | `docs/handoffs/archive/T4_2026-08-13_v3_1_z_generated_machine_authority_redesign_analysis.md` | `7d0ccac1f14edae616da381f135232db7f92af53c3bf0bc36c47f579283b9d5e` |
| formal design prompt | `docs/prompts/phase6_t4_v3_1_z_generated_machine_authority_redesign_analysis.md` | `6a7a6ecfe6d06be1630a9b9df3c266138c30b5e3bd4de4a2783c748da6b07d14` |
| review-gate liveness protocol | `docs/review_gate_liveness_protocol.md` | `3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181` |
| Root-T0 final Y adjudication | `docs/handoffs/archive/T0_2026-08-13_v3_1_y_final_escalation_adjudication.md` | `6b5d126565ab4f8764d65825c37589e37f52f2576d25593239c028ee1608c3f4` |
| formal T7 final Y review | `docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_delta_review_2.md` | `0ad54e21f62d233e6c26720918c85ac6dfdb12f254f02d6169ed4af348df9dd4` |
| terminal Y package | `configs/phase6_v3_1_y_external_protocol_package.json` | `5dc0b062c7da463bb3aa4283b38060201c8d6fd7a6902dd0d677273306b9d0b7` |
| terminal Y contract | `configs/phase6_v3_1_y_external_protocol_contract.json` | `c3d601940b8f297eb23cccad404c8ec5c326ffc6fb9a1dfa005ec6f5db3ef45c` |

The frozen V3.0 inputs are byte-identical and are not modified by GMA-Z1:

| Authority | SHA-256 |
|---|---|
| `docs/prompts/phase6_v3_master_prompt.md` | `f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7` |
| `docs/phase6_v3_0_validation_contract.md` | `0f8b8c96e01321231377c857ab40d710aa80ac06dce9084029fe2914b1ef37d3` |
| `docs/phase6_v3_0_formula_map.md` | `e5b556667c28ac8b611430d2dfb4faa5da82b9c7f0c8251251029e3f8c8d0eac` |
| `docs/phase6_v3_0_phase_taxonomy.md` | `fb91f4cf888dd4984174304783875c9f2e591490df8519bafd2e0b0f73053460` |
| `docs/phase6_v3_0_literature_matrix.md` | `088834348e980b81f814340a2a2c460b5bf11239521085c358bed7a90f603328` |
| `configs/phase6_v3_0_domain.json` | `803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b` |
| `configs/phase6_v3_0_thresholds.json` | `91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a` |
| `configs/phase6_v3_0_external_anchor_matrix.json` | `06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485` |
| `references/notes/phase6_v3_absorption_scattering_conventions.md` | `82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a` |
| `docs/handoffs/archive/T7_2026-08-11_v3_0_contract_review.md` | `b672c7f33d2f3cc891f455c6d8123ed846309a07244696da34236f8e254c0126` |

The exact package compiler runtime is CPython 3.14.6 at
`/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14`,
cache tag `cpython-314`, SHA-256
`b502cb4c5b46b8d4192ec6bcb600ce8922f1afc396fcf646e8765c6eba74a0bf`.
The WolframKernel is identity input only and was not launched:
`/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel`,
version `14.3.0 for Mac OS X ARM (64-bit) (July 8, 2025)`, SHA-256
`70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c`,
mode `0755`, nlink `1`, size `167488`.

The BHPT snapshot metadata SHA-256 is
`8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488`.
It binds 25 mode-`0444`, nlink-1 regular files and five mode-`0555`
directories, content inventory
`d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2`,
and restored identity inventory
`a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27`.

The project-local `mpmath` overlay is an exact-tree authority, not an ambient
import.  The frozen root
`runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314` contains 155
regular mode-`0644`, nlink-1 files, 14 mode-`0755` directories, 53 checked
CPython-3.14 bytecode files, and 4,075,822 file bytes.  Declaration-order
canonical digests are content
`d63a843bc3777d25005cfde6073faead19e5cf324522fa605ea763d5efb5559c`,
identity `70e7c3312f2b68b3dbb52a20b260de68a1ebb6c7596f5610f6c760bbb577c097`,
directory `04187b60e25cb250657c170e913c55e86c998b96dedc4087904eadc7d36dc06a`,
and portable tree
`57382a11ce8be19a6282e144323d9ee0ea15067fa7367d633b40833397fcf61a`.
The compiler validates every file, directory, `RECORD` entry, pyc magic/header
and source correspondence without importing the overlay.  Future runs require
the pure-Python backend with `MPMATH_NOGMPY=1`, `PYTHONNOUSERSITE=1`, a clean
fixed `PYTHONPATH`, and no `gmp`/`gmpy2` import candidate.

The only future science-observation helper allowlist is source-hash and
symbol-surface closed: `phase6_v3_external_direct.py`
`981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4`,
`phase6_v3_hp_unitarity_oracle.py`
`a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7`,
and `phase6_mpmath_radial.py`
`bb92fea624f01df347b0f3c5537bfd8be0319c0eb1d4302e9b81a26bef473c80`.
The transitive project import closure additionally binds `schwgw/__init__.py`,
`schwgw/validation/__init__.py`, and `contracts.py` by their spec identities.
The legacy CLI SHA-256
`01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4`
and every helper API that returns an admission `PASS` are denylisted.  Helpers
may produce observations only; the generated parent owns all comparisons and
verdicts.

The seven protected sources and their frozen SHA-256 identities are:

| Path | SHA-256 |
|---|---|
| `src/schwgw/numerics/radial_solver.py` | `9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9` |
| `src/schwgw/numerics/conditioned_radial.py` | `91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2` |
| `src/schwgw/numerics/scaled_tortoise_radial.py` | `d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df` |
| `src/schwgw/numerics/adaptive_jost_radial.py` | `3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896` |
| `src/schwgw/numerics/matching.py` | `9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340` |
| `src/schwgw/numerics/physical_boundary_radial.py` | `fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f` |
| `src/schwgw/numerics/boundary_conditions.py` | `b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22` |

## 3. Single-source and noncircular package layout

The canonical declarative source is exactly:

```text
configs/phase6_v3_1_z_machine_authority_spec.json
```

The downstream package record is exactly
`configs/phase6_v3_1_z_generated_machine_authority_package.json`.  It records
its literal path but cannot embed its own SHA-256; its observed final identity
is bound by each downstream prompt and formal review.

It has exactly the 39 top-level keys frozen in the accepted analysis.  Every
ordered collection is an array.  Objects are lookup maps only where unique-key
lookup is declared; object insertion order never carries semantics.  The
loader rejects duplicate, missing, extra, mistyped, noncanonical, or unresolved
content before expansion.

The package-time compiler is exactly:

```text
scripts/phase6_v3_1_z_generate_machine_authority.py
```

It may build only a fresh absent absolute output root.  It reopens immutable
inputs with no-follow regular-file checks, records start and end ledgers, and
fails if any path, resolution, device/inode, mode, nlink, size, mtime, or hash
drifts during a read or generation.  Its read-only `validate-spec`, `check`,
and `compare` commands do not mutate a frozen output tree.

The generated root is exactly `generated/phase6_v3_1_z`.  The closure is
layered to avoid self-reference:

```text
spec + generator
  -> generated leaves
  -> leaf_manifest.json (excludes itself, bundle_root, checkpoint)
  -> bundle_root.json
  -> package_checkpoint.json (closes files/directories; excludes itself)
  -> this design
  -> package JSON
  -> seven prompts, each binding the finalized package
```

The package contains no prompt SHA-256, no future archive SHA-256, and no
self SHA-256.  It contains only literal prompt/archive/dispatch/root paths and
their declared runtime identity source.  Each future prompt binds the already
finalized package/spec/generator/design and the three terminal generated
identities.  A future review digest enters only through a later one-use
dispatch after the named archive exists.

## 4. Canonical encoding and generated membership

Authority scalars are tagged arrays only:

```text
["s",string]  ["i",canonical-base10]  ["b",boolean]  ["n"]
["h",64-lowercase-hex]  ["d",canonical-AP-decimal]
["a",schema_id,...ordered tagged members...]
```

Canonical objects use sorted keys, UTF-8 without BOM, no NaN/Infinity, and
exactly one trailing LF.  Authority arrays use compact JSON and one trailing
LF.  JSONL has one canonical array per LF-terminated line.  All ART and DER
digests use the frozen `SCHWO-V31Z` domain separators and explicitly tagged,
ordered inputs.

The generated root contains these unsharded leaves:

```text
schema_catalog.json
digest_dag.json
operation_dags.json
path_grammar.json
authority_progression.json
resource_projection.json
validator_python.py
validator_wolfram.wl
compatibility_observer.wls
shard_inventory.json
conformance_vectors/conformance_expansion_index.json
mutation_oracle/mutation_expansion_index.json
```

It also contains predicate, conformance, and mutation JSONL shards, plus the
three noncircular terminal records:

```text
leaf_manifest.json
bundle_root.json
package_checkpoint.json
```

Every collection shard contains at most 4096 rows.  Names are exactly:

```text
<collection>/<collection>_<index:04d>_<first:09d>_<last:09d>.jsonl
```

Ordinals are contiguous, every nonfinal shard has 4096 rows, and the final
shard has the remainder.  Predicate instances have exactly 20 shards, from
`predicate_instances_0000_000000000_000004095.jsonl` through
`predicate_instances_0019_000077824_000080723.jsonl`.  The leaf manifest
enumerates every literal leaf path, role, size, required mode, required nlink,
and SHA-256.  It binds `shard_inventory.json`, whose literal rows enumerate
each shard range and row count.  These two closed records jointly bind all
shard membership; no wildcard or filesystem enumeration is accepted as
membership authority.

The finalized identities are recorded in the package:

| Identity | SHA-256 |
|---|---|
| canonical spec | `d220d33202f8002e6364ce792ffb72559bafa87bda673f750e3caf96351a02db` |
| package compiler | `553b663410ba5a6aaf0f0a48aa7388e2ad70835f56be4efd762e7d5a04056e40` |
| leaf manifest raw bytes | `e111679723272a4c03967e20729e950222197097aa330859fbd449ea36f40ddf` |
| generated leaf inventory authority | `f230c992551da3b13ffacd893639e1cb87073cc57086f5331a3205782c7ee4ef` |
| bundle-root file raw bytes | `91ea795f5644f9b2b03a68c255d97a3be2d92d11319b9f55a2001a59d9a0c980` |
| bundle-root authority | `38b05963da0de1977feff8c7ebf2d7dae05b7022a35a6cd263894ee79a07a6c0` |
| package-checkpoint raw bytes | `94429a5b85b32ceb08e298b992d85d79d5fde938245884f63de56deb7ccd6ab2` |
| portable generated-tree authority | `2937dea5f8b169bcb85ed200c3b911d6eedee9438291d1e5101c4f361369a94d` |
| resource-projection raw bytes | `2a6a1ee033b5ee40981ccea5d569b30cbc74121a3292fe64d26376f5f99aec27` |

This document does not embed its own digest.  Its final SHA-256 is computed
after the document is frozen and is recorded only by the downstream package;
that one-way edge avoids a design self-hash cycle.

All candidate regular artifacts--the package JSON, spec, compiler, design,
generated leaves, and seven non-member companion prompts--are frozen mode
`0444`, nlink `1`.  Generated directories are mode `0555`; all generated
entries are direct, regular/directory, non-symlink, non-hardlinked members.
The package records actual final path, size, mode, nlink, and SHA-256 for spec,
compiler, design, and generated closure points.  The generated
manifest/checkpoint transitively binds every generated leaf.  Prompt hashes
are deliberately outside the package to preserve the one-way prompt-to-
package binding.

## 5. Exact operation expansion

Expansion order is declaration order only:

```text
operation -> call-plan entry -> P00...P17 -> predicate family -> axis row-major
```

No sorting, set conversion, hash-map iteration, runtime discovery, skipped
axis, or unbound placeholder is permitted.

| Operation | Calls | Predicates/events/prefixes | Frames/ACKs | Finals | Opens | Seeds/exits/receipts/P17 |
|---|---:|---:|---:|---:|---:|---:|
| compatibility | 1 | 151 | 82 | 18 | 17 | 1 each |
| source-load micro | 1 | 409 | 263 | 18 | 17 | 1 each |
| full sentinel | 35 | 14,315 | 9,205 | 630 | 595 | 35 each |
| official | 161 | 65,849 | 42,343 | 2,898 | 2,737 | 161 each |
| **global** | **198** | **80,724** | **51,893** | **3,564** | **3,366** | **198 each** |

The compatibility stage predicate vector is:

```text
[5,9,9,5,6,17,10,8,11,11,7,6,4,8,16,7,4,8]
```

The micro/sentinel/official vector is:

```text
[5,9,5,10,120,4,3,16,24,24,67,7,4,24,68,7,4,8]
```

Compatibility has one call and 118 fully literal package fixtures.  It is
science-incapable.  Source-load micro has exactly one call: anchor ordinal 0,
`kM=0.1`, `ell=2`, odd parity, node `P1`, and exits before the
ReggeWheelerRadial public API.  Full sentinel has exactly 35 calls: the ordered
23 anchors at `P1`, then anchor ordinals 3 and 22 at nodes
`P0,I0,I2,O2,O4,O8`.  Official has exactly 161 calls in
`call_ordinal=7*anchor_ordinal+node_ordinal` order with node order
`P0,P1,I0,I2,O2,O4,O8`.

## 6. Schemas, predicates, digest DAG, and FSM

Every generated predicate row has exactly 26 ordered fields and binds its
identity, operation/call/stage position, actor/ownership, value schema,
observer, expected-expression AST, comparison, evidence plan, null policy,
reason codes, path expression, dependencies, and row digest.  Unknown IDs,
unresolved dependencies, wrong value/result types, duplicate IDs, position
collisions, call-plan collisions, or generated-path collisions are fatal.

The schema catalog contains 13 primary schemas and 17 nested schemas.  Every
field freezes JSON/WL wire type, Python type, nullability, finite domain,
constant/derived/source rule, authority owner, and digest dependencies.  The
primary schemas are:

```text
child_observation_frame, parent_event, prefix_checkpoint,
final_stage_checkpoint, ack, stage_open_authority, stage0_seed,
child_exit_authority, lifecycle_receipt, p17_closure, terminal_manifest,
operation_terminal_manifest, root_terminal_checkpoint
```

The 17 nested schemas close file/directory/root/stream/process identity,
call-directory seal, writer-held/release closure, resolved evidence, science
counters, failure closure, dispatch consumption, run contract, source ledger,
failure termination, pre-root failure, and terminal checkpoint.  There are no
open dictionaries.

P00 is parent-only and binds raw request bytes, dispatch identity, dispatch
consumption, root identity, call plan, path grammar, and session seed before a
child can launch.  P17 is parent-only after child exit receipt, bounded wait,
reap, process-group emptiness, stream closure, and source-end closure.  Stage
16 cannot open P17 itself.  The path authority and digest DAG bind every
event/prefix/final/ACK/open edge, stage0 seed, child exit, lifecycle receipt,
P17 closure, call terminal, operation terminal, root checkpoint, and external
writer-release closeout.  The DAG is acyclic and uses explicit predecessor
and ordered-input lists.

The only valid progression is:

```text
stage0 seed
 -> first event/prefix
 -> all ordered stage predicates
 -> final-stage checkpoint
 -> ACKs bind frame + prefix + final
 -> parent barrier/observer closure
 -> next-stage open
 -> ...
 -> P16 child-exit authority
 -> receipt/wait/reap/process-group empty/streams closed
 -> parent-only open P17
 -> P17 events/final
 -> call terminal manifest/checkpoint/seal
 -> next call or operation terminal
 -> root checkpoint while writer lock is held
 -> immutable root close
 -> external writer-release closeout
```

Crash, timeout, malformed bytes, early EOF, child self-confirmation,
observation after ACK, missing/duplicate/out-of-order frame, prefix/final/ACK
replay, predecessor substitution, descendant rehash, cross-call reuse,
cross-operation reuse, process leakage, lock release before close, late writer,
mode/nlink drift, symlink/hardlink/alias, manifest drift, or source drift all
fail closed.  No missing success stage is synthesized.

## 7. Conformance and mutation authority

The generated conformance collection includes codec known-answer vectors,
all schema bootstrap vectors, predicate-row vectors, canonical/noncanonical
wire cases, chain vectors, and the complete compatibility fixture set.  The
Python and Wolfram validators must reach the frozen expected disposition and
reason code without consulting candidate runtime code.

The mutation oracle covers 100% of declared fields and graph edges without
sampling.  Its expansion index freezes the ordered coverage universe, recipe
count, coverage-obligation count, shard ranges, and ordered digest.  It covers
at least missing/extra/type/null/domain/value/hash/order/dependency/ownership,
cross-schema/cross-call/cross-operation substitution, duplicate keys,
noncanonical JSON/JSONL/tag/decimal/integer/hash encodings, DAG/FSM/path edge
mutation, replay, crash boundaries, file identity, permissions, aliasing,
hardlinks, manifest closure, and future-authority collisions.  Rehashing a
mutated descendant cannot make a mutation valid because immutable predecessor
edges and the frozen bundle root remain external to the candidate mutation.

Final generated counts are:

| Collection | Rows/obligations | Shards |
|---|---:|---:|
| predicate instances | 80,724 | 20 |
| conformance vectors | `159` | `1` |
| mutation recipes | `2105410` | `515` |
| mutation coverage obligations | `2105410` | n/a |

## 8. Frozen scientific graph

GMA-Z1 changes only the construction of machine authority.  It does not alter
science, thresholds, domain, source, method, precision, convention, or
certificates.

- Route A remains exactly 496 ordered odd/even modes and 9,920 ladder records
  on the frozen 11-frequency/248-pair domain.  Each mode expands 22 candidates
  but executes 20 unique logical nodes after the exact baseline duplicate is
  removed twice: three `r_in`, 16 outer/Jost, and three tolerance candidates.
  The ordered-mode inventory is
  `e4d09740c032c3c48ae43be56c1dd11512527b6266f5974f444302bb4afc45d8`;
  DOP853 transport, the exact 2x2 solve, and the no-pseudoinverse/no-fallback
  rules are literal machine rows.
- Route U is selected only after a fresh complete Route A, in that exact 496
  order, by direct `log_Gamma_flux < log(1e-8)`.  `0 <= N_U <= 496` and the
  precision record count is runtime-derived `3*N_U`.  Fixed 318/954, old
  route maps, `Gamma_S`, cache, checkpoint, and predecessor evidence are
  forbidden.  Its precision schedule is literal
  `p0=20*ceil(max(80,30-e10)/20)`, then `p0,p0+40,p0+100`, with 30 guard
  digits and parent-owned adjacent bounds `2e-5` for `logGamma` and `5e-8`
  for symmetric-relative `S`; helper-returned admission status is forbidden.
- Route B remains exactly `102/458`: 40 LOW, 38 TURNING, and 24 EVANESCENT
  keys; 306 universal nodes at `80/120/180` dps plus 152 turning extras.
  Its ordered inventory is
  `25c4b2831924bd550a44e59df35b1d2b2687b66e0e1e2b96fb3ef88086667bf3`.
- Route C remains exact 23 odd anchors and `161/322/483`, using BHPT
  ReggeWheeler `NumericalIntegration`, spin 2, independent In/Up solutions,
  exact rational frequencies, nodes `P0,P1,I0,I2,O2,O4,O8`, selected node
  `P1`, P0 precision `90/45/45`, P1/boundary precision `120/60/60`, and zero
  MST calls.  Exact frequency fractions, the outer-radius formula, overlap
  multipliers `0.80/0.88/0.96`, and the restricted helper symbol surface are
  machine-bound.  The ordered anchor inventory is
  `5e93fca57b6d4fb82762043fedea4631de92111164c8c4a991d76925e3867c76`.
- Full sentinel remains `35/70/105` and all sentinel values are
  nonpromotable to official science.
- Direct `Gamma_flux=F_H/F_in` and independent `Gamma_S=1-|S|^2` remain
  separate routes.
- All 16 thresholds and the five certificate IDs remain exact.

The 16 threshold IDs and values are exactly those in the frozen V3.0 threshold
authority: `2e-6`, `2e-4`, `1e-8`, `2e-8`, `2e-4`, `2e-10`, `2e-8`,
`2e-6`, `5e-7`, `1e-4`, `1e-6`, `2e-4`, `2e-6`, `3e-4`, `1e-6`,
and `2e-4` in declaration order.  The certificate IDs are
`V3_MODE_GREYBODY_NUMERICAL`, `V3_MODE_GREYBODY_FLUX_VS_S`,
`V3_MODE_GREYBODY_EXTERNAL`, `V3_MODE_PARITY_PROBABILITY`, and
`V3_MODE_DOMAIN_COVERAGE`.

## 9. Package-generation protocol and measured closure

The finalized spec and compiler were validated and then invoked under the
frozen CPython runtime against two distinct fresh absent temporary output
roots.  A third publication generation used the same frozen bytes and a fresh
absent temporary publication root.  Only after all three portable trees were
byte-identical were those bytes mechanically published to the authorized
`generated/phase6_v3_1_z` path; the final read-only tree was then compared
again with the publication root.  No temporary tree is an authority source
and no absolute temporary path enters portable bytes.

| Run | Wall (s) | Peak RSS (bytes) | Files | Directories | Bytes | Result |
|---|---:|---:|---:|---:|---:|---|
| independent A | `65.11382895801216` | `279363584` | `551` | `4` | `1006400405` | PASS |
| independent B | `65.13320479192771` | `279330816` | `551` | `4` | `1006400405` | PASS |
| publication | `63.802429917035624` | `279543808` | `551` | `4` | `1006400405` | PASS |

Each run satisfies wall `<=600 s`, peak RSS `<4 GiB`, and generated bytes
`<2 GiB`.  All three source-ledger start/end digests equal
`16fe0ec58576025e9f74b833fee07a297cad327e3c594876e2d815d8d06f7e1b`; every run reports start=end.  Independent A/B and
the publication tree have byte-identical portable inventories with
`555` entries and portable comparison digest
`4436fabdb19449f4ec31953d4f08f4e23390ef2a2521303eeb4cdd67c8569456`.

The source ledger freezes, for every regular input, the requested path,
resolved path, SHA-256, size, mode, nlink, device, and inode, observed under a
no-follow open with before/opened/after stat equality.  It separately freezes
CPython and Wolfram runtime identities, the BHPT metadata and 25-file/5-dir
closure, the full mpmath overlay and helper/import closure, content/identity
inventory digests, and all present threat-only records.  The package records
the canonical ledger digest rather than embedding a device-dependent ledger
into portable generated bytes.

The following checks all pass before publication:

- duplicate-key/canonical spec validation, exact 39-key schema, all registry
  reference/type/ownership/dependency checks, exact operation counts, digest
  acyclicity, and collision absence;
- read-only full-tree checks for every generated byte, shard name/range/count,
  schema, digest, manifest, mode, nlink, and portable checkpoint;
- two independent fresh-tree comparisons and publication-tree comparison;
- exhaustive mutation expansion index coverage with no sampling;
- generated Python validator compile and conformance/mutation checks;
- package-frozen Wolfram validator and compatibility observer static
  zero-science/call-graph checks; Wolfram is not launched at package time;
- Ruff check and format check on the compiler and CPython compile validation;
- exact authorized-path audit, future authority/implementation/root absence,
  and no related writer/runtime/science process;
- final mode/nlink/hash/source identity audit after sealing.

Any mismatch, nondeterminism, cap violation, unresolved ID, implicit behavior,
hidden semantic callback, incomplete mutation coverage, source drift, or
future-path collision is a STOP.  It cannot be repaired by sampling, changing
shards, relaxing a cap, editing science, or publishing a misleading package.

## 10. Future implementation scope

A formal package-review ADVANCE may authorize T6 to edit exactly these six
initially absent paths:

```text
scripts/phase6_v3_1_z_raw_observer.wls
src/schwgw/validation/phase6_v3_1_z_authority_runtime.py
src/schwgw/validation/phase6_v3_1_z_external_route.py
scripts/phase6_v3_1_z_external_protocol.py
tests/unit/test_phase6_v3_1_z_authority_runtime.py
tests/regression/test_phase6_v3_1_z_authority_publication.py
```

Generated authorities and scientific/protected sources remain read-only.  T6
is zero-science: it may implement and test the consumer but may not launch
Wolfram or any solver and may not create an executable root.  A seventh path,
generated-byte edit, core-physics edit, fallback, or scientific-contract drift
requires a distinct Root-T0 package adjudication.

## 11. Literal future authority graph and zero-repair rule

The future review archives are exactly:

```text
docs/handoffs/archive/T7_2026-08-14_v3_1_z_generated_machine_authority_package_review.md
docs/handoffs/archive/T7_2026-08-14_v3_1_z_generated_machine_authority_implementation_review.md
docs/handoffs/archive/T7_2026-08-14_v3_1_z_wolfram_compatibility_review.md
docs/handoffs/archive/T7_2026-08-14_v3_1_z_source_load_micro_review.md
docs/handoffs/archive/T7_2026-08-14_v3_1_z_full_sentinel_review.md
docs/handoffs/archive/T7_2026-08-14_v3_1_z_scientific_review.md
```

The one-use dispatch paths are exactly:

```text
docs/handoffs/archive/T0_2026-08-14_v3_1_z_implementation_dispatch_attempt_0001.json
docs/handoffs/archive/T0_2026-08-14_v3_1_z_wolfram_compatibility_dispatch_attempt_0001.json
docs/handoffs/archive/T0_2026-08-14_v3_1_z_source_load_micro_dispatch_attempt_0001.json
docs/handoffs/archive/T0_2026-08-14_v3_1_z_full_sentinel_dispatch_attempt_0001.json
docs/handoffs/archive/T0_2026-08-14_v3_1_z_official_dispatch_attempt_0001.json
```

The executable root parent is exactly
`/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/runs/phase6/classic_scattering`.
The four basename grammars are the frozen
`v3_1_z_{wolfram_compatibility,source_load_micro,full_sentinel,official}_v1_<UTC>_py314`
regular expressions in the generated path authority.  Every root is a fresh,
non-symlink, no-alias direct child created only after one-use O_EXCL dispatch
consumption.  Any failed or interrupted dispatch/root is immutable and
permanently non-reusable.

The only graph is:

```text
package -> formal package review -> implementation dispatch -> T6
 -> formal implementation review -> compatibility dispatch/root/review
 -> source-load-micro dispatch/root/review
 -> full-sentinel dispatch/root/review
 -> fresh official dispatch/root -> scientific review
```

The first five formal reviews may advance only with the exact three-line
envelope declared by their prompts: `ADVANCE_DECISION: ADVANCE`,
`CLAIM_STATUS: NOT_ASSESSED`, and their literal gate label.  The scientific
review verdict and claim status are evidence-derived and are never prefilled.

V3.1-Z v1 has zero bounded repair cycles, zero retry roots, zero resume, zero
alternate attempts, and zero delta-review paths at every node.  Any
non-ADVANCE, `REPAIR`, `FAIL`, `ESCALATE`, malformed/missing archive, or
interruption returns to Root T0 for distinct-gate adjudication.  It does not
authorize an in-family repair.

## 12. Resource policy for future execution

Package generation is limited to 600 seconds, peak RSS below 4 GiB, generated
bytes below 2 GiB, and concurrency one.  Compatibility and source-load micro
whole roots are each limited to 16 MiB and 120 seconds.  Full sentinel is
limited to 8 hours and 8 GiB; official is limited to the unchanged 36 hours
and 8 GiB.  Every executable operation additionally requires:

```text
projected_root_bytes <= floor(free_workspace_bytes/4)
free_workspace_bytes >= 4*projected_root_bytes
```

The byte projection is generated from exact frame/ACK/raw-stream/schema counts
without empirical margin or compression assumption.  Sentinel resource
evidence may authorize official admission only after formal sentinel review;
sentinel scientific values remain nonpromotable.

The generated projection is exact and package-bound:

| Operation | Projected root bytes | Whole-root gate |
|---|---:|---:|
| compatibility | 4,313,088 | <=16,777,216 |
| source-load micro | 8,595,456 | <=16,777,216 |
| full sentinel | 295,270,400 | free-space quarter rule |
| official | 1,357,654,016 | free-space quarter rule |

The formula includes 4,096-byte frame maxima, 2,048-byte ACK maxima, exact
per-schema record maxima, 1 MiB stdout and 256 KiB stderr per call, and fixed
per-call/per-operation authority allowances.  Neither compression nor an
empirical safety margin may be used to make a failing projection pass.

## 13. Formal package review obligation

Formal T7 must be source-distinct.  It must not import the candidate compiler,
generated validators, or their expected answers.  From the canonical spec it
must independently rebuild a temporary bundle, verify every reference,
schema, row, digest input/order/domain separator, operation count, path, shard,
manifest, authority edge, conformance disposition, and exhaustive mutation
obligation, then byte-compare its results with the candidate bundle.  It must
also verify package/prompt/source hashes, final modes/nlinks, authorized-path
closure, future-path absence, and the zero-science boundary.

An advance is exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-Z GENERATED MACHINE-AUTHORITY PACKAGE READY FOR T6
```

Any other complete result must follow
`docs/review_gate_liveness_protocol.md`; it cannot silently omit a verdict,
invent a repair cycle, or authorize T6.

## 14. Nonclaims and checkpoint

This package does not claim:

- T6 implementation, runtime protocol correctness, compatibility, source
  loading, sentinel success, official execution, or scientific acceptance;
- an independent external even-sector solve;
- common absolute scattering-phase validation beyond `PARTIAL`;
- Li-figure equivalence, finite-radius observer validity, full-domain V3,
  V3.2, or global GREEN;
- promotion of any U/X/Y runtime/science/control byte;
- a fixed Route-U count; or
- reuse of sentinel values in official science.

`V3.1-Z science NOT_ASSESSED; no T6 implementation/runtime/V3.2/global GREEN.`

CHECKPOINT / V3.1-Z GENERATED MACHINE-AUTHORITY PACKAGE CANDIDATE READY FOR ROOT T0 AND FORMAL T7
