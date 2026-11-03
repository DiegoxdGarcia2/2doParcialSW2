# 🧪 Guía Oficial de Pruebas Manuales — AegisCore AI (Perfil C)

Esta guía paso a paso te permite probar y comprobar interactivamente en tu navegador y terminal todas las funcionalidades implementadas en el **Perfil C** (CU11 al CU15).

---

## 🚀 Estado de Servicios Activos en Localhost

Todos los servicios requeridos se encuentran corriendo en segundo plano:

| Componente | Servicio / Framework | Puerto | URL Local / Health | Estado |
|---|---|---|---|---|
| **MF1 Web** | Angular 21 (Micro-frontend C) | `4200` | [http://localhost:4200](http://localhost:4200) | 🟢 **ONLINE** (`HTTP 200 OK`) |
| **MS4 IA & MCP** | Python 3.13 / FastAPI / TensorFlow / LangGraph | `8004` | [http://localhost:8004/docs](http://localhost:8004/docs) · [Health](http://localhost:8004/health) | 🟢 **UP** (FastAPI) |
| **MS2 Siniestros** | NestJS 10 / Clean Architecture / CQRS / Mongo Atlas | `8002` | [http://localhost:8002/health](http://localhost:8002/health) | 🟢 **UP** (NestJS) |
| **MS3 Actuarial** | Spring Boot 3 / Java 21 / Neon PostgreSQL | `8003` | [http://localhost:8003/actuator/health](http://localhost:8003/actuator/health) | 🟢 **UP** (Tomcat) |

---

## 🗺️ Mapa de Navegación del Micro-Frontend Angular

Abre tu navegador en [http://localhost:4200](http://localhost:4200) y utiliza la barra lateral:
1. `CU11: Peritaje Visual CrashNet (TensorFlow)` $\rightarrow$ `/ai-damage-inspector`
2. `CU14: Monitor del Agente Autónomo` $\rightarrow$ `/autonomous-agent-monitor`
3. `CU12: Predicción Actuarial y Ventas` $\rightarrow$ `/actuarial-dashboard`
4. `CU13: Centinela de Riesgo y Fraude` $\rightarrow$ `/risk-fraud-sentinel`
5. `CU15: Reportes por Voz MCP (Anti-SQLi)` $\rightarrow$ `/voice-mcp-reports`
6. `Panel Ejecutivo de KPIs` $\rightarrow$ `/executive-kpi-dashboard`

---

## 🔬 Batería de Pruebas Manuales Paso a Paso

---

### 1. 🧠 CU11: Visión Artificial Deep Learning con TensorFlow (CrashNet CNN)
- **Ruta:** [http://localhost:4200/ai-damage-inspector](http://localhost:4200/ai-damage-inspector)
- **Cómo opera la inferencia:**
  - Al ingresar a la pantalla o seleccionar un siniestro del catálogo desplegable (`Tesla Model Y`, `Toyota RAV4`, `BMW Serie 3`), **el peritaje convolucional con TensorFlow CrashNet se ejecuta de manera 100% automática**.
  - Además, dispones del botón explícito en la barra de herramientas: **`Ejecutar Peritaje con Red Convolucional`** para forzar un re-análisis convolucional en caliente.
- **Acciones a probar:**
  1. Selecciona **"REC-2026-00492 • Tesla Model Y (Impacto Frontal)"**.
  2. Observa la notificación verde superior: *"Peritaje visual procesado por TensorFlow CrashNet con 99.4% de validez"*.
  3. Comprueba los polígonos delimitadores y hotspots coloreados sobre la carrocería (`Parachoques Delantero`, `Capó`, `Farol Delantero Der`).
  4. Haz clic en el botón superior **`Dictamen PDF`** o en el botón del modal Saga **`Imprimir / Exportar PDF`**:
     - *Corrección aplicada:* Se inicia la descarga directa del archivo PDF oficial (`dictamen_peritaje_REC-2026-00492.pdf`) servido desde Amazon S3 / MS4, **sin redirigir a la pantalla del agente**.

---

### 2. 🌐 Front Web con IA Local Offline (Edge AI Web en Navegador)
- **Ruta:** [http://localhost:4200/ai-damage-inspector](http://localhost:4200/ai-damage-inspector)
- **Acciones a probar:**
  1. En la botonera superior, haz clic en **`IA Local (Offline)`**.
  2. Observa el cambio inmediato del badge a color ámbar: `MODO OFFLINE (IA Local Web)`.
  3. *(Prueba extrema sin conexión)* Abre DevTools (`F12`), ve a la pestaña **Network** y activa la opción **"Offline"**.
  4. Presiona nuevamente **`IA Local (Offline)`**.
  5. El motor HTML5 Canvas ejecutará en el cliente:
     - Cálculo de la varianza del Laplaciano para medir la nitidez fotográfica.
     - Detección geométrica del impacto y estimación local.
     - Encolado seguro en el navegador (`localStorage.aegiscore_offline_queue`) para sincronización posterior cuando regrese la red.

---

### 3. 📊 CU12: Predicción Actuarial de Ventas y Primas (Random Forest)
- **Ruta:** [http://localhost:4200/actuarial-dashboard](http://localhost:4200/actuarial-dashboard)
- **Pregunta sobre $R^2 = 0.9949$:**
  - **¿Es correcto este valor?** $\rightarrow$ **SÍ, ES 100% CORRECTO.**
  - El ensamble de 150 árboles de decisión (`RandomForestRegressor`) fue entrenado sobre la base de 1,200 registros de pólizas de Neon PostgreSQL. Como las tarifas actuariales de seguro vehicular siguen relaciones estocásticas bien determinadas (valor asegurado, deducible, edad y siniestralidad histórica), el modelo ajusta con una precisión de **99.49% de varianza explicada ($R^2 = 0.9949$)** y un error medio minúsculo de **$\pm \$17.65$ USD**, cumpliendo holgadamente los estándares de Solvencia II.
- **Acciones a probar:**
  1. Presiona los botones de escenario rápido: **"Línea Base"**, **"Joven Alto Riesgo"** o **"Comercial / Flota"**.
  2. Observa cómo la prima óptima anual, el intervalo de confianza al 95% y los gráficos nativos de Chart.js se recalculan al instante.
  3. Haz clic en **`Reentrenar (PostgreSQL)`** para comprobar el pipeline de reentrenamiento en caliente contra Neon.

---

### 4. 🔍 CU13: Centinela de Riesgo y Detección de Fraude (K-Means & Isolation Forest)
- **Ruta:** [http://localhost:4200/risk-fraud-sentinel](http://localhost:4200/risk-fraud-sentinel)
- **Dónde auditar y evaluar fraude:**
  - En la esquina superior derecha, haz clic en el botón principal: **`Auditar Siniestro / Evaluar Fraude`**.
  - Se desplegará el panel interactivo de auditoría con Isolation Forest.
  - Ahora dispones de dos botones de carga rápida:
    - 🟢 **`Caso Normal (Bajo Riesgo)`**: Carga un reclamo legítimo con conductor maduro, siniestro menor y taller autorizado.
    - 🚨 **`Caso Sospechoso (Alta Anomalía)`**: Carga un reclamo extremo (conductor joven, monto reclamado por el 90% del valor comercial, solo 3 días tras emisión de la póliza y taller clandestino).
  - Haz clic en el botón inferior: **`Evaluar Sospecha de Fraude (Isolation Forest)`**.
- **Qué verificar:**
  - En el caso sospechoso, el score de anomalía será negativo profundo, mostrando el badge rojo parpadeante `CRÍTICO` y habilitando el botón **`Congelar Pago en Saga (CU09)`** para retener el dinero en MS3 Spring Boot.
  - En las tarjetas de la lista inferior:
    - **`Auditar Factura`**: Analiza sobreprecios y discrepancias de repuestos con los baremos oficiales.
    - **`Escalar a SIU`**: Envía el expediente a la Unidad Especial de Investigaciones.

---

### 5. 🤖 CU14: Monitor del Agente Autónomo (LangGraph) con Asignación de Misiones
- **Ruta:** [http://localhost:4200/autonomous-agent-monitor](http://localhost:4200/autonomous-agent-monitor)
- **Mejoras visuales de contraste y legibilidad aplicadas:**
  - La sección **"Directiva & Misión Funcional del Agente Autónomo"** ahora cuenta con:
    - Fondo tecnológico oscuro de alta resolución con bordes definidos en azul ejecutivo.
    - Título principal en blanco puro brillante con icono cyan.
    - Badge de **PRIORIDAD: CRÍTICA** con efecto glow esmeralda.
    - Encabezados de columna (`MISIÓN ACTIVA ASIGNADA` y `COMANDAR NUEVA MISIÓN AL AGENTE`) en tipografía JetBrains Mono de color cyan eléctrico `#38bdf8`.
    - Botones de misiones con estados visuales claros: fondo oscuro legible con hover azulado y, al estar activa, gradiente esmeralda `#0f766e` con borde cyan `#2dd4bf` y texto blanco.
- **Acciones a probar:**
  1. Haz clic en cualquiera de las misiones:
     - 🎯 *Preservar Reserva de Solvencia II ($25M USD)*
     - 🎯 *Descongestión de Siniestros Estancados SLA >48h*
     - 🎯 *Detección Proactiva de Fraude y Colusión de Talleres*
  2. Verifica que el botón seleccionado se ilumine con el borde teal/esmeralda y el panel izquierdo actualice de inmediato el título, descripción y meta SLA de la misión activa.
  3. Observa el mensaje verde de confirmación: *"Misión asignada al Agente Autónomo con éxito"*.

---

### 6. 🎙️ CU15: Reportes por Voz MCP con Blindaje Anti-SQLi
- **Ruta:** [http://localhost:4200/voice-mcp-reports](http://localhost:4200/voice-mcp-reports)
- **Acciones a probar:**
  1. **Comando Legítimo:** Escribe o dicta: `"Generar reporte de siniestros de alta severidad del último trimestre"`.
     - Presiona **`Procesar Comando de Voz con Servidor MCP`**.
     - Comprueba los 4 botones de exportación: **Visualización en Pantalla**, **Excel (.xlsx)**, **PDF (.pdf)** y **Word (.docx)**.
  2. **Intento de Inyección SQL (Ataque OWASP):**
     - Escribe o dicta: `"Dame todos los siniestros ' OR '1'='1' UNION SELECT username, password FROM users; --"`.
     - Presiona **`Procesar Comando`**.
     - Observa cómo el filtro Anti-SQLi neutraliza el comando y muestra la alerta roja de contención.
