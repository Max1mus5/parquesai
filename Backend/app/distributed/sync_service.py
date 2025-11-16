"""
Servicio de sincronización distribuida para el sistema de juegos
"""
import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.distributed.berkeley_algorithm import BerkeleyTimeSync, NodeRole, NodeStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class DistributedSyncService:
    """Servicio principal de sincronización distribuida"""
    
    def __init__(self):
        self.berkeley_sync: Optional[BerkeleyTimeSync] = None
        self.is_initialized = False
        self.node_discovery_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Configuración del nodo
        self.node_config = {
            "node_id": f"parques_node_{settings.NODE_ID if hasattr(settings, 'NODE_ID') else 'default'}",
            "role": NodeRole.MASTER,  # Por defecto maestro, puede cambiar
            "sync_interval": 30.0,
            "timeout": 5.0,
            "max_offset_threshold": 1.0
        }
        
        # Registro de nodos conocidos
        self.known_nodes: Dict[str, Dict[str, Any]] = {}
        
        # Métricas del servicio
        self.service_metrics = {
            "start_time": None,
            "total_sync_cycles": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "nodes_discovered": 0,
            "average_sync_accuracy": 0.0
        }
    
    async def initialize(
        self, 
        role: NodeRole = NodeRole.MASTER,
        node_id: Optional[str] = None,
        sync_interval: float = 30.0
    ):
        """Inicializar el servicio de sincronización"""
        if self.is_initialized:
            logger.warning("Sync service already initialized")
            return
        
        # Configurar nodo
        if node_id:
            self.node_config["node_id"] = node_id
        self.node_config["role"] = role
        self.node_config["sync_interval"] = sync_interval
        
        # Crear instancia de Berkeley
        self.berkeley_sync = BerkeleyTimeSync(
            node_id=self.node_config["node_id"],
            role=role,
            sync_interval=sync_interval,
            timeout=self.node_config["timeout"],
            max_offset_threshold=self.node_config["max_offset_threshold"]
        )
        
        # Iniciar servicio Berkeley
        await self.berkeley_sync.start_sync_service()
        
        # Iniciar tareas auxiliares
        self.node_discovery_task = asyncio.create_task(self._node_discovery_loop())
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        self.is_initialized = True
        self.service_metrics["start_time"] = datetime.now()
        
        logger.info(f"Distributed sync service initialized as {role.value} node: {self.node_config['node_id']}")
    
    async def shutdown(self):
        """Cerrar el servicio de sincronización"""
        if not self.is_initialized:
            return
        
        logger.info("Shutting down distributed sync service...")
        
        # Cancelar tareas
        if self.node_discovery_task:
            self.node_discovery_task.cancel()
        if self.health_check_task:
            self.health_check_task.cancel()
        
        # Cerrar Berkeley sync
        if self.berkeley_sync:
            await self.berkeley_sync.stop_sync_service()
        
        self.is_initialized = False
        logger.info("Distributed sync service shut down")
    
    async def register_node(
        self, 
        node_id: str, 
        address: str, 
        port: int, 
        role: NodeRole = NodeRole.SLAVE
    ):
        """Registrar un nuevo nodo en el sistema"""
        if not self.is_initialized or not self.berkeley_sync:
            raise RuntimeError("Sync service not initialized")
        
        # Registrar en Berkeley si somos maestro
        if self.berkeley_sync.role == NodeRole.MASTER and role == NodeRole.SLAVE:
            await self.berkeley_sync.register_slave_node(node_id, address, port)
        
        # Agregar a nodos conocidos
        self.known_nodes[node_id] = {
            "node_id": node_id,
            "address": address,
            "port": port,
            "role": role.value,
            "registered_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.service_metrics["nodes_discovered"] += 1
        logger.info(f"Registered {role.value} node: {node_id} at {address}:{port}")
    
    async def unregister_node(self, node_id: str):
        """Desregistrar un nodo del sistema"""
        if not self.is_initialized or not self.berkeley_sync:
            return
        
        # Desregistrar de Berkeley si somos maestro
        if self.berkeley_sync.role == NodeRole.MASTER:
            await self.berkeley_sync.unregister_slave_node(node_id)
        
        # Remover de nodos conocidos
        if node_id in self.known_nodes:
            del self.known_nodes[node_id]
            logger.info(f"Unregistered node: {node_id}")
    
    async def set_master_node(self, master_id: str, address: str, port: int):
        """Configurar nodo maestro (para nodos esclavos)"""
        if not self.is_initialized or not self.berkeley_sync:
            raise RuntimeError("Sync service not initialized")
        
        if self.berkeley_sync.role == NodeRole.SLAVE:
            await self.berkeley_sync.set_master_node(master_id, address, port)
            logger.info(f"Set master node: {master_id} at {address}:{port}")
    
    def get_synchronized_time(self) -> float:
        """Obtener tiempo sincronizado actual"""
        if self.berkeley_sync:
            return self.berkeley_sync.get_synchronized_time()
        return time.time()
    
    def get_synchronized_datetime(self) -> datetime:
        """Obtener datetime sincronizado actual"""
        if self.berkeley_sync:
            return self.berkeley_sync.get_synchronized_datetime()
        return datetime.now()
    
    def get_time_offset(self) -> float:
        """Obtener offset de tiempo local"""
        if self.berkeley_sync:
            return self.berkeley_sync.local_time_offset
        return 0.0
    
    async def force_sync(self) -> Dict[str, Any]:
        """Forzar sincronización inmediata"""
        if not self.is_initialized or not self.berkeley_sync:
            return {"error": "Sync service not initialized"}
        
        if self.berkeley_sync.role != NodeRole.MASTER:
            return {"error": "Only master nodes can force sync"}
        
        try:
            # Realizar sincronización Berkeley
            await self.berkeley_sync._perform_berkeley_sync()
            
            self.service_metrics["total_sync_cycles"] += 1
            self.service_metrics["successful_syncs"] += 1
            
            return {
                "success": True,
                "message": "Forced synchronization completed",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.service_metrics["failed_syncs"] += 1
            logger.error(f"Error in forced sync: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_time_request(self) -> Dict[str, Any]:
        """Manejar solicitud de tiempo (para nodos esclavos)"""
        if not self.berkeley_sync:
            return {"error": "Sync service not initialized"}
        
        return self.berkeley_sync.handle_time_request()
    
    def handle_time_adjustment(self, adjustment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar ajuste de tiempo (para nodos esclavos)"""
        if not self.berkeley_sync:
            return {"error": "Sync service not initialized"}
        
        result = self.berkeley_sync.handle_time_adjustment(adjustment_data)
        
        # Actualizar métricas del servicio
        if result.get("success"):
            self.service_metrics["successful_syncs"] += 1
        else:
            self.service_metrics["failed_syncs"] += 1
        
        return result
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Obtener estado completo de sincronización"""
        status = {
            "service": {
                "initialized": self.is_initialized,
                "node_config": self.node_config,
                "known_nodes": len(self.known_nodes),
                "metrics": self.service_metrics
            }
        }
        
        if self.berkeley_sync:
            status["berkeley"] = self.berkeley_sync.get_sync_status()
        
        status["nodes"] = self.known_nodes
        
        return status
    
    def get_sync_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de sincronización"""
        base_metrics = self.service_metrics.copy()
        
        if self.berkeley_sync:
            berkeley_stats = self.berkeley_sync.sync_stats
            base_metrics.update({
                "berkeley_total_syncs": berkeley_stats["total_syncs"],
                "berkeley_successful_syncs": berkeley_stats["successful_syncs"],
                "berkeley_failed_syncs": berkeley_stats["failed_syncs"],
                "berkeley_average_offset": berkeley_stats["average_offset"],
                "berkeley_max_offset": berkeley_stats["max_offset"],
                "berkeley_last_sync_duration": berkeley_stats["last_sync_duration"]
            })
        
        # Calcular métricas adicionales
        if base_metrics["total_sync_cycles"] > 0:
            base_metrics["success_rate"] = (
                base_metrics["successful_syncs"] / base_metrics["total_sync_cycles"]
            )
        else:
            base_metrics["success_rate"] = 0.0
        
        if base_metrics["start_time"]:
            uptime = datetime.now() - base_metrics["start_time"]
            base_metrics["uptime_seconds"] = uptime.total_seconds()
        
        return base_metrics
    
    async def _node_discovery_loop(self):
        """Loop de descubrimiento de nodos"""
        while self.is_initialized:
            try:
                await self._discover_nodes()
                await asyncio.sleep(60.0)  # Descubrir cada minuto
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in node discovery: {e}")
                await asyncio.sleep(30.0)
    
    async def _discover_nodes(self):
        """Descubrir nodos en la red (implementación básica)"""
        # En una implementación real, esto podría usar:
        # - Multicast DNS
        # - Consul/etcd para service discovery
        # - Base de datos compartida
        # - Broadcast UDP
        
        # Por ahora, solo log de placeholder
        logger.debug("Node discovery cycle (placeholder)")
    
    async def _health_check_loop(self):
        """Loop de verificación de salud de nodos"""
        while self.is_initialized:
            try:
                await self._check_node_health()
                await asyncio.sleep(30.0)  # Verificar cada 30 segundos
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check: {e}")
                await asyncio.sleep(15.0)
    
    async def _check_node_health(self):
        """Verificar salud de nodos conocidos"""
        current_time = datetime.now()
        
        for node_id, node_info in list(self.known_nodes.items()):
            try:
                last_seen = datetime.fromisoformat(node_info["last_seen"])
                time_since_seen = (current_time - last_seen).total_seconds()
                
                # Marcar nodos como inactivos si no se han visto en 5 minutos
                if time_since_seen > 300:
                    node_info["status"] = "inactive"
                    logger.warning(f"Node {node_id} marked as inactive (last seen {time_since_seen:.0f}s ago)")
                
                # Remover nodos que no se han visto en 30 minutos
                if time_since_seen > 1800:
                    await self.unregister_node(node_id)
                    logger.info(f"Removed inactive node {node_id}")
                    
            except Exception as e:
                logger.error(f"Error checking health of node {node_id}: {e}")
    
    async def sync_game_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sincronizar evento de juego con timestamp distribuido"""
        if not self.is_initialized:
            return {"error": "Sync service not initialized"}
        
        # Agregar timestamp sincronizado al evento
        sync_time = self.get_synchronized_time()
        sync_datetime = self.get_synchronized_datetime()
        
        event_data.update({
            "sync_timestamp": sync_time,
            "sync_datetime": sync_datetime.isoformat(),
            "node_id": self.node_config["node_id"],
            "time_offset": self.get_time_offset()
        })
        
        return {
            "success": True,
            "synchronized_event": event_data,
            "sync_info": {
                "local_time": time.time(),
                "synchronized_time": sync_time,
                "offset": self.get_time_offset()
            }
        }
    
    async def validate_event_timing(
        self, 
        event_timestamp: float, 
        tolerance: float = 2.0
    ) -> Dict[str, Any]:
        """Validar timing de un evento contra tiempo sincronizado"""
        current_sync_time = self.get_synchronized_time()
        time_diff = abs(current_sync_time - event_timestamp)
        
        is_valid = time_diff <= tolerance
        
        return {
            "valid": is_valid,
            "time_difference": time_diff,
            "tolerance": tolerance,
            "current_sync_time": current_sync_time,
            "event_timestamp": event_timestamp,
            "message": "Event timing valid" if is_valid else f"Event timing invalid (diff: {time_diff:.3f}s)"
        }


# Instancia global del servicio
distributed_sync_service = DistributedSyncService()