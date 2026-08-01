# T4 Current Handoff

Last updated: 2026-07-20
Thread: T4ac, literal failed-child radial/Q018 gate.

## Exact decision

```text
GREEN / LITERAL FAILED-CHILD RADIAL GATE READY
```

## Frozen evidence

- Exact 41-frequency literal failed-child radial-only contract, both sectors,
  eight Table-I points, every `ell=2..ell_max`, maximum lmax 360, and
  unchanged `M=1`, `r_out=300`, `r_in_eps=1e-6`, `rtol=1e-10`, `atol=1e-12`.
- Classification: 146,416 unique records; 140,096 default-covered; 6,270
  structured uncovered; 50 structured solver-failed; zero default-other.
- Measured transitions: 6,320. Direct oracle: 6,320/6,320 validated; maximum
  effective residual `8.751294801378416e-16`; maximum relative sensitivity
  `1.7849602030606062e-07`; 300 sensitivity anchors passed.
- All 41 checkpoints are `complete=true`, `decision=PASS`, exact contract and
  output-hash matches. The ordered checkpoint hashes are recorded in
  `runs/phase5/fig5_fig6_literal_failed_child_radial_gate/manifest.md` and
  `docs/phase5_literal_failed_child_radial_gate.md`.
- Integrated adapter preflight: 6,320/6,320 passed, zero failures; maximum
  effective/boundary residual `8.751294801378416e-16`, maximum match condition
  number `4.014261744966441`, and zero relative differences in `psi`,
  `dpsi_dr`, and `A_out` against saved direct-oracle values.
- Default-covered modes make zero oracle calls; every physical, frequency,
  sector, mode, point, boundary, and tolerance mismatch fails closed.

## Provenance and artifacts

- Frozen candidate: `f3a64522642abfaa2e0f3933125df06ae76895e4`, parent
  `fa22f20f775c1b15ae533c03047d156687e5f3bf`.
- Exact five-path implementation commit:
  `6e86d8b419d8c09af38e226400f7439f7cdfed79`, parent exactly the candidate.
- Classification snapshot:
  `e675b751fd4beae2446597034b99f847e0cc3528551bfc30f8efd3460ad944fe`.
- Final-adapter snapshot:
  `8188b306fea0190654f752190f0ab6e96ef6970b16fea704b9cdb99ca96c7ccc`.
- Root SHA-256: classification
  `e5c934568ff1a9f80838df3fc674fea153e4c638777e6d7c9c2c2d32d0024e5b`;
  oracle `b4954a152aa81853fe53931bcb9ee9820b6d6da6d923019288f276d0519c52c6`;
  preflight `08b5542a26c0b95f6bf10005aeb21681f75735f53b924f894f1c133081ee2873`;
  manifest `6b55500aae750f7b2400627825220f18e2ca9f608a4c977707e4f2ec363e78c8`.
- Pre-T4ac handoff was archived byte-identically at
  `docs/handoffs/archive/T4_2026-07-18_pre_t4ac_literal_failed_child_radial_gate.md`,
  SHA-256 `ef08a825a060fb317aaf6743bd54dda221a9ad23f58ecfdcc27028ef5cab66dd`.

## Verification

- Fresh classification/oracle audit: `PASS records=146416 transitions=6320
  checkpoints=41`.
- Focused pytest: 4 passed, 352 deselected, 7 subtests passed.
- Ruff on the exact five implementation paths: passed.
- Fresh full pytest: 659 passed, 117 skipped, 1 xfailed, 103 warnings, 97
  subtests passed in 317.17 s.
- Exact-five-path commit scope, committed/worktree blob identity,
  `git diff --check`, checkpoint/root cardinality, and forbidden-output searches
  all passed.

## Scope and next handoff

No lmax extension, automatic/recursive midpoint, uniform/full grid,
amplification, production, plot, fixture, Kirchhoff, paper-style output,
replacement task, T7cc/T8ar/T7cd dispatch, or GitHub action occurred. T4ac
returns only to T0. Any T7cc dispatch remains a separate T0 action.
