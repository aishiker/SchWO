# T7 Current Handoff
Last updated: 2026-07-16

Thread: T7by, targeted adaptive radial/Q018 gate independent review.

## Exact Decision

```text
ACCEPT GREEN / TARGETED ADAPTIVE RADIAL GATE ACCEPTED
```

This GREEN means only that T0 may dispatch the separately frozen T8ap
package. T7by did not dispatch T8ap and did not authorize new frequencies,
full production, plots, fixtures, paper work, Kirchhoff work, lmax extension,
40/79-frequency production, a 0.025 scan, or GitHub action.

The pre-T7by T7bx handoff is archived at:

```text
docs/handoffs/archive/T7_2026-07-15_pre_t7by_targeted_adaptive_radial_review.md
```

## Independent Nine-Check Result

1. **PASS — commit and scope.** Commit
   `e783e406c8dc74f9d62c280a4c7d07eb794e6ed2` changes exactly the frozen
   gate script, literal envelope, radial solver, and two physics-test paths.
   It changes no IO, scattering, observable, config, fixture, accepted source,
   or unrelated implementation path.
2. **PASS — contract and cardinality.** The independent formula
   `sum_k (ell_max(k)-1) * 2 sectors * 8 points` gives exactly `42,224`.
   Direct raw-record reconstruction finds 42,224 unique complete keys with no
   missing or extra key. All 13 exact checkpoint files are `complete=true`,
   `decision=PASS`, have correct per-frequency cardinality and canonical
   output hash, and bind the classification snapshot.
3. **PASS — fresh default classification.** A deterministic 28-mode fresh
   sample covers all 13 frequencies, both sectors, all eight exact point IDs,
   `default_covered`, structured uncovered, and structured solver-failed.
   All 28 classifications reproduce the raw records exactly. The complete
   artifact contains 40,608 covered, 1,596 uncovered, 20 solver-failed, and
   zero default-other/unstructured records.
4. **PASS — direct oracle.** Classification transitions, oracle evidence, and
   resume preflight have the same 1,616 unique
   `(kM,sector,ell,point_id)` keys. Independent producer-anchor reconstruction
   gives 86 exact anchors and reproduces every stored first/last plus
   point-coverage group. Fourteen zero-transition `(kM,sector)` groups are
   explicitly empty. The independently selected 16-key complementary matrix
   uses the lexicographic median of every nonempty group plus the last missing
   point keys; all fresh dps/tolerance variants pass. Fresh dps80 values match
   stored oracle values exactly, maximum direct relative difference is zero,
   and maximum complementary sensitivity is
   `1.7162826325557131e-7 < 5e-6`.
5. **PASS — literal envelope identity.** Independent AST literal expansion
   gives exactly 1,616 keys and equals the raw transition set. It contains
   exactly the 13 frozen frequencies and 26 sector-aware groups, with no
   interpolation, inferred membership, unstated frequency, or import-time
   run-file loading.
6. **PASS — adapter behavior.** All 16 complementary direct-match anchors
   reproduce oracle `psi`, `dpsi_dr`, and `A_out` with zero relative
   difference and exact solver/warning/point metadata. A default-covered
   opt-in mode makes zero oracle calls. Wrong M, k, token, radius, sector,
   r_out, r_in_eps, rtol, and atol fail closed with exact reasons. A forced
   recoverable fallback proves wrong point membership and wrong ell are
   rejected as `mode is outside measured targeted-adaptive transition set`;
   when the default path covers such a mode, it correctly returns without
   invoking the adapter.
7. **PASS — checkpoint and provenance.** The classification snapshot
   `f20ae61c736034138d0dadded4512c8f1e7afa95124e5dd16624930f1e404c40`
   independently reconstructs from the final gate script, parent-commit
   pre-adapter radial blob, oracle module, Table-I source, and frozen docs.
   The final-adapter snapshot
   `71f5b8ecb9f43cfb0f4f70529767b1a8bbcfa4b7ca470ac633ff8aa4b6d50478`
   independently reconstructs from the exact commit and five blobs; its
   bridge to the classification snapshot is exact. The gate directory has
   exactly 17 expected files, no `.tmp` or quarantine artifact, and the
   manifest hashes every checkpoint. Oracle records declare requested dps80,
   actual dps53, and `double_precision_scipy`; fresh 70/80/100 requests all
   report the same actual backend honestly.
8. **PASS — tests and quality.** Focused pytest:
   `348 passed, 65 warnings, 18 subtests passed`. Ruff: all checks passed.
   The recovery continuation discarded an interrupted partial full-suite run
   and reran from zero: `627 passed, 117 skipped, 1 xfailed, 101 warnings, 81
   subtests passed in 311.79s`. Warnings are the existing Weyl/Wigner
   overflow/divide diagnostics and deliberately exercised SciPy radial
   fail-closed paths; no new failure or warning class occurred.
9. **PASS — isolation.** The required searches for T8ap targeted-adaptive
   refinement, dense-scan production, and paper-style outputs are empty.
   Gate temp/quarantine search, commit whitespace check, and forbidden-scope
   checks are empty. T7by modified no implementation, test, script, config,
   artifact, accepted source, or T0/T4/T8 handoff.

## Frozen Package SHA-256

```text
4227f655093b0a91ef7a1a770ed6471cced94302bdfac635cd9538da3773a71a  design
0f2fa49bba95c2775f4383c225d09e2acd48f74eb6e72bfc77be3a80b5a30f56  T4aa plan
8fbc4b16aa1c04cd9ad84b25c7a66849af8b4de1c3b74ec294ec0e4c290a1f34  T8ap plan
93fbf16b0e5c913bb025c7fdb8535aea35b4efe421237bfef61b8d43a8cc4957  T4aa prompt
d2191354e6c1e8fbfb2a31ad4a009035fdad24047ca578168e6ff01a9bc445e3  T7by prompt
6d4e2a33f93899d58d9dc1a5681d50737a05637a00df3076108ea4ae4368991f  T8ap prompt
75b91045ac7532050b6ba5e9aa6b49ac5a191eb00a3343bb2312446085c818f3  T7bz prompt
```

## Artifact And Implementation SHA-256

```text
aa3af55cd8454d610ebcd31fd8bbda5d37522a9a4e2279c8622decf3459a1b83  classification_manifest.json
002889f81ebce0574b948912217bf1231add3411253855db71adf2769b441d02  oracle_validation.json
a39bacfea6f2728129fde71b791c6f4f18eba05b34e9fa7dcf49b8b64d9824d4  resume_preflight.json
c1ea41c47e17647449c22a6cbd23fe4326a0bacd81f53d05fe70077a05fff32b  gate script
0241d998ad166d834141bbafebfaa0bb5e13ed2f68afaea907c3079140ece90d  literal envelope
70f6bbed3266fdcf229af80b73a51416b8be056acf3d8ecbd73f4c86e73c997e  final radial solver
cecc76558900b0a6fe2b8a1568fd7e48a3cfe903a3472d698714b4a665743eb7  integration-design test
fffefa7f46b505fd2c6e6b108f6700abf05f6e2285e04a3d7e48a26cf305108f  radial-solver test
745ab7dc07a62ceb9923313eed155c0975fad95f1b52934b6f94bba2fdbd35d4  pre-adapter radial blob
```

Complete per-checkpoint hashes remain in
`runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/manifest.md`.

## Review-Only Changed Paths

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-15_pre_t7by_targeted_adaptive_radial_review.md`

The exact GREEN, reviewed commit and hashes, independent counts/maxima, fresh
tests, and isolation evidence were successfully sent to T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636`. Only T0 may dispatch the separately
frozen T8ap package.
