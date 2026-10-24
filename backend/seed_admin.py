"""
Script de seed — crée les départements de référence et l'unique compte
administrateur du système.

Contrairement au chatbot FGCL (où 12 comptes techniciens étaient pré-créés),
aucun compte technicien n'est créé ici : chaque technicien s'inscrit
lui-même via POST /auth/register (J5), puis attend la validation d'un
administrateur (J7). Seul le compte admin, nécessaire pour effectuer cette
validation, est pré-créé.

Usage :
    python seed_admin.py

Personnalisation (optionnel) : définir ADMIN_EMAIL et ADMIN_PASSWORD dans
le fichier .env avant de lancer ce script, sinon des valeurs par défaut
sont utilisées (à changer immédiatement après la première connexion).
"""

import os
from dotenv import load_dotenv

from database import SessionLocal, engine, Base
from models import Department, Technician
from security import hash_password

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@fgcl.local")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changez_ce_mot_de_passe")

DEPARTMENTS = ["Digitalisation", "Infra/Réseau"]


def run():
    Base.metadata.create_all(bind=engine)  # filet de sécurité si init_db.py n'a pas encore été lancé
    db = SessionLocal()

    for nom in DEPARTMENTS:
        if db.query(Department).filter(Department.nom == nom).first() is None:
            db.add(Department(nom=nom))
    db.commit()
    print(f"Départements en place : {[d.nom for d in db.query(Department).all()]}")

    admin_existant = db.query(Technician).filter(Technician.role == "admin").first()
    if admin_existant:
        print(f"Un compte admin existe déjà ({admin_existant.email}) — aucune action nécessaire.")
        db.close()
        return

    premier_departement = db.query(Department).first()
    admin = Technician(
        email=ADMIN_EMAIL,
        password_hash=hash_password(ADMIN_PASSWORD),
        department_id=premier_departement.id,
        status="actif",
        role="admin",
    )
    db.add(admin)
    db.commit()
    print(f"Compte admin créé : {ADMIN_EMAIL} / mot de passe : {ADMIN_PASSWORD}")
    print("⚠️  Pense à changer ce mot de passe (fonctionnalité à ajouter plus tard).")
    db.close()


if __name__ == "__main__":
    run()
