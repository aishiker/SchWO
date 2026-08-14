# Phase 6 V1 generic conditioning scan

## Purpose and non-goals

This runner provides the auditable generic float64 baseline and transition-
calibration layer for the frozen Phase-6 radial domain.  It is a mode-level
radial S-matrix scan, not a paper-figure reproduction gate.  It neither reads
nor renders Li figures, and it has no all-shards entry point.

The implementation is split between:

- `src/schwgw/validation/phase6_conditioning_scan.py`: frozen input binding,
  generic outer-boundary selection, solve-plan construction, result
  qualification, and separate numerical/convention budgets;
- `scripts/phase6_run_conditioning_scan_shard.py`: one-shard execution,
  exclusive artifact publication, immutable terminal protocol, strict resume,
  and shard aggregation.

No result from this single-backend layer is a global or strict physical PASS.
Acceptance remains per key, per observable, and per parameter domain.

## Frozen inputs

The loader accepts only the already frozen roots and exact identities below.

| Input | Count | SHA-256 |
| --- | ---: | --- |
| `D_union.jsonl` | 17,818 keys | `a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b` |
| `domain_contract.json` | — | `7ed99b905c3a1301d96101f357ab1fd9f4bc6e9a4922cb242d28e7cf06bb3bcf` |
| domain `manifest.json` | — | `f11d127e0bcfafa8f2fe24b2d3cec3e0cedc60f644d4285e6d52e53d8358d2d2` |
| `D_transition_calibration.jsonl` | 158 keys | `942fce669ee62f8194859f0481f7f3e926f4771176ec627d9013cda610dcb951` |
| `shard_inventory.jsonl` | 86 shards | `b652ceb41d0dfa3c25f10d246e98bc707721faf4d83b049b3410dc4ca0b4efff` |
| `execution_contract.json` | — | `25ad4b4e723edbd44651edaa63df415141de504b85288b12c2a6a973fcb420ab` |
| execution `manifest.json` | — | `1de9d445d888cbb5ddbf426cc062d2fb5128cad111437ce7d147df6e004aed48` |

Each invocation must select exactly one frozen `kM;sector` shard.  It cannot
alter either frozen contract.

## Generic baseline policy

For each key, preflight examines the frozen candidate sequence

`r_out/M = (300, 600, 1200, 2400, 4800, 9600, 19200)`.

The first candidate satisfying every raw gate is selected:

- `r_out / (sqrt(ell(ell+1))/k) >= 1.35`;
- `V(r_out) / k^2 <= 0.55` (a negative or non-finite probe fails closed);
- `k r_out >= 25`;
- no more than 4,096 estimated 5M outer integration segments;
- scaled two-column Jost condition number no larger than `1e8`;
- relative Jost determinant at least `1e-10`.

The probe uses the generic Regge-Wheeler or Zerilli potential and the
`jost_1_over_r` basis at order 160.  It contains no Q018 or other paper-specific
envelope.  If no frozen candidate passes, the key publishes
`UNSUPPORTED_FAIL_CLOSED`, makes zero radial-solver calls, and carries finite
unassessed uncertainty sentinels.

A supported key receives exactly one float64 baseline:

- required radius `40M`;
- `r_in - 2M = 1e-6 M`;
- `rtol=1e-10`, `atol=1e-12`;
- Jost order 160;
- generic conditioned backend, exact 2x2 matching, no legacy, NP, or
  pseudoinverse path.

The stored mode convention is unit incoming, `A_in=1`, with
`S_ell = -A_out/(-1)^ell`.  The complex amplitudes, log-amplitude/phase form,
required-radius state, flux residual, conditioning diagnostics, and exact
request identity are retained.

## Transition calibration

Only the frozen 158 transition keys receive the four calibration axes.  The
baseline occurs once, followed by nine distinct variations:

- two additional `r_in` nodes: `3e-6`, `3e-7`;
- two additional members of a three-point frozen `r_out` window;
- three additional Jost orders: 80, 120, 224;
- two additional tolerance pairs: `(1e-8,1e-10)` and
  `(1e-12,1e-14)`.

