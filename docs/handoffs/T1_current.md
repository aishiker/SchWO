# T1 Current Handoff

Last updated: 2026-08-11T11:27:39Z

Thread role: formal T1 primary-literature and physics-convention owner.

Task identity: `019f5fb7-9d0a-78b0-af5e-25a663dd153b`

Scientific stage: `Phase 6 / V3.0`

Artifact revision: `r1`

## 1. Current state

T1 completed the bounded, zero-science V3.0 primary-literature, formula,
phase, domain, anchor, and threshold freeze specified by
`docs/prompts/phase6_t1_v3_0_literature_formula_freeze.md`.

Terminal T1 state:

`CHECKPOINT / V3.0 ANALYTIC-LITERATURE BENCHMARK CONTRACT FROZEN`

This is a T1 candidate checkpoint, not an accepted gate. Root T0 must dispatch
the already frozen formal T7 read-only contract review. T1 did not contact T7
or authorize V3.1/V3.2/V3.3/V3.4.

No radial solver, partial-wave sum, V3 producer, absorption/glory numerical
scan, benchmark, Li figure, or full test suite was run.

## 2. Frozen input verification

Start identities matched and the same identities must match again at handoff
verification:

- V3 master prompt:
  `f8c48d9379efcc2534748e33b62a302ba7bd6fe11282b4b4ad6e7a9ae850b1c7`
- T1 V3.0 prompt:
  `03a352b881c97f1f767092340d5dc65f61e800dafde9c28b9f870eaa5ad454cc`
- V2-to-V3 transition:
  `4493c1359974bf58abcc4b93ebe30a6ebab5edef9bc229654c873846a95bfebb`
- dispatch addendum:
  `5a36c7fc72fcf10241a0ae0261cf220d08830c11466660c8259bfbc71b2c16db`
- V2 convention contract:
  `1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`
- V2 selected domain:
  `9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`
- current V2 release manifest:
  `51ddf1580448382be7e182f92cf76bbf53ed39f15418af9e546f357979c743eb`
- V1 radial manifest:
  `2ceb769e9f67f0a66f115aba23a82d573e400ea155741b7801cfbfcd501a4728`
- V1 production-state manifest:
  `7508ec43ba066d97acb00e8745b33ee3f422b2a8819c30874a4a03c22b8616f4`
- V1 selected-independent manifest:
  `aa66df4f449372e1af660cee8b0757d23ab494bd631bde1c229eb2ee29a2d78c`
- D-union plan:
  `de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3`

The seven protected radial source hashes are embedded in all three V3.0 JSON
configs and matched their V2 authority at start. Any end mismatch requires the
exact frozen HOLD instead of this checkpoint.

## 3. Required V3.0 outputs and SHA-256

| File | SHA-256 |
|---|---|
| `docs/phase6_v3_0_validation_contract.md` | `0f8b8c96e01321231377c857ab40d710aa80ac06dce9084029fe2914b1ef37d3` |
| `docs/phase6_v3_0_formula_map.md` | `e5b556667c28ac8b611430d2dfb4faa5da82b9c7f0c8251251029e3f8c8d0eac` |
| `docs/phase6_v3_0_phase_taxonomy.md` | `fb91f4cf888dd4984174304783875c9f2e591490df8519bafd2e0b0f73053460` |
| `docs/phase6_v3_0_literature_matrix.md` | `088834348e980b81f814340a2a2c460b5bf11239521085c358bed7a90f603328` |
| `configs/phase6_v3_0_domain.json` | `803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b` |
| `configs/phase6_v3_0_thresholds.json` | `91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a` |
| `configs/phase6_v3_0_external_anchor_matrix.json` | `06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485` |
| `references/notes/phase6_v3_absorption_scattering_conventions.md` | `82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a` |

The pre-V3.0 handoff was copied byte-for-byte to
`docs/handoffs/archive/T1_2026-08-11_pre_v3_0_freeze.md`; its SHA-256 is
`6b8013ff6b9d0002caf6d11c2ee3348aa28b865894891c2a338b3160ee05918f`.

## 4. Scientific decisions frozen

- `exp(-i omega t)`; existing V2 Schwarzschild tortoise/Jost phase retained.
- `S_l^p=(-1)^(l+1) A_out^p/A_in^p`; free reference `S=1`.
- Signed Wronskian currents are distinct from positive incident, outgoing, and
  horizon fluxes.
- `Gamma_flux=F_H/F_in` is the direct route;
  `Gamma_S=1-|S|^2` is an independent consistency route.
- Tiny positive Gamma is stored and compared in log domain; underflowed zero
  is not acceptable.
- Odd/even solves are independent. The Chandrasekhar parity relation is a
  check, not an even-sector producer.
- Total absorption uses the equal-parity-weight, gap-free sum beginning at
  `ell=2`.
- Page's spin-2 low-frequency law and the `27*pi*M^2` capture scale are the
  absorption asymptotes.
- Folacci--Ould El Hadj supplies the adopted exact `f/g`, `S-1`, and
  total/free/scattered structure.
- Yennie--Ravenhall--Wilson supplies the adopted recurrence; `q=2` is
  production and `q=1,2,3` is the ladder.
