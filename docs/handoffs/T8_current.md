# T8 Current Handoff

Last updated: 2026-07-15

## Thread Role And Current Status

T8ao completed the frozen metadata-only repair of the accepted T8an
Delta(kM)=0.1 nine-frequency risk-pilot package. The v1 scientific generation
contract and every non-metadata NumPy array are unchanged; the active package
now has an explicit v2 units/ordering metadata contract.

Exact decision:

```text
GREEN / DELTA0P1 RISK-PILOT UNITS METADATA HARDENED
```

The predecessor T8an handoff is archived byte-for-byte at
`docs/handoffs/archive/T8_2026-07-15_pre_t8ao_units_metadata_repair.md`.

## Completed Work

- Commit `689c075` implements the repair in exactly four frozen paths:
  `src/schwgw/io/tablei_risk_pilot.py`,
  `scripts/phase5_repair_delta0p1_risk_pilot_metadata.py`,
  `tests/unit/test_tablei_risk_pilot.py`, and
  `tests/regression/test_delta0p1_risk_pilot_metadata_repair.py`.
- The original 23-file active package is preserved byte-for-byte under
  `runs/phase5/fig5_fig6_delta0p1_risk_pilot/quarantine/t8ao_pre_units_metadata/source/`.
- The complete repaired candidate is retained under the sibling `candidate/`
  directory. The resumable repair ledger is
  `runs/phase5/fig5_fig6_delta0p1_risk_pilot/quarantine/t8ao_pre_units_metadata/repair_ledger.json`.
- The active package was replaced by the metadata-only migration. No T8an
  scientific runner, solver, polarization, radial/cache path, or sampling
  metric computation was invoked.
- The v1 generation contract remains
  `92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9`.
  The independently reconstructed v2 metadata contract is
  `1bd32a3e2988ef786c3777859f76f8d38a276cdacd12cdadba7f79e843ca0161`.
  The repair ledger SHA256 is
  `ec4c6784a26e53b583c032fe360f51b940f5dfe6d58e705b2c3412fbeb9c717c`.

## Active Artifact Hashes

The active package has exactly 23 physical files and the manifest has exactly
22 non-self records:

```text
8729ad80043a1837793264b101a776a08e92191c7856cf792ed34683b743859e  checkpoint_ledger.json
92720f77a8a365f7555d78f6d8e5522f430714945e1878502055a6485f323be0  frequencies/kM_0p4.npz
eecf83f4239056c2b551879d0fc2e38f7e3aa6169968ea0b5225e3fa1801401e  frequencies/kM_0p4.npz.json
5fa3ff156f46978ca608ded88b564497b516d7ec0a01bd5997606fbe6d80ac2a  frequencies/kM_0p8.npz
3a69774878744935831385e23b3309ed3b3feb6f70a8a13b884ac36eaf88853a  frequencies/kM_0p8.npz.json
9b86413b41a3bbe23a8ceb4541dba10e19d512a7cb8bd9d53ab3794c187cd432  frequencies/kM_0p9.npz
e2ebb9c66fcd8dc9737a2d4056dad92ed5ad73f2a2519307453c8f99fea1fade  frequencies/kM_0p9.npz.json
1d08bbdf9d3ff80eeb5e0b8df6eae440dddee7f8babe16c85eb27ad6290dba0e  frequencies/kM_1p6.npz
05cbddcd46c3c1a5161eeab58e72ee8144ac695f8857ce3914e208704d8f0584  frequencies/kM_1p6.npz.json
09e4266161f4b92efd59000ba3757f8f4b2737a81aace2ac69c1a01529d7cd3d  frequencies/kM_1p7.npz
71ba72c7511dcb1b089049ea417821b317910ac487fe3106f0018ae7f7d4449e  frequencies/kM_1p7.npz.json
47a10fc3dec2861c740ee772e509039b97c9a510bd7591ef9315b17583125283  frequencies/kM_2p8.npz
8f82b2c2ce08f50d21ff8a043b1ff2b10dcc842fecf164db039267dc50dc9c24  frequencies/kM_2p8.npz.json
97d4d774280b590d75dea913963cd7246c376ec1cc491dced9c746db4d9c56fa  frequencies/kM_2p9.npz
8ba2f48c8c3ec0291b336e12e9baf38f5109eaa578f60f32b52f4a7bd900c839  frequencies/kM_2p9.npz.json
60bf10b67772c2d8197f7db5f372252cf3bdf90a8837e02567fd7c7a5a6ca081  frequencies/kM_3p8.npz
9c108ccf5fe0eb77cf8cce989b48e44c87c78f16c226caa61fc504f86bf23a3a  frequencies/kM_3p8.npz.json
ed7fe65781baedc5f75885d56bd41fed321ac0d3581ea50f46a7f68f260ae44e  frequencies/kM_3p9.npz
373fbada222620d2f1917a5309d23702af3b83541c04e18dc740ea5c505dda98  frequencies/kM_3p9.npz.json
27301b9f300563a5feb654b48d9ef11ca8eb1e10f9c065c805534adfb27bfd78  manifest.md
7e1e8646bfa51b09cd96ee301e8847fdc830128d7eca7ac770031bc7b13ce42b  risk_pilot_sampling_audit.json
69cf9812ddd51d6486f854b77b76d202c281d719041cc07e8e87c1af9bd973f7  risk_pilot_values.npz
b812a4325b9afca91ee360b68dc3e959115f2d992fba21b60cf70a7ad3ce3566  risk_pilot_values.npz.json
```

