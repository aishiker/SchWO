# SchWO 对 Li–Hou–Zhao 8 幅图复刻结果的独立审查

日期：2026-08-02

审查对象：`SchWO_source.zip` 解压后的代码、测试、保存数值数据和 `artifacts/figures-20260801/` 图像；参考论文为 arXiv:2512.23933v1。

## 结论摘要

| 对象 | 主要判断 | 置信度 |
|---|---|---:|
| Fig.1 | 径向方程、归一化和 exact-vs-asymptotic 主体实现基本可信 | 高 |
| Fig.2，尤其 kM=2、θ=π/6 | 项目得到的有限饱和值更符合有限半径高-ℓ物理；论文中约 10 个数量级的跃升很可能是论文数值/作图异常 | 较高，但仍建议独立高精度 spot check |
| Fig.3–4 | 当前结果不是论文 observable convention 的严格实现；主要问题在 Weyl 全五分量和正频率极化桥，而不是 RW/Zerilli 径向求解 | 高 |
| Fig.5–6 Kirchhoff 虚线 | 论文 Eq.(47) 与论文曲线互相矛盾；代码忠实实现了印刷公式，因此曲线错误。Eq.(47) 指数符号大概率是排版错误 | 极高 |
| Fig.5–6 BH-scattering 点 | 当前项目的极化输出层有实质性缺陷/未闭合；不能据此判论文精确点错误 | 高 |
| Fig.7 | 依赖同一 full-Weyl/observable 桥，当前只能视为内部 diagnostic | 高 |
| Fig.8 | Appendix D/E series reduction 结构基本正确；差异主要来自项目自加的有限-r_out 修正和数值/解析高-ℓ尾匹配，而不是明确的论文错误 | 高 |

## 一、审查范围与独立检查

### 代码与数据

重点检查：

- `src/schwgw/paper_figures/li_hou_zhao.py`
- `src/schwgw/scattering/weyl.py`
- `src/schwgw/scattering/partial_wave.py`
- `src/schwgw/scattering/observables.py`
- `src/schwgw/scattering/kirchhoff.py`
- `src/schwgw/scattering/asymptotic.py`
- `src/schwgw/io/asymptotic.py`
- `tests/unit/test_kirchhoff.py`
- `tests/unit/test_weyl_modes.py`
- `artifacts/figures-20260801/figure1` 至 `figure8`

独立执行的 focused tests：

```text
48 passed, 2 subtests passed
```

覆盖 asymptotic scattering、Fig.8 I/O、Kirchhoff、polarization、transmission 和 Weyl 模块。需要强调：这些测试主要证明“代码对自身冻结公式的一致性”，并不自动证明“与论文真实计算一致”。

完整测试套件在本次审查设置的 120 秒上限内未跑完，因此本报告不声称独立完成了 full-suite 验证。

## 二、Fig.2：最后一个子图为什么差得最明显

### 2.1 项目真正计算了什么

`compute_strict_np_psi4_convergence` 直接计算 Kinnersley tetrad 下的 strict `Psi4`：

```text
radial RW/Zerilli solution
→ metric reconstruction
→ weyl_mode_components
→ sum Psi4 over m and parity
```

它发生在 incident-tetrad transform、Route-B tidal packaging 和 `h_plus/h_cross` 提取之前。因此，阶段 3 的 packaged-polarization 问题不能解释 Fig.2 的差异。

### 2.2 保存数据的高-ℓ行为

在 `r=60M`、`kM=2`、`theta=pi/6`：

```text
最终 log10|Psi4| = 0.2772768631
最大值             = 0.3853415335，出现在 ell=79
```

代表性 shell：

```text
ell=110  |Delta Psi4_l| = 2.43e-1
ell=120  |Delta Psi4_l| = 2.52e-1
ell=130  |Delta Psi4_l| = 1.90e-4
ell=140  |Delta Psi4_l| = 1.38e-4
ell=153  |Delta Psi4_l| = 1.98e-8
ell=180  |Delta Psi4_l| = 3.98e-18
```

这正是有限半径 partial-wave 在 `ell` 超过局部传播阈值 `ell ~ kr=120` 后应出现的衰减。

论文最后一图的蓝线却在 `ell~90–130` 上升约 10 个数量级，然后保持巨大平台。它与同文“finite-radius 方法消除高-ℓ过估和发散”的叙述存在明显张力。

