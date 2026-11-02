#!/bin/bash
# Script de démarrage pour l'hébergement en ligne (Render).
#
# Pourquoi réinitialiser la base à CHAQUE démarrage, et pas une seule fois :
# sur le plan gratuit de Render, le disque local est remis à zéro à chaque
# fois que le service redémarre OU se réveille après une mise en veille
# (qui survient après ~15 minutes sans visite). Sans ce script, le service
# démarrerait avec une base vide et aucun département -> toute inscription
# échouerait immédiatement.
#
# Comportement assumé : chaque réveil repart sur un jeu de données de démo
# fraîches (comptes + incidents), pas sur un historique persistant — adapté
# à une démonstration publique, pas à un usage réel en production.

set -e  # arrête le script immédiatement si une commande échoue

echo "=== Initialisation de la base de données ==="
python init_db.py
python seed_admin.py
python seed_demo_data.py

echo "=== Démarrage du serveur ==="
uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
