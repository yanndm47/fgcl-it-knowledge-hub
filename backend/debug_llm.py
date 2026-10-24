"""
Script de diagnostic pour tester l'intégration Gemini isolément (J18),
sans attendre que le reste du pipeline (recherche + score, J19) soit
branché. Utilise deux fausses solutions pour vérifier uniquement que la
connexion à Gemini fonctionne et que la réponse est cohérente.

Usage :
    python debug_llm.py "le wifi ne répond plus au 2e étage"

Nécessite une vraie GEMINI_API_KEY dans le fichier .env.
"""

import sys
from types import SimpleNamespace
from llm import generate_recommendation


def main():
    if len(sys.argv) < 2:
        print('Usage : python debug_llm.py "texte de la demande à tester"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    # Deux fausses solutions, pour tester uniquement l'appel à Gemini
    # (le vrai classement par score arrivera au J19).
    fake_solutions = [
        {
            "solution": SimpleNamespace(contenu="Redémarrer le routeur et attendre 30 secondes avant de le rebrancher", stars_count=4),
            "score": 0.91,
            "is_accepted": True,
        },
        {
            "solution": SimpleNamespace(contenu="Vérifier que le câble Ethernet du routeur est bien branché", stars_count=1),
            "score": 0.42,
            "is_accepted": False,
        },
    ]

    print(f"Requête testée : {query!r}")
    print("Appel de Gemini en cours...\n")

    try:
        response = generate_recommendation(query, fake_solutions)
        print("--- Réponse de Gemini ---")
        print(response)
        print("---")
        print("\n✅ La connexion à Gemini fonctionne.")
    except RuntimeError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue lors de l'appel à Gemini : {e}")


if __name__ == "__main__":
    main()
