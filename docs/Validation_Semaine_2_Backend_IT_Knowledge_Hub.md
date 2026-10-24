# Validation — Semaine 2, partie backend (J8 à J12)
### IT Knowledge Hub — Cœur métier : incidents, solutions, fermeture, étoiles

**Objectif de cette portion de semaine** : la plateforme fonctionne comme un vrai outil collaboratif côté backend — déclarer, répondre, fermer avec la règle de propriété, étoiler — avant de construire l'interface visuelle (J13-J14, à venir).

---

## 1. Récapitulatif jour par jour

| Jour | Contenu | Statut |
|---|---|---|
| J8 | CRUD incidents : déclaration, liste (avec filtres statut/département et tri par date), détail. `opened_by` fixé côté serveur, infalsifiable | ✅ Validé |
| J9 | CRUD solutions : proposition par tout technicien (y compris sur un incident qui n'est pas le sien), liste chronologique, refus sur incident fermé | ✅ Validé |
| J10 | **Fermeture de ticket réservée à l'ouvreur** (règle métier centrale) : deux chemins (solution existante retenue, ou solution documentée par l'ouvreur lui-même) | ✅ Validé |
| J11 | Système d'étoiles : `stars_count` calculé, auto-vote interdit, double vote interdit (double filet applicatif + contrainte base) | ✅ Validé |
| J12 | Filtrage par département/statut et tri par date | ✅ Déjà couvert au J8 (implémenté en même temps que la liste des incidents), pas de développement supplémentaire nécessaire |

## 2. Batterie de tests exécutés

34 scénarios exécutés sur les quatre journées, méthodologie identique à la Semaine 1 (un statut par scénario).

### J8 — Incidents (10 scénarios)

| # | Scénario | Résultat | Statut |
|---|---|---|---|
| 1 | Déclaration sans jeton | Rejet 401 | ✅ |
| 2 | Déclaration valide | Création réussie, code 201 | ✅ |
| 3 | `opened_by` correspond au vrai technicien connecté | Conforme | ✅ |
| 4 | Tentative d'injection d'un faux `opened_by` dans la requête | Ignoré, valeur réelle conservée | ✅ |
| 5 | Déclaration par un second technicien dans un autre département | Conforme | ✅ |
| 6 | Visibilité inter-départements (pas de cloisonnement à la consultation) | Conforme | ✅ |
| 7 | Filtrage par département | Conforme | ✅ |
| 8 | Filtrage par statut | Conforme | ✅ |
| 9 | Consultation du détail par un tiers | Conforme | ✅ |
| 10 | Incident inexistant | Rejet 404 | ✅ |

### J9 — Solutions (8 scénarios)

| # | Scénario | Résultat | Statut |
|---|---|---|---|
| 1 | Proposition sans jeton | Rejet 401 | ✅ |
| 2 | Un technicien répond à un incident qui n'est pas le sien | Conforme | ✅ |
| 3 | `author_id` correspond au vrai auteur | Conforme | ✅ |
| 4 | L'ouvreur répond aussi sur son propre incident | Conforme (autorisé) | ✅ |
| 5 | Liste chronologique des solutions | Conforme | ✅ |
| 6 | Réponse sur un incident inexistant | Rejet 404 | ✅ |
| 7 | Réponse sur un incident fermé | Rejet 400 | ✅ |
| 8 | Contenu vide | Rejet 422 | ✅ |

### J10 — Fermeture de ticket (9 scénarios)

| # | Scénario | Résultat | Statut |
|---|---|---|---|
| 1 | **Un non-ouvreur tente de fermer le ticket** | Rejet 403 | ✅ |
| 2 | Fermeture sans jeton | Rejet 401 | ✅ |
| 3 | Fournir les deux champs de fermeture à la fois | Rejet 400 | ✅ |
| 4 | Fournir aucun des deux champs | Rejet 400 | ✅ |
| 5 | Fermeture avec une solution existante retenue | Conforme, statut `ferme` | ✅ |
| 6 | Refermer un ticket déjà fermé | Rejet 400 | ✅ |
| 7 | Fermeture avec solution documentée par l'ouvreur | Conforme, `is_documented_by_opener = true` | ✅ |
| 8 | `accepted_solution_id` pointant vers un autre incident | Rejet 404 | ✅ |
| 9 | Fermeture d'un incident inexistant | Rejet 404 | ✅ |

### J11 — Étoiles (7 scénarios)

| # | Scénario | Résultat | Statut |
|---|---|---|---|
| 1 | **Auto-vote de l'auteur sur sa propre solution** | Rejet 400 | ✅ |
| 2 | Vote sans jeton | Rejet 401 | ✅ |
| 3 | Vote normal | Conforme, `stars_count` incrémenté | ✅ |
| 4 | **Double vote du même technicien sur la même solution** | Rejet 409 | ✅ |
| 5 | Vote d'un troisième technicien différent | Conforme, compteur à jour | ✅ |
| 6 | Cohérence du compteur via la liste des solutions | Conforme | ✅ |
| 7 | Vote sur une solution inexistante | Rejet 404 | ✅ |

**34 scénarios testés, 34 conformes.**

## 3. Points de vigilance confirmés (les plus sensibles du cahier des charges)

- La propriété du ticket (J10) et l'anti-triche du vote (J11) sont les deux règles les plus critiques du projet — toutes deux testées avec des tentatives de contournement actives, pas seulement des cas nominaux.
- La contrainte anti double-vote repose sur **deux couches indépendantes** (vérification applicative + contrainte unique en base), une défense en profondeur plutôt qu'un seul point de contrôle.

## 4. État du dépôt Git

```
1f6e3d1 J11 - Systeme d'etoiles (POST /solutions/id/star), anti auto-vote et anti double-vote
f057d87 J10 - Fermeture de ticket reservee a l'ouvreur, solution existante ou documentee
7708712 J9 - CRUD solutions (proposition, liste), refus sur incident ferme
e4095f6 J8 - CRUD incidents (declaration, liste avec filtres, detail), opened_by fixe cote serveur
932965b Validation Semaine 1 - document de synthese et checklist
```

## 5. Checklist de validation

- [x] Déclaration, consultation et filtrage des incidents opérationnels
- [x] Proposition de solutions par tout technicien, y compris sur un ticket qui n'est pas le sien
- [x] Règle de propriété du ticket vérifiée activement (tentative de contournement testée et bloquée)
- [x] Système d'étoiles avec double protection anti-triche (auto-vote, double vote)
- [x] 34 scénarios de test documentés et conformes

## 6. Prochaine étape

J13-J14 : construction du frontend technicien (inscription/connexion, dashboard, formulaire de déclaration, page de détail avec étoilage et bouton de fermeture réservé à l'ouvreur) — pour rendre visuellement utilisable tout ce qui vient d'être validé côté backend.
