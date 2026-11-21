# PROJET BIBLIO-IIT

Application console de gestion de bibliothèque (Python + SQLite).
Aucune bibliothèque externe n'est nécessaire.

## Lancer

    python main.py

Au premier lancement, la base `data/bibliotheque.db` est créée avec un catalogue
de départ (22 livres). Les données sont conservées ensuite.

## Tester

    pip install pytest
    pytest

## Architecture

    PROJET BIBLIO-IIT/
    ├── main.py                  point d'entrée
    ├── app/                     ce que fait l'application
    │   ├── console.py           menus et saisies
    │   ├── service.py           emprunter, rendre, prolonger...
    │   ├── regles.py            durée, limite, retards, prolongation
    │   └── modeles.py           Livre, Membre, Emprunt
    ├── data/                    tout ce qui touche aux données
    │   ├── depot_sqlite.py      requêtes SQL
    │   ├── catalogue_initial.py livres chargés au premier lancement
    │   └── bibliotheque.db      créée automatiquement (non versionnée)
    └── tests/

Appels : `console -> service -> regles` et `service -> depot_sqlite -> modeles`.
La console ne parle jamais directement à la base.

## Règles de la bibliothèque

- Durée d'emprunt : 14 jours.
- 3 livres maximum en même temps par membre.
- Prolongation : 1 fois (+14 jours), si le livre n'est pas en retard.
- Un livre ne peut pas être emprunté s'il l'est déjà.
- Pour rendre ou prolonger, il faut le code du livre ET le matricule de l'emprunteur.
- Le matricule a le format IIT-01.
- On peut modifier un livre (titre, auteur, année, catégorie) et le nom d'un membre ; le code du livre et le matricule ne changent pas.
