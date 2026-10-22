# 🛡️ AegisCore AI — Sistema Distribuido ERP, Peritaje Inteligente y Liquidación Autónoma

> **Materia:** Ingeniería de Software II (2do Parcial SW2) — Grupo #27  
> **Metodología de Desarrollo:** **ICONIX** (Modelo de Dominio, Casos de Uso con GUI, Análisis de Robustez BCE y Diagramas de Secuencia en **UML 2.5+** con métodos operacionales en la Clase de Control).  
> **Fecha Objetivo de Entrega Final:** 10 - 12 de noviembre.

---

## 🏛️ 1. Arquitectura Obligatoria en 4 Niveles

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ NIVEL 1: FRONTENDS HETEROGÉNEOS + SINGLE SIGN-ON (SSO)                                 │
│  • Keycloak SSO (OAuth2 / OIDC con JWT RS256 - Inicio de Sesión Único)                 │
│  • Angular 17+ (ERP Admin, Dashboard KPIs nativo en código, Consola Voz MCP)           │
│  • React 18+ PWA (Portal Clientes GraphQL, Soporte Offline, IA Local Web ONNX/TF.js)   │
│  • Flutter (App Peritos 100% Offline, SQLite local, Agente IA Local TensorFlow Lite)   │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                    │  GraphQL / REST + Idempotency-Key (UUIDv4)
┌───────────────────────────────────▼────────────────────────────────────────────────────┐
│ NIVEL 4: GATEWAY, ORQUESTACIÓN SAGA Y AUTOMATIZACIÓN MULTICANAL                        │
│  • Apollo GraphQL Supergraph Router (Gateway unificado federado)                       │
│  • Apache Kafka (Broker de Eventos y Orquestación Saga CU09 + Rollback Compensatorio)  │
│  • n8n Automation (Flujos WhatsApp -> ERP -> Facturación PDF y Siniestros Emergencia)  │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────────────────────┐
│ NIVEL 2: 4 MICROSERVICIOS, 4 LENGUAJES, 3 ARQUITECTURAS DE CÓDIGO                      │
│  • MS1: PHP 8.3 / Laravel      -> Patrón: Domain-Driven Design (DDD)                   │
│  • MS2: TypeScript / NestJS 10 -> Patrón: Clean Architecture + CQRS                    │
│  • MS3: Java 21 / Spring Boot 3-> Patrón: Arquitectura Hexagonal (Ports & Adapters)    │
│  • MS4: Python 3.11 / FastAPI  -> ML, Deep Learning TensorFlow, LangGraph y Servidor MCP│
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────────────────────┐
│ NIVEL 3: PERSISTENCIA POLÍGLOTA (3 MOTORES DE BASES DE DATOS)                          │
│  • PostgreSQL 16 (Relacional ACID: Clientes, Pólizas, Facturas, Pagos QR, Liquidación) │
│  • MongoDB 7     (NoSQL Documental: Expedientes Siniestros, Peritajes, Logs Agentes)   │
│  • DynamoDB Local(NoSQL Clave-Valor: IdempotencyRecords UUIDv4 y Sesiones SSO)         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 👥 2. Paquetes de Trabajo Equilibrados (3 Integrantes)

Para desarrollar en paralelo de forma autónoma sin bloqueos, el proyecto se distribuye en 3 Células Verticales mediante **Contratos Congelados**:

| Célula / Perfil | Casos de Uso | Tecnologías Asignadas | Puntos / Horas |
|---|---|---|---|
| **Perfil A** (Comercial, SSO, Web React & n8n) | **CU01, CU02, CU03, CU04, CU05** | Keycloak SSO, MS1 PHP (DDD + GraphQL), React PWA (IA Local Web TF.js/ONNX), n8n (WhatsApp Pedidos -> Factura PDF) | 42 pts / 26 hrs |
| **Perfil B** (Siniestros, Móvil Offline & Saga) | **CU06, CU07, CU08, CU09, CU10** | MS2 NestJS (Clean Arch + MongoDB + Push), MS3 Spring Boot (Hexagonal + Orquestador Saga en 3 MS), Flutter (SQLite + TFLite), DynamoDB | 44 pts / 29 hrs |
| **Perfil C** (IA, TensorFlow, Agentes, MCP & Angular) | **CU11, CU12, CU13, CU14, CU15** | MS4 Python FastAPI, Scikit-Learn (Random Forest, K-Means, Isolation Forest), TensorFlow CNN, LangGraph, Servidor MCP Voz + Anti-SQLi, Angular Admin | 43 pts / 28 hrs |

---

## 🔒 3. Contratos de Integración Congelados (`contracts/`)

