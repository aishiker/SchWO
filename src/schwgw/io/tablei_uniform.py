"""Transactional 40-point production path for the Fig. 5/6 Table-I curves.

This module deliberately has no interpolation path: every row in the merged
artifact is either one of the accepted source rows or a verified, directly
computed missing-frequency transaction.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Sequence
from typing import Any, Callable, Mapping

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.io.tablei import TABLEI_POINTS
from schwgw.io.tablei_risk_pilot import _FrequencyRadialCache
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.numerics.experimental.q018_rescaled_oracle import (
    RescaledOracleRequest,
    solve_q018_rescaled_oracle,
)
from schwgw.numerics.radial_solver import RadialDiagnostics, RadialSolution
from schwgw.scattering.partial_wave import (
    compute_flat_no_lens_polarization,
    compute_polarization,
)

UNIFORM_FREQUENCIES = tuple(round(i / 10, 1) for i in range(1, 41))
MISSING_FREQUENCIES = (
    0.6,
    0.7,
    1.1,
    1.2,
    1.3,
    1.4,
    1.8,
    1.9,
    2.1,
    2.2,
    2.3,
    2.4,
    2.6,
    2.7,
    3.1,
    3.2,
    3.3,
    3.4,
    3.6,
    3.7,
)
UNIFORM_LMAX_VALUES: dict[float, tuple[int, ...]] = {
    0.6: (24, 36, 60, 84),
    0.7: (24, 36, 60, 84),
    1.1: (36, 60, 84, 108, 132),
    1.2: (36, 60, 84, 108, 132),
    1.3: (48, 72, 96, 120, 144),
    1.4: (48, 72, 96, 120, 144),
    1.8: (108, 132, 156, 180),
    1.9: (108, 132, 156, 180),
    2.1: (120, 144, 180, 216),
    2.2: (120, 144, 180, 216),
    2.3: (120, 144, 180, 216),
    2.4: (120, 144, 180, 216),
    2.6: (156, 180, 216, 252),
    2.7: (156, 180, 216, 252),
    3.1: (228, 252, 276, 300),
    3.2: (228, 252, 276, 300),
    3.3: (228, 252, 276, 300),
    3.4: (228, 252, 276, 300),
    3.6: (264, 288, 312, 336),
    3.7: (264, 288, 312, 336),
}
CONVERGENCE_TOLERANCE = 1.0e-4
SCHEMA_VERSION = "phase5_tablei_uniform40_v1"
DEFAULT_REVIEW_NPZ = Path(
    "runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz"
)
DEFAULT_PILOT_NPZ = Path(
    "runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_values.npz"
)


class UniformContractError(ValueError):
    """Raised when uniform production would violate its immutable contract."""


def _uniform_radial_solver(
    sector: Any,
    ell: int,
    k: float,
    background: Any,
    boundary_config: BoundaryConfig | None = None,
) -> Any:
    """Use the production solve, with a narrow rescaled fallback on a no-go.

    The fallback is not a zero-tail approximation.  It invokes the existing
    Riccati/log-amplitude backend at the exact requested Table-I radius and
    preserves the same equation, outer boundary, tolerances, and unit-incoming
    normalization.  Only the two structured high-dynamic-range no-go errors
    are eligible; every other production-solver failure is propagated.
    """

    config = boundary_config or BoundaryConfig()
    try:
        return solve_radial_mode(sector, ell, k, background, config)
    except RuntimeError as exc:
        message = str(exc)
        if not any(
            code in message
            for code in (
                "evanescent_tail_required_radius_uncovered",
                "evanescent_tail_required_radius_solver_failed",
            )
        ):
            raise
    if config.required_eval_radius is None or config.r_out is None:
        raise UniformContractError(
            "uniform rescaled fallback requires explicit evaluation and outer radii"
        )
    required_radius = float(config.required_eval_radius)
    result = solve_q018_rescaled_oracle(
        RescaledOracleRequest(
            sector=sector,
            ell=ell,
            k=float(k),
            required_radius=required_radius,
            r_out=float(config.r_out),
            r_in_eps=float(config.r_in_eps),
            rtol=float(config.rtol),
            atol=float(config.atol),
            method_hint="tablei_uniform_rescaled_log_amplitude",
        ),
        background,
    )
    diagnostics = dict(result.diagnostics)
    residual = max(
        float(diagnostics["outer_boundary_residual"]),
        float(diagnostics["normalization_residual"]),
        float(diagnostics["log_derivative_match_residual"]),
    )
    if not result.valid_at_required_radius or residual > 1.0e-7:
        raise UniformContractError(
            "uniform rescaled fallback failed its exact-radius residual gate"
        )
    step = 1.0e-6
    r_grid = np.asarray([required_radius, required_radius + step], dtype=float)
    psi = np.asarray(
        [result.psi, result.psi + result.dpsi_dr * step], dtype=complex
    )
    derivative = np.asarray([result.dpsi_dr, result.dpsi_dr], dtype=complex)
    phase_factor = -result.A_out / (((-1) ** ell) * result.A_in)
    return RadialSolution(
        sector=sector,
        ell=ell,
        k=k,
        r_grid=r_grid,
        psi=psi,
        dpsi_dr=derivative,
        A_in=complex(result.A_in),
        A_out=complex(result.A_out),
        phase_factor=complex(phase_factor),
        phase_shift=complex(-0.5j * np.log(phase_factor)),
        diagnostics=RadialDiagnostics(
            boundary_residual=float(diagnostics["outer_boundary_residual"]),
            wronskian_residual=residual,
            flux_residual=residual,
            ode_n_steps=int(diagnostics["riccati_steps"])
            + int(diagnostics["outward_steps"]),
            ode_status="Table-I uniform rescaled/log-amplitude fallback",
            r_in=float(background.horizon_radius * (1.0 + config.r_in_eps)),
            r_out=float(config.r_out),
            atol=float(config.atol),
            rtol=float(config.rtol),
            match_condition_number=float(diagnostics["match_condition_number"]),
            solver="tablei_uniform_rescaled_log_amplitude",
            raw_wronskian_residual=float(
                diagnostics["log_derivative_match_residual"]
            ),
        ),
        background=background,
        valid_until_r=required_radius,
    )


def _token(km: float) -> str:
    return f"{km:g}".replace(".", "p")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    return value


def _atomic_no_overwrite(path: Path, writer: Callable[[Path], None]) -> None:
    """Publish a completed file atomically, failing rather than replacing it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise UniformContractError(f"refusing to overwrite {path}")
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    os.close(fd)
    temporary = Path(raw)
    try:
        writer(temporary)
        os.link(temporary, path)  # atomic create; fails if another writer won.
    except FileExistsError as exc:
        raise UniformContractError(f"refusing to overwrite {path}") from exc
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_json_no_overwrite(path: Path, value: Mapping[str, Any]) -> None:
    _atomic_no_overwrite(
        path,
        lambda tmp: tmp.write_text(
            json.dumps(_json_safe(value), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        ),
    )


def _atomic_npz_no_overwrite(path: Path, arrays: Mapping[str, np.ndarray]) -> None:
    def write(tmp: Path) -> None:
        with tmp.open("wb") as stream:
            np.savez_compressed(stream, **arrays)

    _atomic_no_overwrite(path, write)


def _relative_delta(final: np.ndarray, previous: np.ndarray) -> np.ndarray:
    return np.abs(final - previous) / np.maximum(
        1.0, np.maximum(np.abs(final), np.abs(previous))
    )


def _frequency_paths(output_dir: Path, km: float) -> tuple[Path, Path]:
    npz = output_dir / "frequencies" / f"kM_{_token(km)}.npz"
    return npz, Path(str(npz) + ".json")


def _transaction_valid(npz: Path, sidecar: Path, km: float) -> bool:
    if not npz.is_file() or not sidecar.is_file():
        return False
    try:
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
        with np.load(npz, allow_pickle=False) as data:
            okay = (
                float(data["kM"]) == km
                and data["F_plus_complex"].shape == (8,)
                and tuple(data["lmax_values"].tolist()) == UNIFORM_LMAX_VALUES[km]
            )
        return bool(
            okay
            and meta.get("complete") is True
            and meta.get("kM") == km
            and meta.get("npz_sha256") == _sha256(npz)
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return False


def _compute_frequency(
    kM: float,
    *,
    polarization_solver: Callable[..., Any],
    flat_solver: Callable[..., Any],
    radial_solver: Callable[..., Any],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Directly compute one missing frequency using the risk-pilot point mode."""
    if kM not in UNIFORM_LMAX_VALUES:
        raise UniformContractError(f"not a missing kM: {kM}")
    started = time.monotonic()
    lvals = UNIFORM_LMAX_VALUES[kM]
    plus = np.empty((len(lvals), 8), complex)
    cross = np.empty_like(plus)
    cache = _FrequencyRadialCache(radial_solver)
    bg = SchwarzschildBackground(M=1.0)
    for row, lmax in enumerate(lvals):
        for index in sorted(range(8), key=lambda i: TABLEI_POINTS[i].r, reverse=True):
            point = TABLEI_POINTS[index]
            boundary = BoundaryConfig(
                r_out=300.0,
                r_in_eps=1e-6,
                rtol=1e-10,
                atol=1e-12,
                required_eval_radius=point.r,
            )
            lens = polarization_solver(
                background=bg,
                k=kM,
                r=point.r,
                theta=point.theta,
                phi=point.phi,
                A_plus=0.9 + 1.1j,
                A_cross=0.4 + 0.6j,
                lmax=lmax,
                boundary_config=boundary,
                radial_solver=cache,
            )
            flat = flat_solver(
                k=kM,
                r=point.r,
                theta=point.theta,
                phi=point.phi,
                A_plus=0.9 + 1.1j,
                A_cross=0.4 + 0.6j,
                lmax=lmax,
            )
            if (
                not all(
                    np.isfinite(
                        [
                            lens.h_plus.real,
                            lens.h_plus.imag,
                            lens.h_cross.real,
                            lens.h_cross.imag,
                        ]
                    )
                )
                or not flat.h_plus
                or not flat.h_cross
            ):
                raise UniformContractError(f"invalid amplification ratio at kM={kM}")
            plus[row, index] = lens.h_plus / flat.h_plus
            cross[row, index] = lens.h_cross / flat.h_cross
    dplus, dcross = (
        _relative_delta(plus[-1], plus[-2]),
        _relative_delta(cross[-1], cross[-2]),
    )
    if max(dplus.max(), dcross.max()) > CONVERGENCE_TOLERANCE:
        raise UniformContractError(f"final adjacent lmax pair failed at kM={kM}")
    meta = {
        "schema_version": SCHEMA_VERSION,
        "complete": True,
        "kM": kM,
        "lmax_values": list(lvals),
        "final_lmax_pair": list(lvals[-2:]),
        "convergence_tolerance": CONVERGENCE_TOLERANCE,
        "max_final_pair_delta_plus": float(dplus.max()),
        "max_final_pair_delta_cross": float(dcross.max()),
        "M": 1.0,
        "A_plus": 0.9 + 1.1j,
        "A_cross": 0.4 + 0.6j,
        "boundary": {"r_out": 300.0, "r_in_eps": 1e-6, "rtol": 1e-10, "atol": 1e-12},
        "radial_path": "direct_required_radius_solve",
        "runtime_seconds": time.monotonic() - started,
        "no_interpolation": True,
    }
    arrays = {
        "kM": np.asarray(kM),
        "point_ids": np.asarray([p.point_id for p in TABLEI_POINTS]),
        "point_group": np.asarray([p.group for p in TABLEI_POINTS]),
        "point_x": np.asarray([p.x for p in TABLEI_POINTS]),
        "point_y": np.asarray([p.y for p in TABLEI_POINTS]),
        "point_z": np.asarray([p.z for p in TABLEI_POINTS]),
        "point_r": np.asarray([p.r for p in TABLEI_POINTS]),
        "point_theta": np.asarray([p.theta for p in TABLEI_POINTS]),
        "point_phi": np.asarray([p.phi for p in TABLEI_POINTS]),
        "lmax_values": np.asarray(lvals),
        "F_plus_history": plus,
        "F_cross_history": cross,
        "F_plus_complex": plus[-1],
        "F_cross_complex": cross[-1],
        "abs_F_plus": np.abs(plus[-1]),
        "abs_F_cross": np.abs(cross[-1]),
        "arg_F_plus_principal": np.angle(plus[-1]),
        "arg_F_cross_principal": np.angle(cross[-1]),
        "final_pair_delta_plus": dplus,
        "final_pair_delta_cross": dcross,
        "metadata_json": np.asarray(json.dumps(_json_safe(meta), sort_keys=True)),
    }
    return arrays, meta


def run_tablei_uniform_missing(
    *,
    output_dir: str | Path,
    resume: bool = False,
    frequencies: Sequence[float] | None = None,
    polarization_solver: Callable[..., Any] | None = None,
    flat_solver: Callable[..., Any] | None = None,
    radial_solver: Callable[..., Any] | None = None,
) -> Path:
    """Produce only the twenty missing direct transactions; never overwrites them."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    selected = MISSING_FREQUENCIES if frequencies is None else tuple(frequencies)
    if (
        len(set(selected)) != len(selected)
        or any(km not in MISSING_FREQUENCIES for km in selected)
        or tuple(sorted(selected)) != selected
    ):
        raise UniformContractError(
            "selected frequencies must be a unique ordered subset of the missing grid"
        )
    for km in selected:
        npz, sidecar = _frequency_paths(output, km)
        if npz.exists() or sidecar.exists():
            if resume and _transaction_valid(npz, sidecar, km):
                continue
            raise UniformContractError(
                f"existing transaction is not a verified resume: {km}"
            )
        arrays, meta = _compute_frequency(
            km,
            polarization_solver=polarization_solver or compute_polarization,
            flat_solver=flat_solver or compute_flat_no_lens_polarization,
            radial_solver=radial_solver or _uniform_radial_solver,
        )
        _atomic_npz_no_overwrite(npz, arrays)
        meta["npz_sha256"] = _sha256(npz)
        _atomic_json_no_overwrite(sidecar, meta)
    return output


def preflight_tablei_uniform(
    *,
    review_npz: str | Path = DEFAULT_REVIEW_NPZ,
    pilot_npz: str | Path = DEFAULT_PILOT_NPZ,
    transaction_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Read-only completeness and source-binding check; never calls a solver."""
    review, pilot = Path(review_npz), Path(pilot_npz)
    for path in (review, pilot):
        if not path.is_file():
            raise UniformContractError(f"missing accepted source: {path}")
    source_rows = _accepted_rows(review, pilot)
    missing = list(MISSING_FREQUENCIES)
    if transaction_dir is not None:
        missing = []
        root = Path(transaction_dir)
        for km in MISSING_FREQUENCIES:
            npz, sidecar = _frequency_paths(root, km)
            if not _transaction_valid(npz, sidecar, km):
                missing.append(km)
    return {
        "schema_version": SCHEMA_VERSION,
        "uniform_frequencies": list(UNIFORM_FREQUENCIES),
        "accepted_source_hashes": {
            "review_npz": _sha256(review),
            "pilot_npz": _sha256(pilot),
        },
        "accepted_uniform_rows": sorted(source_rows),
        "missing_transactions": missing,
        "ready_to_merge": not missing,
    }


def _accepted_rows(review: Path, pilot: Path) -> dict[float, tuple[Path, int]]:
    result: dict[float, tuple[Path, int]] = {}
    for path in (review, pilot):
        with np.load(path, allow_pickle=False) as data:
            for i, raw in enumerate(np.asarray(data["kM_values"], dtype=float)):
                km = round(float(raw), 1)
                # The accepted review grid also contains 0.75, 1.25, etc.;
                # these are not uniform-tenth rows and must never be rounded
                # into this production grid.
                if km in UNIFORM_FREQUENCIES and abs(float(raw) - km) <= 1.0e-12:
                    if km in result:
                        raise UniformContractError(f"duplicate accepted kM={km}")
                    result[km] = (path, i)
    if set(result) != set(UNIFORM_FREQUENCIES) - set(MISSING_FREQUENCIES):
        raise UniformContractError(
            "accepted sources do not cover exactly the twenty non-missing uniform rows"
        )
    return result


def merge_tablei_uniform(
    *,
    output_path: str | Path,
    review_npz: str | Path = DEFAULT_REVIEW_NPZ,
    pilot_npz: str | Path = DEFAULT_PILOT_NPZ,
    transaction_dir: str | Path,
) -> Path:
    """Merge 20 accepted rows and 20 verified transactions without interpolation."""
    review, pilot, output, root = (
        Path(review_npz),
        Path(pilot_npz),
        Path(output_path),
        Path(transaction_dir),
    )
    if output.exists() or Path(str(output) + ".json").exists():
        raise UniformContractError(f"refusing to overwrite merge output {output}")
    accepted = _accepted_rows(review, pilot)
    preflight = preflight_tablei_uniform(
        review_npz=review, pilot_npz=pilot, transaction_dir=root
    )
    if not preflight["ready_to_merge"]:
        raise UniformContractError(
            f"missing verified transactions: {preflight['missing_transactions']}"
        )
    loaded = {path: np.load(path, allow_pickle=False) for path in (review, pilot)}
    try:
        first = loaded[review]
        rows: dict[str, list[np.ndarray]] = {
            name: []
            for name in (
                "F_plus_complex",
                "F_cross_complex",
                "abs_F_plus",
                "abs_F_cross",
                "arg_F_plus_principal",
                "arg_F_cross_principal",
                "final_pair_delta_plus",
                "final_pair_delta_cross",
            )
        }
        binding = []
        for km in UNIFORM_FREQUENCIES:
            if km in accepted:
                path, idx = accepted[km]
                data = loaded[path]
                binding.append(
                    {
                        "kM": km,
                        "kind": "accepted",
                        "source": str(path),
                        "sha256": _sha256(path),
                        "row": idx,
                    }
                )
                for name in rows:
                    rows[name].append(np.asarray(data[name][idx]))
            else:
                npz, sidecar = _frequency_paths(root, km)
                data = np.load(npz, allow_pickle=False)
                binding.append(
                    {
                        "kM": km,
                        "kind": "transaction",
                        "source": str(npz),
                        "sha256": _sha256(npz),
                        "sidecar_sha256": _sha256(sidecar),
                    }
                )
                for name in rows:
                    rows[name].append(np.asarray(data[name]))
                data.close()
        arrays = {
            "kM_values": np.asarray(UNIFORM_FREQUENCIES),
            **{
                name: first[name]
                for name in (
                    "point_ids",
                    "point_group",
                    "point_x",
                    "point_y",
                    "point_z",
                    "point_r",
                    "point_theta",
                    "point_phi",
                    "paper_theta_deg",
                    "paper_xi_over_xi0",
                )
                if name in first.files
            },
        }
        arrays.update({name: np.stack(value) for name, value in rows.items()})
        arrays["arg_F_plus_unwrapped"] = np.unwrap(
            arrays["arg_F_plus_principal"], axis=0
        )
        arrays["arg_F_cross_unwrapped"] = np.unwrap(
            arrays["arg_F_cross_principal"], axis=0
        )
        metadata = {
            "schema_version": SCHEMA_VERSION,
            "shape": [40, 8],
            "source_binding": binding,
            "accepted_source_hashes": preflight["accepted_source_hashes"],
            "no_interpolation": True,
            "principal_phase_stored": True,
            "unwrapped_phase_display_only": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        arrays["metadata_json"] = np.asarray(
            json.dumps(_json_safe(metadata), sort_keys=True)
        )
        _atomic_npz_no_overwrite(output, arrays)
        metadata["npz_sha256"] = _sha256(output)
        _atomic_json_no_overwrite(Path(str(output) + ".json"), metadata)
    finally:
        for data in loaded.values():
            data.close()
    return output


__all__ = [
    "CONVERGENCE_TOLERANCE",
    "MISSING_FREQUENCIES",
    "SCHEMA_VERSION",
    "UNIFORM_FREQUENCIES",
    "UNIFORM_LMAX_VALUES",
    "UniformContractError",
    "merge_tablei_uniform",
    "preflight_tablei_uniform",
    "run_tablei_uniform_missing",
]
