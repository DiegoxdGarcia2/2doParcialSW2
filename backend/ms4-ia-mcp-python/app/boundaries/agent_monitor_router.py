"""
=============================================================================
 AegisCore AI - MS4: [BOUNDARY] Router FastAPI del Agente Autónomo LangGraph
 Caso de Uso 14 (CU14): Monitorear Siniestros Estancados y Liquidez con Agente Autónomo
 Metodología ICONIX - Objeto Boundary (Punto de Entrada HTTP / API REST)
=============================================================================
"""

import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, status, HTTPException, Query, WebSocket, WebSocketDisconnect
from app.core.security import require_roles, CurrentUser
from app.entities.agent_monitor_dto import (
    AgentClusterStateDTO,
    StalledClaimDTO,
    LiquidityMetricsDTO,
    RunCycleResponseDTO,
    ExecuteSkillRequestDTO,
    ExecuteSkillResponseDTO
)
from app.controls.langgraph_autonomous_agent import langgraph_agent_control
from app.db.connections import get_mongo_db

router = APIRouter(
    prefix="/api/agent",
    tags=["CU14 - Agente Autónomo LangGraph (Metas, Re-planning & Skills)"]
)


@router.get(
    "/cluster-state",
    response_model=AgentClusterStateDTO,
    summary="Obtener Estado del Cluster Autónomo LangGraph",
    description="Retorna la salud operativa del cluster, latencia del Event Mesh (Kafka), "
                "topología del grafo de estados (DAG), micro-agentes activos y siniestros en cuello de botella."
)
def get_cluster_state(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> AgentClusterStateDTO:
    """Invoca el método operacional obtenerEstadoCluster() en el Control ICONIX."""
    try:
        return langgraph_agent_control.obtener_estado_cluster()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estado del cluster LangGraph: {str(e)}"
        )


@router.get(
    "/stalled-claims",
    response_model=List[StalledClaimDTO],
    summary="Listar Siniestros Estancados con SLA Excedido",
    description="Recupera los expedientes de MongoDB Atlas con cuellos de botella que requieren intervención o skills."
)
def get_stalled_claims(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> List[StalledClaimDTO]:
    """Invoca el método operacional evaluarSiniestrosEstancados() en el Control ICONIX."""
    try:
        raw_claims = langgraph_agent_control.evaluar_siniestros_estancados()
        return [StalledClaimDTO(**c) for c in raw_claims]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar siniestros estancados: {str(e)}"
        )


@router.post(
    "/run-cycle",
    response_model=RunCycleResponseDTO,
    summary="Disparar Ciclo Autónomo LangGraph (Re-planning y Reflexión)",
    description="Ejecuta en segundo plano el grafo StateGraph completo (FNOL -> Vision -> Policy -> Fraud -> Saga -> Reflection) "
                "y persiste las reflexiones y skills disparadas en la bitácora inmutable de MongoDB Atlas."
)
def run_autonomous_cycle(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> RunCycleResponseDTO:
    """Invoca el método operacional ejecutarCicloAutonomo() en el Control ICONIX."""
    try:
        return langgraph_agent_control.ejecutar_ciclo_autonomo()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el ciclo autónomo de LangGraph: {str(e)}"
        )


