# Guide de déploiement en ligne
### Backend sur Render, frontend sur GitHub Pages — tout gratuit

**Avant de commencer** : applique la mise à jour du zip le plus récent (3 fichiers modifiés : `backend/main.py`, `frontend/api.js`, nouveau `backend/start.sh`), et pousse-la sur ton dépôt GitHub (`git add .`, `git commit -m "Préparation déploiement"`, `git push`).

**Limite à connaître et à assumer** (identique à celle déjà rencontrée sur FGCL) : le plan gratuit de Render donne 512 Mo de RAM, et **remet le disque à zéro à chaque réveil** du service (après ~15 minutes d'inactivité). Le script `start.sh` recrée automatiquement les données de démo à chaque démarrage — la plateforme déployée ne garde donc pas d'historique entre deux périodes d'inactivité. C'est un choix assumé pour une démonstration publique, pas pour un usage réel.

---

## Partie A — Déployer le backend sur Render

### A1. Créer un compte Render

1. Va sur **render.com**, clique sur **"Get Started"**.
2. Inscris-toi avec ton compte **GitHub** directement (le plus simple, ça lui donne accès à tes dépôts).

### A2. Créer le service web

1. Sur le tableau de bord Render, clique **"New +"** → **"Web Service"**.
2. Connecte ton dépôt GitHub (`it-knowledge-hub` ou le nom que tu lui as donné) — autorise Render à y accéder si demandé.
3. Remplis les champs :
   - **Name** : `it-knowledge-hub` (ou ce que tu veux, ça devient une partie de l'adresse finale)
   - **Region** : la plus proche de toi (ou n'importe laquelle)
   - **Branch** : `master`
   - **Root Directory** : `backend`
   - **Runtime** : `Python 3`
   - **Build Command** : `pip install -r ../requirements.txt`
   - **Start Command** : `bash start.sh`
   - **Instance Type** : **Free**

### A3. Configurer les variables d'environnement

Toujours sur cette page de création, descends jusqu'à **"Environment Variables"**, et ajoute une par une **toutes** les valeurs de ton fichier `.env` local (ouvre-le pour les copier) :

| Clé | Valeur |
|---|---|
| `GEMINI_API_KEY` | ta vraie clé |
| `JWT_SECRET_KEY` | ta vraie clé |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_EXPIRATION_MINUTES` | `1440` |
| `ADMIN_EMAIL` | ton email admin |
| `ADMIN_PASSWORD` | ton mot de passe admin |
| `DATABASE_URL` | `sqlite:///./knowledge_hub.db` |
| `FRONTEND_URL` | *(laisse vide pour l'instant, on y revient en partie C)* |

### A4. Lancer le déploiement

1. Clique **"Create Web Service"** en bas de page.
2. Render installe les dépendances et démarre le service — ça peut prendre **5 à 10 minutes** la première fois (le modèle d'IA doit se télécharger).
3. Une fois prêt, Render affiche une adresse du type `https://it-knowledge-hub-xxxx.onrender.com` — **copie-la**, tu en as besoin pour la suite.
4. Teste-la : va sur `https://ton-adresse.onrender.com/health` dans ton navigateur, tu dois voir `{"status":"ok",...}`.

---

## Partie B — Déployer le frontend sur GitHub Pages

### B1. Préparer une branche dédiée au frontend

Dans ton terminal, à la racine de ton projet (avec le venv activé n'a pas d'importance ici, c'est Git) :
```
git subtree push --prefix frontend origin gh-pages
```
Cette commande copie **uniquement** le contenu de ton dossier `frontend/` dans une nouvelle branche `gh-pages`, sans toucher à ta branche principale.

### B2. Activer GitHub Pages

1. Va sur ton dépôt GitHub, dans le navigateur.
2. Onglet **"Settings"** → section **"Pages"** (menu de gauche).
3. Sous "Build and deployment" → "Source", choisis **"Deploy from a branch"**.
4. Branche : **`gh-pages`**, dossier : **`/ (root)`**. Clique **"Save"**.
5. Attends 1-2 minutes, rafraîchis la page : une adresse apparaît en haut, du type `https://ton-pseudo.github.io/it-knowledge-hub/`.

---

## Partie C — Connecter les deux

### C1. Mettre à jour le frontend avec la vraie adresse du backend

1. Ouvre `frontend/api.js` en local.
2. Remplace `https://REMPLACE-MOI.onrender.com` par ta vraie adresse Render (celle notée en A4).
3. Sauvegarde, puis republie cette branche :
```
git add frontend/api.js
git commit -m "Adresse backend deployee"
git subtree push --prefix frontend origin gh-pages
```

### C2. Mettre à jour le backend avec la vraie adresse du frontend

1. Retourne sur Render → ton service → onglet **"Environment"**.
2. Modifie la variable `FRONTEND_URL` avec ta vraie adresse GitHub Pages (celle notée en B2), **sans slash à la fin**.
3. Sauvegarde — Render redéploie automatiquement.

### C3. Tester pour de vrai

1. Va sur ton adresse GitHub Pages (`.../login.html`).
2. Connecte-toi avec un compte de démo (`alice.demo@fgcl.cm` / `Demo2026!`).
3. **La première requête peut prendre 30 à 60 secondes** si le service Render s'était endormi (le temps qu'il se réveille) — c'est normal, pas un bug.

---

## À mentionner en soutenance si on te demande "c'est déployé ?"

- Oui, backend et frontend sont accessibles publiquement.
- Limite assumée et documentée : plan gratuit, service qui s'endort après 15 min d'inactivité (premier chargement plus lent après une pause), et données remises à zéro à chaque réveil — exactement la même nature de contrainte déjà rencontrée et documentée sur le projet FGCL précédent.
