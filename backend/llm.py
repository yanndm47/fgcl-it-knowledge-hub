"""
Intégration Gemini pour la génération de réponse du chatbot (J18).

Utilise le nouveau SDK officiel `google-genai` (package `google.genai`),
et NON l'ancien `google-generativeai` : ce dernier est officiellement
déprécié par Google ("all support has ended"), repéré en testant ce
module avant de le livrer. Comme ce projet démarre à neuf (contrairement
à FGCL, qui utilisait déjà l'ancien SDK avant cette dépréciation), autant
partir directement sur la base soutenable.

Chargement PARESSEUX, même principe qu'au J15 pour le modèle
d'embedding : la clé API n'est lue et le client Gemini n'est créé qu'au
premier vrai appel, jamais à l'importation du fichier.

Décision de conception (à noter comme telle en soutenance) : plutôt que
de demander au LLM de lever lui-même une balise "aucun incident
similaire" (comme le faisait le chatbot FGCL avec [URGENCE_DETECTEE]),
la décision "y a-t-il une correspondance suffisante ?" est prise ici de
façon ALGORITHMIQUE, à partir du seuil de distance calibré au J16
(is_similar_enough, dans vector_store.py). C'est plus fiable qu'une
auto-détection par le LLM (pas de risque d'hallucination sur ce point
précis), et entièrement testable sans dépendre du réseau. Gemini n'est
appelé QUE lorsqu'il y a déjà au moins une solution pertinente à formuler.
"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()  # chargé explicitement ici, sans dépendre de l'ordre d'import
               # d'autres fichiers (bug corrigé : debug_llm.py importait ce
               # module seul, sans jamais déclencher le chargement du .env)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

NO_MATCH_MESSAGE = (
    "Je n'ai trouvé aucun incident suffisamment similaire dans l'historique. "
    "Je te propose de créer un nouveau ticket pour cet incident — les prochains "
    "techniciens qui rencontreront le même problème pourront s'appuyer sur ta solution."
)

SYSTEM_PROMPT = """Tu es l'assistant du IT Knowledge Hub de FGCL, une plateforme
interne de capitalisation des incidents informatiques.

Tu reçois la description d'un nouvel incident déclaré par un technicien, ainsi
qu'une liste de solutions déjà appliquées sur des incidents similaires,
classées par pertinence (score combinant : solution officiellement retenue,
nombre d'étoiles reçues par les autres techniciens, proximité avec l'incident
actuel, fraîcheur).

Ta tâche : rédiger une réponse claire, professionnelle et concise en français,
qui présente ces solutions au technicien dans l'ordre donné, en expliquant
brièvement pourquoi chacune est pertinente. Ne t'appuie que sur les solutions
fournies ci-dessous — n'invente jamais de solution supplémentaire, de
procédure ou de détail technique qui n'y figure pas."""

_client = None


def _get_client():
    """Crée et met en cache le client Gemini, une seule fois."""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY absente du .env — impossible d'appeler Gemini. "
                "Récupère une clé sur Google AI Studio et ajoute-la à ton .env."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def build_prompt(query_text: str, ranked_solutions: list[dict]) -> str:
    """
    Construit le texte envoyé à Gemini à partir de la demande et des
    solutions déjà classées (J17). Fonction pure, testable sans réseau.
    """
    lines = [
        f"Nouvel incident déclaré par le technicien : {query_text}",
        "",
        "Solutions candidates, déjà classées par pertinence :",
    ]
    for i, item in enumerate(ranked_solutions, 1):
        solution = item["solution"]
        badge = " [solution officiellement retenue sur son incident d'origine]" if item.get("is_accepted") else ""
        lines.append(
            f"{i}. {solution.contenu} "
            f"(score {item['score']:.2f}, {solution.stars_count} étoile(s){badge})"
        )
    lines.append("")
    lines.append("Rédige la recommandation à présenter au technicien.")
    return "\n".join(lines)


def generate_recommendation(query_text: str, ranked_solutions: list[dict]) -> str:
    """
    Appelle Gemini pour formuler la réponse finale à partir des solutions
    déjà classées. C'est la SEULE fonction de ce module qui a besoin d'un
    vrai accès réseau et d'une vraie clé API.
    """
    prompt = build_prompt(query_text, ranked_solutions)
    client = _get_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=[SYSTEM_PROMPT, prompt],
    )
    return response.text
