"""
Modelos de base de datos para usuarios
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    preferred_color = Column(String(20), nullable=True)
    
    # Relaciones
    game_players = relationship("GamePlayer", back_populates="user")
    game_moves = relationship("GameMove", back_populates="player")
    statistics = relationship("GameStatistics", back_populates="user", uselist=False)


class GameStatistics(Base):
    __tablename__ = "game_statistics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    total_games = Column(Integer, default=0, nullable=False)
    games_won = Column(Integer, default=0, nullable=False)
    games_lost = Column(Integer, default=0, nullable=False)
    games_abandoned = Column(Integer, default=0, nullable=False)
    total_moves = Column(Integer, default=0, nullable=False)
    total_captures = Column(Integer, default=0, nullable=False)
    total_captured = Column(Integer, default=0, nullable=False)
    average_game_duration_seconds = Column(Integer, default=0, nullable=False)
    favorite_color = Column(String(20), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relación
    user = relationship("User", back_populates="statistics")
    
    @property
    def win_rate(self) -> float:
        """Calcular tasa de victorias"""
        if self.total_games == 0:
            return 0.0
        return self.games_won / self.total_games