# T6 Current Handoff

Last updated: 2026-08-14

## Current state — V3.1 manually stopped; T6 not authorized

The user manually stopped the V3.1 chain. No T6 implementation, test repair,
Wolfram/BHPT/AP/radial/solver/science call, dispatch/root creation, V3.2
transition or global GREEN is authorized.  Do not use any historical V3.1,
V3.1-U, V3.1-X, V3.1-Y or V3.1-Z prompt below as live authority.

The current stop report is
`docs/reports/phase6_v3_1_all_versions_failure_defect_report_20260814.md`
(`a707e9ca893af160932a0012a03623356b1905f3a45b1b8c0ef5e1c314b13f93`).
The compact computation/source bundle is
`SchWO_Phase6_V3_1_all_versions_computation_bundle_20260814.zip`
(`8fe85269a28ddf912b209c319983f6ff2d47e5cddcb52e8a63f9c9ab9c78414d`).

Future T6 work requires a fresh Root-T0 instruction.

## Superseded state — V3.1-Y package under formal T7 review; T6 not authorized

Root T0 froze distinct package `configs/phase6_v3_1_y_external_protocol_package.json`
at SHA-256 `bbb9e97636a8da63d6e29be2a013fb99f09c8667a1608688de03006a9d916203`.
Formal T7 is reviewing it.  T6 may not act unless T7 returns the exact package
`ADVANCE / NOT_ASSESSED` verdict and Root T0 separately dispatches frozen T6
prompt `db022d4b...b015`.  Until then, code/tests, Wolfram, dispatch/root,
micro/sentinel/official science and V3.2 are forbidden.

## Prior terminal state — V3.1-X exact-five implementation not accepted

T6 completed the repair-cycle-2 exact-five static/synthetic implementation
checkpoint, but its single development real-Wolfram zero-science launch failed
closed before solver/science and its temporary transcript was lost.  T6
returned `ESCALATE / NOT_ASSESSED`; Root T0 did not authorize a T6 retry.

Formal T7 then ran its one permitted persistent review preflight and also
received rc69 at the WLS semantic normalizer.  Final archive SHA-256 is
`e5f9b9503e16b053525dfba7dacb661abc433211d49dcccb2c5c9dc442af1dee`.
V3.1-X is frozen; T6 has no current implementation or execution authority.
V3.1-Y is design-only in formal T4.  No Wolfram, solver, dispatch/root, V3.2
or global GREEN is authorized for T6.

Thread: Phase 6 T6 V2.4 selected-release live-handoff control-plane repair.

## Current authorization — await V3.1-X authority-bridge package review

Root T0 froze the distinct control-plane package
`configs/phase6_v3_1_x_authority_bridge_package.json`, SHA-256
`d043a1c7198496c9f0314a898585762e10b2df5054ea43250a724f7a9c6e054a`,
after the source implementation gate exhausted repair cycle `2/2`. This is not
repair cycle 3. It only proposes changing the stale fixed implementation-review
path plus two zero-science test files.

T6 is not yet authorized to implement. Formal T7 must first accept the exact
package. If Root T0 later dispatches prompt
`docs/prompts/phase6_t6_v3_1_x_authority_bridge_implementation.md`
(`12042b33...42b7a`), T6 must remain within the exact three paths and may not
run Wolfram/solver, create dispatch/root, change scientific bytes or start
V3.2.

## V2.4 control-plane repair V2 checkpoint

```text
CHECKPOINT / V2 SELECTED-DOMAIN RELEASE CONTROL-PLANE REPAIR V2 FROZEN
```

Root T0's pre-T7 independent audit found that V2.4's own historical
`check-only` and reconstruction fixture still requested the original
dispatch-time T7 handoff byte identity. The bounded repair changes only those
read-only callers to pass `require_dispatch_review_identity=False`.

Actual V2.4 publication retains the default strict `True` gate at both start
and end. Regressions simulate an advanced live handoff, prove historical
reconstruction remains available, prove the strict path rejects an identity
mismatch, and prove publication creates no output root before that gate.
`DISPATCH_T7_SHA256`, certificates, source scientific states, thresholds,
conventions, domain and predecessor artifacts are unchanged.

## Current V2 selected-release authority

```text
runs/phase6/asymptotic_waveform/v2_selected_release_v2_20260811T083414_py314
```

| file | SHA-256 |
|---|---|
| `manifest.json` | `51ddf1580448382be7e182f92cf76bbf53ed39f15418af9e546f357979c743eb` |
| `release_ledger.json` | `8bbc4d098ca64ac256a63a09e4e5744191f314038fe140c131eaf7606f75ba49` |
| `report.json` | `58157a422fabed9be8bb9956c3097296c6dfd30b8d8065d4731edf6fe5a826dc` |
| `source_map.json` | `9011a2cff8a944d68234a32cd754c7b6482b61644464fc512b906e2fbec76fb7` |
| `summary.json` | `25dcc333085e3cd7150bf9e954766ae60a942f3a6e51c20ff36a4081077045cb` |

The root is `0555`; all five files are direct regular `0444`/nlink1.
Exclusive creation, fsync, start/end hashes, in-place reload and a distinct
temporary-copy reload passed. Exactly one matching v2 root exists.

The v2 release ledger and summary are byte-identical to v1: twelve ordered
certificates remain 11 `PASS` and one absolute-phase `PARTIAL`; the exact
30-key/120-record domain, budgets, native evidence, claim ceiling,
`global_status=null` and `radial_solve_count=0` are unchanged. Only the
report/source-map/manifest provenance reflects this repair.

## Superseded v1 preservation

`runs/phase6/asymptotic_waveform/v2_selected_release_v1_20260811T081608_py314`
remains immutable and byte-for-byte unchanged. Its five hashes remain
`1500c198...27d3f` / `8bbc4d09...ba49` / `44b6e503...fc0c` /
`bc459ba0...08c7` / `25dcc333...45cb`. It is superseded evidence and forbidden
as current authority.

## Repair-owned identities

| path | SHA-256 |
|---|---|
| `src/schwgw/validation/phase6_v2_selected_release.py` | `b6f7c0055d92bf663917a30144793441dc590d6388d56b19f37e210f1bcc54d7` |
| `scripts/phase6_v2_4_publish_selected_release.py` | `7bcb29fcb2a811bc7fb353f59ac42a0ce1293a6a829066136f7b048281af4e7c` |
| `tests/unit/test_phase6_v2_4_selected_release.py` | `b84e7795cd2e449b8f121d139047ea443d02a714e1c823bcf75670d521370f98` |
| `tests/regression/test_phase6_v2_4_release_publication.py` | `600016d04bc87ce99e1e55e14a9bb6095b7e9709f5a13a3befac8197211930fb` |

## Repair verification

