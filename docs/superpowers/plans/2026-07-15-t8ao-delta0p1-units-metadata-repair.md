# T8ao Delta(kM)=0.1 Units Metadata Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the active T8an risk-pilot metadata contract by recording exact units and ordering while proving every saved non-metadata NumPy array is unchanged.

**Architecture:** Keep the v1 scientific generation contract immutable and add a separate v2 metadata contract. A dedicated migration path validates the frozen 23-file package, preserves an in-project byte-for-byte backup, constructs a fully validated candidate tree without calling scientific code, and atomically replaces active files through a resumable journal.

**Tech Stack:** Python 3.10+, NumPy, JSON, Markdown manifest, pathlib/shutil, pytest, Ruff, SHA-256.

---

## File Map And Hard Boundary

Implementation commit paths are exactly:

```text
src/schwgw/io/tablei_risk_pilot.py
scripts/phase5_repair_delta0p1_risk_pilot_metadata.py
tests/unit/test_tablei_risk_pilot.py
tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
```

Generated and coordination paths are separate:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot/
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-15_pre_t8ao_units_metadata_repair.md
```

Do not modify `SCHEMA_VERSION`; it remains
`phase5_t8an_delta0p1_risk_pilot_v1` and is part of the immutable scientific
generation provenance. Do not change the T8an runner, IO exports, solver,
adapter, cache, physics, lmax, points, frequencies, thresholds, accepted
inputs, plots, fixtures, or paper outputs.

This plan authorizes no `0.05`, `0.025`, full-grid, plotting, fixture,
Kirchhoff, interpolation, smoothing, fill, or paper-style computation.

## Frozen Active Package

The migration starts only if all five root hashes match:

```text
79d4c0f596650dcfb4d63c7e40758ea4afa82d2fe0e0cd3de5aa088bbbfd5ccd  checkpoint_ledger.json
2e0a9fee1b6729466affd4c5f7f6e86c96e696e20882c9f4ad52ae3792d82957  risk_pilot_values.npz
2a9aa472e64747047cb28de90912eecf138b28884d87e8b8219e78d99482772f  risk_pilot_values.npz.json
461d040a180dfa8e5a743967285e67f8b682f8f67607f1c0c7a5c8ab2399d7bd  risk_pilot_sampling_audit.json
120ccd8f11e681bc6d2b3054bd7522ef331a282421f7661dd7888c993b052212  manifest.md
```

The active tree has exactly 23 files excluding every `quarantine/` subtree.
The manifest has exactly 22 non-self entries.

### Task 1: Add TDD RED For The Metadata-Only Contract

**Files:**
- Modify: `tests/unit/test_tablei_risk_pilot.py`
- Create: `tests/regression/test_delta0p1_risk_pilot_metadata_repair.py`

- [ ] **Step 1: Add the new public-in-module imports to the unit test**

Extend the existing import from `schwgw.io.tablei_risk_pilot` with:

```python
from schwgw.io.tablei_risk_pilot import (
    GENERATION_CONTRACT_HASH,
    METADATA_REPAIR_ID,
    METADATA_SCHEMA_VERSION,
    ORDERING_CONTRACT,
    UNITS_CONTRACT,
    repair_delta0p1_risk_pilot_metadata,
)
```

- [ ] **Step 2: Add exact constant assertions**

```python
def test_t8ao_metadata_contract_constants() -> None:
    assert GENERATION_CONTRACT_HASH == (
        "92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9"
    )
    assert METADATA_SCHEMA_VERSION == (
        "phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering"
    )
    assert METADATA_REPAIR_ID == "T8ao/T7bx-units-ordering"
    assert ORDERING_CONTRACT["frequency_order"] == list(PILOT_FREQUENCIES)
    assert ORDERING_CONTRACT["point_order"] == [
        point.point_id for point in pilot.TABLEI_POINTS
    ]
    assert set(UNITS_CONTRACT) == {
        "per_frequency_arrays",
        "aggregate_arrays",
        "numeric_metadata",
    }
