from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.io.tablei import TABLEI_POINTS
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.scattering.partial_wave import (
    compute_flat_no_lens_polarization,
    compute_polarization,
)


PILOT_FREQUENCIES = (0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9)
PILOT_LMAX_VALUES: dict[float, tuple[int, ...]] = {
    0.4: (24, 36, 60, 84),
    0.8: (24, 36, 60, 84),
    0.9: (24, 36, 60, 84),
    1.6: (72, 96, 120, 144),
    1.7: (84, 108, 132, 156),
    2.8: (180, 204, 228, 252),
    2.9: (192, 216, 240, 264),
    3.8: (276, 300, 324, 348),
    3.9: (288, 312, 336, 360),
}
ADAPTER_NAME = "q018_tablei_delta0p1_risk_pilot_transition"
CONVERGENCE_TOLERANCE = 1.0e-4
SCHEMA_VERSION = "phase5_t8an_delta0p1_risk_pilot_v1"
_T7BV_GREEN = "ACCEPT GREEN / DELTA0P1 RISK-PILOT RADIAL GATE ACCEPTED"
_T7BV_RECORD_PATH = Path("docs/handoffs/T7_current.md")
_DEFAULT_OUTPUT_DIR = Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot")
_DEFAULT_REVIEW_NPZ = Path(
    "runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz"
)
_DEFAULT_GATE_DIR = Path(
    "runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate"
)
_FROZEN_REVIEW_HASHES = {
    "npz": "a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb",
    "json": "2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537",
    "manifest": "86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf",
}
_FROZEN_GATE_HASHES = {
    "classification_manifest.json": "ee051831e1da7ebb250cab37d7da3a64d8a57298b445577f238d9cefae319d54",
    "oracle_validation.json": "8f6d23da0894d0abfb42867bf911b9da95090ad5293bc76289daf4522e4067f9",
    "resume_preflight.json": "59e99ade6993eab6d570f8a2ad18f0778595f7309fbb87fbf1edf32903b80968",
}
_ROOT_FILES = {
    "checkpoint_ledger.json",
    "risk_pilot_values.npz",
    "risk_pilot_values.npz.json",
    "risk_pilot_sampling_audit.json",
    "manifest.md",
}