- targeted V2.4: `12 passed`;
- affected V2.3/V2.4: `27 passed`;
- all Phase-6/V2: `393 passed, 2 skipped, 2 warnings in 114.86s`;
- full suite: `1579 passed, 119 skipped, 1 xfailed, 151 warnings, 104 subtests passed in 464.56s`;
- four repair-owned files: Ruff format/check PASS;
- compileall, repository `git diff --check`, collision/process checks,
  protected/source start/end hashes, v1 five-file preservation, v1/v2
  ledger-summary byte identity, manifest/permissions and both reloads: PASS.

Repository-wide Ruff retains the pre-existing out-of-scope baseline of 152
files that would be reformatted and three lint findings. No out-of-scope file
was changed. T6 did not dispatch or message T7.

## V2.4 terminal checkpoint

```text
CHECKPOINT / V2 SELECTED-DOMAIN RELEASE FROZEN
```

Root T0's exact V2.4 prompt SHA-256 was
`635f08459f876d0be6bd2f9a76acc8bd89cec6ada0529b33318e2010bc500806`.
The formal predecessor verdict was exactly `ADVANCE_DECISION: ADVANCE`,
`CLAIM_STATUS: PARTIAL`, and
`ACCEPT GREEN / V2.3 SELECTED-DOMAIN WAVEFORM AND FLUX CLOSURE READY FOR V2.4`.
T6 did not dispatch or message T7 and added no scientific calculation.

## V2 selected-domain release authority

The single immutable release root is:

```text
runs/phase6/asymptotic_waveform/v2_selected_release_v1_20260811T081608_py314
```

| file | SHA-256 |
|---|---|
| `manifest.json` | `1500c198333c87e0a75bdb0bfedf881f11bc9eb307a17fd1ef5cf97a2df27d3f` |
| `release_ledger.json` | `8bbc4d098ca64ac256a63a09e4e5744191f314038fe140c131eaf7606f75ba49` |
| `report.json` | `44b6e50302653784798b7015eb9fb5509b08e5f85603a720a5f8216fd1b0fc0c` |
| `source_map.json` | `bc459ba099dbbec3bf48b7c68c9a55828c2b9029a24afbd0d9143c02166108c7` |
| `summary.json` | `25dcc333085e3cd7150bf9e954766ae60a942f3a6e51c20ff36a4081077045cb` |

The root is `0555`; all five files are direct regular `0444`/nlink1. Exclusive
creation, fsync, start/end rehash, in-place reload and a distinct temporary-copy
reload passed. Exactly one matching release root exists.

## Exact certificate state

The release natively reloaded the immutable V2.1, V2.2-v3 and V2.3-v2 roots
and derived exactly twelve ordered certificates. Eleven are `PASS`; only
`V2_ABSOLUTE_PHASE_CONVENTION` is `PARTIAL`, matching the accepted source
ceiling. Each certificate contains the exact 30-key/120-record channel domain,
separate numerical and convention uncertainty budgets, evidence roots and
hashes, independence boundary, nonclaims, protected radial hashes and both
V2.0 authority hashes. Publisher source upgrades are fail-closed.

The summary stores `global_status=null`, `global_green_permitted=false`,
`claim_status=PARTIAL`, `absolute_phase=PARTIAL`,
`full_domain_v2=NOT_ASSESSED`, and `radial_solve_count=0`. No full-domain,
angular-sum, finite-observer, Li-figure, global-GREEN or 17,818-key
extrapolation claim is made. V1 full-domain independent certification remains
`PARTIAL`.

## T0-adjudicated V2.3 read-only control-plane repair

The initial required full-suite run exposed a live-handoff false positive:
historical V2.3 reconstruction/check-only callers still required the original
execution-time T7 handoff byte identity after T7 had legally advanced to V2.4.
Per Root T0's bounded adjudication, only the historical `check-only` and
reconstruction test callers now pass `require_dispatch_review_identity=False`.

Actual V2.3 publication continues to use the default strict `True` dispatch
gate, with dedicated regression coverage. `DISPATCH_T7_SHA256`,
`src/schwgw/validation/phase6_v2_flux_closure.py`, all formulas/records and all
published roots are unchanged. The science/validation module hash remains
`dd14b7910890ff752c34e9fae55147a2ad08e33777b07a13919737342f1eaa8a`.

Current bounded control-plane identities are:

| path | SHA-256 |
|---|---|
| `scripts/phase6_v2_3_publish_flux_closure.py` | `3e07834eb2b948862aac3811659d94cb4896b0c8ee2c8d74e0e4b94f6f62f983` |
| `tests/unit/test_phase6_v2_3_flux_closure.py` | `147288fb8416bbaf71847ad69c6b08bbcb2d9b334c870b4bc9e1fe29e6239d08` |
| `tests/regression/test_phase6_v2_3_flux_publication.py` | `7db015fd0575dfd8e7355a6724df1f353e5c0dc10709f3eef7efdd751ec71dee` |

## Verification record

Exact CPython `3.14.6`, mpmath `1.4.1`, the absolute overlay first and
`PYTHONDONTWRITEBYTECODE=1` were used.

- targeted V2.4 release tests: `9 passed`;
- affected V2.3/V2.4 control-plane tests: `24 passed`;
- all Phase-6/V2 tests: `390 passed, 2 skipped, 2 warnings in 108.36s`;
- full suite: `1576 passed, 119 skipped, 1 xfailed, 151 warnings, 104 subtests passed in 462.01s`;
- seven owned/control-plane Python files: Ruff format/check PASS;
- compileall, repository `git diff --check`, start/end source/protected hashes,
  process/collision checks, permissions/nlink/manifest and both immutable
  reloads: PASS.

Repository-wide Ruff retains the pre-existing out-of-scope baseline of 152
files that would be reformatted and three lint findings; none was modified.
The full closeout is `docs/phase6_v2_selected_domain_closeout.md`.

## V2.3 summary precision-provenance repair checkpoint

```text
CHECKPOINT / V2.3 SUMMARY PRECISION-PROVENANCE REPAIR V2 FROZEN
```

Root T0's bounded `CONTROL_PLANE_REPAIR` prompt SHA-256 is
`531cc709a766693d925adb9ff82163648b155adf538540872563d63abdde23c9`.
The required predecessor checkpoint and all five predecessor identities were
exact.  T6 did not dispatch or message T7, did not start V2.4, and did not call
a radial solver, angular sum, Li figure or paper-figure workflow.

## V2.3 current immutable authority

The single fresh repair root is:

```text
runs/phase6/asymptotic_waveform/v2_3_flux_closure_v2_20260811T050013_py314
```

| file | SHA-256 |
|---|---|
| `manifest.json` | `a0fc62a4e8fc47176832d8b749285e7f0be9cad46e69911900230f591028694b` |
| `records.jsonl` | `ba8617224c89c7122e27d0399dafc510d126dd2b4cfd0ca2d8f741ae2a454d39` |
| `report.json` | `3d8fa27847887f4cb9605f18b1241f948a87362f6a2f3f4e056d678061cd6166` |
| `source_ledger.json` | `2c91e4b4f1567b5911e3fda2611b64d303e8dba16484be9d450403225677ac2a` |
| `summary.json` | `336379cf0e20e14af898f4e4dee04523fb851d4c70c23efedfed3d49d935c29f` |

