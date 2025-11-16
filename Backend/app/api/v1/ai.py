"""
Endpoints para el sistema de IA y bots
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.security import get_current_user
from app.db.models.user import User
from app.ai.ai_service import ai_service
from app.ai.difficulty_levels import DifficultyLevel
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/ai", tags=["ai"])

class AddBotRequest(BaseModel):
    """Request para agregar bot a un juego"""
    game_id: str
    difficulty: str = "medium"

class BotMoveRequest(BaseModel):
    """Request para obtener movimiento de bot"""
    game_id: str
    dice_value: int

@router.get("/difficulties")
async def get_difficulty_levels():
    """Obtener niveles de dificultad disponibles"""
    return {
        "difficulties": ai_service.get_available_difficulties(),
        "default": "medium"
    }

@router.post("/bot/add")
async def add_bot_to_game(
    request: AddBotRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Agregar un bot IA a un juego"""
    try:
        # Validar nivel de dificultad
        try:
            difficulty = DifficultyLevel(request.difficulty.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid difficulty level: {request.difficulty}"
            )
        
        # Agregar bot al juego
        success = await ai_service.add_bot_to_game(db, request.game_id, difficulty)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not add bot to game. Game may be full or not exist."
            )
        
        bot_info = ai_service.get_bot_info(request.game_id)
        
        return {
            "success": True,
            "message": "Bot added successfully",
            "bot_info": bot_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding bot: {str(e)}"
        )

@router.get("/bot/{game_id}/info")
async def get_bot_info(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """Obtener información del bot en un juego"""
    bot_info = ai_service.get_bot_info(game_id)
    
    if not bot_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No bot found in this game"
        )
    
    return bot_info

@router.post("/bot/move")
async def get_bot_move(
    request: BotMoveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener movimiento del bot (para testing)"""
    try:
        bot_move = await ai_service.get_bot_move(
            db, request.game_id, request.dice_value
        )
        
        if not bot_move:
            return {
                "move": None,
                "message": "No valid moves available for bot"
            }
        
        return {
            "move": {
                "player_id": bot_move.player_id,
                "piece_index": bot_move.piece_index,
                "from_position": bot_move.from_position,
                "to_position": bot_move.to_position,
                "dice_value": bot_move.dice_value,
                "captures_opponent": bot_move.captures_opponent
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting bot move: {str(e)}"
        )

@router.post("/bot/{game_id}/execute-turn")
async def execute_bot_turn(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Ejecutar turno completo del bot"""
    try:
        success = await ai_service.execute_bot_turn(db, game_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not execute bot turn. May not be bot's turn or bot not found."
            )
        
        return {
            "success": True,
            "message": "Bot turn executed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing bot turn: {str(e)}"
        )

@router.delete("/bot/{game_id}")
async def remove_bot_from_game(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remover bot de un juego"""
    ai_service.remove_bot_from_game(game_id)
    
    return {
        "success": True,
        "message": "Bot removed from game"
    }

@router.get("/bot/{game_id}/is-turn")
async def is_bot_turn(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verificar si es el turno del bot"""
    is_turn = await ai_service.is_bot_turn(db, game_id)
    
    return {
        "is_bot_turn": is_turn,
        "game_id": game_id
    }

@router.get("/stats")
async def get_ai_stats():
    """Obtener estadísticas del sistema IA"""
    return {
        "active_bots": len(ai_service.active_bots),
        "games_with_bots": list(ai_service.active_bots.keys()),
        "available_algorithms": ["random", "minimax", "mcts"],
        "difficulty_levels": list(DifficultyLevel)
    }

@router.post("/test/evaluate-position")
async def test_position_evaluation(
    game_id: str,
    player_id: str,
    difficulty: str = "medium",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Evaluar posición del juego (para testing y debugging)"""
    try:
        # Validar dificultad
        try:
            diff_level = DifficultyLevel(difficulty.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid difficulty level: {difficulty}"
            )
        
        # Crear bot temporal para evaluación
        bot = ai_service.create_bot(diff_level)
        bot.set_player_info(player_id, None)
        
        # Obtener estado del juego
        from app.services.game_service import GameService
        game_service = GameService()
        game_state = await game_service.get_game_state(db, game_id, player_id)
        
        if not game_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        
        # Evaluar posición
        score = bot.evaluate_position(game_state, player_id)
        
        return {
            "game_id": game_id,
            "player_id": player_id,
            "difficulty": difficulty,
            "position_score": score,
            "evaluation_details": {
                "pieces_at_home": sum(1 for p in game_state.players[player_id].pieces if p == -1),
                "pieces_at_goal": sum(1 for p in game_state.players[player_id].pieces if p >= 68),
                "pieces_in_play": sum(1 for p in game_state.players[player_id].pieces if 0 <= p < 68)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating position: {str(e)}"
        )