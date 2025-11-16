"""
Modelos de base de datos para IA y recomendaciones
"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base


class AIBotDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class RecommendationType(str, Enum):
    OPTIMAL = "optimal"
    DEFENSIVE = "defensive"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"


class AIBot(Base):
    __tablename__ = "ai_bots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    difficulty = Column(String(20), nullable=False, index=True)
    algorithm = Column(String(50), nullable=False)  # minimax, mcts, hybrid
    parameters = Column(JSON, nullable=False)  # depth, iterations, etc.
    win_rate = Column(Float, default=0.0, nullable=False)
    games_played = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    training_data = relationship("AITrainingData", back_populates="bot")


class AITrainingData(Base):
    __tablename__ = "ai_training_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    bot_id = Column(UUID(as_uuid=True), ForeignKey("ai_bots.id"), nullable=False, index=True)
    game_state = Column(JSON, nullable=False)
    move_made = Column(JSON, nullable=False)
    move_evaluation = Column(Float, nullable=False)
    game_outcome = Column(String(20), nullable=False)  # win, loss, draw
    learning_weight = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    # game = relationship("Game", back_populates="ai_training_data")  # TODO: Implementar cuando esté listo
    bot = relationship("AIBot", back_populates="training_data")


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    player_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    turn_number = Column(Integer, nullable=False, index=True)
    game_state = Column(JSON, nullable=False)
    recommended_moves = Column(JSON, nullable=False)  # Lista de movimientos recomendados
    recommendation_type = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    player_followed = Column(Boolean, nullable=True)  # null si aún no se decide
    actual_move = Column(JSON, nullable=True)
    processing_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    # game = relationship("Game", back_populates="recommendation_logs")  # TODO: Implementar cuando esté listo
    # player = relationship("User", back_populates="recommendation_logs")  # TODO: Implementar cuando esté listo


class GameAnalysis(Base):
    __tablename__ = "game_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, unique=True, index=True)
    total_turns = Column(Integer, nullable=False)
    game_duration_seconds = Column(Integer, nullable=False)
    winner_analysis = Column(JSON, nullable=False)
    player_performances = Column(JSON, nullable=False)
    critical_moments = Column(JSON, nullable=False)
    move_quality_scores = Column(JSON, nullable=False)
    recommendation_accuracy = Column(Float, nullable=True)
    ai_insights = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DistributedSyncLog(Base):
    __tablename__ = "distributed_sync_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    sync_type = Column(String(50), nullable=False)  # berkeley, ntp, manual
    client_timestamps = Column(JSON, nullable=False)
    server_timestamp = Column(DateTime, nullable=False)
    calculated_offset = Column(Integer, nullable=False)  # milliseconds
    sync_accuracy_ms = Column(Integer, nullable=False)
    participants = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)