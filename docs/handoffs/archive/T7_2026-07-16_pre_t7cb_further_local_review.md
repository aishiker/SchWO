# T7 Current Handoff

Last updated: 2026-07-17

Thread: T7ca, further-local radial/Q018 gate independent review.

## Exact Decision

```text
ACCEPT GREEN / FURTHER LOCAL RADIAL GATE ACCEPTED
```

This GREEN authorizes only T0 to perform its frozen fresh verification and, if
still exact, dispatch the separately frozen T8aq package. T7ca did not dispatch
T8aq and did not authorize another frequency, recursive midpoint, full or
uniform production, plot, fixture, Kirchhoff, paper work, or GitHub action.

The exact pre-T7ca T7bz handoff bytes are archived at:

```text
docs/handoffs/archive/T7_2026-07-16_pre_t7ca_further_local_radial_review.md
```

Archive SHA-256:
`8edd808e543460f943eb217af248b2edd52d7ea7d1827e99315b4f49f6521d9e`.

## Independent Nine-Check Result

1. **PASS — start gate, commit, and scope.** T4ab reported exactly
   `GREEN / FURTHER LOCAL RADIAL GATE READY`. Implementation commit
   `c3a6479703f6c2d64aa2903edc7cf2db3d1ed112`, parent
   `76b57c90d6e54594ca480e1dcf629af685d9098f`, changes exactly the frozen
   gate script, literal envelope, radial solver, and two physics-test paths.
   No IO, scattering, observable, config, fixture, accepted source, or
   unrelated implementation path is present.
2. **PASS — contract and cardinality.** Independent evaluation of
   `sum_k (ell_max(k)-1) * 2 sectors * 8 points` gives exactly 81,792.
   Direct raw-record reconstruction finds 81,792 unique keys equal to the
   complete expected Cartesian key set. Counts are 78,574 default-covered,
   3,178 structured uncovered, 40 structured solver-failed, and zero
   default-other. All 24 checkpoint files are `complete=true`,
   `decision=PASS`; their per-frequency contracts, canonical contract/output
   hashes, classification snapshot, file hashes, and record unions are exact.
3. **PASS — fresh default classification.** A fresh deterministic 50-mode
   sample covers all 24 frequencies, both sectors, all eight exact point IDs,
   default-covered, structured uncovered, and structured solver-failed.
   Every result reproduces the raw classification; there is no omission or
   mismatch.
4. **PASS — direct oracle.** Raw transitions, oracle validation, and resume
   preflight contain the same 3,218 unique
   `(kM,sector,ell,point_id)` keys without odd/even inference. All stored
   complex fields are finite and all validation flags pass. Independently
   recomputed maxima are effective/outer residual
   `7.116571212464012e-16`, normalization residual
   `5.900916318210353e-16`, log-derivative residual
   `4.3478013790170573e-16`, condition number
   `4.001677852348993`, `abs(A_in-1)=0`, and stored sensitivity
   `1.7593903638313873e-7 < 5e-6`. Producer reconstruction gives exactly
   172 first/last/point-coverage anchors and explicitly preserves 24 empty
   groups. A fresh 26-key complementary matrix uses the lexicographic median
   of every nonempty group plus the last transition for globally uncovered
   exact point IDs. Fresh dps65/80/95 and loose/tight variants have zero
   failures, maximum relative difference from saved dps80 equal to zero,
   maximum sensitivity `3.853799963899222e-8`, and maximum effective
   residual `4.742874840267547e-16`. Requested precision is recorded
   separately from the honest SciPy double-precision actual dps53 backend.
5. **PASS — literal envelope.** Independent AST literal expansion, without
   importing the producer helper, yields exactly 3,218 keys and equals the raw
   transition set. It contains exactly 24 frequencies, 48 sector-aware group
   entries, eight exact point/radius pairs, exact token mapping, no extra
   frequency, and no interpolation, inferred membership, or import-time run
   file loading.
