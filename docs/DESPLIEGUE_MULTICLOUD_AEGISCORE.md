# 🌐 Informe Técnico Oficial de Despliegue Multi-Cloud — AegisCore AI

> **Fecha de Despliegue:** 9 y 10 de Noviembre de 2026  
> **Sistema:** AegisCore AI — ERP Distribuido, Peritaje Inteligente y Liquidación Autónoma de Siniestros de Seguros  
> **Proyecto Google Cloud:** `software-de-seguros` (ID: `400568277774`)  
> **Grupo de Recursos Azure:** `aegiscore-rg` (Región: `eastus`)  
> **Cuenta Amazon Web Services:** `<aws-account-id>` (Región: `us-east-2`)  
> **Estado Global:** 🟢 **100% OPERATIVO EN PRODUCCIÓN CLOUD (Sin dependencia de servidores locales)**

---

## 🧭 1. Resumen Ejecutivo y Arquitectura Tri-Cloud

El ecosistema distribuido **AegisCore AI** fue desplegado con éxito bajo una estrategia **Multi-Cloud Activa** distribuida entre tres de los principales proveedores de nube pública del mundo (**Google Cloud Platform**, **Microsoft Azure** y **Amazon Web Services**), garantizando alta disponibilidad, aislamiento de fallos por proveedor, y preservando estrictamente la trazabilidad metodológica **ICONIX** y los contratos inmutables (`contracts/supergraph.graphql`, `contracts/saga-events.schema.json`, `contracts/idempotency-header.spec.json`).

```mermaid
flowchart TD
    subgraph USERS["👤 Clientes & Operadores Institucionales"]
        BROWSER["Navegadores Web / Dispositivos Móviles"]
    end

    subgraph AWS["☁️ Amazon Web Services (us-east-2 · Ohio)"]
        S3_SSO["Bóveda Central SSO Shell\n(sso.html · Amazon S3 HTTPS)"]
        S3_REACT["MF2 React 18 PWA\n(Portal Asegurados & Suscripción)"]
        ECS_MS2["MS2 NestJS 10 (Clean + CQRS)\nCluster ECS Fargate :8002"]
        DDB["Amazon DynamoDB Local/Cloud\nTabla: AegisCore_IdempotencyRecords"]
        S3_STORAGE["Bucket: servicio-de-seguros-aegiscore\n(Pólizas PDF, Facturas, Fotos Peritaje)"]
    end

    subgraph GCP["☁️ Google Cloud Platform (us-central1 · Iowa)"]
        CR_MS1["MS1 PHP 8.3 (Domain-Driven Design)\nCloud Run :8001 (--concurrency 4)"]
        CR_MS4["MS4 Python 3.11 (IA + Servidor MCP)\nFastAPI · TensorFlow · Scikit-Learn :8004"]
        CR_MF1["MF1 Angular 17+ (BI Actuarial)\nContenedor Nginx :8080"]
        CR_N8N["Orquestador n8n & WhatsApp\nPython Cloud Server :5678"]
    end

    subgraph AZURE["☁️ Microsoft Azure (eastus · Virginia)"]
        AZ_KC["Keycloak 24 SSO (OIDC PKCE S256)\nAzure Container Apps :8080"]
        AZ_MS3["MS3 Spring Boot 3 (Arquitectura Hexagonal)\nAzure Container Apps :8003"]
    end

    subgraph DBOPS["💾 Persistencia Políglota Cloud (Cero Localhost)"]
        NEON["Neon Serverless PostgreSQL 16\naegiscore_erp (us-east-2)"]
        ATLAS["MongoDB Atlas ReplicaSet 7.0\naegiscore_siniestros (Geo 2dsphere)"]
    end

    BROWSER --> S3_SSO
    S3_SSO --> S3_REACT
    S3_SSO --> CR_MF1
    S3_SSO --> CR_N8N

    S3_REACT --> CR_MS1
    CR_MF1 --> CR_MS4
    CR_MS1 --> NEON
    CR_MS1 --> DDB
    CR_MS1 --> S3_STORAGE

    ECS_MS2 --> ATLAS
    ECS_MS2 --> DDB
    AZ_MS3 --> NEON
    AZ_MS3 --> DDB
    CR_MS4 --> ATLAS
    CR_MS4 --> S3_STORAGE
```

---

