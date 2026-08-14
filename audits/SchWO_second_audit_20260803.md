# SchWO 第二轮独立审查：五项整改与 Li–Hou–Zhao Figure 1–8

日期：2026-08-03  
审查对象：`SchWO_source_latest_20260803.zip`  
重点文件：

- `audits/SchWO_audit_response_20260802.md`
- `docs/reports/SchWO_audit_five_repairs_20260802.md`
- `src/schwgw/scattering/metric_curvature.py`
- `src/schwgw/numerics/matching.py`
- `src/schwgw/scattering/mst.py`
- `src/schwgw/io/fig8_mst.py`
- 最新 Fig.1–8 数值数据、PDF/PNG 与 comparison artifacts

## 1. 总结结论

### 1.1 工程整改是否完成

上一轮提出的五项工作，按“是否真正写入代码、生成新数据并通过测试”的标准，已经完成：

1. direct RW metric → linearized Riemann → electric tidal projection 已实现；
2. Fig.2 的 80-digit 独立径向 spot check 已执行；
3. Fig.8 的高 \(\ell\) 段已换成 direct MST；
4. Fig.3–7 已全量重算；
5. Fig.3–8 已重新渲染并进行 raster comparison。

因此，不能再说上一版指出的问题“没有处理”。

### 1.2 科学问题是否全部闭合

没有。当前状态应该是：

- **代码整改：GREEN**；
- **SchWO 自身 convention 下的内部一致性：GREEN**；
- **与 Li–Hou–Zhao 原文逐图严格等价：仍为 YELLOW**。

最重要的剩余系统误差并不是旧的 lower-NP pseudoinverse，而是：

1. **有限外边界的纯平面波匹配**：在 \(r_{\rm out}=300M\) 处直接匹配
   \(e^{\pm ikr_*}\)，没有加入 \(1/r\) 渐近级数或 Jost/MST infinity data；
2. **观察者标架不完全相同**：SchWO 使用 Schwarzschild 静态正交标架，Li 文使用由平直 Cartesian tetrad 经坐标 Jacobian 得到的 incident-aligned tetrad；
3. **MST 尚缺外部独立归一化 benchmark**：recurrence residual 很小只能证明 recurrence 解得准，不能单独证明物理 scattering normalization 完全正确。

这三个问题分别主要影响：

- Fig.4 高频形状；
- Fig.5/6 相位；
- Fig.7 apparent-mode morphology；
- Fig.8 与原图的逐点等价性。

## 2. 对上一轮问题的逐项验收

| 上一轮问题 | 最新实施 | 第二轮判定 |
|---|---|---|
| Kirchhoff Eq.(47) 符号 | 已区分 `standard_point_mass` 与 `literal_paper_v1`，默认前者；有独立轴上解析测试 | **完全完成** |
| lower-NP / positive-frequency observable bridge | 已实现 direct metric-curvature bridge，不再依赖 lower-NP pseudoinverse | **核心缺陷已修；paper tetrad 等价性仍未闭合** |
| raw full-quintuple / parity / \((+k,-k)\) / Table-I tests | 均已加入 focused tests | **完成** |
| Fig.4 incident double counting | renderer 已改为直接消费保存的 total field | **完全完成** |
| Fig.2 任意精度 spot check | 80-digit mpmath、tortoise RK4/log-derivative、step halving | **实质完成，但仍共享有限外边界与 Psi4 reconstruction convention** |
| Fig.8 取消 empirical blend | \(\ell=20\ldots502\) direct MST；无 overlap blend/offset | **高 \(\ell\) 完成；低 \(\ell\) 和外部归一化 benchmark 尚未完全闭合** |
| Fig.3–7 全量重算 | 已完成并生成 durable artifacts | **完成** |
| 600 dpi 重绘及逐 panel 对照 | 已完成 | **完成** |

## 3. direct metric-curvature bridge 的独立审查

### 3.1 已经正确解决的部分

新 production 路线为：

