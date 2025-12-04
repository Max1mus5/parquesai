"""
Script para probar la conexión a la base de datos y verificar las tablas
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, inspect
from app.core.config import settings

async def test_database_connection():
    """Probar la conexión a la base de datos"""
    print("🔍 Probando conexión a la base de datos...")
    print(f"📊 URL: {settings.DATABASE_URL[:50]}...")
    
    try:
        # Crear engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=True,
            pool_pre_ping=True,
        )
        
        # Probar conexión
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa!")
            
            # Verificar versión de PostgreSQL
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📦 PostgreSQL version: {version[:50]}...")
            
            # Listar tablas existentes
            print("\n📋 Tablas en la base de datos:")
            result = await conn.execute(text(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
            ))
            tables = result.fetchall()
            
            if not tables:
                print("⚠️  No hay tablas en la base de datos!")
                print("💡 Necesitas ejecutar las migraciones de Alembic")
                return False
            
            for (table,) in tables:
                print(f"  ✓ {table}")
                
                # Contar registros en cada tabla
                try:
                    count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.scalar()
                    print(f"    └─ {count} registros")
                except Exception as e:
                    print(f"    └─ Error al contar: {e}")
            
            # Verificar tablas necesarias
            table_names = [t[0] for t in tables]
            required_tables = ['users', 'games', 'game_players', 'game_moves']
            
            print("\n🔍 Verificando tablas requeridas:")
            for table in required_tables:
                if table in table_names:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} - ¡FALTA!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    finally:
        await engine.dispose()

async def check_migration_status():
    """Verificar el estado de las migraciones de Alembic"""
    print("\n🔄 Verificando estado de migraciones...")
    
    try:
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )
        
        async with engine.connect() as conn:
            # Verificar tabla de versiones de Alembic
            result = await conn.execute(text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                )
                """
            ))
            has_alembic_table = result.scalar()
            
            if not has_alembic_table:
                print("⚠️  Tabla alembic_version no existe")
                print("💡 Ejecuta: cd Backend && alembic upgrade head")
                return
            
            # Obtener versión actual
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            
            if version:
                print(f"✅ Migración actual: {version}")
            else:
                print("⚠️  No hay migraciones aplicadas")
                print("💡 Ejecuta: cd Backend && alembic upgrade head")
                
    except Exception as e:
        print(f"❌ Error al verificar migraciones: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 PARQUÉS DISTRIBUIDO - TEST DE BASE DE DATOS")
    print("=" * 60)
    asyncio.run(test_database_connection())
    asyncio.run(check_migration_status())
    print("\n" + "=" * 60)
