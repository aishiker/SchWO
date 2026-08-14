# T4 archive — V3.1-X sentinel repair-cycle-2 source-ledger design analysis

Date: 2026-08-13
Task: formal T4, zero-science design analysis
Primary design:
`docs/phase6_v3_1_x_sentinel_repair_cycle2_source_ledger_design.md`
SHA-256:
`582bc3248a6acf7164485203d317b2cdc0d2a7819a13dcdb584e86e9a90bebdf`

## Result

```text
DESIGN READY / V3.1-X FINAL SOURCE-LEDGER REPAIR IS BOUNDED AND NON-CIRCULAR
SCIENCE STATUS / NOT_ASSESSED
EXECUTION AUTHORITY / NONE
```

The terminal blocker was independently reconstructed from immutable bytes.
Canonical request records present object members as
`[context,mode,nlink,path,sha256,size]`; the WLS creates semantically identical
associations as `[context,path,sha256,size,mode,nlink]`.  Wolfram `SameQ`
rejects the different Association insertion order at line 132.  All eight
records have identical semantic values, and the numerical call at line 143 is
not reached.  Attempt 0002 therefore made zero scientific calls and establishes
no numerical failure.

## Recommended bounded repair

Implement one and only one WLS semantic normalizer:

```text
[context, path, sha256, size, mode, nlink]
```

It first requires the exact six-key set and exact types/values, then projects
both expected and freshly discovered records into that fixed list.  The eight
record list remains in the frozen context order; there is no list sorting,
set conversion, deduplication, field dropping, path normalization fallback or
structural Association equality.

The repair is insufficiently tested by a Python fake that copies request
records into output.  Therefore the first post-review executable stage must be
a distinct one-use source-load micro-sentinel: exactly one real Wolfram launch
for `V3A-MODE-BHPT-RW-001/P1`, complete request/overlay/Paclet/context/FindFile
and start/end ledger closure, then exit before `ReggeWheelerRadial`.  Required
counters are one Wolfram launch and zero external API, solver, boundary,
overlap and scientific calls.  The result is explicitly non-scientific and
non-reusable.

## Exact authority sequence

1. Freeze a repair-cycle-2 package and formal package review.
2. Modify at most the WLS, producer, CLI, unit test and regression test.  The
   core direct physics module remains frozen.
3. Formal T7 implementation delta review must `ADVANCE`.
4. T0 may then publish only
   `T0_2026-08-13_v3_1_x_source_load_micro_sentinel_dispatch_attempt_0001.json`
   for a fresh root matching
   `v3_1_x_source_load_micro_sentinel_v1_<UTC>_py314`.
5. Formal T7 review of that immutable micro root must `ADVANCE`.
6. Only then may T0 publish the distinct
   `T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0003.json`
   for a fresh
   `v3_1_x_external_direct_sentinel_repair2_v1_<UTC>_py314` root.
7. Formal T7 review of the exact 35/70/105 full sentinel must `ADVANCE` before
   the unchanged official attempt-0001 can become eligible.

Future review paths are fixed by the package, but their future digests are
supplied only by a later T0 dispatch.  This removes circular implementation
authority.  No alternate path, current handoff, glob, environment selector or
fallback authority is accepted.

Any implementation-delta, micro or full-sentinel failure is terminal
`ESCALATE`; attempts 0001/0002 and their roots remain permanently non-reusable,
and repair cycle 3 is forbidden.

## Allowed implementation scope

```text
scripts/phase6_v3_1_x_bhpt_direct.wls
src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
scripts/phase6_v3_1_x_external_direct.py
tests/unit/test_phase6_v3_external_direct.py
tests/regression/test_phase6_v3_external_direct_publication.py
```

Explicitly excluded:

```text
src/schwgw/validation/phase6_v3_external_direct.py
all seven protected radial files
all V3.0 domain/threshold/convention authorities
all snapshot/overlay and failed-root bytes
```

## Mandatory adversarial closure

The future test package must cover:

- all Association member-order permutations as positives after exact-key-set
  validation;
- missing/extra/duplicate JSON members and source records;
- record/context reorder, wrong field/value/type and duplicate context/path;
- path traversal, alias, symlink, hardlink, inode replacement and source drift;
- competing/preloaded Paclet contexts and wrong `FindFile` origin;
- fake-child self-confirmation rejected as formal boundary evidence;
- exact micro key/operation and zero counters, with solver branch unreachable;
- cross-use of micro evidence as full-sentinel/official science rejected;
- dispatch/root/review namespace, non-circular future review and one-use
  consumption;
