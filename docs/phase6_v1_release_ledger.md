# Phase 6 V1 release ledger

Status: fresh repaired V1/V1Q evidence ledger published on 2026-08-10.  This
closes the current implementation-failure repair and evidence-release slice,
not the outstanding full-domain scientific acceptance budgets.

## Repaired V1/V1Q publication — 2026-08-10

The current canonical source map is
`configs/phase6_v1_repaired_release_map_20260810.json`, SHA-256
`aef59e5fe9db485b8b5c2b2909befe3777cd9ce6e0e4ecc75200392b52e8fe30`.
It binds 13 terminal sources and 14 observable/domain certificates.  The fresh
preparation root is
`runs/phase6/v1_release_preparation_repaired_v2_20260810_py314`; its canonical
submission and manifest SHA-256 values are
`fc0c45db3cff9c7e68219cf26c298e45e162b6cc40d2598729e6266c4920b72f`
and `6911f209b76965a807be44543674f21c1b225c4736ad3659b97b2b83ea2c970d`.

The current release root is
`runs/phase6/v1_release_repaired_v2_20260810_py314`.  Its ledger and manifest
SHA-256 values are
`7ef62d6b3ff883570510854ff230821a7d3ca89c8596602df2c36d1cff66e0db`
and `a139e76ac28eba5ae4595aa0bfaad6b7a9814fd2301aa7cdfd3f993fd556e594`.
Independent immutable reload passes.  The exact count is
`PASS=2`, `PARTIAL=12`, `FAIL=0`, `NOT_ASSESSED=0`, with
`global_status=null`.  PASS is limited to V0 implementation verification and
V6 release policy.

The radial implementation failures are closed in the current evidence:
production exact-eight states cover `16,048/16,048`, and the turning-aware
generic `D_union` baseline is `17,818/17,818` algorithmic PASS with zero FAIL.
The selected direct RW/Zerilli comparison also passes `30/30` native numerical
gates.  The physical release certificates remain PARTIAL because independent
arbitrary-precision/external and convention coverage is not full-domain; the
release does not split a composite selected comparison into invented evidence
roles.  See `docs/phase6_v1_radial_repair_v2_20260810.md`.

The 2026-08-09 chain below remains immutable and is retained as the historical
pre-repair release.

## Historical formal V1 publication — 2026-08-09

The canonical source map is
`configs/phase6_v1_release_map_20260809.json`, SHA-256
`c2e388e6a93af227a77f5ad26731357f13ae58236811e80b86457deb12aa4c04`.
It names 13 terminal sources and 15 observable/domain certificates.  The
strict preparation root is
`runs/phase6/v1_release_preparation_v2_20260809_py314`; its canonical
submission SHA-256 is
`6ff1369e7c5e0dc549922a0fed9797e62f9bc9e256253eefd9dbd17b0779dd1e`
and its manifest SHA-256 is
`a00c6df60a194d73bae420eb6023743f6ca26772b26c38bd2fbaf252258e1a53`.

The authoritative release root is
`runs/phase6/v1_release_v1_20260809_py314`.  Its ledger and manifest SHA-256
values are, respectively,
`3f289a9f41c2ee0389e12bdf41b8f331274b3504195411dd0a19f01766f6adb4`
and
`45339f748e17bdaeb2e2aae2b5cea1988e00c61ca2feca5260e7e54e45df18cf`.
Both roots passed independent immutable reload.  The release contains exactly
15 certificates: `PASS=2`, `PARTIAL=6`, `FAIL=6`, and `NOT_ASSESSED=1`.
The only PASS certificates are V0 implementation/provenance cleanup and V6
release-policy enforcement.  The ledger stores `global_status=null`; it does
not assign a project-wide scientific status.

