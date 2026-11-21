"""L'interface console : menus et saisies. Aucune règle ici, on appelle le service."""
from pathlib import Path

from data.catalogue_initial import charger_catalogue_initial
from data.depot_sqlite import DepotSQLite
from app.modeles import Livre
from app.service import Bibliotheque, ErreurGestion

MENU_PRINCIPAL = """
========== BiblioIIT ==========
1. Catalogue
2. Membres
3. Emprunts
4. Suivi
5. Statistiques
0. Quitter
"""

MENU_CATALOGUE = """
===== CATALOGUE =====
1. Rechercher un livre
2. Lister les livres
3. Ajouter un livre
4. Modifier un livre
0. Retour
"""

MENU_MEMBRES = """
===== MEMBRES =====
1. Inscrire un membre
2. Consulter un membre
3. Lister les membres
4. Modifier le nom d'un membre
0. Retour
"""

MENU_EMPRUNTS = """
===== EMPRUNTS =====
1. Emprunter un livre
2. Prolonger un emprunt
3. Rendre un livre
0. Retour
"""

MENU_SUIVI = """
===== SUIVI =====
1. Emprunts en cours
2. Retards
3. Historique
0. Retour
"""


# ---------- petits outils ----------
def jour(une_date):
    """date(2026, 11, 17) -> '17/11/2026'"""
    return une_date.strftime("%d/%m/%Y")


def demander(message):
    """Redemande tant que la réponse est vide."""
    while True:
        texte = input(message).strip()
        if texte:
            return texte
        print("Ce champ est obligatoire.")


def demander_annee():
    while True:
        texte = input("Année (0 si inconnue) : ").strip()
        if texte.isdigit():
            return int(texte)
        print("Veuillez saisir un nombre.")


def afficher_livres(liste):
    """liste = [(livre, emprunt), ...]"""
    if not liste:
        print("Aucun livre trouvé.")
        return
    for livre, emprunt in liste:
        annee = livre.annee if livre.annee else "?"
        if emprunt:
            statut = f"Emprunté, retour le {jour(emprunt.date_retour_prevue)}"
        else:
            statut = "Disponible"
        print(f"{livre.code} | {livre.titre} - {livre.auteur} ({annee}) [{statut}]")


def afficher_emprunts(service, emprunts):
    if not emprunts:
        print("Aucun emprunt.")
        return
    for e in emprunts:
        livre = service.depot.obtenir_livre(e.code_livre)
        membre = service.depot.obtenir_membre(e.matricule)
        ligne = f"{e.code_livre} {livre.titre} | {membre.nom} ({e.matricule}) | "
        ligne += f"emprunté le {jour(e.date_emprunt)}, retour prévu le {jour(e.date_retour_prevue)}"
        if e.date_retour_reelle:
            ligne += f", rendu le {jour(e.date_retour_reelle)}"
        print(ligne)


# ---------- sous-menus ----------
def menu_catalogue(service):
    while True:
        print(MENU_CATALOGUE)
        choix = input("Votre choix : ").strip()
        try:
            if choix == "0":
                return
            elif choix == "1":
                terme = input("Mot-clé (titre, auteur, code) : ")
                afficher_livres(service.livres_avec_statut(terme))
            elif choix == "2":
                afficher_livres(service.livres_avec_statut())
            elif choix == "3":
                code = demander("Code (ex : L050) : ").upper()
                titre = demander("Titre : ")
                auteur = demander("Auteur : ")
                annee = demander_annee()
                categorie = input("Catégorie (facultatif) : ").strip()
                service.ajouter_livre(Livre(code, titre, auteur, annee, categorie))
                print("Livre ajouté.")
            elif choix == "4":
                code = demander("Code du livre à modifier : ").upper()
                livre = service.depot.obtenir_livre(code)
                if not livre:
                    raise ErreurGestion("Livre introuvable.")
                print("Appuyez sur Entrée pour garder la valeur actuelle.")
                titre = input(f"Titre [{livre.titre}] : ").strip()
                auteur = input(f"Auteur [{livre.auteur}] : ").strip()
                texte_annee = input(f"Année [{livre.annee}] : ").strip()
                categorie = input(f"Catégorie [{livre.categorie}] : ").strip()
                annee = None
                if texte_annee:
                    if not texte_annee.isdigit():
                        raise ErreurGestion("L'année doit être un nombre.")
                    annee = int(texte_annee)
                service.modifier_livre(code, titre, auteur, annee, categorie)
                print("Livre modifié.")
            else:
                print("Choix invalide.")
        except ErreurGestion as erreur:
            print("Impossible :", erreur)


