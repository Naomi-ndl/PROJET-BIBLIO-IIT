"""Les trois objets du projet : Livre, Membre, Emprunt."""


class Livre:
    def __init__(self, code, titre, auteur, annee, categorie=""):
        self.code = code
        self.titre = titre
        self.auteur = auteur
        self.annee = annee            # 0 = année inconnue
        self.categorie = categorie


class Membre:
    def __init__(self, matricule, nom):
        self.matricule = matricule
        self.nom = nom


class Emprunt:
    def __init__(self, id, code_livre, matricule, date_emprunt,
                 date_retour_prevue, date_retour_reelle=None, nb_prolongations=0):
        self.id = id
        self.code_livre = code_livre
        self.matricule = matricule
        self.date_emprunt = date_emprunt
        self.date_retour_prevue = date_retour_prevue
        self.date_retour_reelle = date_retour_reelle   # None tant que le livre n'est pas rendu
        self.nb_prolongations = nb_prolongations