The root is `0555`; all five files are direct regular `0444`/nlink1 files.
Exclusive publication, fsync, start/end rehash, in-place reload and a distinct
temporary-copy reload passed.  Both reloads were explicitly run from ambient
`mp.dps=15`; ambient precision remained 15 afterward.

## Exact bounded repair

The sole defect was control-plane precision provenance: the predecessor
`_summary()` called `_extrema()` after the 120-record builder had left
`mp.workdps(100)`.  The repair wraps all summary-extrema parsing, comparison
and serialization in explicit `mp.workdps(WORKING_DPS)` and adds strict reload
validation of all stored extrema.

The regression begins at ambient `mp.dps=15`, rebuilds the 120 records and
constructs summary/report, then repeats at ambient 100.  Corrected summary and
report scientific content are byte-identical, all extrema exactly match the
canonical record strings at 100 dps, and ambient precision is restored.

Corrected selected values are:

| field | exact corrected value |
|---|---:|
| minimum external horizon fraction | `9.373615409990476292528436114160436756813021669668934587236550056169801667903105000000000000000000000e-1498` |
| maximum SchWO balance residual | `2.456693814984740735626905876280748921163992416622833176415819278372141073001165780195065440402033493e-10` |
| maximum external balance residual | `1.507593570579673192937307132619084520714038294582231000000000000000000005723877939848698251816805805e-29` |

The repair-owned source identities are:

| path | SHA-256 |
|---|---|
| `src/schwgw/validation/phase6_v2_flux_closure.py` | `dd14b7910890ff752c34e9fae55147a2ad08e33777b07a13919737342f1eaa8a` |
| `tests/unit/test_phase6_v2_3_flux_closure.py` | `170a9d4391294e5c3c3f4e0f8f3a1045f0277553cd0ea6a1d6fe6b31f653c213` |

The publisher and regression-publication test were not changed; their hashes
remain `f42241e1...e1406` and `c8bb426d...a93c8`.

## Science-byte preservation and predecessor state

The candidate `records.jsonl` is byte-identical to the predecessor; both have
SHA-256
`ba8617224c89c7122e27d0399dafc510d126dd2b4cfd0ca2d8f741ae2a454d39`.
Exactly 120/120 records and all frozen numeric/predicate checks remain PASS;
`radial_solve_count=0`.  No formula, threshold, comparator, source input,
record construction, uncertainty vocabulary, scientific conclusion or claim
ceiling changed.

The predecessor root
`runs/phase6/asymptotic_waveform/v2_3_flux_closure_v1_20260811T044845_py314`
remains byte-for-byte preserved with manifest/records/report/source-ledger/
summary hashes `1371e85d...ceb2b` / `ba861722...4d39` /
`d76ed626...fcad` / `930e6858...f7ee` / `2b6d334d...b45e`.  It is immutable
superseded evidence and forbidden as current V2.3 authority.

## Bounded verification record

Exact CPython `3.14.6`, mpmath `1.4.1`, the absolute project overlay first and
`PYTHONDONTWRITEBYTECODE=1` were used.

- focused V2.3 tests: `16 passed in 2.39s`;
- all Phase-6/V2 tests: `379 passed, 2 skipped, 2 warnings in 104.80s`;
- Ruff format: `4 files already formatted`; Ruff check: PASS;
- compileall, repository `git diff --check`, permissions/nlink/manifest,
  predecessor/candidate records byte identity, collision/process checks,
  independent reloads and start/end frozen/protected hashes: PASS.

Per the bounded repair prompt, the full suite was not rerun.  The completed
predecessor result (`1564 passed, 119 skipped, 1 xfailed, 151 warnings, 104
subtests passed`) remains valid.  No residual V2.3/radial/Li/Wolfram process
remained.

The claim ceiling is unchanged: selected-domain flux closure remains `PASS`,
`absolute_phase=PARTIAL`, full-domain V2 and observer/angular/Li claims remain
`NOT_ASSESSED`, `global_status=null`, and `global_green_permitted=false`.

## V2.3 terminal checkpoint

```text
CHECKPOINT / V2.3 SELECTED-DOMAIN FLUX CLOSURE EVIDENCE V2 FROZEN
```

Root T0's exact V2.3-v2 dispatch was authenticated with prompt SHA-256
`25f2f42febaaec9c6eb8ebe621ff1d095648c5aca4f0154c4b3c8b9acd959ba0`.
The required pre-execution threshold verdict was present exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V2.3 FLUX THRESHOLD CONTRACT READY FOR BOUNDED EXECUTION
```

The build-time T7 handoff SHA-256 was
`d8911118767749712b82927c4511a8a9ea3217b1e60808c5ef0101c8ab577554`.
The accepted V2.2-v3 predecessor verdict was also exact:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PARTIAL
GATE_LABEL: ACCEPT GREEN / V2.2 SELECTED-DOMAIN WAVEFORM ROUTES READY FOR V2.3
```

T6 stopped at this checkpoint.  It did not dispatch or message T7 and did not
start V2.4.

## V2.3 immutable authority

The single fresh publication is:

```text
runs/phase6/asymptotic_waveform/v2_3_flux_closure_v1_20260811T044845_py314
```

The root is direct `0555`; all five files are direct regular `0444`/nlink1
files.  There is no writer lock or staging residue.

| file | SHA-256 |
|---|---|
| `manifest.json` | `1371e85d80f97c5b3152a5103c3a7bda64a8e0094052cf2e8d3cd8e35d1ceb2b` |
| `records.jsonl` | `ba8617224c89c7122e27d0399dafc510d126dd2b4cfd0ca2d8f741ae2a454d39` |
| `report.json` | `d76ed626701f7d40c890a95ee30b32f77ca8314213d36bc6278b9993848afcad` |
| `source_ledger.json` | `930e68580dd6d7594349af673b6b436118b34657e2bdad84e551c6c25e69f7ee` |
| `summary.json` | `2b6d334d586b12565a1800ef4edeeea046c2e0151f52bad5adf6ad04447db45e` |

Publication used an exclusive single-writer lock, exclusive file creation,
fsync, start/end rehash, sealing, native immutable reload and a second reload
from a distinct temporary filesystem location.  All passed.  Exactly one
`v2_3_flux_closure_v1_*_py314` root exists.

## V2.3 scientific construction and result

Exactly 120/120 mandatory records were reconstructed: 30 accepted radial
keys, both `m=-2,+2`, and both plus/cross incident columns.  All mandatory
quantities were evaluated under `mp.workdps(100)` from frozen decimal strings;
the ambient precision was restored and no mandatory flux/current/fraction or
residual was cast to binary64.  `radial_solve_count=0`.

