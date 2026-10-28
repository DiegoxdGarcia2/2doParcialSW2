# 🧠 Perfil C: Casos de Uso CU11 al CU15 — Inteligencia Artificial, Agentes & MCP

> **Responsable:** Célula C (Perfil C) — Grupo #27  
> **Microservicio:** `MS4: Python 3.11 / FastAPI`  
> **Frontend:** `MF1: Angular 17+ Admin & BI`  
> **Metodología:** ICONIX (Boundary, Control, Entity) + UML 2.5+  

---

## 📌 Matriz de Casos de Uso

| ID | Nombre | Algoritmo / Patrón | Entrada | Salida | Persistencia |
|---|---|---|---|---|---|
| **[[CU11]]** | Visión Artificial y Detección de Choques | TensorFlow 2 / Keras CNN (CrashNet) | Foto/Video del siniestro | Severidad, Bounding Boxes, Heatmap | MongoDB (`expedientes_siniestros`) |
| **[[CU12]]** | Predicción de Ventas y Primas Óptimas | Scikit-Learn Random Forest Regressor | Datos demográficos y vehículo | Prima técnica, $R^2$, Gini Importance | PostgreSQL 16 (`dataset_historico_ml_polizas`) |
| **[[CU13]]** | Segmentación y Detección de Fraude | K-Means + Isolation Forest | Vector comportamental del siniestro | Score anomalía, Cluster, Bandera SIU | MongoDB (`flag_fraude_siu`) |
| **[[CU14]]** | Monitoreo y Re-planning Continuo | LangGraph StateGraph (Agente Autónomo) | Métricas de salud del cluster | Reflexión cognitiva, Skills correctivas | `agent_cluster_state.json` |
| **[[CU15]]** | Reportes por Voz y Servidor MCP | Servidor MCP + Whisper + OWASP Anti-SQLi | Audio o prompt dictado por voz | Reportes descargables (XLSX, PDF, DOCX) | Archivos físicos con SHA-256 en disco |

---

## 🏛️ Trazabilidad ICONIX de los Casos de Uso

### CU11: Visión Artificial Choques con TensorFlow CNN
- **Boundary:** `VisionInspectorAngularView` (`/ai-damage-inspector`), `POST /api/v1/vision/analyze-crash`.
- **Control:** `CrashVisionControl::predecirSeveridadCrashNet(imagen_bytes)`.
- **Entity:** `CrashNetKerasModel` (`crashnet_v1_weights.h5`), MongoDB `expedientes_siniestros`.

### CU12: Predicción de Ventas y Primas Óptimas
- **Boundary:** `ActuarialSalesPredictionView` (`/actuarial-sales`), `POST /api/v1/ml/predict-sales-premium`.
- **Control:** `SupervisedMlControl::entrenarYPredecirPrimaRandomForest(dto)`.
- **Entity:** `RandomForestJoblibModel` (100 Trees), PostgreSQL `dataset_historico_ml_polizas`.

### CU13: Segmentación K-Means y Detección Fraude Isolation Forest
- **Boundary:** `RiskFraudSentinelView` (`/risk-fraud-sentinel`), `POST /api/v1/ml/evaluate-claim-fraud`.
- **Control:** `UnsupervisedFraudControl::evaluarSiniestroSospechoso(id_siniestro)`.
- **Entity:** `KMeansClusterArtifact` ($k=4$), `IsolationForestArtifact` ($c=0.08$), MongoDB.

### CU14: Monitoreo y Re-planning con Agente Autónomo LangGraph
- **Boundary:** `AutonomousAgentMonitorView` (`/autonomous-agent-monitor`), `POST /api/v1/agent/trigger-evaluation`.
- **Control:** `LangGraphAutonomousAgentControl::ejecutarCicloAutonomo()`.
- **Entity:** `AgentStateGraphArtifact` (`agent_cluster_state.json`), Health Check APIs.

### CU15: Reportes Dinámicos por Voz con Servidor MCP y Anti-SQLi
- **Boundary:** `VoiceMcpReportsView` (Angular), `HomeDashboardScreen` / `PeritajeCaptureScreen` (Flutter), `POST /api/v1/mcp/voice-command`.
- **Control:** `VoiceMcpControl::procesarComandoVozCompleto()`, `OwaspAntiSqliGuard`, `McpProtocolServer`.
- **Entity:** `OwaspSecurityAuditDTO`, `McpToolDefinitionDTO`, `GeneratedDocumentDTO`, `artifacts/reports/*`.

---

## 🔗 Referencias Cruzadas
- [[02 - Arquitectura del Sistema/Arquitectura 4 Niveles y Patrones|Arquitectura General del Sistema]]
- [[03 - Modulos y Servicios Core/MS4 Python IA y Servidor MCP|Documentación Técnica MS4 Python]]
- [[03 - Modulos y Servicios Core/MF1 Angular Admin y Dashboard BI|Documentación Micro-Frontend Angular]]
- [[04 - Base de Datos y Modelos/Persistencia Poliglota y Esquemas|Persistencia Políglota]]
