import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from data.depot_sqlite import DepotSQLite
from app.modeles import Livre
from app.service import Bibliotheque, ErreurGestion

AUJOURDHUI = date(2026, 11, 17)


class TestBibliotheque(unittest.TestCase):
    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()
        depot = DepotSQLite(Path(self.dossier.name) / "test.db")
        self.biblio = Bibliotheque(depot)
        for i in range(1, 4):
            self.biblio.ajouter_livre(Livre(f"L00{i}", f"Livre {i}", "Auteur", 2000))
        self.biblio.inscrire_membre("IIT-01", "Awa Traoré")

    def tearDown(self):
        self.dossier.cleanup()

    def test_emprunter(self):
        retour = self.biblio.emprunter("L001", "IIT-01", AUJOURDHUI)
        self.assertEqual(retour, AUJOURDHUI + timedelta(days=14))

    def test_livre_deja_emprunte(self):
        self.biblio.emprunter("L001", "IIT-01", AUJOURDHUI)
        self.biblio.inscrire_membre("IIT-02", "Yao")
        with self.assertRaises(ErreurGestion):
            self.biblio.emprunter("L001", "IIT-02", AUJOURDHUI)

    def test_livre_ou_membre_inconnu(self):
        with self.assertRaises(ErreurGestion):
            self.biblio.emprunter("L999", "IIT-01", AUJOURDHUI)
        with self.assertRaises(ErreurGestion):
            self.biblio.emprunter("L001", "IIT-99", AUJOURDHUI)

    def test_limite_emprunts(self):
        self.biblio.ajouter_livre(Livre("L004", "Livre 4", "Auteur", 2000))
        self.biblio.emprunter("L001", "IIT-01", AUJOURDHUI)
        self.biblio.emprunter("L002", "IIT-01", AUJOURDHUI)
        self.biblio.emprunter("L003", "IIT-01", AUJOURDHUI)
        with self.assertRaises(ErreurGestion):       # 4e livre refusé (limite 3)
            self.biblio.emprunter("L004", "IIT-01", AUJOURDHUI)

    def test_rendre(self):
        self.biblio.emprunter("L001", "IIT-01", AUJOURDHUI)
        retard = self.biblio.rendre("L001", "IIT-01", AUJOURDHUI + timedelta(days=10))
        self.assertEqual(retard, 0)
        self.biblio.emprunter("L001", "IIT-01", AUJOURDHUI)   # de nouveau disponible

    def test_rendre_en_retard(self):
        self.biblio.emprunter("L001", "IIT-01", AUJOURDHUI)
        retard = self.biblio.rendre("L001", "IIT-01", AUJOURDHUI + timedelta(days=20))
        self.assertEqual(retard, 6)

    def test_rendre_livre_non_emprunte(self):
        with self.assertRaises(ErreurGestion):
            self.biblio.rendre("L001", "IIT-01", AUJOURDHUI)

    def test_rendre_par_un_autre_membre_refuse(self):
        self.biblio.inscrire_membre("IIT-02", "Yao")
        self.biblio.emprunter("L001", "IIT-01", AUJOURDHUI)
        with self.assertRaises(ErreurGestion):
            self.biblio.rendre("L001", "IIT-02", AUJOURDHUI)
        self.biblio.rendre("L001", "IIT-01", AUJOURDHUI)    # le bon membre peut rendre

    def test_prolonger_par_un_autre_membre_refuse(self):
        self.biblio.inscrire_membre("IIT-02", "Yao")
        self.biblio.emprunter("L001", "IIT-01", AUJOURDHUI)
        with self.assertRaises(ErreurGestion):
            self.biblio.prolonger("L001", "IIT-02", AUJOURDHUI)

    def test_prolonger(self):
        self.biblio.emprunter("L001", "IIT-01", AUJOURDHUI)
        nouvelle = self.biblio.prolonger("L001", "IIT-01", AUJOURDHUI)
        self.assertEqual(nouvelle, AUJOURDHUI + timedelta(days=28))   # 14 + 14
        with self.assertRaises(ErreurGestion):                        # une seule fois
            self.biblio.prolonger("L001", "IIT-01", AUJOURDHUI)

    def test_prolonger_livre_non_emprunte(self):
        with self.assertRaises(ErreurGestion):
            self.biblio.prolonger("L001", "IIT-01", AUJOURDHUI)

    def test_retards(self):
        self.biblio.emprunter("L001", "IIT-01", AUJOURDHUI)
        self.assertEqual(len(self.biblio.retards(AUJOURDHUI)), 0)
        self.assertEqual(len(self.biblio.retards(AUJOURDHUI + timedelta(days=15))), 1)

    def test_matricule_invalide(self):
        with self.assertRaises(ErreurGestion):
            self.biblio.inscrire_membre("abc", "Test")

    def test_modifier_livre(self):
        self.biblio.modifier_livre("L001", titre="Nouveau titre", annee=1999)
        livre = self.biblio.depot.obtenir_livre("L001")
        self.assertEqual(livre.titre, "Nouveau titre")
        self.assertEqual(livre.annee, 1999)
        self.assertEqual(livre.auteur, "Auteur")          # inchangé

    def test_modifier_livre_inconnu(self):
        with self.assertRaises(ErreurGestion):
            self.biblio.modifier_livre("L999", titre="X")

    def test_modifier_nom_membre(self):
        self.biblio.modifier_nom_membre("IIT-01", "Awa Koné")
        self.assertEqual(self.biblio.depot.obtenir_membre("IIT-01").nom, "Awa Koné")
        with self.assertRaises(ErreurGestion):
            self.biblio.modifier_nom_membre("IIT-99", "Inconnu")
        with self.assertRaises(ErreurGestion):
            self.biblio.modifier_nom_membre("IIT-01", "")

    def test_recherche(self):
        self.assertEqual(len(self.biblio.rechercher_livres("Livre 2")), 1)
        self.assertEqual(len(self.biblio.rechercher_livres("Auteur")), 3)


if __name__ == "__main__":
    unittest.main()
