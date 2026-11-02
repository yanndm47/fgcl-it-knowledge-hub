"""
IT Knowledge Hub — point d'entrée FastAPI.

Squelette du Jour 3 : l'application démarre et répond, mais ne contient
encore aucune route métier. Les routeurs seront ajoutés progressivement :

- J5-J7  : routers/auth.py        (inscription, connexion, validation admin)
- J8-J10 : routers/incidents.py   (déclaration, consultation, fermeture)
- J9,J11 : routers/solutions.py   (proposition de solutions, étoiles)
- J19    : routers/chatbot.py     (analyse, recherche, classement, recommandation)
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, admin, incidents, solutions, departments, chatbot, notifications_router

load_dotenv()

app = FastAPI(
    title="IT Knowledge Hub",
    description="Plateforme collaborative de capitalisation et de résolution des incidents IT",
    version="0.1.0",
)

# Origines autorisées : toujours le frontend local (développement), plus
# l'origine réelle du frontend déployé (ex. GitHub Pages), lue depuis la
# variable d'environnement FRONTEND_URL définie sur l'hébergeur en ligne —
# jamais codée en dur, pour ne pas avoir à republier le code à chaque
# changement d'adresse.
_allowed_origins = ["http://127.0.0.1:5500", "http://localhost:5500"]
_deployed_frontend = os.getenv("FRONTEND_URL")
if _deployed_frontend:
    _allowed_origins.append(_deployed_frontend)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Vérification simple que l'API répond — utile pour le développement local et le déploiement."""
    return {"status": "ok", "service": "it-knowledge-hub"}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
app.include_router(solutions.router, tags=["solutions"])
app.include_router(departments.router, prefix="/departments", tags=["departments"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
app.include_router(notifications_router.router, prefix="/notifications", tags=["notifications"])
