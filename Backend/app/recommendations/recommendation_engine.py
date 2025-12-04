"""
Motor de recomendaciones inteligente para el juego Parqués
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import random
import math

from app.recommendations.pattern_analyzer import (
    PatternAnalyzer, PlayerPattern, PlayStyle, GamePhase
)
from app.core.game_constants import PlayerColor
from app.ai.difficulty_levels import DifficultyLevel


class RecommendationType(Enum):
    """Tipos de recomendaciones"""
    STRATEGY = "strategy"
    OPPONENT = "opponent"
    COLOR = "color"
    DIFFICULTY = "difficulty"
    TRAINING = "training"
    IMPROVEMENT = "improvement"


@dataclass
class Recommendation:
    """Recomendación individual"""
    type: RecommendationType
    title: str
    description: str
    confidence: float  # 0.0 - 1.0
    priority: int      # 1 = alta, 2 = media, 3 = baja
    data: Dict[str, Any]  # Datos específicos de la recomendación


@dataclass
class RecommendationSet:
    """Conjunto de recomendaciones para un usuario"""
    user_id: str
    recommendations: List[Recommendation]
    generated_at: str
    player_pattern: PlayerPattern


class RecommendationEngine:
    """Motor principal de recomendaciones"""
    
    def __init__(self, pattern_analyzer: PatternAnalyzer):
        self.pattern_analyzer = pattern_analyzer
        self.recommendation_cache: Dict[str, RecommendationSet] = {}
    
    def generate_recommendations(
        self, 
        user_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> RecommendationSet:
        """Generar recomendaciones personalizadas para un usuario"""
        
        # Obtener patrón del jugador
        player_pattern = self.pattern_analyzer.get_player_pattern(user_id)
        if not player_pattern:
            # Si no hay patrón, crear uno por defecto
            player_pattern = self.pattern_analyzer._create_default_pattern(user_id)
        
        recommendations = []
        
        # Generar diferentes tipos de recomendaciones
        recommendations.extend(self._generate_strategy_recommendations(player_pattern, context))
        recommendations.extend(self._generate_opponent_recommendations(player_pattern, context))
        recommendations.extend(self._generate_color_recommendations(player_pattern, context))
        recommendations.extend(self._generate_difficulty_recommendations(player_pattern, context))
        recommendations.extend(self._generate_training_recommendations(player_pattern, context))
        recommendations.extend(self._generate_improvement_recommendations(player_pattern, context))
        
        # Ordenar por prioridad y confianza
        recommendations.sort(key=lambda r: (r.priority, -r.confidence))
        
        # Limitar a las mejores recomendaciones
        recommendations = recommendations[:10]
        
        recommendation_set = RecommendationSet(
            user_id=user_id,
            recommendations=recommendations,
            generated_at=str(datetime.now()),
            player_pattern=player_pattern
        )
        
        self.recommendation_cache[user_id] = recommendation_set
        return recommendation_set
    
    def _generate_strategy_recommendations(
        self, 
        pattern: PlayerPattern, 
        context: Optional[Dict[str, Any]]
    ) -> List[Recommendation]:
        """Generar recomendaciones de estrategia"""
        recommendations = []
        
        # Recomendación basada en estilo de juego
        if pattern.play_style == PlayStyle.AGGRESSIVE:
            if pattern.win_rate < 0.3:
                recommendations.append(Recommendation(
                    type=RecommendationType.STRATEGY,
                    title="Considera un enfoque más balanceado",
                    description="Tu estilo agresivo puede estar limitando tus victorias. "
                               "Intenta combinar ataques con movimientos defensivos.",
                    confidence=0.8,
                    priority=1,
                    data={
                        "current_style": "aggressive",
                        "suggested_style": "balanced",
                        "reason": "low_win_rate"
                    }
                ))
        
        elif pattern.play_style == PlayStyle.DEFENSIVE:
            if pattern.avg_game_duration > 35:
                recommendations.append(Recommendation(
                    type=RecommendationType.STRATEGY,
                    title="Sé más proactivo en tus movimientos",
                    description="Tus juegos tienden a ser largos. Considera tomar más riesgos "
                               "calculados para acelerar tu progreso.",
                    confidence=0.7,
                    priority=2,
                    data={
                        "current_style": "defensive",
                        "suggested_style": "balanced",
                        "reason": "long_games"
                    }
                ))
        
        # Recomendación basada en rendimiento por fase
        weakest_phase = min(pattern.performance_by_phase.items(), key=lambda x: x[1])
        if weakest_phase[1] < 0.4:
            phase_name = weakest_phase[0].value
            recommendations.append(Recommendation(
                type=RecommendationType.STRATEGY,
                title=f"Mejora tu juego en la fase {phase_name}",
                description=f"Tu rendimiento en la fase {phase_name} del juego es bajo. "
                           f"Practica estrategias específicas para esta fase.",
                confidence=0.9,
                priority=1,
                data={
                    "weak_phase": phase_name,
                    "performance": weakest_phase[1],
                    "suggestions": self._get_phase_suggestions(weakest_phase[0])
                }
            ))
        
        return recommendations
    
    def _generate_opponent_recommendations(
        self, 
        pattern: PlayerPattern, 
        context: Optional[Dict[str, Any]]
    ) -> List[Recommendation]:
        """Generar recomendaciones de oponentes"""
        recommendations = []
        
        # Recomendar nivel de IA basado en habilidad
        if pattern.win_rate < 0.2:
            recommendations.append(Recommendation(
                type=RecommendationType.OPPONENT,
                title="Practica contra IA nivel fácil",
                description="Para mejorar tus habilidades, te recomendamos jugar contra "
                           "bots de nivel fácil hasta ganar más consistencia.",
                confidence=0.9,
                priority=1,
                data={
                    "recommended_difficulty": "easy",
                    "reason": "skill_building",
                    "target_win_rate": 0.4
                }
            ))
        
        elif pattern.win_rate > 0.6:
            recommendations.append(Recommendation(
                type=RecommendationType.OPPONENT,
                title="Desafíate contra IA nivel experto",
                description="Tu alto nivel de juego te permite enfrentar desafíos mayores. "
                           "Prueba contra bots expertos para seguir mejorando.",
                confidence=0.8,
                priority=2,
                data={
                    "recommended_difficulty": "expert",
                    "reason": "skill_advancement",
                    "current_win_rate": pattern.win_rate
                }
            ))
        
        # Recomendación de juego multijugador
        if pattern.consistency > 0.7:
            recommendations.append(Recommendation(
                type=RecommendationType.OPPONENT,
                title="Únete a partidas multijugador",
                description="Tu juego consistente te hace un buen candidato para partidas "
                           "multijugador competitivas.",
                confidence=0.7,
                priority=2,
                data={
                    "game_type": "multiplayer",
                    "reason": "high_consistency",
                    "consistency_score": pattern.consistency
                }
            ))
        
        return recommendations
    
    def _generate_color_recommendations(
        self, 
        pattern: PlayerPattern, 
        context: Optional[Dict[str, Any]]
    ) -> List[Recommendation]:
        """Generar recomendaciones de color"""
        recommendations = []
        
        # Si el jugador tiene colores muy preferidos, sugerir variedad
        if len(pattern.preferred_colors) <= 1:
            other_colors = [color for color in PlayerColor if color not in pattern.preferred_colors]
            recommended_color = random.choice(other_colors)
            
            recommendations.append(Recommendation(
                type=RecommendationType.COLOR,
                title=f"Prueba jugar con {recommended_color.value}",
                description="Experimentar con diferentes colores puede ayudarte a "
                           "desarrollar nuevas estrategias y adaptabilidad.",
                confidence=0.6,
                priority=3,
                data={
                    "recommended_color": recommended_color.value,
                    "reason": "variety",
                    "current_preferences": [c.value for c in pattern.preferred_colors]
                }
            ))
        
        return recommendations
    
    def _generate_difficulty_recommendations(
        self, 
        pattern: PlayerPattern, 
        context: Optional[Dict[str, Any]]
    ) -> List[Recommendation]:
        """Generar recomendaciones de dificultad"""
        recommendations = []
        
        # Recomendar dificultad basada en win rate y adaptabilidad
        if pattern.win_rate < 0.25 and pattern.adaptability < 0.5:
            recommendations.append(Recommendation(
                type=RecommendationType.DIFFICULTY,
                title="Comienza con dificultad fácil",
                description="Para construir confianza y aprender las mecánicas básicas, "
                           "te recomendamos empezar con bots de dificultad fácil.",
                confidence=0.9,
                priority=1,
                data={
                    "recommended_difficulty": DifficultyLevel.EASY.value,
                    "reason": "skill_building",
                    "current_win_rate": pattern.win_rate
                }
            ))
        
        elif pattern.win_rate > 0.4 and pattern.adaptability > 0.6:
            recommendations.append(Recommendation(
                type=RecommendationType.DIFFICULTY,
                title="Prueba dificultad difícil",
                description="Tu buen rendimiento y adaptabilidad sugieren que puedes "
                           "manejar desafíos más complejos.",
                confidence=0.8,
                priority=2,
                data={
                    "recommended_difficulty": DifficultyLevel.HARD.value,
                    "reason": "skill_advancement",
                    "current_win_rate": pattern.win_rate,
                    "adaptability": pattern.adaptability
                }
            ))
        
        return recommendations
    
    def _generate_training_recommendations(
        self, 
        pattern: PlayerPattern, 
        context: Optional[Dict[str, Any]]
    ) -> List[Recommendation]:
        """Generar recomendaciones de entrenamiento"""
        recommendations = []
        
        # Entrenamiento basado en debilidades
        if pattern.risk_tolerance < 0.3:
            recommendations.append(Recommendation(
                type=RecommendationType.TRAINING,
                title="Practica tomar riesgos calculados",
                description="Tu juego es muy conservador. Practica identificar cuándo "
                           "vale la pena tomar riesgos para obtener ventajas.",
                confidence=0.8,
                priority=2,
                data={
                    "training_type": "risk_taking",
                    "current_risk_tolerance": pattern.risk_tolerance,
                    "exercises": [
                        "Practica capturas cuando tengas ventaja numérica",
                        "Intenta bloquear oponentes en situaciones clave",
                        "Sal de casa con 5 cuando sea estratégicamente ventajoso"
                    ]
                }
            ))
        
        elif pattern.risk_tolerance > 0.8:
            recommendations.append(Recommendation(
                type=RecommendationType.TRAINING,
                title="Desarrolla paciencia estratégica",
                description="Tu estilo muy arriesgado puede beneficiarse de más paciencia "
                           "y planificación a largo plazo.",
                confidence=0.8,
                priority=2,
                data={
                    "training_type": "strategic_patience",
                    "current_risk_tolerance": pattern.risk_tolerance,
                    "exercises": [
                        "Practica mantener piezas seguras cuando sea posible",
                        "Planifica movimientos con 2-3 turnos de anticipación",
                        "Evalúa riesgos antes de cada movimiento agresivo"
                    ]
                }
            ))
        
        # Entrenamiento de consistencia
        if pattern.consistency < 0.4:
            recommendations.append(Recommendation(
                type=RecommendationType.TRAINING,
                title="Trabaja en la consistencia",
                description="Tu rendimiento varía mucho entre juegos. Practica mantener "
                           "un nivel estable de juego.",
                confidence=0.7,
                priority=2,
                data={
                    "training_type": "consistency",
                    "current_consistency": pattern.consistency,
                    "exercises": [
                        "Establece una rutina de análisis antes de cada movimiento",
                        "Practica contra el mismo nivel de IA repetidamente",
                        "Revisa tus juegos para identificar errores recurrentes"
                    ]
                }
            ))
        
        return recommendations
    
    def _generate_improvement_recommendations(
        self, 
        pattern: PlayerPattern, 
        context: Optional[Dict[str, Any]]
    ) -> List[Recommendation]:
        """Generar recomendaciones de mejora específicas"""
        recommendations = []
        
        # Mejora basada en estrategias favoritas
        if "balanced_play" in pattern.favorite_strategies:
            recommendations.append(Recommendation(
                type=RecommendationType.IMPROVEMENT,
                title="Especialízate en una estrategia",
                description="Tu juego balanceado es bueno, pero especializarte en una "
                           "estrategia específica puede darte ventaja competitiva.",
                confidence=0.6,
                priority=3,
                data={
                    "improvement_type": "specialization",
                    "current_strategies": pattern.favorite_strategies,
                    "suggested_specializations": [
                        "Estrategia de bloqueo avanzado",
                        "Juego agresivo controlado",
                        "Defensa y contraataque"
                    ]
                }
            ))
        
        # Mejora basada en duración de juegos
        if pattern.avg_game_duration > 40:
            recommendations.append(Recommendation(
                type=RecommendationType.IMPROVEMENT,
                title="Acelera tu toma de decisiones",
                description="Tus juegos tienden a ser largos. Practica tomar decisiones "
                           "más rápidas sin sacrificar calidad.",
                confidence=0.7,
                priority=2,
                data={
                    "improvement_type": "decision_speed",
                    "current_avg_duration": pattern.avg_game_duration,
                    "target_duration": 30,
                    "tips": [
                        "Practica reconocimiento de patrones comunes",
                        "Establece límites de tiempo para tus movimientos",
                        "Usa intuición para movimientos obvios"
                    ]
                }
            ))
        
        return recommendations
    
    def _get_phase_suggestions(self, phase: GamePhase) -> List[str]:
        """Obtener sugerencias específicas para una fase del juego"""
        suggestions = {
            GamePhase.EARLY: [
                "Prioriza sacar piezas de casa con 5 o 6",
                "Mantén piezas en posiciones seguras inicialmente",
                "Observa las estrategias de tus oponentes"
            ],
            GamePhase.MIDDLE: [
                "Busca oportunidades de captura seguras",
                "Usa bloqueos estratégicos para ralentizar oponentes",
                "Balancea agresión con protección de tus piezas"
            ],
            GamePhase.LATE: [
                "Prioriza llevar piezas a la meta sobre capturas",
                "Calcula exactamente los movimientos necesarios para ganar",
                "Mantén la presión sobre oponentes cercanos a ganar"
            ]
        }
        return suggestions.get(phase, [])
    
    def get_cached_recommendations(self, user_id: str) -> Optional[RecommendationSet]:
        """Obtener recomendaciones desde cache"""
        return self.recommendation_cache.get(user_id)
    
    def update_recommendations(
        self, 
        user_id: str, 
        feedback: Dict[str, Any]
    ) -> RecommendationSet:
        """Actualizar recomendaciones basado en feedback del usuario"""
        # Implementar lógica de feedback para mejorar recomendaciones futuras
        current_recommendations = self.recommendation_cache.get(user_id)
        
        if current_recommendations:
            # Ajustar confianza basado en feedback
            for rec in current_recommendations.recommendations:
                if feedback.get(rec.title) == "helpful":
                    rec.confidence = min(rec.confidence + 0.1, 1.0)
                elif feedback.get(rec.title) == "not_helpful":
                    rec.confidence = max(rec.confidence - 0.1, 0.1)
        
        # Regenerar recomendaciones con el feedback incorporado
        return self.generate_recommendations(user_id, {"feedback": feedback})
    
    def clear_cache(self):
        """Limpiar cache de recomendaciones"""
        self.recommendation_cache.clear()


# Importar datetime que faltaba
from datetime import datetime