6. **PASS — adapter behavior.** The fresh 26-key integrated-adapter matrix
   reproduces saved `psi`, `dpsi_dr`, and `A_out` exactly, with the exact
   solver and warning labels. A default-covered opt-in mode makes zero direct
   oracle calls. Wrong M, k outside the frozen `atol=1e-15` comparison,
   radius, point membership, ell, r_out, r_in_eps, rtol, and atol fail closed
   with exact reasons. Invalid sector text fails at the public boundary with
   `ValueError: sector must be 'odd' or 'even'`; both valid sectors are
   independently represented in the literal map.
7. **PASS — double-layer provenance.** Classification snapshot
   `52889944b58ec8aae442afb7c743679fcbbd9d3dd21819cc61cf1364b683eb43`
   independently reconstructs from the final gate script, parent-commit
   pre-adapter radial blob, direct oracle, Table-I source, complete frozen
   package, immutable sources, and input contract. The only live-source
   difference is the intentionally later final radial blob; the exact parent
   blob hash is
   `70f6bbed3266fdcf229af80b73a51416b8be056acf3d8ecbd73f4c86e73c997e`.
   Final-adapter snapshot
   `ba6e63d87c7cc2cad4a64300a775bc07059d7a21760dbd431e411f6508febcb3`
   independently reconstructs from the exact commit and all five live
   commit/blob hashes and links back to the classification snapshot. All 25
   frozen path/hash inputs match. Checkpoints compare only to the
   classification snapshot. The 28-file gate directory has exactly 24
   checkpoints plus four roots, no temp/quarantine, and the manifest binds
   every hash. Resume preflight passes 3,218/3,218 with zero relative
   `psi/dpsi_dr/A_out` difference and zero failures.
8. **PASS — tests and quality.** Fresh focused pytest:
   `352 passed, 67 warnings, 27 subtests passed in 301.63s`. Ruff on the
   exact five paths: all checks passed. Fresh full pytest:
   `643 passed, 117 skipped, 1 xfailed, 103 warnings, 90 subtests passed in
   315.95s`. Warnings are existing Weyl/Wigner numerical diagnostics and
   deliberately exercised SciPy radial fail-closed paths; no new failure or
   warning class occurred.
9. **PASS — isolation.** Required searches for T8aq further-local refinement,
   dense production, uniform 0.025/0.0125 scans, paper candidates, and radial
   gate PNG/PDF/SVG/NPZ products are empty. Five-path worktree diff and
   `git diff --check` are empty. T7ca changed no implementation, test,
   script, config, artifact, accepted source, or T0/T4/T8 handoff.

## Frozen Package SHA-256

```text
88fa71a39606b9b37ea202a0e16d25af7a2e4597bce0c697df02c57a666c365b  design
7812fe2062cd04d494c1ed427c2bf37bb036c8864ab4f0330b96ceb928c5ce0a  T4ab plan
56891ef34f168a05e43806d7177ca721c10180483224c75ef95df5a1e118b56b  T8aq plan
2e6dbb5508d800442b0cfec9e89c5de4daacfe34abbd475963fabeae24727e3e  T4ab prompt
132e6ec9cca4d91fbcef38d1354ee0e9028f2d30de73e308b8acb1ed1571cb85  T7ca prompt
ad34bc2338fadcc51685b499910ff13a4ecda5f7567af186f0d39bc99f33f354  T8aq prompt
99f03928c2b3e51d2cd30614d6401fb4da81375a99fa08bf330fdb2d4459e10b  T7cb prompt
```

## Gate And Implementation SHA-256

```text
3bfe7d84a463e332d77724f58189fe3f565d9a385a4431f5a92ea58f15d11696  classification_manifest.json
82ebed2447f7566a391ea1915c88ee3bf55f0c86b8c0207e2bd1eb2ca075d0c0  oracle_validation.json
8fdabdbd1bc4765d1ee5155824df1ba88b154c58e14058d68129d58ec36a1021  resume_preflight.json
ef479476d683366654c3c2209aba817fa8ca35a68bbf86782a39e88ce9a60bc0  manifest.md
b1efa83f5b6686c2c9d7e14264e5147f1710e2c2f5a0c7b218f01b60a6260e2c  gate script
6363c5674e6ab2f4eeec1d505d93e8ca1bb531e7e44a7342bd3ba3609a864b17  literal envelope
a16040f29bc1a80a0257aa59d3710882857da0b846781809184f1bddb98becc7  final radial solver
071df34c1cb71754420203f2d68d3121f5a9e7b27237b47395f82801b8bdb3b1  integration-design test
52f09add92e99b5c069b3463ab2ec30fcab65b1a03fbb49f445fd854e054751e  radial-solver test
```