### 2.3 为什么我更倾向于论文图异常

- 跃升位置跟 `ell~kr` 精确相关，这是 radial outward/inward basis 在转向区病态、渐近展开越界或消去误差爆炸的典型位置。
- 项目 Fig.1 对低/高 `ell` exact-vs-asymptotic 的总体结构复现良好，表明径向层并非全面错误。
- `kM=2` 的异常区主要使用 ordinary `bidirectional_match`，并不是项目后期 Q018 高-ℓ oracle 人为压低结果；Q018 只在更高 `ell` 才介入。
- 对应径向解的 boundary residual 和稳定化 Wronskian/flux diagnostic 是有界的。
- 固定有限 `r` 时，`ell` 大于 `kr` 的模式应进入 evanescent/Bessel-tail 区，不应持续贡献 `10^10` 级总振幅。

### 2.4 尚需补的最终证明

作者未公开 raw data/code。为了把“很可能”升级为“数值上几乎确定”，建议用一个完全独立的任意精度实现检查：

```text
(kM, r/M, theta, ell) = (2, 60, pi/6, 110,120,130,140)
```

采用 60–100 位精度的 Riccati/log-derivative 或高精度双端 BVP，直接比较单壳 `Delta Psi4_l`。在这一步完成前，最严谨表述是：**强证据支持论文 Fig.2 的高频蓝线存在数值/作图问题，而不是 SchWO 程序缺陷。**

## 三、Fig.5/6 Kirchhoff 虚线：可以明确定位的论文公式错误

论文印刷式为

```text
F = exp(pi gamma/2) (-gamma)^(-i gamma) Gamma(1+i gamma)
    1F1(-i gamma,1;-i gamma eta^2),
gamma=-2Mk.
```

`src/schwgw/scattering/kirchhoff.py` 完全照此实现。

在光轴 `eta=0`，幂因子模为 1，利用

```text
|Gamma(1+i gamma)|^2 = pi gamma / sinh(pi gamma)
```

可得印刷式：

```text
|F(0)|^2 = 4 pi Mk / (exp(4 pi Mk)-1).
```

于是：

```text
Mk=0.1  |F|=7.0706e-1
Mk=0.5  |F|=1.0842e-1
Mk=1.0  |F|=6.6199e-3
Mk=2.0  |F|=1.7483e-5
Mk=4.0  |F|=8.6223e-11
```

这正是 SchWO 的黑色虚线快速衰减到零。

但论文 Fig.5 的光轴虚线在 `Mk=4` 上升到约 `7.1`。把指数改为

```text
exp(-pi gamma/2)
```

便得到

```text
|F(0)|^2 = 4 pi Mk / (1-exp(-4 pi Mk)),
```

并且

```text
Mk=4  |F|=7.0898154036,
```

与论文曲线精确同量级。这个负号也是标准点质量波光学 amplification factor 的分支。

因此这里的责任划分非常清楚：

- **程序对论文印刷 Eq.(47) 是正确的。**
- **论文 Eq.(47) 的指数符号大概率写反了。**
- **论文作图大概率使用了正确的负号公式。**

当前 `test_kirchhoff.py` 只是再次用同一个正号表达式生成 oracle，因此会把这个论文排版错误锁成“测试通过”。测试应改为增加独立的光轴解析恒等式，并同时保留 `literal_paper_v1` 与 `standard_point_mass` 两种显式 convention。

## 四、Fig.5/6 精确 scattering 点：主要是项目 observable 层的问题

### 4.1 当前 production 链

```text
RW/Zerilli modes
→ Kinnersley strict NP quintuple
→ incident tetrad
→ full-NP-to-electric-tidal pseudoinverse
→ E_xx,E_xy
→ h_plus=2E_xx/k^2, h_cross=2E_xy/k^2
```

Route B 的最后一步本身物理上合理；问题是它依赖**全部五个 strict NP scalars 都正确**。

### 4.2 `Z1/Z0` 不是论文 Eq.(35g-h) 的实现

`src/schwgw/scattering/weyl.py` 明确写道，为保持正频率复振幅线性，把论文带星号的关系改成：

```text
Z1 = (2/f) Z3
Z0 = (2/f)^2 Z4
```

