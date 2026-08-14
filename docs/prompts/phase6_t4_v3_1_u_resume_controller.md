# Formal T4 prompt — V3.1-U bounded resume-controller implementation

You are the existing formal SchWO T4 task.  This prompt is dormant until Root
T0 supplies the exact formal-T7 archive-only package approval for gate
`phase6_v3_1_u_resume_controller_repair_1`.

## Claim and boundary

This is bounded repair cycle 1 of the distinct V3.1-U gate.  It repairs only a
missing control-plane resume path after a verified system interruption.  It is
not V3.1-U scientific acceptance, not a retry of failed predecessor r3, not
repair cycle 3 of the exhausted predecessor gate and not V3.2.

Read fully: `project.md`; the frozen current bytes of `status.md`, T0/T4/T7
handoffs; the review-gate liveness protocol/template; the replacement package,
design and formal package-approval archive; and
`docs/phase6_v3_1_u_resume_controller_design.md` with SHA-256
`094235c0ce0158521da81ec0587899dc6dc942ab92866e8afe8f3102487fa9d7`.
Rehash every package binding before work.

## Hard provenance constraint

The interrupted root's original `source_start.json` binds these exact live
coordination bytes:

```text
status.md
  15d29b641b66b061c8865edb72eb811519360bda6a314515fd115cbe1ab96158
docs/handoffs/T0_current.md
  f80779de4990d6d18581d8ee4bccef1393f3a61b6fdb7cdbced272a357ac0ffa
docs/handoffs/T7_current.md
  61e25ccb891b992cc82426a135dca1bccdaafa3f84ccb9bfa338a6d3e8a4c383
```

Do not modify any of them.  Do not update T4 current/archive either during
implementation; return exact results to T0 through the formal task.  Formal T7
reviews for this repair are archive-only.  Current surfaces are updated only
after the science root becomes terminal.

## Allowed implementation files

Only add these four paths:

```text
src/schwgw/validation/phase6_v3_hp_unitarity_resume.py
scripts/phase6_v3_1_hp_unitarity_resume.py
tests/unit/test_phase6_v3_hp_unitarity_resume.py
tests/regression/test_phase6_v3_hp_unitarity_resume_publication.py
```

Do not edit the original five V3.1-U implementation/test files, any frozen
package/prompt/design, any of the seven protected radial files, any threshold,
domain, formula or convention, or any existing evidence root.

## Real-root prohibition for this turn

The only real interrupted root is:

```text
runs/phase6/classic_scattering/
v3_1_hp_unitarity_deficit_v1_20260811T143911Z_py314
```

This implementation turn may inspect it read-only only.  Do not acquire or
rename its lock, create `resume_control`, append JSONL, run a science solver,
create a terminal artifact, change a permission, or start a background process.
All state-changing verification must use fresh temporary copies or synthetic
fixtures.  At end, independently prove the real root's frozen prefix and file
inventory are unchanged and no writer exists.

## Required controller

Implement the exact state machine, stable-lock exclusion, atomic authority chain,
intent/prepared/commit transactions, deterministic recovery and dual-validator
closure in the design.  The CLI must expose clearly separated commands:

```text
inspect   # strictly read-only; no lock or file creation
resume    # requires exact reviewed package, T7 implementation approval and
          # one-use T0 dispatch authority
validate  # terminal read-only original+additive validation
```

`resume` must refuse to start before all three authorities are present and
exact.  It must use the executable/runtime/cwd frozen by the original
`run_contract.json`.  It may append only the exact validated suffix after the
last committed ordinal and must never truncate, replace, reformat or rewrite
existing science bytes.

The original `.writer.lock` is the never-renamed stable exclusion pathname.
Hold its nonblocking flock until the root is terminal 0555 and both validators
pass; then retain it as a 0444 manifest-bound artifact.  All authority,
prepared, checkpoint and commit final names must be published from complete
fsynced staging bytes with Darwin `renamex_np(RENAME_EXCL)` and directory fsync;
partial final-name metadata is forbidden.  An incomplete pre-commit attempt is
preserved and explicitly adjudicated by the next monotone attempt before any
science call.

The additive validator must independently rebuild every attempt, lock identity,
intent/prepared/commit transaction, call ordinal, immutable prefix range,
checkpoint, source identity, route order, terminal artifact and manifest entry.
The original terminal validator with `validate_live_sources=True` remains
mandatory and authoritative.

## Required verification before return

Use real filesystem operations in temporary directories, including
`O_APPEND`, `O_EXCL`, `O_NOFOLLOW`, `fsync`, directory fsync and `flock`.
Exercise at least:

- synthetic prefixes 0, 1, 435 and 495;
- exact continuation calls 435..495 without any call below 435;
- immutable original prefix hashes and full Route-A-before-route-map order;
- Route-U/B/C and terminal publication recovery;
- a second system interruption with monotone attempt authority;
- forced death before/during/after every authority staging/atomic-publication
  boundary, proving the stable lock pathname is never absent and partial
  final-name authorities are impossible;
- forced death after every byte of each prepared Route-A/U/B JSONL block and
  staged Route-C publication, proving an exact authenticated byte prefix is
  completed by appending only its missing tail;
- every corruption/live-writer/symlink/hardlink/torn/duplicate/gap/source-drift
  and authority-drift negative case specified in the design;
- original and additive validators on a complete temporary candidate;
- a temporary byte-for-byte copy of the actual interrupted prefix with all
  science functions replaced by deterministic zero-solver fixtures, proving
  discovery and recovery without touching the source root.

Run focused tests, adjacent V3.1-U tests, Ruff format/check, py_compile and
`git diff --check`.  Rehash the package, design, original five sources, seven
protected files, three frozen coordination files and the real interrupted
prefix at start/end.

Return exact changed-file hashes, test commands/counts, temp-copy evidence
identities and a complete statement that the real root was not modified.  Do
not run `resume` on the real root, dispatch T7, start V3.2 or claim science
PASS.  T0 owns the next formal review and dispatch.
