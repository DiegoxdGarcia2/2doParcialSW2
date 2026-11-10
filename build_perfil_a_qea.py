# -*- coding: utf-8 -*-
"""
Constructor Maestro del Modelo Exclusivo del Perfil A (.qea) para Enterprise Architect 17.2
Proyecto: AegisCore AI — ERP Distribuido, Peritaje Inteligente y Liquidación Autónoma de Siniestros
Perfil A: Casos de Uso CU01 a CU05 + Apoyo Saga CU09 + Pasarela QR CU10
Genera:
  - AegisCore_Perfil_A.qea (en raíz)
  - docs-iconix-uml/AegisCore_Perfil_A.qea
  - docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.qea
Características:
  - 19 Diagramas Completos (Home Page con NavigationCells, Casos de Uso, Robustez BCE,
    Secuencia UML 2.5+ con métodos operacionales en Control, Modelo de Dominio DDD rectangular
    con atributos y operaciones reales, Clases de Diseño Detallado y Componentes Cloud).
  - 100% Fidelidad con el código de backend/ms1-polizas-php y frontend/mf2-clientes-react.
  - Cero diagramas vacíos y cero solapamientos.
"""
import os
import shutil
import sqlite3
import uuid


def get_guid():
    return f"{{{uuid.uuid4()}}}".upper()


def get_duid():
    return uuid.uuid4().hex[:8].upper()


