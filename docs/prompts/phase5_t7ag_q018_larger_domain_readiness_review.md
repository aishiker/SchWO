# Phase 5 T7ag Prompt: Independent Review Of Q018 Larger-Domain Readiness

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ag`。

你的任务是独立复核 T4l 的 Q018 larger-domain readiness audit。不要生成新
wave-field artifacts，不要绘图，不要修改 physics convention。

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
9. `docs/q018_larger_domain_readiness.md`
10. `docs/prompts/phase5_t4l_q018_larger_domain_readiness.md`
11. `runs/phase4/m4_production_first_pass/manifest.md`

也要按项目规则先检查是否有已安装且适用的 plugin/skill；如有适合做本地
验证、系统化 debugging 或文献 notes 查验的能力，应使用并在 `status.md`
记录。

## 2. Review Scope

Independently verify:

- T4l did not modify `src/` unless explicitly justified by a stop condition.
- No new M4/M5 wave-field artifact was generated.
- No plots were generated.
- No `kM=4` run was performed or claimed.
- No convention, threshold, `lmax`, Route B, Q005, Q014, or Q018 policy change
  occurred.
- `docs/q018_larger_domain_readiness.md` exists and contains the required
  source checksum, metadata summary, candidate-domain table, targeted radial
  probe table, and GREEN/YELLOW/RED classification.

## 3. Independent Checks

### 3.1 Source checksum

Recompute SHA-256 for:

```text
runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz
```

Confirm it matches both:

- `runs/phase4/m4_production_first_pass/manifest.md`;
- T4l's report.

### 3.2 Metadata and Q018 warning schema

Load the NPZ with project IO helpers or a direct read-only inspection.

Verify:

- `kM=2.0`;
- grid is `x-z`, range `[-30,30]^2`, shape `(121,121)`;
- `lmax=180`, `lmax_values=[108,132,156,180]`;
- Q018 warnings are structured;
- all `evanescent_tail_suppressed` warnings include enough metadata to assess
  `valid_until_r`;
- `min(valid_until_r)` agrees with T4l's report within roundoff.

### 3.3 Candidate-domain coverage

Independently recompute coverage for:

| candidate | required radius |
|---|---:|
| accepted `[-30,30]^2` | `42.42640687119285` |
| angular R60_K2 | `60.0` |
| x-z `[-40,40]^2` | `56.568542494923804` |
| x-z `[-60,60]^2` | `84.8528137423857` |

Acceptance criterion:

```text
covered iff every relevant suppressed-mode valid_until_r > required radius
```

Do not infer larger-domain acceptance from the accepted `[-30,30]^2` case.

### 3.4 Targeted radial probes

Review T4l's targeted probe table. Re-run at least a minimal independent subset:

```text
M=1
k=2.0
r_out=300.0
ell in [152,153,180]
sector in [odd, even]
```

Confirm:

- solver path and warning code classification are consistent with T4l;
- no unstructured radial exception occurs;
- `valid_until_r` conclusions are consistent;
- no hidden `lmax` reduction or threshold relaxation occurred.

If this minimal subset is too slow, stop and report exactly where it stalls.

## 4. Review Decision

Classify T4l's result:

- **ACCEPT GREEN**: R60_K2 and all tested larger-domain candidates are covered
  by the current policy and probes.
- **ACCEPT YELLOW**: current accepted `[-30,30]^2` remains valid, but R60_K2
  or larger domains are not covered; next action must be a T4 method-hardening
  slice before any R60_K2/T8 production run.
- **REJECT / RED**: source checksum mismatch, malformed metadata, unstructured
  probe failure, hidden source/convention/threshold changes, or unsupported
  claims.

YELLOW is not a failure of the accepted M4/M5 archive. It means the next
larger-domain run is not yet allowed.

## 5. Validation Commands

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run targeted read-only inspection/probe commands sufficient to support the
review. Record exact commands and outcomes in `status.md`.

## 6. status.md Update

At the end update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- source checksum verification;
- independent metadata verification;
- independent coverage result;
- targeted probe subset result;
- ACCEPT GREEN / ACCEPT YELLOW / REJECT RED decision;
- commands run;
- test results;
- open issues;
- next action prompt recommendation.

Do not mark R60_K2, larger-domain, or `kM=4` work accepted unless the evidence
actually supports that classification.
