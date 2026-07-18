# T8aq Coordination-Record Correction Design

Date: 2026-07-18

Status: bounded T0 repair candidate for independent read-only review. It is
not executable until this exact package receives:

```text
REVIEW GREEN / T0 REPAIR PACKAGE APPROVED
```

This package does not modify or replace the frozen seven-file further-local
design package at commit `76b57c90d6e54594ca480e1dcf629af685d9098f`.
It creates no new scientific task, frequency, solver run, artifact, threshold,
or downstream authorization.

## 1. Failure Being Repaired

T8aq completed its producer responsibilities and generated a valid immutable
artifact package, but its recovery closeout recorded:

```text
YELLOW / FURTHER LOCAL FREQUENCY EVIDENCE PARTIAL
```

That decision used failures of the phase and hierarchy diagnostics as a T8aq
scientific acceptance gate. The frozen authority assigns those scientific
acceptance tests to T7cb instead:

- design Section 9 and the T8aq plan Task 5 require the T8aq audit to be
  diagnostic-only and to emit no scientific acceptance decision;
- design Section 10 and the T7cb prompt require T7cb to independently rebuild
  and judge all 816 phase and 768 hierarchy records;
- the generated audit itself records `diagnostic_only=true` and
  `acceptance_decision_emitted=false`.

The bounded failure is therefore a coordination-record decision
misclassification. It is not a scientific, numerical, nonfinite, test, scope,
artifact, contract, hash, or provenance failure.

## 2. Immutable Evidence

The correction is valid only while all of the following remain exact:

- frozen seven-file package commit:
  `76b57c90d6e54594ca480e1dcf629af685d9098f`;
- T8aq implementation commit:
  `c34268b6977d9e4e228f0bcc29b628390bd1b1bb`, parent
  `c3a6479703f6c2d64aa2903edc7cf2db3d1ed112`, changing exactly the five
  frozen implementation/test paths;
- generation contract:
  `a43ab0769a73768723505b2bee0715646e215624cc5b5efd880d97bcfff778f1`;
- metadata contract:
  `ff4210c449dfedb5b37228f76e9d91d71488935c7c5064c40b1ddefb961e8d96`;
- exact 24 atomic NPZ/JSON transaction pairs, 53 active files, and 52
  non-self manifest records;
- root SHA-256 values:

```text
7b63e0689a01e32e27397007a3e458c800e2802bdd72c3f582a6e8a6bec4ae72  checkpoint_ledger.json
27c263e8cb4b3270fe3103a9d79617a345a383a636da0ab3af4f954432fdf50b  further_local_values.npz
df30e1f3cb3d17f87bc8f62470a87d5bca2e6819543fe9430b5c48a1d9552a8e  further_local_values.npz.json
a5f5e9d91d1b932fbec307244d35ebee688cfecaf2b11a54672b7eb2d33a2395  further_local_sampling_audit.json
f84d6a1fb2cee35d2a00e81756110d2b75b99edca2946e79e2f70362f7350f3c  manifest.md
```

- focused tests `12 passed`, Ruff pass, and full suite
  `655 passed, 117 skipped, 1 xfailed`;
- no temporary/quarantine file or forbidden output.

Any mismatch stops the correction. It must not be repaired under this
package.

## 3. Correct Producer/Reviewer Semantics

T8aq's exact producer decision answers only whether the frozen evidence was
generated completely and validly. Because all producer artifact, contract,
test, provenance, scope, and isolation gates pass, its corrected decision is:

```text
GREEN / FURTHER LOCAL FREQUENCY EVIDENCE GENERATED
```

This GREEN makes no scientific acceptance claim. In particular, the existing
audit contains exactly 816 finite phase records, 768 finite hierarchy records,
and 80 summaries. A direct T0 reconstruction observes two phase records that
fail strict `absolute_phase_step < pi/2` and 153 hierarchy records that fail
`child_relative_step <= parent_relative_step + 2e-15`; the maxima are
`2.009547281330329` and `0.3055122866114057` excess, respectively. These
values remain immutable diagnostics and must not be hidden, changed, repaired,
or used by T8aq to emit scientific acceptance.

Only frozen T7cb may independently reconstruct those records and return one
of its exact scientific decisions. T7cb may not trust T8aq or T0 counts as its
proof.

## 4. Exact Allowed Writes

The existing T8 task may write only:

```text
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-18_pre_coordination_record_correction.md
```

The archive must be a byte-identical copy of the current misclassified T8
handoff before the current handoff is updated. The corrected records must:

1. state the exact producer GREEN;
2. explain that the prior YELLOW is superseded solely because it applied
   T7cb's scientific decision rule at the producer stage;
3. preserve every artifact, contract, hash, test, scope, recovery, and
   diagnostic fact;
4. label the 816/768 observations as diagnostic-only and pending independent
   T7cb judgment;
5. state that T8 did not rerun or modify the generator, solver, transactions,
   aggregate, audit, manifest, implementation, or tests;
6. return to T0 without dispatching T7cb.

No other file may change under this correction.

## 5. Forbidden Actions

This package forbids:

- editing the frozen seven files or creating a replacement design;
- editing implementation, tests, source, config, accepted evidence, or any
  active artifact;
- rerunning the generator or solver, recomputing any frequency, or changing a
  transaction identity;
- changing phase/hierarchy definitions, thresholds, units, dtype, ordering,
  lmax, boundary/Q018 policy, or radial adapter scope;
- lmax extension, automatic or recursive midpoint selection, another
  frequency, uniform/full grid, production, plot, fixture, Kirchhoff, or
  paper-style work;
- dispatching T7cb from the correction task;
- GitHub action.

## 6. Stop And Downstream Rules

Stop and report T0 if any immutable identity, artifact, contract, test, scope,
or provenance check is missing, changed, or ambiguous; if the exact archive
path already exists with nonmatching bytes; if any allowed-write boundary
would be exceeded; or if the existing T8 task is unavailable.

After exact correction completion, only T0 may fresh-verify the unchanged
evidence and coordination diff. Only then may T0 send the already-frozen T7cb
prompt to the existing T7 task. This package authorizes no new frequency and
no action after T7cb.

## 7. Candidate Identity

The candidate consists of exactly these three new files:

```text
docs/superpowers/specs/2026-07-18-t8aq-coordination-record-correction-design.md
docs/superpowers/plans/2026-07-18-t8aq-coordination-record-correction.md
docs/prompts/phase5_t8aq_coordination_record_correction.md
```

T0 freezes them in one exact three-file Git commit and supplies that commit,
parent, blob IDs, and SHA-256 values to the independent reviewer. Any content
change creates a new candidate identity and invalidates prior review.
