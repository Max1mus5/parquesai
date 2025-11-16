"""
Constantes y configuraciones del juego Parqués
"""
from enum import Enum
from typing import Dict, List, Tuple

class PlayerColor(str, Enum):
    """Colores de los jugadores"""
    RED = "red"
    BLUE = "blue" 
    YELLOW = "yellow"
    GREEN = "green"

class GameStatus(str, Enum):
    """Estados del juego"""
    WAITING = "waiting"
    ACTIVE = "active"
    PAUSED = "paused"
    FINISHED = "finished"
    CANCELLED = "cancelled"

class PieceStatus(str, Enum):
    """Estados de las fichas"""
    HOME = "home"          # En casa
    BOARD = "board"        # En el tablero
    SAFE_ZONE = "safe_zone"  # En zona segura
    GOAL = "goal"          # En la meta

class MoveType(str, Enum):
    """Tipos de movimiento"""
    EXIT_HOME = "exit_home"      # Salir de casa
    NORMAL_MOVE = "normal_move"  # Movimiento normal
    CAPTURE = "capture"          # Comer ficha
    ENTER_GOAL = "enter_goal"    # Entrar a la meta
    BLOCKED = "blocked"          # Movimiento bloqueado

# Configuraciones del tablero
BOARD_SIZE = 68  # Total de casillas en el tablero principal
SAFE_POSITIONS = [5, 12, 17, 22, 29, 34, 39, 46, 51, 56, 63, 0]  # Posiciones seguras
HOME_POSITIONS = 4  # Fichas por jugador
GOAL_POSITIONS = 8  # Casillas en la zona de meta

# Posiciones iniciales por color
STARTING_POSITIONS: Dict[PlayerColor, int] = {
    PlayerColor.RED: 5,
    PlayerColor.BLUE: 22,
    PlayerColor.YELLOW: 39,
    PlayerColor.GREEN: 56
}

# Posiciones de entrada a la zona de meta
GOAL_ENTRY_POSITIONS: Dict[PlayerColor, int] = {
    PlayerColor.RED: 0,
    PlayerColor.BLUE: 17,
    PlayerColor.YELLOW: 34,
    PlayerColor.GREEN: 51
}

# Configuraciones del dado
DICE_MIN = 1
DICE_MAX = 6
EXIT_HOME_VALUES = [5, 6]  # Valores necesarios para salir de casa

# Configuraciones del juego
MAX_PLAYERS = 4
MIN_PLAYERS = 2
MAX_TURNS_WITHOUT_PROGRESS = 50  # Para evitar juegos infinitos

# Puntuaciones
POINTS_FOR_CAPTURE = 10
POINTS_FOR_GOAL = 50
POINTS_FOR_WIN = 100

# Posiciones especiales del tablero
class BoardPositions:
    """Mapeo de posiciones especiales del tablero"""
    
    @staticmethod
    def get_safe_positions() -> List[int]:
        """Obtener todas las posiciones seguras"""
        return SAFE_POSITIONS.copy()
    
    @staticmethod
    def is_safe_position(position: int) -> bool:
        """Verificar si una posición es segura"""
        return position in SAFE_POSITIONS
    
    @staticmethod
    def get_starting_position(color: PlayerColor) -> int:
        """Obtener posición inicial de un color"""
        return STARTING_POSITIONS[color]
    
    @staticmethod
    def get_goal_entry_position(color: PlayerColor) -> int:
        """Obtener posición de entrada a la meta de un color"""
        return GOAL_ENTRY_POSITIONS[color]
    
    @staticmethod
    def calculate_next_position(current_position: int, steps: int) -> int:
        """Calcular siguiente posición en el tablero circular"""
        return (current_position + steps) % BOARD_SIZE
    
    @staticmethod
    def get_goal_positions(color: PlayerColor) -> List[int]:
        """Obtener posiciones de la zona de meta para un color"""
        base = GOAL_ENTRY_POSITIONS[color]
        return [base + i for i in range(1, GOAL_POSITIONS + 1)]

# Configuraciones de IA
class AILevel(str, Enum):
    """Niveles de dificultad de la IA"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

AI_THINKING_TIME: Dict[AILevel, float] = {
    AILevel.EASY: 0.5,
    AILevel.MEDIUM: 1.0,
    AILevel.HARD: 2.0,
    AILevel.EXPERT: 3.0
}

# Configuraciones de WebSocket
WEBSOCKET_EVENTS = {
    "GAME_CREATED": "game_created",
    "PLAYER_JOINED": "player_joined",
    "PLAYER_LEFT": "player_left",
    "GAME_STARTED": "game_started",
    "TURN_CHANGED": "turn_changed",
    "DICE_ROLLED": "dice_rolled",
    "PIECE_MOVED": "piece_moved",
    "PIECE_CAPTURED": "piece_captured",
    "PLAYER_WON": "player_won",
    "GAME_ENDED": "game_ended",
    "ERROR": "error"
}

# Mensajes del juego
GAME_MESSAGES = {
    "GAME_CREATED": "Juego creado exitosamente",
    "PLAYER_JOINED": "Jugador se unió al juego",
    "PLAYER_LEFT": "Jugador abandonó el juego",
    "GAME_STARTED": "¡El juego ha comenzado!",
    "TURN_STARTED": "Es tu turno",
    "DICE_ROLLED": "Dado lanzado",
    "PIECE_MOVED": "Ficha movida",
    "PIECE_CAPTURED": "¡Ficha capturada!",
    "PIECE_REACHED_GOAL": "¡Ficha llegó a la meta!",
    "PLAYER_WON": "¡Jugador ganó!",
    "INVALID_MOVE": "Movimiento inválido",
    "NOT_YOUR_TURN": "No es tu turno",
    "GAME_FULL": "El juego está lleno",
    "GAME_NOT_FOUND": "Juego no encontrado"
}