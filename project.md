# Schwarzschild 引力波波光学求解器项目设计

项目代号：`schw-gw-waveoptics`

版本：v0.1-design

更新时间：2026-07-05

## 1. 项目目标

本项目的目标是构建一个可验证、可扩展的 Schwarzschild 黑洞引力波波光学数值求解器。首要目标不是逐像素复刻某篇论文的所有图，而是实现一套物理约定清晰、数值流程正确、可复现实验参数扫描的研究代码。若输入与参考论文完全一致的物理参数、截断、网格和绘图约定，程序应自然输出同一物理数据和同类图像。

核心计算对象是 Schwarzschild 背景上的线性引力扰动散射：入射平面引力波经 Regge–Wheeler/Zerilli master equations 求解，再通过有限半径 partial-wave 求和、metric reconstruction、Weyl scalar 重构和 geodesic-deviation 关系得到可观测的 `h_plus` 与 `h_cross` 频域振幅及波场图。

## 2. 物理范围

### 2.1 第一阶段支持

- 背景：Schwarzschild 黑洞，内部单位 `G = c = M = 1`，外部配置使用无量纲量 `kM`、`r/M`。
- 理论：GR 真空 Schwarzschild 黑洞线性扰动。
- 扰动分解：频域 + 张量球谐 + parity-even / parity-odd partial waves。
- 主方程：Regge–Wheeler 方程与 Zerilli 方程。
- 入射波：远源平面引力波，默认沿 `+z` 方向传播，输入复振幅 `A_plus(k)`、`A_cross(k)`。
- 输出：
  - 径向 master variables `psi_odd[l,m](k,r)`、`psi_even[l,m](k,r)`；
  - Weyl scalars `Psi_0 ... Psi_4`；
  - `h_plus(k,r,theta,phi)`、`h_cross(k,r,theta,phi)`；
  - diffraction pattern、finite-radius wave field、transmission factors；
  - partial-wave convergence diagnostics。

### 2.2 明确不在第一阶段支持

- Kerr / Teukolsky spin-weighted spheroidal formalism。
- 非真空、带源项自力问题。
- 新理论引力中的额外极化自动推导。
- 通用静态球对称黑洞的扰动方程自动符号推导。
- 全数值相对论。

## 3. 理论依据和文献角色

本项目以目标论文的有限距离 partial-wave Schwarzschild GW scattering 方案为主线。该论文强调传统渐近展开在 optical axis 和 Poisson spot 附近会发散，因此采用有限距离观测者并放弃径向波函数的渐近展开，从而得到收敛的 partial-wave 描述。其主流程包括：Schwarzschild 背景、tensor-harmonic partial-wave 展开、RW/Zerilli 方程、入射平面 GW 边界条件、metric reconstruction、Weyl scalars、tetrad transformation 和 `+ / cross` 极化提取。

辅助文献定位如下：

- Regge & Wheeler：odd-parity Schwarzschild perturbation 和 Regge–Wheeler 方程的基础。
- Zerilli：even-parity perturbation 的 Schrödinger 型方程与 Zerilli potential。
- Moncrief：gauge-invariant 变量、约束一致性和 Hamiltonian 角度。
- Martel & Poisson：现代 covariant, gauge-invariant Schwarzschild perturbation formalism；明确 even sector 的 Zerilli–Moncrief function 和 odd sector 的 Cunningham–Price–Moncrief function，并给出辐射波形、能量和角动量如何由两个 gauge-invariant scalar functions 表达。
- Pound & Wardell：现代黑洞扰动理论综述；提供不同 tensor bases、RW gauge、metric reconstruction、Teukolsky/RWZ/Lorenz gauge 之间的结构参照。
- Maggiore：GW TT gauge、geodesic deviation、能量流和传播的基础约定，用于解释 `h_plus`、`h_cross` 的物理意义。

## 4. 总体架构

### 4.1 顶层数据流

