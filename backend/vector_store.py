"""
Pipeline d'embedding incrémental — moteur de similarité entre incidents.

Différence volontaire avec le chatbot FGCL : là-bas, toute la base
vectorielle était supprimée et reconstruite à chaque mise à jour
(build_vector_db.py). Ça ne passe pas à l'échelle ici, puisque les
incidents arrivent en continu au fil de l'usage réel. On fait donc un
UPSERT (ajout/mise à jour) incident par incident, au moment de sa
création — jamais de reconstruction totale.

Chargement PARESSEUX (lazy) : le modèle d'IA et la base vectorielle ne
sont initialisés qu'au premier vrai besoin (première déclaration
d'incident), pas au démarrage de l'application. Ça évite de bloquer tout
le serveur au lancement si le téléchargement du modèle est lent, et ça
permet de tester le reste du code sans dépendre du réseau.
"""

import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

# Même modèle que le chatbot FGCL : multilingue (français inclus), léger,
# déjà calibré et maîtrisé sur le projet précédent.
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Seuil de distance en dessous duquel un incident est considéré comme
# "assez similaire" pour être proposé au chatbot (J17-J19). Repris comme
# point de départ du seuil calibré sur le chatbot FGCL (0,63 en distance
# cosinus) ; À RECALIBRER ici avec debug_search.py une fois quelques
# incidents réels indexés — le vocabulaire et la longueur des textes
# diffèrent (incidents structurés vs FAQ libre), le seuil optimal peut
# donc différer légèrement.
SIMILARITY_THRESHOLD = 0.63


def is_similar_enough(distance: float) -> bool:
    """Un incident est-il assez proche pour être considéré comme un match ?"""
    return distance <= SIMILARITY_THRESHOLD


# Seuil plus strict que SIMILARITY_THRESHOLD : au-delà de la simple similarité
# thématique, ceci détecte un incident QUASI IDENTIQUE, probablement un doublon
# (ex. deux techniciens qui déclarent le même wifi en panne à 5 minutes d'écart).
DUPLICATE_THRESHOLD = 0.15


def find_possible_duplicates(query_text: str, top_k: int = 3) -> list[str]:
    """
    Cherche, PARMI LES INCIDENTS DÉJÀ INDEXÉS, ceux quasi identiques au texte
    donné. À appeler AVANT d'indexer le nouvel incident (sinon il se
    trouverait lui-même). Ne bloque jamais la création — sert seulement à
    avertir le technicien qu'un incident très proche existe peut-être déjà.
    """
    matches = search_similar_incidents(query_text, top_k=top_k)
    return [m["incident_id"] for m in matches if m["distance"] <= DUPLICATE_THRESHOLD]

_collection = None  # initialisé au premier appel de _get_collection()


def _get_collection():
    """Initialise (une seule fois) le modèle d'embedding et la collection ChromaDB."""
    global _collection
    if _collection is None:
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_or_create_collection(
            name="incidents",
            embedding_function=embedding_function,
            # Explicite et important : le seuil SIMILARITY_THRESHOLD (0.63)
            # a été calibré sur une DISTANCE COSINUS. Sans ce réglage,
            # ChromaDB utilise par défaut une distance euclidienne (l2),
            # dont l'échelle de valeurs n'a rien à voir -> le seuil devient
            # totalement faux sans qu'aucune erreur ne soit levée (bug
            # découvert en conditions réelles : tout ressortait comme "non
            # similaire" même pour un incident quasi identique).
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def build_incident_text(titre: str, symptomes: str, contexte: str | None) -> str:
    """
    Construit le texte qui sera encodé pour un incident.

    Choix assumé : titre + symptômes + contexte (si présent), plutôt que
    symptômes + contexte seuls. Le titre porte souvent une bonne partie du
    sens ("Wifi inaccessible"), surtout quand le contexte est vide (champ
    optionnel) — l'inclure améliore la qualité de la recherche par
    similarité sans coût supplémentaire. Fonction pure, sans dépendance
    réseau : testable isolément.
    """
    parts = [titre, symptomes]
    if contexte:
        parts.append(contexte)
    return ". ".join(parts)


def upsert_incident(incident_id: str, titre: str, symptomes: str, contexte: str | None, department_id: str) -> None:
    """
    Encode un incident et l'ajoute (ou le met à jour) dans la base
    vectorielle. Appelé une seule fois, à la création de l'incident.
    """
    text = build_incident_text(titre, symptomes, contexte)
    _get_collection().upsert(
        ids=[incident_id],
        documents=[text],
        metadatas=[{"department_id": department_id}],
    )


def search_similar_incidents(query_text: str, top_k: int = 5) -> list[dict]:
    """
    Cherche les incidents les plus proches sémantiquement d'un texte donné.
    Renvoie une liste de dicts {incident_id, distance}, du plus proche au
    plus éloigné. Une distance plus petite = plus similaire.
    """
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        return []

    results = collection.query(
        query_texts=[query_text],
        n_results=min(top_k, count),
    )

    matches = []
    for incident_id, distance in zip(results["ids"][0], results["distances"][0]):
        matches.append({"incident_id": incident_id, "distance": distance})
    return matches
