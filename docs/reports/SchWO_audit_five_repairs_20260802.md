# SchWO 审计后五项科学修复闭合报告

日期：2026-08-02

本报告对应 `audits/SchWO_audit_20260802.md` 与
`audits/SchWO_audit_response_20260802.md` 中尚未闭合的五项工作。所有新计算
均写入新目录；2026-08-01 及更早的 NPZ、JSON 和图像没有被覆盖。

## 1. 直接 observable bridge：已实现

新增的 production 路径为

```text
RW/Zerilli master solution
  -> Appendix-A RW-gauge metric components
  -> metric value/first/second coordinate jets
  -> delta R_abcd on Schwarzschild
  -> static incident-Cartesian orthonormal frame
  -> E_xx = delta R(e_t,e_x,e_t,e_x)
     E_xy = delta R(e_t,e_x,e_t,e_y)
  -> h_plus = 2 E_xx/k^2, h_cross = 2 E_xy/k^2
```

实现位于 `src/schwgw/scattering/metric_curvature.py`。它不再从不可靠的
lower-NP scalar completion 反演 tidal tensor。`strict NP` 只保留为由同一
`delta R_abcd` 独立收缩得到的诊断量。

### 数值微分修复

初版直接桥对 dense ODE interpolation 做二阶有限差分，在高 `ell` 下会把
插值误差放大为 `O(h^-2)`，造成 Fig.4 高频曲线的非物理锯齿。本轮已改为
直接使用 RW/Zerilli 方程

```text
psi''  = p psi' + q psi,
psi''' = (p' + p^2 + q) psi' + (q' + p q) psi,
```

只对平滑的代数重构系数使用 Richardson-extrapolated 五点差分。生产路径
只在 observer anchor 查询 ODE solution，不再对 dense solution 做径向差分。

### 独立测试边界

- flat Cartesian TT wave 的 `delta R_0i0j`；
- 显式 `(+k,-k)` real-field reconstruction；
- flat partial-wave plane-wave recovery；
- pure-plus/pure-cross reflection-plane decoupling；
- `x -> -x` 下六个投影量的精确 parity；
- Table-I 光轴极限；
- curved one-point radial-stencil halving；
- direct `delta R` contraction 与独立 Kinnersley `Psi4` 公式交叉校验；
- ODE solution 只允许在 anchor 被查询。

需要严格区分：这些测试闭合了代码实现和 convention；作者没有公开 raw
observable data，因此它们不能单独证明论文采用了完全相同的 finite-radius
tetrad/normalization convention。

## 2. Fig.2 任意精度独立 spot check：已完成

脚本 `scripts/verify_fig2_high_precision.py` 不调用项目 SciPy radial solver，
而使用 80-digit `mpmath`、tortoise-coordinate RK4、独立 horizon 与 infinity
bases、log-derivative matching、step halving 和四阶 Richardson extrapolation。

冻结 artifact：

```text
runs/phase5/paper_figures/fig2_high_precision_20260802/
  fig2_high_precision_spotcheck.json
SHA-256 801ecbfda75b3cc9526bd9d244c2771e43ef2b46620581c0fb72c9193fca3bcc
```

在 `(kM,r/M,theta)=(2,60,pi/6)`：

| ell | independent shell `|Delta Psi4_ell|` | double-precision relative difference |
|---:|---:|---:|
| 110 | 0.2429801534 | 1.62e-5 |
| 120 | 0.2515841173 | 2.31e-5 |
| 130 | 1.903513530e-4 | 7.08e-6 |
| 140 | 1.383117977e-4 | 1.53e-5 |

因此独立计算排除了论文曲线所暗示的巨大高-`ell` shell。80 digits 是工作
精度，而不是宣称输出有 80 个正确数字；当前离散误差由 coarse/fine 结果
单独记录。可以严谨地说“强证据支持论文 Fig.2 高频 panel 存在数值或作图
异常”，仍不把没有作者 raw data 的因果来源写成已证明事实。

## 3. Fig.8 direct high-ell MST：已完成

新增 `src/schwgw/scattering/mst.py` 和
`scripts/phase5_generate_fig8_direct_mst.py`。最终数据的 `ell=20..502` 来自
直接 MST recurrence/minimal-solution phase 计算；没有 finite-`r_out` phase
offset、raised-cosine overlap 或 empirical blend。