Every record explicitly carries the real-field-peak time average `1/2`,
`sigma_l=(ell+2)!/(ell-2)!`, `N_lm^p=c_lm^p/A_in_raw`, and the odd bridge
`Psi_CPM=(2i/omega)Psi_RW`.  Signed currents are oriented as
`J_in<0`, `J_out,total>0`, and `J_h<0`.  Route A and Route B total outgoing
coefficients were independently reconstructed as frozen free plus accepted
scattered coefficients.  Free/scattered squares are stored only as
nonadditive diagnostics and never enter balance.

The external direct witness uses the immutable original wp60 unit-incident
coefficients `A_in=1`, `A_out=reflection_ratio`, and
`T_horizon=transmission`; matching-basis incidence/reflection are retained
separately.  Odd nodes are direct Regge--Wheeler and even nodes are
independently solved Zerilli.

All six frozen numeric bounds and every exact predicate pass for all 120
records.  Selected extrema are:

| quantity | minimum | maximum |
|---|---:|---:|
| SchWO normalized balance residual | `1.9470318901176466e-16` | `2.4566938149847410e-10` |
| external normalized balance residual | `1.9083499790066837e-42` | `1.5075935705796733e-29` |
| Route-A/Route-B outgoing flux fraction difference | `0` | `0` |
| SchWO/external outgoing flux fraction difference | `1.9470318901176466e-16` | `5.0802505127305707e-12` |
| SchWO/external horizon fraction relative difference | `2.4539253513128565e-10` | `1.2221015159674824e-7` |

The smallest external horizon flux fraction is retained as the positive
100-digit value
`9.373615409990476240606543253796878289661300356491515003892678180379002016777380090956134044420557438e-1498`.
There is no signal floor or record omission.

## V2.3 owned implementation identities

| path | SHA-256 |
|---|---|
| `src/schwgw/validation/phase6_v2_flux_closure.py` | `10aec74f620e624275230cc213c042299972d0e15555e4901319c47dda8a4f43` |
| `scripts/phase6_v2_3_publish_flux_closure.py` | `f42241e1e49f2a10b8192a0d8071813580ca66f4803058ceed7ab8d43fbe1406` |
| `tests/unit/test_phase6_v2_3_flux_closure.py` | `bd1609d6b9a9e7a20f0bea671456ca12b4d2ba43506a83fa51b616ea606982c0` |
| `tests/regression/test_phase6_v2_3_flux_publication.py` | `c8bb426d6a4281029744ac27c424042902af8c2f7379c0da3faadf14b49a93c8` |
| `docs/phase6_v2_3_flux_closure_20260811.md` | `00b05f7c15ee404a7d6178ed0170f70502f01b45654969e1c50275b8e244706d` |

The tests cover frozen-input tamper, a Route-A factor tamper,
binary64-underflow retention, record omission, scattered-only balance,
exclusive writer/tamper publication behavior, and ambient mpmath precision
restoration.

## V2.3 verification record

All commands used exact CPython `3.14.6`, mpmath `1.4.1`, the absolute
project overlay first and `PYTHONDONTWRITEBYTECODE=1`.

- focused threshold/flux/publication tests: `15 passed in 2.00s`;
- all `tests/unit/test_phase6*.py` plus V2 regression tests:
  `378 passed, 2 skipped, 2 warnings in 106.29s`;
- complete pytest: `1564 passed, 119 skipped, 1 xfailed, 151 warnings,
  104 subtests passed in 445.74s`;
- focused Ruff format: `4 files already formatted`; focused Ruff check: PASS;
- compileall, repository `git diff --check`, native V2.1/V2.2-v3 reload,
  publication collision check, manifest/mode/nlink checks, start/end protected
  hashes, independent reloads and pre/post process checks: PASS.

No residual V2.3, radial, Wolfram or Li process remained.

## V2.3 protected identities and claim ceiling

At start and end the threshold contract/rationale/test hashes remained
`6cc64b3...8808`, `ce0da14...ee8`, and `ba85493...a5e4`; the V2.0
contract/domain and D_union plan remained `1251392...9517`,
`9703286...818`, and `de26684...67e3`.  All seven protected radial source
hashes matched exactly.  No frozen threshold, convention, domain, radial,
T7, V2.2, V1, external or V2.4 byte was modified.

The summary intentionally retains `claim_status=PARTIAL` because
`absolute_phase=PARTIAL`; selected-domain flux closure is `PASS`.
`global_status=null`, `global_green_permitted=false`, full-domain V2, angles
and angular sums, finite-radius observer responses and Li figures are
`NOT_ASSESSED`.  No global GREEN is claimed.

## 0. Post-checkpoint T7 adjudication synchronized by Root T0