而没有复共轭。

这个改动不是普通代码优化，而是对论文物理约定的实质改写。论文 Eq.(42) 是 real-time `Re/Im` 关系；若要转换成单边正频率复振幅，必须显式处理 `(-k,-m)` reality partner。论文 v1 没有把这条桥写完整，项目也没有完整推导，而是先选择了一个线性替代。

### 4.3 flat diagnostic 实际掩盖了 raw lower-Weyl 错误

`compute_flat_no_lens_partial_wave_strict_np_weyl` 并不是直接验证 raw 五分量。它调用 `_complete_flat_type_n_kinnersley_weyl`：

- 保留 raw `Psi3/Psi4`；
- 把 raw `Psi0/Psi1/Psi2` 丢弃；
- 用最小二乘强制补出一个 incident-frame type-N 场。

独立 flat-space probe（`k=0.5,r=20,lmax=40,A_plus=1,A_cross=0`）得到：

```text
theta=0.4:
  raw full-quintuple relative error       = 1.186e-1
  raw transformed Psi4 relative error    = 1.756e-2
  type-N-completed full error             = 2.09e-15

theta=1.0:
  raw full-quintuple relative error       = 9.624e-1
  raw transformed Psi4 relative error    = 3.402e-1
  type-N-completed full error             = 1.92e-15
```

也就是说，现有 flat tests 的 machine-precision pass 主要证明“补全器能把结果投影回预期 type-N 空间”，并没有证明 production 所依赖的 raw `Psi0...Psi4` 正确。

### 4.4 Fig.5/6 数据的直接症状

在第一个 Table-I 点、`kM=0.1`：

```text
SchWO |F_plus|  = 0.6337
SchWO |F_cross| = 1.2788
```

论文中两种极化点基本重合。到高频，SchWO 的 cross 通道约为 plus 的两倍，正好对应图像中最明显的偏差。

这类差异无法用 `lmax`、绘图 DPI 或 Kirchhoff baseline 解释，因为它发生在 BH-scattering 实线数据本身。

### 4.5 责任判断

- 项目 RW/Zerilli 径向层并非首要嫌疑。
- 项目 full-Weyl / positive-frequency / polarization bridge **尚未闭合，属于实质性程序设计缺陷**。
- 论文自身也有约定欠说明：Eq.(35g-h) 的星号与单频正频率数据、Eq.(42) 的 real-time `Re/Im` 如何组合，没有给出可直接编码的完整 `(-k,-m)` 规则。
- 因此，现阶段不能据 SchWO 的 Fig.5/6 实点差异认定作者的 BH-scattering 数据错误。

最稳的修法不是继续调 `Psi0_pack/Psi4_pack`，而是：

1. 从 RW-gauge metric components 直接计算线性化 Riemann/Weyl tensor；
2. 在 incident Cartesian orthonormal tetrad 中直接投影 `E_xx`、`E_xy`；
3. 由 `h_plus=2E_xx/k^2`、`h_cross=2E_xy/k^2` 输出；
4. 把 NP quintuple 仅作为独立交叉校验。

备选方案是完整推导并实现 `(+k,m)` 与 `(-k,-m)` 的 reality bridge，但工程风险更高。

## 五、Fig.8：算法主体没坏，差异来自高-ℓ相移输入不是作者原始数据

### 5.1 Appendix D/E 实现

项目正确实现了：

- even/odd phase-factor combinations；
- helicity-preserving / reversing matrix entries；
- Eq.(E5) series-reduction recursion；
- `d sigma/d Omega = |M22|^2+|M12|^2`。

### 5.2 项目额外做了论文没有声明的处理

当前 Fig.8 不是纯 direct numerical phase-shift 结果。它采用：

```text
numerical phases through ell=180
→ exp[-i ell(ell+1)/(k r_out)] finite-r_out correction
→ Poisson-Sasaki/Dolan Coulomb/MST large-ell tail
→ raised-cosine overlap blend
→ output ell=502, common target ell=500
```

重叠区最大相位残差约 `0.03–0.067 rad`。这是合理的数值工程，但它不可能与作者未公开的 phase-shift sequence 逐点相同。

### 5.3 真正的收敛情况

