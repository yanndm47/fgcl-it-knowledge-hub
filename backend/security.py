"""
Fonctions de hachage et de vérification des mots de passe.

Utilise la bibliothèque bcrypt directement, plutôt que passlib : passlib 1.7.4
est incompatible avec les versions récentes de bcrypt (>=4.1), qui ont supprimé
un attribut interne que passlib utilisait pour se configurer. bcrypt seul fait
exactement le même travail, sans cette couche intermédiaire fragile.
"""

import bcrypt


def hash_password(password: str) -> str:
    """Transforme un mot de passe en clair en un hash bcrypt (irréversible)."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond bien à un hash déjà stocké."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
