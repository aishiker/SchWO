# 对 `SchWO_audit_20260802.md` 的独立复核与整改

日期：2026-08-02

## 2026-08-02 最终闭合补充（取代本文早期“尚未闭合”状态）

本文下方第 3、5.4、7、10 节保留的是本轮开始时的审计边界和修复理由，
不再代表最终项目状态。其列出的五项后续工作现已全部实施并验证：

1. 已从 Appendix-A RW-gauge metric 直接计算 Schwarzschild 背景上的
   linearized Riemann，并在 incident Cartesian orthonormal frame 投影
   `E_xx/E_xy`，production 路线不再依赖 lower-NP pseudoinverse completion；
2. Fig.2 已由独立 80-digit `mpmath` tortoise-RK4/log-derivative matching
   对 `ell=110,120,130,140` spot check；结果支持 SchWO 的高-`ell` tail，
   但仍按“强证据而非作者错误的因果证明”报告；
3. Fig.8 的 `ell=20..502` 已改为 direct MST minimal-solution recurrence，
   不再使用 finite-`r_out` offset、raised-cosine overlap 或 empirical blend；
4. Fig.3--7 已用 direct metric-curvature bridge 全量重算；
5. Fig.3--8 已从保存数据重新渲染 PDF/约 600 dpi PNG，并完成逐 panel
   source-bound raster comparison。

统一 validator 为 `PASS`：

```text
runs/phase5/paper_figures/audit_repairs_20260802/
  audit_repairs_validation_odejet.json
SHA-256 f791d88897d9c877f0ec95defc6cfa083a0c683837a36a7e030f7da5f7d308cb
```

完整结果、artifact hashes、收敛量、600 dpi 图像和定量对照见
`docs/reports/SchWO_audit_five_repairs_20260802.md`。五项整改状态为
**COMPLETE**；严格论文等价性仍为 **YELLOW**，因为 Fig.4 `kM=2`、
Fig.5/6 phase 与 Fig.7 longitudinal morphology 尚有量化残差，且作者未公开
raw figure data。该边界是科学不确定性，不是未执行上述五项整改。

本文逐项复核 `audits/SchWO_audit_20260802.md` 的事实、推理和责任判断，
并记录本轮已经实施的代码修正。结论分为：

- **成立**：代码、保存数据或独立解析关系可以直接复现；
- **部分成立**：主要证据成立，但最终因果结论仍缺独立验证；
- **尚未闭合**：审计指出了真实风险，但现有信息不足以给出唯一物理解。

本轮没有覆盖、修改或“修饰”既有科学数据。所有旧图和旧 NPZ 保持原样，
但不再把未闭合的 Fig. 3--7 observable 当作论文级物理复现。

## 1. 总结判定

| 审计对象 | 独立判定 | 回应与处理 |
|---|---|---|
| Fig. 1 | 成立（限定在径向层） | exact/asymptotic、`A_in` 归一化、tortoise phase 和保存参数相互一致；未发现需改动的径向公式。 |
| Fig. 2 高频末图 | 部分成立 | 有限半径高-ell tail 的物理论证成立，但普通双端匹配在转向区的 condition number 极大；没有任意精度 BVP 前不能断言论文算错。已在 metadata 中明确标为“强证据而非证明”。 |
| Kirchhoff Eq. (47) | 成立 | 印刷正号与标准点质量公式及论文虚线均矛盾。默认改为 `standard_point_mass`；保留 `literal_paper_v1` 做取证复现。 |
| Fig. 3/5/6/7 observable bridge | 成立 | 当前 full-NP pseudoinverse 缺少 `(+k,m)`/`(-k,-m)` reality bridge；现有输出已统一标为 `physical_claim=false`。 |
| flat-space full-quintuple test | 成立 | raw lower-Weyl error 可精确复现；旧 type-N completion 的 machine-precision pass 会掩盖错误。已新增 raw regression。 |
| Fig. 4 total/scattered surface | 成立，且找到具体额外 bug | 保存场已是 incoming + reflected；旧 renderer 又加一次 incident wave，发生 double count。renderer 已改为直接使用保存总场。 |
| Fig. 8 | 成立 | series reduction 主体无明显错误；旧 aggregate convergence 混合 q=0/1/2，且 empirical high-ell matching 对 `r_out`/overlap 有可见敏感性。已拆分诊断并加入只读扫描 API。 |

## 2. Fig. 1：径向层判断成立

保存的 Fig. 1 数据与配置直接表明：

1. exact radial state 由数值 RW/Zerilli 解给出；
2. 每个模式使用外区 incoming coefficient `A_in` 归一；
3. 渐近相位使用 Schwarzschild tortoise coordinate；
4. exact/asymptotic 的频率、半径、ell 和 parity 均记录在 artifact metadata。

因此，审计所说“径向方程、归一化和 exact-vs-asymptotic 主体基本可信”
成立。它只证明径向层和当前 convention 自洽，不自动证明后续
polarization observable 与论文一致。本项无需改写数值代码。

## 3. Fig. 2：高-ell 衰减证据成立，但“论文错图”尚未证明

