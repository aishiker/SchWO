# SchWO Phase 6 V3.1 全版本错误与缺陷报告

日期：2026-08-14（Asia/Shanghai）  
范围：V3.1 base、V3.1-U、V3.1-X、V3.1-Y、V3.1-Z  
状态：用户于 V3.1-Z 初次正式 T7 package review 期间手动停止本链；自动 heartbeat 已删除。

## 1. 结论摘要

V3.1 没有形成可接受的科学 release，也没有授权 V3.2。整个分支经历了五种不同性质的问题：

1. **真实的数值或科学不闭合**：base 的首个 Route-A 节点无法稳定求解；修复后首个模式又以 74.359 倍超出冻结的 log-Gamma route threshold。V3.1-U 的最终 23-anchor MST sentinel 只有 14 PASS、9 MST_FAILED。
2. **外部运行接口缺陷**：Wolfram `$ScriptCommandLine`/`$CommandLine` 使用错误、Python/WLS 对同一 source ledger 使用不同 key 顺序、真实进程环境包含未建模的 macOS/CPython 注入项。
3. **持久化与恢复协议缺陷**：writer lock、authority publication、prepared/append/checkpoint/commit、第二次中断恢复和增量 validator 未形成可独立重建的闭包。
4. **证据与 provenance 缺陷**：失败分支未保存 exact failed key、stdout/stderr、WLS/kernel/BHPT source identity；loaded-source closure、precision witness、dispatch authority 与 sentinel admission 曾出现 false acceptance。
5. **governance/spec 过度复杂且不自洽**：Y/Z 试图用越来越大的 machine-authority 协议消除实现自由度，但 schema、predicate-value semantics、P00/P17/lifecycle/terminal binding 仍不完备；Z 又出现 declarative spec 与生成 validator 的 decimal grammar 冲突，以及生成语义仍藏在 generator 源码中的问题。

关键判断：V3.1 的反复失败并非单一 solver bug。根本问题是把科学算法、外部 runtime、一次性 dispatch、可恢复 publication、形式化 authority 和独立审查同时放进一个不可逆 gate，而 exact production path 没有先通过足够贴近真实运行的、低成本、可重复 preflight。

## 2. 术语与证据边界

- **科学失败**：冻结的数值/物理 acceptance criterion 被真实数据违反，或冻结方法不能覆盖冻结域。
- **实现失败**：代码不能实现已经冻结的 contract，但不等价于物理结论错误。
- **control-plane 缺陷**：路径、manifest、dispatch、lock、环境、permission、handoff、review authority 等控制面错误。
- **provenance 缺陷**：无法独立确定实际执行了哪些 bytes、输入、外部模块或失败节点。
- **NOT_ASSESSED**：没有形成足够证据，不能解释为 PASS 或 FAIL。

本报告以仓库内 T4/T7 archives、冻结 packages/designs/prompts、失败 roots 和当前 source/tests 为依据。V3.1-Z 的 T7 turn 被用户中断，未发布正式 archive，因此 Z 的两项问题只能标为“正式 T7 hostile review 的可复现 preliminary findings”，不能冒充完成的双轴 verdict。

## 3. 总时间线

