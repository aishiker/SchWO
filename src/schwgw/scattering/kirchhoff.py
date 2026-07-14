from __future__ import annotations

from dataclasses import dataclass
import importlib
from types import MappingProxyType
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class KirchhoffEq47Result:
    gamma: np.ndarray
    eta: np.ndarray
    F_complex: np.ndarray
    abs_F: np.ndarray
    arg_F_principal: np.ndarray
    valid_mask: np.ndarray
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "gamma", np.asarray(self.gamma, dtype=float))
        object.__setattr__(self, "eta", np.asarray(self.eta, dtype=float))
        object.__setattr__(self, "F_complex", np.asarray(self.F_complex, dtype=complex))
        object.__setattr__(self, "abs_F", np.asarray(self.abs_F, dtype=float))
        object.__setattr__(
            self, "arg_F_principal", np.asarray(self.arg_F_principal, dtype=float)
        )
        object.__setattr__(self, "valid_mask", np.asarray(self.valid_mask, dtype=bool))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


def compute_kirchhoff_eq47(
    *,
    kM_values: np.ndarray,
    r_over_M: np.ndarray,
    theta: np.ndarray,
    dps: int = 50,
) -> KirchhoffEq47Result:
    """Evaluate the frozen scalar Eq. (47) comparison on a frequency/point grid."""

    kM = _positive_vector(kM_values, name="kM_values")
    radius = _positive_vector(r_over_M, name="r_over_M")
    angle = _theta_vector(theta, expected_size=radius.size)
    precision = int(dps)
    if precision != dps or precision < 30:
        raise ValueError("dps must be an integer greater than or equal to 30.")

    mp = _load_mpmath()
    gamma = -2.0 * kM
    eta = 0.5 * np.sqrt(radius) * np.tan(angle)
    values = np.empty((kM.size, radius.size), dtype=np.complex128)
    with mp.workdps(precision):
        for frequency_index, gamma_value in enumerate(gamma):
            gamma_mp = mp.mpf(str(float(gamma_value)))
            log_prefactor = (
                mp.pi * gamma_mp / 2
                + (-1j * gamma_mp) * mp.log(-gamma_mp)
                + mp.loggamma(1 + 1j * gamma_mp)
            )
            prefactor = mp.exp(log_prefactor)
            for point_index, eta_value in enumerate(eta):
                eta_mp = mp.mpf(str(float(eta_value)))
                kummer = mp.hyp1f1(
                    -1j * gamma_mp,
                    1,
                    -1j * gamma_mp * eta_mp**2,
                )
                values[frequency_index, point_index] = complex(prefactor * kummer)

    valid = np.isfinite(values.real) & np.isfinite(values.imag)
    if not valid.all():
        bad = np.argwhere(~valid).tolist()
        raise RuntimeError(f"Eq. (47) backend returned non-finite values at {bad}.")

    metadata = {
        "baseline": {
            "kind": "kirchhoff_eq47_scalar_comparison",
            "source": "Li-Hou-Zhao Eq. (47)",
            "fourier": "exp(-i k t)",
            "gamma_definition": "gamma = -2 M k",
            "power_branch": "principal real log for -gamma=2Mk>0",
            "gamma_function_branch": "principal complex Gamma(1+i gamma)",
            "kummer": "1F1(a,b,z)=Kummer M(a,b,z)",
            "argument": "-i gamma eta^2",
            "theta_F": "principal Arg(F_K) in (-pi, pi]",
            "comparison_only": True,
            "not_denominator": True,
            "not_mask": True,
            "not_normalization": True,
            "polarization_independent": True,
            "backend": "mpmath",
            "backend_version": str(mp.__version__),
            "dps": precision,
        }
    }
    return KirchhoffEq47Result(
        gamma=gamma,
        eta=eta,
        F_complex=values,
        abs_F=np.abs(values),
        arg_F_principal=np.angle(values),
        valid_mask=valid,
        metadata=metadata,
    )


def _load_mpmath():
    try:
        return importlib.import_module("mpmath")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Kirchhoff Eq. (47) requires the project optional dependency; "
            "install with `pip install -e '.[oracle]'`."
        ) from exc


def _positive_vector(values: np.ndarray, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional array.")
    if not np.isfinite(array).all() or np.any(array <= 0.0):
        raise ValueError(f"{name} must contain positive finite values.")
    return array


def _theta_vector(values: np.ndarray, *, expected_size: int) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size != expected_size:
        raise ValueError("theta must be one-dimensional and match r_over_M.")
    if not np.isfinite(array).all() or np.any(np.abs(array) >= np.pi / 2):
        raise ValueError("theta must be finite and satisfy abs(theta) < pi/2.")
    return array