独立加载
`runs/phase5/paper_figures/fig2_strict_psi4_convergence/fig2_strict_psi4_convergence_data.npz`
重现：

```text
kM=2, r/M=60, theta=pi/6
final log10|Psi4| = 0.2772768631
```

shell 在 `ell > kr = 120` 后迅速进入 evanescent tail，且 Q018 只从
`ell=153` 起介入，所以“不是 Q018 人为压低 110--140 区间”成立。

但复核同时发现，`ell=79,90,110,120,130,140` 的 ordinary
`bidirectional_match` condition number 约从 `1e132` 增长到 `1e275`。
小 Wronskian/flux residual 并不能独立排除病态基底中的 correlated
cancellation。因此当前严格结论只能是：

> SchWO 的有限平台具有较强物理和数值证据，论文曲线可疑；但在
> 60--100 位、独立 Riccati/log-derivative 或双端 BVP spot check 完成前，
> 不能把论文异常写成已证实事实。

已修改 Fig. 2 metadata，显式记录
`independent_arbitrary_precision_spotcheck_completed=false`，避免未来报告
过度宣称。任意精度 probe 尚未实现，这是本轮保留的 P1 工作，而不是
一个已经修好的项目。

## 4. Kirchhoff Eq. (47)：审计结论成立并已修复

论文 v1 印刷

```text
exp(+pi*gamma/2),  gamma=-2Mk,
```

在光轴给出

```text
|F(0)|^2 = 4*pi*Mk/(exp(4*pi*Mk)-1),
```

会随 `Mk` 指数衰减；这正是旧项目虚线。标准点质量分支和论文图像所需
的符号是

```text
exp(-pi*gamma/2),
|F(0)|^2 = 4*pi*Mk/(1-exp(-4*pi*Mk)).
```

已实施：

- `compute_kirchhoff(..., prefactor_convention="standard_point_mass")` 成为默认；
- `compute_kirchhoff_eq47(...)` 明确保留印刷公式
  `literal_paper_v1`；
- `standard_point_mass_axis_intensity(...)` 用独立 `expm1` 解析式验证光轴，
  不复用 Gamma/Kummer 实现；
- artifact schema 升级并记录选用的 convention；
- Fig. 5/6 渲染入口改用标准分支；
- 文档保留论文 typo 的取证说明。

所以责任判断是：旧程序忠实抄录了印刷式；论文 Eq. (47) 的符号几乎
可以确定是排版错误；论文作图使用的应是负号分支。

## 5. Fig. 3/5/6/7：full-Weyl / positive-frequency bridge 问题成立

### 5.1 Eq. (35g-h) 的星号没有被真正实现

当前 raw production 路径使用同一正频率下的线性关系，而论文式含
complex conjugation。对一个 real field，complex conjugation 牵涉
`(-k,-m)` partner；不能把星号直接解释为 same-`(+k,m)` conjugation，
也不能无推导地删掉星号。论文没有给出完整可编码桥，项目也尚未闭合。

### 5.2 flat completion 的掩盖效应可复现

在审计给出的 flat probe 上，独立复现：

```text
theta=0.4: raw full error 0.1186258665; raw Psi4 error 0.0175636850
theta=1.0: raw full error 0.9623614894; raw Psi4 error 0.3401586264
```

而 least-squares type-N completion 后误差降至约 `1e-15`。因此旧测试
只证明 completion 能投影回目标子空间，并没有验证 raw quintuple。

### 5.3 已实施的安全修正

- 新增 raw strict-NP flat diagnostic，并将以上两组数值冻结为 regression；
- full-NP pseudoinverse 明确命名为 diagnostic bridge；
- `observable_bridge_validated=false`、
  `positive_frequency_reality_bridge_validated=false`、
  `physical_claim=false` 写入 solver、Table-I、transmission、Fig. 7 等
  paper-facing metadata；
- paper-inferred Eq. (42) continuation 只保留为带标签的 hypothesis；
- 增加 reflection-plane off-diagonal leakage 诊断。literal same-`k,m`
  conjugation probe 的 leakage 约为 `1.05`，所以它也不能作为修复。

### 5.4 尚未实施的物理修复

审计推荐的最终方案是合理的：从 RW-gauge metric perturbation 直接构造
linearized Riemann/Weyl，在 incident Cartesian orthonormal tetrad 投影
`E_xx`、`E_xy`。这需要完整推导、符号/数值交叉验证和新的 production
数据，不能靠更换一行共轭或重新标定曲线完成。

因此本轮选择“隔离错误 claim + 增加能抓错的测试”，没有伪造一个
未经验证的新 observable。现有 Fig. 3、5、6、7 精确点均应视为 historical
diagnostics，不能称为与论文已经对齐。

## 6. Fig. 4：确认了 incident wave double counting

沿代码数据流检查可见：

```text
incident partial-wave coefficient c_lm
-> scale = c_lm/A_in
-> same radial solution contains incoming + reflected parts
-> saved h_plus/h_cross is the total field
```

