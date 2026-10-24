"""
Calcul du score combiné des solutions (J17).

Formule retenue (cahier des charges, section 5) :
    score = 0,4 × solution_acceptée
          + 0,3 × (étoiles / étoiles_max_du_lot)
          + 0,2 × similarité_incident_source
          + 0,1 × fraîcheur

Ces poids sont un point de départ documenté, ajustables empiriquement
une fois de vraies données disponibles — même démarche que le seuil de
similarité du J16.

Ce module est volontairement séparé en deux niveaux :
  1. compute_solution_score() : pur calcul, aucune dépendance à la base
     de données ni au modèle d'IA -> entièrement testable.
  2. rank_solutions_for_matches() : assemble les données réelles (venant
     de la base) autour de ce calcul -> testable avec de fausses
     correspondances, sans avoir besoin du vrai modèle d'embedding.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from models import Solution, Incident

# Poids de la formule — modifiables ici en un seul endroit si le jury
# ou l'usage réel suggère un rééquilibrage.
WEIGHT_ACCEPTED = 0.4
WEIGHT_STARS = 0.3
WEIGHT_SIMILARITY = 0.2
WEIGHT_FRESHNESS = 0.1

# Fraîcheur : décroissance douce sur ~30 jours (un incident d'aujourd'hui
# pèse plein pot, un incident d'il y a 30 jours pèse moitié moins, etc.)
FRESHNESS_HALF_LIFE_DAYS = 30


def compute_solution_score(
    is_accepted: bool,
    stars_count: int,
    max_stars_in_set: int,
    similarity_distance: float,
    created_at: datetime,
    now: datetime | None = None,
) -> float:
    """
    Calcule le score d'UNE solution. Fonction pure : mêmes entrées ->
    toujours la même sortie, aucun accès base de données ou réseau.
    """
    now = now or datetime.now(timezone.utc)

    accepted_component = 1.0 if is_accepted else 0.0

    stars_component = (stars_count / max_stars_in_set) if max_stars_in_set > 0 else 0.0

    # Conversion distance -> similarité : plus la distance est petite, plus
    # la similarité doit être grande. Approximation simple assumée, à
    # affiner une fois de vraies distances observées (cf. J16).
    similarity_component = max(0.0, 1 - similarity_distance)

    age_days = max(0.0, (now - created_at).total_seconds() / 86400)
    freshness_component = 1 / (1 + age_days / FRESHNESS_HALF_LIFE_DAYS)

    return (
        WEIGHT_ACCEPTED * accepted_component
        + WEIGHT_STARS * stars_component
        + WEIGHT_SIMILARITY * similarity_component
        + WEIGHT_FRESHNESS * freshness_component
    )


def rank_solutions_for_matches(matches: list[dict], db: Session, top_k: int = 3) -> list[dict]:
    """
    À partir d'une liste de correspondances d'incidents similaires
    (typiquement renvoyée par vector_store.search_similar_incidents),
    récupère toutes leurs solutions, calcule le score combiné de chacune,
    et renvoie les 'top_k' meilleures, triées par score décroissant.

    Séparé de la recherche vectorielle elle-même : cette fonction ne
    dépend que de la base de données, donc testable sans le vrai modèle.
    """
    distance_by_incident = {m["incident_id"]: m["distance"] for m in matches}
    incident_ids = list(distance_by_incident.keys())

    if not incident_ids:
        return []

    solutions = db.query(Solution).filter(Solution.incident_id.in_(incident_ids)).all()
    if not solutions:
        return []

    incidents_by_id = {
        i.id: i for i in db.query(Incident).filter(Incident.id.in_(incident_ids)).all()
    }

    max_stars_in_set = max((s.stars_count for s in solutions), default=0)
    now = datetime.now(timezone.utc)

    scored = []
    for solution in solutions:
        incident = incidents_by_id.get(solution.incident_id)
        is_accepted = incident is not None and incident.accepted_solution_id == solution.id
        distance = distance_by_incident.get(solution.incident_id, 1.0)

        created_at = solution.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        score = compute_solution_score(
            is_accepted=is_accepted,
            stars_count=solution.stars_count,
            max_stars_in_set=max_stars_in_set,
            similarity_distance=distance,
            created_at=created_at,
            now=now,
        )
        scored.append({
            "solution": solution,
            "score": score,
            "incident_id": solution.incident_id,
            "is_accepted": is_accepted,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
