from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when a solver YAML config violates the T8 data-output schema."""


@dataclass(frozen=True)
class BackgroundConfig:
    M: float


@dataclass(frozen=True)
class WaveConfig:
    kM: float
    A_plus: complex
    A_cross: complex


@dataclass(frozen=True)
class RangeSettings:
    start: float
    stop: float
    step: float
    endpoint: bool

    def to_dict(self) -> dict[str, float | bool]:
        return {
            "start": self.start,
            "stop": self.stop,
            "step": self.step,
            "endpoint": self.endpoint,
        }


@dataclass(frozen=True)
class ObserverConfig:
    kind: str = "angular"
    r: float | None = None
    theta_values: tuple[float, ...] = ()
    phi_values: tuple[float, ...] = ()
    theta_range: RangeSettings | None = None
    phi_range: RangeSettings | None = None
    x_values: tuple[float, ...] = ()
    z_values: tuple[float, ...] = ()
    invalid_radius_policy: str | None = None


@dataclass(frozen=True)
class BoundarySettings:
    r_in_eps: float
    r_out: float
    rtol: float
    atol: float
    required_eval_radius: float | None = None
    experimental_required_radius_oracle: str | None = None


@dataclass(frozen=True)
class NumericsConfig:
    lmax: int
    boundary: BoundarySettings


@dataclass(frozen=True)
class ConvergenceConfig:
    enabled: bool
    lmax_values: tuple[int, ...]
    theta_values: tuple[float, ...]
    phi_values: tuple[float, ...]
    selected_threshold: float
    near_axis_threshold: float
    theta_range: RangeSettings | None = None
    phi_range: RangeSettings | None = None


@dataclass(frozen=True)
class SolverConfig:
    case_id: str
    output: str
    background: BackgroundConfig
    wave: WaveConfig
    observer: ObserverConfig
    numerics: NumericsConfig
    convergence: ConvergenceConfig | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "case_id": self.case_id,
            "output": self.output,
            "background": {"M": self.background.M},
            "wave": {
                "kM": self.wave.kM,
                "A_plus": _complex_to_dict(self.wave.A_plus),
                "A_cross": _complex_to_dict(self.wave.A_cross),
            },
            "observer": self._observer_to_dict(),
            "numerics": {
                "lmax": self.numerics.lmax,
                "boundary": self._boundary_to_dict(),
            },
        }
        if self.convergence is not None:
            convergence_payload = {
                "enabled": self.convergence.enabled,
                "lmax_values": list(self.convergence.lmax_values),
                "theta_values": list(self.convergence.theta_values),
                "phi_values": list(self.convergence.phi_values),
                "selected_threshold": self.convergence.selected_threshold,
                "near_axis_threshold": self.convergence.near_axis_threshold,
            }
            if self.convergence.theta_range is not None:
                convergence_payload["theta_range"] = self.convergence.theta_range.to_dict()
            if self.convergence.phi_range is not None:
                convergence_payload["phi_range"] = self.convergence.phi_range.to_dict()
            payload["convergence"] = convergence_payload
        return payload

    def _boundary_to_dict(self) -> dict[str, Any]:
        boundary = {
            "r_in_eps": self.numerics.boundary.r_in_eps,
            "r_out": self.numerics.boundary.r_out,
            "rtol": self.numerics.boundary.rtol,
            "atol": self.numerics.boundary.atol,
        }
        if self.numerics.boundary.required_eval_radius is not None:
            boundary["required_eval_radius"] = self.numerics.boundary.required_eval_radius
        if self.numerics.boundary.experimental_required_radius_oracle is not None:
            boundary["experimental_required_radius_oracle"] = (
                self.numerics.boundary.experimental_required_radius_oracle
            )
        return boundary

    def _observer_to_dict(self) -> dict[str, Any]:
        if self.observer.kind == "angular":
            observer = {
                "r": self.observer.r,
                "theta_values": list(self.observer.theta_values),
                "phi_values": list(self.observer.phi_values),
            }
            if self.observer.theta_range is not None:
                observer["theta_range"] = self.observer.theta_range.to_dict()
            if self.observer.phi_range is not None:
                observer["phi_range"] = self.observer.phi_range.to_dict()
            return observer
        if self.observer.kind == "xz_plane":
            return {
                "kind": "xz_plane",
                "x_values": list(self.observer.x_values),
                "z_values": list(self.observer.z_values),
                "invalid_radius_policy": self.observer.invalid_radius_policy,
            }
        raise ConfigError(f"Unsupported observer.kind in SolverConfig: {self.observer.kind}.")


def load_config(path: str | Path) -> SolverConfig:
    """Load and validate a YAML solver-output config."""

    config_path = Path(path)
    with config_path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict):
        raise ConfigError("Config root must be a YAML mapping.")
    return parse_config(raw)


def parse_config(raw: dict[str, Any]) -> SolverConfig:
    case_id = _required_string(raw, "case_id")
    output = _required_string(raw, "output")

    background_raw = _required_mapping(raw, "background")
    mass = _required_float(background_raw, "background.M")
    if mass <= 0.0:
        raise ConfigError("background.M must be positive.")

    wave_raw = _required_mapping(raw, "wave")
    kM = _required_float(wave_raw, "wave.kM")
    if kM <= 0.0:
        raise ConfigError("wave.kM must be positive.")
    A_plus = _required_complex(wave_raw, "wave.A_plus")
    A_cross = _required_complex(wave_raw, "wave.A_cross")

    observer_raw = _required_mapping(raw, "observer")
    observer = _parse_observer(observer_raw, mass=mass)

    numerics_raw = _required_mapping(raw, "numerics")
    lmax = _required_int(numerics_raw, "numerics.lmax")
    if lmax < 2:
        raise ConfigError("numerics.lmax must be at least 2.")
    boundary_raw = _required_mapping(numerics_raw, "numerics.boundary")
    boundary = BoundarySettings(
        r_in_eps=_required_float(boundary_raw, "numerics.boundary.r_in_eps"),
        r_out=_required_float(boundary_raw, "numerics.boundary.r_out"),
        rtol=_required_float(boundary_raw, "numerics.boundary.rtol"),
        atol=_required_float(boundary_raw, "numerics.boundary.atol"),
        required_eval_radius=_optional_float(
            boundary_raw,
            "numerics.boundary.required_eval_radius",
        ),
        experimental_required_radius_oracle=_optional_string(
            boundary_raw,
            "numerics.boundary.experimental_required_radius_oracle",
        ),
    )
    if boundary.r_in_eps <= 0.0:
        raise ConfigError("numerics.boundary.r_in_eps must be positive.")
    _validate_boundary_covers_observer(boundary, observer, mass=mass)
    if boundary.rtol <= 0.0 or boundary.atol <= 0.0:
        raise ConfigError("numerics.boundary tolerances must be positive.")
    if boundary.required_eval_radius is not None:
        if not math.isfinite(boundary.required_eval_radius):
            raise ConfigError("numerics.boundary.required_eval_radius must be finite.")
        if boundary.required_eval_radius <= 2.0 * mass:
            raise ConfigError("numerics.boundary.required_eval_radius must be greater than 2M.")
        if boundary.required_eval_radius > boundary.r_out:
            raise ConfigError("numerics.boundary.required_eval_radius must not exceed r_out.")
    convergence = _optional_convergence(raw, lmax)

    return SolverConfig(
        case_id=case_id,
        output=output,
        background=BackgroundConfig(M=mass),
        wave=WaveConfig(kM=kM, A_plus=A_plus, A_cross=A_cross),
        observer=observer,
        numerics=NumericsConfig(lmax=lmax, boundary=boundary),
        convergence=convergence,
    )


def _parse_observer(raw: dict[str, Any], *, mass: float) -> ObserverConfig:
    kind = raw.get("kind", "angular")
    if not isinstance(kind, str):
        raise ConfigError("observer.kind must be a string.")
    if kind not in {"angular", "xz_plane"}:
        raise ConfigError("observer.kind must be one of ['angular', 'xz_plane'].")
    if kind == "angular":
        radius = _required_float(raw, "observer.r")
        if radius <= 2.0 * mass:
            raise ConfigError("observer.r must be greater than 2M.")
        theta_values, theta_range = _axis_values_or_range(
            raw,
            prefix="observer",
            axis="theta",
            allow_endpoint_false=True,
        )
        phi_values, phi_range = _axis_values_or_range(
            raw,
            prefix="observer",
            axis="phi",
            allow_endpoint_false=True,
        )
        return ObserverConfig(
            kind="angular",
            r=radius,
            theta_values=theta_values,
            phi_values=phi_values,
            theta_range=theta_range,
            phi_range=phi_range,
        )

    policy = _required_string(raw, "observer.invalid_radius_policy")
    if policy != "mask":
        raise ConfigError("observer.invalid_radius_policy must be 'mask'.")
    x_values = _xz_axis_values(raw, axis="x")
    z_values = _xz_axis_values(raw, axis="z")
    valid_radii = _valid_xz_radii(x_values, z_values, mass=mass)
    if not valid_radii:
        raise ConfigError("observer x-z grid must contain at least one valid point.")
    return ObserverConfig(
        kind="xz_plane",
        x_values=x_values,
        z_values=z_values,
        invalid_radius_policy=policy,
    )


def _xz_axis_values(raw: dict[str, Any], *, axis: str) -> tuple[float, ...]:
    values_key = f"{axis}_values"
    range_key = f"{axis}_range"
    dotted_values = f"observer.{values_key}"
    dotted_range = f"observer.{range_key}"
    has_values = values_key in raw
    has_range = range_key in raw
    if has_values and has_range:
        raise ConfigError(f"{dotted_values} and {dotted_range} are mutually exclusive.")
    if has_values:
        return _required_float_sequence(raw, dotted_values)
    if has_range:
        values, _ = _range_values(
            raw,
            dotted_range,
            allow_endpoint_false=False,
        )
        return values
    return _required_float_sequence(raw, dotted_values)


def _axis_values_or_range(
    raw: dict[str, Any],
    *,
    prefix: str,
    axis: str,
    allow_endpoint_false: bool,
) -> tuple[tuple[float, ...], RangeSettings | None]:
    values_key = f"{axis}_values"
    range_key = f"{axis}_range"
    dotted_values = f"{prefix}.{values_key}"
    dotted_range = f"{prefix}.{range_key}"
    has_values = values_key in raw
    has_range = range_key in raw
    if has_values and has_range:
        raise ConfigError(f"{dotted_values} and {dotted_range} are mutually exclusive.")
    if has_values:
        return _required_float_sequence(raw, dotted_values), None
    if has_range:
        return _range_values(
            raw,
            dotted_range,
            allow_endpoint_false=allow_endpoint_false,
        )
    raise ConfigError(f"Missing required field: {dotted_values} or {dotted_range}.")


def _range_values(
    raw: dict[str, Any],
    key: str,
    *,
    allow_endpoint_false: bool,
) -> tuple[tuple[float, ...], RangeSettings]:
    range_raw = _required_mapping(raw, key)
    start = _required_float(range_raw, f"{key}.start")
    stop = _required_float(range_raw, f"{key}.stop")
    step = _required_float(range_raw, f"{key}.step")
    endpoint = _required_bool(range_raw, f"{key}.endpoint")
    if endpoint is not True and not allow_endpoint_false:
        raise ConfigError(f"{key}.endpoint must be true.")
    if step <= 0.0:
        raise ConfigError(f"{key}.step must be positive.")
    if stop <= start:
        raise ConfigError(f"{key}.stop must be greater than start.")
    settings = RangeSettings(
        start=start,
        stop=stop,
        step=step,
        endpoint=endpoint,
    )
    if endpoint:
        span_steps = (stop - start) / step
        rounded_steps = round(span_steps)
        if not math.isclose(
            span_steps,
            rounded_steps,
            rel_tol=1.0e-12,
            abs_tol=1.0e-12,
        ):
            raise ConfigError(f"{key} must land exactly on stop when endpoint is true.")
        values = [_canonical_float(start + index * step) for index in range(rounded_steps + 1)]
        values[-1] = _canonical_float(stop)
        return tuple(values), settings

    values = []
    index = 0
    while True:
        value = start + index * step
        if value >= stop or math.isclose(value, stop, rel_tol=1.0e-12, abs_tol=1.0e-12):
            break
        values.append(_canonical_float(value))
        index += 1
        if index > 10_000_000:
            raise ConfigError(f"{key} generated too many values.")
    if not values:
        raise ConfigError(f"{key} generated an empty range.")
    return tuple(values), settings


def _canonical_float(value: float) -> float:
    value = float(value)
    if abs(value) < 1.0e-14:
        return 0.0
    return value


def _valid_xz_radii(
    x_values: tuple[float, ...],
    z_values: tuple[float, ...],
    *,
    mass: float,
) -> list[float]:
    valid_radii = []
    horizon_radius = 2.0 * mass
    for z_value in z_values:
        for x_value in x_values:
            radius = math.hypot(x_value, z_value)
            if math.isfinite(radius) and radius > horizon_radius:
                valid_radii.append(radius)
    return valid_radii


def _validate_boundary_covers_observer(
    boundary: BoundarySettings,
    observer: ObserverConfig,
    *,
    mass: float,
) -> None:
    if observer.kind == "angular":
        if observer.r is None:
            raise ConfigError("observer.r is required for angular grids.")
        if boundary.r_out <= observer.r:
            raise ConfigError("numerics.boundary.r_out must be greater than observer.r.")
        return

    valid_radii = _valid_xz_radii(
        observer.x_values,
        observer.z_values,
        mass=mass,
    )
    if not valid_radii:
        raise ConfigError("observer x-z grid must contain at least one valid point.")
    if boundary.r_out <= max(valid_radii):
        raise ConfigError(
            "numerics.boundary.r_out must be greater than the maximum valid x-z radius."
        )


def _optional_convergence(raw: dict[str, Any], numerics_lmax: int) -> ConvergenceConfig | None:
    if "convergence" not in raw:
        return None
    convergence_raw = raw["convergence"]
    if not isinstance(convergence_raw, dict):
        raise ConfigError("convergence must be a mapping.")
    enabled = _required_bool(convergence_raw, "convergence.enabled")
    if not enabled:
        return None
    lmax_values = _required_lmax_sequence(convergence_raw, "convergence.lmax_values")
    if numerics_lmax != lmax_values[-1]:
        raise ConfigError("numerics.lmax must equal convergence.lmax_values[-1].")
    theta_values, theta_range = _axis_values_or_range(
        convergence_raw,
        prefix="convergence",
        axis="theta",
        allow_endpoint_false=True,
    )
    phi_values, phi_range = _axis_values_or_range(
        convergence_raw,
        prefix="convergence",
        axis="phi",
        allow_endpoint_false=True,
    )
    selected_threshold = _required_float(
        convergence_raw,
        "convergence.selected_threshold",
    )
    near_axis_threshold = _required_float(
        convergence_raw,
        "convergence.near_axis_threshold",
    )
    if selected_threshold <= 0.0:
        raise ConfigError("convergence.selected_threshold must be positive.")
    if near_axis_threshold <= 0.0:
        raise ConfigError("convergence.near_axis_threshold must be positive.")
    return ConvergenceConfig(
        enabled=True,
        lmax_values=lmax_values,
        theta_values=theta_values,
        phi_values=phi_values,
        selected_threshold=selected_threshold,
        near_axis_threshold=near_axis_threshold,
        theta_range=theta_range,
        phi_range=phi_range,
    )


def _required_mapping(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = _lookup(raw, key)
    if not isinstance(value, dict):
        raise ConfigError(f"{key} must be a mapping.")
    return value


def _required_string(raw: dict[str, Any], key: str) -> str:
    value = _lookup(raw, key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key} must be a non-empty string.")
    return value


def _required_float(raw: dict[str, Any], key: str) -> float:
    value = _lookup(raw, key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{key} must be a real number.")
    return float(value)


def _optional_float(raw: dict[str, Any], key: str) -> float | None:
    lookup_key = key.rsplit(".", maxsplit=1)[-1]
    if lookup_key not in raw:
        return None
    value = raw[lookup_key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{key} must be a real number.")
    return float(value)


def _required_int(raw: dict[str, Any], key: str) -> int:
    value = _lookup(raw, key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{key} must be an integer.")
    return int(value)


def _required_bool(raw: dict[str, Any], key: str) -> bool:
    value = _lookup(raw, key)
    if not isinstance(value, bool):
        raise ConfigError(f"{key} must be a boolean.")
    return value


def _optional_string(raw: dict[str, Any], key: str) -> str | None:
    lookup_key = key.rsplit(".", maxsplit=1)[-1]
    if lookup_key not in raw:
        return None
    value = raw[lookup_key]
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key} must be a non-empty string.")
    return value


def _required_float_sequence(raw: dict[str, Any], key: str) -> tuple[float, ...]:
    value = _lookup(raw, key)
    if not isinstance(value, list) or not value:
        raise ConfigError(f"{key} must be a non-empty list.")
    values = []
    for index, item in enumerate(value):
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ConfigError(f"{key}[{index}] must be a real number.")
        values.append(float(item))
    return tuple(values)


def _required_lmax_sequence(raw: dict[str, Any], key: str) -> tuple[int, ...]:
    value = _lookup(raw, key)
    if not isinstance(value, list) or len(value) < 2:
        raise ConfigError(f"{key} must be a list with at least two entries.")
    values = []
    previous = None
    for index, item in enumerate(value):
        if isinstance(item, bool) or not isinstance(item, int):
            raise ConfigError(f"{key}[{index}] must be an integer.")
        if item < 2:
            raise ConfigError(f"{key}[{index}] must be at least 2.")
        if previous is not None and item <= previous:
            raise ConfigError(f"{key} must be strictly increasing.")
        values.append(int(item))
        previous = item
    return tuple(values)


def _required_complex(raw: dict[str, Any], key: str) -> complex:
    value = _lookup(raw, key)
    if not isinstance(value, dict):
        raise ConfigError(f"{key} must be a mapping with real and imag.")
    real = _required_float(value, f"{key}.real")
    imag = _required_float(value, f"{key}.imag")
    return complex(real, imag)


def _lookup(raw: dict[str, Any], dotted_key: str) -> Any:
    key = dotted_key.rsplit(".", maxsplit=1)[-1]
    if key not in raw:
        raise ConfigError(f"Missing required field: {dotted_key}.")
    return raw[key]


def _complex_to_dict(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


__all__ = [
    "BackgroundConfig",
    "BoundarySettings",
    "ConvergenceConfig",
    "ConfigError",
    "NumericsConfig",
    "ObserverConfig",
    "RangeSettings",
    "SolverConfig",
    "WaveConfig",
    "load_config",
    "parse_config",
]
