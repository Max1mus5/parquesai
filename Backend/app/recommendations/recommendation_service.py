"""
Servicio de recomendaciones inteligente
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from app.db.models.game import Game, GamePlayer, GameMove as DBGameMove
from app.db.models.user import User, GameStatistics
from app.recommendations.pattern_analyzer import PatternAnalyzer, PlayerPattern
from app.recommendations.recommendation_engine import (
    RecommendationEngine, RecommendationSet, Recommendation, RecommendationType
)
from app.core.game_constants import PlayerColor, GameStatus


class RecommendationService:
    """Servicio principal de recomendaciones"""
    
    def __init__(self):
        self.pattern_analyzer = PatternAnalyzer()
        self.recommendation_engine = RecommendationEngine(self.pattern_analyzer)
        self._last_analysis_update: Dict[str, datetime] = {}
    
    async def get_user_recommendations(
        self, 
        db: AsyncSession, 
        user_id: str,
        force_refresh: bool = False
    ) -> RecommendationSet:
        """Obtener recomendaciones para un usuario"""
        
        # Verificar si necesitamos actualizar el análisis
        if force_refresh or self._should_update_analysis(user_id):
            await self._update_user_analysis(db, user_id)
        
        # Generar o obtener recomendaciones
        recommendations = self.recommendation_engine.get_cached_recommendations(user_id)
        if not recommendations or force_refresh:
            recommendations = self.recommendation_engine.generate_recommendations(user_id)
        
        return recommendations
    
    async def get_strategy_recommendations(
        self, 
        db: AsyncSession, 
        user_id: str
    ) -> List[Recommendation]:
        """Obtener recomendaciones específicas de estrategia"""
        recommendations = await self.get_user_recommendations(db, user_id)
        return [r for r in recommendations.recommendations 
                if r.type == RecommendationType.STRATEGY]
    
    async def get_opponent_recommendations(
        self, 
        db: AsyncSession, 
        user_id: str
    ) -> List[Recommendation]:
        """Obtener recomendaciones de oponentes"""
        recommendations = await self.get_user_recommendations(db, user_id)
        return [r for r in recommendations.recommendations 
                if r.type == RecommendationType.OPPONENT]
    
    async def get_training_recommendations(
        self, 
        db: AsyncSession, 
        user_id: str
    ) -> List[Recommendation]:
        """Obtener recomendaciones de entrenamiento"""
        recommendations = await self.get_user_recommendations(db, user_id)
        return [r for r in recommendations.recommendations 
                if r.type == RecommendationType.TRAINING]
    
    async def analyze_game_performance(
        self, 
        db: AsyncSession, 
        game_id: str, 
        user_id: str
    ) -> Dict[str, Any]:
        """Analizar el rendimiento de un usuario en un juego específico"""
        
        # Obtener datos del juego
        game_query = select(Game).options(
            selectinload(Game.players),
            selectinload(Game.moves)
        ).where(Game.id == game_id)
        
        result = await db.execute(game_query)
        game = result.scalar_one_or_none()
        
        if not game:
            return {"error": "Game not found"}
        
        # Verificar que el usuario participó en el juego
        user_player = None
        for player in game.players:
            if player.user_id == user_id:
                user_player = player
                break
        
        if not user_player:
            return {"error": "User did not participate in this game"}
        
        # Convertir datos para análisis
        game_data = {
            "id": str(game.id),
            "duration": self._calculate_game_duration(game),
            "winner_color": self._get_winner_color(game),
            "players": [
                {
                    "id": str(p.id),
                    "user_id": str(p.user_id),
                    "color": p.color.value,
                    "score": 0,  # Calcular basado en piezas
                    "pieces": []  # Simular estado de piezas
                }
                for p in game.players
            ]
        }
        
        moves_data = [
            {
                "player_id": str(move.player_id),
                "move_type": "standard",  # Simplificado
                "timestamp": move.created_at
            }
            for move in game.moves
        ]
        
        # Analizar el juego
        analysis = self.pattern_analyzer.analyze_game(game_data, moves_data)
        
        # Obtener rendimiento específico del usuario
        user_performance = analysis.player_performances.get(str(user_player.id), 0.5)
        
        # Generar insights específicos del juego
        insights = self._generate_game_insights(analysis, user_player, user_performance)
        
        return {
            "game_id": game_id,
            "user_performance": user_performance,
            "game_duration": analysis.duration,
            "strategies_used": analysis.strategies_used,
            "key_moments": analysis.key_moments,
            "insights": insights,
            "recommendations": self._generate_post_game_recommendations(
                analysis, user_player, user_performance
            )
        }
    
    async def get_improvement_suggestions(
        self, 
        db: AsyncSession, 
        user_id: str
    ) -> Dict[str, Any]:
        """Obtener sugerencias específicas de mejora"""
        
        # Obtener patrón del jugador
        pattern = self.pattern_analyzer.get_player_pattern(user_id)
        if not pattern:
            await self._update_user_analysis(db, user_id)
            pattern = self.pattern_analyzer.get_player_pattern(user_id)
        
        if not pattern:
            return {"error": "No data available for analysis"}
        
        # Identificar áreas de mejora
        improvement_areas = []
        
        # Análisis de win rate
        if pattern.win_rate < 0.25:
            improvement_areas.append({
                "area": "win_rate",
                "current": pattern.win_rate,
                "target": 0.35,
                "priority": "high",
                "suggestions": [
                    "Practica contra IA de nivel fácil",
                    "Estudia estrategias básicas de Parqués",
                    "Observa replays de jugadores expertos"
                ]
            })
        
        # Análisis de consistencia
        if pattern.consistency < 0.5:
            improvement_areas.append({
                "area": "consistency",
                "current": pattern.consistency,
                "target": 0.7,
                "priority": "medium",
                "suggestions": [
                    "Establece una rutina de análisis antes de cada movimiento",
                    "Practica contra el mismo nivel de dificultad repetidamente",
                    "Mantén un diario de juegos para identificar patrones"
                ]
            })
        
        # Análisis de adaptabilidad
        if pattern.adaptability < 0.5:
            improvement_areas.append({
                "area": "adaptability",
                "current": pattern.adaptability,
                "target": 0.7,
                "priority": "medium",
                "suggestions": [
                    "Experimenta con diferentes estrategias",
                    "Juega contra diferentes estilos de oponentes",
                    "Practica ajustar tu estrategia según el contexto del juego"
                ]
            })
        
        # Análisis por fases
        for phase, performance in pattern.performance_by_phase.items():
            if performance < 0.4:
                improvement_areas.append({
                    "area": f"{phase.value}_game",
                    "current": performance,
                    "target": 0.6,
                    "priority": "high",
                    "suggestions": self._get_phase_improvement_suggestions(phase)
                })
        
        return {
            "user_id": user_id,
            "overall_skill_level": self._calculate_skill_level(pattern),
            "improvement_areas": improvement_areas,
            "strengths": self._identify_strengths(pattern),
            "next_steps": self._generate_next_steps(improvement_areas)
        }
    
    async def update_recommendations_with_feedback(
        self, 
        db: AsyncSession, 
        user_id: str, 
        feedback: Dict[str, Any]
    ) -> RecommendationSet:
        """Actualizar recomendaciones basado en feedback del usuario"""
        return self.recommendation_engine.update_recommendations(user_id, feedback)
    
    async def get_personalized_challenges(
        self, 
        db: AsyncSession, 
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Obtener desafíos personalizados para el usuario"""
        
        pattern = self.pattern_analyzer.get_player_pattern(user_id)
        if not pattern:
            await self._update_user_analysis(db, user_id)
            pattern = self.pattern_analyzer.get_player_pattern(user_id)
        
        if not pattern:
            return []
        
        challenges = []
        
        # Desafío basado en win rate
        if pattern.win_rate < 0.5:
            challenges.append({
                "id": "improve_win_rate",
                "title": "Mejora tu tasa de victoria",
                "description": f"Alcanza una tasa de victoria del 40% (actual: {pattern.win_rate:.1%})",
                "target": 0.4,
                "current": pattern.win_rate,
                "reward": "Desbloquea nuevas estrategias avanzadas",
                "difficulty": "medium"
            })
        
        # Desafío de consistencia
        if pattern.consistency < 0.7:
            challenges.append({
                "id": "consistency_challenge",
                "title": "Mantén la consistencia",
                "description": "Gana 3 juegos consecutivos contra IA de tu nivel",
                "target": 3,
                "current": 0,
                "reward": "Acceso a análisis avanzado de partidas",
                "difficulty": "hard"
            })
        
        # Desafío de adaptabilidad
        if pattern.adaptability < 0.6:
            challenges.append({
                "id": "adaptability_challenge",
                "title": "Maestro de la adaptación",
                "description": "Gana juegos usando 3 estrategias diferentes",
                "target": 3,
                "current": len(pattern.favorite_strategies),
                "reward": "Título de 'Estratega Versátil'",
                "difficulty": "medium"
            })
        
        return challenges
    
    def _should_update_analysis(self, user_id: str) -> bool:
        """Verificar si necesitamos actualizar el análisis del usuario"""
        last_update = self._last_analysis_update.get(user_id)
        if not last_update:
            return True
        
        # Actualizar cada 24 horas o si no hay patrón en cache
        time_threshold = datetime.now() - timedelta(hours=24)
        pattern_exists = self.pattern_analyzer.get_player_pattern(user_id) is not None
        
        return last_update < time_threshold or not pattern_exists
    
    async def _update_user_analysis(self, db: AsyncSession, user_id: str):
        """Actualizar análisis de patrones del usuario"""
        
        # Obtener historial de juegos del usuario
        games_query = select(Game).options(
            selectinload(Game.players),
            selectinload(Game.moves)
        ).join(GamePlayer).where(
            and_(
                GamePlayer.user_id == user_id,
                Game.status == GameStatus.FINISHED
            )
        ).order_by(desc(Game.created_at)).limit(50)  # Últimos 50 juegos
        
        result = await db.execute(games_query)
        games = result.scalars().all()
        
        # Convertir a formato para análisis
        game_history = []
        move_history = []
        
        for game in games:
            # Encontrar el jugador en este juego
            user_player = None
            for player in game.players:
                if player.user_id == user_id:
                    user_player = player
                    break
            
            if user_player:
                game_data = {
                    "id": str(game.id),
                    "user_id": user_id,
                    "player_color": user_player.color.value,
                    "winner_id": str(game.winner_id) if game.winner_id else None,
                    "duration": self._calculate_game_duration(game),
                    "created_at": game.created_at
                }
                game_history.append(game_data)
                
                # Agregar movimientos del usuario
                user_moves = [
                    {
                        "game_id": str(game.id),
                        "player_id": str(user_player.id),
                        "move_type": "standard",  # Simplificado
                        "timestamp": move.created_at
                    }
                    for move in game.moves if move.player_id == user_player.id
                ]
                move_history.extend(user_moves)
        
        # Analizar patrones
        pattern = self.pattern_analyzer.analyze_player_history(
            user_id, game_history, move_history
        )
        
        # Actualizar timestamp
        self._last_analysis_update[user_id] = datetime.now()
    
    def _calculate_game_duration(self, game: Game) -> float:
        """Calcular duración del juego en minutos"""
        if game.finished_at and game.created_at:
            duration = (game.finished_at - game.created_at).total_seconds() / 60
            return max(duration, 1.0)  # Mínimo 1 minuto
        return 25.0  # Duración por defecto
    
    def _get_winner_color(self, game: Game) -> Optional[str]:
        """Obtener color del ganador"""
        if game.winner_id:
            for player in game.players:
                if player.id == game.winner_id:
                    return player.color.value
        return None
    
    def _generate_game_insights(
        self, 
        analysis, 
        user_player, 
        user_performance: float
    ) -> List[str]:
        """Generar insights específicos del juego"""
        insights = []
        
        if user_performance > 0.7:
            insights.append("Excelente rendimiento en este juego")
        elif user_performance < 0.3:
            insights.append("Hay oportunidades de mejora en tu estrategia")
        
        if analysis.duration > 40:
            insights.append("El juego fue más largo de lo usual - considera ser más agresivo")
        elif analysis.duration < 15:
            insights.append("Juego rápido - buen control del ritmo")
        
        if "aggressive_play" in analysis.strategies_used:
            insights.append("Mostraste un estilo agresivo en este juego")
        
        return insights
    
    def _generate_post_game_recommendations(
        self, 
        analysis, 
        user_player, 
        user_performance: float
    ) -> List[str]:
        """Generar recomendaciones post-juego"""
        recommendations = []
        
        if user_performance < 0.4:
            recommendations.append("Practica más contra IA de nivel similar")
            recommendations.append("Revisa las estrategias básicas de Parqués")
        
        if analysis.duration > 35:
            recommendations.append("Intenta tomar decisiones más rápidas")
            recommendations.append("Practica reconocimiento de patrones comunes")
        
        return recommendations
    
    def _calculate_skill_level(self, pattern: PlayerPattern) -> str:
        """Calcular nivel de habilidad general"""
        score = (
            pattern.win_rate * 0.4 +
            pattern.consistency * 0.3 +
            pattern.adaptability * 0.3
        )
        
        if score >= 0.8:
            return "expert"
        elif score >= 0.6:
            return "advanced"
        elif score >= 0.4:
            return "intermediate"
        else:
            return "beginner"
    
    def _identify_strengths(self, pattern: PlayerPattern) -> List[str]:
        """Identificar fortalezas del jugador"""
        strengths = []
        
        if pattern.win_rate > 0.5:
            strengths.append("Alta tasa de victoria")
        
        if pattern.consistency > 0.7:
            strengths.append("Juego consistente")
        
        if pattern.adaptability > 0.7:
            strengths.append("Buena adaptabilidad")
        
        if pattern.risk_tolerance > 0.6 and pattern.win_rate > 0.4:
            strengths.append("Buen manejo del riesgo")
        
        # Analizar rendimiento por fases
        best_phase = max(pattern.performance_by_phase.items(), key=lambda x: x[1])
        if best_phase[1] > 0.6:
            strengths.append(f"Excelente en fase {best_phase[0].value}")
        
        return strengths if strengths else ["Potencial de mejora en todas las áreas"]
    
    def _generate_next_steps(self, improvement_areas: List[Dict[str, Any]]) -> List[str]:
        """Generar próximos pasos basados en áreas de mejora"""
        if not improvement_areas:
            return ["Continúa practicando para mantener tu nivel"]
        
        # Priorizar por importancia
        high_priority = [area for area in improvement_areas if area["priority"] == "high"]
        
        next_steps = []
        
        if high_priority:
            area = high_priority[0]
            next_steps.extend(area["suggestions"][:2])  # Top 2 sugerencias
        
        next_steps.append("Juega regularmente para mantener el progreso")
        next_steps.append("Experimenta con diferentes estrategias")
        
        return next_steps[:4]  # Máximo 4 pasos
    
    def _get_phase_improvement_suggestions(self, phase) -> List[str]:
        """Obtener sugerencias de mejora para una fase específica"""
        from app.recommendations.pattern_analyzer import GamePhase
        
        suggestions = {
            GamePhase.EARLY: [
                "Practica la salida eficiente de casa",
                "Estudia las mejores posiciones iniciales",
                "Aprende cuándo es seguro sacar múltiples piezas"
            ],
            GamePhase.MIDDLE: [
                "Mejora tu juego táctico y capturas",
                "Practica el uso estratégico de bloqueos",
                "Desarrolla mejor timing para ataques"
            ],
            GamePhase.LATE: [
                "Practica el cálculo exacto para llegar a meta",
                "Mejora la defensa en situaciones críticas",
                "Aprende a mantener la presión hasta el final"
            ]
        }
        
        return suggestions.get(phase, ["Practica más juegos en esta fase"])


# Crear instancia global del servicio
recommendation_service = RecommendationService()