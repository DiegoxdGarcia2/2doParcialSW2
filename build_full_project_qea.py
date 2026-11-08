# -*- coding: utf-8 -*-
"""
Constructor Maestro del Modelo de Proyecto Completo (.qea) para Enterprise Architect 17.2
Proyecto: AegisCore AI — ERP Distribuido, Peritaje Inteligente y Liquidación Autónoma de Siniestros
Genera:
  - 30 Diagramas Completos (Home Page con NavigationCells, Casos de Uso Generales y por Módulo,
    Robustez BCE amplios, Secuencia UML 2.5+ con métodos en Control, Dominio con Clases Rectangulares
    y Atributos/Operaciones sin círculos gigantes, y Componentes en 4 Niveles).
  - Ningún diagrama vacío.
  - Cero solapamiento de elementos (coordenadas calculadas y separadas).
  - Enlaces nativos completos con DUID, SOID, EOID y mensajes de secuencia síncronos con PtStartX/PtEndX.
"""
import sqlite3
import shutil
import uuid
import os

def get_guid():
    return f"{{{uuid.uuid4()}}}".upper()

def get_duid():
    return uuid.uuid4().hex[:8].upper()

def build_qea():
    base_template = r"C:\Program Files\Sparx Systems\EA Trial\EABase.qea"
    target_qea = "AegisCore_AI.qea"

    shutil.copy(base_template, target_qea)
    print(f"Copiado base EABase.qea a {target_qea}")

    conn = sqlite3.connect(target_qea)
    cur = conn.cursor()

    # 1. Crear Paquete Raíz del Modelo
    root_model_pkg_id = 2
    cur.execute("""
        INSERT INTO t_package (Package_ID, Name, Parent_ID, ea_guid)
        VALUES (2, 'EA_Model_AegisCore_AI', 1, ?)
    """, (get_guid(),))

    cur.execute("""
        INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid)
        VALUES (1, 1, 'Package', 'EA_Model_AegisCore_AI', ?)
    """, (get_guid(),))

    # 2. Paquetes Principales del Sistema
    packages = [
        (3, '01_Modulo_Comercial_SSO_Polizas', root_model_pkg_id),
        (4, '02_Modulo_Siniestros_Movil_Saga', root_model_pkg_id),
        (5, '03_Modulo_IA_Agentes_MCP_BI', root_model_pkg_id),
        (6, '04_Modelo_Dominio_Global', root_model_pkg_id),
        (7, '05_Arquitectura_Componentes_Global', root_model_pkg_id)
    ]
    for pid, pname, parent in packages:
        cur.execute("INSERT INTO t_package (Package_ID, Name, Parent_ID, ea_guid) VALUES (?, ?, ?, ?)", (pid, pname, parent, get_guid()))
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid) VALUES (?, ?, 'Package', ?, ?)", (pid, parent, pname, get_guid()))

    # 3. Actores Globales del Sistema (IDs 10 to 17)
    actors = [
        (10, 'Cliente Asegurado'),
        (11, 'Perito de Campo'),
        (12, 'Ajustador de Siniestros'),
        (13, 'Auditor de Riesgos y Analista BI'),
        (14, 'Director Comercial y Finanzas'),
        (15, 'Broker Apache Kafka'),
        (16, 'Bot WhatsApp y Servidor MCP'),
        (17, 'Usuario')
    ]
    for aid, aname in actors:
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid) VALUES (?, 2, 'Actor', ?, ?)", (aid, aname, get_guid()))

    # 4. Todos los Casos de Uso (CU01 al CU15) (IDs 21 to 35)
    use_cases = [
        (21, 3, "CU01: Autenticación Centralizada SSO con Keycloak"),
        (22, 3, "CU02: Consulta Estado Unificado Asegurado en GraphQL"),
        (23, 3, "CU03: Administrar Catálogo Planes, Coberturas y Clientes"),
        (24, 3, "CU04: Cotización Web PWA con Validación IA Local"),
        (25, 3, "CU05: Automatización Pedido WhatsApp a Factura n8n"),
        (26, 4, "CU06: Reportar Siniestro SOS con Triaje Geoespacial"),
        (27, 4, "CU07: Inspeccionar Daños Offline en Campo con Edge AI"),
        (28, 4, "CU08: Sincronizar Expediente con Idempotencia DynamoDB"),
        (29, 4, "CU09: Liquidar Siniestro con Saga Transversal y Rollback"),
        (30, 4, "CU10: Procesar Cobro Recurrente y Pago QR Idempotente"),
        (31, 5, "CU11: Analizar Daños de Choques con CNN CrashNet"),
        (32, 5, "CU12: Predecir Ventas y Primas con Random Forest"),
        (33, 5, "CU13: Segmentar Riesgo K-Means y Detectar Fraude"),
        (34, 5, "CU14: Monitoreo Autónomo de Metas con LangGraph"),
        (35, 5, "CU15: Generar Reportes por Voz con Servidor MCP Anti-SQLi")
    ]
    for ucid, uc_pkg, ucname in use_cases:
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid) VALUES (?, ?, 'UseCase', ?, ?)", (ucid, uc_pkg, ucname, get_guid()))

    # 5. Clases BCE de Robustez y Secuencia (IDs 51 to 100)
    bce_classes = [
        # CU01
        (51, 3, "Class", "boundary", "LoginKeycloakSSOView"),
        (52, 3, "Class", "control", "KeycloakSSOControl"),
        (53, 3, "Class", "entity", "UsuarioSesionEntity"),
        # CU02
        (54, 3, "Class", "boundary", "PortalClientesGraphQLView"),
        (55, 3, "Class", "control", "ApolloSupergraphGatewayControl"),
        (56, 3, "Class", "entity", "ResumenUnificadoAseguradoEntity"),
        # CU04
        (57, 3, "Class", "boundary", "CotizadorWebPWAView"),
        (58, 3, "Class", "control", "ValidadorNitidezLocalWebControl"),
        (59, 3, "Class", "entity", "CotizacionPolizaEntity"),
        # CU05
        (60, 3, "Class", "boundary", "CanalWhatsAppWebhook"),
        (61, 3, "Class", "control", "OrquestadorWorkflowN8nControl"),
        (62, 3, "Class", "entity", "FacturaFiscalPDFEntity"),
        # CU06
        (63, 4, "Class", "boundary", "SiniestroSosMobileView"),
        (64, 4, "Class", "control", "SiniestroEmergencyControl"),
        (65, 4, "Class", "entity", "ExpedienteSiniestroEntity"),
        (66, 4, "Class", "entity", "PeritoGuardiaEntity"),
        # CU07
        (67, 4, "Class", "boundary", "CamaraPeritajeOfflineView"),
        (68, 4, "Class", "control", "PeritajeOfflineTFLiteControl"),
        (69, 4, "Class", "entity", "InspeccionOfflineSQLiteEntity"),
        (70, 4, "Class", "entity", "ModeloTFLiteQuantized"),
        # CU08
        (71, 4, "Class", "boundary", "ColaSincronizacionOfflineView"),
        (72, 4, "Class", "control", "SyncIdempotentControl"),
        (73, 4, "Class", "entity", "IdempotencyRecordEntity"),
        # CU09
        (74, 4, "Class", "boundary", "LiquidacionSiniestroAdminView"),
        (75, 4, "Class", "control", "SagaLiquidacionOrchestratorControl"),
        (76, 4, "Class", "control", "ReclamoEstadoControl_MS2"),
        (77, 4, "Class", "control", "PolizaCoberturaControl_MS1"),
        (78, 4, "Class", "entity", "SagaInstanceEntity"),
        (79, 4, "Class", "entity", "OrdenLiquidacionEntity"),
        (80, 4, "Class", "entity", "ContratoPolizaEntity"),
        # CU10
        (81, 4, "Class", "boundary", "CobroPrimaQRView"),
        (82, 4, "Class", "control", "PagoPrimaQRControl"),
        (83, 4, "Class", "entity", "TransaccionPagoQREntity"),
        # CU11
        (84, 5, "Class", "boundary", "VisionArtificialUploadView"),
        (85, 5, "Class", "control", "CrashNetVisionControl"),
        (86, 5, "Class", "entity", "ReporteInspeccionIAEntity"),
        # CU12
        (87, 5, "Class", "boundary", "PrediccionDemandaPrimasView"),
        (88, 5, "Class", "control", "RandomForestActuarialControl"),
        (89, 5, "Class", "entity", "DatasetHistoricoPolizasEntity"),
        # CU13
        (90, 5, "Class", "boundary", "SentinelFraudeView"),
        (91, 5, "Class", "control", "UnsupervisedFraudControl"),
        (92, 5, "Class", "entity", "ClusterAseguradoEntity"),
        (93, 5, "Class", "entity", "AlertaFraudeAnomaliaEntity"),
        # CU14
        (94, 5, "Class", "boundary", "AutonomousAgentMonitorView"),
        (95, 5, "Class", "control", "LangGraphAutonomousAgentControl"),
        (96, 5, "Class", "entity", "ClusterAgentStateEntity"),
        # CU15
        (97, 5, "Class", "boundary", "MicrofonoVoiceReportView"),
        (98, 5, "Class", "control", "VoiceMcpOwaspControl"),
        (99, 5, "Class", "control", "McpProtocolServer"),
        (100, 5, "Class", "entity", "ReporteEjecutivoDescargableEntity"),
        # Componentes Nivel 1 a 4 (IDs 101 to 109)
        (101, 7, "Component", "Nivel 1: Frontend", "App Móvil Flutter (SQLite + TFLite)"),
        (102, 7, "Component", "Nivel 1: Frontend", "Portal Clientes React PWA (ONNX Local)"),
        (103, 7, "Component", "Nivel 1: Frontend", "Panel Admin Angular 17+ (Dashboards BI)"),
        (104, 7, "Component", "Nivel 2: Backend", "MS1 Pólizas y Clientes PHP Laravel (DDD)"),
        (105, 7, "Component", "Nivel 2: Backend", "MS2 Siniestros y Triaje NestJS (Clean/CQRS)"),
        (106, 7, "Component", "Nivel 2: Backend", "MS3 Motor Actuarial Spring Boot (Hexagonal)"),
        (107, 7, "Component", "Nivel 2: Backend", "MS4 IA, Agentes y Servidor MCP FastAPI"),
        (108, 7, "Node", "Nivel 3: Persistencia", "Persistencia Políglota (PG, Mongo, DynamoDB, Redis)"),
        (109, 7, "Node", "Nivel 4: Mensajería", "Apache Kafka & Apollo Supergraph Router")
    ]
    for cid, cpkg, ctype, cstereo, cname in bce_classes:
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Stereotype, Name, ea_guid) VALUES (?, ?, ?, ?, ?, ?)", (cid, cpkg, ctype, cstereo, cname, get_guid()))

    # 5.1 Sistemas y Participantes Externos en Secuencias UML 2.5+ (IDs 220 to 228)
    ext_participants = [
        (220, 3, "Class", "system", "Servidor Keycloak"),
        (221, 3, "Class", "service", "MS1 Pólizas PHP (DDD)"),
        (222, 3, "Class", "storage", "Almacenamiento S3 / MinIO"),
        (223, 4, "Class", "service", "PushNotificationGateway"),
        (224, 4, "Class", "service", "Pasarela Bancaria BCB"),
        (225, 5, "Class", "ai_model", "CNN CrashNet (Keras/TensorFlow)"),
        (226, 5, "Class", "environment", "Entorno de Servicios / Despacho"),
        (227, 5, "Class", "ai_model", "Motor Whisper STT"),
        (228, 5, "Node", "database", "PostgreSQL 16 Engine")
    ]
    for cid, cpkg, ctype, cstereo, cname in ext_participants:
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Stereotype, Name, ea_guid) VALUES (?, ?, ?, ?, ?, ?)", (cid, cpkg, ctype, cstereo, cname, get_guid()))

    # 6. Clases Reales del Modelo de Dominio (IDs 201 to 212) — Estándar UML Rectangular (Sin círculos gigantes)
    domain_classes = [
        (201, 6, "Usuario", [
            ("usuarioId", "UUID"),
            ("email", "String"),
            ("nombreCompleto", "String"),
            ("rol", "String"),
            ("activo", "Boolean")
        ], ["iniciarSesion()", "cerrarSesion()"]),
        (202, 6, "Asegurado", [
            ("aseguradoId", "UUID"),
            ("carnetIdentidad", "String"),
            ("telefono", "String"),
            ("direccion", "String"),
            ("scoreCrediticio", "Float")
        ], ["consultarEstadoUnificado()"]),
        (203, 6, "Poliza", [
            ("polizaId", "UUID"),
            ("numeroPoliza", "String"),
            ("planTipo", "String"),
            ("fechaInicio", "DateTime"),
            ("fechaVencimiento", "DateTime"),
            ("primaMensualBOB", "Decimal"),
            ("limiteCoberturaBOB", "Decimal"),
            ("estado", "String")
        ], ["verificarVigencia()", "bloquearCobertura()", "compensarCobertura()"]),
        (204, 6, "VehiculoAsegurado", [
            ("vin", "String"),
            ("placa", "String"),
            ("marca", "String"),
            ("modelo", "String"),
            ("anio", "Integer"),
            ("valorComercialBOB", "Decimal")
        ], []),
        (205, 6, "Cotizacion", [
            ("cotizacionId", "UUID"),
            ("primaCalculadaBOB", "Decimal"),
            ("puntajeNitidezDoc", "Float"),
            ("documentoValido", "Boolean"),
            ("fechaCreacion", "DateTime")
        ], ["calcularTarifa()"]),
        (206, 6, "ExpedienteSiniestro", [
            ("siniestroId", "UUID"),
            ("codigoSiniestro", "String"),
            ("fechaHoraSiniestro", "DateTime"),
            ("latitud", "Float"),
            ("longitud", "Float"),
            ("nivelGravedad", "String"),
            ("estadoReclamo", "String"),
            ("costoEstimadoReparacion", "Decimal")
        ], ["registrarEmergencia()", "cambiarEstado()"]),
        (207, 6, "PeritajeInspeccion", [
            ("inspeccionId", "UUID"),
            ("peritoId", "UUID"),
            ("fechaPeritaje", "DateTime"),
            ("severidadIA", "String"),
            ("confianzaIA", "Float"),
            ("idempotencyKey", "String"),
            ("sincronizado", "Boolean")
        ], ["guardarInspeccionLocal()"]),
        (208, 6, "IdempotencyRecord", [
            ("idempotencyKey", "String"),
            ("payloadSha256", "String"),
            ("requestUri", "String"),
            ("status", "String"),
            ("responseCode", "Integer"),
            ("createdAt", "DateTime")
        ], ["validarReintento()"]),
        (209, 6, "SagaLiquidacion", [
            ("sagaId", "UUID"),
            ("siniestroId", "UUID"),
            ("polizaId", "UUID"),
            ("montoIndemnizarBOB", "Decimal"),
            ("estadoSaga", "String"),
            ("fechaInicio", "DateTime")
        ], ["avanzarPaso()", "ejecutarCompensacion()"]),
        (210, 6, "OrdenLiquidacion", [
            ("ordenId", "UUID"),
            ("codigoDesembolso", "String"),
            ("montoNetoBOB", "Decimal"),
            ("bancoDestino", "String"),
            ("estadoPago", "String")
        ], ["procesarDesembolso()"]),
        (211, 6, "TransaccionPagoQR", [
            ("transaccionId", "UUID"),
            ("codigoQR", "String"),
            ("importeBOB", "Decimal"),
            ("fechaExpiracion", "DateTime"),
            ("estadoPago", "String")
        ], ["generarQR()", "conciliarPago()"]),
        (212, 6, "FacturaFiscal", [
            ("facturaId", "UUID"),
            ("numeroFactura", "String"),
            ("nitCliente", "String"),
            ("totalBOB", "Decimal"),
            ("urlPdfS3", "String")
        ], ["emitirFacturaPDF()"])
    ]

    attr_counter = 1
    op_counter = 100
    for dc_id, dc_pkg, dc_name, attrs, ops in domain_classes:
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid) VALUES (?, ?, 'Class', ?, ?)", (dc_id, dc_pkg, dc_name, get_guid()))
        for aname, atype in attrs:
            cur.execute("""
                INSERT INTO t_attribute (ID, Object_ID, Name, Type, Scope, ea_guid)
                VALUES (?, ?, ?, ?, 'Public', ?)
            """, (attr_counter, dc_id, aname, atype, get_guid()))
            attr_counter += 1
        for op in ops:
            cur.execute("""
                INSERT INTO t_operation (OperationID, Object_ID, Name, Scope, ea_guid)
                VALUES (?, ?, ?, 'Public', ?)
            """, (op_counter, dc_id, op, get_guid()))
            op_counter += 1

    # Operaciones operacionales en las Clases de Control BCE
    bce_ops = [
        (52, ["iniciarFlujoPKCE(redirectUri)", "validarOAuthPKCE()", "emitirJWTRS256(claims)", "inicializarSesion(jwtClaims, roles)"]),
        (55, ["resolverSubgrafosFederados()", "consolidarResumenAsegurado()"]),
        (58, ["analizarNitidezKernelLaplaciano()", "validarUmbralNitidez065()"]),
        (61, ["recibirMensajeWhatsApp(payloadJson)", "generarFacturaPDF(poliza, qrFiscal, sha256)", "almacenarDocumento(facturaBytes)", "enviarDocumentoPorChat(pdfUrl)"]),
        (64, ["procesarReporteEmergencia(dto)", "calcularPrioridadTriajeGeoespacial()", "asignarPeritoMasCercano()", "despacharAlertaPush(peritoId, expedienteId)"]),
        (68, ["capturarFotografiasEvidencia(cameraBytes)", "preprocesarImagen(224x224, float32)", "ejecutarInferenciaLocalTFLite(tensors)", "calcularEstimacionBaremo(severidad)", "generarIdempotencyKey()"]),
        (72, ["extraerLotePendienteSQLite()", "validarIdempotenciaDynamoDB(key)", "sincronizarConMongoDB(expediente)", "actualizarEstadoSincronizado()"]),
        (75, ["iniciarSagaLiquidacion(siniestroId, monto)", "solicitarBloqueoCoberturaMS1()", "calcularMontoIndemnizable()", "insertOrdenDesembolso(montoNeto)", "ejecutarRollbackSemantico()"]),
        (76, ["bloquearSiniestro(siniestroId)", "revertirEstadoSiniestro(siniestroId)"]),
        (77, ["reservarCobertura(polizaId, monto)", "compensarCobertura(polizaId, monto)"]),
        (82, ["generarCobroQREMV(polizaId, monto)", "validarIdempotenciaPago(key, hash)", "asentarTransaccionContable(nroRecibo, monto)"]),
        (85, ["clasificarDanoCrashNet(tensorBatch)", "preprocesarRGBNormalizado(tensor)", "generarHeatmapGradCAM(targetLayer)", "calcularEstimacionBaremo(severidad)", "guardarDiagnosticoIA(severidad, baremo, heatmapUrl)"]),
        (88, ["entrenarModeloRandomForest()", "predecirDemandaVentas()", "calcularPrimaTecnicaOptima()"]),
        (91, ["segmentarAseguradosKMeans()", "detectarAnomaliasIsolationForest()", "marcarBanderaSIUFraude()"]),
        (95, ["evaluarSaludCluster()", "evaluarDesviacionMetas()", "planificarSkillsLangGraph()", "ejecutarAccionRebalanceo()"]),
        (98, ["transcribirAudioWhisper(audioBytes)", "sanitizarPromptAntiSQLi(texto)", "invocarToolMcpParametrizada(toolName, args)"]),
        (99, ["ejecutarToolParametrizada(tool, params)", "generarReporteExcelPDF(datos)"])
    ]
    for ctrl_id, ops in bce_ops:
        for op in ops:
            cur.execute("INSERT INTO t_operation (OperationID, Object_ID, Name, ea_guid) VALUES (?, ?, ?, ?)", (op_counter, ctrl_id, op, get_guid()))
            op_counter += 1

    # 7. Crear los 30 Diagramas Visuales del Sistema
    diagrams = [
        (1, 2, "Custom", "00. Panel de Navegación del Sistema Global (Home Page)"),
        (2, 2, "Use Case", "01. Diagrama General de Casos de Uso del Sistema (CU01 al CU15)"),
        (3, 3, "Use Case", "02. Casos de Uso - Módulo Comercial y SSO (CU01-CU05)"),
        (4, 4, "Use Case", "03. Casos de Uso - Módulo Siniestros y Saga (CU06-CU10)"),
        (5, 5, "Use Case", "04. Casos de Uso - Módulo Inteligencia Artificial y MCP (CU11-CU15)"),
        (6, 3, "Analysis", "05. Robustez BCE - CU01 (SSO Keycloak)"),
        (7, 3, "Analysis", "06. Robustez BCE - CU04 (Cotización Web con IA Local)"),
        (8, 3, "Analysis", "07. Robustez BCE - CU05 (Pedidos WhatsApp Factura n8n)"),
        (9, 4, "Analysis", "08. Robustez BCE - CU06 (Siniestro SOS Triaje)"),
        (10, 4, "Analysis", "09. Robustez BCE - CU07 (Inspección Offline Edge AI TFLite)"),
        (11, 4, "Analysis", "10. Robustez BCE - CU08 (Sincronización Idempotente DynamoDB)"),
        (12, 4, "Analysis", "11. Robustez BCE - CU09 (Liquidación Saga Transversal)"),
        (13, 4, "Analysis", "12. Robustez BCE - CU10 (Cobro Recurrente Pago QR)"),
        (14, 5, "Analysis", "13. Robustez BCE - CU11 (Visión Artificial CNN CrashNet)"),
        (15, 5, "Analysis", "14. Robustez BCE - CU12 (Predicción Ventas Random Forest)"),
        (16, 5, "Analysis", "15. Robustez BCE - CU13 (Segmentación K-Means y Fraude)"),
        (17, 5, "Analysis", "16. Robustez BCE - CU14 (Monitoreo Autónomo LangGraph)"),
        (18, 5, "Analysis", "17. Robustez BCE - CU15 (Reportes por Voz Servidor MCP Anti-SQLi)"),
        (19, 3, "Sequence", "18. Secuencia UML 2.5+ - CU01 (Autenticación SSO Keycloak)"),
        (20, 3, "Sequence", "19. Secuencia UML 2.5+ - CU05 (Flujo WhatsApp a Factura n8n)"),
        (21, 4, "Sequence", "20. Secuencia UML 2.5+ - CU06 (Triaje SOS Geoespacial)"),
        (22, 4, "Sequence", "21. Secuencia UML 2.5+ - CU07 (Inspección Offline TFLite)"),
        (23, 4, "Sequence", "22. Secuencia UML 2.5+ - CU08 (Sync Idempotente DynamoDB)"),
        (24, 4, "Sequence", "23. Secuencia UML 2.5+ - CU09 (Saga Transversal y Rollback Kafka)"),
        (25, 4, "Sequence", "24. Secuencia UML 2.5+ - CU10 (Pago QR Idempotente)"),
        (26, 5, "Sequence", "25. Secuencia UML 2.5+ - CU11 (Detección Choques CrashNet)"),
        (27, 5, "Sequence", "26. Secuencia UML 2.5+ - CU14 (Agente Autónomo LangGraph)"),
        (28, 5, "Sequence", "27. Secuencia UML 2.5+ - CU15 (Voz MCP con Filtro Anti-SQLi)"),
        (29, 6, "Logical", "28. Diagrama de Clases - Modelo de Dominio Global ERP"),
        (30, 7, "Component", "29. Diagrama de Componentes y Arquitectura Global en 4 Niveles")
    ]

    pdata_std = "HideRel=0;ShowTags=0;ShowReqs=0;ShowCons=0;OpParams=1;ShowSN=0;ScalePI=0;PPgs.cx=1;PPgs.cy=1;PSize=9;ShowIcons=1;SuppCN=0;HideProps=0;HideParents=0;UseAlias=0;HideAtts=0;HideOps=0;HideStereo=0;HideEStereo=0;ShowRec=1;ShowRes=0;ShowShape=1;FormName=;"
    style_ex_std = "ExcludeRTF=0;DocAll=0;HideQuals=0;AttPkg=1;ShowTests=0;ShowMaint=0;SuppressFOC=0;INT_ARGS=;INT_RET=;INT_ATT=;SeqTopMargin=50;MatrixActive=0;SwimlanesActive=1;KanbanActive=0;MatrixLineWidth=1;MatrixLineClr=0;MatrixLocked=0;TConnectorNotation=UML 2.1;TExplicitNavigability=0;AdvancedElementProps=1;AdvancedFeatureProps=1;AdvancedConnectorProps=1;m_bElementClassifier=1;SPT=1;MDGDgm=;STBLDgm=;ShowNotes=0;VisibleAttributeDetail=0;ShowOpRetType=1;SuppressBrackets=0;SuppConnectorLabels=0;PrintPageHeadFoot=0;ShowAsList=0;SuppressedCompartments=;Theme=:119;SaveTag=7A7E97D4;"

    for did, dpkg, dtype, dname in diagrams:
        cur.execute("""
            INSERT INTO t_diagram (
                Diagram_ID, Package_ID, ParentID, Diagram_Type, Name, Version, Author,
                ea_guid, cx, cy, PDATA, StyleEx
            ) VALUES (?, ?, 0, ?, ?, '2.0', 'Grupo #27 SW2', ?, 1400, 950, ?, ?)
        """, (did, dpkg, dtype, dname, get_guid(), pdata_std, style_ex_std))

    # Estructuras para gestión de objetos y enlaces
    dobj_map = {}
    conn_counter = 0

    def add_dobj(did, oid, left, top, right, bottom):
        duid = get_duid()
        center_x = (left + right) // 2
        dobj_map[(did, oid)] = (duid, left, top, right, bottom, center_x)
        obj_style = f"DUID={duid};BCol=-1;BFol=-1;LCol=-1;"
        cur.execute("""
            INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, ObjectStyle)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (did, oid, left, -top, right, -bottom, obj_style))

    def add_conn(name, ctype, sid, tid, did, seq_no=0, pt_y=0, direction="Source -> Destination"):
        nonlocal conn_counter
        conn_counter += 1
        guid = get_guid()

        s_info = dobj_map.get((did, sid))
        t_info = dobj_map.get((did, tid))
        soid = s_info[0] if s_info else "00000000"
        eoid = t_info[0] if t_info else "00000000"
        start_x = s_info[5] if s_info else 100
        end_x = t_info[5] if t_info else 300

        if ctype == "Sequence":
            if sid == tid:
                p_sx = start_x
                p_ex = start_x + 5
                p_sy = pt_y
                p_ey = pt_y - 15
                s_edge = 0
                e_edge = 0
                r_style = 2
            else:
                p_sx = start_x
                p_ex = end_x
                p_sy = pt_y
                p_ey = pt_y
                s_edge = 2 if start_x <= end_x else 4
                e_edge = 4 if start_x <= end_x else 2
                r_style = 1

            pdata5_metric = "$LLB=;LLT=;LMT=CX=68:CY=26:OX=0:OY=0:HDN=0:BLD=0:ITA=0:UND=0:CLR=-1:ALN=0:DIR=0:ROT=0;LMB=;LRT=;LRB=;IRHS=;ILHS=;"

            cur.execute("""
                INSERT INTO t_connector (
                    Connector_ID, Name, Direction, Connector_Type,
                    SourceAccess, DestAccess, Start_Object_ID, End_Object_ID,
                    Top_Mid_Label, Start_Edge, End_Edge, PtStartX, PtStartY, PtEndX, PtEndY,
                    SeqNo, RouteStyle, LineColor, DiagramID,
                    PDATA1, PDATA2, PDATA3, PDATA4, PDATA5, ea_guid,
                    DestIsNavigable, SourceIsNavigable, StateFlags, SourceStyle, DestStyle
                ) VALUES (?, ?, ?, 'Sequence', 'Public', 'Public', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, -1, ?, 'Synchronous', 'retval=void;', 'Call', '0', ?, ?, 1, 0, 'Activation=0;ExtendActivationUp=0;', 'Owned=0;Navigable=Non-Navigable;', 'Owned=0;Navigable=Navigable;')
            """, (
                conn_counter, name, direction, sid, tid,
                f" {name}", s_edge, e_edge, p_sx, p_sy, p_ex, p_ey,
                seq_no, r_style, did, pdata5_metric, guid
            ))
        else:
            cur.execute("""
                INSERT INTO t_connector (
                    Connector_ID, Name, Direction, Connector_Type,
                    SourceAccess, DestAccess, Start_Object_ID, End_Object_ID,
                    RouteStyle, LineColor, DiagramID, ea_guid,
                    SourceStyle, DestStyle
                ) VALUES (?, ?, ?, ?, 'Public', 'Public', ?, ?, 3, -1, ?, ?, 'Owned=0;Navigable=Non-Navigable;', 'Owned=0;Navigable=Navigable;')
            """, (
                conn_counter, name, direction, ctype, sid, tid, did, guid
            ))

            style_str = f"Mode=3;EOID={eoid};SOID={soid};Color=-1;LWidth=0;"
            geom_str = "EDGE=2;$LLB=;LLT=;LMT=;LMB=;LRT=;LRB=;IRHS=;ILHS=;"
            cur.execute("""
                INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Geometry, Style, Hidden)
                VALUES (?, ?, ?, ?, 0)
            """, (did, conn_counter, geom_str, style_str))

        return conn_counter

    # =========================================================================
    # DIAGRAMA 1: Home Page con Celdas de Navegación Interactivas (NavigationCell)
    # =========================================================================
    nav_cells = [
        (301, "01. Diagrama General de Casos de Uso (CU01 al CU15)", 2, 60, 60, 420, 180),
        (302, "02. Casos de Uso - Módulo Comercial y SSO (CU01-CU05)", 3, 460, 60, 820, 180),
        (303, "03. Casos de Uso - Módulo Siniestros y Saga (CU06-CU10)", 4, 860, 60, 1220, 180),
        (304, "04. Casos de Uso - Módulo IA y MCP (CU11-CU15)", 5, 60, 220, 420, 340),
        (305, "28. Diagrama de Clases - Modelo de Dominio Global ERP", 29, 460, 220, 820, 340),
        (306, "29. Diagrama de Componentes y Arquitectura Global", 30, 860, 220, 1220, 340)
    ]
    for n_id, n_name, target_did, l, t, r, b in nav_cells:
        cur.execute("""
            INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, Stereotype, PDATA1, PDATA3, ea_guid)
            VALUES (?, 2, 'Text', ?, 'NavigationCell', ?, 1, ?)
        """, (n_id, n_name, target_did, get_guid()))
        add_dobj(1, n_id, l, t, r, b)

    # =========================================================================
    # DIAGRAMA 2: General de Casos de Uso (CU01 al CU15) — 3 Columnas por Módulo
    # =========================================================================
    # Actores a la izquierda (X = 40 a 160)
    act_y = 50
    for aid, aname in actors:
        add_dobj(2, aid, 40, act_y, 160, act_y + 75)
        act_y += 95

    # 3 Columnas de Casos de Uso:
    # Col 1: Comercial (CU01-CU05) -> X = 260 a 520
    # Col 2: Siniestros (CU06-CU10) -> X = 560 a 820
    # Col 3: IA y MCP (CU11-CU15) -> X = 860 a 1140
    uc_col_map = {
        21: (260, 50),  22: (260, 135), 23: (260, 220), 24: (260, 305), 25: (260, 390),
        26: (560, 50),  27: (560, 135), 28: (560, 220), 29: (560, 305), 30: (560, 390),
        31: (860, 50),  32: (860, 135), 33: (860, 220), 34: (860, 305), 35: (860, 390)
    }
    for ucid, uc_pkg, ucname in use_cases:
        x, y = uc_col_map[ucid]
        add_dobj(2, ucid, x, y, x + 260, y + 60)

    # Conectores en Diagrama 2
    add_conn("Inicia Sesión SSO", "Use Case", 10, 21, 2)
    add_conn("Consulta Estado GraphQL", "Use Case", 10, 22, 2)
    add_conn("Cotiza Póliza Web PWA", "Use Case", 10, 24, 2)
    add_conn("Contrata por WhatsApp", "Use Case", 10, 25, 2)
    add_conn("Reporta Emergencia SOS", "Use Case", 10, 26, 2)
    add_conn("Paga Prima QR", "Use Case", 10, 30, 2)
    add_conn("Atiende Triaje SOS", "Use Case", 11, 26, 2)
    add_conn("Inspecciona Daños Offline", "Use Case", 11, 27, 2)
    add_conn("Sincroniza con DynamoDB", "Use Case", 11, 28, 2)
    add_conn("Liquida Indemnización", "Use Case", 12, 29, 2)
    add_conn("Audita Daños CrashNet", "Use Case", 12, 31, 2)
    add_conn("Analiza Demanda y Primas", "Use Case", 13, 32, 2)
    add_conn("Monitorea Fraude y Clusters", "Use Case", 13, 33, 2)
    add_conn("Supervisa Agente Autónomo", "Use Case", 14, 34, 2)
    add_conn("Consulta Reportes por Voz", "Use Case", 14, 35, 2)
    add_conn("Orquesta Rollback Saga", "Use Case", 15, 29, 2)
    add_conn("Despacha Automatización n8n", "Use Case", 16, 25, 2)
    add_conn("Sirve Tools MCP Tipadas", "Use Case", 16, 35, 2)

    # =========================================================================
    # DIAGRAMA 3: Casos de Uso - Módulo Comercial y SSO (CU01-CU05)
    # =========================================================================
    add_dobj(3, 10, 50, 60, 160, 140)   # Cliente Asegurado
    add_dobj(3, 14, 50, 220, 160, 300)  # Director Comercial
    add_dobj(3, 16, 50, 380, 160, 460)  # Bot WhatsApp
    m1_ucs = [(21, 60), (22, 145), (23, 230), (24, 315), (25, 400)]
    for ucid, y in m1_ucs:
        add_dobj(3, ucid, 350, y, 650, y + 60)
    add_conn("Autenticación SSO", "Use Case", 10, 21, 3)
    add_conn("Consulta Estado", "Use Case", 10, 22, 3)
    add_conn("Cotiza PWA", "Use Case", 10, 24, 3)
    add_conn("Confirma Pedido", "Use Case", 10, 25, 3)
    add_conn("Administra Catálogo", "Use Case", 14, 23, 3)
    add_conn("Despacha Factura n8n", "Use Case", 16, 25, 3)

    # =========================================================================
    # DIAGRAMA 4: Casos de Uso - Módulo Siniestros y Saga (CU06-CU10)
    # =========================================================================
    add_dobj(4, 10, 50, 60, 160, 140)   # Cliente Asegurado
    add_dobj(4, 11, 50, 190, 160, 270)  # Perito de Campo
    add_dobj(4, 12, 50, 320, 160, 400)  # Ajustador
    add_dobj(4, 15, 50, 450, 160, 530)  # Broker Kafka
    m2_ucs = [(26, 60), (27, 145), (28, 230), (29, 315), (30, 400)]
    for ucid, y in m2_ucs:
        add_dobj(4, ucid, 350, y, 660, y + 60)
    add_conn("Reporta SOS", "Use Case", 10, 26, 4)
    add_conn("Paga Cuota QR", "Use Case", 10, 30, 4)
    add_conn("Atiende Emergencia", "Use Case", 11, 26, 4)
    add_conn("Inspecciona Offline", "Use Case", 11, 27, 4)
    add_conn("Sincroniza Lote", "Use Case", 11, 28, 4)
    add_conn("Aprueba Liquidación", "Use Case", 12, 29, 4)
    add_conn("Orquesta Rollback", "Use Case", 15, 29, 4)

    # =========================================================================
    # DIAGRAMA 5: Casos de Uso - Módulo IA y MCP (CU11-CU15)
    # =========================================================================
    add_dobj(5, 12, 50, 60, 160, 140)   # Ajustador
    add_dobj(5, 13, 50, 190, 160, 270)  # Auditor BI
    add_dobj(5, 14, 50, 320, 160, 400)  # Director
    add_dobj(5, 16, 50, 450, 160, 530)  # Servidor MCP
    m3_ucs = [(31, 60), (32, 145), (33, 230), (34, 315), (35, 400)]
    for ucid, y in m3_ucs:
        add_dobj(5, ucid, 350, y, 670, y + 60)
    add_conn("Audita Choque CNN", "Use Case", 12, 31, 5)
    add_conn("Calcula Prima Random Forest", "Use Case", 13, 32, 5)
    add_conn("Segmenta y Detecta Fraude", "Use Case", 13, 33, 5)
    add_conn("Supervisa Agente Autónomo", "Use Case", 14, 34, 5)
    add_conn("Dicta Consulta por Voz", "Use Case", 14, 35, 5)
    add_conn("Resuelve Tools MCP Parametrizadas", "Use Case", 16, 35, 5)

    # =========================================================================
    # DIAGRAMAS 6 a 18: Robustez BCE con Amplia Separación Horizontal
    # =========================================================================
    rob_defs = [
        (6, 51, 52, 53, "1. Enviar credenciales SSO", "2. Generar token JWT RS256"),
        (7, 57, 58, 59, "1. Capturar foto documento", "2. Validar nitidez Laplaciano >=0.65"),
        (8, 60, 61, 62, "1. Webhook pedido WhatsApp", "2. Generar Factura Fiscal PDF n8n"),
        (9, 63, 64, 65, "1. Reportar emergencia SOS GPS", "2. Persistir expediente y triaje"),
        (10, 67, 68, 69, "1. Capturar fotograma choque", "2. Inferir TFLite y guardar SQLite"),
        (11, 71, 72, 73, "1. POST sync con Idempotency-Key", "2. Verificar o adquirir lock DynamoDB"),
        (12, 74, 75, 78, "1. Autorizar liquidación ($1,200 BOB)", "2. Iniciar Saga y orquestar rollback"),
        (13, 81, 82, 83, "1. Solicitar cobro cuota QR", "2. Validar idempotencia y asentar pago"),
        (14, 84, 85, 86, "1. Cargar imagen siniestro", "2. Clasificar severidad CrashNet CNN"),
        (15, 87, 88, 89, "1. Parámetros conductor y vehículo", "2. Predecir prima Random Forest"),
        (16, 90, 91, 92, "1. Vector siniestralidad", "2. Detectar anomalía Isolation Forest"),
        (17, 94, 95, 96, "1. Métricas de salud del cluster", "2. Re-planificar metas LangGraph"),
        (18, 97, 98, 99, "1. Dictar nota de voz pericial", "2. Transcribir Whisper y filtrar Anti-SQLi")
    ]
    for rdid, rbid, rcid, reid, m1, m2 in rob_defs:
        add_dobj(rdid, rbid, 60, 80, 220, 160)
        add_dobj(rdid, rcid, 390, 80, 570, 170)
        add_dobj(rdid, reid, 740, 80, 930, 160)
        add_conn(m1, "Association", rbid, rcid, rdid)
        add_conn(m2, "Association", rcid, reid, rdid)

    # =========================================================================
    # DIAGRAMAS 19 a 28: Secuencia UML 2.5+ Completos (Fieles a PlantUML / Markdown)
    # =========================================================================
    seq_defs = [
        # 19. Secuencia CU01: Autenticación Centralizada SSO con Keycloak (5 Lifelines, 12 Mensajes)
        (19, [
            (17, 80, 110),   # Usuario (Actor)
            (51, 310, 120),  # LoginKeycloakSSOView (Boundary)
            (52, 540, 120),  # KeycloakSSOControl (Control)
            (220, 770, 120), # Servidor Keycloak (System)
            (53, 1000, 120)  # UsuarioSesionEntity (Entity)
        ], [
            ("1. Presiona \"Ingresar con Keycloak\"", 17, 51, -80),
            ("2. iniciarFlujoPKCE(redirectUri)", 51, 52, -125),
            ("3. GET /auth?response_type=code&code_challenge=...", 52, 220, -170),
            ("4. Presenta formulario de credenciales", 220, 17, -215),
            ("5. Envía credenciales (usr, pwd)", 17, 220, -260),
            ("6. Emite código de autorización (code)", 220, 52, -305),
            ("7. POST /token (code + code_verifier)", 52, 220, -350),
            ("8. Retorna tokens JWT (Access RS256 + Refresh)", 220, 52, -395),
            ("9. inicializarSesion(jwtClaims, roles)", 52, 53, -440),
            ("10. Sesión creada", 53, 52, -485),
            ("11. Redirigir a Dashboard con permisos", 52, 51, -530),
            ("12. Muestra pantalla según rol autorizado", 51, 17, -575)
        ]),

        # 20. Secuencia CU05: Flujo WhatsApp a Factura Fiscal PDF con n8n (6 Lifelines, 11 Mensajes)
        (20, [
            (10, 70, 100),   # Cliente Asegurado (Actor)
            (60, 270, 110),  # CanalWhatsAppWebhook (Boundary)
            (61, 480, 120),  # OrquestadorWorkflowN8nControl (Control)
            (221, 690, 110), # MS1 Pólizas PHP (DDD) (Service)
            (222, 900, 110), # Almacenamiento S3 / MinIO (Storage)
            (62, 1110, 110)  # FacturaFiscalPDFEntity (Entity)
        ], [
            ("1. CONFIRMAR PEDIDO COT-88102", 10, 60, -80),
            ("2. recibirMensajeWhatsApp(payloadJson)", 60, 61, -125),
            ("3. POST /api/v1/polizas/emitir-desde-cotizacion", 61, 221, -170),
            ("4. 201 Created (PolizaId: POL-2026-0041)", 221, 61, -215),
            ("5. generarFacturaPDF(poliza, qrFiscal, sha256)", 61, 61, -260),
            ("6. almacenarDocumento(facturaBytes)", 61, 222, -305),
            ("7. URL prefirmada segura", 222, 61, -350),
            ("8. registrarFacturaEmitida(nroFactura, urlPdf)", 61, 62, -395),
            ("9. Factura persistida", 62, 61, -440),
            ("10. enviarDocumentoPorChat(pdfUrl)", 61, 60, -485),
            ("11. Recibe Factura Oficial en PDF con código QR", 60, 10, -530)
        ]),

        # 21. Secuencia CU06: Triaje SOS Geoespacial y Despacho de Perito (6 Lifelines, 11 Mensajes)
        (21, [
            (10, 70, 100),   # Asegurado (Actor)
            (63, 270, 110),  # SiniestroSosMobileView (Boundary)
            (64, 480, 120),  # SiniestroEmergencyControl (Control)
            (66, 690, 110),  # PeritoGuardiaEntity (2dsphere)
            (65, 900, 110),  # ExpedienteSiniestroEntity (Mongo)
            (223, 1110, 110) # PushNotificationGateway (Service)
        ], [
            ("1. Presiona botón rojo \"EMERGENCIA SOS\"", 10, 63, -80),
            ("2. Capturar coordenadas GPS (-17.783, -63.182)", 63, 63, -125),
            ("3. procesarReporteEmergencia(dto)", 63, 64, -170),
            ("4. buscarPeritoMasCercano(coords, radio25km)", 64, 66, -215),
            ("5. Perito encontrado: \"Ing. Perito Juan\" (a 3.2 km)", 66, 64, -260),
            ("6. guardarExpediente(expedienteDoc)", 64, 65, -305),
            ("7. Expediente guardado: SIN-2026-00050", 65, 64, -350),
            ("8. despacharAlertaPush(peritoId, expedienteId)", 64, 223, -395),
            ("9. Alerta despachada", 223, 64, -440),
            ("10. 201 Created (SiniestroRegistradoDto)", 64, 63, -485),
            ("11. Muestra código SIN-2026-00050 y perito en camino", 63, 10, -530)
        ]),

        # 22. Secuencia CU07: Captura e Inferencia Móvil Offline con Edge AI (5 Lifelines, 11 Mensajes)
        (22, [
            (11, 80, 110),   # Perito de Campo (Actor)
            (67, 310, 120),  # CamaraPeritajeOfflineView (Boundary)
            (68, 540, 120),  # PeritajeOfflineTFLiteControl (Control)
            (70, 770, 120),  # ModeloTFLiteQuantized (Model)
            (69, 1000, 120)  # InspeccionOfflineSQLiteEntity (Entity)
        ], [
            ("1. Encuadra parachoque abollado y presiona obturador", 11, 67, -80),
            ("2. capturarFotografiasEvidencia(cameraBytes)", 67, 68, -125),
            ("3. preprocesarImagen(224x224, float32)", 68, 68, -170),
            ("4. ejecutarInferenciaLocalTFLite(tensors)", 68, 70, -215),
            ("5. Vector probabilidades: [0.02, 0.10, 0.85, 0.03]", 70, 68, -260),
            ("6. calcularEstimacionBaremo(\"Moderado\") -> 1,200 BOB", 68, 68, -305),
            ("7. generarIdempotencyKey() -> UUIDv4 + Hash", 68, 68, -350),
            ("8. insertarInspeccionSQLite(inspeccionOfflineDto)", 68, 69, -395),
            ("9. Registro guardado localmente", 69, 68, -440),
            ("10. Presenta diagnóstico: \"Daño Moderado (85%)\"", 68, 67, -485),
            ("11. Confirma peritaje guardado sin internet", 67, 11, -530)
        ]),

        # 23. Secuencia CU08: Sincronización Idempotente con DynamoDB (<5 ms) (5 Lifelines, 10 Mensajes)
        (23, [
            (11, 80, 110),   # Perito de Campo (Actor)
            (71, 310, 120),  # ColaSincronizacionOfflineView (Boundary)
            (72, 540, 120),  # SyncIdempotentControl (Control)
            (73, 770, 120),  # IdempotencyRecordEntity (DynamoDB)
            (65, 1000, 120)  # ExpedienteSiniestroEntity (MongoDB)
        ], [
            ("1. Recupera señal 4G y presiona \"Sincronizar Lote\"", 11, 71, -80),
            ("2. POST /sync-offline (Header: X-Idempotency-Key)", 71, 72, -125),
            ("3. GetItem(idempotencyKey) [<5 ms]", 72, 73, -170),
            ("4. Clave No Existe: null", 73, 72, -215),
            ("5. PutItem(key, hash, status=\"IN_PROGRESS\")", 72, 73, -260),
            ("6. insertOne(expedienteConsolidado)", 72, 65, -305),
            ("7. 201 Created (Expediente Guardado en MongoDB)", 65, 72, -350),
            ("8. UpdateItem(status=\"COMPLETED\", resCode=201)", 72, 73, -395),
            ("9. 201 Created (Expediente Sincronizado)", 72, 71, -440),
            ("10. Marca inspección como SINCRONIZADA en SQLite", 71, 11, -485)
        ]),

        # 24. Secuencia CU09: Liquidación Autónoma Transversal con Saga y Rollback en Kafka (7 Lifelines, 13 Mensajes)
        (24, [
            (12, 60, 100),   # Ajustador (Actor)
            (74, 230, 110),  # LiquidacionSiniestroAdminView (Boundary)
            (75, 400, 120),  # SagaLiquidacionOrchestratorControl (Control MS3)
            (15, 570, 100),  # Apache Kafka (Broker Actor)
            (76, 740, 110),  # ReclamoEstadoControl_MS2 (Control MS2)
            (77, 910, 110),  # PolizaCoberturaControl_MS1 (Control MS1)
            (79, 1080, 110)  # OrdenLiquidacionEntity (Entity Postgres)
        ], [
            ("1. Presiona \"Aprobar Liquidación (1,200 BOB)\"", 12, 74, -80),
            ("2. iniciarSagaLiquidacion(siniestroId, 1200 BOB)", 74, 75, -125),
            ("3. Publish: ClaimSettlementInitiated", 75, 15, -170),
            ("4. Consume: ClaimSettlementInitiated", 15, 76, -215),
            ("5. PATCH /siniestros/bloquear -> Estado LIQUIDANDO", 76, 76, -260),
            ("6. Publish: ClaimStatusLocked", 76, 15, -305),
            ("7. Consume: ClaimStatusLocked", 15, 77, -350),
            ("8. Reservar cobertura 1,200 BOB en PostgreSQL", 77, 77, -395),
            ("9. Publish: PolicyCoverageReserved", 77, 15, -440),
            ("10. Consume: PolicyCoverageReserved", 15, 75, -485),
            ("11. insertOrdenDesembolso(1080 BOB [neto deducible])", 75, 79, -530),
            ("12. Publish: SettlementApproved", 75, 15, -575),
            ("13. 200 OK: Liquidación Desembolsada", 75, 74, -620)
        ]),

        # 25. Secuencia CU10: Cobro Recurrente y Pago QR Idempotente (6 Lifelines, 12 Mensajes)
        (25, [
            (10, 70, 100),   # Cliente Asegurado (Actor)
            (81, 270, 110),  # CobroPrimaQRView (Boundary)
            (82, 480, 120),  # PagoPrimaQRControl (Control)
            (224, 690, 110), # Pasarela Bancaria BCB (Service)
            (73, 900, 110),  # IdempotencyRecordEntity (DynamoDB)
            (83, 1110, 110)  # TransaccionPagoQREntity (Postgres)
        ], [
            ("1. Solicita pago de cuota mensual (350 BOB)", 10, 81, -80),
            ("2. generarCobroQREMV(polizaId, 350 BOB)", 81, 82, -125),
            ("3. Solicitar payload QR EMVCo", 82, 224, -170),
            ("4. Retorna QR String con vencimiento 15 min", 224, 82, -215),
            ("5. Despliega imagen QR en pantalla", 82, 81, -260),
            ("6. Escanea y transfiere desde app bancaria", 10, 224, -305),
            ("7. Callback POST /qr/callback (X-Idempotency-Key)", 224, 82, -350),
            ("8. GetItem(key) [<5 ms]", 82, 73, -395),
            ("9. asentarTransaccionContable(nroRecibo, 350 BOB)", 82, 83, -440),
            ("10. UpdateItem(status=\"COMPLETED\")", 82, 73, -485),
            ("11. Notifica pago recibido en tiempo real", 82, 81, -530),
            ("12. Presenta Recibo Digital REC-99120", 81, 10, -575)
        ]),

        # 26. Secuencia CU11: Visión Artificial CNN CrashNet y Grad-CAM (5 Lifelines, 12 Mensajes)
        (26, [
            (13, 80, 110),   # Auditor / Ajustador (Actor)
            (84, 310, 120),  # VisionArtificialUploadView (Boundary)
            (85, 540, 120),  # CrashNetVisionControl (Control)
            (225, 770, 120), # CNN CrashNet (Keras/TensorFlow) (Model)
            (86, 1000, 120)  # ReporteInspeccionIAEntity (MongoDB)
        ], [
            ("1. Sube fotografía de siniestro vehicular", 13, 84, -80),
            ("2. POST /api/v1/ia/crashnet/analizar (multipart/data)", 84, 85, -125),
            ("3. Preprocesar RGB normalizado [224x224]", 85, 85, -170),
            ("4. clasificarDanoCrashNet(tensorBatch)", 85, 225, -215),
            ("5. Probabilidades: {Severo: 0.914, Moderado: 0.08}", 225, 85, -260),
            ("6. generarHeatmapGradCAM(targetLayer=\"conv_final\")", 85, 225, -305),
            ("7. Matriz de calor Grad-CAM sobreexpuesta", 225, 85, -350),
            ("8. calcularEstimacionBaremo(\"Severo\") -> 3,800 BOB", 85, 85, -395),
            ("9. guardarDiagnosticoIA(severidad, baremo, heatmapUrl)", 85, 86, -440),
            ("10. Diagnóstico persistido", 86, 85, -485),
            ("11. 200 OK (Heatmap Imagen, 91.4% Confianza, Baremo)", 85, 84, -530),
            ("12. Visualiza mapa de calor y desglose de piezas", 84, 13, -575)
        ]),

        # 27. Secuencia CU14: Bucle de Razonamiento del Agente Autónomo LangGraph (5 Lifelines, 9 Mensajes)
        (27, [
            (13, 80, 110),   # Auditor BI (Actor)
            (94, 310, 120),  # AutonomousAgentMonitorView (Boundary)
            (95, 540, 120),  # LangGraphAutonomousAgentControl (Control)
            (96, 770, 120),  # ClusterAgentStateEntity (Entity)
            (226, 1000, 120) # Entorno de Servicios / Despacho (System)
        ], [
            ("1. Suscribirse a feed de razonamiento SSE", 94, 95, -80),
            ("2. PerceptionNode: leerMetricasSaludCluster()", 95, 226, -125),
            ("3. Métricas: SLA Cuadrante Norte = 38 min (>30 min)", 226, 95, -170),
            ("4. ReasoningNode: evaluarDesviacionMetas()", 95, 95, -215),
            ("5. PlanningNode: seleccionarSkill(\"RebalancearPeritos\")", 95, 95, -260),
            ("6. ActionNode: ejecutarSkill(origen=\"Centro\", qty=2)", 95, 226, -305),
            ("7. Rebalanceo confirmado en despacho", 226, 95, -350),
            ("8. actualizarEstadoCluster(state=\"GOAL_MET\", SLA=22m)", 95, 96, -395),
            ("9. Push evento SSE con árbol de razonamiento actualizado", 95, 94, -440)
        ]),

        # 28. Secuencia CU15: Reportes por Voz MCP con Blindaje Anti-SQLi (6 Lifelines, 12 Mensajes)
        (28, [
            (14, 70, 100),   # Directivo (Actor)
            (97, 270, 110),  # MicrofonoVoiceReportView (Boundary)
            (98, 480, 120),  # VoiceMcpOwaspControl (Control)
            (227, 690, 110), # Motor Whisper STT (Model)
            (99, 900, 110),  # Servidor MCP Protocol (Control)
            (228, 1110, 110) # PostgreSQL 16 (Consultas Compiladas) (Node)
        ], [
            ("1. Presiona micrófono y dicta instrucción ejecutiva", 14, 97, -80),
            ("2. POST /transcribe-and-query (audioBlob)", 97, 98, -125),
            ("3. transcribirAudioWhisper(audioBytes)", 98, 227, -170),
            ("4. Texto: \"Dame siniestros moderados liquidados en SCZ\"", 227, 98, -215),
            ("5. sanitizarPromptAntiSQLi(textoTranscrito)", 98, 98, -260),
            ("6. invocarToolTipada(\"consultar_liquidaciones\", args)", 98, 99, -305),
            ("7. SELECT parametrizado compilado en ORM", 99, 228, -350),
            ("8. 14 registros recuperados", 228, 99, -395),
            ("9. generarReporteExcelPDF(datos)", 99, 99, -440),
            ("10. URL descarga segura + Síntesis resumen", 99, 98, -485),
            ("11. 200 OK (Audio respuesta + Enlace descarga)", 98, 97, -530),
            ("12. Reproduce audio y habilita botón \"Descargar XLSX\"", 97, 14, -575)
        ])
    ]

    for sdid, lifelines, msgs in seq_defs:
        max_bottom = 660 if len(msgs) <= 9 else 780
        for l_obj_id, cx, w in lifelines:
            add_dobj(sdid, l_obj_id, cx - w // 2, 40, cx + w // 2, max_bottom)
        s_no = 1
        for mname, sid, tid, py in msgs:
            add_conn(mname, "Sequence", sid, tid, sdid, seq_no=s_no, pt_y=py)
            s_no += 1

    # =========================================================================
    # DIAGRAMA 29: Modelo de Dominio Global ERP (Clases Rectangulares con Atributos)
    # =========================================================================
    # Matriz 4 Columnas x 3 Filas limpia y con amplio espacio (Cero solapamiento)
    # Col 1: X = 50 a 280
    # Col 2: X = 350 a 580
    # Col 3: X = 650 a 880
    # Col 4: X = 950 a 1180
    # Fila 1: Y = 50 a 200 (Usuario, Asegurado, Poliza, VehiculoAsegurado)
    # Fila 2: Y = 270 a 420 (Cotizacion, ExpedienteSiniestro, PeritajeInspeccion, IdempotencyRecord)
    # Fila 3: Y = 490 a 640 (FacturaFiscal, SagaLiquidacion, OrdenLiquidacion, TransaccionPagoQR)
    dom_layout = [
        (201, 50, 50, 270, 190),     # Usuario
        (202, 340, 50, 560, 190),    # Asegurado
        (203, 630, 50, 870, 200),    # Poliza
        (204, 940, 50, 1180, 200),   # VehiculoAsegurado

        (205, 50, 270, 270, 420),    # Cotizacion
        (206, 340, 270, 570, 430),   # ExpedienteSiniestro
        (207, 640, 270, 870, 430),   # PeritajeInspeccion
        (208, 940, 270, 1180, 420),  # IdempotencyRecord

        (212, 50, 490, 270, 640),    # FacturaFiscal
        (209, 340, 490, 570, 640),   # SagaLiquidacion
        (210, 640, 490, 870, 640),   # OrdenLiquidacion
        (211, 940, 490, 1180, 640)   # TransaccionPagoQR
    ]
    for oid, l, t, r, b in dom_layout:
        add_dobj(29, oid, l, t, r, b)

    add_conn("es-un", "Generalization", 202, 201, 29)
    add_conn("contrata", "Composition", 202, 203, 29)
    add_conn("ampara", "Composition", 203, 204, 29)
    add_conn("deriva-de", "Aggregation", 203, 205, 29)
    add_conn("factura-mensual", "Association", 203, 212, 29)
    add_conn("abono-prima", "Association", 203, 211, 29)
    add_conn("cubre-accidente", "Association", 203, 206, 29)
    add_conn("detalla-evidencias", "Composition", 206, 207, 29)
    add_conn("asegurado-por", "Dependency", 207, 208, 29)
    add_conn("protegido-por", "Dependency", 211, 208, 29)
    add_conn("resuelve-financieramente", "Association", 206, 209, 29)
    add_conn("genera-desembolso", "Composition", 209, 210, 29)

    # =========================================================================
    # DIAGRAMA 30: Componentes y Arquitectura Global en 4 Niveles
    # =========================================================================
    comp_layout = [
        (101, 60, 50, 300, 160),    # Flutter
        (102, 60, 210, 300, 320),   # React PWA
        (103, 60, 370, 300, 480),   # Angular Admin
        (104, 400, 50, 650, 160),   # MS1 PHP
        (105, 400, 210, 650, 320),  # MS2 NestJS
        (106, 400, 370, 650, 480),  # MS3 Spring Boot
        (107, 400, 530, 650, 640),  # MS4 Python FastAPI
        (108, 770, 200, 1020, 370), # Persistencia Políglota
        (109, 1080, 200, 1330, 370) # Kafka y Gateway
    ]
    for cid, l, t, r, b in comp_layout:
        add_dobj(30, cid, l, t, r, b)
    add_conn("HTTP REST Idempotente", "Dependency", 101, 105, 30)
    add_conn("Consulta GraphQL", "Dependency", 102, 104, 30)
    add_conn("BI Dashboards", "Dependency", 103, 107, 30)
    add_conn("ACID PostgreSQL", "Association", 104, 108, 30)
    add_conn("MongoDB 2dsphere", "Association", 105, 108, 30)
    add_conn("Hexagonal JPA", "Association", 106, 108, 30)
    add_conn("ML Scikit/TF", "Association", 107, 108, 30)
    add_conn("Saga Bus Eventos", "Association", 106, 109, 30)
    add_conn("Compensacion Kafka", "Dependency", 109, 104, 30)
    add_conn("Reversión Kafka", "Dependency", 109, 105, 30)

    conn.commit()
    conn.close()

    # Sincronizar copias en el repositorio
    shutil.copy(target_qea, "AegisCore_Perfil_B.qea")
    shutil.copy(target_qea, "docs-iconix-uml/AegisCore_AI.qea")
    shutil.copy(target_qea, "docs-iconix-uml/AegisCore_Perfil_B.qea")
    shutil.copy(target_qea, "docs-iconix-uml/enterprise-architect/aegiscore-perfil-b-ea17.qea")

    print(f"Éxito: AegisCore_AI.qea completamente reconstruido.")
    print(f"Total Diagramas: {len(diagrams)} (Todos con elementos y conectores)")
    print(f"Total Conectores y Mensajes: {conn_counter}")

if __name__ == "__main__":
    build_qea()
