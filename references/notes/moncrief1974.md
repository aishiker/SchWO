# Moncrief 1974 notes

Source PDF:
`references/papers/moncrief1974.pdf`

Role:
- Gauge-invariant interpretation of Schwarzschild perturbation master
  variables.
- Cross-check for the statement that RW/Zerilli equations have
  gauge-invariant significance.

## Project-relevant points

- Moncrief derives odd and even gauge-invariant variables and shows that the
  Regge-Wheeler and Zerilli equations are not merely artifacts of one gauge.
- The RW gauge is a convenient representation, but the master equations can
  be interpreted gauge-invariantly.

## Convention caveats

- Moncrief's gauge-invariant variables are not identical to the target-paper
  `psi_odd` and `psi_even` used by this project.
- Phase 0 freezes the target-paper normalization:

```text
psi_tilde^(-) = -f h_tilde^(B1)/r
psi_tilde^(+) = Lambda^(-1) [h_tilde^(T0)/r + f h_tilde^(Rt)/(i k)]
```

- Any later comparison to Moncrief variables must write the conversion
  explicitly in `docs/equation_map.md` before implementation.
