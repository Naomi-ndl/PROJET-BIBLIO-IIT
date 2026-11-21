"""Les livres déjà enregistrés au premier lancement.

Pour ajouter un livre au catalogue de départ : ajoute une ligne dans la liste.
annee = 0 veut dire "année inconnue".
"""
from app.modeles import Livre

LIVRES_INITIAUX = [
    Livre("L001", "Le Petit Prince", "Antoine de Saint-Exupéry", 1943, "Conte"),
    Livre("L002", "Les Soleils des indépendances", "Ahmadou Kourouma", 1968, "Roman"),
    Livre("L003", "Une si longue lettre", "Mariama Bâ", 1979, "Roman"),
    Livre("L004", "La Perle", "John Steinbeck", 1947, "Roman"),
    Livre("L005", "La Tulipe noire", "Alexandre Dumas", 1850, "Roman"),
    Livre("L006", "Cinq contes", "Guy de Maupassant", 1928, "Contes"),
    Livre("L007", "Allah n'est pas obligé", "Ahmadou Kourouma", 2000, "Roman"),
    Livre("L008", "Le Vieux Nègre et la médaille", "Ferdinand Oyono", 1956, "Roman"),
    Livre("L009", "Monsieur Thôgô-Gnini", "Bernard Dadié", 1970, "Théâtre"),
    Livre("L010", "Les Frasques d'Ébinto", "Amadou Koné", 1975, "Roman"),
    Livre("L011", "Le Retour de l'enfant soldat", "François d'Assise N'Dah", 20084, "Roman"),
    Livre("L012", "Une vie de boy", "Ferdinand Oyono", 1956, "Roman"),
    Livre("L013", "Climbié", "Bernard Dadié", 1956, "Roman"),
    Livre("L014", "L'Aventure ambiguë", "Cheikh Hamidou Kane", 1961, "Roman"),
    Livre("L015", "Les Bouts de bois de Dieu", "Ousmane Sembène", 1960, "Roman"),
    Livre("L016", "L'Enfant noir", "Camara Laye", 1953, "Roman"),
    Livre("L017", "En attendant le vote des bêtes sauvages", "Ahmadou Kourouma", 1998, "Roman"),
    Livre("L018", "L'Étranger", "Albert Camus", 1942, "Roman"),
    Livre("L019", "Les Misérables", "Victor Hugo", 1862, "Roman"),
    Livre("L020", "Candide", "Voltaire", 1759, "Conte"),
    Livre("L021", "Germinal", "Émile Zola", 1885, "Roman"),
    Livre("L022", "Antigone", "Jean Anouilh", 1944, "Théâtre"),
]


def charger_catalogue_initial(depot):
    """Ajoute les livres de départ SI la base est vide. Retourne le nombre ajouté."""
    if depot.chercher_livres():      # la base contient déjà des livres
        return 0
    for livre in LIVRES_INITIAUX:
        depot.ajouter_livre(livre)
    return len(LIVRES_INITIAUX)