After the T6 checkpoint, the existing formal T7 task completed delta review 1
against the exact v3 identities and returned:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PARTIAL
GATE_LABEL: ACCEPT GREEN / V2.2 SELECTED-DOMAIN WAVEFORM ROUTES READY FOR V2.3
```

The T7 durable record is at `docs/handoffs/T7_current.md`; its frozen review
prompt SHA-256 is
`93abcd27bfbba5fad66e1edf4ce6b85614a287a65cdc8814847fea856ff2b118`.
The sole current V2.2 authority is the v3 root in section 2.  The v2 root is
immutable superseded evidence and forbidden as current authority.  This
bounded GREEN does not start V2.3: `absolute_phase=PARTIAL`, full-domain V2
`NOT_ASSESSED`, full-domain V1 independent certification `PARTIAL`,
`global_status=null`, and no global GREEN remain unchanged.

## 1. V2.2 repair cycle 1 terminal decision

```text
CHECKPOINT / V2.2 EXTERNAL WP60 PRECISION REPAIR V3 FROZEN
```

The Root T0 repair dispatch was authenticated with prompt SHA-256
`8e1c589ff7381b89d76f23e242d2497c2bab73ffcf7823fd998799a3d3cd97a4`.
The required formal T7 state was present exactly:

```text
ADVANCE_DECISION: REPAIR
CLAIM_STATUS: PARTIAL
GATE_LABEL: REVIEW YELLOW / V2.2 CHANGES REQUIRED
blocker_id: v22_external_wp60_precision_scope
```

This is bounded repair cycle 1.  T6 stopped at the checkpoint, did not
dispatch or message T7, and did not start V2.3.

## 2. Fresh immutable V3 artifact

The single official repair root is:

```text
runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v3_20260811T113135_py314
```

It is sealed `0555`; all five files are direct `0444`/nlink1 files.

| file | SHA-256 |
|---|---|
| `manifest.json` | `3981aeb5424cbac4e7774fc84b5f03d5764561ea21a7338a60f19bf5f0d46660` |
| `records.jsonl` | `2f7b466036d1481766794aa13581dd9824c851a7e405117f94e192d849f526c9` |
| `report.json` | `fc66bb1a66f10257b80827ee292d180b0582587c3291332471971731dc352f9b` |
| `source_ledger.json` | `9fdbd6302fdc0eea93cc1ced1db76f2355343b3538dfee35f5145ac8e5b518a1` |
| `summary.json` | `fdd314e760c4fa71c555f9eadb13eeb8389d0b24c0f6e8822eb1005afc9b8b19` |

Exclusive publication, the publisher's post-seal reload, a separate fresh-
process reload and official-root collision rejection all passed.  Exactly one
`v2_2_waveform_routes_v3_*_py314` root exists.

## 3. Blocker repair and independent source reconstruction

`_external_inventory()` now retains each original wp60 `phase_factor`
mapping as decimal strings.  Conversion is delayed until the record loop is
inside `mp.workdps(80)`.  Every record stores both the exact source-decimal
mapping and `external_S_l_parse_dps=80`.

Publication reload now reopens the immutable external wp60 nodes, rebinds each
record to its accepted V2.1 source record, parses the original strings at 80
dps, and reconstructs Route A/B/C plus all three pair records.  It does not use
the candidate's `external_S_l` as the Route-C authority.  A fresh independent
CPython process beginning at default `mp.dps=15` returned:

```text
external_S_l source matches:       120/120
Route-C coefficient source matches: 120/120
pairwise comparator source matches: 360/360
working_dps: 80
ambient_dps after reload: 15
```

The new regression also proves the superseded v2 root fails this source-
anchored precision check.  The repair-owned source identities are:

| path | SHA-256 |
|---|---|
| `src/schwgw/validation/phase6_v2_waveform_routes.py` | `2e996d5070f6db370523dbd3c9f620a6b2dcca6c9d37c79c9c9ed2b8860b4fe4` |
| `tests/unit/test_phase6_v2_2_waveform_routes.py` | `da88978565b7587e421f8692fe993a046a1246659caa8e7e41fd31e5978dde27` |
| `tests/regression/test_phase6_v2_2_waveform_publication.py` | `a5a7f1879b1d153d31c2a5c6d765d28c4002512bf11e94fca9893a31d88c77d6` |

## 4. Passed-invariant preservation and comparator result

All nine T7 `passed_items` remain exact.  The inventory remains 15 parity
pairs, 30 radial keys and 120 records.  Route A objects and Route B objects
are byte-for-byte field-equal to their v2 counterparts for 120/120 records;
Route B formulas and implementation were not edited.  Odd direct RW and
independently solved even Zerilli provenance, fixed scale/no fit, all 1440
frozen comparator gates, signal floor, separate budgets, scope exclusions and
canonical immutable publication remain PASS.

| pair | scaled complex max | relative magnitude max | wrapped phase max | invariant max |
|---|---:|---:|---:|---:|
| A/B | 0 | 0 | 0 | 0 |
| A/C | `1.7268260303698522136620714390448437e-8` | `6.8881218099830081017293822416282636e-8` | `8.6341320575893380780232116884862305e-9` | `1.6867592039929375143632359829068915e-8` |
| B/C | `1.7268260303698522136620714390448437e-8` | `6.8881218099830081017293822416282636e-8` | `8.6341320575893380780232116884862305e-9` | `1.6867592039929375143632359829068915e-8` |

The minimum signal-floor value for every pair is
`0.2157380334003980381944413604204866`, strictly above `0.1`.  There are zero
comparator failures.

## 5. Verification record

Verification used CPython `3.14.6`, mpmath `1.4.1`,
`PYTHONDONTWRITEBYTECODE=1` and the frozen absolute overlay-first
`PYTHONPATH`:

- exact T7 focused recheck: `10 passed in 1.14s`;
- all Phase-6/V2 tests: `363 passed, 2 skipped, 2 warnings in 105.42s`;
- complete pytest suite: `1549 passed, 119 skipped, 1 xfailed, 151 warnings,
  104 subtests passed in 449.59s`;
- focused Ruff format: `3 files already formatted`;
- focused Ruff check, compileall and scoped `git diff --check`: PASS;
- frozen/source/old-v2 start/end hashes, process check, fresh-root check,
  independent reload and collision rejection: PASS.

The first all-Phase-6 invocation used the prompt's relative overlay-first
spelling and was rejected before scientific assertions by two preexisting
runtime tests that require the exact absolute `PYTHONPATH` environment string.
The identical suite then passed under the frozen absolute overlay-first path;
the runtime policy and tests were not modified.

## 6. Preserved identities, superseded evidence and nonclaims

All 23 protected/frozen identities matched at start and end, including the
repair prompt, historical v2 prompt, convention contract, domain, D_union
plan, threshold package, seven protected radial sources, V2.1 records/root,
external manifest and all five old-v2 files.

The old v2 root remains byte-for-byte unchanged:

| file | SHA-256 |
|---|---|
| `manifest.json` | `7b1fd01983dc03e8c3c027b74e3d01aac2962a129614248d6a2e96284cf5093f` |
| `records.jsonl` | `9ae79a006fdbd9f86a385b085bc1cb4d9fcdea52b2debccf7a0b16bfb970ec74` |
| `report.json` | `6e9ce7cfb18390e21fbe5385d57ff77acfc3aed7929c294c54cee7b9b1ea5a0a` |
| `source_ledger.json` | `18ca221fa2b221bffdc22cd1bcb4f24b91485dce70817ae8003b4b50e81de66d` |
| `summary.json` | `76e289f748490b77a6266d7ae6723f7e6f4498cc9660a2a78d402aea31b3966e` |

It is immutable superseded evidence and forbidden as current V2.2 authority.
The v3 summary retains `radial_solve_count=0`, `global_status=null`,
`global_green_permitted=false`, `absolute_phase=PARTIAL`, full-domain V2
`NOT_ASSESSED`, and full-domain V1 independent certification `PARTIAL`.
Flux, finite-radius observer, angular/`m` sum, total-plane-wave infinity sum
and Li-figure claims remain outside this gate.  Formal T7 delta review remains
pending; this checkpoint does not itself grant advance.

## 7. Preserved V2.2 v2 predecessor record

```text
CHECKPOINT / V2.2 THREE-ROUTE ASYMPTOTIC WAVEFORM EVIDENCE V2 FROZEN
```

The Root T0 superseding dispatch was authenticated with prompt SHA-256
`4fd8f01c51cb8df41a14e6ac15b46270e6da108a3fba99b366c61c06b0787689`.
Both required formal T7 decisions were present exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V2.1 MODE-LEVEL ASYMPTOTIC AMPLITUDES READY FOR V2.2

ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V2.2 WAVEFORM THRESHOLD CONTRACT READY FOR EXECUTION
```

