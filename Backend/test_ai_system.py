"""
Test simple para verificar el sistema de IA
"""
import asyncio
from app.ai.difficulty_levels import DifficultyLevel, DifficultyConfig
from app.ai.ai_bot import RandomBot
from app.ai.minimax import MinimaxBot
from app.ai.mcts import MCTSBot
from app.ai.ai_service import AIService
from app.services.game_engine import GameState, GameMove, Player
from app.core.game_constants import PlayerColor

def test_difficulty_levels():
    """Test configuración de niveles de dificultad"""
    print("Testing difficulty levels...")
    
    # Test all difficulty levels
    for level in DifficultyLevel:
        config = DifficultyConfig.get_config(level)
        print(f"  {level.value}: {config['description']}")
        assert config is not None
        assert 'algorithm' in config
        assert 'description' in config
    
    print("✅ Difficulty levels test passed")

def test_bot_creation():
    """Test creación de bots"""
    print("Testing bot creation...")
    
    ai_service = AIService()
    
    # Test creating different types of bots
    easy_bot = ai_service.create_bot(DifficultyLevel.EASY)
    assert isinstance(easy_bot, RandomBot)
    print("  ✅ Easy bot (Random) created")
    
    medium_bot = ai_service.create_bot(DifficultyLevel.MEDIUM)
    assert isinstance(medium_bot, MinimaxBot)
    print("  ✅ Medium bot (Minimax) created")
    
    hard_bot = ai_service.create_bot(DifficultyLevel.HARD)
    assert isinstance(hard_bot, MinimaxBot)
    print("  ✅ Hard bot (Minimax) created")
    
    expert_bot = ai_service.create_bot(DifficultyLevel.EXPERT)
    assert isinstance(expert_bot, MCTSBot)
    print("  ✅ Expert bot (MCTS) created")
    
    print("✅ Bot creation test passed")

def test_game_state_evaluation():
    """Test evaluación de estado del juego"""
    print("Testing game state evaluation...")
    
    # Crear estado de juego simple
    game_state = GameState(id="test_game")
    
    # Crear jugador de prueba
    from app.services.game_engine import Player, Piece
    player = Player(
        id="player1",
        user_id="user1", 
        color=PlayerColor.BLUE,
        name="Test Player"
    )
    
    # Configurar fichas manualmente
    player.pieces = [
        Piece(id="blue_0", color=PlayerColor.BLUE, position=-1),  # en casa
        Piece(id="blue_1", color=PlayerColor.BLUE, position=-1),  # en casa
        Piece(id="blue_2", color=PlayerColor.BLUE, position=0),   # en inicio
        Piece(id="blue_3", color=PlayerColor.BLUE, position=10)   # avanzada
    ]
    
    game_state.players["player1"] = player
    
    # Crear bot y evaluar
    bot = RandomBot(DifficultyLevel.MEDIUM)
    bot.set_player_info("player1", PlayerColor.BLUE)
    
    score = bot.evaluate_position(game_state, "player1")
    print(f"  Position score: {score}")
    assert isinstance(score, float)
    
    print("✅ Game state evaluation test passed")

async def test_bot_move_selection():
    """Test selección de movimientos del bot"""
    print("Testing bot move selection...")
    
    # Crear movimientos válidos de prueba
    from app.ai.ai_bot import BotMove
    valid_moves = [
        BotMove(
            player_id="player1",
            piece_id="blue_0",
            piece_index=0,
            from_position=-1,
            to_position=0,
            dice_value=5
        ),
        BotMove(
            player_id="player1", 
            piece_id="blue_1",
            piece_index=1,
            from_position=10,
            to_position=15,
            dice_value=5
        )
    ]
    
    # Crear estado de juego
    game_state = GameState(id="test_game")
    
    from app.services.game_engine import Player, Piece
    player = Player(
        id="player1",
        user_id="user1",
        color=PlayerColor.BLUE,
        name="Test Player"
    )
    
    # Configurar fichas manualmente
    player.pieces = [
        Piece(id="blue_0", color=PlayerColor.BLUE, position=-1),  # en casa
        Piece(id="blue_1", color=PlayerColor.BLUE, position=10),  # en tablero
        Piece(id="blue_2", color=PlayerColor.BLUE, position=-1),  # en casa
        Piece(id="blue_3", color=PlayerColor.BLUE, position=-1)   # en casa
    ]
    
    game_state.players["player1"] = player
    
    # Test con bot aleatorio
    bot = RandomBot(DifficultyLevel.EASY)
    bot.set_player_info("player1", PlayerColor.BLUE)
    
    chosen_move = await bot.choose_move(game_state, valid_moves)
    assert chosen_move in valid_moves
    print("  ✅ Random bot chose a valid move")
    
    print("✅ Bot move selection test passed")

def test_ai_service_info():
    """Test información del servicio IA"""
    print("Testing AI service info...")
    
    ai_service = AIService()
    
    # Test getting difficulty levels
    difficulties = ai_service.get_available_difficulties()
    assert len(difficulties) == 4  # easy, medium, hard, expert
    print(f"  Available difficulties: {list(difficulties.keys())}")
    
    print("✅ AI service info test passed")

async def main():
    """Ejecutar todos los tests"""
    print("🤖 Testing AI System for Parqués Distribuido")
    print("=" * 50)
    
    try:
        test_difficulty_levels()
        test_bot_creation()
        test_game_state_evaluation()
        await test_bot_move_selection()
        test_ai_service_info()
        
        print("=" * 50)
        print("🎉 All AI system tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())