from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

import numpy as np

from schwgw.scattering.partial_wave import compute_flat_no_lens_polarization


@dataclass(frozen=True)
class PointwiseAmplificationResult:
    """Pointwise wave-optics amplification against the flat no-lens baseline."""

    F_plus_complex: np.ndarray
    F_cross_complex: np.ndarray
    amplification_plus: np.ndarray
    amplification_cross: np.ndarray
    intensity_plus_ratio: np.ndarray
    intensity_cross_ratio: np.ndarray
    F_pol_norm: np.ndarray
    I_pol_ratio: np.ndarray
    valid_ratio_plus_mask: np.ndarray
    valid_ratio_cross_mask: np.ndarray
    valid_ratio_norm_mask: np.ndarray
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "F_plus_complex", np.asarray(self.F_plus_complex))
        object.__setattr__(self, "F_cross_complex", np.asarray(self.F_cross_complex))
        object.__setattr__(self, "amplification_plus", np.asarray(self.amplification_plus))
        object.__setattr__(self, "amplification_cross", np.asarray(self.amplification_cross))
        object.__setattr__(
            self,
            "intensity_plus_ratio",
            np.asarray(self.intensity_plus_ratio),
        )
        object.__setattr__(
            self,
            "intensity_cross_ratio",
            np.asarray(self.intensity_cross_ratio),
        )
        object.__setattr__(self, "F_pol_norm", np.asarray(self.F_pol_norm))
        object.__setattr__(self, "I_pol_ratio", np.asarray(self.I_pol_ratio))
        object.__setattr__(
            self,
            "valid_ratio_plus_mask",
            np.asarray(self.valid_ratio_plus_mask, dtype=bool),
        )
        object.__setattr__(
            self,
            "valid_ratio_cross_mask",
            np.asarray(self.valid_ratio_cross_mask, dtype=bool),
        )
        object.__setattr__(
            self,
            "valid_ratio_norm_mask",
            np.asarray(self.valid_ratio_norm_mask, dtype=bool),
        )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


def compute_pointwise_amplification(
    *,
    h_plus_lensed: np.ndarray,
    h_cross_lensed: np.ndarray,
    h_plus_unlensed: np.ndarray,
    h_cross_unlensed: np.ndarray,
    valid_lensed_mask: np.ndarray | None,
    A_plus: complex,
    A_cross: complex,
    denominator_atol_factor: float = 1.0e-14,
    denominator_rtol_factor: float = 1.0e-12,
) -> PointwiseAmplificationResult:
    """Compute M5 pointwise wave-optics amplification ratios."""

    atol_factor = _positive_factor(
        denominator_atol_factor,
        name="denominator_atol_factor",
    )
    rtol_factor = _positive_factor(
        denominator_rtol_factor,
        name="denominator_rtol_factor",
    )
    plus_lensed = np.asarray(h_plus_lensed, dtype=complex)
    cross_lensed = np.asarray(h_cross_lensed, dtype=complex)
    plus_unlensed = np.asarray(h_plus_unlensed, dtype=complex)
    cross_unlensed = np.asarray(h_cross_unlensed, dtype=complex)
    _validate_same_shape(
        plus_lensed,
        cross_lensed,
        plus_unlensed,
        cross_unlensed,
    )
    valid_mask = _valid_mask(valid_lensed_mask, shape=plus_lensed.shape)

    real_dtype = np.float64
    tiny = np.finfo(real_dtype).tiny
    a_scale = max(abs(complex(A_plus)), abs(complex(A_cross)), tiny)

    h_norm_lensed = np.sqrt(np.abs(plus_lensed) ** 2 + np.abs(cross_lensed) ** 2)
    h_norm_unlensed = np.sqrt(
        np.abs(plus_unlensed) ** 2 + np.abs(cross_unlensed) ** 2
    )

    plus_grid_scale = _max_valid_abs(plus_unlensed, valid_mask)
    cross_grid_scale = _max_valid_abs(cross_unlensed, valid_mask)
    norm_grid_scale = _max_valid_real(h_norm_unlensed, valid_mask)
    eps_plus = max(atol_factor * a_scale, rtol_factor * plus_grid_scale)
    eps_cross = max(atol_factor * a_scale, rtol_factor * cross_grid_scale)
    eps_norm = max(atol_factor * a_scale, rtol_factor * norm_grid_scale)

    valid_plus = valid_mask & np.isfinite(plus_unlensed) & (np.abs(plus_unlensed) > eps_plus)
    valid_cross = (
        valid_mask
        & np.isfinite(cross_unlensed)
        & (np.abs(cross_unlensed) > eps_cross)
    )
    valid_norm = (
        valid_mask
        & np.isfinite(h_norm_unlensed)
        & (h_norm_unlensed > eps_norm)
    )

    f_plus = _complex_nan_array(plus_lensed.shape)
    f_cross = _complex_nan_array(cross_lensed.shape)
    f_plus[valid_plus] = plus_lensed[valid_plus] / plus_unlensed[valid_plus]
    f_cross[valid_cross] = cross_lensed[valid_cross] / cross_unlensed[valid_cross]

    f_norm = _real_nan_array(plus_lensed.shape)
    i_norm = _real_nan_array(plus_lensed.shape)
    f_norm[valid_norm] = h_norm_lensed[valid_norm] / h_norm_unlensed[valid_norm]
    i_norm[valid_norm] = (
        h_norm_lensed[valid_norm] ** 2 / h_norm_unlensed[valid_norm] ** 2
    )

    metadata = {
        "normalization": {
            "kind": "pointwise_wave_optics_amplification",
            "version": "m5a_t1_v1",
            "baseline": "flat_no_lens",
            "baseline_api": "compute_flat_no_lens_polarization",
            "fourier": "exp(-i k t)",
            "incident_direction": "+z",
            "same_k": True,
            "same_A_plus_A_cross": True,
            "same_observer_coordinates": True,
            "polarization_bridge": (
                "Route B incident-frame electric tidal packaged scalars"
            ),
            "no_schwarzschild_horizon_boundary_in_baseline": True,
            "no_tiny_M_baseline": True,
            "excludes_radial_horizon_transmission": True,
            "excludes_radial_absorption": True,
            "denominator_policy": (
                "independent masks, NaN where denominator mask is false"
            ),
            "denominator_atol_factor": atol_factor,
            "denominator_rtol_factor": rtol_factor,
            "eps_plus": float(eps_plus),
            "eps_cross": float(eps_cross),
            "eps_norm": float(eps_norm),
            "mask_fields": [
                "valid_ratio_plus_mask",
                "valid_ratio_cross_mask",
                "valid_ratio_norm_mask",
            ],
        }
    }

    amplification_plus = np.abs(f_plus)
    amplification_cross = np.abs(f_cross)
    return PointwiseAmplificationResult(
        F_plus_complex=f_plus,
        F_cross_complex=f_cross,
        amplification_plus=amplification_plus,
        amplification_cross=amplification_cross,
        intensity_plus_ratio=amplification_plus**2,
        intensity_cross_ratio=amplification_cross**2,
        F_pol_norm=f_norm,
        I_pol_ratio=i_norm,
        valid_ratio_plus_mask=valid_plus,
        valid_ratio_cross_mask=valid_cross,
        valid_ratio_norm_mask=valid_norm,
        metadata=metadata,
    )


