"""
Historique d'activité d'un technicien : statistiques agrégées + fil
d'activité récente, en combinant trois sources (incidents ouverts,
solutions proposées, étoiles données) en une seule liste triée par date.
"""

from sqlalchemy.orm import Session
from models import Incident, Solution, Star


def get_technician_stats(db: Session, technician_id: str) -> dict:
    """Chiffres clés pour les cartes de statistiques de la page Historique."""
    incidents_opened = db.query(Incident).filter(Incident.opened_by == technician_id)
    incidents_opened_count = incidents_opened.count()
    incidents_resolved_count = incidents_opened.filter(Incident.status == "ferme").count()
    solutions_authored_count = db.query(Solution).filter(Solution.author_id == technician_id).count()
    stars_given_count = db.query(Star).filter(Star.voter_id == technician_id).count()

    solution_ids = [s.id for s in db.query(Solution.id).filter(Solution.author_id == technician_id).all()]
    stars_received_count = (
        db.query(Star).filter(Star.solution_id.in_(solution_ids)).count() if solution_ids else 0
    )

    return {
        "incidents_opened": incidents_opened_count,
        "incidents_resolved": incidents_resolved_count,
        "solutions_authored": solutions_authored_count,
        "stars_given": stars_given_count,
        "stars_received": stars_received_count,
    }


def get_technician_activity_feed(db: Session, technician_id: str, limit: int = 20) -> list[dict]:
    """
    Combine 3 types d'événements en un seul fil chronologique :
    incidents ouverts, solutions proposées, étoiles données par CE technicien.
    """
    feed = []

    for incident in db.query(Incident).filter(Incident.opened_by == technician_id).all():
        feed.append({
            "type": "incident_opened",
            "description": f"Incident déclaré : « {incident.titre} »",
            "date": incident.created_at,
            "related_incident_id": incident.id,
        })

    for solution in db.query(Solution).filter(Solution.author_id == technician_id).all():
        feed.append({
            "type": "solution_authored",
            "description": "Solution proposée",
            "date": solution.created_at,
            "related_incident_id": solution.incident_id,
        })

    for star in db.query(Star).filter(Star.voter_id == technician_id).all():
        solution = db.get(Solution, star.solution_id)
        feed.append({
            "type": "star_given",
            "description": "Solution étoilée",
            "date": star.created_at,
            "related_incident_id": solution.incident_id if solution else None,
        })

    feed.sort(key=lambda item: item["date"], reverse=True)
    return feed[:limit]
