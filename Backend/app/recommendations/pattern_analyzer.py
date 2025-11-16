"""
Analizador de patrones de juego para el sistema de recomendaciones
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics
from collections import defaultdict, Counter

from app.core.game_constants import PlayerColor, GameStatus


class PlayStyle(Enum):
    """Estilos de juego identificados"""
    AGGRESSIVE = "aggressive"      # Juega rápido, toma riesgos
    DEFENSIVE = "defensive"        # Juega conservador, evita riesgos
    BALANCED = "balanced"          # Equilibrio entre agresivo y defensivo
    STRATEGIC = "strategic"        # Planifica a largo plazo
    OPPORTUNISTIC = "opportunistic" # Aprovecha oportunidades


class GamePhase(Enum):
    """Fases del juego"""
    EARLY = "early"       # Primeros movimientos, salir de casa
    MIDDLE = "middle"     # Desarrollo del juego
    LATE = "late"         # Final del juego


@dataclass
class PlayerPattern:
    """Patrón de juego de un jugador"""
    user_id: str
    play_style: PlayStyle
    preferred_colors: List[PlayerColor]
    avg_game_duration: float
    win_rate: float
    favorite_strategies: List[str]
    performance_by_phase: Dict[GamePhase, float]
    risk_tolerance: float  # 0.0 = muy conservador, 1.0 = muy arriesgado
    adaptability: float    # Qué tan bien se adapta a diferentes situaciones
    consistency: float     # Qué tan consistente es su rendimiento


@dataclass
class GameAnalysis:
    """Análisis de un juego específico"""
    game_id: str
    duration: float
    winner_color: Optional[PlayerColor]
    player_performances: Dict[str, float]
    key_moments: List[Dict[str, Any]]
    strategies_used: List[str]
    phase_durations: Dict[GamePhase, float]


class PatternAnalyzer:
    """Analizador de patrones de juego"""
    
    def __init__(self):
        self.patterns_cache: Dict[str, PlayerPattern] = {}
        self.game_analyses: Dict[str, GameAnalysis] = {}
    
    def analyze_player_history(
        self, 
        user_id: str, 
        game_history: List[Dict[str, Any]],
        move_history: List[Dict[str, Any]]
    ) -> PlayerPattern:
        """Analizar el historial de un jugador para identificar patrones"""
        
        if not game_history:
            return self._create_default_pattern(user_id)
        
        # Análisis básico de estadísticas
        total_games = len(game_history)
        wins = sum(1 for game in game_history if game.get('winner_id') == user_id)
        win_rate = wins / total_games if total_games > 0 else 0.0
        
        # Análisis de colores preferidos
        color_usage = Counter(game.get('player_color') for game in game_history)
        preferred_colors = [PlayerColor(color) for color, _ in color_usage.most_common(2)]
        
        # Análisis de duración de juegos
        durations = [game.get('duration', 0) for game in game_history if game.get('duration')]
        avg_duration = statistics.mean(durations) if durations else 30.0
        
        # Análisis de estilo de juego basado en movimientos
        play_style = self._analyze_play_style(move_history)
        
        # Análisis de rendimiento por fase
        performance_by_phase = self._analyze_phase_performance(game_history, move_history)
        
        # Análisis de tolerancia al riesgo
        risk_tolerance = self._calculate_risk_tolerance(move_history)
        
        # Análisis de adaptabilidad
        adaptability = self._calculate_adaptability(game_history, move_history)
        
        # Análisis de consistencia
        consistency = self._calculate_consistency(game_history)
        
        # Estrategias favoritas
        favorite_strategies = self._identify_favorite_strategies(move_history)
        
        pattern = PlayerPattern(
            user_id=user_id,
            play_style=play_style,
            preferred_colors=preferred_colors,
            avg_game_duration=avg_duration,
            win_rate=win_rate,
            favorite_strategies=favorite_strategies,
            performance_by_phase=performance_by_phase,
            risk_tolerance=risk_tolerance,
            adaptability=adaptability,
            consistency=consistency
        )
        
        self.patterns_cache[user_id] = pattern
        return pattern
    
    def _create_default_pattern(self, user_id: str) -> PlayerPattern:
        """Crear patrón por defecto para jugadores nuevos"""
        return PlayerPattern(
            user_id=user_id,
            play_style=PlayStyle.BALANCED,
            preferred_colors=[PlayerColor.BLUE, PlayerColor.RED],
            avg_game_duration=25.0,
            win_rate=0.25,  # 25% esperado en juego de 4 jugadores
            favorite_strategies=["balanced_play"],
            performance_by_phase={
                GamePhase.EARLY: 0.5,
                GamePhase.MIDDLE: 0.5,
                GamePhase.LATE: 0.5
            },
            risk_tolerance=0.5,
            adaptability=0.5,
            consistency=0.5
        )
    
    def _analyze_play_style(self, move_history: List[Dict[str, Any]]) -> PlayStyle:
        """Analizar el estilo de juego basado en los movimientos"""
        if not move_history:
            return PlayStyle.BALANCED
        
        # Métricas para determinar estilo
        aggressive_moves = 0
        defensive_moves = 0
        strategic_moves = 0
        total_moves = len(move_history)
        
        for move in move_history:
            move_type = move.get('move_type', '')
            
            # Movimientos agresivos: atacar, tomar riesgos
            if 'attack' in move_type or 'capture' in move_type:
                aggressive_moves += 1
            
            # Movimientos defensivos: proteger piezas, jugar seguro
            elif 'safe' in move_type or 'protect' in move_type:
                defensive_moves += 1
            
            # Movimientos estratégicos: bloquear, posicionarse
            elif 'block' in move_type or 'position' in move_type:
                strategic_moves += 1
        
        if total_moves == 0:
            return PlayStyle.BALANCED
        
        aggressive_ratio = aggressive_moves / total_moves
        defensive_ratio = defensive_moves / total_moves
        strategic_ratio = strategic_moves / total_moves
        
        # Determinar estilo dominante
        if aggressive_ratio > 0.4:
            return PlayStyle.AGGRESSIVE
        elif defensive_ratio > 0.4:
            return PlayStyle.DEFENSIVE
        elif strategic_ratio > 0.3:
            return PlayStyle.STRATEGIC
        else:
            return PlayStyle.BALANCED
    
    def _analyze_phase_performance(
        self, 
        game_history: List[Dict[str, Any]], 
        move_history: List[Dict[str, Any]]
    ) -> Dict[GamePhase, float]:
        """Analizar rendimiento por fase del juego"""
        
        phase_performance = {
            GamePhase.EARLY: 0.5,
            GamePhase.MIDDLE: 0.5,
            GamePhase.LATE: 0.5
        }
        
        # Análisis simplificado basado en resultados de juegos
        wins_by_phase = defaultdict(int)
        games_by_phase = defaultdict(int)
        
        for game in game_history:
            duration = game.get('duration', 30)
            won = game.get('winner_id') == game.get('user_id')
            
            # Clasificar juego por duración (aproximación de fase donde se decidió)
            if duration < 15:  # Juego corto - decidido en fase temprana
                phase = GamePhase.EARLY
            elif duration < 30:  # Juego medio - decidido en fase media
                phase = GamePhase.MIDDLE
            else:  # Juego largo - decidido en fase tardía
                phase = GamePhase.LATE
            
            games_by_phase[phase] += 1
            if won:
                wins_by_phase[phase] += 1
        
        # Calcular rendimiento por fase
        for phase in GamePhase:
            if games_by_phase[phase] > 0:
                phase_performance[phase] = wins_by_phase[phase] / games_by_phase[phase]
        
        return phase_performance
    
    def _calculate_risk_tolerance(self, move_history: List[Dict[str, Any]]) -> float:
        """Calcular tolerancia al riesgo del jugador"""
        if not move_history:
            return 0.5
        
        risky_moves = 0
        safe_moves = 0
        
        for move in move_history:
            move_type = move.get('move_type', '')
            
            if any(keyword in move_type for keyword in ['attack', 'risky', 'aggressive']):
                risky_moves += 1
            elif any(keyword in move_type for keyword in ['safe', 'defensive', 'protect']):
                safe_moves += 1
        
        total_classified = risky_moves + safe_moves
        if total_classified == 0:
            return 0.5
        
        return risky_moves / total_classified
    
    def _calculate_adaptability(
        self, 
        game_history: List[Dict[str, Any]], 
        move_history: List[Dict[str, Any]]
    ) -> float:
        """Calcular adaptabilidad del jugador"""
        if len(game_history) < 3:
            return 0.5
        
        # Medir variabilidad en estrategias y rendimiento
        strategies_used = set()
        performance_variance = []
        
        for game in game_history:
            # Simular estrategias basadas en duración y resultado
            duration = game.get('duration', 30)
            won = game.get('winner_id') == game.get('user_id')
            
            if duration < 20:
                strategies_used.add('quick_game')
            elif duration > 40:
                strategies_used.add('long_game')
            
            if won:
                strategies_used.add('winning_strategy')
            
            # Usar duración como proxy de rendimiento
            performance_variance.append(duration)
        
        # Adaptabilidad basada en variedad de estrategias
        strategy_diversity = len(strategies_used) / 5.0  # Normalizar a 0-1
        
        # Adaptabilidad basada en consistencia de rendimiento
        if len(performance_variance) > 1:
            variance = statistics.variance(performance_variance)
            # Menor varianza = más consistente = menos adaptable en este contexto
            variance_factor = min(variance / 100.0, 1.0)
        else:
            variance_factor = 0.5
        
        return min((strategy_diversity + variance_factor) / 2.0, 1.0)
    
    def _calculate_consistency(self, game_history: List[Dict[str, Any]]) -> float:
        """Calcular consistencia del jugador"""
        if len(game_history) < 3:
            return 0.5
        
        # Medir consistencia en rendimiento
        performances = []
        for game in game_history:
            # Usar duración y resultado como métricas de rendimiento
            duration = game.get('duration', 30)
            won = game.get('winner_id') == game.get('user_id')
            
            # Crear score de rendimiento
            performance_score = duration
            if won:
                performance_score *= 1.5  # Bonus por ganar
            
            performances.append(performance_score)
        
        if len(performances) < 2:
            return 0.5
        
        # Calcular coeficiente de variación (menor = más consistente)
        mean_perf = statistics.mean(performances)
        std_perf = statistics.stdev(performances)
        
        if mean_perf == 0:
            return 0.5
        
        cv = std_perf / mean_perf
        # Convertir a score de consistencia (0-1, donde 1 = muy consistente)
        consistency = max(0.0, 1.0 - min(cv, 1.0))
        
        return consistency
    
    def _identify_favorite_strategies(self, move_history: List[Dict[str, Any]]) -> List[str]:
        """Identificar estrategias favoritas del jugador"""
        if not move_history:
            return ["balanced_play"]
        
        strategy_counts = defaultdict(int)
        
        # Analizar patrones en los movimientos
        for move in move_history:
            move_type = move.get('move_type', '')
            
            if 'attack' in move_type:
                strategy_counts['aggressive_play'] += 1
            elif 'safe' in move_type:
                strategy_counts['defensive_play'] += 1
            elif 'block' in move_type:
                strategy_counts['blocking_strategy'] += 1
            else:
                strategy_counts['balanced_play'] += 1
        
        # Retornar las 3 estrategias más usadas
        top_strategies = sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)
        return [strategy for strategy, _ in top_strategies[:3]]
    
    def analyze_game(
        self, 
        game_data: Dict[str, Any], 
        moves_data: List[Dict[str, Any]]
    ) -> GameAnalysis:
        """Analizar un juego específico"""
        
        game_id = game_data.get('id', '')
        duration = game_data.get('duration', 0)
        winner_color = game_data.get('winner_color')
        
        # Analizar rendimiento de jugadores
        player_performances = {}
        for player in game_data.get('players', []):
            player_id = player.get('id')
            # Calcular rendimiento basado en posición final, movimientos, etc.
            performance = self._calculate_player_performance(player, moves_data)
            player_performances[player_id] = performance
        
        # Identificar momentos clave
        key_moments = self._identify_key_moments(moves_data)
        
        # Identificar estrategias usadas
        strategies_used = self._identify_game_strategies(moves_data)
        
        # Calcular duración por fase
        phase_durations = self._calculate_phase_durations(duration, moves_data)
        
        analysis = GameAnalysis(
            game_id=game_id,
            duration=duration,
            winner_color=PlayerColor(winner_color) if winner_color else None,
            player_performances=player_performances,
            key_moments=key_moments,
            strategies_used=strategies_used,
            phase_durations=phase_durations
        )
        
        self.game_analyses[game_id] = analysis
        return analysis
    
    def _calculate_player_performance(
        self, 
        player_data: Dict[str, Any], 
        moves_data: List[Dict[str, Any]]
    ) -> float:
        """Calcular rendimiento de un jugador en un juego"""
        # Métricas básicas
        score = player_data.get('score', 0)
        pieces_home = sum(1 for piece in player_data.get('pieces', []) 
                         if piece.get('status') == 'finished')
        
        # Contar movimientos del jugador
        player_moves = [move for move in moves_data 
                       if move.get('player_id') == player_data.get('id')]
        
        # Calcular performance score
        performance = (score * 0.4 + pieces_home * 0.3 + len(player_moves) * 0.3) / 10.0
        return min(performance, 1.0)
    
    def _identify_key_moments(self, moves_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identificar momentos clave del juego"""
        key_moments = []
        
        for i, move in enumerate(moves_data):
            # Identificar capturas, bloqueos, llegadas a meta, etc.
            if move.get('captured_piece'):
                key_moments.append({
                    'type': 'capture',
                    'move_index': i,
                    'player_id': move.get('player_id'),
                    'description': 'Captura de pieza enemiga'
                })
            
            if move.get('piece_finished'):
                key_moments.append({
                    'type': 'finish',
                    'move_index': i,
                    'player_id': move.get('player_id'),
                    'description': 'Pieza llegó a la meta'
                })
        
        return key_moments
    
    def _identify_game_strategies(self, moves_data: List[Dict[str, Any]]) -> List[str]:
        """Identificar estrategias usadas en el juego"""
        strategies = set()
        
        capture_count = sum(1 for move in moves_data if move.get('captured_piece'))
        block_count = sum(1 for move in moves_data if move.get('blocked_opponent'))
        
        if capture_count > len(moves_data) * 0.1:
            strategies.add('aggressive_play')
        
        if block_count > len(moves_data) * 0.05:
            strategies.add('blocking_strategy')
        
        strategies.add('standard_play')
        
        return list(strategies)
    
    def _calculate_phase_durations(
        self, 
        total_duration: float, 
        moves_data: List[Dict[str, Any]]
    ) -> Dict[GamePhase, float]:
        """Calcular duración de cada fase del juego"""
        total_moves = len(moves_data)
        
        if total_moves == 0:
            return {
                GamePhase.EARLY: total_duration / 3,
                GamePhase.MIDDLE: total_duration / 3,
                GamePhase.LATE: total_duration / 3
            }
        
        # Dividir movimientos en fases
        early_moves = total_moves // 3
        middle_moves = total_moves // 3
        late_moves = total_moves - early_moves - middle_moves
        
        return {
            GamePhase.EARLY: (early_moves / total_moves) * total_duration,
            GamePhase.MIDDLE: (middle_moves / total_moves) * total_duration,
            GamePhase.LATE: (late_moves / total_moves) * total_duration
        }
    
    def get_player_pattern(self, user_id: str) -> Optional[PlayerPattern]:
        """Obtener patrón de jugador desde cache"""
        return self.patterns_cache.get(user_id)
    
    def clear_cache(self):
        """Limpiar cache de patrones"""
        self.patterns_cache.clear()
        self.game_analyses.clear()