# **PLAN MAESTRO DE DESARROLLO Y SELECCIÓN DE CASOS DE USO Y TAREAS**

**Proyecto:** AegisCore AI — Sistema Distribuido de Gestión Empresarial (ERP), Peritaje Inteligente y Liquidación Autónoma de Siniestros de Seguros  
Materia: Ingeniería de Software II (2do Parcial SW2) — Grupo \#27  
Metodología: ICONIX (Modelado de Dominio, Casos de Uso con Prototipos GUI, Diagramas de Robustez Boundary-Control-Entity y Diagramas de Secuencia en UML 2.5+)  
**Fecha Objetivo de Entrega Final:** 10 \- 12 de noviembre (Desarrollo iterativo en 4 semanas para 3 integrantes)

# **1\. RESUMEN DE LA ARQUITECTURA EN 4 NIVELES Y STACK TECNOLÓGICO OBLIGATORIO**

## **Nivel 1: Micro-Frontends, Clientes e IA Local (3 Frameworks \+ SSO)**

* **Acceso Único (SSO):** Keycloak con OAuth 2.0 / OpenID Connect (OIDC) y JWT RS256. Permite iniciar sesión una sola vez en una entrada unificada y navegar entre las 3 aplicaciones sin volver a autenticarse.  
* **Micro-Frontend 1 — Angular:** Portal ERP Administrativo, Visor de Peritajes IA, Consola de Reportes Generativos por Voz y Dashboard Estadístico Nativo en código con KPIs (sin Power BI).  
* **Micro-Frontend 2 — React (PWA):** Portal de Autoservicio y Cotización Comercial para asegurados con GraphQL, soporte Offline e IA Local en el navegador (TensorFlow.js / ONNX Runtime Web) para validar la nitidez de documentos antes de subirlos.  
* **Cliente 3 — Flutter / PWA (App Móvil Peritos):** Aplicación móvil que utiliza hardware nativo (Cámara, GPS, Micrófono, Lector QR), opera 100% Offline con base de datos local SQLite e incorpora un Agente Funcional con IA Local (TensorFlow Lite) para detectar daños vehiculares sin conexión a internet.

## **Nivel 2: Microservicios Backend (4 Microservicios, 4 Lenguajes, 3 Arquitecturas de Código)**

* **MS1 — Core ERP de Pólizas, Clientes y Facturación:** Lenguaje PHP 8.3 (Laravel) \| Patrón: DDD (Domain-Driven Design) \| API: GraphQL. Gestiona clientes, planes de seguro, coberturas, emisión de pólizas y facturas/notas de venta.  
  \|---\|reclamos viales y médicos, expedientes multimedia y sincronización offline idempotente.  
* **MS3 — Motor Actuarial, Cobranzas y Orquestador Saga:** Lenguaje Java (Spring Boot 3\) \| Patrón: Arquitectura Hexagonal (Ports & Adapters). Gestiona cálculos actuariales, reservas técnicas, cobro de primas por QR y coordina la Transacción Transversal Saga en 3 microservicios con compensación/rollback.  
* **MS4 — Inteligencia Artificial, Deep Learning, Agentes y Servidor MCP:** Lenguaje Python (FastAPI) \| Librerías: Scikit-Learn (Random Forest, K-Means, Isolation Forest), TensorFlow/Keras (Visión Artificial para imágenes y videos de choques), LangGraph (Agentes Autónomos con Metas y Skills), Whisper STT y Servidor con Protocolo MCP (Model Context Protocol) con blindaje OWASP contra Inyección SQL por voz.

## **Nivel 3: Persistencia Políglota (3 Motores de Bases de Datos)**

* **PostgreSQL (Relacional SQL):** Conectado a MS1 (PHP) y MS3 (Spring Boot) para datos transaccionales ACID (usuarios, clientes, pólizas, coberturas, facturas, cobros y liquidaciones).  
* **MongoDB (NoSQL Documental):** Conectado a MS2 (NestJS) y MS4 (Python) para expedientes dinámicos de siniestros, resultados de redes neuronales TensorFlow y bitácoras de agentes.  
* **Amazon DynamoDB (NoSQL Clave-Valor):** Conectado transversalmente para almacenar las llaves de idempotencia (Idempotency-Keys) con latencia sub-milisegundo, evitando registros o cobros duplicados cuando la app móvil o web sincroniza con mala señal de internet.

