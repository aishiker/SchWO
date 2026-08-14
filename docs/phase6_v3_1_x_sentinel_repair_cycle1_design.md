# Phase 6 V3.1-X sentinel bounded repair cycle 1

Date: 2026-08-13

Gate: `phase6_v3_1_x_external_direct_route_v1`

Repair ID: `phase6_v3_1_x_sentinel_argv_repair_cycle1_v1`

State at freeze: `FAIL / BOUNDED REPAIR 1 PACKAGE CANDIDATE`

This is the first bounded repair of the distinct V3.1-X sentinel gate.  It is
not V3.1-U repair cycle 3, it does not reuse the failed sentinel, and it does
not change a numerical method, domain, precision, threshold, convention or
protected radial source.

## Frozen failure and cause

The one-use sentinel root
`runs/phase6/classic_scattering/v3_1_x_external_direct_sentinel_v1_20260813T055002Z_py314`
is immutable `FAIL`, nonresumable and nonretryable.  Its dispatch was consumed
exactly once.  The first child used the reviewed five-element process argv

```text
WolframKernel -script WLS REQUEST OUTPUT
```

and returned `64`; its exact stdout was
`usage: phase6_v3_1_x_bhpt_direct.wls REQUEST OUTPUT`.  No request was
imported, no BHPT source was loaded and no numerical integration ran.  The
remaining 34 planned calls were not started.

Formal T7 classified the sole class-A blocker as
`v31x-sentinel-wls-scriptcommandline-contract-mismatch`.  The reviewed WLS
reads `$ScriptCommandLine`, but WolframKernel 14.3 exposes the actual launch
vector through `$CommandLine`; the actual zero-science probe returned

```text
$ScriptCommandLine = {}
$CommandLine = {WolframKernel, -script, WLS, REQUEST, OUTPUT}
```

The probe is diagnostic only and is not scientific evidence.

## Exact repair

Exactly four files may change:

```text
scripts/phase6_v3_1_x_bhpt_direct.wls
src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
tests/unit/test_phase6_v3_external_direct.py
tests/regression/test_phase6_v3_external_direct_publication.py
```

The WLS must accept only the exact five-element `$CommandLine` shape whose
first element is the frozen WolframKernel path, second is `-script`, third is
the frozen WLS path, and fourth/fifth are the request/output paths.  Missing,
extra, reordered or alternate forms fail before request import.  No fallback
to `$ScriptCommandLine`, `$CommandLine` slicing, environment-selected parsing,
alternate launcher, `wolframscript`, or shell wrapper is permitted.

The producer change is control-plane only: its fixed implementation-review
path must name the predeclared future archive

```text
docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_implementation_delta_review.md
```

and must require the exact repair verdict, package/review/failure authorities,
and all six live post-repair implementation hashes.  The future archive hash
must remain supplied by a later Root-T0 dispatch; it may not be hard-coded.

The two test files must cover the exact positive shape, all negative shapes,
old-YELLOW/old-bridge/arbitrary review rejection, exact six-hash binding,
environment/argv/cwd/executable/launcher/replay guards, and the existing
sentinel/official publication invariants.

## Zero-science handshake

Formal T4 must run one real-kernel argv handshake using a temporary request
path that is guaranteed absent and a temporary output path that is absent.
With the exact reviewed five-element launch, the repaired WLS must pass argv
parsing and fail at the next guard with exactly
`request must exist and output must be absent` and exit `73`.  This proves the
argv boundary only: the request is never imported, an overlay is never made,
BHPT is never loaded and a solver is never called.

Negative handshakes may use missing/extra/reordered arguments but must also
stop before request import.  Temporary probe files must be removed after the
test and never enter a formal evidence root.

## Frozen invariants and liveness

- The V3.1-X package, exact 23-key Route-C inventory, 35-call sentinel graph,
  161-call official graph, six overlays and direct NumericalIntegration
  method remain unchanged.
- All precision schedules, route-admission criteria, V3.0 authorities,
  16 thresholds, five certificates and seven protected radial identities
  remain unchanged.
- The failed sentinel dispatch/root are forbidden for all future use.
- Package review does not consume repair cycle 1.  A formal implementation
  delta review that accepts the four-file repair consumes cycle 1 and permits
  only Root T0 to create one different dispatch for one fresh absent sentinel
  root.
- V3.1-X permits at most two bounded repairs.  No official dispatch, V3.2 or
  global GREEN follows from this package or its implementation review.

## Required verification

Formal T4 must run the focused unit/regression suites under exact CPython
3.14 and the frozen mpmath overlay, the real-kernel zero-science handshake,
Ruff check/format, in-memory compile and four-path `git diff --check`.  It must
rehash all package, source, runtime and protected authorities at start/end and
report exact before/after hashes and zero science calls.

