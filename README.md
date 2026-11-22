# PROJET BIBLIO-IIT

Application console de gestion de bibliothèque développée en **Python avec SQLite**.

## Lancement

```bash
python main.py
```

Au premier lancement, la base de données `data/bibliotheque.db` est créée automatiquement avec 22 livres. Les données sont conservées après chaque utilisation.

## Fonctionnalités

| Menu | Actions |
|---|---|
| Catalogue | Rechercher, lister, ajouter et modifier un livre |
| Membres | Inscrire, consulter, lister et modifier un membre |
| Emprunts | Emprunter, prolonger et rendre un livre |
| Suivi | Consulter les emprunts en cours, les retards et l'historique |
| Statistiques | Consulter le nombre de livres, d'emprunts, de retards et de membres |

## Règles de gestion

- Chaque livre possède un seul exemplaire et ne peut pas être emprunté s'il est déjà emprunté.
- Durée d'emprunt : 14 jours.
- Maximum 3 livres simultanément par membre.
- Une seule prolongation de 14 jours, si l'emprunt n'est pas en retard.
- Pour rendre ou prolonger un emprunt, le code du livre et le matricule du membre sont nécessaires.

## Organisation du projet

```text
PROJET BIBLIO-IIT/
├── main.py
├── app/
│   ├── console.py
│   ├── service.py
│   ├── regles.py
│   └── modeles.py
├── data/
│   ├── depot_sqlite.py
│   └── catalogue_initial.py
└── tests/
```

- `main.py` : point d'entrée du programme.
- `console.py` : menus et saisies utilisateur.
- `service.py` : opérations de la bibliothèque.
- `regles.py` : règles de gestion des emprunts.
- `modeles.py` : modèles Livre, Membre et Emprunt.
- `depot_sqlite.py` : accès à la base de données.
- `catalogue_initial.py` : catalogue chargé au premier lancement.
- `tests/` : tests automatisés.

**Fonctionnement :** la console communique avec le service, qui applique les règles de gestion et utilise le dépôt SQLite pour accéder aux données. La console n'accède jamais directement à la base de données.

auteur:N'DOLI MOAYE MARIE EUNICE NAOMI