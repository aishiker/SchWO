# SchWO 第二轮独立审查回应与针对性精修

日期：2026-08-03  
回应对象：`audits/SchWO_second_audit_20260803.md`

## 1. 总结裁决

第二轮审查关于剩余主要误差源的判断成立。本轮没有重新打开已经被
direct metric-curvature bridge 取代的 lower-NP pseudoinverse 问题，也没有
把内部一致性误写成 Li--Hou--Zhao 严格逐图复刻。

本轮完成了以下工程与 bounded numerical hardening：

1. production outer matching 从 finite-`r_out` bare plane waves 改为由
   RW/Zerilli 方程递推的 Jost `1/r` series；
2. Fig.2、Fig.4、Fig.5/6 的生产/验证入口加入 `r_out=(300,600,1200)M`
   ladder、quadratic `1/r_out` extrapolation、raw ladder 与 uncertainty；
3. direct curvature 增加
   `static_orthonormal | li_literal_cartesian` 两套显式 observer frame；
4. Fig.5/6 增加 principal/raw、unwrapped、global-offset 与
   offset-removed residual diagnostics；
5. 补充 Fig.4 `kM=2` shell/Q018 bounded audit；
6. Fig.8 的低阶 `ell=2..19` 去掉 heuristic finite-radius phase correction，
   改为 Jost ladder/extrapolation；
7. 增加严格的外部 BHPT Toolkit/ReggeWheeler MST benchmark importer、
   Wolfram runner 与 fail-closed preflight；
8. 将 Fig.8 strict claim 固定为 `false`，并把 direct-curvature 的泛化
   `physical_claim` 收紧为 `false`，另存 gauge/frame-qualified claim；
9. 增加 curved first-Bianchi 与 linearized-Ricci vacuum permanent tests。

但是，以下工作尚未完成：

- 新 Jost/r-out/frame contract 下的 Fig.2/4/5/6 全分辨率 paper-facing
  数据和图像尚未全部重算；本轮 evidence 是 bounded refinement，不是最终
  replacement figure package；
- 外部 BHPT/MST complex phase benchmark 已在随后发现的外置 SSD
  WolframKernel 下完成；odd sector 是独立 ReggeWheeler MST 值，even sector
  仍由 exact Chandrasekhar/Starobinsky parity relation 导出，不能误写为
  第二套独立 even radial solver；
- Fig.4 `kM=2` 的 full selected-angle、all-shell production audit 仍未闭合；
- Fig.5/6 far-axis phase residual 仍大，不能用单个 global phase offset 消除。

因此本轮总状态仍为：

```text
internal implementation / bounded diagnostics: GREEN
paper-facing regenerated artifact set: INCOMPLETE
strict Li-paper reproduction: YELLOW (not GREEN)
```

## 2. P0-1：受控 infinity outer basis

### 修复

`src/schwgw/numerics/matching.py` 新增
`outer_asymptotic_basis(...)`，使用

```text
J_±(r) = exp(± i k r_star) sum_{n=0}^N a_n^(±) / r^n
```

并从 exact RW/Zerilli equation 递推系数，而不是拟合 phase correction。
`BoundaryConfig.outer_basis="jost_1_over_r"`、
`outer_series_order=160` 已成为 production default；outward shooting、BVP、
bidirectional match 和 Q018 matching 均走同一 basis。历史
`outer_basis="plane_wave"` 只允许显式 diagnostic。

### 验证

bounded evidence 的最大 Jost local ODE residual 为
`8.913236564402399e-10`；相同 probe 的 bare-plane residual 最小值约为
`0.9999999999966247`。这说明新 basis 在所测 envelope 内满足局部方程，
但它不替代 `r_out -> infinity` convergence。

关键源文件 SHA-256：

- `matching.py`: `9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340`
- `boundary_conditions.py`: `1c938bb2240af04f93fdadc4ac01bb90bb41ca72fbf47f2f693402f8b7ebe561`

## 3. P0-2：Fig.2/4/5/6 的 r_out ladder 与 extrapolation

### 修复

- `scripts/verify_fig2_high_precision.py`：schema v3，固定三点 ladder，逐
  `ell/sector/r_out` 保存 coarse/fine RK4、Richardson result、quadratic
  `1/r_out` extrapolation 和与末两点线性外推的差值；
- `scripts/phase5_generate_direct_curvature_angular.py`：Fig.4 对每个
  `r_out` 使用独立 cache/config，保存 raw `h_plus/h_cross` ladder、外推场和
  uncertainty；
- `src/schwgw/io/direct_tablei.py` 与
  `scripts/phase5_recompute_direct_curvature_fig56.py`：Fig.5/6 的每个
  Table-I 点和每个 `lmax` 使用独立 radius cache，先做 r-out extrapolation，
  再做 final-pair lmax convergence；transaction/merge metadata 绑定完整 ladder。