```text
Config
  ├─ background: Schwarzschild(M)
  ├─ wave: kM, A_plus, A_cross, incident_direction
  ├─ observer_grid: r, theta, phi or x-z plane
  ├─ numerics: lmax, tolerances, r_in, r_out, method
  └─ outputs: fields, diffraction, transmission, diagnostics

Background + Perturbation Model
  ├─ f(r), r_star(r), horizons
  ├─ V_odd(l,r), V_even(l,r)
  └─ reconstruction operators J_a^{odd/even}

Incident Plane GW
  ├─ A_L, A_R from A_plus, A_cross
  ├─ A_lm^{odd/even}
  └─ c_lm^{odd/even}

Radial Solver
  ├─ solve RW/Zerilli ODE for each (sector,l,m,k)
  ├─ match horizon/infinity boundary conditions
  ├─ compute phase shift, transmission coefficient
  └─ cache radial functions and derivatives

Partial-Wave Assembly
  ├─ spin-weighted harmonics
  ├─ metric reconstruction
  ├─ Weyl scalar assembly
  ├─ tetrad transform
  └─ h_plus, h_cross extraction

Validation + Visualization
  ├─ convergence curves
  ├─ finite-radius field maps
  ├─ diffraction patterns
  ├─ transmission factors
  └─ benchmark comparisons
```

### 4.2 建议仓库结构

```text
schw-gw-waveoptics/
├─ project.md                         # 总项目说明，给人和 Codex 都读
├─ status.md                          # 实时进度记录，所有线程必须更新
├─ README.md                          # 简短入口和安装/运行说明
├─ pyproject.toml                     # Python 包配置
├─ configs/
│  ├─ schwarzschild_fig3_like.yaml
│  ├─ convergence_k1_r60.yaml
│  └─ transmission_scan.yaml
├─ src/schwgw/
│  ├─ __init__.py
│  ├─ types.py                        # dataclasses, complex array types, units
│  ├─ constants.py
│  ├─ backgrounds/
│  │  ├─ base.py                       # StaticSphericalBackground interface
│  │  └─ schwarzschild.py
│  ├─ perturbations/
│  │  ├─ sectors.py                    # Odd/Even sector abstractions
│  │  ├─ potentials.py                 # RW/Zerilli potentials
│  │  ├─ rwz.py                        # master equation definitions
│  │  ├─ reconstruction.py             # J operators and metric components
│  │  └─ conventions.py                # signs, Fourier convention, harmonic convention
│  ├─ waves/
│  │  ├─ incident.py                   # plane GW coefficients
│  │  ├─ polarizations.py              # A_plus/A_cross/A_L/A_R conversion
│  │  └─ rotations.py                  # future: arbitrary incident direction
│  ├─ angular/
│  │  ├─ scalar_harmonics.py
│  │  ├─ spin_weighted.py
│  │  ├─ tensor_harmonics.py
│  │  └─ wigner.py
│  ├─ numerics/
│  │  ├─ radial_solver.py
│  │  ├─ boundary_conditions.py
│  │  ├─ matching.py
│  │  ├─ convergence.py
│  │  └─ cache.py
│  ├─ scattering/
│  │  ├─ problem.py                    # high-level ScatteringProblem
│  │  ├─ partial_wave.py
│  │  ├─ weyl.py
│  │  ├─ tetrad.py
│  │  ├─ observables.py
│  │  └─ transmission.py
│  ├─ viz/
│  │  ├─ fields.py
│  │  ├─ diffraction.py
│  │  ├─ convergence.py
│  │  └─ phase.py
│  └─ io/
│     ├─ config.py
│     ├─ results.py                    # HDF5/NPZ output schema
│     └─ logging.py
├─ tests/
│  ├─ unit/
│  ├─ physics/
│  └─ regression/
├─ benchmarks/
│  ├─ reference_parameters.md
│  └─ reference_data_registry.md
├─ examples/
│  ├─ run_single_frequency.py
│  ├─ plot_wavefield.py
│  └─ scan_transmission.py
├─ notebooks/
│  └─ exploratory_validation.ipynb
├─ docs/
│  ├─ physics_spec.md
│  ├─ equation_map.md
│  ├─ architecture.md
│  ├─ workstreams.md
│  ├─ numerics.md
│  ├─ validation_plan.md
│  ├─ handoffs/
│  │  ├─ README.md
│  │  ├─ T0_current.md
│  │  ├─ T1_current.md
│  │  ├─ T3_current.md
│  │  ├─ T4_current.md
│  │  ├─ T6_current.md
│  │  ├─ T7_current.md
│  │  ├─ T8_current.md
│  │  └─ archive/
│  ├─ extension_interface.md
│  └─ codex_instructions.md
├─ references/
│  ├─ manifest.md                    # 文献用途、优先级、对应模块
│  ├─ papers/                        # 原始 PDF，只作源材料
│  └─ notes/                         # Codex 整理出的公式笔记和 convention 对照
└─ data/
   ├─ raw/
   ├─ processed/
   └─ fixtures/
```

