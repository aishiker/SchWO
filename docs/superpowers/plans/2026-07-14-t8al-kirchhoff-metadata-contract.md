# T8al Kirchhoff Metadata Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add explicit units and dtype metadata to the accepted Kirchhoff review-grid artifact without changing any formula, branch, grid, or saved numerical array.

**Architecture:** Modify only the Kirchhoff artifact serializer and its focused contract test. Regenerate the same three ignored baseline files from the unchanged accepted T8aj input, and prove every non-metadata NPZ array is byte-identical to the T8ak version using frozen NumPy-array SHA-256 fingerprints.

**Tech Stack:** Python, NumPy, JSON, Markdown manifest, pytest, Ruff, project-local mpmath backend already installed in `.venv`.

---

## File Map And Hard Boundary

- Modify `src/schwgw/io/kirchhoff.py`: explicit array units/dtype mappings, schema v2, manifest contract.
- Modify `tests/unit/test_kirchhoff_artifact.py`: RED/GREEN assertions for embedded metadata, sidecar, manifest, and actual array dtypes.
- Regenerate only `runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz`, its JSON sidecar, and `manifest.md`.
- Modify `status.md`, `docs/handoffs/T8_current.md`, and the required T8 archive.

Do not modify the Eq. (47) compute module, script, IO exports, T8aj inputs,
production solver/transmission/Q018/polarization/viz/config/fixture paths, or
create any plot/dense-production/paper-style output.

### Task 1: Add Failing Units And Dtype Contract Tests

**Files:**
- Modify: `tests/unit/test_kirchhoff_artifact.py`

- [ ] **Step 1: Add exact expected mappings**

Add after `PAPER_XI`:

```python
EXPECTED_UNITS = {
    "kM_values": "dimensionless (M k)",
    "point_ids": "identifier",
    "point_x": "dimensionless (x/M)",
    "point_y": "dimensionless (y/M)",
    "point_z": "dimensionless (z/M)",
    "point_r": "dimensionless (r/M)",
    "point_theta": "radian",
    "paper_xi_over_xi0": "dimensionless",
    "gamma": "dimensionless",
    "eta": "dimensionless",
    "eta_minus_paper": "dimensionless",
    "F_kirchhoff_complex": "dimensionless",
    "abs_F_kirchhoff": "dimensionless",
    "arg_F_kirchhoff_principal": "radian",
    "arg_F_kirchhoff_unwrapped": "radian",
    "valid_kirchhoff_mask": "boolean",
}

EXPECTED_DTYPES = {
    "kM_values": "float64",
    "point_ids": "<U16",
    "point_x": "float64",
    "point_y": "float64",
    "point_z": "float64",
    "point_r": "float64",
    "point_theta": "float64",
    "paper_xi_over_xi0": "float64",
    "gamma": "float64",
    "eta": "float64",
    "eta_minus_paper": "float64",
    "F_kirchhoff_complex": "complex128",
    "abs_F_kirchhoff": "float64",
    "arg_F_kirchhoff_principal": "float64",
    "arg_F_kirchhoff_unwrapped": "float64",
    "valid_kirchhoff_mask": "bool",
}
```

- [ ] **Step 2: Extend the artifact contract test**

Inside the existing `with np.load(...)` block, add:

```python
        embedded = json.loads(str(data["metadata_json"].item()))
        assert embedded["schema_version"] == (
            "phase5_t8al_kirchhoff_review_grid_v2_units_dtype"
        )
        assert embedded["units"] == EXPECTED_UNITS
        assert embedded["dtype"] == EXPECTED_DTYPES
        for name, expected_dtype in EXPECTED_DTYPES.items():
            assert str(data[name].dtype) == expected_dtype
```

After loading the sidecar, add:

```python
    assert metadata["schema_version"] == (
        "phase5_t8al_kirchhoff_review_grid_v2_units_dtype"
    )
    assert metadata["units"] == EXPECTED_UNITS
    assert metadata["dtype"] == EXPECTED_DTYPES
    manifest_text = manifest.read_text(encoding="utf-8")
    assert "## Units and dtypes" in manifest_text
    for name in EXPECTED_UNITS:
        expected_line = (
            f"- `{name}`: unit=`{EXPECTED_UNITS[name]}`; "
            f"dtype=`{EXPECTED_DTYPES[name]}`"
        )
        assert expected_line in manifest_text
```

