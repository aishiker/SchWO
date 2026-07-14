# Phase 5 T4l Prompt: Q018 Larger-Domain Readiness For kM=2

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4l`。

本 slice 的目标是做 **Q018 larger-domain readiness audit**，只回答一个问题：

```text
当前 kM=2 的 high-ell evanescent-tail policy，是否足以支持 R60_K2
或比 [-30,30]^2 更大的 observer domain？
```

不要生成新的 wave-field artifact，不要绘图，不要启动 `kM=4`，不要修改
physics convention。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/phase4_production_closeout.md`
8. `docs/phase5_m5_four_frequency_closeout.md`
9. `docs/prompts/phase4_t4k_q018_high_ell_evanescent_tail.md`
10. `docs/prompts/phase4_t7u_fig3_multifrequency_q018_review.md`
11. `runs/phase4/m4_production_first_pass/manifest.md`

也要按项目规则先检查是否有已安装且适用的 plugin/skill；如有可帮助本地
数值诊断、论文 notes 查验或系统化 debugging 的能力，应使用并在
`status.md` 记录。

## 2. 当前已知事实

已接受的 M4/M5 production domain 是：

```text
kM=[0.5,1.0,1.5,2.0]
x/M,z/M in [-30,30]
dx=dz=0.5M
max observer radius = sqrt(30^2 + 30^2) = 42.42640687119285 M
```

Q018 当前接受边界只覆盖这个 same-domain case：

```text
kM=2.0
warning code = evanescent_tail_suppressed
minimum accepted valid_until_r = 42.472089355131786 M
```

这 **不能自动外推** 到：

- R60_K2；
- `[-40,40]^2`；
- `[-60,60]^2`；
- `kM=4`；
- 任意更大 observer domain。

## 3. Scope

允许：

- 读取现有代码和 artifact metadata。
- 运行 targeted radial diagnostics。
- 运行短小 Python inspection snippets。
- 创建一个诊断报告：

```text
docs/q018_larger_domain_readiness.md
```

- 更新 `status.md`。

除非你发现 metadata/reporting API 明显缺失且无法完成本 audit，否则不要修改
`src/`。如果认为必须改 `src/`，先停止并在 `status.md` 说明原因，不要自行改。

禁止：

- 不要生成新的 M4/M5 NPZ/HDF5 wave-field artifact。
- 不要生成 plots。
- 不要运行 full x-z grid solver。
- 不要启动或声称通过 `kM=4` stress。
- 不要修改 Fourier/harmonic/tetrad/RWZ/Route B/Q005/Q014 convention。
- 不要放宽 radial thresholds、lmax convergence thresholds 或 Q018 policy thresholds。
- 不要通过降低 `lmax`、缩小域或去掉 warnings 来制造通过结果。

## 4. 诊断任务

### 4.1 读取并复核已接受的 kM=2 source metadata

检查：

```text
runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz
```

确认并记录：

- source file SHA-256 是否匹配 manifest；
- grid kind、x/z range、shape、`lmax`、`lmax_values`；
- Q018 warning count；
- warning codes；
- 每个 `evanescent_tail_suppressed` warning 的 `ell`、`sector`、
  `valid_until_r`、barrier/action metadata；
- 当前 accepted domain 的 `r_max = sqrt(30^2+30^2)`；
- `min(valid_until_r) - r_max`。

### 4.2 Candidate-domain table

建立并写入报告的候选域表：

| candidate | required radius |
|---|---:|
| accepted `[-30,30]^2` | `42.42640687119285` |
| angular R60_K2 | `60.0` |
| x-z `[-40,40]^2` | `56.568542494923804` |
| x-z `[-60,60]^2` | `84.8528137423857` |

对每个 candidate 判断：

```text
covered iff every relevant suppressed-mode valid_until_r > required radius
```

不要把 current accepted-domain pass 外推为 larger-domain pass。

### 4.3 Targeted radial probe, kM=2 only

运行 targeted radial diagnostics，只用于理解 readiness，不生成 grid。

建议参数：

```text
M=1
k=2.0
r_out=300.0
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
ell in [144, 150, 152, 153, 156, 168, 180]
sector in [odd, even]
observer radii to assess: [42.42640687119285, 56.568542494923804, 60.0, 84.8528137423857]
```

For each `(sector, ell)` record:

- solver path;
- whether it returns a regular radial solution or a structured
  `evanescent_tail_suppressed` warning;
- `valid_until_r` if present;
- boundary residual;
- raw/effective Wronskian residual if available;
- expected flux scale if available;
- whether each candidate radius is covered.

This diagnostic may use existing public/internal radial functions, but do not
change implementation.

### 4.4 Decision classification

Classify the result:

- **GREEN for R60_K2** only if every high-ell suppressed mode needed by
  the current `kM=2,lmax=180` policy has `valid_until_r > 60.0` and targeted
  radial probes show no unstructured failure.
- **YELLOW** if accepted `[-30,30]^2` remains covered but R60_K2 or larger
  domains are not covered by current metadata; recommend a specific next
  T4 method slice before any R60_K2/T8 run.
- **RED** if current accepted-domain metadata is inconsistent, source checksum
  fails, warnings are missing/malformed, or targeted probes reveal a new
  unstructured radial failure.

Expected possibility: YELLOW is a valid result. Do not force GREEN.

## 5. Report Requirements

Create:

```text
docs/q018_larger_domain_readiness.md
```

The report must include:

1. Scope and non-scope.
2. Source artifact path and checksum check.
3. Accepted-domain metadata summary.
4. Candidate-domain coverage table.
5. Targeted radial probe table.
6. GREEN/YELLOW/RED classification.
7. Explicit next recommendation:
   - if GREEN: what T8/T7 slice may safely run next;
   - if YELLOW: what T4 method hardening is required before R60_K2;
   - if RED: what blocker must be fixed first.
8. A clear statement that this report does not validate `kM=4`.

## 6. Validation Commands

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run a targeted command or snippet that performs the metadata/probe checks
used in the report. Record exact commands and outcomes in `status.md`.

## 7. Stop Conditions

Stop and report without modifying `src/` if any of these occur:

- source checksum mismatch;
- accepted M4/M5 metadata is inconsistent with `status.md` or the closeout docs;
- Q018 warning metadata lacks enough fields to assess `valid_until_r`;
- targeted radial probe reveals an unstructured exception for `kM=2`;
- a single targeted probe takes more than 20 minutes;
- supporting R60_K2 clearly requires changing the radial algorithm.

## 8. status.md Update

At the end update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- source checksum result;
- candidate-domain coverage result;
- targeted probe summary;
- GREEN/YELLOW/RED classification;
- commands run;
- test results;
- open issues;
- concrete next action and prompt recommendation for T7ag review.

Do not mark R60_K2 or larger-domain work accepted until T7 independently
reviews this slice.
