import unittest

from schwgw.perturbations import Sector
from schwgw.perturbations.sectors import Sector as ModuleSector


class SectorTests(unittest.TestCase):
    def test_sector_enum_values_match_public_convention(self) -> None:
        self.assertEqual(Sector.ODD.value, "odd")
        self.assertEqual(Sector.EVEN.value, "even")

    def test_sector_enum_constructs_from_strings(self) -> None:
        self.assertIs(Sector("odd"), Sector.ODD)
        self.assertIs(Sector("even"), Sector.EVEN)

    def test_package_import_exposes_sector_enum(self) -> None:
        self.assertIs(Sector, ModuleSector)