```

- [ ] **Step 3: Add an isolated copy-of-frozen-package regression fixture**

Create `tests/regression/test_delta0p1_risk_pilot_metadata_repair.py`. The
fixture copies the durable v1 source backup when it exists and otherwise
copies the current pre-repair active tree. It never calls a scientific runner:

```python
from __future__ import annotations

from io import BytesIO
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import NoReturn

import numpy as np
import pytest

import schwgw.io.tablei_risk_pilot as pilot
from schwgw.io.tablei_risk_pilot import (
    METADATA_SCHEMA_VERSION,
    PilotContractError,
    repair_delta0p1_risk_pilot_metadata,
)


_PROJECT_PACKAGE = Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot")
_DURABLE_SOURCE = (
    _PROJECT_PACKAGE
    / "quarantine"
    / "t8ao_pre_units_metadata"
    / "source"
)


def _frozen_source() -> Path:
    source = _DURABLE_SOURCE if _DURABLE_SOURCE.is_dir() else _PROJECT_PACKAGE
    if not (source / "manifest.md").is_file():
        pytest.skip("frozen T8an package is unavailable")
    return source


def _copy_frozen_v1_package(tmp_path: Path) -> Path:
    source = _frozen_source()
    output = tmp_path / "risk_pilot"
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if "quarantine" in relative.parts:
            continue
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    return output


def _canonical_array_fingerprints(root: Path) -> dict[str, str]:
    paths = tuple(sorted((root / "frequencies").glob("*.npz"))) + (
        root / "risk_pilot_values.npz",
    )
    result: dict[str, str] = {}
    for path in paths:
        with np.load(path, allow_pickle=False) as data:
            for name in data.files:
                if name == "metadata_json":
                    continue
                stream = BytesIO()
                np.save(stream, data[name], allow_pickle=False)
                key = f"{path.relative_to(root)}::{name}"
                result[key] = hashlib.sha256(stream.getvalue()).hexdigest()
    return dict(sorted(result.items()))


def _assert_all_required_metadata_surfaces(root: Path) -> None:
    json_paths = tuple(sorted((root / "frequencies").glob("*.npz.json"))) + (
        root / "risk_pilot_values.npz.json",
        root / "checkpoint_ledger.json",
        root / "risk_pilot_sampling_audit.json",
    )
    for path in json_paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        assert value["schema_version"] == METADATA_SCHEMA_VERSION
        assert value["units"] == pilot.UNITS_CONTRACT
        assert value["ordering"] == pilot.ORDERING_CONTRACT
        assert value["generation_contract_hash"] == pilot.GENERATION_CONTRACT_HASH
        assert value["metadata_contract_hash"]
    for path in tuple(sorted((root / "frequencies").glob("*.npz"))) + (
        root / "risk_pilot_values.npz",
    ):
        with np.load(path, allow_pickle=False) as data:
            value = json.loads(str(data["metadata_json"].item()))
        assert value["schema_version"] == METADATA_SCHEMA_VERSION
        assert value["units"] == pilot.UNITS_CONTRACT
        assert value["ordering"] == pilot.ORDERING_CONTRACT
    manifest = (root / "manifest.md").read_text(encoding="utf-8")
    assert "## Units" in manifest
    assert "## Ordering" in manifest
