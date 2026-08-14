# T7cl — Relocated Benchmark-Identity Binding Repair Review

Work only in existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` as an independent read-only
reviewer. Do not create a task, subagent, proxy, or descendant.

## Required Reading

Fully read:

- `project.md`, `status.md`, current T0/T4/T7/T8 handoffs;
- frozen T4ae, T4af, T4ag, and T4ah design/plan/prompts;
- the exact four-file T4ai candidate supplied by root T0;
- the complete consumed T4ah witness preparation, request, durable run,
  streams, producer control audit, independent pair audit, output pair, and
  official-audit start-gate failure;
- frozen T4ah driver/preflight/runtime/complete-290 evidence;
- frozen scientific runner, especially `BenchmarkIdentity`,
  `_gate_identity()`, `_benchmark_identity()`, `_identity_payload()`, and
  official audit behavior;
- canonical/legacy/golden references and current process/transient state.

Verify candidate commit, parent, ref, exact four added paths,
commit/worktree blobs, file sizes, SHA-256 values, and `git diff --check`.
Review only that exact identity.

## Independent Review

Check that:

1. The T4ah producer is exactly exit0/no-signal/empty-stderr/reaped/PG-empty
   with valid durable records and immutable evidence.
2. Its 22 scientific arrays are independently bitwise identical to
   canonical, legacy, and golden references, but no completed witness is
   claimed because official audit never launched.
3. The authorization is consumed; the isolated pair cannot be reused,
   audited under a changed driver, or promoted downstream.
4. The expected `46403a00...6c48` and observed `db7937fa...69b8` identities
   are independently reconstructed using the runner's exact `_json_safe`
   plus `json.dumps(..., sort_keys=True, separators=(",", ":"),
   allow_nan=False)` canonical JSON, including the default
   `ensure_ascii=True`, followed by UTF-8 encoding.
5. The seven-field payloads differ only in `gate_sha256`.
6. Primary/detached gate manifests `101823bb...4eb4` and
   `b0c9b521...8a09` differ only because the five exact gate records contain
   different absolute roots; all five repository paths, hashes, and sizes
   are otherwise exact.
7. Table-I input manifest `6c20e1d5...4010` and every non-gate benchmark
   component remain exact.
8. The proposed prelaunch derivation is deterministic for an arbitrary
   exact detached root and binds a complete payload, not an observed or
   allowlisted arbitrary digest.
   Independently exercise a detached root with non-ASCII path components:
   runner and proposed derivation bytes/digests must be identical, while an
   otherwise identical `ensure_ascii=False` variant must differ and be
   rejected.  ASCII-only root restriction is not an acceptable repair.
9. Producer start/terminal, NPZ metadata, JSON sidecar, durable records,
   producer audit, and matching official audit are all required to equal
   the one prelaunch-derived binding.
10. Producer and official audit must use the same detached root/runtime and
    independently derive the same identity.
11. Matrix/canonical context still requires only the fixed primary identity;
    detached identity cannot leak into matrix acceptance.
12. Negative tests cover root/path/content/payload/phase/alias/link/
    writeability/post-prelaunch drift and producer/audit mismatch.
13. Phase A is exact Python 3.14, zero-science, includes every old test, and
    stops at a fresh root-T0 checkpoint.
14. The repair does not modify runner, implementation, runtime, complete
    290 inputs, config, science, thresholds, canonical pairs, or downstream
    semantics.
15. A new witness requires a new root-T0 authorization and performs a new
    full producer plus audit; no reuse or implicit retry.
16. T4 code uses sol/high only and no new agent.

Freshly verify current refs, primary/exact-fourteen, driver/preflight/
runtime/HOLD evidence, output pair, canonical hash/stat/inodes, remaining
absent units, external object, and zero unexpected process/transient state.

Any arbitrary-identity acceptance, incomplete payload binding, path-only
comparison without byte/hash checks, phase confusion, reuse, implicit retry,
Unicode-root serialization drift, scientific criterion change, or identity
drift is a blocker.

## No Writes Or Dispatch

Do not edit files, artifacts, environment, status, handoffs, or candidate.
Do not run preflight, witness, official audit, matrix, or science. Do not
dispatch T4/T7ch/T8 or perform GitHub actions.

## Exact Decision

Return to root T0 with exactly one:

```text
REVIEW GREEN / T0 RELOCATED BENCHMARK IDENTITY REPAIR APPROVED
REVIEW YELLOW / T0 RELOCATED BENCHMARK IDENTITY CHANGES REQUIRED
REVIEW RED / T0 RELOCATED BENCHMARK IDENTITY REPAIR INVALID
```

Then report exact candidate identity, independent evidence, and bounded
blockers if any.