- child failures at Popen/stream/timeout/terminate/kill/wait/reap/result/
  manifest/permission boundaries;
- unknown/extra/torn/noncanonical artifacts and manifest tampering.

Additional newly identified fail-closed surfaces are duplicate JSON-member
collapse, preloaded context/Paclet contamination, same-byte inode replacement,
micro/full operation confusion, fake-child self-confirmation and source drift
after micro approval.  These are control/provenance hazards only; closing them
does not alter a scientific threshold.

## Resource conclusion

The immutable failed first-child durations were approximately 3.24 s and
4.87 s; the latter included complete package/context loading.  The micro
projection is therefore lower/central/upper `3 s / 5 s / 120 s`, with one
process, zero science and a 16 MiB hard root cap.  These are fail-closed
operational limits.  They do not alter the full sentinel's frozen resource
gate.  No defensible numerical runtime projection exists because neither
failed attempt reached a numerical call.

## Frozen review state

Passed/frozen: repaired real argv interface; attempt-0002 one-use authority;
35-call graph totality; child lifecycle; package/domain/threshold/convention;
seven protected identities; eight exact source values; no reuse/downstream
execution.

Failed/in scope: only normalized source-ledger comparison plus the missing
real RawJSON-to-Wolfram source-load boundary test.

Not assessed: 35-call science, 70 boundary solutions, 105 overlaps, official
science, 16 thresholds, five certificates, V3.2 and global GREEN.

## Start/end identity audit

Every listed identity was rehashed at the start and again after writing these
two design-only documents.  The values are unchanged:

| Role | Start SHA-256 | End SHA-256 |
|---|---|---|
| WLS | `24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6` | `24df8e68eef190dfd43348537bf2ce487aec5947f439f117f072bb96e8751da6` |
| direct core | `981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4` | `981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4` |
| producer | `81a33a4157d6e07b03621bff069c9383914464c16ce4314a9f7a556c7e1cd088` | `81a33a4157d6e07b03621bff069c9383914464c16ce4314a9f7a556c7e1cd088` |
| CLI | `072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768` | `072a3520bb32090e1dd872037f4570cd29a35ffc7d47a0788d426d3840e7e768` |
| unit test | `056c7273edbdb612d3fc99c4b493f2fe4c96dc15b8ae7aa3a872587f33f3aaba` | `056c7273edbdb612d3fc99c4b493f2fe4c96dc15b8ae7aa3a872587f33f3aaba` |
| regression test | `24d26a8a9c2e0ad573b97f76b39db7743f2d6639cd57978be93f0c310062f858` | `24d26a8a9c2e0ad573b97f76b39db7743f2d6639cd57978be93f0c310062f858` |
| package | `6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752` | `6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752` |
| domain | `803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b` | `803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b` |
| thresholds | `91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a` | `91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a` |
| convention | `82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a` | `82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a` |

Seven protected source SHA-256 values are unchanged:

```text
radial_solver.py             9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
conditioned_radial.py        91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
scaled_tortoise_radial.py    d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
adaptive_jost_radial.py      3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
matching.py                  9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
physical_boundary_radial.py  fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
boundary_conditions.py       b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
```

Failed-root terminal identities are unchanged:

```text
attempt 0001 manifest d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772
attempt 0001 failure  c002664933d58913b5793ffc1100a5958cb1dfdd12d0c9b3664ffa9ddfb2f541
attempt 0002 ledger   1aefc643d6bc8b18218a3d26817a3b5e03f66c2b402c4338b607954cb1a36d08
attempt 0002 manifest 6e0d2349d998f76ee8d149e4551bf27222c5d93bf4ec9fb7b790adbc9f506109
attempt 0002 failure  c002664933d58913b5793ffc1100a5958cb1dfdd12d0c9b3664ffa9ddfb2f541
```

No WolframKernel, solver or scientific process was launched; no dispatch or
evidence root was created; status and current handoffs were not edited.

## T0 recommendation

Freeze the primary design and this archive into a final repair-cycle-2
package, then follow the staged authority graph exactly.  Do not authorize a
35-call sentinel before the real source-load micro-sentinel receives formal
T7 `ADVANCE`.  This is the minimum repair that tests the actual failed boundary
without changing science.
