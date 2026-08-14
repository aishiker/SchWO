# Phase 6 V3.1-Z generated machine-authority redesign analysis

Date: 2026-08-14 (Asia/Shanghai)  
Gate: `phase6_v3_1_z_generated_machine_authority_redesign_v1`  
Task: formal T4 `019f5fa6-1288-7c01-8a87-4c4370cf5517`  
Mode: read-only analysis / zero science / design only

## 1. Decision

Recommend **GMA-Z1: a generated authority bundle with a reduced-observation
child boundary**.

One duplicate-key-rejecting declarative typed specification is compiled,
before any runtime implementation exists, into:

1. every expanded predicate instance and its complete semantics;
2. every wire and durable artifact schema;
3. the domain-separated digest DAG and the four operation DAGs;
4. canonical positive conformance vectors;
5. a complete, mechanically expandable one-field/one-edge mutation oracle;
6. Python and Wolfram Language codec/schema adapters; and
7. a non-self-referential inventory and bundle root.

The future runtime may consume these frozen bytes but may not generate its own
expected values, comparison rules, evidence plans, path grammar, digest
inputs, or transition graph.  The Wolfram child emits observations only.  A
parent-owned engine constructs semantic events and decisions from the frozen
bundle.  Formal T7 must independently recompile the declarative source without
importing either the candidate generator or the generated validators.

This is a distinct authority-construction algorithm.  V3.1-Y relied on
hand-written prose/templates plus runtime interpretation; GMA-Z1 makes the
closed predicate semantics and acceptance bytes package-time generated
artifacts.  No Y package, namespace, dispatch, root, transcript, value, cache,
checkpoint, route map, timing, or partial success is renamed or promoted.

This document is a design recommendation, not a package, implementation,
scientific result, or review verdict.

## 2. Start gate and immutable boundary

### 2.1 Formal authorities

The following identities were freshly recomputed before this document was
created.

| Role | Path | SHA-256 |
|---|---|---|
| exact T4 prompt | `docs/prompts/phase6_t4_v3_1_z_generated_machine_authority_redesign_analysis.md` | `6a7a6ecfe6d06be1630a9b9df3c266138c30b5e3bd4de4a2783c748da6b07d14` |
| Root-T0 final Y adjudication | `docs/handoffs/archive/T0_2026-08-13_v3_1_y_final_escalation_adjudication.md` | `6b5d126565ab4f8764d65825c37589e37f52f2576d25593239c028ee1608c3f4` |
| formal T7 Y delta review 2 | `docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_delta_review_2.md` | `0ad54e21f62d233e6c26720918c85ac6dfdb12f254f02d6169ed4af348df9dd4` |
| review-gate liveness protocol | `docs/review_gate_liveness_protocol.md` | `3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181` |
| terminal Y package | `configs/phase6_v3_1_y_external_protocol_package.json` | `5dc0b062c7da463bb3aa4283b38060201c8d6fd7a6902dd0d677273306b9d0b7` |
| terminal Y contract | `configs/phase6_v3_1_y_external_protocol_contract.json` | `c3d601940b8f297eb23cccad404c8ec5c326ffc6fb9a1dfa005ec6f5db3ef45c` |
| terminal Y design | `docs/phase6_v3_1_y_external_protocol_design.md` | `78fc6d2d62549ebb907c80685f41222d0e5be5f85329e071cd0510c5da20bb44` |
| terminal Y analysis | `docs/phase6_v3_1_y_external_protocol_redesign_analysis.md` | `4e4f6eff3b22c170bf9502d86c3d5af70d5221a5aa746ac266f77e5065c60cd0` |
| prior T4 Y archive | `docs/handoffs/archive/T4_2026-08-13_v3_1_y_external_protocol_redesign_analysis.md` | `e162a1fc5e396c11234fef09bdeb04f8c1e7496da588da105971a4c8868dbefb` |
| initial Y review | `docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_review.md` | `1cc0da4cdfd7c9aecf7306ba7dd7b10219ce14f93e3a1c8bca37afe12417ac6b` |
| Y delta review 1 | `docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_delta_review_1.md` | `63c1ae9286fa5cb7b07ee4c2995a7cf6bb71f9e1bc941399d46861f65f1aa499` |

All five terminal Y future-review prompts and its T6 prompt were also rehashed:

| Path | SHA-256 |
|---|---|
| `docs/prompts/phase6_t6_v3_1_y_external_protocol_implementation.md` | `32ec19023973a4f49801efaa9dade8fd47d97e5919befd5f7634191f50a576a5` |
| `docs/prompts/phase6_t7_v3_1_y_external_protocol_package_review.md` | `2c4487fb3fab836f297a8b0bb405f0b51acdeb68593f901541a475cb48c8cb01` |
| `docs/prompts/phase6_t7_v3_1_y_external_protocol_implementation_review.md` | `9bd7f90e1615e82db053461a60de23389d18fbe61171f6ee7253741dc87665f0` |
| `docs/prompts/phase6_t7_v3_1_y_wolfram_protocol_compatibility_review.md` | `1571a13fe7e88bd03012a375dcd8abfc7c913db85c00db36f053a33f0cf0cafb` |
| `docs/prompts/phase6_t7_v3_1_y_source_load_micro_review.md` | `157b0e943d170c60779d4eef1a28c3086f8c89b2a88795849c32f95b4d8051d0` |
| `docs/prompts/phase6_t7_v3_1_y_full_sentinel_review.md` | `9a40e2334989235bfc50690046b870318678ea7e7b64e31f155582a82d0f80c4` |
| `docs/prompts/phase6_t7_v3_1_y_science_review.md` | `c5d30024c7418888d267b9de044ae3336acbf709894d89dbf89b44d5b23e112b` |

The required current-state inputs were read at the start gate and were not
edited by this task:

| Path | Start SHA-256 |
|---|---|
| `project.md` | `fdba5646eb0d9bb0776ea6148e509d91124871cf371ac08a7229b10e18b63b9a` |
| `status.md` | `3a63b18f1a56a7a7cb41351f34ccdb04870358b1881634e00f24a7b1178d4ad1` |
| `docs/handoffs/T0_current.md` | `297adae85c4d1973ddaa1d267d3a486f9d975506d738b190ce58a3cd7551d1d0` |
| `docs/handoffs/T4_current.md` | `012da075c1cbd9b35d6d7776a330c67f804e40ae67cefa7a4557d2085a1f029e` |
| `docs/handoffs/T7_current.md` | `8bbf1d045f3aba93d9b8b89a8c459c25567e04112fbea6c7566dbe0eb9b586bb` |

Their headers consistently identify Y as frozen and Z as design-only.  They
are coordination snapshots, not substitutes for the immutable adjudication
and review archives above.

Formal T7's terminal result is exactly `ESCALATE / NOT_ASSESSED`.  Y repairs
1 and 2 are consumed, and Y repair 3, implementation, compatibility, micro,
sentinel, official execution, and V3.2 are forbidden.

### 2.2 V3.0 scientific authorities

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

The V3.0 T7 result was contract readiness, not V3.1 science or global GREEN.

### 2.3 Runtime, external source, and protected sources

The exact external runtime remains
`/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel`,
SHA-256
`70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c`,
mode `0755`, nlink `1`, size `167488`.  It was statted and hashed but not
executed.

The BHPT snapshot metadata is
`runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json`,
SHA-256
`8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488`.
It binds 25 regular `0444` nlink-1 files, five `0555` directories, content
inventory
`d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2`,
and restored identity inventory
`a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27`.
The snapshot has no `.git`; commit association is inherited historical
metadata, not independently proved by the restored tree.

Seven protected radial sources were unchanged at the start gate:

| Path | SHA-256 |
|---|---|
| `src/schwgw/numerics/radial_solver.py` | `9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9` |
| `src/schwgw/numerics/conditioned_radial.py` | `91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2` |
| `src/schwgw/numerics/scaled_tortoise_radial.py` | `d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df` |
| `src/schwgw/numerics/adaptive_jost_radial.py` | `3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896` |
| `src/schwgw/numerics/matching.py` | `9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340` |
| `src/schwgw/numerics/physical_boundary_radial.py` | `fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f` |
| `src/schwgw/numerics/boundary_conditions.py` | `b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22` |

No related Wolfram, BHPT, arbitrary-precision radial, Route A/U/B/C, or
solver process was active.  Both authorized output paths were absent before
publication.

### 2.4 Historical adversarial evidence only

The following records are inputs to the threat model, never promotable
science or control authority:

- failed V3.1-U official failure / manifest / observed route-map:
  `e3874e7565dc35498513af8112577810dd9059035f43a9d4573d633c2ae752aa`,
  `f977a0d555652d028b3b73d18990b902f37a55c3dd9305c6e6da55f66593050d`,
  `5eee07ece78204265fe45069ef57a653a61a8ee9d09ff4b4d7e8928bb385c822`;
- V3.1-U repair-2 sentinel failure / manifest:
  `c80327f57b56f762fde9df3b215cf94c895e98de8c0d1e48157a31b44a65dc23`,
  `e9ef19b336e1eb9faac34b2f080f2c4956fd2316eb050287e769cbdb401aead4`;
- V3.1-X attempt-0001 / attempt-0002 manifests:
  `d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772`,
  `6e0d2349d998f76ee8d149e4551bf27222c5d93bf4ec9fb7b790adbc9f506109`;
- V3.1-X review temporary tree:
  `64602b35aec85f8facac412b90eb8e8a329fe5300e493d76fc1afd1d1f31a534`;
- terminal U and X reviews:
  `e51f32f1f7d633ff78a653d9ab2a0a49d5c1ef0d32c57f84cb9fda63abc80b55`,
  `e5f9b9503e16b053525dfba7dacb661abc433211d49dcccb2c5c9dc442af1dee`;
- Root-T0 X adjudication:
  `7fd2012a57e86a8b085114c3b68243db616e8437983bf150ee85b2474775cee5`.

The failed route map observed `N_U=318`; that number and `954` nodes are not
acceptance inputs.  Z must regenerate Route A and derive `N_U` afresh.

## 3. Frozen scientific contract

GMA-Z1 changes authority construction only.  The following are immutable:

- Route A: exactly 496 independently solved odd/even modes and 9,920 ladder
  records over the frozen 11-frequency, 248-pair domain;
- Route U: after fresh complete Route A, in the same exact 496 order, select
  exactly those entries satisfying the direct-horizon predicate
  `log_Gamma_flux < log(1e-8)`; `0 <= N_U <= 496`, with exactly `3*N_U`
  precision records; selection may not read `Gamma_S`, predecessor evidence,
  a cache, a fixed count, or an old route map;
- Route B: exactly `102/458`;
- Route C: exact 23 odd anchors and `161/322/483`; BHPT ReggeWheeler
  `NumericalIntegration`, spin 2, independent In/Up solutions, nodes
  `P0,P1,I0,I2,O2,O4,O8`, P0 precision `90/45/45`, P1 and boundary precision
  `120/60/60`, selected node P1, exact rational frequency, MST calls zero,
  no internal fallback;
- full sentinel: exactly `35/70/105`, with no value reuse in official science;
- direct `Gamma_flux=F_H/F_in` and independent
  `Gamma_S=1-|S|^2` remain separate routes;
- source, method, precision, convention, parity, Fourier sign, and phase
  taxonomy remain unchanged.

The exact operation call plans are also immutable.  Source-load micro call 0
is the first external anchor `(kM=0.1, ell=2, odd)` at node `P1` and exits
before its public API.  Full-sentinel calls 0--22 are the 23 ordered anchors at
`P1`; calls 23--28 are anchor ordinal 3 at nodes
`P0,I0,I2,O2,O4,O8`; calls 29--34 are anchor ordinal 22 at the same node
order.  Official call ordinal is exactly
`7*anchor_ordinal + node_ordinal` with node order
`P0,P1,I0,I2,O2,O4,O8`.  Every session ID, predicate row, path, seed, frame,
event, and terminal artifact binds the call-plan-entry digest, preventing
cross-call replay.

The 16 frozen blocking thresholds are:

| ID | Limit |
|---|---:|
| `V3T-S-COMPLEX-001` | `2e-6` |
| `V3T-LOGGAMMA-001` | `2e-4` |
| `V3T-FLUX-BALANCE-001` | `1e-8` |
| `V3T-GAMMA-ROUTES-001` | `2e-8` |
| `V3T-GAMMA-ROUTES-LOG-001` | `2e-4` |
| `V3T-GAMMA-PHYSICAL-001` | `2e-10` |
| `V3T-PARITY-PROB-001` | `2e-8` |
| `V3T-PARITY-PHASE-001` | `2e-6` |
| `V3T-PRECISION-S-001` | `5e-7` |
| `V3T-PRECISION-LOGGAMMA-001` | `1e-4` |
| `V3T-RIN-S-001` | `1e-6` |
| `V3T-RIN-LOGGAMMA-001` | `2e-4` |
| `V3T-ROUT-JOST-S-001` | `2e-6` |
| `V3T-ROUT-JOST-LOGGAMMA-001` | `3e-4` |
| `V3T-TOLERANCE-S-001` | `1e-6` |
| `V3T-TOLERANCE-LOGGAMMA-001` | `2e-4` |

The exact five certificate IDs remain:

1. `V3_MODE_GREYBODY_NUMERICAL`;
2. `V3_MODE_GREYBODY_FLUX_VS_S`;
3. `V3_MODE_GREYBODY_EXTERNAL`;
4. `V3_MODE_PARITY_PROBABILITY`;
5. `V3_MODE_DOMAIN_COVERAGE`.

Missing blocking evidence is never PASS.  Numerical and convention budgets
remain separate.  External Route C is independent odd-only evidence; no
independent external even-sector result exists.  Common absolute phase remains
`PARTIAL`.  No Li-figure, finite-radius observer, full-domain V3, V3.2, or
global GREEN claim follows.

## 4. Exact failure being redesigned

The terminal Y contract has eight schema tables containing 192 fields
(`27/29/18/24/21/29/25/19`).  One hundred one field rules say only “derived
from exact profile and preceding immutable authority.”  Its 24 production
predicate templates all contain only:

```text
template_id, id_format, applicable_operations, stage_id,
observer_id, axis_order, axis_values
```

They do not freeze `field_id`, ownership, value type, comparison, expected
value, or ordered evidence inputs.  In addition:

- P00 lacks a unique seed-to-event authority mapping;
- the lifecycle receipt is only a tuple type, not a canonical artifact;
- the eight P17 predicates lack exact evidence plans; and
- the terminal manifest has no complete schema or digest formula.

