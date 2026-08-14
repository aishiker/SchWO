# SchWO 第三轮审查：从论文复刻转向独立物理验证

日期：2026-08-06  
审查对象：`SchWO_third_audit_package_20260806.zip`

## 1. 审查目标

本轮不再以“Li–Hou–Zhao 八幅图是否逐图一致”为唯一验收标准，而是区分三个不同问题：

1. **Verification**：代码是否准确求解了它声称求解的 RW/Zerilli 方程、边界条件和重构公式？
2. **Physical validation**：这些方程和输出是否对应定义清楚、可操作测量的物理量？
3. **Paper reproduction**：在 Li 文的具体 tetrad、相位、归一化和绘图约定下，能否复现其结果？

第三项只能作为辅助 benchmark，不能替代前两项。

## 2. 总体裁决

当前最科学的结论不是“整个程序已经 GREEN”，也不是“程序仍然不可信”，而是分层判断：

| 层次 | 当前判断 | 说明 |
|---|---|---|
| Schwarzschild 背景、RW/Zerilli 势和主方程 | GREEN | 公式、渐近行为和单元测试充分；没有发现结构性错误 |
| RW-gauge metric reconstruction | GREEN | 与冻结公式一致，targeted tests 通过 |
| 普通振荡区径向散射解与 S-matrix | GREEN（已测域） | 与外部 BHPT/MST odd-sector 复相位在 `kM=0.5,1,1.5,2`, `ell=20..40` 达到约 `9.2e-15` 一致 |
| Jost 外边界实现 | GREEN/YELLOW | 局部方程残差好，且已有 `r_out` ladder；但仍应形成系统的 `r_in/r_out/Jost-order/precision` 误差预算 |
| 高 `ell`/turning/evanescent 的 Q018 路径 | YELLOW | 是 Fig.5/6 高频结果的大部分模式来源，但尚无覆盖实际生产域的独立外部有限半径 radial benchmark |
| metric → linearized Riemann → tidal tensor 代数 | GREEN/YELLOW | 独立 targeted tests 通过；旧 lower-NP pseudoinverse 已不再是主生产桥 |
| 无穷远 gauge-invariant waveform/flux | 尚未闭合 | 应使用 Zerilli–Moncrief 与 Cunningham–Price–Moncrief 规范化建立标准 waveform/flux benchmark |
| 有限半径 `h_plus/h_cross` | YELLOW-GREEN，需限定含义 | 当前是 **RW gauge + 指定 observer frame 下的等效潮汐应变**；尚未证明为唯一、observer-independent 的有限半径“波形” |
| Li 逐图复刻 | YELLOW | 可保留为二级回归测试，不再作为物理正确性的唯一裁判 |

因此，可以称 SchWO 为：

> 一个已经具备可信核心径向散射能力、且能计算指定规范和观察者下有限半径潮汐响应的 Schwarzschild 引力波波光学研究框架。

暂时不宜称为：

> 已完全验证的、对任意有限半径都给出唯一物理 `h_+,h_×` 的黑盒求解器。

## 3. 本轮独立检查

本轮在包内重新运行了以下 targeted tests：

```text
53 passed, 3 subtests passed in 26.67s
```

覆盖：

- Schwarzschild background；
- RW/Zerilli potentials；
- metric reconstruction；
- external MST benchmark importer/contract；
- asymptotic scattering；
- direct metric-curvature；
- flat incident-wave decomposition。

这支持核心模块的可信度，但不等于独立复跑了项目报告中的完整 `1144 passed` 全库测试，也不替代外部物理 benchmark。

## 4. 最新修改中真正成立的进展

### 4.1 外边界已从裸平面波升级为 Jost `1/r` 基

生产路径现在使用

\[
J_\pm(r)=e^{\pm i k r_*}\sum_{n=0}^{N}\frac{a_n^{(\pm)}}{r^n},
\]

而不是在有限 `r_out` 直接假设纯 `e^{±ikr_*}`。这是必要且正确的修复。Fig.5/6 又使用了 `r_out=(1200,1800,2400)M` 的 ladder 与二次 `1/r_out` 外推，最大报告 uncertainty 约 `8.42e-4`。这说明有限外边界误差已大幅受控。

### 4.2 外部 BHPT/MST odd-sector benchmark 很强，但覆盖域仍有限

包内 benchmark 比较了 `kM=(0.5,1,1.5,2)`、`ell=20..40`，odd phase factor 的最大复绝对误差约 `9.21e-15`。这是目前最有力的独立证据之一。

