# Phase 6 — V3 经典散射与吸收独立验证：Root T0 总调度 Prompt

版本：v1.0  
日期：2026-08-11  
适用项目：`schw-gw-waveoptics / SchWO`  
建议仓库路径：`docs/prompts/phase6_v3_master_prompt.md`

---

## 使用方法

将下方“**可直接复制给 Root T0 的完整 Prompt**”整体发送给当前 Root T0 线程。

本文件把 V3 拆为：

- `V3.0`：文献、公式、相位语义、参数域和阈值冻结；
- `V3.1`：逐模灰体因子、反射/透射概率和 parity 检验；
- `V3.2`：总吸收截面、低频与高频极限；
- `V3.3`：低频微分散射截面与 helicity amplitudes；
- `V3.4`：高频后向 glory 与高角动量相干求和；
- `V3.5`：逐 observable、逐参数域的正式 release certificate。

执行原则：

1. `V3.0` 未获独立 T7 `ADVANCE/PASS` 前，不运行 V3 科学计算。
2. V3.1–V3.2 属于 **phase-insensitive absorption branch**，可在绝对相位仍为 `PARTIAL` 时推进。
3. V3.3–V3.4 属于 **phase-sensitive coherent-scattering branch**；只有在 \(\ell\)-dependent phase、odd/even relative phase、free/scattered reference phase 均满足冻结条件后才可启动。
4. 不把 Li–Hou–Zhao 图像当作主要验收标准；Li 图只保留为 secondary regression。
5. 不允许 global GREEN；每项证书都必须带 domain、numerical uncertainty、convention uncertainty 和 nonclaims。

---

# 可直接复制给 Root T0 的完整 Prompt

