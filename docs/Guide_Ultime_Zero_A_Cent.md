# Le Guide Ultime — IT Knowledge Hub expliqué à partir de zéro
### Pour quelqu'un qui ne connaît que le HTML de base

Ce document ne suppose **rien**. Chaque mot technique est expliqué la première fois qu'il apparaît. Lis-le dans l'ordre, du début à la fin — chaque partie s'appuie sur la précédente.

---

# PARTIE 0 — Les concepts absolus, avant même de parler du projet

## 0.1 Qu'est-ce qu'un programme ?

Un programme, c'est une suite d'instructions écrites dans un langage que l'ordinateur peut comprendre et exécuter, une par une, dans l'ordre. Le HTML que tu connais **n'est pas vraiment un programme** — c'est un langage de **description** (il décrit à quoi ressemble une page : "ici un titre, ici un bouton"), pas un langage qui **fait des calculs ou prend des décisions**.

Le projet utilise deux vrais langages de programmation :
- **Python** : pour tout ce qui se passe côté serveur (le "cerveau" caché du système).
- **JavaScript** : pour rendre les pages HTML interactives (ce qui se passe quand tu cliques sur un bouton).

## 0.2 Fichier, dossier, extension

Un **fichier** est un document sur ton ordinateur. Une **extension** (les lettres après le point, comme `.html`, `.py`, `.css`) dit à l'ordinateur quel type de contenu il contient et quel programme doit l'ouvrir. Un **dossier** (ou "répertoire") est un conteneur qui range plusieurs fichiers ensemble.

## 0.3 Client et serveur — le concept le plus important à comprendre

Imagine un restaurant :
- **Le client**, c'est toi, assis à table (dans le projet : ton navigateur web, qui affiche les pages HTML).
- **Le serveur**, c'est la cuisine, qui ne se voit pas depuis la salle, mais qui prépare vraiment les plats (dans le projet : le programme Python qui tourne en arrière-plan, invisible, qui gère les données et applique les règles).
- Quand tu commandes (tu cliques sur "Se connecter"), ta commande part vers la cuisine, qui la traite et te renvoie un plat (une réponse).

Dans ce projet, il y a littéralement **deux programmes séparés qui tournent en même temps** sur ton ordinateur :
1. Le **backend** (la cuisine) : lancé avec la commande `uvicorn main:app --reload`.
2. Le **frontend** (la salle, ce que tu vois) : lancé avec `python -m http.server 5500`.

Ils se parlent à travers Internet (même si, ici, tout se passe sur ta propre machine — `127.0.0.1` veut dire littéralement "cet ordinateur-ci").

## 0.4 Qu'est-ce qu'une requête HTTP ?

