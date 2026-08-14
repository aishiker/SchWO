# Phase-6 V1 successful-domain continuity diagnostic

This isolated diagnostic live-rebuilds the immutable V1 conditioning campaign,
enumerates its exact 12,020 `COMPLETED`/`PARTIAL` keys, and runs one
scaled-tortoise baseline solve per selected key with the predecessor
`r_in`, `r_out`, tolerance, and Jost-order configuration. It compares
`A_out` (complex, modulus, wrapped phase), `log|T|`, transmission phase, and
flux quantities with the predecessor payload.

It is a same-equation, same-Jost implementation continuity check. It defines
no acceptance threshold: measured keys remain `PARTIAL`, solver errors remain
`FAIL`, convention uncertainty is `NOT_ASSESSED`, `scientific_acceptance=false`,
and global GREEN is forbidden. It does not rerun paper figures or assess
finite-radius observer response.

Smoke command (exact CPython 3.14):

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_run_v1_radial_success_continuity.py \
  --output-root runs/phase6/radial_validation/<fresh-smoke-root> \
  --limit 1
```

Full command, only after T0 review, omits `--limit`. An interrupted unsealed
root can be continued only with explicit `--resume`; the runner validates the
contract, implementation hashes, and exact canonical JSONL prefix before
continuing. A kernel-held nonblocking writer lock prevents concurrent writers,
and each key record is fsynced before progress advances. Terminal files are
sealed `0444` and the root `0555`.
