"""
=============================================================================
 AegisCore AI - MS4: [ENTITY] DTOs para Monitoreo con Agente Autónomo LangGraph
 Caso de Uso 14 (CU14): Monitorear Siniestros Estancados y Liquidez
 Metodología ICONIX - Objeto Entity (Contratos de Datos Tipados)
=============================================================================
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import datetime


class AgentNodeStatusDTO(BaseModel):
    """Estado y latencia de cada nodo en el Grafo de Estados (DAG) de LangGraph."""
    nodo_id: str = Field(..., description="Identificador único del nodo en el grafo")
    nombre: str = Field(..., description="Nombre descriptivo del nodo de procesamiento")
    estado: str = Field(default="IDLE", description="Estado: IDLE, RUNNING, SUCCESS, FAILED, BYPASSED")
    latencia_ms: int = Field(default=0, description="Tiempo de procesamiento del nodo en milisegundos")
    completado: bool = Field(default=False, description="Indica si el paso concluyó en el ciclo activo")
    descripcion: Optional[str] = Field(None, description="Detalle del procesamiento realizado")


class ActiveMicroAgentDTO(BaseModel):
    """Ficha operativa de cada micro-agente en sesión dentro del cluster."""
    agente_id: str = Field(..., description="Código de identificación del agente")
    nombre: str = Field(..., description="Nombre del rol especializado")
    rol: str = Field(..., description="Responsabilidad operativa dentro de la cadena")
    kafka_topic: str = Field(default="claims-core-v1", description="Topic de Kafka suscrito")
    estado: str = Field(default="ONLINE", description="ONLINE, PROCESSING, STANDBY")
    skill_primaria: str = Field(..., description="Habilidad principal asociada")
    latencia_actual_ms: int = Field(default=42, description="Latencia observada")


class StalledClaimDTO(BaseModel):
    """Información técnica y causa raíz de un siniestro en cuello de botella."""
    numero_reclamo: str = Field(..., description="Identificador del expediente de siniestro")
    numero_poliza: str = Field(..., description="Código de póliza de seguro")
    estado_actual: str = Field(..., description="Estado del expediente en MongoDB Atlas")
    dias_estancado: int = Field(..., description="Tiempo transcurrido sin avance en días")
    cuello_botella: str = Field(..., description="Causa raíz del bloqueo")
    accion_sugerida: str = Field(..., description="Skill recomendada por el agente autónomo")
    modelo_vehiculo: Optional[str] = Field("Vehículo Asegurado", description="Datos del bien asegurado")
    monto_estimado_usd: float = Field(default=0.0, description="Monto en riesgo o cotizado")
    score_fraude: float = Field(default=0.0, description="Score de anomalía del modelo Isolation Forest")


class LiquidityMetricsDTO(BaseModel):
    """Evaluación en tiempo real de suficiencia de capital y reservas técnicas (Solvencia II)."""
    reserva_capital_total_usd: float = Field(default=25000000.0, description="Fondo total de reservas técnicas")
    compromisos_activos_usd: float = Field(..., description="Suma de indemnizaciones en proceso de liquidación")
    reserva_remanente_usd: float = Field(..., description="Capital líquido disponible post-pagos")
    ratio_cobertura_pct: float = Field(..., description="Porcentaje de cobertura de reservas")
    estado_solvencia: str = Field(default="SOLVENTE", description="SOLVENTE, ALERTA_PREVENTIVA, CRITICO")
    umbral_minimo_pct: float = Field(default=80.0, description="Límite reglamentario de solvencia")


class AgentLogEventDTO(BaseModel):
    """Evento registrado en la bitácora cronológica del agente en MongoDB Atlas."""
    evento_id: str = Field(..., description="Identificador único del evento")
    timestamp: str = Field(..., description="Marca de tiempo ISO-8601")
    nodo: str = Field(..., description="Nodo o agente que emitió el evento")
    tipo_evento: str = Field(..., description="TRANSICION_DAG, DISPARO_SKILL, REFLEXION, ALERTA_LIQUIDEZ")
    detalle: str = Field(..., description="Descripción técnica de la acción ejecutada")
    impacto_expedientes: int = Field(default=0, description="Número de siniestros afectados")


class AgentClusterStateDTO(BaseModel):
    """Estado global del cluster autónomo LangGraph para visualización en el dashboard."""
    cluster_estado: str = Field(default="SYNCHRONIZED", description="SYNCHRONIZED, RECONFIGURING, DEGRADED")
    salud_cluster_pct: float = Field(default=99.98, description="Porcentaje de disponibilidad operativa")
    latencia_promedio_ms: int = Field(default=42, description="Latencia global del Event Mesh")
    kafka_broker: str = Field(default="Kafka v3.6 (Topic: claims-core-v1)", description="Bus de mensajería")
    dag_estado: str = Field(default="DAG ACTIVE", description="Estado del grafo de estados LangGraph")
    nodos_grafo: List[AgentNodeStatusDTO] = Field(default_factory=list, description="Lista de nodos del DAG")
    micro_agentes: List[ActiveMicroAgentDTO] = Field(default_factory=list, description="Agentes en sesión")
    siniestros_estancados: List[StalledClaimDTO] = Field(default_factory=list, description="Casos detectados")
    metricas_liquidez: LiquidityMetricsDTO = Field(..., description="Evaluación de reservas")
    ultima_reflexion: str = Field(..., description="Conclusión del nodo de reflexión de LangGraph")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class ExecuteSkillRequestDTO(BaseModel):
    """Payload para forzar o autorizar la ejecución de una skill sobre un siniestro."""
    numero_reclamo: str = Field(..., description="Expediente sobre el cual actuar")
    skill_id: str = Field(..., description="SKILL_REASIGNAR_PERITO_GPS, SKILL_FAST_TRACK_APROBACION, SKILL_SOLICITAR_SEGUNDA_EVIDENCIA, SKILL_CONGELAR_LIQUIDACION_SAGA")
    motivo: Optional[str] = Field("Aprobación manual por auditor en consola Angular", description="Justificación de la acción")


class ExecuteSkillResponseDTO(BaseModel):
    """Respuesta de la ejecución de una habilidad autónoma."""
    exito: bool = Field(..., description="Resultado de la ejecución")
    numero_reclamo: str = Field(..., description="Expediente procesado")
    skill_ejecutada: str = Field(..., description="Habilidad disparada")
    nuevo_estado_expediente: str = Field(..., description="Nuevo estado del siniestro en MongoDB Atlas")
    detalle: str = Field(..., description="Resultado y asignación generada")
    bitacora_id: str = Field(..., description="Identificador en bitacora_agente_autonomo")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class RunCycleResponseDTO(BaseModel):
    """Resultado consolidado del ciclo autónomo ejecutado por LangGraph."""
    ciclo_id: str = Field(..., description="Identificador único del ciclo")
    duracion_total_ms: int = Field(..., description="Tiempo total de ejecución del grafo")
    siniestros_analizados: int = Field(..., description="Total de expedientes evaluados")
    siniestros_resueltos: int = Field(..., description="Expedientes desbloqueados con skills")
    skills_disparadas: List[str] = Field(default_factory=list, description="Lista de habilidades ejecutadas")
    reflexion_final: str = Field(..., description="Razonamiento generado por el nodo de reflexión")
    cluster_state: AgentClusterStateDTO = Field(..., description="Nuevo estado consolidado del cluster")
    persistencia_bitacora_id: str = Field(..., description="ID del documento en MongoDB Atlas")