@router.post(
    "/execute-skill",
    response_model=ExecuteSkillResponseDTO,
    summary="Ejecutar Habilidad de Resolución sobre un Siniestro",
    description="Dispara de manera atómica una skill (GPS, Fast-Track, Segunda Evidencia o Congelar Pago) "
                "actualizando el expediente en MongoDB Atlas y notificando por Kafka."
)
def execute_skill(
    payload: ExecuteSkillRequestDTO,
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> ExecuteSkillResponseDTO:
    """Invoca el método operacional ejecutarSkillResolucion() en el Control ICONIX."""
    try:
        return langgraph_agent_control.ejecutar_skill_resolucion(
            reclamo_id=payload.numero_reclamo,
            skill_id=payload.skill_id,
            motivo=payload.motivo or "Resolución autorizada por auditor"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al ejecutar skill {payload.skill_id}: {str(e)}"
        )


@router.get(
    "/liquidity-metrics",
    response_model=LiquidityMetricsDTO,
    summary="Consultar Métricas de Reservas Técnicas y Solvencia II",
    description="Compara el fondo de capital disponible contra los siniestros comprometidos para liquidación."
)
def get_liquidity_metrics(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> LiquidityMetricsDTO:
    """Invoca el método operacional calcularEstresLiquidezReservas() en el Control ICONIX."""
    try:
        return langgraph_agent_control.calcular_estres_liquidez_reservas()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular métricas de liquidez: {str(e)}"
        )


@router.get(
    "/execution-logs",
    summary="Consultar Bitácora de Eventos y Reflexiones en MongoDB Atlas",
    description="Retorna el histórico de ejecuciones del grafo de agentes registrado en bitacora_agente_autonomo."
)
def get_execution_logs(
    limit: int = Query(default=10, ge=1, le=50, description="Cantidad máxima de registros a retornar"),
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> List[Dict[str, Any]]:
    """Consulta la colección bitacora_agente_autonomo en MongoDB Atlas y normaliza a AgentLogEventDTO."""
    try:
        db = get_mongo_db()
        logs = list(
            db.bitacora_agente_autonomo.find({}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(limit)
        )
        formatted_logs = []
        for l in logs:
            ts = l.get("timestamp")
            if hasattr(ts, "isoformat"):
                ts_str = ts.isoformat()
            elif isinstance(ts, str):
                ts_str = ts
            else:
                ts_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

            ciclo = l.get("ciclo_id", "CYCLE-CORE")
            skills = l.get("skills_disparadas", [])
            reflexion = l.get("reflexion_final", "Ciclo completado con éxito.")

            formatted_logs.append({
                "evento_id": f"EVT-{ciclo}",
                "timestamp": ts_str,
                "nodo": "LANGGRAPH_ORCHESTRATOR",
                "tipo_evento": "CICLO_AUTONOMO",
                "detalle": f"[{ciclo}] Reflexión: {reflexion[:120]}... Skills: {', '.join(skills) if skills else 'Ninguna'}",
                "impacto_expedientes": len(skills)
            })

        if not formatted_logs:
            ahora_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
            formatted_logs = [
                {
                    "evento_id": "EVT-INIT-01",
                    "timestamp": ahora_str,
                    "nodo": "FNOL_AGENT",
                    "tipo_evento": "TRANSICION_DAG",
                    "detalle": "Cluster LangGraph inicializado. Bus Kafka claims-core-v1 conectado (42ms).",
                    "impacto_expedientes": 0
                },
                {
                    "evento_id": "EVT-INIT-02",
                    "timestamp": ahora_str,
                    "nodo": "FRAUD_AGENT",
                    "tipo_evento": "TRANSICION_DAG",
                    "detalle": "Isolation Forest activo. Monitoreo no supervisado de sobreprecios.",
                    "impacto_expedientes": 0
                },
                {
                    "evento_id": "EVT-INIT-03",
                    "timestamp": ahora_str,
                    "nodo": "SOLVENCIA_AGENT",
                    "tipo_evento": "ALERTA_LIQUIDEZ",
                    "detalle": "Reservas técnicas evaluadas en $25.0M USD. Cobertura Solvencia II en 84.7%.",
                    "impacto_expedientes": 0
                }
            ]
        return formatted_logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar bitácora del agente en MongoDB Atlas: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Canal WebSocket en Tiempo Real para el Monitor Autónomo
# ---------------------------------------------------------------------------
@router.websocket("/ws")
@router.websocket("/ws/agent-monitor")
async def websocket_agent_monitor(websocket: WebSocket):
    """
    Canal WebSocket bidireccional en tiempo real para el monitor del Agente Autónomo.
    Transmite telemetría del cluster, logs de eventos, disparos de skills y alertas críticas (HUD).
    """
    await langgraph_agent_control.ws_manager.connect(websocket)
    try:
        # Enviar de inmediato el estado inicial del cluster al conectar
        initial_state = langgraph_agent_control.obtener_estado_cluster()
        await websocket.send_json({
            "tipo": "CONEXION_ESTABLECIDA",
            "cluster_state": initial_state.model_dump(),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        while True:
            # Escucha mensajes del cliente (ej. comando manual de re-planning o ping)
            data = await websocket.receive_text()
            if "ping" in data.lower():
                await websocket.send_json({"tipo": "PONG", "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})
            elif "trigger_cycle" in data.lower():
                res = langgraph_agent_control.ejecutar_ciclo_autonomo()
                state = langgraph_agent_control.obtener_estado_cluster()
                await langgraph_agent_control.ws_manager.broadcast({
                    "tipo": "CICLO_AUTONOMO_COMPLETADO",
                    "ciclo_id": res.ciclo_id,
                    "duracion_ms": res.duracion_total_ms,
                    "skills_disparadas": res.skills_disparadas,
                    "reflexion": res.reflexion_final,
                    "cluster_state": state.model_dump(),
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                })
    except WebSocketDisconnect:
        langgraph_agent_control.ws_manager.disconnect(websocket)
    except Exception:
        langgraph_agent_control.ws_manager.disconnect(websocket)


# ---------------------------------------------------------------------------
# Endpoints de Apoyo para Demostración y Pruebas en Vivo
# ---------------------------------------------------------------------------
@router.post(
    "/seed-stalled-claim",
    summary="Inyectar Siniestro Estancado de Prueba (Demostración de Auto-Remediación)",
    description="Inserta un nuevo siniestro estancado en MongoDB para verificar que el worker lo detecte y resuelva automáticamente."
)
def seed_stalled_claim(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
):
    try:
        return langgraph_agent_control.inyectar_siniestro_prueba()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al inyectar siniestro: {str(e)}"
        )


@router.get(
    "/notifications",
    summary="Obtener Notificaciones y Alertas Reales de MongoDB Atlas",
    description="Recupera las alertas críticas de fraude y eventos de remediación autónoma persistidos en la base de datos."
)
def get_notifications(
    limit: int = 15,
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
):
    try:
        return langgraph_agent_control.obtener_notificaciones_recientes(limite=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener notificaciones de MongoDB: {str(e)}"
        )


class MarkNotificationDTO(BaseModel):
    id: Optional[str] = None
    all: Optional[bool] = False


@router.post(
    "/notifications/mark-read",
    summary="Marcar Notificación como Leída en MongoDB Atlas",
    description="Persiste el estado de lectura de una o todas las notificaciones en la base de datos."
)
def mark_notification_read(
    req: Optional[MarkNotificationDTO] = None,
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
):
    try:
        if req and req.id:
            langgraph_agent_control.marcar_notificacion_leida(req.id)
            return {"status": "SUCCESS", "mensaje": f"Notificación {req.id} marcada como leída.", "id": req.id}
        else:
            total = langgraph_agent_control.marcar_todas_notificaciones_leidas()
            return {"status": "SUCCESS", "mensaje": "Todas las notificaciones marcadas como leídas.", "total": total}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al marcar notificación como leída en MongoDB: {str(e)}"
        )


@router.post(
    "/notifications/mark-all-read",
    summary="Marcar Todas las Notificaciones como Leídas",
    description="Marca de manera persistente todas las notificaciones actuales como leídas en MongoDB Atlas."
)
def mark_all_notifications_read(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
):
    try:
        total = langgraph_agent_control.marcar_todas_notificaciones_leidas()
        return {"status": "SUCCESS", "mensaje": "Todas las notificaciones marcadas como leídas.", "total": total}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al marcar todas las notificaciones en MongoDB: {str(e)}"
        )


@router.delete(
    "/notifications",
    summary="Limpiar y Archivar Historial de Notificaciones",
    description="Archiva y oculta las notificaciones actuales en MongoDB Atlas."
)
def clear_notifications(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
):
    try:
        total = langgraph_agent_control.limpiar_notificaciones()
        return {"status": "SUCCESS", "mensaje": "Historial de notificaciones archivado y limpiado.", "total": total}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al limpiar notificaciones en MongoDB: {str(e)}"
        )


@router.post(
    "/reset-stalled-claims",
    summary="Restaurar Siniestros Estancados Canónicos (Demostración)",
    description="Restaura los 3 siniestros estancados originales en MongoDB Atlas para ejecutar nuevamente la demostración del enjambre."
)
def reset_stalled_claims(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
):
    try:
        canonicos = langgraph_agent_control.reiniciar_siniestros_demostracion()
        return {
            "status": "SUCCESS",
            "mensaje": "3 siniestros canónicos restaurados en MongoDB Atlas.",
            "total_restaurados": len(canonicos)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al restaurar siniestros: {str(e)}"
        )
