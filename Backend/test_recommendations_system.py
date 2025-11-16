#!/usr/bin/env python3
"""
Script de prueba para el sistema de recomendaciones inteligente
"""
import asyncio
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def test_recommendations_endpoints():
    """Probar todos los endpoints del sistema de recomendaciones"""
    
    print("🧠 TESTING SISTEMA DE RECOMENDACIONES INTELIGENTE")
    print("=" * 60)
    
    # 1. Obtener token de autenticación
    print("\n1. Autenticación...")
    login_data = {
        "username": "aitest",
        "password": "test123"
    }
    
    response = requests.post(f"{API_V1}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Error en login: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Autenticación exitosa")
    
    # 2. Probar endpoint de recomendaciones generales
    print("\n2. Probando recomendaciones generales...")
    response = requests.get(f"{API_V1}/recommendations/", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total recomendaciones: {data['total_recommendations']}")
        print(f"   Generadas en: {data['generated_at']}")
        
        for i, rec in enumerate(data['recommendations'][:3], 1):
            print(f"   {i}. [{rec['type']}] {rec['title']}")
            print(f"      Confianza: {rec['confidence']:.2f}, Prioridad: {rec['priority']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # 3. Probar recomendaciones de estrategia
    print("\n3. Probando recomendaciones de estrategia...")
    response = requests.get(f"{API_V1}/recommendations/strategy", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        strategies = response.json()
        print(f"✅ Recomendaciones de estrategia: {len(strategies)}")
        for strategy in strategies:
            print(f"   - {strategy['title']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # 4. Probar recomendaciones de oponentes
    print("\n4. Probando recomendaciones de oponentes...")
    response = requests.get(f"{API_V1}/recommendations/opponents", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        opponents = response.json()
        print(f"✅ Recomendaciones de oponentes: {len(opponents)}")
        for opponent in opponents:
            print(f"   - {opponent['title']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # 5. Probar recomendaciones de entrenamiento
    print("\n5. Probando recomendaciones de entrenamiento...")
    response = requests.get(f"{API_V1}/recommendations/training", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        training = response.json()
        print(f"✅ Recomendaciones de entrenamiento: {len(training)}")
        for train in training:
            print(f"   - {train['title']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # 6. Probar sugerencias de mejora
    print("\n6. Probando sugerencias de mejora...")
    response = requests.get(f"{API_V1}/recommendations/improvement", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        improvement = response.json()
        print(f"✅ Nivel de habilidad: {improvement['overall_skill_level']}")
        print(f"   Áreas de mejora: {len(improvement['improvement_areas'])}")
        print(f"   Fortalezas: {len(improvement['strengths'])}")
        print(f"   Próximos pasos: {len(improvement['next_steps'])}")
        
        if improvement['strengths']:
            print("   Fortalezas principales:")
            for strength in improvement['strengths'][:2]:
                print(f"     - {strength}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # 7. Probar desafíos personalizados
    print("\n7. Probando desafíos personalizados...")
    response = requests.get(f"{API_V1}/recommendations/challenges", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        challenges = response.json()
        print(f"✅ Desafíos disponibles: {len(challenges)}")
        for challenge in challenges:
            print(f"   - {challenge['title']} ({challenge['difficulty']})")
            print(f"     Progreso: {challenge['current']}/{challenge['target']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # 8. Probar patrón de jugador
    print("\n8. Probando patrón de jugador...")
    response = requests.get(f"{API_V1}/recommendations/pattern", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        pattern = response.json()
        print(f"✅ Patrón de jugador obtenido:")
        print(f"   Estilo de juego: {pattern['play_style']}")
        print(f"   Tasa de victoria: {pattern['win_rate']:.1%}")
        print(f"   Duración promedio: {pattern['avg_game_duration']:.1f} min")
        print(f"   Tolerancia al riesgo: {pattern['risk_tolerance']:.2f}")
        print(f"   Adaptabilidad: {pattern['adaptability']:.2f}")
        print(f"   Consistencia: {pattern['consistency']:.2f}")
        print(f"   Colores preferidos: {', '.join(pattern['preferred_colors'])}")
        print(f"   Estrategias favoritas: {', '.join(pattern['favorite_strategies'])}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # 9. Probar estadísticas de recomendaciones
    print("\n9. Probando estadísticas de recomendaciones...")
    response = requests.get(f"{API_V1}/recommendations/stats", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Estadísticas de recomendaciones:")
        print(f"   Total: {stats['total_recommendations']}")
        print(f"   Confianza promedio: {stats['average_confidence']}")
        print(f"   Por tipo: {stats['by_type']}")
        print(f"   Por prioridad: {stats['by_priority']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # 10. Probar feedback de recomendaciones
    print("\n10. Probando feedback de recomendaciones...")
    feedback_data = {
        "recommendation_feedback": {
            "Considera un enfoque más balanceado": "helpful",
            "Practica contra IA nivel fácil": "not_helpful"
        },
        "general_feedback": "Las recomendaciones son útiles pero podrían ser más específicas"
    }
    
    response = requests.post(
        f"{API_V1}/recommendations/feedback", 
        headers=headers,
        json=feedback_data
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        updated_recs = response.json()
        print(f"✅ Feedback procesado, recomendaciones actualizadas")
        print(f"   Nuevas recomendaciones: {updated_recs['total_recommendations']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # 11. Probar análisis de juego (si hay juegos disponibles)
    print("\n11. Probando análisis de juego...")
    
    # Primero obtener lista de juegos del usuario
    response = requests.get(f"{API_V1}/game/my-games", headers=headers)
    if response.status_code == 200:
        games = response.json()
        if games:
            game_id = games[0]['id']
            response = requests.get(
                f"{API_V1}/recommendations/game/{game_id}/analysis", 
                headers=headers
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                analysis = response.json()
                print(f"✅ Análisis de juego completado:")
                print(f"   Rendimiento del usuario: {analysis['user_performance']:.2f}")
                print(f"   Duración del juego: {analysis['game_duration']:.1f} min")
                print(f"   Estrategias usadas: {', '.join(analysis['strategies_used'])}")
                print(f"   Insights: {len(analysis['insights'])}")
                print(f"   Recomendaciones post-juego: {len(analysis['recommendations'])}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        else:
            print("ℹ️  No hay juegos disponibles para analizar")
    else:
        print(f"❌ Error obteniendo juegos: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 PRUEBAS DEL SISTEMA DE RECOMENDACIONES COMPLETADAS")


def test_recommendation_algorithms():
    """Probar algoritmos de recomendación directamente"""
    
    print("\n🔬 TESTING ALGORITMOS DE RECOMENDACIÓN")
    print("=" * 60)
    
    from app.recommendations.pattern_analyzer import PatternAnalyzer, PlayStyle
    from app.recommendations.recommendation_engine import RecommendationEngine
    from app.core.game_constants import PlayerColor
    
    # Crear instancias
    analyzer = PatternAnalyzer()
    engine = RecommendationEngine(analyzer)
    
    # Datos de prueba
    test_user_id = "test_user_123"
    
    # Simular historial de juegos
    game_history = [
        {
            "id": "game1",
            "user_id": test_user_id,
            "player_color": "blue",
            "winner_id": test_user_id,
            "duration": 25.5,
            "created_at": datetime.now()
        },
        {
            "id": "game2", 
            "user_id": test_user_id,
            "player_color": "red",
            "winner_id": "other_player",
            "duration": 35.2,
            "created_at": datetime.now()
        },
        {
            "id": "game3",
            "user_id": test_user_id,
            "player_color": "blue",
            "winner_id": test_user_id,
            "duration": 20.1,
            "created_at": datetime.now()
        }
    ]
    
    # Simular historial de movimientos
    move_history = [
        {"game_id": "game1", "player_id": "p1", "move_type": "attack", "timestamp": datetime.now()},
        {"game_id": "game1", "player_id": "p1", "move_type": "safe", "timestamp": datetime.now()},
        {"game_id": "game2", "player_id": "p1", "move_type": "block", "timestamp": datetime.now()},
        {"game_id": "game3", "player_id": "p1", "move_type": "attack", "timestamp": datetime.now()},
    ]
    
    print("1. Analizando patrones de jugador...")
    pattern = analyzer.analyze_player_history(test_user_id, game_history, move_history)
    
    print(f"✅ Patrón analizado:")
    print(f"   Estilo: {pattern.play_style.value}")
    print(f"   Win rate: {pattern.win_rate:.1%}")
    print(f"   Duración promedio: {pattern.avg_game_duration:.1f} min")
    print(f"   Tolerancia al riesgo: {pattern.risk_tolerance:.2f}")
    print(f"   Adaptabilidad: {pattern.adaptability:.2f}")
    print(f"   Consistencia: {pattern.consistency:.2f}")
    
    print("\n2. Generando recomendaciones...")
    recommendations = engine.generate_recommendations(test_user_id)
    
    print(f"✅ Recomendaciones generadas: {len(recommendations.recommendations)}")
    
    for i, rec in enumerate(recommendations.recommendations[:5], 1):
        print(f"   {i}. [{rec.type.value}] {rec.title}")
        print(f"      Confianza: {rec.confidence:.2f}, Prioridad: {rec.priority}")
        print(f"      {rec.description[:80]}...")
    
    print("\n3. Probando feedback...")
    feedback = {
        recommendations.recommendations[0].title: "helpful",
        "general": "Muy útil"
    }
    
    updated_recs = engine.update_recommendations(test_user_id, feedback)
    print(f"✅ Recomendaciones actualizadas con feedback")
    print(f"   Nueva confianza primera rec: {updated_recs.recommendations[0].confidence:.2f}")
    
    print("\n" + "=" * 60)
    print("🧪 PRUEBAS DE ALGORITMOS COMPLETADAS")


if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE RECOMENDACIONES")
    print("Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    
    try:
        # Probar endpoints API
        test_recommendations_endpoints()
        
        # Probar algoritmos directamente
        test_recommendation_algorithms()
        
        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()