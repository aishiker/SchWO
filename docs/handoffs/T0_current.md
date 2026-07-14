# T0 Current Handoff

Date: 2026-07-14

Thread: T0, project coordination and gate scheduling.

## Current Status

The bounded T8al/T7bt Kirchhoff units/dtype metadata-contract gate is closed.

T7bt exact decision:

```text
ACCEPT GREEN / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT ACCEPTED
```

T0 exact decision:

```text
ACCEPT GREEN / FIG5-FIG6 KIRCHHOFF METADATA GATE CLOSED
```

All nine frozen checks pass. The accepted correction is metadata-only: every
one of the 16 non-metadata arrays has canonical NumPy `.npy` bytes identical
to the frozen, hash-verified T8ak backup and matches its frozen fingerprint.
Embedded NPZ metadata, JSON sidecar, manifest, and actual dtypes agree on the
exact units/dtype contract.

No scientific or production stage follows this gate. The user requested a
Codex-update maintenance pause after the current T8/T7/T0 round.

## T0 Fresh Verification

- Commit `7966be1 fix: record Kirchhoff units and dtypes` contains exactly:
  - `src/schwgw/io/kirchhoff.py`
  - `tests/unit/test_kirchhoff_artifact.py`
- Direct backup/current audit, without calling the serializer or compute API:

```text
T0_T7BT_NINE_GATE_CORE_AUDIT=PASS arrays=16
```

- All 16 canonical `np.save(..., allow_pickle=False)` byte streams are
  old-vs-new identical and match the frozen SHA256 mapping.
- Schema is exactly
  `phase5_t8al_kirchhoff_review_grid_v2_units_dtype`.
- Embedded and sidecar `units`/`dtype` mappings cover all and only the 16
  non-metadata arrays; manifest lines and actual array dtypes agree.
- The baseline directory contains exactly the NPZ, JSON sidecar, and manifest.
- Focused pytest: `9 passed in 0.39s`.
- Ruff: `All checks passed!`.
- T0 full pytest:
  `558 passed, 117 skipped, 1 xfailed, 85 warnings, 79 subtests passed in
  317.86s (0:05:17)`.
- Forbidden production diff and downstream-output checks are empty.
- Existing warnings remain the known Weyl/Wigner/radial numerical warnings.

## Accepted Hashes

Pre-hardening T8ak backup:

```text
a91f0a5f5eb672ac897ea776f7577d4f33b89c72154dc1b665c8ced06cbec53c  tablei_kirchhoff_baseline_values.npz
86670c426ada2284d334a017b6abdfc36443d0fb7ea82606f3d544de17788a19  tablei_kirchhoff_baseline_values.npz.json
53d852b25bd73bb25cecb37518e72a010c5b3882cf5e86799e4b695178586d49  manifest.md
```

Accepted T8aj inputs:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  tablei_dense_review_values.npz
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  tablei_dense_review_values.npz.json
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  manifest.md
```

Accepted T8al outputs:

```text
66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55  tablei_kirchhoff_baseline_values.npz
0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3  tablei_kirchhoff_baseline_values.npz.json
fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632  manifest.md
```

## Frozen Scientific Boundary

- Eq. (47), principal branches, positive-frequency no-conjugation policy,
  coordinate-derived eta, backend `mpmath 1.4.1`, and `dps=60` are unchanged.
- The accepted 18-frequency by eight-Table-I-point grid and every numerical
  array, mask, phase, and non-claim are unchanged.
- Kirchhoff remains a scalar, polarization-independent comparison baseline.
- It must not enter the solver, denominator, masks, normalization,
  calibration, Q018/boundary policy, or polarization channels.
- No plot, dense/40-frequency production, fixture, interpolation, smoothing,
  Appendix D/E, or paper-style candidate is authorized.

## GitHub Milestone Synchronization

This independent GREEN is a high-risk-gate major node under `project.md`.

Authorized synchronization scope:

- six existing T8ak/T8al implementation/design/plan commits from `d6519e4`
  through `7966be1`;
- `project.md` with the user-approved Codex auto-dispatch and GitHub milestone
  rules;
- `status.md`;
- current T0/T7/T8 handoffs;
- T0/T7/T8 archives belonging to the T8aj→T7br→T8ak→T7bs→T8al→T7bt chain.

Explicitly excluded:

- independent T1/T2/T3/T5/T6 handoff changes;
- ignored `runs/` artifacts and `/tmp` backups;
- raw/private data, secrets/credentials, unexpected large files, and any
  unrelated or unreviewed path.

Remote preflight:

- configured repository is private;
- default/current authorized branch is `main`;
- `origin/main...HEAD` was `0 6` after fresh fetch;
- GitHub authentication is available;
- outgoing committed secret scan is clean;
- force push, history rewrite, branch deletion, PR creation, and repository
  visibility changes are not authorized.

Pre-push status:

```text
GitHub sync authorized; completion verification pending
```

## Runtime Task And Monitor State

- T0 task: `019f5ec5-84ba-79e2-8c77-1160b150a636`
- T8 task: `019f5ece-f578-7b91-8f61-df882c656591`
- T7 task: `019f5ed1-b421-7ec2-9bac-8d134855a1ed`

T8al and T7bt are complete. Neither task starts any later work. The heartbeat
automation `monitor-t8ak-t7bs-gate` must be deleted after the GitHub sync and
final T0 verification.

## Maintenance Pause And Exact Next Action

No next-task prompt is provided. This is intentional and required because the
user asked to update Codex after the current round.

After the scope-explicit non-force push is verified:

```text
PAUSED / USER CODEX UPDATE
```

During the pause:

- do not design, schedule, dispatch, or start another task;
- do not reuse T8ak/T8al/T7bs/T7bt prompts;
- do not create a new monitor or thread;
- wait for an explicit user instruction to resume.

## Definition Of Done

- T7bt exact GREEN independently accepted by T0.
- T0 fresh artifact, fingerprint, schema, scope, focused, Ruff, and full-suite
  checks pass.
- Closeout status and T0 handoff are committed in the explicit milestone
  scope.
- Current `main` is pushed non-force and `origin/main == HEAD` is verified.
- GitHub completion is recorded durably.
- The gate monitor is deleted.
- T0 enters maintenance pause without a next-stage prompt or dispatch.