The threshold contract/rationale/test identities were respectively
`8c2ab9ca254df9c15e3947479bb0af3bb6204f37d326b52c16a0984604ae005e`,
`c96a0c640ffb2789c34e8e9ff364d42cc6cfe427b374a7cff1299d196b3c91b6`,
and `71918930e4b1384ab66adaf5e7d89bc55c31c30f156fa6f153332542759c611a`.

### V2.2 v2 formal artifact

The single fresh no-overwrite root is:

```text
runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v2_20260811T104500_py314
```

It is sealed `0555`; all five files are direct `0444`/nlink1 files.  The
exclusive publish, post-seal reload, separate strict reconstruction and
same-root collision rejection all passed.

| file | SHA-256 |
|---|---|
| `records.jsonl` | `9ae79a006fdbd9f86a385b085bc1cb4d9fcdea52b2debccf7a0b16bfb970ec74` |
| `report.json` | `6e9ce7cfb18390e21fbe5385d57ff77acfc3aed7929c294c54cee7b9b1ea5a0a` |
| `summary.json` | `76e289f748490b77a6266d7ae6723f7e6f4498cc9660a2a78d402aea31b3966e` |
| `source_ledger.json` | `18ca221fa2b221bffdc22cd1bcb4f24b91485dce70817ae8003b4b50e81de66d` |
| `manifest.json` | `7b1fd01983dc03e8c3c027b74e3d01aac2962a129614248d6a2e96284cf5093f` |

### V2.2 v2 three-route result and observable chain

The exact accepted inventory contains 15 parity pairs, 30 radial keys and
120 unique `(radial key, incident column, m)` records.  It stores 360 route
amplitudes, 360 mandatory pair evaluations and 1440 comparator values.  Every
record and every pair is present; all signal-floor and comparator states are
`PASS`.

Route A maps the accepted V2.1 Li scattered master coefficient to MP ZM/CPM.
Route B independently evaluates an RW-gauge metric leading-coefficient chain,
the direct asymptotic curvature/`Psi4` coefficient, and the frozen symmetric
outgoing tetrad.  Its recorded reduced relations are

```text
odd:  B_t/r=q, B_1/r=-q, r Psi4_K=-omega q/2
even: T_0/r^2=i omega q, R_t/r=omega^2 q,
      L_0/r=-omega^2 q, h_tt/r=-omega^2 q,
      r Psi4_K=-omega^2 q/4
Psi4_symmetric=2 Psi4_K
H_even=-2 Psi4_symmetric/omega^2
H_odd=2 Psi4_symmetric/(i omega^2)
```

The Route B internal complex residual maximum is exactly zero.  It neither
copies Route A's final coefficient nor uses a finite-radius observer API,
`static_orthonormal`, `li_literal_cartesian`, packaged-NP pseudoinverse or a
radial solver.  Route C uses only immutable external direct odd RW and
independently solved even Zerilli evidence plus the explicitly shared frozen
analytic convention.  The external manifest
`e12c49b00efecc9c65d42699f2a5052ecac1fe2c988312ed21c4da085fe5ee6d`,
all 92 members and exact 30-key order were independently verified.

Observed pair maxima are:

| pair | scaled complex | relative magnitude | wrapped phase | phase invariant |
|---|---:|---:|---:|---:|
| A/B | 0 | 0 | 0 | 0 |
| A/C | `1.72682603135230412469898e-8` | `6.88812181630939736986968e-8` | `8.634132123709245139796707e-9` | `1.686759204377777113456819e-8` |
| B/C | `1.72682603135230412469898e-8` | `6.88812181630939736986968e-8` | `8.634132123709245139796707e-9` | `1.686759204377777113456819e-8` |

The minimum normalized signal is
`0.21573803340039804377`, strictly above the frozen `0.1` floor.  Every
record stores the fixed `C_record`, exact threshold path/hash/field, no-fit
state, pairwise shared-source provenance, and separate numerical/convention
budgets.  No per-mode phase fit, global complex rescaling or post-result
threshold change was used.

### V2.2 v2 claims and stop boundary

The artifact states:

```text
radial_solve_count=0
global_status=null
global_green_permitted=false
selected_domain_comparator_state=PASS
claim_status=PARTIAL
absolute_phase=PARTIAL
```

The final two `PARTIAL` states are the frozen absolute-phase claim ceiling;
they do not erase the independently passing magnitude, phase-invariant and
no-fit relative-phase evidence.  Angles, angular/`m` sums, finite-radius
observer responses, a total plane wave at null infinity, Li figures and
full-domain V2 remain `NOT_ASSESSED`.  Full-domain V1 independent scientific
certification remains `PARTIAL`.  This is not global GREEN.

T6 stopped at this checkpoint.  It did not dispatch or message T7 and did not
start V2.3.

### V2.2 v2 implementation and verification

New bounded V2.2 files are:

```text
src/schwgw/scattering/phase6_v2_2_waveform_routes.py
src/schwgw/validation/phase6_v2_waveform_routes.py
scripts/phase6_v2_2_publish_waveform_routes.py
tests/unit/test_phase6_v2_2_waveform_routes.py
tests/regression/test_phase6_v2_2_waveform_publication.py
docs/phase6_v2_2_waveform_routes_20260811.md
```

Verification used exact CPython `3.14.6`, project overlay first and
`PYTHONDONTWRITEBYTECODE=1`:

- threshold-contract plus targeted route/publication tests: `8 passed in 0.98s`;
- all Phase-6/V2 tests: `361 passed, 2 skipped, 2 warnings in 106.86s`;
- complete pytest suite: `1547 passed, 119 skipped, 1 xfailed, 151 warnings,
  104 subtests passed in 455.34s`;
- focused Ruff format: `5 files already formatted`;
- focused Ruff check, compileall and `git diff --check`: PASS;
- immutable reload/reconstruction: 120 records, 360 route amplitudes, 360 pair
  evaluations, 1440 comparators and zero failures;
- start/end identity checks, source member rehash, process check and single-root
  collision check: PASS.