通用外推实现位于
`src/schwgw/numerics/r_out_extrapolation.py`，SHA-256
`e2790d5a518b7a60bde66194ca269dd52660aa4899bec9896e562e54abada13b`。

### 当前证据边界

quick bounded Table-I probe 的最大外推 uncertainty 为
`5.6817381855198166e-05`；`kM=2` shell probe 的最大外推 uncertainty 为
`1.915985015991124e-08`。这些数值只适用于本轮 bounded sampling，不能
外推为完整 Fig.4/5/6 高分辨率误差上限。

## 4. P0-3：dual observer frame

### 修复

`src/schwgw/scattering/metric_curvature.py` 的全部 direct-curvature public
paths 接受显式：

```text
observer_frame = "static_orthonormal" | "li_literal_cartesian"
```

`static_orthonormal` 仍是物理默认；`li_literal_cartesian` 是将 Li 文的
flat-Cartesian tetrad 按其 coordinate Jacobian literal 推入 Schwarzschild
coordinates 的 paper-comparison diagnostic。config、result、Table-I、Fig.3、
Fig.4 和 Fig.5/6 metadata 均保留所选 frame。

bounded Table-I probe 中两套 frame 的最大相对差为
`0.06666666666661208`，与审查报告中的约 6.67% 一致。

泛化 metadata 已收紧为：

```text
physical_claim = false
gauge = "Regge-Wheeler"
physical_within_frozen_gauge_frame_convention = true
literal_li_paper_observer_equivalence = (frame == "li_literal_cartesian")
paper_equivalence = "YELLOW"
```

因此不会再把 chosen-frame 物理结果误读为 literal paper equivalence。

## 5. P0-4：Fig.5/6 phase decomposition

`src/schwgw/scattering/phase_diagnostics.py` 新增独立、无 phase fitting 的
diagnostic surface，保存：

- principal/raw circular residual；
- continuous unwrapped phase residual；
- 每 panel circular global offset；
- offset-removed residual；
- 跨 panel 单一 global offset 及其 residual。

对现有 direct-curvature uniform-40 artifact 的 bounded re-analysis 得到：

| polarization | raw global circular MAE | one-offset removed MAE |
|---|---:|---:|
| plus | 1.12397058397 rad | 0.653283023316 rad |
| cross | 1.11360485819 rad | 0.659880691831 rad |

near panels 在逐 panel offset 后明显改善，但最远 panel 仍约
`1.32 rad`。所以审查结论得到确认：差异不是一个可被统一 phase shift
消除的 convention mismatch。没有用 offset 修改 production data。

## 6. P1-5：Fig.4 kM=2 shell/Q018 audit

bounded shell evidence 覆盖 `ell=108..132`（围绕 `kr=120`）并单独记录
Q018 envelope `ell=153..180`。当前抽样中：

- shell extrapolation uncertainty 最大为 `1.915985015991124e-08`；
- Q018 selected records 的 branch/warning provenance 被保存；
- renderer 没有重新引入 incident-field double counting。

这项结果是 **PARTIAL**。它完成了 radial-shell 与 Q018 provenance 层，
但没有完成审查要求的四个 selected angles 下 all-shell complex
contribution、`lmax=120/160/200/240` 与 doubled angular-grid 的全量联合验收。
因此 Fig.4 `kM=2` 仍是 YELLOW。

## 7. P1-6：外部 BHPT/MST complex phase benchmark

已增加：

- `scripts/bhpt_reggewheeler_mst_benchmark.wls`；
- `scripts/benchmark_fig8_bhpt_mst.py`；
- `src/schwgw/scattering/mst_benchmark.py`；
- `tests/unit/test_mst_benchmark.py`。

合同固定 `kM=(0.5,1,1.5,2)`、所有 `ell=20..40`，禁止 fitted phase、
conjugation、offset 或 normalization correction。odd convention 直接由
ReggeWheeler incidence/reflection 取得；even factor 明确标为通过 exact
Chandrasekhar/Starobinsky relation 导出，而不是伪称第二个独立 even solver。
importer 对 source URL、MIT license、commit、source SHA、完整 mode keys、
complex modulus/convention 全部 fail-closed。

上游只读 source：

- repository: `https://github.com/BlackHolePerturbationToolkit/ReggeWheeler`
- documentation: `https://bhptoolkit.org/ReggeWheeler/`
- commit: `2e01209271fb3d0d92705d5c27bd9e00a6140981`
- `Kernel/ReggeWheelerRadial.m` SHA-256:
  `2af593f527b39d2b7ece71f99e50ecb6b84399342251985004d6d2e2c3fed41f`

