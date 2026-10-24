"""
Dépendances FastAPI réutilisables — notamment la récupération du
technicien actuellement connecté à partir de son jeton JWT.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import Technician
from jwt_utils import decode_access_token

# tokenUrl indique à la documentation interactive (/docs) où envoyer email/mot
# de passe pour obtenir un jeton — il ne redirige rien automatiquement.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_technician(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Technician:
    """
    Extrait le technicien correspondant au jeton fourni dans l'en-tête
    Authorization: Bearer <token> de la requête. Lève une erreur 401 si le
    jeton est absent, invalide, expiré, ou ne correspond à aucun compte.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_error

    technician_id = payload.get("sub")
    if technician_id is None:
        raise credentials_error

    technician = db.get(Technician, technician_id)
    if technician is None:
        raise credentials_error

    return technician


def require_admin(current: Technician = Depends(get_current_technician)) -> Technician:
    """
    Comme get_current_technician, mais exige en plus que le compte ait le
    rôle 'admin'. À utiliser sur toutes les routes réservées à l'administration.
    """
    if current.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette action est réservée aux administrateurs",
        )
    return current