## **Nivel 4: Gateway, Orquestación y Automatización**

* **Apollo GraphQL Router / API Gateway:** Punto de entrada unificado para subgrafos GraphQL y rutas REST.  
* **n8n (Automatización Multicanal):** Conecta WhatsApp \+ Core ERP \+ Servicio de Facturación/Correo (pedidos de pólizas por WhatsApp a factura PDF y reporte de siniestros por WhatsApp).  
* **Apache Kafka / RabbitMQ:** Bus de eventos para el Patrón Saga y monitoreo autónomo de agentes.

# **2\. MODALIDAD DE SELECCIÓN PARA LOS 3 INTEGRANTES (PAQUETES EQUILIBRADOS)**

Para trabajar de manera independiente sin bloquearse y luego unir todo mediante contratos estándar, el proyecto se divide en 3 Células Verticales (Perfiles A, B y C). Cada integrante puede elegir un Perfil completo (5 Casos de Uso y 8 Tareas del Sprint Backlog) o acordar intercambios equivalentes:

* **PERFIL / OPCIÓN A (Enfoque Core Comercial, SSO, Web React & Automatización n8n — 42 Puntos / 26 Horas):**  
  * **Casos de Uso:** CU01, CU02, CU03, CU04 y CU05.  
  * **Componentes a cargo:** Keycloak SSO, MS1 en PHP 8.3 (DDD \+ GraphQL), PostgreSQL (Esquema Comercial), Micro-Frontend React PWA (con IA Local Web ONNX/TF.js) y Flujos en n8n (WhatsApp a ERP y Factura).  
* **PERFIL / OPCIÓN B (Enfoque Siniestros, Móvil Offline, Idempotencia & Transacción Saga — 44 Puntos / 29 Horas):**   
  * **Casos de Uso:** CU06, CU07, CU08, CU09 y CU10.  
  * **Componentes a cargo:** MS2 en NestJS (Clean Architecture \+ MongoDB \+ Push), MS3 en Java Spring Boot 3 (Arquitectura Hexagonal \+ Orquestador Saga en 3 Microservicios), Amazon DynamoDB (Idempotency-Key) y App Móvil Flutter (SQLite Offline \+ Agente IA Local TensorFlow Lite \+ GPS/Cámara/QR).  
* **PERFIL / OPCIÓN C (Enfoque IA, Deep Learning TensorFlow, Agentes, Protocolo MCP & Angular BI — 43 Puntos / 28 Horas):**  
  * **Casos de Uso:** CU11, CU12, CU13, CU14 y CU15.  
  * **Componentes a cargo:** MS4 en Python FastAPI, Modelos ML Supervisado (Random Forest) y No Supervisado (K-Means \+ Isolation Forest), Deep Learning con TensorFlow (imágenes/video), Agente Autónomo (Goals & Skills), Servidor MCP para Reportes por Voz (Excel, PDF, Word) con blindaje Anti-SQLi y Micro-Frontend Angular (ERP Admin \+ Dashboards KPIs en código).

# **3\. TABLA MAESTRA DE CASOS DE USO PARA ESCOGER (CU01 AL CU15)**

