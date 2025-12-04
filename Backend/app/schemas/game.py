"""
Esquemas Pydantic para el juego Parqués
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.core.game_constants import PlayerColor, GameStatus, PieceStatus, MoveType

# Esquemas de request
class GameCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    max_players: int = Field(default=4, ge=2, le=4)
    is_private: bool = False
    password: Optional[str] = None
    creator_color: PlayerColor = PlayerColor.RED

class GameJoinRequest(BaseModel):
    color: PlayerColor
    password: Optional[str] = None

class GameMoveRequest(BaseModel):
    piece_id: str
    to_position: int
    dice_value: int
    is_last_move: Optional[bool] = False  # True si es el último movimiento del turno

# Esquemas de response
class PieceResponse(BaseModel):
    id: str
    position: int
    status: PieceStatus

class PlayerResponse(BaseModel):
    id: str
    name: str
    color: PlayerColor
    score: int
    pieces: List[PieceResponse] = []
    is_ai: bool = False

class GameResponse(BaseModel):
    id: str
    name: str
    status: GameStatus
    max_players: int
    current_players: int
    is_private: bool
    created_by: str
    created_at: datetime

class GameStateResponse(BaseModel):
    id: str
    status: GameStatus
    players: List[PlayerResponse]
    current_player_id: Optional[str]
    board: Dict[int, List[str]]
    last_dice_value: Optional[int]
    last_dice1: Optional[int]
    last_dice2: Optional[int]
    is_pair: bool
    winner_id: Optional[str]

class DiceRollResponse(BaseModel):
    dice1: int
    dice2: int
    total: int
    is_pair: bool
    can_continue: bool  # True si sacó par y puede seguir jugando

class ValidMovesResponse(BaseModel):
    moves: List[Dict[str, Any]]

class GameMoveResponse(BaseModel):
    success: bool
    move: Dict[str, Any]
    message: Optional[str] = None

class GameSummaryResponse(BaseModel):
    id: str
    status: GameStatus
    players: List[Dict[str, Any]]
    current_player_id: Optional[str]
    last_dice_value: Optional[int]
    last_dice1: Optional[int]
    last_dice2: Optional[int]
    is_pair: bool
    winner_id: Optional[str]
    created_at: str
    started_at: Optional[str]
    finished_at: Optional[str]

# Esquemas para WebSocket
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GameCreatedMessage(WebSocketMessage):
    type: str = "game_created"

class PlayerJoinedMessage(WebSocketMessage):
    type: str = "player_joined"

class PlayerLeftMessage(WebSocketMessage):
    type: str = "player_left"

class GameStartedMessage(WebSocketMessage):
    type: str = "game_started"

class TurnChangedMessage(WebSocketMessage):
    type: str = "turn_changed"

class DiceRolledMessage(WebSocketMessage):
    type: str = "dice_rolled"

class PieceMovedMessage(WebSocketMessage):
    type: str = "piece_moved"

class PieceCapturedMessage(WebSocketMessage):
    type: str = "piece_captured"

class PlayerWonMessage(WebSocketMessage):
    type: str = "player_won"

class GameEndedMessage(WebSocketMessage):
    type: str = "game_ended"

class ErrorMessage(WebSocketMessage):
    type: str = "error"