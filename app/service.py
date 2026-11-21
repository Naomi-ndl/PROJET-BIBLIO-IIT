"""La logique de l'application : elle utilise les règles et le dépôt.

La console appelle uniquement ce fichier (jamais la base directement).
"""
from datetime import date

from app import regles
from app.modeles import Membre


class ErreurGestion(Exception):
    """Une erreur normale (livre introuvable, déjà emprunté...) à afficher à l'utilisateur."""


class Bibliotheque:
    def __init__(self, depot):
        self.depot = depot

    # ---------- CATALOGUE ----------
    def ajouter_livre(self, livre):
        if not livre.code or not livre.titre or not livre.auteur:
            raise ErreurGestion("Le code, le titre et l'auteur sont obligatoires.")
        if self.depot.obtenir_livre(livre.code):
            raise ErreurGestion("Ce code de livre existe déjà.")
        self.depot.ajouter_livre(livre)

    def modifier_livre(self, code, titre="", auteur="", annee=None, categorie=""):
        """Modifie les champs donnés. Un champ vide (ou None) reste inchangé."""
        livre = self.depot.obtenir_livre(code)
        if not livre:
            raise ErreurGestion("Livre introuvable.")
        if titre:
            livre.titre = titre
        if auteur:
            livre.auteur = auteur
        if annee is not None:
            livre.annee = annee
        if categorie:
            livre.categorie = categorie
        self.depot.modifier_livre(livre)
        return livre

    def rechercher_livres(self, terme=""):
        return self.depot.chercher_livres(terme)

    def livres_avec_statut(self, terme=""):
        """Liste de (livre, emprunt). emprunt vaut None si le livre est disponible."""
        resultat = []
        for livre in self.depot.chercher_livres(terme):
            emprunt = self.depot.emprunt_en_cours_du_livre(livre.code)
            resultat.append((livre, emprunt))
        return resultat

    # ---------- MEMBRES ----------
    def inscrire_membre(self, matricule, nom):
        if not regles.matricule_valide(matricule):
            raise ErreurGestion("Matricule invalide. Format attendu : IIT-01")
        if not nom:
            raise ErreurGestion("Le nom est obligatoire.")
        if self.depot.obtenir_membre(matricule):
            raise ErreurGestion("Ce matricule est déjà inscrit.")
        self.depot.ajouter_membre(Membre(matricule, nom))

    def modifier_nom_membre(self, matricule, nom):
        if not nom:
            raise ErreurGestion("Le nom est obligatoire.")
        if not self.depot.obtenir_membre(matricule):
            raise ErreurGestion("Membre introuvable.")
        self.depot.modifier_nom_membre(matricule, nom)

    def consulter_membre(self, matricule):
        """Retourne (membre, liste de ses emprunts en cours)."""
        membre = self.depot.obtenir_membre(matricule)
        if not membre:
            raise ErreurGestion("Membre introuvable.")
        return membre, self.depot.emprunts_en_cours(matricule)

    def lister_membres(self):
        return self.depot.lister_membres()

    # ---------- EMPRUNTS ----------
    def emprunter(self, code_livre, matricule, aujourdhui=None):
        """Enregistre un emprunt. Retourne la date de retour prévue."""
        aujourdhui = aujourdhui or date.today()

        livre = self.depot.obtenir_livre(code_livre)
        if not livre:
            raise ErreurGestion("Livre introuvable.")
        membre = self.depot.obtenir_membre(matricule)
        if not membre:
            raise ErreurGestion("Membre introuvable. Inscrivez-le d'abord.")
        if self.depot.emprunt_en_cours_du_livre(code_livre):
            raise ErreurGestion(f"Le livre « {livre.titre} » est déjà emprunté.")

        nb_en_cours = len(self.depot.emprunts_en_cours(matricule))
        autorise, message = regles.peut_emprunter(nb_en_cours)
        if not autorise:
            raise ErreurGestion(message)

        date_retour = regles.calculer_date_retour(aujourdhui)
        self.depot.ajouter_emprunt(code_livre, matricule, aujourdhui, date_retour)
        return date_retour

    def _emprunt_du_membre(self, code_livre, matricule):
        """Retrouve l'emprunt en cours de ce livre ET vérifie qu'il appartient à ce membre."""
        emprunt = self.depot.emprunt_en_cours_du_livre(code_livre)
        if not emprunt:
            raise ErreurGestion("Ce livre n'est pas emprunté.")
        if emprunt.matricule != matricule:
            raise ErreurGestion("Ce livre n'a pas été emprunté par ce membre.")
        return emprunt

    def prolonger(self, code_livre, matricule, aujourdhui=None):
        """Prolonge l'emprunt en cours du livre. Retourne la nouvelle date."""
        aujourdhui = aujourdhui or date.today()
        emprunt = self._emprunt_du_membre(code_livre, matricule)
        autorise, message = regles.peut_prolonger(emprunt, aujourdhui)
        if not autorise:
            raise ErreurGestion(message)
        nouvelle_date = regles.nouvelle_date_retour(emprunt)
        self.depot.prolonger_emprunt(emprunt.id, nouvelle_date)
        return nouvelle_date

    def rendre(self, code_livre, matricule, aujourdhui=None):
        """Enregistre le retour. Retourne le nombre de jours de retard (0 si à l'heure)."""
        aujourdhui = aujourdhui or date.today()
        emprunt = self._emprunt_du_membre(code_livre, matricule)
        self.depot.rendre_emprunt(emprunt.id, aujourdhui)
        if regles.est_en_retard(emprunt, aujourdhui):
            return (aujourdhui - emprunt.date_retour_prevue).days
        return 0

    # ---------- SUIVI ----------
    def emprunts_en_cours(self):
        return self.depot.emprunts_en_cours()

    def retards(self, aujourdhui=None):
        return [e for e in self.depot.emprunts_en_cours()
                if regles.est_en_retard(e, aujourdhui)]

    def historique(self):
        return self.depot.historique()

    def statistiques(self):
        nb_livres = len(self.depot.chercher_livres())
        nb_emprunts = len(self.depot.emprunts_en_cours())
        return {
            "livres": nb_livres,
            "disponibles": nb_livres - nb_emprunts,
            "emprunts": nb_emprunts,
            "retards": len(self.retards()),
            "membres": len(self.depot.lister_membres()),
        }
