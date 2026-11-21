import tempfile
import unittest
from pathlib import Path

from data.catalogue_initial import LIVRES_INITIAUX, charger_catalogue_initial
from data.depot_sqlite import DepotSQLite
from app.modeles import Livre


class TestCatalogueInitial(unittest.TestCase):
    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()
        self.depot = DepotSQLite(Path(self.dossier.name) / "test.db")

    def tearDown(self):
        self.dossier.cleanup()

    def test_codes_uniques(self):
        codes = [livre.code for livre in LIVRES_INITIAUX]
        self.assertEqual(len(codes), len(set(codes)))

    def test_charge_une_base_vide(self):
        self.assertEqual(charger_catalogue_initial(self.depot), len(LIVRES_INITIAUX))
        self.assertEqual(len(self.depot.chercher_livres()), len(LIVRES_INITIAUX))

    def test_ne_recharge_pas_deux_fois(self):
        charger_catalogue_initial(self.depot)
        self.assertEqual(charger_catalogue_initial(self.depot), 0)

    def test_ne_touche_pas_une_base_remplie(self):
        self.depot.ajouter_livre(Livre("X1", "Mon livre", "Moi", 2026))
        self.assertEqual(charger_catalogue_initial(self.depot), 0)


if __name__ == "__main__":
    unittest.main()
