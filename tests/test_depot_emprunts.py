import tempfile
import unittest
from datetime import date
from pathlib import Path

from app.modeles import Livre, Membre
from data.depot_sqlite import DepotSQLite

AUJOURDHUI = date(2026, 11, 17)
RETOUR = date(2026, 12, 1)


class TestDepotMembresEtEmprunts(unittest.TestCase):
    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()
        self.depot = DepotSQLite(Path(self.dossier.name) / "test.db")
        self.depot.ajouter_livre(Livre("L001", "Livre 1", "Auteur", 2000))
        self.depot.ajouter_membre(Membre("IIT-01", "Awa Traoré"))

    def tearDown(self):
        self.dossier.cleanup()

    def test_membre_ajoute_et_retrouve(self):
        membre = self.depot.obtenir_membre("IIT-01")
        self.assertEqual(membre.nom, "Awa Traoré")
        self.assertIsNone(self.depot.obtenir_membre("IIT-99"))

    def test_modifier_nom_membre(self):
        self.depot.modifier_nom_membre("IIT-01", "Awa Koné")
        self.assertEqual(self.depot.obtenir_membre("IIT-01").nom, "Awa Koné")

    def test_emprunt_en_cours(self):
        self.assertIsNone(self.depot.emprunt_en_cours_du_livre("L001"))
        self.depot.ajouter_emprunt("L001", "IIT-01", AUJOURDHUI, RETOUR)
        emprunt = self.depot.emprunt_en_cours_du_livre("L001")
        self.assertEqual(emprunt.matricule, "IIT-01")
        self.assertEqual(emprunt.date_retour_prevue, RETOUR)
        self.assertEqual(emprunt.nb_prolongations, 0)

    def test_rendre_emprunt(self):
        identifiant = self.depot.ajouter_emprunt("L001", "IIT-01", AUJOURDHUI, RETOUR)
        self.depot.rendre_emprunt(identifiant, AUJOURDHUI)
        self.assertIsNone(self.depot.emprunt_en_cours_du_livre("L001"))
        self.assertEqual(len(self.depot.historique()), 1)

    def test_prolonger_emprunt(self):
        identifiant = self.depot.ajouter_emprunt("L001", "IIT-01", AUJOURDHUI, RETOUR)
        self.depot.prolonger_emprunt(identifiant, date(2026, 12, 15))
        emprunt = self.depot.emprunt_en_cours_du_livre("L001")
        self.assertEqual(emprunt.date_retour_prevue, date(2026, 12, 15))
        self.assertEqual(emprunt.nb_prolongations, 1)

    def test_emprunts_en_cours_d_un_membre(self):
        self.depot.ajouter_emprunt("L001", "IIT-01", AUJOURDHUI, RETOUR)
        self.assertEqual(len(self.depot.emprunts_en_cours("IIT-01")), 1)
        self.assertEqual(len(self.depot.emprunts_en_cours("IIT-02")), 0)


if __name__ == "__main__":
    unittest.main()
