# T7 Current Handoff

Last updated: 2026-07-15

Thread: T7bx, `Delta(kM)=0.1` risk-pilot units/ordering metadata-repair
independent review.

## Exact Decision

```text
ACCEPT GREEN / DELTA0P1 RISK-PILOT ARTIFACT CONTRACT REPAIRED
```

The repaired package passes all nine frozen review checks. This GREEN accepts
only the v2 artifact contract and preserves the independent scientific state:

```text
YELLOW / TARGETED ADAPTIVE FREQUENCY REFINEMENT REQUIRED
```

No new frequency, refinement, production, plot, fixture, Kirchhoff, or paper
work is authorized. T7bx did not call the T8ao migration helper and did not
modify any implementation or artifact.

The pre-T7bx T7bw handoff is archived at:

```text
docs/handoffs/archive/T7_2026-07-15_pre_t7bx_units_metadata_repair.md
```

## Independent Nine-Check Result

1. **PASS — implementation scope.** Commit `689c075` changes exactly the four
   frozen paths: the risk-pilot module, thin metadata-repair CLI, unit test,
   and metadata-repair regression test. No solver, adapter, scientific runner,
   IO export, config, fixture, visualization, or unrelated path is included.
2. **PASS — frozen sources.** The durable source backup contains exactly the
   original 23 active files. Its five frozen root hashes and all 22 old
   manifest entries match; the generation contract remains
   `92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9`.
   All six accepted T8aj/T4z anchors match freshly hashed files and every
   declared source surface.
3. **PASS — direct numerical identity.** A standalone audit that imports no
   T8ao helper directly loaded all ten source-backup/active NPZ pairs. All 219
   non-`metadata_json` arrays have identical key order/set, shape, dtype,
   `np.array_equal` values, and SHA-256 of
   `np.save(BytesIO(), array, allow_pickle=False)` bytes. The candidate tree
   has the same 219 fingerprints.
4. **PASS — metadata contract reconstruction.** T7bx independently rebuilt
   the exact three-part units registry, ordering registry, complete sorted
   219-entry fingerprint map, and canonical compact-JSON payload. The result
   is exactly
   `1bd32a3e2988ef786c3777859f76f8d38a276cdacd12cdadba7f79e843ca0161`
   on every declared surface.
5. **PASS — required surfaces.** All nine per-frequency embedded objects,
   nine sidecars, aggregate embedded/sidecar, checkpoint ledger, sampling
   audit, and manifest carry the exact v2 schema, generation/metadata hash
   split, repair identity, source anchors, pre-repair provenance, units, and
   ordering. Aggregate nested frequency metadata exactly equals the repaired
   sidecars, including their active NPZ hashes.
6. **PASS — coverage and actual arrays.** Units keys cover all and only the 22
   per-frequency and 21 aggregate non-metadata arrays. Actual frequency,
   point, frequency-local `lmax`, history/final/aggregate axes, coordinate
   geometry, and ordering match the frozen registries. Coordinates/radii are
   expressed in `M`, angles/phases in radians, complex amplification and
   deltas are dimensionless, and masks are Boolean.
7. **PASS — journal/cardinality/provenance.** Source, candidate, and active
   trees each contain exactly 23 package files; each manifest has 22 non-self
   records. The repair ledger is `state=complete`, has exact source/candidate
   hash maps, 23 copied and 23 replaced paths, 219 fingerprints, and no
   ambiguous or third-state file. No `.tmp` exists. The 11-file historical
   runner-cache quarantine remains excluded from active data and provenance.
8. **PASS — legacy/scientific preservation.** Every legacy metadata value is
   unchanged outside the frozen mutation allowlist. Source and repaired
   sampling sequences are JSON-semantically identical. Fresh reconstruction
   confirms all masks true, final-pair maxima
   `6.136118112992297e-11` plus and `5.492389935680416e-10` cross, 224 finite
   phase steps with maximum `1.4363184904108022 < pi/2`, exactly 38 frozen
   magnitude-dominance failures, and exactly 51 strict interior extrema.
9. **PASS — tests and isolation.** Focused pytest, Ruff, full pytest, source-
   hash, commit-scope, forbidden implementation/config/fixture diff, active
   temporary-file check, and forbidden downstream-output check all pass.

## Independently Reconstructed Contracts

```text
generation_contract_hash = 92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9
metadata_contract_hash   = 1bd32a3e2988ef786c3777859f76f8d38a276cdacd12cdadba7f79e843ca0161
schema_version           = phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering
metadata_repair_id       = T8ao/T7bx-units-ordering
array_pairs              = 10
non_metadata_arrays      = 219
canonical_fingerprints   = 219
```

Frozen ordering verified against actual arrays:

```text
frequency_order = [0.4,0.8,0.9,1.6,1.7,2.8,2.9,3.8,3.9]
point_order = [
  near_axis_x0_z30, near_axis_x1_z30,
  near_axis_x2_z30, near_axis_x3_z30,
  far_axis_x10_z30, far_axis_x15_z30,
  far_axis_x20_z30, far_axis_x25_z30
]
per_frequency_history_axes = [lmax, point]
per_frequency_final_axes = [point]
aggregate_field_axes = [frequency, point]
```

## Durable Pre-Repair Identity

```text
79d4c0f596650dcfb4d63c7e40758ea4afa82d2fe0e0cd3de5aa088bbbfd5ccd  checkpoint_ledger.json
2e0a9fee1b6729466affd4c5f7f6e86c96e696e20882c9f4ad52ae3792d82957  risk_pilot_values.npz
2a9aa472e64747047cb28de90912eecf138b28884d87e8b8219e78d99482772f  risk_pilot_values.npz.json
461d040a180dfa8e5a743967285e67f8b682f8f67607f1c0c7a5c8ab2399d7bd  risk_pilot_sampling_audit.json
120ccd8f11e681bc6d2b3054bd7522ef331a282421f7661dd7888c993b052212  manifest.md
```

## Active Artifact SHA-256

The independently verified active package has exactly these 23 files; the
manifest contains the corresponding 22 non-self records:

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

Repair-ledger SHA-256:

```text
ec4c6784a26e53b583c032fe360f51b940f5dfe6d58e705b2c3412fbeb9c717c
```

## Fresh Verification

- Focused pytest: `18 passed in 2.11s`.
- Ruff: `All checks passed!`.
- Full pytest: `624 passed, 117 skipped, 1 xfailed, 101 warnings, 81 subtests
  passed in 326.73s`.
- Full-suite warnings are the existing Weyl/Wigner and deliberately exercised
  SciPy fail-closed warnings; no T8ao metadata path failed.
- Forbidden implementation/config/fixture diff: empty.
- Forbidden downstream-output command: empty.
- Active `.tmp` search: empty.

## Review-Only Changed Paths And Boundary

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-15_pre_t7bx_units_metadata_repair.md`

T7bx changed no implementation, test, script, config, artifact, accepted
input, or T0/T4/T8 handoff. It did not run the migration helper, scientific
runner, `0.05`, `0.025`, full grid, plot, fixture, Kirchhoff, or paper-style
work. Only T0 may close the gate, apply the project major-node GitHub rule, or
design a later adaptive-frequency stage. The exact GREEN and retained
scientific YELLOW were successfully sent to T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636` after fresh verification.