Therefore different implementations can produce incompatible acceptance bytes
while each claims conformance.  Adding more prose, tests, or another Y repair
would not change the authority algorithm; it would preserve the same
self-certification surface.  Z instead makes the complete semantic closure a
generated package artifact that exists before runtime implementation.

## 5. Materially different architecture comparison

| Architecture | Independence and trust boundary | Target-language mismatch | Proof/implementation burden | Runtime overhead | Crash recovery | Hostile mutation coverage | Distinct from Y? |
|---|---|---|---|---|---|---|---|
| **A. Generated Authority Bundle (GMA-Z1)** | Declarative spec and package compiler are frozen before T6. T7 uses a source-distinct recompiler. Runtime consumes generated bytes; WL child only observes. Trusted base is spec, generator identity, canonical codecs, SHA-256, and parent POSIX primitives. | Low: authority records are schema-ordered arrays and tagged scalars; no Association/dict insertion order. Real Python/WL parity is gated before science. | High once, then mechanical. Semantics are authored once and expanded deterministically. | Moderate-to-high control I/O: one immutable event/prefix per predicate plus stage and terminal artifacts; streaming shards bound memory. Exact cost must be generated before package freeze. | Generated DAG defines every crash edge, receipt, failure closure, and interruption stop; no implicit retry. | Exhaustive generated field/edge recipes; descendant-rehash attacks are checked against immutable bundle roots and predecessor edges. | **Yes.** Authority is generated, closed, and independently rebuilt rather than interpreted from prose. |
| **B. Formal protocol state machine plus generated adapters** | A TLA+/PlusCal/Apalache-style transition model can strongly separate control flow from runtime. | Medium-high: a refinement is still needed from model values to concrete JSON/WL/POSIX bytes. | Highest: model, refinement, code generation, data schema, and toolchain identities all need review. | High offline model/refinement cost; moderate runtime if adapters are generated, plus a frozen formal-toolchain dependency. | Best deadlock/replay reasoning, but concrete file/value crash semantics remain a second authority unless integrated with a typed data spec. | Excellent transition coverage; incomplete for predicate values/evidence by itself. | Yes, but it does not directly close the recurring value/evidence blocker. Suitable as secondary verification of A's generated FSM. |
| **C. Reduced-boundary child plus hand-written parent authority engine** | Child trust is small, but parent implementation becomes both producer and acceptance oracle. | Low at child boundary. | Moderate initially, high maintenance across schemas and predicates. | Lowest child wire volume, but the parent still writes the full evidence chain and bears bespoke validation cost. | Can be engineered safely, but crash rules and comparisons remain implementation-defined. | Tests exercise the implementation's own choices; common-mode self-certification remains. | Only partially. Without A, it repeats the substantive Y blocker. Use the reduced child boundary as a property of A, not as sole authority. |
| **D. N-version hand-written Python/WL validators** | Two implementations appear independent, but both can resolve the same ambiguous prose identically or incompatibly. | High; WL/Python numeric, Unicode, path, and equality semantics diverge. | Approximately double implementation and diagnostic cost. | Roughly doubles validator CPU/memory and adds consensus traffic and diagnostic storage. | Consensus adds recovery states and does not define which byte stream is authoritative. | Good drift detector, poor source of unique expected semantics. | Yes operationally, but scientifically inferior to A and not recommended. |

Recommendation: architecture A, with C's observation-only child boundary and
an optional non-authoritative finite-state model from B.  D is rejected.

## 6. GMA-Z1 declarative source

### 6.1 Proposed package-time authority paths

These paths are recommendations for a future Root-T0 package freeze; they are
not created or authorized by this analysis:

```text
configs/phase6_v3_1_z_generated_machine_authority_package.json
configs/phase6_v3_1_z_machine_authority_spec.json
docs/phase6_v3_1_z_generated_machine_authority_design.md
scripts/phase6_v3_1_z_generate_machine_authority.py
generated/phase6_v3_1_z/leaf_manifest.json
generated/phase6_v3_1_z/bundle_root.json
generated/phase6_v3_1_z/package_checkpoint.json
generated/phase6_v3_1_z/schema_catalog.json
generated/phase6_v3_1_z/digest_dag.json
generated/phase6_v3_1_z/operation_dags.json
generated/phase6_v3_1_z/path_grammar.json
generated/phase6_v3_1_z/validator_python.py
generated/phase6_v3_1_z/validator_wolfram.wl
generated/phase6_v3_1_z/compatibility_observer.wls
```

Generated validators are frozen package outputs, not future T6-editable
implementation paths.

The `generated_output_plan` fixes `max_rows_per_jsonl_shard=4096` and this
filename function for every row collection:

```text
<collection>/<collection>_<shard_index:04d>_<first_global_ordinal:09d>_<last_global_ordinal:09d>.jsonl
```

Rows use compact canonical arrays, one per LF-terminated line.  Shard index
starts at zero; global ordinals are contiguous; every nonfinal shard contains
exactly 4096 rows; the final shard contains the remainder.  Empty required
collections are an error, not an empty shard.  Therefore 80,724 predicates
produce exactly 20 predicate shards, from
`predicate_instances_0000_000000000_000004095.jsonl` through
`predicate_instances_0019_000077824_000080723.jsonl`.

Conformance-vector and mutation-oracle row counts are outputs of the frozen
spec expansion.  The same formula determines their exact shard count and
names.  Before package freeze, `leaf_manifest.json` must enumerate every
literal generated path, range, row count, byte size, mode, nlink, and SHA-256;
no wildcard is accepted by a package, runtime, or review.  The digest DAG is
the single canonical `digest_dag.json` containing an exact ordered node array;
it is not sharded, and exceeding the package byte/RSS cap is a STOP rather
than authority to change this representation.

### 6.2 Exact top-level spec schema

The spec must be duplicate-key-rejecting canonical JSON with exactly these
top-level keys, in semantic rather than insertion-order authority:

```text
schema
gate_id
spec_revision
canonical_codec
type_registry
json_shape_registry
value_schema_registry
algorithm_registry
policy_registry
null_rule_registry
null_matrix_registry
fixture_constructor_registry
selector_registry
catalog_registry
reason_code_registry
observer_registry
executor_registry
comparison_registry
expected_expression_registry
evidence_input_registry
identity_policy_registry
path_expression_registry
immutable_inputs
stages
operations
call_plans
predicate_families
artifact_schemas
digest_nodes
state_machine
path_grammar
authority_progression
conformance_vector_registry
conformance_vector_plans
mutation_operator_registry
mutation_plans
generated_output_plan
resource_limits
nonclaims
```

Unknown, missing, duplicate, or differently typed keys fail generation.
Identifiers use frozen printable ASCII grammars.  All arrays are ordered.
Objects are maps only where lookup by unique key is explicitly declared; no
object insertion order is authoritative.

### 6.3 Complete expanded predicate row

Every generated predicate instance is one ordered array with this exact field
order:

```text
[
  predicate_id,
  predicate_row_revision,
  operation,
  call_ordinal,
  call_key_digest,
  axis_bindings,
  record_ordinal_or_null,
  stage_ordinal,
  stage_id,
  stage_instance_ordinal,
  operation_instance_ordinal,
  global_instance_ordinal,
  owner,
  observer_id,
  executor_id,
  field_id,
  value_type_id,
  nullable,
  null_rule_id,
  comparison_id,
  expected_value_schema_id,
  expected_kind,
  expected_literal_or_null,
  expected_expression_or_null,
  ordered_evidence_plan,
  science_capable
]
```

Rules:

- `predicate_id` is globally unique and canonical ASCII.
- `predicate_row_revision` is the literal spec revision.
- `axis_bindings` is the exact ordered array
  `[[axis_id,typed_value], ...]` in family-declaration order; it is never
  reconstructed from the rendered predicate ID.  `record_ordinal_or_null` is
  a redundant generated projection checked against `axis_bindings`, null only
  for families with no record axis.
- ordinals are JSON integers, non-negative, and reject booleans.
- `owner` is exactly `PARENT_OBSERVED` or `CHILD_OBSERVED_PARENT_VERIFIED`.
- observer, executor, type, null rule, comparison, expected schema, identity
  policy, and digest node IDs must resolve to exactly one registry row.
- `expected_kind` is `LITERAL` or `DERIVED`.  Exactly one of the two following
  fields is non-null.
- a derived expression is a typed acyclic AST using only the single closed
  constructor registry in Section 6.4.  Arbitrary Python/WL code, clocks,
  environment lookup, globbing, unordered sets, filesystem discovery, and
  callbacks are forbidden.
- every evidence item is an ordered array
  `[evidence_plan_id,role,kind,path_expression_id,identity_policy_id,required_digest_node_id]`
  and must be byte-for-byte equal to the uniquely named row in
  `evidence_input_registry`.
  Runtime sorting, filtering, deduplication, optional omission, or implicit
  evidence is forbidden.
- `science_capable` is a literal boolean.  Compatibility and pre-solver micro
  predicates are all false.

The compiler type-checks every expression, proves the expected-expression DAG
acyclic, and rejects forward/unknown references.  Each expanded row has a
domain-separated digest and is included in the generated bundle inventory.

### 6.4 Closed registry row schemas and evaluator vocabulary

The single source must not contain registry names whose behavior is supplied
later by T6.  Each registry uses the following exact ordered row schema.

```text
type_registry row =
  [type_id, wire_tag, json_shape_id, python_type_predicate_id,
   wolfram_head_predicate_id, canonicalizer_id, domain_expression_id,
   nullable, ordered_mutation_operator_ids]

json_shape_registry row =
  [json_shape_id, shape_kind, exact_length_or_null,
   ordered_member_schema_ids_or_null, additional_members_allowed,
   duplicate_members_allowed, number_token_policy_id_or_null]

value_schema_registry row =
  [value_schema_id, type_id, nullable, null_rule_id,
   element_schema_id_or_null, exact_length_or_null,
   minimum_or_null, maximum_or_null, enum_values_or_null,
   field_schema_ids_or_null]

algorithm_registry row =
  [algorithm_id, algorithm_kind, ordered_input_value_schema_ids,
   output_value_schema_id, closed_typed_ast_or_literal_table,
   null_rule_id, ordered_success_reason_codes,
   ordered_failure_reason_codes, science_capable]

policy_registry row =
  [policy_id, policy_kind, ordered_input_schema_ids,
   literal_payload_schema_id, literal_payload,
   decision_expression_id_or_null, output_schema_id,
   ordered_failure_reason_codes]

null_rule_registry row =
  [null_rule_id, null_matrix_id, row_ordinal,
   ordered_operand_null_bitmap,
   resulting_outcome, resulting_value_or_null, reason_code]

null_matrix_registry row =
  [null_matrix_id, comparison_id, operand_count,
   ordered_null_rule_ids, required_bitmap_count,
   bitmap_order="LEXICOGRAPHIC_FALSE_BEFORE_TRUE"]

fixture_constructor_registry row =
  [constructor_id, constructor_kind, ordered_input_schema_ids,
   output_schema_id, algorithm_id, literal_parameters,
   expected_output_authority_sha256]

selector_registry row =
  [selector_id, input_catalog_id, output_row_kind,
   closed_typed_selector_ast, ordered_result_policy_id,
   expected_cardinality_expression_id]

catalog_registry row =
  [catalog_id, row_value_schema_id, ordered_row_source_id,
   expected_row_count_expression_id, ordered_row_digest_node_id]

reason_code_registry row =
  [reason_code, reason_class, terminality,
   earliest_rejection_state, science_claim_permitted]

observer_registry row =
  [observer_id, actor, source_kind, observation_algorithm_id,
   output_value_schema_id, ordered_default_evidence_plan_ids,
   science_capable]

executor_registry row =
  [executor_id, runtime_identity_id, entrypoint_id, argv_template_id,
   cwd_policy_id, environment_policy_id, callgraph_allowlist_id,
   stdout_protocol_id, science_capable]

comparison_registry row =
  [comparison_id, left_value_schema_id, right_value_schema_id,
   operator_id, null_matrix_id, tolerance_authority_id_or_null,
   result_schema_id, pass_result_literal, pass_reason_code,
   fail_reason_code, indeterminate_reason_code]

evidence_input_registry row =
  [evidence_plan_id, role, kind, path_expression_id,
   identity_policy_id, required_digest_node_id]

identity_policy_registry row =
  [identity_policy_id, allowed_kind, require_nofollow,
   required_mode_or_null, required_nlink_or_null,
   require_device_inode, require_size, require_content_sha256,
   alias_policy_id, start_end_policy_id]

path_expression_registry row =
  [path_expression_id, base_authority_id, ordered_literal_and_typed_segments,
   normalization_policy_id, direct_child_required, namespace_regex_id]

expected_expression_registry row =
  [expression_id, result_value_schema_id, typed_ast,
   ordered_dependency_ids]
```

Every referenced registry ID must occur exactly once.  All enum domains and
all null matrices are literal arrays in the spec.  The package compiler emits
the fully joined semantic row for human review; runtime lookup through a
second unconstrained registry is forbidden.

There are no opaque behavior names.  Every behavior-bearing field above is
resolved as follows, and generation fails if an ID is absent, duplicated, or
appears in the wrong registry category:

- `python_type_predicate_id`, `wolfram_head_predicate_id`,
  `canonicalizer_id`, `observation_algorithm_id`,
  and comparison `operator_id` resolve to `algorithm_registry`;
- `json_shape_id` resolves to exactly one `json_shape_registry` row, whose
  `shape_kind` is the closed enum `STRING,INTEGER,BOOLEAN,NULL,ARRAY,OBJECT`;
  authority objects always set both member-extension and duplicate-member
  flags false;
- `runtime_identity_id`, `entrypoint_id`, `argv_template_id`,
  `cwd_policy_id`, `environment_policy_id`, `callgraph_allowlist_id`,
  `stdout_protocol_id`, `tolerance_authority_id`, `alias_policy_id`,
  `start_end_policy_id`, `base_authority_id`, `normalization_policy_id`, and
  `namespace_regex_id` resolve to `policy_registry`;
- `null_rule_id` resolves to one `null_rule_registry` row and
  `null_matrix_id` to one `null_matrix_registry` row; the latter must list
  exactly `2^operand_count` rules, whose unique bitmaps exhaust the domain in
  lexicographic false-before-true order; and
- every fixture/expected constructor and every success/failure/indeterminate
  reason resolves to `fixture_constructor_registry` and
  `reason_code_registry`, respectively.

`algorithm_kind` is a closed enum:

```text
PURE_TYPED_AST, STRICT_JSON_DECODE, CANONICAL_TAGGED_ENCODE,
SHA256_RAW_BYTES, POSIX_LSTAT_NOFOLLOW, POSIX_OPEN_NOFOLLOW_READ_HASH,
POSIX_DIRECTORY_INVENTORY, POSIX_ALIAS_GRAPH,
RAW_STREAM_FRAME_DECODE, PROCESS_LIFECYCLE_OBSERVE,
CANONICAL_DECIMAL_EVALUATE, OBSERVATION_PROJECTION,
MUTATION_BYTE_TRANSFORM, MUTATION_TYPED_ROW_TRANSFORM
```

The spec contains the complete literal operator/arity/type/error table for
each kind.  `policy_kind` is likewise closed:

```text
RUNTIME_IDENTITY, ENTRYPOINT, ARGV_TEMPLATE, CWD_DIRECTORY,
REQUESTED_ENVIRONMENT, OBSERVED_ENVIRONMENT, CALLGRAPH_ALLOWLIST,
STDOUT_PROTOCOL, TOLERANCE_AUTHORITY, ALIAS_POLICY, START_END_POLICY,
PATH_BASE, NORMALIZATION_POLICY, NAMESPACE_FULLMATCH,
FILE_MODE_NLINK_POLICY, RESOURCE_LIMIT, NUMBER_TOKEN_POLICY,
ORDERED_RESULT_POLICY
```

Each policy's `literal_payload` contains the exact path or identity authority,
ordered argv/environment entries, allowed callgraph rows, stream grammar,
mode/nlink values, or full-match grammar needed to decide it.  It cannot name
a Python function, WL symbol, environment lookup, glob, or later runtime
configuration.  `OBSERVATION_PROJECTION` may only project a source-bound raw
record into a declared value schema; it cannot compute expected values,
compare, or decide PASS.  A science-capable observation row additionally
binds the exact reviewed source/function/dependency closure in its policy
payload.  Thus the future package must literally populate these rows before
T7 review; T6 has no semantic callback surface to fill.

For complete reference closure, the compiler additionally enforces this
unique target table:

- every `type_id`, `value_schema_id`, `element_schema_id`,
  `field_schema_id`, `result_schema_id`, `output_value_schema_id`, and other
  `*_value_schema_id` resolves to the correspondingly named `type_registry`
  or `value_schema_registry` row;
- `number_token_policy_id`, `ordered_result_policy_id`, every executor/policy
  ID, and every identity/path policy ID resolves to `policy_registry`;
- `ordered_mutation_operator_ids`, mutation-plan `operator_id`, and
  `exact_transform_algorithm_id` resolve through
  `mutation_operator_registry` to the permitted mutation
  `algorithm_registry` kind;
- fixture `algorithm_id` resolves to `algorithm_registry` and its literal
  parameters validate against the constructor input schemas;
- `decision_expression_id`, `domain_expression_id`,
  `expected_cardinality_expression_id`, and every count/dependency expression
  resolve to `expected_expression_registry` unless the field is explicitly
  named `algorithm_id`;
- `input_catalog_id` and `ordered_row_source_id` resolve to
  `catalog_registry` and one literal generated catalog source; catalog
  dependencies are acyclic;
- every evidence-plan ID resolves to `evidence_input_registry`;
- `required_digest_node_id`, `ordered_row_digest_node_id`, and every artifact
  digest reference resolve to the unique `digest_nodes` row;
- all outcome IDs resolve to `reason_code_registry`; and
- every operation, stage, axis, call-plan, schema, path, observer, executor,
  fixture, policy, and algorithm ID resolves to the corresponding unique
  top-level declarative row.

Unknown, cross-category, multiply defined, unconsumed, or cyclic IDs fail
generation.  The fully joined review catalog contains no unresolved string
ending in `_id` or `_ids`; this is itself a generated invariant and mutation
target.

The closed control-plane operator set is:

```text
EXACT_BYTES
EXACT_TAGGED_VALUE
EXACT_ORDERED_ARRAY
EXACT_STRING
EXACT_INTEGER
EXACT_BOOLEAN
EXACT_HASH256
ENUM_MEMBER
ASCII_FULLMATCH
COUNT_EQ
ORDERED_DIGEST_EQ
FILE_IDENTITY_EQ
DIRECTORY_IDENTITY_EQ
STREAM_IDENTITY_EQ
NO_ALIAS
SOURCE_START_END_EQ
PROCESS_SUCCESS
RAW_STREAM_WITHIN_BOUND
ALL_TRUE
```

The closed scientific-comparison operator set, whose operands are canonical
arbitrary-precision decimal or complex-decimal records, is:

```text
DECIMAL_LT
DECIMAL_LE
ABS_DIFFERENCE_LE
SYMMETRIC_RELATIVE_DIFFERENCE_LE
LOG_ABS_DIFFERENCE_LE
INTERVAL_VIOLATION_LE
WRAPPED_PHASE_DIFFERENCE_LE
```

Their mathematical formulas and domain rules are copied mechanically from the
frozen V3.0 formula/threshold authorities into literal expression rows; T6 may
not redefine them.  A zero, negative, nonfinite, unavailable, or out-of-domain
operand follows the threshold JSON's exact applicability rule or returns the
literal `INDETERMINATE` reason code; it never silently clips, floors, promotes,
or passes.  Scientific evaluation uses only canonical decimal strings and a
future package-bound arbitrary-precision evaluator/dependency inventory.  It
may not parse through binary64.  The future package must provide literal
conformance vectors for every boundary and inapplicable branch, and T7 must
recompute them with a source-distinct evaluator.  Until that package exists,
no science comparator is authorized by this analysis.

The only AST constructors are the exact finite set:

```text
CONST, AUTHORITY_REF, FIELD, AXIS, INDEX, LENGTH, HASH, CONCAT,
AND, OR, NOT, EQ, LT, LE, ABS, ADD, SUBTRACT, MULTIPLY, DIVIDE,
SQUARE, SQRT, LN, MAX, MIN, WRAP_TO_PI
```

Each constructor has a literal arity and input/output type row.  There are no
general function names, imports, evaluation strings, callbacks, or dynamic
symbol lookup.  Division by zero, invalid `LN`/`SQRT`, nonfinite value, or
precision shortfall produces a typed indeterminate result and blocks a
required predicate.

`ordered_evidence_plan` in the predicate row is distinct from runtime
`ordered_resolved_evidence`.  Resolution is a generated one-to-one map:

```text
resolved evidence row =
  [plan_ordinal, evidence_plan_id, role, kind, relative_path,
   resolved_identity_schema_id, resolved_identity_authority_sha256,
   content_sha256_or_null, required_digest_authority_sha256,
   identity_policy_result]
```

Cardinality and order must exactly equal the predicate plan.  No evidence row
may be inferred, omitted, filtered, sorted, or shared by alias.

### 6.5 Expansion order and collision rules

The only expansion order is:

```text
operation declaration order
  -> call-plan declaration order
  -> stage ordinal P00 ... P17
  -> predicate-family declaration order
  -> axis declaration order, row-major (left axis slowest)
```

No lexical sorting, set conversion, hash-map iteration, or runtime discovery
is allowed.  Every family declares literal finite axes.  Its format
placeholders must equal its axis names exactly, with no unused axis and no
implicit Cartesian dimension.

Generation fails on duplicate or non-monotone:

- predicate ID;
- `(operation, call_ordinal, stage_ordinal, stage_instance_ordinal)`;
- operation/global instance ordinal;
- call/session ID;
- schema, digest-node, observer, executor, comparison, evidence, path, or
  fixture ID;
- generated durable path; or
- call-plan key.

The future spec must mechanically re-establish the inherited operation
cardinalities:

| Operation | Calls | Predicates/events | Child frames/ACKs | Prefixes | Final-stage checkpoints | Opens | Seeds/exits |
|---|---:|---:|---:|---:|---:|---:|---:|
| compatibility | 1 | 151 | 82 | 151 | 18 | 17 | 1/1 |
| source-load micro | 1 | 409 | 263 | 409 | 18 | 17 | 1/1 |
| full sentinel | 35 | 14,315 | 9,205 | 14,315 | 630 | 595 | 35/35 |
| official | 161 | 65,849 | 42,343 | 65,849 | 2,898 | 2,737 | 161/161 |

The global predicate count is 80,724.  These counts constrain protocol
coverage; they do not authorize scientific execution.

## 7. Canonical types, encodings, and digests

### 7.1 Scalar vocabulary

Authority values use tagged JSON arrays only:

```text
["s", UTF-8 string]
["i", canonical base-10 integer string]
["b", true|false]
["n"]
["h", exactly 64 lowercase ASCII hexadecimal characters]
["d", canonical arbitrary-precision decimal string]
["a", schema_id, ...ordered members...]
```

`bool` is never an integer.  `NaN`, `Infinity`, machine reals, negative zero
aliases, locale formatting, Unicode normalization by implication, and
noncanonical exponents are rejected.  Decimal syntax and significant-digit
policy are frozen in the type registry and shared byte-for-byte by generated
Python and WL adapters.

### 7.2 Encodings

Let `UTF8(x)` mean strict UTF-8 without BOM.

```text
C_SPEC(object) = UTF8(JSON with duplicate rejection, sorted keys,
                      ensure_ascii=false, indent=2, allow_nan=false,
                      exactly one trailing LF)

C_ARRAY(array) = UTF8(compact JSON array, ensure_ascii=false,
                       allow_nan=false, no insignificant whitespace,
                       exactly one trailing LF)
```

Every generated authority and wire artifact is a schema-ordered array encoded
by `C_ARRAY`.  Canonical objects are limited to the spec and human-facing
manifests; their object order is not an authority input.

For avoidance of doubt, every digest input below is tagged before encoding:
`S(x)=["s",x]`, `I(x)=["i",canonical_base10(x)]`, `B(x)=["b",x]`,
`N=["n"]`, `H(x)=["h",x]`, and `D(x)=["d",canonical_decimal(x)]`.
Schema-generated compound values use `A(schema_id, ...tagged members...)`.
`ENC` and `DER` reject bare/untyped JSON scalars; examples that show names
below abbreviate these mandatory tags and are not an alternative encoding.

### 7.3 Domain-separated functions

```text
F(bytes) = lowercase_hex(SHA256(bytes))

ENC(schema_id, revision, tagged_payload) =
  C_ARRAY([S(schema_id), I(revision), ...tagged_payload])

ART(schema_id, revision, tagged_payload) =
  F(b"SCHWO-V31Z\0ARTIFACT\0" + ASCII(schema_id) + b"\0" +
    ENC(schema_id, revision, tagged_payload))

DER(label, tagged_items) =
  F(b"SCHWO-V31Z\0DERIVED\0" + ASCII(label) + b"\0" +
    C_ARRAY(tagged_items))
```

`label` is a literal registry value, never caller supplied.  Cross-schema or
cross-label substitution must fail even when payload bytes happen to match.

The generated leaf manifest excludes itself, the bundle-root record, and the
package checkpoint.  Let `LEAVES` be its exact ordered tagged rows
`A("generated-leaf-row-v1",S(relative_path),I(size),I(mode),I(nlink),
H(F(file_bytes)),S(role))`.  Then:

```text
LEAF_INVENTORY_SHA = DER("generated-leaf-inventory-v1", LEAVES)
```

`leaf_manifest.json` is exactly
`ENC("generated-leaf-manifest-v1",1,[H(SPEC_SHA),H(GENERATOR_SHA),
H(LEAF_INVENTORY_SHA),A("leaf-rows-v1",...LEAVES)])`.  Define
`LEAF_MANIFEST_RAW_SHA=F(those exact bytes)` and
`LEAF_MANIFEST_ART=ART("generated-leaf-manifest-v1",1,the same tagged
payload)`.  Then, exactly:

```text
BUNDLE_ROOT = DER("generated-bundle-root-v1",
                  [H(SPEC_SHA), H(GENERATOR_SHA),
                   H(LEAF_INVENTORY_SHA), H(LEAF_MANIFEST_RAW_SHA),
                   H(LEAF_MANIFEST_ART)])
```

`bundle_root.json` is exactly:

```text
ENC("generated-bundle-root-v1",1,
    [H(SPEC_SHA),H(GENERATOR_SHA),H(LEAF_INVENTORY_SHA),
     H(LEAF_MANIFEST_RAW_SHA),H(LEAF_MANIFEST_ART),H(BUNDLE_ROOT)])
```

Define each portable generated file row as
`[S(relative_path),I(size),I(required_mode),I(required_nlink),H(raw_sha),
S(role)]` and each generated directory row as
`[S(relative_path),I(required_mode),I(required_nlink),
H(DER("ordered-child-names-v1",ordered tagged child names))]`.  Rows follow
`generated_output_plan` declaration/preorder, never filesystem enumeration or
lexical sorting.  `package_checkpoint.json` is exactly:

```text
ENC("generated-package-checkpoint-v1",1,
    [H(SPEC_SHA),H(GENERATOR_SHA),H(LEAF_MANIFEST_RAW_SHA),
     H(F(bundle_root.json exact bytes)),H(BUNDLE_ROOT),
     A("generated-file-rows-v1",...all generated file rows except checkpoint),
     A("generated-directory-rows-v1",...all generated directory rows),
     H(DER("generated-package-tree-v1",all file and directory rows)),
     B(true)])
```

This portable checkpoint deliberately excludes device/inode so independent
temporary recompilations are byte-identical.  The later frozen package source
ledger separately records and validates the final tree's actual no-follow
path/device/inode/mode/nlink/size/hash identities.  The package binds the
checkpoint's external raw SHA-256 and file identity.  None of these three records is embedded in
generated validator bytes; validators receive the verified `BUNDLE_ROOT` at
load time.  This exact layered membership removes both self-reference and a
replaceable unbound inventory file.

## 8. Generated primary artifact schemas

The package-time generated schema catalog enumerates every field with JSON
type, Python type, WL head, nullability, finite enum/domain, literal/derived rule, and
digest dependencies.  The applicable prefix plus each listed suffix is the
complete exact primary catalog; fields may not be inserted or omitted.
Nested `FileIdentity`, `ProcessClosure`, `StreamIdentity`,
`FailureClosure`, and `ScienceCounters` are themselves generated schemas, not
open dictionaries.

Primary schemas 8.1--8.11 are per-call session artifacts and begin with this
exact `SessionPrefix`:

```text
schema_id, schema_revision, bundle_root, gate_id, operation,
call_ordinal, call_plan_entry_sha256, session_sha256,
dispatch_sha256, request_sha256
```

Primary schemas 8.12--8.13 are operation/root artifacts and instead begin
with this non-overlapping exact `OperationRootPrefix`:

```text
schema_id, schema_revision, bundle_root, gate_id, operation,
dispatch_consumption_sha256, run_contract_sha256, root_identity_sha256
```