- [ ] **Step 3: Run the focused test and observe the required RED**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_kirchhoff_artifact.py -q
```

Expected: the contract test fails with `KeyError: 'units'` or the old schema
version. A different failure must be diagnosed before implementation.

### Task 2: Implement The Minimal Serializer Contract

**Files:**
- Modify: `src/schwgw/io/kirchhoff.py`
- Test: `tests/unit/test_kirchhoff_artifact.py`

- [ ] **Step 1: Add exact module constants**

Add below `_ETA_MISMATCH_LIMIT`:

```python
_ARRAY_UNITS = {
    "kM_values": "dimensionless (M k)",
    "point_ids": "identifier",
    "point_x": "dimensionless (x/M)",
    "point_y": "dimensionless (y/M)",
    "point_z": "dimensionless (z/M)",
    "point_r": "dimensionless (r/M)",
    "point_theta": "radian",
    "paper_xi_over_xi0": "dimensionless",
    "gamma": "dimensionless",
    "eta": "dimensionless",
    "eta_minus_paper": "dimensionless",
    "F_kirchhoff_complex": "dimensionless",
    "abs_F_kirchhoff": "dimensionless",
    "arg_F_kirchhoff_principal": "radian",
    "arg_F_kirchhoff_unwrapped": "radian",
    "valid_kirchhoff_mask": "boolean",
}

_EXPECTED_ARRAY_DTYPES = {
    "kM_values": "float64",
    "point_ids": "<U16",
    "point_x": "float64",
    "point_y": "float64",
    "point_z": "float64",
    "point_r": "float64",
    "point_theta": "float64",
    "paper_xi_over_xi0": "float64",
    "gamma": "float64",
    "eta": "float64",
    "eta_minus_paper": "float64",
    "F_kirchhoff_complex": "complex128",
    "abs_F_kirchhoff": "float64",
    "arg_F_kirchhoff_principal": "float64",
    "arg_F_kirchhoff_unwrapped": "float64",
    "valid_kirchhoff_mask": "bool",
}
```

- [ ] **Step 2: Build and validate output arrays before metadata**

Immediately after `baseline_metadata = dict(...)`, construct:

```python
    output_arrays = {
        **arrays,
        "gamma": result.gamma,
        "eta": eta,
        "eta_minus_paper": eta_minus_paper,
        "F_kirchhoff_complex": result.F_complex,
        "abs_F_kirchhoff": result.abs_F,
        "arg_F_kirchhoff_principal": result.arg_F_principal,
        "arg_F_kirchhoff_unwrapped": np.unwrap(
            result.arg_F_principal, axis=0
        ),
        "valid_kirchhoff_mask": result.valid_mask,
    }
    actual_dtypes = {
        name: str(np.asarray(value).dtype)
        for name, value in output_arrays.items()
    }
    if actual_dtypes != _EXPECTED_ARRAY_DTYPES:
        raise RuntimeError(
            "Kirchhoff artifact dtype contract mismatch: "
            f"expected {_EXPECTED_ARRAY_DTYPES}, got {actual_dtypes}"
        )
```

- [ ] **Step 3: Add explicit metadata and bump schema**

Replace the schema value and add two top-level fields:

```python
        "schema_version": "phase5_t8al_kirchhoff_review_grid_v2_units_dtype",
        "units": dict(_ARRAY_UNITS),
        "dtype": dict(actual_dtypes),
```

Keep every formula, branch, backend, hash, eta, and non-claim field unchanged.

- [ ] **Step 4: Save the validated array mapping**

Replace the repeated array arguments in `np.savez_compressed` with:

```python
    np.savez_compressed(
        output_npz,
        **output_arrays,
        metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)),
    )
```

- [ ] **Step 5: Add the manifest units/dtypes section**

In `_manifest_text`, before the closing triple quote, add:

```python
## Units and dtypes