## 5. 核心模块边界

### 5.1 `backgrounds`

职责：提供静态球对称背景的几何函数。

第一阶段只实现 Schwarzschild：

- `f(r) = 1 - 2M/r`
- `r_star(r) = r + 2M log(r/(2M)-1)`
- `dr_star_dr = 1/f(r)`
- horizon radius `r_h = 2M`

扩展接口应允许：

- 非 Schwarzschild 的 `A(r), B(r)` 或 `f(r), g(r)`；
- 自定义 tortoise coordinate；
- 自定义边界类型和 horizon asymptotics。

### 5.2 `perturbations`

职责：定义 master sectors、potentials、ODE 和 metric reconstruction。

Schwarzschild GR 中：

- odd sector：Regge–Wheeler potential `V_odd(l,r)`；
- even sector：Zerilli potential `V_even(l,r)`；
- master equation：`d2 psi/dr_star2 + [k^2 - V_l(r)] psi = 0`；
- reconstruction：RW gauge 下从 `psi_odd/even` 得到需要的 metric components。

### 5.3 `waves`

职责：将入射 GW 参数转换为 partial-wave boundary data。

输入：

- `A_plus(k)`
- `A_cross(k)`
- `incident_direction = +z` 第一阶段固定

输出：

- `A_L = (A_plus + i A_cross)/sqrt(2)`
- `A_R = (A_plus - i A_cross)/sqrt(2)`
- `A_lm_even/odd`
- `c_lm_even/odd`

### 5.4 `angular`

职责：所有角向基函数与 convention。

必须集中实现，不允许分散在求和代码中：

- scalar spherical harmonics `Y_lm`；
- spin-weighted spherical harmonics `_sY_lm`；
- tensor harmonics normalization；
- Wigner-D function；
- `+z` 入射时 `m = ±2` 选择规则；
- 未来支持任意入射方向时的旋转。

### 5.5 `numerics`

职责：径向 ODE 数值求解与边界匹配。

推荐实现路线：

1. 对每个 `(sector, l, k)` 构造一维 ODE。
2. 从近 horizon 处施加 purely ingoing 解：`psi ~ exp(-i k r_star)`。
3. 向外积分到 `r_out`。
4. 在 `r_out` 匹配为 `A_in exp(-i k r_star) + A_out exp(+i k r_star)`。
5. 缩放解，使 `A_in` 等于目标入射系数 `c_lm`。
6. 保存 scaled radial solution、derivative、phase shift、transmission coefficient。

必须暴露诊断：

- Wronskian / flux conservation residual；
- boundary residual；
- ODE tolerance sensitivity；
- `r_out` sensitivity；
- `lmax` convergence。

### 5.6 `scattering`

职责：把径向解、角向函数和重构公式组合成观测量。

步骤：

