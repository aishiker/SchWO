# Phase 6 V3.0 dispatch addendum — formal T1 identity correction

Created at: `2026-08-11T11:17:34Z`

Timezone: `UTC`

Scientific stage: `V3.0`

Artifact revision: `dispatch-addendum-r1`

## Correction

The frozen transition document
`docs/phase6_v2_to_v3_transition.md` correctly records all scientific
authority identities, the bounded V2-to-V3 adjudication, the V3.0 prompts and
the required T1-to-T7-to-T4 dependency. Its statement that no formal T1 task
was present was based on the Codex list API's most-recent-50 window and is
superseded only for task-dispatch state by this addendum.

The user supplied a screenshot showing the older formal T1 task. A read-only
query of the local Codex task index and a subsequent official `read_thread`
call resolved it as:

```text
thread_id: 019f5fb7-9d0a-78b0-af5e-25a663dd153b
title: 接手T1线程
status: idle before dispatch
archived: false
cwd: /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO
role: formal T1 literature and physical conventions
```

Root T0 dispatched the unchanged frozen T1 prompt to that exact existing task
using `gpt-5.6-sol/high`. No new task or substitute reviewer was created.

Frozen prompt and science identities are unchanged:

| Input | SHA-256 |
|---|---|
| `docs/prompts/phase6_t1_v3_0_literature_formula_freeze.md` | `03a352b881c97f1f767092340d5dc65f61e800dafde9c28b9f870eaa5ad454cc` |
| `docs/prompts/phase6_t7_v3_0_contract_review.md` | `74a14af6d9876ac5f29431693a27d6279c7838448c93974fc5a0812a8ad50563` |
| `docs/prompts/phase6_v3_master_prompt.md` | `f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7` |
| `docs/phase6_v2_to_v3_transition.md` | `4493c1359974bf58abcc4b93ebe30a6ebab5edef9bc229654c873846a95bfebb` |

This is a bounded control-plane correction. It changes no formula, convention,
domain, threshold, source identity, protected implementation byte, immutable
science artifact, branch authorization predicate or claim status.

## Current dependency state

```text
formal T1 V3.0: dispatched / active
formal T7 V3.0: not dispatched; awaits T1 checkpoint and identity verification
formal T4 V3.1: not dispatched; awaits T7 ADVANCE/PASS and
                absorption_branch_authorized=true
V3 numerical execution: not authorized
```

No global GREEN is claimed. All V3 science remains NOT_ASSESSED while V3.0 is
in progress.