The BHPT-direct source/method certificate is FAIL because the full 24-hour,
800-digit external direct-integration attempt timed out with zero external
records.  The planned direct-versus-conditioned comparator therefore has no
terminal immutable result and remains NOT_ASSESSED; no comparison values were
invented.  Conditioning, production eight-radius, Stage-A arbitrary-precision,
and production-backend certificates preserve their native fail-closed modes.
All V2--V5 observable certificates remain selected-domain PARTIAL.

The first publication attempt,
`runs/phase6/v1_release_preparation_v1_20260809_py314`, was sealed after the
release validator rejected a native Stage-A caveat containing project/global
status wording.  It contains no canonical submission or manifest and is not
authoritative.  The raw scientific evidence was unchanged.  The preparation
adapter now performs one exact, auditable rewrite to domain-qualified prose
and fails closed on any other unrecognized project-wide status wording; the
fresh v2 preparation is the only accepted preparation root.

The V1 release layer is a certifier. It performs no radial solve, observable
measurement, paper-figure render, or threshold calibration. Its only accepted
unit of scientific status is one named observable on one explicit parameter
domain. The ledger deliberately stores `global_status=null`; it has no
project-wide GREEN/PASS field.

## Authoritative predecessor bindings

Every submission must bind the exact immutable bytes below, including each
contract and its manifest:

| binding | root | contract SHA-256 |
|---|---|---|
| `domain_v3` | `runs/phase6/v1_domain_freeze_v3_20260806` | `7ed99b905c3a1301d96101f357ab1fd9f4bc6e9a4922cb242d28e7cf06bb3bcf` |
| `execution_v4` | `runs/phase6/v1_execution_contract_v4_20260806` | `25ad4b4e723edbd44651edaa63df415141de504b85288b12c2a6a973fcb420ab` |
| `aggregation_v8` | `runs/phase6/v1_aggregation_contract_v8_20260806` | `742db1cf159e0bb9c41eb2621b7084f09bca65acd934fdcf639f25f486fa49d2` |
| `observable_v2` | `runs/phase6/v1_observable_contract_v2_20260806` | `3853df8fbc245b81552198d99201778e4020d82f618e3f80ac745768fc3d104b` |

The validator also reopens the live files, checks canonical JSON, `0444`
files, `0555` direct parent roots, `nlink=1`, exact paths/hashes, manifest to
contract linkage, domain cardinalities (`16048/1770/3392/17818`), the 158-key
transition set, 30-key external-direct set, and 86-shard inventory. A stale or
superseded predecessor is rejected rather than silently accepted.

## Three-layer evidence model

1. A producer writes a raw scientific, diagnostic, policy, or blocker result
   into its own fresh immutable evidence root.
2. A normalized `schwgw_phase6_v1_release_evidence_envelope_v1` binds those
   raw bytes and declares their role, independence class, exact gate/
   observable/domain scopes, and state.
3. A `schwgw_phase6_v1_release_certificate_v1` cites envelope IDs and records
   one state plus separate numerical and convention budgets for one explicit
   domain.

An envelope source artifact has an explicit role:

- `RESULT`: a result or result-metadata artifact; the same bytes cannot occur
  in another envelope;
- `INPUT`, `CONFIG`, `SOURCE_SNAPSHOT`, `THRESHOLD`, `CONVENTION`: supporting
  artifacts which may legitimately be shared.

Every source and envelope identity is rechecked against live immutable bytes.
Symlinks, hardlinks, missing files, mutable files/roots, duplicate result
bytes, noncanonical JSON/JSONL, schema drift, and non-finite JSON numbers are
fail-closed errors.

Evidence roles are:

```text
PRIMARY_SCIENCE
INDEPENDENT_SCIENCE
IMPLEMENTATION_VERIFICATION
POLICY_VERIFICATION
CONVENTION_DEFINITION
BLOCKER
FAILURE_DIAGNOSTIC
SECONDARY_PAPER_REGRESSION
CONTRACT_ONLY
```