限制是：

- even sector 是通过精确 parity relation 导出，不是第二套独立 even radial solve；
- 未覆盖 `ell≈kr` turning region 和 Fig.5/6 实际使用的大量高 `ell` Q018 模式；
- 比较重点是 asymptotic phase/S-matrix，而不是有限半径 radial value 和其导数。

### 4.3 direct metric-curvature bridge 已解决旧极化桥的核心缺陷

当前主链是：

```text
RW/Zerilli master modes
→ RW-gauge metric
→ linearized Riemann
→ specified observer tetrad
→ E_xx, E_xy
→ equivalent h_plus, h_cross
```

这比通过未独立验证的 lower-NP pseudoinverse 恢复潮汐张量可靠得多。

### 4.4 Fig.2 高 `ell` 爆炸更可能是论文侧异常

Jost/r_out 生产数据与 80 位独立径向积分在 `ell=110,120,130,140` 的 shell amplitude 上达到约 `10^-5` 相对一致，而没有出现论文 Fig.2 最后一格那种约十个数量级爆炸。现有证据强烈支持 SchWO 的有限 tail，但仍应把旧 pre-Jost `stored_double_shell_psi4` 明确标记为 superseded。

### 4.5 Fig.4 的 `0.403` 不应继续被解释为“最终不收敛”

最新 shell audit 的 checkpoint 是 `lmax=120,160,200,240`：

- `120→160` 最大相对变化约 `0.403`，说明 `lmax=120` 不够；
- `160→200` 已约 `5.3e-11`；
- `200→240` 为零，是因为更高 shell 已进入当前 suppression policy。

因此，Fig.4 selected probes 的 partial-wave sum 在当前算法内已经由 `lmax≈160` 收敛。真正未闭合的是 **高 `ell` Q018/suppression 分支是否由独立算法验证**，而不是简单的 `lmax` 不收敛。

## 5. 当前最重要的剩余风险

### 5.1 Q018 已占据 Fig.5/6 高频生产的大部分模式

最新 Li-frame Fig.5/6 每个 `r_out` 的模式统计为：

| `kM` | unique radial modes | dense-local Q018 modes | 比例 |
|---:|---:|---:|---:|
| 0.5 | 166 | 130 | 78.3% |
| 1.0 | 214 | 138 | 64.5% |
| 2.0 | 358 | 202 | 56.4% |
| 2.5 | 454 | 258 | 56.8% |
| 3.0 | 550 | 314 | 57.1% |
| 4.0 | 718 | 402 | 56.0% |

这里最关键的逻辑是：

> 很小的 `lmax` final-pair delta 和 `r_out` uncertainty 只证明同一 Q018 算法内部稳定，不能证明 Q018 自身在全部生产域物理正确。

因此 Fig.5/6 当前最大的 validation gap 不是相位图像，而是 Q018 高 `ell` 有限半径 radial solution 的外部独立验证。

### 5.2 generic radial solver 中存在大量 Table-I/论文专用 envelope

`radial_solver.py` 中存在显式的：

- Table-I point/radius；
- `kM=4`；
- 特定 `ell` 段；
- review-grid frequency；
- 多个论文任务命名的 Q018 oracle。

这些 fail-closed envelope 在项目开发阶段有用，但它们把“通用数值算法”和“特定论文算例的已审配置”混进了同一核心模块。它不直接造成数据错误，却削弱了程序作为独立通用 solver 的可信度。

应改成：

```text
Generic scaled radial backend
+ generic conditioning/error estimator
+ external experiment configuration
```

而不是核心 solver 知道 Li Table-I 的具体点和频率。

### 5.3 `precision_dps` 目前不代表真正任意精度

Q018 request 暴露 `precision_dps`，但实现仍固定记录：

```text
precision_dps = 53
precision_note = double_precision_scipy
```

这不是错误，但接口命名容易让人误以为已进行了高精度积分。应：

- 要么删掉/重命名为 `requested_precision_dps` diagnostic；
- 要么真正增加 `mpmath/Arb/Mathematica` 高精度 backend。

### 5.4 近视界边界仍只有 leading ingoing form

当前在

\[
r_{\rm in}=2M(1+\epsilon)
\]

只使用

\[
\psi=e^{-ikr_*},\qquad
\partial_r\psi=-\frac{ik}{f}\psi.
\]

应补：

- near-horizon Frobenius series；或
- `r_in_eps` ladder。

否则外边界已经精修，而内边界误差仍没有形成对等的预算。

