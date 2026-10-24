# Validation — Semaine 1 (J1 à J7)
### IT Knowledge Hub — Fondations, authentification, inscription et validation admin

**Objectif de la semaine** (rappel du planning) : disposer d'une base de données validée, d'un environnement de développement propre, et d'un système d'authentification/inscription complet, avant toute logique métier sur les incidents.

---

## 1. Récapitulatif jour par jour

| Jour | Contenu | Statut |
|---|---|---|
| J1 | Cahier des charges, état des lieux (existant FGCL réutilisé/évolué/reconstruit), choix techniques | ✅ Validé |
| J2 | Schéma relationnel complet (5 tables) et diagramme entité-association | ✅ Validé |
| J3 | Structure de projet, dépôt Git initialisé, `.gitignore` vérifié avant le premier commit, environnement local fonctionnel | ✅ Validé |
| J4 | Modèles ORM SQLAlchemy (Department, Technician, Incident, Solution, Star), script d'initialisation de la base | ✅ Validé |
| J5 | Inscription des techniciens (`POST /auth/register`), hachage bcrypt, statut `pending` par défaut, seed de l'admin unique | ✅ Validé |
| J6 | Connexion et jetons JWT (`POST /auth/login`), route protégée de test (`GET /auth/me`) | ✅ Validé |
| J7 | Validation admin des comptes en attente (`GET /admin/pending-technicians`, `POST .../approve`, `DELETE .../reject`) | ✅ Validé |

## 2. Batterie de tests exécutés

Méthodologie reprise du chatbot FGCL (batterie systématique, un statut par scénario), appliquée ici au cycle d'authentification.

| # | Scénario testé | Comportement attendu | Résultat observé | Statut |
|---|---|---|---|---|
| 1 | Inscription avec données valides | Compte créé, statut `pending`, code 201 | Conforme | ✅ |
| 2 | Réponse à l'inscription | `password_hash` absent de la réponse | Conforme | ✅ |
| 3 | Inscription avec un email déjà utilisé | Rejet avec code 409 | Conforme | ✅ |
| 4 | Inscription avec un département inexistant | Rejet avec code 404 | Conforme | ✅ |
| 5 | Inscription avec un mot de passe trop court (< 8 caractères) | Rejet avec code 422 (validation Pydantic) | Conforme | ✅ |
| 6 | Connexion d'un compte encore `pending` | Rejet avec code 403 | Conforme | ✅ |
| 7 | Connexion avec les identifiants admin (seedés) | Connexion réussie, jeton reçu | Conforme | ✅ |
| 8 | Connexion avec un mauvais mot de passe | Rejet avec code 401 | Conforme | ✅ |
| 9 | Connexion avec un email inconnu | Rejet avec code 401, message identique au cas précédent | Conforme | ✅ |
| 10 | Accès à une route protégée sans jeton | Rejet avec code 401 | Conforme | ✅ |
| 11 | Accès à une route protégée avec un jeton valide | Informations du compte renvoyées | Conforme | ✅ |
| 12 | Accès à une route protégée avec un jeton falsifié | Rejet avec code 401 | Conforme | ✅ |
| 13 | Connexion d'un compte validé manuellement | Connexion réussie | Conforme | ✅ |
| 14 | Un technicien normal accède à une route admin | Rejet avec code 403 | Conforme | ✅ |
| 15 | Un admin liste les comptes en attente | Liste correcte renvoyée | Conforme | ✅ |
| 16 | Un admin approuve un compte en attente | Statut passé à `actif`, code 200 | Conforme | ✅ |
| 17 | Connexion du compte juste après approbation | Connexion réussie | Conforme | ✅ |
| 18 | Ré-approbation d'un compte déjà actif | Rejet avec code 400 | Conforme | ✅ |
| 19 | Approbation d'un identifiant de compte inexistant | Rejet avec code 404 | Conforme | ✅ |
| 20 | Rejet (suppression) d'un compte en attente | Code 204, compte supprimé | Conforme | ✅ |
| 21 | Connexion après rejet du compte | Rejet avec code 401 (email inconnu) | Conforme | ✅ |
| 22 | Accès à une route admin sans aucun jeton | Rejet avec code 401 (avant même la vérification du rôle) | Conforme | ✅ |

**22 scénarios testés, 22 conformes.**

## 3. Décisions techniques prises en cours de semaine (à mentionner en soutenance)

- **Remplacement de `passlib` par `bcrypt` utilisé directement** : `passlib==1.7.4` s'est révélé incompatible avec les versions récentes de `bcrypt` (>=4.1), qui ont retiré un attribut interne dont `passlib` a besoin. Détecté et corrigé pendant le développement, avant toute mise en production — même type de vigilance que sur le chatbot FGCL.
- **Message d'erreur volontairement identique** entre "email inconnu" et "mot de passe incorrect" à la connexion, pour ne pas laisser un attaquant déduire quels emails existent dans la base.
- **Rejet d'un compte = suppression définitive**, plutôt qu'un statut `rejected` conservé en base — choix simple assumé pour ce cycle, à documenter comme tel si le jury interroge ce point.

## 4. État du dépôt Git

```
ed925c4 J7 - Validation admin des comptes en attente (approve/reject), dependance require_admin
078777f J6 - Connexion JWT (POST /auth/login), dependance get_current_technician, GET /auth/me
bd9c493 J5 - Inscription technicien (POST /auth/register), hachage bcrypt direct, seed admin
fde6cbe J4 - Modeles ORM (SQLAlchemy) et script d'initialisation de la base
4d9e81a J3 - Initialisation du projet : structure, dependances, .gitignore, README
```

Historique propre, un commit par jour, aucun secret ni base de données versionné (vérifié dès le J3).

## 5. Checklist de fin de semaine

- [x] Schéma de base de données validé et implémenté
- [x] Environnement de développement fonctionnel (Python 3.11, dépendances installées sans erreur)
- [x] `.gitignore` vérifié en conditions réelles (aucun secret exposé)
- [x] Cycle complet inscription → validation admin → connexion → accès protégé, testé de bout en bout
- [x] Contrôle d'accès par rôle (technicien vs admin) vérifié
- [x] 22 scénarios de test documentés et conformes

## 6. Prochaine étape

Semaine 2 (J8 à J14) : cœur métier — déclaration d'incidents, proposition de solutions, règle de propriété du ticket (seul l'ouvreur peut fermer), système d'étoiles.
