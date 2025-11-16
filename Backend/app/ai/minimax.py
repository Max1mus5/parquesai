"""
Bot IA usando algoritmo Minimax para el juego Parqués
"""
import asyncio
import random
from typing import List, Optional, Tuple
from app.services.game_engine import GameState, GameMove, Player
from .ai_bot import AIBot

class MinimaxBot(AIBot):
    """Bot IA que usa el algoritmo Minimax"""
    
    async def choose_move(self, game_state: GameState, valid_moves: List[GameMove]) -> GameMove:
        """Elegir el mejor movimiento usando Minimax"""
        await self._simulate_thinking_time()
        
        if not valid_moves:
            return None
        
        # Si debe cometer un error, elegir un movimiento subóptimo
        if self._should_make_mistake():
            # Elegir entre los movimientos menos óptimos
            worst_moves = valid_moves[-3:] if len(valid_moves) >= 3 else valid_moves
            return random.choice(worst_moves)
        
        depth = self.config.get("depth", 2)
        best_move = None
        best_score = float('-inf')
        
        # Evaluar cada movimiento posible
        for move in valid_moves:
            # Simular el movimiento
            new_state = self._simulate_move(game_state, move)
            
            # Evaluar usando Minimax
            score = await self._minimax(
                new_state, 
                depth - 1, 
                False,  # Es turno del oponente
                float('-inf'), 
                float('inf')
            )
            
            # Agregar ruido aleatorio para variabilidad
            score += random.uniform(-0.5, 0.5)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move or valid_moves[0]
    
    async def _minimax(
        self, 
        game_state: GameState, 
        depth: int, 
        is_maximizing: bool,
        alpha: float, 
        beta: float
    ) -> float:
        """Algoritmo Minimax con poda Alpha-Beta"""
        
        # Caso base: profundidad 0 o juego terminado
        if depth == 0 or self._is_terminal_state(game_state):
            return self.evaluate_position(game_state, self.player_id)
        
        if is_maximizing:
            max_score = float('-inf')
            
            # Simular todos los movimientos posibles para nuestro bot
            possible_moves = self._get_possible_moves(game_state, self.player_id)
            
            for move in possible_moves:
                new_state = self._simulate_move(game_state, move)
                score = await self._minimax(new_state, depth - 1, False, alpha, beta)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                
                # Poda Alpha-Beta
                if beta <= alpha:
                    break
            
            return max_score
        else:
            min_score = float('inf')
            
            # Simular movimientos de los oponentes
            opponents = [pid for pid in game_state.players.keys() if pid != self.player_id]
            
            if opponents:
                # Elegir el oponente más amenazante
                opponent_id = self._get_most_threatening_opponent(game_state, opponents)
                possible_moves = self._get_possible_moves(game_state, opponent_id)
                
                for move in possible_moves:
                    new_state = self._simulate_move(game_state, move)
                    score = await self._minimax(new_state, depth - 1, True, alpha, beta)
                    min_score = min(min_score, score)
                    beta = min(beta, score)
                    
                    # Poda Alpha-Beta
                    if beta <= alpha:
                        break
            
            return min_score
    
    def _simulate_move(self, game_state: GameState, move: GameMove) -> GameState:
        """Simular un movimiento y retornar el nuevo estado"""
        # Crear una copia profunda del estado del juego
        new_state = GameState()
        new_state.game_id = game_state.game_id
        new_state.status = game_state.status
        new_state.current_player = game_state.current_player
        new_state.turn_order = game_state.turn_order.copy()
        new_state.dice_value = game_state.dice_value
        new_state.consecutive_sixes = game_state.consecutive_sixes
        
        # Copiar jugadores
        for player_id, player in game_state.players.items():
            new_player = Player(
                id=player.id,
                user_id=player.user_id,
                color=player.color,
                pieces=player.pieces.copy(),
                is_winner=player.is_winner
            )
            new_state.players[player_id] = new_player
        
        # Aplicar el movimiento
        if move.player_id in new_state.players:
            player = new_state.players[move.player_id]
            
            # Mover la ficha
            if 0 <= move.piece_index < len(player.pieces):
                player.pieces[move.piece_index] = move.to_position
                
                # Si captura oponente, enviar ficha capturada a casa
                if move.captures_opponent:
                    for other_player_id, other_player in new_state.players.items():
                        if other_player_id != move.player_id:
                            for i, pos in enumerate(other_player.pieces):
                                if pos == move.to_position:
                                    other_player.pieces[i] = -1
                                    break
        
        return new_state
    
    def _get_possible_moves(self, game_state: GameState, player_id: str) -> List[GameMove]:
        """Obtener todos los movimientos posibles para un jugador"""
        if player_id not in game_state.players:
            return []
        
        moves = []
        player = game_state.players[player_id]
        dice_value = random.randint(1, 6)  # Simular tirada de dado
        
        for i, piece_pos in enumerate(player.pieces):
            # Movimiento desde casa
            if piece_pos == -1 and dice_value in [5, 6]:
                move = GameMove(
                    player_id=player_id,
                    piece_index=i,
                    from_position=-1,
                    to_position=0,
                    dice_value=dice_value
                )
                moves.append(move)
            
            # Movimiento normal
            elif piece_pos >= 0 and piece_pos < 68:
                new_pos = piece_pos + dice_value
                if new_pos <= 72:  # No pasar de la meta
                    move = GameMove(
                        player_id=player_id,
                        piece_index=i,
                        from_position=piece_pos,
                        to_position=min(new_pos, 72),
                        dice_value=dice_value
                    )
                    
                    # Verificar si captura oponente
                    if new_pos < 68:
                        for other_player_id, other_player in game_state.players.items():
                            if other_player_id != player_id:
                                if new_pos in other_player.pieces:
                                    move.captures_opponent = True
                                    break
                    
                    moves.append(move)
        
        return moves
    
    def _get_most_threatening_opponent(self, game_state: GameState, opponents: List[str]) -> str:
        """Obtener el oponente más amenazante"""
        best_opponent = opponents[0]
        best_score = float('-inf')
        
        for opponent_id in opponents:
            score = self.evaluate_position(game_state, opponent_id)
            if score > best_score:
                best_score = score
                best_opponent = opponent_id
        
        return best_opponent
    
    def _is_terminal_state(self, game_state: GameState) -> bool:
        """Verificar si el estado es terminal (juego terminado)"""
        for player in game_state.players.values():
            if player.is_winner:
                return True
            
            # Verificar si todas las fichas están en la meta
            if all(pos >= 68 for pos in player.pieces):
                return True
        
        return False