### 5.5 光轴仍通过固定 `theta=10^-6` clamp 处理

这不能自动证明轴上极限存在且数值正确。应增加

\[
\epsilon_\theta=10^{-3},10^{-4},\ldots,10^{-8}
\]

的 ladder 与解析/数值外推，并保存轴极限 uncertainty。

### 5.6 flat oracle 还不是完整 production-pipeline oracle

direct Cartesian TT flat oracle 很适合验证极化符号与归一化，但它绕过：

- plane-wave partial-wave decomposition；
- RW gauge reconstruction；
- radial solver；
- finite-radius angular sum。

所以必须保留一个较小规模但真正端到端的 flat partial-wave test，不能只凭 direct oracle 宣称整条链通过。

### 5.7 metadata 中仍有过期描述

当前以下模块仍写有旧的

```text
full strict-NP pseudoinverse tidal projection
polarization_bridge_validated = false
```

包括：

- `src/schwgw/scattering/transmission.py`
- `src/schwgw/io/results.py`
- `src/schwgw/io/tablei.py`

同时 `legacy_adapter.py` 的若干默认值仍是 `physical_claim=True`。这属于明确的 provenance bug，应优先修复；否则后续结果文件会错误描述实际生产算法。

## 6. “有限半径 h_plus/h_cross”究竟是什么

这是项目下一阶段必须严格处理的概念问题。

在无穷远辐射区，`h_plus/h_cross` 可由 gauge-invariant master functions 或 `Psi4` 定义，物理含义清楚。

在有限半径强场区：

- 辐射场、近场和背景潮汐并没有唯一局部分解；
- `+ / cross` 依赖观察者四速度、空间三标架和横向基；
- 一阶曲率扰动在固定背景坐标点的表示会随 gauge 改变；真正的测量还包括观察者世界线和 tetrad 的相应变换。

因此当前的输出最准确名称是：

```text
finite-radius, RW-gauge, chosen-observer equivalent tidal strain
```

不是“错误量”，但也不是无需限定的唯一 waveform。

建议把首要有限半径输出改为完整潮汐张量：

\[
E_{\hat i\hat j}
=
\delta C_{\alpha\mu\beta\nu}
 e_{\hat i}^{\alpha}u^{\mu}
 e_{\hat j}^{\beta}u^{\nu},
\]

再把

\[
h^{\rm equiv}_{+}=\frac{E_{\hat x\hat x}-E_{\hat y\hat y}}{k^2},
\qquad
h^{\rm equiv}_{\times}=\frac{2E_{\hat x\hat y}}{k^2}
\]

作为针对单色波和给定 tetrad 的派生量。

## 7. 严格的独立验证计划

### Gate V0：claim/provenance 清理

1. 修正 stale pseudoinverse metadata。
2. 将 legacy NP completion/pseudoinverse 移入明确的 `legacy/diagnostics` 层。
3. 所有有限半径结果必须记录：
   - gauge；
   - observer worldline/congruence；
   - tetrad；
   - polarization basis；
   - tortoise/time phase origin；
   - axis regularization；
   - `r_in/r_out/Jost order/lmax`；
   - production backend；
   - physical claim 的限定语。
4. 修正 Fig.4 状态描述：`lmax` 已收敛，高 `ell` backend 外部验证待完成。

### Gate V1：径向 S-matrix 与通量守恒

对每个 `(sector,ell,k)` 验证：

\[
\left|R_{\ell}^{(\pm)}\right|^2+
\left|T_{\ell}^{(\pm)}\right|^2=1
\]

并保存 Wronskian/flux budget。

至少扫描：

```text
kM = 0.01, 0.05, 0.1, 0.5, 1, 2, 4, 8
ell = 2 ... actual production lmax
```

重点加密：

```text
ell ≈ k r_eval
Q018/turning/evanescent transition region
```

必须同时做：

- `r_in_eps` ladder；
- `r_out` ladder；
- Jost order ladder；
- ODE tolerance ladder；
- double vs arbitrary precision；
- BHPT MST vs direct numerical integration；
- even sector 独立有限半径验证。

长期结构上，应把 Table-I 专用 Q018 envelope 移出 core solver。

### Gate V2：无穷远 gauge-invariant waveform

建立 Martel–Poisson normalization：

- even：Zerilli–Moncrief function；
- odd：Cunningham–Price–Moncrief function。

用三条独立路线计算同一 waveform：

