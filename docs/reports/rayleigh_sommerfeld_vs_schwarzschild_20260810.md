# Rayleigh--Sommerfeld I 与 Schwarzschild 自旋-2响应的直接比较

日期：2026-08-10

## 1. 结论先行

`F_Schwarzschild` 不能称为不附带条件的“绝对正确结果”。本报告所用结果是：

- 精确 Schwarzschild 背景上的**线性**引力扰动；
- Regge--Wheeler/Zerilli 径向方程；
- Regge--Wheeler gauge 下重建度规扰动与线性化 Riemann 张量；
- 在指定的 `static_orthonormal` 观测者标架中投影潮汐张量；
- 有限半径、有限分波截断的数值解，并使用 Jost `1/r` 外边界级数和
  `r_out/M=(1200,1800,2400)` 外推。

所以更准确的称呼是：**在上述冻结的线性 Schwarzschild 模型、gauge 与
观测者标架内，目前项目中物理结构最完整、数值收敛性最好的参考解**。
它仍不是非线性广义相对论的全局精确解，也不自动等于 Li 文采用的 tetrad
或有限半径响应定义。高 `ell` Q018 径向分支的独立外部验证也尚未覆盖全部
生产域。

尽管如此，逐点比较给出很稳健的物理结论：RS-I 在最低频端与
Schwarzschild 响应较接近；随着 `kM` 增大，二者迅速分离。在
`lambda` 接近 Schwarzschild 半径 `r_s=2M` 时，差异已经是数量级为一的，
而且不能用一个任意整体相位消除。

## 2. 比较的两个量

### 2.1 Schwarzschild 参考响应

对纯 `+` 入射和纯 `x` 入射分别定义

```text
F_Schw,+ = h_+^(pure + input) / (A_+ exp(i k z)),
F_Schw,x = h_x^(pure x input) / (A_x exp(i k z)).
```

其中 `h_+`、`h_x` 不是由 Li 文的 Kirchhoff/Fresnel 表达式构造，而是由

```text
RW/Zerilli master variables
-> RW-gauge metric perturbation
-> linearized Riemann tensor
-> static orthonormal observer-frame tidal tensor
-> h_+, h_x
```

直接得到。在本次八个 `y=0,z/M=30` 的 Table-I 点上，交叉偏振响应恰好为
零，因此纯入射对角响应与同时入射的结果在数值上完全一致。不过，本报告仍
使用纯入射对角响应，因为标量 RS-I 本身没有偏振混合机制。

### 2.2 RS-I 候选响应

RS-I 使用物理 Cartesian 几何 `x/M=(0,1,2,3,10,15,20,25)`、`z/M=30`，
将同一个弱场点质量薄相位屏

```text
U_L(rho) = (rho/sqrt(4 M z))^(-4 i kM)
```

用精确 outgoing Rayleigh--Sommerfeld-I angular spectrum 传播，并除以无透镜
平面波 `exp(i k z)`。这里没有使用 Li Eq. (47) 的坐标 lift，也没有假定 Li
文中的 Fresnel/Kirchhoff `F` 是正确答案。

RS-I 仍然只是标量、弱场、无限薄相位屏模型；它没有 Schwarzschild 强场核、
视界吸收边界条件或 spin-2 偏振输运。因此同一个 `F_RS-I` 分别与
`F_Schw,+` 和 `F_Schw,x` 比较。

## 3. 诊断量

本报告采用

```text
amplitude residual = abs(abs(F_RS/F_Schw) - 1),
phase residual     = abs(arg(F_RS/F_Schw)),
complex residual   = abs(F_RS/F_Schw - 1).
```

另外，在每个频率上只允许乘一个对所有八个空间点共同的单位模复相位，使
平方差最小，再计算 offset-removed residual。它只消除相位零点/传播时间原点
的一项 convention，不会改变空间依赖的相位结构或振幅。

Schwarzschild 数据有 40 个 `kM=0.1,0.2,...,4.0` 样本；RS-I 数据在相同点
直接取值。未使用插值、平滑、拟合或重采样。两套频率的最大浮点表示差为
`4.44e-16`。

## 4. 数值结果

下表给出八个空间点上的统计。`complex mean` 是平均复相对差，
`complex max` 是最大复相对差，`aligned mean` 是去掉每频率一个共同相位后的
平均复相对差。

### 4.1 `+` 偏振

| `kM` | `lambda/r_s=pi/(kM)` | 最大振幅差 | 最大相位差 [rad] | complex mean | complex max | aligned mean |
|---:|---:|---:|---:|---:|---:|---:|
| 0.1 | 31.416 | 0.070 | 0.029 | 0.039 | 0.072 | 0.027 |
| 0.3 | 10.472 | 0.118 | 0.142 | 0.141 | 0.178 | 0.089 |
| 0.5 | 6.283 | 0.150 | 0.263 | 0.197 | 0.267 | 0.131 |
| 1.0 | 3.142 | 0.298 | 0.531 | 0.434 | 0.510 | 0.180 |
| 1.6 | 1.963 | 0.461 | 0.883 | 0.679 | 0.986 | 0.313 |
| 3.1 | 1.013 | 0.789 | 1.701 | 0.832 | 1.523 | 0.921 |
| 3.2 | 0.982 | 0.467 | 1.740 | 0.812 | 1.559 | 0.757 |
| 4.0 | 0.785 | 0.876 | 2.188 | 1.217 | 2.491 | 0.868 |