最初的 fail-closed preflight evidence：

`runs/phase5/paper_figures/bhpt_mst_benchmark_preflight_20260803_v2/`

- request SHA-256:
  `c3f7f7fca280c2a5a18bf45c225d1d48a38460cdbd31854d9779c38d4f0b97f5`
- preflight SHA-256:
  `ad65f88b490371dc7acbd48fee2f57c50b2f3c16c8ed22af0fbd6bdb51e1ada7`
- blocked SHA-256:
  `bfaa2e49bff30e191face0cf0d32e001afcbbf7c33cc955d42ccc9e91b9cf6a8`

该 v2 root 在当时没有显式 kernel 路径，`wolframscript` return code 255；
它仍保持 immutable，并正确记录 `science_executed=false`、
`external_mst_records_generated=0`。随后确认可用内核为
`/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel`
（Wolfram 14.3）。

fresh completed evidence：

`runs/phase5/paper_figures/bhpt_mst_benchmark_20260803_v4/`

- external BHPT record：84 modes，覆盖
  `kM=(0.5,1,1.5,2)`、`ell=20..40`；
- Wolfram working precision：240 digits，`PrecisionGoal=AccuracyGoal=80`；
- comparison status：`PASS`，tolerance `1e-9`；
- maximum odd/even complex absolute error：
  `9.211213737287328e-15`；
- comparison SHA-256：
  `274786add2947174fd6be43224c5e28de4c3da1b14a6fd9f97638a3c55218281`；
- raw external JSON SHA-256：
  `0a6359692b9321a60c3f0308a2119968af57c7a0541cd27b6e9636334853f08e`。

这个结果闭合了 independent odd-sector complex phase benchmark；even-sector
结果仍明确标记为 exact parity transform，而非独立 even BHPT solve。

## 8. P1-7：low-ell Fig.8

`src/schwgw/io/fig8_mst.py` 的低阶 `ell=2..19` 已不再采用单个
`r_out=300M` numerical phase 加 heuristic correction。当前实现使用
`r_out=(300,600,1200)M` 的 Jost numerical phase，并对 odd/even complex
phase factor 做 quadratic `1/r_out` extrapolation，同时保存 raw ladders 和
uncertainty。`ell>=20` 继续使用项目 direct MST。

这完成了审查允许的 “improved infinity matching” 路线。外部 BHPT odd
complex phase benchmark 也已通过，但 even factor 仍不是第二套独立 radial
solve。因此 Fig.8 维持 YELLOW-GREEN，而不是把有限验证过度解释为严格
paper-equivalence GREEN。

## 9. P1-8/9：metadata hardening

### Fig.8

所有新 producer/loader 都要求：

```text
strict_paper_reproduction_claim = false
paper_equivalence = "YELLOW"
```

loader 会拒绝缺失或为 `true` 的 strict claim。历史 immutable artifact 不做
in-place rewrite；其纠正记录为
`audits/fig8_metadata_correction_20260803.json`，SHA-256
`35d60f46d57a612392e6e973c8b30f61cf4041fa0f58e17ced835c5ddf305bab`。

### direct curvature

通用 `physical_claim=true` 已移除。新 metadata 必须同时携带 exact
gauge、observer frame、frame-qualified validity 与 `paper_equivalence=YELLOW`。
Fig.7 apparent modes 继续是 `physical_claim=false`、`diagnostic_only`。

## 10. 永久测试与验证

新增或扩展的 tests 覆盖：

- Jost coefficient/data/residual、production routing 与 plane diagnostic；
- complex `r_out` extrapolation 和 uncertainty；
- dual observer-frame regression；
- curved first Bianchi identity；
- curved linearized Ricci vacuum residual；
- phase raw/unwrapped/offset decomposition；
- Fig.5/6 transaction ladder/extrapolation/frame binding；
- Fig.8 strict-claim round trip/rejection；
- external MST convention/importer 的 positive/negative cases。

最终 targeted verification：

```text
69 passed
Ruff: All checks passed
compileall: PASS
git diff --check: PASS
```

随后完成全库验证：

```text
1144 passed, 117 skipped, 1 xfailed, 109 warnings,
104 subtests passed in 371.42s
```

skip/xfail 是仓库既有的条件性/诊断边界；warnings 来自既有 Weyl
pseudoinverse forensic tests、SciPy Q018 fail-closed paths 和 Wigner 高阶
诊断，没有新增 test failure。

bounded numerical evidence：

- report:
  `runs/phase5/paper_figures/second_audit_refinement_20260803_v2/second_audit_refinement.json`