## Verification

- Independent no-helper numerical audit:
  `T8AO_NUMERICAL_ARRAY_IDENTITY=PASS`. All 10 NPZ source/active pairs and
  all 219 arrays have identical key order/set, shape, dtype,
  `np.testing.assert_array_equal`, and canonical `.npy` SHA256.
- Independent no-helper metadata/provenance audit:
  `T8AO_METADATA_SURFACES_AND_PROVENANCE=PASS`. It reconstructed the metadata
  contract, checked all units/ordering surfaces, legacy provenance, 23/22
  cardinality, source/candidate/active hashes, and unchanged sampling
  sequences.
- Focused pytest: `18 passed in 1.84s` (final closeout rerun).
- Ruff: `All checks passed!`.
- Mandatory full pytest: `624 passed, 117 skipped, 1 xfailed, 101 warnings,
  81 subtests passed in 311.91s`.
- Scientific runner guard: `T8AO_SCIENTIFIC_RUNNER_GUARD=PASS`.
- The six accepted T8aj/T4z/T7bv source/gate hashes freshly match. The commit
  path set is exactly the frozen four paths. Forbidden implementation/config,
  fixture, production, refinement, plot, Kirchhoff, and paper-style searches
  are empty. No GitHub push occurred.

## Incomplete Work

- T7bx must independently review the repaired artifact contract from the
  durable pre-repair backup and active package. T8ao does not independently
  accept its own repair.
- The prior scientific result remains non-accepted: all 224 phase steps were
  finite with maximum `1.4363184904108022`, but there were 38 exact
  magnitude-dominance failures and 51 strict interior extrema. T7bx owns only
  the artifact-contract review; no sampling refinement or production decision
  is authorized.
- Full 40/79-frequency production, 0.05/0.025 refinement, plots, fixtures,
  Kirchhoff, and paper-style work remain unstarted and separately gated.

## Blocking Issues And Non-Blocking Warnings

- No T8ao blocker remains.
- The repair changes only schema/metadata/provenance surfaces and NPZ archive
  container bytes. Scientific arrays are exactly unchanged as established by
  the independent canonical-array audit.
- Existing quarantine trees are intentional provenance and are excluded from
  the active 23-file package and manifest.

## Must-Read Files For The Next Thread

1. `docs/prompts/phase5_t7bx_delta0p1_units_metadata_repair_review.md`
2. `docs/prompts/phase5_t8ao_delta0p1_units_metadata_repair.md`
3. `docs/superpowers/specs/2026-07-15-t8ao-t7bx-delta0p1-units-metadata-repair-design.md`
4. `docs/superpowers/plans/2026-07-15-t8ao-delta0p1-units-metadata-repair.md`
5. `runs/phase5/fig5_fig6_delta0p1_risk_pilot/manifest.md`
6. `runs/phase5/fig5_fig6_delta0p1_risk_pilot/quarantine/t8ao_pre_units_metadata/repair_ledger.json`
7. `status.md` under the 2026-07-15 T8ao entry.

## Frozen Decisions

- The v1 generation contract, frequencies, Table-I points, lmax windows,
  amplitudes, boundary values, adapter policy, tolerance, source/gate hashes,
  saved arrays, and sampling sequences are immutable.
- The v2 metadata schema is
  `phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering`; units and ordering must
  be explicit and hash-bound independently of the generation contract.
- Source, candidate, active, ledger, and manifest cardinality/provenance rules
  are frozen by the approved design and plan.

## Forbidden Actions

- Do not invoke the T8an scientific runner, solver, polarization, radial/cache,
  or sampling-metric computation.
- Do not change physics, thresholds, lmax, Q018/boundary policy, accepted T8aj
  products, T4z/T7bv gate products, or any non-metadata array.
- Do not start 0.05/0.025 refinement, full-grid production, plots/PDF/PNG,
  fixtures, Kirchhoff, paper-style work, or GitHub push.
- T7bx must not call the T8ao migration helper or repair artifacts.

## Superseded Prompts

- `docs/prompts/phase5_t8ao_delta0p1_units_metadata_repair.md` is complete and
  must not be rerun.
- The T8an scientific runner prompt remains historical and must not be used to
  regenerate or reinterpret this package.

## Exact Next Task

Dispatch T7bx in the existing T7 task with `gpt-5.6-sol/high`:

```text
你现在是 T7bx：Delta(kM)=0.1 risk-pilot units/ordering metadata repair 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bx_delta0p1_units_metadata_repair_review.md。请从 durable pre-repair backup 与 active artifacts 直接重建 array fingerprints 和 metadata contract，独立核验全部 units/ordering surfaces、23/22 cardinality、legacy provenance、tests 与 scope。不得调用 T8ao migration helper，不得修复 artifact，不得启动 0.05/0.025/full-grid/plot/paper work。
```

## Allowed/Forbidden Files And Definition Of Done

- T7bx is read-only except for its own T7 coordination records explicitly
  authorized by its prompt. T8ao artifacts and implementation are frozen.
- Required verification is direct reconstruction from source backup and active
  artifacts, independent array fingerprints and metadata hash, all
  units/ordering/provenance/cardinality checks, focused and full tests, scope
  checks, and forbidden-output searches.
- T8ao is done because the durable source/candidate/ledger, active 23-file
  package, exact non-metadata array identity, v2 metadata contract, fresh
  tests, scope checks, archive, this handoff, and `status.md` are complete with
  the exact GREEN decision.