Thus a supported non-transition key makes one solve and a supported transition
key makes ten solves.  If all keys were supported, the exact upper plan would
contain 19,240 calls: 17,818 baselines plus 1,422 calibration variations.  The
runner performs no automatic retry.

## The 40M versus production finite-radius boundary

The `40M` state is only a generic required-radius, mode-level S-matrix check.
It is not evidence for the eight Fig.5/6 production points, whose radii are
approximately `30M` through `39.051M`.  Every key therefore records:

- `required_radius_radial_state`: at most `PARTIAL` at exactly `40M`;
- `production_finite_radius_states`: `NOT_ASSESSED`;
- `observer_response_claim`: `false`.

The actual eight-radius state evidence and Q018 selected-mode validation must
be produced by a separate observable-specific gate with its own worldline,
tetrad, numerical, and convention budgets.  This scan must never be cited as a
substitute for that evidence.

## Budgets and statuses

Every key checkpoint carries distinct numerical and convention budgets.  The
numerical budget contains the frozen execution-contract fields for `r_in`,
`r_out`, Jost order, ODE tolerance, arithmetic precision, axis limit, `lmax`,
and independent-backend difference.  Missing axes and the not-yet-run
independent backend use a finite maximum-float sentinel rather than a false
zero.  Transition-axis components are the maximum absolute complex-S change
from the one baseline.

The convention budget separately records observer, tetrad, polarization,
phase-origin, and total-scattered-definition uncertainty.  Unfrozen
conventions remain explicitly unassessed.  A baseline flux residual no larger
than `1e-6` may give the local `flux_conservation` observable a numerical PASS,
but the key as a whole remains `PARTIAL` because independent-backend and
absolute-convention closure are absent.  A failed baseline, failed ladder
node, or excessive flux residual fails closed.  `global_green_permitted` is
always false.

## Publication and resume protocol

The output root must be a fresh absolute direct path.  JSON artifacts are
canonical and are published by an O_EXCL staging file plus an exclusive
hardlink.  Existing paths are never replaced.  Published files are mode 0444;
the terminal root is mode 0555.

For a locally executed key, publication order is:

1. solver payload envelope;
2. key result, which binds the payload identity and checkpoint resume claims;
3. key checkpoint, with the final result identity;
4. exactly one key terminal.

Every key receives a terminal even after a post-allocation shard failure,
unless the filesystem itself rejects terminal publication; such protocol
errors are listed explicitly in the immutable top-level failure artifact.
The terminal distinguishes completed, unsupported/failed, post-solver,
post-artifact, not-started, strictly reused, and blocked-predecessor states.

Resume is intentionally conservative.  A predecessor must be a direct
immutable 0555 root with the exact same scientific context.  Reuse requires
the frozen validator to find a complete local PASS: key, latest attempt,
numerical budget, convention budget, every observable, and every ladder node
must all be PASS with exact artifact identities.  Current single-backend
PARTIAL results are therefore not silently reused or recomputed; the successor
publishes `BLOCKED_NONREUSABLE_PREDECESSOR` with zero solver calls.  A
`NOT_STARTED_DUE_TO_SHARD_FAILURE` predecessor key may be executed in the
successor.  A wholly fresh root is required to deliberately rerun non-PASS
keys.

## Invocation

After a separate review approves actual numerical execution, one shard can be
started as follows:

```bash
.venv/bin/python scripts/phase6_run_conditioning_scan_shard.py \
  --output-root /absolute/fresh/path \
  --shard-id 'kM=1;sector=odd'
```

An immutable predecessor can be supplied with `--resume-from`.  There is no
CLI switch for fake solver or selector injection; those paths require an
explicit in-process test mode and are marked
`TEST_ONLY_FAKE_INJECTION_NO_SCIENTIFIC_USE` in the run contract.

This implementation task did not execute that command, start a production
scan, create a formal evidence root, or rerun any paper figure.
