# T0 Current Handoff

Date: 2026-07-15

Thread: T0, project coordination and gate scheduling.

## Current Status

The accepted metadata repair remains closed GREEN while its scientific state
remains the independently established:

```text
YELLOW / TARGETED ADAPTIVE FREQUENCY REFINEMENT REQUIRED
```

The user approved the bounded thirteen-frequency repair direction and
authorized execution. The project-required independent T0 package review is:

```text
REVIEW GREEN / T0 REPAIR PACKAGE APPROVED
```

Current chain state:

```text
T4aa DISPATCHED / ACTIVE
T7by frozen / not started
T8ap frozen / not started
T7bz frozen / not started
```

The frozen T4aa message was sent successfully to the existing T4 task with
`5.6 Sol High`. No later stage is authorized until its immediately preceding
exact GREEN and T0-owned gate.

## Reviewed Immutable Package

The exact approved candidate is commit:

```text
ff953ccc4ad9699e06e6a26dc3f8256f9ee8960e
```

The independent reviewer verified these exact blobs and file SHA-256 values:

```text
90d4638f03d47ae89be088e7fef78ba2bea44dac  4227f655093b0a91ef7a1a770ed6471cced94302bdfac635cd9538da3773a71a  docs/superpowers/specs/2026-07-15-t4aa-t8ap-targeted-adaptive-refinement-design.md
1baf450461eeb137c370962fbcd625782009d0fb  0f2fa49bba95c2775f4383c225d09e2acd48f74eb6e72bfc77be3a80b5a30f56  docs/superpowers/plans/2026-07-15-t4aa-targeted-adaptive-radial-gate.md
1801cd66c09d53b39c053ea37a61d9cf8b06ef39  8fbc4b16aa1c04cd9ad84b25c7a66849af8b4de1c3b74ec294ec0e4c290a1f34  docs/superpowers/plans/2026-07-15-t8ap-targeted-adaptive-refinement.md
4b73ada7e8e74975236333372ce6bc6d01100fc0  93fbf16b0e5c913bb025c7fdb8535aea35b4efe421237bfef61b8d43a8cc4957  docs/prompts/phase5_t4aa_targeted_adaptive_radial_gate.md
ef170c44ce7548f73e44a040d4f266f6e69e809d  d2191354e6c1e8fbfb2a31ad4a009035fdad24047ca578168e6ff01a9bc445e3  docs/prompts/phase5_t7by_targeted_adaptive_radial_review.md
48268096d7216b830cde66b1aaf45ffc697e724e  6d4e2a33f93899d58d9dc1a5681d50737a05637a00df3076108ea4ae4368991f  docs/prompts/phase5_t8ap_targeted_adaptive_refinement.md
f947a7462333fd09dc12c80675026a99c064688a  75b91045ac7532050b6ba5e9aa6b49ac5a191eb00a3343bb2312446085c818f3  docs/prompts/phase5_t7bz_targeted_adaptive_refinement_review.md
```

Any substantive change to those seven files invalidates the reviewer GREEN and
requires a new immutable identity and re-review.

## Frozen Scientific Scope

Exact new frequencies:

```text
[0.35,0.45,0.85,0.95,1.55,1.65,1.725,
 2.775,2.85,2.95,3.775,3.85,3.95]
```

They are exactly ten midpoints of failed `0.1` parents plus three midpoints of
already-failing `0.05` parents. The literal parent/child mapping is frozen in
design Section 6 and may not be inferred from floating-point adjacency.

Independently verified cardinalities:

```text
T4aa default classification records = 42224
T8ap/T7bz phase records             = 432
T8ap/T7bz child/parent records      = 416
T8ap active/manifest cardinality    = 31/30
```

No lmax extension is authorized. An initial T8ap final-pair failure is YELLOW.
No full grid, uniform `0.025`, recursive midpoint, interpolation, plot, fixture,
Kirchhoff, paper-style output, or production claim is part of this slice.

