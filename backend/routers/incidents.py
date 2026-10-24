"""
Routes de gestion des incidents — déclaration et consultation (J8).

La fermeture d'un ticket (réservée à son ouvreur) sera ajoutée au J10.
"""

from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import Incident, Department, Technician, Solution, Favorite
from schemas import IncidentCreate, IncidentOut, IncidentClose, IncidentCreateResponse
from dependencies import get_current_technician
import vector_store
import notifications

router = APIRouter()


@router.post("", response_model=IncidentCreateResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """
    Déclare un nouvel incident.

    Point important : 'opened_by' n'est PAS lu depuis le corps de la requête
    (le schéma IncidentCreate ne le contient même pas) — il est fixé ici,
    côté serveur, à partir du technicien authentifié. Un technicien ne peut
    donc jamais déclarer un incident au nom de quelqu'un d'autre.
    """
    department = db.get(Department, payload.department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="Département introuvable")

    # Détection de doublons AVANT la création : on cherche parmi les
    # incidents DÉJÀ indexés, donc avant d'ajouter celui-ci (sinon il se
    # trouverait lui-même). Ne bloque jamais — seulement un avertissement.
    duplicate_query_text = vector_store.build_incident_text(payload.titre, payload.symptomes, payload.contexte)
    try:
        possible_duplicates = vector_store.find_possible_duplicates(duplicate_query_text)
    except Exception:
        # Si le modèle d'embedding est indisponible, on ne bloque pas la
        # déclaration de l'incident pour autant — la détection de doublons
        # est un confort, pas une condition bloquante.
        possible_duplicates = []

    incident = Incident(
        titre=payload.titre,
        description=payload.description,
        symptomes=payload.symptomes,
        contexte=payload.contexte,
        department_id=payload.department_id,
        opened_by=current.id,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Indexation vectorielle incrémentale : cet incident devient immédiatement
    # comparable aux autres, sans reconstruire toute la base (cf. J15).
    try:
        vector_store.upsert_incident(
            incident_id=incident.id,
            titre=incident.titre,
            symptomes=incident.symptomes,
            contexte=incident.contexte,
            department_id=incident.department_id,
        )
    except Exception:
        # Même logique : l'indexation échoue -> l'incident reste créé quand
        # même. Il pourra être rattrapé plus tard via reindex_all.py.
        pass

    return IncidentCreateResponse(**IncidentOut.model_validate(incident).model_dump(), possible_duplicates=possible_duplicates)


@router.get("", response_model=list[IncidentOut])
def list_incidents(
    status_filter: Optional[str] = Query(default=None, alias="status", description="ouvert | ferme"),
    department_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """
    Liste les incidents, visibles par tout technicien connecté quel que soit
    son département (choix de cadrage : capitalisation collective).
    Filtres optionnels par statut et par département.
    """
    query = db.query(Incident)
    if status_filter is not None:
        query = query.filter(Incident.status == status_filter)
    if department_id is not None:
        query = query.filter(Incident.department_id == department_id)
    return query.order_by(Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """Détail d'un incident précis."""
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident introuvable")
    return incident


@router.post("/{incident_id}/close", response_model=IncidentOut)
def close_incident(
    incident_id: str,
    payload: IncidentClose,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """
    Ferme un incident — RÉSERVÉ STRICTEMENT à son ouvreur (opened_by).

    Deux façons de clore, mutuellement exclusives :
      1. accepted_solution_id : retenir une solution déjà proposée par quelqu'un.
      2. own_solution_content : l'ouvreur documente lui-même la solution trouvée
         (crée une nouvelle Solution avec is_documented_by_opener=True).
    """
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident introuvable")

    # La vérification qui protège tout le système : comparaison stricte entre
    # l'identifiant du technicien connecté et celui qui a ouvert le ticket.
    if incident.opened_by != current.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le technicien ayant ouvert ce ticket peut le fermer",
        )

    if incident.status == "ferme":
        raise HTTPException(status_code=400, detail="Cet incident est déjà fermé")

    has_existing = payload.accepted_solution_id is not None
    has_own = payload.own_solution_content is not None

    if has_existing == has_own:
        # Vrai si les deux sont fournis, ou si aucun ne l'est -> dans les deux cas, invalide
        raise HTTPException(
            status_code=400,
            detail="Fournir exactement un des deux champs : accepted_solution_id OU own_solution_content",
        )

    if has_existing:
        solution = db.get(Solution, payload.accepted_solution_id)
        if solution is None or solution.incident_id != incident_id:
            raise HTTPException(status_code=404, detail="Solution introuvable pour cet incident")
        incident.accepted_solution_id = solution.id
    else:
        own_solution = Solution(
            incident_id=incident_id,
            author_id=current.id,
            contenu=payload.own_solution_content,
            is_documented_by_opener=True,
        )
        db.add(own_solution)
        db.flush()  # obtient own_solution.id sans encore valider définitivement la transaction
        incident.accepted_solution_id = own_solution.id

    incident.status = "ferme"
    incident.closed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(incident)

    # Notifie l'auteur de la solution retenue, sauf si c'est l'ouvreur
    # lui-même (cas de own_solution_content, il n'a pas besoin de s'auto-notifier).
    accepted_solution = db.get(Solution, incident.accepted_solution_id)
    if accepted_solution is not None and accepted_solution.author_id != current.id:
        notifications.create_notification(
            db, recipient_id=accepted_solution.author_id, notif_type="incident_closed",
            message=f"Ta solution a été retenue pour clore l'incident « {incident.titre} »",
            related_incident_id=incident.id,
        )

    return incident


@router.get("/favorites/mine", response_model=list[IncidentOut])
def list_my_favorites(
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """Liste des incidents que le technicien connecté a mis en favori, du plus récent au plus ancien."""
    return (
        db.query(Incident)
        .join(Favorite, Favorite.incident_id == Incident.id)
        .filter(Favorite.technician_id == current.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )


@router.post("/{incident_id}/favorite", status_code=status.HTTP_201_CREATED)
def add_favorite(
    incident_id: str,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """Ajoute un incident aux favoris du technicien connecté."""
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident introuvable")

    existing = (
        db.query(Favorite)
        .filter(Favorite.technician_id == current.id, Favorite.incident_id == incident_id)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Cet incident est déjà dans tes favoris")

    db.add(Favorite(technician_id=current.id, incident_id=incident_id))
    db.commit()
    return {"message": "Ajouté aux favoris"}


@router.delete("/{incident_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    incident_id: str,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """Retire un incident des favoris du technicien connecté."""
    favorite = (
        db.query(Favorite)
        .filter(Favorite.technician_id == current.id, Favorite.incident_id == incident_id)
        .first()
    )
    if favorite is None:
        raise HTTPException(status_code=404, detail="Cet incident n'est pas dans tes favoris")

    db.delete(favorite)
    db.commit()