| ID | Caso de Uso | Microservicio / Backend | Frontend / Canal | Base de Datos | Tecnología Impuesta Aplicada | Puntos | Horas Est. | Responsable |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **CU01** | Iniciar Sesión Único Multi-Aplicación (SSO) | Keycloak OIDC \+ Gateway | Angular, React, Flutter | PostgreSQL \+ DynamoDB | Inicio de Sesión Único (SSO) en los 3 Frontends | 8 pts | 5 hrs | Person |
| **CU02** | Consultar Estado Unificado de Pólizas, Vehículos y Siniestros | Gateway GraphQL (MS1 \+ MS2) | React (Apollo Client) | PostgreSQL, MongoDB, DynamoDB | Federación GraphQL \+ Agregación Nivel 3 | 8 pts | 5 hrs | Person |
| **CU03** | Gestionar Catálogo de Planes de Seguro, Coberturas y Clientes | MS1: PHP 8.3 (Patrón DDD) | Angular | PostgreSQL | Lenguaje PHP \+ Arquitectura DDD \+ GraphQL con FK | 8 pts | 5 hrs | Person |
| **CU04** | Cotizar y Emitir Póliza en Línea con Validación por IA Local Web | MS1: PHP 8.3 (DDD \+ GraphQL) | React PWA (TF.js / ONNX Web) | PostgreSQL | Front Web con IA Local \+ Funcionamiento Offline \+ GraphQL | 10 pts | 6 hrs | Person |
| **CU05** | Contratar / Renovar Póliza por WhatsApp y Emitir Factura PDF | n8n \+ MS1: PHP | WhatsApp API \+ Correo SMTP | PostgreSQL | Automatización n8n (Pedidos WhatsApp \-\> ERP \-\> Factura PDF) | 8 pts | 5 hrs | Person |
| **CU06** | Reportar Siniestro Vial de Emergencia por WhatsApp con Triaje IA | MS2: NestJS (Clean Arch) \+ n8n | WhatsApp \+ Push Móvil | MongoDB | Lenguaje NestJS \+ Clean Architecture \+ MongoDB \+ Push | 8 pts | 5 hrs | Person |
| **CU07** | Inspeccionar Daños del Vehículo Offline con Agente de IA Local | Edge AI en Dispositivo Móvil | Flutter (Cámara, GPS, Micrófono) | SQLite (Local en Móvil) | App Móvil Offline (SQLite) \+ Agente Funcional IA Local (TFLite) | 10 pts | 7 hrs | Person |
| **CU08** | Sincronizar Expediente de Siniestro con Control de Idempotencia | MS2: NestJS (Clean Arch) | Flutter (Background Sync) | Amazon DynamoDB \+ MongoDB | Mecanismo de Idempotencia (Idempotency-Key) con Mala Señal | 8 pts | 5 hrs | Person |
| **CU09** | Liquidar y Pagar Indemnización de Siniestro (Patrón Saga) | MS3: Java Spring Boot (Hexagonal) \+ MS1 \+ MS2 | Angular \+ Kafka | PostgreSQL \+ MongoDB | Transacción Transversal en 3 Microservicios (Saga \+ Rollback) | 10 pts | 7 hrs | Person |
| **CU10** | Procesar Cobro Recurrente de Primas y Pago QR Idempotente | MS3: Java Spring Boot (Hexagonal) | React / Flutter (Lector QR) | PostgreSQL \+ DynamoDB | Java Spring Boot \+ Arquitectura Hexagonal \+ Idempotencia Pagos | 8 pts | 5 hrs | Person |
| **CU11** | Analizar Fotografía/Video de Siniestro con Deep Learning | MS4: Python FastAPI (TensorFlow) | Angular (Visor Peritaje IA) | MongoDB | Deep Learning con TensorFlow (Procesamiento Imagen y Video) | 9 pts | 6 hrs | Person |
| **CU12** | Predecir Siniestralidad, Ventas de Pólizas y Prima Óptima | MS4: Python (Scikit-Learn) | Angular (Dashboard KPIs en código) | PostgreSQL / Dataset Sintético | ML Supervisado (Random Forest) \+ Dashboard Nativo con KPIs | 8 pts | 5 hrs | Person |
| **CU13** | Segmentar Asegurados por Riesgo y Detectar Fraudes | MS4: Python (Scikit-Learn) | Angular | MongoDB | ML No Supervisado (K-Means \+ Isolation Forest) | 8 pts | 5 hrs | Person |
| **CU14** | Monitorear Siniestros Estancados y Liquidez con Agente Autónomo | MS4: Python (LangGraph \+ Kafka) | Monitor en Angular | MongoDB | Agentes Inteligentes Funcionales (Metas y Skills) | 8 pts | 5 hrs | Person |
| **CU15** | Generar Reportes Dinámicos por Voz mediante Protocolo MCP | MS4: Python (MCP Server \+ Whisper) | Angular / Flutter (Micrófono) | Réplicas PostgreSQL y MongoDB | Protocolo MCP \+ Reportes por Voz (Excel, PDF, Word) \+ Anti-SQLi | 10 pts | 7 hrs | Person |