现有 metadata 中把 q=0、q=1、q=2 的最大变化混成一个数，因而显示约 `0.9999`，容易误判整个 Fig.8 不收敛。把 reduction order 分开后，在 `theta/pi>=0.2` 的 `ellmax 402→502` 比较中：

```text
q=2 normalized max change:
  kM=0.5  4.55e-7
  kM=1.0  1.02e-6
  kM=1.5  1.21e-6
  kM=2.0  3.32e-6
```

q=1 也大体稳定，局部大 relative error 主要出现在曲线零点附近；q=0 本来就是未 regularize 的 cutoff-dependent 点云，外观对 `ellmax` 极其敏感。

### 5.4 责任判断

- **没有证据表明论文 Fig.8 本身算错。**
- SchWO 的 red/green regularized curves 已相当接近论文，主体算法可信。
- 蓝色 q=0 点云差异不具有很强物理意义，因为它本来就不收敛。
- 残余差异主要归因于项目的 high-ell tail、finite-r_out phase correction、cutoff 和采样网格不同。

要严格复刻，应使用作者相同的 `ellmax`、`r_out`、phase extraction 和原始 phase shifts；或者独立把 numerical/MST phase shifts 直接推进到足够高 `ell`，取消经验 blend。

## 六、逐图责任表

| Figure | 主要差异源 | 程序缺陷 | 论文问题 |
|---|---|---:|---:|
| 1 | 轻微绘图/参数差 | 小 | 无明显证据 |
| 2 | 高频 `theta=pi/6` 高-ℓ跃升 | 当前证据不支持 | 很可能有数值/作图异常 |
| 3 | total/scattered surface + 极化桥 | 是 | 约定欠说明 |
| 4 | total/scattered surface + asymptotic baseline | 是/未闭合 | 可能有定义不清，暂无错误证明 |
| 5 | 虚线 Eq.(47)；实点极化桥 | 虚线忠实实现错式；实点有缺陷 | Eq.(47) 符号几乎确定错误 |
| 6 | 同 Fig.5 | 同上 | 同上 |
| 7 | apparent-mode projection 依赖 raw full NP | 是 | 暂无错误证明 |
| 8 | 高-ℓ相移尾、cutoff、采样 | 近似而非根本错误 | 暂无错误证明 |

## 七、最低返工修复顺序

### P0：Kirchhoff convention 修正

新增参数：

```text
prefactor_convention = "standard_point_mass" | "literal_paper_v1"
```

默认用 `standard_point_mass`，同时记录 paper-v1 typo。新增解析测试：

```text
eta=0: |F|^2 = 4*pi*kM/(1-exp(-4*pi*kM))
```

### P0：重做 observable bridge

- 不再从未经验证的 raw lower NP scalars 反推 tidal tensor。
- 从 metric perturbation 直接计算 incident-frame `E_ij`。
- 保留 strict NP 作为独立 output/diagnostic。

### P0：增加能真正抓错的测试

1. flat raw quintuple test：禁止 type-N completion。
2. `phi=0` 反射对称面上的 pure-plus / pure-cross parity test。
3. full real-field `(+k,-k)` reconstruction test。
4. one-point Table-I benchmark，先闭合 `(x,z)=(0,30)M`。

### P1：Fig.2 独立任意精度 probe

只算 8–16 个 `(sector,ell)`，不重跑整图；目标是独立确认 `ell=110–140` 不存在巨大 shell。

### P1：Fig.8 高-ℓ基准

- 分开报告 q=0/q=1/q=2 convergence。
- 扫描 `r_out` 和 overlap window。
- 最终用 direct MST/asymptotic phase solver 替代 raised-cosine empirical blend。

## 八、最终判断

这不是“程序全错”或“作者全错”的二选一：

- **论文存在一个几乎可以确定的公式排版错误：Eq.(47) 指数符号。**
- **论文 Fig.2 的高频蓝线很可能存在数值/绘图异常。**
- **SchWO 对 Fig.5/6 精确点和 Fig.3/4/7 的主要偏差，来自项目尚未物理闭合的 full-Weyl/positive-frequency polarization bridge。**
- **Fig.8 的 series-reduction 主体基本可靠，差异属于高-ℓ相移输入和截断实现不同。**

在没有作者代码或 raw data 的情况下，最合理的下一步是先做低成本的 P0/P1 probes，而不是继续大网格重算。
