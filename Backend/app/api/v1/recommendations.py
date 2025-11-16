"""
Endpoints API para el sistema de recomendaciones inteligente
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models.user import User
from app.core.security import get_current_user
from app.recommendations.recommendation_service import recommendation_service
from app.recommendations.recommendation_engine import RecommendationType


router = APIRouter()


# Schemas de respuesta
class RecommendationResponse(BaseModel):
    """Respuesta de recomendación individual"""
    type: str
    title: str
    description: str
    confidence: float
    priority: int
    data: Dict[str, Any]


class RecommendationSetResponse(BaseModel):
    """Respuesta de conjunto de recomendaciones"""
    user_id: str
    recommendations: List[RecommendationResponse]
    generated_at: str
    total_recommendations: int


class PlayerPatternResponse(BaseModel):
    """Respuesta de patrón de jugador"""
    user_id: str
    play_style: str
    preferred_colors: List[str]
    avg_game_duration: float
    win_rate: float
    favorite_strategies: List[str]
    risk_tolerance: float
    adaptability: float
    consistency: float


class GameAnalysisResponse(BaseModel):
    """Respuesta de análisis de juego"""
    game_id: str
    user_performance: float
    game_duration: float
    strategies_used: List[str]
    key_moments: List[Dict[str, Any]]
    insights: List[str]
    recommendations: List[str]


class ImprovementSuggestionsResponse(BaseModel):
    """Respuesta de sugerencias de mejora"""
    user_id: str
    overall_skill_level: str
    improvement_areas: List[Dict[str, Any]]
    strengths: List[str]
    next_steps: List[str]


class ChallengeResponse(BaseModel):
    """Respuesta de desafío personalizado"""
    id: str
    title: str
    description: str
    target: float
    current: float
    reward: str
    difficulty: str


class FeedbackRequest(BaseModel):
    """Request de feedback de recomendaciones"""
    recommendation_feedback: Dict[str, str]  # title -> "helpful" | "not_helpful"
    general_feedback: Optional[str] = None


@router.get("/", response_model=RecommendationSetResponse)
async def get_user_recommendations(
    force_refresh: bool = Query(False, description="Forzar actualización de recomendaciones"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener recomendaciones personalizadas para el usuario actual"""
    try:
        recommendation_set = await recommendation_service.get_user_recommendations(
            db, str(current_user.id), force_refresh
        )
        
        return RecommendationSetResponse(
            user_id=recommendation_set.user_id,
            recommendations=[
                RecommendationResponse(
                    type=rec.type.value,
                    title=rec.title,
                    description=rec.description,
                    confidence=rec.confidence,
                    priority=rec.priority,
                    data=rec.data
                )
                for rec in recommendation_set.recommendations
            ],
            generated_at=recommendation_set.generated_at,
            total_recommendations=len(recommendation_set.recommendations)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendations: {str(e)}"
        )


@router.get("/strategy", response_model=List[RecommendationResponse])
async def get_strategy_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener recomendaciones específicas de estrategia"""
    try:
        recommendations = await recommendation_service.get_strategy_recommendations(
            db, str(current_user.id)
        )
        
        return [
            RecommendationResponse(
                type=rec.type.value,
                title=rec.title,
                description=rec.description,
                confidence=rec.confidence,
                priority=rec.priority,
                data=rec.data
            )
            for rec in recommendations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting strategy recommendations: {str(e)}"
        )


@router.get("/opponents", response_model=List[RecommendationResponse])
async def get_opponent_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener recomendaciones de oponentes"""
    try:
        recommendations = await recommendation_service.get_opponent_recommendations(
            db, str(current_user.id)
        )
        
        return [
            RecommendationResponse(
                type=rec.type.value,
                title=rec.title,
                description=rec.description,
                confidence=rec.confidence,
                priority=rec.priority,
                data=rec.data
            )
            for rec in recommendations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting opponent recommendations: {str(e)}"
        )


