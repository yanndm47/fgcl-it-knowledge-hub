"""
IT Knowledge Hub — point d'entrée FastAPI.

Squelette du Jour 3 : l'application démarre et répond, mais ne contient
encore aucune route métier. Les routeurs seront ajoutés progressivement :

- J5-J7  : routers/auth.py        (inscription, connexion, validation admin)
- J8-J10 : routers/incidents.py   (déclaration, consultation, fermeture)
- J9,J11 : routers/solutions.py   (proposition de solutions, étoiles)
- J19    : routers/chatbot.py     (analyse, recherche, classement, recommandation)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, admin, incidents, solutions, departments, chatbot, notifications_router

app = FastAPI(
    title="IT Knowledge Hub",
    description="Plateforme collaborative de capitalisation et de résolution des incidents IT",
    version="0.1.0",
)

# À restreindre à l'origine réelle du frontend avant tout déploiement (cf. cahier des charges, section 6)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
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
