# T7 Archived Handoff — Pre-T7bx Units Metadata Repair Review

Last updated: 2026-07-15

Thread: T7bw, `Delta(kM)=0.1` nine-frequency risk-pilot independent review.

## Exact Decision

```text
REJECT RED / DELTA0P1 RISK PILOT INVALID
```

The numerical arrays are converged, finite, correctly checkpointed, and
provenance-consistent, but the artifact violates the frozen minimum metadata
contract: no active per-frequency sidecar, aggregate sidecar, ledger, audit,
or manifest records units. Frozen design Section 8.3 requires metadata to
record exact ordering **and units**, and T7bw check 3 says to require units.
Under the prompt's severity rule this is an invalid artifact and therefore
RED, not a nonblocking qualification. Independently, every one of the 224
observed adjacent unwrapped phase steps is finite and strictly below `pi/2`,
while the frozen magnitude-dominance criterion fails for 38 records. The
latter result alone would require targeted `0.05` evidence, but it cannot
downgrade an artifact-contract RED to YELLOW. T7bw performs no repair.

The pre-T7bw T7bv handoff is archived at:

```text
docs/handoffs/archive/T7_2026-07-14_pre_t7bw_delta0p1_pilot_review.md
```

## Independent Nine-Check Result

1. **PASS — commit/scope.** Commits `c068868` and `47c3d63` together change
   exactly the five frozen T8an implementation/test paths. The latter fixes
   only point-local radial-cache domain reuse and regenerates all nine active
   transactions under the final contract. No radial solver, scattering
   formula, visualization, config, fixture, or unrelated path is in scope.
2. **PASS — gates/source hashes.** The accepted T8aj triplet and the T4z/T7bv
   classification, oracle, and preflight hashes all match their frozen
   values. Selected radial/scattering/risk-envelope source hashes and final
   Git commit provenance also match.
3. **FAIL — units metadata contract.** Direct loading,
   without T8an helpers, verifies exact frequency/point ordering, shapes,
   actual dtypes, masks, finiteness, `lmax` windows, final pairs, deltas,
   warnings, and adapter counts. All masks are true; maximum final-pair deltas
   are `6.136118112992297e-11` plus and `5.492389935680416e-10` cross, below
   `1e-4`. However, a direct recursive search finds no units record in any
   active sidecar, ledger, audit, or manifest. The frozen convention would
   make the intended units inferable (`kM`, `F`, and deltas dimensionless;
   coordinates/radii in `M`; angles/phases in radians; `lmax` dimensionless
   integer; masks Boolean), but inferability is not the required explicit
   artifact metadata. This contract failure determines the exact RED.
4. **PASS — checkpoint/provenance.** The independently reconstructed contract
   hash is `92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9`.
   There are exactly nine complete ledger entries, 18 active per-frequency
   files, and 22 manifest records; no `.tmp` exists. The quarantined old-
   contract transactions are excluded from the active ledger and manifest.
5. **PASS — aggregate identity.** Independent stacking of every per-frequency
   NPZ array is exact (`np.array_equal`) to the aggregate arrays. Aggregate
   unwrapped phases equal fresh `np.unwrap`; embedded JSON and sidecars agree
   apart from the sidecar's required NPZ hash.
6. **PASS — five local sequences.** T7bw directly combined accepted T8aj
   endpoints with pilot rows into exactly `[0.3,0.4,0.5]`,
   `[0.75,0.8,0.9,1.0]`, `[1.5,1.6,1.7,1.75]`,
   `[2.75,2.8,2.9,3.0]`, and `[3.75,3.8,3.9,4.0]`. Fresh arrays reproduce
   the saved sampling audit, which was used only as a comparison target.
7. **PASS — observed phase criterion.** All 224 steps are finite, have spacing
   `<=0.1`, and satisfy `abs(Delta unwrapped phase)<pi/2`.
