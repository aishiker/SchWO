# Phase 6 conditioning full-campaign index V1

## Scope

The conditioning campaign index is a read-only integrity and accounting layer
over the 86 frozen Phase-6 conditioning shards. It does not invoke a radial
solver, render a paper figure, or use Li-figure agreement as an acceptance
gate.

Publication is permitted only when the immutable shard roots reproduce the
frozen execution inventory exactly:

- 86 distinct `kM/sector` shards;
- 17,818 ordered and unique `D_union` keys;
- 16,048 production keys and 1,770 extension keys;
- 158 transition-calibration keys;
- the exact frozen domain, execution, and aggregation-v8 identities.

The index is evidence of the scientific calculations that actually ran. Its
release metadata is therefore fixed as:

- `scientific_evidence=true`;
- `science_executed=true`;
- `kernel_unit_test_only=false`;
- `contract_only=false`;
- `overall_state=FAIL` if any key is a scientific `FAIL`, otherwise
  `overall_state=PARTIAL`.

Neither state is a global GREEN claim.

## Independent shard reload

Every shard must be a direct mode-`0555` directory. Every child must be a
direct, canonical-JSON, mode-`0444`, nlink-one file. The validator reloads and
cross-checks:

1. `run_contract.json`, including exact shard/key plans, transition membership,
   generic conditioning policy, source hashes, runtime identity, and
   `paper_figure_runs=0`;
2. every key terminal, checkpoint, result, and payload envelope;
3. the payload-to-checkpoint projection, solver-call count, ladder nodes,
   failure reasons, and generic-backend provenance;
4. `shard_result.json` and `shard_checkpoint.json` as exact reductions of the
   reloaded key evidence;
5. `manifest.json` and all embedded artifact identities.

Only local `COMPLETED` and `COMPLETED_FAIL_CLOSED` terminals are eligible for
the V1 campaign. `COMPLETED_FAIL_CLOSED` means a completed scientific
fail-closed result; it is not counted as an execution failure. Missing,
not-started, blocked-resume, post-publication-failure, or otherwise incomplete
terminals reject campaign publication.

## Aggregation semantics

The index separately records:

- key and terminal status counts;
- numerical-budget status and per-component assessed/sentinel counts;
- convention-budget status and per-component assessed/sentinel counts;
- per-observable status counts;
- exact raw failure-reason counts;
- supported/unsupported outer-selection counts and selected `r_out` counts;
- transition-key, transition-node, and transition solver-call counts;
- runtime identity groups and implementation source SHA-256 hashes;
- the original immutable top-level identities of every shard.

`production_finite_radius_states` must remain `NOT_ASSESSED` for all 17,818
keys. The index also fixes `observer_response_claim=false`,
`global_green_permitted=false`, `paper_agreement_gate=false`, and
`li_figure_agreement_primary_gate=false`.

## Strict root mapping

There are two mutually exclusive input forms.

Explicit roots require exactly 86 arguments:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/src \
/opt/homebrew/bin/python3.14 \
/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/scripts/phase6_publish_conditioning_campaign.py \
  --output-root /absolute/fresh/campaign/root \
  --shard-root /absolute/root/for/shard-1 \
  --shard-root /absolute/root/for/shard-2
```

The `--shard-root` option must be repeated for all 86 roots. Argument order is
irrelevant because the validator remaps the roots through each immutable run
contract, then restores frozen shard order.

Alternatively, `--roots-parent` uses exact V1 names:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/src \
/opt/homebrew/bin/python3.14 \
/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/scripts/phase6_publish_conditioning_campaign.py \
  --output-root /absolute/fresh/campaign/root \
  --roots-parent /absolute/conditioning/roots/parent
```

For example, `kM=0.5;sector=odd` maps to
`v1_conditioning_scan_k0p5_odd_v1_20260808_py314`. Within the
`v1_conditioning_scan_` namespace, missing or extra names are rejected.
Unrelated evidence roots outside that namespace are ignored.

## Publication protocol

The output root must be a fresh absolute direct path. Validation of all 86
inputs occurs before allocation. Publication uses O_EXCL staging files and
exclusive hard links, then seals:

- `conditioning_campaign_index.json` as mode `0444`;
- `manifest.json` as mode `0444`;
- the campaign root as mode `0555`.

The sealed root is immediately reloaded and the full index is rebuilt from the
86 original shard roots. Existing paths are never replaced. This implementation
does not itself publish a formal campaign root; publication waits until all 86
shards have been sealed.