```text
你现在是 SchWO 项目的 Root T0。

======================================================================
0. 当前阶段裁定与严格边界
======================================================================

当前 V2 最终独立判词为：

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PARTIAL

ACCEPT GREEN / V2 SELECTED-DOMAIN
GAUGE-INVARIANT WAVEFORM AND FLUX VALIDATION COMPLETE

唯一 current V2 authority：

runs/phase6/asymptotic_waveform/
v2_selected_release_v2_20260811T083414_py314

其关键身份：

manifest.json
51ddf1580448382be7e182f92cf76bbf53ed39f15418af9e546f357979c743eb

release_ledger.json
8bbc4d098ca64ac256a63a09e4e5744191f314038fe140c131eaf7606f75ba49

report.json
58157a422fabed9be8bb9956c3097296c6dfd30b8d8065d4731edf6fe5a826dc

source_map.json
9011a2cff8a944d68234a32cd754c7b6482b61644464fc512b906e2fbec76fb7

summary.json
25dcc333085e3cd7150bf9e954766ae60a942f3a6e51c20ff36a4081077045cb

V2 certificate ceiling：

- 11 PASS；
- V2_ABSOLUTE_PHASE_CONVENTION = PARTIAL；
- full_domain_v2 = NOT_ASSESSED；
- global_status = null；
- global_green_permitted = false；
- radial_solve_count = 0。

本轮正式裁定为：

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PARTIAL

ACCEPT GREEN / V2 SELECTED-DOMAIN VALIDATION
SUFFICIENT FOR BOUNDED V3.0 CONTRACT FREEZE

该裁定只授权 V3.0 zero-science contract freeze。
它不授权立即运行 V3.1–V3.5，不授权 full-domain V3，不授权 Li figure
重算，不授权 global GREEN。

======================================================================
1. 必读文件和身份检查
======================================================================

按顺序读取：

1. project.md
2. status.md
3. docs/handoffs/T0_current.md
4. docs/handoffs/T1_current.md
5. docs/handoffs/T4_current.md
6. docs/handoffs/T6_current.md
7. docs/handoffs/T7_current.md
8. docs/review_gate_liveness_protocol.md
9. docs/templates/t7_gate_verdict_template.md
10. docs/phase6_independent_physical_validation.md
11. phase6_v2_selected_domain_closeout.md 或仓库内对应 closeout
12. configs/phase6_v2_0_convention_contract_20260810.json
13. configs/phase6_v2_0_selected_domain_20260810.json
14. 当前 V1 repaired release、V1 external direct、V1 AP selected evidence
15. 当前 V2.1、V2.2-v3、V2.3-v2、V2.4-v2 immutable roots
16. references/manifest.md
17. docs/equation_map.md
18. docs/physics_spec.md

必须重新核验：

- current V2 root 与上述五个 hashes；
- V2.0 convention/domain contract identity；
- V1 current radial authority；
- current T7 双轴 verdict；
- protected source hashes；
- superseded roots 不得被 current pipeline 引用。

若任一 current identity 不一致，立即返回：

HOLD / V3 FROZEN INPUT IDENTITY MISMATCH

并明确 mismatch path、expected hash、observed hash、owner、解除条件。
不得自行重建或替换 frozen input。

======================================================================
2. V3 的科学目标与非目标
======================================================================

V3 的主要目标是：

1. 用成熟 Schwarzschild 引力波散射理论验证逐模灰体因子和吸收概率；
2. 验证总吸收截面及其低频、高频极限；
3. 在相位约定闭合后，验证低频微分散射截面、helicity-preserving / reversing
   amplitudes；
4. 验证高频 backward glory 的峰位、宽度、振幅和 spin-2 Bessel 结构；
5. 为每个 observable 和参数域发布独立 certificate。

V3 不做：

- 有限半径 static/Li observer response；
- detector worldline/tetrad operational response；
- 2×2 finite-radius polarization transfer matrix；
- Li Fig.3–7 重算；
- 以 raster 相似度作为主要真值；
- full-domain/global GREEN；
- 未经 contract 的 threshold 临时选择。

V3 的主要参考必须来自 primary literature，而不是仅依赖 Li 文的二手转述。
至少检查并纳入：

- Handler & Matzner, Gravitational wave scattering, Phys. Rev. D 22 (1980)；
- Dolan, Scattering of long-wavelength gravitational waves, Phys. Rev. D 77 (2008)；
- Dolan, Scattering and absorption of gravitational plane waves by rotating black holes,
  CQG 25 (2008)，取 Schwarzschild 极限；
- Folacci & Ould El Hadj, gravitational-wave scattering by Schwarzschild,
  Phys. Rev. D 100 (2019)；
- series reduction 的 primary source；
- Regge–Wheeler、Zerilli、Moncrief、Martel–Poisson normalization 文献；
- 必要时 Sánchez 等经典吸收文献。

T1 必须使用项目允许的 arXiv/文献 skills 搜索和核对 primary sources。
不得把模型记忆直接写成冻结公式。

======================================================================
3. 总体执行链
======================================================================

必须依次创建、冻结并 hash 下列 prompt：

V3.0：
- docs/prompts/phase6_t1_v3_0_literature_formula_freeze.md
- docs/prompts/phase6_t7_v3_0_contract_review.md

V3.1：
- docs/prompts/phase6_t4_v3_1_mode_greybody.md
- docs/prompts/phase6_t7_v3_1_review.md

V3.2：
- docs/prompts/phase6_t4_v3_2_total_absorption.md
- docs/prompts/phase6_t7_v3_2_review.md

V3.3：
- docs/prompts/phase6_t6_v3_3_low_frequency_scattering.md
- docs/prompts/phase6_t7_v3_3_review.md

V3.4：
- docs/prompts/phase6_t6_v3_4_glory_helicity.md
- docs/prompts/phase6_t7_v3_4_review.md

V3.5：
- docs/prompts/phase6_t6_v3_5_selected_release.md
- docs/prompts/phase6_t7_v3_5_review.md

严格依赖：

V3.0 T1
→ V3.0 T7
→ V3.1 T4
→ V3.1 T7
→ V3.2 T4
→ V3.2 T7

V3.3 与 V3.4 只有在 V3.0 相位语义 gate 明确授权后才可继续：

V3.0 phase-sensitive branch authorized
→ V3.3 T6
→ V3.3 T7
→ V3.4 T6
→ V3.4 T7

最终：

V3.2 T7 GREEN
+ 若 phase-sensitive branch 已授权，则 V3.4 T7 GREEN
→ V3.5 T6
→ V3.5 T7
→ Root T0 final adjudication

若 phase-sensitive branch 尚未授权，允许先发布 absorption-only V3 release，
但必须将 V3.3/V3.4 记为 NOT_ASSESSED，不得伪造完整 V3 closure。

======================================================================
4. T7 审核活性规则
======================================================================

所有 T7 review 必须使用双轴判词：

ADVANCE_DECISION:
- ADVANCE
- REPAIR
- ESCALATE

CLAIM_STATUS:
- PASS
- PARTIAL
- FAIL
- NOT_ASSESSED

CLAIM_STATUS=PARTIAL 不自动阻止 ADVANCE。

finding 必须分类：

A. BLOCKING_CURRENT_GATE
B. NONBLOCKING_LIMITATION
C. CONTROL_PLANE_REPAIR
D. FOLLOW_UP_DEBT

只有 A 类可阻止推进。
A 类必须写出 violated contract item、exact evidence、expected/observed、
bounded repair、allowed files、recheck command、unblock condition。

每个 gate 最多两轮 bounded repair。第二轮仍未闭合时，必须：

ESCALATE / T0 ADJUDICATION REQUIRED

不得无限 YELLOW/HOLD。
不得把 full-domain 未覆盖、future task 未完成、Li 图不一致等 out-of-scope
限制追溯性加入当前 gate。

======================================================================
5. V3.0：零科学计算的文献、公式、相位、域与阈值冻结
======================================================================

V3.0 只允许文献和 contract 工作，不允许运行 radial solver、partial-wave sum
或任何 V3 producer。

T1 必须创建：

1. docs/phase6_v3_0_validation_contract.md
2. docs/phase6_v3_0_formula_map.md
3. docs/phase6_v3_0_phase_taxonomy.md
4. docs/phase6_v3_0_literature_matrix.md
5. configs/phase6_v3_0_domain.json
6. configs/phase6_v3_0_thresholds.json
7. configs/phase6_v3_0_external_anchor_matrix.json
8. references/notes/phase6_v3_absorption_scattering_conventions.md

V3.0 必须冻结以下对象。

A. mode-level scattering quantities

- incident amplitude；
- reflected amplitude；
- horizon-transmitted amplitude；
- complex S_l^(odd/even)；
- signed currents；
- positive physical fluxes；
- greybody factor Gamma_l^(odd/even)；
- reflection probability；
- transmission/absorption probability；
- parity relation 与其适用边界。

不得只用 1-|S|^2 作为唯一 horizon absorption 证据；必须保留 direct horizon
flux route，并把 1-|S|^2 作为独立 consistency route。

B. total absorption cross section

- 逐模 partial cross section 的精确 normalization；
- 是否对 parity/helicity 求和，以及权重；
- 单位：M^2 或无量纲 sigma/M^2；
- l 起点；
- lmax 选择；
- tail bound；
- low-frequency expansion；
- high-frequency geometric-optics limit；
- oscillatory corrections 是否属于 mandatory gate 或 diagnostic。

不得在 V3.0 前把任何模型记忆中的 prefactor 写入 production。
公式必须有 primary-source equation mapping 或独立推导。

C. differential scattering / helicity amplitudes

- helicity-preserving amplitude f(theta)；
- helicity-reversing amplitude g(theta)；
- d sigma/d Omega 的定义；
- odd/even S-matrix 组合；
- free-incident subtraction；
- long-range/Coulomb phase；
- forward-direction distributional structure；
- series reduction / analytic subtraction 的精确 recurrence；
- angle exclusion window；
- reduction-order ladder；
- lmax/tail convergence。

D. low-frequency analytic benchmark

冻结 primary-source 下的 spin-2 Schwarzschild low-frequency differential
cross-section 公式、适用范围、误差阶数和角度范围。

若 contract 最终采用常见形式：

M^{-2} d sigma/d Omega
= [cos^8(theta/2)+sin^8(theta/2)] / sin^4(theta/2)

必须由 primary source 重新核对 normalization 与 helicity convention，不能仅因
该公式常见就直接冻结。

E. high-frequency / glory benchmark

冻结：

- geometric-optics capture cross section；
- critical impact parameter；
- backward glory formula；
- spin-2 对应 Bessel order；
- glory impact parameter b_g；
- |db/dtheta| at theta=pi；
- amplitude、peak location、width 的 comparator；
- 可接受角区和 frequency domain。

若采用 sigma_abs → 27 pi M^2 或 spin-2 glory J_4 结构，也必须绑定 primary
source、units 和 asymptotic error policy。

F. phase taxonomy

必须将 V2_ABSOLUTE_PHASE_CONVENTION=PARTIAL 分解为：

1. common retarded-time origin；
2. frequency-dependent common phase；
3. ell-dependent phase；
4. odd/even relative phase；
5. total/free/scattered reference phase；
6. Coulomb/long-range phase subtraction；
7. spin-weighted harmonic phase convention。

逐项标记 PASS / PARTIAL / NOT_ASSESSED，并明确它影响：

- V3.1 greybody；
- V3.2 total absorption；
- V3.3 differential scattering；
- V3.4 glory/helicity。

V3.1/V3.2 可在只有 common overall phase 未闭合时推进。
若 ell-dependent phase、odd/even relative phase 或 total/free/scattered phase
仍 PARTIAL/NOT_ASSESSED，则 V3.3/V3.4 必须 NO-GO。

G. domain freeze

V3.0 必须分别冻结：

- V3.1 mode-domain；
- V3.2 frequency grid 与 l-sum domain；
- V3.3 low-frequency grid、angle grid 和 forward exclusion；
- V3.4 high-frequency grid、backward-angle grid；
- external selected anchors；
- arbitrary-precision anchors。

V2 的 30-key domain 只能作为 inherited controls，不能冒充 V3 的完整
low/high-frequency domain。

H. thresholds

所有 comparator 必须在计算前冻结：

- complex S；
- log Gamma；
- flux balance；
- parity probability difference；
- lmax adjacent change；
- tail upper bound；
- analytic-limit relative error；
- external-backend error；
- angle-grid change；
- reduction-order change；
- glory peak/width/amplitude error。

每个 threshold 必须有：path、hash、field、单位、domain、理由和来源。
不得使用 V1/V2 的 radial threshold 代替新的 observable threshold。

V3.0 T1 完成时只允许返回：

CHECKPOINT / V3.0 ANALYTIC-LITERATURE BENCHMARK CONTRACT FROZEN

T7 必须独立核查 primary references、formula mapping、phase dependency、domain、
threshold 和 scope。

允许的 GREEN：

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS

ACCEPT GREEN / V3.0 ANALYTIC-LITERATURE BENCHMARK CONTRACT READY

T7 还必须给出两个显式布尔字段：

absorption_branch_authorized: true|false
phase_sensitive_scattering_branch_authorized: true|false

======================================================================
6. V3.1：逐模灰体因子和吸收概率
======================================================================

只有 V3.0 T7 对 absorption branch 给出授权后，T0 才派发 V3.1 给 T4。

V3.1 目标：

在 frozen V3.1 domain 上计算 odd/even mode-level：

- S_l；
- reflection probability；
- direct horizon flux；
- Gamma_l；
- log Gamma_l；
- flux balance；
- parity probability relation；
- numerical ladders；
- external selected comparators。

必须至少使用：

Route A：SchWO production radial backend；
Route B：SchWO independent arbitrary-precision selected backend；
Route C：external direct/MST selected backend。

independence boundary 必须如实记录。

必须区分：

Gamma_flux = F_H / F_in
Gamma_S = 1 - |S_l|^2

两者分别计算，互相比较；不得由一个定义另一个。

对于极小 Gamma：

- 保存 arbitrary-exponent decimal string；
- 保存 log10 Gamma 或 ln Gamma；
- 禁止 binary64 下溢为零后仍宣称 PASS；
- comparator 使用 log-domain 和 absolute flux residual，不使用普通相对误差。

必须做：

- r_in ladder；
- r_out/Jost-order ladder；
- tolerance/precision ladder；
- ordinary/turning/evanescent/high-ell 分层；
- odd/even 独立 solve，不把 parity-derived even 冒充独立 even；
- selected external crosscheck。

V3.1 输出：

runs/phase6/classic_scattering/
v3_1_mode_greybody_v1_<timestamp>_py314

至少包含：

- manifest.json
- records.jsonl
- summary.json
- report.json
- source_map.json
- uncertainty_budget.json

必须有 certificates：

- V3_MODE_GREYBODY_NUMERICAL
- V3_MODE_GREYBODY_FLUX_VS_S
- V3_MODE_GREYBODY_EXTERNAL
- V3_MODE_PARITY_PROBABILITY
- V3_MODE_DOMAIN_COVERAGE

T4 完成时：

CHECKPOINT / V3.1 MODE GREYBODY EVIDENCE FROZEN

T7 GREEN 仅表示 frozen V3.1 domain 可进入 V3.2；full-domain 未覆盖是
NONBLOCKING_LIMITATION，不得单独造成 YELLOW。

======================================================================
7. V3.2：总吸收截面和低/高频极限
======================================================================

只有 V3.1 T7 `ADVANCE` 后启动。

V3.2 必须：

1. 按 V3.0 frozen normalization 由 Gamma_l 构造 partial absorption cross section；
2. 对连续 ell 序列求和，不允许使用 V2 稀疏 key 集；
3. 为每个 kM 自适应选择 ell_max；
4. 保存 ell_max ladder；
5. 给出 tail upper bound 或受控 asymptotic tail；
6. 分别保存 odd/even 与总和；
7. 比较 SchWO 与 external selected data；
8. 检查低频解析 scaling；
9. 检查高频 geometric-optics limit；
10. 必要时记录高频 oscillatory absorption 结构，但只有 V3.0 冻结为 mandatory
    时才作为 blocker。

每个频率必须保存：

- sigma_abs/M^2；
- partial sums；
- odd/even contributions；
- selected ell_max；
- adjacent-lmax change；
- tail estimate；
- numerical uncertainty；
- convention uncertainty；
- analytic benchmark residual；
- external benchmark residual。

低频和高频不能只取一个点。
必须使用 frozen frequency ladder，并做拟合/外推时保存：

- 拟合模型；
- 选择区间；
- 参数协方差或稳健误差；
- 更换区间后的敏感性；
- 不允许通过选择有利区间隐藏偏差。

V3.2 输出：

runs/phase6/classic_scattering/
v3_2_total_absorption_v1_<timestamp>_py314

证书：

- V3_PARTIAL_ABSORPTION_SUM
- V3_TOTAL_ABSORPTION_CONVERGENCE
- V3_LOW_FREQUENCY_ABSORPTION_LIMIT
- V3_HIGH_FREQUENCY_CAPTURE_LIMIT
- V3_ABSORPTION_EXTERNAL_BENCHMARK

T4 完成时：

CHECKPOINT / V3.2 TOTAL ABSORPTION EVIDENCE FROZEN

T7 GREEN 可允许 absorption-only V3 release，即使 phase-sensitive branch 仍未授权。

======================================================================
8. V3.3：低频微分散射与 helicity amplitudes
======================================================================

只有以下条件同时满足才启动：

- V3.0 T7：phase_sensitive_scattering_branch_authorized=true；
- ell-dependent phase 已 PASS；
- odd/even relative phase 已 PASS；
- total/free/scattered reference phase 已 PASS；
- V3.1 mode evidence 已 GREEN。

V3.3 目标：

- 计算 helicity-preserving amplitude f(theta)；
- 计算 helicity-reversing amplitude g(theta)；
- 计算 d sigma/d Omega；
- 验证 low-frequency analytic result；
- 验证 coherent partial-wave sum 的 convergence。

必须明确区分：

- total outgoing；
- free incident outgoing；
- scattered outgoing；
- S_l - 1 结构；
- forward long-range contribution；
- regularized/reduced series；
- physical angle domain。

禁止：

- 在 null infinity 对 total plane wave 直接普通求和；
- 通过逐 ell 或逐 angle 相位拟合；
- 用 Li Fig.8 raster 作为 primary truth；
- 将 q=0 未正则化点云作为严格复现 gate；
- 在 forward singular region 用有限值“填洞”。

必须做 convergence matrix：

- ell_max ladder；
- series-reduction order ladder；
- angle-grid ladder；
- forward-exclusion ladder；
- arbitrary-precision selected angles；
- external literature/code selected anchors。

low-frequency comparison必须报告：

- f、g 分别比较；
- total d sigma/d Omega 比较；
- angle-dependent relative error；
- 不适用于 forward singularity 的区域；
- frequency-scaling residual；
- numerical/convention budgets。

V3.3 输出：

runs/phase6/classic_scattering/
v3_3_low_frequency_scattering_v1_<timestamp>_py314

证书：

- V3_HELICITY_PRESERVING_AMPLITUDE
- V3_HELICITY_REVERSING_AMPLITUDE
- V3_LOW_FREQUENCY_DIFFERENTIAL_CROSS_SECTION
- V3_SERIES_REDUCTION_CONVERGENCE
- V3_FORWARD_DOMAIN_POLICY

T6 完成时：

CHECKPOINT / V3.3 LOW-FREQUENCY SCATTERING EVIDENCE FROZEN

======================================================================
9. V3.4：高频 backward glory 与 helicity
======================================================================

只有 V3.3 T7 GREEN 后启动。

V3.4 必须建立两条独立路线：

Route A：SchWO partial-wave S-matrix + spin-2 angular assembly；
Route B：独立 null-geodesic / geometric-optics glory predictor。

Route B 不得调用 Route A 的 phase shifts 或拟合结果。

必须保存和比较：

- backward-angle differential cross section；
- glory peak angle；
- peak amplitude；
- half-maximum width 或 frozen width measure；
- Bessel-order structure；
- helicity reversal；
- kM scaling；
- ell_max/reduction-order convergence；
- geodesic b_g 与 derivative；
- numerical/convention uncertainty。

不得以“形状看起来像”作为 PASS。
必须使用 V3.0 冻结的 quantitative comparators。

V3.4 输出：

runs/phase6/classic_scattering/
v3_4_glory_helicity_v1_<timestamp>_py314

证书：

- V3_BACKWARD_GLORY_PEAK
- V3_BACKWARD_GLORY_WIDTH
- V3_BACKWARD_GLORY_AMPLITUDE
- V3_GLORY_GEODESIC_CROSSCHECK
- V3_HIGH_FREQUENCY_HELICITY
- V3_HIGH_ELL_TAIL_CONTROL

T6 完成时：

CHECKPOINT / V3.4 GLORY AND HELICITY EVIDENCE FROZEN

======================================================================
10. V3.5：selected-domain release
======================================================================

V3.5 不新增公式、不修改 solver、不扩大 domain，只聚合已经独立审核接受的
V3.1–V3.4 evidence。

如果 phase-sensitive branch 未执行，允许 absorption-only release；对应散射和
glory certificates 必须为 NOT_ASSESSED。

正式 certificate inventory 至少包括：

1. V3_MODE_GREYBODY
2. V3_MODE_FLUX_S_EQUIVALENCE
3. V3_MODE_EXTERNAL_INDEPENDENCE
4. V3_PARITY_PROBABILITY
5. V3_TOTAL_ABSORPTION
6. V3_LOW_FREQUENCY_ABSORPTION
7. V3_HIGH_FREQUENCY_CAPTURE
8. V3_LOW_FREQUENCY_DIFFERENTIAL_SCATTERING
9. V3_HELICITY_AMPLITUDES
10. V3_SERIES_REDUCTION
11. V3_BACKWARD_GLORY
12. V3_PARTIAL_WAVE_TAIL_CONTROL
13. V3_PHASE_CONVENTION
14. V3_SELECTED_DOMAIN_RELEASE_POLICY

每项必须包含：

- exact observable；
- exact domain；
- PASS / PARTIAL / FAIL / NOT_ASSESSED；
- numerical uncertainty；
- convention uncertainty；
- evidence roots/hashes；
- independence boundary；
- nonclaims；
- protected-file hashes；
- V3.0 contract/domain/threshold hashes。

强制：

- global_status = null；
- global_green_permitted = false；
- 不得声称 full-domain V3；
- 不得声称完整 SchWO validation；
- 不得声称 finite-radius detector response；
- 不得声称 Li figure equivalence；
- 不得把 absorption-only release 冒充完整 scattering release。

V3.5 输出：

runs/phase6/classic_scattering/
v3_selected_release_v1_<timestamp>_py314

以及：

docs/phase6_v3_selected_domain_closeout.md

T6 完成时：

CHECKPOINT / V3 SELECTED-DOMAIN RELEASE FROZEN

T7 最终可返回：

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS|PARTIAL

ACCEPT GREEN / V3 SELECTED-DOMAIN CLASSIC SCATTERING VALIDATION COMPLETE

其中 CLAIM_STATUS 可以因为未执行 phase-sensitive branch 或 full-domain 未覆盖而
保持 PARTIAL；只要 release 对当前 bounded scope 诚实闭合，就不得因此阻止推进。

======================================================================
11. 代码与文件修改边界
======================================================================

V3.0 允许修改：

- docs/phase6_v3_*.md
- docs/prompts/phase6_*v3*.md
- configs/phase6_v3_*.json|yaml
- references/notes/phase6_v3_*.md
- references/manifest.md（仅增加 V3 primary sources）
- docs/equation_map.md（仅增加 V3 mapping；不得改 V1/V2 frozen mapping）
- status.md
- docs/handoffs/T0_current.md
- docs/handoffs/T1_current.md
- docs/handoffs/T7_current.md

V3.1/V3.2 允许修改：

- 新建 src/schwgw/scattering/absorption*.py
- 新建 src/schwgw/validation/phase6_v3*.py
- 新建 scripts/phase6_v3*.py
- 新建 tests/unit|physics|regression/test_phase6_v3*.py
- fresh runs/phase6/classic_scattering/**
- V3 docs/config/status/handoffs

V3.3/V3.4 允许修改：

- 新建或有界修改 asymptotic scattering / helicity / series-reduction 模块；
- 不得改 V1 radial backend；
- 不得改 V2 frozen asymptotic normalization；
- 不得改 finite-radius observer modules。

全阶段禁止修改：

- current V1/V2 immutable artifacts；
- V2.0 frozen contract/domain；
- V1 protected radial files；
- frozen Fourier/tortoise/harmonic/master conventions；
- Li figure artifacts；
- legacy NP/pseudoinverse science path；
- numerical thresholds after producer starts；
- Git history rewrite/force push/destructive operation。

如需修改 frozen science/convention：

立即停止并返回 Root T0；必须建立新的 contract identity 和独立 review。

======================================================================
12. 验证、artifact 与 provenance 规则
======================================================================

每个 science producer 必须：

- 使用 exact frozen runtime；
- fresh unique no-overwrite root；
- O_EXCL 或等价独占发布；
- fsync；
- root 0555、files 0444/nlink1；
- canonical serialization；
- in-place reload；
- distinct-temp-copy reload；
- start/end protected hash；
- process/transient/collision check；
- source map；
- manifest；
- machine-readable summary；
- human report；
- separate numerical/convention uncertainty budget。

测试策略：

- 每个子阶段运行 targeted tests；
- 运行所有 Phase-6/V3 tests；
- T7 acceptance 前运行 full suite；
- Ruff check/format 仅要求 zero-new-delta，不强制清理既有全仓 baseline；
- compileall；
- git diff --check。

T7 必须从原始 evidence 独立重建关键量，不得只调用 candidate validator 作为
科学证明。

======================================================================
13. 当前这一轮的实际动作
======================================================================

本轮只执行：

1. 创建 V2→V3 transition document；
2. 创建并冻结 V3.0 T1/T7 prompts；
3. 记录 prompt hashes；
4. 更新 status.md 与 T0 handoff；
5. 派发 V3.0 给现有 T1；
6. V3.0 T1 完成后派发 T7 independent review；
7. 在 V3.0 T7 verdict 返回前停止。

当前不得派发 V3.1–V3.5。
当前不得运行 radial solver、partial-wave sum、absorption scan 或 glory scan。
当前不得自动进入 V4。
```