def flat_no_lens_baseline_at_point(
    *,
    k: float,
    r: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    lmax: int = 2,
) -> tuple[complex, complex]:
    """Return the flat/no-lens baseline at one observer point."""

    result = compute_flat_no_lens_polarization(
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=A_plus,
        A_cross=A_cross,
        lmax=lmax,
    )
    return result.h_plus, result.h_cross


def _positive_factor(value: float, *, name: str) -> float:
    factor = float(value)
    if not np.isfinite(factor) or factor <= 0.0:
        raise ValueError(f"{name} must be positive and finite.")
    return factor


def _validate_same_shape(*arrays: np.ndarray) -> None:
    shape = arrays[0].shape
    if any(array.shape != shape for array in arrays):
        raise ValueError("All lensed and unlensed polarization arrays must have the same shape.")


def _valid_mask(mask: np.ndarray | None, *, shape: tuple[int, ...]) -> np.ndarray:
    if mask is None:
        return np.ones(shape, dtype=bool)
    valid = np.asarray(mask, dtype=bool)
    if valid.shape != shape:
        raise ValueError("valid_lensed_mask must have the same shape as polarization arrays.")
    return valid


def _max_valid_abs(values: np.ndarray, valid_mask: np.ndarray) -> float:
    mask = valid_mask & np.isfinite(values)
    if not np.any(mask):
        return 0.0
    return float(np.max(np.abs(values[mask])))


def _max_valid_real(values: np.ndarray, valid_mask: np.ndarray) -> float:
    mask = valid_mask & np.isfinite(values)
    if not np.any(mask):
        return 0.0
    return float(np.max(values[mask]))


def _complex_nan_array(shape: tuple[int, ...]) -> np.ndarray:
    values = np.empty(shape, dtype=complex)
    values[...] = np.nan + 1.0j * np.nan
    return values


def _real_nan_array(shape: tuple[int, ...]) -> np.ndarray:
    values = np.empty(shape, dtype=float)
    values[...] = np.nan
    return values


__all__ = [
    "PointwiseAmplificationResult",
    "compute_pointwise_amplification",
    "flat_no_lens_baseline_at_point",
]