@router.get("/training", response_model=List[RecommendationResponse])
async def get_training_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener recomendaciones de entrenamiento"""
    try:
        recommendations = await recommendation_service.get_training_recommendations(
            db, str(current_user.id)
        )
        
        return [
            RecommendationResponse(
                type=rec.type.value,
                title=rec.title,
                description=rec.description,
                confidence=rec.confidence,
                priority=rec.priority,
                data=rec.data
            )
            for rec in recommendations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting training recommendations: {str(e)}"
        )


@router.get("/game/{game_id}/analysis", response_model=GameAnalysisResponse)
async def analyze_game_performance(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analizar el rendimiento del usuario en un juego específico"""
    try:
        analysis = await recommendation_service.analyze_game_performance(
            db, game_id, str(current_user.id)
        )
        
        if "error" in analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=analysis["error"]
            )
        
        return GameAnalysisResponse(**analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing game performance: {str(e)}"
        )


@router.get("/improvement", response_model=ImprovementSuggestionsResponse)
async def get_improvement_suggestions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener sugerencias específicas de mejora"""
    try:
        suggestions = await recommendation_service.get_improvement_suggestions(
            db, str(current_user.id)
        )
        
        if "error" in suggestions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=suggestions["error"]
            )
        
        return ImprovementSuggestionsResponse(**suggestions)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting improvement suggestions: {str(e)}"
        )


@router.get("/challenges", response_model=List[ChallengeResponse])
async def get_personalized_challenges(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener desafíos personalizados para el usuario"""
    try:
        challenges = await recommendation_service.get_personalized_challenges(
            db, str(current_user.id)
        )
        
        return [ChallengeResponse(**challenge) for challenge in challenges]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting personalized challenges: {str(e)}"
        )


@router.post("/feedback", response_model=RecommendationSetResponse)
async def submit_recommendation_feedback(
    feedback: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enviar feedback sobre recomendaciones para mejorar futuras sugerencias"""
    try:
        feedback_data = {
            **feedback.recommendation_feedback,
            "general": feedback.general_feedback
        }
        
        updated_recommendations = await recommendation_service.update_recommendations_with_feedback(
            db, str(current_user.id), feedback_data
        )
        
        return RecommendationSetResponse(
            user_id=updated_recommendations.user_id,
            recommendations=[
                RecommendationResponse(
                    type=rec.type.value,
                    title=rec.title,
                    description=rec.description,
                    confidence=rec.confidence,
                    priority=rec.priority,
                    data=rec.data
                )
                for rec in updated_recommendations.recommendations
            ],
            generated_at=updated_recommendations.generated_at,
            total_recommendations=len(updated_recommendations.recommendations)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing feedback: {str(e)}"
        )


@router.get("/pattern", response_model=PlayerPatternResponse)
async def get_player_pattern(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener patrón de juego del usuario actual"""
    try:
        # Asegurar que el análisis esté actualizado
        await recommendation_service.get_user_recommendations(db, str(current_user.id))
        
        pattern = recommendation_service.pattern_analyzer.get_player_pattern(str(current_user.id))
        
        if not pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pattern data available. Play some games first."
            )
        
        return PlayerPatternResponse(
            user_id=pattern.user_id,
            play_style=pattern.play_style.value,
            preferred_colors=[color.value for color in pattern.preferred_colors],
            avg_game_duration=pattern.avg_game_duration,
            win_rate=pattern.win_rate,
            favorite_strategies=pattern.favorite_strategies,
            risk_tolerance=pattern.risk_tolerance,
            adaptability=pattern.adaptability,
            consistency=pattern.consistency
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting player pattern: {str(e)}"
        )


@router.get("/stats")
async def get_recommendation_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener estadísticas del sistema de recomendaciones"""
    try:
        # Obtener recomendaciones actuales
        recommendation_set = await recommendation_service.get_user_recommendations(
            db, str(current_user.id)
        )
        
        # Calcular estadísticas
        total_recommendations = len(recommendation_set.recommendations)
        by_type = {}
        by_priority = {}
        avg_confidence = 0
        
        for rec in recommendation_set.recommendations:
            # Por tipo
            rec_type = rec.type.value
            by_type[rec_type] = by_type.get(rec_type, 0) + 1
            
            # Por prioridad
            priority = f"priority_{rec.priority}"
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # Confianza promedio
            avg_confidence += rec.confidence
        
        if total_recommendations > 0:
            avg_confidence /= total_recommendations
        
        return {
            "total_recommendations": total_recommendations,
            "by_type": by_type,
            "by_priority": by_priority,
            "average_confidence": round(avg_confidence, 2),
            "generated_at": recommendation_set.generated_at,
            "user_id": str(current_user.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendation stats: {str(e)}"
        )