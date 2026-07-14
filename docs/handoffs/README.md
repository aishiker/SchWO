# Thread Handoffs

This directory stores compact current-state handoff files for Codex threads.
They are the first recovery point when a thread reaches context limits or a new
thread takes over the same workstream.

## Files

Current handoffs use:

```text
docs/handoffs/T0_current.md
docs/handoffs/T1_current.md
docs/handoffs/T3_current.md
docs/handoffs/T4_current.md
docs/handoffs/T6_current.md
docs/handoffs/T7_current.md
docs/handoffs/T8_current.md
...
```

Archived handoffs use:

```text
docs/handoffs/archive/T7_2026-07-08_fig5_fig6_tablei_plan_review.md
```

## Required Content

Each `T*_current.md` file must be concise but precise. Do not paste chat
history. Preserve decisions, reasons, files, commands, test results, and next
actions.

Required sections:

1. Thread role and current status.
2. Completed work.
3. Incomplete work.
4. Blocking issues and non-blocking warnings.
5. Files the next thread must read, ordered by priority.
6. Frozen decisions that must not be reopened casually.
7. Forbidden actions.
8. Superseded prompts that must not be reused.
9. Exact next task the next thread can run.
10. Allowed files to modify, forbidden files, verification commands, and
    definition of done.

## Update Rule

Every thread must update its own current handoff before finishing a task:

```text
T0 -> docs/handoffs/T0_current.md
T7 -> docs/handoffs/T7_current.md
T8 -> docs/handoffs/T8_current.md
```

If the handoff marks a major closeout or historical boundary, copy the previous
current file into `docs/handoffs/archive/` with a dated descriptive name before
overwriting it.

`status.md` remains the authoritative global timeline. Handoff files are
workstream-local recovery summaries and must point back to the relevant
`status.md` entries and prompt files.