---

## 预期阶段产物

V3 完整链建议形成以下目录：

```text
docs/
├─ phase6_v2_to_v3_transition.md
├─ phase6_v3_0_validation_contract.md
├─ phase6_v3_0_formula_map.md
├─ phase6_v3_0_phase_taxonomy.md
├─ phase6_v3_0_literature_matrix.md
├─ phase6_v3_selected_domain_closeout.md
└─ prompts/
   ├─ phase6_t1_v3_0_literature_formula_freeze.md
   ├─ phase6_t7_v3_0_contract_review.md
   ├─ phase6_t4_v3_1_mode_greybody.md
   ├─ phase6_t7_v3_1_review.md
   ├─ phase6_t4_v3_2_total_absorption.md
   ├─ phase6_t7_v3_2_review.md
   ├─ phase6_t6_v3_3_low_frequency_scattering.md
   ├─ phase6_t7_v3_3_review.md
   ├─ phase6_t6_v3_4_glory_helicity.md
   ├─ phase6_t7_v3_4_review.md
   ├─ phase6_t6_v3_5_selected_release.md
   └─ phase6_t7_v3_5_review.md

configs/
├─ phase6_v3_0_domain.json
├─ phase6_v3_0_thresholds.json
└─ phase6_v3_0_external_anchor_matrix.json

runs/phase6/classic_scattering/
├─ v3_1_mode_greybody_*/
├─ v3_2_total_absorption_*/
├─ v3_3_low_frequency_scattering_*/
├─ v3_4_glory_helicity_*/
└─ v3_selected_release_*/
```

---

## V3 最终允许的科学声明

在全部相应 gate 通过后，可按证书范围声明：

```text
SchWO mode greybody factors and flux balance:
PASS on declared V3.1 domain.

SchWO total gravitational-wave absorption cross section:
PASS on declared V3.2 frequency and multipole domain.

SchWO low-frequency differential scattering and helicity amplitudes:
PASS only if V3.3 phase-sensitive gate is independently accepted.

SchWO backward glory:
PASS only if V3.4 geodesic and partial-wave routes independently agree.
```

禁止声明：

```text
SchWO globally validated.
All frequencies and multipoles validated.
Finite-radius detector response validated.
Li et al. figures reproduced.
```
