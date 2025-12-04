"""
Servicio de juego - Lógica de negocio para el juego Parqués
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.db.models.game import Game, GamePlayer, GameMove as DBGameMove
from app.db.models.user import User, GameStatistics
from app.services.game_engine import game_engine, GameState, Player, GameMove
from app.core.game_constants import PlayerColor, GameStatus, WEBSOCKET_EVENTS
from app.schemas.game import (
    GameCreateRequest, GameJoinRequest, GameMoveRequest,
    GameResponse, GameStateResponse, PlayerResponse
)

class GameService:
    """Servicio principal para manejo de juegos"""
    
    def __init__(self):
        self.active_games: Dict[str, GameState] = {}
    
    async def create_game(
        self, 
        db: AsyncSession, 
        user_id: str, 
        request: GameCreateRequest
    ) -> GameResponse:
        """Crear un nuevo juego"""
        
        # Verificar que el usuario existe
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Crear juego en la base de datos
        db_game = Game(
            name=request.name,
            max_players=request.max_players,
            is_private=request.is_private,
            password_hash=request.password if request.password else None,
            created_by=user_id,
            status=GameStatus.WAITING
        )
        
        db.add(db_game)
        await db.commit()
        await db.refresh(db_game)
        
        # Crear estado del juego en memoria
        game_state = game_engine.create_game(str(db_game.id))
        self.active_games[str(db_game.id)] = game_state
        
        # Agregar al creador como jugador
        await self.join_game(
            db, 
            str(db_game.id), 
            user_id, 
            GameJoinRequest(color=request.creator_color)
        )
        
        return GameResponse(
            id=str(db_game.id),
            name=db_game.name,
            status=db_game.status,
            max_players=db_game.max_players,
            current_players=1,
            is_private=db_game.is_private,
            created_by=str(db_game.created_by),
            created_at=db_game.created_at
        )
    
    async def join_game(
        self, 
        db: AsyncSession, 
        game_id: str, 
        user_id: str, 
        request: GameJoinRequest
    ) -> PlayerResponse:
        """Unirse a un juego existente"""
        
        # Verificar que el juego existe
        result = await db.execute(
            select(Game).where(Game.id == game_id)
        )
        db_game = result.scalar_one_or_none()
        if not db_game:
            raise ValueError("Juego no encontrado")
        
        if db_game.status != GameStatus.WAITING:
            raise ValueError("El juego ya ha comenzado")
        
        # Verificar contraseña si es necesario
        if db_game.is_private and db_game.password_hash:
            if not request.password or request.password != db_game.password_hash:
                raise ValueError("Contraseña incorrecta")
        
        # Verificar que el usuario existe
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Verificar que no esté ya en el juego
        result = await db.execute(
            select(GamePlayer).where(
                GamePlayer.game_id == game_id,
                GamePlayer.user_id == user_id
            )
        )
        existing_player = result.scalar_one_or_none()
        if existing_player:
            raise ValueError("Ya estás en este juego")
        
        # Obtener estado del juego
        game_state = self.active_games.get(game_id)
        if not game_state:
            game_state = game_engine.create_game(game_id)
            self.active_games[game_id] = game_state
        
        # Agregar jugador al motor de juego
        success = game_engine.add_player(
            game_id, 
            user_id, 
            user.display_name or user.username,
            request.color
        )
        
        if not success:
            raise ValueError("No se pudo agregar al juego (color ocupado o juego lleno)")
        
        # Agregar jugador a la base de datos
        db_player = GamePlayer(
            game_id=game_id,
            user_id=user_id,
            color=request.color,
            joined_at=datetime.utcnow()
        )
        
        db.add(db_player)
        await db.commit()
        
        return PlayerResponse(
            id=user_id,
            name=user.display_name or user.username,
            color=request.color,
            score=0,
            is_ai=False
        )
    
    async def start_game(self, db: AsyncSession, game_id: str, user_id: str) -> bool:
        """Iniciar un juego"""
        
        # Verificar que el usuario es el creador
        result = await db.execute(
            select(Game).where(Game.id == game_id, Game.created_by == user_id)
        )
        db_game = result.scalar_one_or_none()
        if not db_game:
            raise ValueError("Solo el creador puede iniciar el juego")
        
        if db_game.status != GameStatus.WAITING:
            raise ValueError("El juego ya ha comenzado")
        
        # Verificar que hay suficientes jugadores
        result = await db.execute(
            select(GamePlayer).where(GamePlayer.game_id == game_id)
        )
        players = result.scalars().all()
        
        if len(players) < 2:
            raise ValueError("Se necesitan al menos 2 jugadores")
        
        # Iniciar juego en el motor
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Estado del juego no encontrado")
        
        success = game_engine.start_game(game_id)
        if not success:
            raise ValueError("No se pudo iniciar el juego")
        
        # Actualizar base de datos
        await db.execute(
            update(Game)
            .where(Game.id == game_id)
            .values(status=GameStatus.ACTIVE, started_at=datetime.utcnow())
        )
        await db.commit()
        
        return True
    
    async def roll_dice(
        self, 
        db: AsyncSession, 
        game_id: str, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Lanzar el dado DOS veces (reglas de Parqués)"""
        
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Juego no encontrado")
        
        # Encontrar el player_id del usuario
        player_id = None
        for pid, player in game_state.players.items():
            if player.user_id == user_id:
                player_id = pid
                break
        
        if not player_id:
            raise ValueError("No estás en este juego")
        
        dice_result = game_engine.roll_dice(game_id, player_id)
        if dice_result is None:
            raise ValueError("No es tu turno o el juego no está activo")
        
        return dice_result
    
    async def pass_turn(
        self, 
        db: AsyncSession, 
        game_id: str, 
        user_id: str
    ) -> bool:
        """Pasar turno cuando no hay movimientos válidos"""
        
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Juego no encontrado")
        
        # Encontrar el player_id del usuario
        player_id = None
        for pid, player in game_state.players.items():
            if player.user_id == user_id:
                player_id = pid
                break
        
        if not player_id:
            raise ValueError("No estás en este juego")
        
        success = game_engine.pass_turn(game_id, player_id)
        if not success:
            raise ValueError("No puedes pasar turno en este momento")
        
        return True
    
    async def get_valid_moves(
        self, 
        db: AsyncSession, 
        game_id: str, 
        user_id: str, 
        dice_value: int
    ) -> List[Dict]:
        """Obtener movimientos válidos"""
        
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Juego no encontrado")
        
        # Encontrar el player_id del usuario
        player_id = None
        for pid, player in game_state.players.items():
            if player.user_id == user_id:
                player_id = pid
                break
        
        if not player_id:
            raise ValueError("No estás en este juego")
        
        return game_engine.get_valid_moves(game_id, player_id, dice_value)
    
    async def make_move(
        self, 
        db: AsyncSession, 
        game_id: str, 
        user_id: str, 
        request: GameMoveRequest
    ) -> Optional[GameMove]:
        """Realizar un movimiento"""
        
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Juego no encontrado")
        
        # Encontrar el player_id del usuario
        player_id = None
        for pid, player in game_state.players.items():
            if player.user_id == user_id:
                player_id = pid
                break
        
        if not player_id:
            raise ValueError("No estás en este juego")
        
        # Realizar movimiento
        game_move = game_engine.make_move(
            game_id, 
            player_id, 
            request.piece_id, 
            request.to_position, 
            request.dice_value,
            request.is_last_move
        )
        
        if not game_move:
            raise ValueError("Movimiento inválido")
        
        # Guardar movimiento en base de datos
        db_move = DBGameMove(
            game_id=game_id,
            player_id=user_id,
            piece_id=request.piece_id,
            from_position=game_move.from_position,
            to_position=game_move.to_position,
            dice_value=request.dice_value,
            move_type=game_move.move_type,
            captured_piece_id=game_move.captured_piece_id
        )
        
        db.add(db_move)
        
        # Si el juego terminó, actualizar estadísticas
        if game_state.status == GameStatus.FINISHED:
            await self._update_game_statistics(db, game_state)
            
            # Actualizar estado del juego en BD
            await db.execute(
                update(Game)
                .where(Game.id == game_id)
                .values(
                    status=GameStatus.FINISHED,
                    finished_at=datetime.utcnow(),
                    winner_id=game_state.winner_id
                )
            )
        
        await db.commit()
        return game_move
    
    async def get_game_state(
        self, 
        db: AsyncSession, 
        game_id: str, 
        user_id: str
    ) -> GameStateResponse:
        """Obtener estado completo del juego"""
        
        # Verificar que el usuario está en el juego
        result = await db.execute(
            select(GamePlayer).where(
                GamePlayer.game_id == game_id,
                GamePlayer.user_id == user_id
            )
        )
        player = result.scalar_one_or_none()
        if not player:
            raise ValueError("No tienes acceso a este juego")
        
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Juego no encontrado")
        
        # Convertir estado del juego a respuesta
        players = []
        for player_data in game_state.players.values():
            pieces = []
            for piece in player_data.pieces:
                pieces.append({
                    'id': piece.id,
                    'position': piece.position,
                    'status': piece.status
                })
            
            players.append(PlayerResponse(
                id=player_data.id,
                name=player_data.name,
                color=player_data.color,
                score=player_data.score,
                pieces=pieces,
                is_ai=player_data.is_ai
            ))
        
        return GameStateResponse(
            id=game_state.id,
            status=game_state.status,
            players=players,
            current_player_id=game_state.current_player_id,
            board=game_state.board,
            last_dice_value=game_state.last_dice_value,
            last_dice1=game_state.last_dice1,
            last_dice2=game_state.last_dice2,
            is_pair=game_state.is_pair,
            winner_id=game_state.winner_id
        )
    
    async def leave_game(
        self, 
        db: AsyncSession, 
        game_id: str, 
        user_id: str
    ) -> bool:
        """Abandonar un juego"""
        
        # Remover de la base de datos
        result = await db.execute(
            select(GamePlayer).where(
                GamePlayer.game_id == game_id,
                GamePlayer.user_id == user_id
            )
        )
        player = result.scalar_one_or_none()
        if not player:
            return False
        
        await db.delete(player)
        
        # Remover del motor de juego
        game_state = self.active_games.get(game_id)
        if game_state:
            # Encontrar player_id
            player_id = None
            for pid, p in game_state.players.items():
                if p.user_id == user_id:
                    player_id = pid
                    break
            
            if player_id:
                game_engine.remove_player(game_id, player_id)
        
        await db.commit()
        return True
    
    async def get_available_games(self, db: AsyncSession) -> List[GameResponse]:
        """Obtener juegos disponibles para unirse"""
        
        result = await db.execute(
            select(Game)
            .where(Game.status == GameStatus.WAITING)
            .order_by(Game.created_at.desc())
        )
        games = result.scalars().all()
        
        response = []
        for game in games:
            # Contar jugadores actuales
            result = await db.execute(
                select(GamePlayer).where(GamePlayer.game_id == str(game.id))
            )
            current_players = len(result.scalars().all())
            
            response.append(GameResponse(
                id=str(game.id),
                name=game.name,
                status=game.status,
                max_players=game.max_players,
                current_players=current_players,
                is_private=game.is_private,
                created_by=str(game.created_by),
                created_at=game.created_at
            ))
        
        return response
    
    async def get_game(self, game_id: str) -> Optional[Game]:
        """Obtener juego por ID desde la base de datos"""
        from app.db.database import get_db
        
        try:
            async for db in get_db():
                result = await db.execute(select(Game).where(Game.id == uuid.UUID(game_id)))
                return result.scalar_one_or_none()
        except Exception:
            return None
    
    async def _update_game_statistics(self, db: AsyncSession, game_state: GameState):
        """Actualizar estadísticas de los jugadores"""
        
        for player in game_state.players.values():
            if not player.user_id:
                continue
            
            # Obtener estadísticas actuales
            result = await db.execute(
                select(GameStatistics).where(GameStatistics.user_id == player.user_id)
            )
            stats = result.scalar_one_or_none()
            
            if not stats:
                stats = GameStatistics(user_id=player.user_id)
                db.add(stats)
            
            # Actualizar estadísticas
            stats.games_played += 1
            
            if game_state.winner_id == player.id:
                stats.games_won += 1
            
            # Calcular movimientos y capturas del jugador
            player_moves = [
                move for move in game_state.moves_history 
                if move.player_id == player.id
            ]
            
            stats.total_moves += len(player_moves)
            stats.total_captures += sum(
                1 for move in player_moves 
                if move.captured_piece_id is not None
            )
            
            # Calcular duración promedio (aproximada)
            if game_state.started_at and game_state.finished_at:
                duration = (game_state.finished_at - game_state.started_at).total_seconds()
                if stats.games_played == 1:
                    stats.average_game_duration_seconds = int(duration)
                else:
                    # Promedio ponderado
                    total_duration = stats.average_game_duration_seconds * (stats.games_played - 1) + duration
                    stats.average_game_duration_seconds = int(total_duration / stats.games_played)

# Instancia global del servicio
game_service = GameService()