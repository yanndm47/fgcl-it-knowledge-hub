# Procédure de test global pré-soutenance

18 étapes, dans l'ordre, pour vérifier l'application de bout en bout avant la soutenance.

## Partie 1 — Réinitialisation et tests automatiques (CMD, dossier backend, venv actif)

1. `del knowledge_hub.db` puis `rmdir /s /q chroma_db` (ignorer les erreurs "n'existe pas")
2. `python init_db.py`
3. `python seed_admin.py`
4. `python seed_demo_data.py` — noter les 3 comptes et 3 incidents affichés
5. `python test_e2e.py` — DOIT afficher 14 test(s) réussi(s), 0 échec(s)

## Partie 2 — Lancement des serveurs

6. Backend : `uvicorn main:app --reload` (garder la fenêtre ouverte)
7. Frontend (nouvelle fenêtre CMD) : `cd frontend` puis `python -m http.server 5500`

## Partie 3 — Vérifications manuelles dans le navigateur

8. Inscrire un compte neuf (`register.html`) → tenter de se connecter → doit être refusé (pending)
9. Se connecter en admin → approuver ce nouveau compte
10. Se reconnecter avec ce compte → doit fonctionner
11. Se connecter avec `alice.demo@fgcl.cm` / `Demo2026!` → vérifier les statistiques du tableau de bord
12. Ouvrir l'incident fermé → vérifier badge "solution retenue" + étoiles
13. Ouvrir l'incident à solutions concurrentes → vérifier l'affichage des deux réponses
14. **Fenêtre de navigation privée** avec `bob.demo@fgcl.cm` → vérifier que la section de fermeture n'apparaît PAS sur un ticket qui n'est pas le sien
15. Cycle complet en direct sur le 3ᵉ incident (répondre → étoiler → fermer)
16. Tester le chatbot avec une question pertinente (doit trouver l'incident 1)
17. Tester le chatbot avec une question hors sujet (doit dire "aucune correspondance", ne rien inventer)
18. Réduire la largeur du navigateur → vérifier le bouton ☰ et l'ouverture du menu mobile

## Partie 4 — Ne rien casser après un test réussi

Si tout fonctionne, laisser les fenêtres ouvertes et le navigateur connecté sur `alice.demo` — c'est l'état de départ recommandé pour la soutenance (voir `Checklist_Jour_Soutenance.md`, Partie B).
