"""
Implementación del Algoritmo de Sincronización Berkeley
"""
import asyncio
import time
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import uuid
import aiohttp
import json

logger = logging.getLogger(__name__)


class NodeRole(Enum):
    """Roles de los nodos en el algoritmo Berkeley"""
    MASTER = "master"
    SLAVE = "slave"


class NodeStatus(Enum):
    """Estados de los nodos"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    SYNCHRONIZING = "synchronizing"


@dataclass
class TimeReading:
    """Lectura de tiempo de un nodo"""
    node_id: str
    timestamp: float
    local_time: float
    network_delay: float = 0.0
    received_at: float = field(default_factory=time.time)


@dataclass
class TimeAdjustment:
    """Ajuste de tiempo para un nodo"""
    node_id: str
    adjustment: float  # Segundos a ajustar (positivo = adelantar, negativo = atrasar)
    target_time: float
    confidence: float = 1.0


@dataclass
class SyncNode:
    """Nodo en el sistema de sincronización"""
    node_id: str
    address: str
    port: int
    role: NodeRole
    status: NodeStatus = NodeStatus.ACTIVE
    last_sync: Optional[datetime] = None
    time_offset: float = 0.0  # Offset respecto al tiempo maestro
    network_delay: float = 0.0
    sync_count: int = 0
    error_count: int = 0


class BerkeleyTimeSync:
    """Implementación del algoritmo de sincronización Berkeley"""
    
    def __init__(
        self, 
        node_id: str, 
        role: NodeRole = NodeRole.SLAVE,
        sync_interval: float = 30.0,
        timeout: float = 5.0,
        max_offset_threshold: float = 1.0
    ):
        self.node_id = node_id
        self.role = role
        self.sync_interval = sync_interval
        self.timeout = timeout
        self.max_offset_threshold = max_offset_threshold
        
        # Estado del nodo
        self.local_time_offset = 0.0
        self.is_running = False
        self.last_sync_time = None
        
        # Para nodo maestro
        self.slave_nodes: Dict[str, SyncNode] = {}
        self.sync_history: List[Dict[str, Any]] = []
        
        # Para nodo esclavo
        self.master_node: Optional[SyncNode] = None
        
        # Estadísticas
        self.sync_stats = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "average_offset": 0.0,
            "max_offset": 0.0,
            "last_sync_duration": 0.0
        }
        
        # Task de sincronización
        self.sync_task: Optional[asyncio.Task] = None
    
    def get_synchronized_time(self) -> float:
        """Obtener tiempo sincronizado actual"""
        return time.time() + self.local_time_offset
    
    def get_synchronized_datetime(self) -> datetime:
        """Obtener datetime sincronizado actual"""
        return datetime.fromtimestamp(self.get_synchronized_time())
    
    async def start_sync_service(self):
        """Iniciar servicio de sincronización"""
        if self.is_running:
            logger.warning(f"Sync service already running for node {self.node_id}")
            return
        
        self.is_running = True
        logger.info(f"Starting Berkeley sync service for {self.role.value} node {self.node_id}")
        
        if self.role == NodeRole.MASTER:
            self.sync_task = asyncio.create_task(self._master_sync_loop())
        else:
            self.sync_task = asyncio.create_task(self._slave_sync_loop())
    
    async def stop_sync_service(self):
        """Detener servicio de sincronización"""
        self.is_running = False
        
        if self.sync_task:
            self.sync_task.cancel()
            try:
                await self.sync_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f"Stopped Berkeley sync service for node {self.node_id}")
    
    # Métodos para nodo MAESTRO
    
    async def register_slave_node(self, node_id: str, address: str, port: int):
        """Registrar un nodo esclavo"""
        if self.role != NodeRole.MASTER:
            raise ValueError("Only master nodes can register slaves")
        
        slave_node = SyncNode(
            node_id=node_id,
            address=address,
            port=port,
            role=NodeRole.SLAVE
        )
        
        self.slave_nodes[node_id] = slave_node
        logger.info(f"Registered slave node {node_id} at {address}:{port}")
    
    async def unregister_slave_node(self, node_id: str):
        """Desregistrar un nodo esclavo"""
        if node_id in self.slave_nodes:
            del self.slave_nodes[node_id]
            logger.info(f"Unregistered slave node {node_id}")
    
    async def _master_sync_loop(self):
        """Loop principal del nodo maestro"""
        while self.is_running:
            try:
                await self._perform_berkeley_sync()
                await asyncio.sleep(self.sync_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in master sync loop: {e}")
                await asyncio.sleep(5.0)  # Esperar antes de reintentar
    
    async def _perform_berkeley_sync(self):
        """Realizar sincronización Berkeley completa"""
        if not self.slave_nodes:
            logger.debug("No slave nodes to synchronize")
            return
        
        sync_start = time.time()
        logger.info(f"Starting Berkeley synchronization with {len(self.slave_nodes)} slaves")
        
        # Paso 1: Recopilar tiempos de todos los nodos esclavos
        time_readings = await self._collect_slave_times()
        
        # Paso 2: Calcular tiempo promedio y ajustes
        adjustments = self._calculate_time_adjustments(time_readings)
        
        # Paso 3: Enviar ajustes a los nodos esclavos
        await self._send_time_adjustments(adjustments)
        
        # Actualizar estadísticas
        sync_duration = time.time() - sync_start
        self._update_sync_stats(adjustments, sync_duration)
        
        # Guardar en historial
        self.sync_history.append({
            "timestamp": datetime.now().isoformat(),
            "duration": sync_duration,
            "nodes_synced": len(adjustments),
            "average_adjustment": statistics.mean([abs(adj.adjustment) for adj in adjustments]) if adjustments else 0,
            "max_adjustment": max([abs(adj.adjustment) for adj in adjustments]) if adjustments else 0
        })
        
        # Mantener solo los últimos 100 registros
        if len(self.sync_history) > 100:
            self.sync_history = self.sync_history[-100:]
        
        logger.info(f"Berkeley synchronization completed in {sync_duration:.3f}s")
    
    async def _collect_slave_times(self) -> List[TimeReading]:
        """Recopilar tiempos de todos los nodos esclavos"""
        time_readings = []
        master_time = time.time()
        
        # Agregar tiempo del maestro
        time_readings.append(TimeReading(
            node_id=self.node_id,
            timestamp=master_time,
            local_time=master_time,
            network_delay=0.0
        ))
        
        # Recopilar tiempos de esclavos en paralelo
        tasks = []
        for node_id, node in self.slave_nodes.items():
            if node.status == NodeStatus.ACTIVE:
                task = asyncio.create_task(self._request_slave_time(node))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, TimeReading):
                    time_readings.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error collecting slave time: {result}")
        
        return time_readings
    
    async def _request_slave_time(self, node: SyncNode) -> Optional[TimeReading]:
        """Solicitar tiempo a un nodo esclavo específico"""
        request_time = time.time()
        
        try:
            url = f"http://{node.address}:{node.port}/sync/time"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_time = time.time()
                        
                        # Calcular delay de red (aproximado)
                        network_delay = (response_time - request_time) / 2
                        
                        # Ajustar tiempo por delay de red
                        adjusted_time = data["timestamp"] + network_delay
                        
                        node.network_delay = network_delay
                        node.last_sync = datetime.now()
                        node.sync_count += 1
                        
                        return TimeReading(
                            node_id=node.node_id,
                            timestamp=adjusted_time,
                            local_time=data["timestamp"],
                            network_delay=network_delay
                        )
                    else:
                        logger.warning(f"Failed to get time from {node.node_id}: HTTP {response.status}")
                        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout requesting time from {node.node_id}")
            node.error_count += 1
        except Exception as e:
            logger.error(f"Error requesting time from {node.node_id}: {e}")
            node.error_count += 1
            
            # Marcar nodo como fallido si hay muchos errores
            if node.error_count > 3:
                node.status = NodeStatus.FAILED
                logger.warning(f"Marking node {node.node_id} as failed due to repeated errors")
        
        return None
    
    def _calculate_time_adjustments(self, time_readings: List[TimeReading]) -> List[TimeAdjustment]:
        """Calcular ajustes de tiempo usando el algoritmo Berkeley"""
        if len(time_readings) < 2:
            return []
        
        # Extraer timestamps
        timestamps = [reading.timestamp for reading in time_readings]
        
        # Calcular tiempo promedio (excluyendo outliers)
        average_time = self._calculate_robust_average(timestamps)
        
        # Calcular ajustes para cada nodo
        adjustments = []
        
        for reading in time_readings:
            # No ajustar el tiempo del maestro
            if reading.node_id == self.node_id:
                continue
            
            # Calcular ajuste necesario
            adjustment = average_time - reading.timestamp
            
            # Crear ajuste solo si es significativo
            if abs(adjustment) > 0.001:  # 1ms threshold
                confidence = self._calculate_adjustment_confidence(adjustment, timestamps)
                
                adjustments.append(TimeAdjustment(
                    node_id=reading.node_id,
                    adjustment=adjustment,
                    target_time=average_time,
                    confidence=confidence
                ))
        
        return adjustments
    
    def _calculate_robust_average(self, timestamps: List[float]) -> float:
        """Calcular promedio robusto excluyendo outliers"""
        if len(timestamps) <= 2:
            return statistics.mean(timestamps)
        
        # Usar mediana si hay pocos valores
        if len(timestamps) <= 5:
            return statistics.median(timestamps)
        
        # Para más valores, excluir outliers usando IQR
        sorted_times = sorted(timestamps)
        n = len(sorted_times)
        
        q1_idx = n // 4
        q3_idx = 3 * n // 4
        
        q1 = sorted_times[q1_idx]
        q3 = sorted_times[q3_idx]
        iqr = q3 - q1
        
        # Filtrar outliers
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        filtered_times = [t for t in timestamps if lower_bound <= t <= upper_bound]
        
        # Si se filtraron demasiados valores, usar todos
        if len(filtered_times) < len(timestamps) * 0.5:
            filtered_times = timestamps
        
        return statistics.mean(filtered_times)
    
    def _calculate_adjustment_confidence(self, adjustment: float, all_timestamps: List[float]) -> float:
        """Calcular confianza del ajuste basado en la dispersión de tiempos"""
        if len(all_timestamps) <= 1:
            return 1.0
        
        # Calcular desviación estándar
        std_dev = statistics.stdev(all_timestamps)
        
        # Confianza inversamente proporcional a la desviación y al ajuste
        base_confidence = 1.0 / (1.0 + std_dev)
        adjustment_penalty = 1.0 / (1.0 + abs(adjustment))
        
        return min(base_confidence * adjustment_penalty, 1.0)
    
    async def _send_time_adjustments(self, adjustments: List[TimeAdjustment]):
        """Enviar ajustes de tiempo a los nodos esclavos"""
        if not adjustments:
            return
        
        tasks = []
        for adjustment in adjustments:
            node = self.slave_nodes.get(adjustment.node_id)
            if node and node.status == NodeStatus.ACTIVE:
                task = asyncio.create_task(self._send_adjustment_to_slave(node, adjustment))
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_adjustment_to_slave(self, node: SyncNode, adjustment: TimeAdjustment):
        """Enviar ajuste de tiempo a un nodo esclavo específico"""
        try:
            url = f"http://{node.address}:{node.port}/sync/adjust"
            
            payload = {
                "adjustment": adjustment.adjustment,
                "target_time": adjustment.target_time,
                "confidence": adjustment.confidence,
                "master_id": self.node_id
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            node.time_offset = adjustment.adjustment
                            logger.debug(f"Successfully sent adjustment {adjustment.adjustment:.3f}s to {node.node_id}")
                        else:
                            logger.warning(f"Slave {node.node_id} rejected adjustment: {result.get('message')}")
                    else:
                        logger.warning(f"Failed to send adjustment to {node.node_id}: HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Error sending adjustment to {node.node_id}: {e}")
            node.error_count += 1
    
    # Métodos para nodo ESCLAVO
    
    async def set_master_node(self, master_id: str, address: str, port: int):
        """Configurar nodo maestro"""
        if self.role != NodeRole.SLAVE:
            raise ValueError("Only slave nodes can set master")
        
        self.master_node = SyncNode(
            node_id=master_id,
            address=address,
            port=port,
            role=NodeRole.MASTER
        )
        
        logger.info(f"Set master node {master_id} at {address}:{port}")
    
    async def _slave_sync_loop(self):
        """Loop principal del nodo esclavo"""
        while self.is_running:
            try:
                # Los esclavos esperan solicitudes del maestro
                # Este loop principalmente mantiene el estado y estadísticas
                await asyncio.sleep(self.sync_interval)
                
                # Verificar si el maestro está activo
                if self.master_node and self.last_sync_time:
                    time_since_sync = time.time() - self.last_sync_time
                    if time_since_sync > self.sync_interval * 3:
                        logger.warning(f"No sync from master for {time_since_sync:.1f}s")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in slave sync loop: {e}")
                await asyncio.sleep(5.0)
    
    def handle_time_request(self) -> Dict[str, Any]:
        """Manejar solicitud de tiempo del maestro"""
        current_time = time.time()
        
        return {
            "node_id": self.node_id,
            "timestamp": current_time,
            "local_offset": self.local_time_offset,
            "last_sync": self.last_sync_time,
            "sync_count": self.sync_stats["total_syncs"]
        }
    
    def handle_time_adjustment(self, adjustment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar ajuste de tiempo del maestro"""
        try:
            adjustment = adjustment_data["adjustment"]
            target_time = adjustment_data["target_time"]
            confidence = adjustment_data.get("confidence", 1.0)
            master_id = adjustment_data.get("master_id")
            
            # Verificar que el ajuste no sea demasiado grande
            if abs(adjustment) > self.max_offset_threshold:
                logger.warning(f"Rejecting large time adjustment: {adjustment:.3f}s")
                return {
                    "success": False,
                    "message": f"Adjustment too large: {adjustment:.3f}s"
                }
            
            # Aplicar ajuste gradualmente para cambios grandes
            if abs(adjustment) > 0.1:  # 100ms
                # Aplicar solo una fracción del ajuste
                actual_adjustment = adjustment * 0.5
                logger.info(f"Applying gradual adjustment: {actual_adjustment:.3f}s (requested: {adjustment:.3f}s)")
            else:
                actual_adjustment = adjustment
            
            # Aplicar ajuste
            old_offset = self.local_time_offset
            self.local_time_offset += actual_adjustment
            self.last_sync_time = time.time()
            
            # Actualizar estadísticas
            self.sync_stats["total_syncs"] += 1
            self.sync_stats["successful_syncs"] += 1
            self.sync_stats["average_offset"] = (
                (self.sync_stats["average_offset"] * (self.sync_stats["total_syncs"] - 1) + abs(actual_adjustment)) /
                self.sync_stats["total_syncs"]
            )
            self.sync_stats["max_offset"] = max(self.sync_stats["max_offset"], abs(actual_adjustment))
            
            logger.info(f"Applied time adjustment: {actual_adjustment:.3f}s (offset: {old_offset:.3f}s -> {self.local_time_offset:.3f}s)")
            
            return {
                "success": True,
                "applied_adjustment": actual_adjustment,
                "new_offset": self.local_time_offset,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error handling time adjustment: {e}")
            self.sync_stats["failed_syncs"] += 1
            return {
                "success": False,
                "message": str(e)
            }
    
    def _update_sync_stats(self, adjustments: List[TimeAdjustment], duration: float):
        """Actualizar estadísticas de sincronización"""
        self.sync_stats["total_syncs"] += 1
        self.sync_stats["last_sync_duration"] = duration
        
        if adjustments:
            self.sync_stats["successful_syncs"] += 1
            
            avg_adjustment = statistics.mean([abs(adj.adjustment) for adj in adjustments])
            max_adjustment = max([abs(adj.adjustment) for adj in adjustments])
            
            # Actualizar promedio móvil
            total_syncs = self.sync_stats["total_syncs"]
            self.sync_stats["average_offset"] = (
                (self.sync_stats["average_offset"] * (total_syncs - 1) + avg_adjustment) / total_syncs
            )
            self.sync_stats["max_offset"] = max(self.sync_stats["max_offset"], max_adjustment)
        else:
            self.sync_stats["failed_syncs"] += 1
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Obtener estado de sincronización"""
        status = {
            "node_id": self.node_id,
            "role": self.role.value,
            "is_running": self.is_running,
            "local_time": time.time(),
            "synchronized_time": self.get_synchronized_time(),
            "time_offset": self.local_time_offset,
            "last_sync": self.last_sync_time,
            "stats": self.sync_stats.copy()
        }
        
        if self.role == NodeRole.MASTER:
            status["slave_nodes"] = {
                node_id: {
                    "address": f"{node.address}:{node.port}",
                    "status": node.status.value,
                    "last_sync": node.last_sync.isoformat() if node.last_sync else None,
                    "time_offset": node.time_offset,
                    "network_delay": node.network_delay,
                    "sync_count": node.sync_count,
                    "error_count": node.error_count
                }
                for node_id, node in self.slave_nodes.items()
            }
            status["sync_history"] = self.sync_history[-10:]  # Últimos 10 registros
        else:
            if self.master_node:
                status["master_node"] = {
                    "node_id": self.master_node.node_id,
                    "address": f"{self.master_node.address}:{self.master_node.port}",
                    "status": self.master_node.status.value
                }
        
        return status