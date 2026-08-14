# Phase 6 V2 selected-domain closeout

Date: 2026-08-11

## Terminal checkpoint

```text
CHECKPOINT / V2 SELECTED-DOMAIN RELEASE CONTROL-PLANE REPAIR V2 FROZEN
```

This is a bounded release/certification aggregation. It adds no formula,
threshold, convention, parameter, route, radial solve, angular sum, observer
response or scientific measurement. The exact release domain is the accepted
30 radial keys, `m=-2,+2`, and the plus/cross unit incident columns, for 120
ordered records. Extrapolation to the 17,818-key full domain is forbidden.

## Immutable authority

The sole V2 selected-domain release root is:

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

The root is direct `0555`; all five files are direct regular `0444`/nlink1
files. Exclusive creation, fsync, in-place reload and a distinct temporary-copy
reload passed. Exactly one matching V2 selected release root exists.

The predecessor
`runs/phase6/asymptotic_waveform/v2_selected_release_v1_20260811T081608_py314`
remains immutable and byte-for-byte unchanged. Its manifest/ledger/report/
source-map/summary hashes remain `1500c198...27d3f` / `8bbc4d09...ba49` /
`44b6e503...fc0c` / `bc459ba0...08c7` / `25dcc333...45cb`. It is now
superseded evidence and forbidden as current authority. The v2 ledger and
summary are byte-identical to v1; only report/source-map/manifest provenance
changed.

## Certificate inventory

| certificate | state |
|---|---|
| `V2_MODE_AMPLITUDE_NORMALIZATION` | `PASS` |
| `V2_TOTAL_FREE_SCATTERED_DECOMPOSITION` | `PASS` |
| `V2_MASTER_ROUTE_WAVEFORM` | `PASS` |
| `V2_CURVATURE_ROUTE_WAVEFORM` | `PASS` |
| `V2_EXTERNAL_ROUTE_WAVEFORM` | `PASS` |
| `V2_ROUTE_CROSSCHECK` | `PASS` |
| `V2_INFINITY_FLUX` | `PASS` |
| `V2_HORIZON_FLUX` | `PASS` |
| `V2_RADIAL_FLUX_BALANCE` | `PASS` |
| `V2_WAVEFORM_CURRENT_FLUX_EQUIVALENCE` | `PASS` |
| `V2_ABSOLUTE_PHASE_CONVENTION` | `PARTIAL` |
| `V2_SELECTED_DOMAIN_RELEASE_POLICY` | `PASS` |

Every certificate carries its exact domain, separate numerical and convention
uncertainty budgets, evidence-root/file hashes, independence boundary,
nonclaims, protected radial hashes, and the V2.0 convention/domain authority
hashes. States were derived fail-closed by native reload of the immutable V2.1,
V2.2-v3 and V2.3-v2 roots; the release publisher cannot upgrade a source.

## Read-only V2.3 control-plane compatibility repair

During the required full-suite run, historical V2.3 reconstruction tests and
the `check-only` command correctly rejected the now-advanced live T7 handoff
because they still requested the original execution-time handoff byte identity.
Root T0 classified this as a bounded control-plane false positive.

The repair changes only the historical read-only callers to pass
`require_dispatch_review_identity=False`. The actual V2.3 publication path
continues to use the default `True`; a dedicated regression proves this gate
remains fail-closed. `DISPATCH_T7_SHA256`, the V2.3 validation/science module,
all formulas and records, and every published V2.3 root remain unchanged. The
V2.3 science/validation module SHA-256 remains
`dd14b7910890ff752c34e9fae55147a2ad08e33777b07a13919737342f1eaa8a`.

## V2.4 live-handoff control-plane repair

The pre-T7 independent audit found the same liveness trap in V2.4's own
historical `check-only` and unit reconstruction fixture. Those two read-only
callers now explicitly pass `require_dispatch_review_identity=False`.
`validate_published_selected_release` already used that historical-reload
setting and required no change.

The actual V2.4 publisher still calls the start and end gates with the default
strict `True`. A regression simulates a legally advanced live handoff and
proves both properties: the historical reconstruction succeeds while the
strict path rejects the dispatch-byte mismatch; a separate publish-path probe
proves no output root is created before strict gate acceptance.

`DISPATCH_T7_SHA256`, certificate/science derivation, all thresholds,
conventions, domains, predecessor artifacts and V1 release bytes are
unchanged. The current repair-owned identities are:

| path | SHA-256 |
|---|---|
| `src/schwgw/validation/phase6_v2_selected_release.py` | `b6f7c0055d92bf663917a30144793441dc590d6388d56b19f37e210f1bcc54d7` |
| `scripts/phase6_v2_4_publish_selected_release.py` | `7bcb29fcb2a811bc7fb353f59ac42a0ce1293a6a829066136f7b048281af4e7c` |
| `tests/unit/test_phase6_v2_4_selected_release.py` | `b84e7795cd2e449b8f121d139047ea443d02a714e1c823bcf75670d521370f98` |
| `tests/regression/test_phase6_v2_4_release_publication.py` | `600016d04bc87ce99e1e55e14a9bb6095b7e9709f5a13a3befac8197211930fb` |

## Verification

Exact CPython `3.14.6`, mpmath `1.4.1`, the absolute overlay-first
`PYTHONPATH`, and `PYTHONDONTWRITEBYTECODE=1` were used.

- targeted V2.4 release tests: `12 passed`;
- affected V2.3/V2.4 control-plane tests: `27 passed`;
- all Phase-6/V2 tests: `393 passed, 2 skipped, 2 warnings`;
- full suite: `1579 passed, 119 skipped, 1 xfailed, 151 warnings, 104 subtests passed`;
- four repair-owned Python files: Ruff format/check PASS;
- compileall, repository `git diff --check`, source/protected start/end hashes,
  process and collision checks, permissions, manifest, immutable in-place reload
  and temporary-copy reload: PASS.

Repository-wide Ruff retains the pre-existing out-of-scope baseline of 152
files that would be reformatted and three lint findings. No out-of-scope file
was modified to address that baseline.

## Claim ceiling and nonclaims

The machine summary sets `global_status=null`,
`global_green_permitted=false`, `claim_status=PARTIAL`,
`absolute_phase=PARTIAL`, `full_domain_v2=NOT_ASSESSED`, and
`radial_solve_count=0`. It does not certify global SchWO validation, a complete
angular waveform, finite-radius observer response, Li-figure equivalence, or
full-domain V2. V1 full-domain independent scientific certification remains
`PARTIAL`.
