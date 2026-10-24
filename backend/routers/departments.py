"""
Route de consultation des départements.

Volontairement PUBLIQUE (pas de vérification de jeton) : le formulaire
d'inscription en a besoin AVANT que la personne ait un compte, donc avant
qu'elle puisse s'authentifier.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Department
from schemas import DepartmentOut

router = APIRouter()


@router.get("", response_model=list[DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    """Liste tous les départements — utilisé pour peupler les menus déroulants du frontend."""
    return db.query(Department).order_by(Department.nom).all()
