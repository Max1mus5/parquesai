"""
Endpoints de la API para el juego Parqués
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user
from app.db.models.user import User
from app.services.game_service import game_service
from app.schemas.game import (
    GameCreateRequest, GameJoinRequest, GameMoveRequest,
    GameResponse, GameStateResponse, PlayerResponse,
    DiceRollResponse, ValidMovesResponse
)

router = APIRouter()

@router.post("/create", response_model=GameResponse)
async def create_game(
    request: GameCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Crear un nuevo juego"""
    try:
        game = await game_service.create_game(db, str(current_user.id), request)
        return game
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/available", response_model=List[GameResponse])
async def get_available_games(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener juegos disponibles para unirse"""
    try:
        games = await game_service.get_available_games(db)
        return games
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/{game_id}/join", response_model=PlayerResponse)
async def join_game(
    game_id: str,
    request: GameJoinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unirse a un juego existente"""
    try:
        player = await game_service.join_game(db, game_id, str(current_user.id), request)
        return player
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/{game_id}/start")
async def start_game(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Iniciar un juego"""
    try:
        success = await game_service.start_game(db, game_id, str(current_user.id))
        return {"success": success, "message": "Juego iniciado exitosamente"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/{game_id}/roll-dice", response_model=DiceRollResponse)
async def roll_dice(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lanzar el dado DOS veces (reglas de Parqués)"""
    try:
        dice_result = await game_service.roll_dice(db, game_id, str(current_user.id))
        return DiceRollResponse(**dice_result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{game_id}/valid-moves/{dice_value}", response_model=ValidMovesResponse)
async def get_valid_moves(
    game_id: str,
    dice_value: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener movimientos válidos para el valor del dado"""
    try:
        moves = await game_service.get_valid_moves(db, game_id, str(current_user.id), dice_value)
        return ValidMovesResponse(moves=moves)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/{game_id}/move")
async def make_move(
    game_id: str,
    request: GameMoveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Realizar un movimiento"""
    try:
        game_move = await game_service.make_move(db, game_id, str(current_user.id), request)
        if not game_move:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Movimiento inválido"
            )
        
        return {
            "success": True,
            "move": {
                "piece_id": game_move.piece_id,
                "from_position": game_move.from_position,
                "to_position": game_move.to_position,
                "move_type": game_move.move_type,
                "captured_piece_id": game_move.captured_piece_id,
                "timestamp": game_move.timestamp.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{game_id}/state", response_model=GameStateResponse)
async def get_game_state(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener estado completo del juego"""
    try:
        game_state = await game_service.get_game_state(db, game_id, str(current_user.id))
        return game_state
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/{game_id}/pass-turn")
async def pass_turn(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Pasar turno cuando no hay movimientos válidos"""
    try:
        success = await game_service.pass_turn(db, game_id, str(current_user.id))
        return {"success": True, "message": "Turno pasado exitosamente"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/{game_id}/leave")
async def leave_game(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Abandonar un juego"""
    try:
        success = await game_service.leave_game(db, game_id, str(current_user.id))
        return {"success": success, "message": "Has abandonado el juego"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{game_id}/summary")
async def get_game_summary(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener resumen del juego"""
    try:
        from app.services.game_engine import game_engine
        summary = game_engine.get_game_summary(game_id)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Juego no encontrado"
            )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )