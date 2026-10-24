# Checklist du jour de la soutenance
### À faire la VEILLE, puis à re-vérifier le MATIN MÊME

Chaque étape est expliquée comme si tu la faisais pour la première fois. Suis-les dans l'ordre, une par une.

---

## Partie A — À faire la VEILLE (pas le matin même, pour avoir le temps de réagir en cas de souci)

### A1 — Vérifier que tu as bien la toute dernière version du projet

1. Ouvre l'explorateur de fichiers Windows.
2. Va dans ton dossier de travail : `Téléchargements > Claude 3 > it-knowledge-hub`.
3. Vérifie que le dossier `docs/` contient bien tous ces fichiers (clic dedans, regarde la liste) :
   - `Cahier_des_charges_IT_Knowledge_Hub.docx`
   - `Rapport_Projet_IT_Knowledge_Hub.docx`
   - `Soutenance_IT_Knowledge_Hub.pptx`
   - `Guide_Soutenance_Questions_Jury.md`
   - Les documents de validation des 4 semaines

Si un fichier manque, redemande-le-moi avant la veille au soir, pas le matin même.

### A2 — Repartir d'une base 100% propre, avec les données de démo

Ouvre CMD (touche Windows, tape `cmd`, Entrée). Tape ces commandes **une par une**, Entrée après chacune :

```
cd "C:\Users\User\Downloads\Claude 3\it-knowledge-hub"
venv\Scripts\activate
cd backend
```

Puis :
```
del knowledge_hub.db
rmdir /s /q chroma_db
python init_db.py
python seed_admin.py
python seed_demo_data.py
```

**Ce que tu dois voir à la fin** : un message listant 3 comptes techniciens de démo (`alice.demo@fgcl.cm`, `bob.demo@fgcl.cm`, `chloe.demo@fgcl.cm`, tous avec le mot de passe `Demo2026!`) et 3 incidents. **Note ces identifiants sur un papier ou dans un fichier texte que tu garderas ouvert pendant la soutenance** — tu ne dois pas avoir à les chercher en direct.

### A3 — Faire une sauvegarde de cette base "propre"

Toujours dans le dossier `backend`, copie ces deux éléments ailleurs (par exemple sur une clé USB, ou dans un dossier `Backup_Soutenance` sur ton Bureau) :
- Le fichier `knowledge_hub.db`
- Le dossier `chroma_db` entier

**Pourquoi** : si tu casses quelque chose en manipulant pendant une répétition, tu pourras juste recopier ces deux éléments par-dessus au lieu de tout refaire depuis zéro le jour J.

### A4 — Tester le cycle complet une dernière fois

```
python test_e2e.py
```
Tu dois voir `14 test(s) réussi(s), 0 échec(s)` (si ton réseau fonctionne au moment du test). Si tu as moins de 14, note lequel a échoué et dis-le-moi avant le jour J.

### A5 — Préparer un filet de sécurité : captures d'écran ou vidéo

Au cas où le wifi de la salle de soutenance ne fonctionne pas (ça arrive), prépare **à l'avance**, chez toi :
1. Fais tourner l'application normalement (backend + frontend + tout fonctionne).
2. Fais des captures d'écran (touche `Windows + Maj + S` sur Windows) de : la page de connexion, le tableau de bord, un incident fermé avec sa solution retenue, une conversation avec l'assistant IA qui trouve une solution.
3. Range ces images dans un dossier `Plan_B_Captures` facilement accessible.
4. Optionnel mais recommandé : enregistre une courte vidéo (2-3 minutes) de toi en train d'utiliser l'application, avec un logiciel comme Xbox Game Bar (déjà installé sur Windows, `Windows + G` pour l'ouvrir).

---

## Partie B — À refaire le MATIN MÊME (même si tout a marché la veille)

### B1 — Vérifier la connexion internet de la salle, si possible avant l'heure

Le chatbot a besoin d'internet pour appeler Gemini. Si tu peux tester la connexion de la salle avant ton passage, fais-le.

### B2 — Relancer les deux serveurs, dans l'ordre

**Terminal 1 :**
```
cd "C:\Users\User\Downloads\Claude 3\it-knowledge-hub"
venv\Scripts\activate
cd backend
uvicorn main:app --reload
```
Attends `Application startup complete.`

**Terminal 2 (nouvelle fenêtre CMD) :**
```
cd "C:\Users\User\Downloads\Claude 3\it-knowledge-hub\frontend"
python -m http.server 5500
```

### B3 — Ouvrir le navigateur et se connecter AVANT de rentrer dans la salle

1. Va sur `http://127.0.0.1:5500/login.html`.
2. Connecte-toi avec `alice.demo@fgcl.cm` / `Demo2026!`.
3. Vérifie que le tableau de bord affiche bien les 3 incidents de démo.
4. Va sur l'Assistant IA, pose la question `le wifi ne repond plus`, vérifie qu'il répond correctement.

**Si tout ça fonctionne, laisse le navigateur ouvert sur cette page, ne le ferme plus.**

### B4 — Préparer les fenêtres pour la présentation

- Garde ouverts seulement : les 2 fenêtres CMD (backend + frontend), le navigateur, et ta présentation PowerPoint.
- Ferme tout le reste (autres onglets, autres logiciels) pour éviter les notifications ou lenteurs pendant la démo.
- Mets ton ordinateur en mode "Ne pas déranger" si possible (pour éviter qu'une notification s'affiche à l'écran pendant la projection).

---

## Partie C — Plan B si quelque chose casse PENDANT la soutenance

| Problème | Action immédiate |
|---|---|
| Pas d'internet dans la salle | Passe directement aux captures d'écran / vidéo de secours préparées à l'avance (Partie A5). Explique simplement : "le chatbot a besoin d'un accès réseau pour Gemini, voici son fonctionnement en images." |
| Le serveur backend plante | Ne panique pas : ferme la fenêtre CMD, relance les 2 commandes de B2. Ça prend 10 secondes. |
| Une page semble bloquée / bug visuel | Rafraîchis simplement la page (`F5` ou `Ctrl+R`) avant de chercher un vrai problème. |
| Une question du jury te bloque totalement | Relis mentalement la consigne du guide de questions : ne jamais dire "je ne sais pas" sec — reformule "ce point précis n'a pas été creusé dans ce cycle, voici comment je l'aborderais". |
