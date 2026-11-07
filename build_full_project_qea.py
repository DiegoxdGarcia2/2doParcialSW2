# -*- coding: utf-8 -*-
"""
Constructor del Modelo de Proyecto Completo (.qea) para Enterprise Architect 17.2
Proyecto: AegisCore AI — ERP Distribuido, Peritaje Inteligente y Liquidación Autónoma de Siniestros
Alcance Total: Todos los Módulos (CU01 al CU15) — Comercial, Siniestros e Inteligencia Artificial
Genera enlaces y conectores nativos compatibles con Sparx Enterprise Architect 17.2 (DUID, SOID, EOID, Sequence Messages)
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
    print(f"Copiado EABase.qea a {target_qea}")

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

    # 2. Paquetes Principales
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

    # 3. Actores Globales del Sistema (IDs 10 to 16)
    actors = [
        (10, 'Cliente Asegurado'),
        (11, 'Perito de Campo'),
        (12, 'Ajustador de Siniestros'),
        (13, 'Auditor de Riesgos y Analista BI'),
        (14, 'Director Comercial y Finanzas'),
        (15, 'Broker Apache Kafka'),
        (16, 'Bot WhatsApp y Servidor MCP')
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

    # 5. Clases BCE de Robustez y Dominio (IDs 51 to 105)
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

    # Operaciones operacionales en las Clases de Control
    operations = [
        (52, ["autenticarOAuthPKCE()", "validarTokenJWTRS256()"]),
        (55, ["resolverSubgrafosFederados()", "consolidarResumenAsegurado()"]),
        (58, ["analizarNitidezKernelLaplaciano()", "validarUmbralNitidez065()"]),
        (61, ["procesarMensajeWhatsApp()", "dispararEmisionFacturaPDF()"]),
        (64, ["procesarReporteEmergencia(dto)", "calcularPrioridadTriajeGeoespacial()", "asignarPeritoMasCercano()"]),
        (68, ["capturarFotografiasEvidencia()", "ejecutarInferenciaLocalTFLite()", "generarIdempotencyKey()"]),
        (72, ["extraerLotePendienteSQLite()", "validarIdempotenciaDynamoDB()", "sincronizarConMongoDB()"]),
        (75, ["iniciarSagaLiquidacion()", "solicitarBloqueoCoberturaMS1()", "calcularMontoIndemnizable()", "ejecutarRollbackSemantico()"]),
        (82, ["generarCobroQREMV()", "validarIdempotenciaPago()", "asentarTransaccionContable()"]),
        (85, ["clasificarDanoCrashNet()", "generarHeatmapGradCAM()", "calcularEstimacionBaremo()"]),
        (88, ["entrenarModeloRandomForest()", "predecirDemandaVentas()", "calcularPrimaTecnicaOptima()"]),
        (91, ["segmentarAseguradosKMeans()", "detectarAnomaliasIsolationForest()", "marcarBanderaSIUFraude()"]),
        (95, ["evaluarSaludCluster()", "planificarSkillsLangGraph()", "ejecutarAccionRebalanceo()"]),
        (98, ["transcribirAudioWhisper()", "sanitizarPromptAntiSQLi()", "invocarToolMcpParametrizada()"])
    ]
    op_counter = 1
    for ctrl_id, ops in operations:
        for op in ops:
            cur.execute("INSERT INTO t_operation (OperationID, Object_ID, Name, ea_guid) VALUES (?, ?, ?, ?)", (op_counter, ctrl_id, op, get_guid()))
            op_counter += 1

    # 6. Crear los Diagramas Visuales del Sistema
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

    pdata_standard = "HideRel=0;ShowTags=0;ShowReqs=0;ShowCons=0;OpParams=1;ShowSN=0;ScalePI=0;PPgs.cx=1;PPgs.cy=1;PSize=9;ShowIcons=1;SuppCN=0;HideProps=0;HideParents=0;UseAlias=0;HideAtts=0;HideOps=0;HideStereo=0;HideEStereo=0;ShowRec=1;ShowRes=0;ShowShape=1;FormName=;"
    style_ex_standard = "ExcludeRTF=0;DocAll=0;HideQuals=0;AttPkg=1;ShowTests=0;ShowMaint=0;SuppressFOC=0;INT_ARGS=;INT_RET=;INT_ATT=;SeqTopMargin=50;MatrixActive=0;SwimlanesActive=1;KanbanActive=0;MatrixLineWidth=1;MatrixLineClr=0;MatrixLocked=0;TConnectorNotation=UML 2.1;TExplicitNavigability=0;AdvancedElementProps=1;AdvancedFeatureProps=1;AdvancedConnectorProps=1;m_bElementClassifier=1;SPT=1;MDGDgm=;STBLDgm=;ShowNotes=0;VisibleAttributeDetail=0;ShowOpRetType=1;SuppressBrackets=0;SuppConnectorLabels=0;PrintPageHeadFoot=0;ShowAsList=0;SuppressedCompartments=;Theme=:119;SaveTag=7A7E97D4;"

    for did, dpkg, dtype, dname in diagrams:
        cur.execute("""
            INSERT INTO t_diagram (
                Diagram_ID, Package_ID, ParentID, Diagram_Type, Name, Version, Author,
                ea_guid, cx, cy, PDATA, StyleEx
            ) VALUES (?, ?, 0, ?, ?, '2.0', 'Grupo #27 SW2', ?, 1300, 850, ?, ?)
        """, (did, dpkg, dtype, dname, get_guid(), pdata_standard, style_ex_standard))

    # Mapeo de objetos colocados en diagramas para SOID y EOID: (did, oid) -> (duid, left, top, right, bottom, center_x)
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
                # Mensaje recursivo / llamada interna
                p_sx = s_info[3] if s_info else start_x + 50
                p_ex = p_sx + 20
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
            # Conector estándar de relaciones (Association, Use Case, Dependency, Composition)
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

    # --- Diagrama 1: Home Page Navegación ---
    home_elements = [
        (3, 50, 60, 380, 160),   # Modulo Comercial
        (4, 450, 60, 780, 160),  # Modulo Siniestros
        (5, 850, 60, 1220, 160), # Modulo IA
        (6, 250, 260, 580, 360), # Dominio
        (7, 650, 260, 1020, 360) # Arquitectura Componentes
    ]
    for oid, l, t, r, b in home_elements:
        add_dobj(1, oid, l, t, r, b)
    add_conn("1. Planes y Clientes", "Dependency", 3, 4, 1)
    add_conn("2. Siniestros e Inferencia", "Dependency", 4, 5, 1)
    add_conn("3. Modelo de Dominio Compartido", "Dependency", 4, 6, 1)
    add_conn("4. Arquitectura Distribuida 4 Niveles", "Dependency", 5, 7, 1)

    # --- Diagrama 2: General de Casos de Uso (CU01 al CU15) ---
    ay = 50
    for aid, _ in actors:
        add_dobj(2, aid, 40, ay, 120, ay+80)
        ay += 105
    uy = 30
    for ucid, _, _ in use_cases:
        col = 240 if ucid <= 28 else (560 if ucid <= 32 else 880)
        row = (uy % 500) + 30
        add_dobj(2, ucid, col, row, col+280, row+65)
        uy += 80

    # Relaciones Actores a Use Cases en Diagrama 2
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

    # --- Robustez BCE para cada caso representativo (Diagramas 6 a 18) ---
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
        add_dobj(rdid, rbid, 50, 60, 220, 140)
        add_dobj(rdid, rcid, 320, 60, 540, 150)
        add_dobj(rdid, reid, 640, 60, 850, 140)
        add_conn(m1, "Association", rbid, rcid, rdid)
        add_conn(m2, "Association", rcid, reid, rdid)

    # --- Secuencia UML 2.5+ para Casos de Uso Clave (Diagramas 19 a 28) ---
    seq_defs = [
        (19, [(51, 60), (52, 280), (53, 500)], [
            ("1. ingresarCredenciales(usr, pwd)", 51, 52, -90),
            ("2. validarOAuthPKCE()", 52, 52, -135),
            ("3. emitirJWTRS256(claims)", 52, 53, -180),
            ("4. 200 OK (TokenBearer)", 52, 51, -225)
        ]),
        (20, [(60, 60), (61, 280), (62, 500)], [
            ("1. recibirMensajeWhatsApp(pedido)", 60, 61, -90),
            ("2. registrarPedidoEnERP()", 61, 61, -135),
            ("3. generarFacturaPDF(SHA256)", 61, 62, -180),
            ("4. enviarFacturaPorWhatsApp(pdfUrl)", 61, 60, -225)
        ]),
        (21, [(63, 60), (64, 270), (66, 480), (65, 690)], [
            ("1. procesarReporteEmergencia(dto)", 63, 64, -90),
            ("2. buscarPeritoMasCercano(25km)", 64, 66, -135),
            ("3. guardarExpediente(expDoc)", 64, 65, -180),
            ("4. 201 Created (SIN-2026-00050)", 64, 63, -225)
        ]),
        (22, [(67, 60), (68, 270), (70, 480), (69, 690)], [
            ("1. capturarEvidencia(cameraBytes)", 67, 68, -90),
            ("2. ejecutarInferenciaLocal(tensors)", 68, 70, -135),
            ("3. insertarInspeccionSQLite(key, hash)", 68, 69, -180),
            ("4. peritajeProtegidoOffline()", 68, 67, -225)
        ]),
        (23, [(71, 60), (72, 280), (73, 500), (65, 720)], [
            ("1. POST sync (Header: Idempotency-Key)", 71, 72, -90),
            ("2. GetItem(key) [DynamoDB <5ms]", 72, 73, -135),
            ("3. insertOne(expDoc) [MongoDB]", 72, 65, -180),
            ("4. UpdateItem(COMPLETED, 201)", 72, 73, -225),
            ("5. 201 Created / Cache HIT", 72, 71, -270)
        ]),
        (24, [(74, 60), (75, 260), (78, 460), (76, 660), (77, 860), (79, 1060)], [
            ("1. iniciarSagaLiquidacion(1200 BOB)", 74, 75, -90),
            ("2. guardarSaga(INICIADA)", 75, 78, -135),
            ("3. Paso 1: PATCH /bloquear-siniestro", 75, 76, -180),
            ("4. Paso 2: POST /bloquear-cobertura", 75, 77, -225),
            ("5. Paso 3: insertOrdenDesembolso(1080 BOB)", 75, 79, -270),
            ("6. [Rollback Kafka] CompensateCoverage", 75, 77, -315),
            ("7. [Rollback Kafka] RevertClaimStatus", 75, 76, -360),
            ("8. 200 OK / 422 Rollback Ejecutado", 75, 74, -405)
        ]),
        (25, [(81, 60), (82, 280), (73, 500), (83, 720)], [
            ("1. solicitarCobroQR(350 BOB)", 81, 82, -90),
            ("2. generarQREMVCo(Idempotency-Key)", 82, 81, -135),
            ("3. validarIdempotencia(key, hash)", 82, 73, -180),
            ("4. asentarTransaccionContable()", 82, 83, -225),
            ("5. comprobanteFiscal(REC-99120)", 82, 81, -270)
        ]),
        (26, [(84, 60), (85, 280), (86, 500)], [
            ("1. subirImagenVehiculoDanado(file)", 84, 85, -90),
            ("2. procesarConvolucionCrashNetCNN()", 85, 85, -135),
            ("3. guardarDiagnosticoIA(severidad, baremo)", 85, 86, -180),
            ("4. 200 OK (HeatmapGradCAM, Severidad)", 85, 84, -225)
        ]),
        (27, [(94, 60), (95, 280), (96, 500)], [
            ("1. leerMetricasSaludCluster()", 94, 95, -90),
            ("2. razonarGrafoEstadosLangGraph()", 95, 95, -135),
            ("3. actualizarEstadoCluster(state)", 95, 96, -180),
            ("4. ejecutarSkillRebalanceo()", 95, 94, -225)
        ]),
        (28, [(97, 60), (98, 280), (99, 500), (100, 720)], [
            ("1. dictarComandoVoz(audioBuffer)", 97, 98, -90),
            ("2. transcribirWhisperSTT()", 98, 98, -135),
            ("3. sanitizarFiltroAntiSQLi()", 98, 98, -180),
            ("4. invocarToolParametrizada(consultar)", 98, 99, -225),
            ("5. generarReporteXLSX_PDF(datos)", 99, 100, -270),
            ("6. 200 OK (EnlaceDescargaSegura)", 98, 97, -315)
        ])
    ]
    for sdid, lifelines, msgs in seq_defs:
        for l_obj_id, lx in lifelines:
            add_dobj(sdid, l_obj_id, lx, 40, lx+130, 480)
        s_no = 1
        for mname, sid, tid, py in msgs:
            add_conn(mname, "Sequence", sid, tid, sdid, seq_no=s_no, pt_y=py)
            s_no += 1

    # --- Diagrama 29: Modelo de Dominio Global ERP (Clases) ---
    dom_objs = [
        (53, 50, 40, 240, 130),
        (56, 290, 40, 480, 130),
        (59, 530, 40, 720, 130),
        (65, 770, 40, 960, 130),
        (69, 50, 200, 240, 290),
        (73, 290, 200, 480, 290),
        (78, 530, 200, 720, 290),
        (79, 770, 200, 960, 290),
        (80, 50, 360, 240, 450),
        (83, 290, 360, 480, 450),
        (86, 530, 360, 720, 450),
        (92, 770, 360, 960, 450)
    ]
    for oid, l, t, r, b in dom_objs:
        add_dobj(29, oid, l, t, r, b)
    add_conn("asociadoA", "Association", 53, 56, 29)
    add_conn("origina", "Association", 56, 59, 29)
    add_conn("cubre", "Association", 80, 65, 29)
    add_conn("documenta", "Association", 65, 69, 29)
    add_conn("protegidoPor", "Dependency", 69, 73, 29)
    add_conn("orquesta", "Association", 65, 78, 29)
    add_conn("emite", "Composition", 78, 79, 29)
    add_conn("controlIdempotencia", "Dependency", 83, 73, 29)
    add_conn("peritadoPorIA", "Association", 65, 86, 29)
    add_conn("evaluadoCluster", "Association", 65, 92, 29)

    # --- Diagrama 30: Componentes y Arquitectura Global en 4 Niveles ---
    comp_layout = [
        (101, 50, 50, 260, 160),   # Flutter
        (102, 50, 220, 260, 330),  # React PWA
        (103, 50, 390, 260, 500),  # Angular Admin
        (104, 350, 50, 580, 160),  # MS1 PHP
        (105, 350, 220, 580, 330), # MS2 NestJS
        (106, 350, 390, 580, 500), # MS3 Spring Boot
        (107, 350, 560, 580, 670), # MS4 Python FastAPI
        (108, 680, 220, 920, 380), # Persistencia Poliglota
        (109, 980, 220, 1220, 380) # Kafka y Gateway
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

    # Copiar a las ubicaciones del repositorio
    shutil.copy(target_qea, "AegisCore_Perfil_B.qea")
    shutil.copy(target_qea, "docs-iconix-uml/AegisCore_AI.qea")
    shutil.copy(target_qea, "docs-iconix-uml/AegisCore_Perfil_B.qea")
    shutil.copy(target_qea, "docs-iconix-uml/enterprise-architect/aegiscore-perfil-b-ea17.qea")

    print(f"Éxito: Modelo Global del Proyecto construido en {target_qea}")
    print(f"Total de Diagramas: {len(diagrams)} (Home Page, Casos de Uso, Robustez BCE, Secuencia UML 2.5+, Clases y Componentes)")
    print(f"Total de Conectores/Mensajes: {conn_counter}")

if __name__ == "__main__":
    build_qea()
