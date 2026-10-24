"""
Test de bout en bout (J23) — rejoue le parcours utilisateur complet du
projet, de l'inscription jusqu'au chatbot, en une seule fois. Sert de
suite de non-régression : à relancer après toute modification importante
du code pour vérifier que rien de déjà construit ne s'est cassé.

Usage :
    python test_e2e.py

Les étapes nécessitant un vrai accès réseau (recherche vectorielle,
appel Gemini) sont automatiquement ignorées avec un message clair si ce
réseau n'est pas disponible, sans faire échouer le reste de la suite.
"""

import os
import sys
import uuid
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from main import app
from database import SessionLocal, engine, Base
from models import Department
import vector_store

load_dotenv()
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@fgcl.local")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changez_ce_mot_de_passe")

Base.metadata.create_all(bind=engine)

client = TestClient(app)
passed = 0
failed = 0


def check(label, condition):
    global passed, failed
    if condition:
        print(f"✅ {label}")
        passed += 1
    else:
        print(f"❌ {label}")
        failed += 1


def skip(label, reason):
    print(f"⏭️  {label} — IGNORÉ ({reason})")


def run():
    db = SessionLocal()
    dept = db.query(Department).first()
    db.close()
    if dept is None:
        print("Aucun département en base — lance d'abord : python seed_admin.py")
        sys.exit(1)

    print("=== 1. Authentification ===")
    r = client.post("/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    check("Connexion admin", r.status_code == 200)
    if r.status_code != 200:
        print(f"   → Échec avec ADMIN_EMAIL={ADMIN_EMAIL!r}. Vérifie ces valeurs dans ton .env")
        print(f"   → Détail renvoyé par l'API : {r.json()}")
        print(f"\nRésultat : {passed} test(s) réussi(s), {failed} échec(s) — arrêt, le reste dépend de l'admin")
        sys.exit(1)
    admin_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    suffix = uuid.uuid4().hex[:6]
    email_a, email_b = f"alice.{suffix}@fgcl.cm", f"bob.{suffix}@fgcl.cm"

    r = client.post("/auth/register", json={"email": email_a, "password": "motdepasse123", "department_id": dept.id})
    check("Inscription technicien A", r.status_code == 201)
    r = client.post("/auth/register", json={"email": email_b, "password": "motdepasse123", "department_id": dept.id})
    check("Inscription technicien B", r.status_code == 201)

    r = client.post("/auth/login", data={"username": email_a, "password": "motdepasse123"})
    check("Connexion refusée avant validation admin (403)", r.status_code == 403)

    print("\n=== 2. Validation admin ===")
    r = client.get("/admin/pending-technicians", headers=admin_headers)
    pending_emails = [t["email"] for t in r.json()]
    check("Les deux comptes apparaissent en attente", email_a in pending_emails and email_b in pending_emails)
    for t in r.json():
        if t["email"] in (email_a, email_b):
            client.post(f"/admin/technicians/{t['id']}/approve", headers=admin_headers)

    r = client.post("/auth/login", data={"username": email_a, "password": "motdepasse123"})
    check("Connexion technicien A après validation", r.status_code == 200)
    headers_a = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = client.post("/auth/login", data={"username": email_b, "password": "motdepasse123"})
    headers_b = {"Authorization": f"Bearer {r.json()['access_token']}"}

    print("\n=== 3. Cycle incident complet ===")
    original_upsert = vector_store.upsert_incident
    network_available = True
    try:
        r = client.post("/incidents", json={
            "titre": "Test bout en bout - wifi",
            "description": "Description de test",
            "symptomes": "symptome de test",
            "department_id": dept.id,
        }, headers=headers_a)
    except Exception:
        network_available = False
        vector_store.upsert_incident = lambda **kwargs: None
        r = client.post("/incidents", json={
            "titre": "Test bout en bout - wifi",
            "description": "Description de test",
            "symptomes": "symptome de test",
            "department_id": dept.id,
        }, headers=headers_a)

    check("Déclaration d'incident par A", r.status_code == 201)
    incident_id = r.json()["id"]

    r = client.post(f"/incidents/{incident_id}/solutions", json={"contenu": "Redémarrer le routeur"}, headers=headers_b)
    check("B répond à l'incident de A", r.status_code == 201)
    solution_id = r.json()["id"]

    r = client.post(f"/solutions/{solution_id}/star", headers=headers_a)
    check("A étoile la solution de B", r.status_code == 201 and r.json()["stars_count"] == 1)

    print("\n=== 4. Vérifications de non-régression (règles critiques) ===")
    r = client.post(f"/incidents/{incident_id}/close", json={"accepted_solution_id": solution_id}, headers=headers_b)
    check("RÉGRESSION — B ne peut PAS fermer le ticket de A (403)", r.status_code == 403)

    r = client.post(f"/solutions/{solution_id}/star", headers=headers_a)
    check("RÉGRESSION — double vote refusé (409)", r.status_code == 409)

    r = client.post(f"/incidents/{incident_id}/close", json={"accepted_solution_id": solution_id}, headers=headers_a)
    check("A ferme le ticket avec la solution de B", r.status_code == 200 and r.json()["status"] == "ferme")

    r = client.post(f"/incidents/{incident_id}/solutions", json={"contenu": "trop tard"}, headers=headers_b)
    check("RÉGRESSION — réponse refusée sur ticket fermé (400)", r.status_code == 400)

    vector_store.upsert_incident = original_upsert

    print("\n=== 5. Chatbot (nécessite le vrai modèle + Gemini) ===")
    if not network_available:
        skip("Recherche + recommandation du chatbot", "réseau indisponible dans cet environnement")
    else:
        try:
            r = client.post("/chatbot/ask", json={"message": "le wifi ne repond plus"}, headers=headers_a)
            check(f"Chatbot répond (statut {r.status_code})", r.status_code == 200)
        except Exception as e:
            skip("Recherche + recommandation du chatbot", f"{type(e).__name__} : {e}")

    print()
    print(f"Résultat : {passed} test(s) réussi(s), {failed} échec(s)")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run()