```

Then add:

```python
def test_metadata_repair_preserves_arrays_and_never_calls_science(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    before = _canonical_array_fingerprints(output)

    def forbidden(*args: object, **kwargs: object) -> NoReturn:
        del args, kwargs
        raise AssertionError("scientific compute path called by metadata repair")

    monkeypatch.setattr(pilot, "compute_polarization", forbidden)
    monkeypatch.setattr(pilot, "compute_flat_no_lens_polarization", forbidden)
    monkeypatch.setattr(pilot, "solve_radial_mode", forbidden)
    monkeypatch.setattr(pilot, "_compute_frequency", forbidden)
    monkeypatch.setattr(pilot, "run_delta0p1_risk_pilot", forbidden)

    repaired = repair_delta0p1_risk_pilot_metadata(output_dir=output)
    assert repaired == output / "risk_pilot_values.npz"
    assert _canonical_array_fingerprints(output) == before
    _assert_all_required_metadata_surfaces(output)
```

- [ ] **Step 4: Add failure and resume coverage**

Add these exact tests:

```python
def test_metadata_repair_stops_on_active_hash_mismatch(tmp_path: Path) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    sidecar = output / "frequencies" / "kM_0p4.npz.json"
    sidecar.write_bytes(sidecar.read_bytes() + b" ")
    with pytest.raises(PilotContractError, match="pre-repair|manifest|hash"):
        repair_delta0p1_risk_pilot_metadata(output_dir=output)


def test_metadata_repair_stops_on_tampered_backup(tmp_path: Path) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    repair_delta0p1_risk_pilot_metadata(output_dir=output)
    backup_manifest = (
        output
        / "quarantine"
        / "t8ao_pre_units_metadata"
        / "source"
        / "manifest.md"
    )
    backup_manifest.write_bytes(backup_manifest.read_bytes() + b"tampered")
    with pytest.raises(PilotContractError, match="backup|source|hash"):
        repair_delta0p1_risk_pilot_metadata(output_dir=output)


def test_metadata_repair_resumes_a_mixed_active_tree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    before = _canonical_array_fingerprints(output)
    real_replace = os.replace
    active_replacements = 0

    def interrupt(source: str | Path, destination: str | Path) -> None:
        nonlocal active_replacements
        source_path = Path(source)
        destination_path = Path(destination)
        if (
            source_path.name.endswith(".t8ao-install.tmp")
            and output in destination_path.parents
        ):
            active_replacements += 1
            if active_replacements == 5:
                raise OSError("synthetic T8ao interruption")
        real_replace(source, destination)

    monkeypatch.setattr(pilot.os, "replace", interrupt)
    with pytest.raises(OSError, match="synthetic T8ao interruption"):
        repair_delta0p1_risk_pilot_metadata(output_dir=output)
    monkeypatch.setattr(pilot.os, "replace", real_replace)

    repair_delta0p1_risk_pilot_metadata(output_dir=output)
    assert _canonical_array_fingerprints(output) == before
    _assert_all_required_metadata_surfaces(output)


def test_metadata_repair_rejects_units_or_ordering_drift(tmp_path: Path) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    repair_delta0p1_risk_pilot_metadata(output_dir=output)
    candidate = (
        output
        / "quarantine"
        / "t8ao_pre_units_metadata"
        / "candidate"
        / "risk_pilot_sampling_audit.json"
    )
    value = json.loads(candidate.read_text(encoding="utf-8"))
    value["ordering"]["frequency_order"] = list(reversed(pilot.PILOT_FREQUENCIES))
    candidate.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    with pytest.raises(PilotContractError, match="candidate|ordering|hash"):
        repair_delta0p1_risk_pilot_metadata(output_dir=output)


def test_scientific_runner_rejects_a_metadata_repaired_package(
    tmp_path: Path,
) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    repair_delta0p1_risk_pilot_metadata(output_dir=output)
    with pytest.raises(PilotContractError, match="metadata-repaired package"):
        pilot.run_delta0p1_risk_pilot(output_dir=output, resume=True)
```

The public function must validate the durable source and candidate even after
the ledger says `complete`; a completed ledger never suppresses integrity
checks.

- [ ] **Step 5: Run the focused tests and observe the required RED**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_tablei_risk_pilot.py \
  tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
```

Expected: collection fails because the six new symbols do not yet exist. A
different failure must be diagnosed before implementation.

### Task 2: Define Exact Units, Ordering, And Metadata Identity

**Files:**
- Modify: `src/schwgw/io/tablei_risk_pilot.py`
- Test: `tests/unit/test_tablei_risk_pilot.py`

- [ ] **Step 1: Add immutable metadata constants without changing v1**

Add below `SCHEMA_VERSION`:

```python
GENERATION_CONTRACT_HASH = (
    "92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9"
)
METADATA_SCHEMA_VERSION = (
    "phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering"
)
METADATA_REPAIR_ID = "T8ao/T7bx-units-ordering"
_PRE_REPAIR_ROOT_HASHES = {
    "checkpoint_ledger.json": "79d4c0f596650dcfb4d63c7e40758ea4afa82d2fe0e0cd3de5aa088bbbfd5ccd",
    "risk_pilot_values.npz": "2e0a9fee1b6729466affd4c5f7f6e86c96e696e20882c9f4ad52ae3792d82957",
    "risk_pilot_values.npz.json": "2a9aa472e64747047cb28de90912eecf138b28884d87e8b8219e78d99482772f",
    "risk_pilot_sampling_audit.json": "461d040a180dfa8e5a743967285e67f8b682f8f67607f1c0c7a5c8ab2399d7bd",
    "manifest.md": "120ccd8f11e681bc6d2b3054bd7522ef331a282421f7661dd7888c993b052212",
}
```

- [ ] **Step 2: Add exact array-unit registries**

```python
_PER_FREQUENCY_ARRAY_UNITS = {
    "kM": "dimensionless (M k)",
    "point_ids": "identifier",
    "point_group": "category label",
    "point_x": "M",
    "point_y": "M",
    "point_z": "M",
    "point_r": "M",
    "point_theta": "radian",
    "point_phi": "radian",
    "lmax_values": "dimensionless integer",
    "F_plus_history": "dimensionless complex amplification",
    "F_cross_history": "dimensionless complex amplification",
    "F_plus_complex": "dimensionless complex amplification",
    "F_cross_complex": "dimensionless complex amplification",
    "abs_F_plus": "dimensionless",
    "abs_F_cross": "dimensionless",
    "arg_F_plus_principal": "radian",
    "arg_F_cross_principal": "radian",
    "valid_ratio_plus_mask": "boolean",
    "valid_ratio_cross_mask": "boolean",
    "final_pair_delta_plus": "dimensionless",
    "final_pair_delta_cross": "dimensionless",
}

_AGGREGATE_ARRAY_UNITS = {
    "kM_values": "dimensionless (M k)",
    "point_ids": "identifier",
    "point_group": "category label",
    "point_x": "M",
    "point_y": "M",
    "point_z": "M",
    "point_r": "M",
    "point_theta": "radian",
    "point_phi": "radian",
    "F_plus_complex": "dimensionless complex amplification",
    "F_cross_complex": "dimensionless complex amplification",
    "abs_F_plus": "dimensionless",
    "abs_F_cross": "dimensionless",
    "arg_F_plus_principal": "radian",
    "arg_F_cross_principal": "radian",
    "valid_ratio_plus_mask": "boolean",
    "valid_ratio_cross_mask": "boolean",
    "final_pair_delta_plus": "dimensionless",
    "final_pair_delta_cross": "dimensionless",
    "arg_F_plus_unwrapped": "radian",
    "arg_F_cross_unwrapped": "radian",
}

_NUMERIC_METADATA_UNITS = {
    "kM": "dimensionless (M k)",
    "frequencies": "dimensionless (M k)",
    "lmax_values": "dimensionless integer",
    "final_lmax_pair": "dimensionless integer",
    "runtime_seconds": "second",
    "radial_solve_count": "count",
    "radial_reuse_count": "count",
    "radial_warning_count": "count",
    "adapter_use_count": "count",
    "max_final_pair_delta_plus": "dimensionless",
    "max_final_pair_delta_cross": "dimensionless",
    "shape": "count",
    "sequence": "dimensionless (M k)",
    "complex_values": "dimensionless complex amplification",
    "magnitude": "dimensionless",
    "relative_magnitude_steps": "dimensionless",
    "magnitude_total_variation": "dimensionless",
    "max_relative_magnitude_step": "dimensionless",
    "unwrapped_phase": "radian",
    "absolute_phase_steps": "radian",
    "phase_total_variation": "radian",
    "max_absolute_phase_step": "radian",
    "interior_extrema.sequence_index": "count",
    "interior_extrema.point_index": "count",
}

UNITS_CONTRACT = {
    "per_frequency_arrays": _PER_FREQUENCY_ARRAY_UNITS,
    "aggregate_arrays": _AGGREGATE_ARRAY_UNITS,
    "numeric_metadata": _NUMERIC_METADATA_UNITS,
}
```

- [ ] **Step 3: Add exact ordering**

```python
ORDERING_CONTRACT = {
    "frequency_order": list(PILOT_FREQUENCIES),
    "point_order": [
        "near_axis_x0_z30",
        "near_axis_x1_z30",
        "near_axis_x2_z30",
        "near_axis_x3_z30",
        "far_axis_x10_z30",
        "far_axis_x15_z30",
        "far_axis_x20_z30",
        "far_axis_x25_z30",
    ],
    "per_frequency_history_axes": ["lmax", "point"],
    "per_frequency_final_axes": ["point"],
    "aggregate_field_axes": ["frequency", "point"],
    "lmax_values": {
        str(kM): list(PILOT_LMAX_VALUES[kM]) for kM in PILOT_FREQUENCIES
    },
}
```

- [ ] **Step 4: Add canonical fingerprint and contract helpers**

Implement these exact interfaces:

```python
def _canonical_array_fingerprint(value: np.ndarray) -> str:
    buffer = BytesIO()
    np.save(buffer, np.asarray(value), allow_pickle=False)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def _active_npz_paths(root: Path) -> tuple[Path, ...]:
    return tuple(sorted((root / "frequencies").glob("*.npz"))) + (
        root / "risk_pilot_values.npz",
    )


def _canonical_array_fingerprints(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in _active_npz_paths(root):
        with np.load(path, allow_pickle=False) as data:
            for name in data.files:
                if name != "metadata_json":
                    key = f"{path.relative_to(root)}::{name}"
                    result[key] = _canonical_array_fingerprint(data[name])
    return dict(sorted(result.items()))
```

Build `metadata_contract_hash` from canonical compact JSON containing exactly
the v2 schema, units contract, ordering contract, immutable generation hash,
frozen pre-repair manifest hash, and sorted fingerprint map.

- [ ] **Step 5: Run the constant/helper tests**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_tablei_risk_pilot.py -k 'metadata_contract or fingerprint'
```

Expected: the new pure-contract tests pass; migration tests may still fail.

### Task 3: Implement A Durable, Resumable Metadata Migration

**Files:**
- Modify: `src/schwgw/io/tablei_risk_pilot.py`
- Test: `tests/regression/test_delta0p1_risk_pilot_metadata_repair.py`

- [ ] **Step 1: Freeze the exact repair layout**

```text
quarantine/t8ao_pre_units_metadata/
  source/<23 original active relative paths>
  candidate/<23 repaired active relative paths>
  repair_ledger.json
```

The repair ledger stores `state`, all 23 source hashes, all 23 candidate
hashes after staging, the canonical fingerprint map, metadata-contract hash,
and sorted `replaced_paths`. Existing
`quarantine/runner_cache_domain_pre_47c3d63/` is untouched.

- [ ] **Step 2: Validate the original package before any copy**

Implement `_validate_pre_repair_active_tree(root)` to require:

```python
assert _sha256(root / "manifest.md") == _PRE_REPAIR_ROOT_HASHES["manifest.md"]
assert len(_active_relative_files(root)) == 23
assert len(_parse_manifest(root / "manifest.md")) == 22
```

The parser must validate every manifest path, byte size, and SHA-256. It must
reject absolute paths, `..`, duplicates, missing files, extra active files,
temporary files, and any manifest self-entry.

Before this preflight, the public repair function checks whether the repair
ledger already exists. With no ledger it requires the exact all-v1 tree. With
an existing ledger it validates durable source and candidate trees first, then
validates each active path against the journaled source-or-candidate state;
it must not incorrectly demand that a partially replaced tree still have the
old root hashes.

Freshly call `_input_records(_DEFAULT_REVIEW_NPZ, _DEFAULT_GATE_DIR)` and
require its six exact hashes to equal the preserved ledger/source metadata.
Do not call `_validate_start_gate`, because T7bw RED—not T7bv GREEN—is the
current repair start gate.

- [ ] **Step 3: Create or resume the byte-preserving source backup**

Write the initial ledger atomically before copying. Copy one file at a time
with `shutil.copy2`; after each copy verify the frozen SHA-256 and update the
ledger. On resume, every existing backup file must match its recorded source
hash; missing files may be copied, but a mismatch is a hard stop.

- [ ] **Step 4: Build common repair metadata**

```python
common = {
    "schema_version": METADATA_SCHEMA_VERSION,
    "generation_contract_hash": GENERATION_CONTRACT_HASH,
    "contract_hash": GENERATION_CONTRACT_HASH,
    "metadata_contract_hash": metadata_contract_hash,
    "metadata_only_repair": True,
    "metadata_repair_id": METADATA_REPAIR_ID,
    "units": UNITS_CONTRACT,
    "ordering": ORDERING_CONTRACT,
    "source_hashes": source_hashes,
    "pre_repair_provenance": {
        "manifest_sha256": _PRE_REPAIR_ROOT_HASHES["manifest.md"],
        "root_sha256": _PRE_REPAIR_ROOT_HASHES,
    },
}
```

Merge this into each legacy metadata object. Preserve every legacy value not
explicitly replaced by the v2 schema/contract additions. Do not refresh the
legacy `git`, `selected_code_hashes`, runtimes, warnings, cache counts, lmax,
or scientific values.

- [ ] **Step 5: Stage the nine frequency pairs**

For each source frequency NPZ, copy every non-`metadata_json` array exactly,
replace only `metadata_json`, write the candidate NPZ atomically, calculate
its hash, then write the candidate sidecar with that new `npz_sha256`. Require
the units registry keys to equal the non-metadata NPZ key set exactly.

- [ ] **Step 6: Stage aggregate, audit, ledger, and manifest**

Stage in dependency order:

1. aggregate NPZ and its sidecar, preserving nested frequency metadata except
   for the authorized common additions and changed NPZ hashes;
2. sampling audit with common contract fields and no changed sequence record;
3. checkpoint ledger with updated nine NPZ/JSON hashes, the complete
   fingerprint map, units, ordering, and unchanged scientific counters;
4. manifest last, containing exactly 22 candidate hashes plus human-readable
   `## Units`, `## Ordering`, `generation_contract_hash`, and
   `metadata_contract_hash` sections.

- [ ] **Step 7: Validate the complete candidate before replacement**

Require candidate active cardinality 23, manifest records 22, all required
metadata surfaces, exact units-key coverage, exact ordering, source hashes,
legacy-field preservation, and old/candidate array equality by key, shape,
dtype, `np.array_equal`, and canonical fingerprint.

- [ ] **Step 8: Replace through the journal and support mixed-tree resume**

Replace each active path only after candidate validation. After every
replacement append its relative path to `replaced_paths` and atomically update
the ledger. On resume, paths in `replaced_paths` must match candidate hashes
and all other active paths must match source hashes. Any third state is a hard
stop.

Because `os.replace` consumes its source, copy each validated candidate to an
active sibling named `<active-name>.t8ao-install.tmp`, verify that temporary
against the candidate hash, and replace from the temporary. Keep the canonical
candidate tree intact for T7bx. On resume, a matching install temporary may be
reused or recreated; a mismatching one is a hard stop. No install temporary
may remain after completion.

During a journaled mixed-tree resume, active enumeration may tolerate only the
single ledger-associated install temporary whose hash equals its candidate.
It is excluded from the final 23-file count and must disappear before the
ledger becomes complete.

- [ ] **Step 9: Add the public repair entry point**

```python
def repair_delta0p1_risk_pilot_metadata(
    *,
    output_dir: str | Path = _DEFAULT_OUTPUT_DIR,
) -> Path:
    """Harden only T8an metadata; never recompute scientific values."""
```

The function returns the active aggregate NPZ only after a final direct audit
marks the repair ledger `complete`. Add it to this module's `__all__`, but do
not change `src/schwgw/io/__init__.py`.

Add a fail-closed guard at the beginning of `run_delta0p1_risk_pilot`: if the
T8ao repair ledger exists, raise:

```python
raise PilotContractError(
    "metadata-repaired package is immutable; scientific runner forbidden"
)
```

This check occurs before `_validate_start_gate` or any compute selection and
prevents a later v1 resume from downgrading the repaired v2 surfaces.

- [ ] **Step 10: Run all focused tests**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_tablei_risk_pilot.py \
  tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
```

Expected: all focused tests pass, including interruption resume and
fail-on-call science isolation.

### Task 4: Add The Thin Repair CLI

**Files:**
- Create: `scripts/phase5_repair_delta0p1_risk_pilot_metadata.py`
- Modify: `tests/regression/test_delta0p1_risk_pilot_metadata_repair.py`

- [ ] **Step 1: Implement the exact CLI**

```python
from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.io.tablei_risk_pilot import (
    PilotContractError,
    repair_delta0p1_risk_pilot_metadata,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Repair only the Delta(kM)=0.1 risk-pilot metadata contract"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        repair_delta0p1_risk_pilot_metadata(output_dir=args.output_dir)
    except PilotContractError as exc:
        print(f"risk-pilot metadata repair error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Test the script boundary**

Import the script module, monkeypatch only
`repair_delta0p1_risk_pilot_metadata`, and require it receives exactly the
provided `Path`. Assert the script contains no reference to
`run_delta0p1_risk_pilot`, `compute_polarization`, `solve_radial_mode`,
`schwgw.viz`, `kirchhoff`, or any frequency argument.

- [ ] **Step 3: Run focused tests and Ruff**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_tablei_risk_pilot.py \
  tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
.venv/bin/python -m ruff check \
  src/schwgw/io/tablei_risk_pilot.py \
  scripts/phase5_repair_delta0p1_risk_pilot_metadata.py \
  tests/unit/test_tablei_risk_pilot.py \
  tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
```

Expected: all tests pass and Ruff reports `All checks passed!`.

- [ ] **Step 4: Commit exactly the four implementation/test paths**

```bash
git add \
  src/schwgw/io/tablei_risk_pilot.py \
  scripts/phase5_repair_delta0p1_risk_pilot_metadata.py \
  tests/unit/test_tablei_risk_pilot.py \
  tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
git diff --cached --check
git diff --cached --name-only
git commit -m "fix: harden risk-pilot units metadata"
```

Expected: exactly four paths in the implementation commit.

### Task 5: Repair The Active Package Without Scientific Recompute

**Files:**
- Replace metadata bytes only under: `runs/phase5/fig5_fig6_delta0p1_risk_pilot/`

- [ ] **Step 1: Run the frozen preflight**

```bash
shasum -a 256 \
  runs/phase5/fig5_fig6_delta0p1_risk_pilot/checkpoint_ledger.json \
  runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_values.npz \
  runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_values.npz.json \
  runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_sampling_audit.json \
  runs/phase5/fig5_fig6_delta0p1_risk_pilot/manifest.md
```

Expected: exactly the five frozen hashes at the top of this plan. Also require
23 active files, 22 manifest records, no active `.tmp`, and the six frozen
T8aj/T4z source hashes from the design.

- [ ] **Step 2: Run only the repair CLI**

```bash
PYTHONPATH=src .venv/bin/python \
  scripts/phase5_repair_delta0p1_risk_pilot_metadata.py
```

Expected: no scientific solver output; the repair ledger reaches `complete`.

- [ ] **Step 3: Run an independent old/new array audit**

Use a standalone Python command that does not import
`schwgw.io.tablei_risk_pilot`. Load all ten source-backup and active NPZ pairs,
require identical non-metadata key sets, shapes, dtypes,
`np.testing.assert_array_equal`, and identical canonical `.npy` SHA-256.
Print exactly:

```text
T8AO_NUMERICAL_ARRAY_IDENTITY=PASS
```

- [ ] **Step 4: Run an independent metadata-surface audit**

Directly load all nine embedded metadata objects, nine sidecars, aggregate
embedded/sidecar, ledger, audit, manifest, repair ledger, and candidate/source
trees. Require exact v2 schema, generation/metadata hash split, units,
ordering, fingerprints, 23/22 cardinality, old hashes, candidate hashes, and
actual NPZ array-key coverage. Print exactly:

```text
T8AO_METADATA_SURFACES_AND_PROVENANCE=PASS
```

- [ ] **Step 5: Prove scientific records were preserved without recomputation**

Require old/new sampling `sequences` to be JSON-semantically identical and all
non-metadata arrays to be exactly identical. Then record, without independently
recomputing metrics, the frozen facts: all masks true; final-pair maxima
`6.136118112992297e-11` plus and `5.492389935680416e-10` cross; 224 finite
phase steps with frozen maximum `1.4363184904108022`; 38 magnitude-dominance
failures; and 51 strict interior extrema. T7bx owns fresh scientific
reconstruction. T8ao emits no new scientific decision.

### Task 6: Fresh Verification And T8ao Handoff

**Files:**
- Modify: `status.md`
- Modify: `docs/handoffs/T8_current.md`
- Create: `docs/handoffs/archive/T8_2026-07-15_pre_t8ao_units_metadata_repair.md`

- [ ] **Step 1: Run fresh focused, Ruff, and full tests**

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_tablei_risk_pilot.py \
  tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
.venv/bin/python -m ruff check \
  src/schwgw/io/tablei_risk_pilot.py \
  scripts/phase5_repair_delta0p1_risk_pilot_metadata.py \
  tests/unit/test_tablei_risk_pilot.py \
  tests/regression/test_delta0p1_risk_pilot_metadata_repair.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Expected: all focused/full tests pass and Ruff is clean.

- [ ] **Step 2: Run exact scope and forbidden-output checks**

```bash
git diff --name-only HEAD^ HEAD
git diff -- src/schwgw/scattering src/schwgw/numerics src/schwgw/viz configs tests/regression/fixtures
find \
  runs/phase5/fig5_fig6_dense_scan_production \
  runs/phase5/fig5_fig6_delta0p05_targeted \
  runs/phase5/fig5_fig6_paper_style_candidates \
  -maxdepth 2 -type f -print 2>/dev/null | sort
```

Expected: the implementation commit lists exactly four frozen paths; both
forbidden commands are empty.

- [ ] **Step 3: Record exactly one T8ao decision**

```text
GREEN / DELTA0P1 RISK-PILOT UNITS METADATA HARDENED
YELLOW / DELTA0P1 RISK-PILOT UNITS METADATA PARTIAL
RED / DELTA0P1 RISK-PILOT UNITS METADATA BLOCKED
```

GREEN requires every preceding identity, metadata, provenance, test, scope,
and forbidden-output check. Record new 23 active hashes, metadata-contract
hash, implementation commit, and unchanged scientific summary.

- [ ] **Step 4: Dispatch T7bx only after exact GREEN**

Send the frozen review prompt to existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` using `gpt-5.6-sol`, thinking `high`.
On YELLOW, RED, incomplete, or ambiguous state, notify T0 only and start
nothing downstream. Do not create a new task.

## Execution Route

The user already reviewed the design and authorized direct execution in the
existing T8 task. This supersedes the generic execution-choice question. T8ao
must use `executing-plans`, TDD, systematic debugging for unexpected failures,
and verification-before-completion. T7bx is a separate independent review.