| 分支 | 阶段 | 主要结果 | 性质 | 终态 |
|---|---|---|---|---|
| V3.1 base | 初始运行 | 首个 Route-A 节点 singular Jacobian；fallback non-monotonic grid；runner 仅硬编码单节点；JSONL 实为 multiline JSON | 数值 + 实现 + publication | REPAIR / FAIL |
| V3.1 base | repair 1 | 20-node sentinel 8 PASS / 12 FAIL；冻结 baseline 仍失败 | 数值/节点策略 | REPAIR / FAIL |
| V3.1 base | repair 2 | solver 和完整 orchestration 闭合；首模式 log-Gamma route 差 0.0148718 > 0.0002 | 直接科学 threshold 失败 | ESCALATE / FAIL |
| V3.1-U | resume/controller | lock、原子 publication、二次中断恢复、additive validator 多次发现 false acceptance | control-plane | 修复后才允许运行 |
| V3.1-U | 初始 official | Route-U exponent-2 closed boundary 在 220 dps 因 roundoff 被误拒绝 | 实现/数值域构造 | REPAIR / FAIL |
| V3.1-U | repair 1 | A/U/B 完成；Route-C child rc70，但未持久化 failed key/error/runtime identity | provenance + external execution | REPAIR / FAIL |
| V3.1-U | repair 2 | 多轮 source/environment/entry-authority 修复后，one-shot 23-anchor sentinel 为 14 PASS / 9 MST_FAILED | 外部方法 totality 失败 | ESCALATE / FAIL |
| V3.1-X | implementation | sentinel admission、loaded sources、durable supervision、dispatch env、precision witness 五类 false acceptance | 实现 + control-plane | 两轮修复 |
| V3.1-X | sentinel attempt 1 | WLS 错读 `$ScriptCommandLine`，首调用 rc64 | 外部接口 | REPAIR / FAIL |
| V3.1-X | sentinel attempt 2 | exact source values 相同，但 Association key order 不同，`SameQ` 误拒绝并 rc69 | 序列化/接口 | REPAIR / FAIL |
| V3.1-X | repair 2 | package 先缺 micro-review authority；修复后 real-Wolfram semantic normalizer 仍 rc69 且诊断不足 | authority + runtime | ESCALATE / NOT_ASSESSED |
| V3.1-Y | initial package | operation/predicate ambiguity、wire/FSM schema 不完整、Route-U 固定 318 与 fresh-selector 冲突 | 设计/spec | REPAIR / NOT_ASSESSED |
| V3.1-Y | repair 1/2 | 多项闭合，但 predicate values、P00、lifecycle receipt、P17、terminal manifest 仍不能由冻结 bytes 唯一重建 | machine-authority spec | ESCALATE / NOT_ASSESSED |
| V3.1-Z | generated authority | 1 GB generated candidate 可重复生成；T7 发现 decimal grammar 冲突和 spec 非自包含，随后用户停止 | preliminary spec/compiler | 无正式 verdict |

## 4. V3.1 base：错误与缺陷

### 4.1 初始 Route-A 原生失败

首个冻结节点为 `kM=0.005, ell=2, odd`。stabilized BVP 报 singular Jacobian，protected bidirectional fallback 报 non-monotonic grid。该节点没有完成，因此 Route A/B/C、16 thresholds 和 5 certificates 均无法评估。

对应 blocker：`v31_route_a_first_node_native_failure`。

### 4.2 official runner scope 不完整

初始 runner 只硬编码一个 Route-A call；没有 496-mode loop、9920 ladder nodes、102/458 AP graph、23 external records、完整 threshold evaluation、resume/checkpoint 或 certificates。即使首节点意外 PASS，runner 仍会强制进入失败终态。

对应 blocker：`v31_official_runner_incomplete_scope`。

### 4.3 JSONL publication 缺陷

所谓 canonical ladder JSONL record 被写成 multiline JSON。whole-file JSON 有效，但逐行 JSONL reload 失败。这是 publication/serialization 缺陷，不是首节点数值失败的原因。

### 4.4 repair-cycle-1 sentinel 仍失败

冻结 20-node graph 只有 multiplier 4/8 的 8 个节点 PASS；multiplier 1/2 的 12 个节点失败，包括冻结 baseline。失败异常为：

- `scaled-tortoise Jost matching inputs are invalid`（7）
- `scaled-tortoise incoming Jost coefficient is unresolved`（5）

如果事后选用 multiplier 4/8，会构成 result-dependent favorable selection，因此未被允许。

### 4.5 repair-cycle-2 的直接科学失败

最终 repair 已让首 key 的 20/20 nodes 与完整 `496/9920/102/458/23` orchestration 闭合，但 official r3 在第一个模式触发：

```text
Gamma_flux = 1.836777608324503e-14
Gamma_S    = 1.8096635301389888e-14
abs(log(Gamma_flux)-log(Gamma_S)) = 0.01487180343263006
frozen limit = 0.0002
ratio to limit = 74.3590171631503
```

