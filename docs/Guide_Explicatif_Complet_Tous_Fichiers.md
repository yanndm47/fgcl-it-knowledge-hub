# Guide explicatif complet — tous les fichiers du projet
### IT Knowledge Hub — pour pouvoir expliquer n'importe quelle pièce du système

**Comment utiliser ce document** : chaque fichier est présenté avec deux informations : **à quoi il sert** (le rôle) et **comment il fonctionne** (le mécanisme, en une ou deux phrases). C'est le document à relire juste avant la soutenance pour n'être jamais pris au dépourvu sur un fichier précis.

---

## 1. Fichiers à la racine du projet

| Fichier | À quoi il sert | Comment il fonctionne |
|---|---|---|
| `.env` | Contient les vraies valeurs secrètes (clé Gemini, clé JWT, identifiants admin) | Jamais versionné dans Git ; lu automatiquement par `python-dotenv` au démarrage de plusieurs fichiers backend |
| `.env.example` | Modèle du `.env`, sans vraies valeurs | Sert de documentation : montre quelles variables créer, sans révéler de secret |
| `.gitignore` | Liste les fichiers que Git ne doit jamais suivre | Exclut `venv/`, `.env`, les bases de données (`*.db`), `chroma_db/`, les caches Python |
| `requirements.txt` | Liste exacte des bibliothèques Python et leur version | Lu par `pip install -r requirements.txt` pour recréer un environnement identique |
| `README.md` | Mode d'emploi général du projet | Explique l'architecture, l'installation, le lancement |

## 2. Backend — fichiers centraux

| Fichier | À quoi il sert | Comment il fonctionne |
|---|---|---|
| `main.py` | Point d'entrée de l'application | Crée l'objet FastAPI, configure CORS, branche tous les routers (`auth`, `admin`, `incidents`, `solutions`, `departments`, `chatbot`) |
| `database.py` | Connexion à la base de données | Crée le moteur SQLAlchemy pointant vers `knowledge_hub.db`, fournit `get_db()` (une session par requête, fermée automatiquement) |
| `models.py` | Traduction des 5 tables en classes Python | `Department`, `Technician`, `Incident`, `Solution`, `Star` — chacune hérite de `Base` ; contient la contrainte unique `(solution_id, voter_id)` sur `Star` |
| `schemas.py` | Forme exacte des données reçues/renvoyées par l'API | Classes Pydantic (`TechnicianCreate`, `IncidentOut`, `ChatbotResponse`, etc.) — valident automatiquement les requêtes et filtrent les réponses (ex. `password_hash` n'est jamais renvoyé) |
| `security.py` | Hachage des mots de passe | Deux fonctions : `hash_password()` (bcrypt) et `verify_password()` — remplace `passlib`, incompatible avec les versions récentes de bcrypt |
| `jwt_utils.py` | Création et vérification des jetons de connexion | `create_access_token()` signe un jeton valable 24h ; `decode_access_token()` le vérifie ; charge lui-même le `.env` |
| `dependencies.py` | Fonctions de garde réutilisables | `get_current_technician()` lit le jeton et retrouve le technicien ; `require_admin()` ajoute la vérification du rôle |
| `vector_store.py` | Moteur de recherche par similarité | Encode les incidents avec `sentence-transformers`, les stocke dans ChromaDB (distance cosinus), calcule les doublons potentiels ; chargement paresseux du modèle |
| `scoring.py` | Calcul du score combiné des solutions | `compute_solution_score()` (formule pure) et `rank_solutions_for_matches()` (assemble les vraies données de la base) |
| `llm.py` | Intégration Gemini | `build_prompt()` assemble la question et les solutions classées ; `generate_recommendation()` appelle Gemini (SDK `google-genai`) |

## 3. Backend — routes de l'API (`routers/`)

| Fichier | À quoi il sert | Endpoints principaux |
|---|---|---|
| `auth.py` | Inscription et connexion | `POST /auth/register` (statut `pending`), `POST /auth/login` (refuse si non validé), `GET /auth/me` |
| `admin.py` | Validation des comptes | `GET /admin/pending-technicians`, `POST .../approve`, `DELETE .../reject` — protégés par `require_admin` |
| `incidents.py` | Cycle de vie d'un incident | `POST /incidents` (déclaration, détection de doublons), `GET /incidents` (liste filtrable), `POST /incidents/{id}/close` (règle de propriété du ticket) |
| `solutions.py` | Réponses et étoiles | `POST /incidents/{id}/solutions`, `POST /solutions/{id}/star` (anti auto-vote, anti double-vote) |
| `departments.py` | Liste des départements | `GET /departments` — seule route publique utile aux formulaires avant connexion |
| `chatbot.py` | Assemblage complet de l'intelligence | `POST /chatbot/ask` : recherche → filtre de seuil → classement → génération Gemini |

