# T7 Current Handoff

Last updated: 2026-07-14

Thread: T7bt, Fig.5/Fig.6 Kirchhoff units/dtype metadata-contract independent
review.

## Thread Role And Current Status

T7bt completed an independent read-only review of the bounded T8al
metadata-contract hardening.

Exact decision:

```text
ACCEPT GREEN / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT ACCEPTED
```

All nine frozen review checks pass. The T8al correction is metadata-only:
every one of the 16 non-metadata arrays has canonical NumPy `.npy` bytes
identical to the hash-verified T8ak backup and matches its frozen SHA256
fingerprint. Embedded NPZ metadata, JSON sidecar, manifest, and actual array
dtypes agree on the exact units/dtype contract.

This acceptance does not authorize T7 to start plotting, dense production,
fixtures, paper-style work, GitHub synchronization, or any later task.

The pre-T7bt T7bs handoff is archived at:

```text
docs/handoffs/archive/T7_2026-07-14_pre_t7bt_metadata_contract.md
```

## Nine Required Checks

1. **PASS — commit scope.** Commit `7966be1 fix: record Kirchhoff units and
   dtypes` changes exactly `src/schwgw/io/kirchhoff.py` and
   `tests/unit/test_kirchhoff_artifact.py`.
2. **PASS — schema.** Embedded metadata and sidecar both use exactly
   `phase5_t8al_kirchhoff_review_grid_v2_units_dtype`.
3. **PASS — metadata coverage/equality.** Embedded and sidecar top-level
   `units` and `dtype` mappings are equal and cover exactly all 16
   non-metadata NPZ arrays, with no omission or extra entry. Full embedded
   metadata equals the sidecar after removing its two output-file fields.
4. **PASS — actual dtype.** Every actual array dtype exactly equals its
   declared dtype, including `complex128`, `<U16`, `bool`, and all `float64`
   arrays.
5. **PASS — manifest.** The manifest contains exactly the same 16 unit/dtype
   pairs and records the current NPZ and sidecar hashes.
6. **PASS — numerical identity.** For every non-metadata array, canonical
   `.npy` bytes are exactly identical between the current artifact and the
   T8ak backup. All 16 SHA256 values match the frozen mapping in the T8al plan.
7. **PASS — source and file boundary.** T8aj NPZ/JSON/manifest hashes remain
   unchanged; the current baseline directory contains exactly NPZ, JSON
   sidecar, and manifest. The backup itself has all three frozen T8ak hashes.
8. **PASS — fresh tests.** Focused pytest is `9 passed in 0.35s`; Ruff is
   clean; full pytest is `558 passed, 117 skipped, 1 xfailed, 85 warnings, 79
   subtests passed in 313.30s (0:05:13)`.
9. **PASS — forbidden scope/output.** The T8al commit and worktree have no
   forbidden production-path diff. Forbidden plot/dense-production/
   paper-style searches are empty, and no implementation or artifact was
   modified by T7bt.

## Hashes Rechecked

Pre-hardening T8ak backup:

```text
a91f0a5f5eb672ac897ea776f7577d4f33b89c72154dc1b665c8ced06cbec53c  tablei_kirchhoff_baseline_values.npz
86670c426ada2284d334a017b6abdfc36443d0fb7ea82606f3d544de17788a19  tablei_kirchhoff_baseline_values.npz.json
53d852b25bd73bb25cecb37518e72a010c5b3882cf5e86799e4b695178586d49  manifest.md
```

Accepted T8aj inputs, unchanged:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  tablei_dense_review_values.npz
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  tablei_dense_review_values.npz.json
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  manifest.md
```

Current T8al outputs:

```text
66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55  tablei_kirchhoff_baseline_values.npz
0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3  tablei_kirchhoff_baseline_values.npz.json
fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632  manifest.md
```

## Independent Array Evidence

The review loaded the frozen T8ak NPZ backup and current T8al NPZ directly,
without calling the serializer or Kirchhoff compute API. For all 16 arrays it:

- serialized each array independently with `np.save(..., allow_pickle=False)`;
- required exact equality of the resulting bytes between old and new;
- recomputed SHA256 from the current bytes;
- required equality to the frozen per-array mapping in the T8al plan;
- required the actual dtype to equal the declared mapping.

Result:

```text
non_metadata_array_count 16
T7BT_ARRAY_BYTE_IDENTITY_AND_FINGERPRINTS=PASS
T7BT_METADATA_SURFACES=PASS
```

## Checks Run

```text
focused pytest: 9 passed in 0.35s
Ruff: All checks passed!
full pytest: 558 passed, 117 skipped, 1 xfailed, 85 warnings,
             79 subtests passed in 313.30s (0:05:13)
```

The first forbidden-output command omitted the prompt's stderr suppression and
returned exit 1 because all three forbidden directories do not exist.
`systematic-debugging` identified this as a reviewer-command construction
issue. The exact frozen command was then rerun and returned exit 0 with empty
output. No forbidden artifact was found.

## Review-Only Changed Paths

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-14_pre_t7bt_metadata_contract.md`

No source, test, script, config, artifact, plot, dense-production output, or
other handoff was modified by T7bt.

## Incomplete Work And Next Owner

- T0 must inspect this exact GREEN, close the gate, update durable T0 records,
  and independently decide/perform any scope-explicit GitHub milestone sync.
- Under the user's pause instruction, T0 must then enter maintenance pause and
  must not design or dispatch a later stage until the user explicitly resumes.
- T7bt starts no next task.

## Frozen Decisions

- Eq. (47), its branches, no-conjugation policy, grid, backend `mpmath 1.4.1`,
  `dps=60`, and all numerical arrays remain unchanged.
- Kirchhoff remains scalar, polarization-independent, and comparison-only.
- It must not enter solver, denominator, masks, normalization, calibration,
  Q018, boundary policy, or polarization channels.
- The exact units/dtype mappings, schema-v2 identifier, and all 16 frozen array
  fingerprints are accepted as the artifact contract.

## Forbidden Actions

- Do not modify or regenerate the T8al implementation or artifacts from T7.
- Do not create plots, 40-frequency/dense production, fixtures, interpolation,
  smoothing, Appendix D/E, or paper-style candidates.
- Do not push GitHub or start a later scientific task from T7.
- Do not change models to bypass a scientific, scope, or test failure.

## Files The Next Thread Must Read

1. `status.md`
2. `docs/handoffs/T7_current.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T8_current.md`
5. `docs/prompts/phase5_t7bt_fig5_fig6_kirchhoff_metadata_contract_review.md`
6. `docs/superpowers/plans/2026-07-14-t8al-kirchhoff-metadata-contract.md`
7. `src/schwgw/io/kirchhoff.py`
8. `tests/unit/test_kirchhoff_artifact.py`
9. the three current baseline files

## Superseded Prompts

- T8ak/T8al implementation prompts and T7bs review prompt are complete and
  must not be reused to mutate this accepted artifact.
- T12/T12b and all later plotting/production prompts remain superseded.

## Exact Next Task And Definition Of Done

Send the exact GREEN plus new three hashes, 16/16 fingerprint result,
focused/Ruff/full-pytest results, and review-only file list to T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636`.

T7bt is done only after those records are freshly verified, all six T8aj/T8al
hashes remain unchanged, and the T0 message succeeds.
