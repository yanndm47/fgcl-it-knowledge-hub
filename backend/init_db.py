"""
Script d'initialisation de la base de données.

Crée physiquement les tables définies dans models.py, si elles n'existent
pas déjà. À exécuter une seule fois au démarrage du projet, ou après
suppression du fichier knowledge_hub.db pour repartir de zéro.

Usage :
    python init_db.py
"""

from database import engine, Base
import models  # noqa: F401 -- import nécessaire pour que Base "connaisse" toutes les classes ci-dessus

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée : toutes les tables ont été créées avec succès.")