```text
runs/phase5/paper_figures/fig8_direct_mst_20260802/
  fig8_direct_mst_l502_n1440.npz
SHA-256 22924f659f5881f024643d04438a031ee245a82a2091b9ba4c0d94a79e84e141
```

- exact `ell=2..502`；
- direct MST `ell=20..502`；
- 最大 low/direct-MST transition mismatch `1.339e-3`；
- 最大 recurrence residual `1.85e-68`；
- even/odd Starobinsky parity relation 与 unit-modulus gates 通过；
- q=0/q=1/q=2 分开记录，不再把未正则化点云与正则化曲线混成一个
  convergence 数字。

## 4. Fig.3--7 重算：最终 artifact 与数值结果

全部 no-overwrite transactions 已闭合。生产根为

```text
runs/phase5/paper_figures/direct_curvature_odejet_recompute_20260802/
```

Fig.3/7 使用 `241 x 241` 网格；Fig.4 使用每频率 1025 个角点；Fig.5/6
使用论文 Table-I 八个位置和 `kM=0.1,0.2,...,4.0` 的 40 个频率。

### 4.1 Fig.3 与 Fig.7：四个完整网格

四个 XZ-grid transaction 均 natural exit 0；每个网格有 57,884 个 valid
点和 197 个 horizon-mask 点，`x -> -x` parity、mask identity 和最终
`lmax` pair convergence 均通过。Fig.3 / Fig.7 NPZ SHA-256 分别为：

| `kM` | Fig.3 direct curvature | Fig.7 apparent projection |
|---:|---|---|
| 0.5 | `2823065d...95c0` | `a2d106f3...d4dd` |
| 1.0 | `534bc919...fc4` | `6cbd6a38...c5c6` |
| 1.5 | `cd2fd316...458` | `e1c29e06...acf8` |
| 2.0 | `070f2557...e8c1` | `9b12cff6...3e7c` |

Fig.3 的 production PNG 使用论文可见范围 `[-7,7]`；这只改变显示映射，
不修改、截断或重写 NPZ。另存的 nearest-neighbour numerical-audit 图保留
原始 full range，manifest 明确记录 `display_clipping`。

### 4.2 Fig.4：direct-curvature angular recomputation

四个 direct angular NPZ SHA-256 为：

```text
kM=0.5  af045e106d35bdde610c0eefc14716be96157755dcdb6b11c07ebabd11900be8
kM=1.0  a9453786a520dedb822bca7ae802bc20e159586f87fadd052d9a9c6efbc19974
kM=1.5  9e91f635633439914f1dd78f45f71061926ade4a6bd8ee20ef509adc687dc36e
kM=2.0  2f8bcd12d71558d34a2ba4cc7f51c6b4a05acef229ce015c031c797b6ade4b7a
```

逐像素 digitization 只能作为 raster diagnostic，不是作者 raw data。对论文
红/蓝曲线的 mean absolute error（plus / cross）为：

| `kM` | plus MAE | cross MAE |
|---:|---:|---:|
| 0.5 | 0.1840 | 0.06955 |
| 1.0 | 0.1870 | 0.07300 |
| 1.5 | 0.1825 | 0.07281 |
| 2.0 | 0.5574 | 0.2760 |

低三频 morphology 已明显接近原图；`kM=2` 仍有宽谷/平台差异。因此 Fig.4
不能被标记为 strict paper equivalence。定量文件 SHA-256 为
`6d8b8a47044f1c2c96794b6bbd604f60401a293341dc519746759c32a431576a`。

### 4.3 Fig.5/6：40 频率、八位置完整重算

40 个独立 transaction 全部完成并合并为：

```text
fig56_direct_curvature_uniform40.npz
SHA-256 185aefd5622004f28449b4f39b9827d8a862b45f5edb78c4712eed04153bbc2b
shape   (40, 8)
```

所有值 finite；plus/cross 最大最终 `lmax` pair delta 分别为
`5.62e-10` / `4.12e-10`。与同一论文 raster marker 比较：

| 路线 | amplitude MAE | phase circular MAE |
|---|---:|---:|
| old lower-NP completion | 0.528143 | 1.977851 rad |
| direct metric-curvature | 0.173955 | 1.111339 rad |

