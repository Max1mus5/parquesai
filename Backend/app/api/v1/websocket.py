"""
Endpoints para WebSocket y comunicación en tiempo real
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.db.models.user import User
from app.sockets.socket_manager import socket_manager
from app.sockets.game_events import game_events

router = APIRouter(prefix="/websocket", tags=["websocket"])

@router.get("/info")
async def websocket_info():
    """Información sobre el sistema WebSocket"""
    return {
        "status": "active",
        "connected_users": len(socket_manager.session_users),
        "active_games": len(socket_manager.game_rooms),
        "events_available": [
            "connect", "disconnect", "join_game", "leave_game",
            "make_move", "roll_dice", "pass_turn"
        ]
    }

@router.get("/connected-users")
async def get_connected_users(current_user: User = Depends(get_current_user)):
    """Obtener usuarios conectados (solo para usuarios autenticados)"""
    return {
        "connected_users": list(socket_manager.session_users.values()),
        "total": len(socket_manager.session_users)
    }

@router.get("/game/{game_id}/connected")
async def get_game_connected_users(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """Obtener usuarios conectados en un juego específico"""
    connected_users = socket_manager.get_connected_users_in_game(game_id)
    return {
        "game_id": game_id,
        "connected_users": connected_users,
        "total": len(connected_users)
    }

@router.post("/broadcast/{game_id}")
async def broadcast_to_game(
    game_id: str,
    message: dict,
    current_user: User = Depends(get_current_user)
):
    """Enviar mensaje broadcast a un juego (solo para testing)"""
    try:
        await socket_manager.broadcast_to_game(
            game_id, 
            "admin_message", 
            {
                "message": message,
                "sender": current_user.username,
                "timestamp": "now"
            }
        )
        return {"success": True, "message": "Mensaje enviado"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando mensaje: {str(e)}"
        )