No operation/root record contains a synthetic call ordinal, session, request,
or call-plan entry; no per-call record may use `OperationRootPrefix`.

`session_sha256` is derived with mandatory tags as:

```text
DER("session-v1", [H(bundle_root), S(gate_id), S(operation),
                    I(call_ordinal), H(call_plan_entry_sha256),
                    H(dispatch_sha256), H(request_sha256),
                    H(root_identity_sha256),
                    H(prior_call_terminal_manifest_authority_sha256) or N,
                    H(prior_call_terminal_checkpoint_file_identity_sha256)
                      or N,
                    H(prior_call_directory_seal_closeout_authority_sha256)
                      or N])
```

All three prior-call inputs are null only for call zero.  A later call requires
all three and must bind the immediately preceding successful call.  The
checkpoint FileIdentity is observed under the lock before close;
the subsequently published `CallDirectorySealCloseout` binds that checkpoint
and the actual post-chmod
DirectoryIdentity while the operation flock remains held.  A manifest or
checkpoint without that seal closeout cannot seed the next call.

### 8.0 Generated nested authority schemas

No primary-schema field may contain an open dictionary.  The catalog must
generate these exact ordered nested rows:

```text
FileIdentity =
  [relative_path, resolved_path, kind="REGULAR", device, inode, mode,
   nlink, size, content_sha256, nofollow_reopen, alias_group_id]

DirectoryIdentity =
  [relative_path, resolved_path, kind="DIRECTORY", device, inode, mode,
   nlink, ordered_entry_names_sha256, nofollow_reopen, alias_group_id]

RootIdentity =
  [resolved_root, relative_root, parent_directory_identity_sha256,
   basename, namespace_id, device, inode, mode, nlink,
   direct_child, no_alias]

StreamIdentity =
  [role, relative_path, file_identity_sha256, raw_size,
   raw_content_sha256, frame_count, last_frame_sha256_or_null,
   exactly_one_final_lf, within_frozen_limit]

ProcessClosure =
  [pid, sid, pgid, return_code, signal_or_null, timed_out,
   terminate_attempted, terminate_result, kill_attempted, kill_result,
   waited, reaped, process_group_empty, wait_error_count,
   ordered_wait_error_sha256s, related_process_count]

CallDirectorySealCloseout =
  [bundle_root, gate_id, operation, call_ordinal, session_sha256,
   terminal_checkpoint_file_identity_sha256,
   call_directory_identity_sha256_before_close,
   call_directory_identity_sha256_after_close,
   closed_mode, directory_fsynced, parent_directory_fsynced,
   operation_lock_still_held, post_close_mutation_count, status]

WriterHeldClosure =
  [lock_relative_path, lock_file_identity_sha256, flock_acquired,
   exclusive_owner_pid, exclusive_owner_sid, exclusive_owner_pgid,
   competing_writer_count, lock_scope="OPERATION",
   held_at_observation, required_hold_through_root_checkpoint,
   expected_release_after_root_close]

WriterReleaseCloseout =
  [bundle_root, gate_id, operation, dispatch_consumption_sha256,
   root_terminal_checkpoint_file_identity_sha256,
   lock_file_identity_sha256, former_owner_pid, former_owner_sid,
   former_owner_pgid, flock_released, root_mode_after_close,
   root_directory_identity_sha256_after_close,
   active_writer_count_after_release, related_process_count_after_release,
   closeout_observer_id, status]

ResolvedEvidence =
  [plan_ordinal, evidence_plan_id, role, kind, relative_path,
   resolved_identity_schema_id, resolved_identity_authority_sha256,
   content_sha256_or_null, required_digest_authority_sha256,
   identity_policy_result]

ScienceCounters =
  [wolfram_kernel_launches, bhpt_public_api_calls,
   regge_wheeler_radial_calls, external_api_calls, solver_calls,
   boundary_solutions, overlap_records, route_a_modes,
   route_a_ladder_records, route_u_modes, route_u_precision_records,
   route_b_modes, route_b_records, route_c_anchors, route_c_api_calls,
   route_c_boundary_solutions, route_c_overlap_records]

FailureClosure =
  [failure_class, stage_ordinal_or_null, predicate_id_or_null,
   edge_id_or_null, reason_code, exception_type_or_null,
   exception_message_sha256_or_null, offending_raw_sha256_or_null,
   last_frame_sha256_or_null, last_event_authority_sha256_or_null,
   last_prefix_authority_sha256_or_null,
   last_stage_final_authority_sha256_or_null,
   last_stage_open_authority_sha256_or_null,
   failure_termination_authority_sha256_or_null,
   lifecycle_receipt_authority_sha256_or_null,
   resumable, scientific_pass]
```

Modes are exact integers (for example, displayed octal `0444` is decimal
`292` in the integer payload).  File and directory identities are distinct;
receipt `cwd` is a `DirectoryIdentity`, never a `FileIdentity`.  Every
identity is parent-observed by no-follow reopen/stat/rehash and exact
alias-graph closure.

Supporting artifacts likewise have generated ordered schemas:

```text
DispatchConsumption =
  [dispatch_file_identity_sha256, dispatch_raw_sha256,
   dispatch_canonical_sha256, attempt_ordinal, operation,
   exact_root, prior_review_path, prior_review_sha256,
   package_sha256, bundle_root, executable_identity_sha256,
   exact_argv, exact_cwd_directory_identity_sha256,
   requested_environment, expected_observed_environment,
   consumed_file_identity_sha256, one_use, consumed_before_child]

RunContract =
  [gate_id, operation, bundle_root, dispatch_consumption_sha256,
   root_identity_sha256, executable_identity_sha256, exact_argv,
   cwd_directory_identity_sha256, requested_environment,
   observed_environment_contract_sha256, source_plan_sha256,
   operation_plan_sha256, resource_limits_sha256, nonclaims_sha256]

SourceLedger =
  [boundary_kind, source_plan_sha256,
   ordered_file_identity_authorities,
   ordered_directory_identity_authorities,
   wolfram_runtime_identity_sha256,
   bhpt_snapshot_metadata_sha256,
   bhpt_content_inventory_sha256,
   bhpt_identity_inventory_sha256,
   ordered_loaded_context_source_tuples,
   ordered_dependency_tree_identities,
   source_inventory_sha256,
   compared_boundary_authority_sha256_or_null,
   start_end_equal_or_null]

FailureTerminationAuthority =
  [failure_closure_prefix_sha256, pid, sid, pgid,
   terminate_after_ns, kill_after_ns, stdout_limit, stderr_limit,
   expected_next_frame=null, status="AUTHORIZED_TO_TERMINATE"]

PreRootControlFailure =
  [schema_id="pre-root-control-failure-v1", schema_revision=1,
   bundle_root, gate_id, operation,
   package_checkpoint_file_identity_sha256,
   package_review_file_identity_sha256,
   implementation_review_file_identity_sha256_or_null,
   prior_operation_review_file_identity_sha256_or_null,
   dispatch_file_identity_sha256, dispatch_consumed=false,
   executable_file_identity_sha256, exact_argv_sha256,
   cwd_directory_identity_sha256,
   requested_environment_sha256, observed_environment_sha256,
   requested_root, root_created=false, failure_stage, reason_code,
   related_process_count, science_counters,
   terminal_status="CONTROL_FAILURE_NO_ROOT"]

TerminalCheckpoint =
  [terminal_manifest_file_identity_sha256,
   premanifest_inventory_file_identity_sha256,
   postmanifest_precheckpoint_inventory_file_identity_sha256,
   call_directory_identity_sha256_before_close,
   expected_closed_call_directory_mode,
   writer_held_closure_sha256,
   process_closure_sha256, terminal_kind, seal_commit]
```

The path grammar gives each artifact one literal path.  Source end reopens and
rehashes every start identity rather than comparing cached summaries.
`ordered_resolved_evidence` in `parent_event` is an exact array of
`ResolvedEvidence`; its row count/order/IDs must equal the predicate row's
`ordered_evidence_plan` one-for-one.
`PreRootControlFailure` is published only at literal path
`runs/phase6/transients/v3_1_z_pre_root_failures/<exact_dispatch_basename>.json`
with O_EXCL/no-follow, mode `0444`, nlink 1, file/parent fsync, and reload.  The
basename comes from the one listed dispatch path, never a glob or argument.
Its authority roles and order are exactly the fields above; nullability of the
two review identities follows the operation's fixed predecessor graph.  Both
`dispatch_consumed` and `root_created` must be false.  It is not a
session/root artifact and cannot claim a terminal science status.
Every V3.1-Z v1 `FailureClosure.resumable` value is the literal false.

### 8.1 `child_observation_frame`

Ordered suffix:

```text
frame_sequence, proposed_event_sequence, stage_ordinal, stage_id,
frame_kind, predicate_or_barrier_id, predicate_row_sha256_or_null,
record_ordinal_or_null, field_id, observer_id, value_type_id,
observed_value, stage_authority_sha256,
previous_child_frame_raw_sha256_or_null,
prior_prefix_checkpoint_sha256, raw_stream_offset
```

The child never emits expected values, comparison results, PASS/FAIL, or
terminal status.  `frame_kind` is exactly `PREDICATE`, `CONTROL_BARRIER`, or
`PREDICATE_BARRIER`.  A compatibility `CONTROL_BARRIER` has null predicate row
and creates no logical request event; it opens the exact parent-fixture plan.
A production `PREDICATE_BARRIER` has the non-null generated request-predicate
row and becomes the first logical event of that stage before the remaining
parent observations.  Its `field_id`, observer, type, and observed request
literal come from that row.  The generated null matrix forbids either role
from being substituted for the other.  Parent validation of the raw frame
precedes any semantic event or ACK.

### 8.2 `parent_event`

Ordered suffix:

```text
event_sequence, stage_ordinal, stage_id, predicate_id,
predicate_row_sha256, stage_instance_ordinal, owner, observer_id,
executor_id, field_id, value_type_id, comparison_id, expected_value,
observed_value, outcome, child_frame_sequence_or_null,
child_frame_raw_sha256_or_null, barrier_id_or_null,
stage_authority_sha256, previous_event_authority_sha256_or_null,
ordered_resolved_evidence
```

The parent loads the predicate row from the immutable bundle, independently
observes or verifies the value, applies the frozen comparison, and constructs
the event.  Live progression requires `outcome=PASS`; FAIL or INDETERMINATE
enters immutable failure terminalization.

### 8.3 `prefix_checkpoint`

Ordered suffix:

```text
through_event_sequence, total_event_count, stage_event_count,
current_event_authority_sha256, previous_prefix_authority_sha256_or_null,
prior_chain_sha256, stage_authority_sha256, prefix_chain_sha256,
all_pass_through
```

The first event of each call uses the zero-chain seed from `stage0_seed`;
event and prefix sequence numbers do not reset at stage boundaries.  Later
prefixes use the preceding prefix chain.  Counts and hashes are recomputed
from prior immutable artifacts, never trusted from this record.

### 8.4 `final_stage_checkpoint`

Ordered suffix:

```text
stage_ordinal, stage_id, stage_authority_sha256,
first_event_sequence, last_event_sequence, declared_event_count,
ordered_predicate_ids_sha256, ordered_event_authorities_sha256,
first_prefix_authority_sha256, last_prefix_authority_sha256,
prior_stage_final_authority_sha256_or_null,
barrier_id_or_null, actor_profile_id, all_pass
```

P00 is the sole stage whose prior final is null.  Every other final binds the
previous stage final.  Exact event and predicate inventories come from the
generated operation DAG.

### 8.5 `ack`

Ordered suffix:

```text
frame_sequence, acknowledged_frame_raw_sha256,
committed_through_event_sequence, durable_prefix_authority_sha256,
final_stage_authority_sha256_or_null,
next_stage_open_authority_sha256_or_null,
child_exit_authority_sha256_or_null,
expected_next_frame_sequence_or_null,
expected_next_event_sequence_or_null,
ack_kind, outcome
```

`outcome` is the literal `PASS`.  The exact null matrix is generated for
`EVENT`, `STAGE_FINAL`, `PARENT_BARRIER_FINAL`, and `CHILD_EXIT`.  ACK bytes
are O_EXCL-published, fsynced, reloaded, and validated before sending.  No
negative ACK exists.

### 8.6 `stage_open_authority`

Ordered suffix:

```text
from_stage_ordinal, from_stage_id,
from_stage_final_authority_sha256, from_last_prefix_authority_sha256,
prior_open_or_seed_authority_sha256,
to_stage_ordinal, to_stage_id, actor_profile_id,
expected_first_frame_sequence_or_null,
expected_first_event_sequence, expected_first_predicate_id,
declared_event_count, ordered_predicate_ids_sha256,
barrier_id_or_null, observer_plan_sha256, path_grammar_sha256,
child_exit_authority_sha256_or_null,
lifecycle_receipt_authority_sha256_or_null, status
```

`status` is literal `OPEN`.  Open 1 binds final0 plus the seed.  Opens 2--16
bind the preceding final/open.  Open17 is parent-only: it has no expected
child frame and must bind both child exit authority and the durable lifecycle
receipt.  Stage opens are one-use.

### 8.7 `stage0_seed`

Ordered suffix:

```text
root_relative_path, root_identity_sha256,
dispatch_raw_sha256, dispatch_canonical_sha256,
request_raw_sha256, request_canonical_sha256,
run_contract_sha256, source_start_plan_sha256,
prior_call_terminal_manifest_sha256_or_null,
prior_call_terminal_checkpoint_file_identity_sha256_or_null,
prior_call_directory_seal_closeout_authority_sha256_or_null,
expected_p00_predicate_ids_sha256, expected_p00_count,
zero_event_chain_seed_sha256, p00_observer_plan_sha256,
path_grammar_sha256, status
```

`expected_p00_count` is exactly 5 and `status` is literal `SEALED`.  The five
P00 predicates are exactly `RAW_BYTES`, `NO_DUPLICATE_MEMBER`,
`CANONICAL_BYTES`, `DISPATCH_IDENTITY`, and `ROOT_IDENTITY`; all are
parent-owned.  P00 has no stage-open file.  Every P00 event and prefix uses
`ART(stage0_seed)` as its non-null stage authority.  Final0 binds the seed and
five events; open1 binds final0 and the seed.  This is the sole valid seed-edge
mapping.

Their generated semantic rows are fixed by this table (the future spec uses
the exact fully qualified IDs, while the short names are shown here):