C'est le "message" que le client envoie au serveur pour demander quelque chose, et le message que le serveur renvoie en réponse. Chaque requête a :
- Une **adresse** (ex. `/auth/login`).
- Une **méthode** : `GET` (je veux récupérer une information), `POST` (je veux créer/envoyer quelque chose), `DELETE` (je veux supprimer).
- Parfois un **corps** (les données envoyées, ex. l'email et le mot de passe).

## 0.5 Qu'est-ce qu'une API ?

API = **le "guichet"** par lequel le frontend peut demander des choses précises au backend, sans avoir besoin de savoir comment le backend fonctionne à l'intérieur. Chaque "guichet" a une adresse précise (ex. `POST /incidents` = "je veux déclarer un nouvel incident").

## 0.6 Qu'est-ce que JSON ?

C'est juste un format d'écriture pour envoyer des données structurées, très proche de ce que tu connais peut-être en HTML pour les attributs. Exemple :
```json
{
  "email": "alice@fgcl.cm",
  "password": "motdepasse123"
}
```
C'est juste une liste de paires "nom : valeur", entre accolades. Le frontend et le backend s'échangent presque tout sous cette forme.

## 0.7 Qu'est-ce qu'une base de données ?

Une base de données stocke des informations de façon organisée, en **tables** — comme des feuilles de calcul Excel géantes. Une table a des **colonnes** (les catégories d'information, ex. "email", "mot de passe") et des **lignes** (chaque enregistrement individuel, ex. un technicien précis). Dans ce projet, la base de données s'appelle **SQLite**, et tient dans un seul fichier : `knowledge_hub.db`.

## 0.8 Concepts de base de la programmation (Python)

- **Une variable** : une boîte avec un nom, qui contient une valeur. `age = 25` crée une variable nommée `age` qui contient `25`.
- **Une fonction** : un bloc de code réutilisable, auquel on donne un nom, qu'on peut "appeler" (exécuter) autant de fois qu'on veut. En Python, ça commence par `def nom_de_la_fonction():`.
- **Une classe** : un "moule" pour créer des objets qui ont tous la même structure. Dans ce projet, chaque table de la base de données (ex. "Technician") est représentée par une classe Python.
- **Un import** : quand un fichier Python a besoin d'utiliser du code écrit dans un autre fichier, il l'"importe" avec le mot `import`.
- **Une condition (`if`)** : "si telle chose est vraie, fais ceci, sinon fais cela".
- **`return`** : dans une fonction, ça veut dire "renvoie cette valeur, et arrête l'exécution de la fonction ici".

---

# PARTIE 1 — Vue d'ensemble du projet

**IT Knowledge Hub** est une plateforme utilisée par les techniciens informatiques de l'entreprise FGCL. Elle sert à :
- Déclarer un problème informatique rencontré (un "incident").
- Proposer des solutions à des incidents déclarés par d'autres.
- Voter ("étoiler") pour signaler qu'une solution a vraiment fonctionné.
- Fermer un ticket en indiquant quelle solution a résolu le problème.
- Poser une question à un assistant intelligent (chatbot) qui retrouve tout seul, dans l'historique, la solution la plus pertinente.

Le but final : que le savoir technique de l'équipe ne se perde plus, et que la même panne ne soit jamais résolue deux fois "à partir de zéro" par deux personnes différentes qui s'ignorent.

---

# PARTIE 2 — L'architecture générale, avec une analogie complète

Reprenons l'analogie du restaurant, appliquée précisément à ce projet :

| Élément du restaurant | Élément du projet | Rôle |
|---|---|---|
| La salle, les tables, le menu | **Le frontend** (dossier `frontend/`) | Ce que le technicien voit et clique dans son navigateur |
| La cuisine | **Le backend** (dossier `backend/`) | Reçoit les commandes, applique les recettes (les règles), prépare la réponse |
| Le garde-manger | **La base de données** (`knowledge_hub.db`) | Stocke tous les ingrédients (comptes, incidents, solutions) |
| Un livre de recettes personnalisées, appris par cœur au fil du temps | **La base vectorielle** (`chroma_db/`) | Permet de retrouver rapidement "quel plat ressemble à celui-ci ?" |
| Un chef consultant externe, très cultivé, qu'on appelle au téléphone pour un avis | **Gemini (intelligence artificielle de Google)** | Formule la réponse finale du chatbot en langage naturel |

## Où sont rangés les fichiers ?

```
it-knowledge-hub/
├── backend/         → toute la "cuisine" (Python)
│   └── routers/     → chaque "guichet" de commande, un fichier par famille de plats
├── frontend/        → toute la "salle" (HTML/CSS/JS)
└── docs/            → tous les documents écrits sur le projet
```

---

# PARTIE 3 — Le Backend, expliqué fichier par fichier

## 3.1 `main.py` — la porte d'entrée du restaurant

C'est le fichier qui démarre tout. Extrait simplifié :
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
```
- `from fastapi import FastAPI` : on importe l'outil FastAPI (le "cadre" qui gère les requêtes HTTP à notre place).
- `app = FastAPI()` : on crée l'application elle-même — la variable `app` représente tout le restaurant.
- `@app.get("/health")` : cette ligne étrange (un "décorateur") dit : "quand quelqu'un demande `/health` en GET, exécute la fonction juste en dessous".
- `def health_check(): return {"status": "ok"}` : la fonction renvoie un petit JSON disant "je suis vivant".

Ensuite, `main.py` "branche" tous les autres guichets (`routers/`) à l'application.

## 3.2 `database.py` — le branchement vers le garde-manger

```python
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```
- `engine` : la connexion technique vers le fichier `knowledge_hub.db`.
- `SessionLocal` : une "usine" qui crée une conversation temporaire avec la base à chaque fois qu'une requête en a besoin, et qui la referme automatiquement après.

## 3.3 `models.py` — transformer les tables en "moules" Python

Rappel : une classe est un moule. Voici le moule pour la table des départements :
```python
class Department(Base):
    __tablename__ = "departments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), unique=True)
```
- `__tablename__` : le nom réel de la table dans le fichier de base de données.
- `id` : l'identifiant unique de chaque département (une longue suite de caractères aléatoires, un UUID).
- `nom` : le nom du département, qui doit être unique (`unique=True` empêche d'avoir deux fois "Digitalisation").

Il y a 5 moules dans ce fichier : `Department`, `Technician`, `Incident`, `Solution`, `Star`. La règle la plus importante du fichier est sur `Star` :
```python
__table_args__ = (UniqueConstraint("solution_id", "voter_id"),)
```
Ça dit à la base de données : "n'accepte jamais deux lignes avec la même combinaison (solution, votant)" — impossible de voter deux fois pour la même solution, même en cas de bug ailleurs dans le code.

## 3.4 `schemas.py` — les formulaires que le backend accepte ou refuse

Une classe ici décrit **la forme exacte** qu'une donnée doit avoir pour être acceptée :
```python
class TechnicianCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    department_id: str
```
Si quelqu'un essaie de s'inscrire avec un mot de passe de 3 caractères, ou un email mal formé (pas de `@`), la requête est **automatiquement rejetée** avant même d'exécuter la moindre ligne de notre propre code — FastAPI et Pydantic (l'outil derrière `BaseModel`) font cette vérification tout seuls.

## 3.5 `security.py` — transformer un mot de passe en secret illisible

```python
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")
```
`bcrypt.hashpw` prend le mot de passe en clair et le transforme en une suite de caractères illisible et **impossible à inverser** (on ne peut pas "retrouver" le mot de passe à partir du résultat). C'est ça qu'on stocke en base — jamais le vrai mot de passe.

## 3.6 `jwt_utils.py` — le bracelet de festival

Analogie complète : à l'entrée d'un festival, tu montres ta pièce d'identité une seule fois. On te donne un bracelet. Ensuite, pour entrer dans chaque zone, tu montres juste le bracelet — pas besoin de reprouver qui tu es à chaque fois.

```python
def create_access_token(data: dict) -> str:
    ...
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```
Cette fonction crée le "bracelet" (le jeton JWT), signé avec une clé secrète que seul le serveur connaît — personne ne peut fabriquer un faux bracelet sans connaître cette clé.

## 3.7 `dependencies.py` — le videur à l'entrée de chaque zone

```python
def get_current_technician(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    ...
    return technician
```
Cette fonction est appelée automatiquement par FastAPI avant d'exécuter certaines routes. Elle vérifie le bracelet (le jeton), et si tout est en ordre, elle renvoie "voici qui est connecté". Si le bracelet est faux ou absent, elle bloque tout de suite avec une erreur "401 non autorisé".

## 3.8 Les fichiers `routers/` — chaque famille de guichets

- **`auth.py`** : inscription (`POST /auth/register`) et connexion (`POST /auth/login`).
- **`admin.py`** : validation des comptes en attente.
- **`incidents.py`** : déclarer, consulter, fermer un incident.
- **`solutions.py`** : proposer une réponse, voter (étoiler).
- **`departments.py`** : juste lister les départements (pour remplir les menus déroulants).
- **`chatbot.py`** : le point d'entrée unique de l'assistant intelligent.

Exemple détaillé, la règle la plus critique du projet, dans `incidents.py` :
```python
if incident.opened_by != current.id:
    raise HTTPException(status_code=403, detail="Seul le technicien ayant ouvert ce ticket peut le fermer")
```
`incident.opened_by` = qui a créé ce ticket. `current.id` = qui est connecté en ce moment (grâce au "videur" du 3.7). Si ce n'est pas la même personne, on refuse (`403` = code d'erreur standard signifiant "interdit").

---

# PARTIE 4 — L'intelligence artificielle du chatbot, expliquée à partir de zéro

## 4.1 Qu'est-ce qu'un "embedding" ?

Imagine que chaque phrase puisse être transformée en un point précis sur une immense carte, où **les phrases qui veulent dire la même chose sont proches sur la carte**, même si elles n'utilisent pas les mêmes mots. "Le wifi ne marche plus" et "impossible de se connecter au réseau sans fil" seraient deux points très proches sur cette carte, même si aucun mot n'est identique.

Un "embedding", c'est exactement ça : une transformation d'un texte en une liste de nombres (des "coordonnées" sur cette carte à des centaines de dimensions). Cette transformation est faite par un modèle d'intelligence artificielle déjà entraîné (`paraphrase-multilingual-MiniLM-L12-v2`), qu'on utilise ici tel quel, sans l'avoir créé nous-mêmes.

## 4.2 Qu'est-ce qu'une base de données vectorielle ?

C'est une base de données spécialisée (ici, **ChromaDB**) qui ne stocke pas du texte classique, mais des coordonnées (des "vecteurs"). Sa spécialité : étant donné un nouveau point, elle sait très vite dire "voici les points déjà connus les plus proches de celui-ci".

## 4.3 Qu'est-ce qu'un LLM (comme Gemini) ?

LLM = "Large Language Model" (grand modèle de langage). C'est une intelligence artificielle entraînée sur d'énormes quantités de texte, capable de comprendre une demande en langage naturel et de rédiger une réponse cohérente. Dans ce projet, on ne demande **jamais** à Gemini d'inventer une solution — on lui donne des solutions déjà existantes (trouvées dans notre propre base), et on lui demande seulement de les présenter clairement.

## 4.4 `vector_store.py` — le "cartographe"

```python
def upsert_incident(incident_id, titre, symptomes, contexte, department_id):
    text = build_incident_text(titre, symptomes, contexte)
    _get_collection().upsert(ids=[incident_id], documents=[text], ...)
```
À chaque nouvel incident déclaré, cette fonction transforme son texte en coordonnées et l'ajoute à la carte (`upsert` = ajouter ou mettre à jour).

```python
def search_similar_incidents(query_text, top_k=5):
    results = collection.query(query_texts=[query_text], n_results=top_k)
    ...
```
Pour une nouvelle question, cette fonction retrouve les incidents dont les coordonnées sont les plus proches.

## 4.5 `scoring.py` — classer les solutions trouvées

Une fois qu'on a trouvé des incidents similaires, il faut choisir **quelle solution parmi toutes celles proposées** est la meilleure à recommander. La formule :
```
score = 0,4 × (solution officiellement retenue ?)
      + 0,3 × (nombre d'étoiles, normalisé)
      + 0,2 × (proximité avec la question posée)
      + 0,1 × (fraîcheur, les solutions récentes comptent un peu plus)
```

## 4.6 `llm.py` — parler à Gemini

```python
def generate_recommendation(query_text, ranked_solutions):
    prompt = build_prompt(query_text, ranked_solutions)
    response = client.models.generate_content(model=GEMINI_MODEL_NAME, contents=[SYSTEM_PROMPT, prompt])
    return response.text
```
`build_prompt` rédige un texte qui explique à Gemini : "voici la question, voici les solutions déjà classées, rédige une recommandation claire à partir de CES solutions uniquement". Gemini renvoie du texte, qu'on affiche tel quel au technicien.

## 4.7 `chatbot.py` — assembler les quatre étapes

```python
matches = vector_store.search_similar_incidents(payload.message)
good_matches = [m for m in matches if vector_store.is_similar_enough(m["distance"])]
if not good_matches:
    return ChatbotResponse(found_match=False, message=llm.NO_MATCH_MESSAGE, ...)
ranked = scoring.rank_solutions_for_matches(good_matches, db)
message = llm.generate_recommendation(payload.message, ranked)
```
Ligne par ligne : chercher les incidents proches → garder seulement ceux assez proches (seuil) → si rien d'assez proche, proposer de créer un ticket → sinon, classer les solutions → demander à Gemini de rédiger la réponse finale.

---

# PARTIE 5 — Le Frontend, expliqué à partir de ton HTML déjà connu

Tu connais déjà le HTML (balises, structure de page). Voici ce qui s'ajoute :

## 5.1 CSS — les "variables" de couleur

```css
:root {
  --primaire: #003D92;
}
.btn-primary { background: var(--primaire); }
```
`:root` définit des "variables" de style réutilisables partout (change la couleur une fois ici, elle change partout). `var(--primaire)` va chercher cette valeur.

## 5.2 JavaScript — rendre une page interactive

Le JavaScript s'exécute **dans le navigateur du visiteur**, pas sur le serveur. Il peut réagir à des clics, modifier la page affichée, et surtout : **envoyer des requêtes au backend** sans recharger toute la page.

```javascript
async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const data = await response.json();
  return data;
}
```
- `fetch(...)` : la fonction JavaScript native qui envoie une requête HTTP (le "client" qui demande quelque chose au "serveur", cf. Partie 0.3).
- `await` : "attends que cette opération se termine avant de continuer" (une requête réseau prend un peu de temps).
- `response.json()` : transforme la réponse (en texte JSON) en un objet JavaScript utilisable.

## 5.3 Le fichier `api.js` — la boîte à outils commune

Toutes les pages utilisent les mêmes fonctions, écrites une seule fois ici :
- `apiFetch()` : envoie une requête, en ajoutant automatiquement le "bracelet" (jeton JWT) s'il existe.
- `renderSidebar()` : construit le menu de navigation à gauche.
- `getToken()` / `setToken()` : lit/écrit le jeton dans le navigateur (`localStorage`, une mémoire qui survit même si on ferme l'onglet).

## 5.4 Chaque page, en une phrase

- `login.html` : formulaire → envoie à `/auth/login` → si succès, stocke le jeton, redirige.
- `register.html` : formulaire → envoie à `/auth/register`.
- `dashboard.html` : au chargement, demande la liste des incidents (`GET /incidents`), l'affiche.
- `incident-detail.html` : demande le détail d'UN incident, affiche ses solutions, propose les boutons (étoiler, fermer) seulement si les conditions sont remplies.
- `chatbot.html` : capture ce que tu tapes, l'envoie à `/chatbot/ask`, affiche la réponse.

---

# PARTIE 6 — Le parcours complet, étape par étape, fichier par fichier

1. **Tu ouvres `login.html`.** Tu tapes ton email/mot de passe, tu cliques "Se connecter".
2. **`api.js` envoie une requête** `POST /auth/login` avec ces informations.
3. **`routers/auth.py` la reçoit**, vérifie le mot de passe via `security.py`, crée un jeton via `jwt_utils.py`.
4. **Le jeton revient au navigateur**, stocké par `api.js`.
5. **Tu es redirigé vers `dashboard.html`**, qui demande `GET /incidents` (avec le jeton, automatiquement ajouté par `apiFetch`).
6. **`routers/incidents.py` vérifie le jeton** (via `dependencies.py`), récupère les incidents dans `models.py`/`database.py`, les renvoie.
7. **Tu déclares un incident** (`incident-new.html` → `POST /incidents`) → `incidents.py` l'enregistre ET l'envoie à `vector_store.py` pour l'indexer.
8. **Un collègue répond** → `solutions.py` enregistre sa réponse.
9. **Tu étoiles sa réponse** → `solutions.py` vérifie que tu n'es pas l'auteur, que tu n'as pas déjà voté, puis enregistre.
10. **Tu fermes le ticket** → `incidents.py` vérifie que c'est bien toi qui l'as ouvert, enregistre la solution retenue.
11. **N'importe qui pose une question au chatbot** → `chatbot.py` orchestre `vector_store.py` + `scoring.py` + `llm.py` pour produire une réponse.

---

# PARTIE 7 — Les bugs rencontrés, comme autant de leçons

- **Python trop récent (J3)** : la version de Python installée par défaut était trop nouvelle pour certains outils du projet → installé une version plus ancienne et compatible.
- **Bibliothèque de hachage incompatible (J5)** : deux outils censés fonctionner ensemble (`passlib` et `bcrypt`) ne l'étaient plus dans leurs dernières versions → utilisé `bcrypt` directement, sans intermédiaire.
- **La recherche ne trouvait jamais rien (J19)** : la "carte" (ChromaDB) mesurait les distances d'une façon différente de celle prévue par le seuil de similarité → précisé explicitement la bonne méthode de calcul.
- **Modèle d'IA retiré du catalogue (J18)** : Google a cessé de proposer un modèle qu'on utilisait → remplacé par un modèle encore disponible.

Le point commun de tous ces bugs : **rien ne plantait bruyamment** — le système répondait "normalement", juste avec un résultat incorrect. Ce sont les bugs les plus difficiles à repérer, et les plus intéressants à raconter en soutenance.

---

# PARTIE 8 — Glossaire final (tous les mots techniques du document)

- **API** : le guichet par lequel deux programmes se parlent.
- **Backend** : la partie invisible, le programme serveur.
- **Base de données** : un système de stockage organisé en tables.
- **bcrypt** : la méthode utilisée pour rendre un mot de passe illisible et non réversible.
- **ChromaDB** : la base de données spécialisée dans la recherche par similarité.
- **Classe (Python)** : un moule pour créer des objets structurés.
- **Client** : celui qui demande (ton navigateur).
- **Embedding** : la transformation d'un texte en coordonnées numériques.
- **Fonction** : un bloc de code réutilisable.
- **Frontend** : la partie visible, les pages web.
- **Gemini** : l'intelligence artificielle de Google utilisée pour rédiger les réponses du chatbot.
- **JSON** : un format d'écriture de données structurées.
- **JWT** : le "bracelet" numérique prouvant qu'on est connecté.
- **LLM** : un grand modèle de langage (comme Gemini).
- **ORM** : l'outil qui traduit des classes Python en vraies tables de base de données (ici, SQLAlchemy).
- **Requête HTTP** : le message envoyé du client vers le serveur (et sa réponse).
- **Serveur** : celui qui répond (le backend).
- **UUID** : un identifiant unique généré aléatoirement.
- **Variable** : une boîte nommée qui contient une valeur.
