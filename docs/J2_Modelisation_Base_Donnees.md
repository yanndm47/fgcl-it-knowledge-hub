# J2 — Modélisation de la base de données
### IT Knowledge Hub

Livrable du Jour 2 : schéma relationnel complet, avec types, contraintes et justifications. Le diagramme entité-association correspondant a été présenté en conversation.

---

## DEPARTMENTS

| Champ | Type | Contraintes |
|---|---|---|
| id | UUID | PK |
| nom | VARCHAR(100) | NOT NULL, UNIQUE |

Table simple, reprise directement de la logique FGCL (Digitalisation, Infra/Réseau, extensible à un 3e département sans changement de schéma).

## TECHNICIANS

| Champ | Type | Contraintes |
|---|---|---|
| id | UUID | PK |
| email | VARCHAR(255) | NOT NULL, UNIQUE |
| password_hash | VARCHAR(255) | NOT NULL (bcrypt) |
| status | ENUM('pending','actif') | NOT NULL, défaut `pending` |
| department_id | UUID | FK → departments.id, NOT NULL |
| role | ENUM('technicien','admin') | NOT NULL, défaut `technicien` |
| created_at | DATETIME | NOT NULL, défaut now() |

Notes :
- `status = pending` bloque la connexion (vérifié au login, pas seulement à l'inscription).
- Un seul compte `role = admin` créé par script de seed ; tous les autres proviennent de `POST /auth/register`.
- Index sur `email` (recherche au login) et sur `department_id` (filtrage).

## INCIDENTS

| Champ | Type | Contraintes |
|---|---|---|
| id | UUID | PK |
| titre | VARCHAR(200) | NOT NULL |
| description | TEXT | NOT NULL |
| symptomes | TEXT | NOT NULL |
| contexte | TEXT | nullable |
| department_id | UUID | FK → departments.id, NOT NULL |
| opened_by | UUID | FK → technicians.id, NOT NULL |
| status | ENUM('ouvert','ferme') | NOT NULL, défaut `ouvert` |
| accepted_solution_id | UUID | FK → solutions.id, nullable |
| created_at | DATETIME | NOT NULL, défaut now() |
| closed_at | DATETIME | nullable |

Notes :
- `opened_by` est fixé côté serveur à l'utilisateur authentifié — jamais transmis par le client (clé de la règle de propriété du ticket).
- `accepted_solution_id` référence `solutions.id` : contrainte à créer en différé (la table `solutions` dépend elle-même de `incidents`), ou `FK` nullable ajoutée après création des deux tables.
- Index sur `department_id`, `status`, et `opened_by`.
- `symptomes` + `contexte` = champ source de l'embedding vectoriel (concaténés avant encodage).

## SOLUTIONS

| Champ | Type | Contraintes |
|---|---|---|
| id | UUID | PK |
| incident_id | UUID | FK → incidents.id, NOT NULL |
| author_id | UUID | FK → technicians.id, NOT NULL |
| contenu | TEXT | NOT NULL |
| is_documented_by_opener | BOOLEAN | NOT NULL, défaut false |
| created_at | DATETIME | NOT NULL, défaut now() |

Notes :
- `is_documented_by_opener = true` distingue la solution que l'ouvreur rédige lui-même en fermant le ticket (au lieu de sélectionner une réponse d'un collègue).
- Index sur `incident_id` (récupération des solutions d'un incident, requête la plus fréquente).

## STARS

| Champ | Type | Contraintes |
|---|---|---|
| id | UUID | PK |
| solution_id | UUID | FK → solutions.id, NOT NULL |
| voter_id | UUID | FK → technicians.id, NOT NULL |
| created_at | DATETIME | NOT NULL, défaut now() |

Notes :
- **Contrainte unique composite `(solution_id, voter_id)`** — un technicien ne peut étoiler qu'une seule fois la même solution. C'est la contrainte la plus critique du schéma : sans elle, le classement par étoiles devient manipulable.
- Vérification applicative (pas seulement contrainte SQL) : `voter_id != solutions.author_id` pour interdire l'auto-vote.
- Index sur `solution_id` (calcul du nombre d'étoiles par solution, requête fréquente du moteur de classement).

---

## Relations résumées

- Un département a plusieurs techniciens et plusieurs incidents rattachés (1-N).
- Un technicien ouvre plusieurs incidents et propose plusieurs solutions (1-N chacun).
- Un incident reçoit plusieurs solutions (1-N).
- Une solution reçoit plusieurs étoiles, chacune d'un technicien différent (1-N avec contrainte d'unicité).

## Ce qui reste volontairement hors de ce schéma (cf. cahier des charges, section 7)

- Pas de table de notifications (hors périmètre).
- Pas de table d'historique de réattribution (contrairement à FGCL, il n'y a pas d'attribution automatique de ticket ici — l'ouvreur reste propriétaire de bout en bout).
- Pas de partitionnement par département au niveau du schéma — le cloisonnement, quand il existe, est géré en filtre applicatif, pas en table séparée.

## Prochaine étape (J3)

Initialisation de l'environnement de projet et mise en place du `.gitignore` avant toute écriture de code applicatif.