1. 读取 radial cache。
2. 执行 metric reconstruction。
3. 计算 Kinnersley tetrad 下 Weyl scalars。
4. 转换到与入射方向对齐的 tetrad。
5. 用 geodesic deviation 定义的关系提取 `hddot_plus`、`hddot_cross`。
6. 对频域单色波使用 `h = - hddot / k^2`。
7. 输出 complex field amplitudes。

### 5.7 `viz`

职责：绘图只消费数据，不重新做物理计算。

图像类型：

- `h_plus`、`h_cross` 的二维波场图；
- optical axis 附近 Poisson spot；
- angular diffraction pattern；
- partial-wave convergence；
- transmission factor amplitude/phase；
- asymptotic-vs-finite-radius 对照。

### 5.8 `references`

职责：集中管理项目文献来源和公式追踪，不属于运行时代码。

目录约定：

- `references/papers/`：存放原始论文 PDF。
- `references/manifest.md`：记录每篇文献的用途、优先级、对应模块和关键公式范围。
- `docs/equation_map.md`：记录代码模块与文献公式、notes、测试之间的映射。
- `references/notes/`：存放 Codex 整理出的公式笔记、符号翻译、convention 对照和推导检查。

执行规则：

- 后续线程需要文献依据时，先读 `references/manifest.md`，再读对应 `references/notes/*.md`，最后必要时回到 `references/papers/*.pdf`。
- 不要只依赖 PDF 原文做实现；关键公式必须整理进 `references/notes/` 或 `docs/physics_spec.md`，并在 `docs/equation_map.md` 中建立映射。
- 若不同文献的符号、归一化、Fourier convention、tetrad convention 或 gauge convention 冲突，必须在 notes 或 `docs/physics_spec.md` 中显式说明转换关系。

## 6. 线程分工

本项目适合让 Codex 开多个相对独立的线程，每个线程只改自己负责的模块，并通过测试和 `status.md` 汇合。

| 线程 | 名称 | 主要责任 | 主要输出 | 依赖 | 验收标准 |
|---|---|---|---|---|---|
| T0 | 项目协调与规格冻结 | 维护 `project.md`、`status.md`、接口约定、DoD、线程 handoff prompt | 决策记录、接口冻结表、可执行 prompt | 全部 | 每次合并前 status 更新，接口变更有记录；每次提出下一步方案时同步给出对应 prompt |
| T1 | 文献与物理约定 | 整理公式、符号、Fourier convention、harmonic convention；维护 `references/manifest.md`、`references/notes/` 和 equation map | `docs/physics_spec.md`, `references/notes/`, `docs/equation_map.md` | 无 | 所有公式有来源；符号表无冲突；每个实现公式能追溯到 notes 或文献 |
| T2 | 背景与主方程 | 实现 Schwarzschild 背景、RW/Zerilli potentials、ODE RHS | `backgrounds/`, `perturbations/potentials.py` | T1 | potential asymptotics 和单位测试通过 |
| T3 | 角向基与旋转 | 实现 `Y_lm`、`_sY_lm`、Wigner-D、tensor harmonic normalization | `angular/` | T1 | 正交归一、spin-weight ladder、m=±2 测试通过 |
| T4 | 径向 ODE 与匹配 | 实现 shooting/matching、phase shift、transmission coefficient | `numerics/` | T2 | Wronskian/flux residual 达标；M→0 可解析测试通过 |
| T5 | 入射平面波与边界系数 | 实现 `A_plus/A_cross -> c_lm` | `waves/incident.py` | T1,T3 | M→0 重构平面波通过 |
| T6 | 重构、Weyl 和极化 | 实现 metric reconstruction、Weyl scalars、tetrad transform、`h_plus/cross` | `scattering/` | T2,T3,T4,T5 | 频域符号、极化 sanity tests 通过 |
| T7 | 验证与基准 | 写 unit/physics/regression tests，构造 benchmark fixtures | `tests/`, `benchmarks/` | T2-T6 | CI 全通过；误差阈值记录在 status |
| T8 | 可视化与 CLI | 配置驱动运行、HDF5/NPZ 输出、绘图脚本 | `examples/`, `viz/`, `io/` | T6,T7 | 一条命令生成波场图和 convergence 图 |
| T9 | 扩展接口 | 抽象静态球对称背景和 general sector API | `docs/extension_interface.md`, interfaces | T0,T2,T6 | Schwarzschild 后端不破坏；mock background 可接入 |