```text
RW/Zerilli master variables
→ RW-gauge metric components and derivatives
→ δR_abcd on Schwarzschild
→ incident-frame electric tidal tensor
→ h_plus = 2 E_xx/k²
→ h_cross = 2 E_xy/k²
```

这确实绕开了旧路线中最危险的步骤：

```text
incomplete lower NP scalars
→ pseudoinverse completion
→ electric tidal tensor
```

我用一个与项目函数独立书写的 full-Riemann-from-metric-jets 计算，对
`linearized_riemann_from_metric_jets(...)` 做了中心差分方向导数检查。相对误差为：

| \(\epsilon\) | relative error |
|---:|---:|
| \(10^{-3}\) | \(1.80\times10^{-10}\) |
| \(3\times10^{-4}\) | \(1.06\times10^{-10}\) |
| \(10^{-4}\) | \(3.27\times10^{-10}\) |

Riemann 指标顺序、第一指标降低产生的背景曲率项以及复杂振幅线性化均通过。

Focused test suite：

```text
40 passed in 13.90s
```

覆盖 metric-curvature、MST、Kirchhoff、Table-I、Fig.4、Fig.8 I/O/plotting。

### 3.2 仍应收紧的 claim

当前代码和 artifacts 中多处写：

```text
physical_claim = true
observable_bridge_validated = 1
```

这个表述偏强。更准确的标签应是：

```text
gauge = "Regge-Wheeler"
observer_frame = "static_orthonormal_incident_aligned"
physical_within_frozen_gauge_frame_convention = true
literal_li_paper_observer_equivalence = false
paper_equivalence = "YELLOW"
```

理由是：有限半径的 \(\delta R_{\alpha\beta\gamma\delta}\) 及其在未扰动静态标架上的投影仍依赖背景-扰动识别和观察者标架；它是一个合理、可复现的物理 convention，但不是自动等于 Li 文的 tetrad convention。

### 3.3 建议补的永久测试

目前 flat TT、Riemann symmetries、parity、anchor-only ODE jet 等测试很好。还建议补：

1. curved-case linearized Ricci vacuum residual；
2. first Bianchi identity；
3. direct metric-curvature result 与独立 gauge-invariant asymptotic waveform 的远区比较；
4. observer-frame switch 的 regression。

## 4. 最大的剩余数值问题：有限 \(r_{\rm out}\) 的外边界

### 4.1 当前实现

`src/schwgw/numerics/matching.py` 在有限半径直接使用：

\[
\psi=A_{\rm in}e^{-ikr_*}+A_{\rm out}e^{ikr_*},
\]

\[
\partial_r\psi=\frac{-ik}{f}A_{\rm in}e^{-ikr_*}
+\frac{ik}{f}A_{\rm out}e^{ikr_*}.
\]

所有 paper-facing 主计算大多使用：

```text
r_out = 300 M
```

没有加入 RW/Zerilli 势导致的 \(1/r\)、\(1/r^2\) 修正。

### 4.2 为什么对高 \(\ell\) 不够

以 Fig.2/4 的高频代表点

\[
kM=2,\qquad \ell=140,\qquad r_{\rm out}=300M
\]

为例：

\[
\frac{V_\ell(r_{\rm out})}{k^2}\simeq 5.45\times10^{-2},
\]

并不小。离心势尾部产生的 leading phase 量级约为

\[
\int_{r_{\rm out}}^\infty \frac{V_\ell}{2k}\,dr_*
\sim \frac{\ell(\ell+1)}{2kr_{\rm out}}
\simeq16.45\;{\rm rad}.
\]

这不表示最终误差必然是 16 rad，因为一部分被公共相位或归一化吸收，但说明
“在 \(300M\) 处已是纯 \(e^{\pm ikr_*}\)”不是受控近似。

### 4.3 独立实际数值 probe

在 Table-I 光轴点、\(kM=0.5\)、\(\ell_{\max}=12\) 下，只改 \(r_{\rm out}\)：

