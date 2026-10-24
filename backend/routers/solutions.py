"""
Routes de gestion des solutions proposées sur un incident (J9).

Le système d'étoiles (J11) et la fermeture de ticket avec choix de la
solution retenue (J10) viendront compléter ce module.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import Solution, Incident, Technician, Star
from schemas import SolutionCreate, SolutionOut
from dependencies import get_current_technician
import notifications

# Pas de préfixe ici : les chemins complets sont écrits explicitement
# ci-dessous (/incidents/{incident_id}/solutions), pour rester lisibles
# dans /docs sous la même section que les incidents.
router = APIRouter()


@router.post(
    "/incidents/{incident_id}/solutions",
    response_model=SolutionOut,
    status_code=status.HTTP_201_CREATED,
)
def propose_solution(
    incident_id: str,
    payload: SolutionCreate,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """
    Propose une solution sur un incident. N'importe quel technicien connecté
    peut répondre, y compris si l'incident n'est pas le sien — c'est la base
    de la capitalisation collective. Un incident fermé n'accepte plus de
    nouvelles réponses.
    """
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident introuvable")
    if incident.status == "ferme":
        raise HTTPException(status_code=400, detail="Cet incident est fermé, impossible d'ajouter une réponse")

    solution = Solution(
        incident_id=incident_id,
        author_id=current.id,
        contenu=payload.contenu,
    )
    db.add(solution)
    db.commit()
    db.refresh(solution)

    # Notifie l'ouvreur du ticket, sauf s'il répond lui-même à son propre incident.
    if incident.opened_by != current.id:
        notifications.create_notification(
            db, recipient_id=incident.opened_by, notif_type="new_solution",
            message=f"Nouvelle réponse sur ton incident « {incident.titre} »",
            related_incident_id=incident.id,
        )

    return solution


@router.get("/incidents/{incident_id}/solutions", response_model=list[SolutionOut])
def list_solutions(
    incident_id: str,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """Liste toutes les solutions proposées sur un incident, de la plus ancienne à la plus récente."""
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident introuvable")

    return (
        db.query(Solution)
        .filter(Solution.incident_id == incident_id)
        .order_by(Solution.created_at.asc())
        .all()
    )


@router.post(
    "/solutions/{solution_id}/star",
    response_model=SolutionOut,
    status_code=status.HTTP_201_CREATED,
)
def star_solution(
    solution_id: str,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """
    Étoile une solution pour signaler qu'elle a fonctionné.

    Deux garde-fous, pour que le classement par étoiles reste fiable :
      1. Interdiction de l'auto-vote (un auteur ne peut pas étoiler sa propre réponse).
      2. Un seul vote par (solution, technicien) — garanti à la fois ici en
         Python ET par la contrainte unique posée en base au J2 (double filet).
    """
    solution = db.get(Solution, solution_id)
    if solution is None:
        raise HTTPException(status_code=404, detail="Solution introuvable")

    if solution.author_id == current.id:
        raise HTTPException(status_code=400, detail="Impossible d'étoiler sa propre solution")

    existing = (
        db.query(Star)
        .filter(Star.solution_id == solution_id, Star.voter_id == current.id)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Vous avez déjà étoilé cette solution")

    star = Star(solution_id=solution_id, voter_id=current.id)
    db.add(star)
    try:
        db.commit()
    except IntegrityError:
        # Filet de sécurité si deux votes arrivent en même temps (contrainte unique de la base)
        db.rollback()
        raise HTTPException(status_code=409, detail="Vous avez déjà étoilé cette solution")

    db.refresh(solution)

    # Notifie l'auteur de la solution (l'auto-vote est déjà interdit plus haut, pas de risque de doublon inutile).
    notifications.create_notification(
        db, recipient_id=solution.author_id, notif_type="new_star",
        message="Une de tes solutions a reçu une étoile ⭐",
        related_incident_id=solution.incident_id,
    )

    return solution
