# Suggested configs

## configs/schwarzschild_fig3_like.yaml

```yaml
background:
  name: schwarzschild
  M: 1.0
wave:
  kM_values: [0.1, 0.5, 1.0, 2.0, 4.0]
  A_plus: "0.9+1.1j"
  A_cross: "0.4+0.6j"
  incident_direction: [0, 0, 1]
observer:
  kind: xz_plane
  x_min: -30
  x_max: 30
  z_min: -30
  z_max: 30
  n_x: 400
  n_z: 400
numerics:
  lmax_rule: "ceil(k*r + max(10, 0.15*k*r))"
  r_in_eps: 1.0e-6
  r_out: 300.0
  ode_method: DOP853
  rtol: 1.0e-10
  atol: 1.0e-12
outputs:
  format: hdf5
  save_radial: true
  save_weyl: true
  save_plots_metadata: true
```

## configs/convergence_k1_r60.yaml

```yaml
background:
  name: schwarzschild
  M: 1.0
wave:
  kM_values: [1.0]
  A_plus: "0.9+1.1j"
  A_cross: "0.4+0.6j"
observer:
  kind: angular
  r_obs: 60.0
  theta_min: 0.0
  theta_max: 3.141592653589793
  n_theta: 800
  phi: 0.0
numerics:
  lmax_values: [40, 60, 75, 90]
  r_in_eps: 1.0e-6
  r_out: 300.0
  ode_method: DOP853
  rtol: 1.0e-10
  atol: 1.0e-12
outputs:
  format: hdf5
```
