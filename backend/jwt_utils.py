"""
Génération et vérification des jetons JWT (JSON Web Token).

Principe en une phrase : après une connexion réussie, le serveur remet au
technicien un jeton signé numériquement. À chaque requête suivante, le
technicien renvoie ce jeton ; le serveur vérifie sa signature (sans avoir
besoin de re-consulter la base pour un mot de passe) pour savoir qui fait
la demande.
"""

import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import jwt, JWTError

load_dotenv()  # chargé explicitement ici aussi (même correctif défensif que
               # llm.py), pour que ce module fonctionne même importé seul,
               # sans dépendre de ce qu'un autre fichier a déjà chargé avant.

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))

if not SECRET_KEY:
    # Filet de secours pour que le projet tourne même sans .env créé, MAIS
    # cette clé par défaut est publique (visible dans ce fichier) : elle ne
    # doit jamais être utilisée telle quelle en dehors du développement local.
    SECRET_KEY = "dev-secret-key-A-CHANGER-absolument-avant-toute-mise-en-ligne"
    print("⚠️  JWT_SECRET_KEY absente du .env : utilisation d'une clé de développement non sécurisée.")


def create_access_token(data: dict) -> str:
    """Crée un jeton signé, valable EXPIRATION_MINUTES minutes, contenant les données passées."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Vérifie la signature et l'expiration d'un jeton ; renvoie son contenu si valide, None sinon."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


RESET_TOKEN_MINUTES = 15


def create_reset_token(technician_id: str) -> str:
    """
    Jeton dédié à la réinitialisation de mot de passe : durée de vie très
    courte (15 min), et un champ 'purpose' distinct des jetons de connexion
    normaux, pour qu'un jeton de réinitialisation volé ne puisse jamais
    servir à se connecter, et inversement.
    """
    to_encode = {"sub": technician_id, "purpose": "password_reset"}
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_reset_token(token: str) -> str | None:
    """Vérifie un jeton de réinitialisation et renvoie l'id du technicien s'il est valide, sinon None."""
    payload = decode_access_token(token)
    if payload is None or payload.get("purpose") != "password_reset":
        return None
    return payload.get("sub")
