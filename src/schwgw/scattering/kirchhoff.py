from __future__ import annotations

from dataclasses import dataclass
import importlib
from types import MappingProxyType
from typing import Literal, Mapping

import numpy as np


KirchhoffPrefactorConvention = Literal[
    "standard_point_mass",
    "literal_paper_v1",
]


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
    """Evaluate Eq. (47) exactly as printed by Li--Hou--Zhao.

    The paper prints ``exp(+pi*gamma/2)`` with ``gamma=-2*M*k``.  Keep this
    function byte-for-byte compatible with that documented surface.  The
    separately named :func:`compute_kirchhoff_figure_consistent` evaluates
    the sign needed to reproduce the oscillatory dashed curves in Figs. 5--6.
    """

    return compute_kirchhoff(
        kM_values=kM_values,
        r_over_M=r_over_M,
        theta=theta,
        dps=dps,
        prefactor_convention="literal_paper_v1",
    )


def compute_kirchhoff_figure_consistent(
    *,
    kM_values: np.ndarray,
    r_over_M: np.ndarray,
    theta: np.ndarray,
    dps: int = 50,
) -> KirchhoffEq47Result:
    r"""Evaluate the Fig. 5/6-consistent Kirchhoff convention.

    This uses

    ``exp(-pi*gamma/2) (-gamma)^(-i*gamma) Gamma(1+i*gamma)``

    with ``gamma=-2*M*k`` and the same Kummer factor and branches as the
    printed Eq. (47).  The real exponential changes the magnitude only; the
    complex phase is identical to the printed-sign result.
    """

    return compute_kirchhoff(
        kM_values=kM_values,
        r_over_M=r_over_M,
        theta=theta,
        dps=dps,
        prefactor_convention="standard_point_mass",
    )


def compute_kirchhoff(
    *,
    kM_values: np.ndarray,
    r_over_M: np.ndarray,
    theta: np.ndarray,
    dps: int = 50,
    prefactor_convention: KirchhoffPrefactorConvention = "standard_point_mass",
) -> KirchhoffEq47Result:
    r"""Evaluate the point-mass Kirchhoff amplification on a point grid.

    ``standard_point_mass`` is the scientific default and uses
    ``exp(-pi*gamma/2)`` for ``gamma=-2Mk``.  ``literal_paper_v1`` is retained
    only to reproduce the sign printed in Li--Hou--Zhao v1 Eq. (47); that
    printed sign fails the independent on-axis point-mass identity and does
    not reproduce the paper's own Figs. 5--6.
    """

    conventions = {
        "standard_point_mass": (
            -1,
            "kirchhoff_standard_point_mass_comparison",
            (
                "standard point-mass convention; Li-Hou-Zhao Eq. (47) with "
                "figure-consistent exp(-pi gamma/2) prefactor"
            ),
        ),
        "literal_paper_v1": (
            1,
            "kirchhoff_eq47_literal_paper_v1_comparison",
            "Li-Hou-Zhao v1 Eq. (47), literal printed sign",
        ),
    }
    try:
        exponential_sign, kind, source = conventions[prefactor_convention]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            "prefactor_convention must be 'standard_point_mass' or "
            "'literal_paper_v1'."
        ) from exc
    return _compute_kirchhoff(
        kM_values=kM_values,
        r_over_M=r_over_M,
        theta=theta,
        dps=dps,
        exponential_sign=exponential_sign,
        kind=kind,
        source=source,
        prefactor_convention=prefactor_convention,
    )


def standard_point_mass_axis_intensity(kM_values: np.ndarray) -> np.ndarray:
    r"""Return the independent on-axis identity ``|F(eta=0)|^2``.

    For the standard point-mass branch and ``gamma=-2Mk``,

    ``|F(0)|^2 = 4*pi*Mk / (1 - exp(-4*pi*Mk))``.

    The ``expm1`` form remains accurate at small positive ``Mk`` and does not
    reuse the complex Kummer/Gamma implementation exercised by
    :func:`compute_kirchhoff`.
    """

    kM = _positive_vector(kM_values, name="kM_values")
    numerator = 4.0 * np.pi * kM
    return numerator / (-np.expm1(-numerator))


def _compute_kirchhoff(
    *,
    kM_values: np.ndarray,
    r_over_M: np.ndarray,
    theta: np.ndarray,
    dps: int,
    exponential_sign: int,
    kind: str,
    source: str,
    prefactor_convention: KirchhoffPrefactorConvention,
) -> KirchhoffEq47Result:
    if exponential_sign not in {-1, 1}:
        raise ValueError("exponential_sign must be -1 or +1.")

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
                exponential_sign * mp.pi * gamma_mp / 2
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
            "kind": kind,
            "source": source,
            "prefactor_convention": prefactor_convention,
            "fourier": "exp(-i k t)",
            "gamma_definition": "gamma = -2 M k",
            "real_exponential_prefactor": (
                "exp(+pi gamma/2)"
                if exponential_sign == 1
                else "exp(-pi gamma/2)"
            ),
            "printed_equation_preserved_by": "compute_kirchhoff_eq47",
            "paper_v1_equation_status": (
                "known_printed-sign discrepancy with Figs. 5--6 and the "
                "standard on-axis point-mass identity"
            ),
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
