"""Pure mode-level formulas for the frozen Phase-6 V2.2 three-route gate.

This module has no filesystem, radial-solver, angular-sum, or observer-frame
effects.  Route B implements the large-r RW-gauge metric/curvature chain in a
reduced tensor-harmonic channel, so no observation angle is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass

import mpmath as mp


ROUTE_PAIRS = ("A_B", "A_C", "B_C")
SECTORS = ("odd", "even")


class WaveformRouteError(ValueError):
    """Raised when an input violates the frozen V2.2 mode-level domain."""


@dataclass(frozen=True)
class RouteBAsymptoticChain:
    """Audit intermediates for RW metric -> Kinnersley -> symmetric Psi4."""

    metric_leading_coefficients: dict[str, mp.mpc]
    kinnersley_r_psi4_reduced: mp.mpc
    kinnersley_internal_residual: mp.mpc
    symmetric_r_psi4_reduced: mp.mpc
    recovered_mp_master_coefficient: mp.mpc


@dataclass(frozen=True)
class PairComparatorValues:
    """The four frozen V2.2 comparison values for one route pair."""

    scale_normalized_complex_difference: mp.mpf
    relative_magnitude_difference: mp.mpf
    wrapped_relative_phase_rad: mp.mpf
    phase_invariant_scale_normalized_magnitude_difference: mp.mpf
    signal_floor_value: mp.mpf


def _validate_mode(*, ell: int, sector: str, omega: mp.mpf) -> None:
    if isinstance(ell, bool) or not isinstance(ell, int) or ell < 2:
        raise WaveformRouteError("ell must be an integer >= 2")
    if sector not in SECTORS:
        raise WaveformRouteError(f"unknown sector: {sector!r}")
    if not mp.isfinite(omega) or omega <= 0:
        raise WaveformRouteError("omega must be finite and positive")


def sector_bridge_factor(sector: str, omega: mp.mpf) -> mp.mpc:
    """Return ``F_even=1`` or ``F_odd=2 i/omega``."""

    _validate_mode(ell=2, sector=sector, omega=omega)
    return mp.mpc(1) if sector == "even" else 2j / omega


def scattered_li_master_coefficient(*, ell: int, c_lm: mp.mpc, S_l: mp.mpc) -> mp.mpc:
    """Return the scattered Li coefficient ``(-1)^ell c_lm (1-S_l)``."""

    if isinstance(ell, bool) or not isinstance(ell, int) or ell < 2:
        raise WaveformRouteError("ell must be an integer >= 2")
    if not all(mp.isfinite(value) for value in (mp.re(c_lm), mp.im(c_lm))):
        raise WaveformRouteError("c_lm must be finite")
    if not all(mp.isfinite(value) for value in (mp.re(S_l), mp.im(S_l))):
        raise WaveformRouteError("S_l must be finite")
    parity = mp.mpf(-1 if ell % 2 else 1)
    return parity * c_lm * (1 - S_l)


def route_a_mp_coefficient(
    *, sector: str, omega: mp.mpf, li_scattered: mp.mpc
) -> mp.mpc:
    """Map the accepted V2.1 Li scattered coefficient to ZM/CPM."""

    return sector_bridge_factor(sector, omega) * li_scattered


def rw_gauge_metric_leading_coefficients(
    *, sector: str, omega: mp.mpf, li_scattered: mp.mpc
) -> dict[str, mp.mpc]:
    """Return the independent outgoing RW-gauge large-r leading coefficients.

    The outgoing master is ``psi=q exp(+i omega r_star)[1+O(1/r)]``.  Applying
    the frozen Appendix-A RW-gauge reconstruction before taking ``r->inf``
    gives the reduced coefficients below.  They retain the metric route while
    factoring out the common radial exponential and tensor harmonic.
    """

    _validate_mode(ell=2, sector=sector, omega=omega)
    q = li_scattered
    if sector == "odd":
        return {
            "Bt_over_r": q,
            "B1_over_r": -q,
        }
    return {
        "T0_over_r_squared": 1j * omega * q,
        "Rt_over_r": omega**2 * q,
        "L0_over_r": -(omega**2) * q,
        "tt_over_r": -(omega**2) * q,
    }


def route_b_rw_metric_curvature_coefficient(
    *, ell: int, sector: str, omega: mp.mpf, li_scattered: mp.mpc
) -> RouteBAsymptoticChain:
    """Extract the MP master coefficient through direct asymptotic curvature.

    The direct large-r Kinnersley ``Z4`` limit is evaluated from independently
    reconstructed RW-gauge metric leading coefficients.  The frozen
    symmetric tetrad coefficient is exactly twice the Kinnersley coefficient.
    The final inverse is the sector-specific MP strain/master relation, not a
    copy of Route A.
    """

    _validate_mode(ell=ell, sector=sector, omega=omega)
    metric = rw_gauge_metric_leading_coefficients(
        sector=sector,
        omega=omega,
        li_scattered=li_scattered,
    )
    if sector == "odd":
        from_bt = -(omega / 2) * metric["Bt_over_r"]
        from_b1 = +(omega / 2) * metric["B1_over_r"]
        z4_kinnersley = from_bt
        residual = from_bt - from_b1
    else:
        from_tt = metric["tt_over_r"] / 4
        from_rt = -metric["Rt_over_r"] / 4
        from_l0 = metric["L0_over_r"] / 4
        z4_kinnersley = from_tt
        residual = (from_tt - from_rt) + (from_tt - from_l0)
    psi4_symmetric = 2 * z4_kinnersley
    if sector == "even":
        recovered = -2 * psi4_symmetric / omega**2
    else:
        recovered = 2 * psi4_symmetric / (1j * omega**2)
    return RouteBAsymptoticChain(
        metric_leading_coefficients=metric,
        kinnersley_r_psi4_reduced=z4_kinnersley,
        kinnersley_internal_residual=residual,
        symmetric_r_psi4_reduced=psi4_symmetric,
        recovered_mp_master_coefficient=recovered,
    )


def route_c_external_mp_coefficient(
    *, ell: int, sector: str, omega: mp.mpf, c_lm: mp.mpc, external_S_l: mp.mpc
) -> mp.mpc:
    """Map immutable external odd-RW/even-Zerilli scattering data to MP."""

    _validate_mode(ell=ell, sector=sector, omega=omega)
    li_scattered = scattered_li_master_coefficient(
        ell=ell,
        c_lm=c_lm,
        S_l=external_S_l,
    )
    return sector_bridge_factor(sector, omega) * li_scattered


def fixed_record_scale(*, sector: str, omega: mp.mpf, c_lm: mp.mpc) -> mp.mpf:
    """Return the non-fitted scale ``abs(F_sector*c_lm)``."""

    value = abs(sector_bridge_factor(sector, omega) * c_lm)
    if not mp.isfinite(value) or value <= 0:
        raise WaveformRouteError("C_record must be finite and nonzero")
    return value


def compare_route_pair(
    left: mp.mpc, right: mp.mpc, *, record_scale: mp.mpf
) -> PairComparatorValues:
    """Evaluate all four frozen comparators without a phase or scale fit."""

    if not mp.isfinite(record_scale) or record_scale <= 0:
        raise WaveformRouteError("record_scale must be finite and positive")
    for label, value in (("left", left), ("right", right)):
        if not all(mp.isfinite(x) for x in (mp.re(value), mp.im(value))):
            raise WaveformRouteError(f"{label} route amplitude is nonfinite")
    left_abs = abs(left)
    right_abs = abs(right)
    denominator = max(left_abs, right_abs)
    relmag = mp.mpf(0) if denominator == 0 else abs(left_abs - right_abs) / denominator
    product = left * mp.conj(right)
    phase = mp.mpf(0) if product == 0 else abs(mp.arg(product))
    return PairComparatorValues(
        scale_normalized_complex_difference=abs(left - right) / record_scale,
        relative_magnitude_difference=relmag,
        wrapped_relative_phase_rad=phase,
        phase_invariant_scale_normalized_magnitude_difference=(
            abs(left_abs - right_abs) / record_scale
        ),
        signal_floor_value=min(left_abs, right_abs) / record_scale,
    )


__all__ = [
    "PairComparatorValues",
    "ROUTE_PAIRS",
    "RouteBAsymptoticChain",
    "WaveformRouteError",
    "compare_route_pair",
    "fixed_record_scale",
    "route_a_mp_coefficient",
    "route_b_rw_metric_curvature_coefficient",
    "route_c_external_mp_coefficient",
    "rw_gauge_metric_leading_coefficients",
    "scattered_li_master_coefficient",
    "sector_bridge_factor",
]
