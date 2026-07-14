# Regge-Wheeler 1957 notes

Source PDF:
`references/papers/regge1957.pdf`

Role:
- Historical and foundational reference for odd-parity Schwarzschild
  perturbations and the Regge-Wheeler equation.
- Used as a sanity check for the odd potential and RW gauge idea, not as the
  primary software convention.

## Project-relevant points

- Odd and even perturbations separate by parity.
- The odd-sector radial equation can be written in tortoise coordinate form
  as a one-dimensional wave equation with an effective potential.
- Gauge freedom is used to simplify the odd perturbation variables, which is
  the origin of the RW gauge language.

## Convention caveats

- The paper uses older notation and sign conventions.
- It should not be used directly for `psi_odd` normalization in this project.
- The project odd potential is fixed by `docs/physics_spec.md` Sec. 5:

```text
V_l^(-)(r) = f(r)/r^2 [l(l+1) - 6M/r]
```

with the target-paper `exp(-i k t)` Fourier convention and boundary phases.