def menu_membres(service):
    while True:
        print(MENU_MEMBRES)
        choix = input("Votre choix : ").strip()
        try:
            if choix == "0":
                return
            elif choix == "1":
                matricule = demander("Matricule (ex : IIT-01) : ").upper()
                nom = demander("Nom complet : ")
                service.inscrire_membre(matricule, nom)
                print("Membre inscrit.")
            elif choix == "2":
                matricule = demander("Matricule : ").upper()
                membre, emprunts = service.consulter_membre(matricule)
                print(f"{membre.nom} ({membre.matricule})")
                print(f"Emprunts en cours : {len(emprunts)}")
                afficher_emprunts(service, emprunts)
            elif choix == "3":
                membres = service.lister_membres()
                if not membres:
                    print("Aucun membre inscrit.")
                for m in membres:
                    print(f"{m.matricule} | {m.nom}")
            elif choix == "4":
                matricule = demander("Matricule du membre : ").upper()
                nom = demander("Nouveau nom : ")
                service.modifier_nom_membre(matricule, nom)
                print("Nom modifié.")
            else:
                print("Choix invalide.")
        except ErreurGestion as erreur:
            print("Impossible :", erreur)


def menu_emprunts(service):
    while True:
        print(MENU_EMPRUNTS)
        choix = input("Votre choix : ").strip()
        try:
            if choix == "0":
                return
            elif choix == "1":
                code = demander("Code du livre : ").upper()
                matricule = demander("Matricule : ").upper()
                retour = service.emprunter(code, matricule)
                print(f"Emprunt enregistré. Retour prévu le {jour(retour)}.")
            elif choix == "2":
                code = demander("Code du livre : ").upper()
                matricule = demander("Matricule de l'emprunteur : ").upper()
                nouvelle = service.prolonger(code, matricule)
                print(f"Emprunt de {matricule} prolongé. Nouveau retour le {jour(nouvelle)}.")
            elif choix == "3":
                code = demander("Code du livre : ").upper()
                matricule = demander("Matricule de l'emprunteur : ").upper()
                retard = service.rendre(code, matricule)
                print(f"Livre rendu par {matricule}. Merci !")
                if retard > 0:
                    print(f"Attention : {retard} jour(s) de retard.")
            else:
                print("Choix invalide.")
        except ErreurGestion as erreur:
            print("Impossible :", erreur)


def menu_suivi(service):
    while True:
        print(MENU_SUIVI)
        choix = input("Votre choix : ").strip()
        if choix == "0":
            return
        elif choix == "1":
            afficher_emprunts(service, service.emprunts_en_cours())
        elif choix == "2":
            afficher_emprunts(service, service.retards())
        elif choix == "3":
            afficher_emprunts(service, service.historique())
        else:
            print("Choix invalide.")


def afficher_statistiques(service):
    stats = service.statistiques()
    print("\n===== STATISTIQUES =====")
    print("Livres au catalogue :", stats["livres"])
    print("Livres disponibles  :", stats["disponibles"])
    print("Emprunts en cours   :", stats["emprunts"])
    print("Emprunts en retard  :", stats["retards"])
    print("Membres             :", stats["membres"])


# ---------- programme principal ----------
def main():
    # La base est créée dans le dossier data/, peu importe d'où on lance le programme.
    depot = DepotSQLite(Path(__file__).parent.parent / "data" / "bibliotheque.db")
    ajoutes = charger_catalogue_initial(depot)
    if ajoutes:
        print(f"{ajoutes} livres ajoutés au catalogue de départ.")
    service = Bibliotheque(depot)

    while True:
        print(MENU_PRINCIPAL)
        choix = input("Votre choix : ").strip()
        if choix == "0":
            print("Au revoir !")
            break
        elif choix == "1":
            menu_catalogue(service)
        elif choix == "2":
            menu_membres(service)
        elif choix == "3":
            menu_emprunts(service)
        elif choix == "4":
            menu_suivi(service)
        elif choix == "5":
            afficher_statistiques(service)
        else:
            print("Choix invalide.")


if __name__ == "__main__":
    main()
