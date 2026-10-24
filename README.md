# IT Knowledge Hub

Plateforme collaborative de capitalisation et de résolution des incidents informatiques,
intégrant un chatbot capable d'analyser une demande, de rechercher les incidents
similaires déjà résolus, et de recommander les solutions les plus pertinentes à
partir de leur taux de validation.

Projet académique réalisé à FGCL, en continuité du chatbot d'assistance FGCL
(voir `docs/` pour le cahier des charges complet et le planning des 30 jours).

## Statut actuel (Jour 3)

Squelette de projet uniquement — structure de dossiers, dépendances et
environnement en place. Aucune fonctionnalité métier n'est encore implémentée
(voir le planning des 30 jours pour le détail jour par jour).

## Architecture

```
it-knowledge-hub/
├── .env.example              Modèle de variables d'environnement (à copier en .env)
├── .gitignore                 Exclut venv/, chroma_db/, .env, __pycache__/, *.db
├── requirements.txt            Dépendances de production
├── README.md
│
├── backend/
│   ├── main.py                 Point d'entrée FastAPI (squelette, routers à venir)
│   ├── database.py              Connexion SQLAlchemy (à implémenter J4)
│   ├── models.py                 Modèles ORM des 5 tables (à implémenter J4)
│   ├── schemas.py                 Schémas Pydantic de requête/réponse
│   └── routers/                    Un module par domaine (auth, incidents, solutions, chatbot)
│
├── frontend/
│   ├── index.html               Page d'accueil (squelette)
│   └── style.css
│
├── docs/                        Cahier des charges, schéma de base de données, planning
└── knowledge_base/              Réservé si besoin de documents de référence complémentaires
```

## Installation

1. `python -m venv venv` puis activation (`venv\Scripts\activate` sous Windows, `source venv/bin/activate` sous Linux/Mac)
2. `pip install -r requirements.txt`
3. Copier `.env.example` en `.env` et renseigner les vraies valeurs (clé Gemini, clé JWT)

## Lancement (développement local)

**Backend :**
```
cd backend
uvicorn main:app --reload
```
Vérifier que l'API répond : `http://127.0.0.1:8000/health`

**Frontend :**
```
cd frontend
python -m http.server 5500
```
Puis ouvrir `http://127.0.0.1:5500/index.html`

## Documentation

- `docs/Cahier_des_charges_IT_Knowledge_Hub.docx` — spécifications complètes, état des lieux, planning des 30 jours
- `docs/J2_Modelisation_Base_Donnees.md` — schéma relationnel détaillé

## Sécurité — point de vigilance dès le départ

Leçon tirée du projet précédent (chatbot FGCL) : le `.gitignore` doit exclure
la base de données et le `.env` **avant le premier commit**, pas après — une
correction a posteriori ne supprime pas l'historique Git déjà exposé.
