from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from schwgw.io.tablei import TABLEI_POINTS
from schwgw.scattering.kirchhoff import compute_kirchhoff_eq47


EXPECTED_KM_VALUES = np.array(
    [
        0.1,
        0.2,
        0.3,
        0.5,
        0.75,
        1.0,
        1.25,
        1.5,
        1.75,
        2.0,
        2.25,
        2.5,
        2.75,
        3.0,
        3.25,
        3.5,
        3.75,
        4.0,
    ],
    dtype=float,
)
EXPECTED_POINT_X = np.array([0.0, 1.0, 2.0, 3.0, 10.0, 15.0, 20.0, 25.0])
EXPECTED_POINT_Z = np.full(8, 30.0)
EXPECTED_SOURCE_NPZ_SHA256 = (
    "a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb"
)
EXPECTED_SOURCE_JSON_SHA256 = (
    "2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537"
)
EXPECTED_SOURCE_MANIFEST_SHA256 = (
    "86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf"
)

_EXPECTED_POINT_IDS = np.asarray([point.point_id for point in TABLEI_POINTS])
_EXPECTED_POINT_Y = np.asarray([point.y for point in TABLEI_POINTS], dtype=float)
_EXPECTED_POINT_R = np.asarray([point.r for point in TABLEI_POINTS], dtype=float)
_EXPECTED_POINT_THETA = np.asarray([point.theta for point in TABLEI_POINTS], dtype=float)
_EXPECTED_PAPER_XI = np.asarray(
    [point.paper_xi_over_xi0 for point in TABLEI_POINTS], dtype=float
)
_ETA_MISMATCH_LIMIT = 5.0e-5