| \(r_{\rm out}/M\) | \(F_+\) | \(|F_+|\) | \(\arg F_+\) |
|---:|---|---:|---:|
| 300 | \(2.02102+2.39246i\) | 3.13183 | 0.86936 |
| 450 | \(2.31146+2.33127i\) | 3.28293 | 0.78966 |
| 600 | \(2.45844+2.28532i\) | 3.35658 | 0.74892 |

即使只用低 \(\ell_{\max}=12\)，300→450 的复振幅相对变化仍约 9.0%，相位变化约 0.080 rad；450→600 仍约 4.6%，相位变化约 0.041 rad。

在 \(\ell_{\max}=36\) 时：

| \(r_{\rm out}/M\) | \(F_+\) | \(|F_+|\) | phase |
|---:|---|---:|---:|
| 150 | \(1.59243+1.64947i\) | 2.29273 | 0.80299 |
| 300 | \(1.93428+1.54137i\) | 2.47331 | 0.67283 |

变化约 14.5%，相位变化约 0.130 rad。

因此：

> 固定 \(r_{\rm out}=300M\) 时的 \(\ell_{\max}\) convergence，只证明 partial-wave sum 对这套有限边界数据收敛；它不证明已经收敛到真正的 spatial-infinity scattering problem。

### 4.4 修复建议

优先级最高：

1. 构造 RW/Zerilli outgoing/ingoing Jost asymptotic series：
   \[
   e^{\pm ikr_*}\left(1+\frac{a_1}{r}+\frac{a_2}{r^2}+\cdots\right);
   \]
2. 或从更大半径用 Riccati/log-derivative infinity data 向内积分；
3. 或用 MST/Coulomb-wave solution 直接提供 outer basis；
4. 对每个 paper-facing artifact 保存
   `r_out_ladder=[300,600,1200,...]` 和 extrapolated value；
5. phase acceptance 必须包含 \(r_{\rm out}\) 收敛，而不能只包含 \(\ell_{\max}\) 收敛。

## 5. 另一个重要差异：观察者 tetrad/orthonormal frame

Li 文 Eq.(36) 使用平直 Cartesian null tetrad，并通过 Cartesian–Schwarzschild Jacobian 进行坐标变换。SchWO 新 bridge 使用 Schwarzschild 静态正交标架：

\[
e_{\hat t}=f^{-1/2}\partial_t,\qquad
 e_{\hat r}=f^{1/2}\partial_r.
\]

这两个选择在无穷远一致，在 \(r=30M\) 并不完全一致。

独立 probe：\(kM=0.5,\ell_{\max}=12,r_{\rm out}=300M\)。

### 光轴 \((x,z)=(0,30)M\)

```text
static orthonormal:
F = 2.02102 + 2.39246 i, |F|=3.13183, phase=0.86936

Li-literal coordinate-Cartesian:
F = 1.88629 + 2.23296 i, |F|=2.92304, phase=0.86936
```

振幅差正好约 6.67%。

### \((x,z)=(10,30)M\)

```text
static orthonormal:
F = 1.07660 + 0.03107 i, |F|=1.07704, phase=0.02885

Li-literal coordinate-Cartesian:
F = 1.02441 + 0.01985 i, |F|=1.02461, phase=0.01937
```

复振幅差约 4.96%。

结论：观察者标架差异足以改变 Fig.3/5/6/7 的振幅和局部 morphology，但不能单独解释 Fig.5/6 中约 1 rad 的 phase residual。

建议增加：

```text
observer_frame =
  "static_orthonormal"      # 物理默认
  "li_literal_cartesian"    # 论文复刻模式
```

两套结果都保存，不能把其中一套悄悄重命名为另一套。

## 6. Figure-by-Figure 最新判定

### Fig.1 — GREEN（径向验证层）

- exact/asymptotic 主体实现可信；
- 未发现新的根本错误；
- 建议把 odd/even 两个 sector 都作为 supplement 保存；
- 仍应增加 \(r_{\rm out}\) ladder，以免 asymptotic comparison 与有限边界 normalization 共享偏差。

### Fig.2 — YELLOW-GREEN