对应 blocker：`v31_gamma_routes_log_scientific_failure`。这是冻结 criterion 的直接失败，不是权限、manifest 或资源问题。

## 5. V3.1-U：错误与缺陷

### 5.1 resume controller package 的 crash-consistency 缺陷

初版设计在创建 replacement 前先 rename stale lock，并以 final pathname 原位写 authority。可达 crash state 包括 stable lock pathname 消失、final authority 只写入前缀，而后续 attempt 又被要求验证完整链。

对应 blocker：`v31ur_lock_authority_publication_not_interruption_atomic`。

### 5.2 prepared/append 协议不支持第二次中断恢复

设计把任何 torn line 都判 terminal，却又宣称可安全处理第二次系统中断。它没有区分“authenticated prepared bytes 的精确前缀”和“未知/篡改 suffix”。

对应 blocker：`v31ur_prepared_append_protocol_not_second_interrupt_resumable`。

### 5.3 additive validator false acceptance

validator 接受未知 attempt-level control file；即使七份 authority files 全是 `{}`，只要重算 self-reported `authority_commit` hash，仍可能通过。其根本问题是校验 self-consistency，而非独立重建 allowed-set、schema、root、lock、source ledger、approval 和 monotone chain。

对应 blocker：`v31ur_additive_validator_false_acceptance`。

### 5.4 Route-U closed-boundary roundoff

在 `kM=0.005, ell=10, odd`、220 dps，理论上满足闭边界的 exponent-2 auxiliary radius 因计算表达式出现约 `-7.082e-220` 而被 `>=` 拒绝；120/160 dps 则恰好为零并通过。几何 admissibility 不应由该精度敏感的相减决定。

对应 blocker：`v31u_auxiliary_radius_closed_boundary_roundoff`。

### 5.5 repair 1 的 Route-C 失败不可诊断

repair 1 完成 Route A 496/9920、Route U 318/954 和 Route B 102/458，但 Route-C child exit 70，0/23 records。失败 branch 没有持久化：

- exact failed anchor/key 与 error class；
- raw stdout/stderr、exit/wait receipt；
- 实际 WLS、WolframKernel 与完整 BHPT source identity。

因此只能知道 `MST_FAILED`、`AMPLITUDE_INVALID` 或 output-shape error 至少发生一个，不能确定是哪一个。

对应 blocker：`v31u_route_c_external_totality_and_provenance`。

### 5.6 repair 2 package/implementation 的 control-plane 缺陷

先后发现并修复/澄清：

- `v31u_repair2_sentinel_entry_authority_undefined`：one-use sentinel 的 executable/argv/cwd/env/root derivation authority 不唯一；
- `v31u_repair2_loaded_source_snapshot_closure_false_acceptance`：loaded-source/snapshot validator 可接受不完整或自洽但错误的 closure；
- `v31u_repair2_sentinel_runtime_environment_allowlist_false_acceptance`：只投影允许的 env keys，会忽略 caller 注入的额外 key；
- `v31u_repair2_sentinel_runtime_environment_allowlist_unlaunchable`：改成比较完整 `os.environ` 后，真实 macOS/CPython 又会自动加入 `LC_CTYPE` 与 `__CF_USER_TEXT_ENCODING`，导致合法 frozen launch 无法通过。

这些都说明真实 process startup environment 没有在 package freeze 前做 exact-binary preflight。

### 5.7 repair 2 的最终外部方法 totality 失败

one-shot 23-anchor Route-C sentinel 完整执行了一次且没有 retry：14 PASS、9 ERROR，error 全为 `MST_FAILED / ReggeWheelerRadial returned $Failed`。失败 anchors：

- `kM=0.1`: `ell=2,3,4,8`
- `kM=0.5`: `ell=2,3,4,10`
- `kM=2`: `ell=18`

对应 blocker：`v31u_repair2_route_c_sentinel_totality_failure`。这证明冻结的 MST 方法没有满足 exact-23 totality gate；它不自动证明底层物理错误。

