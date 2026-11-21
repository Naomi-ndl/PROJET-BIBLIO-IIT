"""Tout ce qui parle à la base de données SQLite.

Ce fichier ne contient que des requêtes SQL : aucune règle, aucun print.
"""
import sqlite3
from contextlib import closing
from datetime import date

from app.modeles import Livre, Membre, Emprunt


def _vers_date(texte):
    """'2026-11-17' -> date(2026, 11, 17) ; None reste None."""
    return date.fromisoformat(texte) if texte else None


class DepotSQLite:
    def __init__(self, chemin="bibliotheque.db"):
        self.chemin = str(chemin)
        self._creer_tables()

    # ---------- outils internes ----------
    def _connexion(self):
        connexion = sqlite3.connect(self.chemin)
        connexion.row_factory = sqlite3.Row   # accès aux colonnes par leur nom
        return connexion

    def _lire(self, sql, params=()):
        """Exécute un SELECT et retourne toutes les lignes."""
        with closing(self._connexion()) as connexion:
            return connexion.execute(sql, params).fetchall()

    def _ecrire(self, sql, params=()):
        """Exécute un INSERT/UPDATE. Retourne (id_ajoute, nb_lignes_modifiees)."""
        with closing(self._connexion()) as connexion:
            with connexion:   # valide (commit) automatiquement
                curseur = connexion.execute(sql, params)
                return curseur.lastrowid, curseur.rowcount

    def _creer_tables(self):
        with closing(self._connexion()) as connexion:
            with connexion:
                connexion.executescript("""
                    CREATE TABLE IF NOT EXISTS livres (
                        code TEXT PRIMARY KEY,
                        titre TEXT NOT NULL,
                        auteur TEXT NOT NULL,
                        annee INTEGER NOT NULL,
                        categorie TEXT NOT NULL DEFAULT ''
                    );
                    CREATE TABLE IF NOT EXISTS membres (
                        matricule TEXT PRIMARY KEY,
                        nom TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS emprunts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code_livre TEXT NOT NULL,
                        matricule TEXT NOT NULL,
                        date_emprunt TEXT NOT NULL,
                        date_retour_prevue TEXT NOT NULL,
                        date_retour_reelle TEXT,
                        nb_prolongations INTEGER NOT NULL DEFAULT 0
                    );
                """)

    # ---------- conversion ligne SQL -> objet ----------
    def _en_livre(self, ligne):
        return Livre(ligne["code"], ligne["titre"], ligne["auteur"],
                     ligne["annee"], ligne["categorie"])

    def _en_membre(self, ligne):
        return Membre(ligne["matricule"], ligne["nom"])

    def _en_emprunt(self, ligne):
        return Emprunt(ligne["id"], ligne["code_livre"], ligne["matricule"],
                       _vers_date(ligne["date_emprunt"]),
                       _vers_date(ligne["date_retour_prevue"]),
                       _vers_date(ligne["date_retour_reelle"]),
                       ligne["nb_prolongations"])

    # ---------- LIVRES ----------
    def ajouter_livre(self, livre):
        self._ecrire(
            "INSERT INTO livres VALUES (?, ?, ?, ?, ?)",
            (livre.code, livre.titre, livre.auteur, livre.annee, livre.categorie))

    def obtenir_livre(self, code):
        lignes = self._lire("SELECT * FROM livres WHERE code = ?", (code,))
        return self._en_livre(lignes[0]) if lignes else None

    def chercher_livres(self, terme=""):
        """Cherche dans le code, le titre, l'auteur et la catégorie."""
        motif = f"%{terme.strip()}%"
        lignes = self._lire(
            """SELECT * FROM livres
               WHERE code LIKE ? OR titre LIKE ? OR auteur LIKE ? OR categorie LIKE ?
               ORDER BY code""",
            (motif, motif, motif, motif))
        return [self._en_livre(ligne) for ligne in lignes]

    def modifier_livre(self, livre):
        """Met à jour le titre, l'auteur, l'année et la catégorie (le code ne change pas)."""
        self._ecrire(
            "UPDATE livres SET titre = ?, auteur = ?, annee = ?, categorie = ? WHERE code = ?",
            (livre.titre, livre.auteur, livre.annee, livre.categorie, livre.code))

    # ---------- MEMBRES ----------
    def ajouter_membre(self, membre):
        self._ecrire("INSERT INTO membres VALUES (?, ?)",
                     (membre.matricule, membre.nom))

    def obtenir_membre(self, matricule):
        lignes = self._lire("SELECT * FROM membres WHERE matricule = ?", (matricule,))
        return self._en_membre(lignes[0]) if lignes else None

    def lister_membres(self):
        lignes = self._lire("SELECT * FROM membres ORDER BY nom")
        return [self._en_membre(ligne) for ligne in lignes]

    def modifier_nom_membre(self, matricule, nom):
        self._ecrire("UPDATE membres SET nom = ? WHERE matricule = ?", (nom, matricule))

    # ---------- EMPRUNTS ----------
    def ajouter_emprunt(self, code_livre, matricule, date_emprunt, date_retour_prevue):
        identifiant, _ = self._ecrire(
            """INSERT INTO emprunts (code_livre, matricule, date_emprunt, date_retour_prevue)
               VALUES (?, ?, ?, ?)""",
            (code_livre, matricule, date_emprunt.isoformat(), date_retour_prevue.isoformat()))
        return identifiant

    def emprunt_en_cours_du_livre(self, code_livre):
        """L'emprunt non rendu de ce livre, ou None s'il est disponible."""
        lignes = self._lire(
            "SELECT * FROM emprunts WHERE code_livre = ? AND date_retour_reelle IS NULL",
            (code_livre,))
        return self._en_emprunt(lignes[0]) if lignes else None

    def emprunts_en_cours(self, matricule=None):
        """Tous les emprunts non rendus (ou seulement ceux d'un membre)."""
        if matricule is None:
            lignes = self._lire(
                "SELECT * FROM emprunts WHERE date_retour_reelle IS NULL "
                "ORDER BY date_retour_prevue")
        else:
            lignes = self._lire(
                "SELECT * FROM emprunts WHERE date_retour_reelle IS NULL AND matricule = ? "
                "ORDER BY date_retour_prevue", (matricule,))
        return [self._en_emprunt(ligne) for ligne in lignes]

    def historique(self):
        lignes = self._lire(
            "SELECT * FROM emprunts WHERE date_retour_reelle IS NOT NULL ORDER BY id DESC")
        return [self._en_emprunt(ligne) for ligne in lignes]

    def prolonger_emprunt(self, identifiant, nouvelle_date):
        self._ecrire(
            """UPDATE emprunts
               SET date_retour_prevue = ?, nb_prolongations = nb_prolongations + 1
               WHERE id = ?""",
            (nouvelle_date.isoformat(), identifiant))

    def rendre_emprunt(self, identifiant, date_retour):
        self._ecrire("UPDATE emprunts SET date_retour_reelle = ? WHERE id = ?",
                     (date_retour.isoformat(), identifiant))
