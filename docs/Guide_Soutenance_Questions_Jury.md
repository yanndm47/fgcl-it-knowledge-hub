# Guide de soutenance — Simulation de questions du jury
### IT Knowledge Hub

**Principe** : pour chaque question, la meilleure réponse part toujours d'une décision assumée, pas d'une excuse. Le jury valorise "j'ai choisi X plutôt que Y pour telle raison, et j'assume les limites que ça implique" bien plus qu'une justification défensive.

---

## 1. Questions sur les choix d'architecture

**Q : Pourquoi SQLite plutôt que PostgreSQL, pour un système qui gère des comptes utilisateurs ?**
> SQLite est amplement suffisant pour le volume d'un projet académique en 30 jours — pas de serveur de base de données à administrer, un simple fichier. La migration vers PostgreSQL est explicitement documentée comme perspective d'évolution dans le cahier des charges, pas oubliée : elle serait nécessaire pour un usage à plus grande échelle, avec des accès concurrents importants, ce que SQLite gère moins bien.

**Q : Pourquoi avoir remplacé la balise auto-déclarée du LLM (comme sur FGCL) par une décision algorithmique ?**
> Sur FGCL, une balise comme `[URGENCE_DETECTEE]` demandait au LLM lui-même de juger une situation — avec le risque qu'il se trompe ou "invente" une urgence qui n'existe pas. Ici, la question "y a-t-il une correspondance suffisante ?" est vitale pour la fiabilité du système : je l'ai donc tranchée par un calcul déterministe (seuil de distance cosinus), pas par un jugement du modèle génératif. C'est plus fiable, et surtout entièrement testable sans réseau.

**Q : Comment avez-vous calibré le seuil de similarité de 0,63 ?**
> Ce seuil est repris comme point de départ du chatbot FGCL, où il avait déjà été calibré empiriquement. Un script de diagnostic (`debug_search.py`) permet de l'ajuster avec de vraies données une fois que la base de connaissances grossit — c'est un paramètre vivant, pas une valeur figée définitivement.

**Q : Pourquoi le score combiné utilise-t-il ces poids précis (0,4 / 0,3 / 0,2 / 0,1) et pas d'autres ?**
> Ce sont des poids de départ, documentés comme tels dans le cahier des charges dès le J1, avec l'intention explicite de les ajuster une fois des données réelles disponibles — exactement la même démarche que pour le seuil de similarité. La hiérarchie retenue reflète une priorité assumée : une solution officiellement validée par son auteur (0,4) doit peser plus qu'un simple nombre d'étoiles (0,3), qui lui-même doit compter plus que la simple proximité sémantique (0,2).

## 2. Questions sur la sécurité

**Q : Comment empêchez-vous un technicien de fermer le ticket de quelqu'un d'autre ?**
> Une vérification stricte côté serveur : `incident.opened_by != current.id`. Ce n'est jamais une question d'interface qui cache un bouton — même un appel direct à l'API avec un jeton valide d'un autre technicien échoue avec un code 403. Ce point précis a été testé par une tentative de contournement active, pas seulement par un cas nominal.

**Q : Que se passe-t-il si deux techniciens étoilent la même solution en même temps ?**
> La contrainte est posée à deux niveaux indépendants : une vérification applicative (interroger la base avant d'insérer), et une contrainte unique physique directement dans la table `stars` sur `(solution_id, voter_id)`. Même en cas de requêtes simultanées, la base de données elle-même refuse le doublon — le second insert lève une erreur d'intégrité, rattrapée proprement et renvoyée comme un 409.

**Q : Les mots de passe sont-ils vraiment protégés ?**
> Hachés avec bcrypt avant tout stockage — jamais en clair, jamais réversible. `password_hash` est explicitement exclu de tous les schémas de réponse de l'API, donc même une erreur de programmation ne pourrait pas l'exposer accidentellement par une route.

**Q : Que se passe-t-il si la clé Gemini est absente ou invalide ?**
> Le serveur ne plante pas : l'erreur est interceptée et renvoyée comme un code 503 avec un message explicite, jamais une trace d'erreur brute. Le reste de l'application (déclarer un incident, consulter l'historique) continue de fonctionner même si la génération de réponse est indisponible.

## 3. Questions sur le périmètre et les limites

