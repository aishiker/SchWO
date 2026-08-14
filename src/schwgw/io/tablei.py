from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from schwgw.io.results import AmplificationGridResult, load_amplification_results


SCHEMA_VERSION = "phase5_t8ac_tablei_v1"
CASE_ID = "FIG5_FIG6_TABLEI_FOUR_FREQUENCY_READONLY"
DEFAULT_KM_VALUES = (0.5, 1.0, 1.5, 2.0)


@dataclass(frozen=True)
class TableIPoint:
    point_id: str
    group: str
    x: float
    y: float
    z: float
    paper_theta_deg: float
    paper_xi_over_xi0: float
    x_index: int
    z_index: int

    @property
    def r(self) -> float:
        return float(np.sqrt(self.x * self.x + self.y * self.y + self.z * self.z))

    @property
    def theta(self) -> float:
        return float(np.arctan2(abs(self.x), self.z))

    @property
    def phi(self) -> float:
        return 0.0 if self.x >= 0.0 else float(np.pi)

    def metadata(self) -> dict[str, Any]:
        return {
            "point_id": self.point_id,
            "group": self.group,
            "x": float(self.x),
            "y": float(self.y),
            "z": float(self.z),
            "r": self.r,
            "theta": self.theta,
            "phi": self.phi,
            "paper_theta_deg": float(self.paper_theta_deg),
            "paper_xi_over_xi0": float(self.paper_xi_over_xi0),
            "x_index": int(self.x_index),
            "z_index": int(self.z_index),
        }


TABLEI_POINTS: tuple[TableIPoint, ...] = (
    TableIPoint("near_axis_x0_z30", "near_axis", 0.0, 0.0, 30.0, 0.0, 0.0, 60, 120),
    TableIPoint("near_axis_x1_z30", "near_axis", 1.0, 0.0, 30.0, 1.90915, 0.0913, 62, 120),
    TableIPoint("near_axis_x2_z30", "near_axis", 2.0, 0.0, 30.0, 3.81407, 0.1828, 64, 120),
    TableIPoint("near_axis_x3_z30", "near_axis", 3.0, 0.0, 30.0, 5.71059, 0.2745, 66, 120),
    TableIPoint("far_axis_x10_z30", "far_axis", 10.0, 0.0, 30.0, 18.4349, 0.9372, 80, 120),
    TableIPoint("far_axis_x15_z30", "far_axis", 15.0, 0.0, 30.0, 26.5651, 1.4479, 90, 120),
    TableIPoint("far_axis_x20_z30", "far_axis", 20.0, 0.0, 30.0, 33.6901, 2.0015, 100, 120),
    TableIPoint("far_axis_x25_z30", "far_axis", 25.0, 0.0, 30.0, 39.8056, 2.6038, 110, 120),
)


TEST_SMALL_POINTS: tuple[TableIPoint, ...] = (
    TableIPoint("test_x0_z1", "near_axis", 0.0, 0.0, 1.0, 0.0, 0.0, 1, 2),
)


def builtin_tablei_points(name: str) -> tuple[TableIPoint, ...]:
    if name == "table-i":
        return TABLEI_POINTS
    if name == "test-small":
        return TEST_SMALL_POINTS
    raise ValueError("builtin points must be 'table-i' or 'test-small'.")