`INDEPENDENT_SCIENCE` must declare `ALGORITHMICALLY_INDEPENDENT` or
`EXTERNAL_SOURCE`. Science envelopes also carry an ordered set of
implementation-source SHA-256 values which must occur in their immutable
`RESULT` metadata. A physical PASS requires both primary and independent
science, and their implementation-source sets must be disjoint. A runtime
blocker must instead declare `NOT_ASSESSED`,
`science_executed=false`, `scientific_evidence=false`, and an uppercase code
such as `BLOCKED_BY_RUNTIME`. It cannot support a PASS/FAIL budget or
certificate. Contract-only evidence is likewise unable to promote a result.

Li–Hou–Zhao figure agreement may be wrapped only as
`SECONDARY_PAPER_REGRESSION`. The validator rejects a primary gate containing
Li agreement, paper-figure agreement, or raster matching. It also requires
the submission and every envelope to declare that no full paper-figure rerun
was performed in this phase.

## Required certificate inventory

At least one explicit-domain certificate is required for every row:

| gate | observable |
|---|---|
| V0 | `claim_provenance_cleanup` |
| V1 | `radial_s_matrix_flux` |
| V1Q | `generic_conditioning_backend` |
| V2 | `master_to_strain_flux` |
| V2 | `metric_psi4_external_crosscheck` |
| V3 | `spin2_scattering_limits` |
| V4 | `finite_radius_tidal_detector` |
| V5 | `complex_lensing_matrix` |
| V6 | `release_uncertainty_policy` |

Additional certificates may split any observable into more parameter
domains, but duplicate `(gate, observable, domain_id)` scopes are rejected.
The allowed states are exactly `NOT_ASSESSED`, `PARTIAL`, `PASS`, and `FAIL`.
They are counted, not collapsed into a gate-wide or project-wide colour.

V0 and V6 are implementation/policy gates, so their physical uncertainty
components are explicitly `NOT_APPLICABLE`. Every V1/V1Q/V2/V3/V4/V5
certificate must carry all numerical components:

```text
lmax, r_in, r_out, jost_order, ode_tolerance,
arithmetic_precision, axis_limit, backend_difference
```

and all convention/observable components:

```text
observer, worldline, tetrad, polarization_basis,
phase_origin, total_scattered_definition
```

Each component has its own applicability, state, canonical decimal estimate,
units, reason, and evidence IDs. A physical PASS requires complete domain
coverage and PASS for every required component. `PARTIAL`, `FAIL`, and
`NOT_ASSESSED` remain publishable when they honestly describe the evidence.

## Publication protocol

The input is one canonical JSON submission with schema
`schwgw_phase6_v1_release_submission_v1`. Once all cited evidence envelopes
have been frozen, first run the non-writing preflight:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_publish_v1_release.py \
  --submission /absolute/path/to/canonical_submission.json \
  --check-only
```

It reloads every live identity and derives all counts while reporting
`output_written=false`. After that passes, the expected formal invocation is:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_publish_v1_release.py \
  --submission /absolute/path/to/canonical_submission.json \
  --output-root /absolute/path/to/a_fresh_release_root
```

The output root must not exist. Publication uses exclusive creation and never
replaces a path. It creates exactly:

```text
release_ledger.json
manifest.json
```

Both files are canonical JSON, regular `0444`, `nlink=1`; the root is sealed
`0555`. The manifest is derived from the ledger and records certificate/state/
gate counts, the submission hash, `global_status=null`, and the no-global-
GREEN/no-Li-primary/no-paper-rerun policy. Reload validation rechecks every
contract, envelope, source artifact, certificate, count, permission, and
identity.

Do not run that command against a formal `runs/phase6/...` root until all
Stage-A, conditioning, external BHPT, and observable evidence selected for the
release has reached a terminal immutable state. Development tests must use
temporary fresh roots only.

## Strict preparation/composition layer

Raw producer metadata is deliberately not hand-transcribed into release
envelopes. The preparation helper accepts one canonical declarative map with
schema `schwgw_phase6_v1_release_preparation_map_v1`. A source record contains
only:

```text
evidence_id
adapter
absolute origin_root
ordered relative_path + expected SHA-256 inventory
adapter-specific selector (only the observable certificate selector is nonempty)
```

The two campaign adapters also require a single `projection` selector. It is
restricted to `radial_s_matrix_flux` or `generic_conditioning_backend`; it is
not a state, threshold, or user-defined coverage claim.

Certificate plans declare an explicit gate, observable, domain, expected
cardinality, evidence IDs, and physical acceptance method. They do not contain
a result state, assessed cardinality, or uncertainty value. The typed adapter
extracts those fields from native immutable evidence. Unknown fields are
rejected, so a map cannot add `state=PASS`, substitute a budget, or re-label a
blocker as science.

A canonical map has this exact outer shape (arrays may contain multiple typed
records):

```json
{
  "schema": "schwgw_phase6_v1_release_preparation_map_v1",
  "preparation_id": "phase6_v1_preparation_identifier",
  "release_id": "phase6_v1_release_identifier",
  "sources": [
    {
      "evidence_id": "typed_evidence_identifier",
      "adapter": "TYPED_PHYSICAL_RESULT_V1",
      "origin_root": "/absolute/path/to/terminal_immutable_root",
      "expected_artifacts": [
        {"relative_path": "report.json", "sha256": "64-lowercase-hex"}
      ],
      "selector": {}
    }
  ],
  "certificates": [
    {
      "certificate_id": "per_observable_domain_identifier",
      "gate": "V3",
      "observable": "spin2_scattering_limits",
      "parameter_domain": {
        "domain_id": "explicit_domain_identifier",
        "description": "explicit non-global parameter domain",
        "parameters": {"kM": ["0.01", "0.1"]},
        "selection_policy": "exact frozen item-index construction",
        "expected_items": 2
      },
      "evidence_ids": ["typed_evidence_identifier"],
      "primary_acceptance_gate": "independent physical benchmarks and frozen thresholds"
    }
  ],
  "policy": {
    "acceptance_is_per_observable_and_domain": true,
    "full_paper_figure_rerun_performed": false,
    "global_green_permitted": false,
    "li_figure_agreement_primary_gate": false,
    "publisher_generated_science": false
  }
}
```

The actual map must include at least one certificate plan for every V0/V1/
V1Q/V2–V6 observable slice. Certificate and evidence IDs are ordered unique;
every source must be cited, and duplicate native result bytes are rejected
(the only sharing exception is one validated observable bundle selected into
different native certificate IDs, or one validated campaign root selected
into its two frozen projections). Evidence with different native cardinalities
is not combined into a forged common domain: Stage-A (8 anchors), legacy MST
(84 modes), BHPT direct (30 modes), conditioning D_union (17,818 keys), the
conditioning transition domain (158 keys), and production D_prod (16,048
keys) require separate explicit-domain certificates unless exact item-ID
equality/intersection is proved.

The currently supported adapters are:

| adapter | native source and conservative release meaning |
|---|---|
| `STAGE_A_MPMATH_V1` | exact selected-anchor evidence/manifest/checkpoint; binds the exact eight-anchor domain, not D_prod=16,048, and preserves all eight terminal states. Any included `FAIL_CLOSED_NUMERICAL_INSTABILITY` forces the envelope and containing certificate to `FAIL`, even when the native top-level label is YELLOW. |
| `CONDITIONING_SHARD_V1` | strict producer reload of one terminal conditioning shard. Shards in the same method family union exact key identities; different validation methods do not add unrelated coverage. A native aggregate attempt FAIL forces release FAIL even if an aggregate acceptance field is PARTIAL or NOT_ASSESSED. |
| `CONDITIONING_CAMPAIGN_V1` | exact two-file 86-shard campaign root plus full native reload. `radial_s_matrix_flux` projects exact D_union=17,818; `generic_conditioning_backend` projects the exact 158-key transition domain. Native fail-closed keys force certificate FAIL. Component budgets remain domain-specific: zero-assessed `backend_difference`, observer, worldline, tetrad, polarization, and total-scattered fields stay `NOT_ASSESSED` rather than being relabelled FAIL or zero. |
| `BHPT_MST_LEGACY_V1` | only the exact Phase-5 v4 comparison and external bytes with the two frozen hashes. Odd-sector MST is external; parity-derived even remains explicit. A native benchmark PASS is capped at release `PARTIAL`. |
| `BHPT_DIRECT_V1` | exact formal-root manifest inventory and 30-record native validator. A successful source/method/algebra check remains calibration `PARTIAL`; a non-executed runtime record remains a blocker. |
| `BHPT_DIRECT_COMPARISON_V1` | exact `comparison.json` + `report.json` + `manifest.json` from the 30-key BHPT-direct versus conditioned-radial producer. The adapter calls the native three-file validator and source rebuild, requires 24 `PARTIAL` + 6 `FAIL`, preserves the external/internal `source_role_ledger` and full source identities, and can support only V1 `radial_s_matrix_flux`. The six native failures force the certificate to `FAIL`. |
| `OBSERVABLE_FORMAL_ROOT_V1` | strict populated-observable-bundle reload and one exact native certificate selection. A single normalized envelope cannot launder its internal primary and independent roles, so native PASS is conservatively capped at `PARTIAL`. |
| `TYPED_PHYSICAL_RESULT_V1` | future immutable campaign report whose ordered exact expected-item IDs, assessed item states, coverage, two uncertainty budgets, source hashes, and aggregate state are mutually derived and validated. A BHPT-direct comparison report is explicitly rejected here: it must use the dedicated three-file adapter, so copying `report.json` alone cannot bypass native comparison/manifest/source validation. |
| `PRODUCTION_FINITE_RADIUS_V1` | a strict typed future observer-response report. Until its worldline/tetrad pure-gauge test passes, its output kind must remain `FINITE_RADIUS_TIDAL_RESPONSE` and it cannot PASS V4. This is not the radial-state campaign adapter below. |
| `PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1` | exact `campaign_result.json` plus manifest from the 80-shard production radial-state publisher. Both permitted projections bind all D_prod=16,048 keys because the generic backend and eight-radii solve ran over the full production domain; it may support V1/V1Q only and is prohibited from V4. Observer/tetrad/detector claims remain `NOT_ASSESSED`; any native mode FAIL forces the certificate to FAIL independently of component-budget states. |
| `V0_IMPLEMENTATION_VERIFICATION_V1` | final machine-readable stale-metadata, legacy-NP isolation, legacy-pseudoinverse isolation, and full-test report. Documentation or a contract alone cannot PASS V0. |

### Recommended canonical V1 map inventory

Use one certificate per method/domain. Do not combine the rows below merely
because they share V1 or V1Q. In particular, the eight Stage-A keys, 84 MST
records, 30 direct-calibration keys, 158 transition keys, D_prod=16,048, and
D_union=17,818 are distinct item-ID coverages.