8. **FAIL — magnitude dominance.** Using exactly
   `|a-b|/max(1,|a|,|b|)`, 38 refined records exceed their same-point,
   same-component accepted coarse endpoint step by more than `2e-15`.
   Exact failures and the evidence proposal are recorded below.
9. **PASS — tests/isolation.** Focused tests, Ruff, and the full suite pass.
   The required forbidden-output query is empty. T7bw generated no full grid,
   `0.05` scan, plot, fixture, paper candidate, repair, or new artifact.

## Exact Magnitude-Dominance Failures

The following list names every failed interval and its exact point/component
membership; together these groups contain 38 records.

- Sequence `[0.3,0.4,0.5]`: plus `[0.3,0.4]`
  `far_axis_x20_z30`; plus `[0.4,0.5]` `far_axis_x20_z30`; cross
  `[0.4,0.5]` `far_axis_x25_z30`.
- Sequence `[0.75,0.8,0.9,1.0]`: plus `[0.8,0.9]`
  `far_axis_x25_z30`; plus `[0.9,1.0]` `near_axis_x3_z30`; cross
  `[0.8,0.9]` and `[0.9,1.0]` `far_axis_x25_z30`.
- Sequence `[1.5,1.6,1.7,1.75]`: plus `[1.6,1.7]`
  `far_axis_x25_z30`; cross `[1.5,1.6]` `far_axis_x10_z30`; cross
  `[1.6,1.7]` `far_axis_x10_z30`, `far_axis_x15_z30`; cross
  `[1.7,1.75]` `far_axis_x10_z30`.
- Sequence `[2.75,2.8,2.9,3.0]`: plus `[2.8,2.9]`
  `far_axis_x20_z30`, `far_axis_x25_z30`; cross `[2.75,2.8]`
  `near_axis_x2_z30`, `far_axis_x15_z30`, `far_axis_x20_z30`,
  `far_axis_x25_z30`; cross `[2.8,2.9]` `far_axis_x15_z30`; cross
  `[2.9,3.0]` `near_axis_x2_z30`, `far_axis_x10_z30`,
  `far_axis_x15_z30`, `far_axis_x25_z30`.
- Sequence `[3.75,3.8,3.9,4.0]`: plus `[3.75,3.8]`
  `near_axis_x0_z30`, `far_axis_x25_z30`; plus `[3.8,3.9]`
  `near_axis_x0_z30`, `near_axis_x2_z30`, `far_axis_x25_z30`; plus
  `[3.9,4.0]` `near_axis_x0_z30`, `far_axis_x25_z30`; cross
  `[3.75,3.8]` `near_axis_x0_z30`; cross `[3.8,3.9]`
  `near_axis_x0_z30`, `near_axis_x3_z30`, `far_axis_x20_z30`,
  `far_axis_x25_z30`; cross `[3.9,4.0]` `near_axis_x0_z30`,
  `far_axis_x20_z30`, `far_axis_x25_z30`.

If a separately authorized repair and independent re-review later resolve the
artifact-contract RED, the scientific magnitude result identifies these
missing half-step frequencies for a possible frozen YELLOW evidence design:

```text
kM = [0.35, 0.45, 0.85, 0.95, 1.55, 1.65, 2.85, 2.95, 3.85, 3.95]
```

This analysis targets all selected `0.1` subintervals. It is not authorization
to run them, and it does not erase the
already observed failures on three existing `0.05` edge intervals:
`[1.7,1.75]`, `[2.75,2.8]`, and `[3.75,3.8]`. A future T0 design must state
how those existing edge failures and new midpoint evidence will be interpreted;
T7bw invents no additional threshold.

## Phase Maxima And Magnitude Summaries

For each sequence/component, the table gives the largest observed phase step,
then the point/interval with maximum magnitude total variation, and finally
the largest single relative magnitude step with its accepted coarse comparator.

