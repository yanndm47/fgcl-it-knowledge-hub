"""
Script de reconstruction complète de la base vectorielle à partir des
incidents déjà présents dans la base SQLite.

À utiliser :
- après suppression du dossier chroma_db/ (perte de l'index) ;
- après un changement de configuration de la collection (comme le
  passage à la distance cosinus, corrigé au J19) ;
- après un changement de modèle d'embedding.

Différence avec le pipeline normal (J15) : celui-ci indexe un incident
à la fois, à sa création. Celui-ci reconstruit TOUT en une fois, à
utiliser ponctuellement, pas à chaque changement.

Usage :
    python reindex_all.py
"""

from database import SessionLocal
from models import Incident
import vector_store


def run():
    db = SessionLocal()
    incidents = db.query(Incident).all()
    print(f"{len(incidents)} incident(s) à réindexer...")

    for i, incident in enumerate(incidents, 1):
        vector_store.upsert_incident(
            incident_id=incident.id,
            titre=incident.titre,
            symptomes=incident.symptomes,
            contexte=incident.contexte,
            department_id=incident.department_id,
        )
        print(f"  [{i}/{len(incidents)}] {incident.titre}")

    db.close()
    print("Réindexation terminée.")


if __name__ == "__main__":
    run()
