# T7 V3.1-U resume-controller machine-authority correction

Date: 2026-08-12

Classification: `CONTROL_PLANE_REPAIR`

This archive-only delta verification corrects only the machine-readable
authority surface of the completed T7 implementation delta recheck. It does
not reopen or alter the scientific review, implementation review, evidence,
verdict, claim status, limitations or nonclaims.

## Bound prior review

```text
path: docs/handoffs/archive/T7_2026-08-12_v3_1_u_resume_controller_implementation_delta_recheck_1.md
sha256: 81ea85f29c67a514e24c877ec1a1733837f7b01ca617547eed794f3220c5df82
```

The prior review remains immutable. Its evidence and conclusions are adopted
unchanged and hash-bound above.

## Human-readable verdict — unchanged

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U RESUME CONTROLLER READY FOR ONE-USE T0 DISPATCH
```

## Exact machine-authority block

The following tokens are literal, case-sensitive, identity-bound authority
tokens for the reviewed candidate:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
V3.1-U RESUME-CONTROLLER
2fcd2e4cc57845b32573047fa3989e1bfcd4f520eefcea6f6df6504d164602fe
248d5c871d6e8784eded31f3f28afb4e54da74e6f8af996ee7c83068935880c2
49746f878feb16eb98800b5a2dfa949ab1690c2286eb612ebbd7d8e4f68b6291
373200067cf5558084a6e60f9a6b7c5fe5f0d43b3e7142afb1ee2cbe258ae5f9
a6c2b7110dd7383645f63d7b38a5c9ecb73cf82699afa5eee410decac75936e0
```

Identity meanings:

```yaml
machine_authority:
  exact_gate_token: V3.1-U RESUME-CONTROLLER
  package:
    path: configs/phase6_v3_1_u_resume_controller_package.json
    sha256: 2fcd2e4cc57845b32573047fa3989e1bfcd4f520eefcea6f6df6504d164602fe
  repaired_implementation:
    - path: src/schwgw/validation/phase6_v3_hp_unitarity_resume.py
      sha256: 248d5c871d6e8784eded31f3f28afb4e54da74e6f8af996ee7c83068935880c2
    - path: scripts/phase6_v3_1_hp_unitarity_resume.py
      sha256: 49746f878feb16eb98800b5a2dfa949ab1690c2286eb612ebbd7d8e4f68b6291
    - path: tests/unit/test_phase6_v3_hp_unitarity_resume.py
      sha256: 373200067cf5558084a6e60f9a6b7c5fe5f0d43b3e7142afb1ee2cbe258ae5f9
    - path: tests/regression/test_phase6_v3_hp_unitarity_resume_publication.py
      sha256: a6c2b7110dd7383645f63d7b38a5c9ecb73cf82699afa5eee410decac75936e0
```

## Correction scope and boundaries

- Finding class: `CONTROL_PLANE_REPAIR`.
- Delta action: add the exact hyphenated machine token and explicit package
  identity required by production `validate_authorities`.
- Original verdict, review evidence, passed/failed inventories, claims and
  nonclaims remain exactly unchanged.
- The previously generated dispatch bound to the old archive is superseded,
  forbidden and unconsumed; it must not be used or replayed.
- `status.md`, `docs/handoffs/T0_current.md`,
  `docs/handoffs/T7_current.md` and the real interrupted root are unchanged.
- V3.1-U science remains `NOT_ASSESSED`.
- This correction authorizes no science by itself, no V3.2, no global GREEN,
  and no reuse or promotion of predecessor evidence.

The only bounded authorization retained from the immutable prior verdict is
readiness for a fresh, one-use Root-T0 dispatch that binds this correction
archive and all exact identities above.