| Sequence | Component | Max phase step and attribution | Max magnitude total variation | Largest relative magnitude step; coarse comparator |
|---|---|---|---|---|
| `0.3..0.5` | plus | `1.4363184904108022`, `far_axis_x25_z30`, `[0.3,0.4]` | `0.3730514300220806`, `far_axis_x15_z30` | `0.2194724507029765`, `far_axis_x25_z30`, `[0.4,0.5]`; `0.33783922604352745` |
| `0.3..0.5` | cross | `0.488198419765648`, `far_axis_x15_z30`, `[0.3,0.4]` | `0.9537053545502086`, `far_axis_x25_z30` | `0.3972875049197165`, `far_axis_x25_z30`, `[0.4,0.5]`; `0.3131500025131307` |
| `0.75..1.0` | plus | `0.6073276825949729`, `far_axis_x20_z30`, `[0.9,1.0]` | `0.44355892725492485`, `far_axis_x15_z30` | `0.2267316114768957`, `far_axis_x15_z30`, `[0.8,0.9]`; `0.44355892725492485` |
| `0.75..1.0` | cross | `0.6896552894525365`, `far_axis_x20_z30`, `[0.75,0.8]` | `1.7643213800514306`, `far_axis_x15_z30` | `0.6615944508855898`, `far_axis_x15_z30`, `[0.9,1.0]`; `0.8039700767407513` |
| `1.5..1.75` | plus | `0.4302742816623899`, `far_axis_x25_z30`, `[1.7,1.75]` | `0.4224074128103431`, `far_axis_x20_z30` | `0.2166097380541815`, `far_axis_x20_z30`, `[1.6,1.7]`; `0.23278297717135887` |
| `1.5..1.75` | cross | `1.2409224252368016`, `far_axis_x15_z30`, `[1.5,1.6]` | `1.3553974717771355`, `far_axis_x10_z30` | `0.6299277545521185`, `far_axis_x10_z30`, `[1.5,1.6]`; `0.0955419626728986` |
| `2.75..3.0` | plus | `0.8380606439701611`, `far_axis_x20_z30`, `[2.9,3.0]` | `0.6713961657417713`, `far_axis_x15_z30` | `0.30461099904819894`, `far_axis_x20_z30`, `[2.8,2.9]`; `0.26857031871723847` |
| `2.75..3.0` | cross | `0.38649341622404687`, `near_axis_x2_z30`, `[2.8,2.9]` | `0.8204983070576386`, `near_axis_x3_z30` | `0.3043194075134724`, `far_axis_x25_z30`, `[2.75,2.8]`; `0.09496813519694003` |
| `3.75..4.0` | plus | `0.741854306800739`, `far_axis_x15_z30`, `[3.9,4.0]` | `0.6360174003321006`, `far_axis_x10_z30` | `0.27161938497049964`, `far_axis_x15_z30`, `[3.8,3.9]`; `0.4819631483988341` |
| `3.75..4.0` | cross | `0.556514438285804`, `far_axis_x20_z30`, `[3.8,3.9]` | `0.9276805784517359`, `near_axis_x0_z30` | `0.3453402021420441`, `far_axis_x10_z30`, `[3.9,4.0]`; `0.6796263787285783` |

## Interior Magnitude Extrema

There are 51 strict interior extrema. Equal-frequency extrema below are
grouped by type; omitted point/component combinations have no strict interior
extremum.

- `0.3..0.5`: plus minimum at `0.4` for `far_axis_x20_z30`; cross maximum
  at `0.4` for `far_axis_x25_z30`.
- `0.75..1.0`: plus minimum at `0.8` for `near_axis_x3_z30`, and maxima at
  `0.9` for `near_axis_x3_z30`, `far_axis_x25_z30`; cross minimum at `0.8`
  for `near_axis_x3_z30`, maxima at `0.9` for `near_axis_x3_z30`,
  `far_axis_x20_z30`, and minimum at `0.9` for `far_axis_x25_z30`.
- `1.5..1.75`: plus maxima at `1.6` for `far_axis_x10_z30`,
  `far_axis_x15_z30`, `far_axis_x20_z30`, `far_axis_x25_z30`, and minimum at
  `1.7` for `far_axis_x25_z30`; cross minima at `1.6` for
  `far_axis_x10_z30`, `far_axis_x15_z30`, and maxima at `1.7` for
  `far_axis_x20_z30`, `far_axis_x25_z30`.
