"""
Script para probar la restauración de juegos desde la base de datos
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models.game import Game
from app.services.game_service import game_service

async def test_game_restore():
    """Probar la restauración de juegos desde la base de datos"""
    print("=" * 60)
    print("🎮 TEST DE RESTAURACIÓN DE JUEGOS DESDE BASE DE DATOS")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        # Obtener juegos activos o en espera de la base de datos
        result = await db.execute(
            select(Game)
            .where(Game.status.in_(['waiting', 'active']))
            .limit(5)
        )
        games = result.scalars().all()
        
        if not games:
            print("\n⚠️  No hay juegos activos o en espera en la base de datos")
            print("💡 Crea un juego primero desde el frontend")
            return
        
        print(f"\n📊 Encontrados {len(games)} juegos en la base de datos:")
        
        for game in games:
            print(f"\n  🎲 Juego: {game.name}")
            print(f"     ID: {game.id}")
            print(f"     Estado: {game.status}")
            print(f"     Creado: {game.created_at}")
            
            # Verificar si está en memoria
            in_memory = str(game.id) in game_service.active_games
            print(f"     En memoria: {'✅ Sí' if in_memory else '❌ No'}")
            
            if not in_memory:
                print(f"     🔄 Intentando restaurar desde BD...")
                try:
                    restored_game = await game_service._restore_game_from_db(
                        db, 
                        str(game.id)
                    )
                    
                    if restored_game:
                        print(f"     ✅ Juego restaurado exitosamente!")
                        print(f"        - Jugadores: {len(restored_game.players)}")
                        print(f"        - Estado: {restored_game.status}")
                    else:
                        print(f"     ❌ No se pudo restaurar el juego")
                except Exception as e:
                    print(f"     ❌ Error al restaurar: {e}")
        
        print("\n" + "=" * 60)
        print(f"📈 Total de juegos en memoria ahora: {len(game_service.active_games)}")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_game_restore())
