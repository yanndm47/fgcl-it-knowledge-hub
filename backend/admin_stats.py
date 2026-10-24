"""
Statistiques agrégées pour le tableau de bord administrateur : vue
d'ensemble, évolution mensuelle des incidents, répartition par département.
"""

from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Technician, Incident, Department


def get_overview(db: Session) -> dict:
    """Les 4 chiffres clés de la vue d'ensemble."""
    active_technicians = db.query(Technician).filter(Technician.status == "actif").count()
    total_incidents = db.query(Incident).count()
    resolved = db.query(Incident).filter(Incident.status == "ferme").count()
    resolution_rate = round((resolved / total_incidents) * 100) if total_incidents > 0 else 0

    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    incidents_this_month = db.query(Incident).filter(Incident.created_at >= start_of_month).count()

    return {
        "active_technicians": active_technicians,
        "total_incidents": total_incidents,
        "incidents_this_month": incidents_this_month,
        "resolution_rate": resolution_rate,
    }


def get_incidents_by_month(db: Session, months: int = 6) -> list[dict]:
    """
    Nombre d'incidents déclarés par mois, sur les 'months' derniers mois
    (y compris les mois à zéro incident, pour un graphique continu).
    """
    rows = (
        db.query(
            func.strftime("%Y-%m", Incident.created_at).label("month"),
            func.count(Incident.id).label("count"),
        )
        .group_by("month")
        .all()
    )
    counts_by_month = {row.month: row.count for row in rows}

    now = datetime.now(timezone.utc)
    result = []
    for i in range(months - 1, -1, -1):
        year = now.year
        month = now.month - i
        while month <= 0:
            month += 12
            year -= 1
        key = f"{year:04d}-{month:02d}"
        result.append({"month": key, "count": counts_by_month.get(key, 0)})
    return result


def get_top_departments(db: Session, limit: int = 5) -> list[dict]:
    """Départements classés par nombre d'incidents déclarés, décroissant."""
    rows = (
        db.query(Department.nom, func.count(Incident.id).label("count"))
        .join(Incident, Incident.department_id == Department.id)
        .group_by(Department.nom)
        .order_by(func.count(Incident.id).desc())
        .limit(limit)
        .all()
    )
    return [{"name": nom, "count": count} for nom, count in rows]
