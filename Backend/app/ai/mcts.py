"""
Bot IA usando algoritmo Monte Carlo Tree Search (MCTS) para el juego Parqués
"""
import asyncio
import math
import random
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from app.services.game_engine import GameState, GameMove, Player
from .ai_bot import AIBot

@dataclass
class MCTSNode:
    """Nodo del árbol MCTS"""
    state: GameState
    parent: Optional['MCTSNode'] = None
    move: Optional[GameMove] = None
    children: List['MCTSNode'] = None
    visits: int = 0
    wins: float = 0.0
    untried_moves: List[GameMove] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.untried_moves is None:
            self.untried_moves = []
    
    def is_fully_expanded(self) -> bool:
        """Verificar si el nodo está completamente expandido"""
        return len(self.untried_moves) == 0
    
    def is_terminal(self) -> bool:
        """Verificar si el nodo es terminal"""
        for player in self.state.players.values():
            if player.is_winner or all(pos >= 68 for pos in player.pieces):
                return True
        return False
    
    def ucb1_score(self, exploration_constant: float = 1.4) -> float:
        """Calcular puntuación UCB1 para selección"""
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.wins / self.visits
        exploration = exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration
    
    def best_child(self, exploration_constant: float = 1.4) -> 'MCTSNode':
        """Seleccionar el mejor hijo usando UCB1"""
        return max(self.children, key=lambda child: child.ucb1_score(exploration_constant))
    
    def most_visited_child(self) -> 'MCTSNode':
        """Obtener el hijo más visitado"""
        return max(self.children, key=lambda child: child.visits)