## 7. 里程碑

### M0：文档与接口冻结

- `project.md`、`status.md`、`physics_spec.md` 完成。
- 明确内部 convention：`e^{-ikt}`、`G=c=M=1`、Schwarzschild coordinates、RW gauge、spin-weighted harmonics convention。
- 完成 repo skeleton。
- `references/manifest.md` 建立，`docs/equation_map.md` 建立。
- `tests/` 可空跑或最小测试跑通。

M0 工作纪律：

- M0 不写 solver；若已有公式层代码，只作为 skeleton sanity，不扩大到径向求解、Weyl、plotting 或 CLI workflow。
- T0 只维护职责、结构、读写规则、status 和 handoff prompt。
- T1 只冻结 convention 和公式映射，不实现求解器。
- T7 只建立测试框架、容差策略、fixture 格式和本地/CI 命令，不要求物理回归数据。

### M1：基础 Schwarzschild RWZ solver

- 背景、potentials、tortoise coordinate。
- 单个 `(l,k,sector)` 径向解。
- horizon/infinity boundary matching。
- Wronskian / flux diagnostics。

### M2：入射平面 GW 和 partial-wave coefficients

- `A_plus/A_cross` 到 `c_lm^odd/even`。
- M→0 平面波重构测试。
- 支持 `m=±2` 的默认 +z 入射。

### M3：Weyl scalars 和 polarizations

- metric reconstruction。
- `Psi_0 ... Psi_4`。
- tetrad transformation。
- `h_plus`、`h_cross` complex field amplitudes。

### M4：有限半径波场与收敛

- 计算 `r=60M`、`kM = 0.1 ... 4.0`。
- `lmax ~ k r` 自动建议。
- 生成 convergence plots、wave-field maps。

M4 内部分两层验收：

- M4-lite / validation-grade：用较小但可审计的网格和频率组合打通 YAML
  配置、saved complex data、metadata、read-only plotting、convergence history
  和 T7 independent review。
- M4-production / journal-grade：在 M4-lite 和相关 radial/partial-wave
  blocker 全部关闭后，再安排期刊级高分辨率 wave-field / diffraction
  maps。production 图仍属于 M4，因为它们是有限半径波场和图像输出；
  不应推迟到 M5，除非图像目标本身是 transmission factor。

### M5：transmission factor 与对照实验

- 定义 unlensed/lensed waveform ratio。
- 实现频率扫描。
- 可选实现 Kirchhoff scalar baseline 作为对照，而非主算法。

### M6：扩展接口稳定化

- `StaticSphericalBackground` 与 `MasterSector` 抽象可用于新黑洞。
- 记录新黑洞接入所需最小数据：metric functions、tortoise、master potentials、boundary asymptotics、reconstruction/observable map。

## 8. 验证策略

验证必须分层进行，不允许只凭最终图片相似来判断程序正确。

### 8.1 单元测试

- `f(r)`、`r_star(r)`、`dr_star/dr`。
- RW/Zerilli potentials 的 horizon 和 infinity 极限。
- spherical Bessel asymptotics。
- `Y_lm`、`_sY_lm` normalization。
- Wigner-D identity。

### 8.2 物理测试

- `M -> 0`：散射解退化为平面 GW。
- 单个 `l` 模：边界残差和 Wronskian 守恒。
- odd/even potentials 的已知 asymptotics。
- partial-wave convergence 随 `lmax` 改善。
- optical axis 附近有限，不出现 asymptotic partial-wave divergence。