```text
[Z.EVID.P00.REQUEST_RAW, REQUEST, RAW_BYTES,
 Z.PATH.CALL.REQUEST_RAW, Z.IDPOL.IMMUTABLE_RAW_INPUT,
 Z.DIGEST.REQUEST_RAW]
[Z.EVID.P00.STRICT_PARSE, PARSE_RECEIPT, STRICT_JSON_PARSE,
 Z.PATH.CALL.REQUEST_PARSE_RECEIPT, Z.IDPOL.IMMUTABLE_AUTHORITY,
 Z.DIGEST.REQUEST_PARSE_RECEIPT]
[Z.EVID.P00.CANONICAL_REQUEST, REQUEST, CANONICAL_BYTES,
 Z.PATH.CALL.REQUEST_CANONICAL, Z.IDPOL.IMMUTABLE_AUTHORITY,
 Z.DIGEST.REQUEST_CANONICAL]
[Z.EVID.P00.DISPATCH, DISPATCH, FILE_IDENTITY,
 Z.PATH.ROOT.DISPATCH_SOURCE, Z.IDPOL.EXTERNAL_IMMUTABLE_FILE,
 Z.DIGEST.DISPATCH_FILE_IDENTITY]
[Z.EVID.P00.DISPATCH_CONSUMPTION, DISPATCH, CONSUMPTION_AUTHORITY,
 Z.PATH.ROOT.DISPATCH_CONSUMPTION, Z.IDPOL.IMMUTABLE_AUTHORITY,
 Z.DIGEST.DISPATCH_CONSUMPTION]
[Z.EVID.P00.ROOT, ROOT, DIRECTORY_IDENTITY,
 Z.PATH.ROOT.IDENTITY, Z.IDPOL.FRESH_ROOT_DIRECTORY,
 Z.DIGEST.ROOT_IDENTITY]
```

These rows use the same exact six-field evidence-registry order stated in
Section 6.4.

| P00 predicate | field / value schema | comparison and expected value | ordered evidence-plan IDs |
|---|---|---|---|
| `RAW_BYTES` | `request_raw_sha256 / HASH256` | `EXACT_HASH256`; dispatch-bound raw request SHA | `Z.EVID.P00.REQUEST_RAW`, `Z.EVID.P00.DISPATCH` |
| `NO_DUPLICATE_MEMBER` | `duplicate_member_free / BOOLEAN` | `EXACT_BOOLEAN`; literal `true` | `Z.EVID.P00.REQUEST_RAW`, `Z.EVID.P00.STRICT_PARSE` |
| `CANONICAL_BYTES` | `request_canonical_sha256 / HASH256` | `EXACT_HASH256`; canonical re-encoding SHA from the strict parse | `Z.EVID.P00.REQUEST_RAW`, `Z.EVID.P00.CANONICAL_REQUEST` |
| `DISPATCH_IDENTITY` | `dispatch_file_identity_sha256 / HASH256` | `EXACT_HASH256`; dispatch-consumption-bound FileIdentity authority SHA | `Z.EVID.P00.DISPATCH`, `Z.EVID.P00.DISPATCH_CONSUMPTION` |
| `ROOT_IDENTITY` | `root_identity_sha256 / HASH256` | `EXACT_HASH256`; stage0-seed-bound fresh RootIdentity authority SHA | `Z.EVID.P00.ROOT`, `Z.EVID.P00.DISPATCH_CONSUMPTION` |

All five use `PARENT_OBSERVED`, the generated parent authority observer, and
literal non-null value schemas.  The named evidence rows resolve to exact
paths and identity policies through `evidence_input_registry`; they are not
implementation aliases.

### 8.8 `child_exit_authority`

Ordered suffix:

```text
stage16_final_authority_sha256,
stage16_last_prefix_authority_sha256,
expected_return_code, expected_first_p17_event_sequence,
stdout_raw_limit_bytes, stderr_raw_limit_bytes,
exit_timeout_ns, status
```

`expected_return_code=0`; `status=AUTHORIZED_TO_EXIT`.  It is committed before
the final child ACK.  The child validates that ACK, flushes both streams, and
exits.  It cannot emit P17 evidence.

### 8.9 `lifecycle_receipt`

Ordered suffix:

```text
exit_authority_kind,
child_exit_authority_sha256_or_null,
failure_termination_authority_sha256_or_null,
executable_file_identity, argv, cwd_directory_identity,
requested_environment, observed_environment,
pid, sid, pgid, started_monotonic_ns, ended_monotonic_ns,
stdout_stream_identity, stderr_stream_identity,
accepted_frame_count, last_frame_raw_sha256_or_null,
eof_observed, return_code, signal_or_null, timed_out,
terminate_attempted, terminate_result, kill_attempted, kill_result,
waited, reaped, process_group_empty, wait_error_count,
ordered_wait_error_digests, related_process_closure,
writer_lock_identity, status
```

`exit_authority_kind` is exactly `NORMAL_EXIT` or `FAILURE_TERMINATION` and
the two following authorities obey an exact XOR null matrix.  The normal
branch binds the P16 child-exit authority.  A failure before P16 binds a
separately generated `FailureTerminationAuthority`; it never fabricates a
normal child-exit record.  All fields are parent-observed.  The `cwd` field is
specifically a `DirectoryIdentity` authority.  Monotonic timestamps are diagnostic and
never determine order or acceptance.  Requested and observed environments
are distinct exact generated schemas.  On success, return code is zero,
signal is null, timeout false, waited/reaped/process-group-empty true, and
wait error count zero.  Failure receipts retain the actual values.  The
receipt is O_EXCL/no-follow published, fsynced with its parent, reloaded, and
hashed with `ART`; a tuple embedded only in another record is insufficient.

### 8.10 `p17_closure`

Ordered suffix:

```text
open17_authority_sha256, child_exit_authority_sha256,
lifecycle_receipt_authority_sha256,
first_p17_event_sequence, last_p17_event_sequence,
p17_event_count, ordered_p17_predicate_ids_sha256,
ordered_p17_event_authorities_sha256,
last_p17_prefix_authority_sha256,
final17_authority_sha256, all_pass
```

The eight parent-owned P17 predicates are exactly `RETURN_CODE`, `SIGNAL`,
`TIMEOUT`, `WAITED`, `REAPED`, `PROCESS_GROUP_EMPTY`, `RAW_STDOUT_BOUND`, and
`RAW_STDERR_BOUND`.  Every row's ordered evidence contains child exit and
lifecycle receipt; the two stream rows additionally contain the corresponding
stream identity.  P17 has no child frame, ACK, or next open.  The P17 event and
prefix chains continue from P16 and do not reset.

The evidence registry contains these four literal rows:

```text
[Z.EVID.P17.EXIT, AUTHORITY, CHILD_EXIT_AUTHORITY,
 Z.PATH.CALL.CHILD_EXIT, Z.IDPOL.IMMUTABLE_AUTHORITY,
 Z.DIGEST.CHILD_EXIT]
[Z.EVID.P17.RECEIPT, PROCESS_RECEIPT, LIFECYCLE_RECEIPT,
 Z.PATH.CALL.LIFECYCLE_RECEIPT, Z.IDPOL.IMMUTABLE_AUTHORITY,
 Z.DIGEST.LIFECYCLE_RECEIPT]
[Z.EVID.P17.STDOUT, RAW_STREAM, STDOUT,
 Z.PATH.CALL.STDOUT_RAW, Z.IDPOL.IMMUTABLE_RAW_STREAM,
 Z.DIGEST.STDOUT_STREAM]
[Z.EVID.P17.STDERR, RAW_STREAM, STDERR,
 Z.PATH.CALL.STDERR_RAW, Z.IDPOL.IMMUTABLE_RAW_STREAM,
 Z.DIGEST.STDERR_STREAM]
```

Here the displayed rows are
`[evidence_plan_id,role,kind,path_expression_id,identity_policy_id,required_digest_node_id]`.
The eight predicate rows are then literal and complete:

| P17 predicate | field / value schema | comparison and expected value | ordered evidence-plan IDs |
|---|---|---|---|
| `RETURN_CODE` | `return_code / INTEGER` | `EXACT_INTEGER`; `0` | `EXIT`, `RECEIPT` |
| `SIGNAL` | `signal_or_null / OPTIONAL_INTEGER` | `EXACT_TAGGED_VALUE`; null | `EXIT`, `RECEIPT` |
| `TIMEOUT` | `timed_out / BOOLEAN` | `EXACT_BOOLEAN`; false | `EXIT`, `RECEIPT` |
| `WAITED` | `waited / BOOLEAN` | `EXACT_BOOLEAN`; true | `EXIT`, `RECEIPT` |
| `REAPED` | `reaped / BOOLEAN` | `EXACT_BOOLEAN`; true | `EXIT`, `RECEIPT` |
| `PROCESS_GROUP_EMPTY` | `process_group_empty / BOOLEAN` | `EXACT_BOOLEAN`; true | `EXIT`, `RECEIPT` |
| `RAW_STDOUT_BOUND` | `stdout_within_bound / BOOLEAN` | `EXACT_BOOLEAN`; true | `EXIT`, `RECEIPT`, `STDOUT` |
| `RAW_STDERR_BOUND` | `stderr_within_bound / BOOLEAN` | `EXACT_BOOLEAN`; true | `EXIT`, `RECEIPT`, `STDERR` |

Short evidence names in the table expand only to the four fully qualified IDs
above.  Owner is `PARENT_OBSERVED`; observer is the generated lifecycle/raw-
stream parent observer.  No child field or manifest summary can substitute
for these evidence rows.

### 8.11 `terminal_manifest`

Ordered suffix:

```text
terminal_kind, spec_sha256, generator_sha256,
generated_leaf_inventory_sha256,
root_identity_sha256, stage0_seed_authority_sha256,
prior_call_terminal_manifest_sha256_or_null,
prior_call_terminal_checkpoint_file_identity_sha256_or_null,
prior_call_directory_seal_closeout_authority_sha256_or_null,
ordered_stage_final_authorities_sha256,
ordered_stage_open_authorities_sha256,
last_event_authority_sha256_or_null,
last_prefix_authority_sha256_or_null,
child_exit_authority_sha256_or_null,
lifecycle_receipt_authority_sha256_or_null,
p17_closure_authority_sha256_or_null,
result_artifact_identity_or_null, failure_artifact_identity_or_null,
session_output_inventory_sha256,
premanifest_inventory_file_identity_sha256,
source_ledger_start_sha256, source_ledger_end_sha256,
source_ledger_equal, science_counters,
threshold_bundle_sha256_or_null, certificate_bundle_sha256_or_null,
writer_held_closure_sha256, process_closure_sha256,
nonclaims_sha256, terminal_status
```

It is a generated tagged union with exact branches `SUCCESS`,
`FAILURE_PRELAUNCH`, `FAILURE_CHILD_ACTIVE`, and `FAILURE_POSTREAP`.  Each
branch has a generated null/value matrix and exact `FailureClosure` evidence.
A success requires P17 closure.  A failure before dispatch consumption/root
creation is recorded only as a generated `PreRootControlFailure` at an exact
transient-authority path; it is not a session-manifest branch and cannot
consume a dispatch or claim a root/session/seed.
Within the root, `FAILURE_PRELAUNCH` means dispatch was consumed and
root/session/seed were durably created but no child was launched; it forbids
child exit, receipt, and P17 artifacts.  A child-active failure requires the
failure-termination authority plus the actual receipt/process closure; a
post-reap failure requires its normal-exit or failure receipt as observed.
The manifest has no self hash.  Its file
identity is committed by an external terminal checkpoint and, for a successful
call, becomes the next call's seed input.

Terminal membership is exactly layered:

1. `premanifest_inventory.json` lists every immutable per-call session
   artifact created so
   far except itself, terminal manifest, and terminal checkpoint;
2. the terminal manifest binds the full `FileIdentity` authority of that premanifest
   inventory;
3. `postmanifest_precheckpoint_inventory.json` lists every artifact including
   the premanifest inventory and terminal manifest, but excludes itself and
   the terminal checkpoint;
4. `terminal_checkpoint.json` binds both inventories' full `FileIdentity`
   authorities and the terminal-manifest full `FileIdentity` authority; and
5. the formal outer review binds the checkpoint's file SHA/stat identity.

Neither inventory contains its own row.  The exact exclusions are literal in
the generated path grammar.  Unknown files, missing rows, or replacement of
either inventory fails closure.

Each call lives in a direct `protocol/call_NNNN/` session directory.  Its
terminal checkpoint seals only that directory; later calls cannot reopen it.
After the last expected call, an operation-level premanifest inventory lists
all exact per-call terminal checkpoints and the fixed root-level authorities.
An operation terminal manifest then binds that inventory, exact call count and
order, the ordered call-terminal-authority digest, aggregate science counters,
source start/end, thresholds/certificates where applicable, and process/writer
closure.  A root-level postmanifest inventory and external root checkpoint use
the same non-self-referential three-layer scheme.  Thus call 0 can bind call 1
without attempting to seal the entire still-growing operation root, while the
final root still has one exact closed inventory.

### 8.12 `operation_terminal_manifest`

This generated schema, distinct from the per-call manifest, has the exact
ordered suffix:

```text
terminal_kind, operation_plan_sha256, expected_call_count,
completed_call_count, failing_call_ordinal_or_null,
next_call_ordinal_or_null, failure_closure_sha256_or_null,
ordered_call_plan_entry_sha256s, ordered_call_session_ids,
ordered_call_terminal_checkpoint_file_identity_sha256s,
ordered_call_terminal_manifest_authority_sha256s,
ordered_call_directory_seal_closeout_authority_sha256s,
ordered_call_terminal_chain_sha256,
operation_premanifest_inventory_file_identity_sha256,
source_ledger_start_sha256, source_ledger_end_sha256,
source_ledger_equal, aggregate_science_counters,
threshold_bundle_sha256_or_null, certificate_bundle_sha256_or_null,
writer_held_closure_sha256, aggregate_process_closure_sha256,
nonclaims_sha256, terminal_status
```

`terminal_kind` is the closed enum `SUCCESS`, `FAILURE_CALL`,
`FAILURE_PRECALL`, or `FAILURE_BETWEEN_CALLS`.  `SUCCESS` requires `completed_call_count == expected_call_count`, no failing
ordinal, exact call-plan order, every sealed per-call checkpoint, source
equality, and all applicable blocking predicates.  `FAILURE_CALL` requires the
exact maximal completed-call prefix plus the single immutable failing-call
terminal; it cannot omit, reorder, promote, or retry a call.  The operation
premanifest excludes itself, the operation postmanifest inventory, and the
root checkpoint.