```text
A. gauge-invariant master functions -> asymptotic h_plus/h_cross
B. reconstructed metric/curvature -> Psi4 -> h_plus/h_cross at large r
C. external BHPT/MST radial amplitudes -> asymptotic waveform
```

并检查：

```text
waveform agreement
energy flux at infinity
horizon absorption flux
radial S-matrix flux balance
```

这一 gate 是项目真正从“会算图”变成“已验证 GW solver”的关键。

### Gate V3：不依赖 Li 的解析/经典文献 benchmark

必须加入：

1. **长波极限的 spin-2 differential cross section**

\[
\lim_{M\omega\to0}
M^{-2}\frac{d\sigma}{d\Omega}
=
\frac{\cos^8(\theta/2)+\sin^8(\theta/2)}{\sin^4(\theta/2)}.
\]

2. **吸收截面**

- spin-2 在 `Mω→0` 时趋零；
- 高频趋向

\[
\sigma_{\rm abs}\to27\pi M^2.
\]

3. **helicity preserving/reversing amplitudes** 和 odd/even phase relation。
4. **backward glory** 的峰位、宽度和随频率的标度。
5. series-reduction order 与 `lmax` convergence。

这些 benchmark 比 Li 的有限半径图更成熟，也更适合验证核心 S-matrix。

### Gate V4：有限半径操作性可观测量

选定至少两类观察者：

```text
static Schwarzschild observer
radially free-falling observer
```

为每类观察者明确：

- worldline；
- Fermi-Walker transported tetrad；
- `E_ij` 和必要时 `B_ij`；
- detector arm response / geodesic deviation。

增加非平凡 pure-gauge test：对 `h_{mu nu}` 施加已知 gauge transformation，同时一致变换观察者世界线和 tetrad，最终 detector response 必须不变。

完成这一 gate 后，有限半径结果才可从“gauge-fixed equivalent strain”升级为“operational detector response”。

### Gate V5：偏振传播矩阵与相位定义

不要只计算

\[
F_+=h_+/A_+,
\qquad
F_\times=h_\times/A_\times.
\]

应对两组独立入射基矢计算完整 `2×2` 复传递矩阵：

\[
\begin{pmatrix}h_+\\h_\times\end{pmatrix}_{\rm out}
=
\mathbf F
\begin{pmatrix}A_+\\A_\times\end{pmatrix}_{\rm in}.
\]

然后验证 polarization-basis rotation covariance，并输出：

- singular values；
- `tr(F†F)`；
- helicity mixing；
- basis-dependent matrix elements。

绝对相位必须显式冻结：

- tortoise coordinate additive constant；
- coordinate/retarded time origin；
- incident-wave baseline；
- Coulomb/long-range phase subtraction。

只有相位参考冻结后，Fig.5/6 的约 `0.417 rad` 残差才有明确物理意义。

### Gate V6：误差预算与 release policy

每个正式结果必须分别报告：

```text
Numerical uncertainty:
  lmax
  r_in
  r_out
  Jost order
  ODE tolerance
  arithmetic precision
  axis limit
  backend difference

Convention/observable spread:
  observer
  tetrad
  polarization basis
  phase origin
  total/scattered definition
```

不再给整个项目一个笼统 GREEN，而是为每个 observable 和参数域给出 validity certificate。

## 8. 推荐实施顺序

```text
P0: V0 provenance cleanup
P0: V1 radial/flux/high-ell independent validation
P1: V2 gauge-invariant asymptotic waveform
P1: V3 analytic and literature benchmarks
P2: V4 finite-radius operational observer response
P2: V5 polarization matrix and phase closure
P3: V6 release/uncertainty framework
```

在 V1–V3 完成之前，不建议重新大规模生成 Li 八幅图；这些图保留为 secondary regression suite 即可。

## 9. 最终科学判断

当前数据支持以下陈述：

> SchWO 已经可靠地实现了 Schwarzschild RW/Zerilli 散射问题的核心结构，并在普通模域通过了很强的外部 S-matrix 验证。它的 direct metric-curvature 路线能够给出定义清楚的、RW gauge 与指定 observer frame 下的有限半径潮汐响应。

当前数据还不支持以下更强陈述：

> SchWO 已经在全部生产高 `ell` 域得到独立验证，或者其有限半径 `h_+,h_×` 是不依赖 gauge、observer 和 tetrad 的唯一物理波形。

下一阶段应以通量、外部 MST/直接积分、无穷远 gauge-invariant waveform、经典低频/高频 benchmark 和操作性 detector response 为主，而不是继续把 Li 图像相似度当成唯一真值标准。
