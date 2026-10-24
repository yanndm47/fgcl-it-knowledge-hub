"""
Routes de consultation des notifications, et point d'entrée WebSocket
pour les recevoir en temps réel.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from database import get_db
from models import Notification, Technician
from schemas import NotificationOut
from dependencies import get_current_technician
from jwt_utils import decode_access_token
from notifications import manager

router = APIRouter()


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """Les 50 notifications les plus récentes du technicien connecté, les plus récentes en premier."""
    return (
        db.query(Notification)
        .filter(Notification.recipient_id == current.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current: Technician = Depends(get_current_technician),
):
    """Marque une notification comme lue — uniquement la sienne."""
    notif = db.get(Notification, notification_id)
    if notif is None or notif.recipient_id != current.id:
        raise HTTPException(status_code=404, detail="Notification introuvable")
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


@router.websocket("/ws")
async def notifications_websocket(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """
    Connexion WebSocket pour recevoir les notifications en direct.

    Le jeton JWT est passé en paramètre d'URL (?token=...) et non dans un
    en-tête HTTP : l'API JavaScript native `new WebSocket(url)` du
    navigateur ne permet pas d'ajouter d'en-têtes personnalisés à la
    poignée de main WebSocket, contrairement à un fetch() classique.
    """
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=4401)
        return

    technician_id = payload.get("sub")
    technician = db.get(Technician, technician_id)
    if technician is None:
        await websocket.close(code=4401)
        return

    await manager.connect(technician_id, websocket)
    try:
        while True:
            # On ne fait rien de ce que le client pourrait envoyer — cette
            # connexion ne sert qu'à RECEVOIR des notifications, jamais à
            # en envoyer. On attend juste pour garder la connexion ouverte.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(technician_id, websocket)