`FAILURE_PRECALL` covers dispatch consumption plus operation root/run-contract
creation before call-0 seed publication: completed count is zero, failing
ordinal is zero, and no call terminal may exist.  `FAILURE_BETWEEN_CALLS`
covers a failure after call `k-1` is checkpointed and closed but before call
`k` seed exists: it binds the exact maximal sealed prefix, next ordinal `k`,
the prior call manifest and checkpoint identity, and a typed `FailureClosure`,
without fabricating a failing-call session.  `FAILURE_CALL` alone requires
the single immutable failing-call terminal.  These branches close every
operation-root failure window without pretending an atomic cross-call step.
Every completed-prefix branch binds each prior call's manifest, checkpoint,
`CallDirectorySealCloseout`, post-close DirectoryIdentity, and ordered chain;
in particular `FAILURE_BETWEEN_CALLS` cannot call a merely checkpointed but
unsealed predecessor “closed.”

### 8.13 `root_terminal_checkpoint`

The final root checkpoint has the exact ordered suffix:

```text
operation_terminal_manifest_file_identity_sha256,
operation_premanifest_inventory_file_identity_sha256,
operation_postmanifest_precheckpoint_inventory_file_identity_sha256,
dispatch_consumption_file_identity_sha256,
writer_held_closure_sha256, aggregate_process_closure_sha256,
terminal_kind, seal_commit
```

It is the only root-level terminal authority.  It is published after the
operation postmanifest inventory, binds full file identities rather than only
content digests, is excluded from that inventory, and is itself bound by the
formal review.  `seal_commit=true` is a commitment to execute the close
sequence below; it is not a self-report that the still-held lock was already
released.  No later call, recovery record, or unknown path may be added.

### 8.14 Physical close and writer-release authority

The generated path/state plan freezes this sequence:

1. Create the fresh direct-child operation root and every active directory
   mode `0700`; create the stable never-renamed `.writer.lock` with exclusive
   creation, acquire its flock, and keep that same file descriptor locked
   through root-checkpoint publication and root-directory close.
2. Publish each immutable file by a same-directory mode-`0600` temporary,
   write/full `fsync`, `renamex_np(RENAME_EXCL)` (or a package-reviewed exact
   equivalent), no-follow reopen/reload/rehash, chmod `0444`, file `fsync`, and
   parent-directory `fsync`.  A missing platform primitive is a STOP, not
   permission to overwrite.
3. After each per-call terminal checkpoint, independently reload its exact
   inventory, chmod that call's directories bottom-up to `0555`, fsync each
   directory and its parent, and O_EXCL-publish a mode-`0444`
   `CallDirectorySealCloseout` at literal path
   `protocol/call_seals/call_<call_ordinal:04d>.json` in the still-writable
   root-level control directory.  It binds the checkpoint FileIdentity, pre/post-close call
   DirectoryIdentities, mode `0555`, both fsync facts, zero post-close
   mutations, and `operation_lock_still_held=true`.  Reload/fsync that record.
   The operation flock remains held; no per-call artifact claims lock release.
   The next call seed is forbidden until this closeout exists and validates.
4. After the last/failing operation branch, observe and publish
   `WriterHeldClosure`, then operation inventories/manifest and the root
   checkpoint, all under the flock.  Reload their exact identities and verify
   the complete allowed-path inventory.
5. Chmod every remaining evidence directory bottom-up to `0555`, including
   the root, fsync them and the exact root parent, and reobserve the expected
   post-close root/directory identities.  No root byte may change afterward.
6. Release the flock without altering its closed file.  A parent-owned
   observer then O_EXCL-publishes mode-`0444`
   `runs/phase6/transients/v3_1_z_writer_closeouts/<root_basename>.json`, a
   `WriterReleaseCloseout` binding the root checkpoint, post-close root
   identity, lock identity, former owner, released=true, zero active writers,
   and zero related processes; fsync its parent.  The formal T7 review must
   bind both the immutable root checkpoint and this external closeout.

Wrong mode, link, alias, missing fsync/reload, a mutable post-close directory,
closeout-before-checkpoint, release-before-root-close, continued writer, or
post-close mutation is fail-closed.  The closeout cannot alter or complete a
scientific predicate; it proves only the physically unavoidable fact that
becomes observable after the locked root has been sealed.

## 9. Derived digest DAG

The generated digest catalog must freeze every node's ordered input list,
type, label, and predecessor set.  At minimum it contains:

| Node | Exact ordered inputs |
|---|---|
| `predicate_row` | `[H(spec_sha), A(predicate-row-v1, exact tagged row)]` |
| `call_plan_entry` | `[S(operation), I(call_ordinal), A(call-key-v1, exact tagged key/node tuple), I(prior_call_ordinal) or N]` |
| `session` | `[H(bundle_root),S(gate),S(operation),I(call),H(call_plan),H(dispatch),H(request),H(root_identity),H(prior_success_manifest) or N,H(prior_success_checkpoint_file_identity) or N,H(prior_call_directory_seal_closeout) or N]` |
| `ordered_predicate_ids` | `[S(predicate_id_0),...,S(predicate_id_n)]` in declaration order |
| `ordered_event_authorities` | `[H(ART(event_0)),...,H(ART(event_n))]` in event order |
| `observer_plan` | `[S(operation),I(call),I(stage),S(actor_profile),S(barrier) or N,A(observer-row-v1,...),...]` |
| `path_grammar` | `[S(operation),A(path-row-v1,...),...]` in literal declaration order |
| `zero_event_chain_seed` | `[H(bundle),S(gate),I(revision),H(session),H(dispatch),H(request),H(root),H(P00_ID_digest),I(5),H(path_grammar)]` |
| `event` | `ART(parent_event-v1, exact tagged fields including A(resolved-evidence-v1,...) rows)` |
| `prefix_chain` | `[H(bundle),S(gate),I(revision),H(session),I(event_seq),H(prior_chain),H(event_authority),H(stage_authority)]` |
| `stage_final` | `ART(final-stage-v1, exact tagged stage span, predicate/event digests, prefix ends, prior final or N, actor/barrier)` |
| `stage_open` | `ART(stage-open-v1, tagged prior final/prefix/open-or-seed, target plan, observer/path, exit/receipt null matrix)` |
| `child_exit` | `ART(child-exit-v1,[H(final16),H(prefix16),I(0),I(next_event),I(stdout_limit),I(stderr_limit),I(timeout_ns),S(status)])` |
| `failure_termination` | `ART(failure-termination-v1, exact tagged failure prefix/process/timeout/stream contract)` |
| `lifecycle_receipt` | `ART(lifecycle-receipt-v1, exact tagged exit XOR, process, stream, and lock fields)` |
| `p17_closure` | `ART(p17-closure-v1,[H(open17),H(exit),H(receipt),I(first),I(last),I(8),H(ids),H(events),H(prefix),H(final17),B(all_pass)])` |
| `call_premanifest_inventory` | `DER("call-premanifest-inventory-v1", exact ordered `A(file-identity-v1,...)` rows under the literal exclusion set)` |
| `terminal_manifest` | `ART(terminal-manifest-v1, SessionPrefix plus every exact tagged Section-8.11 field including prior manifest+checkpoint and call-premanifest FileIdentity)` |
| `call_postmanifest_inventory` | `DER("call-postmanifest-precheckpoint-inventory-v1", exact ordered FileIdentity rows including premanifest+manifest and excluding itself+checkpoint)` |
| `call_terminal_checkpoint` | `ART(call-terminal-checkpoint-v1,[H(manifest FileIdentity),H(premanifest FileIdentity),H(postmanifest FileIdentity),H(call-directory preclose identity),I(0555),H(writer-held),H(process-closure),S(kind),B(seal_commit)])` |
| `call_directory_seal_closeout` | `ART(call-directory-seal-closeout-v1,[H(bundle),S(gate),S(operation),I(call),H(session),H(checkpoint FileIdentity),H(preclose DirectoryIdentity),H(postclose DirectoryIdentity),I(0555),B(dir_fsync),B(parent_fsync),B(lock_held),I(0),S(status)])` |
| `ordered_call_terminal_chain` | for call `k`, `DER("ordered-call-terminal-chain-v1",[H(prior_chain) or N,I(k),H(call_manifest_authority),H(call_checkpoint_file_identity),H(call_directory_seal_closeout),H(postclose_call_directory_identity)])` |
| `operation_premanifest_inventory` | `DER("operation-premanifest-inventory-v1", exact ordered root-authority and sealed-call checkpoint FileIdentity rows)` |
| `operation_terminal_manifest` | `ART(operation-terminal-manifest-v1, OperationRootPrefix plus every exact tagged Section-8.12 field)` |
| `operation_postmanifest_inventory` | `DER("operation-postmanifest-precheckpoint-inventory-v1", exact ordered FileIdentity rows including operation premanifest+manifest and excluding itself+root checkpoint)` |
| `writer_held_closure` | `ART(writer-held-closure-v1, exact tagged stable-lock owner/contender/hold-policy fields observed before checkpoint)` |
| `root_terminal_checkpoint` | `ART(root-terminal-checkpoint-v1, OperationRootPrefix plus every exact tagged Section-8.13 field)` |
| `writer_release_closeout` | `ART(writer-release-closeout-v1,[H(bundle),S(gate),S(operation),H(dispatch-consumption),H(root-checkpoint FileIdentity),H(lock FileIdentity),I(pid),I(sid),I(pgid),B(released),I(0555),H(closed-root DirectoryIdentity),I(active_writers),I(related_processes),S(observer),S(status)])` |

The compiler rejects cycles, missing nodes, ambiguous producers, duplicate
edges, and any node that reads its own or a descendant's digest.  Timestamps,
filenames not derived from the path grammar, and manifest self-reports never
enter chain authority.

## 10. Operation plans and finite state machine

### 10.1 Actor and barrier profiles

For each call, frame, event, prefix, and child-frame sequences begin at zero.
They are monotone across stages and reset only at a new call.  The next call
may open only from the preceding call's successful terminal manifest.

Compatibility:

- P00 parent-only prelaunch;
- P01--P07 child observation predicates;
- P08--P14 each use one child control-barrier request followed by parent fixture
  events with exact logical counts `11,11,7,6,4,8,16`;
- P15--P16 child observation predicates;
- P17 parent-only post-reap;
- no Paclet, source load, public scientific API, boundary solve, overlap, AP,
  or radial call.

Micro, sentinel, and official:

- P00 parent-only;
- P01--P09 child observation predicates;
- P10 source-start barrier: one generated request predicate plus 66 parent
  observations, total 67;
- P11--P13 child observation predicates;
- P14 source-end barrier: one request plus 67 parent observations, total 68;
- P15--P16 child observation predicates;
- P17 parent-only.

The source-load micro authorizes no solver/public-API call and has an explicit
pre-solver exit predicate.  Sentinel and official use the frozen 35- and
161-call plans respectively.  A barrier frame is transport control, not an
extra logical predicate except where the generated production profile assigns
the request predicate explicitly.

### 10.2 Valid progression

```text
parent seals seed
  -> parent commits five P00 events/prefixes
  -> parent commits final0 and open1
  -> one Popen
  -> receive raw child frame
  -> validate against bundle and prior authority
  -> parent constructs event
  -> commit event and prefix
  -> if nonfinal: durable EVENT ACK
  -> if stage final: commit final and next open, then durable STAGE_FINAL ACK
  -> for barrier: commit all finite parent observations/final/open,
     then one durable PARENT_BARRIER_FINAL ACK
  -> final P16 frame/event/prefix/final16
  -> commit child-exit authority
  -> durable CHILD_EXIT ACK
  -> child flush/EOF/exit
  -> parent wait/reap/process-group closure and durable receipt
  -> commit open17
  -> eight parent P17 events/prefixes/final17
  -> P17 closure
  -> terminal manifest and external terminal checkpoint
```

There is no wait cycle: after a frame, every input needed for its ACK is
available without waiting for another frame.  An ACK is never sent before all
artifacts it names are fsynced and reloaded.  Stage17 has no child frame or
ACK.

### 10.3 Failure and interruption

Any schema, type, identity, source, comparison, sequence, publication,
timeout, process, path, or resource error prevents an advancing ACK.  Under a
stable parent writer lock, the controller commits the first blocker, raw
offending bytes, and last authenticated authorities; then performs exact
terminate -> bounded wait -> kill-if-needed -> wait/reap -> PG-empty closure,
publishes the true lifecycle receipt and the matching failure-union manifest,
and closes the root immutable.  Missing normal stages are not synthesized.

A scientific or protocol failure consumes its dispatch/root and is not
resumable.  V3.1-Z v1 also authorizes no system-interruption resume: an
interrupted partial root remains immutable diagnostic evidence and the gate
ESCALATES to Root T0.  No new dispatch, alternate attempt, same-root append,
retry, or resume controller is part of this namespace.  A later resume design
would require a distinct gate/package/review and cannot be inferred here.

## 11. Generated conformance and mutation authority

The spec is the sole source of vector and mutation semantics.  Its exact row
schemas are:

```text
conformance_vector_registry row =
  [vector_id, vector_plan_id, vector_ordinal, scope_id,
   initial_authority_fixture_ids, operation_or_schema_id,
   typed_input_values, expected_encoded_bytes,
   expected_artifact_or_wire_sha256,
   expected_disposition, expected_reason_code,
   expected_terminal_state, expected_science_counters]

conformance_vector_plan row =
  [vector_plan_id, expansion_axis_ids, expansion_axis_values,
   expansion_order, fixture_constructor_id,
   expected_constructor_id, required_coverage_ids]

mutation_operator_registry row =
  [operator_id, applicable_target_kinds, applicable_type_ids,
   parameter_schema_id, exact_transform_algorithm_id,
   output_canonicality, default_disposition,
   default_reason_code, earliest_rejection_state]

mutation_plan row =
  [mutation_plan_id, source_vector_selector_id,
   target_selector_id, ordered_operator_ids,
   parameter_expansion_values, rehash_descendants,
   expected_disposition_override_or_null,
   expected_reason_override_or_null]
```

The closed mutation algorithms are literal byte/row transformations, not
function names supplied by T6:

```text
DELETE_FIELD_OR_POSITION(index)
INSERT_UNKNOWN_FIELD_OR_POSITION(index, typed_value)
DUPLICATE_JSON_MEMBER(raw_member_bytes)
REPLACE_TAG(index, replacement_tag)
REPLACE_VALUE(index, canonical_typed_value)
TOGGLE_NULL(index)
REPLACE_ENUM_WITH_LITERAL(index, outsider)
REPLACE_INTEGER_WITH_BOUNDARY(index, {-1,0,max,max+1})
REPLACE_HASH(index, {short,uppercase,nonhex,wrong64})
REPLACE_DECIMAL(index, {nan,inf,negzero,noncanonical_exp,wrong_value})
SWAP_ADJACENT_POSITIONS(left_index)
DELETE_ROW(global_ordinal)
DUPLICATE_ROW(global_ordinal)
MOVE_ROW(source_ordinal,target_ordinal)
TRUNCATE_BYTES(byte_offset)
APPEND_BYTES(exact_suffix)
APPEND_EXTRA_LF
PAD_TO_OVERSIZE(exact_target_size)
REPLACE_EDGE_SOURCE(edge_id, foreign_authority_sha256)
REPLAY_FROM_SESSION(source_session,target_session)
RECOMPUTE_DECLARED_DESCENDANT_HASHES
```

