"""
Modèles ORM SQLAlchemy — traduction en code du schéma défini au J2
(voir docs/J2_Modelisation_Base_Donnees.md pour le détail de chaque champ).
"""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def generate_uuid() -> str:
    """Génère un identifiant unique universel (UUID) sous forme de texte."""
    return str(uuid.uuid4())


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    nom: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    technicians: Mapped[List["Technician"]] = relationship(back_populates="department")
    incidents: Mapped[List["Incident"]] = relationship(back_populates="department")


class Technician(Base):
    __tablename__ = "technicians"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending | actif
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="technicien")  # technicien | admin
    department_id: Mapped[str] = mapped_column(String(36), ForeignKey("departments.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Champs de profil, tous optionnels : un compte reste utilisable sans
    # les avoir renseignés, ils ne servent qu'à personnaliser l'affichage.
    nom_complet: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    site: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    telephone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    department: Mapped["Department"] = relationship(back_populates="technicians")
    incidents_opened: Mapped[List["Incident"]] = relationship(
        back_populates="opener", foreign_keys="Incident.opened_by"
    )
    solutions: Mapped[List["Solution"]] = relationship(back_populates="author")
    stars: Mapped[List["Star"]] = relationship(back_populates="voter")
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="technician")


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    symptomes: Mapped[str] = mapped_column(Text, nullable=False)
    contexte: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    department_id: Mapped[str] = mapped_column(String(36), ForeignKey("departments.id"), nullable=False, index=True)
    opened_by: Mapped[str] = mapped_column(String(36), ForeignKey("technicians.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ouvert", index=True)  # ouvert | ferme
    accepted_solution_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("solutions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    department: Mapped["Department"] = relationship(back_populates="incidents")
    opener: Mapped["Technician"] = relationship(back_populates="incidents_opened", foreign_keys=[opened_by])
    solutions: Mapped[List["Solution"]] = relationship(
        back_populates="incident", foreign_keys="Solution.incident_id"
    )
    accepted_solution: Mapped[Optional["Solution"]] = relationship(foreign_keys=[accepted_solution_id])


class Solution(Base):
    __tablename__ = "solutions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id"), nullable=False, index=True)
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("technicians.id"), nullable=False)
    contenu: Mapped[str] = mapped_column(Text, nullable=False)
    is_documented_by_opener: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    incident: Mapped["Incident"] = relationship(back_populates="solutions", foreign_keys=[incident_id])
    author: Mapped["Technician"] = relationship(back_populates="solutions")
    stars: Mapped[List["Star"]] = relationship(back_populates="solution")

    @property
    def stars_count(self) -> int:
        """Nombre d'étoiles reçues par cette solution — calculé, pas stocké en base."""
        return len(self.stars)


class Star(Base):
    __tablename__ = "stars"
    __table_args__ = (UniqueConstraint("solution_id", "voter_id", name="uq_solution_voter"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    solution_id: Mapped[str] = mapped_column(String(36), ForeignKey("solutions.id"), nullable=False, index=True)
    voter_id: Mapped[str] = mapped_column(String(36), ForeignKey("technicians.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    solution: Mapped["Solution"] = relationship(back_populates="stars")
    voter: Mapped["Technician"] = relationship(back_populates="stars")


class Notification(Base):
    """
    Une notification adressée à un technicien précis (nouvelle réponse sur
    son incident, étoile reçue, ticket fermé avec sa solution, compte
    validé...). Toujours persistée en base, ET poussée en direct par
    WebSocket si le destinataire est connecté au moment de l'événement.
    """
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    recipient_id: Mapped[str] = mapped_column(String(36), ForeignKey("technicians.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False)  # new_solution | new_star | incident_closed | account_approved
    message: Mapped[str] = mapped_column(Text, nullable=False)
    related_incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id"), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Favorite(Base):
    """
    Un incident marqué comme favori par un technicien — accès rapide
    depuis la page Favoris, sans devoir refouiller la liste complète.
    Même principe anti-doublon que Star : un technicien ne peut mettre
    en favori le même incident qu'une seule fois.
    """
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("technician_id", "incident_id", name="uq_technician_incident_favorite"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    technician_id: Mapped[str] = mapped_column(String(36), ForeignKey("technicians.id"), nullable=False, index=True)
    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    technician: Mapped["Technician"] = relationship(back_populates="favorites")
    incident: Mapped["Incident"] = relationship()
