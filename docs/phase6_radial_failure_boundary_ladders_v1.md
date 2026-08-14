# Phase-6 V1 failed-domain boundary ladders

This diagnostic reloads the immutable conditioning campaign and enumerates its
exact 5,798 fail-closed keys. For each selected key it runs five pole-safe
scaled-tortoise nodes: the frozen baseline, `r_in_eps=3e-6`,
`r_in_eps=3e-7`, `r_out=2*selected`, and `r_out=4*selected`. All nodes keep
`rtol=1e-10`, `atol=1e-12`, and Jost order 160.

Outputs include baseline-relative complex/modulus/wrapped-phase `S`, `log|T|`,
required-radius state, and flux differences. The result is diagnostic only:
there is no acceptance threshold, convention uncertainty is `NOT_ASSESSED`,
`scientific_acceptance=false`, and global GREEN is forbidden.

Exact CPython 3.14 smoke:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_run_v1_radial_failure_boundary_ladders.py \
  --output-root runs/phase6/radial_validation/<fresh-root> --limit 1
```

Omit `--limit` only after T0 review. Resume an interrupted unsealed root with
explicit `--resume`; the runner validates source hashes and the fsynced JSONL
prefix before continuing. Terminal files are `0444` and the root is `0555`.