class MCTSBot(AIBot):
    """Bot IA que usa Monte Carlo Tree Search"""
    
    async def choose_move(self, game_state: GameState, valid_moves: List[GameMove]) -> GameMove:
        """Elegir el mejor movimiento usando MCTS"""
        await self._simulate_thinking_time()
        
        if not valid_moves:
            return None
        
        # Si debe cometer un error, elegir un movimiento subóptimo
        if self._should_make_mistake():
            return random.choice(valid_moves)
        
        # Configuración MCTS
        simulations = self.config.get("simulations", 1000)
        exploration_constant = self.config.get("exploration_constant", 1.4)
        
        # Crear nodo raíz
        root = MCTSNode(state=game_state, untried_moves=valid_moves.copy())
        
        # Ejecutar simulaciones MCTS
        for _ in range(simulations):
            await self._mcts_iteration(root, exploration_constant)
        
        # Seleccionar el mejor movimiento
        if root.children:
            best_child = root.most_visited_child()
            return best_child.move
        
        return valid_moves[0]
    
    async def _mcts_iteration(self, root: MCTSNode, exploration_constant: float):
        """Una iteración completa de MCTS"""
        # 1. Selección
        node = self._select(root, exploration_constant)
        
        # 2. Expansión
        if not node.is_terminal() and not node.is_fully_expanded():
            node = self._expand(node)
        
        # 3. Simulación
        result = await self._simulate(node)
        
        # 4. Retropropagación
        self._backpropagate(node, result)
    
    def _select(self, node: MCTSNode, exploration_constant: float) -> MCTSNode:
        """Fase de selección: navegar por el árbol usando UCB1"""
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.best_child(exploration_constant)
        return node
    
    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Fase de expansión: agregar un nuevo nodo hijo"""
        if node.untried_moves:
            move = node.untried_moves.pop()
            new_state = self._simulate_move(node.state, move)
            
            # Obtener movimientos válidos para el nuevo estado
            new_valid_moves = self._get_valid_moves_for_state(new_state)
            
            child = MCTSNode(
                state=new_state,
                parent=node,
                move=move,
                untried_moves=new_valid_moves.copy()
            )
            
            node.children.append(child)
            return child
        
        return node
    
    async def _simulate(self, node: MCTSNode) -> float:
        """Fase de simulación: juego aleatorio hasta el final"""
        current_state = self._copy_game_state(node.state)
        max_moves = 100  # Límite para evitar simulaciones infinitas
        moves_count = 0
        
        while not self._is_terminal_state(current_state) and moves_count < max_moves:
            # Obtener jugador actual
            current_player_id = current_state.current_player
            if current_player_id not in current_state.players:
                break
            
            # Obtener movimientos válidos
            valid_moves = self._get_valid_moves_for_state(current_state)
            if not valid_moves:
                # Cambiar turno si no hay movimientos
                current_state = self._advance_turn(current_state)
                continue
            
            # Elegir movimiento aleatorio
            move = random.choice(valid_moves)
            current_state = self._simulate_move(current_state, move)
            
            # Avanzar turno
            current_state = self._advance_turn(current_state)
            moves_count += 1
        
        # Evaluar el resultado final
        return self._evaluate_final_state(current_state)
    
    def _backpropagate(self, node: MCTSNode, result: float):
        """Fase de retropropagación: actualizar estadísticas"""
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent
    
    def _simulate_move(self, game_state: GameState, move: GameMove) -> GameState:
        """Simular un movimiento y retornar el nuevo estado"""
        new_state = self._copy_game_state(game_state)
        
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
                
                # Verificar si el jugador ganó
                if all(pos >= 68 for pos in player.pieces):
                    player.is_winner = True
        
        return new_state
    
    def _copy_game_state(self, game_state: GameState) -> GameState:
        """Crear una copia profunda del estado del juego"""
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
        
        return new_state
    
    def _get_valid_moves_for_state(self, game_state: GameState) -> List[GameMove]:
        """Obtener movimientos válidos para un estado dado"""
        current_player_id = game_state.current_player
        if current_player_id not in game_state.players:
            return []
        
        moves = []
        player = game_state.players[current_player_id]
        dice_value = random.randint(1, 6)  # Simular tirada de dado
        
        for i, piece_pos in enumerate(player.pieces):
            # Movimiento desde casa
            if piece_pos == -1 and dice_value in [5, 6]:
                move = GameMove(
                    player_id=current_player_id,
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
                        player_id=current_player_id,
                        piece_index=i,
                        from_position=piece_pos,
                        to_position=min(new_pos, 72),
                        dice_value=dice_value
                    )
                    
                    # Verificar si captura oponente
                    if new_pos < 68:
                        safe_positions = [0, 5, 12, 17, 22, 29, 34, 39, 46, 51, 56, 63]
                        if new_pos not in safe_positions:
                            for other_player_id, other_player in game_state.players.items():
                                if other_player_id != current_player_id:
                                    if new_pos in other_player.pieces:
                                        move.captures_opponent = True
                                        break
                    
                    moves.append(move)
        
        return moves
    
    def _advance_turn(self, game_state: GameState) -> GameState:
        """Avanzar al siguiente turno"""
        if not game_state.turn_order:
            return game_state
        
        current_index = game_state.turn_order.index(game_state.current_player)
        next_index = (current_index + 1) % len(game_state.turn_order)
        game_state.current_player = game_state.turn_order[next_index]
        
        return game_state
    
    def _is_terminal_state(self, game_state: GameState) -> bool:
        """Verificar si el estado es terminal"""
        for player in game_state.players.values():
            if player.is_winner or all(pos >= 68 for pos in player.pieces):
                return True
        return False
    
    def _evaluate_final_state(self, game_state: GameState) -> float:
        """Evaluar el estado final del juego"""
        if self.player_id not in game_state.players:
            return 0.0
        
        player = game_state.players[self.player_id]
        
        # Si ganamos, retornar 1.0
        if player.is_winner or all(pos >= 68 for pos in player.pieces):
            return 1.0
        
        # Si perdimos (otro jugador ganó), retornar 0.0
        for other_player_id, other_player in game_state.players.items():
            if other_player_id != self.player_id:
                if other_player.is_winner or all(pos >= 68 for pos in other_player.pieces):
                    return 0.0
        
        # Evaluación intermedia basada en progreso
        our_score = self.evaluate_position(game_state, self.player_id)
        
        # Normalizar la puntuación entre 0 y 1
        max_possible_score = 200.0  # Estimación del máximo puntaje posible
        normalized_score = max(0.0, min(1.0, (our_score + 100) / max_possible_score))
        
        return normalized_score