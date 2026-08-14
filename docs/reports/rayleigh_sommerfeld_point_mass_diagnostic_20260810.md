# 点质量引力相位屏的 Rayleigh--Sommerfeld 诊断

日期：2026-08-10

## 1. 结论先行

1. **“Kirchhoff 衍射理论数学上不自洽”需要加限定。** Green 定理给出的完整 Kirchhoff 曲面积分本身是严格恒等式；经典孔径问题中不自洽的是所谓 Kirchhoff 孔径边界假设：在不透明屏上同时令场和法向导数为零、在孔径内又同时令二者等于入射场数据。Helmholtz 方程的 Dirichlet 与 Neumann 数据不能这样独立指定。
2. **Rayleigh--Sommerfeld I（RS-I）确实消除了上述孔径边界条件矛盾。** 它只以孔径面上的场作为 Dirichlet 数据，并用半空间 outgoing Green function 传播。
3. **Li--Hou--Zhao 文中标作 Kirchhoff 的式 (47)，并不是黑屏开孔的边值问题。** 它是弱场、标量、薄透镜、近轴条件下的 Fresnel 相位屏积分。因此，把自由传播从 Fresnel 改成 RS-I，只能修正球面距离、倾斜因子和倏逝分量；它不能补回 Schwarzschild 长程势、黑洞强场核心，也不能描述自旋 2 偏振输运。
4. 对同一个点质量相位屏完成的稳定 RS-I 计算显示：**在本模型中，波长趋于无穷（`kM -> 0`）时 RS-I 与 Fresnel 的差异反而趋于零，而不是单调增大。** 原因是相位屏本身同时趋于透明，两个归一化放大因子都趋于 1。
5. RS-I 对已有 Fig. 5/6 推断散射数据的振幅平均距离仅有小幅改善，但相位和完整复振幅整体并未改善。因此，**不能把 Fig. 5/6 的主要不一致归因于 Kirchhoff 孔径边界条件，也不能用 RS-I 替换后就宣称问题已解决。**

## 2. 数学区分

### 2.1 完整 Kirchhoff 曲面积分

对满足 Helmholtz 方程的场 `U`，若闭曲面上的 `U` 与 `partial_n U` 是同一个真实解的相容 Cauchy 数据，则 Green 恒等式给出

\[
U(P)=\frac{1}{4\pi}\int_S
\left[U(Q)\,\partial_n G(P,Q)-G(P,Q)\,\partial_nU(Q)\right]\,dS_Q,
\qquad
G=\frac{e^{ikR}}{R}.
\]

这一步没有数学矛盾。矛盾来自传统 Kirchhoff 孔径近似对屏面数据的额外指定，而不是来自 Green 恒等式。

### 2.2 RS-I 半空间传播

RS-I 只把平面 `z=0` 上的场 `U_L(rho)` 作为输入。采用 `exp(-i omega t)` 约定，其无歧义的角谱形式为

\[
U(\boldsymbol{x},z)=
\int\frac{d^2q}{(2\pi)^2}\,
\widetilde U_L(\boldsymbol q)
e^{i\boldsymbol q\cdot\boldsymbol x}
e^{iz\sqrt{k^2-q^2}},
\]

其中

\[
\sqrt{k^2-q^2}=i\sqrt{q^2-k^2}\qquad(q>k)
\]

取 outgoing 倏逝支。这里保留了 Fresnel 近似所舍去的精确纵向波数和 `q>k` 倏逝波。

## 3. 本次实际计算的模型

为了只检验“把 Li 的自由传播从 Fresnel 换成 RS-I”这一件事，保持其余相位屏假设不变：

\[
U_L(\rho)=\left(\frac{\rho}{\rho_E}\right)^{-4ikM},
\qquad
\rho_E=\sqrt{4Mz}.
\]

径向 Hankel 变换可以解析完成，剩下传播和倏逝两段一维积分。结果除以无透镜平面波 `exp(ikz)`。传播积分先减去渐近平面波项，再解析加入其 Abel 尾积分；这避免了小 `kM` 时直接振荡积分出现的伪零点。

计算范围：

- `kM = 0.001 ... 4`，共 57 个频点；
- Li Table-I 的 8 个观测点；
- 主比较采用与式 (47) 的无量纲像坐标严格相同的几何嵌入：`z_RS=r`、`x_RS=r tan(theta)`；
- 另以 `z_RS=30M`、`x_RS=x_Table-I` 检验几何解释的不唯一性；
- 主计算 40 位十进制精度，独立复算 50 位；最大绝对差 `6.28e-16`，最大相对差 `6.47e-16`。

