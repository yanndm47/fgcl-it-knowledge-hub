"""
Notifications en temps réel — gestionnaire de connexions WebSocket et
fonction centrale de création/diffusion d'une notification.

Principe : une notification est TOUJOURS persistée en base (pour être
consultable même hors ligne, via GET /notifications). Si le destinataire
est connecté au moment précis de l'événement (WebSocket ouvert), elle lui
est en plus poussée immédiatement, sans qu'il ait besoin de recharger la
page.

Détail technique : les routes de ce projet sont écrites en fonctions
SYNCHRONES (def, pas async def), alors qu'envoyer un message sur une
WebSocket est une opération ASYNCHRONE. Le pont entre les deux est
`asyncio.run_coroutine_threadsafe`, qui programme l'envoi sur la boucle
d'événements associée à la connexion, depuis un contexte synchrone.
"""

import asyncio
from typing import Dict, List, Tuple
from fastapi import WebSocket

from database import SessionLocal
from models import Notification


class ConnectionManager:
    def __init__(self):
        # technician_id -> liste de (websocket, boucle d'événements associée)
        self.active: Dict[str, List[Tuple[WebSocket, asyncio.AbstractEventLoop]]] = {}

    async def connect(self, technician_id: str, websocket: WebSocket):
        await websocket.accept()
        loop = asyncio.get_event_loop()
        self.active.setdefault(technician_id, []).append((websocket, loop))

    def disconnect(self, technician_id: str, websocket: WebSocket):
        conns = self.active.get(technician_id, [])
        self.active[technician_id] = [c for c in conns if c[0] is not websocket]

    def push(self, technician_id: str, payload: dict):
        """Envoie 'payload' à toutes les connexions actives de ce technicien (0, 1 ou plusieurs onglets)."""
        for ws, loop in self.active.get(technician_id, []):
            try:
                asyncio.run_coroutine_threadsafe(ws.send_json(payload), loop)
            except Exception:
                pass  # une connexion fermée entre-temps ne doit jamais faire planter la route appelante


manager = ConnectionManager()


def create_notification(db, recipient_id: str, notif_type: str, message: str, related_incident_id: str | None = None):
    """
    Crée une notification en base et la pousse en direct si possible.
    'recipient_id' peut être None (ex. auteur inconnu) -> ne fait rien
    silencieusement plutôt que de planter la route appelante.
    """
    if not recipient_id:
        return None

    notif = Notification(
        recipient_id=recipient_id, type=notif_type, message=message,
        related_incident_id=related_incident_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    manager.push(recipient_id, {
        "id": notif.id, "type": notif.type, "message": notif.message,
        "related_incident_id": notif.related_incident_id,
        "created_at": notif.created_at.isoformat(),
    })
    return notif
