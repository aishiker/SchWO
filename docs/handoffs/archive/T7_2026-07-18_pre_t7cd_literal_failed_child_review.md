# T7 Current Handoff — T7cc Literal Failed-Child Radial Gate Independent Review

Date: 2026-07-20
Role: T7cc review-only. No repair, downstream dispatch, threshold change, implementation/artifact mutation, or GitHub action.

## Exact decision

```text
ACCEPT GREEN / LITERAL FAILED-CHILD RADIAL GATE ACCEPTED
```

This decision authorizes only T0 fresh verification. T7cc did not start T8ar or T7cd and does not authorize a new midpoint, uniform/full grid, amplification, production, plot, fixture, Kirchhoff, or paper-style work.

## Start gate and frozen identity

- T4 current reports exactly `GREEN / LITERAL FAILED-CHILD RADIAL GATE READY`.
- Reviewed repair candidate: `f3a64522642abfaa2e0f3933125df06ae76895e4`, parent `fa22f20f775c1b15ae533c03047d156687e5f3bf`.
- Frozen seven-file SHA-256 values are unchanged:
  - design: `0052af7360e06f5218360839a50e21b6d154cfc98dffd526328c43d962f58b58`;
  - T4ac plan: `824594ad257f39d7e56d738837b16ceb8cde081bf12acba5e294fcaad594a75d`;
  - T8ar plan: `972c74186364a3506001616b4f8fe8deb1563a1a1f44548b89bd96f08bd6ef7c`;
  - T4ac prompt: `9189e68169774cfdf9abe6afee31c81ef95c30cc15269c7d9a8ede76d77ee655`;
  - T7cc prompt: `4a8097a3b8728b290139596e4611440a3de34a1a26c4503c3c38c074c462a3b7`;
  - T8ar prompt: `dcdb2849111475cd2dbe45371607bc96181ca4abcadcf27d28f2cf20dc9fb242`;
  - T7cd prompt: `0e9fcb766e722aa15f59544e5997eb81f861f2c2375f861389604a944b9395ed`.
- The pre-review T7cb handoff was archived byte-for-byte at `docs/handoffs/archive/T7_2026-07-18_pre_t7cc_literal_failed_child_radial_review.md`; both source-before-replacement and archive SHA-256 are `57cae192228d9d29b1cc39c82cc8c7bd3844811e3a0b35faaa1dbdc2c799bd01`.

## Independent frequency, lmax, and classification reconstruction

- Direct loading of all 153 immutable T7cb hierarchy failures yields exactly 41 unique literal child midpoints. Both strict phase-failed intervals are included. Seven child intervals having no hierarchy failure are absent, and no passing child interval or unstated frequency is added.
- Exact ordered frequencies:
  `[0.3125, 0.3375, 0.3625, 0.3875, 0.8625, 0.9125, 0.9375, 0.9625, 0.9875, 1.5125, 1.5375, 1.5625, 1.5875, 1.6125, 1.6375, 1.6625, 1.6875, 1.70625, 1.71875, 2.78125, 2.79375, 2.8125, 2.8375, 2.8625, 2.8875, 2.9125, 2.9375, 2.9625, 2.9875, 3.75625, 3.76875, 3.78125, 3.79375, 3.8125, 3.8375, 3.8625, 3.8875, 3.9125, 3.9375, 3.9625, 3.9875]`.
- Tokens and all four lmax windows per frequency were independently derived from the frozen parent rules. Maximum lmax is 360. The exact Cartesian count is `146,416 = sum_k (max(lmax_k)-1)*2*8`, with unique complete `(k, sector, ell, point_id)` keys.
- Independent class counts: `140,096 default_covered`, `6,270 default_fail_closed_uncovered`, `50 default_fail_closed_solver_failed`, and zero unstructured/default-other. Exact transition count is `6,320`.

## Checkpoints, artifacts, and provenance

- The active gate contains exactly 45 files: 41 atomic checkpoint JSON files and four roots. Every checkpoint is `complete=true`, `decision=PASS`; canonical input-contract hashes, output hashes, exact per-frequency key cardinality, and ordered manifest membership independently match. There is no active temp/quarantine file.
- Root SHA-256 values:
  - classification: `e5c934568ff1a9f80838df3fc674fea153e4c638777e6d7c9c2c2d32d0024e5b`;
  - oracle: `b4954a152aa81853fe53931bcb9ee9820b6d6da6d923019288f276d0519c52c6`;
  - resume preflight: `08b5542a26c0b95f6bf10005aeb21681f75735f53b924f894f1c133081ee2873`;
  - manifest: `6b55500aae750f7b2400627825220f18e2ca9f608a4c977707e4f2ec363e78c8`.
