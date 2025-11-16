"""
Motor de juego Parqués - Lógica principal y validaciones
"""
import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field

from app.core.game_constants import (
    PlayerColor, GameStatus, PieceStatus, MoveType, BoardPositions,
    BOARD_SIZE, HOME_POSITIONS, GOAL_POSITIONS, EXIT_HOME_VALUES,
    POINTS_FOR_CAPTURE, POINTS_FOR_GOAL, POINTS_FOR_WIN,
    MAX_TURNS_WITHOUT_PROGRESS
)

@dataclass
class Piece:
    """Representa una ficha del juego"""
    id: str
    color: PlayerColor
    position: int = -1  # -1 = en casa, 0-67 = tablero, 68+ = meta
    status: PieceStatus = PieceStatus.HOME
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass
class Player:
    """Representa un jugador"""
    id: str
    user_id: Optional[str]
    color: PlayerColor
    name: str
    pieces: List[Piece] = field(default_factory=list)
    score: int = 0
    is_ai: bool = False
    ai_level: Optional[str] = None
    
    def __post_init__(self):
        if not self.pieces:
            self.pieces = [
                Piece(id=f"{self.color}_{i}", color=self.color)
                for i in range(HOME_POSITIONS)
            ]

@dataclass
class GameMove:
    """Representa un movimiento en el juego"""
    player_id: str
    piece_id: str
    from_position: int
    to_position: int
    dice_value: int
    move_type: MoveType
    captured_piece_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class GameState:
    """Estado completo del juego"""
    id: str
    players: Dict[str, Player] = field(default_factory=dict)
    current_player_id: Optional[str] = None
    status: GameStatus = GameStatus.WAITING
    board: Dict[int, List[str]] = field(default_factory=dict)  # posición -> lista de piece_ids
    last_dice_value: Optional[int] = None
    moves_history: List[GameMove] = field(default_factory=list)
    winner_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    turns_without_progress: int = 0
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        # Inicializar tablero vacío
        for i in range(BOARD_SIZE):
            self.board[i] = []