振幅 MAE 降低约 67%，phase circular MAE 降低约 44%。论文蓝色三角大多
被红色三角覆盖：可分离的 blue remnants 只有 55 个 amplitude 和 5 个 phase
样本；重叠样本的 median red-blue difference 为 0.0772 和 0.1213 rad。
这些结果支持“两偏振在论文 raster 上大量重叠”，但不等于两个模式完全相同。

残余 phase mismatch 随 panel 增大到约 `0.56--1.59 rad`；缺少作者 raw data
时，不能唯一归因于 branch、time convention 或未公开的 finite-radius
polarization convention。定量比较文件 SHA-256 为
`9a0c93cf459502797157d90f694c66a88292db3a9b098013506b9eff951fdd96`。

## 5. 600 dpi 重绘与逐 panel 对照

最终渲染使用保存数据，不在 renderer 内补算科学量。渲染根为：

```text
runs/phase5/paper_figures/audit_repairs_20260802/rendered_odejet_v2/
render_manifest.json
SHA-256 3a167d859b0a2c198df6c84cd63e1badc6a51a47c0bdb67812e06cb6a437b962
```

全部主图同时保存 PDF 和约 600 dpi PNG：

| Figure | PNG dimensions | PNG SHA-256 |
|---|---:|---|
| Fig.3 | 4260 x 2190 | `1dc74cac...f792` |
| Fig.4 | 6900 x 3360 | `8a73ab69...bc84` |
| Fig.5 | 7020 x 3090 | `dde6215e...b1ef` |
| Fig.6 | 7020 x 3090 | `61b34261...f1e` |
| Fig.7 | 4260 x 4980 | `c2a801f7...b6da` |
| Fig.8 | 6840 x 1830 | `e2a54a33...7f9c` |

比较分成：

1. source-bound published-page crop 与新图并排；
2. Fig.4 饱和红/蓝 exact 曲线的 raster digitization；
3. Fig.5/6 红/蓝 triangle raster digitization 与 circular phase metric；
4. Fig.8 direct-MST curve 的视觉和 transition/convergence 双重审计。

比较总 manifest SHA-256 为
`a0040fcd68bd4e869df1a57f60ad261343b7c0d2c004c49fb1d635a53e6ec979`。
人工逐 panel QA 的结论是：Fig.3 和 Fig.8 最接近；Fig.5/6 amplitude
显著改善；Fig.4 `kM=2`、Fig.5/6 phase 以及 Fig.7 longitudinal morphology
仍有明确差异。二者不能混为一谈；残余差异被保留为科学不确定性，没有用
调色、归一化或经验修形隐藏。

## 6. 统一验收、测试与最终状态

统一只读 validator：

```text
runs/phase5/paper_figures/audit_repairs_20260802/
  audit_repairs_validation_odejet.json
SHA-256 f791d88897d9c877f0ec95defc6cfa083a0c683837a36a7e030f7da5f7d308cb
status  PASS
```

验证环境为 Python 3.10.2 / NumPy 2.2.6 / SciPy 1.15.3。实现完成后的完整
project suite 为：

```text
1131 passed, 117 skipped, 1 xfailed, 109 warnings,
104 subtests passed in 664.80s
```

最终 Fig.3 display-window 修正后又运行 focused suite：`22 passed,
34 deselected`；exact CPython 3.14 路径为 `13 passed, 1 skipped`，唯一 skip
是该 runtime 未安装 optional `mpmath` oracle，而不是 production solver
缺失。相关 Python 文件 Ruff PASS，最终 `git diff --check` PASS。

五项整改的工程/计算状态为 **COMPLETE**：direct curvature bridge、Fig.2
任意精度 spot check、Fig.8 direct MST、Fig.3--7 全量重算、600 dpi 重绘与
逐 panel 对照均有 durable artifact。严格的论文等价性仍为 **YELLOW**，原因
是作者没有公开 raw figure data，且 Fig.4 高频、Fig.5/6 phase 和 Fig.7
longitudinal morphology 仍存在可量化差异。该 YELLOW 不否定修复完成，也
不允许把残余差异写成已经解释或已经与论文完全一致。