The final post-documentation reload was also run explicitly as

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/src /opt/homebrew/bin/python3.14 scripts/phase6_v2_2_publish_waveform_routes.py reload --root runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v2_20260811T104500_py314
```

It returned `status=PASS`, 120 records, 360 route amplitudes, 360 pair
evaluations, 1440 comparators and zero failures.  An immediately preceding
invocation with only `PYTHONPATH=src` stopped before validation with
`ModuleNotFoundError: mpmath`; it changed no bytes and was corrected by the
required frozen absolute overlay-first command above.

Full-repository Ruff retained only the preexisting out-of-scope baseline:
three old lint errors (`test_io_results.py` F841, `test_tablei_extraction.py`
F401, `test_weyl_modes.py` F401) and 152 old files that would reformat.  These
were recorded without modification.

### V2.2 v2 frozen identities at terminal

The end rehash reproduced the threshold package, V2.0 convention/domain,
D_union plan and all seven protected-radial identities exactly.  The accepted
V2.1 manifest/records remained
`ae39829a3e95169f88aa7ce95639e5e3d473c9b7db23d6301cea24d40109ad90` /
`eb0e36ae49a1b868f22279d9948e748a69f89d281890df3e6af5ea4356d1bcc5`.
The external manifest remained
`e12c49b00efecc9c65d42699f2a5052ecac1fe2c988312ed21c4da085fe5ee6d`.

## 8. Preserved historical V2.2 HOLD predecessor

### Historical V2.2 terminal decision

```text
HOLD / V2.2 FROZEN WAVEFORM THRESHOLD ABSENT
ADVANCE_DECISION: ESCALATE
CLAIM_STATUS: NOT_ASSESSED
```

The Root T0 V2.2 dispatch was authenticated with prompt SHA-256
`689a9e7593cb2f928e5f262922118d41b0b05aa1eb7de87688a65c80349cd768`.
The required predecessor decision was present exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: PASS
GATE_LABEL: ACCEPT GREEN / V2.1 MODE-LEVEL ASYMPTOTIC AMPLITUDES READY FOR V2.2
```

The accepted V2.1 manifest remains
`ae39829a3e95169f88aa7ce95639e5e3d473c9b7db23d6301cea24d40109ad90`.
No V2.2 implementation or publication was started because the mandatory
threshold gate failed before route evaluation.

### Historical protocol-qualified HOLD details

```text
exact_reason: Mandatory A/B, A/C and B/C relative-magnitude, wrapped-relative-phase and phase-invariant comparators have no applicable acceptance threshold frozen before execution by path, SHA-256 and field.  The only non-null numerical threshold collection found is the external radial plan's flux/S/Jost/precision collection, which the frozen V2.2 prompt explicitly forbids repurposing as waveform thresholds.
unblock_condition: Root T0/user freezes a new identity-bound V2.2 waveform-threshold contract that specifies every mandatory comparator definition, units, numerical value, applicable route pair and exact selected domain, plus its path/SHA-256/field, and then formally redispatches T6 under that new frozen basis.
owner: Root T0 (V2 gate and threshold governance)
minimum_next_action: Freeze the minimal V2.2 waveform-threshold contract with independently auditable identities; current T6 must not infer, invent, weaken or write it.
independent_downstream_work_may_proceed: true
```

The final field permits only work independent of V2.2.  The dependent
V2.3/V2.4 chain may not proceed.

### Historical exact pre-execution evidence

- `configs/phase6_v2_0_convention_contract_20260810.json`
  (`1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517`):
  zero threshold-key occurrences; its acceptance policy requires future PASS
  components to pass frozen thresholds but does not create them.
- `configs/phase6_v2_0_selected_domain_20260810.json`
  (`9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818`):
  zero threshold-key occurrences.
- The accepted V2.1 `report.json` and `summary.json`: zero threshold-key
  occurrences.  V2.1's algebraic identity intentionally records
  `threshold=null` in its 120 records and is not a waveform acceptance gate.
- `runs/phase6/v1_observable_contract_v2_20260806/observable_contract.json`
  (`3853df8fbc245b81552198d99201778e4020d82f618e3f80ac745768fc3d104b`):
  zero threshold-key occurrences.
- `data/processed/phase6/v1_observable_measurements_selected_v1_20260808_py314/submission.json`
  (`ee8e76413914d0af465b00b86c954c5a342a672f5f7de9d312de1474cbfd7146`)
  and `runs/phase6/v1_observable_evidence_selected_v1_20260808_py314/observable_evidence.json`
  (`291745e684bd5354f4c42949126061117036efc3a3464c894c0d82275c312dad`):
  91 threshold-key occurrences each, all `null`; the selected evidence says
  no a-priori threshold or independent backend is bound.
- The external Route C plan contains only
  `numerical_thresholds.{flux_unitarity_residual,matching_radius_complex_S_spread,precision_log_abs_transmission,precision_relative_complex_S,precision_wrapped_phase_transmission_rad}`.
  These are radial-source checks, not A/B/A/C/B/C waveform thresholds.
- `docs/review_gate_liveness_protocol.md`
  (`3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181`)
  explicitly states that V2.2 liveness does not create, infer, repurpose or
  weaken a missing threshold.

### Historical identity, ordering and non-action audit

The V2.0 contract, selected domain, D_union plan and seven protected radial
hashes all matched the frozen prompt at start.  The V2.1 verifier also rehashed
all eight contract-listed V1 authorities successfully.

The authoritative external Route C root
`runs/phase6/radial_validation/v1_external_bhpt_direct_bounded_selected_v1_20260810_py314`
is `0555`; its manifest (`e12c49b00efecc9c65d42699f2a5052ecac1fe2c988312ed21c4da085fe5ee6d`)
binds 92 direct `0444`/nlink1 artifacts, all independently rehashed.  Its
summary is `50f448455ddf978591bf210ec103a1475ea0ccc0c3efd477dda77962081c644b`.
The exact 30-key order matches the V2.0 selected domain, the external result
order and the radial-key blocks in all 120 V2.1 records.

After the durable-record update, an independent end rehash reproduced every
prompt-listed V2.0/D_union/protected-radial hash, the V2.2 prompt hash, the
V2.1 manifest hash and both external-root hashes.  The V2.1 strict reload
again returned exactly 120 records, all eight contract-listed V1 authorities
rehash-verified, `git diff --check` passed, the fresh V2.2 root pattern remained
absent, and the final process check found no residual CPython 3.14, pytest,
Phase-6 publisher/runner or Wolfram kernel process.

T6 called no radial solver, constructed no route amplitude, added no angle,
performed no angular/`m` sum, created no output root and ran no paper figure.
No targeted/full test or publication command was appropriate after the
pre-execution HOLD.  T6 did not dispatch or message T7 and did not start V2.3.

## 9. Preserved V2.1 predecessor record

### V2.1 terminal decision

```text
CHECKPOINT / V2.1 MODE-LEVEL ASYMPTOTIC AMPLITUDES FROZEN
```

The formal Root T0 V2.1 dispatch is complete.  T6 stopped at the checkpoint.
T6 did not dispatch or message T7 and did not start V2.2.  The predecessor
decision was exactly:

```text
ACCEPT GREEN / V2.0 CONVENTION CONTRACT READY FOR BOUNDED V2.1 IMPLEMENTATION
```

### V2.1 formal artifact

The single fresh no-overwrite root is:

```text
runs/phase6/asymptotic_waveform/v2_1_mode_amplitudes_v1_20260810T184729_py314
```

It is sealed `0555`; all five files are direct `0444`/nlink1 files.  Internal
post-seal reload and a separate command-line reload both passed.

