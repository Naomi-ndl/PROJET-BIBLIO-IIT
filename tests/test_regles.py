import unittest
from datetime import date, timedelta

from app import regles
from app.modeles import Emprunt

AUJOURDHUI = date(2026, 11, 17)


def un_emprunt(**champs):
    base = dict(id=1, code_livre="L001", matricule="IIT-01",
                date_emprunt=AUJOURDHUI, date_retour_prevue=AUJOURDHUI + timedelta(days=5))
    base.update(champs)
    return Emprunt(**base)


class TestRegles(unittest.TestCase):
    def test_matricule(self):
        self.assertTrue(regles.matricule_valide("IIT-01"))
        self.assertFalse(regles.matricule_valide("IIT-1"))
        self.assertFalse(regles.matricule_valide("IIT-001"))
        self.assertFalse(regles.matricule_valide("E2026-001"))
        self.assertFalse(regles.matricule_valide("abc"))

    def test_date_retour(self):
        self.assertEqual(regles.calculer_date_retour(AUJOURDHUI),
                         AUJOURDHUI + timedelta(days=14))

    def test_limite_emprunts(self):
        self.assertTrue(regles.peut_emprunter(2)[0])
        self.assertFalse(regles.peut_emprunter(3)[0])

    def test_retard(self):
        self.assertFalse(regles.est_en_retard(un_emprunt(), AUJOURDHUI))
        en_retard = un_emprunt(date_retour_prevue=AUJOURDHUI - timedelta(days=1))
        self.assertTrue(regles.est_en_retard(en_retard, AUJOURDHUI))
        rendu = un_emprunt(date_retour_prevue=AUJOURDHUI - timedelta(days=1),
                           date_retour_reelle=AUJOURDHUI)
        self.assertFalse(regles.est_en_retard(rendu, AUJOURDHUI))

    def test_prolongation_ok(self):
        self.assertTrue(regles.peut_prolonger(un_emprunt(), AUJOURDHUI)[0])

    def test_prolongation_refusee(self):
        deja = un_emprunt(nb_prolongations=1)
        self.assertFalse(regles.peut_prolonger(deja, AUJOURDHUI)[0])
        retard = un_emprunt(date_retour_prevue=AUJOURDHUI - timedelta(days=1))
        self.assertFalse(regles.peut_prolonger(retard, AUJOURDHUI)[0])
        rendu = un_emprunt(date_retour_reelle=AUJOURDHUI)
        self.assertFalse(regles.peut_prolonger(rendu, AUJOURDHUI)[0])

    def test_nouvelle_date(self):
        emprunt = un_emprunt()
        self.assertEqual(regles.nouvelle_date_retour(emprunt),
                         emprunt.date_retour_prevue + timedelta(days=14))


if __name__ == "__main__":
    unittest.main()
