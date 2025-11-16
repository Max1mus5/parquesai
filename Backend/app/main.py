"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import socketio
import time
import logging
import asyncio
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.game import router as game_router
from app.api.v1.websocket import router as websocket_router
from app.api.v1.ai import router as ai_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.distributed import router as distributed_router
from app.sockets.socket_manager import socket_manager
from app.ai.ai_service import ai_service

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API para el juego Parqués Distribuido con IA",
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Crear aplicación Socket.io
socket_app = socketio.ASGIApp(socket_manager.sio, app)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de hosts confiables
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # En producción, especificar hosts exactos
)


# Middleware personalizado para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log de request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log de response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Rutas de salud
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Parqués Distribuido API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


# Incluir routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(game_router, prefix=f"{settings.API_V1_STR}/game", tags=["game"])
app.include_router(websocket_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(recommendations_router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["recommendations"])
app.include_router(distributed_router, prefix=f"{settings.API_V1_STR}/sync", tags=["distributed-sync"])


# Eventos de startup y shutdown
@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    logger.info("Starting Parqués Distribuido API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Iniciar task de manejo de bots en segundo plano
    asyncio.create_task(bot_background_task())


@app.on_event("shutdown")
async def shutdown_event():
    """Eventos al cerrar la aplicación"""
    logger.info("Shutting down Parqués Distribuido API...")


async def bot_background_task():
    """Task en segundo plano para manejar turnos de bots"""
    from app.db.database import get_db
    
    while True:
        try:
            async for db in get_db():
                await ai_service.handle_bot_turns_in_background(db)
                break  # Solo necesitamos una sesión
        except Exception as e:
            logger.error(f"Error in bot background task: {e}")
        
        # Esperar 2 segundos antes de la siguiente verificación
        await asyncio.sleep(2)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:socket_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )