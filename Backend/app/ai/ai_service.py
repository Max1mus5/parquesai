"""
Servicio para manejar bots IA en el juego Parqués
"""
import uuid
import asyncio
from typing import Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.game_engine import GameState, GameMove
from app.services.game_service import GameService
from app.core.game_constants import PlayerColor
from .ai_bot import AIBot, RandomBot
from .minimax import MinimaxBot
from .mcts import MCTSBot
from .difficulty_levels import DifficultyLevel, DifficultyConfig

class AIService:
    """Servicio principal para manejar bots IA"""
    
    def __init__(self):
        self.active_bots: Dict[str, AIBot] = {}  # game_id -> bot
        self.game_service = GameService()
    
    def create_bot(self, difficulty: DifficultyLevel) -> AIBot:
        """Crear un bot IA según el nivel de dificultad"""
        config = DifficultyConfig.get_config(difficulty)
        algorithm = config.get("algorithm", "random")
        
        if algorithm == "minimax":
            return MinimaxBot(difficulty)
        elif algorithm == "mcts":
            return MCTSBot(difficulty)
        else:
            return RandomBot(difficulty)
    
    async def add_bot_to_game(
        self, 
        db: AsyncSession, 
        game_id: str, 
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    ) -> bool:
        """Agregar un bot IA a un juego"""
        try:
            # Importar el motor de juego directamente
            from app.services.game_engine import game_engine
            
            # Verificar que el juego existe
            game_state = game_engine.get_game(game_id)
            if not game_state or len(game_state.players) >= 4:
                return False
            
            # Crear bot
            bot = self.create_bot(difficulty)
            
            # Crear usuario bot
            bot_user_id = str(uuid.uuid4())
            bot_username = f"Bot_{difficulty.value.capitalize()}_{len(game_state.players) + 1}"
            
            # Determinar color disponible
            used_colors = [player.color for player in game_state.players.values()]
            available_colors = [color for color in PlayerColor if color not in used_colors]
            
            if not available_colors:
                return False
            
            bot_color = available_colors[0]
            
            # Agregar bot al juego usando el motor de juego
            success = game_engine.add_player(
                game_id=game_id,
                user_id=bot_user_id,
                name=bot_username,
                color=bot_color,
                is_ai=True,
                ai_level=difficulty.value
            )
            
            if success:
                # Configurar bot
                bot.set_player_info(bot_user_id, bot_color)
                self.active_bots[game_id] = bot
                return True
            
            return False
            
        except Exception as e:
            print(f"Error adding bot to game: {e}")
            return False
    
    async def get_bot_move(
        self, 
        db: AsyncSession, 
        game_id: str, 
        dice_value: int
    ) -> Optional[GameMove]:
        """Obtener el movimiento del bot para un juego"""
        if game_id not in self.active_bots:
            return None
        
        try:
            bot = self.active_bots[game_id]
            
            # Obtener estado actual del juego
            game_state = await self.game_service.get_game_state(db, game_id, bot.player_id)
            if not game_state:
                return None
            
            # Obtener movimientos válidos
            valid_moves = await self.game_service.get_valid_moves(
                db, game_id, bot.player_id, dice_value
            )
            
            if not valid_moves:
                return None
            
            # Elegir movimiento usando el bot
            chosen_move = await bot.choose_move(game_state, valid_moves)
            return chosen_move
            
        except Exception as e:
            print(f"Error getting bot move: {e}")
            return None
    
    async def execute_bot_turn(
        self, 
        db: AsyncSession, 
        game_id: str
    ) -> bool:
        """Ejecutar el turno completo de un bot"""
        if game_id not in self.active_bots:
            return False
        
        try:
            bot = self.active_bots[game_id]
            
            # Verificar que es el turno del bot
            game_state = await self.game_service.get_game_state(db, game_id, bot.player_id)
            if not game_state or game_state.current_player != bot.player_id:
                return False
            
            # Tirar dado
            dice_result = await self.game_service.roll_dice(db, game_id, bot.player_id)
            if not dice_result:
                return False
            
            dice_value = dice_result.get("dice_value", 1)
            
            # Obtener movimiento del bot
            bot_move = await self.get_bot_move(db, game_id, dice_value)
            
            if bot_move:
                # Ejecutar movimiento
                from app.schemas.game import GameMoveRequest
                move_request = GameMoveRequest(
                    piece_index=bot_move.piece_index,
                    dice_value=dice_value
                )
                
                move_result = await self.game_service.make_move(
                    db, game_id, bot.player_id, move_request
                )
                
                return move_result is not None
            else:
                # Si no hay movimientos válidos, pasar turno
                await self.game_service.pass_turn(db, game_id, bot.player_id)
                return True
                
        except Exception as e:
            print(f"Error executing bot turn: {e}")
            return False
    
    def remove_bot_from_game(self, game_id: str):
        """Remover bot de un juego"""
        if game_id in self.active_bots:
            del self.active_bots[game_id]
    
    def get_bot_info(self, game_id: str) -> Optional[Dict]:
        """Obtener información del bot en un juego"""
        if game_id not in self.active_bots:
            return None
        
        bot = self.active_bots[game_id]
        config = bot.config
        
        return {
            "difficulty": bot.difficulty.value,
            "algorithm": config.get("algorithm", "random"),
            "description": config.get("description", "Bot IA"),
            "player_id": bot.player_id,
            "color": bot.color.value if bot.color else None
        }
    
    def get_available_difficulties(self) -> Dict:
        """Obtener niveles de dificultad disponibles"""
        return DifficultyConfig.get_all_levels()
    
    async def is_bot_turn(self, db: AsyncSession, game_id: str) -> bool:
        """Verificar si es el turno de un bot"""
        if game_id not in self.active_bots:
            return False
        
        bot = self.active_bots[game_id]
        game_state = await self.game_service.get_game_state(db, game_id, "system")
        
        return (game_state and 
                game_state.current_player == bot.player_id)
    
    async def handle_bot_turns_in_background(self, db: AsyncSession):
        """Manejar turnos de bots en segundo plano"""
        for game_id in list(self.active_bots.keys()):
            try:
                if await self.is_bot_turn(db, game_id):
                    await self.execute_bot_turn(db, game_id)
                    # Pequeña pausa para no sobrecargar
                    await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error handling bot turn for game {game_id}: {e}")

# Instancia global del servicio IA
ai_service = AIService()