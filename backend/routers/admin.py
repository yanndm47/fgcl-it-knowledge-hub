"""
Routes réservées aux administrateurs : validation ou rejet des comptes
techniciens en attente d'inscription.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Technician
from schemas import TechnicianOut, AdminStatsOut
from dependencies import require_admin
import notifications
import admin_stats

router = APIRouter()


@router.get("/pending-technicians", response_model=list[TechnicianOut])
def list_pending_technicians(
    db: Session = Depends(get_db),
    admin: Technician = Depends(require_admin),
):
    """Liste tous les comptes techniciens en attente de validation."""
    return db.query(Technician).filter(Technician.status == "pending").all()


@router.post("/technicians/{technician_id}/approve", response_model=TechnicianOut)
def approve_technician(
    technician_id: str,
    db: Session = Depends(get_db),
    admin: Technician = Depends(require_admin),
):
    """Valide un compte technicien en attente : il pourra désormais se connecter."""
    technician = db.get(Technician, technician_id)
    if technician is None:
        raise HTTPException(status_code=404, detail="Technicien introuvable")
    if technician.status != "pending":
        raise HTTPException(status_code=400, detail="Ce compte n'est pas en attente de validation")

    technician.status = "actif"
    db.commit()
    db.refresh(technician)

    notifications.create_notification(
        db, recipient_id=technician.id, notif_type="account_approved",
        message="Ton compte a été validé — tu peux maintenant te connecter.",
    )

    return technician


@router.delete("/technicians/{technician_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
def reject_technician(
    technician_id: str,
    db: Session = Depends(get_db),
    admin: Technician = Depends(require_admin),
):
    """Rejette et supprime un compte technicien en attente (ex. inscription frauduleuse ou erronée)."""
    technician = db.get(Technician, technician_id)
    if technician is None:
        raise HTTPException(status_code=404, detail="Technicien introuvable")
    if technician.status != "pending":
        raise HTTPException(status_code=400, detail="Ce compte n'est pas en attente de validation")

    db.delete(technician)
    db.commit()


@router.get("/stats", response_model=AdminStatsOut)
def get_admin_stats(
    db: Session = Depends(get_db),
    admin: Technician = Depends(require_admin),
):
    """Vue d'ensemble analytique : chiffres clés, évolution mensuelle, top départements."""
    return {
        "overview": admin_stats.get_overview(db),
        "incidents_by_month": admin_stats.get_incidents_by_month(db),
        "top_departments": admin_stats.get_top_departments(db),
    }