# **4\. TABLA DE TAREAS DEL SPRINT BACKLOG (SP-01 AL SP-24)**

## **Semana 1: Infraestructura, Contratos y Diseño Preliminar ICONIX**

| Código | Descripción de la Tarea Técnica | Relacionado a | Prioridad | Puntos | Horas | Responsable |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **SP-01** | Configurar `docker-compose.yml` con PostgreSQL, MongoDB, DynamoDB Local, Kafka, Keycloak y n8n | Transversal | Alta | 8 pts | 4 hrs | Todo el equipo |
| **SP-02** | Elaborar Modelo de Dominio, Requisitos (RF01-RF07) y Prototipos GUI de ICONIX | CU01-CU15 | Alta | 8 pts | 4 hrs | Todo el equipo |
| **SP-03** | Crear script físico SQL en PostgreSQL (Pólizas, Clientes, Facturas, Liquidación) y poblar dataset sintético histórico | CU03, CU09, CU12 | Alta | 8 pts | 4 hrs | Perfil A |
| **SP-04** | Configurar colecciones en MongoDB (Siniestros) y tabla `IdempotencyRecords` en Amazon DynamoDB | CU06, CU08, CU10 | Alta | 7 pts | 3 hrs | Perfil B |
| **SP-05** | Configurar reino de Keycloak SSO (OAuth2/OIDC) para login único entre Angular, React y Flutter | CU01 | Alta | 8 pts | 4 hrs | Perfil A |

## **Semana 2: Desarrollo de Microservicios Backend y Patrones de Código**

| Código | Descripción de la Tarea Técnica | Relacionado a | Prioridad | Puntos | Horas | Responsable |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **SP-06** | Implementar MS1 en PHP 8.3 (Laravel) bajo patrón DDD con queries y mutaciones GraphQL | CU02, CU03, CU04 | Alta | 10 pts | 6 hrs | Perfil A |
| **SP-07** | Implementar MS2 en NestJS bajo Clean Architecture \+ CQRS conectado a MongoDB y Notificaciones Push | CU06, CU08 | Alta | 9 pts | 5 hrs | Perfil B |
| **SP-08** | Programar interceptor de Idempotencia (`Idempotency-Key`) contra Amazon DynamoDB en NestJS y Spring Boot | CU08, CU10 | Alta | 9 pts | 5 hrs | Perfil B |
| **SP-09** | Implementar MS3 en Java Spring Boot 3 bajo Arquitectura Hexagonal (Cálculo actuarial, reservas y pagos QR) | CU09, CU10 | Alta | 9 pts | 6 hrs | Perfil B |
| **SP-10** | Programar Orquestador del Patrón Saga (MS3 Spring Boot \+ MS1 PHP \+ MS2 NestJS) y compensación/rollback en Kafka | CU09 | Alta | 10 pts | 6 hrs | Perfil B (apoyo Perfil A) |

## **Semana 3: Inteligencia Artificial, MCP, Automatización n8n y Micro-Frontends**

