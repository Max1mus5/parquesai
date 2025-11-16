"""
Servicio de autenticación
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.db.models.user import User, GameStatistics
from app.schemas.auth import UserRegister, UserLogin
from app.schemas.user import UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from app.db.database import get_db


class AuthService:
    
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserRegister) -> UserResponse:
        """Registrar un nuevo usuario"""
        
        # Verificar si el email ya existe
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Verificar si el username ya existe
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Crear el usuario
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            id=uuid.uuid4(),
            username=user_data.username,
            email=user_data.email,
            display_name=user_data.display_name or user_data.username,
            password_hash=hashed_password,
            is_active=True,
            is_verified=False,  # En producción, requerirá verificación por email
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        await db.flush()
        
        # Crear estadísticas iniciales del usuario
        user_stats = GameStatistics(
            id=uuid.uuid4(),
            user_id=db_user.id,
            total_games=0,
            games_won=0,
            games_lost=0,
            games_abandoned=0,
            total_moves=0,
            total_captures=0,
            total_captured=0,
            average_game_duration_seconds=0,
            favorite_color="red",
            updated_at=datetime.utcnow()
        )
        
        db.add(user_stats)
        await db.commit()
        await db.refresh(db_user)
        
        return UserResponse.from_orm(db_user)
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, credentials: UserLogin) -> Optional[User]:
        """Autenticar usuario con email y contraseña"""
        
        result = await db.execute(select(User).where(User.email == credentials.email))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(credentials.password, user.password_hash):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user
    
    @staticmethod
    async def login_user(db: AsyncSession, credentials: UserLogin) -> dict:
        """Login de usuario y generación de tokens"""
        
        user = await AuthService.authenticate_user(db, credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear tokens
        access_token_expires = timedelta(minutes=30)  # 30 minutos
        refresh_token_expires = timedelta(days=7)     # 7 días
        
        access_token = create_access_token(
            subject=str(user.id),
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            subject=str(user.id),
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "user": UserResponse.from_orm(user)
        }
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Obtener usuario por ID"""
        
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user_profile(db: AsyncSession, user_id: uuid.UUID, update_data: dict) -> UserResponse:
        """Actualizar perfil de usuario"""
        
        user = await AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Actualizar campos permitidos
        allowed_fields = ['display_name', 'bio', 'avatar_url', 'preferences']
        for field, value in update_data.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        
        return UserResponse.from_orm(user)
    
    @staticmethod
    async def change_password(db: AsyncSession, user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
        """Cambiar contraseña de usuario"""
        
        user = await AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verificar contraseña actual
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        # Actualizar contraseña
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        await db.commit()
        
        return True
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: uuid.UUID) -> bool:
        """Desactivar cuenta de usuario"""
        
        user = await AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        await db.commit()
        
        return True
    
    async def verify_token(self, token: str) -> Optional[User]:
        """Verificar token JWT y obtener usuario"""
        try:
            user_id = verify_token(token, "access")
            if not user_id:
                return None
            
            # Obtener sesión de base de datos
            async for db in get_db():
                user = await self.get_user_by_id(db, uuid.UUID(user_id))
                return user
        except Exception:
            return None