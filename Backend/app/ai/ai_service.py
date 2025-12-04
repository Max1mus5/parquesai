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
        self.active_bots: Dict[str, Dict[str, AIBot]] = {}  # game_id -> {player_id -> bot}
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
            print(f"🤖 Intentando agregar bot al juego {game_id} con dificultad {difficulty}")
            # Importar modelos necesarios
            from app.services.game_engine import game_engine
            from app.db.models.game import GamePlayer
            from app.db.models.user import User
            from datetime import datetime
            
            # Verificar que el juego existe
            game_state = game_engine.get_game(game_id)
            print(f"🎮 Estado del juego: {game_state is not None}")
            if game_state:
                print(f"👥 Jugadores actuales: {len(game_state.players)}/4")
            if not game_state or len(game_state.players) >= 4:
                print(f"❌ No se puede agregar bot: juego no existe o está lleno")
                return False
            
            # Crear bot
            bot = self.create_bot(difficulty)
            print(f"✅ Bot creado: {type(bot).__name__}")
            
            # Crear usuario bot con ID único
            bot_user_id = str(uuid.uuid4())
            # Usar UUID para garantizar username y email únicos
            unique_suffix = str(uuid.uuid4())[:8]
            bot_username = f"Bot_{difficulty.value.capitalize()}_{unique_suffix}"
            
            # Determinar color disponible
            used_colors = [player.color for player in game_state.players.values()]
            available_colors = [color for color in PlayerColor if color not in used_colors]
            
            if not available_colors:
                print(f"❌ No hay colores disponibles")
                return False
            
            bot_color = available_colors[0]
            
            # CREAR UN USUARIO BOT EN LA BASE DE DATOS
            bot_user = User(
                id=bot_user_id,
                username=bot_username.lower(),
                email=f"{bot_user_id}@bot.local",  # Usar UUID para email único
                display_name=bot_username,
                password_hash="$2b$12$BOT.NO.LOGIN.ALLOWED",  # Hash inválido para evitar login
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            db.add(bot_user)
            await db.flush()  # Flush para que exista antes de crear el GamePlayer
            
            # Agregar bot al juego usando el motor de juego
            player_id = game_engine.add_player(
                game_id=game_id,
                user_id=bot_user_id,
                name=bot_username,
                color=bot_color,
                is_ai=True,
                ai_level=difficulty.value
            )
            
            if player_id:  # Ahora retorna player_id o None
                # Configurar bot con el player_id correcto
                bot.set_player_info(player_id, bot_color)
                
                # Guardar bot con el player_id (NO bot_user_id)
                if game_id not in self.active_bots:
                    self.active_bots[game_id] = {}
                self.active_bots[game_id][player_id] = bot
                
                print(f"✅ Bot guardado con player_id: {player_id}")
                
                # Guardar el bot como jugador en la base de datos
                db_player = GamePlayer(
                    game_id=game_id,
                    user_id=bot_user_id,
                    color=bot_color,
                    joined_at=datetime.utcnow()
                )
                
                db.add(db_player)
                await db.commit()
                
                print(f"✅ Bot agregado exitosamente: {bot_username} ({bot_color.value}) al juego {game_id}")
                
                return True
            
            print(f"❌ game_engine.add_player retornó False")
            return False
            
        except Exception as e:
            print(f"❌ Error adding bot to game: {e}")
            import traceback
            traceback.print_exc()
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
            # Obtener el bot del jugador actual
            from app.services.game_engine import game_engine
            game_state = game_engine.get_game(game_id)
            if not game_state:
                print(f"❌ Game state not found for {game_id}")
                return None
            
            current_player_id = game_state.current_player_id
            
            # Verificar si el jugador actual es un bot
            if current_player_id not in self.active_bots[game_id]:
                print(f"❌ Current player {current_player_id} is not a bot")
                return None
            
            bot = self.active_bots[game_id][current_player_id]
            
            # Obtener movimientos válidos directamente del game_engine
            valid_moves = game_engine.get_valid_moves(game_id, current_player_id, dice_value)
            
            if not valid_moves:
                print(f"⚠️ No valid moves for bot {current_player_id}")
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
            print(f"❌ Game {game_id} not found in active_bots")
            return False
        
        try:
            from app.services.game_engine import game_engine
            
            # Obtener estado del juego
            game_state = game_engine.get_game(game_id)
            if not game_state:
                print(f"❌ Game state not found for {game_id}")
                return False
            
            current_player_id = game_state.current_player_id
            print(f"🔍 Current player ID: {current_player_id}")
            print(f"🔍 Active bots in game: {list(self.active_bots[game_id].keys())}")
            
            # Verificar si el jugador actual es un bot
            if current_player_id not in self.active_bots[game_id]:
                print(f"❌ Current player {current_player_id} is not a bot")
                return False
            
            bot = self.active_bots[game_id][current_player_id]
            
            # Tirar dado DOS veces usando el motor de juego
            from app.services.game_engine import game_engine
            dice_result = game_engine.roll_dice(game_id, current_player_id)
            
            if not dice_result:
                print(f"❌ Bot no pudo lanzar dados")
                return False
            
            dice_value = dice_result['total']  # Usar la suma de ambos dados
            print(f"🎲 Bot tiró: {dice_result['dice1']} + {dice_result['dice2']} = {dice_value}, par={dice_result['is_pair']}")
            
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
                # Si no hay movimientos válidos, pasar turno usando game_engine
                print(f"⚠️ No valid moves for bot {current_player_id}, passing turn")
                game_engine.pass_turn(game_id, current_player_id)
                return True
                
        except Exception as e:
            print(f"Error executing bot turn: {e}")
            return False
    
    def remove_bot_from_game(self, game_id: str, player_id: str = None):
        """Remover bot de un juego"""
        if game_id in self.active_bots:
            if player_id and player_id in self.active_bots[game_id]:
                del self.active_bots[game_id][player_id]
            else:
                del self.active_bots[game_id]
    
    def get_bot_info(self, game_id: str, player_id: str = None) -> Optional[Dict]:
        """Obtener información del bot en un juego"""
        if game_id not in self.active_bots:
            return None
        
        if player_id:
            if player_id not in self.active_bots[game_id]:
                return None
            bot = self.active_bots[game_id][player_id]
            config = bot.config
            
            return {
                "difficulty": bot.difficulty.value,
                "algorithm": config.get("algorithm", "random"),
                "description": config.get("description", "Bot IA"),
                "player_id": bot.player_id,
                "color": bot.color.value if bot.color else None
            }
        else:
            # Retornar info de todos los bots en el juego
            return {
                pid: {
                    "difficulty": bot.difficulty.value,
                    "algorithm": bot.config.get("algorithm", "random"),
                    "description": bot.config.get("description", "Bot IA"),
                    "player_id": bot.player_id,
                    "color": bot.color.value if bot.color else None
                }
                for pid, bot in self.active_bots[game_id].items()
            }
    
    def get_available_difficulties(self) -> Dict:
        """Obtener niveles de dificultad disponibles"""
        return DifficultyConfig.get_all_levels()
    
    async def is_bot_turn(self, db: AsyncSession, game_id: str) -> bool:
        """Verificar si es el turno de un bot"""
        if game_id not in self.active_bots:
            return False
        
        try:
            from app.services.game_engine import game_engine
            game_state = game_engine.get_game(game_id)
            
            if not game_state:
                return False
            
            # Verificar si el jugador actual es alguno de los bots
            current_player_id = game_state.current_player_id
            return current_player_id in self.active_bots[game_id]
            
        except Exception as e:
            print(f"Error checking bot turn: {e}")
            return False
    
    async def handle_bot_turns_in_background(self, db: AsyncSession):
        """Manejar turnos de bots en segundo plano"""
        for game_id in list(self.active_bots.keys()):
            try:
                if await self.is_bot_turn(db, game_id):
                    print(f"🤖 Bot turn detected in game {game_id}, executing...")
                    success = await self.execute_bot_turn(db, game_id)
                    if success:
                        print(f"✅ Bot turn executed successfully in game {game_id}")
                    else:
                        print(f"❌ Bot turn failed in game {game_id}")
                    # Pequeña pausa para no sobrecargar
                    await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Error handling bot turn for game {game_id}: {e}")

# Instancia global del servicio IA
ai_service = AIService()