- report SHA-256:
  `71656a7aaad5ee98aecdaf979742498e98de037a2060cc5ce85f9d6627c2a534`
- combined NPZ SHA-256:
  `2cf3ffae7a36a05a58084f17381264df4426e8bc5422f5dfa068cdcbcf0d0f82`

## 11. 逐图状态（本轮后）

| Figure | 状态 | 本轮改变 | 仍未闭合 |
|---|---|---|---|
| Fig.1 | GREEN | production outer basis hardened | 建议补充同样的 r-out supplement，不改变当前 verdict |
| Fig.2 | YELLOW-GREEN | high-precision入口加入 Jost + r-out ladder/extrapolation | full high-precision ladder 尚未运行 |
| Fig.3 | YELLOW-GREEN | dual frame 与 qualified metadata | 新 convention 下 full raster 未重算 |
| Fig.4 | YELLOW | Jost ladder production path；bounded shell/Q018 audit | kM=2 full shell/angle/grid gate 未通过 |
| Fig.5 | amp YELLOW-GREEN；phase YELLOW/RED | Jost ladder、dual frame、phase decomposition | full rerun 与 far-axis phase residual |
| Fig.6 | amp YELLOW-GREEN；phase YELLOW/RED | 同 Fig.5 | 同 Fig.5 |
| Fig.7 | diagnostic-only YELLOW | observer frame 显式；generic claim 收紧 | paper L-row 内部疑点与 gauge/tetrad dependence |
| Fig.8 | q=2 YELLOW-GREEN | low-ell Jost extrapolation；strict claim 修正；external BHPT odd phase PASS | even factor 仅由 exact parity relation 导出；strict paper equivalence 未闭合 |

## 12. 下一步与禁止误读

下一项科学工作应依次是：

1. 运行 Fig.2 full precision r-out ladder；
2. 运行 Fig.4 `kM=2` full shell/angle/grid audit；
3. 运行 Fig.5/6 两套 frame 的 full r-out-ladder production rerun，并重新
   生成 phase residual package；
4. 只有上述 paper-facing artifact 和逐图 acceptance
   全部闭合后，才允许重新判断 strict Li-paper reproduction。

当前明确禁止以下陈述：

```text
strict Li-paper reproduction GREEN
Fig.4 kM=2 closed
Fig.5/6 phase reproduced
independent even-sector BHPT radial normalization validated
all paper-facing figures regenerated under the new boundary/frame contract
```

## 13. 2026-08-06 Fig.5/6 full dual-frame production closeout

第 12 节中的 Fig.5/6 full rerun 已完成，不再是 pending item。本次使用
exact CPython 3.14.6，对两种 observer frame 均完成
`kM=0.1..4.0` 的 40 个频率与 8 个 Table-I 位置：

- `static_orthonormal` merged NPZ SHA-256:
  `c6468da4e4f844461a884976a10c5063019b9e74f8ec5a2cd45247dabc9af776`;
- `li_literal_cartesian` merged NPZ SHA-256:
  `a47623535b7b4ae62756c79e80f21f58ca14a0c4e911096efb6d781d73000e55`;
- 两者均为 `(40,8)` finite complex arrays，使用 Jost `1/r` basis、
  `r_out=(1200,1800,2400)` 与 quadratic `1/r_out` extrapolation;
- 最大 final-pair `lmax` delta 为
  `4.5309249774413517e-10`，最大 diagonal r-out uncertainty 为
  `8.417822542313249e-4`;
- 两套 600-DPI PNG、vector PDF、sidecar 和 phase diagnostics 均已生成在
  `runs/phase5/paper_figures/fig56_jost_rout_render_*_20260806_py314/`;
- focused verification: `27 passed in 1.75s`，数组 shape/finite、hash、
  raster dimensions 与 visual QA 全部 PASS。

与冻结 paper raster 红色 marker 的定量比较表明，Li-literal frame 的
cross amplitude MAE 为 `0.1832402084409184`，优于 static frame 的
`0.2730699665395479`。但 phase circular MAE 仍约为 `0.417 rad`，而且
一个全局 phase offset 不能解释差异：Li-literal plus/cross 的
one-offset-removed MAE 为 `0.4137375/0.4191221 rad`。

因此本轮的严格结论是：

```text
Fig.5/6 full numerical production + merge + render: COMPLETE
Fig.5/6 amplitude: YELLOW-GREEN, Li-literal frame favored
Fig.5/6 phase: YELLOW, not reproduced exactly
strict Li-paper reproduction: YELLOW
```

不得重复这次高成本 Fig.5/6 计算。后续应转向 Fig.4 `kM=2` 等仍未闭合
的科学边界，而不是重算已闭合的 40-point transactions。