## 4. Backend — scripts utilitaires (lancés à la main, jamais par l'API)

| Fichier | À quoi il sert | Quand l'utiliser |
|---|---|---|
| `init_db.py` | Crée les tables dans la base | Une fois au départ, ou après avoir supprimé `knowledge_hub.db` |
| `seed_admin.py` | Crée les départements et le compte admin | Juste après `init_db.py` |
| `seed_demo_data.py` | Prépare un jeu de données de démonstration cohérent | Avant une démo (3 comptes, 3 incidents dans des états différents) |
| `reindex_all.py` | Reconstruit tout l'index vectoriel depuis la base SQL | Après suppression de `chroma_db/`, ou changement de configuration de la recherche |
| `debug_search.py` | Diagnostique la recherche par similarité en ligne de commande | Pour calibrer `SIMILARITY_THRESHOLD` avec de vraies données |
| `debug_llm.py` | Teste l'appel à Gemini isolément | Pour vérifier que la clé API fonctionne, sans passer par tout le pipeline |
| `test_e2e.py` | Suite de non-régression complète | À relancer après toute modification importante du code |

## 5. Frontend

| Fichier | À quoi il sert | Comment il fonctionne |
|---|---|---|
| `style.css` | Tout le design visuel | Variables de couleurs reprises de la charte FGCL, mise en page sidebar + contenu, composants (cartes, pastilles, boutons) |
| `api.js` | Fonctions partagées par toutes les pages | `apiFetch()` (appel générique avec jeton automatique), `renderSidebar()`/`renderTopheader()` (construction de la navigation), gestion du menu mobile |
| `index.html` | Aiguillage automatique | Redirige vers `login.html` ou `dashboard.html`/`admin-dashboard.html` selon la connexion et le rôle |
| `login.html` | Connexion | Formulaire email/mot de passe, appelle `POST /auth/login`, redirige selon le rôle |
| `register.html` | Inscription | Formulaire avec sélection du département, appelle `POST /auth/register` |
| `forgot-password.html` | Mot de passe oublié | Page visuelle fidèle à la maquette ; **non fonctionnelle** (aucun backend de réinitialisation construit), le dit explicitement |
| `dashboard.html` | Tableau de bord technicien | Statistiques calculées à partir des vrais incidents, liste filtrable, lien vers la déclaration |
| `incident-new.html` | Déclaration d'un incident | Formulaire (titre, symptômes, description, contexte, département) |
| `incident-detail.html` | Détail d'un incident | Affichage, liste des solutions, bouton étoiler, formulaire de réponse, section de fermeture visible **seulement pour l'ouvreur** |
| `admin-dashboard.html` | Espace admin | Liste des comptes en attente avec boutons Approuver/Rejeter ; redirige les non-admins |
| `chatbot.html` | Assistant IA | Interface de chat, suggestions rapides, appelle `POST /chatbot/ask`, affiche les solutions sources |
| `assets/logo.png` | Le vrai logo FGCL | Utilisé sur toutes les pages (sidebar et pages de connexion) |

## 6. Comment tout s'articule (résumé du flux complet)

1. **Un visiteur s'inscrit** (`register.html` → `auth.py`) → compte `pending`.
2. **Un admin valide** (`admin-dashboard.html` → `admin.py`) → compte `actif`.
3. **Le technicien se connecte** (`login.html` → `auth.py` → `jwt_utils.py`) → reçoit un jeton.
4. **Il déclare un incident** (`incident-new.html` → `incidents.py` → `vector_store.py` pour l'indexation).
5. **Un collègue répond** (`incident-detail.html` → `solutions.py`).
6. **Des techniciens étoilent** (`solutions.py`, contrainte posée dans `models.py`).
7. **L'ouvreur ferme le ticket** (`incidents.py`, vérification stricte de propriété).
8. **N'importe qui interroge l'assistant** (`chatbot.html` → `chatbot.py` → `vector_store.py` + `scoring.py` + `llm.py`) → réponse formulée par Gemini à partir des vraies solutions déjà classées.

## 7. Documents produits (dossier `docs/`)

- `Cahier_des_charges_IT_Knowledge_Hub.docx` — spécifications complètes
- `J2_Modelisation_Base_Donnees.md` — schéma détaillé
- `Document_Cadre_Recapitulatif_J1-J14.md` — explications pédagogiques des 14 premiers jours
- `Validation_Semaine_1/2/3_...` — batteries de tests par semaine
- `Rapport_Projet_IT_Knowledge_Hub.docx` — rapport final complet
- `Soutenance_IT_Knowledge_Hub.pptx` — les 12 slides
- `Guide_Soutenance_Questions_Jury.md` — questions pièges et réponses
- `Checklist_Jour_Soutenance.md` — procédure du jour J
