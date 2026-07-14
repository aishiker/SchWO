# T8 Handoff Archive — Pre-T8am Review-Grid Diagnostics

Archived: 2026-07-14

This archive supersedes the prior T8al current handoff. Its exact decision was:

```text
GREEN / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT HARDENED
```

T8al’s metadata-only commit was `7966be1 fix: record Kirchhoff units and
dtypes`. It preserved all 16 non-metadata arrays byte-for-byte, retained the
accepted Eq. (47) scalar, polarization-independent Kirchhoff boundary, and
produced the frozen baseline triplet:

```text
66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55  tablei_kirchhoff_baseline_values.npz
0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3  tablei_kirchhoff_baseline_values.npz.json
fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632  manifest.md
```

The successor T8am task may only consume this accepted baseline read-only,
together with the accepted T8aj 18×8 exact review-grid triplet. It does not
reopen T8al’s serializer/schema work or authorize any solver, production,
interpolation, smoothing, fixture, or paper-style work.
