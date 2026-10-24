"""
Script de préparation d'un jeu de données de démonstration (J29).

Objectif : ne JAMAIS improviser la création de comptes/incidents en
direct devant le jury (trop risqué : fautes de frappe, oublis, lenteur).
Ce script prépare en une fois une situation de démo cohérente et
reproductible, avec des identifiants notés clairement à la fin.

Usage :
    python seed_demo_data.py

À exécuter APRÈS init_db.py et seed_admin.py, sur une base fraîchement
réinitialisée (rm knowledge_hub.db avant, comme d'habitude).
"""

from database import SessionLocal, engine, Base
from models import Department, Technician, Incident, Solution, Star
from security import hash_password
import vector_store

Base.metadata.create_all(bind=engine)

DEMO_PASSWORD = "Demo2026!"


def run():
    db = SessionLocal()
    departments = db.query(Department).all()
    if not departments:
        print("Aucun département en base — lance d'abord : python seed_admin.py")
        return
    dept_a, dept_b = departments[0], departments[-1]

    # --- Comptes de démonstration, déjà validés (pas besoin de refaire le
    #     cycle d'inscription/validation en direct) ---
    demo_technicians = [
        ("alice.demo@fgcl.cm", dept_a),
        ("bob.demo@fgcl.cm", dept_a),
        ("chloe.demo@fgcl.cm", dept_b),
    ]
    created_technicians = {}
    for email, dept in demo_technicians:
        existing = db.query(Technician).filter(Technician.email == email).first()
        if existing:
            created_technicians[email] = existing
            continue
        tech = Technician(
            email=email,
            password_hash=hash_password(DEMO_PASSWORD),
            department_id=dept.id,
            status="actif",
            role="technicien",
        )
        db.add(tech)
        db.flush()
        created_technicians[email] = tech
    db.commit()

    alice = created_technicians["alice.demo@fgcl.cm"]
    bob = created_technicians["bob.demo@fgcl.cm"]
    chloe = created_technicians["chloe.demo@fgcl.cm"]

    def index_safely(incident):
        try:
            vector_store.upsert_incident(
                incident_id=incident.id, titre=incident.titre, symptomes=incident.symptomes,
                contexte=incident.contexte, department_id=incident.department_id,
            )
        except Exception as e:
            print(f"  ⚠️  Indexation vectorielle ignorée pour '{incident.titre}' ({type(e).__name__})")

    # --- Incident 1 : DÉJÀ FERMÉ, avec solution retenue + étoiles ---
    # Sert à montrer : historique résolu, badge "solution retenue", étoiles.
    inc1 = Incident(
        titre="Wifi inaccessible au 2e étage",
        description="Plus aucun appareil ne se connecte au wifi du bureau depuis ce matin.",
        symptomes="le wifi est visible mais impossible de se connecter, erreur de mot de passe incorrect",
        contexte="Redémarrage du poste déjà tenté sans succès",
        department_id=dept_a.id, opened_by=alice.id, status="ouvert",
    )
    db.add(inc1); db.commit(); db.refresh(inc1)
    index_safely(inc1)

    sol1 = Solution(incident_id=inc1.id, author_id=bob.id, contenu="Redémarrer le routeur et attendre 30 secondes avant de le rebrancher.")
    db.add(sol1); db.commit(); db.refresh(sol1)
    db.add(Star(solution_id=sol1.id, voter_id=alice.id))
    db.add(Star(solution_id=sol1.id, voter_id=chloe.id))
    db.commit()

    inc1.accepted_solution_id = sol1.id
    inc1.status = "ferme"
    db.commit()

    # --- Incident 2 : OUVERT, deux solutions concurrentes (une étoilée) ---
    # Sert à montrer : plusieurs réponses, classement par pertinence côté chatbot.
    inc2 = Incident(
        titre="Imprimante RH bloquée en bourrage papier",
        description="L'imprimante du service RH affiche un bourrage papier en continu.",
        symptomes="voyant orange clignotant, message 'bourrage papier' persistant même après ouverture du capot",
        contexte=None,
        department_id=dept_b.id, opened_by=chloe.id, status="ouvert",
    )
    db.add(inc2); db.commit(); db.refresh(inc2)
    index_safely(inc2)

    sol2a = Solution(incident_id=inc2.id, author_id=alice.id, contenu="Retirer le bac papier, vérifier qu'aucun morceau de papier ne reste coincé au fond.")
    sol2b = Solution(incident_id=inc2.id, author_id=bob.id, contenu="Nettoyer les rouleaux d'entraînement avec un chiffon légèrement humide.")
    db.add_all([sol2a, sol2b]); db.commit(); db.refresh(sol2a); db.refresh(sol2b)
    db.add(Star(solution_id=sol2a.id, voter_id=chloe.id))
    db.commit()

    # --- Incident 3 : tout frais, SANS solution ---
    # Sert à démontrer en direct : proposer une réponse, étoiler, fermer.
    inc3 = Incident(
        titre="Lenteur anormale de l'application métier",
        description="L'application interne met plus de 10 secondes à charger chaque page depuis hier.",
        symptomes="chargement très lent, parfois timeout, uniquement sur le réseau du bureau",
        contexte=None,
        department_id=dept_a.id, opened_by=bob.id, status="ouvert",
    )
    db.add(inc3); db.commit(); db.refresh(inc3)
    index_safely(inc3)

    # On capture les infos utiles AVANT de fermer la session : une fois
    # fermée, SQLAlchemy ne peut plus recharger les attributs des objets
    # (DetachedInstanceError) — piège classique, corrigé ici.
    titre_inc1, titre_inc2, titre_inc3 = inc1.titre, inc2.titre, inc3.titre

    db.close()

    print("\n=== Jeu de données de démonstration prêt ===\n")
    print("Comptes techniciens (déjà validés, mot de passe identique) :")
    for email, _ in demo_technicians:
        print(f"  - {email} / {DEMO_PASSWORD}")
    print("\nIncidents créés :")
    print(f"  - [FERMÉ]  {titre_inc1}  (solution retenue + 2 étoiles)")
    print(f"  - [OUVERT] {titre_inc2}  (2 solutions concurrentes, 1 étoilée)")
    print(f"  - [OUVERT] {titre_inc3}  (aucune solution — à utiliser pour la démo live)")
    print("\nSuggestion de question à poser au chatbot pendant la démo :")
    print('  "le wifi ne repond plus" → doit retrouver l\'incident 1 et sa solution retenue')


if __name__ == "__main__":
    run()