这是**标量弱场相位屏诊断**，不是新的 Schwarzschild 自旋 2 解。

## 4. 数值结果

### 4.1 长波区

对 8 个观测点取最大误差：

| `kM` | 最大振幅相对差 | 最大相位差 | 最大复振幅相对差 | 最大倏逝分量占比 |
|---:|---:|---:|---:|---:|
| 0.001 | 0.275% | 0.00465 rad | 0.539% | 1.19% |
| 0.00562 | 1.12% | 0.0102 rad | 1.51% | 3.19% |
| 0.01 | 1.61% | 0.0112 rad | 1.95% | 3.92% |
| 0.1 | 3.23% | 0.0300 rad | 3.57% | 2.47% |

因此，在本点质量相位屏模型中，`kM <= 0.1` 的 RS-I 修正至多约为复振幅的 3.57%，并在 `kM -> 0` 时趋于零。

这并不否认“有限孔径尺寸与波长相当时，Kirchhoff 孔径假设可能恶化”。经典孔径中 Kirchhoff--RS 差异是从孔径边缘发出的 boundary wave，取决于孔径尺度/波长和观测方向。当前引力相位屏既没有有限黑屏，也没有有限孔径边缘，所以不能直接套用该单调长波直觉。

必须注意尺度约定。若 `k=2 pi/lambda` 且 Schwarzschild 半径 `r_s=2M`，则

\[
\frac{\lambda}{r_s}=\frac{\pi}{kM}.
\]

所以 `lambda=r_s` 对应 `kM=pi`，而不是 `kM << 1`。主网格 `0.001 <= kM <= 4` 实际覆盖 `0.785 <= lambda/r_s <= 3142`。在额外计算的精确波长比锚点上，8 个 Table-I 点的最大误差为：

| `lambda/r_s` | `kM` | 最大振幅相对差 | 最大相位差 | 最大复振幅相对差 | 最大倏逝分量占比 |
|---:|---:|---:|---:|---:|---:|
| 1 | pi | 44.2% | 0.535 rad | 51.2% | 0.047% |
| 2 | pi/2 | 26.9% | 0.193 rad | 34.6% | 0.066% |
| 10 | pi/10 | 7.29% | 0.0909 rad | 9.12% | 0.688% |
| 100 | pi/100 | 2.65% | 0.0110 rad | 2.77% | 4.29% |
| 1000 | pi/1000 | 0.726% | 0.00839 rad | 1.11% | 2.40% |

`lambda=r_s` 时，光轴上的复振幅差为 20.8%，而表中 51.2% 是 8 个点中的最坏离轴值。该尺度上倏逝分量极小；大差异主要来自非近轴传播相位，而不是近场倏逝波。

### 4.2 中高频和离轴点

RS-I 与 Fresnel 的差异随非近轴几何和累积相位增强：

| `kM` | 最大振幅相对差 | 最大相位差 | 最大复振幅相对差 |
|---:|---:|---:|---:|
| 0.5 | 13.8% | 0.0815 rad | 14.4% |
| 1 | 18.6% | 0.245 rad | 25.0% |
| 2 | 30.1% | 0.271 rad | 38.2% |
| 4 | 33.7% | 0.508 rad | 53.0% |

全网格的最大复振幅差为 75.9%。远离光轴时，两种三维几何嵌入本身的差异也可以达到 `O(1)`，说明薄透镜式 (47) 在大角度下并没有唯一的“RS 替换”。

### 4.3 对 Fig. 5/6 的影响

把 Fig. 5/6 中原有的 Fresnel--Kirchhoff 虚线换成上述 RS-I 虚线，并与项目中已有的推断自旋 2 散射曲线比较。以下是全部 8 个点、全部 40 个 `kM=0.1...4` 样本的平均距离：

| 偏振 | 基线 | 振幅 MAE | 圆周相位 MAE | 复振幅平均相对距离 |
|---|---|---:|---:|---:|
| `+` | Fresnel | 0.4798 | 1.472 rad | 1.538 |
| `+` | RS-I | 0.4625 | 1.530 rad | 1.572 |
| `x` | Fresnel | 0.4547 | 1.462 rad | 1.464 |
| `x` | RS-I | 0.4388 | 1.522 rad | 1.487 |

