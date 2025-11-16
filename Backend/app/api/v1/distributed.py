"""
Endpoints API para el sistema de sincronización distribuida
"""
import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models.user import User
from app.core.security import get_current_user
from app.distributed.sync_service import distributed_sync_service
from app.distributed.berkeley_algorithm import NodeRole


router = APIRouter()


# Schemas de request/response
class NodeRegistrationRequest(BaseModel):
    """Request para registrar un nodo"""
    node_id: str
    address: str
    port: int
    role: str = "slave"  # "master" o "slave"


class MasterNodeRequest(BaseModel):
    """Request para configurar nodo maestro"""
    master_id: str
    address: str
    port: int


class TimeAdjustmentRequest(BaseModel):
    """Request para ajuste de tiempo"""
    adjustment: float
    target_time: float
    confidence: float = 1.0
    master_id: str


class GameEventSyncRequest(BaseModel):
    """Request para sincronizar evento de juego"""
    event_type: str
    event_data: Dict[str, Any]
    game_id: Optional[str] = None


class TimingValidationRequest(BaseModel):
    """Request para validar timing de evento"""
    event_timestamp: float
    tolerance: float = 2.0


# Endpoints públicos (no requieren autenticación para comunicación entre nodos)

@router.get("/time")
async def get_node_time():
    """Obtener tiempo del nodo actual (usado por algoritmo Berkeley)"""
    try:
        time_info = distributed_sync_service.handle_time_request()
        return time_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting node time: {str(e)}"
        )


@router.post("/adjust")
async def adjust_node_time(adjustment_data: TimeAdjustmentRequest):
    """Ajustar tiempo del nodo (usado por algoritmo Berkeley)"""
    try:
        result = distributed_sync_service.handle_time_adjustment(adjustment_data.dict())
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Time adjustment failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adjusting node time: {str(e)}"
        )


# Endpoints administrativos (requieren autenticación)

@router.get("/status")
async def get_sync_status(current_user: User = Depends(get_current_user)):
    """Obtener estado completo del sistema de sincronización"""
    try:
        status = distributed_sync_service.get_sync_status()
        return status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting sync status: {str(e)}"
        )


@router.get("/metrics")
async def get_sync_metrics(current_user: User = Depends(get_current_user)):
    """Obtener métricas del sistema de sincronización"""
    try:
        metrics = distributed_sync_service.get_sync_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting sync metrics: {str(e)}"
        )


@router.post("/nodes/register")
async def register_node(
    node_data: NodeRegistrationRequest,
    current_user: User = Depends(get_current_user)
):
    """Registrar un nuevo nodo en el sistema de sincronización"""
    try:
        # Validar rol
        if node_data.role not in ["master", "slave"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be 'master' or 'slave'"
            )
        
        role = NodeRole.MASTER if node_data.role == "master" else NodeRole.SLAVE
        
        await distributed_sync_service.register_node(
            node_data.node_id,
            node_data.address,
            node_data.port,
            role
        )
        
        return {
            "success": True,
            "message": f"Node {node_data.node_id} registered successfully",
            "node_id": node_data.node_id,
            "role": node_data.role
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering node: {str(e)}"
        )


@router.delete("/nodes/{node_id}")
async def unregister_node(
    node_id: str,
    current_user: User = Depends(get_current_user)
):
    """Desregistrar un nodo del sistema"""
    try:
        await distributed_sync_service.unregister_node(node_id)
        
        return {
            "success": True,
            "message": f"Node {node_id} unregistered successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unregistering node: {str(e)}"
        )


@router.post("/master")
async def set_master_node(
    master_data: MasterNodeRequest,
    current_user: User = Depends(get_current_user)
):
    """Configurar nodo maestro (para nodos esclavos)"""
    try:
        await distributed_sync_service.set_master_node(
            master_data.master_id,
            master_data.address,
            master_data.port
        )
        
        return {
            "success": True,
            "message": f"Master node {master_data.master_id} configured successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting master node: {str(e)}"
        )


@router.post("/force-sync")
async def force_synchronization(current_user: User = Depends(get_current_user)):
    """Forzar sincronización inmediata"""
    try:
        result = await distributed_sync_service.force_sync()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Synchronization failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error forcing synchronization: {str(e)}"
        )


@router.get("/time/synchronized")
async def get_synchronized_time(current_user: User = Depends(get_current_user)):
    """Obtener tiempo sincronizado actual"""
    try:
        sync_time = distributed_sync_service.get_synchronized_time()
        sync_datetime = distributed_sync_service.get_synchronized_datetime()
        local_time = time.time()
        offset = distributed_sync_service.get_time_offset()
        
        return {
            "local_time": local_time,
            "synchronized_time": sync_time,
            "synchronized_datetime": sync_datetime.isoformat(),
            "time_offset": offset,
            "difference": sync_time - local_time
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting synchronized time: {str(e)}"
        )


# Endpoints para integración con juegos

@router.post("/events/sync")
async def sync_game_event(
    event_data: GameEventSyncRequest,
    current_user: User = Depends(get_current_user)
):
    """Sincronizar evento de juego con timestamp distribuido"""
    try:
        result = await distributed_sync_service.sync_game_event({
            "event_type": event_data.event_type,
            "event_data": event_data.event_data,
            "game_id": event_data.game_id,
            "user_id": str(current_user.id)
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing game event: {str(e)}"
        )


@router.post("/events/validate-timing")
async def validate_event_timing(
    validation_data: TimingValidationRequest,
    current_user: User = Depends(get_current_user)
):
    """Validar timing de un evento contra tiempo sincronizado"""
    try:
        result = await distributed_sync_service.validate_event_timing(
            validation_data.event_timestamp,
            validation_data.tolerance
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating event timing: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check del sistema de sincronización"""
    try:
        is_initialized = distributed_sync_service.is_initialized
        
        if is_initialized:
            sync_time = distributed_sync_service.get_synchronized_time()
            offset = distributed_sync_service.get_time_offset()
            
            return {
                "status": "healthy",
                "initialized": True,
                "synchronized_time": sync_time,
                "time_offset": offset,
                "timestamp": time.time()
            }
        else:
            return {
                "status": "not_initialized",
                "initialized": False,
                "timestamp": time.time()
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }


# Endpoints de configuración

@router.post("/initialize")
async def initialize_sync_service(
    role: str = Query("master", description="Node role: master or slave"),
    node_id: Optional[str] = Query(None, description="Custom node ID"),
    sync_interval: float = Query(30.0, description="Sync interval in seconds"),
    current_user: User = Depends(get_current_user)
):
    """Inicializar el servicio de sincronización"""
    try:
        # Validar rol
        if role not in ["master", "slave"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be 'master' or 'slave'"
            )
        
        node_role = NodeRole.MASTER if role == "master" else NodeRole.SLAVE
        
        await distributed_sync_service.initialize(
            role=node_role,
            node_id=node_id,
            sync_interval=sync_interval
        )
        
        return {
            "success": True,
            "message": "Sync service initialized successfully",
            "role": role,
            "node_id": distributed_sync_service.node_config["node_id"],
            "sync_interval": sync_interval
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing sync service: {str(e)}"
        )


@router.post("/shutdown")
async def shutdown_sync_service(current_user: User = Depends(get_current_user)):
    """Cerrar el servicio de sincronización"""
    try:
        await distributed_sync_service.shutdown()
        
        return {
            "success": True,
            "message": "Sync service shut down successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error shutting down sync service: {str(e)}"
        )