## Frozen Provenance And Safety Decisions

- T4aa transition identity is exact
  `(kM, sector, ell, point_id)`; its literal envelope is sector-aware.
- T4aa keeps a pre-adapter classification snapshot separate from a final
  adapter snapshot. Checkpoint resume compares only the former; preflight and
  manifest bind both through an explicit hash bridge.
- Producer precision anchors use the frozen first/last per nonempty
  `(kM,sector)` plus point-coverage rule. Zero-transition groups remain empty.
  T7by uses a complementary median/last selection for fresh evidence.
- T8ap must finish fake-compute tests and create one exact five-path
  implementation commit before the first real frequency. Every transaction
  binds that commit; no transaction crosses an implementation identity.
- T8ap uses frequency-local certified-domain radial cache reuse and explicit
  generation/metadata contracts with units, dtype and ordering on all surfaces.
- Accepted source artifacts are immutable and hash/path-bound. Current T0
  fresh hashes match all T8aj, T8ao and T4z/T7bv anchors in the frozen prompt.

## Existing Task Chain

```text
T4 = 019f5fa6-1288-7c01-8a87-4c4370cf5517
T7 = 019f5ed1-b421-7ec2-9bac-8d134855a1ed
T8 = 019f5ece-f578-7b91-8f61-df882c656591
```

Use `5.6 Sol High` for normal dispatch:

```text
T4aa exact GREEN -> T4 sends frozen T7by to existing T7
T7by exact GREEN -> returns only to T0
T0 fresh-verifies T7by -> T0 sends frozen T8ap to existing T8
T8ap exact GREEN -> T8 sends frozen T7bz to existing T7
T7bz -> returns only to T0 and starts nothing
```

YELLOW, RED, incomplete, hash mismatch, nonfinite value, test/scope failure or
ambiguous state stops downstream dispatch. A capacity/system interruption may
resume in the same task with `5.6 Terra High` only after T0 proves process,
checkpoint, artifact, contract and scope safety; never use model switching to
bypass a scientific failure.

## Exact Active Task

The following exact message has been sent to the existing T4 task with
`5.6 Sol High`:

```text
你现在是 T4aa：targeted adaptive radial/Q018 gate 执行线程。请读取并严格执行 docs/prompts/phase5_t4aa_targeted_adaptive_radial_gate.md。该 bounded repair package 已由 T0 独立 reviewer 以 exact `REVIEW GREEN / T0 REPAIR PACKAGE APPROVED` 接受，绑定 commit `ff953ccc4ad9699e06e6a26dc3f8256f9ee8960e`。请只执行十三频率 radial classification/direct-oracle/literal sector-aware envelope/fail-closed adapter gate；严格区分 classification snapshot 与 final-adapter snapshot，禁止 lmax extension、T8ap、observable、plot、fixture、Kirchhoff、paper 或 GitHub。只有 exact GREEN 才向现有 T7 派发冻结 T7by；YELLOW/RED 停止并报告 T0。
```

## Allowed And Forbidden T0 Actions

T0 may update `status.md`, this handoff/archive, create the chain monitor, make
scope-explicit coordination commits, inspect tasks/artifacts/tests, and perform
the exact gated messages above. T0 must not edit the seven reviewed files after
GREEN, create replacement tasks, run scientific solvers, relax thresholds, or
start any downstream stage early.

## Definition Of Done For Current Dispatch Slice

- independent package GREEN and immutable identity are recorded;
- T4aa prompt is sent to the existing T4 task using `5.6 Sol High`;
- a monitor watches T4aa -> T7by -> T8ap -> T7bz without restarting healthy
  processes or bypassing exact decisions;
- active monitor ID is
  `monitor-t4aa-t7by-t8ap-t7bz-targeted-refinement` at 20-minute intervals;
- unrelated T1/T2/T3/T5/T6 worktree changes remain untouched;
- no GitHub push occurs at this non-major dispatch boundary.