### 4.2 `x` 偏振

| `kM` | `lambda/r_s=pi/(kM)` | 最大振幅差 | 最大相位差 [rad] | complex mean | complex max | aligned mean |
|---:|---:|---:|---:|---:|---:|---:|
| 0.1 | 31.416 | 0.048 | 0.027 | 0.032 | 0.049 | 0.019 |
| 0.3 | 10.472 | 0.118 | 0.152 | 0.138 | 0.178 | 0.109 |
| 0.5 | 6.283 | 0.229 | 0.264 | 0.220 | 0.267 | 0.156 |
| 1.0 | 3.142 | 0.336 | 0.531 | 0.453 | 0.524 | 0.190 |
| 1.6 | 1.963 | 0.588 | 0.884 | 0.713 | 1.113 | 0.341 |
| 3.1 | 1.013 | 0.295 | 1.701 | 0.817 | 1.545 | 0.885 |
| 3.2 | 0.982 | 0.506 | 1.740 | 0.843 | 1.583 | 0.757 |
| 4.0 | 0.785 | 0.832 | 2.188 | 1.206 | 2.467 | 0.878 |

`lambda=r_s` 对应 `kM=pi`。Schwarzschild 数据没有恰好 `pi` 的样本，且本次
明确禁止插值，因此使用相邻的 `kM=3.1` 和 `3.2`。此处两种偏振的平均复差
约为 `0.81--0.84`，最大复差约为 `1.52--1.58`。去掉一个共同相位后，平均复差
仍约为 `0.76--0.92`。因此偏差不是单纯的整体相位 convention。

某些最大相对差会因参考响应接近局部小值而被放大，所以物理解读不只依赖
`maximum`；平均复差和 offset-removed 平均复差给出同样的数量级结论。

## 5. 与数值误差和标架差异比较

- Schwarzschild `r_out` 外推报告的最大不确定度：`8.42e-4`；
- Schwarzschild 最后两组 `lmax` 的最大相对变化：`4.53e-10`；
- RS-I 高精度重复计算的最大相对差：`6.47e-16`；
- Schwarzschild `static_orthonormal` 与 `li_literal_cartesian` 两种观测者标架
  的最大复差：`6.67e-2`，最大相位差小于 `9.80e-3 rad`。

所以在 `kM` 约为 1 以上，RS-I 与 Schwarzschild 的主要差异远大于当前已量化
的数值误差，也显著大于这两种观测者标架之间的差异。它主要反映两个物理模型
的差别，而不是积分精度、`r_out` 截断或一个简单的 frame 选择。

## 6. 物理解释

当 `kM << 1` 时，波长远大于黑洞尺度，细致的强场结构和偏振输运较不容易被
分辨。弱场薄相位屏加自由空间传播能近似主要相位延迟，因此 RS-I 与
Schwarzschild 在 `kM=0.1` 端只差几个百分点。

当 `lambda` 降至与 `r_s` 同量级时，波开始分辨 Schwarzschild 势垒、视界
边界条件、奇偶宇称通道和 spin-2 偏振结构。RS-I 虽修复了 Kirchhoff 边界条件
不自洽和 paraxial 传播近似，却没有补入这些引力散射物理。因此 RS-I 不能作为
Schwarzschild 自旋-2散射的替代解；它更适合作为“同一弱场相位屏在更严格自由
传播核下会怎样”的独立诊断。

这一判断不要求把 `F_Schwarzschild` 宣称为绝对真值。更谨慎的陈述是：在当前
可验证的线性模型内，Schwarzschild 路线包含更多与黑洞散射直接相关的物理，
而 RS-I 在长波端是合理近似，在 `lambda~r_s` 时出现显著、不可由整体相位消除
的模型偏差。

## 7. 可复核文件

- 数值数组：
  `runs/phase5/paper_figures/rayleigh_sommerfeld_vs_schwarzschild_20260810/rs_vs_schwarzschild_arrays.npz`
- 完整机器可读报告：
  `runs/phase5/paper_figures/rayleigh_sommerfeld_vs_schwarzschild_20260810/comparison_report.json`
- 汇总图（600 dpi PNG / vector PDF）：
  `runs/phase5/paper_figures/rayleigh_sommerfeld_vs_schwarzschild_20260810/rs_vs_schwarzschild_summary.png`
  和 `rs_vs_schwarzschild_summary.pdf`
- 可重复执行脚本：
  `scripts/compare_rayleigh_sommerfeld_schwarzschild.py`

输入 SHA-256：

- Schwarzschild static frame：
  `c6468da4e4f844461a884976a10c5063019b9e74f8ec5a2cd45247dabc9af776`
- Schwarzschild Li-literal frame：
  `a47623535b7b4ae62756c79e80f21f58ca14a0c4e911096efb6d781d73000e55`
- RS-I：
  `3129f6161aefb53c3d424835e9b040fb8a63f3b3e10d3aac3f4e3ac45081a127`