{_array_contract_manifest()}
```

Add this helper below `_file_sha256`:

```python
def _array_contract_manifest() -> str:
    return "\n".join(
        f"- `{name}`: unit=`{_ARRAY_UNITS[name]}`; "
        f"dtype=`{_EXPECTED_ARRAY_DTYPES[name]}`"
        for name in _ARRAY_UNITS
    )
```

- [ ] **Step 6: Run focused tests and Ruff**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_kirchhoff.py tests/unit/test_kirchhoff_artifact.py -q
.venv/bin/python -m ruff check src/schwgw/io/kirchhoff.py tests/unit/test_kirchhoff_artifact.py
```

Expected: `9 passed` and Ruff clean.

- [ ] **Step 7: Commit only the contract code and test**

Run:

```bash
git add src/schwgw/io/kirchhoff.py tests/unit/test_kirchhoff_artifact.py
git diff --cached --check
git diff --cached --name-status
git commit -m "fix: record Kirchhoff units and dtypes"
```

Expected: exactly two paths in the commit.

### Task 3: Regenerate Three Files And Prove Numerical Identity

**Files:**
- Replace only: `runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz`
- Replace only: `runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json`
- Replace only: `runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md`

- [ ] **Step 1: Preserve a non-destructive temporary copy**

Run:

```bash
mkdir -p /tmp/schwo_t8al_pre_metadata_contract
cp runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz /tmp/schwo_t8al_pre_metadata_contract/
cp runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json /tmp/schwo_t8al_pre_metadata_contract/
cp runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md /tmp/schwo_t8al_pre_metadata_contract/
```

Expected: the three pre-hardening files remain available for byte-level array
comparison. Do not remove this temporary backup during T8al/T7bt.

- [ ] **Step 2: Regenerate through the unchanged formula API**

Run:

```bash
PYTHONPATH=src .venv/bin/python scripts/phase5_generate_kirchhoff_baseline.py --dps 60
```

Expected: exactly the same three project paths are rewritten. No fourth file
is created in the baseline directory.

- [ ] **Step 3: Prove every non-metadata array is byte-identical**

Run:

```bash
.venv/bin/python - <<'PY'
from io import BytesIO
import hashlib
import json
from pathlib import Path
import numpy as np

old = Path('/tmp/schwo_t8al_pre_metadata_contract/tablei_kirchhoff_baseline_values.npz')
new = Path('runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz')
expected = {
    'kM_values': '8b237c058da63a43ad3ea86ddc5a2a0587aeb0a06740649463f9660b1f905e5a',
    'point_ids': 'ac426fc8541c04f31a6821c08ea62ed7f1b3b9428cc43ebc053491945e9d25f1',
    'point_x': 'f0d3bf56c388ca014bbaa0dad2022c002712be1518db154795076f36b4246f0e',
    'point_y': '73379d1814b5c32537aba531a73cd69415e1d09e0c0a35eda7c8cb0527b62333',
    'point_z': '9ed95c4d6d729dee7212aa0ba35aaae5d70cc067cf2622aa142e7d6d147285fd',
    'point_r': 'a918d1c1ce9b5212567acd82eabc72cf48968d3e1a2e3929a5bae61775921eb4',
    'point_theta': '016363e3cb7f7e41f560fda97b1db4f18df700e5b03ea14e96a2474d3aeb3af6',
    'paper_xi_over_xi0': 'f1f6fb169498a07073dc184de5c9f764f1f9ea4b27badcfb699d9255b5446e98',
    'gamma': '5d3b7071226b2ad424f024b1fcb825390bc388b7be6aea539930d57735c065c5',
    'eta': 'ee471cd4fdad09f2e18650d9f9d6205b587f7304f756b34abc13ac827aaa4da7',
    'eta_minus_paper': '039685e159cffa49d74314bbd18d9819df3b86b7d3158f2a17601118fa6a4708',
    'F_kirchhoff_complex': 'b5597f571150db08b1b4da7db0d335b272c4dccea6e303ffe001ef774bf75a41',
    'abs_F_kirchhoff': '6bd20cd3f8cc521e6cd7e0b64c923d58c4a0e025b3a34baebf8d573dc3478d37',
    'arg_F_kirchhoff_principal': '536d21d52da3386c84deebf5205f72d5b98fc66d9876be9632957822416abecd',
    'arg_F_kirchhoff_unwrapped': '524da9ef8ed1caa758ca30b38f7f66d9a1639b1515d95d8dfcec4712c645cb6d',
    'valid_kirchhoff_mask': '1fa76763a67279c9ea7c301b9dd67f5c1f518e8ab4bed89f7817379b975dbbfe',
}

with np.load(old, allow_pickle=False) as before, np.load(new, allow_pickle=False) as after:
    assert set(before.files) == set(after.files)
    for name in before.files:
        if name == 'metadata_json':
            continue
        np.testing.assert_array_equal(after[name], before[name])
        buffer = BytesIO()
        np.save(buffer, after[name], allow_pickle=False)
        assert hashlib.sha256(buffer.getvalue()).hexdigest() == expected[name]
    embedded = json.loads(str(after['metadata_json'].item()))
    assert embedded['units']
    assert embedded['dtype']

print('T8AL_NUMERICAL_ARRAY_IDENTITY=PASS')
PY
```