### 8.3 回归测试

固定参数：

```yaml
M: 1
r_obs: 60
kM_values: [0.1, 0.5, 1.0, 2.0, 4.0]
A_plus: 0.9 + 1.1j
A_cross: 0.4 + 0.6j
lmax_rule: ceil(k * r_obs + margin)
```

记录以下数据作为 fixtures：

- selected radial values；
- phase shifts；
- `h_plus/h_cross` at selected angles；
- convergence residuals；
- output plot hashes 或关键图像统计量。

## 9. 扩展新黑洞的接口原则

本项目不会假设“换一个 metric function 就自动得到新黑洞的引力波波光学”。对任意新的静态球对称黑洞，至少需要提供：

1. 背景 metric functions 和 horizon structure。
2. tortoise coordinate 或可数值积分的 `dr_star/dr`。
3. axial/polar master equations。
4. 对应 effective potentials。
5. 入射平面波在该背景的边界匹配规范。
6. metric reconstruction 或直接 observable reconstruction。
7. Weyl/polarization 定义是否仍为 GR 两自由度。
8. 可验证 benchmark。

因此扩展接口应允许接入新模型，但不声称自动推导扰动理论。

## 10. Codex 工作规则

- 每个线程先读 `project.md`、`status.md`、对应 docs，再修改代码。
- 每次运行任务前，先检查当前环境是否已有适配的 plugins、connectors 或
  skills；若有与任务直接相关的能力，应按其说明调用并在必要时记录到
  `status.md`。例如 arXiv/文献任务优先使用 arxiv-reading 或相关文献
  skill，图像/可视化任务优先检查可用 plotting/visualization skill，仓库
  协作任务优先检查 GitHub/Codex thread tools。不要为了使用工具而改变任务
  范围；没有适配工具时按普通项目规则执行。
- 任何符号约定变更必须先更新 `docs/physics_spec.md` 和 `status.md` 的 decision log。
- 任何新函数必须有 unit test 或 physics test。
- 绘图函数不得内嵌物理公式；只读取已保存数据。
- 不允许为了让图像好看而修改物理 normalization。
- 任何 benchmark 失败都必须记录失败参数、误差、猜测原因和下一步。
- T7 审查频率压缩规则：T7 主要审查高风险边界，包括新物理公式、新
  convention/API、新 production 数据、benchmark/fixture 晋级、阈值或
  `lmax`/boundary/Q018 策略变更，以及 paper-level/final-journal claim。
  对 read-only plotting、caption/layout、sidecar/manifest polish、同一已接受
  数据源的多种插值显示或 DPI 输出，T8 应先批量生成并自检；T7 只在一批图
  准备晋级为 benchmark 或 paper-quality package 时做 batch review。若 T8
  自检发现物理范围、source metadata、分辨率、Q018 或 no-solver boundary
  问题，必须停止并交回 T0，而不是继续排版。
