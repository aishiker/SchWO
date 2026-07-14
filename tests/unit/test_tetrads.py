import unittest

import numpy as np

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.scattering.tetrads import (
    NullTetrad,
    incident_cartesian_tetrad,
    kinnersley_tetrad,
    tetrad_inner_product,
    tetrad_inner_products,
)


class TetradTests(unittest.TestCase):
    def test_kinnersley_tetrad_has_frozen_null_inner_products(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        tetrad = kinnersley_tetrad(bg, r=20.0, theta=0.7)

        self.assertIsInstance(tetrad, NullTetrad)
        self.assertEqual(tetrad.coordinates, "schwarzschild")

        self.assertAlmostEqual(tetrad_inner_product(tetrad, "l", "l"), 0.0)
        self.assertAlmostEqual(tetrad_inner_product(tetrad, "n", "n"), 0.0)
        self.assertAlmostEqual(tetrad_inner_product(tetrad, "m", "m"), 0.0)
        self.assertAlmostEqual(tetrad_inner_product(tetrad, "l", "n"), -1.0)
        self.assertAlmostEqual(tetrad_inner_product(tetrad, "m", "mbar"), 1.0)

        products = tetrad_inner_products(tetrad)
        self.assertAlmostEqual(products[("l", "n")], -1.0)
        self.assertAlmostEqual(products[("m", "mbar")], 1.0)

    def test_incident_cartesian_tetrad_has_frozen_null_inner_products(self) -> None:
        tetrad = incident_cartesian_tetrad()

        self.assertEqual(tetrad.coordinates, "cartesian")
        self.assertAlmostEqual(tetrad_inner_product(tetrad, "l", "l"), 0.0)
        self.assertAlmostEqual(tetrad_inner_product(tetrad, "n", "n"), 0.0)
        self.assertAlmostEqual(tetrad_inner_product(tetrad, "m", "m"), 0.0)
        self.assertAlmostEqual(tetrad_inner_product(tetrad, "l", "n"), -1.0)
        self.assertAlmostEqual(tetrad_inner_product(tetrad, "m", "mbar"), 1.0)

    def test_kinnersley_tetrad_rejects_horizon_or_polar_axis_inputs(self) -> None:
        bg = SchwarzschildBackground(M=1.0)

        with self.assertRaises(ValueError):
            kinnersley_tetrad(bg, r=2.0, theta=0.7)
        with self.assertRaises(ValueError):
            kinnersley_tetrad(bg, r=20.0, theta=0.0)
        with self.assertRaises(ValueError):
            kinnersley_tetrad(bg, r=20.0, theta=np.pi)


if __name__ == "__main__":
    unittest.main()
