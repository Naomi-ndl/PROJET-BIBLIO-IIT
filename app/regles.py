"""Les règles de la bibliothèque (aucun accès à la base, aucun input).

Chaque fonction répond simplement à une question : "a-t-on le droit ?",
"quelle est la date ?", "est-ce en retard ?"
"""
import re
from datetime import date, timedelta

# --- Les règles, faciles à modifier ---
DUREE_EMPRUNT = 14        # jours
LIMITE_EMPRUNTS = 3       # livres en même temps pour un membre
DUREE_PROLONGATION = 14   # jours ajoutés
MAX_PROLONGATIONS = 1


def matricule_valide(matricule):
    """Format attendu : IIT-01"""
    return re.fullmatch(r"IIT-\d{2}", matricule) is not None


def calculer_date_retour(aujourdhui=None):
    aujourdhui = aujourdhui or date.today()
    return aujourdhui + timedelta(days=DUREE_EMPRUNT)


def peut_emprunter(nb_emprunts_en_cours):
    """Retourne (True/False, message)."""
    if nb_emprunts_en_cours >= LIMITE_EMPRUNTS:
        return False, f"Limite atteinte : {LIMITE_EMPRUNTS} livres maximum par membre."
    return True, "OK"


def est_en_retard(emprunt, aujourdhui=None):
    aujourdhui = aujourdhui or date.today()
    return emprunt.date_retour_reelle is None and emprunt.date_retour_prevue < aujourdhui


def peut_prolonger(emprunt, aujourdhui=None):
    """Retourne (True/False, message)."""
    if emprunt.date_retour_reelle is not None:
        return False, "Ce livre a déjà été rendu."
    if emprunt.nb_prolongations >= MAX_PROLONGATIONS:
        return False, "Cet emprunt a déjà été prolongé une fois."
    if est_en_retard(emprunt, aujourdhui):
        return False, "Un emprunt en retard ne peut pas être prolongé."
    return True, "OK"


def nouvelle_date_retour(emprunt):
    return emprunt.date_retour_prevue + timedelta(days=DUREE_PROLONGATION)