class PilotContractError(ValueError):
    """Raised when the frozen T8an pilot contract cannot be preserved."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _token(kM: float) -> str:
    return f"{float(kM):g}".replace(".", "p")


def _canonical_json(value: Any) -> str:
    return json.dumps(_json_safe(value), sort_keys=True, separators=(",", ":"))


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": float(value.real), "imag": float(value.imag)}
    if isinstance(value, Path):
        return str(value)
    return value


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(_json_safe(dict(value)), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _atomic_npz(path: Path, arrays: Mapping[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        np.savez(stream, **arrays)
    os.replace(temporary, path)


def _covers(solution: Any, required_radius: float) -> bool:
    upper = solution.r_grid[-1] if solution.valid_until_r is None else solution.valid_until_r
    return float(required_radius) <= float(upper)


def _background_signature(background: Any) -> tuple[str, float]:
    return (type(background).__qualname__, float(getattr(background, "M", np.nan)))


def _radial_cache_key(
    sector: Any,
    ell: int,
    k: float,
    background: Any,
    config: BoundaryConfig,
) -> tuple[Any, ...]:
    return (
        str(getattr(sector, "value", sector)),
        int(ell),
        float(k),
        _background_signature(background),
        config.r_out,
        config.r_in_eps,
        config.rtol,
        config.atol,
        config.method,
        config.max_step,
        config.dense_output,
        config.experimental_required_radius_oracle,
    )


class _FrequencyRadialCache:
    def __init__(self, solver: Callable[..., Any]) -> None:
        self._solver = solver
        self._entries: dict[tuple[Any, ...], Any] = {}
        self.solve_count = 0
        self.reuse_count = 0
        self.solutions: list[Any] = []

    def __call__(
        self,
        sector: Any,
        ell: int,
        k: float,
        background: Any,
        boundary_config: BoundaryConfig | None = None,
    ) -> Any:
        config = boundary_config or BoundaryConfig()
        required = config.required_eval_radius
        if required is None:
            raise PilotContractError("risk-pilot radial cache requires an exact radius")
        key = _radial_cache_key(sector, ell, k, background, config)
        existing = self._entries.get(key)
        if existing is not None and _covers(existing, float(required)):
            self.reuse_count += 1
            return existing
        solution = self._solver(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            boundary_config=config,
        )
        self.solve_count += 1
        self.solutions.append(solution)
        if existing is None or _certified_upper(solution) >= _certified_upper(existing):
            self._entries[key] = solution
        return solution


def _certified_upper(solution: Any) -> float:
    value = solution.r_grid[-1] if solution.valid_until_r is None else solution.valid_until_r
    return float(value)


def _selected_code_hashes() -> dict[str, str]:
    candidates = {
        "pilot_module": Path(__file__),
        "partial_wave": Path("src/schwgw/scattering/partial_wave.py"),
        "radial_solver": Path("src/schwgw/numerics/radial_solver.py"),
        "risk_envelope": Path("src/schwgw/numerics/q018_delta0p1_risk_envelope.py"),
    }
    return {name: _sha256(path) for name, path in candidates.items() if path.is_file()}


def _input_records(review_npz: Path, gate_dir: Path) -> tuple[dict[str, Path], dict[str, str]]:
    paths = {
        "review_npz": review_npz,
        "review_json": review_npz.with_suffix(review_npz.suffix + ".json"),
        "review_manifest": review_npz.parent / "manifest.md",
        **{f"gate_{name}": gate_dir / name for name in _FROZEN_GATE_HASHES},
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise PilotContractError(f"missing frozen input(s): {missing}")
    hashes = {name: _sha256(path) for name, path in paths.items()}
    review_actual = {
        "npz": hashes["review_npz"],
        "json": hashes["review_json"],
        "manifest": hashes["review_manifest"],
    }
    if review_actual != _FROZEN_REVIEW_HASHES:
        raise PilotContractError("accepted T8aj source hash mismatch")
    gate_actual = {
        name: hashes[f"gate_{name}"] for name in _FROZEN_GATE_HASHES
    }
    if gate_actual != _FROZEN_GATE_HASHES:
        raise PilotContractError("accepted T4z/T7bv gate hash mismatch")
    return paths, hashes


def _contract(source_hashes: Mapping[str, str]) -> tuple[dict[str, Any], str]:
    value = {
        "schema_version": SCHEMA_VERSION,
        "frequencies": PILOT_FREQUENCIES,
        "lmax_values": {str(k): v for k, v in PILOT_LMAX_VALUES.items()},
        "points": [point.metadata() for point in TABLEI_POINTS],
        "M": 1.0,
        "A_plus": 0.9 + 1.1j,
        "A_cross": 0.4 + 0.6j,
        "incident_direction": "+z",
        "r_out": 300.0,
        "r_in_eps": 1.0e-6,
        "rtol": 1.0e-10,
        "atol": 1.0e-12,
        "convergence_tolerance": CONVERGENCE_TOLERANCE,
        "adapter": ADAPTER_NAME,
        "source_hashes": dict(source_hashes),
        "selected_code_hashes": _selected_code_hashes(),
    }
    return value, hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _validate_start_gate() -> None:
    try:
        record = _T7BV_RECORD_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise PilotContractError(f"cannot read T7bv record: {exc}") from exc
    if _T7BV_GREEN not in record:
        raise PilotContractError("T7bv exact GREEN is absent")


def _validate_output_tree(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    for path in output_dir.iterdir():
        if path.is_dir() and path.name in {"frequencies", "quarantine"}:
            continue
        if path.is_file() and path.name in _ROOT_FILES:
            continue
        raise PilotContractError(f"unexpected output path: {path}")
    frequencies = output_dir / "frequencies"
    if frequencies.exists():
        allowed = {
            f"kM_{_token(k)}.npz" for k in PILOT_FREQUENCIES
        } | {f"kM_{_token(k)}.npz.json" for k in PILOT_FREQUENCIES}
        for path in frequencies.iterdir():
            if not path.is_file() or path.name not in allowed:
                raise PilotContractError(f"unexpected frequency artifact: {path}")


def _load_ledger(path: Path, contract_hash: str) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "contract_hash": contract_hash,
            "completed": {},
        }
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PilotContractError(f"invalid checkpoint ledger: {exc}") from exc
    if value.get("contract_hash") != contract_hash or not isinstance(
        value.get("completed"), dict
    ):
        raise PilotContractError("checkpoint ledger contract mismatch")
    return value


def _transaction_paths(output_dir: Path, kM: float) -> tuple[Path, Path]:
    npz = output_dir / "frequencies" / f"kM_{_token(kM)}.npz"
    return npz, npz.with_suffix(npz.suffix + ".json")


def _valid_transaction(
    npz: Path,
    sidecar: Path,
    entry: Mapping[str, Any] | None,
    *,
    kM: float,
    contract_hash: str,
    source_hashes: Mapping[str, str],
) -> bool:
    if entry is None or not npz.is_file() or not sidecar.is_file():
        return False
    if entry.get("npz_sha256") != _sha256(npz) or entry.get("json_sha256") != _sha256(sidecar):
        return False
    try:
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        with np.load(npz, allow_pickle=False) as data:
            arrays_ok = (
                float(data["kM"].item()) == float(kM)
                and np.array_equal(data["point_ids"].astype(str), np.asarray([p.point_id for p in TABLEI_POINTS]))
                and data["F_plus_complex"].shape == (8,)
                and data["F_cross_complex"].shape == (8,)
            )
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False
    return bool(
        arrays_ok
        and metadata.get("complete") is True
        and metadata.get("contract_hash") == contract_hash
        and metadata.get("source_hashes") == dict(source_hashes)
        and metadata.get("adapter") == ADAPTER_NAME
        and metadata.get("lmax_values") == list(PILOT_LMAX_VALUES[kM])
    )


def _quarantine_pair(output_dir: Path, npz: Path, sidecar: Path) -> None:
    quarantine = output_dir / "quarantine"
    quarantine.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for path in (npz, sidecar):
        if path.exists():
            os.replace(path, quarantine / f"{path.name}.{stamp}")


def _warning_summary(cache: _FrequencyRadialCache) -> tuple[list[str], int]:
    codes: list[str] = []
    adapter_count = 0
    for solution in cache.solutions:
        diagnostics = getattr(solution, "diagnostics", None)
        for warning in getattr(diagnostics, "warnings", ()):
            code = str(getattr(warning, "code", "unknown"))
            codes.append(code)
            if code == "q018_tablei_delta0p1_risk_pilot_transition_oracle_used":
                adapter_count += 1
    return sorted(set(codes)), adapter_count


def _compute_frequency(
    kM: float,
    *,
    contract: Mapping[str, Any],
    contract_hash: str,
    source_hashes: Mapping[str, str],
    polarization_solver: Callable[..., Any],
    flat_solver: Callable[..., Any],
    radial_solver: Callable[..., Any],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    started = time.monotonic()
    background = SchwarzschildBackground(M=1.0)
    lmax_values = PILOT_LMAX_VALUES[kM]
    plus_history = np.empty((len(lmax_values), 8), dtype=np.complex128)
    cross_history = np.empty_like(plus_history)
    plus_mask = np.empty((len(lmax_values), 8), dtype=bool)
    cross_mask = np.empty_like(plus_mask)
    cache = _FrequencyRadialCache(radial_solver)
    point_order = sorted(range(8), key=lambda index: TABLEI_POINTS[index].r, reverse=True)
    for row, lmax in enumerate(lmax_values):
        for point_index in point_order:
            point = TABLEI_POINTS[point_index]
            boundary = BoundaryConfig(
                r_out=300.0,
                r_in_eps=1.0e-6,
                rtol=1.0e-10,
                atol=1.0e-12,
                required_eval_radius=point.r,
                experimental_required_radius_oracle=ADAPTER_NAME,
            )
            lensed = polarization_solver(
                background=background,
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
            valid_plus = _finite_complex(lensed.h_plus) and _finite_complex(flat.h_plus) and abs(flat.h_plus) > 0.0
            valid_cross = _finite_complex(lensed.h_cross) and _finite_complex(flat.h_cross) and abs(flat.h_cross) > 0.0
            plus_mask[row, point_index] = valid_plus
            cross_mask[row, point_index] = valid_cross
            plus_history[row, point_index] = lensed.h_plus / flat.h_plus if valid_plus else np.nan + 1j * np.nan
            cross_history[row, point_index] = lensed.h_cross / flat.h_cross if valid_cross else np.nan + 1j * np.nan
    if not plus_mask.all() or not cross_mask.all():
        raise PilotContractError(f"nonfinite or invalid ratio at kM={kM}")
    delta_plus = _relative_delta(plus_history[-1], plus_history[-2])
    delta_cross = _relative_delta(cross_history[-1], cross_history[-2])
    if not np.all(delta_plus <= CONVERGENCE_TOLERANCE) or not np.all(
        delta_cross <= CONVERGENCE_TOLERANCE
    ):
        raise PilotContractError(
            f"final adjacent lmax pair failed at kM={kM}; "
            f"max_plus={delta_plus.max():.17g}, max_cross={delta_cross.max():.17g}"
        )
    final_plus = plus_history[-1]
    final_cross = cross_history[-1]
    warning_codes, adapter_count = _warning_summary(cache)
    runtime = time.monotonic() - started
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "complete": True,
        "kM": kM,
        "point_ids": [point.point_id for point in TABLEI_POINTS],
        "lmax_values": list(lmax_values),
        "final_lmax_pair": list(lmax_values[-2:]),
        "max_final_pair_delta_plus": float(delta_plus.max()),
        "max_final_pair_delta_cross": float(delta_cross.max()),
        "runtime_seconds": runtime,
        "radial_solve_count": cache.solve_count,
        "radial_reuse_count": cache.reuse_count,
        "radial_warning_codes": warning_codes,
        "radial_warning_count": sum(
            len(getattr(getattr(solution, "diagnostics", None), "warnings", ()))
            for solution in cache.solutions
        ),
        "adapter_use_count": adapter_count,
        "adapter": ADAPTER_NAME,
        "contract_hash": contract_hash,
        "source_hashes": dict(source_hashes),
        "selected_code_hashes": contract["selected_code_hashes"],
        "git": _git_state(),
        "point_only": True,
        "risk_directed_pilot": True,
        "not_40_frequency_production": True,
        "no_kirchhoff": True,
        "no_interpolation": True,
        "no_smoothing": True,
        "no_fill": True,
        "not_fixture": True,
        "not_paper_style": True,
    }
    arrays = {
        "kM": np.asarray(kM),
        "point_ids": np.asarray([point.point_id for point in TABLEI_POINTS]),
        "point_group": np.asarray([point.group for point in TABLEI_POINTS]),
        "point_x": np.asarray([point.x for point in TABLEI_POINTS]),
        "point_y": np.asarray([point.y for point in TABLEI_POINTS]),
        "point_z": np.asarray([point.z for point in TABLEI_POINTS]),
        "point_r": np.asarray([point.r for point in TABLEI_POINTS]),
        "point_theta": np.asarray([point.theta for point in TABLEI_POINTS]),
        "point_phi": np.asarray([point.phi for point in TABLEI_POINTS]),
        "lmax_values": np.asarray(lmax_values, dtype=np.int64),
        "F_plus_history": plus_history,
        "F_cross_history": cross_history,
        "F_plus_complex": final_plus,
        "F_cross_complex": final_cross,
        "abs_F_plus": np.abs(final_plus),
        "abs_F_cross": np.abs(final_cross),
        "arg_F_plus_principal": np.angle(final_plus),
        "arg_F_cross_principal": np.angle(final_cross),
        "valid_ratio_plus_mask": plus_mask[-1],
        "valid_ratio_cross_mask": cross_mask[-1],
        "final_pair_delta_plus": delta_plus,
        "final_pair_delta_cross": delta_cross,
        "metadata_json": np.asarray(json.dumps(_json_safe(metadata), sort_keys=True)),
    }
    return arrays, metadata


def _finite_complex(value: complex) -> bool:
    return bool(np.isfinite(value.real) and np.isfinite(value.imag))


def _relative_delta(final: np.ndarray, previous: np.ndarray) -> np.ndarray:
    scale = np.maximum(1.0, np.maximum(np.abs(final), np.abs(previous)))
    return np.abs(final - previous) / scale


def _git_state() -> dict[str, Any]:
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        status = subprocess.check_output(["git", "status", "--short"], text=True).splitlines()
    except (OSError, subprocess.CalledProcessError):
        return {"available": False}
    return {"available": True, "head": head, "status_short": status}


def _write_transaction(
    output_dir: Path,
    kM: float,
    arrays: Mapping[str, np.ndarray],
    metadata: dict[str, Any],
) -> tuple[Path, Path, dict[str, Any]]:
    npz, sidecar = _transaction_paths(output_dir, kM)
    _atomic_npz(npz, arrays)
    metadata = dict(metadata)
    metadata["npz_sha256"] = _sha256(npz)
    _atomic_json(sidecar, metadata)
    entry = {
        "kM": kM,
        "npz_path": str(npz),
        "json_path": str(sidecar),
        "npz_sha256": _sha256(npz),
        "json_sha256": _sha256(sidecar),
        "runtime_seconds": metadata["runtime_seconds"],
        "radial_solve_count": metadata["radial_solve_count"],
        "radial_reuse_count": metadata["radial_reuse_count"],
        "adapter_use_count": metadata["adapter_use_count"],
        "max_final_pair_delta_plus": metadata["max_final_pair_delta_plus"],
        "max_final_pair_delta_cross": metadata["max_final_pair_delta_cross"],
    }
    return npz, sidecar, entry


def _load_frequency(npz_path: Path) -> dict[str, np.ndarray]:
    with np.load(npz_path, allow_pickle=False) as data:
        return {name: np.asarray(data[name]) for name in data.files if name != "metadata_json"}


def _aggregate(output_dir: Path, ledger: Mapping[str, Any], contract_hash: str) -> None:
    rows = []
    sidecars = []
    for kM in PILOT_FREQUENCIES:
        npz, sidecar = _transaction_paths(output_dir, kM)
        entry = ledger["completed"].get(_token(kM))
        if not _valid_transaction(
            npz,
            sidecar,
            entry,
            kM=kM,
            contract_hash=contract_hash,
            source_hashes=ledger["source_hashes"],
        ):
            raise PilotContractError(f"cannot aggregate invalid kM={kM} transaction")
        rows.append(_load_frequency(npz))
        sidecars.append(json.loads(sidecar.read_text(encoding="utf-8")))
    stack_names = (
        "F_plus_complex", "F_cross_complex", "abs_F_plus", "abs_F_cross",
        "arg_F_plus_principal", "arg_F_cross_principal",
        "valid_ratio_plus_mask", "valid_ratio_cross_mask",
        "final_pair_delta_plus", "final_pair_delta_cross",
    )
    arrays: dict[str, np.ndarray] = {
        "kM_values": np.asarray(PILOT_FREQUENCIES),
        "point_ids": rows[0]["point_ids"],
        "point_group": rows[0]["point_group"],
        "point_x": rows[0]["point_x"],
        "point_y": rows[0]["point_y"],
        "point_z": rows[0]["point_z"],
        "point_r": rows[0]["point_r"],
        "point_theta": rows[0]["point_theta"],
        "point_phi": rows[0]["point_phi"],
    }
    for name in stack_names:
        arrays[name] = np.stack([row[name] for row in rows])
    arrays["arg_F_plus_unwrapped"] = np.unwrap(arrays["arg_F_plus_principal"], axis=0)
    arrays["arg_F_cross_unwrapped"] = np.unwrap(arrays["arg_F_cross_principal"], axis=0)
    aggregate = output_dir / "risk_pilot_values.npz"
    aggregate_meta = {
        "schema_version": SCHEMA_VERSION,
        "contract_hash": contract_hash,
        "source_hashes": ledger["source_hashes"],
        "frequency_metadata": sidecars,
        "shape": [9, 8],
        "point_only": True,
        "risk_directed_pilot": True,
        "not_40_frequency_production": True,
        "no_kirchhoff": True,
        "no_interpolation": True,
        "no_smoothing": True,
        "no_fill": True,
        "not_fixture": True,
        "not_paper_style": True,
    }
    arrays["metadata_json"] = np.asarray(json.dumps(_json_safe(aggregate_meta), sort_keys=True))
    _atomic_npz(aggregate, arrays)
    aggregate_meta["npz_sha256"] = _sha256(aggregate)
    _atomic_json(aggregate.with_suffix(".npz.json"), aggregate_meta)


def _sampling_audit(output_dir: Path, review_npz: Path) -> None:
    aggregate_path = output_dir / "risk_pilot_values.npz"
    with np.load(aggregate_path, allow_pickle=False) as pilot, np.load(
        review_npz, allow_pickle=False
    ) as review:
        pilot_k = pilot["kM_values"]
        review_k = review["kM_values"]
        pilot_values = {
            "plus": pilot["F_plus_complex"], "cross": pilot["F_cross_complex"]
        }
        review_values = {
            "plus": review["F_plus_complex"], "cross": review["F_cross_complex"]
        }
        sequences = ((0.3, 0.4, 0.5), (0.75, 0.8, 0.9, 1.0),
                     (1.5, 1.6, 1.7, 1.75), (2.75, 2.8, 2.9, 3.0),
                     (3.75, 3.8, 3.9, 4.0))
        records: list[dict[str, Any]] = []
        for sequence in sequences:
            for component in ("plus", "cross"):
                values = np.stack([
                    _row_at(k, pilot_k, pilot_values[component], review_k, review_values[component])
                    for k in sequence
                ])
                magnitude = np.abs(values)
                phase = np.unwrap(np.angle(values), axis=0)
                mag_scale = np.maximum(
                    1.0, np.maximum(magnitude[:-1], magnitude[1:])
                )
                mag_steps = np.abs(np.diff(magnitude, axis=0)) / mag_scale
                phase_steps = np.abs(np.diff(phase, axis=0))
                records.append({
                    "sequence": list(sequence),
                    "component": component,
                    "complex_values": values,
                    "magnitude": magnitude,
                    "unwrapped_phase": phase,
                    "relative_magnitude_steps": mag_steps,
                    "absolute_phase_steps": phase_steps,
                    "magnitude_total_variation": np.sum(np.abs(np.diff(magnitude, axis=0)), axis=0),
                    "phase_total_variation": np.sum(phase_steps, axis=0),
                    "max_relative_magnitude_step": float(np.max(mag_steps)),
                    "max_absolute_phase_step": float(np.max(phase_steps)),
                    "interior_extrema": _interior_extrema(magnitude),
                })
    _atomic_json(
        output_dir / "risk_pilot_sampling_audit.json",
        {
            "schema_version": SCHEMA_VERSION,
            "diagnostic_only": True,
            "acceptance_decision_emitted": False,
            "sequences": records,
            "no_interpolation": True,
            "no_smoothing": True,
            "no_fill": True,
        },
    )


def _row_at(
    kM: float,
    pilot_k: np.ndarray,
    pilot_values: np.ndarray,
    review_k: np.ndarray,
    review_values: np.ndarray,
) -> np.ndarray:
    pilot_match = np.flatnonzero(pilot_k == kM)
    if pilot_match.size == 1:
        return pilot_values[pilot_match[0]]
    review_match = np.flatnonzero(review_k == kM)
    if review_match.size == 1:
        return review_values[review_match[0]]
    raise PilotContractError(f"sampling sequence frequency is unavailable: {kM}")


def _interior_extrema(magnitude: np.ndarray) -> list[dict[str, int]]:
    result = []
    for row in range(1, magnitude.shape[0] - 1):
        for column in range(magnitude.shape[1]):
            center = magnitude[row, column]
            if (center > magnitude[row - 1, column] and center > magnitude[row + 1, column]) or (
                center < magnitude[row - 1, column] and center < magnitude[row + 1, column]
            ):
                result.append({"sequence_index": row, "point_index": column})
    return result


def _manifest(output_dir: Path) -> None:
    files = sorted(
        path for path in output_dir.rglob("*")
        if path.is_file() and path.name != "manifest.md" and "quarantine" not in path.parts
    )
    lines = [
        "# Delta(kM)=0.1 Nine-Frequency Point-Only Risk Pilot",
        "",
        "This is not 40-frequency production. No interpolation, smoothing, fill,",
        "Kirchhoff, fixture, plot, or paper-style artifact is included.",
        "",
        "## Files",
        "",
    ]
    for path in files:
        lines.append(
            f"- `{path.relative_to(output_dir)}` — {path.stat().st_size} bytes — SHA256 `{_sha256(path)}`"
        )
    temporary = output_dir / "manifest.md.tmp"
    temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(temporary, output_dir / "manifest.md")


def run_delta0p1_risk_pilot(
    *,
    output_dir: str | Path = _DEFAULT_OUTPUT_DIR,
    accepted_review_npz: str | Path = _DEFAULT_REVIEW_NPZ,
    radial_gate_dir: str | Path = _DEFAULT_GATE_DIR,
    resume: bool = False,
    polarization_solver: Callable[..., Any] | None = None,
    flat_solver: Callable[..., Any] | None = None,
    radial_solver: Callable[..., Any] | None = None,
) -> Path:
    """Run or safely resume the frozen nine-frequency point-only risk pilot."""

    _validate_start_gate()
    output = Path(output_dir)
    review = Path(accepted_review_npz)
    gate = Path(radial_gate_dir)
    _validate_output_tree(output)
    _, source_hashes = _input_records(review, gate)
    contract, contract_hash = _contract(source_hashes)
    output.mkdir(parents=True, exist_ok=True)
    (output / "frequencies").mkdir(exist_ok=True)
    ledger_path = output / "checkpoint_ledger.json"
    ledger = _load_ledger(ledger_path, contract_hash)
    ledger["source_hashes"] = dict(source_hashes)
    compute = compute_polarization if polarization_solver is None else polarization_solver
    flat = compute_flat_no_lens_polarization if flat_solver is None else flat_solver
    radial = solve_radial_mode if radial_solver is None else radial_solver
    for kM in PILOT_FREQUENCIES:
        npz, sidecar = _transaction_paths(output, kM)
        token = _token(kM)
        entry = ledger["completed"].get(token)
        if resume and _valid_transaction(
            npz,
            sidecar,
            entry,
            kM=kM,
            contract_hash=contract_hash,
            source_hashes=source_hashes,
        ):
            continue
        if npz.exists() or sidecar.exists():
            _quarantine_pair(output, npz, sidecar)
            ledger["completed"].pop(token, None)
            _atomic_json(ledger_path, ledger)
        arrays, metadata = _compute_frequency(
            kM,
            contract=contract,
            contract_hash=contract_hash,
            source_hashes=source_hashes,
            polarization_solver=compute,
            flat_solver=flat,
            radial_solver=radial,
        )
        _, _, entry = _write_transaction(output, kM, arrays, metadata)
        ledger["completed"][token] = entry
        ledger["updated_at"] = datetime.now(timezone.utc).isoformat()
        _atomic_json(ledger_path, ledger)
    _aggregate(output, ledger, contract_hash)
    _sampling_audit(output, review)
    _manifest(output)
    return output / "risk_pilot_values.npz"


__all__ = [
    "ADAPTER_NAME",
    "CONVERGENCE_TOLERANCE",
    "PILOT_FREQUENCIES",
    "PILOT_LMAX_VALUES",
    "PilotContractError",
    "run_delta0p1_risk_pilot",
]