| evidence ID | adapter | selector | exact native artifacts |
|---|---|---|---|
| `v0_final_verification` | `V0_IMPLEMENTATION_VERIFICATION_V1` | `{}` | `verification.json` |
| `stage_a_v10_selected_8` | `STAGE_A_MPMATH_V1` | `{}` | `checkpoint.json`, `manifest.json`, `selected_anchor_evidence.json` |
| `bhpt_mst_v4_odd_84` | `BHPT_MST_LEGACY_V1` | `{}` | frozen v4 `comparison.json`, `external_bhpt_mst.json` |
| `bhpt_direct_v3_selected_30` | `BHPT_DIRECT_V1` | `{}` | every direct-root file named by its manifest, plus `manifest.json` |
| `bhpt_direct_conditioned_selected_30` | `BHPT_DIRECT_COMPARISON_V1` | `{}` | `comparison.json`, `manifest.json`, `report.json` |
| `conditioning_d_union_17818` | `CONDITIONING_CAMPAIGN_V1` | `{"projection":"radial_s_matrix_flux"}` | `conditioning_campaign_index.json`, `manifest.json` |
| `conditioning_transition_158` | `CONDITIONING_CAMPAIGN_V1` | `{"projection":"generic_conditioning_backend"}` | same immutable campaign root and two files |
| `production_d_prod_16048_radial` | `PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1` | `{"projection":"radial_s_matrix_flux"}` | `campaign_result.json`, `manifest.json` |
| `production_d_prod_16048_backend` | `PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1` | `{"projection":"generic_conditioning_backend"}` | same immutable campaign root and two files |
| `observable_v2_master_strain` | `OBSERVABLE_FORMAL_ROOT_V1` | `{"source_certificate_id":"master_to_strain_flux:9004bd5f0e835398c528"}` | `observable_evidence.json`, `manifest.json` |
| `observable_v2_metric_psi4` | `OBSERVABLE_FORMAL_ROOT_V1` | `{"source_certificate_id":"metric_psi4_external_crosscheck:16f5e39dc6e8ebfb6f8b"}` | same immutable observable root and two files |
| `observable_v3_spin2_limits` | `OBSERVABLE_FORMAL_ROOT_V1` | `{"source_certificate_id":"spin2_scattering_limits:c9baa860876fb004df53"}` | same immutable observable root and two files |
| `observable_v4_tidal_detector` | `OBSERVABLE_FORMAL_ROOT_V1` | `{"source_certificate_id":"finite_radius_tidal_detector:af87a7d501b28cc0e4c5"}` | same immutable observable root and two files |
| `observable_v5_lensing_matrix` | `OBSERVABLE_FORMAL_ROOT_V1` | `{"source_certificate_id":"complex_lensing_matrix:c58816940553aa09ae2f"}` | same immutable observable root and two files |

The corresponding certificate inventory is:

| gate / observable | recommended domain ID | expected items | sole evidence ID |
|---|---:|---:|---|
| V0 / `claim_provenance_cleanup` | `v0_final_verification_v1` | 1 | `v0_final_verification` |
| V1 / `radial_s_matrix_flux` | `stage_a_selected_8` | 8 | `stage_a_v10_selected_8` |
| V1 / `radial_s_matrix_flux` | `bhpt_mst_odd_selected_84` | 84 | `bhpt_mst_v4_odd_84` |
| V1 / `radial_s_matrix_flux` | `bhpt_direct_source_method_selected_30` | 30 | `bhpt_direct_v3_selected_30` |
| V1 / `radial_s_matrix_flux` | `bhpt_direct_conditioned_selected_30` | 30 | `bhpt_direct_conditioned_selected_30` |
| V1 / `radial_s_matrix_flux` | `conditioning_d_union_17818` | 17,818 | `conditioning_d_union_17818` |
| V1 / `radial_s_matrix_flux` | `production_d_prod_radial_16048` | 16,048 | `production_d_prod_16048_radial` |
| V1Q / `generic_conditioning_backend` | `conditioning_transition_158` | 158 | `conditioning_transition_158` |
| V1Q / `generic_conditioning_backend` | `production_d_prod_backend_16048` | 16,048 | `production_d_prod_16048_backend` |
| V2 / `master_to_strain_flux` | `selected_li_mp_waveform_v1` | 2 | `observable_v2_master_strain` |
| V2 / `metric_psi4_external_crosscheck` | `selected_li_metric_bridge_v1` | 2 | `observable_v2_metric_psi4` |
| V3 / `spin2_scattering_limits` | `selected_conditioned_spin2_benchmarks_v1` | 3 | `observable_v3_spin2_limits` |
| V4 / `finite_radius_tidal_detector` | `selected_two_observer_radial_gauge_v1` | 2 | `observable_v4_tidal_detector` |
| V5 / `complex_lensing_matrix` | `selected_radial_scattering_transfer_v1` | 2 | `observable_v5_lensing_matrix` |
| V6 / `release_uncertainty_policy` | `phase6_v1_v3_v4_v8_v2_policy` | 1 | generated V6 policy evidence |