| Código | Descripción de la Tarea Técnica | Relacionado a | Prioridad | Puntos | Horas | Responsable |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **SP-11** | Entrenar e integrar modelo Random Forest (ML Supervisado para predicción de ventas y primas) en MS4 Python | CU12 | Alta | 8 pts | 4 hrs | Perfil C |
| **SP-12** | Entrenar e integrar K-Means (segmentación) e Isolation Forest (detección de fraude) en MS4 Python | CU13 | Alta | 8 pts | 4 hrs | Perfil C |
| **SP-13** | Implementar red neuronal en TensorFlow / Keras para detección de daños en fotos/videos de choques en MS4 Python | CU11 | Alta | 9 pts | 5 hrs | Perfil C |
| **SP-14** | Construir Servidor MCP en Python \+ Whisper STT \+ blindaje OWASP Anti-SQLi \+ exportación a Excel, PDF y Word | CU15 | Alta | 10 pts | 6 hrs | Perfil C |
| **SP-15** | Programar Agente Autónomo de Monitoreo con Goals & Skills en Python escuchando eventos Kafka | CU14 | Media | 8 pts | 4 hrs | Perfil C |
| **SP-16** | Crear flujos en n8n: Pedido de póliza por WhatsApp \-\> ERP PHP \-\> Factura PDF al correo/WhatsApp, y Siniestro Vial | CU05, CU06 | Alta | 9 pts | 5 hrs | Perfil A |
| **SP-17** | Desarrollar Micro-Frontend 1 en Angular: Panel Admin ERP, Visor IA, Consola de Voz MCP y Dashboard nativo con KPIs | CU03, CU09, CU11-15 | Alta | 9 pts | 6 hrs | Perfil C |
| **SP-18** | Desarrollar Micro-Frontend 2 en React (PWA): Cotizador GraphQL e IA Local Web (ONNX/TF.js) para validar nitidez offline | CU02, CU04, CU10 | Alta | 9 pts | 5 hrs | Perfil A |
| **SP-19** | Desarrollar App Móvil en Flutter: Modo Offline con SQLite, cámara/GPS/QR y Agente IA Local (TensorFlow Lite) | CU07, CU08, CU10 | Alta | 10 pts | 6 hrs | Perfil B |

## **Semana 4: Modelado Detallado UML 2.5+, Pruebas de Resiliencia y Despliegue Cloud**

| Código | Descripción de la Tarea Técnica | Relacionado a | Prioridad | Puntos | Horas | Responsable |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **SP-20** | Elaborar los 15 Diagramas de Robustez (Boundary, Control, Entity) y 15 Diagramas de Secuencia en UML 2.5+ | CU01-CU15 | Alta | 9 pts | 6 hrs | Cada integrante (5 CUs) |
| **SP-21** | Pruebas de corte de red (Offline/Idempotencia en DynamoDB) y prueba de fallo/compensación de la Saga en 3 microservicios | CU08, CU09 | Alta | 8 pts | 4 hrs | Todo el equipo |
| **SP-22** | Pruebas de seguridad OWASP (intento de Inyección SQL por comando de voz neutralizado por el Servidor MCP) | CU15 | Alta | 7 pts | 3 hrs | Perfil C |
| **SP-23** | Despliegue distribuido en contenedores Docker y Kubernetes en proveedores Cloud (AWS, GCP, Azure, Railway/Render) | Todos | Alta | 9 pts | 5 hrs | Todo el equipo |
| **SP-24** | Ensamblaje del Documento Final ICONIX y ensayo de defensa para el 10 \- 12 de noviembre | Todos | Alta | 8 pts | 4 hrs | Todo el equipo |

# **5\. ESTRATEGIA DE UNIÓN E INTEGRACIÓN Y CRITERIOS DE TERMINADO (DEFINITION OF DONE)**

## **Reglas para Desarrollar por Separado y Unir sin Conflictos**

1. **Repositorios Independientes \+ Orquestador Docker:** Cada integrante trabaja en su propio repositorio de microservicio/frontend y expone sus puertos en el archivo `docker-compose.yml` compartido.  
2. **Contratos Congelados en Semana 1:** Se respetan estrictamente los esquemas de GraphQL, la cabecera `Idempotency-Key` (UUIDv4), el formato JSON del evento Saga en Kafka y el token JWT emitido por Keycloak.

## **Entregables Obligatorios por cada Caso de Uso Escogido (ICONIX \+ UML 2.5+)**

Cada compañero es responsable de principio a fin de los 5 Casos de Uso que elija, debiendo entregar:

1. Especificación del Caso de Uso y Prototipo de Interfaz (GUI).  
2. Diagrama de Robustez ICONIX: Conectando explícitamente los objetos Boundary (Vista), Control (Servicio/Controlador) y Entity (Tabla/Colección).  
3. Diagrama de Secuencia y Comunicación en UML 2.5+: Reflejando los mensajes y nombres exactos de los métodos operacionales en la clase de control (validarNitidez(), verificarIdempotencyKey(), insertarPoliza(), compensarCoberturaSaga()).  
4. Código Funcional Desplegado: Endpoint y vista funcionando e integrados en el contenedor Docker/Kubernetes.

