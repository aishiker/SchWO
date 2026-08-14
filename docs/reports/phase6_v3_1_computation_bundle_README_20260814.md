# SchWO Phase 6 V3.1 computation bundle

本 bundle 收集 V3.1 base、U、X、Y、Z 分支相关的手写/冻结计算代码、外部脚本、配置、测试、设计、prompts、dispatch/review archives，以及全版本错误与缺陷报告。

## 包含

- `configs/phase6_v3_0_*` 与 `configs/phase6_v3_1_*`
- `scripts/phase6_v3_1_*`
- `src/schwgw/validation/phase6_v3_*`
- `tests/**/test_phase6_v3_*`
- `docs/phase6_v3_0_*`、`docs/phase6_v3_1_*`
- 所有 V3.1 T0/T4/T7 archive、V3.1 prompts
- V3 conventions、review-gate governance、报告与 inventory

## 明确排除

- `runs/phase6/**`：immutable failure/science roots，约 59 MB；保留原仓库路径，报告和 archives 已记录关键 SHA。
- `generated/phase6_v3_1_z/**`：约 961 MiB、1,006,400,405 bytes 的可由 spec/generator 重建的派生 machine-authority tree；bundle 收录其 spec、generator、package/design 和关键 identities，不复制整棵派生树。
- `/tmp` 或 transient logs/PIDs、Python caches、外部 BHPT 安装副本。
- 非 V3.1 的 Li figures、radial backends 与其它 Phase 5/6 artifacts。

## 校验

`phase6_v3_1_computation_bundle_inventory_20260814.tsv` 记录每个已收录文件的相对路径、字节数和 SHA-256。压缩包本身另有同名 `.sha256` 文件。

本 bundle 是停止点审计包，不是科学 release；不得据此声称 V3.1 PASS、V3.2 authorization 或 global GREEN。
