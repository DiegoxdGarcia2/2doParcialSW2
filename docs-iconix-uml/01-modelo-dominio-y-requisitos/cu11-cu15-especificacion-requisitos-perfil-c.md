# 📋 Especificación de Requisitos y Casos de Uso (CU11 al CU15) — Perfil C
## Metodología ICONIX & Estándar UML 2.5+ — AegisCore AI

---

### 🏛️ Identificación de la Célula de Trabajo
- **Célula:** Perfil C (Inteligencia Artificial, Machine Learning, Deep Learning, Agentes Autónomos, Protocolo MCP y Angular BI).
- **Materia:** Ingeniería de Software II (2do Parcial) — **Grupo:** #27.
- **Responsabilidad:** Microservicio 4 (`backend/ms4-ia-mcp-python`) y Micro-Frontend 1 (`frontend/mf1-admin-angular`).

---

## 📑 Índice de Casos de Uso del Perfil C
1. [CU11: Visión Artificial y Clasificación de Daños en Fotos/Videos de Choques](#-cu11-visión-artificial-y-clasificación-de-daños-en-fotosvideos-de-choques-con-cnn)
2. [CU12: Predicción de Ventas y Primas Óptimas con Machine Learning Supervisado](#-cu12-predicción-de-ventas-y-primas-óptimas-con-random-forest-regressor)
3. [CU13: Segmentación de Clientes (K-Means) y Detección de Fraude (Isolation Forest)](#-cu13-segmentación-de-clientes-k-means-y-detección-de-fraude-isolation-forest)
4. [CU14: Monitoreo Continuo y Re-planning con Agente Autónomo LangGraph](#-cu14-monitoreo-continuo-y-re-planning-con-agente-autónomo-langgraph)
5. [CU15: Generar Reportes Dinámicos por Voz mediante Servidor MCP con Blindaje OWASP Anti-SQLi](#-cu15-generar-reportes-dinámicos-por-voz-mediante-servidor-mcp-con-blindaje-owasp-anti-sqli)

---

## 📷 CU11: Visión Artificial y Clasificación de Daños en Fotos/Videos de Choques con CNN

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU11` |
| **Nombre** | Clasificar severidad y piezas dañadas en fotos o videos de siniestros viales mediante Redes Neuronales Convolucionales (CrashNet CNN). |
| **Actor Primario** | Ajustador de Siniestros / Perito Automotriz. |
| **Disparador** | El usuario carga una fotografía o video del vehículo accidentado en el portal web de peritaje. |
| **Precondiciones** | El usuario está autenticado con rol `PERITO` o `AJUSTADOR`. El archivo es un formato gráfico válido (`.jpg`, `.jpeg`, `.png`, `.mp4`). |
| **Postcondiciones** | Se almacena el dictamen visual en el expediente MongoDB con la etiqueta de severidad, piezas detectadas, confianza y mapa de activación Grad-CAM. |

### 2. Flujo Principal (Happy Path)
1. El perito accede a la vista `/ai-damage-inspector` en el Micro-Frontend Angular.
2. El sistema presenta el área de carga (Drag & Drop) y opciones de simulación de peritajes viales.
3. El perito selecciona una imagen o captura un video del choque y presiona **"Ejecutar Análisis con CrashNet"**.
4. La vista invoca el endpoint `POST /api/v1/vision/analyze-crash` enviando el archivo binario en `multipart/form-data`.
5. El objeto de control `CrashVisionControl` recibe la petición, preprocesa la imagen normalizándola a un tensor $(224 \times 224 \times 3)$ y escala los píxeles al rango $[0, 1]$.
6. La entidad `CrashNetKerasModel` ejecuta la inferencia tensorial a través de 4 bloques convolucionales con activación ReLU, BatchNormalization, MaxPooling y capa de clasificación Softmax.
7. El control computa el vector de probabilidades para las 4 clases de severidad (`BAJA`, `MEDIA`, `ALTA`, `TOTAL`) e infiere las piezas impactadas (Parachoques, Capó, Faroles, Parabrisas, Puerta lateral).
8. El control genera las coordenadas de los Bounding Boxes y el mapa de calor Grad-CAM de las regiones de activación neuronal.
9. El control persiste el peritaje en MongoDB (`aegiscore_siniestros.expedientes`) vinculándolo al ID del siniestro.
10. La vista renderiza la imagen analizada con los Bounding Boxes interactivos, el porcentaje de confianza global y el desglose de costos estimados.

### 3. Flujos Alternativos y Excepciones
- **FA-11.1 (Video Multiframe):** Si el perito carga un archivo de video (`.mp4`), el control invoca `procesarVideoChoque()`, muestrea a razón de 2 frames por segundo, ejecuta inferencia por lote y selecciona los 3 frames de mayor deformación estructural.
- **EX-11.1 (Imagen no identificable / borrosa):** Si la confianza máxima no supera el umbral del $60\%$, el sistema devuelve advertencia `CONFIDENCIA_INSUFICIENTE` y solicita al perito una fotografía con mejor iluminación o ángulo.
- **EX-11.2 (Formato no soportado):** Si el archivo no corresponde a imágenes o video, el boundary responde con código HTTP 415 (Unsupported Media Type).

### 4. Trazabilidad ICONIX
- **Boundary:** `VisionInspectorAngularView` (`/ai-damage-inspector`), `POST /api/v1/vision/analyze-crash`, `POST /api/v1/vision/analyze-crash-video`.
- **Control:** `CrashVisionControl` con métodos `predecirSeveridadCrashNet()`, `procesarVideoChoque()`, `generarMapaCalorGradCam()`.
- **Entity:** `CrashNetKerasModel` (`crashnet_v1_weights.h5`), `InspeccionDanoVisionDTO`, MongoDB `expedientes_siniestros`.

---

## 📈 CU12: Predicción de Ventas y Primas Óptimas con Random Forest Regressor

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU12` |
| **Nombre** | Predecir ventas y calcular prima técnica pura óptima mediante ensamble de Árboles de Decisión (Random Forest Regressor). |
| **Actor Primario** | Actuario Comercial / Gerente de Suscripción. |
| **Disparador** | El actuario ingresa los parámetros demográficos y del vehículo para cotizar o calibrar el portafolio de seguros. |
| **Precondiciones** | El modelo Random Forest se encuentra entrenado y serializado en `app/ml_artifacts/random_forest_regressor_v1.joblib` con base en los 1,200 registros de PostgreSQL. |
| **Postcondiciones** | Se retorna la prima estimada, el score $R^2$, el desglose de importancia de variables (Gini Importance) y la sensibilidad al riesgo. |

### 2. Flujo Principal (Happy Path)
1. El actuario accede a la pantalla `/actuarial-sales-prediction` en Angular BI.
2. Ingresa los parámetros del asegurado: edad, género, años de experiencia, zona geográfica, valor comercial del vehículo, historial de siniestros y uso (particular/comercial).
3. Presiona **"Calcular Prima Óptima con Random Forest"**.
4. La vista emite la solicitud `POST /api/v1/ml/predict-sales-premium` con el payload `PrediccionPrimaRequestDTO`.
5. El control `SupervisedMlControl` consulta la base relacional PostgreSQL `dataset_historico_ml_polizas` para obtener la siniestralidad acumulada en el segmento demográfico.
6. El control transforma las variables mediante One-Hot Encoding y normalización Standard Scaler.
7. La entidad `RandomForestJoblibModel` ejecuta la inferencia combinada de los 100 estimadores (árboles de regresión) promediando la predicción:
   $$\hat{y} = \frac{1}{B} \sum_{b=1}^{B} T_b(\mathbf{x})$$
8. El control calcula la importancia de variables con base en la reducción de impureza de Gini / MSE.
9. El control aplica el margen de solvencia actuarial ($25\%$ de recargo de seguridad y gastos de adquisición).
10. La vista renderiza la tarjeta de prima sugerida, el intervalo de confianza al $95\%$, y el gráfico de barras horizontales de las variables de mayor impacto actuarial.

### 3. Flujos Alternativos y Excepciones
- **FA-12.1 (Simulación de Sensibilidad):** El actuario ajusta un slider de deducible o valor comercial; la vista recalcula en tiempo real con latencia $< 50$ ms.
- **EX-12.1 (Valores fuera de rango actuarial):** Si la edad es menor a 18 años o el valor del vehículo es negativo, el control rechaza la petición con código HTTP 422 (Unprocessable Entity).

### 4. Trazabilidad ICONIX
- **Boundary:** `ActuarialSalesPredictionView` (`/actuarial-sales-prediction`), `POST /api/v1/ml/predict-sales-premium`.
- **Control:** `SupervisedMlControl` con métodos `entrenarYPredecirPrimaRandomForest()`, `calcularImportanciaVariables()`, `validarLimitesActuariales()`.
- **Entity:** `RandomForestJoblibModel` (`random_forest_regressor_v1.joblib`), PostgreSQL `dataset_historico_ml_polizas`, `PrediccionPrimaResponseDTO`.

---

## 🔍 CU13: Segmentación de Clientes (K-Means) y Detección de Fraude (Isolation Forest)

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU13` |
| **Nombre** | Segmentar la cartera de pólizas en 4 clusters conductuales y detectar siniestros fraudulentos mediante árboles de aislamiento (Isolation Forest). |
| **Actor Primario** | Oficial de Cumplimiento / Auditor de la Unidad de Investigación Especial (SIU). |
| **Disparador** | El auditor revisa la cartera global o somete un siniestro sospechoso a evaluación anti-fraude. |
| **Precondiciones** | Los artefactos `kmeans_clustering_v1.joblib` e `isolation_forest_v1.joblib` están cargados en memoria en MS4. |
| **Postcondiciones** | Se etiqueta el expediente con el score de anomalía; si supera el umbral crítico, se activa el estado `BLOQUEADO_AUDITORIA_SIU`. |

### 2. Flujo Principal (Happy Path)
1. El auditor ingresa a `/risk-fraud-sentinel` en Angular Admin.
2. La vista consulta `GET /api/v1/ml/clusters-and-anomalies` y grafica el mapa de dispersión de los 4 clusters (K-Means) con los puntos anómalos destacados en rojo.
3. El auditor ingresa el ID de un siniestro en evaluación y pulsa **"Auditar Siniestro con Isolation Forest"**.
4. La vista despacha `POST /api/v1/ml/evaluate-claim-fraud` con el identificador del reclamo.
5. El control `UnsupervisedFraudControl` recupera de MongoDB y PostgreSQL las características comportamentales del siniestro: días transcurridos desde emisión de la póliza hasta el siniestro, monto reclamado vs valor comercial, historial de reclamos previos y discrepancia horaria.
6. La entidad `KMeansClusterArtifact` proyecta el vector en el espacio euclidiano y le asigna su clúster de pertenencia ($k \in \{0, 1, 2, 3\}$).
7. La entidad `IsolationForestArtifact` calcula la longitud de trayectoria promedio $h(x)$ requerida para aislar la muestra y evalúa el score de anomalía:
   $$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
8. Si el score es negativo ($s > 0.65$), el control clasifica el evento como **Anomalía / Potencial Fraude**.
9. El control actualiza el documento en MongoDB marcando la bandera `flag_fraude_siu: true` y congela temporalmente cualquier orden de liquidación en MS3.
10. La interfaz visualiza el gráfico de radar multidimensional, la justificación de factores de riesgo y las recomendaciones para el equipo pericial.

### 3. Flujos Alternativos y Excepciones
- **FA-13.1 (Siniestro Legítimo):** Si el score indica normalidad ($s \le 0.50$), la interfaz muestra sello verde de conformidad y habilita la liquidación inmediata.
- **EX-13.1 (Expediente Inexistente):** Si el ID de siniestro no existe, el sistema retorna HTTP 404 (Not Found).

### 4. Trazabilidad ICONIX
- **Boundary:** `RiskFraudSentinelView` (`/risk-fraud-sentinel`), `POST /api/v1/ml/evaluate-claim-fraud`, `GET /api/v1/ml/clusters-and-anomalies`.
- **Control:** `UnsupervisedFraudControl` con métodos `segmentarClientesKMeans()`, `detectarAnomaliaIsolationForest()`, `evaluarSiniestroSospechoso()`.
- **Entity:** `KMeansClusterArtifact`, `IsolationForestArtifact`, MongoDB `expedientes_siniestros`.

---

## 🤖 CU14: Monitoreo Continuo y Re-planning con Agente Autónomo LangGraph

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU14` |
| **Nombre** | Supervisar la salud del cluster de microservicios, detectar degradación en SLAs y disparar skills autónomas con Re-planning mediante LangGraph. |
| **Actor Primario** | Director de Operaciones ERP / Sistema Autónomo en Segundo Plano. |
| **Disparador** | Evento de degradación detectado por el sensor de SLAs o ejecución manual desde la consola interactiva. |
| **Precondiciones** | Microservicios MS1, MS2, MS3, MS4 en ejecución o monitoreables. |
| **Postcondiciones** | Se registra un nuevo ciclo en el grafo LangGraph, se actualizan las metas activas y se ejecutan las skills correctivas automáticas. |

### 2. Flujo Principal (Happy Path)
1. El usuario accede a la vista `/autonomous-agent-monitor` en Angular.
2. La vista visualiza el grafo de estados con los 4 nodos principales: `Sensado/Salud`, `Evaluación de Metas`, `Re-planning / Skills` y `Reflexión Final`.
3. El usuario pulsa **"Disparar Ciclo Autónomo LangGraph"**.
4. La vista llama a `POST /api/v1/agent/trigger-evaluation`.
5. El control `LangGraphAutonomousAgentControl` compila y ejecuta el `StateGraph` cíclico.
6. **Nodo 1 (Sensor):** Interroga el estado de salud de MS1 (PHP DDD), MS2 (NestJS CQRS), MS3 (Spring Boot Hexagonal) y MS4 (Python).
7. **Nodo 2 (Evaluador):** Contrasta las métricas observadas contra los 4 Goals corporativos:
   - *Goal 1:* Mantener SLA de Liquidaciones $< 48$ horas.
   - *Goal 2:* Neutralidad de Riesgo de Fraude SIU.
   - *Goal 3:* Alta Disponibilidad del Cluster ($99.9\%$).
   - *Goal 4:* Balance Actuarial de Reservas.
8. **Nodo 3 (Re-planner / Skill Dispatcher):** Si un microservicio presenta latencia o fallos (ej. MS2 degradado), el grafo bifurca condicionalmente hacia el nodo de re-planificación y dispara la skill compensatoria:
   - `skill_reencolar_siniestros_criticos` o `skill_balanceo_cargas_actuariales`.
9. **Nodo 4 (Reflexión):** El agente sintetiza un informe reflexivo en lenguaje natural explicando el diagnóstico, la acción tomada y la recomendación preventiva.
10. El control persiste el nuevo estado en `agent_cluster_state.json`.
11. La vista actualiza la bitácora cronológica, ilumina en verde los nodos ejecutados y renderiza el resumen ejecutivo del ciclo.

### 3. Flujos Alternativos y Excepciones
- **FA-14.1 (Cluster Totalmente Saludable):** Si todos los servicios están en `HEALTHY` y las metas se cumplen, el agente concluye en el nodo de reflexión sin disparar skills paliativas.
- **EX-14.1 (Fallo en Persistencia del Checkpoint):** Si el almacenamiento de estado se corrompe, el agente regenera el estado basal sin interrumpir la operación del cluster.

### 4. Trazabilidad ICONIX
- **Boundary:** `AutonomousAgentMonitorView` (`/autonomous-agent-monitor`), `POST /api/v1/agent/trigger-evaluation`, `GET /api/v1/agent/cluster-state`.
- **Control:** `LangGraphAutonomousAgentControl` con métodos `ejecutarCicloAutonomo()`, `evaluarSaludCluster()`, `replanificarMetas()`, `dispararSkillCompensatoria()`.
- **Entity:** `AgentStateGraphArtifact` (`agent_cluster_state.json`), `AegisCoreMicroservicesCluster`.

---

## 🎙️ CU15: Generar Reportes Dinámicos por Voz mediante Servidor MCP con Blindaje OWASP Anti-SQLi

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU15` |
| **Nombre** | Interpretar comandos dictados por voz con Whisper STT, filtrar inyecciones SQL bajo estándares OWASP, ejecutar Tools MCP parametrizadas y compilar reportes ejecutivos descargables (Excel, PDF, Word). |
| **Actor Primario** | Director Ejecutivo de Operaciones / Perito en Campo. |
| **Disparador** | El usuario dicta un comando de voz a través del micrófono web (Angular) o móvil (Flutter). |
| **Precondiciones** | El usuario tiene micrófono habilitado y acceso a la consola de reportes o la aplicación móvil. |
| **Postcondiciones** | Se genera el archivo físico en `artifacts/reports/` con su hash SHA-256, se registran las métricas en la respuesta y se ofrece descarga directa. |

### 2. Flujo Principal (Happy Path)
1. El usuario accede a `/voice-mcp-reports` en Angular o presiona el botón flotante de micrófono en Flutter (`PeritajeCaptureScreen`).
2. Dicta una orden: *"Generar reporte ejecutivo de siniestros graves en formato PDF"*.
3. El boundary cliente captura el audio en formato binario (`.wav` o `.webm`) o envía el texto dictado en tiempo real.
4. Se despacha la petición a `POST /api/v1/mcp/voice-command`.
5. El objeto de control `VoiceMcpControl` ejecuta el pipeline seguro en 4 etapas:
   - **Etapa 1 (Whisper STT):** Decodifica los frames acústicos y extrae el texto en lenguaje natural.
   - **Etapa 2 (Filtro de Seguridad OWASP Anti-SQLi):** El componente `OwaspAntiSqliGuard` valida léxica y sintácticamente el texto. Al no contener tautologías ni patrones de inyección, otorga el sello de seguridad `SEGURO`.
   - **Etapa 3 (Despacho MCP):** El control mapea la intención a una herramienta tipada del catálogo MCP (`tool_reporte_siniestralidad`) y ejecuta la consulta SQL/Mongo con **parámetros vinculados (prepared statements)**.
   - **Etapa 4 (Compilación Documental):** El exportador correspondiente (`PdfExporter`) compila el archivo físico con la estética corporativa *Executive Precision* y calcula su huella criptográfica SHA-256.
6. El boundary responde con `VoiceMcpExecutionResponse` conteniendo el enlace de streaming `/api/v1/mcp/download-report/{filename}`, el hash SHA-256, los KPIs calculados y la traza de la herramienta MCP.
7. La vista presenta la tarjeta de descarga con botón de descarga inmediata y el resumen de indicadores clave.

### 3. Flujos Alternativos y Excepciones (Blindaje Anti-SQLi en Acción)
- **FA-15.1 (Exportación a Excel / Word):** Si el usuario solicita formato Excel (`.xlsx`) o Word (`.docx`), el sistema utiliza `ExcelExporter` o `WordExporter` compilando tablas con formato de celdas contables y paleta teal corporativa.
- **EX-15.1 (Intento de Inyección SQL Detectado):**
  - Si un usuario malicioso dicta o inyecta: `reporte de siniestros ' OR '1'='1` o `UNION SELECT * FROM usuarios_sso`.
  - El `OwaspAntiSqliGuard` detecta la infracción en $< 2$ ms, clasifica la amenaza con score crítico $\ge 0.95$ y asigna la regla vulnerada (ej. `OWASP-A03:SQLi-Tautology`).
  - El control **aborta inmediatamente** la operación, **bloquea cualquier consulta hacia la base de datos**, retorna código HTTP 400 (Bad Request) y registra el incidente de seguridad en la bitácora.
  - La interfaz de usuario muestra una **alerta visual roja de amenaza neutralizada** informando que el ataque fue bloqueado al $100\%$.

### 4. Trazabilidad ICONIX
- **Boundary:** `VoiceMcpReportsView` (Angular), `VoiceMcpMobileView` (Flutter Card & FAB), `POST /api/v1/mcp/voice-command`, `GET /api/v1/mcp/tools`, `GET /api/v1/mcp/download-report/{filename}`.
- **Control:** `VoiceMcpControl`, `OwaspAntiSqliGuard`, `McpProtocolServer`, `DocumentExportersControl` (`ExcelExporter`, `PdfExporter`, `WordExporter`).
- **Entity:** `VoiceCommandRequest`, `OwaspSecurityAuditDTO`, `McpToolDefinitionDTO`, `GeneratedDocumentDTO`, `VoiceMcpExecutionResponse`, `artifacts/reports/*.{xlsx,pdf,docx}`.

---

## 🎨 6. Conformidad con el Sistema de Diseño ("Executive Precision")
Todos los prototipos de interfaz de usuario de estos 5 casos de uso consumen estrictamente los tokens del Sistema de Diseño Oficial extraído de **Google Stitch MCP** (`projects/9132956203380267795`):
- **Paleta de Colores:**
  - Executive Teal Principal: `#005C55` (600: `#0F766E`, 50: `#F0FDFA`)
  - Deep Navy Corporativo: `#0F172A` / `#1E293B`
  - AI & Telemetry Royal Indigo: `#4F46E5` / `#3F33D6`
  - Base Alabaster: `#F8FAFC`
  - Borde Sutil y Elevaciones: `#E2E8F0` / Shadow LG
- **Tríada Tipográfica:**
  - `Plus Jakarta Sans`: Títulos, KPIs de impacto y encabezados de tarjetas.
  - `Inter`: Formularios, tablas de datos, cuerpos de texto y botones.
  - `JetBrains Mono`: Hashes SHA-256, sentencias parametrizadas, tokens MCP y métricas de tensores.
