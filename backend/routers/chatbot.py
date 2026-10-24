"""
Endpoint chatbot complet (J19) — assemble tout le pipeline :

    recherche de similarité (J15-J16)
        -> classement des solutions (J17)
        -> génération de la recommandation (J18)

en une seule route, `/chatbot/ask`.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Technician
from schemas import ChatbotQuery, ChatbotResponse, ChatbotSolutionOut
from dependencies import get_current_technician
import vector_store
import scoring
import llm

router = APIRouter()


@router.post("/ask", response_model=ChatbotResponse)
def ask_chatbot(
    payload: ChatbotQuery,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """
    Pipeline complet :
    1. Recherche des incidents similaires (vector_store).
    2. Filtre algorithmique par seuil de similarité (is_similar_enough, J16) —
       décide s'il y a une correspondance suffisante SANS demander au LLM
       de le deviner lui-même (cf. décision documentée dans llm.py).
    3. Si rien d'assez proche, ou aucune solution disponible sur les
       incidents trouvés : proposition de créer un ticket, sans appeler Gemini.
    4. Sinon : classement des solutions (scoring.py) puis formulation de la
       réponse par Gemini (llm.py).
    """
    matches = vector_store.search_similar_incidents(payload.message, top_k=5)
    good_matches = [m for m in matches if vector_store.is_similar_enough(m["distance"])]

    if not good_matches:
        return ChatbotResponse(found_match=False, message=llm.NO_MATCH_MESSAGE, solutions=[])

    ranked = scoring.rank_solutions_for_matches(good_matches, db, top_k=3)

    if not ranked:
        # Des incidents proches existent, mais aucune solution n'y a encore
        # été proposée -> rien de concret à recommander pour l'instant.
        return ChatbotResponse(found_match=False, message=llm.NO_MATCH_MESSAGE, solutions=[])

    try:
        message = llm.generate_recommendation(payload.message, ranked)
    except RuntimeError as e:
        # Clé API absente ou mal configurée : erreur claire, pas un plantage brut.
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    solutions_out = [
        ChatbotSolutionOut(solution=item["solution"], score=item["score"], is_accepted=item["is_accepted"])
        for item in ranked
    ]
    return ChatbotResponse(found_match=True, message=message, solutions=solutions_out)
