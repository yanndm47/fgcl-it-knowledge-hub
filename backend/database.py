"""
Connexion à la base de données et gestion des sessions SQLAlchemy.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()  # lit le fichier .env s'il existe déjà ; ne fait rien sinon (pas bloquant au J4)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./knowledge_hub.db")

# check_same_thread=False est nécessaire uniquement pour SQLite utilisé avec FastAPI
# (FastAPI peut accéder à la base depuis un thread différent de celui qui l'a ouverte)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe de base dont hériteront tous les modèles (Department, Technician, Incident, Solution, Star)."""
    pass


def get_db():
    """
    Fournit une session de base de données à une route FastAPI, et la referme
    automatiquement une fois la requête terminée (même en cas d'erreur en cours de route).
    Sera utilisée à partir du J5 dans les routers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