- Pre-adapter classification snapshot: `e675b751fd4beae2446597034b99f847e0cc3528551bfc30f8efd3460ad944fe`.
- Final-adapter snapshot: `8188b306fea0190654f752190f0ab6e96ef6970b16fea704b9cdb99ca96c7ccc`.
- Both snapshots were independently canonicalized; the classification-to-final bridge, immutable T8aq/T4ab/T7cb input hashes, parent radial blob `12a3bd178499548c4b3ad338266eb20c46271595`, and final implementation identities all match.

## Direct oracle, literal envelope, and adapter

- Raw classification transitions, direct-oracle records, and resume-preflight records have exact equality of all `6,320` sector-aware keys. There are 38 explicit zero-transition groups and 44 nonempty `(frequency, sector)` groups; no odd/even symmetry was assumed.
- All oracle fields are finite and all `6,320/6,320` validations pass. Independently recomputed maxima are:
  - `abs(A_in-1) = 0.0`;
  - effective and outer-boundary residual `8.751294801378416e-16`;
  - normalization residual `5.661048867003676e-16`;
  - log-derivative residual `4.201338430629957e-16`;
  - match condition number `4.014261744966441`;
  - relative sensitivity `1.7849602030606062e-07 < 5e-6`.
- Producer anchor selection independently reconstructs to 300 records with all 82 groups represented, including explicit zero-anchor groups; every sensitivity record passes.
- Literal AST expansion, performed without importing the helper, reconstructs 82 group segments and exactly the same 6,320 transition keys across both sectors, all eight point IDs, tokens, ell ranges, and boundaries. The envelope contains no runtime IO, interpolation, inferred membership, or unstated frequency.
- Resume preflight independently passes `6,320/6,320`, with zero failures and zero relative `psi`, `dpsi_dr`, and `A_out` differences.
- Focused tests prove a default-covered mode makes zero oracle calls and all wrong M/k/token/radius/point/ell/sector/boundary/tolerance cases fail closed with structured reasons.
- A fresh independent integrated-adapter matrix selected the lexicographic median key in all 44 nonempty groups and added missing point coverage, producing 46 unique anchors covering all eight point IDs. Every returned solver/warning/point label is exact, and maximum relative difference against direct saved `A_in`, `A_out`, `psi`, and `dpsi_dr` is `0.0` for each field.

## Implementation scope and verification

- Exact implementation commit `6e86d8b419d8c09af38e226400f7439f7cdfed79` has parent exactly the reviewed candidate and changes only the five frozen paths:
  `scripts/phase5_literal_failed_child_radial_gate.py`,
  `src/schwgw/numerics/q018_tablei_literal_failed_child_envelope.py`,
  `src/schwgw/numerics/radial_solver.py`,
  `tests/physics/test_q018_production_integration_design.py`, and
  `tests/physics/test_radial_solver.py`.
- Commit blob/SHA-256 identities respectively:
  - runner `693b764bb13f0fb0c74d0a8eddc2b930bbf48365` / `59393981640f491ab8830898eefa455e1111cc57b07aab2f9b79ea72454543bb`;
  - envelope `0ee1f3dbc829bd6e4debf0f0de4db90501919204` / `0eee55a569c3e65632e417a107d906e4881b702393a3ed69dd4c6ef9484015e0`;
  - radial solver `c1237739e0002024c802272564167cc590d37f7f` / `d818aff2aeaa38946a4212102cef984e92c265e7c1432d1eee88acc535c896b4`;
  - integration test `14cbdd496ef55af300bf5ce5a4c79c71501236c1` / `9be7f0fc0158ae964e4df5355b364753bcc9f62df40cc5c0c33aef06469a28f4`;
  - radial test `5ab4ed9620de8aeef2bfce725cf8740a10c43924` / `20816ea56b8ff71a98301b28fcc67b3408e77dba9686dcd446bb20ecb66df4de`.
- Focused pytest: `4 passed, 352 deselected, 7 subtests passed in 1.30s`.
- Ruff on the exact five paths: `All checks passed!`.
- Fresh full pytest: `659 passed, 117 skipped, 1 xfailed, 103 warnings, 97 subtests passed in 325.95s`.
- Warnings are the existing Weyl/Wigner floating-point diagnostics and intentional SciPy radial fail-closed-path diagnostics; no new failure occurred.
- `git diff --check` is clean. Exact-five commit scope and committed/worktree file identities pass. T8ar implementation/artifact, recursive/uniform/full-grid, amplification, production, plot, fixture, Kirchhoff, paper-style, and gate-local binary/visual/temp/quarantine searches are empty.

## Stop boundary

T7cc modified only `status.md`, `docs/handoffs/T7_current.md`, and its byte-identical predecessor archive. It did not repair T4ac, alter any implementation/test/script/config/artifact/source, create or replace a task, dispatch T8ar/T7cd, relax any threshold, or perform GitHub action.