class GameEngine:
    """Motor principal del juego Parqués"""
    
    def __init__(self):
        self.games: Dict[str, GameState] = {}
    
    def create_game(self, game_id: Optional[str] = None) -> GameState:
        """Crear un nuevo juego"""
        if not game_id:
            game_id = str(uuid.uuid4())
        
        game_state = GameState(id=game_id)
        self.games[game_id] = game_state
        return game_state
    
    def get_game(self, game_id: str) -> Optional[GameState]:
        """Obtener un juego por ID"""
        return self.games.get(game_id)
    
    def add_player(self, game_id: str, user_id: str, name: str, 
                   color: PlayerColor, is_ai: bool = False, 
                   ai_level: Optional[str] = None) -> bool:
        """Agregar un jugador al juego"""
        game = self.get_game(game_id)
        if not game or game.status != GameStatus.WAITING:
            return False
        
        if len(game.players) >= 4:
            return False
        
        # Verificar que el color no esté tomado
        for player in game.players.values():
            if player.color == color:
                return False
        
        player_id = str(uuid.uuid4())
        player = Player(
            id=player_id,
            user_id=user_id,
            color=color,
            name=name,
            is_ai=is_ai,
            ai_level=ai_level
        )
        
        game.players[player_id] = player
        return True
    
    def remove_player(self, game_id: str, player_id: str) -> bool:
        """Remover un jugador del juego"""
        game = self.get_game(game_id)
        if not game or player_id not in game.players:
            return False
        
        # Si el juego ya comenzó, marcar como abandonado
        if game.status == GameStatus.ACTIVE:
            # TODO: Implementar lógica de abandono
            pass
        
        del game.players[player_id]
        
        # Si no quedan jugadores suficientes, cancelar el juego
        if len(game.players) < 2 and game.status == GameStatus.ACTIVE:
            game.status = GameStatus.CANCELLED
        
        return True
    
    def start_game(self, game_id: str) -> bool:
        """Iniciar el juego"""
        game = self.get_game(game_id)
        if not game or game.status != GameStatus.WAITING:
            return False
        
        if len(game.players) < 2:
            return False
        
        game.status = GameStatus.ACTIVE
        game.started_at = datetime.utcnow()
        
        # Establecer orden de turnos (aleatorio)
        player_ids = list(game.players.keys())
        random.shuffle(player_ids)
        game.current_player_id = player_ids[0]
        
        return True
    
    def roll_dice(self, game_id: str, player_id: str) -> Optional[int]:
        """Lanzar el dado"""
        game = self.get_game(game_id)
        if not game or game.status != GameStatus.ACTIVE:
            return None
        
        if game.current_player_id != player_id:
            return None
        
        dice_value = random.randint(1, 6)
        game.last_dice_value = dice_value
        return dice_value
    
    def get_valid_moves(self, game_id: str, player_id: str, dice_value: int) -> List[Dict]:
        """Obtener movimientos válidos para un jugador"""
        game = self.get_game(game_id)
        if not game or player_id not in game.players:
            return []
        
        player = game.players[player_id]
        valid_moves = []
        
        for piece in player.pieces:
            moves = self._get_piece_valid_moves(game, piece, dice_value)
            valid_moves.extend(moves)
        
        return valid_moves
    
    def _get_piece_valid_moves(self, game: GameState, piece: Piece, dice_value: int) -> List[Dict]:
        """Obtener movimientos válidos para una ficha específica"""
        moves = []
        
        if piece.status == PieceStatus.HOME:
            # Solo puede salir con 5 o 6
            if dice_value in EXIT_HOME_VALUES:
                start_pos = BoardPositions.get_starting_position(piece.color)
                if self._can_move_to_position(game, piece, start_pos):
                    moves.append({
                        'piece_id': piece.id,
                        'from_position': -1,
                        'to_position': start_pos,
                        'move_type': MoveType.EXIT_HOME
                    })
        
        elif piece.status == PieceStatus.BOARD:
            # Movimiento normal en el tablero
            new_position = BoardPositions.calculate_next_position(piece.position, dice_value)
            
            # Verificar si debe entrar a la zona de meta
            goal_entry = BoardPositions.get_goal_entry_position(piece.color)
            if self._should_enter_goal_zone(piece, new_position, goal_entry):
                goal_position = self._calculate_goal_position(piece, dice_value, goal_entry)
                if goal_position is not None and self._can_move_to_goal(game, piece, goal_position):
                    moves.append({
                        'piece_id': piece.id,
                        'from_position': piece.position,
                        'to_position': goal_position,
                        'move_type': MoveType.ENTER_GOAL
                    })
            else:
                # Movimiento normal
                if self._can_move_to_position(game, piece, new_position):
                    move_type = MoveType.NORMAL_MOVE
                    if self._would_capture(game, piece, new_position):
                        move_type = MoveType.CAPTURE
                    
                    moves.append({
                        'piece_id': piece.id,
                        'from_position': piece.position,
                        'to_position': new_position,
                        'move_type': move_type
                    })
        
        elif piece.status == PieceStatus.SAFE_ZONE:
            # Movimiento en zona de meta
            new_position = piece.position + dice_value
            goal_positions = BoardPositions.get_goal_positions(piece.color)
            
            if new_position <= max(goal_positions):
                if self._can_move_to_goal(game, piece, new_position):
                    moves.append({
                        'piece_id': piece.id,
                        'from_position': piece.position,
                        'to_position': new_position,
                        'move_type': MoveType.ENTER_GOAL
                    })
        
        return moves
    
    def make_move(self, game_id: str, player_id: str, piece_id: str, 
                  to_position: int, dice_value: int) -> Optional[GameMove]:
        """Realizar un movimiento"""
        game = self.get_game(game_id)
        if not game or game.status != GameStatus.ACTIVE:
            return None
        
        if game.current_player_id != player_id:
            return None
        
        player = game.players.get(player_id)
        if not player:
            return None
        
        # Encontrar la ficha
        piece = None
        for p in player.pieces:
            if p.id == piece_id:
                piece = p
                break
        
        if not piece:
            return None
        
        # Validar el movimiento
        valid_moves = self._get_piece_valid_moves(game, piece, dice_value)
        move_valid = any(
            move['piece_id'] == piece_id and move['to_position'] == to_position
            for move in valid_moves
        )
        
        if not move_valid:
            return None
        
        # Ejecutar el movimiento
        return self._execute_move(game, player, piece, to_position, dice_value)
    
    def _execute_move(self, game: GameState, player: Player, piece: Piece, 
                     to_position: int, dice_value: int) -> GameMove:
        """Ejecutar un movimiento validado"""
        from_position = piece.position
        captured_piece_id = None
        
        # Determinar tipo de movimiento
        if piece.status == PieceStatus.HOME:
            move_type = MoveType.EXIT_HOME
        elif to_position >= BOARD_SIZE:
            move_type = MoveType.ENTER_GOAL
        elif self._would_capture(game, piece, to_position):
            move_type = MoveType.CAPTURE
            captured_piece_id = self._capture_piece(game, to_position, piece.color)
        else:
            move_type = MoveType.NORMAL_MOVE
        
        # Remover ficha de posición anterior
        if piece.status == PieceStatus.BOARD and from_position in game.board:
            if piece.id in game.board[from_position]:
                game.board[from_position].remove(piece.id)
        
        # Actualizar ficha
        piece.position = to_position
        
        if to_position < 0:
            piece.status = PieceStatus.HOME
        elif to_position >= BOARD_SIZE:
            piece.status = PieceStatus.SAFE_ZONE
        elif BoardPositions.is_safe_position(to_position):
            piece.status = PieceStatus.SAFE_ZONE
        else:
            piece.status = PieceStatus.BOARD
        
        # Colocar ficha en nueva posición
        if piece.status == PieceStatus.BOARD:
            if to_position not in game.board:
                game.board[to_position] = []
            game.board[to_position].append(piece.id)
        
        # Crear registro del movimiento
        game_move = GameMove(
            player_id=player.id,
            piece_id=piece.id,
            from_position=from_position,
            to_position=to_position,
            dice_value=dice_value,
            move_type=move_type,
            captured_piece_id=captured_piece_id
        )
        
        game.moves_history.append(game_move)
        
        # Actualizar puntuación
        if move_type == MoveType.CAPTURE:
            player.score += POINTS_FOR_CAPTURE
        elif move_type == MoveType.ENTER_GOAL:
            player.score += POINTS_FOR_GOAL
        
        # Verificar victoria
        if self._check_victory(player):
            game.winner_id = player.id
            game.status = GameStatus.FINISHED
            game.finished_at = datetime.utcnow()
            player.score += POINTS_FOR_WIN
        else:
            # Cambiar turno (a menos que haya sacado 6 o capturado)
            if dice_value != 6 and move_type != MoveType.CAPTURE:
                self._next_turn(game)
        
        return game_move
    
    def _can_move_to_position(self, game: GameState, piece: Piece, position: int) -> bool:
        """Verificar si una ficha puede moverse a una posición"""
        if position < 0 or position >= BOARD_SIZE:
            return False
        
        # Verificar si hay fichas del mismo color (no se pueden apilar)
        if position in game.board:
            for piece_id in game.board[position]:
                for player in game.players.values():
                    for p in player.pieces:
                        if p.id == piece_id and p.color == piece.color:
                            return False
        
        return True
    
    def _can_move_to_goal(self, game: GameState, piece: Piece, position: int) -> bool:
        """Verificar si una ficha puede moverse a la zona de meta"""
        goal_positions = BoardPositions.get_goal_positions(piece.color)
        if position not in goal_positions:
            return False
        
        # Verificar que no haya otra ficha del mismo jugador
        player = None
        for p in game.players.values():
            if any(piece.id == p_piece.id for p_piece in p.pieces):
                player = p
                break
        
        if player:
            for p in player.pieces:
                if p.position == position and p.id != piece.id:
                    return False
        
        return True
    
    def _would_capture(self, game: GameState, piece: Piece, position: int) -> bool:
        """Verificar si un movimiento capturaría una ficha"""
        if BoardPositions.is_safe_position(position):
            return False
        
        if position in game.board and game.board[position]:
            # Hay fichas en la posición, verificar si son de otro color
            for piece_id in game.board[position]:
                for player in game.players.values():
                    for p in player.pieces:
                        if p.id == piece_id and p.color != piece.color:
                            return True
        
        return False
    
    def _capture_piece(self, game: GameState, position: int, capturing_color: PlayerColor) -> Optional[str]:
        """Capturar una ficha en una posición"""
        if position not in game.board:
            return None
        
        captured_piece_id = None
        pieces_to_remove = []
        
        for piece_id in game.board[position]:
            for player in game.players.values():
                for piece in player.pieces:
                    if piece.id == piece_id and piece.color != capturing_color:
                        # Enviar ficha a casa
                        piece.position = -1
                        piece.status = PieceStatus.HOME
                        pieces_to_remove.append(piece_id)
                        captured_piece_id = piece_id
                        break
        
        # Remover fichas capturadas del tablero
        for piece_id in pieces_to_remove:
            game.board[position].remove(piece_id)
        
        return captured_piece_id
    
    def _should_enter_goal_zone(self, piece: Piece, new_position: int, goal_entry: int) -> bool:
        """Verificar si una ficha debe entrar a la zona de meta"""
        # Lógica para determinar si la ficha ha pasado por su entrada de meta
        # y debe dirigirse hacia el centro
        return new_position == goal_entry or (
            piece.position < goal_entry < new_position or
            (piece.position > goal_entry and new_position < piece.position)
        )
    
    def _calculate_goal_position(self, piece: Piece, dice_value: int, goal_entry: int) -> Optional[int]:
        """Calcular posición en la zona de meta"""
        steps_past_entry = dice_value - (goal_entry - piece.position)
        if steps_past_entry <= 0:
            return None
        
        goal_positions = BoardPositions.get_goal_positions(piece.color)
        if steps_past_entry <= len(goal_positions):
            return goal_positions[steps_past_entry - 1]
        
        return None
    
    def _check_victory(self, player: Player) -> bool:
        """Verificar si un jugador ha ganado"""
        return all(piece.status == PieceStatus.GOAL for piece in player.pieces)
    
    def pass_turn(self, game_id: str, player_id: str) -> bool:
        """Pasar turno cuando no hay movimientos válidos"""
        print(f"DEBUG pass_turn: game_id={game_id}, player_id={player_id}")
        
        game = self.get_game(game_id)
        if not game:
            print("DEBUG pass_turn: Game not found")
            return False
            
        if game.status != GameStatus.ACTIVE:
            print(f"DEBUG pass_turn: Game status is {game.status}, not ACTIVE")
            return False

        print(f"DEBUG pass_turn: current_player_id={game.current_player_id}, player_id={player_id}")
        if game.current_player_id != player_id:
            print("DEBUG pass_turn: Not current player's turn")
            return False

        # Cambiar al siguiente turno
        print("DEBUG pass_turn: Changing to next turn")
        self._next_turn(game)
        return True
    
    def _next_turn(self, game: GameState) -> None:
        """Cambiar al siguiente turno"""
        player_ids = list(game.players.keys())
        current_index = player_ids.index(game.current_player_id)
        next_index = (current_index + 1) % len(player_ids)
        game.current_player_id = player_ids[next_index]
        
        # Incrementar contador de turnos sin progreso
        game.turns_without_progress += 1
        
        # Verificar si el juego debe terminar por falta de progreso
        if game.turns_without_progress >= MAX_TURNS_WITHOUT_PROGRESS:
            game.status = GameStatus.FINISHED
            game.finished_at = datetime.utcnow()
    
    def get_game_summary(self, game_id: str) -> Optional[Dict]:
        """Obtener resumen del estado del juego"""
        game = self.get_game(game_id)
        if not game:
            return None
        
        return {
            'id': game.id,
            'status': game.status,
            'players': [
                {
                    'id': player.id,
                    'name': player.name,
                    'color': player.color,
                    'score': player.score,
                    'pieces_home': sum(1 for p in player.pieces if p.status == PieceStatus.HOME),
                    'pieces_board': sum(1 for p in player.pieces if p.status == PieceStatus.BOARD),
                    'pieces_goal': sum(1 for p in player.pieces if p.status == PieceStatus.GOAL),
                    'is_ai': player.is_ai
                }
                for player in game.players.values()
            ],
            'current_player_id': game.current_player_id,
            'last_dice_value': game.last_dice_value,
            'winner_id': game.winner_id,
            'created_at': game.created_at.isoformat(),
            'started_at': game.started_at.isoformat() if game.started_at else None,
            'finished_at': game.finished_at.isoformat() if game.finished_at else None
        }

# Instancia global del motor de juego
game_engine = GameEngine()