def extract_tablei_four_frequency_from_amplification_results(
    result_paths: Sequence[str | Path],
    *,
    output_path: str | Path,
    points: Sequence[TableIPoint] = TABLEI_POINTS,
    expected_kM_values: Sequence[float] = DEFAULT_KM_VALUES,
    created_by_cli: bool = False,
) -> Path:
    """Extract Table-I point-frequency complex ratios from saved M5 artifacts."""

    if len(result_paths) != len(expected_kM_values):
        raise ValueError(
            "Table-I extraction requires exactly four source amplification results."
        )
    paths = [Path(path) for path in result_paths]
    results = [load_amplification_results(path) for path in paths]
    kM_values = [_source_kM(result) for result in results]
    expected = [float(value) for value in expected_kM_values]
    if not np.allclose(kM_values, expected, rtol=0.0, atol=1.0e-12):
        raise ValueError(
            "Table-I extraction requires source files in increasing kM order "
            "[0.5, 1.0, 1.5, 2.0]."
        )
    _validate_points(points)

    arrays = _extract_arrays(results, points)
    metadata = _sidecar_metadata(
        results,
        source_paths=paths,
        points=points,
        arrays=arrays,
        output_path=Path(output_path),
        created_by_cli=created_by_cli,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        output,
        **arrays,
        metadata_json=np.asarray(json.dumps(_json_safe(metadata), sort_keys=True)),
    )
    sidecar = output.with_suffix(output.suffix + ".json")
    sidecar.write_text(
        json.dumps(_json_safe(metadata), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return sidecar


def _extract_arrays(
    results: list[AmplificationGridResult],
    points: Sequence[TableIPoint],
) -> dict[str, np.ndarray]:
    frequency_count = len(results)
    point_count = len(points)
    shape = (frequency_count, point_count)
    f_plus = np.empty(shape, dtype=np.complex128)
    f_cross = np.empty(shape, dtype=np.complex128)
    valid_plus = np.empty(shape, dtype=bool)
    valid_cross = np.empty(shape, dtype=bool)
    valid_norm = np.empty(shape, dtype=bool)
    source_valid = np.empty(shape, dtype=bool)

    for frequency_index, result in enumerate(results):
        _require_xz_amplification_result(result)
        for point_index, point in enumerate(points):
            _verify_point_indices(result, point)
            z_index = int(point.z_index)
            x_index = int(point.x_index)
            f_plus[frequency_index, point_index] = result.F_plus_complex[z_index, x_index]
            f_cross[frequency_index, point_index] = result.F_cross_complex[z_index, x_index]
            valid_plus[frequency_index, point_index] = result.valid_ratio_plus_mask[
                z_index,
                x_index,
            ]
            valid_cross[frequency_index, point_index] = result.valid_ratio_cross_mask[
                z_index,
                x_index,
            ]
            valid_norm[frequency_index, point_index] = result.valid_ratio_norm_mask[
                z_index,
                x_index,
            ]
            assert result.valid_mask is not None
            source_valid[frequency_index, point_index] = result.valid_mask[
                z_index,
                x_index,
            ]

    arg_plus = _principal_phase(f_plus)
    arg_cross = _principal_phase(f_cross)
    valid_field = source_valid.copy()
    return {
        "kM_values": np.asarray([_source_kM(result) for result in results], dtype=float),
        "point_ids": np.asarray([point.point_id for point in points]),
        "point_group": np.asarray([point.group for point in points]),
        "point_x": np.asarray([point.x for point in points], dtype=float),
        "point_y": np.asarray([point.y for point in points], dtype=float),
        "point_z": np.asarray([point.z for point in points], dtype=float),
        "point_r": np.asarray([point.r for point in points], dtype=float),
        "point_theta": np.asarray([point.theta for point in points], dtype=float),
        "point_phi": np.asarray([point.phi for point in points], dtype=float),
        "paper_theta_deg": np.asarray(
            [point.paper_theta_deg for point in points],
            dtype=float,
        ),
        "paper_xi_over_xi0": np.asarray(
            [point.paper_xi_over_xi0 for point in points],
            dtype=float,
        ),
        "x_indices": np.asarray([point.x_index for point in points], dtype=np.int64),
        "z_indices": np.asarray([point.z_index for point in points], dtype=np.int64),
        "F_plus_complex": f_plus,
        "F_cross_complex": f_cross,
        "abs_F_plus": np.abs(f_plus),
        "abs_F_cross": np.abs(f_cross),
        "arg_F_plus_principal": arg_plus,
        "arg_F_cross_principal": arg_cross,
        "arg_F_plus_unwrapped": _unwrap_masked_phases(arg_plus, valid_plus),
        "arg_F_cross_unwrapped": _unwrap_masked_phases(arg_cross, valid_cross),
        "valid_ratio_plus_mask": valid_plus,
        "valid_ratio_cross_mask": valid_cross,
        "valid_ratio_norm_mask": valid_norm,
        "valid_field_mask": valid_field,
        "source_valid_mask": source_valid,
    }


def _sidecar_metadata(
    results: list[AmplificationGridResult],
    *,
    source_paths: list[Path],
    points: Sequence[TableIPoint],
    arrays: dict[str, np.ndarray],
    output_path: Path,
    created_by_cli: bool,
) -> dict[str, Any]:
    source_shas = [_file_sha256(path) for path in source_paths]
    normalizations = [_metadata_object(result.metadata, "normalization") for result in results]
    return {
        "case_id": CASE_ID,
        "schema_version": SCHEMA_VERSION,
        "quantity_kind": "pointwise_wave_optics_amplification_tablei_four_frequency",
        "normalization_kind": "pointwise_wave_optics_amplification",
        "baseline_api": "compute_flat_no_lens_polarization",
        "incident_direction": "+z",
        "fourier": "exp(-i k t)",
        "polarization_bridge": "inherited from source amplification artifacts",
        "polarization_bridge_implementation": "not inferred by Table-I extraction",
        "polarization_bridge_validated": False,
        "positive_frequency_reality_bridge_validated": False,
        "source_bridge_metadata": normalizations,
        "physical_claim": False,
        "source_npz_paths": [str(path) for path in source_paths],
        "source_npz_size_bytes": [int(path.stat().st_size) for path in source_paths],
        "source_npz_sha256": source_shas,
        "source_case_ids": [result.metadata.get("case_id") for result in results],
        "source_kM_values": [float(value) for value in arrays["kM_values"]],
        "source_lmax_values": [
            int(_required_number(result.metadata.get("lmax"), "lmax"))
            for result in results
        ],
        "source_m4_paths": [
            result.metadata.get("source_lensed_result_path") for result in results
        ],
        "source_m4_size_bytes": [
            int(_required_number(result.metadata.get("source_lensed_size_bytes"), "source_lensed_size_bytes"))
            for result in results
        ],
        "source_m4_sha256": [
            result.metadata.get("source_lensed_sha256") for result in results
        ],
        "source_q018_warning_count": [
            int(result.metadata.get("source_q018_warning_count", 0)) for result in results
        ],
        "source_q018_warning_codes": [
            result.metadata.get("source_q018_warning_codes", []) for result in results
        ],
        "point_metadata": [point.metadata() for point in points],
        "frequency_metadata": [
            _frequency_metadata(result, path, sha)
            for result, path, sha in zip(results, source_paths, source_shas, strict=True)
        ],
        "selected_grid_indices": [
            {
                "point_id": point.point_id,
                "x_index": int(point.x_index),
                "z_index": int(point.z_index),
            }
            for point in points
        ],
        "array_axis_order": "ratio_arrays_indexed_as_z_then_x_before_extraction",
        "extraction_array_shape": [int(arrays["F_plus_complex"].shape[0]), int(arrays["F_plus_complex"].shape[1])],
        "phase_policy": {
            "principal": "angle in (-pi, pi]",
            "unwrapped": (
                "unwrap independently along increasing kM for each point and "
                "component; restart after invalid/masked/NaN gaps"
            ),
            "units": "radians",
            "four_frequency_unwrap_is_diagnostic_only": True,
        },
        "normalization_metadata": normalizations,
        "created_by_cli": bool(created_by_cli),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "output_npz_path": str(output_path),
        "no_interpolation": True,
        "no_solver_rerun": True,
        "no_field_recomputation": True,
        "no_kirchhoff_baseline": True,
        "not_paper_level_dense_scan": True,
        "no_kM4": True,
        "no_dense_Mk_scan": True,
        "no_new_physics_convention": True,
        "no_plotting": True,
        "git_commit": None,
        "git_status_available": False,
        "source_code_sha_policy": "unavailable_not_git_repository",
    }


def _frequency_metadata(
    result: AmplificationGridResult,
    path: Path,
    sha256: str,
) -> dict[str, Any]:
    metadata = result.metadata
    return {
        "source_npz_path": str(path),
        "source_npz_size_bytes": int(path.stat().st_size),
        "source_npz_sha256": sha256,
        "source_case_id": metadata.get("case_id"),
        "kM": _source_kM(result),
        "lmax": int(_required_number(metadata.get("lmax"), "lmax")),
        "source_m4_path": metadata.get("source_lensed_result_path"),
        "source_m4_size_bytes": metadata.get("source_lensed_size_bytes"),
        "source_m4_sha256": metadata.get("source_lensed_sha256"),
        "source_q018_warning_count": metadata.get("source_q018_warning_count", 0),
        "source_q018_warning_codes": metadata.get("source_q018_warning_codes", []),
    }


def _require_xz_amplification_result(result: AmplificationGridResult) -> None:
    if result.x is None or result.z is None or result.valid_mask is None:
        raise ValueError("Table-I extraction requires x, z, and valid_mask arrays.")
    if result.x.ndim != 1 or result.z.ndim != 1:
        raise ValueError("Table-I extraction requires 1D x and z arrays.")
    expected_shape = (result.z.size, result.x.size)
    for name, array in [
        ("F_plus_complex", result.F_plus_complex),
        ("F_cross_complex", result.F_cross_complex),
        ("valid_ratio_plus_mask", result.valid_ratio_plus_mask),
        ("valid_ratio_cross_mask", result.valid_ratio_cross_mask),
        ("valid_ratio_norm_mask", result.valid_ratio_norm_mask),
        ("valid_mask", result.valid_mask),
    ]:
        if array.shape != expected_shape:
            raise ValueError(f"{name} shape does not match (z.size, x.size).")


def _verify_point_indices(result: AmplificationGridResult, point: TableIPoint) -> None:
    assert result.x is not None
    assert result.z is not None
    if not (0 <= point.x_index < result.x.size):
        raise ValueError(f"{point.point_id} x_index is outside the saved x grid.")
    if not (0 <= point.z_index < result.z.size):
        raise ValueError(f"{point.point_id} z_index is outside the saved z grid.")
    saved_x = float(result.x[point.x_index])
    saved_z = float(result.z[point.z_index])
    if not np.isclose(saved_x, point.x, rtol=0.0, atol=1.0e-12):
        raise ValueError(
            f"{point.point_id} x_index does not match requested x; "
            f"saved {saved_x}, requested {point.x}. No interpolation is allowed."
        )
    if not np.isclose(saved_z, point.z, rtol=0.0, atol=1.0e-12):
        raise ValueError(
            f"{point.point_id} z_index does not match requested z; "
            f"saved {saved_z}, requested {point.z}. No interpolation is allowed."
        )


def _validate_points(points: Sequence[TableIPoint]) -> None:
    if not points:
        raise ValueError("Table-I extraction requires at least one point.")
    seen = set()
    for point in points:
        if point.point_id in seen:
            raise ValueError(f"Duplicate Table-I point id: {point.point_id}.")
        seen.add(point.point_id)


def _source_kM(result: AmplificationGridResult) -> float:
    value = result.metadata.get("k")
    return _required_number(value, "source kM")


def _principal_phase(values: np.ndarray) -> np.ndarray:
    phase = np.angle(values)
    finite = np.isfinite(phase)
    phase = phase.astype(float, copy=True)
    phase[finite & np.isclose(phase, -np.pi, rtol=0.0, atol=0.0)] = np.pi
    return phase


def _unwrap_masked_phases(principal: np.ndarray, valid_mask: np.ndarray) -> np.ndarray:
    unwrapped = np.full(principal.shape, np.nan, dtype=float)
    for point_index in range(principal.shape[1]):
        start: int | None = None
        for frequency_index in range(principal.shape[0] + 1):
            valid = (
                frequency_index < principal.shape[0]
                and bool(valid_mask[frequency_index, point_index])
                and np.isfinite(principal[frequency_index, point_index])
            )
            if valid and start is None:
                start = frequency_index
            if (not valid or frequency_index == principal.shape[0]) and start is not None:
                stop = frequency_index
                unwrapped[start:stop, point_index] = np.unwrap(
                    principal[start:stop, point_index]
                )
                start = None
    return unwrapped


def _metadata_object(metadata: dict[str, Any], key: str) -> dict[str, Any]:
    value = metadata.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"source metadata missing object: {key}.")
    return value


def _required_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"source metadata missing numeric {label}.")
    numeric = float(value)
    if not np.isfinite(numeric):
        raise ValueError(f"source metadata {label} must be finite.")
    return numeric


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": float(value.real), "imag": float(value.imag)}
    return value


__all__ = [
    "CASE_ID",
    "SCHEMA_VERSION",
    "TABLEI_POINTS",
    "TableIPoint",
    "builtin_tablei_points",
    "extract_tablei_four_frequency_from_amplification_results",
]