- Dolan supplies the low-frequency spin-2 cross section and the Schwarzschild
  spin-2 `J_4` glory benchmark. Exact-geodesic `b_g=5.3570M` and
  `b_g^2|db/dtheta|=4.896M^3` are mandatory; Darwin values are diagnostic.
- An ordinary total-plane-wave partial-wave sum at null infinity is forbidden.
- Published rasters are qualitative unless a separately reviewed
  digitization/author-table artifact is frozen. Li is secondary regression.

## 5. Phase taxonomy

- common retarded-time origin: `PASS`
- frequency-dependent common phase: `PARTIAL`
- ell-dependent phase: `PASS`
- odd/even relative phase: `PASS`
- total/free/scattered reference phase: `PASS`
- Coulomb/long-range phase subtraction: `PASS`
- spin-weighted-harmonic phase convention: `PASS`

The common-phase PARTIAL forbids an absolute complex `f/g` phase claim but
does not block absorption, differential intensity, relative helicity phase, or
glory features. T1 records both branch contracts as complete candidates; only
T7 may set the formal branch booleans.

## 6. Completed validation

Read-only/control validation performed:

- all three JSON files parse;
- canonical sorted-key serialization checks pass;
- required JSON metadata, nonclaims, exact upstream identities, seven
  protected file identities, and four distinct stage domains are present;
- every threshold has stable ID, observable, operator, value, units, domain,
  rationale/derivation, and blocking stage;
- anchor roles and parity-independence limitations are explicit;
- primary-source formula locators and dimensions/signs/conventions were
  manually audited;
- scoped `git diff --check`, end protected rehash, process check, and final
  hash ledger are required at the end of this handoff and must remain clean.

## 7. Incomplete work and blockers

Incomplete by design:

- independent T7 V3.0 contract review has not yet run;
- no V3 branch is authorized;
- no V3 science artifact exists.

Blocking issue for this T1 checkpoint: none, provided final rehash and scoped
checks remain clean.

Nonblocking limitations:

- frequency-dependent absolute common phase remains PARTIAL;
- Handler--Matzner/Dolan/Folacci published plots are not numerical tables;
- external/AP backends named in the anchor matrix are future fresh routes, not
  evidence already generated;
- full-domain V1/V2/V3 certification, global GREEN, Li equivalence, and
  finite-radius detector response remain explicit nonclaims.

## 8. Exact next task

Root T0, not T1, must verify the ledger and dispatch the already frozen formal
T7 read-only review prompt:

`docs/prompts/phase6_t7_v3_0_contract_review.md`

T1 must not contact or start T7, T4, V3.1, or any producer. If T7 later returns
a bounded repair to T1 through T0, change only the explicitly allowed files,
preserve the current candidate identities, and create a new artifact revision
where science/formula/domain/threshold content changes.

## 9. Must-read order for the next T1

1. `project.md`
2. YAML header and latest V3 entries in `status.md`
3. `docs/handoffs/T0_current.md`
4. this handoff
5. `docs/prompts/phase6_t1_v3_0_literature_formula_freeze.md`
6. `docs/prompts/phase6_v3_master_prompt.md`
7. `docs/phase6_v2_to_v3_transition.md`
8. `docs/phase6_v2_to_v3_transition_dispatch_addendum.md`
9. all eight V3.0 outputs
10. the V2 convention/domain authorities and current V1/V2 manifests

The older Phase 5 startup prompt and the archived pre-V3 handoff are historical,
not current task authority.

## 10. Allowed and forbidden files

This completed task wrote only:

- the eight required V3.0 outputs;
- `docs/handoffs/T1_current.md`;
- `docs/handoffs/archive/T1_2026-08-11_pre_v3_0_freeze.md`.

It did not use the optional permission to append
`references/manifest.md`, `docs/equation_map.md`, or
`docs/physics_spec.md`, because the eight dedicated outputs fully carry the
new mapping and this avoids overlap with the pre-existing dirty worktree.

Forbidden without a new T0 authority:

- any `src/`, `scripts/`, `tests/`, or `runs/` change;
- any V1/V2 config, immutable artifact, protected radial source, Li artifact,
  another task handoff, or `status.md` change;
- any solver, partial-wave sum, benchmark, numerical scan, figure generation,
  full suite, GitHub operation, or downstream dispatch.

## 11. Verification commands and definition of done

Required read-only checks:

```bash
jq empty configs/phase6_v3_0_domain.json
jq empty configs/phase6_v3_0_thresholds.json
jq empty configs/phase6_v3_0_external_anchor_matrix.json
shasum -a 256 <all frozen inputs, seven protected files, D-union plan>
shasum -a 256 <eight V3.0 outputs and T1 handoffs>
git diff --check -- <T1 allowed changed files>
ps -axo pid=,ppid=,command=
```

Definition of done:

- all eight outputs exist with the ledger above;
- JSON canonicality/schema/content checks pass;
- primary-source locators and formula conversions are complete;
- final protected identities equal the start identities;
- scoped diff check is clean;
- no V3 producer/process ran;
- only T1-allowed files changed;
- T1 returns only the exact checkpoint recorded in Section 1.
