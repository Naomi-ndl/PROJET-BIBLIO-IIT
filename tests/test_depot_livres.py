import tempfile
import unittest
from pathlib import Path

from app.modeles import Livre
from data.depot_sqlite import DepotSQLite


class TestDepotLivres(unittest.TestCase):
    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()
        self.depot = DepotSQLite(Path(self.dossier.name) / "test.db")
        self.depot.ajouter_livre(Livre("L001", "Le Petit Prince", "Saint-Exupéry", 1943, "Conte"))
        self.depot.ajouter_livre(Livre("L002", "Candide", "Voltaire", 1759, "Conte"))

    def tearDown(self):
        self.dossier.cleanup()

    def test_obtenir_livre(self):
        livre = self.depot.obtenir_livre("L001")
        self.assertEqual(livre.titre, "Le Petit Prince")
        self.assertEqual(livre.annee, 1943)

    def test_obtenir_livre_inconnu(self):
        self.assertIsNone(self.depot.obtenir_livre("L999"))

    def test_chercher_par_titre_auteur_et_categorie(self):
        self.assertEqual(len(self.depot.chercher_livres("Petit")), 1)
        self.assertEqual(len(self.depot.chercher_livres("Voltaire")), 1)
        self.assertEqual(len(self.depot.chercher_livres("Conte")), 2)

    def test_chercher_sans_terme_donne_tout(self):
        self.assertEqual(len(self.depot.chercher_livres()), 2)

    def test_chercher_sans_resultat(self):
        self.assertEqual(self.depot.chercher_livres("zzz"), [])

    def test_modifier_livre(self):
        livre = self.depot.obtenir_livre("L002")
        livre.titre = "Candide ou l'Optimisme"
        self.depot.modifier_livre(livre)
        self.assertEqual(self.depot.obtenir_livre("L002").titre, "Candide ou l'Optimisme")


if __name__ == "__main__":
    unittest.main()
