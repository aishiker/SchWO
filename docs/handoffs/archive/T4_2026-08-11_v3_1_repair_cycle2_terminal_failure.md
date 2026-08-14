# T4 V3.1 bounded repair cycle 2 — terminal scientific failure

Date: 2026-08-11

## Outcome

The formally approved final repair cycle closed both implementation blockers
before official science:

- the exact first Route-A key completed all 20 frozen nodes;
- the complete producer/synthetic graph reconstructed exact
  `496/9920/102/458/23`, 16 thresholds and five certificates.

The unique official artifact-revision-3 run then failed the first blocking
scientific threshold and stopped without retry:

```text
runs/phase6/classic_scattering/v3_1_mode_greybody_r3_20260811T133458Z_py314
mode ordinal 0: kM=0.005, ell=2, odd
V3T-GAMMA-ROUTES-LOG-001 observed 0.01487180343263006
frozen limit 0.0002
```

This is a terminal V3.1 scientific failure, not an implementation exception,
system interruption or authorization to change the frozen threshold. Repair
cycle 2 of 2 is consumed. No cycle 3, retry, V3.2 or global GREEN is claimed.

## Pre-execution evidence

- final real sentinel:
  `/tmp/schwo_v31_repair_cycle2_sentinels_final.json`, SHA-256
  `6c95d7959ef4e50fdafd64ae1fa2f23fba96ef6b101b064fa5f914a77703fe55`;
- external sentinel:
  `/tmp/schwo_v31_repair_cycle2_sentinels_final.external.json`, SHA-256
  `a9b51bd7bc007ac5cd4aa763a8d397a34e916e34e744ac1f00a1d6ad479f5629`;
- first-key result: exact 20/20 completed, all six ladder thresholds PASS;
- direct-versus-shadow:
  `S` symmetric-relative difference `4.904897147934376e-11`,
  `log_Gamma` absolute difference `3.764810685424891e-11`;
- fixed Route-A strata: eight baseline nodes complete with auxiliary exponents
  `2,2,2,2,0,0,0,0` in frozen order;
- independent AP sentinels: eight 80/120-digit nodes complete and all
  applicable precision/Route-A comparison thresholds PASS;
- fresh external sentinel: Wolfram `14.3.0`, `(0.1,2,odd)`, one MST call;
- resource projection: `16559.072901578475 s`, disk gate PASS;
- synthetic full-route publication/reload PASS;
- exact CPython 3.14 V3 tests: `15 passed`;
- Ruff, format, compileall and exact-scope diff check PASS.

Final implementation identities:

```text
src/schwgw/validation/phase6_v3_continued_jost.py
  e7fec2ceb3ad1147108b1ea23696ba61ed6476396eb861ecb3d931cb41088db4
src/schwgw/validation/phase6_v3_mode_greybody_ap.py
  bd592ed6118957c2d44f85c25096c5da11e945465c34b61921627534a3229743
src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py
  a3990e9dc3bc5480478c037a77c0661e805508df49007848185e7178380da29e
scripts/phase6_v3_1_mode_greybody.py
  189fe1908dac6e592f4c8e1767c895058e2655f53bb607d06322714ca130e8d5
scripts/phase6_v3_1_bhpt_mst_cycle2.wls
  a7a53b9fee2e2001132b0b437b233f4fafff1362a113d21105913e2263dcdf6a
tests/unit/test_phase6_v3_cycle2.py
  d86fc31af71a2e3815cf063989918994495c05b1f8655bb8973bb8362c2dca39
```

## Immutable official boundary

The root is `0555`; its nine regular files are `0444`, nlink1; its sole child
directory is `0555`; there are no symlinks, lock files or related processes.

Critical identities:

```text
failure.json
  a6001141310a0629b3b26aa7297891ee37ab06a2a70e29c752e117d237695d47
failed_evaluation.json
  f24765b878f56a849e4c114f73bfb61a5d422bbcf8005db5c799ac4a4b7ecfbc
failure_manifest.json
  ab0f155f14313abed1d95716a30793411ed1d0ac076123933a1b1bbdd9e69fae
records.jsonl
  bff2504d97b5efd390275d2bd090db37d90f8f1849b68eb400ae4471605346ca
ladder_records.jsonl
  93e8a8d02fa8144780a5fd8660b9b68634afe24dda6c7cfd66533b4e86e16397
mode_checkpoints/route_a_0000.json
  986fb105993871a752803555482d1d56d50947192583459d357f18a3cb26a81c
source_start.json
  c73c1c585af9bbfeed8d50a2b28c9c2f94e08b38214b3db716fe1c7e501e2d16
run_contract.json
  94984670999b04ce78c4328f6ad210d874148c385094e801a0f98480afae08cf
```

Exact baseline operands:

```text
S = 0.9950172730764332 - 0.09970268942972751 i
T_H = 8.23009590693428e-09 + 1.352776463596543e-07 i
Gamma_flux = 1.836777608324503e-14
Gamma_S = 1.8096635301389888e-14
log_Gamma_flux = -31.628178565437718
flux_balance_residual = 3.266519330862382e-16
```

The root contains exactly one Route-A mode and 20 ladder records. Route B,
Route C, summary/certificates and success manifest are absent by design after
the early blocking failure. All seven protected radial SHA-256 identities are
unchanged from the approved package.

## Required next action

Root T0 owns read-only boundary verification and dispatch of the frozen formal
T7 delta-review-2 prompt. Since this is final bounded repair cycle 2 and a
blocking scientific threshold failed, T4 does not authorize or propose a
retry, threshold change, protected edit or V3.2 work.
