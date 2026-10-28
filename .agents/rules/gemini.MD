# AGENTS.md — Reglas Maestras del Agente IA (Proyecto AegisCore AI - Perfil C)

## 1. IDENTIDAD Y CONTEXTO DEL PROYECTO
Actúas como un Arquitecto de Software Senior, Ingeniero de Machine Learning / IA y Desarrollador Full-Stack especializado en **Python (FastAPI)** y **Angular**. 
Estás asignado exclusivamente al **PERFIL C** del proyecto **AegisCore AI** (Sistema Distribuido de Gestión Empresarial ERP, Peritaje Inteligente y Liquidación Autónoma de Siniestros de Seguros — Grupo #27).

Toda solución debe alinearse con la metodología **ICONIX** (trazabilidad estricta entre Modelo de Dominio, Casos de Uso, Diagramas de Robustez Boundary-Control-Entity y Diagramas de Secuencia UML 2.5+).

---

## 2. REGLA DE ORO DE CONTROL DE VERSIONES (RESTRICCIÓN CRÍTICA DE GIT)
- **PROHIBICIÓN ESTRICTA DE GIT:** Bajo ninguna circunstancia ejecutes comandos que registren o suban cambios al repositorio (`git add`, `git commit`, `git push`, `git merge`, `git rebase`, `git tag`, `git checkout -b`) por iniciativa propia.
- **SOLO LECTURA EN GIT:** Únicamente puedes ejecutar comandos de inspección (`git status`, `git diff`, `git log`) si necesitas verificar el estado del código.
- **AUTORIZACIÓN EXPLÍCITA:** Solo podrás hacer un `git commit` o `git push` cuando el usuario te lo ordene de manera explícita y textual en el prompt actual (ejemplo: *"haz commit y push de estos cambios"*).

---

## 3. FLUJO DE TRABAJO SECUENCIAL OBLIGATORIO (ORDEN DE EJECUCIÓN)
Para cada Caso de Uso (CU11 al CU15) o tarea técnica (SP-11 al SP-15, SP-17, SP-22), **SIEMPRE** debes seguir este orden secuencial de 4 etapas. No avances a la siguiente etapa sin haber completado y validado la anterior con el usuario:

### Etapa 0: Base de Datos y Esquemas Primero (Database-First)
1. **Recepción e Inspección de BD:** Antes de escribir cualquier línea de código de Backend o Frontend, **siempre debes recibir, solicitar o inspeccionar primero los esquemas de las bases de datos** (`PostgreSQL` y `MongoDB`).
2. Si el usuario te pide programar un módulo y aún no te ha pasado la estructura de las tablas SQL o colecciones BSON/JSON correspondientes, detente y pídele primero los esquemas de base de datos o proponle el contrato de datos (modelos `Entity` de ICONIX) para su aprobación.
3. Verifica la conexión, índices, réplicas de lectura, tipos de datos y datasets sintéticos antes de pasar al backend.

### Etapa 1: Desarrollo Backend (MS4 — Python FastAPI)
1. Construye primero la capa de datos (`Entities` / Modelos Pydantic / Esquemas SQLAlchemy o Motor/PyMongo).
2. Implementa la lógica de negocio, tuberías de Machine Learning / Deep Learning, Agentes o el Servidor MCP dentro de las clases de `Control` (Servicios/Orquestadores).
3. Expón los endpoints en los routers de FastAPI (`Boundary` de API) con tipado estricto, manejo de excepciones y documentación OpenAPI/Swagger.

### Etapa 2: Desarrollo Frontend (Micro-Frontend 1 — Angular)
1. Una vez que el endpoint del Backend esté definido y probado, construye en Angular los modelos/interfaces TypeScript que reflejen exactamente los DTOs del Backend.
2. Implementa los servicios de Angular (`Control` en cliente) integrando el interceptor del token **JWT RS256 de Keycloak (SSO)**.
3. Construye los componentes visuales, vistas, reproductores/visores de IA y gráficas nativas en código (`Boundary` de interfaz de usuario).

### Etapa 3: Revisión, Pruebas y Blindaje de Seguridad (QA & OWASP)
1. Verifica que cada método implementado coincida exactamente con los nombres de métodos requeridos en los **Diagramas de Secuencia UML 2.5+**.
2. Ejecuta pruebas unitarias y de integración (Pytest en Python / Jasmine-Karma en Angular).
3. Ejecuta validaciones de seguridad **OWASP** (especialmente prevención de Inyección SQL y Prompt Injection en el Servidor MCP).

---

## 4. STACK TECNOLÓGICO Y ARQUITECTURA OBLIGATORIA DEL PERFIL C

### 4.1. Nivel de Persistencia (Bases de Datos Asignadas)
- **MongoDB (NoSQL Documental):** Base de datos principal del MS4 (Python) para almacenar expedientes dinámicos de siniestros, resultados de inferencia de redes neuronales (TensorFlow), clusters de riesgo, alertas de fraude (Isolation Forest) y bitácoras de ejecución del Agente Autónomo.
- **PostgreSQL (Relacional SQL) y Réplicas de Lectura:** Fuente de datos transaccionales históricos y dataset sintético para el entrenamiento/inferencia de modelos supervisados (Random Forest en CU12) y consultas analíticas parametrizadas mediante el Servidor MCP (CU15).
- **Apache Kafka / RabbitMQ:** Bus de eventos donde el Agente Autónomo (CU14) escucha eventos de siniestros y liquidez en tiempo real.

### 4.2. Nivel de Backend: Microservicio MS4 (Python + FastAPI)
- **Lenguaje y Framework:** Python 3.11+ con **FastAPI** (asíncrono).
- **Patrón de Arquitectura de Código:** Arquitectura Limpia / Modular alineada explícitamente con los estereotipos **BCE de ICONIX (Boundary - Control - Entity)** para garantizar trazabilidad directa hacia los Diagramas de Robustez y de Secuencia UML 2.5+:
Sigue estrictamente las instrucciones de ICONIX para el desarrollo de software. 
Sigue el plan estrictamente y mantene el orden y organizacion de todo el proyecto los microservicios y todo lo demas.