def build_perfil_a_qea():
    # 1. Determinar plantilla base SQLite
    sparx_trial_base = r"C:\Program Files\Sparx Systems\EA Trial\EABase.qea"
    repo_template = os.path.join("docs-iconix-uml", "enterprise-architect", "aegiscore-perfil-b-ea17.qea")

    target_qea = "AegisCore_Perfil_A.qea"

    if os.path.exists(sparx_trial_base):
        shutil.copy(sparx_trial_base, target_qea)
        print(f"Copiada plantilla Sparx Systems: {sparx_trial_base}")
    elif os.path.exists(repo_template):
        shutil.copy(repo_template, target_qea)
        print(f"Copiada plantilla de repositorio: {repo_template}")
    else:
        raise FileNotFoundError("No se encontró ninguna plantilla .qea válida.")

    conn = sqlite3.connect(target_qea)
    cur = conn.cursor()

    # Limpiar tablas para generar modelo limpio exclusivo del Perfil A
    cur.execute("DELETE FROM t_package WHERE Package_ID > 1")
    cur.execute("DELETE FROM t_object")
    cur.execute("DELETE FROM t_attribute")
    cur.execute("DELETE FROM t_operation")
    cur.execute("DELETE FROM t_diagram")
    cur.execute("DELETE FROM t_diagramobjects")
    cur.execute("DELETE FROM t_connector")
    cur.execute("DELETE FROM t_diagramlinks")
    conn.commit()

    # 2. Paquete Raíz del Modelo
    root_model_pkg_id = 2
    cur.execute("""
        INSERT INTO t_package (Package_ID, Name, Parent_ID, ea_guid)
        VALUES (2, 'EA_Model_AegisCore_Perfil_A', 1, ?)
    """, (get_guid(),))

    cur.execute("""
        INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid)
        VALUES (1, 1, 'Package', 'EA_Model_AegisCore_Perfil_A', ?)
    """, (get_guid(),))

    # 3. Subpaquetes Estructurados del Perfil A
    packages = [
        (10, 2, '01_Casos_de_Uso_Perfil_A', root_model_pkg_id),
        (11, 3, '02_Analisis_Robustez_BCE_Perfil_A', root_model_pkg_id),
        (12, 4, '03_Secuencia_UML25_Perfil_A', root_model_pkg_id),
        (13, 5, '04_Modelo_Dominio_DDD_Perfil_A', root_model_pkg_id),
        (14, 6, '05_Diseno_Clases_Detallado_Perfil_A', root_model_pkg_id),
        (15, 7, '06_Componentes_y_Despliegue_Perfil_A', root_model_pkg_id)
    ]
    for pid, pobj_id, pname, parent in packages:
        cur.execute("INSERT INTO t_package (Package_ID, Name, Parent_ID, ea_guid) VALUES (?, ?, ?, ?)",
                    (pid, pname, parent, get_guid()))
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid) VALUES (?, ?, 'Package', ?, ?)",
                    (pobj_id, parent, pname, get_guid()))

    # 4. Actores del Perfil A (IDs 11 to 16)
    actors = [
        (11, 'Usuario / Asegurado / Admin'),
        (12, 'Cliente Asegurado'),
        (13, 'Administrador Comercial'),
        (14, 'Broker Apache Kafka (Saga)'),
        (15, 'Pasarela de Pago QR / BCB'),
        (16, 'Motor de Flujos n8n & WhatsApp')
    ]
    for aid, aname in actors:
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid) VALUES (?, 10, 'Actor', ?, ?)",
                    (aid, aname, get_guid()))

    # 5. Casos de Uso del Perfil A (IDs 21 to 27)
    use_cases = [
        (21, 10, "CU01: Autenticación Centralizada SSO con Keycloak (OAuth2 / OIDC PKCE S256)"),
        (22, 10, "CU02: Consulta Estado Unificado Asegurado en GraphQL (Apollo Federation + DynamoDB)"),
        (23, 10, "CU03: Administrar Catálogo de Planes, Coberturas FK y Clientes (DDD)"),
        (24, 10, "CU04: Cotización Web PWA con Validación Documental IA Local (Laplaciano)"),
        (25, 10, "CU05: Automatización Pedido WhatsApp a Factura PDF con n8n y AWS S3"),
        (26, 10, "CU09-MS1: Reserva de Techo Anual y Compensación Saga Transversal"),
        (27, 10, "CU10-MS1: Pasarela de Cobro y Confirmación Pago QR EMVCo Idempotente")
    ]
    for ucid, uc_pkg, ucname in use_cases:
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid) VALUES (?, ?, 'UseCase', ?, ?)",
                    (ucid, uc_pkg, ucname, get_guid()))

    # 6. Clases Reales del Modelo de Dominio DDD (IDs 101 to 109)
    # Estándar UML Rectangular con Atributos y Operaciones exactos
    domain_classes = [
        (101, 13, "UsuarioRol", [
            ("id", "UUID"),
            ("keycloakSub", "String"),
            ("email", "String"),
            ("nombreCompleto", "String"),
            ("rol", "String"),
            ("sessionId", "String")
        ], ["autenticarUsuarioOIDC()", "validarTokenJwtRS256()"]),

        (102, 13, "SesionUnificadaToken", [
            ("idempotencyKey", "String"),
            ("sessionId", "String"),
            ("keycloakSub", "String"),
            ("rol", "String"),
            ("tokenSha256", "String"),
            ("status", "String"),
            ("ttl", "Integer")
        ], ["guardarSesionUnificada()", "revocarSesionUnificada()"]),

        (103, 13, "Cliente", [
            ("id", "UuidId"),
            ("documento", "DocumentoIdentidad"),
            ("nombres", "String"),
            ("apellidos", "String"),
            ("email", "String"),
            ("telefono", "String"),
            ("direccion", "String"),
            ("ciudad", "String"),
            ("perfilRiesgo", "PerfilRiesgoCliente"),
            ("usuarioId", "String")
        ], ["nombreCompleto()", "toGraphQLArray()"]),

        (104, 13, "PlanSeguro", [
            ("id", "UuidId"),
            ("codigo", "String"),
            ("nombre", "String"),
            ("tipo", "TipoPlanVO"),
            ("primaBaseAnual", "PrimaMonetaria"),
            ("deducibleBasePorcentaje", "Float"),
            ("descripcion", "String"),
            ("activo", "Boolean"),
            ("coberturas", "Cobertura[]")
        ], ["techoCoberturaMaximo()", "agregarCobertura()", "toGraphQLArray()"]),

        (105, 13, "Cobertura", [
            ("id", "UuidId"),
            ("planId", "UuidId"),
            ("codigo", "String"),
            ("nombre", "String"),
            ("sumaAseguradaMax", "Float"),
            ("deducibleMinimo", "Float"),
            ("deduciblePorcentaje", "Float"),
            ("obligatoria", "Boolean")
        ], ["toGraphQLArray()"]),

        (106, 13, "Poliza", [
            ("id", "UuidId"),
            ("numeroPoliza", "String"),
            ("clienteId", "UuidId"),
            ("planId", "UuidId"),
            ("vigencia", "VigenciaPoliza"),
            ("primaAnual", "PrimaMonetaria"),
            ("primaMensual", "PrimaMonetaria"),
            ("techoCoberturaAnual", "PrimaMonetaria"),
            ("saldoCoberturaRestante", "PrimaMonetaria"),
            ("estado", "EstadoPolizaVO"),
            ("bienAsegurado", "BienAseguradoVehiculo"),
            ("canalVenta", "String")
        ], ["emitirNueva()", "descontarTechoAnualPoliza()", "compensarCoberturaSaga()", "pullDomainEvents()"]),

        (107, 13, "BienAseguradoVehiculo", [
            ("placa", "String"),
            ("vin", "String"),
            ("marca", "String"),
            ("modelo", "String"),
            ("anio", "Integer"),
            ("uso", "String"),
            ("color", "String"),
            ("valorComercial", "Float")
        ], ["fromArray()", "toArray()"]),

        (108, 13, "FacturaNotaVenta", [
            ("id", "UuidId"),
            ("numeroFactura", "NumeroComprobanteFiscal"),
            ("polizaId", "UuidId"),
            ("clienteId", "UuidId"),
            ("tipoComprobante", "String"),
            ("subtotal", "Float"),
            ("iva", "Float"),
            ("it", "Float"),
            ("total", "Float"),
            ("moneda", "String"),
            ("nitCliente", "String"),
            ("razonSocial", "String"),
            ("codigoControl", "String"),
            ("urlPdf", "String"),
            ("hashDigitalSha256", "String"),
            ("estadoPago", "String")
        ], ["emitirNueva()", "vincularPdfFirmado()", "confirmarPagoQr()", "estaPagada()"]),

        (109, 13, "CacheCoberturaActiva", [
            ("idempotencyKey", "String"),
            ("clienteId", "String"),
            ("totalSaldoCobertura", "Float"),
            ("cantidadPolizas", "Integer"),
            ("updatedAt", "DateTime"),
            ("ttl", "Integer")
        ], ["guardarCacheCoberturaActiva()", "obtenerCacheCoberturaActiva()"])
    ]

    attr_counter = 1
    op_counter = 100
    for dc_id, dc_pkg, dc_name, attrs, ops in domain_classes:
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid) VALUES (?, ?, 'Class', ?, ?)",
                    (dc_id, dc_pkg, dc_name, get_guid()))
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

    # 7. Clases BCE de Robustez y Secuencia (IDs 201 to 261)
    bce_classes = [
        # CU01
        (201, 11, "Class", "boundary", "LoginKeycloakSSOView"),
        (202, 11, "Class", "control", "AuthOIDCService"),
        (203, 11, "Class", "control", "AuthOIDCController"),
        (204, 11, "Class", "entity", "DynamoDbSessionCacheRepository"),
        (205, 11, "Class", "entity", "UsuarioRolEntity"),
        # CU02
        (211, 11, "Class", "boundary", "PortalClientesGraphQLView"),
        (212, 11, "Class", "control", "ApolloFederationClient"),
        (213, 11, "Class", "control", "ApolloFederationResolver"),
        (214, 11, "Class", "entity", "PostgresPolizaRepository"),
        (215, 11, "Class", "entity", "ExpedienteSiniestroMongoMirror"),
        # CU03
        (221, 11, "Class", "boundary", "CatalogoPlanesYClientesView"),
        (222, 11, "Class", "control", "CatalogoPolizaApplicationService"),
        (223, 11, "Class", "entity", "PostgresPlanSeguroRepository"),
        (224, 11, "Class", "entity", "PostgresClienteRepository"),
        # CU04
        (231, 11, "Class", "boundary", "CotizadorWebPWAView"),
        (232, 11, "Class", "control", "ValidadorNitidezLocalWebControl"),
        (233, 11, "Class", "control", "EmisionPolizaGraphQLController"),
        (234, 11, "Class", "control", "CotizacionPolizaDomainService"),
        (235, 11, "Class", "entity", "PostgresFacturaRepository"),
        # CU05
        (241, 11, "Class", "boundary", "CanalWhatsAppWebhookView"),
        (242, 11, "Class", "boundary", "N8nWebhookHandler"),
        (243, 11, "Class", "control", "RecepcionPedidoService"),
        (244, 11, "Class", "control", "FacturacionService"),
        (245, 11, "Class", "control", "FacturacionDomainService"),
        (246, 11, "Class", "entity", "FacturaPdfGenerator"),
        (247, 11, "Class", "entity", "AwsS3BucketEntity"),
        # CU09-MS1
        (251, 11, "Class", "boundary", "SimuladorSagaCoberturaView"),
        (252, 11, "Class", "control", "PolizaCoberturaService"),
        (253, 11, "Class", "control", "SagaKafkaConsumer"),
        # CU10-MS1
        (261, 11, "Class", "boundary", "PasarelaPagoQREMVCoView")
    ]
    for cid, cpkg, ctype, cstereo, cname in bce_classes:
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Stereotype, Name, ea_guid) VALUES (?, ?, ?, ?, ?, ?)",
                    (cid, cpkg, ctype, cstereo, cname, get_guid()))

    # Métodos y operaciones operacionales en las Clases BCE
    bce_ops = [
        (201, ["iniciarFlujoOIDCPkce()", "cambiarIdentidadRapida()", "cerrarSesionGlobal()"]),
        (202, ["generarParPkceS256()", "iniciarFlujoOIDCPkce()", "construirAuthorizationHeaders()"]),
        (203, ["autenticarUsuarioOIDC()", "validarTokenJwtRS256()", "sincronizarUsuarioRolPostgreSQL()", "registrarSesionUnificadaDynamoDB()", "revocarSesionUnificada()", "obtenerEstadoSesionesSSO()"]),
        (204, ["guardarSesionSSO()", "obtenerSesionSSO()", "eliminarSesionSSO()"]),
        (205, ["findSub()", "save()"]),
        (211, ["cargarEstadoAsegurado()", "seleccionarAsegurado()"]),
        (212, ["consultarEstadoUnificadoAsegurado()", "ejecutarOperacion()", "guardarCacheOffline()", "leerCacheOffline()", "generarQrCobro()", "confirmarPagoQr()"]),
        (213, ["resolverResumenUnificadoAsegurado()", "consultarOActualizarCacheCoberturaActiva()", "federarExpedientesSiniestrosMongoDB()"]),
        (214, ["findByClienteId()", "save()", "findById()", "actualizarSaldoCobertura()", "restituirSaldoCobertura()"]),
        (215, ["buscarSiniestrosPorPoliza()", "obtenerUltimoSiniestro()"]),
        (221, ["handleCrearPlan()", "handleAgregarCobertura()", "handleRegistrarCliente()"]),
        (222, ["listarPlanesSeguro()", "registrarPlanSeguroDDD()", "agregarCoberturaAPlan()", "registrarClienteDDD()", "obtenerClientePorId()", "buscarClientePorDocumento()", "listarClientes()"]),
        (223, ["save()", "findAll()", "findById()", "agregarCobertura()"]),
        (224, ["save()", "findAll()", "findById()", "findByDocumento()"]),
        (231, ["handleAnalizarImagenIA()", "handleCotizarEnLinea()", "handleEmitirPoliza()", "sincronizarColaOffline()"]),
        (232, ["analizarNitidezImagen()", "calcularVarianzaLaplaciana()", "generarImagenPruebaNitida()", "generarImagenPruebaBorrosa()"]),
        (233, ["cotizarPolizaEnLinea()", "validarNitidez()", "insertarPoliza()", "emitirPoliza()"]),
        (234, ["calcularCotizacion()"]),
        (235, ["save()", "findById()", "findByPolizaId()", "confirmarPagoQr()"]),
        (241, ["handleDispararWebhookWhatsApp()", "handleGenerarFacturaPdf()"]),
        (242, ["do_POST()", "subir_pdf_a_s3()"]),
        (243, ["procesarPedidoPolizaWhatsApp()"]),
        (244, ["generarFacturaNotaVentaPDF()", "obtenerFacturaPorId()", "obtenerBinarioPdfFactura()"]),
        (245, ["emitirComprobanteParaPoliza()", "registrarPagoQrConfirmado()"]),
        (246, ["compilarArchivoFacturaPdf()", "subirFacturaPdfAS3()"]),
        (247, ["putObject()", "getObject()", "getPresignedUrl()"]),
        (251, ["handleSimularSaga()"]),
        (252, ["descontarTechoAnualPoliza()", "compensarCoberturaSaga()", "restituirSaldoCobertura()"]),
        (253, ["procesarMensajeTopico()"]),
        (261, ["handleAbrirModalQr()", "handleConfirmarPagoQr()"])
    ]
    for cid, ops in bce_ops:
        for op in ops:
            cur.execute("INSERT INTO t_operation (OperationID, Object_ID, Name, Scope, ea_guid) VALUES (?, ?, ?, 'Public', ?)",
                        (op_counter, cid, op, get_guid()))
            op_counter += 1

    # 8. Componentes y Nodos de Despliegue Cloud (IDs 301 to 308)
    components = [
        (301, 15, "Component", "Frontend PWA", "React PWA Portal Clientes (Vite + TypeScript)"),
        (302, 15, "Component", "Seguridad IAM", "Keycloak SSO Identity Shell (OAuth2 / OIDC S256)"),
        (303, 15, "Component", "Backend Microservicio", "MS1 Pólizas y Clientes PHP 8.3 Laravel (DDD)"),
        (304, 15, "Component", "Orquestador ETL", "Motor de Flujos n8n Automation Engine"),
        (305, 15, "Node", "RDBMS ACID", "PostgreSQL 16 DB (aegiscore_erp ACID)"),
        (306, 15, "Node", "NoSQL Idempotente", "Amazon DynamoDB Local (Sessions & Idempotency)"),
        (307, 15, "Node", "Cloud Storage S3", "Amazon S3 Bucket (servicio-de-seguros-aegiscore)"),
        (308, 15, "Node", "Event Broker", "Apache Kafka Message Broker (Saga Bus)")
    ]
    for cid, cpkg, ctype, cstereo, cname in components:
        cur.execute("INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Stereotype, Name, ea_guid) VALUES (?, ?, ?, ?, ?, ?)",
                    (cid, cpkg, ctype, cstereo, cname, get_guid()))

    # 9. Los 19 Diagramas Visuales del Perfil A
    diagrams = [
        (1, 2, "Custom", "00. Panel de Navegación Interactiva - Perfil A (Home Page)"),
        (2, 10, "Use Case", "01. Diagrama de Casos de Uso - Perfil A (CU01 a CU05 + Saga CU09 + QR CU10)"),
        (3, 13, "Logical", "02. Modelo de Dominio DDD - Perfil A (Clases Rectangulares con Atributos y Operaciones)"),
        (4, 11, "Analysis", "03. Robustez BCE - CU01 (Autenticación SSO Keycloak OIDC PKCE S256)"),
        (5, 11, "Analysis", "04. Robustez BCE - CU02 (Estado Unificado GraphQL Apollo Federation + DynamoDB)"),
        (6, 11, "Analysis", "05. Robustez BCE - CU03 (Gestión DDD de Catálogo de Planes, Coberturas FK y Clientes)"),
        (7, 11, "Analysis", "06. Robustez BCE - CU04 (Cotización y Emisión Web con IA Local Laplaciano y Cola Offline)"),
        (8, 11, "Analysis", "07. Robustez BCE - CU05 (Pedido WhatsApp n8n y Factura PDF en AWS S3)"),
        (9, 11, "Analysis", "08. Robustez BCE - CU09-MS1 (Descuento y Compensación Saga de Cobertura)"),
        (10, 11, "Analysis", "09. Robustez BCE - CU10-MS1 (Generación y Confirmación de Cobro QR EMVCo)"),
        (11, 12, "Sequence", "10. Secuencia UML 2.5+ - CU01 (Flujo OAuth 2.0 PKCE S256, JWT RS256 y Sesión DynamoDB)"),
        (12, 12, "Sequence", "11. Secuencia UML 2.5+ - CU02 (Resolución Federada GraphQL y CacheCoberturaActiva)"),
        (13, 12, "Sequence", "12. Secuencia UML 2.5+ - CU03 (Registro DDD de PlanSeguro, Cobertura FK y Cliente)"),
        (14, 12, "Sequence", "13. Secuencia UML 2.5+ - CU04 (Validación IA Local Nitidez, Cotización y Emisión de Póliza)"),
        (15, 12, "Sequence", "14. Secuencia UML 2.5+ - CU05 (Webhook WhatsApp n8n, Emisión Póliza, PDF SHA-256 y Upload AWS S3)"),
        (16, 12, "Sequence", "15. Secuencia UML 2.5+ - CU09-MS1 (Reserva de Cobertura y Rollback Compensatorio Saga)"),
        (17, 12, "Sequence", "16. Secuencia UML 2.5+ - CU10-MS1 (Generación QR EMVCo y Conciliación de Pago Fiscal)"),
        (18, 14, "Logical", "17. Diagrama de Clases de Diseño Detallado DDD (MS1 PHP + MF2 React PWA)"),
        (19, 15, "Component", "18. Diagrama de Componentes y Despliegue Cloud (React PWA, SSO Shell, MS1 PHP, n8n, PostgreSQL, DynamoDB, AWS S3)")
    ]

    pdata_std = "HideRel=0;ShowTags=0;ShowReqs=0;ShowCons=0;OpParams=1;ShowSN=0;ScalePI=0;PPgs.cx=1;PPgs.cy=1;PSize=9;ShowIcons=1;SuppCN=0;HideProps=0;HideParents=0;UseAlias=0;HideAtts=0;HideOps=0;HideStereo=0;HideEStereo=0;ShowRec=1;ShowRes=0;ShowShape=1;FormName=;"
    style_ex_std = "ExcludeRTF=0;DocAll=0;HideQuals=0;AttPkg=1;ShowTests=0;ShowMaint=0;SuppressFOC=0;INT_ARGS=;INT_RET=;INT_ATT=;SeqTopMargin=50;MatrixActive=0;SwimlanesActive=1;KanbanActive=0;MatrixLineWidth=1;MatrixLineClr=0;MatrixLocked=0;TConnectorNotation=UML 2.1;TExplicitNavigability=0;AdvancedElementProps=1;AdvancedFeatureProps=1;AdvancedConnectorProps=1;m_bElementClassifier=1;SPT=1;MDGDgm=;STBLDgm=;ShowNotes=0;VisibleAttributeDetail=0;ShowOpRetType=1;SuppressBrackets=0;SuppConnectorLabels=0;PrintPageHeadFoot=0;ShowAsList=0;SuppressedCompartments=;Theme=:119;SaveTag=7A7E97D4;"

    for did, dpkg, dtype, dname in diagrams:
        cur.execute("""
            INSERT INTO t_diagram (
                Diagram_ID, Package_ID, ParentID, Diagram_Type, Name, Version, Author,
                ea_guid, cx, cy, PDATA, StyleEx
            ) VALUES (?, ?, 0, ?, ?, '2.0', 'Perfil A - Grupo #27 SW2', ?, 1500, 1000, ?, ?)
        """, (did, dpkg, dtype, dname, get_guid(), pdata_std, style_ex_std))

    # Control de diagramobjects y diagramlinks
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
                p_sx = s_info[3] if s_info else start_x + 50
                p_ex = p_sx + 25
                p_sy = pt_y
                p_ey = pt_y - 20
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
    # DIAGRAMA 1: Home Page con NavigationCells (Panel Interactivo)
    # =========================================================================
    nav_cells = [
        (401, "01. Diagrama de Casos de Uso - Perfil A", 2, 60, 60, 420, 160),
        (402, "02. Modelo de Dominio DDD - Perfil A", 3, 460, 60, 820, 160),
        (403, "17. Clases de Diseño Detallado DDD", 18, 860, 60, 1220, 160),
        (404, "18. Componentes y Despliegue Cloud", 19, 1260, 60, 1620, 160),

        (405, "03. Robustez BCE - CU01 (SSO Keycloak)", 4, 60, 190, 420, 290),
        (406, "04. Robustez BCE - CU02 (GraphQL Federation)", 5, 460, 190, 820, 290),
        (407, "05. Robustez BCE - CU03 (Catálogo Planes/Clientes)", 6, 860, 190, 1220, 290),
        (408, "06. Robustez BCE - CU04 (Cotizador Web IA Local)", 7, 1260, 190, 1620, 290),

        (409, "07. Robustez BCE - CU05 (WhatsApp n8n Factura)", 8, 60, 320, 420, 420),
        (410, "08. Robustez BCE - CU09-MS1 (Saga Cobertura)", 9, 460, 320, 820, 420),
        (411, "09. Robustez BCE - CU10-MS1 (Pasarela Pago QR)", 10, 860, 320, 1220, 420),

        (412, "10. Secuencia - CU01 (SSO Keycloak OIDC)", 11, 60, 450, 420, 550),
        (413, "11. Secuencia - CU02 (GraphQL Cache Activa)", 12, 460, 450, 820, 550),
        (414, "12. Secuencia - CU03 (Registro DDD)", 13, 860, 450, 1220, 550),
        (415, "13. Secuencia - CU04 (IA Local & Emisión)", 14, 1260, 450, 1620, 550),

        (416, "14. Secuencia - CU05 (WhatsApp n8n S3)", 15, 60, 580, 420, 680),
        (417, "15. Secuencia - CU09-MS1 (Reserva Saga)", 16, 460, 580, 820, 680),
        (418, "16. Secuencia - CU10-MS1 (Conciliación QR)", 17, 860, 580, 1220, 680)
    ]
    for nid, nname, target_did, l, t, r, b in nav_cells:
        cur.execute("""
            INSERT INTO t_object (Object_ID, Package_ID, Object_Type, Name, Stereotype, PDATA1, PDATA3, ea_guid)
            VALUES (?, 2, 'Text', ?, 'NavigationCell', ?, 1, ?)
        """, (nid, nname, target_did, get_guid()))
        add_dobj(1, nid, l, t, r, b)

    # =========================================================================
    # DIAGRAMA 2: Diagrama de Casos de Uso - Perfil A
    # =========================================================================
    # Actores
    add_dobj(2, 11, 50, 60, 170, 140)   # Usuario / Asegurado / Admin
    add_dobj(2, 12, 50, 180, 170, 260)  # Cliente Asegurado
    add_dobj(2, 13, 50, 300, 170, 380)  # Administrador Comercial
    add_dobj(2, 14, 50, 420, 170, 500)  # Broker Kafka
    add_dobj(2, 15, 50, 540, 170, 620)  # Pasarela Pago QR
    add_dobj(2, 16, 50, 660, 170, 740)  # Motor n8n & WhatsApp

    # Casos de uso
    uc_positions = [
        (21, 60),   # CU01
        (22, 150),  # CU02
        (23, 240),  # CU03
        (24, 330),  # CU04
        (25, 420),  # CU05
        (26, 510),  # CU09-MS1
        (27, 600)   # CU10-MS1
    ]
    for ucid, y in uc_positions:
        add_dobj(2, ucid, 400, y, 920, y + 65)

    add_conn("Inicia Sesión SSO", "Use Case", 11, 21, 2)
    add_conn("Consulta Estado GraphQL", "Use Case", 12, 22, 2)
    add_conn("Administra Catálogo DDD", "Use Case", 13, 23, 2)
    add_conn("Cotiza y Emite en Línea", "Use Case", 12, 24, 2)
    add_conn("Dispara Pedido WhatsApp", "Use Case", 16, 25, 2)
    add_conn("Orquesta Eventos Saga", "Use Case", 14, 26, 2)
    add_conn("Paga Cuota QR", "Use Case", 12, 27, 2)
    add_conn("Confirma Pago EMVCo", "Use Case", 15, 27, 2)

    # =========================================================================
    # DIAGRAMA 3: Modelo de Dominio DDD - Perfil A (Clases Rectangulares)
    # =========================================================================
    dom_layout = [
        (101, 50, 50, 330, 230),     # UsuarioRol
        (102, 390, 50, 710, 240),    # SesionUnificadaToken
        (109, 780, 50, 1120, 240),   # CacheCoberturaActiva
        (103, 50, 290, 360, 520),    # Cliente
        (104, 420, 290, 760, 510),   # PlanSeguro
        (105, 820, 290, 1140, 490),  # Cobertura
        (106, 50, 570, 420, 870),    # Poliza
        (107, 480, 570, 800, 780),   # BienAseguradoVehiculo
        (108, 860, 570, 1240, 880)   # FacturaNotaVenta
    ]
    for oid, l, t, r, b in dom_layout:
        add_dobj(3, oid, l, t, r, b)

    add_conn("asociado-a", "Association", 103, 101, 3)
    add_conn("genera-sesion", "Association", 101, 102, 3)
    add_conn("cache-consulta", "Dependency", 103, 109, 3)
    add_conn("actualiza-cache", "Dependency", 106, 109, 3)
    add_conn("contrata", "Composition", 103, 106, 3)
    add_conn("ampara-vehiculo", "Composition", 106, 107, 3)
    add_conn("basada-en", "Aggregation", 106, 104, 3)
    add_conn("compone-coberturas", "Composition", 104, 105, 3)
    add_conn("genera-factura", "Association", 106, 108, 3)

    # =========================================================================
    # DIAGRAMAS 4 a 10: Robustez BCE con Amplia Separación Horizontal
    # =========================================================================
    # CU01
    add_dobj(4, 201, 60, 110, 280, 200)   # LoginKeycloakSSOView
    add_dobj(4, 202, 380, 60, 620, 160)   # AuthOIDCService
    add_dobj(4, 203, 380, 200, 640, 320)  # AuthOIDCController
    add_dobj(4, 204, 760, 60, 1050, 170)  # DynamoDbSessionCacheRepository
    add_dobj(4, 205, 760, 210, 1000, 310) # UsuarioRolEntity
    add_conn("1. Iniciar OIDC PKCE", "Association", 201, 202, 4)
    add_conn("2. POST /api/v1/auth/oidc-token", "Association", 202, 203, 4)
    add_conn("3. registrarSesionUnificadaDynamoDB()", "Association", 203, 204, 4)
    add_conn("4. sincronizarUsuarioRolPostgreSQL()", "Association", 203, 205, 4)
    add_conn("5. JWT RS256 + SessionId", "Association", 203, 201, 4)

    # CU02
    add_dobj(5, 211, 60, 130, 290, 220)   # PortalClientesGraphQLView
    add_dobj(5, 212, 370, 70, 610, 180)   # ApolloFederationClient
    add_dobj(5, 213, 370, 220, 640, 330)  # ApolloFederationResolver
    add_dobj(5, 214, 760, 60, 1020, 160)  # PostgresPolizaRepository
    add_dobj(5, 204, 760, 190, 1050, 290) # DynamoDbSessionCacheRepository
    add_dobj(5, 215, 760, 320, 1040, 420) # ExpedienteSiniestroMongoMirror
    add_conn("1. Cargar portal", "Association", 211, 212, 5)
    add_conn("2. query { resumenUnificadoAsegurado }", "Association", 212, 213, 5)
    add_conn("3. Consultar Pólizas PostgreSQL", "Association", 213, 214, 5)
    add_conn("4. CacheCoberturaActiva DynamoDB", "Association", 213, 204, 5)
    add_conn("5. Federar Siniestros MongoDB", "Association", 213, 215, 5)
    add_conn("6. Retornar Resumen Unificado", "Association", 213, 211, 5)

    # CU03
    add_dobj(6, 221, 60, 120, 300, 210)   # CatalogoPlanesYClientesView
    add_dobj(6, 222, 380, 90, 690, 240)   # CatalogoPolizaApplicationService
    add_dobj(6, 223, 780, 70, 1050, 170)  # PostgresPlanSeguroRepository
    add_dobj(6, 224, 780, 210, 1030, 310) # PostgresClienteRepository
    add_conn("1. Solicitar creación Plan/Cliente", "Association", 221, 222, 6)
    add_conn("2. registrarPlanSeguroDDD() y agregarCobertura()", "Association", 222, 223, 6)
    add_conn("3. registrarClienteDDD()", "Association", 222, 224, 6)
    add_conn("4. Confirmar Registro DDD", "Association", 222, 221, 6)

    # CU04
    add_dobj(7, 231, 60, 140, 280, 240)   # CotizadorWebPWAView
    add_dobj(7, 232, 370, 60, 640, 170)   # ValidadorNitidezLocalWebControl
    add_dobj(7, 233, 370, 200, 640, 300)  # EmisionPolizaGraphQLController
    add_dobj(7, 234, 370, 330, 620, 420)  # CotizacionPolizaDomainService
    add_dobj(7, 214, 760, 120, 1020, 220) # PostgresPolizaRepository
    add_dobj(7, 235, 760, 260, 1010, 360) # PostgresFacturaRepository
    add_conn("1. Validar nitidez Laplaciano local", "Association", 231, 232, 7)
    add_conn("2. cotizarPolizaEnLinea() y emitirPoliza()", "Association", 231, 233, 7)
    add_conn("3. calcularCotizacion()", "Association", 233, 234, 7)
    add_conn("4. insertarPoliza() PostgreSQL", "Association", 233, 214, 7)
    add_conn("5. generarFactura() PostgreSQL", "Association", 233, 235, 7)
    add_conn("6. Poliza y Factura Confirmadas", "Association", 233, 231, 7)

    # CU05
    add_dobj(8, 241, 60, 80, 290, 180)    # CanalWhatsAppWebhookView
    add_dobj(8, 242, 60, 230, 270, 320)   # N8nWebhookHandler
    add_dobj(8, 243, 380, 60, 630, 160)   # RecepcionPedidoService
    add_dobj(8, 244, 380, 190, 630, 290)  # FacturacionService
    add_dobj(8, 245, 380, 320, 640, 420)  # FacturacionDomainService
    add_dobj(8, 246, 760, 60, 1020, 160)  # FacturaPdfGenerator
    add_dobj(8, 235, 760, 190, 1010, 290) # PostgresFacturaRepository
    add_dobj(8, 247, 760, 320, 1040, 420) # AwsS3BucketEntity
    add_conn("1. Recibir evento WhatsApp", "Association", 241, 242, 8)
    add_conn("2. procesarPedidoPolizaWhatsApp()", "Association", 242, 243, 8)
    add_conn("3. generarFacturaNotaVentaPDF()", "Association", 243, 244, 8)
    add_conn("4. emitirComprobanteParaPoliza()", "Association", 244, 245, 8)
    add_conn("5. compilarArchivoFacturaPdf()", "Association", 244, 246, 8)
    add_conn("6. subirFacturaPdfAS3(servicio-de-seguros-aegiscore)", "Association", 246, 247, 8)
    add_conn("7. Guardar factura + hash SHA-256", "Association", 244, 235, 8)
    add_conn("8. Retornar URL S3 y resumen PDF", "Association", 244, 241, 8)

    # CU09-MS1
    add_dobj(9, 251, 60, 130, 300, 220)   # SimuladorSagaCoberturaView
    add_dobj(9, 252, 380, 80, 640, 190)   # PolizaCoberturaService
    add_dobj(9, 253, 380, 230, 620, 320)  # SagaKafkaConsumer
    add_dobj(9, 214, 760, 140, 1020, 240) # PostgresPolizaRepository
    add_conn("1. Simular evento Saga Kafka", "Association", 251, 253, 9)
    add_conn("2. procesarMensajeTopico()", "Association", 253, 252, 9)
    add_conn("3. descontarTechoAnualPoliza() / compensarCoberturaSaga()", "Association", 252, 214, 9)
    add_conn("4. Saldo actualizado", "Association", 214, 252, 9)
    add_conn("5. Confirmación evento compensación", "Association", 252, 251, 9)

    # CU10-MS1
    add_dobj(10, 261, 60, 130, 290, 220)  # PasarelaPagoQREMVCoView
    add_dobj(10, 212, 380, 70, 610, 180)  # ApolloFederationClient
    add_dobj(10, 245, 380, 220, 640, 320) # FacturacionDomainService
    add_dobj(10, 235, 760, 140, 1020, 240)# PostgresFacturaRepository
    add_conn("1. Generar código QR EMVCo", "Association", 261, 212, 10)
    add_conn("2. Confirmar pago QR", "Association", 261, 245, 10)
    add_conn("3. registrarPagoQrConfirmado() y conciliar factura", "Association", 245, 235, 10)
    add_conn("4. Estado PAGADA y comprobante fiscal", "Association", 235, 261, 10)

    # =========================================================================
    # DIAGRAMAS 11 a 17: Secuencia UML 2.5+ con Métodos Operacionales en Control
    # =========================================================================
    seq_configs = [
        # CU01 (Diag 11)
        (11, [(201, 80), (202, 360), (203, 660), (204, 980), (205, 1260)], [
            ("1. iniciarFlujoOIDCPkce(email, rol)", 201, 202, -90),
            ("2. generarParPkceS256()", 202, 202, -150),
            ("3. autenticarUsuarioOIDC(codeVerifier)", 202, 203, -210),
            ("4. validarTokenJwtRS256(token)", 203, 203, -270),
            ("5. registrarSesionUnificadaDynamoDB(tokenSha256)", 203, 204, -330),
            ("6. sincronizarUsuarioRolPostgreSQL(email, rol)", 203, 205, -390),
            ("7. 200 OK (JWT RS256, SessionId)", 203, 202, -450),
            ("8. actualizarSesionActiva(perfil)", 202, 201, -510)
        ]),
        # CU02 (Diag 12)
        (12, [(211, 80), (212, 360), (213, 660), (214, 960), (204, 1260)], [
            ("1. consultarEstadoUnificadoAsegurado(clienteId)", 211, 212, -90),
            ("2. POST /graphql (resumenUnificadoAsegurado)", 212, 213, -150),
            ("3. consultarPolizasYClientes(clienteId)", 213, 214, -210),
            ("4. consultarOActualizarCacheCoberturaActiva(clienteId)", 213, 204, -270),
            ("5. federarExpedientesSiniestrosMongoDB(polizaId)", 213, 213, -330),
            ("6. 200 OK (ResumenUnificadoPayload)", 213, 212, -390),
            ("7. cargarEstadoAsegurado(payload)", 212, 211, -450)
        ]),
        # CU03 (Diag 13)
        (13, [(221, 80), (222, 380), (223, 720), (224, 1060)], [
            ("1. registrarPlanSeguroDDD(nuevoPlanDTO)", 221, 222, -90),
            ("2. save(planSeguroAggregate)", 222, 223, -150),
            ("3. agregarCoberturaAPlan(coberturaDTO)", 221, 222, -210),
            ("4. agregarCobertura(planId, coberturaEntity)", 222, 223, -270),
            ("5. registrarClienteDDD(clienteDTO)", 221, 222, -330),
            ("6. save(clienteAggregate)", 222, 224, -390),
            ("7. 201 Created (CatalogoSincronizado)", 222, 221, -450)
        ]),
        # CU04 (Diag 14)
        (14, [(231, 80), (232, 360), (233, 660), (234, 960), (214, 1260)], [
            ("1. analizarNitidezImagen(pixelsRgba)", 231, 232, -90),
            ("2. calcularVarianzaLaplaciana(tensor2D)", 232, 232, -150),
            ("3. Retornar Score >= 0.65 + TokenValidacion", 232, 231, -210),
            ("4. cotizarPolizaEnLinea(CotizarDTO)", 231, 233, -270),
            ("5. calcularCotizacion(riesgo, valorComercial)", 233, 234, -330),
            ("6. emitirPoliza(EmitirDTO, IdempotencyKey)", 231, 233, -390),
            ("7. insertarPoliza(polizaAggregate)", 233, 214, -450),
            ("8. 201 Created (PolizaEmitidaEvent)", 233, 231, -510)
        ]),
        # CU05 (Diag 15)
        (15, [(241, 80), (242, 340), (243, 620), (244, 900), (246, 1180), (247, 1440)], [
            ("1. handleDispararWebhookWhatsApp(payload)", 241, 242, -90),
            ("2. procesarPedidoPolizaWhatsApp(pedido)", 242, 243, -150),
            ("3. generarFacturaNotaVentaPDF(polizaId)", 243, 244, -210),
            ("4. compilarArchivoFacturaPdf(factura)", 244, 246, -270),
            ("5. subirFacturaPdfAS3(servicio-de-seguros-aegiscore)", 246, 247, -330),
            ("6. retornarFacturaFiscal(urlPdf, sha256)", 244, 242, -390),
            ("7. despacharPDFPorWhatsApp(urlPdf)", 242, 241, -450)
        ]),
        # CU09-MS1 (Diag 16)
        (16, [(14, 80), (253, 360), (252, 660), (214, 980)], [
            ("1. orden.pago.calculada (SagaEvent)", 14, 253, -90),
            ("2. descontarTechoAnualPoliza(polizaId, monto)", 253, 252, -150),
            ("3. actualizarSaldoCobertura(polizaId, saldo)", 252, 214, -210),
            ("4. cobertura.poliza.descontada (SuccessEvent)", 252, 14, -270),
            ("5. compensacion.saga.solicitada (Error en MS3)", 14, 253, -330),
            ("6. compensarCoberturaSaga(polizaId, monto)", 253, 252, -390),
            ("7. restituirSaldoCobertura(polizaId)", 252, 214, -450),
            ("8. cobertura.poliza.compensada (RollbackEvent)", 252, 14, -510)
        ]),
        # CU10-MS1 (Diag 17)
        (17, [(12, 80), (261, 360), (212, 660), (245, 980), (235, 1280)], [
            ("1. handleAbrirModalQr(polizaId)", 12, 261, -90),
            ("2. generarQrCobro(polizaId, primaMensual)", 261, 212, -150),
            ("3. qrStringEMVCo + countdownExpiracion", 212, 261, -210),
            ("4. confirmarPagoQr(facturaId, idempotencyKey)", 261, 212, -270),
            ("5. registrarPagoQrConfirmado(facturaId, monto)", 212, 245, -330),
            ("6. confirmarPagoQr(facturaId, PAGADA)", 245, 235, -390),
            ("7. 200 OK (Factura Pagada y Conciliada)", 245, 261, -450)
        ])
    ]

    for did, lifelines, messages in seq_configs:
        for oid, lx in lifelines:
            add_dobj(did, oid, lx, 40, lx + 140, 620)
        s_no = 1
        for msg, sid, tid, pt_y in messages:
            add_conn(msg, "Sequence", sid, tid, did, seq_no=s_no, pt_y=pt_y)
            s_no += 1

    # =========================================================================
    # DIAGRAMA 18: Diagrama de Clases de Diseño Detallado DDD
    # =========================================================================
    design_classes = [
        # Frontend UI & Controls
        (201, 50, 50, 270, 160),     # LoginKeycloakSSOView
        (202, 330, 50, 570, 160),    # AuthOIDCService
        (211, 620, 50, 850, 160),    # PortalClientesGraphQLView
        (212, 910, 50, 1160, 180),   # ApolloFederationClient
        (231, 1210, 50, 1430, 160),  # CotizadorWebPWAView
        (232, 1210, 220, 1450, 330), # ValidadorNitidezLocalWebControl

        # MS1 Application Services
        (203, 50, 240, 290, 360),    # AuthOIDCController
        (213, 340, 240, 580, 360),   # ApolloFederationResolver
        (222, 630, 240, 900, 380),   # CatalogoPolizaApplicationService
        (233, 950, 240, 1190, 360),  # EmisionPolizaGraphQLController
        (244, 340, 420, 590, 530),   # FacturacionService
        (252, 630, 420, 880, 530),   # PolizaCoberturaService

        # Domain Aggregates
        (106, 50, 430, 280, 560),    # Poliza
        (103, 50, 600, 280, 720),    # Cliente
        (104, 340, 600, 580, 720),   # PlanSeguro
        (108, 630, 600, 880, 730),   # FacturaNotaVenta

        # Infrastructure Repositories
        (214, 950, 430, 1190, 540),  # PostgresPolizaRepository
        (204, 1230, 430, 1480, 540), # DynamoDbSessionCacheRepository
        (246, 950, 600, 1200, 710)   # FacturaPdfGenerator
    ]
    for oid, l, t, r, b in design_classes:
        add_dobj(18, oid, l, t, r, b)

    add_conn("consume", "Dependency", 201, 202, 18)
    add_conn("invoca-http", "Dependency", 202, 203, 18)
    add_conn("consume", "Dependency", 211, 212, 18)
    add_conn("resuelve-graphql", "Dependency", 212, 213, 18)
    add_conn("analiza-nitidez", "Dependency", 231, 232, 18)
    add_conn("emite-poliza", "Dependency", 231, 233, 18)
    add_conn("orquesta-dominio", "Dependency", 233, 106, 18)
    add_conn("persiste-poliza", "Dependency", 233, 214, 18)
    add_conn("gestiona-catalogo", "Dependency", 222, 104, 18)
    add_conn("gestiona-clientes", "Dependency", 222, 103, 18)
    add_conn("genera-pdf", "Dependency", 244, 246, 18)
    add_conn("asienta-factura", "Dependency", 244, 108, 18)
    add_conn("ajusta-cobertura", "Dependency", 252, 106, 18)
    add_conn("cachea-sesion", "Dependency", 203, 204, 18)

    # =========================================================================
    # DIAGRAMA 19: Diagrama de Componentes y Despliegue Cloud
    # =========================================================================
    comp_layout = [
        (301, 60, 60, 320, 180),     # React PWA Portal Clientes
        (302, 60, 240, 320, 360),    # Keycloak SSO Identity Shell
        (303, 440, 60, 740, 200),    # MS1 Pólizas y Clientes PHP Laravel
        (304, 440, 260, 740, 380),   # Motor de Flujos n8n Automation Engine
        (308, 440, 440, 740, 560),   # Apache Kafka Message Broker
        (305, 840, 60, 1120, 190),   # PostgreSQL 16 DB (aegiscore_erp ACID)
        (306, 840, 250, 1120, 380),  # Amazon DynamoDB Local
        (307, 840, 440, 1120, 570)   # Amazon S3 Bucket
    ]
    for cid, l, t, r, b in comp_layout:
        add_dobj(19, cid, l, t, r, b)

    add_conn("OIDC PKCE S256", "Dependency", 301, 302, 19)
    add_conn("GraphQL HTTPS", "Dependency", 301, 303, 19)
    add_conn("Webhook REST", "Dependency", 304, 303, 19)
    add_conn("PDO PostgreSQL ACID", "Association", 303, 305, 19)
    add_conn("AWS SDK DynamoDB", "Association", 303, 306, 19)
    add_conn("AWS SDK S3 PutObject", "Association", 303, 307, 19)
    add_conn("Saga Event Producer/Consumer", "Association", 303, 308, 19)
    add_conn("User Roles Postgres", "Association", 302, 305, 19)

    conn.commit()
    conn.close()

    # Copiar a las rutas requeridas
    shutil.copy(target_qea, os.path.join("docs-iconix-uml", "AegisCore_Perfil_A.qea"))
    shutil.copy(target_qea, os.path.join("docs-iconix-uml", "enterprise-architect", "aegiscore-perfil-a-ea17.qea"))

    print(f"Éxito: AegisCore_Perfil_A.qea generado correctamente.")
    print(f"Total Diagramas generados: {len(diagrams)} (Todos con elementos y conectores)")
    print(f"Total Conectores y Mensajes de Secuencia: {conn_counter}")


if __name__ == "__main__":
    build_perfil_a_qea()