For the comparator and the five observable rows, copy `description`,
`parameters`, and `selection_policy` byte-for-byte from the native typed
report or referenced native parameter-domain artifact. For the campaign rows,
record the frozen key-list SHA-256 in `parameters`; do not type a state or
budget into the map. Source records must be sorted by `evidence_id`,
certificates by `certificate_id`, artifacts by relative path, and every SHA-256
must be computed from the final terminal bytes. Running the preparation CLI
with `--check-only` is the canonical map validator; there is no separate
handwritten status projection.

V0 is generated as `PARTIAL` when that final verification report is absent.
V6 is the only generated PASS: it records the preparation/release validators'
policy verification and the exact v3/v4/v8/v2 bindings. Empty physical slices
receive a `NO_TERMINAL_IMMUTABLE_EVIDENCE` blocker and remain
`NOT_ASSESSED`.

The V0 adapter requires `verification.json` with exact schema
`schwgw_phase6_v1_v0_verification_report_v1` and exactly these fields:

```text
schema
verification_id
checks
source_report_sha256s
verification_state
global_green_permitted=false
li_figure_agreement_primary_gate=false
```

`checks` must contain exactly `stale_production_metadata`,
`legacy_np_isolation`, `legacy_pseudoinverse_isolation`, and
`full_test_suite`. Each record contains exactly `state`, `command`, `passed`,
`failed`, `skipped`, and `report_sha256`. Counts are nonnegative integers; a
nonzero failed count must be `FAIL`, and PASS requires `passed>0, failed=0`.
`source_report_sha256s` is the ordered unique set of all four check-report
hashes. `verification_state` is derived as FAIL if any check FAIL, PASS only if
all four PASS, otherwise PARTIAL.

### Trusted V0 check production

The four source reports are not handwritten. The trusted runner accepts only
a fixed check ID and a fresh output root; it has no state, count, command, or
assertion override. Each `check_report.json` has schema
`schwgw_phase6_v1_v0_check_report_v1` and exactly:

```text
schema, check_id, command_argv, working_directory, exit_status,
assertions, counts, source_identities, execution_complete,
global_green_permitted=false, li_figure_agreement_primary_gate=false
```

Assertions contain only `assertion_id`, `outcome`, and `detail`; counts are
rederived from those outcomes. Exit status must agree with the failed count.
The three implementation checks use a frozen static/dynamic assertion
inventory over bound source identities. `full_test_suite` runs the fixed
`/opt/homebrew/bin/python3.14 -m pytest -q --junitxml=...` command under the
frozen mpmath overlay and derives one assertion per JUnit testcase. Check
roots use O_EXCL writes, `0444`/`nlink=1` files, a `0555` root, and readback
validation.

For each check, choose a distinct fresh absolute root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_run_v0_check.py \
  --check-id stale_production_metadata \
  --output-root /absolute/fresh/v0_stale_metadata_check

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_run_v0_check.py \
  --check-id legacy_np_isolation \
  --output-root /absolute/fresh/v0_legacy_np_check

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_run_v0_check.py \
  --check-id legacy_pseudoinverse_isolation \
  --output-root /absolute/fresh/v0_legacy_pseudoinverse_check

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_run_v0_check.py \
  --check-id full_test_suite \
  --output-root /absolute/fresh/v0_full_test_suite_check
