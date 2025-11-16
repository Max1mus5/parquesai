"""
Modelos de base de datos para juegos
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base


class Game(Base):
    __tablename__ = "games"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), default="waiting", nullable=False, index=True)
    max_players = Column(Integer, default=4, nullable=False)
    is_private = Column(Boolean, default=False, nullable=False)
    password_hash = Column(String(255), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    winner_id = Column(UUID(as_uuid=True), nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relaciones
    players = relationship("GamePlayer", back_populates="game")
    moves = relationship("GameMove", back_populates="game")
    creator = relationship("User", foreign_keys=[created_by])


class GamePlayer(Base):
    __tablename__ = "game_players"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    color = Column(String(20), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    game = relationship("Game", back_populates="players")
    user = relationship("User", back_populates="game_players")


class GameMove(Base):
    __tablename__ = "game_moves"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    player_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    piece_id = Column(String(50), nullable=False)
    from_position = Column(Integer, nullable=False)
    to_position = Column(Integer, nullable=False)
    dice_value = Column(Integer, nullable=False)
    move_type = Column(String(20), nullable=False)
    captured_piece_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    game = relationship("Game", back_populates="moves")
    player = relationship("User", back_populates="game_moves")