def generate_kirchhoff_review_grid_artifact(
    source_npz: str | Path,
    output_dir: str | Path,
    *,
    dps: int = 60,
    enforce_accepted_source: bool = True,
) -> tuple[Path, Path, Path]:
    """Generate the bounded Eq. (47) comparison artifact from accepted T8aj data."""

    source = Path(source_npz)
    source_sidecar = Path(str(source) + ".json")
    source_manifest = source.parent / "manifest.md"
    for path in (source, source_sidecar, source_manifest):
        if not path.is_file():
            raise FileNotFoundError(path)

    source_hashes = {
        "npz": _file_sha256(source),
        "json": _file_sha256(source_sidecar),
        "manifest": _file_sha256(source_manifest),
    }
    if enforce_accepted_source:
        expected_hashes = {
            "npz": EXPECTED_SOURCE_NPZ_SHA256,
            "json": EXPECTED_SOURCE_JSON_SHA256,
            "manifest": EXPECTED_SOURCE_MANIFEST_SHA256,
        }
        if source_hashes != expected_hashes:
            raise ValueError(
                "source hashes do not match the accepted T8aj review-grid artifact"
            )

    with np.load(source, allow_pickle=False) as data:
        arrays = _validated_source_arrays(data)

    eta = 0.5 * np.sqrt(arrays["point_r"]) * np.tan(arrays["point_theta"])
    eta_minus_paper = eta - arrays["paper_xi_over_xi0"]
    max_eta_mismatch = float(np.max(np.abs(eta_minus_paper)))
    if max_eta_mismatch >= _ETA_MISMATCH_LIMIT:
        raise ValueError(
            "coordinate-derived eta differs from paper xi/xi0 by "
            f"{max_eta_mismatch:.17g}, exceeding {_ETA_MISMATCH_LIMIT:.1e}"
        )

    result = compute_kirchhoff_eq47(
        kM_values=arrays["kM_values"],
        r_over_M=arrays["point_r"],
        theta=arrays["point_theta"],
        dps=dps,
    )
    baseline_metadata = dict(result.metadata["baseline"])
    metadata = {
        "case_id": "FIG5_FIG6_REVIEW_GRID_KIRCHHOFF_EQ47_BASELINE",
        "schema_version": "phase5_t8ak_kirchhoff_review_grid_v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "quantity_kind": "kirchhoff_eq47_scalar_comparison",
        "source_npz_path": str(source),
        "source_npz_sha256": source_hashes["npz"],
        "source_json_path": str(source_sidecar),
        "source_json_sha256": source_hashes["json"],
        "source_manifest_path": str(source_manifest),
        "source_manifest_sha256": source_hashes["manifest"],
        "backend": baseline_metadata["backend"],
        "backend_version": baseline_metadata["backend_version"],
        "dps": baseline_metadata["dps"],
        "formula_and_branches": baseline_metadata,
        "eta_mismatch_limit": _ETA_MISMATCH_LIMIT,
        "max_abs_eta_minus_paper": max_eta_mismatch,
        "comparison_only": True,
        "not_denominator": True,
        "not_mask": True,
        "not_normalization": True,
        "polarization_independent": True,
        "no_solver_rerun": True,
        "no_plotting": True,
        "not_40_frequency_production": True,
        "no_fixtures": True,
        "no_paper_style_candidates": True,
        "no_interpolation": True,
        "no_smoothing": True,
        "principal_phase_stored": True,
        "unwrapped_phase_display_only": True,
    }

    output_directory = Path(output_dir)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_npz = output_directory / "tablei_kirchhoff_baseline_values.npz"
    sidecar = Path(str(output_npz) + ".json")
    manifest = output_directory / "manifest.md"
    np.savez_compressed(
        output_npz,
        **arrays,
        gamma=result.gamma,
        eta=eta,
        eta_minus_paper=eta_minus_paper,
        F_kirchhoff_complex=result.F_complex,
        abs_F_kirchhoff=result.abs_F,
        arg_F_kirchhoff_principal=result.arg_F_principal,
        arg_F_kirchhoff_unwrapped=np.unwrap(result.arg_F_principal, axis=0),
        valid_kirchhoff_mask=result.valid_mask,
        metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)),
    )
    output_npz_sha256 = _file_sha256(output_npz)
    sidecar_metadata = dict(metadata)
    sidecar_metadata["output_npz_path"] = str(output_npz)
    sidecar_metadata["output_npz_sha256"] = output_npz_sha256
    sidecar.write_text(
        json.dumps(sidecar_metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    sidecar_sha256 = _file_sha256(sidecar)
    manifest.write_text(
        _manifest_text(
            source_hashes=source_hashes,
            output_npz=output_npz,
            output_npz_sha256=output_npz_sha256,
            sidecar=sidecar,
            sidecar_sha256=sidecar_sha256,
            dps=int(baseline_metadata["dps"]),
            backend_version=str(baseline_metadata["backend_version"]),
            max_eta_mismatch=max_eta_mismatch,
        ),
        encoding="utf-8",
    )
    return output_npz, sidecar, manifest


def _validated_source_arrays(data: np.lib.npyio.NpzFile) -> dict[str, np.ndarray]:
    arrays = {
        "kM_values": np.asarray(data["kM_values"], dtype=float),
        "point_ids": np.asarray(data["point_ids"]),
        "point_x": np.asarray(data["point_x"], dtype=float),
        "point_y": np.asarray(data["point_y"], dtype=float),
        "point_z": np.asarray(data["point_z"], dtype=float),
        "point_r": np.asarray(data["point_r"], dtype=float),
        "point_theta": np.asarray(data["point_theta"], dtype=float),
        "paper_xi_over_xi0": np.asarray(data["paper_xi_over_xi0"], dtype=float),
    }
    if not np.array_equal(arrays["kM_values"], EXPECTED_KM_VALUES):
        raise ValueError("source must use the exact accepted 18-frequency grid")
    expected = {
        "point_ids": _EXPECTED_POINT_IDS,
        "point_x": EXPECTED_POINT_X,
        "point_y": _EXPECTED_POINT_Y,
        "point_z": EXPECTED_POINT_Z,
        "point_r": _EXPECTED_POINT_R,
        "point_theta": _EXPECTED_POINT_THETA,
        "paper_xi_over_xi0": _EXPECTED_PAPER_XI,
    }
    for name, expected_array in expected.items():
        if not np.array_equal(arrays[name], expected_array):
            raise ValueError(f"source {name} does not match the exact Table-I grid")
    return arrays


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_text(
    *,
    source_hashes: dict[str, str],
    output_npz: Path,
    output_npz_sha256: str,
    sidecar: Path,
    sidecar_sha256: str,
    dps: int,
    backend_version: str,
    max_eta_mismatch: float,
) -> str:
    return f"""# Fig.5/Fig.6 Review-Grid Kirchhoff Eq. (47) Baseline

This archive is a scalar, polarization-independent comparison baseline only.
It is not a solver output, production denominator, mask, normalization,
40-frequency scan, fixture, plot, or paper-style candidate.

## Source hashes

- NPZ: `{source_hashes['npz']}`
- JSON: `{source_hashes['json']}`
- manifest: `{source_hashes['manifest']}`

## Output hashes

- `{output_npz}`: `{output_npz_sha256}`
- `{sidecar}`: `{sidecar_sha256}`

## Numerical policy

- Formula: Li-Hou-Zhao Eq. (47), no conjugation.
- Backend: project-local mpmath {backend_version}, dps={dps}.
- Grid: exact accepted 18 frequencies by eight Table-I points.
- Maximum absolute coordinate-derived eta minus rounded paper xi/xi0:
  `{max_eta_mismatch:.17g}` (required `< {_ETA_MISMATCH_LIMIT:.1e}`).
- Principal phase is numerical evidence; unwrapped phase is display-only.
"""