Cada desarrollador programa contra las interfaces formales definidas en:
1. `contracts/supergraph.graphql`: Contrato de esquema GraphQL unificado (Queries, Mutations, Entidades y Extensiones federadas).
2. `contracts/saga-events.schema.json`: Contrato JSON Schema v7 para los comandos y eventos del **Patrón Saga** en Apache Kafka (Paso 1 NestJS, Paso 2 PHP, Paso 3 Spring Boot y reversión compensatoria).
3. `contracts/idempotency-header.spec.json`: Especificación técnica del header `Idempotency-Key` (UUIDv4) y ciclo de vida en Amazon DynamoDB Local.

---

## 🚀 4. Puesta en Marcha Rápida (Entorno Local Docker)

### Requisitos Previos
- Docker Desktop 4.x+ con soporte de Docker Compose v2.
- PowerShell 7+ (Windows) o Bash (Linux / macOS).

### Paso 1: Clonar y Crear el Árbol de Directorios
```powershell
# En Windows:
powershell -ExecutionPolicy Bypass -File .\setup-workspace.ps1

# En Linux / macOS / WSL:
chmod +x setup-workspace.sh
./setup-workspace.sh
```

### Paso 2: Configurar Variables de Entorno
```powershell
copy .env.example .env
```

### Paso 3: Levantar Toda la Infraestructura y Microservicios
```bash
docker compose up -d
```

### Paso 4: Validar Estado de Contenedores
```bash
docker compose ps
```

---

## 🌐 5. Matriz de Puertos y Servicios Expuestos

| Servicio | Contenedor | Puerto Local | Tecnología / Rol |
|---|---|---|---|
| **Keycloak SSO** | `aegiscore-keycloak-sso` | `8080` | OAuth 2.0 / OIDC (Reino `aegiscore`) |
| **MS1 Pólizas** | `aegiscore-ms1-polizas-php` | `8001` | PHP 8.3 / Laravel DDD (`/health`, `/graphql`) |
| **MS2 Siniestros** | `aegiscore-ms2-siniestros-nestjs` | `8002` | NestJS Clean Arch + CQRS (`/health`, `/api/siniestros/demo`) |
| **MS3 Actuarial** | `aegiscore-ms3-actuarial-springboot` | `8003` | Java 21 Spring Boot Hexagonal (`/health`, `/api/actuarial/saga-status`) |
| **MS4 IA & MCP** | `aegiscore-ms4-ia-mcp-python` | `8004` | FastAPI + ML + TensorFlow + MCP (`/health`, `/docs`) |
| **PostgreSQL** | `aegiscore-postgres-erp` | `5432` | Relacional ACID (`aegiscore_erp`) |
| **MongoDB** | `aegiscore-mongo-siniestros` | `27017` | NoSQL Documental (`aegiscore_siniestros`) |
| **DynamoDB Local** | `aegiscore-dynamodb-local` | `8000` | NoSQL Clave-Valor (`IdempotencyRecords`) |
| **Apache Kafka** | `aegiscore-kafka` | `9092` | Event Broker para Saga |
| **Zookeeper** | `aegiscore-zookeeper` | `2181` | Coordinador de Kafka |
| **n8n Automation** | `aegiscore-n8n` | `5678` | Workflows WhatsApp y Facturación |

---

## 🧪 6. Verificación de Bases de Datos Políglotas

### PostgreSQL 16 (Verificar tablas y dataset sintético para Random Forest):
```bash
docker exec -it aegiscore-postgres-erp psql -U aegis_admin -d aegiscore_erp -c "\dt"
docker exec -it aegiscore-postgres-erp psql -U aegis_admin -d aegiscore_erp -c "SELECT count(*) FROM dataset_historico_ml_polizas;"
```
*(Debe retornar 1,200 registros generados para el entrenamiento del modelo predictivo).*

### MongoDB 7 (Verificar expedientes de siniestros e índices geoespaciales):
```bash
docker exec -it aegiscore-mongo-siniestros mongosh aegiscore_siniestros --eval "db.expedientes_siniestros.find().pretty()"
```

### Amazon DynamoDB Local (Verificar tablas y registro idempotente):
```bash
# Con AWS CLI local:
aws dynamodb list-tables --endpoint-url http://localhost:8000 --region us-east-1
```

---

## 🛡️ 7. Seguridad OWASP en el Servidor MCP (CU15)

Para neutralizar cualquier intento de **Inyección SQL por Voz**, el sistema implementa una arquitectura multicapa:
1. **Whisper STT** convierte el audio del usuario a texto.
2. **OWASP Prompt Sanitizer Guard** detecta y aborta cualquier comando malicioso (`DROP`, `DELETE`, `UNION SELECT`, `--`, `OR 1=1`).
3. El LLM **nunca interactúa directamente con la base de datos**; solo puede seleccionar Tools tipadas bajo el protocolo **Model Context Protocol (MCP)** con esquemas JSON rígidos.
4. Las Tools MCP ejecutan consultas a réplicas analíticas mediante **ORMs parametrizados**, garantizando 100% de inmunidad ante inyecciones.
