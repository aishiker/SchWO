# T4 Current Handoff

Last updated: 2026-07-23
Thread: T4ad, another bounded local radial/Q018 gate.

## Exact decision

```text
GREEN / ANOTHER BOUNDED LOCAL RADIAL GATE READY
```

## Frozen evidence

- Exact 55 T7cd failed-child midpoint frequencies, both sectors, eight
  Table-I points, every `ell=2..ell_max`, 239,120 classification records,
  maximum lmax 360, and unchanged numerical/physical conventions.
- Classification: 226,628 default-covered, 12,402 structured uncovered,
  90 structured solver-failed, zero default-other; 12,492 measured transitions.
- Direct oracle: 12,492/12,492 PASS. Max effective residual
  `8.643830320073589e-16`, max condition number `4.0205536912751665`, max
  relative sensitivity `1.765777535540243e-07`; 578 sensitivity records.
- Integrated adapter preflight: 12,492/12,492 PASS, zero failures; max
  effective residual `7.59360758732996e-16`, max condition number
  `4.020553691275165`, and max relative differences `psi=6.215365262365411e-14`,
  `dpsi_dr=6.214996947680988e-14`, `A_out=1.5958845589774503e-13`.
- All 55 atomic checkpoints are complete/PASS. Their ordered SHA-256 ledger is
  frozen in `runs/phase5/fig5_fig6_another_bounded_local_radial_gate/manifest.md`
  and the classification root `checkpoint_sha256` mapping.

## Provenance

- Frozen candidate `9a12fef8e09a46b4ed738723f4127896e64bf4c1`, parent
  `366a517c71b56026bb0f3ca37c14cc75243985b2`.
- Exact-five implementation commit `6b613b475054cecd8ff420c7eb7e1781375c0412`,
  parent exactly the candidate.
- Five blobs: runner `b4966db986a001cbc2ecb6bbe66f58ccc51bb1a1`;
  envelope `11022606a5230b103a9d5d2ed911d8d837f01a37`; radial solver
  `7fe2192d311a1e7215ca56f61dae9dbeadac41fd`; integration test
  `e87ab8535f0f0ddf63e47bdd3610bd3936a27c9d`; radial test
  `5b3347f0fab25d9e2de82fd018e4aa171e058928`.
- Classification snapshot
  `9f8c99dae0c182183a5e54d8bc8371e55f28ef2004dc928ad087829d33710bf7`;
  final-adapter snapshot
  `93f78fbce379fc217c3cf8b3f5b8ae33567b0404e46ba33fad39f323a68ca01b`.
- Roots: classification `73773920be54713bd4dc1e276075212d214b82e978b01078574c935bb23f07e7`;
  oracle `9a5c8beafbe132aff360ad6f1015835b2fe7d3118cfa4fa3762b37f04f920368`;
  preflight `4be554c10536c69dc2f6c140a41fa246829b9ca7d16c192deff6f26129ac8163`;
  manifest `5ef65859eb585cb76cf2fd68f8ecc4e9130cb3104ad17c239abb62e273ab176f`.

## Verification and scope

- Runner audit PASS: 239,120 records, 12,492 transitions, 55 checkpoints.
- Post-preflight focused pytest: 360 passed, 67 warnings, 41 subtests.
- Ruff and `git diff --check`: PASS.
- Fresh full pytest: 674 passed, 117 skipped, 1 xfailed, 103 warnings,
  104 subtests.
- Exact-five commit scope, committed/worktree blob identity, roots,
  provenance, warning classification, and forbidden-output searches PASS.

No threshold relaxation, lmax extension, recursive/automatic midpoint,
uniform/full grid, amplification, production, plot, fixture, Kirchhoff,
paper-style output, task creation/replacement, GitHub action, or T7ce/T8as/T7cf
dispatch occurred. T4ad returns only to T0 and pauses.
