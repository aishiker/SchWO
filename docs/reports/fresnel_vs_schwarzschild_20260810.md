# 标准点质量 Fresnel 响应与 Schwarzschild 自旋-2响应的比较

日期：2026-08-10

## 1. 比较对象

本报告使用标准点质量 Fresnel 放大因子

```text
F_Fr = exp(-pi*gamma/2)
       * (-gamma)^(-i*gamma)
       * Gamma(1+i*gamma)
       * 1F1(-i*gamma; 1; -i*gamma*eta^2),
gamma = -2Mk,
eta = 0.5*sqrt(r/M)*tan(theta).
```

这里采用 `exp(-pi*gamma/2)`，即标准点质量轴上恒等式和 Li 文 Fig.5/6
曲线所要求的符号；**没有**采用 Li--Hou--Zhao v1 Eq. (47) 正文中不自洽的
`exp(+pi*gamma/2)`。后者在 `gamma=-2Mk` 时会额外产生指数压低，不能通过
独立轴上恒等式，也不能复现论文自己的虚线。

Schwarzschild 参考量仍是纯 `+` 和纯 `x` 入射下的对角直接曲率响应：

```text
RW/Zerilli master variables
-> RW-gauge metric perturbation
-> linearized Riemann tensor
-> static orthonormal observer tidal response
-> F_Schw,+ and F_Schw,x.
```

它是 gauge、观测者标架和线性扰动模型限定下的高保真参考，不是无条件的绝对
真值。Fresnel 是偏振无关的标量薄透镜结果，因此同一个 `F_Fr` 分别与两种
Schwarzschild 偏振比较。

## 2. 采样与误差定义

比较覆盖 `kM=0.1,0.2,...,4.0` 和八个 `z/M=30` 的 Table-I 空间点，共
`40x8` 个复数样本。未使用插值、平滑或拟合。误差定义为

```text
amplitude residual = abs(abs(F_Fr/F_Schw)-1),
phase residual     = abs(arg(F_Fr/F_Schw)),
complex residual   = abs(F_Fr/F_Schw-1).
```

另允许在每个频率上乘一个对八个空间点共同的单位模复相位，再计算 aligned
complex residual。它只消除整体相位/时间原点 convention，不调整振幅，也不
改变空间点之间的相对相位。

## 3. Fresnel--Schwarzschild 数值结果

下表给出八个空间点的平均复相对差。括号内是去掉每频率一个共同相位后的值。

| `kM` | `lambda/r_s=pi/(kM)` | `+`：raw（aligned） | `x`：raw（aligned） |
|---:|---:|---:|---:|
| 0.1 | 31.416 | 0.057（0.044） | 0.052（0.038） |
| 0.3 | 10.472 | 0.177（0.111） | 0.153（0.090） |
| 0.5 | 6.283 | 0.238（0.102） | 0.231（0.115） |
| 1.0 | 3.142 | 0.500（0.117） | 0.499（0.124） |
| 1.6 | 1.963 | 0.722（0.187） | 0.742（0.227） |
| 3.1 | 1.013 | 1.152（0.468） | 1.171（0.470） |
| 3.2 | 0.982 | 1.207（0.413） | 1.219（0.425） |
| 4.0 | 0.785 | 1.565（0.425） | 1.548（0.441） |

全部 320 个样本的汇总为：

| 偏振 | 平均振幅差 | 平均相位差 [rad] | 平均复差 | aligned 平均复差 |
|---|---:|---:|---:|---:|
| `+` | 0.147 | 0.864 | 0.833 | 0.305 |
| `x` | 0.176 | 0.860 | 0.843 | 0.338 |

所以：

1. 在 `kM=0.1` 的极长波端，Fresnel 与 Schwarzschild 仍只差约 `5%`；
2. 随频率增加，raw 复差持续增长；
3. 在 `lambda~r_s` 的 `kM=3.1--3.2`，raw 平均复差为 `1.15--1.22`；
4. 去掉一个共同相位后仍有约 `0.41--0.47` 的平均差异，说明 Fresnel 的空间
   振幅和相对相位结构也没有完全对上 Schwarzschild，但它的主要 raw 误差中
   确实包含一个很大的频率依赖整体相位。