80-digit spot check 确实独立于 SciPy radial solver，并得到：

| \(\ell\) | \(|\Delta\Psi_{4,\ell}|\) |
|---:|---:|
| 110 | 0.2429801534 |
| 120 | 0.2515841173 |
| 130 | \(1.9035\times10^{-4}\) |
| 140 | \(1.3831\times10^{-4}\) |

这足以强烈反对论文最后 panel 的 \(10^{10}\) 级平台。

但该脚本仍：

- 在 \(r_{\rm out}=300M\) 用 bare \(e^{\pm ikr_*}\) 初始化外区 basis；
- 使用项目现有 metric reconstruction / `weyl_mode_components` 生成 shell \(\Psi_4\)。

所以它是“独立高精度径向验证”，不是完全独立的 infinity-normalized + independent-Psi4 proof。

当前最严谨结论：

> Li Fig.2 高频蓝线极可能有数值/作图异常；SchWO 的有限 tail 明显更可信，但还应做 outer-boundary ladder 或 MST/Jost outer data 后再写成接近定论的批评。

### Fig.3 — YELLOW-GREEN

- morphology 已明显接近论文；
- Poisson spot、波前弯曲和 plus/cross 层级总体合理；
- 仍有对比度、局部干涉位置差异；
- 主要剩余源是 observer frame 与 outer-boundary phase。

可以作为 SchWO convention 下的物理结果；不能标为逐像素复刻成功。

### Fig.4 — YELLOW；\(kM=2\) 未通过

低三频的 raster MAE 已较小：

| \(kM\) | plus MAE | cross MAE |
|---:|---:|---:|
| 0.5 | 0.1840 | 0.06955 |
| 1.0 | 0.1870 | 0.07300 |
| 1.5 | 0.1825 | 0.07281 |
| 2.0 | 0.5574 | 0.2760 |

`kM=2` 出现宽谷、回升和明显粗糙结构，与原文非小差异。旧 incident double counting 已修，所以不能再归因于 renderer。

优先检查：

1. \(r_{\rm out}\) ladder；
2. shell-by-shell \(\ell\) spectrum，特别是 \(\ell\sim kr\simeq120\)；
3. Q018 transition/oracle 分支；
4. 角网格从 1025 加倍；
5. 两种 observer frame。

当前 Fig.4 的 \(kM=2\) 不应作为最终正确结果冻结。

### Fig.5 / Fig.6 — 振幅 YELLOW-GREEN；相位 YELLOW/RED

新 bridge 的确显著改善：

| 路线 | amplitude MAE | phase circular MAE |
|---|---:|---:|
| old lower-NP | 0.528143 | 1.977851 rad |
| direct curvature | 0.173955 | 1.111339 rad |

但相位仍明显不对。八个 panel 的 raw circular MAE 为：

```text
0.557, 0.795, 0.994, 1.115,
0.986, 1.310, 1.544, 1.591 rad
```

对每个 panel 拟合一个全局 circular phase offset 后，残差 MAE 为：

```text
0.257, 0.268, 0.272, 0.373,
0.498, 0.763, 0.926, 1.342 rad
```

说明：

- near-axis 差异中很大一部分是全局 phase convention / outer-boundary phase；
- far-axis 仍有明显 shape residual，不是简单加一个常数相位就能解决。

当前 phase 不能宣称正确。建议：

1. 先做 \(r_{\rm out}\) phase convergence；
2. 同时输出 principal phase 与 continuous unwrapped phase；
3. 报告“未经对齐的 phase”与“每频率全局 offset 对齐后的 residual”；
4. 两种 observer frame 并列；
5. 轴点做 `axis_regularization=1e-4,1e-5,1e-6,1e-7` sweep。

### Fig.7 — diagnostic-only YELLOW；论文图自身存在内部疑点

项目数据严格满足：

\[
h_L=2h_b
\]

全部像素误差精确为 0。它直接来自 Li 文 Eq.(42e-f)：

\[
\ddot h_b=\frac12\Re\hat\Psi_2,
\qquad
\ddot h_L=\Re\hat\Psi_2.
\]