另有 wrapper 的 `external Route-C amplitude identity mismatch`，但它位于九个 native MST failures 之后，不是决定性原因。

## 6. V3.1-X：错误与缺陷

### 6.1 首次 implementation review 的五个 Class-A 缺陷

1. `v31x-a-sentinel-admission-gates-omitted`：sentinel 只检查结构/资源，可在 current-balance 等冻结数值 criterion 严重超限时仍发布 PASS。
2. `v31x-a-loaded-source-closure-incomplete`：声明 6 个 loaded files，但真实 entry graph 是 8 个；漏掉 `Kernel/MST/MST.m` 与 `RenormalizedAngularMomentum.m`，并且比较的是记录自身而非实际 loaded contexts/files。
3. `v31x-a-durable-supervision-and-totality-incomplete`：缺稳定 held lock、prelaunch/running/receipt/terminal chain、失败节点记录和 batch totality；publication 也没有充分证明 exclusive/no-follow/fsync。
4. `v31x-a-dispatch-environment-authority-unbounded`：任意临时 review/dispatch path 与 caller-added environment key，只要自我回显即可通过。
5. `v31x-a-serialized-precision-unproven`：只验证 decimal 可解析/有限，不证明 90/120-digit node 的每个非精确值确实带有所需 precision/accuracy。

### 6.2 authority-bridge 与 namespace 缺陷

实现审查 archive path 曾仍指向旧 YELLOW authority，需要单独 bridge。随后 producer 只允许 `attempt_0001`，但 immutable failed attempt 已占用同名 namespace；之后的首次 operator launch 又因 Python symlink 和相对 script argv 在 pre-consumption gate fail closed。

这些属于 control-plane，不是科学 failure，但暴露了 dispatch namespace、absolute argv 与 live executable identity 没有在 freeze 前端到端验证。

### 6.3 sentinel attempt 1：Wolfram argv contract 错误

Python 正确调用五元素 `WolframKernel -script WLS REQUEST OUTPUT`，但 WLS 以 `$ScriptCommandLine` 长度 3 为前提。真实 WolframKernel 14.3 使用的接口不同，首 child 在 import/source/solver 前返回 rc64 与 usage 文本。

对应 blocker：`v31x-sentinel-wls-scriptcommandline-contract-mismatch`。

### 6.4 sentinel attempt 2：Association order-sensitive 比较

controller canonical JSON 的 key order 是 `[context,mode,nlink,path,sha256,size]`；WLS literal Association 是 `[context,path,sha256,size,mode,nlink]`。八个 records 的语义值完全相同，但 WLS 使用 order-sensitive `SameQ`，因此在 solver 前 rc69。

对应 blocker：`v31x-sentinel-loaded-source-start-association-order-mismatch`。

### 6.5 repair 2 package 缺 micro-review machine authority

package 只预声明 future micro-review path，却没有冻结 formal micro-terminal review prompt、精确 success/failure tokens 和 non-circular authority DAG。T6 若自行补齐会变成实现自证。

对应 blocker：`v31x-r2-micro-review-authority-contract-missing`。

### 6.6 repair 2 的 real-Wolfram semantic normalizer 仍失败

修正 source-ledger 语义投影后，唯一 real-Wolfram zero-science preflight 仍以 rc69、`loaded-source record semantic mismatch` 失败。实现把多个 leaf predicates 汇总到同一 generic branch，未持久化 record ordinal 或 exact failed predicate，因此无法从 evidence 判断具体不一致。

对应 blocker：`v31x-r2-wls-semantic-normalizer-runtime-failure`。repair 2/2 耗尽后 X 被永久冻结。

## 7. V3.1-Y：错误与缺陷

Y 没有进入 implementation 或 science；其失败发生在 protocol/package design 层。

### 7.1 initial package 的三个 blockers

