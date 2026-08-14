# Formal T6 prompt — V3.1-X repair-cycle-2 source-ledger implementation

Use the existing formal T6 task `019f5faf-bfdd-7aa3-80a9-1c9829daecac`.
This prompt activates only after formal T7 accepts the exact repair-cycle-2
package.  It is the final bounded V3.1-X science repair (`2/2`).

Read completely and rehash: `project.md`; `status.md`; the review-gate
liveness protocol and verdict template; the V3.1-X package/design/review
chain; both immutable failed sentinel roots; the attempt-0002 terminal review;
the repair-cycle-2 design, package and formal package-review archive; this
prompt; and the future T7 implementation-delta prompt.

Also bind the formal future micro-terminal prompt
`docs/prompts/phase6_t7_v3_1_x_source_load_micro_sentinel_terminal_review.md`.
The producer must require its fixed future archive path and a later
dispatch-supplied digest.  The only accepted future success tokens are:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X SOURCE-LOAD MICRO SENTINEL SUFFICIENT FOR ONE-USE FULL SENTINEL DISPATCH
```

The terminal failure envelope is exactly `ADVANCE_DECISION: ESCALATE`,
`CLAIM_STATUS: FAIL`, `GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED`.

Modify exactly these five paths and no others:

1. `scripts/phase6_v3_1_x_bhpt_direct.wls`
2. `src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py`
3. `scripts/phase6_v3_1_x_external_direct.py`
4. `tests/unit/test_phase6_v3_external_direct.py`
5. `tests/regression/test_phase6_v3_external_direct_publication.py`

The direct physics core, V3.0 authorities, source snapshot, method, graph,
precision, thresholds, convention, seven protected radial files and all
existing evidence/dispatch bytes are frozen.

Implementation requirements:

- define one WLS six-field semantic projection in exact order
  `[context,path,sha256,size,mode,nlink]`; require exact keys/types and the
  frozen eight-record context/list order; normalize expected and fresh actual
  ledgers through that same function;
- reject missing/extra/duplicate members or records, reordered contexts,
  duplicate contexts/paths, wrong key/type/value/path/hash/size/mode/nlink,
  traversal, alias, symlink, hardlink and inode/source replacement;
- preserve list order; do not sort records, setify, deduplicate, drop fields or
  use a fallback comparison;
- add the distinct authenticated `source_load_micro_sentinel` operation for
  `V3A-MODE-BHPT-RW-001/P1`: exactly one real Wolfram launch, complete
  request/overlay/Paclet/context/FindFile and source start/end closure, then
  exit before `ReggeWheelerRadial` with every external API, solver, boundary,
  overlap and scientific counter exactly zero;
- implement the fixed one-use micro authority/root/review namespace and the
  later distinct full-sentinel attempt-0003 authority/root/review namespace
  from the frozen design.  Future T7 digests are supplied only by later T0
  dispatches.  Keep official attempt-0001 behavior unchanged;
- validate the micro review at its single fixed path using its
  dispatch-supplied digest, exact success envelope, package and implementation
  identities and the immutable micro root; never accept the failure envelope
  or the 35-call sentinel label as full-sentinel authority;
- make micro artifacts non-scientific and non-reusable, with O_EXCL/no-follow,
  consumption-before-call, exact absolute argv/clean environment, immutable
  terminal/manifest and complete child process closure;
- preserve the prior argv, namespace, lifecycle, graph and protected-source
  PASS invariants.

Mandatory zero-science verification includes static/dataflow proofs,
CPython-3.14 focused and adjacent tests, Ruff/compile/diff-check and adversarial
tests for all listed record/authority/lifecycle cases.  In addition, close the
six newly identified surfaces: duplicate JSON-member collapse, preloaded
Paclet/context contamination, same-byte inode replacement, micro/full route
confusion, fake-child self-confirmation and source drift after micro approval.

You may use a real WolframKernel only for a frozen zero-science handshake that
provably exits before `ReggeWheelerRadial`; do not create a formal dispatch or
evidence root.  Report the exact five hashes, tests, zero counters, start/end
protected identities and any observed runtime handshake transcript.  Do not
write status/current handoffs, contact T7, run full sentinel/official science,
or start V3.2.  Stop after the implementation/preflight checkpoint.
