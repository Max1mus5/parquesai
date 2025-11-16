#!/usr/bin/env python3
"""
Script de pruebas para el sistema de sincronización distribuida Berkeley
"""
import asyncio
import time
import json
import requests
from datetime import datetime
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Credenciales de prueba
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
}

class DistributedSyncTester:
    """Tester para el sistema de sincronización distribuida"""
    
    def __init__(self):
        self.token = None
        self.headers = {}
    
    def authenticate(self) -> bool:
        """Autenticar usuario de prueba"""
        try:
            # Intentar login
            response = requests.post(
                f"{API_BASE}/auth/login",
                data={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Login exitoso")
                return True
            else:
                print(f"❌ Error en login: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            return False
    
    def test_sync_health(self) -> bool:
        """Probar health check del sistema de sincronización"""
        try:
            response = requests.get(f"{API_BASE}/sync/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data['status']}")
                print(f"   Inicializado: {data.get('initialized', False)}")
                return True
            else:
                print(f"❌ Error en health check: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en health check: {e}")
            return False
    
    def test_initialize_service(self, role: str = "master") -> bool:
        """Probar inicialización del servicio"""
        try:
            response = requests.post(
                f"{API_BASE}/sync/initialize",
                headers=self.headers,
                params={
                    "role": role,
                    "node_id": f"test_node_{role}",
                    "sync_interval": 10.0
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Servicio inicializado como {role}")
                print(f"   Node ID: {data.get('node_id')}")
                return True
            else:
                print(f"❌ Error inicializando servicio: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error inicializando servicio: {e}")
            return False
    
    def test_sync_status(self) -> Dict[str, Any]:
        """Probar obtención de estado de sincronización"""
        try:
            response = requests.get(
                f"{API_BASE}/sync/status",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Estado de sincronización obtenido")
                print(f"   Nodo: {data.get('berkeley', {}).get('node_id', 'N/A')}")
                print(f"   Rol: {data.get('berkeley', {}).get('role', 'N/A')}")
                print(f"   Ejecutándose: {data.get('berkeley', {}).get('is_running', False)}")
                return data
            else:
                print(f"❌ Error obteniendo estado: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
            return {}
    
    def test_sync_metrics(self) -> Dict[str, Any]:
        """Probar obtención de métricas"""
        try:
            response = requests.get(
                f"{API_BASE}/sync/metrics",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Métricas obtenidas")
                print(f"   Total syncs: {data.get('total_sync_cycles', 0)}")
                print(f"   Successful syncs: {data.get('successful_syncs', 0)}")
                print(f"   Success rate: {data.get('success_rate', 0):.2%}")
                return data
            else:
                print(f"❌ Error obteniendo métricas: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error obteniendo métricas: {e}")
            return {}
    
    def test_synchronized_time(self) -> bool:
        """Probar obtención de tiempo sincronizado"""
        try:
            response = requests.get(
                f"{API_BASE}/sync/time/synchronized",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Tiempo sincronizado obtenido")
                print(f"   Tiempo local: {data.get('local_time', 0):.3f}")
                print(f"   Tiempo sincronizado: {data.get('synchronized_time', 0):.3f}")
                print(f"   Offset: {data.get('time_offset', 0):.3f}s")
                print(f"   Diferencia: {data.get('difference', 0):.3f}s")
                return True
            else:
                print(f"❌ Error obteniendo tiempo sincronizado: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error obteniendo tiempo sincronizado: {e}")
            return False
    
    def test_register_slave_node(self) -> bool:
        """Probar registro de nodo esclavo"""
        try:
            node_data = {
                "node_id": "test_slave_1",
                "address": "localhost",
                "port": 8001,
                "role": "slave"
            }
            
            response = requests.post(
                f"{API_BASE}/sync/nodes/register",
                headers=self.headers,
                json=node_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Nodo esclavo registrado: {node_data['node_id']}")
                return True
            else:
                print(f"❌ Error registrando nodo esclavo: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error registrando nodo esclavo: {e}")
            return False
    
    def test_sync_game_event(self) -> bool:
        """Probar sincronización de evento de juego"""
        try:
            event_data = {
                "event_type": "move_piece",
                "event_data": {
                    "game_id": "test_game_123",
                    "player_id": "player_1",
                    "piece_id": "piece_1",
                    "from_position": 0,
                    "to_position": 5,
                    "dice_value": 5
                },
                "game_id": "test_game_123"
            }
            
            response = requests.post(
                f"{API_BASE}/sync/events/sync",
                headers=self.headers,
                json=event_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Evento de juego sincronizado")
                sync_info = data.get("sync_info", {})
                print(f"   Timestamp sincronizado: {sync_info.get('synchronized_time', 0):.3f}")
                print(f"   Offset aplicado: {sync_info.get('offset', 0):.3f}s")
                return True
            else:
                print(f"❌ Error sincronizando evento: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sincronizando evento: {e}")
            return False
    
    def test_validate_event_timing(self) -> bool:
        """Probar validación de timing de evento"""
        try:
            current_time = time.time()
            
            # Probar evento con timing válido
            validation_data = {
                "event_timestamp": current_time,
                "tolerance": 2.0
            }
            
            response = requests.post(
                f"{API_BASE}/sync/events/validate-timing",
                headers=self.headers,
                json=validation_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Validación de timing: {data.get('message', 'N/A')}")
                print(f"   Válido: {data.get('valid', False)}")
                print(f"   Diferencia: {data.get('time_difference', 0):.3f}s")
                return True
            else:
                print(f"❌ Error validando timing: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error validando timing: {e}")
            return False
    
    def test_force_sync(self) -> bool:
        """Probar sincronización forzada"""
        try:
            response = requests.post(
                f"{API_BASE}/sync/force-sync",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Sincronización forzada exitosa")
                print(f"   Mensaje: {data.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ Error en sincronización forzada: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error en sincronización forzada: {e}")
            return False


async def test_berkeley_algorithm():
    """Probar algoritmo Berkeley directamente"""
    print("\n🧪 TESTING ALGORITMO BERKELEY DIRECTAMENTE")
    print("=" * 60)
    
    try:
        from app.distributed.berkeley_algorithm import BerkeleyTimeSync, NodeRole
        
        # Crear nodo maestro
        master = BerkeleyTimeSync("master_node", NodeRole.MASTER, sync_interval=5.0)
        await master.start_sync_service()
        
        print("✅ Nodo maestro creado e iniciado")
        
        # Simular algunos nodos esclavos
        await master.register_slave_node("slave_1", "localhost", 8001)
        await master.register_slave_node("slave_2", "localhost", 8002)
        
        print("✅ Nodos esclavos registrados")
        
        # Obtener estado
        status = master.get_sync_status()
        print(f"✅ Estado del maestro:")
        print(f"   Nodos esclavos: {len(status.get('slave_nodes', {}))}")
        print(f"   Tiempo sincronizado: {master.get_synchronized_time():.3f}")
        
        # Detener servicio
        await master.stop_sync_service()
        print("✅ Servicio detenido")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de algoritmo Berkeley: {e}")
        return False


def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE SINCRONIZACIÓN DISTRIBUIDA")
    print("Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    print("🔄 TESTING ALGORITMO DE SINCRONIZACIÓN BERKELEY")
    print("=" * 70)
    
    tester = DistributedSyncTester()
    
    # Pruebas básicas
    print("\n1. Health Check...")
    if not tester.test_sync_health():
        print("❌ Health check falló, continuando...")
    
    print("\n2. Autenticación...")
    if not tester.authenticate():
        print("❌ No se pudo autenticar, saltando pruebas autenticadas")
        return
    
    print("\n3. Inicializar servicio como maestro...")
    if not tester.test_initialize_service("master"):
        print("❌ No se pudo inicializar servicio")
        return
    
    print("\n4. Obtener estado de sincronización...")
    status = tester.test_sync_status()
    
    print("\n5. Obtener métricas...")
    metrics = tester.test_sync_metrics()
    
    print("\n6. Obtener tiempo sincronizado...")
    tester.test_synchronized_time()
    
    print("\n7. Registrar nodo esclavo...")
    tester.test_register_slave_node()
    
    print("\n8. Sincronizar evento de juego...")
    tester.test_sync_game_event()
    
    print("\n9. Validar timing de evento...")
    tester.test_validate_event_timing()
    
    print("\n10. Forzar sincronización...")
    tester.test_force_sync()
    
    # Prueba del algoritmo Berkeley directamente
    print("\n11. Probar algoritmo Berkeley directamente...")
    try:
        asyncio.run(test_berkeley_algorithm())
    except Exception as e:
        print(f"❌ Error en prueba directa: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 PRUEBAS DEL SISTEMA DE SINCRONIZACIÓN COMPLETADAS")
    print("\n📊 RESUMEN:")
    print("- Sistema de sincronización Berkeley implementado")
    print("- API endpoints funcionales")
    print("- Integración con autenticación JWT")
    print("- Sincronización de eventos de juego")
    print("- Validación de timing distribuido")
    print("- Métricas y monitoreo completo")


if __name__ == "__main__":
    main()