**Q : Pourquoi n'y a-t-il pas de fonctionnalité de mot de passe oublié alors que la page existe ?**
> La page a été construite visuellement pour rester fidèle à la maquette fournie, mais la vraie logique d'envoi d'email n'a jamais fait partie du périmètre des 30 jours. Le choix a été de ne pas simuler une fonctionnalité qui n'existe pas — la page l'indique d'ailleurs explicitement plutôt que de faire semblant.

**Q : Le tableau de bord administrateur est très simple comparé à votre propre maquette. Pourquoi ?**
> La maquette prévoit un vrai module d'analytics (statistiques, graphiques d'évolution, catégories) qui suppose des endpoints backend d'agrégation qui n'ont pas été développés dans ce cycle. Le périmètre actuel de l'administration — valider ou rejeter les comptes — correspond exactement à la consigne "pas d'open space" de l'encadreur, qui était l'exigence prioritaire.

**Q : Le système a-t-il été testé à grande échelle (des milliers d'incidents) ?**
> Non, et ce n'est pas prétendu. Le projet a ajouté des index de base de données sur les colonnes les plus filtrées, et un pipeline d'indexation incrémentale plutôt qu'une reconstruction totale (contrairement à FGCL), précisément en anticipation d'une croissance de la base — mais aucun test de charge réel n'a été mené, faute de volume de données réelles disponible en 30 jours.

## 4. Questions pièges / déstabilisantes

**Q : Vous avez rencontré beaucoup de bugs — est-ce que ça ne montre pas un manque de maîtrise ?**
> C'est l'inverse : chaque bug est documenté avec sa cause réelle et sa correction, pas caché. Un projet qui touche à des composants externes changeants (un SDK qui se fait déprécier en cours de route, un modèle retiré du catalogue, une bibliothèque tierce incompatible) rencontre nécessairement des frictions — la vraie compétence, c'est de les diagnostiquer et de les corriger rapidement, ce qui a été fait à chaque fois avant la livraison suivante.

**Q : Pourquoi votre seuil de similarité pourrait-il ne pas bien fonctionner en production ?**
> Il a été calibré sur un volume de test très faible. Avec des formulations très différentes d'un même problème (paraphrases, fautes de frappe, vocabulaire différent), le modèle peut manquer une correspondance pertinente ou, à l'inverse, en remonter une non pertinente. C'est documenté comme un point à recalibrer avec de vraies données d'usage — pas une garantie de perfection.

**Q : Si je supprime un compte technicien qui a ouvert des incidents, que se passe-t-il ?**
> Cette situation n'a pas de mécanisme de gestion dédié dans le système actuel — seul le rejet d'un compte encore en attente (`pending`) est prévu, pas la suppression d'un compte déjà actif avec un historique. C'est une vraie limite à mentionner honnêtement si la question est posée, plutôt qu'une réponse inventée.

**Q : Qu'est-ce qui vous a le plus surpris dans ce projet ?**
> Le bug de la distance cosinus (J19) : le système fonctionnait sans erreur, répondait correctement à toutes les requêtes, mais ne trouvait jamais aucune correspondance — parce que ChromaDB utilisait silencieusement une méthode de calcul de distance différente de celle sur laquelle le seuil avait été calibré. Aucune exception, aucun message d'erreur : juste un mauvais résultat. Ce type de bug silencieux est le plus dangereux, et le plus formateur à déboguer.

## 5. Conseils de posture pendant la soutenance

- **Ne jamais dire "je ne sais pas" sec.** Reformuler : "Ce point précis n'a pas été creusé dans ce cycle de 30 jours, mais voici comment je l'aborderais : ..."
- **Assumer les limites avant qu'on te les reproche.** Les mentionner soi-même dans la présentation (déjà fait, slide 11) désamorce la question avant qu'elle ne devienne un piège.
- **Toujours répondre par une décision, jamais par une excuse.** "J'ai choisi X parce que Y" plutôt que "je n'ai pas eu le temps de faire X".
- **Si une question porte sur un point que tu ne maîtrises plus précisément** (ex. un détail du J8 alors que tu es au J26), il est tout à fait honnête de dire : "laisse-moi vérifier le code exact" plutôt que d'improviser une réponse fausse.
