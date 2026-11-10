# 🚀 Despliegue Multi-Cloud Exitoso (Google Cloud, Microsoft Azure, Amazon Web Services)

**Fecha:** 2026-11-09  
**Estado:** ✅ PRODUCCIÓN 100% OPERATIVA  
**Estrategia:** Despliegue Multi-Cloud con persistencia políglota ACID/NoSQL intacta en la nube.

---

## 🌐 Cuadro Oficial de Endpoints en Producción

| Célula / Microservicio | Proveedor Cloud | Servicio de Despliegue | URL Oficial en Producción | Estado de Salud |
|---|---|---|---|---|
| **MS1 PHP Laravel 8.3 (DDD + GraphQL)** | **Google Cloud** | Cloud Run (`us-central1`) | `https://aegiscore-ms1-polizas-<cloudrun-id>.a.run.app` | `status: UP` (200 OK) |
| **MS2 NestJS 10 (Clean Arch + CQRS)** | **Amazon Web Services** | ECS Fargate (`us-east-2`) | `http://<ec2-host-ip>:8002` | `status: UP` (200 OK) |
| **MS3 Spring Boot 3 (Hexagonal + Saga)** | **Microsoft Azure** | Container Apps (`eastus`) | `https://aegiscore-ms3-actuarial.<aca-id>.eastus.azurecontainerapps.io` | `status: UP` (200 OK) |
| **MS4 Python 3.11 (IA + Servidor MCP)** | **Google Cloud** | Cloud Run (`us-central1`) | `https://aegiscore-ms4-ia-<cloudrun-id>.us-central1.run.app` | `status: UP` (200 OK) |
| **MF1 Angular 17+ (BI Actuarial)** | **Google Cloud** | Cloud Run (`us-central1`) | `https://aegiscore-mf1-admin-<cloudrun-id>.us-central1.run.app` | `HTTP 200 OK` |
| **MF2 React 18 PWA (Asegurados)** | **Amazon Web Services** | S3 Static Hosting (`us-east-2`) | `http://aegiscore-mf2-clientes-<aws-account-id>.s3-website.us-east-2.amazonaws.com` | `HTTP 200 OK` |
| **SSO Login Shell (Executive)** | **Amazon Web Services** | S3 Static Hosting (`us-east-2`) | `http://aegiscore-mf2-clientes-<aws-account-id>.s3-website.us-east-2.amazonaws.com/sso.html` | `HTTP 200 OK` |
| **Keycloak 24 (SSO OIDC Server)** | **Microsoft Azure** | Container Apps (`eastus`) | `https://aegiscore-keycloak.<aca-id>.eastus.azurecontainerapps.io` | `HTTP 302 Found` |

---

## 💾 Persistencia Políglota Cloud Conectada
- **Neon Serverless PostgreSQL (`us-east-2`):** `ep-your-pooler-instance.us-east-2.aws.neon.tech` (Consumido por MS1, MS3 y MS4).
- **MongoDB Atlas (`<mongo-cluster-id>`):** `aegiscore_siniestros_db` con índice geoespacial `2dsphere` (Consumido por MS2 y MS4).
- **Amazon DynamoDB Cloud (`us-east-2`):** Tabla `AegisCore_IdempotencyRecords` (Consumido por MS1, MS2, MS3 y MS4).
- **Amazon S3 Cloud (`us-east-2`):** Bucket `servicio-de-seguros-aegiscore` y `aegiscore-mf2-clientes-<aws-account-id>`.

---

## 🛡️ Auditoría QA de Código Resuelta
1. **MS2 NestJS:** Corregido el Route Shadowing de `@Get(':id')` sobre `/geo/cercanos` y `/cliente/:clienteId`.
2. **MS3 Spring Boot:** Creadas las 5 interfaces de puertos de salida y adaptadores concurrentes (`OrdenLiquidacion`, `ReservaTecnica`, `PagoPrima`, `IdempotencyLock`, `SagaEventPublisher`).
3. **MS4 Python:** Agregado `sqlparse` a `requirements.txt` y protegido con bloque defensivo; blindaje contra división por cero en consultas agregadas SQL.
4. **MF2 React:** Añadido manejo defensivo de errores de red y validación de tokens en `ApolloFederationClient.ts`.