```

After all four roots are terminal, the strict final producer derives the
exact `verification.json`; it accepts no state and writes exactly one `0444`
file into a fresh `0555` root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_publish_v0_verification.py \
  --verification-id phase6_v0_final_verification \
  --stale-production-metadata-report /absolute/fresh/v0_stale_metadata_check/check_report.json \
  --legacy-np-isolation-report /absolute/fresh/v0_legacy_np_check/check_report.json \
  --legacy-pseudoinverse-isolation-report /absolute/fresh/v0_legacy_pseudoinverse_check/check_report.json \
  --full-test-suite-report /absolute/fresh/v0_full_test_suite_check/check_report.json \
  --check-only

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_publish_v0_verification.py \
  --verification-id phase6_v0_final_verification \
  --stale-production-metadata-report /absolute/fresh/v0_stale_metadata_check/check_report.json \
  --legacy-np-isolation-report /absolute/fresh/v0_legacy_np_check/check_report.json \
  --legacy-pseudoinverse-isolation-report /absolute/fresh/v0_legacy_pseudoinverse_check/check_report.json \
  --full-test-suite-report /absolute/fresh/v0_full_test_suite_check/check_report.json \
  --output-root /absolute/fresh/v0_final_verification
```

This implementation has not run the real full suite through that runner and
has not published a formal V0 root; only temporary-fixture publisher tests
were executed.

Every selected native file is stable-read against the map hash, copied with
exclusive creation into the preparation root, and sealed. The normalized
projection records the original path/hash/stat, immutable snapshot identity,
and `copy_sha256_equal=true`. The projection is the unique envelope `RESULT`;
native bytes are `SOURCE_SNAPSHOT` inputs. It also records
`normalization_is_new_science=false` and `publisher_generated_science=false`.
The Phase-5 MST source is the one deliberate mutable-origin exception: only
the two hard-coded v4 hashes are accepted, their bytes are copied unchanged,
and the release validator's `0444`/`0555` rules remain untouched.

The preparation output is a fresh tree:

```text
release_map.json
canonical_submission.json
manifest.json
sources/<evidence_id>/<native bytes>
normalized/<evidence_id>/result.json
envelopes/<evidence_id>/evidence.json
```

All writes use no-replace exclusive creation. Files are `0444`; every nested
directory and the root are `0555`. An interrupted publication is recursively
sealed as a failed audit artifact. Reload validation checks the exact layout,
all identities, byte-for-byte source copies, normalized projections,
envelopes, canonical submission, and the downstream release validator.

Once every referenced producer root is terminal, use this no-write preflight:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_prepare_v1_release.py \
  --release-map /absolute/path/to/canonical_release_map.json \
  --check-only
```

Stage-A/MST maps must put their frozen mpmath overlay before `src` in
`PYTHONPATH`. After preflight succeeds, create a fresh preparation root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_prepare_v1_release.py \
  --release-map /absolute/path/to/canonical_release_map.json \
  --output-root /absolute/path/to/a_fresh_preparation_root
```

Then pass that root's `canonical_submission.json` through
`phase6_publish_v1_release.py --check-only`. Only after both validations pass
should the final release publisher receive a fresh formal output root. Neither
preparation nor final release publication has been run against a formal
Phase-6 root by this implementation slice.

After the four V0 check roots above are frozen, the eventual formal release
handoff has these explicit absolute parameters:

```text
v0_check_report_paths = four absolute .../check_report.json paths
fresh_v0_root         = /absolute/path/to/fresh_v0_final_verification
release_map_path       = /absolute/path/to/canonical_release_map.json
fresh_preparation_root = /absolute/path/to/fresh_phase6_v1_preparation_root
canonical_submission   = <fresh_preparation_root>/canonical_submission.json
fresh_release_root     = /absolute/path/to/fresh_phase6_v1_release_root
```

The final two commands, still to be run only after every source is terminal,
are:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_publish_v1_release.py \
  --submission /absolute/path/to/fresh_phase6_v1_preparation_root/canonical_submission.json \
  --check-only

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_publish_v1_release.py \
  --submission /absolute/path/to/fresh_phase6_v1_preparation_root/canonical_submission.json \
  --output-root /absolute/path/to/fresh_phase6_v1_release_root
```