| file | SHA-256 |
|---|---|
| `records.jsonl` | `eb0e36ae49a1b868f22279d9948e748a69f89d281890df3e6af5ea4356d1bcc5` |
| `report.json` | `a9fbfd658211eb17b2b7d99177ad233b342eefaafffedf10ba56f0b41fb74a3a` |
| `summary.json` | `ae2e1c226c2330cc6f6fbdbb38381fd4db4ea71d71f504ff766398ab6ede1e27` |
| `source_ledger.json` | `1f3064dd334dbc4e0af2c8772c3230d5fd58fc8172003595eafb41035acd4dbc` |
| `manifest.json` | `ae39829a3e95169f88aa7ce95639e5e3d473c9b7db23d6301cea24d40109ad90` |

The manifest binds every non-manifest file.  The source ledger binds all 30
immutable selected-comparison records, the selected-source manifest, both
V2.0 JSONs, every V1 authority listed by the convention contract, the
project-local `mpmath 1.4.1` overlay, and the implementation sources.

### V2.1 implemented behavior

New files:

```text
src/schwgw/scattering/gauge_invariant_asymptotics.py
src/schwgw/validation/phase6_v2_mode_amplitudes.py
scripts/phase6_publish_v2_1_mode_amplitudes.py
tests/unit/test_phase6_v2_mode_amplitudes.py
tests/regression/test_phase6_v2_1_publication.py
docs/phase6_v2_1_mode_amplitudes_20260810.md
```

The formula module is typed, pure, and has no filesystem or solver effects.
The validation module strictly reloads immutable V1 evidence, builds records,
publishes with an exclusive writer, seals the root, and independently reloads
every byte and manifest identity.

Canonical ordering is radial-key ordinal, frozen incident-column order
`plus,cross`, then `m=-2,+2`.  Results are exactly:

- 15 odd/even pairs;
- 30 radial keys;
- 60 records per incident column;
- 120 unique route-mode-column records.

Only these frozen reconstructions are used:

```text
A_in_raw=-A_out_raw/[(-1)^ell S_l]
T_horizon_raw=exp(log_abs_T_horizon) exp(i phase_T_horizon)
```

Every source field, derived complex value, formula, and complex closure
residual is retained.  Mode formulas are evaluated at 80 dps; all 120 horizon
coefficients are nonzero, including a minimum Li magnitude
`2.8030433122098733207e-753`.

Even modes retain `psi_Li_even=Psi_ZM`.  Odd modes separately retain
`psi_Li_odd`, `Psi_RW=psi_Li_odd`, and
`Psi_CPM=(2 i/omega) psi_Li_odd` for `exp(-i omega t)`, plus
`Psi_RW=(1/2) partial_t Psi_CPM`.  RW is never relabelled as CPM.

All 120 records independently evaluate and store the complex residual of

```text
A_out,total,physical
  = A_out,free,physical + A_out,scattered,physical.
```

No threshold was added; the observed maximum 80-dps residual is
`1.8448846400653415643e-81`.

### V2.1 claims and non-claims

The summary states exactly:

```text
radial_solve_count=0
global_status=null
global_green_permitted=false
```

Angles, angular/`m` sums, finite-radius observer responses, Li figures,
physical flux, three-route comparison, and full-domain V2 are not assessed.
No scientific result outside the frozen 120-record structural domain is
accepted.  Full-domain V1 independent scientific certification remains
`PARTIAL`.

No radial solver was imported or called.  No protected radial, angular,
incident-wave, perturbation, reconstruction, observer/tetrad production,
legacy NP/pseudoinverse, figure, V1 artifact, threshold, V2.0 JSON,
`physics_spec.md`, or frozen equation-map file was modified.

### V2.1 frozen input hashes at terminal

The independent end rehash reproduced all required values:

```text
configs/phase6_v2_0_convention_contract_20260810.json
  1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517
configs/phase6_v2_0_selected_domain_20260810.json
  9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818
runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314/plan.json
  de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3
src/schwgw/numerics/radial_solver.py
  9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9
src/schwgw/numerics/conditioned_radial.py
  91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2
src/schwgw/numerics/scaled_tortoise_radial.py
  d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df
src/schwgw/numerics/adaptive_jost_radial.py
  3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896
src/schwgw/numerics/matching.py
  9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340
src/schwgw/numerics/physical_boundary_radial.py
  fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f
src/schwgw/numerics/boundary_conditions.py
  b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22
```

The frozen V2.1 prompt remained
`d5795b7888fee147eefa408cfdbfaef1771bd5d59a7ca0e3bac9aebce2754f55`.
All contract-listed V1 roots and their report/summary/manifest/records/source
ledger identities were also rehashed at publication start and end.

### V2.1 exact verification record

Runtime for Python checks:

```text
/opt/homebrew/bin/python3.14 = CPython 3.14.6
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/src
mpmath=1.4.1
```

Commands and exact results:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/bin/python3.14 -m pytest -q tests/unit/test_phase6_v2_mode_amplitudes.py tests/regression/test_phase6_v2_1_publication.py
  4 passed in 0.54s

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src /opt/homebrew/bin/python3.14 -m pytest -q tests/**/test_phase6*.py
  351 passed, 2 failed, 2 skipped, 2 warnings in 103.66s
  Both failures required the already-frozen absolute overlay-first PYTHONPATH;
  no source, test, threshold, or evidence was changed.

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<absolute overlay>:<absolute src> /opt/homebrew/bin/python3.14 -m pytest -q tests/**/test_phase6*.py
  353 passed, 2 skipped, 2 warnings in 105.77s

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<absolute overlay>:<absolute src> /opt/homebrew/bin/python3.14 -m pytest -q
  1539 passed, 119 skipped, 1 xfailed, 151 warnings,
  104 subtests passed in 457.28s

.venv/bin/python -m ruff format --check .
  existing repository baseline: 152 files would reformat

.venv/bin/python -m ruff check .
  existing repository baseline: 3 errors
  tests/unit/test_io_results.py:F841
  tests/unit/test_tablei_extraction.py:F401
  tests/unit/test_weyl_modes.py:F401

.venv/bin/python -m ruff format --check <five V2.1 Python files>
  5 files already formatted

.venv/bin/python -m ruff check <five V2.1 Python files>
  All checks passed

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<absolute overlay>:<absolute src> /opt/homebrew/bin/python3.14 -c <compileall src scripts tests with temporary pycache prefix>
  PASS

git diff --check
  PASS

git diff --check -- <V2.1 changed files>
  PASS
```

Fresh-root nonexistence, second-publish collision rejection, canonical reload,
manifest identities, modes/nlinks, 120 unique tuples, nonzero horizon
coefficients, and start/end hashes all passed.  The final executable-name
process check found no residual `python3.14`, pytest, SchWO, or Phase-6
numerical process.

### Historical V2.1 next action

Return this checkpoint to Root T0 and stop.  Do not dispatch T7 and do not
start V2.2 from T6.  Any next review or implementation step requires a new
Root T0 action under `docs/review_gate_liveness_protocol.md`.