## 4. 与 RS-I 结果并列

为避免把“更严格的自由传播核”等同于“更接近 Schwarzschild”，同图保留了
物理 Cartesian RS-I 的结果：

| 偏振 | 模型 | 全样本 raw 平均复差 | 全样本 aligned 平均复差 |
|---|---|---:|---:|
| `+` | Fresnel | 0.833 | 0.305 |
| `+` | RS-I | 0.708 | 0.499 |
| `x` | Fresnel | 0.843 | 0.338 |
| `x` | RS-I | 0.729 | 0.530 |

这说明两个不同问题：

- 若保留当前绝对相位 convention，RS-I 的 raw 复差较小；
- 若允许消除一个每频率共同的整体相位，Fresnel 的空间响应形状反而更接近
  Schwarzschild；
- Fresnel 的平均振幅差也较小：`0.147/0.176`，而 RS-I 为
  `0.190/0.218`；
- RS-I 的 raw 平均相位差较小：约 `0.69 rad`，而 Fresnel 约 `0.86 rad`。

因此不能笼统地说 RS-I “修正后显著更接近 Schwarzschild”。RS-I 数学上修复
的是 Kirchhoff 边界条件与 paraxial 自由传播近似，但它仍传播同一个标量弱场
薄相位屏；它没有补入 Schwarzschild 势垒、视界边界条件和 spin-2偏振输运。
Fresnel 在 aligned 空间结构上更接近，也可能部分来自其 `eta` 坐标、Coulomb
相位 convention 与当前有限半径 Table-I 几何之间的匹配；这不是 Fresnel 在
物理上比 RS-I 更完整的证明。

在 `lambda~r_s` 附近尤其明显：

| `kM` | Fresnel `+` raw/aligned | RS-I `+` raw/aligned | Fresnel `x` raw/aligned | RS-I `x` raw/aligned |
|---:|---:|---:|---:|---:|
| 3.1 | 1.152 / 0.468 | 0.832 / 0.921 | 1.171 / 0.470 | 0.817 / 0.885 |
| 3.2 | 1.207 / 0.413 | 0.812 / 0.757 | 1.219 / 0.425 | 0.843 / 0.757 |

## 5. 数值核验

- 以 50 位精度重新计算全部 Fresnel 点，与保存数组的最大相对差为
  `1.17e-16`；
- Schwarzschild `r_out` 外推最大不确定度为 `8.42e-4`；
- Schwarzschild 最后两组 `lmax` 的最大相对变化为 `4.53e-10`；
- static 与 Li-literal 两种 Schwarzschild 观测者标架的最大复差为 `6.67e-2`。

因此高频端 `0.4--1.2` 量级的模型差异远大于当前已量化的数值误差和标架
系统差。

## 6. 物理结论

标准 Fresnel 结果在极长波端可作为 Schwarzschild 响应的几个百分点级近似，
但当波长下降到黑洞尺度时，它的绝对复相位明显失配。允许消除一个整体相位后，
其空间结构仍保留约 `40%--50%` 的平均差异。

Fresnel 与 RS-I 各自在不同诊断量上更接近 Schwarzschild，表明当前主要限制
不是单独的 Fresnel 传播核，而是二者共有的标量弱场薄相位屏模型。若目标是
黑洞尺度附近的引力波散射，Schwarzschild spin-2 边值问题仍是更合适的主参考。

## 7. 文件

- 数值数组：
  `runs/phase5/paper_figures/fresnel_vs_schwarzschild_20260810_v2/fresnel_vs_schwarzschild_arrays.npz`
- 机器可读报告：
  `runs/phase5/paper_figures/fresnel_vs_schwarzschild_20260810_v2/comparison_report.json`
- 600 dpi 图：
  `runs/phase5/paper_figures/fresnel_vs_schwarzschild_20260810_v2/fresnel_rs_vs_schwarzschild_summary.png`
- 矢量图：
  `runs/phase5/paper_figures/fresnel_vs_schwarzschild_20260810_v2/fresnel_rs_vs_schwarzschild_summary.pdf`
- 复算脚本：`scripts/compare_fresnel_schwarzschild.py`
