"""
Bot IA base para el juego Parqués
"""
import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from app.services.game_engine import GameState, GameMove, Player
from app.core.game_constants import PlayerColor, MoveType
from .difficulty_levels import DifficultyLevel, DifficultyConfig

@dataclass
class BotMove:
    """Movimiento simplificado para bots IA"""
    player_id: str
    piece_id: str
    piece_index: int  # Para facilitar el uso
    from_position: int
    to_position: int
    dice_value: int
    captures_opponent: bool = False
    
    def to_game_move(self) -> GameMove:
        """Convertir a GameMove del motor de juego"""
        move_type = MoveType.NORMAL
        if self.from_position == -1:
            move_type = MoveType.EXIT_HOME
        elif self.to_position >= 68:
            move_type = MoveType.ENTER_GOAL
        elif self.captures_opponent:
            move_type = MoveType.CAPTURE
        
        return GameMove(
            player_id=self.player_id,
            piece_id=self.piece_id,
            from_position=self.from_position,
            to_position=self.to_position,
            dice_value=self.dice_value,
            move_type=move_type,
            captured_piece_id=None
        )

class AIBot(ABC):
    """Clase base abstracta para bots IA"""
    
    def __init__(self, difficulty: DifficultyLevel = DifficultyLevel.MEDIUM):
        self.difficulty = difficulty
        self.config = DifficultyConfig.get_config(difficulty)
        self.player_id: Optional[str] = None
        self.color: Optional[PlayerColor] = None
        
    def set_player_info(self, player_id: str, color: PlayerColor):
        """Establecer información del jugador"""
        self.player_id = player_id
        self.color = color
    
    @abstractmethod
    async def choose_move(self, game_state: GameState, valid_moves: List[BotMove]) -> BotMove:
        """Elegir el mejor movimiento disponible"""
        pass
    
    def evaluate_position(self, game_state: GameState, player_id: str) -> float:
        """Evaluar la posición actual del juego para un jugador"""
        if player_id not in game_state.players:
            return -1000.0
        
        player = game_state.players[player_id]
        score = 0.0
        
        # Obtener posiciones de las fichas
        piece_positions = [piece.position for piece in player.pieces]
        
        # Puntuación por fichas en casa (negativo)
        pieces_at_home = sum(1 for pos in piece_positions if pos == -1)
        score -= pieces_at_home * 10
        
        # Puntuación por fichas en meta (muy positivo)
        pieces_at_goal = sum(1 for pos in piece_positions if pos >= 68)
        score += pieces_at_goal * 50
        
        # Puntuación por progreso de fichas
        for pos in piece_positions:
            if pos > 0 and pos < 68:
                # Más puntos por estar más cerca de la meta
                progress = min(pos, 67) / 67.0
                score += progress * 20
        
        # Bonificación por fichas en zona segura
        safe_positions = [0, 5, 12, 17, 22, 29, 34, 39, 46, 51, 56, 63]
        for pos in piece_positions:
            if pos in safe_positions:
                score += 5
        
        # Penalización por fichas vulnerables
        vulnerable_pieces = self._count_vulnerable_pieces(game_state, player_id)
        score -= vulnerable_pieces * 8
        
        # Bonificación por fichas que pueden capturar
        capture_opportunities = self._count_capture_opportunities(game_state, player_id)
        score += capture_opportunities * 15
        
        return score
    
    def _count_vulnerable_pieces(self, game_state: GameState, player_id: str) -> int:
        """Contar fichas vulnerables a ser capturadas"""
        if player_id not in game_state.players:
            return 0
        
        player = game_state.players[player_id]
        vulnerable = 0
        safe_positions = [0, 5, 12, 17, 22, 29, 34, 39, 46, 51, 56, 63]
        
        piece_positions = [piece.position for piece in player.pieces]
        
        for pos in piece_positions:
            if pos > 0 and pos < 68 and pos not in safe_positions:
                # Verificar si hay oponentes que pueden capturar esta ficha
                for other_player_id, other_player in game_state.players.items():
                    if other_player_id != player_id:
                        other_positions = [piece.position for piece in other_player.pieces]
                        for other_pos in other_positions:
                            if other_pos >= 0 and other_pos < 68:
                                # Verificar si puede alcanzar esta posición con dados 1-6
                                for dice in range(1, 7):
                                    if (other_pos + dice) % 68 == pos:
                                        vulnerable += 1
                                        break
        
        return vulnerable
    
    def _count_capture_opportunities(self, game_state: GameState, player_id: str) -> int:
        """Contar oportunidades de captura disponibles"""
        if player_id not in game_state.players:
            return 0
        
        player = game_state.players[player_id]
        opportunities = 0
        safe_positions = [0, 5, 12, 17, 22, 29, 34, 39, 46, 51, 56, 63]
        
        piece_positions = [piece.position for piece in player.pieces]
        
        for pos in piece_positions:
            if pos >= 0 and pos < 68:
                # Verificar si puede capturar oponentes con dados 1-6
                for dice in range(1, 7):
                    target_pos = (pos + dice) % 68
                    if target_pos not in safe_positions:
                        for other_player_id, other_player in game_state.players.items():
                            if other_player_id != player_id:
                                other_positions = [piece.position for piece in other_player.pieces]
                                if target_pos in other_positions:
                                    opportunities += 1
        
        return opportunities
    
    async def _simulate_thinking_time(self):
        """Simular tiempo de pensamiento del bot"""
        thinking_time = self.config.get("thinking_time", 1.0)
        # Agregar variabilidad al tiempo de pensamiento
        actual_time = thinking_time * random.uniform(0.7, 1.3)
        await asyncio.sleep(actual_time)
    
    def _should_make_mistake(self) -> bool:
        """Determinar si el bot debería cometer un error"""
        mistake_prob = self.config.get("mistake_probability", 0.1)
        return random.random() < mistake_prob
    
    def _get_aggressive_factor(self) -> float:
        """Obtener factor de agresividad del bot"""
        return self.config.get("aggressive_play", 0.5)
    
    def _get_defensive_factor(self) -> float:
        """Obtener factor defensivo del bot"""
        return self.config.get("defensive_play", 0.5)

class RandomBot(AIBot):
    """Bot que juega de forma aleatoria mejorada"""
    
    async def choose_move(self, game_state: GameState, valid_moves: List[BotMove]) -> BotMove:
        """Elegir movimiento con lógica aleatoria mejorada"""
        await self._simulate_thinking_time()
        
        if not valid_moves:
            return None
        
        # Si debe cometer un error, elegir completamente al azar
        if self._should_make_mistake():
            return random.choice(valid_moves)
        
        # Lógica mejorada: priorizar ciertos tipos de movimientos
        prioritized_moves = []
        
        for move in valid_moves:
            priority = 0
            
            # Priorizar salir de casa
            if move.from_position == -1:
                priority += 10
            
            # Priorizar llegar a la meta
            if move.to_position >= 68:
                priority += 15
            
            # Priorizar capturas
            if move.captures_opponent:
                priority += 12
            
            # Priorizar movimientos hacia posiciones seguras
            safe_positions = [0, 5, 12, 17, 22, 29, 34, 39, 46, 51, 56, 63]
            if move.to_position in safe_positions:
                priority += 5
            
            prioritized_moves.append((move, priority))
        
        # Ordenar por prioridad y elegir entre los mejores
        prioritized_moves.sort(key=lambda x: x[1], reverse=True)
        
        # Elegir entre los top 3 movimientos
        top_moves = prioritized_moves[:3]
        chosen_move, _ = random.choice(top_moves)
        
        return chosen_move