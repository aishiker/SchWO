import unittest

from schwgw.angular import (
    is_rw_gauge_radiative_label,
    rw_gauge_radiative_labels,
    tensor_harmonic_labels,
    tensor_harmonic_parity,
)


class TensorHarmonicRegistryTests(unittest.TestCase):
    def test_registry_contains_frozen_tensor_harmonic_labels(self) -> None:
        self.assertEqual(
            set(tensor_harmonic_labels()),
            {"tt", "Rt", "L0", "T0", "Et", "E1", "Bt", "B1", "E2", "B2"},
        )

    def test_parity_split_matches_physics_spec(self) -> None:
        even = {label for label in tensor_harmonic_labels() if tensor_harmonic_parity(label) == "even"}
        odd = {label for label in tensor_harmonic_labels() if tensor_harmonic_parity(label) == "odd"}

        self.assertEqual(even, {"tt", "Rt", "L0", "T0", "Et", "E1", "E2"})
        self.assertEqual(odd, {"Bt", "B1", "B2"})

    def test_rw_gauge_radiative_surviving_labels_are_queryable(self) -> None:
        self.assertEqual(set(rw_gauge_radiative_labels("odd")), {"Bt", "B1"})
        self.assertEqual(set(rw_gauge_radiative_labels("even")), {"tt", "Rt", "L0", "T0"})

        self.assertTrue(is_rw_gauge_radiative_label("Bt"))
        self.assertTrue(is_rw_gauge_radiative_label("T0"))
        self.assertFalse(is_rw_gauge_radiative_label("B2"))
        self.assertFalse(is_rw_gauge_radiative_label("E2"))

    def test_unknown_label_or_parity_raises(self) -> None:
        with self.assertRaises(ValueError):
            tensor_harmonic_parity("unknown")
        with self.assertRaises(ValueError):
            rw_gauge_radiative_labels("axial")
