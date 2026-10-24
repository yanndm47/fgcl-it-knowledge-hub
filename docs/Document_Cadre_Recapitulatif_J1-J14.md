# Document cadre — IT Knowledge Hub
### Récapitulatif complet, pédagogique et détaillé (J1 à J14)

**À qui s'adresse ce document** : à toi, en supposant que tu n'as aucune base préalable. Chaque concept technique est expliqué la première fois qu'il apparaît. Tu peux t'en servir comme document de référence unique pour comprendre tout ce qui a été construit, pourquoi, et comment — y compris les erreurs rencontrées en cours de route et comment elles ont été corrigées.

---

## Table des matières

1. Vue d'ensemble du projet
2. Concepts de base, pour débutant complet
3. Architecture générale du projet
4. Semaine 1 en détail (J1 à J7) — fondations et authentification
5. Semaine 2 en détail (J8 à J14) — cœur métier et frontend
6. Récapitulatif de toutes les erreurs rencontrées et corrigées
7. État actuel du dépôt Git
8. Glossaire des termes techniques
9. Prochaine étape (Semaine 3)

---

## 1. Vue d'ensemble du projet

**IT Knowledge Hub** est une plateforme collaborative pour les techniciens support IT de FGCL. Elle permet de :
- déclarer un incident informatique rencontré (ex. "le wifi ne répond plus") ;
- consulter les incidents similaires déjà résolus ;
- proposer des solutions, même sur un incident qui n'est pas le sien ;
- valider une solution comme efficace (étoiles) ;
- fermer un ticket en retenant la meilleure réponse — mais **seul celui qui a ouvert le ticket** a ce droit ;
- (à venir, Semaine 3) interroger un chatbot qui analyse, compare et recommande automatiquement les meilleures solutions à partir de l'historique.

Le projet a démarré en s'appuyant sur l'expérience d'un projet précédent (le chatbot d'assistance FGCL), dont plusieurs briques techniques ont été réutilisées (voir section "Ce qui a été réutilisé" plus bas).

## 2. Concepts de base, pour débutant complet

Avant de rentrer dans le détail, voici les briques fondamentales à comprendre. Si tu connais déjà un concept, passe au suivant.

### Backend / Frontend
- Le **backend** est la partie invisible pour l'utilisateur : le "cerveau" qui stocke les données, applique les règles (qui a le droit de faire quoi), et répond aux demandes. Chez nous : le dossier `backend/`, construit avec **FastAPI** (un framework Python).
- Le **frontend** est ce que l'utilisateur voit et clique dans son navigateur : les pages web. Chez nous : le dossier `frontend/`, en HTML/CSS/JavaScript simple (pas de framework comme React).

### API
Une **API** (Application Programming Interface) est le "guichet" par lequel le frontend demande des choses au backend. Par exemple, quand tu cliques sur "Se connecter", le frontend envoie une requête à l'adresse `/auth/login` du backend, qui répond soit "voici ton accès", soit "refusé".

### Base de données relationnelle
C'est un système qui stocke des données organisées en **tables** (comme des feuilles Excel géantes), avec des **relations** entre elles (ex. un incident "appartient" à un département). Chez nous : **SQLite**, une base de données qui tient dans un simple fichier (`knowledge_hub.db`), suffisante pour ce projet.

### ORM (Object-Relational Mapping)
Plutôt que d'écrire des requêtes SQL brutes ("SELECT * FROM incidents WHERE..."), on écrit du code Python normal, et un outil (**SQLAlchemy**, chez nous) traduit ça en SQL automatiquement. Une table devient une classe Python, une ligne devient un objet.

### Authentification et JWT
S'authentifier = prouver qui on est (email + mot de passe). Une fois authentifié, plutôt que de retaper son mot de passe à chaque action, le serveur donne un **jeton** (JWT, JSON Web Token) — une sorte de bracelet de festival signé numériquement, que le navigateur renvoie à chaque requête pour prouver son identité sans repasser par le mot de passe.

