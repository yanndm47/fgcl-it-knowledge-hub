# Validation — Semaine 3 (J15 à J21)
### IT Knowledge Hub — Intelligence : recherche, classement, chatbot

**Objectif de la semaine** : le chatbot devient capable d'analyser une demande, de retrouver les incidents similaires, de classer les solutions, et de formuler une recommandation — tout en assumant honnêtement ses limites (aucune correspondance, échec de Gemini).

---

## 1. Récapitulatif jour par jour

| Jour | Contenu | Statut |
|---|---|---|
| J15 | Pipeline d'embedding incrémental (`vector_store.py`), upsert à la création d'un incident | ✅ Validé (en conditions réelles) |
| J16 | Script de diagnostic `debug_search.py`, seuil de similarité calibrable | ✅ Outil livré |
| J17 | Calcul du score combiné des solutions (`scoring.py`) | ✅ Validé (6 cas limites + scénario complet) |
| J18 | Intégration Gemini (`llm.py`, SDK `google-genai`) | ✅ Validé en conditions réelles |
| J19 | Endpoint chatbot complet (`POST /chatbot/ask`) | ✅ Validé en conditions réelles |
| J20 | Widget frontend (`chatbot.html`) | ✅ Validé en conditions réelles |

## 2. Bugs découverts et corrigés cette semaine (à mentionner en soutenance)

Cette semaine a été la plus riche en corrections réelles du projet — ce qui est normal : c'est la première fois que des composants externes (modèle d'IA, ChromaDB, Gemini) entrent en jeu.

| # | Bug | Cause | Correction |
|---|---|---|---|
| 1 | `google-generativeai` abandonné par Google | Bibliothèque dépréciée, plus de support | Basculé sur le nouveau SDK officiel `google-genai` avant même la première livraison |
| 2 | Conflit de dépendances `pydantic` | `google-genai` exige `pydantic>=2.12.5`, figé à `2.9.2` depuis le J1 | `pydantic` remonté à `2.12.5`, testé sans régression |
| 3 | `GEMINI_API_KEY` jamais trouvée malgré une vraie clé dans `.env` | `llm.py` ne chargeait jamais lui-même le `.env`, dépendait par coïncidence de l'ordre d'import d'un autre fichier | `load_dotenv()` appelé explicitement dans `llm.py` (et `jwt_utils.py` par précaution) |
| 4 | Modèle `gemini-2.0-flash` renvoie une erreur 404 | Modèle retiré par Google | Remplacé par `gemini-3.5-flash-lite`, déjà validé sur le chatbot FGCL |
| 5 | **Le chatbot ne trouvait jamais aucune correspondance, même pour un incident quasi identique** | La collection ChromaDB utilisait la distance euclidienne par défaut, alors que le seuil (0,63) avait été calibré pour une distance cosinus — deux échelles incompatibles, sans qu'aucune erreur ne soit levée | `metadata={"hnsw:space": "cosine"}` ajouté explicitement à la création de la collection ; script `reindex_all.py` créé pour reconstruire l'index existant |
| 6 | `is_accepted` absent de la réponse du chatbot | `scoring.py` calculait cette information en interne mais ne la transmettait jamais dans son résultat | Ajouté au dictionnaire renvoyé par `rank_solutions_for_matches` |

## 3. Tests déjà validés (par Claude et par BY, en conditions réelles)

| # | Scénario | Résultat |
|---|---|---|
| 1 | Appel Gemini avec une vraie clé API, deux fausses solutions | ✅ Réponse cohérente, bien structurée |
| 2 | Pipeline complet avec un vrai incident indexé, une vraie solution, une vraie question proche | ✅ `found_match: true`, bon incident retrouvé, score cohérent, réponse Gemini fidèle aux données |
| 3 | Question sans aucun incident en base | ✅ `found_match: false`, message de proposition de création de ticket |
| 4 | Accès sans authentification | ✅ Rejeté (401) |
| 5 | Message trop court | ✅ Rejeté (422) |
| 6 | Échec simulé de Gemini (clé manquante) | ✅ Erreur 503 propre, pas de plantage |

## 4. Tests restants — À EXÉCUTER PAR BY (nécessitent le vrai modèle + Gemini)

Ces scénarios ne peuvent pas être testés côté Claude (pas d'accès à Hugging Face ni à l'API Gemini depuis mon environnement). Merci de les exécuter et de m'en partager le résultat.

| # | Scénario à tester | Comment faire | Résultat attendu |
|---|---|---|---|
| 7 | Plusieurs solutions concurrentes sur un même incident, une seule étoilée | Déclarer 1 incident, ajouter 2-3 solutions différentes, en étoiler une seule, interroger le chatbot | La solution étoilée doit ressortir en premier (score plus élevé) |
| 8 | Incident "cold start" (aucune étoile posée nulle part) | Déclarer un incident tout neuf avec une seule solution non étoilée, interroger le chatbot dessus | Doit quand même répondre (score plus faible, mais pas de plantage) |
| 9 | Question formulée très différemment de l'incident mais sur le même sujet | Incident "Wifi inaccessible bâtiment A", question "je ne capte plus le réseau sans fil" | Idéalement retrouvé quand même (le modèle est censé capter le sens, pas juste les mots) — sinon, ajuster `SIMILARITY_THRESHOLD` |
| 10 | Question sur un sujet totalement différent d'un incident existant | Incident wifi en base, question "l'imprimante refuse d'imprimer" | `found_match: false`, ne doit PAS renvoyer la solution wifi par erreur |
| 11 | Incident fermé avec solution documentée par l'ouvreur lui-même (`own_solution_content`) | Fermer un ticket en documentant sa propre solution, puis interroger le chatbot sur un cas similaire | La solution doit apparaître avec `is_accepted: true` |
| 12 | Filtrage insensible au département | Deux incidents similaires dans des départements différents | Le chatbot doit proposer les deux, sans se limiter au département du technicien qui pose la question |

## 5. État du dépôt Git

```
Refonte complete du frontend selon la charte graphique fournie
J20 - Widget chatbot frontend (chatbot.html)
Correction critique J19 : distance cosinus explicite sur ChromaDB
J19 - Endpoint chatbot complet (POST /chatbot/ask)
Correction : modele Gemini par defaut (gemini-3.5-flash-lite)
Correction : llm.py et jwt_utils.py chargent le .env eux-memes
Correction conflit de dependances pydantic
J18 - Integration Gemini (llm.py, SDK google-genai)
J17 - Calcul du score combine des solutions
J16 - Script de diagnostic (debug_search.py)
J15 - Pipeline d'embedding incremental
```

## 6. Checklist de fin de semaine

- [x] Pipeline complet recherche → classement → génération fonctionnel en conditions réelles
- [x] Tous les bugs rencontrés documentés avec leur cause réelle (pas juste "corrigé")
- [x] Interface de chat utilisable, avec suggestions et affichage des solutions sources
- [ ] Scénarios 7 à 12 à exécuter par BY et à valider

## 7. Prochaine étape — Semaine 4

Consolidation : sécurisation, tests de bout en bout, optimisations, rédaction du rapport de projet, préparation de la soutenance (slides, simulation de questions jury).
