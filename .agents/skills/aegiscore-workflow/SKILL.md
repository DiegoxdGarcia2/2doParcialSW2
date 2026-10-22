---
name: aegiscore-workflow
description: >-
  Guía operativa y procedimientos para agentes y desarrolladores de AegisCore AI:
  arranque de docker-compose, verificación de persistencia políglota, ejecución
  de pruebas por microservicio, verificación de contratos y flujo de trabajo colaborativo.
---

# 🛠️ Skill: Flujo de Trabajo y Operaciones en AegisCore AI

Esta skill proporciona las instrucciones paso a paso para que cualquier agente o desarrollador pueda operar, extender y verificar el monorepo sin romper contratos ni alterar la arquitectura en 4 niveles.

---

## 1. Comandos de Arranque y Verificación de Infraestructura

### Levantar Todo el Ecosistema:
```bash
docker compose up -d
```

### Comprobar Estado de Servicios:
```bash
docker compose ps
```

### Puertos de Acceso Rápido:
- **Keycloak SSO:** `http://localhost:8080` (admin / Admin123*)
- **MS1 PHP:** `http://localhost:8001/health`
- **MS2 NestJS:** `http://localhost:8002/health`
- **MS3 Spring Boot:** `http://localhost:8003/health`
- **MS4 Python / FastAPI Docs:** `http://localhost:8004/docs`
- **n8n:** `http://localhost:5678`

---

## 2. Verificación de Persistencia Políglota

### PostgreSQL 16:
```bash
# Entrar a la base relacional
docker exec -it aegiscore-postgres-erp psql -U aegis_admin -d aegiscore_erp

# Validar dataset sintético para Random Forest (debe retornar 1200)
SELECT count(*) FROM dataset_historico_ml_polizas;
```

### MongoDB 7:
```bash
# Validar expedientes de siniestros
docker exec -it aegiscore-mongo-siniestros mongosh aegiscore_siniestros --eval "db.expedientes_siniestros.find().pretty()"
```

### DynamoDB Local:
```bash
aws dynamodb list-tables --endpoint-url http://localhost:8000 --region us-east-1
```

---

## 3. Guía de Desarrollo por Microservicio

### MS1: PHP 8.3 / Laravel (DDD)
- Directorio: `backend/ms1-polizas-php`
- Todo nuevo modelo de negocio debe iniciar en `src/Domain/` antes de tocar la base de datos o controladores.
- Respetar los Value Objects para montos y vigencias.
- Las consultas se exponen mediante **GraphQL** según `contracts/supergraph.graphql`.

### MS2: NestJS 10 (Clean Architecture + CQRS)
- Directorio: `backend/ms2-siniestros-nestjs`
- Separar cada caso de uso en `src/application/use-cases/commands/` o `queries/`.
- Usar el decorador/guard de idempotencia antes de guardar en MongoDB.
- Publicar eventos en Kafka al cambiar el estado del siniestro a `EN_PROCESO_LIQUIDACION`.

### MS3: Spring Boot 3 (Arquitectura Hexagonal)
- Directorio: `backend/ms3-actuarial-springboot`
- Mantener `domain/` libre de anotaciones de Spring o JPA.
- Los casos de uso se implementan como puertos en `application/ports/in/`.
- El orquestador Saga coordina el flujo transaccional y escucha compensaciones en `aegiscore.saga.compensations`.

### MS4: Python 3.11 / FastAPI (IA, Agentes y MCP)
- Directorio: `backend/ms4-ia-mcp-python`
- Modelos supervisados en `app/ml_supervised/`.
- Detección de fraude en `app/ml_unsupervised/`.
- Deep Learning con TensorFlow en `app/dl_tensorflow/`.
- Servidor MCP en `app/mcp_voice_reports/` asegurando el blindaje OWASP contra inyección SQL.

---

## 4. Reglas de Git y Colaboración
1. No modificar unilateralmente `contracts/`.
2. No hacer commit de credenciales ni archivos `.env`.
3. Mantener actualizado el registro en `documentacion_obsidian/` y sincronizar con `python "C:\Users\PERSONAL\.gemini\config\scripts\obsidian_manager.py" sync`.
