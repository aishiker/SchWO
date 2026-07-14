import unittest

import numpy as np

from schwgw.angular.spin_weighted import spin_weighted_sph_harm
from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.perturbations import Sector
from schwgw.perturbations.reconstruction import reconstruct_metric_mode
from schwgw.scattering.partial_wave import direct_cartesian_tt_strict_np_weyl
from schwgw.scattering.weyl import (
    StrictNPScalars,
    WeylModeComponents,
    transform_strict_np_weyl_to_incident_tetrad,
    transform_weyl_to_incident_tetrad,
    weyl_mode_components,
)


class WeylModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bg = SchwarzschildBackground(M=1.0)

    def _metric_mode(self, sector: Sector, psi: complex, dpsi_dr: complex):
        return reconstruct_metric_mode(sector, 2, 0.7, 20.0, psi, dpsi_dr, self.bg)

    def test_zero_metric_mode_gives_zero_weyl_scalars(self) -> None:
        metric_mode = self._metric_mode(Sector.ODD, 0.0, 0.0)

        weyl = weyl_mode_components(Sector.ODD, 2, 1, 0.7, 20.0, 0.4, 0.3, metric_mode, self.bg)

        self.assertIsInstance(weyl, WeylModeComponents)
        for value in weyl.components.values():
            self.assertEqual(value, 0.0)

    def test_weyl_mode_components_are_complex_linear_in_positive_frequency_amplitudes(self) -> None:
        first_metric = self._metric_mode(Sector.EVEN, 0.3 - 0.2j, 0.01 + 0.04j)
        second_metric = self._metric_mode(Sector.EVEN, -0.7 + 0.1j, 0.03 - 0.02j)
        combined_metric = self._metric_mode(
            Sector.EVEN,
            (1.4 - 0.2j) * (0.3 - 0.2j) - 0.6j * (-0.7 + 0.1j),
            (1.4 - 0.2j) * (0.01 + 0.04j) - 0.6j * (0.03 - 0.02j),
        )

        first = weyl_mode_components(Sector.EVEN, 2, 1, 0.7, 20.0, 0.4, 0.3, first_metric, self.bg)
        second = weyl_mode_components(Sector.EVEN, 2, 1, 0.7, 20.0, 0.4, 0.3, second_metric, self.bg)
        combined = weyl_mode_components(
            Sector.EVEN,
            2,
            1,
            0.7,
            20.0,
            0.4,
            0.3,
            combined_metric,
            self.bg,
        )

        for label in combined.components:
            np.testing.assert_allclose(
                combined.components[label],
                (1.4 - 0.2j) * first.components[label] - 0.6j * second.components[label],
                rtol=1e-13,
                atol=1e-14,
            )

    def test_spin_weight_labels_match_psi0_and_psi4_angular_factors(self) -> None:
        metric_mode = self._metric_mode(Sector.ODD, 1.2 - 0.4j, 0.03 + 0.02j)

        weyl = weyl_mode_components(Sector.ODD, 2, 1, 0.7, 20.0, 0.4, 0.3, metric_mode, self.bg)

        self.assertEqual(weyl.spin_weights["Psi4"], -2)
        self.assertEqual(weyl.spin_weights["Psi0"], 2)
        np.testing.assert_allclose(
            weyl.angular_factors["Psi4"],
            spin_weighted_sph_harm(-2, 2, 1, 0.4, 0.3),
            rtol=0.0,
            atol=0.0,
        )
        np.testing.assert_allclose(
            weyl.angular_factors["Psi0"],
            spin_weighted_sph_harm(2, 2, 1, 0.4, 0.3),
            rtol=0.0,
            atol=0.0,
        )

    def test_weyl_mode_formula_smoke_values_match_t6a_audit(self) -> None:
        odd_metric = self._metric_mode(Sector.ODD, 1.2 - 0.4j, 0.03 + 0.02j)
        even_metric = self._metric_mode(Sector.EVEN, 1.2 - 0.4j, 0.03 + 0.02j)

        odd = weyl_mode_components(Sector.ODD, 2, 1, 0.7, 20.0, 0.4, 0.3, odd_metric, self.bg)
        even = weyl_mode_components(Sector.EVEN, 2, 1, 0.7, 20.0, 0.4, 0.3, even_metric, self.bg)

        expected_odd = {
            "Psi4": 0.01295174239258416 - 0.0013690611611635358j,
            "Psi3": -0.00013302868915688584 - 0.0029451822149334493j,
            "Psi2": 0.0003754490167619129 - 8.167512283120008e-06j,
            "Psi1": -4.099689870001805e-05 - 0.0009076488514167335j,
            "Psi0": -0.002628171307657158 + 0.00027781028630232747j,
        }
        expected_even = {
            "Psi4": 0.004536358947088966 - 0.0004585737959393074j,
            "Psi3": -4.246813144669666e-05 - 0.001081235797480753j,
            "Psi2": 0.00013769168156027093 - 3.4390518075871777e-06j,
            "Psi1": -1.3087866188367643e-05 - 0.0003332162012652371j,
            "Psi0": -0.0009205192679557523 + 9.30539271396557e-05j,
        }

        for label, expected in expected_odd.items():
            np.testing.assert_allclose(odd.components[label], expected, rtol=1e-13, atol=1e-14)
        for label, expected in expected_even.items():
            np.testing.assert_allclose(even.components[label], expected, rtol=1e-13, atol=1e-14)

    def test_strict_np_transform_preserves_axis_spin_boost_scaling(self) -> None:
        weyl = {
            "Psi0": 1.0 + 2.0j,
            "Psi1": -0.5 + 0.25j,
            "Psi2": 0.3 - 0.7j,
            "Psi3": 1.2 + 0.4j,
            "Psi4": -0.2 + 0.9j,
        }

        axis = transform_strict_np_weyl_to_incident_tetrad(weyl, theta=0.0, phi=0.0)
        expected_axis = {
            "Psi0": 0.5 + 1.0j,
            "Psi1": -0.3535533905932738 + 0.1767766952966369j,
            "Psi2": 0.3 - 0.7j,
            "Psi3": 1.697056274847714 + 0.5656854249492381j,
            "Psi4": -0.4 + 1.8j,
        }
        for label, expected in expected_axis.items():
            np.testing.assert_allclose(axis[label], expected, rtol=1e-14, atol=1e-14)

    def test_strict_np_scalars_require_full_quintuple_and_frame(self) -> None:
        strict = StrictNPScalars.from_mapping(
            {
                "Psi0": 1.0,
                "Psi1": 2.0,
                "Psi2": 3.0,
                "Psi3": 4.0,
                "Psi4": 5.0,
            },
            frame="incident",
        )

        self.assertEqual(strict.frame, "incident")
        self.assertEqual(strict.as_mapping()["Psi4"], 5.0 + 0.0j)

        with self.assertRaisesRegex(ValueError, "Missing strict NP scalar components"):
            StrictNPScalars.from_mapping(
                {
                    "Psi0": 1.0,
                    "Psi4": 5.0,
                },
                frame="incident",
            )
        with self.assertRaisesRegex(ValueError, "frame"):
            StrictNPScalars.from_mapping(
                {
                    "Psi0": 1.0,
                    "Psi1": 2.0,
                    "Psi2": 3.0,
                    "Psi3": 4.0,
                    "Psi4": 5.0,
                },
                frame="packaged",
            )

    def test_strict_np_transform_matches_direct_tensor_contraction_off_axis(self) -> None:
        for theta in (0.4, 1.0):
            with self.subTest(theta=theta):
                source = direct_cartesian_tt_strict_np_weyl(
                    k=0.5,
                    z=20.0 * np.cos(theta),
                    A_plus=0.9 + 0.2j,
                    A_cross=0.1 - 0.3j,
                    tetrad=_flat_kinnersley_cartesian_legs(theta, 0.0),
                )
                expected = direct_cartesian_tt_strict_np_weyl(
                    k=0.5,
                    z=20.0 * np.cos(theta),
                    A_plus=0.9 + 0.2j,
                    A_cross=0.1 - 0.3j,
                )

                transformed = transform_strict_np_weyl_to_incident_tetrad(
                    source,
                    theta=theta,
                    phi=0.0,
                )

                for label, expected_value in expected.items():
                    np.testing.assert_allclose(
                        transformed[label],
                        expected_value,
                        rtol=1e-12,
                        atol=1e-13,
                    )


def _flat_kinnersley_cartesian_legs(theta: float, phi: float) -> dict[str, np.ndarray]:
    radial = np.array(
        [
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        ],
        dtype=complex,
    )
    theta_leg = np.array(
        [
            np.cos(theta) * np.cos(phi),
            np.cos(theta) * np.sin(phi),
            -np.sin(theta),
        ],
        dtype=complex,
    )
    phi_leg = np.array([-np.sin(phi), np.cos(phi), 0.0], dtype=complex)
    m_leg = np.concatenate([[0.0j], (theta_leg + 1.0j * phi_leg) / np.sqrt(2.0)])
    return {
        "l": np.concatenate([[1.0 + 0.0j], radial]),
        "n": 0.5 * np.concatenate([[1.0 + 0.0j], -radial]),
        "m": m_leg,
        "mbar": np.conjugate(m_leg),
    }


if __name__ == "__main__":
    unittest.main()
