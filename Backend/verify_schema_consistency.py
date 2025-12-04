"""
Script para verificar la consistencia entre los modelos SQLAlchemy y la base de datos
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, inspect
from app.core.config import settings
from app.db.database import Base
from app.db.models import user, game, ai

async def verify_schema_consistency():
    """Verificar que los modelos coincidan con la base de datos"""
    print("=" * 70)
    print("🔍 VERIFICACIÓN DE CONSISTENCIA DEL ESQUEMA")
    print("=" * 70)
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    
    try:
        async with engine.connect() as conn:
            # Obtener metadatos de los modelos
            print("\n📋 Modelos SQLAlchemy definidos:")
            model_tables = {}
            for table_name, table in Base.metadata.tables.items():
                columns = {col.name: str(col.type) for col in table.columns}
                model_tables[table_name] = columns
                print(f"  ✓ {table_name} ({len(columns)} columnas)")
            
            # Obtener esquema de la base de datos
            print("\n📊 Tablas en la base de datos:")
            db_tables = {}
            result = await conn.execute(text(
                """
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
                """
            ))
            
            for table_name, column_name, data_type, is_nullable in result:
                if table_name not in db_tables:
                    db_tables[table_name] = {}
                db_tables[table_name][column_name] = {
                    'type': data_type,
                    'nullable': is_nullable == 'YES'
                }
            
            for table_name in db_tables:
                if table_name != 'alembic_version':
                    print(f"  ✓ {table_name} ({len(db_tables[table_name])} columnas)")
            
            # Comparar modelos vs base de datos
            print("\n🔄 Comparación de esquemas:")
            
            issues_found = False
            
            # Verificar tablas que están en modelos pero no en BD
            for table_name in model_tables:
                if table_name not in db_tables:
                    print(f"  ❌ Tabla '{table_name}' está en modelos pero NO en BD")
                    issues_found = True
            
            # Verificar tablas que están en BD pero no en modelos
            for table_name in db_tables:
                if table_name != 'alembic_version' and table_name not in model_tables:
                    print(f"  ⚠️  Tabla '{table_name}' está en BD pero NO en modelos")
            
            # Verificar columnas en cada tabla
            for table_name in model_tables:
                if table_name in db_tables:
                    model_cols = set(model_tables[table_name].keys())
                    db_cols = set(db_tables[table_name].keys())
                    
                    # Columnas faltantes en BD
                    missing_in_db = model_cols - db_cols
                    if missing_in_db:
                        print(f"  ❌ Tabla '{table_name}' - columnas faltantes en BD:")
                        for col in missing_in_db:
                            print(f"      - {col}")
                        issues_found = True
                    
                    # Columnas extra en BD
                    extra_in_db = db_cols - model_cols
                    if extra_in_db:
                        print(f"  ⚠️  Tabla '{table_name}' - columnas extra en BD:")
                        for col in extra_in_db:
                            print(f"      - {col}")
            
            if not issues_found:
                print("  ✅ Todos los modelos están sincronizados con la base de datos")
            
            # Verificar estado de migraciones
            print("\n🔄 Estado de migraciones:")
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.scalar()
            print(f"  📌 Versión actual: {current_version}")
            
            # Verificar si hay migraciones pendientes
            import os
            versions_dir = "alembic/versions"
            if os.path.exists(versions_dir):
                migration_files = [f for f in os.listdir(versions_dir) if f.endswith('.py') and f != '__pycache__']
                print(f"  📁 Archivos de migración disponibles: {len(migration_files)}")
                for mig_file in sorted(migration_files):
                    revision = mig_file.split('_')[0]
                    is_current = '✅' if revision == current_version else '  '
                    print(f"    {is_current} {mig_file[:60]}")
            
            # Resumen final
            print("\n" + "=" * 70)
            if issues_found:
                print("⚠️  SE ENCONTRARON INCONSISTENCIAS")
                print("💡 Solución:")
                print("   1. Crear nueva migración: alembic revision --autogenerate -m 'Fix schema'")
                print("   2. Aplicar migración: alembic upgrade head")
            else:
                print("✅ EL ESQUEMA ESTÁ CONSISTENTE Y ACTUALIZADO")
            print("=" * 70)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_schema_consistency())
