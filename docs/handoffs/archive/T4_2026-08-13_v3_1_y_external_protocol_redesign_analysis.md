# T4 archive — V3.1-Y external protocol redesign analysis

Date: 2026-08-13
Task: formal T4, read-only/zero-science design analysis
Gate: `phase6_v3_1_y_external_protocol_redesign_analysis_v1`

## Outcome

T4 completed the Root-T0-authorized distinct V3.1-Y protocol analysis.  The
full design is:

```text
docs/phase6_v3_1_y_external_protocol_redesign_analysis.md
SHA-256 9f04538cb1c42df2eb3ec8779376cf56d7f8769312cd99cc9dd6b59b33099377
```

No WolframKernel, BHPT, AP, Route A/U/B/C, radial solver or other numerical
computation was launched.  No package, dispatch, evidence/staging root,
sentinel, official candidate or T7 request was created.  No status or current
handoff was edited.  The only repository writes in this task are the main
analysis and this archive.

## Principal conclusions

1. The old V3.1-X runtime record remains truthfully
   `failed_leaf=UNKNOWN`: its compound semantic branch persisted only generic
   rc69 and no predicate/ordinal/expected/observed record.
2. The frozen WLS nevertheless admits a deterministic **static causal
   reconstruction**.  It calls undefined `StringNormalize[path]`, whereas
   Wolfram 14.3 provides `CharacterNormalize[text,"NFC"]`.  The unresolved
   call is not `SameQ` to the path String, so the first valid source record
   fails the path-normalization leaf and enters the exact observed generic
   branch.  This source-level conclusion must be confirmed, not inferred, by
   the future one-use real-kernel compatibility matrix.
3. The recommended replacement is Protocol A: ordered typed predicate frames
   plus a parent ACK issued only after O_EXCL publication, file+parent fsync,
   reload and hash/stat verification.  The child cannot enter the next stage
   without the exact session/sequence/frame/checkpoint-bound ACK.
4. A child-owned filesystem checkpoint FSM was compared and rejected as the
   authority boundary because its exclusivity/fsync and self-confirmation
   properties are weaker.  A monolithic terminal result was also rejected.
5. The design freezes a persistent one-launch zero-science compatibility
   matrix, then a different one-launch source-load micro sentinel terminating
   before every BHPT/API/solver branch.  Each requires a separate formal T7
   terminal ADVANCE before the next one-use authority exists.
6. Every leaf has a stable predicate ID, ordinal, expected/observed typed
   values and a direct fault.  The matrix additionally covers RawJSON,
   Association projection, exact Boolean semantics, Unicode, regex/string,
   integer types, path/hash/stat/inode/link identity, Paclet contamination,
   source replacement, channel/ACK replay, fake-child self-confirmation,
   partial publication, timeout, wait/reap and PG-empty.
7. V3.1-Y keeps the exact 23 odd anchors, direct NumericalIntegration method,
   node/precision graph, external snapshot, 496-mode production domain, all
   16 thresholds, five certificate IDs, conventions and seven protected
   radial identities.  There is no post-hoc subset, MST fallback, threshold
   relaxation or predecessor science reuse.
8. Suggested future scope is exactly six new Y-specific files: two WLS
   scripts (compatibility and science-capable), one producer, one CLI and two
   tests.  Any seventh path or science-contract change stops package freeze.
9. Fresh authority order is package review → implementation review →
   compatibility dispatch/review → source micro dispatch/review → 35-call
   sentinel dispatch/review → official attempt-0001 dispatch/scientific
   review.  V3.1-X roots, attempts and review preflight are permanently
   denylisted.

## Frozen identities confirmed

```text
Y prompt
  653cd1e8a20fdb6085c5bf1c3081ca19f1632176a3a915bf20798a885a903fb6
T0 final X adjudication
  7fd2012a57e86a8b085114c3b68243db616e8437983bf150ee85b2474775cee5
T7 final X review
  e5f9b9503e16b053525dfba7dacb661abc433211d49dcccb2c5c9dc442af1dee
liveness protocol
  3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181
V3 domain / thresholds / anchors / convention
  803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b
  91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a
  06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485
  82f9c23a9e93e6aaf6cafbddaf62608acf47b976aeff1cda9066733ddad1449a
X WLS / core / producer / CLI / unit / regression
  7a8277b6996fccbd3d0b515ebba8a0fae17a9c6a9efa7a0d3116a9055bbc041f
  981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4
  fa0c9c2cdadead19dd1051c45fb0ac22932641a7266d9717dfd2188377945af8
  b85a8cff88b1cab5c01b50fbd047b403d56c37952ca920bde55668cf7affa574
  e0ad4e08c84921cb1eaaf1a91e351e189e474938678b56d033c3494cbb7574c3
  ee79b8c276cc9eee369e97de83a3008714f090a1c735b7872f05e901cb3a862d
WolframKernel
  70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c
external snapshot metadata / content / restored identity
  8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488
  d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2
  a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27
```

The seven protected source hashes also rehash exactly as recorded in the main
analysis.  Consumed X attempt manifests remain exact:

```text
attempt-0001 d905500bc70d6b562b7118454dfc020a053521d666e68619252c684905516772
attempt-0002 6e0d2349d998f76ee8d149e4551bf27222c5d93bf4ec9fb7b790adbc9f506109
```

## Nonclaims

- This archive does not approve a V3.1-Y package or implementation.
- It does not convert the static failure reconstruction into a new kernel
  observation or change the old runtime leaf from `UNKNOWN`.
- It contains no external odd result and no independent even result.
- It does not authorize compatibility, micro, sentinel, official science,
  V3.2, current-handoff updates or global GREEN.
- No failed science or successful predecessor subset is reusable.

CHECKPOINT / V3.1-Y EXTERNAL PROTOCOL REDESIGN ANALYSIS READY FOR T0 PACKAGE FREEZE