## Checkpoints

- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_0p325.json`: `9d947e03ce5af77a3b9a4b235c035e69f7f2ba08db2e7acef5b3f2c4bf82ba1d`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_0p375.json`: `c92d3db8d8ad069fc2ef208ffc80899b412c6fd4384fdfca707491f5fe71a629`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_0p825.json`: `ca95c45ba7fd1df269b20f63fab3727e1b991992fa4c7144fbceda1bfdbef622`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_0p875.json`: `093458b767bd6356107ed97d485293506a084042da944935302eecf42af9cac9`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_0p925.json`: `1d1f04c2e93fa27efc601428c58b31b64406e3e2d29abdb2fb02423e0cfd5519`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_0p975.json`: `4ede8686cf95bbff0c9e888a99ff57d24f3c2f5402be7c47deec0d70dffe7384`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_1p525.json`: `21b7020735333af365c46a7922f870ca150a0f315647b611703498b0e190a509`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_1p575.json`: `d9956be4dcb2fe9c5c578523229fcd08ff498a4a24fcff4fa089767aaa5f90c4`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_1p625.json`: `d886d664b11562e54d66e1ebbcd9737ce8dc3837b9c9a93c25755b2d19b9cffb`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_1p675.json`: `9ab986304fe6f6d52b5ad9e3054f3ca0e5a75aecb606a545403f1e60b21fc84d`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_1p7125.json`: `d686522ba2477cc742048288ec138ed3a89393690dd8885657d93f68461fafee`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_1p7375.json`: `c03aec9bf296899e17f017649c07387348d02cddc9ebaef6a7dcff9b775ed6fe`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_2p7625.json`: `6e06431ac2228c0eb59fa8aee03ca7ee32a28e57f9a4ec383d4443b9d13d9d25`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_2p7875.json`: `ce9a60e726ea66671af9923017b53946f4bf91b1bb4005d9331dc0cdfb95b1ad`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_2p825.json`: `7ee7e30f04f029ca38e3d18b1abf3049173d9ea96e4692a6beb4581d78cea9f0`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_2p875.json`: `930ae25179a8e7034a9ee6260c0e036dd5a5552c5d0569d8f5772dcd31cee546`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_2p925.json`: `adbf8b0bdb2b50112ee44b846d606d038f6137995f9f56f043a9f474c3e296ea`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_2p975.json`: `2a0bf78b418de174b776163066f8fc3ab0dfc98931091d6bb07df59ee9887537`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_3p7625.json`: `a5ba2c57aea4cee425393c76787e7c51fdb654ed7a1d25b7d619276373167146`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_3p7875.json`: `ce4668ce1270e7033c3106251fb7377a654d0d12da15bbdfe5e75582ef878241`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_3p825.json`: `9f9c2afd1d27766acbda5b628db42dfe213612f08ed96561cba697233253d5c0`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_3p875.json`: `b7aa29de6366f3377eb598d8b3175210865da8b788330a6a59b08a05d9bdde5e`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_3p925.json`: `10aaf838ed18cef1cfb39006cee3f2d92a68f2e3a8582c6499d750af411cdb76`
- `runs/phase5/fig5_fig6_further_local_radial_gate/checkpoint/kM_3p975.json`: `8c1457a1e1f2d9c0cce0b9fa7ff43988ed12c6d6875ac5eb34e6c825d3b22296`

Radial-only evidence. No T8aq, observable, plot, fixture, Kirchhoff,
paper artifact, lmax extension, full-grid/uniform scan, or recursive
midpoint was produced.

## Review-Only Changed Paths

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-16_pre_t7ca_further_local_radial_review.md`

The exact GREEN, reviewed hashes, independent counts/maxima, fresh tests,
scope evidence, and non-claims were successfully sent to T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636`.
