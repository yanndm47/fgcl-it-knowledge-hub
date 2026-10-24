"""
Routes d'authentification.

J5 : inscription uniquement (POST /register).
J6 ajoutera la connexion (POST /login) et la génération de jetons JWT.
J7 ajoutera la validation des comptes en attente par un administrateur.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import Technician, Department
from schemas import (
    TechnicianCreate, TechnicianOut, TechnicianUpdate, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest, ActivityOut,
)
from security import hash_password, verify_password
from jwt_utils import create_access_token, create_reset_token, decode_reset_token
from dependencies import get_current_technician
import activity

router = APIRouter()


@router.post("/register", response_model=TechnicianOut, status_code=status.HTTP_201_CREATED)
def register(payload: TechnicianCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un technicien.

    Le compte est créé avec le statut 'pending' : la connexion (J6) lui sera
    refusée tant qu'un administrateur ne l'aura pas validé (J7). C'est la
    mise en œuvre concrète de la consigne "pas d'open space" de l'encadreur.
    """
    department = db.get(Department, payload.department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="Département introuvable")

    existing = db.query(Technician).filter(Technician.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cet email")

    technician = Technician(
        email=payload.email,
        password_hash=hash_password(payload.password),
        department_id=payload.department_id,
        status="pending",
        role="technicien",
    )
    db.add(technician)
    try:
        db.commit()
    except IntegrityError:
        # Filet de sécurité si deux inscriptions arrivent en même temps avec le même email
        db.rollback()
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cet email")

    db.refresh(technician)
    return technician


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Connexion d'un technicien. Utilise le formulaire standard OAuth2
    (champ 'username' = email, champ 'password') pour rester compatible
    avec le bouton "Authorize" de la documentation interactive (/docs).
    """
    technician = db.query(Technician).filter(Technician.email == form_data.username).first()

    # Message volontairement identique dans les deux cas (email inconnu OU mot de passe faux)
    # pour ne pas révéler à un attaquant si un email existe déjà dans la base.
    if technician is None or not verify_password(form_data.password, technician.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    if technician.status != "actif":
        raise HTTPException(
            status_code=403,
            detail="Compte en attente de validation par un administrateur",
        )

    token = create_access_token({"sub": technician.id, "role": technician.role})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=TechnicianOut)
def read_current_technician(current: Technician = Depends(get_current_technician)):
    """Renvoie les informations du technicien actuellement connecté (à partir de son jeton)."""
    return current


@router.patch("/me", response_model=TechnicianOut)
def update_my_profile(
    payload: TechnicianUpdate,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """
    Met à jour les champs de profil du technicien connecté (nom complet,
    site, téléphone). Un champ non fourni dans la requête reste inchangé
    (exclude_unset=True) — envoyer {} ne réinitialise rien.
    """
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(current, field, value)
    db.commit()
    db.refresh(current)
    return current


@router.get("/me/activity", response_model=ActivityOut)
def my_activity(
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """Statistiques et fil d'activité du technicien connecté (page Historique)."""
    stats = activity.get_technician_stats(db, current.id)
    feed = activity.get_technician_activity_feed(db, current.id)
    return {"stats": stats, "feed": feed}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Demande un lien de réinitialisation de mot de passe.

    Réponse volontairement IDENTIQUE que l'email existe ou non en base,
    pour ne jamais révéler à un attaquant quels emails sont enregistrés
    (même principe que sur /auth/login).

    Pas de serveur d'envoi d'email réel dans ce projet académique : le
    lien est affiché dans la console du serveur, comme un "faux email"
    consultable localement. En production, cette fonction enverrait un
    vrai email au lieu d'un print().
    """
    technician = db.query(Technician).filter(Technician.email == payload.email).first()
    if technician is not None:
        reset_token = create_reset_token(technician.id)
        reset_link = f"http://127.0.0.1:5500/reset-password.html?token={reset_token}"
        print("\n" + "=" * 70)
        print(f"[SIMULATION D'EMAIL] Réinitialisation de mot de passe pour {technician.email}")
        print(f"Lien (valable 15 minutes) : {reset_link}")
        print("=" * 70 + "\n")

    return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Vérifie le jeton de réinitialisation et applique le nouveau mot de passe."""
    technician_id = decode_reset_token(payload.token)
    if technician_id is None:
        raise HTTPException(status_code=400, detail="Lien de réinitialisation invalide ou expiré")

    technician = db.get(Technician, technician_id)
    if technician is None:
        raise HTTPException(status_code=400, detail="Lien de réinitialisation invalide ou expiré")

    technician.password_hash = hash_password(payload.new_password)
    db.commit()

    return {"message": "Mot de passe mis à jour avec succès."}
