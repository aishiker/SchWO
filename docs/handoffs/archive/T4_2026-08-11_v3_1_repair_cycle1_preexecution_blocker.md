# T4 V3.1 repair cycle 1 pre-execution blocker

Date: 2026-08-11

## Terminal state

```text
BLOCKED / V3.1 REPAIR CYCLE 1 MANDATORY ROUTE-A SENTINEL FAILED
```

Formal T7 approved the bounded repair package for execution, not as a
scientific result. T4 rehashed the five immutable package members and then ran
the mandatory non-authoritative `/tmp` sentinel for the exact formerly failed
Route-A key before creating any official root.

The frozen key was `kM=0.005`, odd parity, `ell=2`, required radius `40M`,
with `r_out_base=489.8979485566356`. The complete frozen 20-node graph produced
8 PASS and 12 FAIL records in 6.093446124927141 seconds:

- all eight nodes at outer-radius multipliers 4 and 8 passed;
- the three `r_in_eps` nodes at multiplier 1 failed;
- multiplier-1 Jost orders 80, 120 and 200 failed;
- all four multiplier-2 Jost nodes failed;
- both non-baseline tolerance nodes at multiplier 1 failed.

The failures were exact protected-API exceptions:

- `scaled-tortoise Jost matching inputs are invalid` (7 records);
- `scaled-tortoise incoming Jost coefficient is unresolved` (5 records).

The frozen baseline node itself failed. Selecting the successful multiplier-4
or multiplier-8 nodes would change the frozen node policy and would be a
result-dependent favorable selection, which is forbidden. Closing the
mandatory sentinel therefore requires either a protected radial-backend change
or a newly reviewed node-policy change. Neither is authorized in repair cycle
1.

## Durable diagnostic boundary

- sentinel: `/tmp/schwo_v31_repair_cycle1_route_a_20node_sentinel.json`
- sentinel SHA-256:
  `9cfc3f91d722d212a7dfc22ec3746b27d300ce462ca874e0131986e4f39fa892`
- stderr: `/tmp/schwo_v31_repair_cycle1_route_a_20node_sentinel.stderr`
- stderr SHA-256:
  `31bdbfa60f243467643d168b6df4e96b7667ab30eff6d1557a17f9e7168e1333`
- stderr contains the observed NumPy overflow warning from the failed-node
  evaluation.

The JSON explicitly records `scientific_evidence=false`,
`scientific_acceptance=false` and `official_root_created=false`.

## Closure and nonclaims

- No `v3_1_mode_greybody_r2_*` official root was created.
- Route B AP, Route C external, synthetic publication and runtime/disk gates
  were not launched because the earlier mandatory Route-A gate failed.
- The seven protected radial files, five package files and both immutable r1
  roots were not modified.
- No related process, writer, lock or staging transient remains.
- No V3.1 PASS, V3.2 authorization, independent review or global GREEN is
  claimed.

Root T0 must decide whether a separately reviewed repair cycle 2 may authorize
the required protected-backend or frozen-node-policy change.
