"""
Gestor de WebSockets con Socket.io para comunicación en tiempo real
"""
import socketio
import logging
from typing import Dict, List, Optional
from app.core.config import settings
from app.services.game_service import GameService
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

class SocketManager:
    """Gestor de conexiones WebSocket"""
    
    def __init__(self):
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True
        )
        self.game_service = GameService()
        self.auth_service = AuthService()
        
        # Diccionarios para gestionar conexiones
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.session_users: Dict[str, str] = {}  # session_id -> user_id
        self.game_rooms: Dict[str, List[str]] = {}  # game_id -> [session_ids]
        
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Configurar manejadores de eventos Socket.io"""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            """Manejar nueva conexión"""
            logger.info(f"Cliente conectado: {sid}")
            
            # Verificar autenticación si se proporciona token
            if auth and 'token' in auth:
                try:
                    user_data = await self.auth_service.verify_token(auth['token'])
                    if user_data:
                        user_id = str(user_data.id)
                        self.user_sessions[user_id] = sid
                        self.session_users[sid] = user_id
                        logger.info(f"Usuario autenticado: {user_id} -> {sid}")
                        
                        # Notificar al cliente que está autenticado
                        await self.sio.emit('authenticated', {
                            'user_id': user_id,
                            'username': user_data.username
                        }, room=sid)
                except Exception as e:
                    logger.error(f"Error en autenticación: {e}")
            
            return True
        
        @self.sio.event
        async def disconnect(sid):
            """Manejar desconexión"""
            logger.info(f"Cliente desconectado: {sid}")
            
            # Limpiar sesión
            if sid in self.session_users:
                user_id = self.session_users[sid]
                del self.session_users[sid]
                if user_id in self.user_sessions:
                    del self.user_sessions[user_id]
                
                # Remover de salas de juego
                for game_id, sessions in self.game_rooms.items():
                    if sid in sessions:
                        sessions.remove(sid)
                        # Notificar a otros jugadores
                        await self.sio.emit('player_disconnected', {
                            'user_id': user_id,
                            'game_id': game_id
                        }, room=game_id)
        
        @self.sio.event
        async def join_game(sid, data):
            """Unirse a una sala de juego"""
            try:
                game_id = data.get('game_id')
                if not game_id:
                    await self.sio.emit('error', {'message': 'game_id requerido'}, room=sid)
                    return
                
                # Verificar que el usuario esté autenticado
                if sid not in self.session_users:
                    await self.sio.emit('error', {'message': 'Usuario no autenticado'}, room=sid)
                    return
                
                user_id = self.session_users[sid]
                
                # Verificar que el juego existe y el usuario es parte de él
                game = await self.game_service.get_game(game_id)
                if not game:
                    await self.sio.emit('error', {'message': 'Juego no encontrado'}, room=sid)
                    return
                
                # Unirse a la sala
                await self.sio.enter_room(sid, game_id)
                
                # Agregar a la lista de sesiones del juego
                if game_id not in self.game_rooms:
                    self.game_rooms[game_id] = []
                if sid not in self.game_rooms[game_id]:
                    self.game_rooms[game_id].append(sid)
                
                logger.info(f"Usuario {user_id} se unió al juego {game_id}")
                
                # Notificar al cliente y otros jugadores
                await self.sio.emit('joined_game', {
                    'game_id': game_id,
                    'user_id': user_id
                }, room=sid)
                
                await self.sio.emit('player_joined', {
                    'user_id': user_id,
                    'game_id': game_id
                }, room=game_id, skip_sid=sid)
                
                # Enviar estado actual del juego
                game_state = await self.game_service.get_game_state(game_id)
                await self.sio.emit('game_state_update', game_state, room=sid)
                
            except Exception as e:
                logger.error(f"Error al unirse al juego: {e}")
                await self.sio.emit('error', {'message': 'Error interno del servidor'}, room=sid)
        
        @self.sio.event
        async def leave_game(sid, data):
            """Salir de una sala de juego"""
            try:
                game_id = data.get('game_id')
                if not game_id:
                    return
                
                user_id = self.session_users.get(sid)
                
                # Salir de la sala
                await self.sio.leave_room(sid, game_id)
                
                # Remover de la lista de sesiones
                if game_id in self.game_rooms and sid in self.game_rooms[game_id]:
                    self.game_rooms[game_id].remove(sid)
                
                logger.info(f"Usuario {user_id} salió del juego {game_id}")
                
                # Notificar a otros jugadores
                if user_id:
                    await self.sio.emit('player_left', {
                        'user_id': user_id,
                        'game_id': game_id
                    }, room=game_id)
                
            except Exception as e:
                logger.error(f"Error al salir del juego: {e}")
        
        @self.sio.event
        async def make_move(sid, data):
            """Realizar un movimiento en el juego"""
            try:
                if sid not in self.session_users:
                    await self.sio.emit('error', {'message': 'Usuario no autenticado'}, room=sid)
                    return
                
                user_id = self.session_users[sid]
                game_id = data.get('game_id')
                piece_id = data.get('piece_id')
                dice_value = data.get('dice_value')
                
                if not all([game_id, piece_id is not None, dice_value]):
                    await self.sio.emit('error', {'message': 'Datos incompletos'}, room=sid)
                    return
                
                # Realizar el movimiento usando el servicio de juego
                result = await self.game_service.make_move(
                    game_id=game_id,
                    user_id=int(user_id),
                    piece_id=piece_id,
                    dice_value=dice_value
                )
                
                if result['success']:
                    # Notificar a todos los jugadores del juego
                    await self.sio.emit('move_made', {
                        'user_id': user_id,
                        'game_id': game_id,
                        'piece_id': piece_id,
                        'dice_value': dice_value,
                        'new_position': result.get('new_position'),
                        'game_state': result.get('game_state')
                    }, room=game_id)
                    
                    # Si el juego terminó, notificar
                    if result.get('game_finished'):
                        await self.sio.emit('game_finished', {
                            'winner': result.get('winner'),
                            'game_id': game_id
                        }, room=game_id)
                else:
                    await self.sio.emit('move_error', {
                        'message': result.get('message', 'Movimiento inválido')
                    }, room=sid)
                
            except Exception as e:
                logger.error(f"Error al realizar movimiento: {e}")
                await self.sio.emit('error', {'message': 'Error interno del servidor'}, room=sid)
        
        @self.sio.event
        async def roll_dice(sid, data):
            """Lanzar dados"""
            try:
                if sid not in self.session_users:
                    await self.sio.emit('error', {'message': 'Usuario no autenticado'}, room=sid)
                    return
                
                user_id = self.session_users[sid]
                game_id = data.get('game_id')
                
                if not game_id:
                    await self.sio.emit('error', {'message': 'game_id requerido'}, room=sid)
                    return
                
                # Lanzar dados usando el servicio de juego
                result = await self.game_service.roll_dice(game_id, int(user_id))
                
                if result['success']:
                    # Notificar a todos los jugadores
                    await self.sio.emit('dice_rolled', {
                        'user_id': user_id,
                        'game_id': game_id,
                        'dice_value': result['dice_value'],
                        'can_move': result.get('can_move', False),
                        'available_moves': result.get('available_moves', [])
                    }, room=game_id)
                else:
                    await self.sio.emit('dice_error', {
                        'message': result.get('message', 'No es tu turno')
                    }, room=sid)
                
            except Exception as e:
                logger.error(f"Error al lanzar dados: {e}")
                await self.sio.emit('error', {'message': 'Error interno del servidor'}, room=sid)
        
        @self.sio.event
        async def pass_turn(sid, data):
            """Pasar turno"""
            try:
                if sid not in self.session_users:
                    await self.sio.emit('error', {'message': 'Usuario no autenticado'}, room=sid)
                    return
                
                user_id = self.session_users[sid]
                game_id = data.get('game_id')
                
                if not game_id:
                    await self.sio.emit('error', {'message': 'game_id requerido'}, room=sid)
                    return
                
                # Pasar turno usando el servicio de juego
                result = await self.game_service.pass_turn(game_id, int(user_id))
                
                if result['success']:
                    # Notificar a todos los jugadores
                    await self.sio.emit('turn_passed', {
                        'user_id': user_id,
                        'game_id': game_id,
                        'next_player': result.get('next_player'),
                        'game_state': result.get('game_state')
                    }, room=game_id)
                else:
                    await self.sio.emit('turn_error', {
                        'message': result.get('message', 'No es tu turno')
                    }, room=sid)
                
            except Exception as e:
                logger.error(f"Error al pasar turno: {e}")
                await self.sio.emit('error', {'message': 'Error interno del servidor'}, room=sid)
    
    async def broadcast_to_game(self, game_id: str, event: str, data: dict):
        """Enviar mensaje a todos los jugadores de un juego"""
        await self.sio.emit(event, data, room=game_id)
    
    async def send_to_user(self, user_id: str, event: str, data: dict):
        """Enviar mensaje a un usuario específico"""
        if user_id in self.user_sessions:
            session_id = self.user_sessions[user_id]
            await self.sio.emit(event, data, room=session_id)
    
    def get_connected_users_in_game(self, game_id: str) -> List[str]:
        """Obtener lista de usuarios conectados en un juego"""
        if game_id not in self.game_rooms:
            return []
        
        users = []
        for session_id in self.game_rooms[game_id]:
            if session_id in self.session_users:
                users.append(self.session_users[session_id])
        
        return users

# Instancia global del gestor de sockets
socket_manager = SocketManager()