最新 SchWO 数据中，各 apparent mode 相对物理 plus/cross RMS 规模为：

| \(kM\) | \(h_x\) | \(h_y\) | \(h_b\) | \(h_L\) |
|---:|---:|---:|---:|---:|
| 0.5 | 0.122 | 0.222 | 0.078 | 0.156 |
| 1.0 | 0.139 | 0.274 | 0.112 | 0.224 |
| 1.5 | 0.140 | 0.269 | 0.120 | 0.239 |
| 2.0 | 0.139 | 0.240 | 0.105 | 0.209 |

论文 Fig.7 中 b row 有可见环纹，而 L row 在近似相同色标下几乎全空。这与论文自己的 Eq.(42e-f) 不协调。因此 Fig.7 的纵向差异未必是 SchWO 错；论文很可能对 L row 使用了不同 normalization、被 clipping，或作图数据有误。

不过这些 apparent modes 本身 tetrad/gauge dependent，不是额外 GR 自由度。因此：

- SchWO 当前 nonzero \(h_L\) 比论文图更符合论文公式；
- 但 Fig.7 只能标 `diagnostic_only`；
- 应同时给 raw common-scale、independent-scale 和 unclipped norm table；
- 应询问作者 Fig.7 每一行是否使用同一 normalization。

### Fig.8 — q=2 YELLOW-GREEN；q=0 不应作严格复刻目标

优点：

- \(\ell=20\ldots502\) 已 direct MST；
- recurrence residual \(\lesssim10^{-68}\)；
- even/odd Starobinsky ratio 和 unit modulus tests 通过；
- q=2 的 \(402\to502\) normalized change 约 \(4.4\times10^{-7}\) 到 \(4.4\times10^{-6}\)。

剩余问题：

1. \(\ell=2\ldots19\) 仍来自有限 \(r_{\rm out}=300M\) numerical phases 加 heuristic correction；
2. MST recurrence residual 不是 scattering normalization 的外部验证；
3. 代码只搜索 real \(\nu\)，未覆盖 complex-\(\nu\) branch；
4. 最新 NPZ metadata 错写：
   ```text
   strict_paper_reproduction_claim = true
   ```
   与报告中的 YELLOW、视觉差异及缺少作者 raw data 直接矛盾。

应立即改为：

```text
strict_paper_reproduction_claim = false
paper_equivalence = "YELLOW"
```

并用公开的 Black Hole Perturbation Toolkit MST/ReggeWheeler 或另一个独立 MST 实现，对 \(\ell=20\ldots40\) 做复振幅逐模 benchmark。q=0 点云本来 cutoff-dependent，不应作为“像素一致”验收目标；真正应验收的是 q=2 曲线、低阶相移和 helicity amplitudes。

## 7. 明确的元数据/报告错误

### 7.1 Fig.8 metadata

`fig8_direct_mst_l502_n1440.npz` 中：

```text
strict_paper_reproduction_claim = true
```

这是明确错误，应修正。

### 7.2 direct curvature 的 `physical_claim=true`

不是完全错误，但语义过宽。应改成带 gauge/frame 的限定 claim，避免后续把“内部 convention 下物理合理”误读成“与 Li paper tetrad 严格等价”。

### 7.3 unified validator 的能力边界

当前 validator PASS 主要证明：

- artifacts 完整、finite；
- parity/masks 正确；
- \(\ell_{\max}\) final-pair 收敛；
- direct bridge metadata 正确；
- MST recurrence/parity/unit-modulus gates 通过。

它**没有验证**：

- \(r_{\rm out}\) convergence；
- Li-literal observer frame；
- external MST normalization；
- Fig.5/6 phase 与 paper marker 的 acceptable residual；
- Fig.4 `kM=2` morphology gate。

因此 validator 名称最好区分：

```text
internal_artifact_validator = PASS
paper_equivalence_validator = YELLOW
```

## 8. 推荐的下一阶段任务顺序

### P0：infinity-boundary hardening