1. `v31y-predicate-registry-operation-profile-ambiguous`：四种 operation 的 predicate count、顺序、fixture map 不唯一。
2. `v31y-checkpoint-ack-parent-edge-wire-undefined`：frame/checkpoint/ACK/parent barrier/stage-edge 缺字段级 type/domain/nullability、digest inputs 与完整 FSM binding。
3. `v31y-route-u-graph-authority-contradiction`：固定 `318/954` 与“必须从 exact-496 fresh selector 动态得到 N_U/3N_U、且不可复用 failed predecessor route map”冲突。

### 7.2 repair 1 后剩余问题

operation profiles 与 dynamic Route-U 得到闭合，但仍缺：

- wire/checkpoint/ACK/FSM 的每字段 value/comparison/evidence semantics；
- compatibility barriers 的一致机器定义；
- stage16 child-exit 到 stage17 terminal 的 cryptographic closure；
- distinct final delta-review authority path，导致 T6 start gate 会与旧 YELLOW archive 冲突。

### 7.3 repair 2 后仍未闭合的核心 blocker

虽然八个 schemas、字段数、digest DAG 与结构性 sequencing 更明确，仍有以下内容不能由冻结 bytes 唯一重建：

- predicate `field_id/ownership/value_type/comparison_id/expected_value/evidence-input plan`；
- P00 `stage0_seed -> stage_open_authority` 的唯一映射；
- typed lifecycle receipt schema/self-hash；
- P17 对 child exit、EOF/wait/reap/process-group-empty 的 evidence plan；
- terminal manifest 的完整 schema、field order 与 hash formula。

对应最终 blocker：`v31y-checkpoint-ack-parent-edge-wire-undefined`。由于 repair 2/2 用尽，Y 以 `ESCALATE / NOT_ASSESSED` 冻结。

## 8. V3.1-Z：生成式 machine-authority 候选与中断审查

Z 采用 GMA-Z1：从一个 typed spec 生成约 1,006,400,405 bytes、551 files、80,724 predicates、159 conformance vectors 和 2,105,410 mutation recipes。T4 三次、T0 两次 fresh generation 均 byte-identical，资源约 63 秒和 278 MB RSS。

但“生成可重复”不等于“spec 自包含且独立可重编译”。正式 T7 source-distinct hostile review 在被用户中断前，报告了两项可复现 preliminary defects：

1. spec 的 canonical decimal AST 接受 `1e+00`，两份 generated validators 的 frozen regex 却拒绝它；同一 authority 内 decimal language 不一致。
2. 若干 positional registry 的 column semantics 与三个 generated source templates 只存在于 candidate generator 源码，不在 declarative spec 中；不使用 candidate generator 的独立 recompiler 无法从 spec 唯一地产生全部 authority bytes。

由于 T7 turn 被中断，未生成 `T7_2026-08-14_v3_1_z_generated_machine_authority_package_review.md`，没有正式 `ADVANCE/REPAIR/ESCALATE` verdict。Z 必须记录为 **stopped / formal review incomplete / science NOT_ASSESSED**。

## 9. 跨版本根因分析

### 9.1 production-realistic preflight 太晚

多次错误只有在不可逆 one-use execution 后才暴露：Wolfram argv、macOS env 注入、Association order、真实 loaded contexts、source semantic normalizer。它们本应在冻结 science package 前，以 exact binary + exact argv + exact env + exact source tree 做可重复、零科学 handshake。

### 9.2 science 与 control plane 耦合过深

同一个 gate 同时验证 solver、external package、publication、lock、resume、dispatch、review tokens、authority DAG 和科学 thresholds。任何一层失败都会废弃整个 root，并诱发新的 repair package。

### 9.3 duplicated semantics 导致 drift

相同概念分别存在于 Python、WLS、JSON spec、generated validators、prompt prose 和 T7 reconstruction 中：decimal grammar、source records、key order、env allowlist、predicate values。重复实现使“自洽但不一致”成为常态。

### 9.4 一次性/不可重用规则放大低级错误成本

不可重用对于防止 post-hoc selection 是合理的，但在 argv、path、manifest 或 parser 尚未完全 preflight 时使用 one-shot，会把低成本接口错误变成昂贵的整轮失败。

### 9.5 审查复杂度超过科学对象本身