旧 `fig4_comparison.py` 错把保存数组称为 scattered field，又加了一次
Eq. (46) incident plane wave。这会改变 plateau 和整条曲线，属于确定的
renderer bug。

已修复：

- production metadata 新增
  `field_content="total_incident_plus_reflected"` 及归一化依据；
- Fig. 4 renderer 直接验证并使用保存总场，不再加第二个 incident wave；
- 输出 schema 升至 v3，数组名显式使用 `saved_total`；
- manifest 记录 `incident_wave_added_by_renderer=false`；
- 新增防 double-count regression。

旧 `fig4_exact_asymptotic_comparison_total_v2_20260801` artifact 保留不改，
但已在 physics spec 标为 diagnostic-only。即使修复这项，Fig. 4 仍受上一节
未闭合 observable bridge 影响，不能据此直接宣布论文复现完成。

## 7. Fig. 8：主体成立，convergence 与 matching 诊断已补强

Appendix D/E 的 phase-factor combination、helicity matrix、E5 reduction 和
`|M22|^2+|M12|^2` 可由代码和测试闭合。审计指出的两个问题也成立：

1. 旧 metadata 的单一 max change 混合 q=0、q=1、q=2；
2. numerical-to-analytic tail 使用项目自己的 finite-`r_out` correction 和
   raised-cosine blend，不等价于作者未公开的 raw phase shifts。

已将 ladder diagnostics 分成每个 q、每个频率，并在
`theta/pi >= 0.2` 报告 pointwise relative 和 normalized L-infinity change。
对 `ellmax 402 -> 502` 的 q=2 数据，重现审计值：

```text
kM=0.5  4.552110652e-7
kM=1.0  1.016433399e-6
kM=1.5  1.210640054e-6
kM=2.0  3.324351384e-6
```

新增的只读 matching sensitivity scan 不运行 ODE。以
`r_out=300, overlap_half_width=15` 为参考：

- `r_out=300, width=10` 通过现有 gates，四频率 q=2 normalized
  L-infinity difference 为约
  `0.00433, 0.00475, 0.00602, 0.00303`；
- `r_out=240`、`r_out=360` 以及若干 width 组合被现有 phase/circular-mean
  gates 拒绝。

这支持“Fig. 8 差异主要来自项目特定 matching 输入”的判断。它不是误差条，
也不替代 direct high-ell MST。当前 matched metadata 已明确
`empirical blend=true`、`direct MST=false`、`strict paper reproduction=false`。

## 8. 修改清单

主要代码修改：

- `src/schwgw/scattering/kirchhoff.py`：双 convention、标准默认、独立光轴式；
- `src/schwgw/io/kirchhoff.py`：artifact convention/schema；
- `src/schwgw/scattering/weyl.py`：pseudoinverse bridge 的 diagnostic 状态；
- `src/schwgw/scattering/partial_wave.py`：raw flat-NP API 和 validation flags；
- `src/schwgw/scattering/paper_projection.py`：显式 hypothesis 与 parity leakage；
- `src/schwgw/io/results.py`、`tablei.py`、`transmission.py`：physical-claim 和
  total-field metadata；
- `src/schwgw/viz/fig4_comparison.py`：移除 production field 的 incident double count；
- `src/schwgw/io/asymptotic.py`：per-q convergence 与 matching sensitivity；
- `src/schwgw/paper_figures/li_hou_zhao.py`：Fig. 2 证据边界；
- `docs/physics_spec.md`、`docs/equation_map.md` 和 Kirchhoff convention note：
  同步科学状态。

新增/更新测试覆盖 Kirchhoff 光轴恒等式、显式 convention、raw NP error、
paper projection false claim、Fig. 4 total-field 语义、Fig. 8 per-q 与 matching scan。

## 9. 验证结果

在 exact CPython 3.14.6 下运行本轮相关 focused suite：

```text
116 passed, 1 skipped, 1 xfailed in 6.31s
```

随后运行完整测试集：

```text
1115 passed, 117 skipped, 1 xfailed, 104 subtests passed in 304.47s
```

137 条 warning 来自既有 SciPy/RK 高势垒 fail-closed 测试中的
overflow/invalid diagnostics；没有新增测试失败。

涉及的修改文件通过 Ruff：

```text
All checks passed!
```

`git diff --check` 通过。

## 10. 尚存的科学 blocker

本轮没有把下列项目误报为已完成：

1. Fig. 2 `ell=110--140` 的独立 60--100 位 BVP/Riccati spot check；
2. 从 RW-gauge metric 直接计算 linearized curvature 并投影
   `E_xx/E_xy` 的 production observable bridge；
3. Fig. 8 不依赖 empirical blend 的 direct high-ell MST/phase sequence；
4. 上述 bridge 完成后的 Fig. 3--7 科学数据重算与逐 panel 论文对照。

因此最严谨的当前状态是：Kirchhoff 和 Fig. 4 renderer 的确定性程序错误
已修；Fig. 2 的结论已收紧；Fig. 3--7 的核心物理桥已正确隔离但尚未完成；
Fig. 8 的诊断更透明，但不是作者 raw phase data 的逐点复刻。
