# T4 archive — V3.1 mode-greybody terminal failure

Date: 2026-08-11

## Exact boundary

```text
root runs/phase6/classic_scattering/v3_1_mode_greybody_r1_20260811T120717Z_py314
manifest 78ee1b9b9c9490ddb438639d175a7e9f0ec4b46985c7d35fc604f4a497e0e319
state FAILED_SCIENTIFIC
Route-A attempts/completed 1/0
Route-B attempts/completed 0/0
Route-C attempts/completed 0/0
```

The external runtime blocker was resolved before launch: exact Wolfram kernel
`70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c`
ran a fresh BHPT ReggeWheeler MST smoke successfully.

The first frozen Route-A node (`kM=0.005`, odd, `ell=2`, `r_in_eps=1e-8`,
`r_out=489.8979485566356`, Jost order 160, `rtol=1e-10`, `atol=1e-12`)
failed natively: stabilized BVP reported a singular Jacobian and the protected
bidirectional fallback reported a non-monotonic grid. A separate post-seal
control failure found the one canonical ladder record formatted as multiline
JSON rather than one JSONL line. No retry or mutation is authorized.

The root remains immutable (`0555`; direct files `0444`, nlink1). Numerical
certificate is `FAIL`; all other certificates and independent review are
`NOT_ASSESSED`; `global_status=null`, global GREEN false. V3.2 is forbidden.
