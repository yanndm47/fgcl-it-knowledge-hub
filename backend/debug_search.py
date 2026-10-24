"""
Script de diagnostic de la recherche par similarité (J16).

Reprend le principe de debug_search.py du chatbot FGCL : interroger
directement le moteur de similarité en ligne de commande, voir les
distances réelles, et ajuster SIMILARITY_THRESHOLD (dans vector_store.py)
en connaissance de cause plutôt qu'au hasard.

Usage :
    python debug_search.py "le wifi ne répond plus au 2e étage"

Nécessite qu'au moins un incident ait déjà été déclaré (via l'API ou le
frontend) pour avoir quelque chose à comparer.
"""

import sys
from vector_store import search_similar_incidents, SIMILARITY_THRESHOLD, is_similar_enough
from database import SessionLocal
from models import Incident


def main():
    if len(sys.argv) < 2:
        print('Usage : python debug_search.py "texte de la requête à tester"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    matches = search_similar_incidents(query, top_k=5)

    if not matches:
        print("Aucun incident indexé pour l'instant — déclare au moins un incident avant de tester.")
        return

    db = SessionLocal()
    print(f"\nRequête testée : {query!r}")
    print(f"Seuil de similarité actuel : {SIMILARITY_THRESHOLD}\n")
    print(f"{'Distance':<10} {'Retenu ?':<10} Titre de l'incident")
    print("-" * 60)

    for m in matches:
        incident = db.get(Incident, m["incident_id"])
        titre = incident.titre if incident else "(incident supprimé depuis)"
        retenu = "✅ oui" if is_similar_enough(m["distance"]) else "❌ non"
        print(f"{m['distance']:<10.4f} {retenu:<10} {titre}")

    db.close()
    print(
        "\nSi des incidents pertinents apparaissent comme '❌ non' alors qu'ils "
        "devraient matcher, augmente SIMILARITY_THRESHOLD dans vector_store.py. "
        "Si des incidents non pertinents apparaissent comme '✅ oui', diminue-le."
    )


if __name__ == "__main__":
    main()
