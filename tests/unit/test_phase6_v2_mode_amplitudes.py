from __future__ import annotations

import mpmath as mp

from schwgw.scattering.gauge_invariant_asymptotics import (
    IncidentColumn,
    build_mode_amplitudes,
    incident_master_coefficient,
    reconstruct_raw_amplitudes,
)


def test_frozen_incident_coefficients_and_complex_identity() -> None:
    with mp.workdps(80):
        plus = IncidentColumn(name="plus", A_plus=mp.mpc(1), A_cross=mp.mpc(0))
        cross = IncidentColumn(name="cross", A_plus=mp.mpc(0), A_cross=mp.mpc(1))
        odd_minus = incident_master_coefficient(3, -2, "odd", mp.mpf("0.5"), plus)
        odd_plus = incident_master_coefficient(3, 2, "odd", mp.mpf("0.5"), plus)
        cross_minus = incident_master_coefficient(3, -2, "odd", mp.mpf("0.5"), cross)
        assert mp.almosteq(odd_minus, -odd_plus)
        assert mp.almosteq(cross_minus, 1j * odd_minus)

        raw = reconstruct_raw_amplitudes(
            ell=3,
            A_out_raw=mp.mpc("0.25", "-0.5"),
            S_l=mp.mpc("0.25", "-0.5"),
            log_abs_T_horizon=mp.mpf("-1723.5"),
            phase_T_horizon=mp.mpf("0.125"),
        )
        result = build_mode_amplitudes(
            ell=3,
            m=-2,
            sector="odd",
            omega=mp.mpf("0.5"),
            column=plus,
            raw=raw,
        )
        assert mp.almosteq(
            result.A_out_total_physical,
            result.A_out_free_physical + result.A_out_scattered_physical,
        )
        assert abs(result.identity_residual) < mp.mpf("1e-70")
        assert result.T_horizon_physical != 0
        assert result.mp_master_name == "Psi_CPM"
        assert result.li_master_name == "psi_Li_odd=Psi_RW"
        assert mp.almosteq(result.mp_factor, 2j / mp.mpf("0.5"))


def test_even_is_zm_and_odd_keeps_rw_distinct_from_cpm() -> None:
    with mp.workdps(80):
        column = IncidentColumn(name="plus", A_plus=mp.mpc(1), A_cross=mp.mpc(0))
        raw = reconstruct_raw_amplitudes(
            ell=2,
            A_out_raw=mp.mpc("0.1", "0.2"),
            S_l=mp.mpc("-0.1", "-0.2"),
            log_abs_T_horizon=mp.mpf("-1"),
            phase_T_horizon=mp.mpf("0.3"),
        )
        even = build_mode_amplitudes(
            ell=2,
            m=2,
            sector="even",
            omega=mp.mpf("1"),
            column=column,
            raw=raw,
        )
        assert even.li_master_name == "psi_Li_even"
        assert even.mp_master_name == "Psi_ZM"
        assert even.mp_factor == 1
