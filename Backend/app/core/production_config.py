"""
Configuración específica para producción en Render
"""
import os
from typing import List

def get_cors_origins() -> List[str]:
    """
    Obtiene los orígenes CORS de manera robusta para producción
    """
    cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "*")
    
    if cors_origins == "*":
        return ["*"]
    
    if cors_origins.startswith("[") and cors_origins.endswith("]"):
        try:
            import json
            return json.loads(cors_origins)
        except json.JSONDecodeError:
            pass
    
    # Split por comas
    origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
    return origins if origins else ["*"]

def get_database_url() -> str:
    """
    Obtiene la URL de la base de datos
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is required")
    return db_url

def get_secret_key() -> str:
    """
    Obtiene la clave secreta
    """
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("SECRET_KEY environment variable is required")
    return secret_key

# Configuración para producción
PRODUCTION_CONFIG = {
    "SECRET_KEY": get_secret_key,
    "DATABASE_URL": get_database_url,
    "BACKEND_CORS_ORIGINS": get_cors_origins,
    "ENVIRONMENT": lambda: os.getenv("ENVIRONMENT", "production"),
    "DEBUG": lambda: os.getenv("DEBUG", "false").lower() == "true",
}