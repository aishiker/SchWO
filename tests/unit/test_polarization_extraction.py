from __future__ import annotations

import unittest
from unittest.mock import patch
from types import SimpleNamespace

import numpy as np

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig
from schwgw.perturbations import Sector
import schwgw.scattering.partial_wave as partial_wave_module
from schwgw.scattering.observables import (
    PackagedPolarizationScalars,
    polarization_from_packaged_scalars,
    polarization_from_weyl,
)
from schwgw.scattering.partial_wave import (
    compute_apparent_polarizations,
    compute_polarization,
)
from schwgw.scattering.weyl import StrictNPScalars, compute_packaged_polarization_scalars


class FakeRadialSolution:
    def __init__(self, sector: Sector, ell: int, k: float, background: SchwarzschildBackground) -> None:
        self.sector = sector
        self.ell = ell
        self.k = k
        self.background = background
        self.A_in = 1.0 + 0.0j
        self.diagnostics = SimpleNamespace(
            boundary_residual=1e-13 * ell,
            wronskian_residual=2e-13 * ell,
            match_condition_number=10.0 + ell,
        )

    def psi_at(self, r: float) -> complex:
        sector_weight = 1.0j if self.sector is Sector.ODD else 1.0
        return sector_weight * (0.01 * self.ell + 0.001 * r)

    def dpsi_dr_at(self, r: float) -> complex:
        sector_weight = -0.5j if self.sector is Sector.ODD else 0.5
        return sector_weight * (0.001 * self.ell + 0.0001 * r)


def recording_radial_solver(call_log: list[tuple[Sector, int]]):
    def solve(
        sector: Sector,
        ell: int,
        k: float,
        background: SchwarzschildBackground,
        boundary_config: BoundaryConfig | None = None,
    ) -> FakeRadialSolution:
        del boundary_config
        sector = Sector(sector)
        call_log.append((sector, ell))
        return FakeRadialSolution(sector, ell, k, background)

    return solve


class PolarizationExtractionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bg = SchwarzschildBackground(M=1.0)

    def test_polarization_from_weyl_uses_documented_signs_and_factors(self) -> None:
        k = 2.0
        psi0 = 1.0 + 2.0j
        psi4 = -0.5 + 0.25j

        h_plus, h_cross = polarization_from_weyl(k, psi0, 0.0)
        self.assertEqual(h_plus, -psi0 / k**2)
        self.assertEqual(h_cross, 1.0j * psi0 / k**2)

        h_plus, h_cross = polarization_from_weyl(k, 0.0, psi4)
        self.assertEqual(h_plus, -psi4 / k**2)
        self.assertEqual(h_cross, -1.0j * psi4 / k**2)

        h_plus, h_cross = polarization_from_weyl(k, psi0, psi0)
        self.assertEqual(h_plus, -2.0 * psi0 / k**2)
        self.assertEqual(h_cross, 0.0)

        h_plus, h_cross = polarization_from_weyl(k, psi0, -psi0)
        self.assertEqual(h_plus, 0.0)
        self.assertEqual(h_cross, 2.0j * psi0 / k**2)

    def test_packaged_and_strict_np_scalars_are_not_interchangeable(self) -> None:
        strict_np = StrictNPScalars(
            psi0=1.0 + 0.0j,
            psi1=0.0j,
            psi2=0.0j,
            psi3=0.0j,
            psi4=2.0 + 0.0j,
            frame="incident",
        )
        packaged = PackagedPolarizationScalars(
            psi0_pack=1.0 + 0.0j,
            psi4_pack=2.0 + 0.0j,
        )

        self.assertIsNot(type(strict_np), type(packaged))
        with self.assertRaisesRegex(TypeError, "PackagedPolarizationScalars"):
            polarization_from_packaged_scalars(0.5, strict_np)  # type: ignore[arg-type]

    def test_packaged_scalars_are_tidal_projection_not_strict_np_two_scalar_alias(self) -> None:
        strict_np = StrictNPScalars.from_mapping({
            "Psi0": 0.0j,
            "Psi1": 0.0j,
            "Psi2": 0.0j,
            "Psi3": 0.0j,
            "Psi4": 2.0 - 0.5j,
        }, frame="incident")

        packaged = compute_packaged_polarization_scalars(strict_np)

        self.assertIsInstance(packaged, PackagedPolarizationScalars)
        np.testing.assert_allclose(packaged.psi0_pack, 0.0j, atol=1e-14)
        np.testing.assert_allclose(packaged.psi4_pack, 0.5 * strict_np.psi4, rtol=1e-14)

    def test_compute_polarization_packages_strict_np_before_extraction(self) -> None:
        calls: list[tuple[Sector, int]] = []
        strict_np = {
            "Psi0": 11.0 + 0.0j,
            "Psi1": -2.0j,
            "Psi2": 13.0 + 0.5j,
            "Psi3": 3.0 - 4.0j,
            "Psi4": 17.0 + 0.0j,
        }
        expected_packaged = compute_packaged_polarization_scalars(
            StrictNPScalars.from_mapping(strict_np, frame="incident")
        )

        def fake_extraction(
            k: float,
            packaged: PackagedPolarizationScalars,
        ) -> tuple[complex, complex]:
            self.assertEqual(k, 0.5)
            self.assertIsInstance(packaged, PackagedPolarizationScalars)
            np.testing.assert_allclose(packaged.psi0_pack, expected_packaged.psi0_pack)
            np.testing.assert_allclose(packaged.psi4_pack, expected_packaged.psi4_pack)
            self.assertNotEqual(packaged.psi0_pack, strict_np["Psi0"])
            self.assertNotEqual(packaged.psi4_pack, strict_np["Psi4"])
            return 123.0 + 0.0j, 456.0 + 0.0j

        def legacy_extraction(*args: object, **kwargs: object) -> tuple[complex, complex]:
            raise AssertionError("production must call polarization_from_packaged_scalars")

        with (
            patch.object(
                partial_wave_module,
                "transform_strict_np_weyl_to_incident_tetrad",
                return_value=strict_np,
            ),
            patch.object(
                partial_wave_module,
                "polarization_from_packaged_scalars",
                side_effect=fake_extraction,
            ),
            patch.object(partial_wave_module, "polarization_from_weyl", side_effect=legacy_extraction),
        ):
            result = compute_polarization(
                background=self.bg,
                k=0.5,
                r=20.0,
                theta=0.4,
                phi=0.3,
                A_plus=0.7 - 0.1j,
                A_cross=0.2 + 0.3j,
                lmax=2,
                radial_solver=recording_radial_solver(calls),
            )

        self.assertEqual(result.h_plus, 123.0 + 0.0j)
        self.assertEqual(result.h_cross, 456.0 + 0.0j)
        np.testing.assert_allclose(result.psi0_hat, expected_packaged.psi0_pack)
        np.testing.assert_allclose(result.psi4_hat, expected_packaged.psi4_pack)

    def test_compute_apparent_polarizations_reuses_strict_np_assembly(self) -> None:
        calls: list[tuple[Sector, int]] = []
        strict_np = {
            "Psi0": 11.0 + 0.0j,
            "Psi1": -2.0 + 3.0j,
            "Psi2": 4.0 - 5.0j,
            "Psi3": 6.0 + 7.0j,
            "Psi4": 17.0 + 0.0j,
        }

        with patch.object(
            partial_wave_module,
            "transform_strict_np_weyl_to_incident_tetrad",
            return_value=strict_np,
        ):
            result = compute_apparent_polarizations(
                background=self.bg,
                k=0.5,
                r=20.0,
                theta=0.4,
                phi=0.3,
                A_plus=0.7 - 0.1j,
                A_cross=0.2 + 0.3j,
                lmax=2,
                radial_solver=recording_radial_solver(calls),
            )

        assert result.physical_claim is False
        assert result.frame == "incident"
        assert result.h_x == -(strict_np["Psi1"] + strict_np["Psi3"]) / (2.0 * 0.5**2)
        assert result.h_y == 1.0j * (strict_np["Psi1"] - strict_np["Psi3"]) / (2.0 * 0.5**2)
        assert result.h_b == -strict_np["Psi2"] / (2.0 * 0.5**2)
        assert result.h_longitudinal == -strict_np["Psi2"] / 0.5**2
        assert result.diagnostics["radial_solve_count"] == 2.0
        assert calls == [(Sector.ODD, 2), (Sector.EVEN, 2)]

    def test_invalid_inputs_raise_clear_errors(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            polarization_from_weyl(0.0, 1.0, 0.0)

        with self.assertRaisesRegex(ValueError, "ell >= 2"):
            compute_polarization(
                background=self.bg,
                k=0.5,
                r=20.0,
                theta=0.4,
                phi=0.3,
                A_plus=1.0,
                A_cross=0.0,
                lmax=1,
            )

        with self.assertRaisesRegex(ValueError, "r > 2M"):
            compute_polarization(
                background=self.bg,
                k=0.5,
                r=2.0,
                theta=0.4,
                phi=0.3,
                A_plus=1.0,
                A_cross=0.0,
                lmax=2,
            )

    def test_zero_incident_amplitudes_give_zero_observables_without_radial_solves(self) -> None:
        calls: list[tuple[Sector, int]] = []

        result = compute_polarization(
            background=self.bg,
            k=0.5,
            r=20.0,
            theta=0.4,
            phi=0.3,
            A_plus=0.0,
            A_cross=0.0,
            lmax=4,
            radial_solver=recording_radial_solver(calls),
        )

        self.assertEqual(result.h_plus, 0.0)
        self.assertEqual(result.h_cross, 0.0)
        self.assertEqual(result.psi0_hat, 0.0)
        self.assertEqual(result.psi4_hat, 0.0)
        self.assertEqual(result.diagnostics["radial_solve_count"], 0.0)
        self.assertEqual(calls, [])

    def test_partial_wave_output_is_linear_in_incident_polarizations(self) -> None:
        first_calls: list[tuple[Sector, int]] = []
        second_calls: list[tuple[Sector, int]] = []
        combined_calls: list[tuple[Sector, int]] = []
        kwargs = dict(background=self.bg, k=0.5, r=20.0, theta=0.4, phi=0.3, lmax=3)
        alpha = 1.3 - 0.2j
        beta = -0.4j

        first = compute_polarization(
            **kwargs,
            A_plus=0.7 - 0.1j,
            A_cross=0.2 + 0.3j,
            radial_solver=recording_radial_solver(first_calls),
        )
        second = compute_polarization(
            **kwargs,
            A_plus=-0.2 + 0.5j,
            A_cross=0.4 - 0.6j,
            radial_solver=recording_radial_solver(second_calls),
        )
        combined = compute_polarization(
            **kwargs,
            A_plus=alpha * (0.7 - 0.1j) + beta * (-0.2 + 0.5j),
            A_cross=alpha * (0.2 + 0.3j) + beta * (0.4 - 0.6j),
            radial_solver=recording_radial_solver(combined_calls),
        )

        np.testing.assert_allclose(combined.h_plus, alpha * first.h_plus + beta * second.h_plus)
        np.testing.assert_allclose(combined.h_cross, alpha * first.h_cross + beta * second.h_cross)
        np.testing.assert_allclose(combined.psi0_hat, alpha * first.psi0_hat + beta * second.psi0_hat)
        np.testing.assert_allclose(combined.psi4_hat, alpha * first.psi4_hat + beta * second.psi4_hat)

    def test_radial_solution_cache_is_per_sector_and_ell_not_per_m(self) -> None:
        calls: list[tuple[Sector, int]] = []

        result = compute_polarization(
            background=self.bg,
            k=0.5,
            r=20.0,
            theta=0.4,
            phi=0.3,
            A_plus=0.7 - 0.1j,
            A_cross=0.2 + 0.3j,
            lmax=3,
            radial_solver=recording_radial_solver(calls),
        )

        self.assertEqual(result.diagnostics["radial_solve_count"], 4.0)
        self.assertCountEqual(
            calls,
            [
                (Sector.ODD, 2),
                (Sector.EVEN, 2),
                (Sector.ODD, 3),
                (Sector.EVEN, 3),
            ],
        )


if __name__ == "__main__":
    unittest.main()
