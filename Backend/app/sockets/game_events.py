"""
Eventos específicos del juego para WebSockets
"""
import logging
from typing import Dict, Any
from app.sockets.socket_manager import socket_manager

logger = logging.getLogger(__name__)

class GameEvents:
    """Clase para manejar eventos específicos del juego"""
    
    @staticmethod
    async def notify_game_created(game_id: str, creator_id: str, game_data: Dict[str, Any]):
        """Notificar que se creó un nuevo juego"""
        await socket_manager.send_to_user(creator_id, 'game_created', {
            'game_id': game_id,
            'game_data': game_data
        })
    
    @staticmethod
    async def notify_player_joined(game_id: str, player_id: str, player_data: Dict[str, Any]):
        """Notificar que un jugador se unió al juego"""
        await socket_manager.broadcast_to_game(game_id, 'player_joined_game', {
            'player_id': player_id,
            'player_data': player_data,
            'game_id': game_id
        })
    
    @staticmethod
    async def notify_game_started(game_id: str, game_state: Dict[str, Any]):
        """Notificar que el juego ha comenzado"""
        await socket_manager.broadcast_to_game(game_id, 'game_started', {
            'game_id': game_id,
            'game_state': game_state
        })
    
    @staticmethod
    async def notify_turn_changed(game_id: str, current_player: str, game_state: Dict[str, Any]):
        """Notificar cambio de turno"""
        await socket_manager.broadcast_to_game(game_id, 'turn_changed', {
            'game_id': game_id,
            'current_player': current_player,
            'game_state': game_state
        })
    
    @staticmethod
    async def notify_piece_moved(game_id: str, move_data: Dict[str, Any]):
        """Notificar movimiento de pieza"""
        await socket_manager.broadcast_to_game(game_id, 'piece_moved', {
            'game_id': game_id,
            'move_data': move_data
        })
    
    @staticmethod
    async def notify_piece_captured(game_id: str, capture_data: Dict[str, Any]):
        """Notificar captura de pieza"""
        await socket_manager.broadcast_to_game(game_id, 'piece_captured', {
            'game_id': game_id,
            'capture_data': capture_data
        })
    
    @staticmethod
    async def notify_piece_reached_home(game_id: str, piece_data: Dict[str, Any]):
        """Notificar que una pieza llegó a casa"""
        await socket_manager.broadcast_to_game(game_id, 'piece_reached_home', {
            'game_id': game_id,
            'piece_data': piece_data
        })
    
    @staticmethod
    async def notify_game_finished(game_id: str, winner_data: Dict[str, Any]):
        """Notificar que el juego terminó"""
        await socket_manager.broadcast_to_game(game_id, 'game_finished', {
            'game_id': game_id,
            'winner_data': winner_data
        })
    
    @staticmethod
    async def notify_player_disconnected(game_id: str, player_id: str):
        """Notificar que un jugador se desconectó"""
        await socket_manager.broadcast_to_game(game_id, 'player_disconnected', {
            'game_id': game_id,
            'player_id': player_id
        })
    
    @staticmethod
    async def notify_game_paused(game_id: str, reason: str):
        """Notificar que el juego se pausó"""
        await socket_manager.broadcast_to_game(game_id, 'game_paused', {
            'game_id': game_id,
            'reason': reason
        })
    
    @staticmethod
    async def notify_game_resumed(game_id: str):
        """Notificar que el juego se reanudó"""
        await socket_manager.broadcast_to_game(game_id, 'game_resumed', {
            'game_id': game_id
        })
    
    @staticmethod
    async def notify_chat_message(game_id: str, sender_id: str, message: str):
        """Notificar mensaje de chat"""
        await socket_manager.broadcast_to_game(game_id, 'chat_message', {
            'game_id': game_id,
            'sender_id': sender_id,
            'message': message,
            'timestamp': logger.time()
        })
    
    @staticmethod
    async def notify_error(user_id: str, error_message: str, error_code: str = None):
        """Notificar error a un usuario específico"""
        await socket_manager.send_to_user(user_id, 'game_error', {
            'message': error_message,
            'code': error_code
        })

# Instancia global de eventos de juego
game_events = GameEvents()