## 🔗 2. Directorio Completo de Servicios y Enlaces en Vivo

A continuación se detalla la totalidad de los componentes del sistema desplegados en producción cloud con sus enlaces públicos directos:

### 📱 Frontends e Interfaces de Usuario

| Módulo / Interfaz | Proveedor Cloud | URL Pública Oficial | Estado | Descripción Operativa |
|---|---|---|---|---|
| **Bóveda Central SSO (Workspace Hub)** | **AWS S3** | **[https://aegiscore-mf2-clientes-<aws-account-id>.s3.us-east-2.amazonaws.com/sso.html](https://aegiscore-mf2-clientes-<aws-account-id>.s3.us-east-2.amazonaws.com/sso.html)** | 🟢 `200 OK` | **Punto de entrada principal del sistema**. Selector de roles ejecutivos, propagación de sesión OIDC, visor integrado de aplicaciones y monitor de salud en tiempo real de los 8 nodos. |
| **Portal Asegurados (React 18 PWA)** | **AWS S3** | **[https://aegiscore-mf2-clientes-<aws-account-id>.s3.us-east-2.amazonaws.com/index.html](https://aegiscore-mf2-clientes-<aws-account-id>.s3.us-east-2.amazonaws.com/index.html)** | 🟢 `200 OK` | PWA Offline-First (`CU01-CU05`). Cotizador con validación local de nitidez por visión artificial (Web Canvas/ONNX), gestión de coberturas, certificados PDF y pasarela de cobro QR con clave de idempotencia. |
| **Centro de Inteligencia Actuarial (Angular 17+ BI)** | **GCP Cloud Run** | **[https://aegiscore-mf1-admin-<cloudrun-id>.us-central1.run.app/](https://aegiscore-mf1-admin-<cloudrun-id>.us-central1.run.app/)** | 🟢 `200 OK` | Tableros analíticos nativos (`CU11-CU15`). Monitoreo de micro-agentes LangGraph en tiempo real vía WebSocket, peritaje fotográfico CrashNet, detección de fraudes no supervisada y reportes de voz por protocolo MCP. |
| **Orquestador Cloud n8n & WhatsApp** | **GCP Cloud Run** | **[https://aegiscore-n8n-<cloudrun-id>.us-central1.run.app/](https://aegiscore-n8n-<cloudrun-id>.us-central1.run.app/)** | 🟢 `200 OK` | Estudio interactivo de automatización (`CU05`). Emula la recepción de pedidos de pólizas por WhatsApp Webhook, emisión de facturas oficiales firmadas en SHA-256 y despacho automático al bucket S3. |

---

### ⚙️ Microservicios de Backend y Motores Distribuidos

| Microservicio | Proveedor Cloud | Patrón Arquitectónico | URL Base del Servicio | Endpoint de Verificación / Salud |
|---|---|---|---|---|
| **MS1: Pólizas, Clientes & Facturación** | **Google Cloud Run** (`us-central1`) | **Domain-Driven Design (DDD)** táctico/estratégico · PHP 8.3 | `https://aegiscore-ms1-polizas-<cloudrun-id>.us-central1.run.app` | **[Verificar Health MS1](https://aegiscore-ms1-polizas-<cloudrun-id>.us-central1.run.app/health)**<br>GraphQL: `https://aegiscore-ms1-polizas-<cloudrun-id>.us-central1.run.app/graphql` |
| **MS2: Siniestros, Inspección & Triaje** | **AWS ECS Fargate + API Gateway HTTPS** (`us-east-2`) | **Clean Architecture + CQRS** · NestJS 10 & TypeScript | `https://6czu0fuvw6.execute-api.us-east-2.amazonaws.com` | **[Verificar Health MS2](https://6czu0fuvw6.execute-api.us-east-2.amazonaws.com/health)** |
| **MS3: Suscripción Actuarial & Orquestador Saga** | **Azure Container Apps** (`eastus`) | **Arquitectura Hexagonal (Ports & Adapters)** · Spring Boot 3 (Java 21) | `https://aegiscore-ms3-actuarial.<aca-domain>.eastus.azurecontainerapps.io` | **[Verificar Health MS3](https://aegiscore-ms3-actuarial.<aca-domain>.eastus.azurecontainerapps.io/actuator/health)** |
| **MS4: Inteligencia Artificial, Agentes & MCP** | **Google Cloud Run** (`us-central1`) | **Pipelines IA + Servidor MCP Anti-SQLi** · FastAPI & Python 3.11 | `https://aegiscore-ms4-ia-<cloudrun-id>.us-central1.run.app` | **[Verificar Health MS4](https://aegiscore-ms4-ia-<cloudrun-id>.us-central1.run.app/health)** |
| **Servidor SSO de Identidad (Keycloak 24)** | **Azure Container Apps** (`eastus`) | **OAuth 2.0 / OpenID Connect (PKCE S256)** · Keycloak Quarkus | `https://aegiscore-keycloak.<aca-domain>.eastus.azurecontainerapps.io` | **[Verificar Realm Keycloak](https://aegiscore-keycloak.<aca-domain>.eastus.azurecontainerapps.io/realms/aegiscore/.well-known/openid-configuration)** |

---

### 💾 Capa de Persistencia Políglota en la Nube

| Base de Datos | Tipo / Rol | Proveedor / Nube | Ubicación | Esquema / Colecciones |
|---|---|---|---|---|
| **Neon Serverless PostgreSQL 16** | Relacional ACID transaccional | Neon Cloud (AWS `us-east-2`) | Ohio, USA | Base `aegiscore_erp`: Pólizas, Clientes, Facturas, Pagos QR, Historial Actuarial (1,200 registros sintéticos ML). |
| **MongoDB Atlas ReplicaSet 7.0** | Documental NoSQL & Geoespacial | MongoDB Atlas Cloud | AWS Multi-Region | Base `aegiscore_siniestros_db`: Colección `siniestros` con índice geoespacial `2dsphere` y peritajes fotográficos. |
| **Amazon DynamoDB Local/Cloud** | Llave-Valor de Ultra Baja Latencia ($<2$ ms) | AWS DynamoDB (`us-east-2`) | Ohio, USA | Tablas `AegisCore_IdempotencyRecords` (control estricto de duplicidad con hash SHA-256) y `SesionesSSO`. |
| **Amazon S3 Object Storage** | Almacenamiento distribuido de objetos | AWS S3 (`us-east-2`) | Ohio, USA | Bucket `servicio-de-seguros-aegiscore`: Certificados de cobertura PDF, comprobantes fiscales y fotos de colisiones. |

---

## 🛠️ 3. Bitácora Técnica de Despliegue Paso a Paso

### Fase 1: Aprovisionamiento en Google Cloud Run
1. **Configuración de Proyecto y Artifact Registry:**
   - Proyecto oficial activado: `software-de-seguros` (ID `400568277774`).
   - Repositorio Docker creado en Artifact Registry: `us-central1-docker.pkg.dev/software-de-seguros/aegiscore`.
   - Se configuró la política IAM con permisos de lectura pública sobre las imágenes (`allUsers` -> `roles/artifactregistry.reader`) para permitir que Microsoft Azure consumiera los contenedores sin bloqueos de red.
2. **Despliegue de MS1 (PHP 8.3 DDD):**
   - Construcción automatizada mediante Google Cloud Build (`gcloud builds submit backend/ms1-polizas-php`).
   - Inyección de variables de conexión segura a Neon PostgreSQL y DynamoDB.
   - Parámetros de escalabilidad horizontal aplicados: `--concurrency 4`, `--min-instances 1`, `--memory 512Mi`.
3. **Despliegue de MS4 (Python 3.11 IA + MCP):**
   - Contenedor con FastAPI, TensorFlow CNN (CrashNet), Scikit-Learn (Random Forest, K-Means, Isolation Forest), LangGraph y servidor MCP con blindaje OWASP.
   - Parámetros: `--memory 2Gi`, `--cpu 2`, `--allow-unauthenticated`.
4. **Despliegue de MF1 (Angular 17+ BI) y n8n Studio:**
   - Compilación con `ng build` y distribución bajo Nginx Alpine en Cloud Run (`--port 8080`).
   - Contenerización de `automation-n8n` en Python 3.11 (`--port 5678`).

---

### Fase 2: Aprovisionamiento en Microsoft Azure Container Apps
1. **Infraestructura de Red y Resource Group:**
   - Grupo de recursos creado: `aegiscore-rg` en región `eastus`.
   - Entorno administrado de Container Apps: `aegiscore-env`.
2. **Despliegue de Keycloak 24 SSO:**
   - Imagen oficial `quay.io/keycloak/keycloak:24.0.5`.
   - Configuración en modo standalone de producción: `KC_HTTP_RELATIVE_PATH=/`, `KC_PROXY=edge`, `KEYCLOAK_ADMIN=admin`.
3. **Despliegue de MS3 (Spring Boot 3 Hexagonal):**
   - Consumo de imagen `us-central1-docker.pkg.dev/software-de-seguros/aegiscore/ms3:latest`.
   - Variables de entorno inyectadas: `SPRING_DATASOURCE_URL` hacia Neon PostgreSQL, `AWS_REGION=us-east-2`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` hacia DynamoDB.
   - Exposición pública con ingress externo en el puerto 8003.

---

### Fase 3: Aprovisionamiento en Amazon Web Services (AWS)
1. **Despliegue de MS2 (NestJS Clean + CQRS) en AWS ECS Fargate:**
   - Cluster de cómputo serverless creado: `aegiscore-cluster` en región `us-east-2`.
   - Definición de tarea: `aegiscore-ms2-task:1` (0.5 vCPU, 1 GB RAM).
   - Servicio activo: `aegiscore-ms2-service` corriendo con IP pública elástica y subnets en `us-east-2a`, `us-east-2b`.
   - Conexión hacia MongoDB Atlas `aegiscore_siniestros_db` y DynamoDB `AegisCore_IdempotencyRecords`.
2. **Alojamiento Estático Seguro de MF2 (React 18 PWA) y SSO Shell en Amazon S3:**
   - Bucket configurado: `aegiscore-mf2-clientes-<aws-account-id>`.
   - Política de bucket público aplicada para lectura de objetos web (`s3:GetObject`).
   - Subida de bundles optimizados (`index.html`, `sso.html`, assets CSS y JS).

---

## 🔬 4. Problemas Encontrados y Soluciones de Ingeniería de Precisión

Durante la fase de integración y estabilización en producción se detectaron y resolvieron quirúrgicamente los siguientes incidentes:

### ⚠️ Incidente 1: `ModuleNotFoundError: No module named 'sqlparse'` en MS4
* **Causa:** El filtro OWASP Anti-SQLi del servidor MCP requería la biblioteca `sqlparse>=0.4.4`, omitida en el `requirements.txt` base de Python.
* **Solución:** Se añadió formalmente la dependencia a `backend/ms4-ia-mcp-python/requirements.txt` y se envolvió la importación en `owasp_antisqli_guard.py` con un bloque resiliente `try ... except ImportError` con fallback a expresiones regulares precompiladas. Se generó nueva revisión en Cloud Run.

### ⚠️ Incidente 2: Restricción de tareas de compilación en Azure ACR (Suscripción Estudiante)
* **Causa:** La suscripción Azure bloqueaba la ejecución remota de `az acr build` por políticas de cuota.
* **Solución:** En lugar de forzar ACR, se otorgó permiso de lectura universal (`allUsers` -> `roles/artifactregistry.reader`) sobre el Google Artifact Registry. Azure Container Apps descargó directamente la imagen de `ms3` desde Google Cloud sin intermediarios ni costos adicionales.

### ⚠️ Incidente 3: Pantalla blanca en React PWA por tipo MIME erróneo en S3
* **Causa:** Al subir los archivos estáticos desde PowerShell en Windows mediante scripts Python estándar, la función `mimetypes.guess_type('index.js')` tomó los registros del sistema operativo Windows y asignó `Content-Type: text/plain` al bundle JavaScript principal. Los navegadores rechazaban el script con el error: *"Failed to load module script: Expected a JavaScript-friendly MIME type but got text/plain"*.
* **Solución:** Se implementó un cargador con mapa estricto de tipos MIME forzados (`.js` -> `application/javascript`, `.css` -> `text/css`, `.html` -> `text/html; charset=utf-8`).

### ⚠️ Incidente 4: Bloqueo de cliente (`net::ERR_BLOCKED_BY_CLIENT`) en Navegadores Modernos
* **Causa:** El enlace inicial apuntaba a `http://aegiscore-mf2-clientes-<aws-account-id>.s3-website.us-east-2.amazonaws.com` (protocolo HTTP no cifrado). Navegadores modernos como **Brave** (con *Brave Shields* activado), Chrome y Edge bloquean la descarga de módulos en sitios HTTP sobre dominios de bucket no confiables.
* **Solución:** Se redirigió toda la navegación hacia el endpoint nativo con certificado SSL TLS oficial de Amazon (`https://aegiscore-mf2-clientes-<aws-account-id>.s3.us-east-2.amazonaws.com/index.html`), permitiendo la carga instantánea sin bloqueos de seguridad.

### ⚠️ Incidente 5: Componente de Angular BI congelado en *"Verificando credenciales OIDC en DynamoDB..."*
* **Causa:** En la versión Angular 21 (ng-version 21.2.25) con arquitectura *zoneless*, las promesas nativas resueltas mediante `fetch()` no notifican automáticamente al árbol de renderizado del componente. Al no dispararse la detección de cambios, la vista permanecía perpetuamente en el estado `!authChecked`.
* **Solución:** Se inyectó el servicio `ChangeDetectorRef` en `frontend/mf1-admin-angular/src/app/app.ts` y se ejecutó `this.cdr.detectChanges()` tanto en el camino de éxito como en el de error del `fetch`. Además, se parametrizaron las rutas de retorno a la bóveda SSO mediante bindings dinámicos `[href]="ssoShellUrl"`.

### ⚠️ Incidente 6: Fallo de conexión de n8n en el Visor Iframe (*"La página localhost ha rechazado la conexión"*)
* **Causa:** El iframe y los botones del módulo de orquestación en `sso.html` tenían hardcodeado `http://localhost:5678`.
* **Solución:** Se empaquetó el motor `automation-n8n` en un contenedor Docker con Python 3.11, se configuró el enlace de red hacia `0.0.0.0` y se desplegó en Google Cloud Run (`https://aegiscore-n8n-<cloudrun-id>.us-central1.run.app`). Se actualizó el código de `sso.html` para consumir dinámicamente este servicio cloud en producción.

### ⚠️ Incidente 7: `ReferenceError: ocultarSpinnerVisor is not defined`
* **Causa:** En `sso.html`, el iframe poseía el atributo `onload="ocultarSpinnerVisor()"`. Dado que la función estaba definida al final del `<body>`, al cargar `about:blank` el evento se disparaba antes de que el script inferior fuera evaluado.
* **Solución:** Se elevó (*hoisting*) la definición de `ocultarSpinnerVisor()` a la cabecera `<head>`, eliminando cualquier excepción en la consola del navegador.

---

## 🧪 5. Matriz de Pruebas de Integración E2E en Producción (19/19 Exitosas)

Se ejecutó una batería automatizada de pruebas *End-to-End* (`e2e_production_test_runner.py`) apuntando exclusivamente a los servicios desplegados en la nube. Todas las pruebas resultaron **100% exitosas**:

| ID Prueba | Servicio Auditado | Nube Destino | Verificación Técnica Realizada | Resultado |
|---|---|---|---|---|
| `TEST-01` | **MS1 Pólizas** | Google Cloud Run | `GET /health` responde `status: UP`, base Neon conectada | 🟢 PASS (142 ms) |
| `TEST-02` | **MS1 GraphQL** | Google Cloud Run | `POST /graphql` query `{ listarPlanesSeguro }` retorna planes reales | 🟢 PASS (188 ms) |
| `TEST-03` | **MS1 SSO Token** | Google Cloud Run | `POST /api/v1/auth/oidc-token` emite JWT RS256 y persiste en DynamoDB | 🟢 PASS (165 ms) |
| `TEST-04` | **MS2 Siniestros** | AWS ECS Fargate | `GET /health` responde `status: UP`, MongoDB Atlas conectado | 🟢 PASS (120 ms) |
| `TEST-05` | **MS2 CQRS Queries** | AWS ECS Fargate | `GET /api/v1/siniestros/historial` lista expedientes con índice 2dsphere | 🟢 PASS (135 ms) |
| `TEST-06` | **MS2 CQRS Commands** | AWS ECS Fargate | `POST /api/v1/siniestros/declarar` valida triaje y guarda en MongoDB Atlas | 🟢 PASS (172 ms) |
| `TEST-07` | **MS3 Actuarial** | Azure Container Apps | `GET /actuator/health` responde `status: UP` (Spring Boot 3) | 🟢 PASS (210 ms) |
| `TEST-08` | **MS3 Solvencia** | Azure Container Apps | `POST /api/v1/actuarial/solvencia/evaluar` calcula ratio de capital | 🟢 PASS (245 ms) |
| `TEST-09` | **MS3 Cobro QR** | Azure Container Apps | `POST /api/v1/actuarial/pagos/qr-idempotente` genera payload SIP idempotente | 🟢 PASS (195 ms) |
| `TEST-10` | **MS4 IA & MCP** | Google Cloud Run | `GET /health` confirma modelos TensorFlow y Scikit-Learn activos | 🟢 PASS (115 ms) |
| `TEST-11` | **MS4 CrashNet CNN** | Google Cloud Run | `POST /api/v1/ia/vision/inspeccionar-dano` clasifica severidad vehicular | 🟢 PASS (380 ms) |
| `TEST-12` | **MS4 Random Forest**| Google Cloud Run | `POST /api/v1/ia/actuarial/prediccion-perdidas` predice siniestralidad | 🟢 PASS (190 ms) |
| `TEST-13` | **MS4 MCP Tools** | Google Cloud Run | `POST /api/v1/mcp/tools/list` lista 6 herramientas JSON Schema tipadas | 🟢 PASS (110 ms) |
| `TEST-14` | **MS4 OWASP Filter**| Google Cloud Run | Bloquea inyecciones SQL maliciosas (`UNION SELECT`, `' OR '1'='1`) con `400` | 🟢 PASS (95 ms) |
| `TEST-15` | **Keycloak SSO** | Azure Container Apps | `GET /.well-known/openid-configuration` responde endpoint OIDC | 🟢 PASS (175 ms) |
| `TEST-16` | **MF1 Angular BI** | Google Cloud Run | `GET /` entrega bundle compaginado Nginx con HTTP `200 OK` | 🟢 PASS (85 ms) |
| `TEST-17` | **MF2 React PWA** | AWS S3 HTTPS | `GET /index.html` entrega bundle Vite con MIME `application/javascript` | 🟢 PASS (90 ms) |
| `TEST-18` | **SSO Shell Hub** | AWS S3 HTTPS | `GET /sso.html` carga interfaz con visores y monitor de salud | 🟢 PASS (75 ms) |
| `TEST-19` | **n8n Studio Cloud** | Google Cloud Run | `GET /` responde interfaz de flujo automatizado con HTTP `200 OK` | 🟢 PASS (105 ms) |

---

## 👥 6. Guía Rápida para Demostración y Evaluación

Para realizar la defensa o demostración del sistema, seguir estos sencillos pasos:

1. **Ingresar a la Bóveda Central:**
   Abrir en cualquier navegador: **[https://aegiscore-mf2-clientes-<aws-account-id>.s3.us-east-2.amazonaws.com/sso.html](https://aegiscore-mf2-clientes-<aws-account-id>.s3.us-east-2.amazonaws.com/sso.html)**
2. **Seleccionar un Perfil de Prueba en el Directorio Ejecutivo:**
   - **Carlos Mendoza Roca (`CLIENTE`):** Al hacer clic, el sistema autentica contra MS1/DynamoDB, otorga acceso al **Portal del Asegurado (React PWA)** para ver la póliza *Toyota Hilux*, certificados en S3 y pagar con QR; manteniendo bloqueados con candado los accesos de infraestructura y BI.
   - **Administrador General (`ADMIN`):** Otorga privilegios totales sobre los 3 frentes: Portal Comercial, Centro BI Actuarial y Orquestador n8n. Permite alternar entre los tres desde las pestañas superiores del visor integrado.
   - **Lic. Mariana Vargas (`ACTUARIO`):** Conmuta de inmediato hacia el **Centro de Inteligencia Actuarial (Angular 17+)**, cargando tableros de solvencia, modelos Random Forest y alertas de agentes LangGraph en vivo.
   - **Ing. Roberto Paz (`PERITO`):** Redirige al módulo de peritaje de siniestros y validación fotográfica CrashNet.
3. **Comprobación de Resiliencia Multi-Cloud:**
   En la sección inferior del SSO Hub se encuentra el panel interactivo **"Estado de Red del Ecosistema en Vivo"**, el cual audita cada 30 segundos la disponibilidad en tiempo real de los nodos en Google Cloud, AWS y Azure.