- `2.75..3.0`: plus minima at `2.8` for `near_axis_x0_z30`,
  `near_axis_x1_z30`, `far_axis_x10_z30`, maxima at `2.8` for
  `near_axis_x3_z30`, `far_axis_x25_z30`, maximum at `2.9` for
  `near_axis_x1_z30`, and minima at `2.9` for `near_axis_x3_z30`,
  `far_axis_x15_z30`, `far_axis_x20_z30`; cross minima at `2.8` for
  `near_axis_x0_z30`, `near_axis_x1_z30`, `near_axis_x2_z30`, and maxima at
  `2.9` for `near_axis_x1_z30`, `far_axis_x10_z30`, `far_axis_x15_z30`,
  `far_axis_x20_z30`, `far_axis_x25_z30`.
- `3.75..4.0`: plus maximum at `3.8` for `near_axis_x0_z30`, minima at `3.8`
  for `near_axis_x1_z30`, `near_axis_x3_z30`, maxima at `3.9` for
  `near_axis_x1_z30`, `near_axis_x2_z30`, `far_axis_x20_z30`, and minimum at
  `3.9` for `far_axis_x25_z30`; cross maxima at `3.8` for
  `near_axis_x0_z30`, `near_axis_x3_z30`, `far_axis_x20_z30`,
  `far_axis_x25_z30`, minimum at `3.8` for `near_axis_x1_z30`, maximum at
  `3.9` for `near_axis_x1_z30`, and minima at `3.9` for
  `near_axis_x3_z30`, `far_axis_x20_z30`, `far_axis_x25_z30`.

## Accepted Hashes

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  accepted T8aj NPZ
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  accepted T8aj JSON
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  accepted T8aj manifest
ee051831e1da7ebb250cab37d7da3a64d8a57298b445577f238d9cefae319d54  T4z classification
8f6d23da0894d0abfb42867bf911b9da95090ad5293bc76289daf4522e4067f9  T4z oracle validation
59e99ade6993eab6d570f8a2ad18f0778595f7309fbb87fbf1edf32903b80968  T4z/T7bv preflight
79d4c0f596650dcfb4d63c7e40758ea4afa82d2fe0e0cd3de5aa088bbbfd5ccd  T8an ledger
2e0a9fee1b6729466affd4c5f7f6e86c96e696e20882c9f4ad52ae3792d82957  T8an aggregate NPZ
2a9aa472e64747047cb28de90912eecf138b28884d87e8b8219e78d99482772f  T8an aggregate JSON
461d040a180dfa8e5a743967285e67f8b682f8f67607f1c0c7a5c8ab2399d7bd  T8an sampling audit
120ccd8f11e681bc6d2b3054bd7522ef331a282421f7661dd7888c993b052212  T8an manifest
```

## Fresh Verification

- Direct transaction/provenance/aggregate audit:
  `T7BW_DIRECT_TRANSACTION_PROVENANCE_AGGREGATE_AUDIT=PASS`.
- Independent five-sequence reconstruction:
  `T7BW_FIVE_SEQUENCE_RECONSTRUCTION=PASS`.
- Focused pytest: `11 passed in 0.77s`.
- Ruff: `All checks passed!`.
- Full pytest: `615 passed, 117 skipped, 1 xfailed, 101 warnings, 81 subtests
  passed in 319.20s`.
- Required forbidden-output command: empty.

## Review-Only Changed Paths And Boundary

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-14_pre_t7bw_delta0p1_pilot_review.md`

T7bw modified no implementation, test, script, config, T4/T8 handoff, or
artifact. It did not repair the missing metadata or start full production,
targeted `0.05` computation, plots, fixtures, or paper-style work. Fresh
document/scope verification passed, and the exact RED was successfully sent
to T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636`.