Y/Z 的 machine-authority artifact 达到数万 predicates、数百万 mutation recipes、约 1 GB 派生数据，但仍未消除关键实现自由度。这说明继续增加规则数量没有解决 single-source semantics 与端到端可执行性问题。

## 10. 后续若重启该科学目标，最低设计原则

1. 将 **科学 kernel**、**external-runtime adapter**、**artifact publication**、**governance authority** 分成独立 gates；先让每层有小而稳定的 API。
2. 外部程序必须先通过 exact production binary 的 repeatable compatibility suite；在此阶段允许重复，禁止 science call。
3. 所有序列化 schema、decimal grammar、source ledger 与 predicate semantics 只能有一个 typed source；Python/WLS validator 必须由它生成，不能另写一份规则。
4. 在 one-use science 前执行三个层级：single-call handshake、代表域 micro-sentinel、完整域 dry orchestration。三者均须复用同一 executable path、argv construction、environment normalization 和 source loader。
5. provenance 必须在 child launch 前 durable publish，并在任何退出后保存 failed ordinal、exact predicate、stdout/stderr、wait/reap receipt 与 source identity。
6. 对科学失败和实现失败使用不同 repair budgets；control-plane 修复不得消耗 scientific repair，但也不得通过另起字母分支无限延长 live-lock。
7. 设置 governance complexity budget。若 authority artifact 大于计算代码数个数量级，停止扩写 protocol，回到更小的可执行 contract。

## 11. 当前停止边界与 nonclaims

- heartbeat automation `schwo-v3-1-u-v3-2` 已删除。
- 正式 T7 的 V3.1-Z turn 已被用户中断；未发布正式 Z review archive。
- 未启动 T6 V3.1-Z implementation、Wolfram science、official V3.1-Z root 或 V3.2。
- V3.1 base/U/X/Y 均不得解释为 PASS。
- 本报告不放宽任何 threshold/domain/convention/method/precision，也不把 partial/failed roots 提升为 acceptance evidence。
- 没有 global GREEN、full-domain V3 certification、Li-figure equivalence 或 finite-radius observer claim。

## 12. 主要证据索引

- Base initial/repairs：
  - `docs/handoffs/archive/T4_2026-08-11_v3_1_terminal_failure.md`
  - `docs/handoffs/archive/T4_2026-08-11_v3_1_repair_cycle1_preexecution_blocker.md`
  - `docs/handoffs/archive/T4_2026-08-11_v3_1_repair_cycle2_terminal_failure.md`
  - `docs/handoffs/archive/T7_2026-08-11_v3_1_initial_failure_review.md`
  - `docs/handoffs/archive/T7_2026-08-11_v3_1_repair_cycle2_delta_review.md`
- V3.1-U：
  - `docs/handoffs/archive/T7_2026-08-12_v3_1_u_resume_controller_package_review.md`
  - `docs/handoffs/archive/T7_2026-08-12_v3_1_u_resume_controller_implementation_delta_review.md`
  - `docs/handoffs/archive/T7_2026-08-12_v3_1_u_terminal_scientific_failure_review.md`
  - `docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle1_terminal_scientific_review.md`
  - `docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_sentinel_review.md`
- V3.1-X：
  - `docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_implementation_review.md`
  - `docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_route_sentinel_terminal_review.md`
  - `docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_sentinel_attempt_0002_terminal_review.md`
  - `docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle2_source_ledger_implementation_delta_review.md`
- V3.1-Y：
  - `docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_review.md`
  - `docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_delta_review_1.md`
  - `docs/handoffs/archive/T7_2026-08-13_v3_1_y_external_protocol_package_delta_review_2.md`
- V3.1-Z：
  - `docs/handoffs/archive/T4_2026-08-13_v3_1_z_generated_machine_authority_redesign_analysis.md`
  - `docs/phase6_v3_1_z_generated_machine_authority_design.md`
  - `configs/phase6_v3_1_z_machine_authority_spec.json`
  - interrupted formal T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed`（无正式 archive）。

