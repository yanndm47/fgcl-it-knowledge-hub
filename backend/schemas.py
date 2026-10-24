"""
Schémas Pydantic — définissent la forme exacte des données reçues et
renvoyées par l'API. FastAPI les utilise pour valider automatiquement
les requêtes (ex. rejeter un email mal formé) sans qu'on écrive cette
vérification à la main.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class TechnicianCreate(BaseModel):
    """Données attendues dans le corps de la requête POST /auth/register."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128, description="8 caractères minimum")
    department_id: str


class TechnicianOut(BaseModel):
    """
    Données renvoyées après une inscription réussie.
    Ne contient JAMAIS password_hash : Pydantic ne renvoie que les champs
    listés ici, même si l'objet Technician complet en contient davantage.
    """
    id: str
    email: str
    status: str
    role: str
    department_id: str
    created_at: datetime
    nom_complet: str | None = None
    site: str | None = None
    telephone: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TechnicianUpdate(BaseModel):
    """Champs de profil modifiables — tous optionnels, l'email et le mot de passe ont leurs propres circuits dédiés."""
    nom_complet: str | None = Field(default=None, max_length=150)
    site: str | None = Field(default=None, max_length=100)
    telephone: str | None = Field(default=None, max_length=30)


class DepartmentOut(BaseModel):
    """Données renvoyées pour un département — utilisé pour peupler les formulaires du frontend."""
    id: str
    nom: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Réponse renvoyée après une connexion réussie."""
    access_token: str
    token_type: str = "bearer"


class IncidentCreate(BaseModel):
    """Données attendues pour déclarer un incident (POST /incidents)."""
    titre: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    symptomes: str = Field(min_length=1, max_length=5000)
    contexte: str | None = None
    department_id: str


class IncidentOut(BaseModel):
    """Données renvoyées pour un incident."""
    id: str
    titre: str
    description: str
    symptomes: str
    contexte: str | None
    department_id: str
    opened_by: str
    status: str
    accepted_solution_id: str | None
    created_at: datetime
    closed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class IncidentCreateResponse(IncidentOut):
    """
    Réponse spécifique à la création d'un incident : identique à IncidentOut,
    avec en plus la liste des incidents quasi identiques déjà en base (s'il
    y en a) — un simple avertissement, la création n'est jamais bloquée.
    """
    possible_duplicates: list[str] = []


class SolutionCreate(BaseModel):
    """Données attendues pour proposer une solution (POST /incidents/{id}/solutions)."""
    contenu: str = Field(min_length=1, max_length=5000)


class SolutionOut(BaseModel):
    """Données renvoyées pour une solution."""
    id: str
    incident_id: str
    author_id: str
    contenu: str
    is_documented_by_opener: bool
    created_at: datetime
    stars_count: int

    model_config = ConfigDict(from_attributes=True)


class ChatbotQuery(BaseModel):
    """Question ou incident soumis au chatbot."""
    message: str = Field(min_length=3, max_length=1000)


class ChatbotSolutionOut(BaseModel):
    """Une solution recommandée par le chatbot, avec son score et son statut."""
    solution: SolutionOut
    score: float
    is_accepted: bool


class ChatbotResponse(BaseModel):
    """Réponse complète du chatbot."""
    found_match: bool
    message: str
    solutions: list[ChatbotSolutionOut]


class IncidentClose(BaseModel):
    """
    Données pour fermer un incident. Exactement UN des deux champs doit être
    fourni, jamais les deux, jamais aucun :
    - accepted_solution_id : la solution d'un collègue, choisie comme la bonne réponse
    - own_solution_content : l'ouvreur a trouvé lui-même la solution (ailleurs,
      ou en la documentant après coup) et la rédige à la fermeture
    """
    accepted_solution_id: str | None = None
    own_solution_content: str | None = None


class NotificationOut(BaseModel):
    """Une notification, telle que renvoyée par l'API."""
    id: str
    type: str
    message: str
    related_incident_id: str | None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ForgotPasswordRequest(BaseModel):
    """Email pour lequel demander un lien de réinitialisation."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Jeton de réinitialisation + nouveau mot de passe."""
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class ActivityStatsOut(BaseModel):
    """Statistiques agrégées d'un technicien."""
    incidents_opened: int
    incidents_resolved: int
    solutions_authored: int
    stars_given: int
    stars_received: int


class ActivityFeedItemOut(BaseModel):
    """Un événement du fil d'activité."""
    type: str
    description: str
    date: datetime
    related_incident_id: str | None


class ActivityOut(BaseModel):
    """Réponse complète de la page Historique : stats + fil d'activité."""
    stats: ActivityStatsOut
    feed: list[ActivityFeedItemOut]


class AdminOverviewOut(BaseModel):
    """Les 4 chiffres clés du tableau de bord admin."""
    active_technicians: int
    total_incidents: int
    incidents_this_month: int
    resolution_rate: int


class MonthCountOut(BaseModel):
    month: str
    count: int


class DepartmentCountOut(BaseModel):
    name: str
    count: int


class AdminStatsOut(BaseModel):
    """Réponse complète du tableau de bord admin analytique."""
    overview: AdminOverviewOut
    incidents_by_month: list[MonthCountOut]
    top_departments: list[DepartmentCountOut]
