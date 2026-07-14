# T0 Current Handoff

Date: 2026-07-14

Thread: T0, project coordination and gate scheduling.

## Current Status

T8ak generated the frozen 18-frequency by eight-Table-I-point Kirchhoff Eq.
(47) scalar comparison baseline. T7bs independently reproduced all 144 saved
values at higher precision and returned:

```text
ACCEPT YELLOW / FIG5-FIG6 REVIEW-GRID KIRCHHOFF BASELINE PARTIAL
```

T0 inspected the implementation contract, artifact metadata, actual array
dtypes, numerical evidence, hashes, scope, and fresh test results. The YELLOW
is valid but narrowly bounded: embedded NPZ metadata, the JSON sidecar, and the
manifest do not explicitly record the approved `units` and `dtype` contract.
The formula, branches, numerical arrays, backend, grid, isolation, and tests
are not failing.

T0 authorized T8al followed by T7bt. T8al has now reported:

```text
GREEN / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT HARDENED
```

T0 freshly verified commit `7966be1` contains only the authorized serializer
and artifact-contract test, the three new output hashes and three unchanged
T8aj hashes match the recorded values, the baseline directory contains exactly
three files, all 16 frozen `.npy` fingerprints pass, embedded/sidecar/manifest
metadata agree with actual dtypes, focused pytest reports `9 passed`, and Ruff
is clean. T8al's recorded full-suite result remains subject to the independent
T7bt rerun required by the frozen gate.

T7bt is currently active in the existing T7 task. T0 must wait for its exact
decision before accepting the milestone or synchronizing GitHub.

## Frozen Plan And Prompts

- Implementation plan:
  `docs/superpowers/plans/2026-07-14-t8al-kirchhoff-metadata-contract.md`
- T8al prompt:
  `docs/prompts/phase5_t8al_fig5_fig6_kirchhoff_metadata_contract.md`
- T7bt prompt:
  `docs/prompts/phase5_t7bt_fig5_fig6_kirchhoff_metadata_contract_review.md`
- Planning package commit:
  `20644eb docs: plan Kirchhoff metadata contract hardening`

The plan freezes the exact unit strings, dtype strings, schema-v2 identifier,
per-array `.npy` SHA256 fingerprints, TDD sequence, regeneration boundary,
fresh tests, exact decision labels, and automatic T8al-to-T7bt state machine.

## Runtime Task Bindings

- T0: `019f5ec5-84ba-79e2-8c77-1160b150a636`
- T8: `019f5ece-f578-7b91-8f61-df882c656591`
- T7: `019f5ed1-b421-7ec2-9bac-8d134855a1ed`

T8al completed in the existing T8 task with `gpt-5.6-sol`, thinking `high`,
and its gated T7bt dispatch succeeded. T7bt is running in the existing T7 task
with the same model settings. It is review-only and must report one frozen
exact decision to T0 without starting a later stage.

Only an explicit model-capacity or system interruption may be recovered in the
same task with `gpt-5.6-terra`, thinking `high`, after checking safe state and
avoiding unnecessary recomputation. Scientific failures, non-finite values,
test failures, scope violations, or fingerprint mismatches never qualify for
model fallback.

The existing heartbeat automation `monitor-t8ak-t7bs-gate` has been updated in
place and renamed `Monitor T8al–T7bt metadata gate`; it checks this chain every
20 minutes and must delete itself after the gate is resolved.

User pause instruction: after T8al, T7bt, and T0 gate handling are fully
finished, including the T0 decision, durable status/handoff update, and any
GitHub milestone sync that is actually authorized by an independent GREEN,
T0 must enter a Codex-update maintenance pause. It must not design, dispatch,
or start a later stage until the user explicitly resumes the project.

## Exact T8al Boundary

T8al may modify only:

- `src/schwgw/io/kirchhoff.py`
- `tests/unit/test_kirchhoff_artifact.py`
- the existing NPZ, JSON sidecar, and manifest in
  `runs/phase5/fig5_fig6_kirchhoff_baseline/`