Expected: `T8AL_NUMERICAL_ARRAY_IDENTITY=PASS`.

- [ ] **Step 4: Verify all three metadata surfaces**

Run:

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path
import numpy as np

p = Path('runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz')
side = json.loads(Path(str(p)+'.json').read_text())
with np.load(p, allow_pickle=False) as z:
    embedded = json.loads(str(z['metadata_json'].item()))
    assert embedded['units'] == side['units']
    assert embedded['dtype'] == side['dtype']
    for name, dtype in side['dtype'].items():
        assert str(z[name].dtype) == dtype
manifest = (p.parent/'manifest.md').read_text()
assert '## Units and dtypes' in manifest
for name in side['units']:
    assert f'`{name}`' in manifest
print('T8AL_METADATA_SURFACES=PASS')
PY
```

- [ ] **Step 5: Run full regression and forbidden-scope checks**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q
git diff -- src/schwgw/scattering src/schwgw/numerics src/schwgw/viz configs tests/regression/fixtures
find runs/phase5/fig5_fig6_review_grid_plots runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
shasum -a 256 runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json runs/phase5/fig5_fig6_dense_review_grid/manifest.md
shasum -a 256 runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md
```

Expected: full pytest passes; forbidden diff/output commands are empty; T8aj
hashes remain unchanged; new T8al hashes are recorded.

### Task 4: Record T8al And Auto-Dispatch T7bt

**Files:**
- Modify: `status.md`
- Modify/archive: `docs/handoffs/T8_current.md`, `docs/handoffs/archive/T8_2026-07-14_pre_t8al_metadata_contract.md`

- [ ] **Step 1: Record one exact decision**

```text
GREEN / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT HARDENED
YELLOW / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT PARTIAL
RED / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT BLOCKED
```

GREEN requires RED→GREEN tests, explicit fields on all three surfaces,
byte-identical non-metadata arrays, unchanged T8aj hashes, new artifact hashes,
focused/Ruff/full-pytest PASS, and empty forbidden checks.

- [ ] **Step 2: Dispatch T7bt only after exact GREEN and fresh doc checks**

Send this message to existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` using `gpt-5.6-sol`, thinking `high`:

```text
你现在是 T7bt：Fig.5/Fig.6 Kirchhoff units/dtype metadata-contract 独立复核线程。请读取并严格执行 docs/prompts/phase5_t7bt_fig5_fig6_kirchhoff_metadata_contract_review.md。T8al 只允许补齐 metadata/schema/tests 并替换三份 baseline 文件；请独立证明所有非 metadata 数值数组与 T8ak 逐字节相同，复核 embedded JSON、sidecar、manifest 的 units/dtype 与实际 dtype 一致。不得修改实现或 artifact，不得生成 plots/dense production。完成后把 exact decision 发给 T0 task 019f5ec5-84ba-79e2-8c77-1160b150a636。
```

Also notify T0. On YELLOW/RED/incomplete/ambiguous state, do not start T7bt;
notify T0 only. Do not create a new task.

## Execution Route

The user already authorized execution in the existing T8 task and automatic
review dispatch. This supersedes the generic execution-choice question. T8al
must use `executing-plans`, TDD, and verification-before-completion.