- T0 硬规则：每次 T0 提出下一步方案、阶段推进、go/no-go 判断、线程启动或线程重启建议时，必须同时提供可直接复制给对应线程的 prompt。若方案包含多个线程，必须逐线程给出 prompt、依赖关系、允许修改范围、停止条件和验证命令。若 prompt 需要长期复用，应写入 `docs/prompts/`，并在 `status.md` 记录文件路径；若当前不应启动任何线程，必须明确写出“不提供 prompt”的原因和解除条件。
- T0 Codex 任务自动派发硬规则：当用户已经批准 T0 的下一步方案、对应 prompt 已冻结且目标 Codex 任务仍存在时，T0 必须在向用户报告最终方案的同一轮，通过 Codex task/thread messaging 工具把 prompt 直接发给目标任务；默认模型为 `5.6 Sol High`。多级链只允许上游任务在 exact GREEN、artifact/tests/status/handoff 全部完成并 fresh verify 后，向已冻结的下游复核任务派发；YELLOW、RED、incomplete、artifact 缺失、检查失败或状态不明确时不得启动下游，只能报告 T0。若出现明确的 model-capacity/system interruption，可由 T0 在同一任务使用 `5.6 Terra High` 恢复，且必须先检查进程、checkpoint 和 artifact 状态以避免重复计算；科学错误、测试失败、backend 不稳定或非有限结果不得通过换模型绕过。目标任务缺失、已归档或 messaging 不可用时，不得静默创建新任务，必须停止并报告用户。下游复核完成后只向 T0 回传 exact decision，不得自行开启下一科学阶段。该自动派发规则不授权任何非 T0 任务执行 GitHub push。
- T0 GitHub 重大节点同步硬规则：当 T0 通过本地证据确认项目到达重大节点（包括 milestone/phase closeout、高风险 gate 的独立 GREEN 验收、production/benchmark artifact 的独立接受，或 frozen convention/public API 边界的正式冻结）时，必须先更新并核对 `status.md` 和 `docs/handoffs/T0_current.md`，完成对应 fresh verification，然后同步到项目已配置的私人 GitHub 仓库。同步前必须检查完整 diff 和待提交文件，排除 secrets/credentials、私人原始数据、非预期大文件以及无关或未经审查的工作区改动；使用范围明确的 commit，并以非 force push 推送当前授权分支。若工作区含无关未提交改动、远端或认证不可用、artifact 是否应入库不明确，或验证未通过，则不得盲目 stage/commit/push；必须在 `status.md` 与 T0 handoff 中记录 `GitHub sync pending`、准确阻塞原因和下一项安全操作。本规则不授权 force push、history rewrite、删除远端分支或扩大 GitHub 仓库的可见性。
- Handoff 硬规则：每个线程在完成一个任务或停止在明确状态前，必须创建或更新自己的 `docs/handoffs/T*_current.md`。该文件用于同编号新线程在上下文耗尽后接手，必须简洁但足够精确地记录：当前线程状态、已完成内容、未完成内容、阻塞项、非阻塞 warning、下一线程必须读取的文件优先级、frozen decisions、forbidden actions、可直接执行的 exact next task、允许/禁止修改的文件、验证命令、definition of done，以及已 superseded 且不得再用的旧 prompt。不得逐字复制聊天历史，只保留决策、原因、文件、命令、测试结果和下一步。若某次任务形成阶段性 closeout 或重要历史边界，应先把旧 `T*_current.md` 复制到 `docs/handoffs/archive/T*_<date>_<slug>.md`，再更新 current handoff。`status.md` 仍是全局权威时间线，handoff 是线程本地恢复摘要。
- Artifact 归档规则：smoke、pilot、未复核或临时中间结果可以写入 `/tmp`
  或系统临时目录；但一旦某个数值/图像 artifact 被 T7 接受并用于
  closeout，就必须复制到项目内归档目录，例如
  `runs/phaseN/<slice>/` 或 `data/processed/<slice>/`。归档时应记录原始
  临时路径、项目内路径、文件大小、校验和、生成/复核线程和适用范围。
  后续文档不得只依赖 `/tmp` 或 `/private/tmp` 路径作为正式记录。

## 11. 最小可运行 CLI 目标

```bash
schwgw run configs/schwarzschild_fig3_like.yaml --out runs/fig3_like/
schwgw plot wavefield runs/fig3_like/results.h5 --component h_plus
schwgw plot convergence runs/fig3_like/results.h5
schwgw scan-transmission configs/transmission_scan.yaml --out runs/transmission/
```

## 12. 完成定义

项目第一阶段完成需满足：

- 可配置运行 Schwarzschild finite-radius GW scattering。
- 输出 `h_plus`、`h_cross` 的 complex frequency-domain data。
- 至少两组 `kM` 和一组 `r_obs` 的 convergence 测试通过。
- `M -> 0` 测试通过。
- 关键公式和 convention 全部集中记录。
- 新黑洞扩展接口存在，并有 mock model 测试。
