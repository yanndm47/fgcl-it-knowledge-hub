# État actuel du projet et feuille de route
### IT Knowledge Hub — document de référence pour la remise

**Objectif de ce document** : donner une vue exacte et honnête de ce qui fonctionne aujourd'hui dans le projet, par opposition à ce qui est prévu mais pas encore construit — à présenter tel quel si le jury demande "où en êtes-vous exactement, et que reste-t-il à faire ?"

---

## 1. Ce qui est entièrement fonctionnel aujourd'hui

### 1.1 Le socle des 30 jours (J1 à J30)

- Authentification complète : inscription self-service, validation admin obligatoire ("pas d'open space"), connexion par jeton JWT.
- Cycle complet d'un incident : déclaration, réponses de n'importe quel technicien, étoiles (anti-triche à deux niveaux), fermeture réservée strictement à l'ouvreur du ticket.
- Chatbot intelligent complet : indexation vectorielle incrémentale, recherche par similarité (distance cosinus calibrée), classement des solutions par score combiné, génération de la recommandation par Gemini.
- Frontend complet sur la charte graphique officielle FGCL (sidebar, couleurs, typographie).
- Sécurité auditée (J22), tests de bout en bout automatisés (J23, `test_e2e.py`), optimisations (index de base de données, détection de doublons).
- Documentation complète : cahier des charges, rapport de projet, slides de soutenance, guide de questions du jury, checklist du jour J, script de données de démonstration.

### 1.2 Extensions construites après le J30, sur demande

| Extension | Statut | Détail |
|---|---|---|
| **Notifications en temps réel** | ✅ Fonctionnelle | WebSocket (`/notifications/ws`), cloche avec badge, 4 événements déclencheurs (nouvelle réponse, étoile, fermeture, compte validé) |
| **Réinitialisation de mot de passe** | ✅ Fonctionnelle | Jeton dédié à courte durée de vie (15 min), lien affiché dans la console du serveur (pas de serveur d'email réel) |
| **Historique d'activité** | ✅ Fonctionnelle | Statistiques personnelles + fil chronologique (`/auth/me/activity`) |
| **Dashboard admin analytique** | ✅ Fonctionnelle | Vue d'ensemble, graphique d'évolution sur 6 mois, top départements (`/admin/stats`) |
| **Profil utilisateur (onglet Informations)** | ✅ Fonctionnelle | Nom complet, site, téléphone modifiables (`PATCH /auth/me`) |
| **Base de connaissances** | ✅ Fonctionnelle | Réutilise les incidents déjà résolus comme "articles", classés par département, avec recherche |
| **Favoris** | ✅ Fonctionnelle | Marquer/retirer un incident en favori, page dédiée |

## 2. Travail en cours — prévu mais pas encore livré

Ces éléments sont **visibles dans l'interface** (menu de la sidebar, onglets) mais **désactivés avec une info-bulle honnête**, plutôt que simulés comme fonctionnels. Voici le détail de ce que chacun impliquera, pour que la planification reste visible même sans le code.

### 2.1 Page "Problèmes" (gestion des causes racines, au sens ITIL)

**Principe** : un "problème" est la cause racine potentiellement commune à plusieurs incidents (ex. un switch défectueux qui cause 5 incidents wifi différents sur une semaine). Distinct d'un incident : il peut rester ouvert pendant qu'on l'investigue, et plusieurs incidents viennent s'y rattacher au fil du temps.

**Modèle de données prévu** : une nouvelle table `problems` (titre, description, statut ouvert/résolu, cause racine, créateur, département, dates), et un champ `problem_id` optionnel ajouté à la table `incidents` existante.

**Routes prévues** : création, liste, détail (avec les incidents rattachés), mise à jour (documenter la cause racine, résoudre), rattachement/détachement d'un incident à un problème.

**Frontend prévu** : une page de liste + création, une page de détail avec les incidents liés, et un petit sélecteur sur chaque incident pour le rattacher à un problème existant.

### 2.2 Onglets "Préférences" et "Notifications" du profil

- **Préférences** : un réglage réellement actionnable — activer/désactiver la réception des notifications (`notifications_enabled` sur le compte), respecté par le système d'notifications déjà construit.
- **Notifications** (dans le profil) : un historique complet et consultable de toutes les notifications reçues, au-delà du menu déroulant de la cloche qui n'en montre qu'un aperçu.

### 2.3 Onglets "Timeline", "Pièces jointes" et "Commentaires" sur chaque incident

- **Commentaires** (prioritaire) : un espace d'échange libre sur un incident, distinct d'une "solution" — poser une question, préciser un point, documenter une piste, sans prétendre avoir résolu le problème. Déclenche une notification à l'ouvreur du ticket, sur le même principe que les solutions.
- **Timeline** : une frise chronologique reconstituée à partir des données déjà en base (déclaration, chaque solution proposée, chaque commentaire, fermeture) — aucune nouvelle donnée à stocker, juste un assemblage et un tri de ce qui existe déjà.
- **Pièces jointes** : upload de fichiers (capture d'écran, log, document) sur un incident, avec stockage sur disque, limite de taille (5 Mo) et liste blanche de types de fichiers autorisés pour la sécurité.

## 3. Pourquoi ces 5 éléments ne sont pas encore livrés

Un incident technique a interrompu leur construction à plusieurs reprises pendant la dernière session de travail (réinitialisations de l'environnement de développement), et le délai avant la remise ne permettait pas de les reconstruire avec le même niveau de rigueur de test que le reste du projet. Plutôt que de livrer du code non testé à la dernière minute — ce qui va à l'encontre de toute la méthodologie appliquée depuis le J1 — le choix a été de les documenter précisément comme prochaine étape, et de garder la version actuelle, stable et entièrement testée, pour la remise.

## 4. Comment en parler en soutenance

Si la question arrive, la réponse la plus solide est de présenter ce document tel quel : une planification précise (modèle de données, routes, répartition frontend/backend) existe déjà pour chacun de ces 5 éléments, seule l'implémentation reste à faire — ce qui démontre une méthode de conception, pas une improvisation de dernière minute.