- `status.md`, `docs/handoffs/T8_current.md`, and the required T8 handoff
  archive

It must:

- add explicit top-level `units` and `dtype` mappings to embedded NPZ metadata
  and the JSON sidecar;
- record the same mapping in the manifest;
- bump only the artifact schema to
  `phase5_t8al_kirchhoff_review_grid_v2_units_dtype`;
- first add contract assertions and observe the intended TDD RED;
- back up the three T8ak files under
  `/tmp/schwo_t8al_pre_metadata_contract/` before regeneration;
- regenerate only those same three artifact paths with the existing script;
- prove every non-metadata array is exactly equal to T8ak and retains the
  per-array `.npy` SHA256 fingerprint frozen in the plan;
- rerun focused tests, Ruff, full pytest, input hashes, forbidden-diff, and
  forbidden-output checks.

It must not change the Eq. (47) formula, branch conventions, `mpmath` backend,
precision, grid, array values, masks, phases, non-claims, solver, Q018,
normalization, denominator, polarization, configs, plotting, or accepted T8aj
source artifacts.

## Frozen Evidence

Accepted T8aj source SHA256, which must remain unchanged:

```text
NPZ      a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb
JSON     2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537
manifest 86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf
```

Pre-T8al T8ak output SHA256:

```text
NPZ      a91f0a5f5eb672ac897ea776f7577d4f33b89c72154dc1b665c8ced06cbec53c
JSON     86670c426ada2284d334a017b6abdfc36443d0fb7ea82606f3d544de17788a19
manifest 53d852b25bd73bb25cecb37518e72a010c5b3882cf5e86799e4b695178586d49
```

T7bs fresh evidence:

- all 144 values independently recomputed at 100 dps and exactly equal after
  one `complex128` conversion;
- four 120-dps Kummer-transformation corner checks passed;
- maximum eta mismatch
  `4.337937456566632e-05 < 5e-5`;
- focused pytest `9 passed`, Ruff clean;
- full pytest `558 passed, 117 skipped, 1 xfailed, 85 warnings, 79 subtests`;
- forbidden production diff and downstream-output checks empty.

## Exact Decisions

T8al may use only:

```text
GREEN / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT HARDENED
YELLOW / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT PARTIAL
RED / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT BLOCKED
```

T7bt may use only:

```text
ACCEPT GREEN / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT ACCEPTED
ACCEPT YELLOW / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT PARTIAL
REJECT RED / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT FAILED
```

T7bt is review-only. It must not repair T8al or start any plotting, production,
fixture, or paper-style stage.

## GitHub Status

```text
GitHub sync pending independent GREEN
```

T7bs is YELLOW, so this is not a major-node sync point. T8 and T7 have no push
authority. After T7bt exact GREEN, T0 must independently verify the result,
update `status.md` and this handoff, inspect the accumulated dirty worktree,
and then perform only a scope-explicit non-force GitHub synchronization under
the project rule. Broad staging, force push, history rewrite, secrets, and
unreviewed files remain forbidden.

## Current Task

T7bt is active in existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` with 5.6 Sol High. It must execute
`docs/prompts/phase5_t7bt_fig5_fig6_kirchhoff_metadata_contract_review.md`
without modifying implementation or artifacts. T0 takes no further action
until T7bt returns its exact decision, except capacity-only recovery under the
frozen monitor policy.

## Definition Of Done For This Gate

- T8al exact GREEN proves explicit units/dtypes in all three metadata surfaces
  while every non-metadata array remains byte-identical in canonical `.npy`
  form.
- T8al starts T7bt only after that GREEN and complete fresh verification.
- T7bt independently verifies contract equality, actual dtypes, fingerprints,
  artifact scope, source hashes, tests, and forbidden boundaries.
- T0 inspects T7bt's exact decision and evidence.
- Only T7bt exact GREEN plus T0 acceptance may trigger milestone status/handoff
  finalization and the scoped GitHub synchronization rule.
- After that closure, or after recording a terminal YELLOW/RED outcome, delete
  the gate monitor and pause without preparing or dispatching a next task.