Each transform operates on the vector's stored exact raw bytes or ordered
typed row, with zero-based positions and no parser-dependent normalization.
Its parameter domain is a literal ordered array in the spec.  For compound
attacks, transforms apply left to right.  `RECOMPUTE_DECLARED_DESCENDANT_HASHES`
uses the generated DAG and recomputes every mutable descendant, but cannot
change the frozen bundle root, generated row digest, or immutable predecessor.

Every `exact_transform_algorithm_id` resolves to an `algorithm_registry` row
of kind `MUTATION_BYTE_TRANSFORM` or `MUTATION_TYPED_ROW_TRANSFORM`, whose
literal typed AST implements exactly one transformation above.  Every source
and target selector resolves to a `selector_registry` row; its closed selector
AST may use only `CATALOG, FIELD, EQ, AND, OR, NOT, RANGE, ORDERED_PROJECT`
and must return rows in catalog/global-ordinal order.  It cannot run candidate
code, inspect a filesystem, glob, sort, sample, or infer a target from a
failure.  Selector result cardinality is independently evaluated from its
frozen expression before mutation expansion.  Thus neither generator nor T6
may invent fixture selection or transform semantics.

Expansion order is exact: conformance plan declaration -> plan axes row-major;
then source vector order -> target schema/edge declaration order -> field
order -> mutation-operator declaration order -> parameter order ->
`rehash_descendants=false,true` where applicable.  Mutation IDs include all
these ordinals.  The spec contains at least one small hand-authored bootstrap
vector for each scalar tag, each primary and nested schema, P00, normal exit,
failure termination, P17, and terminal sealing, including literal encoded
bytes and hashes.  The compiler may expand those seeds but may not author
their expected bytes.  Missing bootstrap bytes, an unconsumed field/edge, or a
mutation without one unique disposition is a package-generation failure.

### 11.1 Positive vectors

Package-time vectors must include, with literal expected bytes and digests:

- minimum, maximum, and every nullable branch of every primary/nested schema;
- every enum/type/comparison family;
- a complete compatibility traversal;
- a complete synthetic single-call production traversal;
- P00 seed -> first event -> first prefix -> final0 -> open1;
- P16 -> child exit -> ACK -> receipt -> open17 -> P17 -> terminal;
- a two-call linkage where call 1's successful terminal binds call 2's seed;
- every operation-specific barrier actor plan; and
- success plus each terminal failure union.

All science-shaped values are synthetic tagged literals and every science
counter is zero.

### 11.2 Mutation oracle

Each mutation recipe is an ordered row:

```text
[
  mutation_id,
  target_vector_id,
  target_schema_or_edge_id,
  target_field_or_edge,
  operator_id,
  mutation_parameters,
  mutated_bytes_sha256,
  expected_disposition,
  reason_code,
  earliest_rejection_state,
  rehash_descendants
]
```

`expected_disposition` is exactly one of:

- `REJECT_BEFORE_STATE_CHANGE`;
- `ACCEPT_OBSERVATION_THEN_TERMINAL_FAIL`; or
- `ACCEPT_AND_ADVANCE`, reserved for positive vectors.

The generated oracle must cover, exhaustively and without sampling:

- every schema field: missing, extra, duplicate, wrong type, bool-as-int,
  null toggle, out-of-domain enum/integer/string/hash/decimal, order change,
  NaN/Infinity, noncanonical Unicode/number/exponent, truncation, extra LF,
  extra stdout, and oversize;
- every expanded predicate: owner, observer, executor, field, value type,
  comparison, expected literal/expression, evidence order/path/identity, and
  science-capable flag;
- every DAG edge: missing, duplicate, gap, reorder, reset-at-stage,
  cross-stage/call/operation/session replay, wrong prior event/prefix/final/open,
  ACK-before-fsync, final-without-complete inventory, open-without-final,
  P17-before-reap, and terminal-before-closure;
- P00 seed substitution, receipt process/stream mutation, every P17 evidence
  omission, and terminal inventory/prior-call mutation;
- crash points immediately before and after frame, event, prefix, final, open,
  ACK file/ACK send, child exit, EOF, receipt, each P17 event, P17 closure,
  manifest, and external checkpoint;
- filesystem alias/symlink/hardlink, wrong mode/nlink/inode, unknown path,
  post-close write, and same-byte replacement; and
- an attacker recomputing the mutated file and every descendant self-reported
  hash.  Independent rebuilding from the immutable bundle and prior edge must
  still reject it.

The oracle is stored as bounded fixed-size shards plus an exact expansion
index and Merkle-style ordered shard digest.  Mutated artifact bytes need not
all be stored, but each recipe's output bytes/digest must be uniquely
reconstructible.  No recipe may be silently skipped because of resource cost.

### 11.3 No implementation-generated answers

The package compiler may emit expected vectors because it is a frozen
pre-implementation authority.  Future T6 runtime and tests may only consume
them.  Formal T7 must independently implement the declarative expansion and
canonical codecs from the spec, without importing:

- the candidate generator;
- generated Python/WL validators;
- T6 runtime code; or
- candidate mutation application code.

It must reproduce the complete generated leaf inventory, bundle root,
predicate rows, schema catalog, DAGs, vectors, and mutation dispositions
byte-for-byte.  A candidate validator passing vectors it generated itself is
not package acceptance.

## 12. Python/Wolfram parity before science

The generated Python and WL adapters must first process the package vectors
and produce byte-identical tagged arrays, hashes, and rejection reason codes.
A distinct one-use real-kernel compatibility run then checks JSON duplicate
handling, tagged types, arbitrary-precision decimals, Unicode, path grammar,
frame/ACK dialogue, raw-stream purity, timeouts, wait/reap/PG closure, and
failure windows, with every scientific counter zero.

Only a formal T7 `ADVANCE` review of that compatibility root may authorize a
separate source-load micro.  The micro loads and independently verifies the
exact Wolfram runtime and BHPT source closure, but exits before any
ReggeWheeler public API, boundary solve, overlap, MST, AP, radial, or other
science-capable call.  Only its formal T7 `ADVANCE` may authorize the distinct
35-call sentinel.  No target-language normalization, fallback parser,
Association key order, Python dict order, or implementation-selected
comparison is permitted.

The compatibility executable is exactly the generated, package-frozen
`generated/phase6_v3_1_z/compatibility_observer.wls`.  Static call-graph and
runtime counters must prove it cannot import the BHPT snapshot or call a
scientific API.  It is not the future science-capable
`scripts/phase6_v3_1_z_raw_observer.wls`.  The latter is first exercised by the
source-load micro under an operation flag and generated DAG that exits before
its sole science-capable branch; sentinel/official are the only operations
allowed to cross that branch after their prior formal reviews.  No argv or
environment value may select one executable or operation profile in place of
another.

## 13. Shared components and authority isolation

### 13.1 Allowed trusted components

The package compiler and authority runtime may share only predeclared,
identity-bound infrastructure:

- CPython 3.14 standard-library duplicate-rejecting JSON and SHA-256;
- generated tagged codecs and schema rows;
- POSIX `O_EXCL`, `O_NOFOLLOW`, `flock`, `fsync`, stat/reopen/rehash,
  process wait/reap and process-group observation; and
- the exact Wolfram runtime as a raw-observation producer after compatibility
  acceptance.

No authority-generation component may import the radial solver, BHPT science
package, AP oracle, Route A/U/B/C producer, scientific comparator, or prior
evidence reader.

### 13.2 Reviewed pure scientific helpers

No scientific helper is authorized by this design-only turn.  A future package
may freeze the following exact candidate allowlist, and no other shared
science component, after independently closing each transitive dependency:

| Candidate path | Current SHA-256 | Permitted future role |
|---|---|---|
| `src/schwgw/validation/phase6_v3_external_direct.py` | `981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4` | Route-C observation geometry only: `exact_frequency_fraction`, `outer_radius`, `overlap_radii`; its plan, publication, validation, budget, and PASS functions are not authority inputs. |
| `src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py` | `a6d88685223fddb8c37f8fdd1110c4400252a6e8f30ffebaab1d6eb4dea85be7` | Route-U independent high-precision observation producer only. |
| `src/schwgw/validation/phase6_mpmath_radial.py` | `bb92fea624f01df347b0f3c5537bfd8be0319c0eb1d4302e9b81a26bef473c80` | Transitive numerical dependency of the Route-U observation producer only. |
| the seven protected radial sources in Section 2.3 | exact hashes in Section 2.3 | Frozen Route-A/Route-B numerical observation sources only; never authority generation. |

The current control-plane CLI
`scripts/phase6_v3_1_hp_unitarity.py`
(`01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4`)
and prior U/X/Y producer/controller code are explicitly not reusable authority
components.  A future package must bind the exact project-local mpmath overlay
tree and every imported source at start/end; the module hashes above alone are
not a complete dependency closure.

Future operation adapters may call an accepted allowlisted helper only after
all pre-science authority stages are committed.  Its role is exactly
`OBSERVATION_PRODUCER`.  It may not:

- expand predicates or paths;
- choose expected values or comparisons;
- construct digest inputs;
- select a route from predecessor data;
- decide PASS/FAIL/terminal status; or
- read failed/sentinel outputs as science input.

The Route-U selector is a source-bound pure observation over the fresh
complete Route-A direct `log_Gamma_flux` vector.  It remains dynamic and
ordered.  Any shared helper and all transitive dependencies must be declared
in the spec's immutable-input registry and source start/end ledgers.

## 14. Future implementation and formal review scope

### 14.1 Exact future T6-editable paths

If Root T0 later freezes GMA-Z1, the recommended exact-six implementation
scope is:

```text
scripts/phase6_v3_1_z_raw_observer.wls
src/schwgw/validation/phase6_v3_1_z_authority_runtime.py
src/schwgw/validation/phase6_v3_1_z_external_route.py
scripts/phase6_v3_1_z_external_protocol.py
tests/unit/test_phase6_v3_1_z_authority_runtime.py
tests/regression/test_phase6_v3_1_z_authority_publication.py
```

Generated package outputs and scientific/protected sources are read-only.
Any seventh implementation path, core physics edit, generated-authority edit,
threshold/domain/convention change, or fallback requires a new package review.

### 14.2 Exact future prompt family

Root T0 should predeclare distinct paths for:

```text
docs/prompts/phase6_t6_v3_1_z_generated_machine_authority_implementation.md
docs/prompts/phase6_t7_v3_1_z_generated_machine_authority_package_review.md
docs/prompts/phase6_t7_v3_1_z_generated_machine_authority_implementation_review.md
docs/prompts/phase6_t7_v3_1_z_wolfram_compatibility_review.md
docs/prompts/phase6_t7_v3_1_z_source_load_micro_review.md
docs/prompts/phase6_t7_v3_1_z_full_sentinel_review.md
docs/prompts/phase6_t7_v3_1_z_science_review.md
```

This analysis does not create or authorize any of them.

### 14.3 Literal future archive, dispatch, and root namespaces

To eliminate `latest`/glob/current-handoff authority, the proposed initial Z
package must predeclare these exact archive paths, all absent before their
respective review:

```text
docs/handoffs/archive/T7_2026-08-14_v3_1_z_generated_machine_authority_package_review.md
docs/handoffs/archive/T7_2026-08-14_v3_1_z_generated_machine_authority_implementation_review.md
docs/handoffs/archive/T7_2026-08-14_v3_1_z_wolfram_compatibility_review.md
docs/handoffs/archive/T7_2026-08-14_v3_1_z_source_load_micro_review.md
docs/handoffs/archive/T7_2026-08-14_v3_1_z_full_sentinel_review.md
docs/handoffs/archive/T7_2026-08-14_v3_1_z_scientific_review.md
```

Candidate bytes contain paths but no future review SHA.  A later one-use
dispatch supplies the freshly observed regular-file/mode/nlink/SHA identity
and requires exactly one top-level verdict envelope.  The expected advance
labels are, respectively:

```text
ACCEPT GREEN / V3.1-Z GENERATED MACHINE-AUTHORITY PACKAGE READY FOR T6
ACCEPT GREEN / V3.1-Z IMPLEMENTATION READY FOR COMPATIBILITY DISPATCH
ACCEPT GREEN / V3.1-Z WOLFRAM COMPATIBILITY PASSED
ACCEPT GREEN / V3.1-Z SOURCE-LOAD MICRO PASSED
ACCEPT GREEN / V3.1-Z FULL SENTINEL PASSED
<formal T7 scientific verdict; never pre-assumed by candidate bytes>
```

The first five also require `ADVANCE_DECISION: ADVANCE` and
`CLAIM_STATUS: NOT_ASSESSED`.  The science review's claim status is determined
only after complete evidence and is not hardcoded as an acceptance input.

Exact one-use dispatch paths are:

```text
docs/handoffs/archive/T0_2026-08-14_v3_1_z_implementation_dispatch_attempt_0001.json
docs/handoffs/archive/T0_2026-08-14_v3_1_z_wolfram_compatibility_dispatch_attempt_0001.json
docs/handoffs/archive/T0_2026-08-14_v3_1_z_source_load_micro_dispatch_attempt_0001.json
docs/handoffs/archive/T0_2026-08-14_v3_1_z_full_sentinel_dispatch_attempt_0001.json
docs/handoffs/archive/T0_2026-08-14_v3_1_z_official_dispatch_attempt_0001.json
```

No alternate attempt, fallback, basename suffix, environment-selected path,
or predecessor dispatch is accepted.  The executable root parent is exactly:

```text
/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/runs/phase6/classic_scattering
```

Each root must resolve as a fresh, non-symlink direct child and match exactly
one basename grammar, with a valid UTC timestamp:

```text
^v3_1_z_wolfram_compatibility_v1_[0-9]{8}T[0-9]{6}Z_py314$
^v3_1_z_source_load_micro_v1_[0-9]{8}T[0-9]{6}Z_py314$
^v3_1_z_full_sentinel_v1_[0-9]{8}T[0-9]{6}Z_py314$
^v3_1_z_official_v1_[0-9]{8}T[0-9]{6}Z_py314$
```