1. 实现 \(1/r\) Jost asymptotic series，至少到 3–5 阶；
2. 或以 MST 生成 outer basis；
3. 为 Fig.2/4/5/6 做 `r_out=300,600,1200` ladder；
4. 保存 raw、extrapolated 及 truncation error；
5. 把 phase convergence 纳入 hard gate。

### P0：dual observer-frame mode

实现：

```text
static_orthonormal
li_literal_cartesian
```

先在 Table-I 8 个点和 Fig.4 代表角验证，再决定是否重跑大网格。

### P0：Fig.5/6 phase diagnostic

- raw principal phase；
- unwrapped phase；
- per-frequency/panel global offset；
- offset-removed residual；
- axis-epsilon sweep；
- outer-boundary ladder。

### P1：Fig.4 `kM=2` shell audit

- selected angles：\(\theta/\pi=0.25,0.5,0.75,0.95\)；
- 保存 each-\(\ell\) contribution；
- 标出 ordinary/Q018/MST branch；
- 比较 \(\ell_{\max}=120,160,200,240\) 与不同 \(r_{\rm out}\)。

### P1：Fig.8 external MST benchmark

- 对 \(kM=0.5,1,1.5,2\)、\(\ell=20,25,30,35,40\)；
- 比较 complex odd/even phase factors，而不仅是模和 parity ratio；
- 为低 \(\ell=2\ldots19\) 使用 direct MST 或更可靠 infinity matching；
- 记录参考实现版本、完整 URL、license 和 SHA。

### P1：metadata hardening

修正 Fig.8 strict claim；给 direct curvature 添加 gauge/frame/equivalence 标签；区分 internal PASS 与 paper-equivalence YELLOW。

## 9. 给 T0 的简洁结论

```text
The five requested audit repairs are implemented and the new artifacts are real.
Do not reopen the old lower-NP pseudoinverse issue as the primary blocker.

However, do not declare strict Li-paper reproduction GREEN.
The dominant remaining numerical blocker is the finite-r_out outer matching:
the solver matches to bare exp(±ikr*) at r_out=300M without a controlled 1/r
Jost/MST asymptotic basis. Fixed-r_out lmax convergence does not bound this bias,
and direct probes show 5–15% complex-amplitude sensitivity and O(0.04–0.13 rad)
phase shifts even in low-cost cases.

The second blocker is observer-frame equivalence. The production bridge uses a
static Schwarzschild orthonormal incident frame, while Li Eq.(36)-(38) uses a
coordinate-Cartesian tetrad. Add explicit static_orthonormal and
li_literal_cartesian modes.

Required next slices:
1. infinity-boundary/Jost-or-MST hardening + r_out ladders;
2. dual observer-frame Table-I and Fig.4 probes;
3. Fig.5/6 phase decomposition and axis-epsilon sweep;
4. Fig.4 kM=2 shell/Q018 audit;
5. external MST benchmark and low-ell MST completion;
6. fix Fig.8 strict_paper_reproduction_claim=true and qualify physical_claim.

Current per-figure status:
Fig1 GREEN; Fig2 YELLOW-GREEN; Fig3 YELLOW-GREEN; Fig4 YELLOW with kM=2 open;
Fig5/6 amplitude YELLOW-GREEN but phase YELLOW/RED; Fig7 diagnostic-only YELLOW
with a likely inconsistency in the published L row; Fig8 q=2 YELLOW-GREEN.
```

## 10. 审查限制

- 本轮独立运行了 40 个 focused tests，没有再次运行耗时约 11 分钟的完整 1131-test suite；完整结果来自项目自身保存的测试记录。
- 没有作者 raw numerical data 或公开源码，所有 paper marker comparison 都是 raster-level diagnostic。
- Fig.2 的高精度检查没有完成独立 \(r_{\rm out}\to\infty\) extrapolation。
- 没有在本环境调用外部 Mathematica Black Hole Perturbation Toolkit；因此 MST 的外部 benchmark 是明确下一步，而不是本报告已经完成的事情。