### Hachage de mot de passe
On ne stocke **jamais** un mot de passe en clair dans la base — il est transformé de façon irréversible (**hachage**, via l'algorithme **bcrypt** ici) avant d'être stocké. Même en cas de vol de la base, les mots de passe originaux restent protégés.

### Environnement virtuel (venv)
Une "boîte à outils" isolée et propre à ce projet, contenant exactement les bibliothèques Python dont il a besoin, sans interférer avec d'autres projets sur la même machine.

### Git
Un outil qui enregistre l'historique de chaque modification du code, comme une série de sauvegardes successives, permettant de revenir en arrière si besoin.

## 3. Architecture générale du projet

```
it-knowledge-hub/
├── .env                    Variables sensibles (jamais partagées, exclues de Git)
├── .env.example            Modèle de .env, sans vraies valeurs
├── .gitignore              Liste des fichiers que Git ne doit jamais suivre
├── requirements.txt        Liste exacte des bibliothèques Python nécessaires
├── README.md               Mode d'emploi du projet
│
├── backend/
│   ├── main.py             Point d'entrée : démarre l'application et branche les routes
│   ├── database.py         Connexion à la base de données SQLite
│   ├── models.py           Les 5 tables, traduites en classes Python (SQLAlchemy)
│   ├── schemas.py          Formes exactes des données reçues/renvoyées par l'API
│   ├── security.py         Hachage et vérification des mots de passe (bcrypt)
│   ├── jwt_utils.py         Création et vérification des jetons de connexion
│   ├── dependencies.py      Fonctions réutilisables : "qui est connecté ?", "est-ce un admin ?"
│   ├── init_db.py            Script qui crée les tables dans le fichier de base
│   ├── seed_admin.py          Script qui crée les départements et le compte admin
│   └── routers/                Un fichier par domaine de fonctionnalités :
│       ├── auth.py               inscription, connexion
│       ├── admin.py               validation des comptes en attente
│       ├── incidents.py           déclaration, liste, détail, fermeture
│       ├── solutions.py           proposition de réponses, étoiles
│       └── departments.py        liste des départements
│
├── frontend/
│   ├── style.css            Le design visuel (couleurs, polices, boutons...)
│   ├── api.js                Fonctions partagées pour parler au backend
│   ├── assets/logo.png        Le vrai logo FGCL
│   ├── index.html              Redirige automatiquement selon la connexion
│   ├── login.html               Page de connexion
│   ├── register.html             Page d'inscription
│   ├── dashboard.html             Tableau de bord technicien (liste des incidents)
│   ├── admin-dashboard.html        Tableau de bord admin (comptes à valider)
│   ├── incident-new.html            Formulaire de déclaration
│   └── incident-detail.html          Détail d'un incident, réponses, étoiles, fermeture
│
└── docs/                    Tous les documents de cadrage et de validation produits
```

## 4. Semaine 1 en détail (J1 à J7) — fondations et authentification

### J1 — Cahier des charges
Rédaction des spécifications complètes : périmètre fonctionnel, règles métier tranchées (inscription avec validation admin, visibilité inter-départements, formule de score), choix techniques (FastAPI, SQLAlchemy, SQLite, ChromaDB, Gemini, JWT). Un état des lieux distinguant ce qui est repris de FGCL, ce qui évolue, et ce qui se construit à neuf.

### J2 — Modélisation de la base de données
Conception des 5 tables et de leurs relations :
- **departments** (id, nom)
- **technicians** (id, email, password_hash, status, role, department_id, created_at)
- **incidents** (id, titre, description, symptomes, contexte, department_id, opened_by, status, accepted_solution_id, created_at, closed_at)
- **solutions** (id, incident_id, author_id, contenu, is_documented_by_opener, created_at)
- **stars** (id, solution_id, voter_id, created_at) — avec une **contrainte unique** sur (solution_id, voter_id) pour empêcher un double vote.

### J3 — Environnement de développement
Structure de dossiers créée, dépôt Git initialisé, `.gitignore` mis en place **avant** le premier commit (pour ne jamais exposer `.env` ou la base de données).

**Extrait de `.gitignore` :**
```
venv/
__pycache__/
.env
*.db
chroma_db/
```

### J4 — Modèles ORM (SQLAlchemy)

Chaque table devient une classe Python. Exemple simplifié (`models.py`) :

```python
class Department(Base):
    __tablename__ = "departments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    nom: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
```

- `__tablename__` = nom réel de la table en base.
- `mapped_column(...)` = une colonne, avec son type et ses contraintes.
- `primary_key=True` = identifiant unique de chaque ligne.
- `default=generate_uuid` = génère automatiquement un identifiant aléatoire si non fourni.

La table la plus importante est `Star`, avec sa contrainte anti-triche :
```python
class Star(Base):
    __tablename__ = "stars"
    __table_args__ = (UniqueConstraint("solution_id", "voter_id", name="uq_solution_voter"),)
```
Cette ligne interdit à la base d'accepter deux lignes avec la même combinaison (solution, votant) — même si le code applicatif avait un bug, la base refuserait physiquement le doublon.

`init_db.py` traduit ces classes en vraies tables dans le fichier `knowledge_hub.db`.

### J5 — Inscription des techniciens

Route `POST /auth/register` : reçoit email/mot de passe/département, vérifie que l'email n'est pas déjà pris, hache le mot de passe, crée le compte avec le statut `pending` (en attente).

```python
technician = Technician(
    email=payload.email,
    password_hash=hash_password(payload.password),
    department_id=payload.department_id,
    status="pending",
    role="technicien",
)
```

Le hachage (`security.py`) :
```python
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")
```

### J6 — Connexion et jetons JWT

Route `POST /auth/login` : vérifie email + mot de passe, **refuse si le compte est encore `pending`**, et renvoie un jeton signé si tout est bon.

```python
if technician.status != "actif":
    raise HTTPException(status_code=403, detail="Compte en attente de validation par un administrateur")

token = create_access_token({"sub": technician.id, "role": technician.role})
```

Une fonction réutilisable, `get_current_technician` (`dependencies.py`), vérifie ce jeton sur chaque route protégée — c'est le "videur" qui garde toutes les portes du système.

### J7 — Validation admin

Trois routes réservées aux comptes `role = admin` (protégées par une fonction `require_admin`, qui ajoute juste "es-tu admin ?" par-dessus la vérification du J6) :
- lister les comptes en attente,
- en approuver un (passe à `actif`),
- en rejeter un (suppression définitive).

## 5. Semaine 2 en détail (J8 à J14) — cœur métier et frontend

### J8 — Déclaration et consultation des incidents

Route `POST /incidents` : le champ le plus important du code est que **`opened_by` n'est jamais lu depuis ce que le client envoie** — il est fixé à partir du technicien authentifié :
```python
incident = Incident(
    ...,
    opened_by=current.id,   # jamais depuis payload, pour empêcher toute usurpation
)
```
Testé activement : une tentative d'injection d'un faux `opened_by` dans la requête est bien ignorée.

`GET /incidents` liste tous les incidents, visibles par tous les départements (choix de cadrage : capitalisation collective), avec filtres optionnels (`?status=...`, `?department_id=...`).

### J9 — Solutions

`POST /incidents/{id}/solutions` : n'importe quel technicien connecté peut répondre, même si l'incident n'est pas le sien. Refus si l'incident est déjà `ferme`.

### J10 — Fermeture de ticket (règle métier centrale)

`POST /incidents/{id}/close` — la route la plus surveillée du projet :
```python
if incident.opened_by != current.id:
    raise HTTPException(status_code=403, detail="Seul le technicien ayant ouvert ce ticket peut le fermer")
```
Deux façons de fermer, jamais les deux en même temps :
- `accepted_solution_id` : retenir la réponse d'un collègue ;
- `own_solution_content` : documenter soi-même la solution trouvée (crée une nouvelle solution avec `is_documented_by_opener = true`).

Testé avec une tentative de contournement active (un non-ouvreur essayant de fermer) : rejetée avec un code 403.

### J11 — Système d'étoiles

`POST /solutions/{id}/star`, avec deux protections :
```python
if solution.author_id == current.id:
    raise HTTPException(status_code=400, detail="Impossible d'étoiler sa propre solution")
```
Et la vérification du double vote, doublée par la contrainte de base posée au J2 (défense en profondeur).

`stars_count` n'est pas stocké : c'est une propriété Python calculée à la volée (`len(self.stars)`).

### J13-J14 — Frontend technicien et admin

Construction de 7 pages (login, register, dashboard, incident-new, incident-detail, admin-dashboard, index) et de 2 fichiers partagés (`style.css`, `api.js`).

**Point technique clé de `api.js`** : une seule fonction, `apiFetch()`, ajoute automatiquement le jeton JWT à chaque appel, et le stocke dans le navigateur (`localStorage`).

**Révision demandée par BY** : la première version utilisait une esthétique "outil technique sombre" générique. Après retour, la charte graphique réelle de FGCL a été reproduite en mesurant précisément les couleurs sur le site officiel (fgc-online.net) et le logo :
- Bleu principal : `#1C9EEF`
- Navy (logo) : `#2B4C82`
- Fond blanc, boutons en pilule, cartes à ombre douce.

**Deuxième révision** : séparation complète entre l'espace technicien (`dashboard.html`) et l'espace admin (`admin-dashboard.html`, nouvellement créé), avec redirection automatique selon le rôle après connexion, et un garde-fou qui renvoie un technicien normal loin de l'espace admin s'il essaie d'y accéder directement par l'URL.

## 6. Récapitulatif de toutes les erreurs rencontrées et corrigées

| # | Erreur rencontrée | Cause réelle | Solution appliquée |
|---|---|---|---|
| 1 | `numpy` refuse de s'installer (J3), erreur de compilateur C manquant | Python 3.14 (trop récent) sur la machine, incompatible avec `numpy<2.0` exigé par ChromaDB | Installation de Python 3.11 en parallèle, venv recréé avec `py -3.11 -m venv venv` |
| 2 | `pip install -r requirements.txt` : fichier introuvable | Commande lancée depuis le dossier `backend/` alors que `requirements.txt` est à la racine du projet | `cd ..` avant d'installer |
| 3 | Plantage au démarrage avec `password cannot be longer than 72 bytes` (en interne, lors du développement du J5) | `passlib==1.7.4` incompatible avec les versions récentes de `bcrypt` (>=4.1) | Remplacement de `passlib` par `bcrypt` utilisé directement (`security.py`) |
| 4 | `ModuleNotFoundError: No module named 'email_validator'` au démarrage du serveur (J5) | Le champ `EmailStr` de Pydantic nécessite ce paquet séparé, absent de l'installation initiale | Ajout d'`email-validator` au `requirements.txt` et installation manuelle |
| 5 | `venv` introuvable en pleine séance (après le frontend), `source venv/Scripts/activate` échoue | Le dossier `venv` avait disparu du projet (cause exacte non identifiée — possiblement une manipulation accidentelle) ; aggravé par un collage de plusieurs commandes d'un coup dans le terminal, qui a fait atterrir une commande `cd /` au mauvais moment | Recréation complète du venv (`py -3.11 -m venv venv`), réinstallation des dépendances, règle adoptée : ne jamais coller plusieurs lignes de commande à la fois |

## 7. État actuel du dépôt Git

```
Refonte charte graphique FGCL (vrai logo, palette bleue) + espace admin distinct
J13-J14 - Frontend technicien complet + route GET /departments
Validation Semaine 2 (backend) - document de synthese et checklist
J11 - Systeme d'etoiles, anti auto-vote et anti double-vote
J10 - Fermeture de ticket reservee a l'ouvreur
J9 - CRUD solutions
J8 - CRUD incidents
Validation Semaine 1 - document de synthese et checklist
J7 - Validation admin des comptes en attente
J6 - Connexion JWT
J5 - Inscription technicien
J4 - Modeles ORM et script d'initialisation de la base
J3 - Initialisation du projet
```

## 8. Glossaire des termes techniques utilisés

- **API** : le guichet par lequel le frontend et le backend communiquent.
- **Backend** : la partie serveur, invisible, qui gère les données et la logique.
- **bcrypt** : algorithme de hachage utilisé pour protéger les mots de passe.
- **CORS** : règle de sécurité des navigateurs qui encadre quelles adresses peuvent se parler entre elles.
- **Dépendance (FastAPI)** : une fonction réutilisable injectée automatiquement dans une route (ex. "qui est connecté ?").
- **Endpoint / route** : une adresse précise de l'API (ex. `POST /auth/login`).
- **Frontend** : les pages web que l'utilisateur voit et manipule.
- **JWT** : jeton signé prouvant l'identité d'un utilisateur connecté, sans repasser par le mot de passe à chaque requête.
- **ORM** : outil qui traduit du code Python en requêtes de base de données.
- **Pydantic / schéma** : définit la forme exacte attendue ou renvoyée par une route.
- **Seed** : script qui pré-remplit la base avec des données de départ (ici, les départements et le compte admin).
- **SQLAlchemy** : la bibliothèque Python utilisée comme ORM dans ce projet.
- **UUID** : identifiant unique généré aléatoirement (ex. `b8e2adab-6985-...`), utilisé comme clé primaire de chaque table.
- **venv (environnement virtuel)** : dossier isolé contenant les bibliothèques Python propres à ce projet.

## 9. Prochaine étape — Semaine 3

Construction du "cerveau" du chatbot : pipeline d'embedding incrémental (J15), recherche de similarité entre incidents (J16), calcul du score combiné des solutions (J17), intégration de Gemini pour formuler les recommandations (J18), endpoint chatbot complet (J19), intégration frontend (J20), tests fonctionnels (J21).