The timestamp is parsed and round-tripped as UTC but never determines
authority order.  Dispatch payload root, resolved root, run contract, seed,
and terminal manifest must all be byte-identical on the root string and
identity.  Package/implementation review files and implementation dispatch do
not create a science root.

## 15. Non-circular authority progression

The only recommended progression is:

1. Root T0 freezes spec, generator, generated bundle, package, design, and a
   T7 initial package-review prompt.  The future review path is literal; its
   digest is not embedded in candidate bytes.
2. Formal T7 independently recompiles the spec in a temporary tree, verifies
   the complete bundle and mutation oracle, and publishes one immutable review.
3. A later one-use T0 implementation dispatch supplies that review's observed
   path/SHA/verdict plus current package and bundle roots.
4. T6 implements only the exact-six paths and produces zero-science temp
   evidence; formal T7 independently reviews it.
5. Separate one-use dispatch/root/review triples follow, in order:
   compatibility -> review -> source-load micro -> review -> 35-call sentinel
   -> review -> fresh official -> scientific review.
6. Each dispatch is O_EXCL-consumed before the first child or science-capable
   call, binds the exact prior review, code, bundle, root, argv, cwd,
   requested/observed environment, runtime, source start, and one-use attempt.
7. Every failure root is immutable and non-reusable.  Sentinel values cannot
   enter official science.  A later review digest is supplied only after that
   archive exists; no package or implementation hardcodes its own future
   approval.

V3.1-Z v1 deliberately authorizes zero bounded repair cycles at every node in
this graph.  Formal `REPAIR`, `FAIL`, `ESCALATE`, a missing review, or any
non-ADVANCE token therefore consumes/blocks that node and returns to Root T0
for a distinct-gate adjudication; it cannot create a `_delta_review_1`,
`_delta_review_2`, alternate dispatch, or retry root.  This makes the literal
review paths above complete and prevents the authority-path collision that
ended V3.1-Y.  A future package may not silently raise this zero-repair limit.

An initial package review cannot be replaced by a quoted token, current
handoff, glob, latest-file selection, environment variable, alternate path,
or predecessor Y review.

## 16. Resource projection and hard stops

There is no measured Z generator or runtime, so no empirical resource claim is
made.  The deterministic lower bound is 80,724 predicate rows plus thirteen
primary schemas, nested schemas, four operation DAGs, vectors, and mutation
recipes.  For planning only:

- at 0.8--2.5 KiB per expanded predicate row, predicate shards alone are
  approximately 65--202 MiB;
- a fully materialized field-by-field mutation corpus could reach millions of
  cases and multiple GiB, so the package must store canonical recipes plus an
  exact expansion index rather than omit cases or store every mutated blob;
- official control evidence may contain over 65,000 semantic events plus
  frames, ACKs, prefixes, stage artifacts, and raw streams; its exact byte/file
  projection must be generated from the frozen path grammar before dispatch.

Proposed package control limits, subject to formal review, are:

```text
two independent package generations: byte-identical
each package generation wall: <= 10 minutes
peak RSS: <= 4 GiB
generated bundle bytes: <= 2 GiB
mutation expansion: 100% of declared recipes, no sampling
compatibility and source-load micro: <= 120 s and <= 16 MiB whole root each;
individual stdout/stderr limits must be stricter generated sublimits whose sum
plus all authority artifacts remains within that whole-root cap
official science ceiling: unchanged <= 36 h
for each executable operation in {compatibility,micro,sentinel,official}:
  projected_root_bytes <= floor(currently free workspace bytes / 4)
  and currently free workspace bytes >= 4 * projected_root_bytes
full-sentinel safety ceiling: <= 8 h wall, <= 8 GiB peak RSS
official safety ceiling: <= 36 h wall, <= 8 GiB peak RSS
```

No unlisted smoke or resource-calibration operation exists.  Sentinel
admission uses package-generated deterministic storage bounds, not an
empirical science prediction:

```text
projected_root_bytes(operation) =
  exact generated fixed-authority bytes
  + sum_over_calls(frame_max_bytes * declared_frame_count
                   + ack_max_bytes * declared_ack_count
                   + raw_stdout_limit + raw_stderr_limit
                   + sum_over_output_schemas(max_encoded_record_bytes
                                             * declared_record_count))
```

Every term comes from the generated schema/path/call graph; no margin,
sampling, compression assumption, or predecessor timing enters it.  The
fixed 8-hour/8-GiB sentinel ceilings are governance safety limits proposed to
the package review, not claims about expected runtime.  The formal sentinel
review is the sole declared empirical predecessor for official resource
admission: a later official dispatch must bind its terminal resource record
and the same static byte formula, while retaining—not relaxing—the independent
36-hour/8-GiB official ceiling.  If T7 cannot approve that projection after
the sentinel, official remains unlaunched and the gate ESCALATES.  This makes
the sentinel reachable without inventing a hidden smoke and prevents its
measurements from becoming scientific values or reusable output.

These are control-plane caps, not scientific thresholds.  A zero-science
package-generation measurement must replace the planning range with exact
wall/RSS/file/byte/shard counts before package freeze.  Exceeding a cap is a
STOP requiring Root-T0 redesign/review; it does not permit sampling, sharding
changes after review, case deletion, compressed-only evidence, or silent
resource relaxation.

Absolute stop conditions for all later stages include:

- spec/generator/generated inventory mismatch or nondeterminism;
- independent T7 recompilation mismatch;
- profile/count/Route-U/threshold/certificate/source/protected drift;
- unknown predicate/schema/type/comparison/evidence/digest/path node;
- Python/WL vector or reason-code mismatch;
- bundle/path alias, symlink, hardlink, mode/nlink/source drift;
- compatibility, micro, sentinel, process closure, or source-end failure;
- resource-cap failure;
- need to change science, domain, threshold, precision, method, convention, or
  a protected source; or
- any request to reuse predecessor or sentinel values.

## 17. Hostile failure modes addressed

Beyond the explicit terminal-Y blocker, GMA-Z1 must test at least these same-
surface risks:

1. **Common-mode compiler bug.** Candidate generator and generated validators
   may agree incorrectly.  Mitigation: source-distinct T7 recompiler,
   hand-readable expanded rows, literal bootstrap vectors, and byte identity.
2. **Cross-call replay.** A complete call-0 transcript can be moved to call 1
   if call ordinal/plan/prior terminal are not in every authority.  Mitigation:
   common session prefix and next-call seed binding.
3. **Generated-code injection.** An expected expression could smuggle arbitrary
   Python/WL execution.  Mitigation: closed typed AST, no callbacks/imports,
   static generated-code audit, and science-capable flags.
4. **Manifest circularity or self-certification.** A recomputed manifest can
   attest to itself.  Mitigation: leaf inventory excludes manifest/root;
   external terminal checkpoint commits the manifest.
5. **Association/dict order and Unicode/path drift.** Mitigation: ordered arrays,
   tagged values, explicit UTF-8/Unicode/path grammar, real-kernel parity.
6. **ACK crash ambiguity.** Parent may crash after fsync but before send, or
   after send but before the next frame.  Mitigation: durable ACK identity and
   next frame binding to ACK/open/prefix; no inferred delivery.
7. **Barrier deadlock.** Parent may wait for a child fact that waits for ACK.
   Mitigation: generated finite actor plan and rank-monotone DAG; barrier ACK
   requires only already available parent observations.
8. **Raw-stream contamination.** Package messages or diagnostics can masquerade
   as frames.  Mitigation: exact framed grammar, byte offsets, separate stderr,
   size limit, and rejection of every unframed byte.
9. **Same-byte file replacement/alias.** Hash equality alone can hide identity
   drift.  Mitigation: no-follow reopen/restat, path/dev/inode/mode/nlink/size/
   hash, start/end equality, and alias graph.
10. **Failure-path false PASS.** A partial stage can be reconstructed as a
    normal final after a crash.  Mitigation: typed failure union, last
    authenticated edge, real process receipt, no fabricated P17, and no
    advancing ACK after first failure.
11. **Mutation-oracle self-fulfilment.** Runtime may implement the same wrong
    rule that authored its tests.  Mitigation: package-time oracle plus
    independent T7 recompiler; runtime produces no expected answer.
12. **Route selection contamination.** An observed predecessor `N_U=318` may
    be hardcoded.  Mitigation: fresh complete Route A, exact 496 ordered direct
    values, generated selector predicate, dynamic bounds, explicit denylist.

## 18. Limitations and unresolved risks

1. Independent recompilation reduces but cannot mathematically eliminate a
   common conceptual error in the human-authored spec.
2. Actual generated bundle size, mutation count, and generation time remain
   unknown until a zero-science package compiler exists and is reviewed.
3. Python/WL decimal, Unicode, path, and stream parity still requires a real
   zero-science compatibility run; static generation cannot prove it.
4. POSIX/APFS atomicity, `fsync`, `flock`, process observation, and SHA-256 are
   trusted infrastructure assumptions, not scientific results.
5. The external SSD and exact Wolfram runtime may become unavailable or drift;
   that is a control/runtime blocker, never a scientific failure or fallback
   authorization.
6. Generated authority proves protocol conformance, not correctness of the
   black-hole perturbation calculation.  The exact scientific thresholds and
   independent review remain necessary.
7. External evidence remains odd-only; even parity has no independent external
   solve.  Common absolute phase remains PARTIAL.
8. A formal FSM model can strengthen deadlock/crash assurance but should remain
   secondary until its toolchain and concrete-byte refinement are separately
   frozen.
9. A future resume controller is not designed here.  It cannot be inferred
   from failure handling and must undergo a separate package/review if needed.

## 19. Proof of architectural discontinuity

V3.1-Y's package fixed predicate names, counts, and a high-level wire graph,
but left each predicate's semantic row and terminal authority to the runtime.
GMA-Z1 instead requires, before implementation:

- one complete typed source;
- deterministic full expansion;
- generated exact semantic rows;
- generated complete artifact schemas and digest DAG;
- generated conformance bytes and mutation dispositions;
- independent recompilation by T7; and
- an observation-only child with parent decisions constrained by the frozen
  bundle.

The namespace, spec, bundle, generator, implementation paths, dispatches,
roots, reviews, and terminal artifacts are all new.  Every Y/U/X runtime,
science value, control artifact, executable dispatch, and candidate root is
nonpromotable; immutable reviews and Root-T0 adjudications remain read-only
threat-model authorities.  Scientific scope is preserved rather than narrowed.  Therefore
this is a new gate algorithm, not V3.1-Y repair cycle 3.

## 20. End-state and nonclaims

### 20.1 End-gate identity closure

Immediately before publication, every immutable authority and source in
Section 2 was reopened and rehashed.  The end identities equal the recorded
start identities.  The end-gate coordination snapshot (read-only and not an
authority substitute) is:

| Path | End SHA-256 |
|---|---|
| `project.md` | `fdba5646eb0d9bb0776ea6148e509d91124871cf371ac08a7229b10e18b63b9a` |
| `status.md` | `3a63b18f1a56a7a7cb41351f34ccdb04870358b1881634e00f24a7b1178d4ad1` |
| `docs/handoffs/T0_current.md` | `297adae85c4d1973ddaa1d267d3a486f9d975506d738b190ce58a3cd7551d1d0` |
| `docs/handoffs/T4_current.md` | `012da075c1cbd9b35d6d7776a330c67f804e40ae67cefa7a4557d2085a1f029e` |
| `docs/handoffs/T7_current.md` | `8bbf1d045f3aba93d9b8b89a8c459c25567e04112fbea6c7566dbe0eb9b586bb` |

The decisive formal/control sources close start=end:

| Role | End SHA-256 |
|---|---|
| exact Z prompt | `6a7a6ecfe6d06be1630a9b9df3c266138c30b5e3bd4de4a2783c748da6b07d14` |
| liveness protocol | `3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181` |
| Root-T0 final Y adjudication | `6b5d126565ab4f8764d65825c37589e37f52f2576d25593239c028ee1608c3f4` |
| formal T7 Y delta-2 | `0ad54e21f62d233e6c26720918c85ac6dfdb12f254f02d6169ed4af348df9dd4` |
| terminal Y package / contract | `5dc0b062c7da463bb3aa4283b38060201c8d6fd7a6902dd0d677273306b9d0b7` / `c3d601940b8f297eb23cccad404c8ec5c326ffc6fb9a1dfa005ec6f5db3ef45c` |
| V3.0 domain / thresholds / anchors | `803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b` / `91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a` / `06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485` |
| V3.0 validation / formula / phase / literature | `0f8b8c96e01321231377c857ab40d710aa80ac06dce9084029fe2914b1ef37d3` / `e5b556667c28ac8b611430d2dfb4faa5da82b9c7f0c8251251029e3f8c8d0eac` / `fb91f4cf888dd4984174304783875c9f2e591490df8519bafd2e0b0f73053460` / `088834348e980b81f814340a2a2c460b5bf11239521085c358bed7a90f603328` |
| V3 convention | `82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a` |

Runtime/external/protected source closure is likewise exact:

| Source | End identity |
|---|---|
| WolframKernel (not executed) | SHA `70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c`; mode `0755`; nlink `1`; size `167488` |
| BHPT snapshot metadata | `8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488` |
| BHPT content / restored identity inventories | `d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2` / `a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27` |
| BHPT restored tree | 25/25 regular mode-`0444` nlink-1 files rehashed exact; 5/5 mode-`0555` directories; zero symlinks |
| `radial_solver.py` | `9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9` |
| `conditioned_radial.py` | `91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2` |
| `scaled_tortoise_radial.py` | `d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df` |
| `adaptive_jost_radial.py` | `3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896` |
| `matching.py` | `9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340` |
| `physical_boundary_radial.py` | `fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f` |
| `boundary_conditions.py` | `b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22` |

The end process scan found zero related writers and zero Wolfram/BHPT/AP/
radial/solver/science processes.  The exact stop counters are:

```text
Wolfram launches = 0
BHPT/AP/radial/solver/science calls = 0
dispatch/root created = 0
implementation paths created or modified = 0
V3.2 started = false
```

This analysis created only itself and the separately named T4 archive.  It did
not create a package, generator, config, prompt, implementation path,
dispatch, root, compatibility run, source-load micro, sentinel, or official
science artifact.  It did not execute WolframKernel, BHPT, AP, radial, or any
solver.  It did not modify status or current handoffs and did not contact T7.

V3.1-Z remains design-only and `NOT_ASSESSED`.  Formal package construction,
package review, implementation, compatibility, micro, sentinel, official
science, V3.2, and global GREEN all require separate future authority.

CHECKPOINT / V3.1-Z GENERATED MACHINE-AUTHORITY REDESIGN READY FOR ROOT T0
