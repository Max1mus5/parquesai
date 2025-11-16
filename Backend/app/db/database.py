"""
Configuración de base de datos con SQLAlchemy async
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Crear engine asíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    poolclass=NullPool if settings.DEBUG else None,
    pool_pre_ping=True,
)

# Crear session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base para modelos
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency para obtener sesión de base de datos"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Inicializar base de datos - crear todas las tablas"""
    async with engine.begin() as conn:
        # Importar todos los modelos para que sean registrados
        from app.db.models import user, game, ai  # noqa
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Cerrar conexiones de base de datos"""
    await engine.dispose()