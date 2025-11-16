"""
Esquemas Pydantic para autenticación
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens and underscores')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if len(v) > 100:
            raise ValueError('Password must be less than 100 characters')
        return v
    
    @validator('display_name')
    def validate_display_name(cls, v):
        if v and len(v) > 100:
            raise ValueError('Display name must be less than 100 characters')
        return v


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: 'UserResponse'


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None


class RefreshToken(BaseModel):
    refresh_token: str


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if len(v) > 100:
            raise ValueError('Password must be less than 100 characters')
        return v


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if len(v) > 100:
            raise ValueError('Password must be less than 100 characters')
        return v


class EmailVerification(BaseModel):
    token: str


class ResendVerification(BaseModel):
    email: EmailStr


# Importar UserResponse para evitar circular imports
from app.schemas.user import UserResponse
Token.model_rebuild()