RS-I 使振幅 MAE 下降约 3--4%，但相位误差增大，完整复振幅距离也略增。因此 Fig. 5/6 的差异主要仍来自：

- 标量薄透镜相位屏与完整 Schwarzschild 波散射不是同一个物理问题；
- 薄透镜近似没有黑洞近区和长程势的完整传播；
- 它不携带 `+`/`x` 偏振的曲率散射与输运；
- 大角度下二维像坐标到三维 RS 几何的解释不唯一；
- 相位零点与观测 tetrad/frame 约定仍需单独固定。

## 5. 可复查文件

- 实现：`src/schwgw/scattering/rayleigh_sommerfeld.py`
- 单元测试：`tests/unit/test_rayleigh_sommerfeld.py`
- 全范围计算与绘图：`scripts/render_rayleigh_sommerfeld_point_mass_diagnostic.py`
- Fig. 5/6 对照绘图：`scripts/render_fig56_rayleigh_sommerfeld_diagnostic.py`
- 通过数值审计的数据：`runs/phase5/paper_figures/rayleigh_sommerfeld_point_mass_diagnostic_20260810_v3/`
- Fig. 5/6 RS 对照：`runs/phase5/paper_figures/fig56_rayleigh_sommerfeld_diagnostic_20260810/`

前两次直接振荡积分留下的目录 `..._20260810/` 和 `..._20260810_v2/` 含小频率伪零点，只作为失败数值尝试保留，不得作为科学结果引用。

## 6. Gondran--Gondran (2010) 对本项目的帮助与边界

新增参考文献 `references/papers/gondran2010.pdf` 在其式 (1) 中采用实空间 RS-I 核

\[
\frac{e^{ikR}}{R}\left(1-\frac{1}{ikR}\right)\cos\theta.
\]

这与本项目当前使用的 exact angular-spectrum RS-I 是同一个半空间传播问题的两种表示。它对项目有三项明确用途：

1. 可把有限、平滑截断的相位屏同时送入实空间式 (1) 和角谱实现，形成独立的归一化、outgoing branch 和近场交叉验证。
2. 其 `1/(ikR)` 项明确标出了近场修正尺度。当前观测距离约 `30M`；当 `lambda=r_s` 时 `kR` 约为 94，该项只有约 1%，而 `lambda=100 r_s` 时它成为 `O(1)`。本项目的角谱计算已经隐式完整保留该项。
3. 论文由相位梯度构造能流线，可作为 Poisson spot 和波前弯曲的标量可视化诊断。

但该文研究的是无引力真空中的圆孔、圆盘和双缝，主要示例取 `lambda/R=0.1` 或更小；它没有研究 `lambda` 与黑洞半径相当的曲率散射。其能流线也不能在 `lambda ~ r_s` 时直接解释为引力波射线：这一区域不满足高频 Isaacson/几何光学条件，并且标量模型没有自旋 2 偏振。黑洞视界也不能用 Babinet 原理当作普通不透明圆盘处理。

## 7. 参考依据

- E. Wolf and E. W. Marchand, *Comparison of the Kirchhoff and the Rayleigh--Sommerfeld Theories of Diffraction at an Aperture*, JOSA 54, 587 (1964), https://doi.org/10.1364/JOSA.54.000587 。该文把两种孔径理论之差解释为边缘发出的 boundary wave，并说明大孔径、远场、中等角度时差异很小。
- R. Takahashi and T. Nakamura, *Wave Effects in Gravitational Lensing of Gravitational Waves from Chirping Binaries*, https://arxiv.org/abs/astro-ph/0305055 。这是标准薄透镜引力波光学的代表性推导。
- E. Bruyere, G. Cusin and C. Pitrou, *Beyond-eikonal diffraction integral in gravitational lensing*, https://arxiv.org/abs/2607.24723 。该文明确把通常的引力衍射积分视为完整 Kirchhoff 曲面积分的近似求值，并系统追踪 beyond-eikonal 修正。
- Z. Li, S. Hou and W. Zhao, *Gravitational Lensing of Gravitational Waves: Spin-wave Optics through Black Hole Scattering*, https://arxiv.org/abs/2512.23933 。作者自己也把高频差异归因于传统 Kirchhoff 薄透镜积分遗漏长程引力效应与偏振演化。
- M. Gondran and A. Gondran, *Energy flow lines and the spot of Poisson--Arago*, Am. J. Phys. 78, 598 (2010), https://doi.org/10.1119/1.3291215 。该文给出实空间 RS-I 核并用相位梯度构造标量能流线。
