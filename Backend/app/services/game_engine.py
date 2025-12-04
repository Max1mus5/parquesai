"""
Motor de juego Parqués - Lógica principal y validaciones
"""
import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set, Any
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
    last_dice1: Optional[int] = None  # Primer dado
    last_dice2: Optional[int] = None  # Segundo dado
    is_pair: bool = False  # Si los dados son pares
    jail_attempts: Dict[str, int] = field(default_factory=dict)  # player_id -> intentos
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
                   ai_level: Optional[str] = None) -> Optional[str]:
        """Agregar un jugador al juego. Retorna el player_id si tiene éxito, None si falla."""
        game = self.get_game(game_id)
        if not game or game.status != GameStatus.WAITING:
            return None
        
        if len(game.players) >= 4:
            return None
        
        # Verificar que el color no esté tomado
        for player in game.players.values():
            if player.color == color:
                return None
        
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
        return player_id
    
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
    
    def roll_dice(self, game_id: str, player_id: str) -> Optional[Dict[str, Any]]:
        """
        Lanzar el dado DOS veces consecutivamente (reglas de Parqués)
        Retorna: {
            'dice1': int,
            'dice2': int, 
            'total': int,
            'is_pair': bool,
            'can_continue': bool  # True si sacó par (tiene otro turno)
        }
        """
        game = self.get_game(game_id)
        if not game or game.status != GameStatus.ACTIVE:
            return None
        
        if game.current_player_id != player_id:
            return None
        
        # Lanzar el dado DOS veces
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        
        is_pair = dice1 == dice2
        total = dice1 + dice2
        
        # Guardar en el estado del juego
        game.last_dice1 = dice1
        game.last_dice2 = dice2
        game.last_dice_value = total
        game.is_pair = is_pair
        
        # Verificar si todas las fichas están en casa (cárcel)
        player = game.players[player_id]
        all_in_jail = all(piece.status == PieceStatus.HOME for piece in player.pieces)
        
        # Trackear intentos de salir de cárcel
        if all_in_jail:
            if player_id not in game.jail_attempts:
                game.jail_attempts[player_id] = 0
            
            if not is_pair:
                # NO incrementar aquí, se incrementará en pass_turn si no hay movimientos
                print(f"🔒 Jugador {player_id} en cárcel. Intento {game.jail_attempts[player_id] + 1}/3")
            else:
                # Sacó par, puede salir
                game.jail_attempts[player_id] = 0
                print(f"🔓 Jugador {player_id} sacó PAR! Puede salir de cárcel")
        else:
            # Tiene fichas fuera, resetear contador
            game.jail_attempts[player_id] = 0
        
        print(f"🎲 Jugador {player_id}: dado1={dice1}, dado2={dice2}, total={total}, par={is_pair}")
        
        # Si sacó par y tiene fichas en casa, sacarlas TODAS automáticamente
        if is_pair:
            pieces_released = self._auto_release_all_pieces(game, player_id)
            if pieces_released > 0:
                print(f"🚪 Se sacaron automáticamente {pieces_released} fichas de la casa")
        
        return {
            'dice1': dice1,
            'dice2': dice2,
            'total': total,
            'is_pair': is_pair,
            'can_continue': is_pair  # Si es par, puede seguir jugando
        }
    
    def _auto_release_all_pieces(self, game: GameState, player_id: str) -> int:
        """Sacar automáticamente TODAS las fichas en casa cuando hay un par"""
        player = game.players[player_id]
        start_pos = BoardPositions.get_starting_position(player.color)
        pieces_released = 0
        
        for piece in player.pieces:
            if piece.status == PieceStatus.HOME:
                # En Parqués, cuando sacas par, TODAS las fichas salen
                # aunque haya otras fichas en la posición de salida (se apilan temporalmente)
                
                # Sacar la ficha
                piece.position = start_pos
                piece.status = PieceStatus.BOARD
                
                # Agregar al tablero
                if start_pos not in game.board:
                    game.board[start_pos] = []
                game.board[start_pos].append(piece.id)
                
                # Crear registro del movimiento
                game_move = GameMove(
                    player_id=player.id,
                    piece_id=piece.id,
                    from_position=-1,
                    to_position=start_pos,
                    dice_value=0,  # Salida automática
                    move_type=MoveType.EXIT_HOME,
                    captured_piece_id=None
                )
                game.moves_history.append(game_move)
                
                pieces_released += 1
                print(f"  ✅ Ficha {piece.id} salió automáticamente a posición {start_pos}")
        
        return pieces_released
    
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
            # En Parqués, solo puede salir con PAR (ambos dados iguales)
            if game.is_pair:
                start_pos = BoardPositions.get_starting_position(piece.color)
                if self._can_move_to_position(game, piece, start_pos):
                    moves.append({
                        'piece_id': piece.id,
                        'from_position': -1,
                        'to_position': start_pos,
                        'move_type': MoveType.EXIT_HOME
                    })
                    print(f"✅ Ficha {piece.id} puede salir de casa (par detectado)")
            else:
                print(f"❌ Ficha {piece.id} NO puede salir de casa (no hay par)")
        
        elif piece.status == PieceStatus.BOARD:
            # Verificar si debe entrar a la zona de meta
            goal_entry = BoardPositions.get_goal_entry_position(piece.color)
            
            # Calcular si el movimiento cruza o llega a la entrada de meta
            if self._will_pass_goal_entry(piece.position, dice_value, goal_entry):
                # Calcular cuántos pasos después de la entrada
                steps_to_entry = self._calculate_steps_to_position(piece.position, goal_entry)
                steps_into_goal = dice_value - steps_to_entry
                
                if steps_into_goal > 0 and steps_into_goal <= GOAL_POSITIONS:
                    # Entra a la zona de meta
                    goal_position = BOARD_SIZE + steps_into_goal - 1  # 68, 69, 70...
                    if self._can_move_to_goal(game, piece, goal_position):
                        moves.append({
                            'piece_id': piece.id,
                            'from_position': piece.position,
                            'to_position': goal_position,
                            'move_type': MoveType.ENTER_GOAL
                        })
                        print(f"✅ Ficha {piece.id} puede entrar a meta: pos {piece.position} + {dice_value} = meta {goal_position}")
            else:
                # Movimiento normal en el tablero circular
                new_position = BoardPositions.calculate_next_position(piece.position, dice_value)
                
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
            # SAFE_ZONE puede ser:
            # 1. Zona de meta (posiciones >= 68)
            # 2. Casilla segura en el tablero (5, 12, 17, 22, etc.)
            
            if piece.position >= BOARD_SIZE:
                # Está en zona de meta (68-75)
                new_position = piece.position + dice_value
                max_goal_position = BOARD_SIZE + GOAL_POSITIONS - 1  # 75
                
                # Verificar que no se pase de la meta final
                if new_position <= max_goal_position:
                    if self._can_move_to_goal(game, piece, new_position):
                        move_type = MoveType.ENTER_GOAL
                        
                        moves.append({
                            'piece_id': piece.id,
                            'from_position': piece.position,
                            'to_position': new_position,
                            'move_type': move_type
                        })
                        print(f"✅ Ficha {piece.id} puede avanzar en meta: {piece.position} → {new_position}")
                else:
                    print(f"❌ Ficha {piece.id} se pasaría de meta: {piece.position} + {dice_value} = {new_position} > {max_goal_position}")
            else:
                # Está en una casilla segura del tablero (0-67)
                # Tratarla como si estuviera en BOARD
                goal_entry = BoardPositions.get_goal_entry_position(piece.color)
                
                if self._will_pass_goal_entry(piece.position, dice_value, goal_entry):
                    # Calculará entrada a meta
                    steps_to_entry = self._calculate_steps_to_position(piece.position, goal_entry)
                    steps_into_goal = dice_value - steps_to_entry
                    
                    if steps_into_goal > 0 and steps_into_goal <= GOAL_POSITIONS:
                        goal_position = BOARD_SIZE + steps_into_goal - 1
                        if self._can_move_to_goal(game, piece, goal_position):
                            moves.append({
                                'piece_id': piece.id,
                                'from_position': piece.position,
                                'to_position': goal_position,
                                'move_type': MoveType.ENTER_GOAL
                            })
                            print(f"✅ Ficha {piece.id} puede entrar a meta desde casilla segura")
                else:
                    # Movimiento normal en el tablero
                    new_position = BoardPositions.calculate_next_position(piece.position, dice_value)
                    
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
                        print(f"✅ Ficha {piece.id} puede moverse desde casilla segura: {piece.position} → {new_position}")
        
        return moves
    
    def make_move(self, game_id: str, player_id: str, piece_id: str, 
                  to_position: int, dice_value: int, is_last_move: bool = False) -> Optional[GameMove]:
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
        return self._execute_move(game, player, piece, to_position, dice_value, is_last_move)
    
    def _execute_move(self, game: GameState, player: Player, piece: Piece, 
                     to_position: int, dice_value: int, is_last_move: bool = False) -> GameMove:
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
        if from_position in game.board:
            if piece.id in game.board[from_position]:
                game.board[from_position].remove(piece.id)
                print(f"🔄 Ficha {piece.id} removida de posición {from_position}")
        
        # Actualizar ficha
        piece.position = to_position
        
        # Determinar nuevo estado de la ficha
        if to_position < 0:
            piece.status = PieceStatus.HOME
        elif to_position >= BOARD_SIZE + GOAL_POSITIONS - 1:
            # Llegó a la última posición de meta (coronó)
            piece.status = PieceStatus.GOAL
            print(f"🏆 Ficha {piece.id} CORONÓ en posición {to_position}!")
        elif to_position >= BOARD_SIZE:
            # Está en zona de meta pero no ha coronado
            piece.status = PieceStatus.SAFE_ZONE
            print(f"🎯 Ficha {piece.id} en zona de meta: posición {to_position}")
        else:
            # Está en el tablero circular (0-67)
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
            # Cambiar turno SOLO si:
            # 1. Es el último movimiento del turno (is_last_move=True)
            # 2. Y NO sacó par
            if is_last_move and not game.is_pair:
                print(f"🔄 Último movimiento sin par, cambiando turno de {player.id}")
                self._next_turn(game)
            elif is_last_move and game.is_pair:
                print(f"🎉 Último movimiento con par! El jugador {player.id} tiene otro turno")
            else:
                print(f"⏸️ Movimiento intermedio, el jugador {player.id} puede seguir moviendo")
        
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
        # Verificar que la posición esté en el rango de meta (68-75)
        if position < BOARD_SIZE or position >= BOARD_SIZE + GOAL_POSITIONS:
            return False
        
        # Encontrar al jugador dueño de la ficha
        player = None
        for p in game.players.values():
            if any(piece.id == p_piece.id for p_piece in p.pieces):
                player = p
                break
        
        if not player:
            return False
        
        # Verificar que no haya otra ficha del mismo jugador en esa posición
        for p in player.pieces:
            if p.position == position and p.id != piece.id:
                print(f"❌ Posición {position} ocupada por ficha {p.id} del mismo jugador")
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
        # Esta función ya no se usa, reemplazada por _will_pass_goal_entry
        return False
    
    def _will_pass_goal_entry(self, current_pos: int, steps: int, goal_entry: int) -> bool:
        """Verificar si el movimiento pasará por la entrada de meta del color"""
        # Calcular todas las posiciones que recorrerá
        for i in range(1, steps + 1):
            pos = (current_pos + i) % BOARD_SIZE
            if pos == goal_entry:
                return True
        return False
    
    def _calculate_steps_to_position(self, from_pos: int, to_pos: int) -> int:
        """Calcular cuántos pasos hay de from_pos a to_pos en el tablero circular"""
        if to_pos >= from_pos:
            return to_pos - from_pos
        else:
            # Dar la vuelta al tablero
            return (BOARD_SIZE - from_pos) + to_pos
    
    def _check_victory(self, player: Player) -> bool:
        """Verificar si un jugador ha ganado"""
        return all(piece.status == PieceStatus.GOAL for piece in player.pieces)
    
    def pass_turn(self, game_id: str, player_id: str) -> bool:
        """
        Pasar turno cuando no hay movimientos válidos.
        También maneja el caso de 3 intentos fallidos en cárcel.
        """
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
        
        # Verificar si llegó a 3 intentos en cárcel
        if player_id in game.jail_attempts:
            # Incrementar contador solo al pasar turno
            game.jail_attempts[player_id] += 1
            print(f"⏭️ Jugador {player_id} pasa turno. Intento {game.jail_attempts[player_id]}/3 en cárcel")
            
            if game.jail_attempts[player_id] >= 3:
                print(f"🔄 Jugador {player_id} completó 3 intentos, resetear contador")
                game.jail_attempts[player_id] = 0  # Resetear para el siguiente ciclo

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
            'last_dice1': game.last_dice1,
            'last_dice2': game.last_dice2,
            'is_pair': game.is_pair,
            'winner_id': game.winner_id,
            'created_at': game.created_at.isoformat(),
            'started_at': game.started_at.isoformat() if game.started_at else None,
            'finished_at': game.finished_at.isoformat() if game.finished_at else None
        }

# Instancia global del motor de juego
game_engine = GameEngine()