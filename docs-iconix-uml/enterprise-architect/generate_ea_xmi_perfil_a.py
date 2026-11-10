# -*- coding: utf-8 -*-
"""
Generador de Modelo XML/XMI 2.1 para Enterprise Architect 17.2
Proyecto: AegisCore AI - Perfil A (CU01 al CU05 + Saga CU09 + QR CU10)
ICONIX + UML 2.5+: Casos de Uso, Diagramas de Robustez BCE, Diagramas de Secuencia,
Modelo de Dominio DDD y Arquitectura de Componentes
Genera:
  - docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.xmi
  - docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.xml
  - docs-iconix-uml/aegiscore-perfil-a-iconix-uml25.xmi
"""
import os
import shutil
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom


def gen_id(prefix="EAID"):
    return f"{prefix}_{uuid.uuid4().hex[:8].upper()}"


def build_xmi_perfil_a():
    xmi = ET.Element("xmi:XMI", {
        "xmi:version": "2.1",
        "xmlns:uml": "http://schema.omg.org/spec/UML/2.1",
        "xmlns:xmi": "http://schema.omg.org/spec/XMI/2.1"
    })

    ET.SubElement(xmi, "xmi:Documentation", {
        "exporter": "Enterprise Architect",
        "exporterVersion": "17.2",
        "name": "AegisCore_AI_Perfil_A_ICONIX"
    })

    model = ET.SubElement(xmi, "uml:Model", {
        "xmi:type": "uml:Model",
        "name": "EA_Model_AegisCore_Perfil_A",
        "visibility": "public"
    })

    # Actores Globales del Perfil A
    actores = [
        ("EAID_ACT_USUARIO", "Usuario / Asegurado / Admin"),
        ("EAID_ACT_ASEGURADO", "Cliente Asegurado"),
        ("EAID_ACT_ADMIN_COMERCIAL", "Administrador Comercial"),
        ("EAID_ACT_KAFKA_SAGA", "Broker Apache Kafka (Saga)"),
        ("EAID_ACT_PAGOS_QR", "Pasarela de Pago QR / BCB"),
        ("EAID_ACT_WHATSAPP_N8N", "Motor de Flujos n8n & WhatsApp")
    ]
    for aid, aname in actores:
        ET.SubElement(model, "packagedElement", {
            "xmi:type": "uml:Actor", "xmi:id": aid, "name": aname, "visibility": "public"
        })

    # Paquete Casos de Uso
    pkg_uc = ET.SubElement(model, "packagedElement", {
        "xmi:type": "uml:Package", "xmi:id": "EAID_PKG_USECASES_A", "name": "01_Casos_de_Uso_Perfil_A"
    })

    usecases = [
        ("EAID_UC01", "CU01: Autenticación Centralizada SSO con Keycloak (OAuth2 / OIDC PKCE S256)"),
        ("EAID_UC02", "CU02: Consulta Estado Unificado Asegurado en GraphQL (Apollo Federation + DynamoDB)"),
        ("EAID_UC03", "CU03: Administrar Catálogo de Planes, Coberturas FK y Clientes (DDD)"),
        ("EAID_UC04", "CU04: Cotización Web PWA con Validación Documental IA Local (Laplaciano)"),
        ("EAID_UC05", "CU05: Automatización Pedido WhatsApp a Factura PDF con n8n y AWS S3"),
        ("EAID_UC09", "CU09-MS1: Reserva de Techo Anual y Compensación Saga Transversal"),
        ("EAID_UC10", "CU10-MS1: Pasarela de Cobro y Confirmación Pago QR EMVCo Idempotente")
    ]
    for ucid, ucname in usecases:
        ET.SubElement(pkg_uc, "packagedElement", {
            "xmi:type": "uml:UseCase", "xmi:id": ucid, "name": ucname, "visibility": "public"
        })

    # Paquete Análisis y Diseño ICONIX (BCE)
    pkg_iconix = ET.SubElement(model, "packagedElement", {
        "xmi:type": "uml:Package", "xmi:id": "EAID_PKG_ICONIX_A", "name": "02_Analisis_y_Diseno_ICONIX_BCE"
    })

    # Módulos BCE por Caso de Uso
    cu_modules = [
        {
            "id": "EAID_PKG_BCE_CU01",
            "name": "CU01_Autenticacion_SSO_Keycloak_OIDC_PKCE",
            "boundaries": [
                ("EAID_B_CU01_1", "LoginKeycloakSSOView", ["iniciarFlujoOIDCPkce()", "cambiarIdentidadRapida()", "cerrarSesionGlobal()"])
            ],
            "controls": [
                ("EAID_C_CU01_1", "AuthOIDCService", ["generarParPkceS256()", "iniciarFlujoOIDCPkce()", "construirAuthorizationHeaders()"]),
                ("EAID_C_CU01_2", "AuthOIDCController", ["autenticarUsuarioOIDC()", "validarTokenJwtRS256()", "sincronizarUsuarioRolPostgreSQL()", "registrarSesionUnificadaDynamoDB()", "revocarSesionUnificada()", "obtenerEstadoSesionesSSO()"])
            ],
            "entities": [
                ("EAID_E_CU01_1", "DynamoDbSessionCacheRepository", [("tableName", "String"), ("endpoint", "String"), ("awsRegion", "String")], ["guardarSesionSSO()", "obtenerSesionSSO()", "eliminarSesionSSO()"]),
                ("EAID_E_CU01_2", "UsuarioRolEntity", [("id", "UUID"), ("keycloakSub", "String"), ("email", "String"), ("rol", "String")], ["findSub()", "save()"])
            ]
        },
        {
            "id": "EAID_PKG_BCE_CU02",
            "name": "CU02_Estado_Unificado_GraphQL_Federation",
            "boundaries": [
                ("EAID_B_CU02_1", "PortalClientesGraphQLView", ["cargarEstadoAsegurado()", "seleccionarAsegurado()"])
            ],
            "controls": [
                ("EAID_C_CU02_1", "ApolloFederationClient", ["consultarEstadoUnificadoAsegurado()", "ejecutarOperacion()", "guardarCacheOffline()", "leerCacheOffline()"]),
                ("EAID_C_CU02_2", "ApolloFederationResolver", ["resolverResumenUnificadoAsegurado()", "consultarOActualizarCacheCoberturaActiva()", "federarExpedientesSiniestrosMongoDB()"])
            ],
            "entities": [
                ("EAID_E_CU02_1", "PostgresPolizaRepository", [("dbConnection", "PDO"), ("tableName", "String")], ["findByClienteId()", "save()", "findById()", "actualizarSaldoCobertura()", "restituirSaldoCobertura()"]),
                ("EAID_E_CU02_2", "ExpedienteSiniestroMongoMirror", [("mongoUri", "String"), ("collectionName", "String")], ["buscarSiniestrosPorPoliza()", "obtenerUltimoSiniestro()"])
            ]
        },
        {
            "id": "EAID_PKG_BCE_CU03",
            "name": "CU03_Catalogo_Planes_CoberturasFK_Clientes_DDD",
            "boundaries": [
                ("EAID_B_CU03_1", "CatalogoPlanesYClientesView", ["handleCrearPlan()", "handleAgregarCobertura()", "handleRegistrarCliente()"])
            ],
            "controls": [
                ("EAID_C_CU03_1", "CatalogoPolizaApplicationService", [
                    "listarPlanesSeguro()", "registrarPlanSeguroDDD()", "agregarCoberturaAPlan()",
                    "registrarClienteDDD()", "obtenerClientePorId()", "buscarClientePorDocumento()", "listarClientes()"
                ])
            ],
            "entities": [
                ("EAID_E_CU03_1", "PostgresPlanSeguroRepository", [("dbConnection", "PDO"), ("tableName", "String")], ["save()", "findAll()", "findById()", "agregarCobertura()"]),
                ("EAID_E_CU03_2", "PostgresClienteRepository", [("dbConnection", "PDO"), ("tableName", "String")], ["save()", "findAll()", "findById()", "findByDocumento()"])
            ]
        },
        {
            "id": "EAID_PKG_BCE_CU04",
            "name": "CU04_Cotizacion_Emision_IALocalWeb_ONNX_TFJS",
            "boundaries": [
                ("EAID_B_CU04_1", "CotizadorWebPWAView", ["handleAnalizarImagenIA()", "handleCotizarEnLinea()", "handleEmitirPoliza()", "sincronizarColaOffline()"])
            ],
            "controls": [
                ("EAID_C_CU04_1", "ValidadorNitidezLocalWebControl", ["analizarNitidezImagen()", "calcularVarianzaLaplaciana()", "generarImagenPruebaNitida()", "generarImagenPruebaBorrosa()"]),
                ("EAID_C_CU04_2", "EmisionPolizaGraphQLController", ["cotizarPolizaEnLinea()", "validarNitidez()", "insertarPoliza()", "emitirPoliza()"]),
                ("EAID_C_CU04_3", "CotizacionPolizaDomainService", ["calcularCotizacion()"])
            ],
            "entities": [
                ("EAID_E_CU04_1", "PostgresFacturaRepository", [("dbConnection", "PDO"), ("tableName", "String")], ["save()", "findById()", "findByPolizaId()", "confirmarPagoQr()"])
            ]
        },
        {
            "id": "EAID_PKG_BCE_CU05",
            "name": "CU05_PedidoWhatsApp_n8n_FacturaPDF_AWS_S3",
            "boundaries": [
                ("EAID_B_CU05_1", "CanalWhatsAppWebhookView", ["handleDispararWebhookWhatsApp()", "handleGenerarFacturaPdf()"]),
                ("EAID_B_CU05_2", "N8nWebhookHandler", ["do_POST()", "subir_pdf_a_s3()"])
            ],
            "controls": [
                ("EAID_C_CU05_1", "RecepcionPedidoService", ["procesarPedidoPolizaWhatsApp()"]),
                ("EAID_C_CU05_2", "FacturacionService", ["generarFacturaNotaVentaPDF()", "obtenerFacturaPorId()", "obtenerBinarioPdfFactura()"]),
                ("EAID_C_CU05_3", "FacturacionDomainService", ["emitirComprobanteParaPoliza()", "registrarPagoQrConfirmado()"])
            ],
            "entities": [
                ("EAID_E_CU05_1", "FacturaPdfGenerator", [("tmpDirectory", "String"), ("fontPath", "String")], ["compilarArchivoFacturaPdf()", "subirFacturaPdfAS3()"]),
                ("EAID_E_CU05_2", "AwsS3BucketEntity", [("bucketName", "String"), ("region", "String")], ["putObject()", "getObject()", "getPresignedUrl()"])
            ]
        },
        {
            "id": "EAID_PKG_BCE_CU09",
            "name": "CU09_Saga_Reserva_Compensacion_Cobertura",
            "boundaries": [
                ("EAID_B_CU09_1", "SimuladorSagaCoberturaView", ["handleSimularSaga()"])
            ],
            "controls": [
                ("EAID_C_CU09_1", "PolizaCoberturaService", ["descontarTechoAnualPoliza()", "compensarCoberturaSaga()", "restituirSaldoCobertura()"]),
                ("EAID_C_CU09_2", "SagaKafkaConsumer", ["procesarMensajeTopico()"])
            ],
            "entities": []
        },
        {
            "id": "EAID_PKG_BCE_CU10",
            "name": "CU10_Pasarela_Cobro_PagoQR_EMVCo",
            "boundaries": [
                ("EAID_B_CU10_1", "PasarelaPagoQREMVCoView", ["handleAbrirModalQr()", "handleConfirmarPagoQr()"])
            ],
            "controls": [],
            "entities": []
        }
    ]

    all_bce_elements = []

    for mod in cu_modules:
        pkg_mod = ET.SubElement(pkg_iconix, "packagedElement", {
            "xmi:type": "uml:Package", "xmi:id": mod["id"], "name": mod["name"]
        })

        for bid, bname, bops in mod["boundaries"]:
            b_elem = ET.SubElement(pkg_mod, "packagedElement", {
                "xmi:type": "uml:Class", "xmi:id": bid, "name": bname, "visibility": "public"
            })
            for op in bops:
                ET.SubElement(b_elem, "ownedOperation", {"xmi:id": f"OP_{bid}_{abs(hash(op))%100000}", "name": op})
            all_bce_elements.append((bid, bname, "Boundary", "boundary"))

        for cid, cname, cops in mod["controls"]:
            c_elem = ET.SubElement(pkg_mod, "packagedElement", {
                "xmi:type": "uml:Class", "xmi:id": cid, "name": cname, "visibility": "public"
            })
            for op in cops:
                ET.SubElement(c_elem, "ownedOperation", {"xmi:id": f"OP_{cid}_{abs(hash(op))%100000}", "name": op})
            all_bce_elements.append((cid, cname, "Control", "control"))

        for entity_tuple in mod["entities"]:
            eid, ename, eatts = entity_tuple[0], entity_tuple[1], entity_tuple[2]
            eops = entity_tuple[3] if len(entity_tuple) > 3 else []
            e_elem = ET.SubElement(pkg_mod, "packagedElement", {
                "xmi:type": "uml:Class", "xmi:id": eid, "name": ename, "visibility": "public"
            })
            for aname, atype in eatts:
                ET.SubElement(e_elem, "ownedAttribute", {
                    "xmi:type": "uml:Property", "xmi:id": f"ATT_{eid}_{abs(hash(aname))%100000}", "name": aname
                })
            for op in eops:
                ET.SubElement(e_elem, "ownedOperation", {"xmi:id": f"OP_{eid}_{abs(hash(op))%100000}", "name": op})
            all_bce_elements.append((eid, ename, "Entity", "entity"))

    # Paquete Modelo de Dominio DDD (Clases Rectangulares)
    pkg_domain = ET.SubElement(model, "packagedElement", {
        "xmi:type": "uml:Package", "xmi:id": "EAID_PKG_DOMAIN_A", "name": "03_Modelo_Dominio_DDD_Perfil_A"
    })

    domain_classes_data = [
        ("EAID_DOM_USUARIO_ROL", "UsuarioRol", [
            ("id", "UUID"), ("keycloakSub", "String"), ("email", "String"),
            ("nombreCompleto", "String"), ("rol", "String"), ("sessionId", "String")
        ], ["autenticarUsuarioOIDC()", "validarTokenJwtRS256()"]),

        ("EAID_DOM_SESION_TOKEN", "SesionUnificadaToken", [
            ("idempotencyKey", "String"), ("sessionId", "String"), ("keycloakSub", "String"),
            ("rol", "String"), ("tokenSha256", "String"), ("status", "String"), ("ttl", "Integer")
        ], ["guardarSesionUnificada()", "revocarSesionUnificada()"]),

        ("EAID_DOM_CLIENTE", "Cliente", [
            ("id", "UuidId"), ("documento", "DocumentoIdentidad"), ("nombres", "String"),
            ("apellidos", "String"), ("email", "String"), ("telefono", "String"),
            ("direccion", "String"), ("ciudad", "String"), ("perfilRiesgo", "PerfilRiesgoCliente"),
            ("usuarioId", "String")
        ], ["nombreCompleto()", "toGraphQLArray()"]),

        ("EAID_DOM_PLAN_SEGURO", "PlanSeguro", [
            ("id", "UuidId"), ("codigo", "String"), ("nombre", "String"),
            ("tipo", "TipoPlanVO"), ("primaBaseAnual", "PrimaMonetaria"),
            ("deducibleBasePorcentaje", "Float"), ("descripcion", "String"),
            ("activo", "Boolean"), ("coberturas", "Cobertura[]")
        ], ["techoCoberturaMaximo()", "agregarCobertura()", "toGraphQLArray()"]),

        ("EAID_DOM_COBERTURA", "Cobertura", [
            ("id", "UuidId"), ("planId", "UuidId"), ("codigo", "String"),
            ("nombre", "String"), ("sumaAseguradaMax", "Float"),
            ("deducibleMinimo", "Float"), ("deduciblePorcentaje", "Float"),
            ("obligatoria", "Boolean")
        ], ["toGraphQLArray()"]),

        ("EAID_DOM_POLIZA", "Poliza", [
            ("id", "UuidId"), ("numeroPoliza", "String"), ("clienteId", "UuidId"),
            ("planId", "UuidId"), ("vigencia", "VigenciaPoliza"),
            ("primaAnual", "PrimaMonetaria"), ("primaMensual", "PrimaMonetaria"),
            ("techoCoberturaAnual", "PrimaMonetaria"), ("saldoCoberturaRestante", "PrimaMonetaria"),
            ("estado", "EstadoPolizaVO"), ("bienAsegurado", "BienAseguradoVehiculo"),
            ("canalVenta", "String")
        ], ["emitirNueva()", "descontarTechoAnualPoliza()", "compensarCoberturaSaga()", "pullDomainEvents()"]),

        ("EAID_DOM_VEHICULO", "BienAseguradoVehiculo", [
            ("placa", "String"), ("vin", "String"), ("marca", "String"),
            ("modelo", "String"), ("anio", "Integer"), ("uso", "String"),
            ("color", "String"), ("valorComercial", "Float")
        ], ["fromArray()", "toArray()"]),

        ("EAID_DOM_FACTURA", "FacturaNotaVenta", [
            ("id", "UuidId"), ("numeroFactura", "NumeroComprobanteFiscal"),
            ("polizaId", "UuidId"), ("clienteId", "UuidId"), ("tipoComprobante", "String"),
            ("subtotal", "Float"), ("iva", "Float"), ("it", "Float"), ("total", "Float"),
            ("moneda", "String"), ("nitCliente", "String"), ("razonSocial", "String"),
            ("codigoControl", "String"), ("urlPdf", "String"), ("hashDigitalSha256", "String"),
            ("estadoPago", "String")
        ], ["emitirNueva()", "vincularPdfFirmado()", "confirmarPagoQr()", "estaPagada()"]),

        ("EAID_DOM_CACHE_COBERTURA", "CacheCoberturaActiva", [
            ("idempotencyKey", "String"), ("clienteId", "String"),
            ("totalSaldoCobertura", "Float"), ("cantidadPolizas", "Integer"),
            ("updatedAt", "DateTime"), ("ttl", "Integer")
        ], ["guardarCacheCoberturaActiva()", "obtenerCacheCoberturaActiva()"])
    ]

    for did, dname, datts, dops in domain_classes_data:
        c_elem = ET.SubElement(pkg_domain, "packagedElement", {
            "xmi:type": "uml:Class", "xmi:id": did, "name": dname, "visibility": "public"
        })
        for aname, atype in datts:
            ET.SubElement(c_elem, "ownedAttribute", {
                "xmi:type": "uml:Property", "xmi:id": f"ATT_{did}_{abs(hash(aname))%100000}",
                "name": aname, "type": atype
            })
        for op in dops:
            ET.SubElement(c_elem, "ownedOperation", {
                "xmi:id": f"OP_{did}_{abs(hash(op))%100000}", "name": op
            })
        all_bce_elements.append((did, dname, "Class", ""))

    # Extensiones específicas para Enterprise Architect 17.2
    ea_ext = ET.SubElement(xmi, "xmi:Extension", {
        "extender": "Enterprise Architect",
        "extenderID": "6.5"
    })

    ea_elements = ET.SubElement(ea_ext, "elements")
    for elid, elname, eltype, elstereo in all_bce_elements:
        elem = ET.SubElement(ea_elements, "element", {
            "xmi:idref": elid, "name": elname, "type": eltype
        })
        ET.SubElement(elem, "properties", {"sType": eltype, "scope": "public"})
        if elstereo:
            ET.SubElement(elem, "extendedProperties", {"stereotype": elstereo})

    # Diagramas para Enterprise Architect
    ea_diagrams = ET.SubElement(ea_ext, "diagrams")

    # 1. Diagrama de Casos de Uso
    diag_uc = ET.SubElement(ea_diagrams, "diagram", {
        "xmi:id": "EAID_DIAG_UC_A",
        "name": "01. Diagrama de Casos de Uso - Perfil A"
    })
    ET.SubElement(diag_uc, "properties", {"type": "Use Case", "name": "Casos de Uso Perfil A"})
    diag_uc_elems = ET.SubElement(diag_uc, "elements")
    y_pos = 50
    for ucid, ucname in usecases:
        ET.SubElement(diag_uc_elems, "element", {
            "subject": ucid, "geometry": f"Left=380;Top={y_pos};Right=780;Bottom={y_pos+65};"
        })
        y_pos += 85
    act_y = 60
    for aid, _ in actores:
        ET.SubElement(diag_uc_elems, "element", {
            "subject": aid, "geometry": f"Left=50;Top={act_y};Right=160;Bottom={act_y+75};"
        })
        act_y += 90

    # 2. Diagramas de Robustez BCE por Caso de Uso
    for i, mod in enumerate(cu_modules, start=1):
        diag_rob = ET.SubElement(ea_diagrams, "diagram", {
            "xmi:id": f"EAID_DIAG_ROB_{mod['id']}",
            "name": f"Robustez BCE - {mod['name']}"
        })
        ET.SubElement(diag_rob, "properties", {"type": "Analysis", "name": f"Robustez BCE {mod['name']}"})
        rob_elems = ET.SubElement(diag_rob, "elements")

        bx, by = 60, 80
        for bid, _, _ in mod["boundaries"]:
            ET.SubElement(rob_elems, "element", {"subject": bid, "geometry": f"Left={bx};Top={by};Right={bx+200};Bottom={by+80};"})
            by += 110

        cx, cy = 360, 80
        for cid, _, _ in mod["controls"]:
            ET.SubElement(rob_elems, "element", {"subject": cid, "geometry": f"Left={cx};Top={cy};Right={cx+240};Bottom={cy+90};"})
            cy += 120

        ex, ey = 740, 80
        for entity_info in mod["entities"]:
            eid = entity_info[0]
            ET.SubElement(rob_elems, "element", {"subject": eid, "geometry": f"Left={ex};Top={ey};Right={ex+240};Bottom={ey+80};"})
            ey += 110

    # 3. Diagramas de Secuencia UML 2.5+
    seq_descriptions = [
        ("CU01", "10. Secuencia UML 2.5+ - CU01 (Flujo OAuth 2.0 PKCE S256, JWT RS256 y Sesión DynamoDB)", [
            ("LoginKeycloakSSOView", "AuthOIDCService", "iniciarFlujoOIDCPkce(email, rol)"),
            ("AuthOIDCService", "AuthOIDCService", "generarParPkceS256()"),
            ("AuthOIDCService", "AuthOIDCController", "autenticarUsuarioOIDC(codeVerifier)"),
            ("AuthOIDCController", "AuthOIDCController", "validarTokenJwtRS256(token)"),
            ("AuthOIDCController", "DynamoDbSessionCacheRepository", "registrarSesionUnificadaDynamoDB(tokenSha256)"),
            ("AuthOIDCController", "UsuarioRolEntity", "sincronizarUsuarioRolPostgreSQL(email, rol)"),
            ("AuthOIDCController", "AuthOIDCService", "200 OK (JWT RS256, SessionId)"),
            ("AuthOIDCService", "LoginKeycloakSSOView", "actualizarSesionActiva(perfil)")
        ]),
        ("CU02", "11. Secuencia UML 2.5+ - CU02 (Resolución Federada GraphQL y CacheCoberturaActiva)", [
            ("PortalClientesGraphQLView", "ApolloFederationClient", "consultarEstadoUnificadoAsegurado(clienteId)"),
            ("ApolloFederationClient", "ApolloFederationResolver", "POST /graphql (resumenUnificadoAsegurado)"),
            ("ApolloFederationResolver", "PostgresPolizaRepository", "consultarPolizasYClientes(clienteId)"),
            ("ApolloFederationResolver", "DynamoDbSessionCacheRepository", "consultarOActualizarCacheCoberturaActiva(clienteId)"),
            ("ApolloFederationResolver", "ExpedienteSiniestroMongoMirror", "federarExpedientesSiniestrosMongoDB(polizaId)"),
            ("ApolloFederationResolver", "ApolloFederationClient", "200 OK (ResumenUnificadoPayload)"),
            ("ApolloFederationClient", "PortalClientesGraphQLView", "cargarEstadoAsegurado(payload)")
        ]),
        ("CU03", "12. Secuencia UML 2.5+ - CU03 (Registro DDD de PlanSeguro, Cobertura FK y Cliente)", [
            ("CatalogoPlanesYClientesView", "CatalogoPolizaApplicationService", "registrarPlanSeguroDDD(nuevoPlanDTO)"),
            ("CatalogoPolizaApplicationService", "PostgresPlanSeguroRepository", "save(planSeguroAggregate)"),
            ("CatalogoPlanesYClientesView", "CatalogoPolizaApplicationService", "agregarCoberturaAPlan(coberturaDTO)"),
            ("CatalogoPolizaApplicationService", "PostgresPlanSeguroRepository", "agregarCobertura(planId, coberturaEntity)"),
            ("CatalogoPlanesYClientesView", "CatalogoPolizaApplicationService", "registrarClienteDDD(clienteDTO)"),
            ("CatalogoPolizaApplicationService", "PostgresClienteRepository", "save(clienteAggregate)"),
            ("CatalogoPolizaApplicationService", "CatalogoPlanesYClientesView", "201 Created (CatalogoSincronizado)")
        ]),
        ("CU04", "13. Secuencia UML 2.5+ - CU04 (Validación IA Local Nitidez, Cotización y Emisión de Póliza)", [
            ("CotizadorWebPWAView", "ValidadorNitidezLocalWebControl", "analizarNitidezImagen(pixelsRgba)"),
            ("ValidadorNitidezLocalWebControl", "ValidadorNitidezLocalWebControl", "calcularVarianzaLaplaciana(tensor2D)"),
            ("ValidadorNitidezLocalWebControl", "CotizadorWebPWAView", "Score >= 0.65 + TokenValidacion"),
            ("CotizadorWebPWAView", "EmisionPolizaGraphQLController", "cotizarPolizaEnLinea(CotizarDTO)"),
            ("EmisionPolizaGraphQLController", "CotizacionPolizaDomainService", "calcularCotizacion(riesgo, valor)"),
            ("CotizadorWebPWAView", "EmisionPolizaGraphQLController", "emitirPoliza(EmitirDTO, IdempotencyKey)"),
            ("EmisionPolizaGraphQLController", "PostgresPolizaRepository", "insertarPoliza(polizaAggregate)"),
            ("EmisionPolizaGraphQLController", "CotizadorWebPWAView", "201 Created (PolizaEmitidaEvent)")
        ]),
        ("CU05", "14. Secuencia UML 2.5+ - CU05 (Webhook WhatsApp n8n, Emisión Póliza, PDF SHA-256 y Upload AWS S3)", [
            ("CanalWhatsAppWebhookView", "N8nWebhookHandler", "handleDispararWebhookWhatsApp(payload)"),
            ("N8nWebhookHandler", "RecepcionPedidoService", "procesarPedidoPolizaWhatsApp(pedido)"),
            ("RecepcionPedidoService", "FacturacionService", "generarFacturaNotaVentaPDF(polizaId)"),
            ("FacturacionService", "FacturaPdfGenerator", "compilarArchivoFacturaPdf(factura)"),
            ("FacturaPdfGenerator", "AwsS3BucketEntity", "subirFacturaPdfAS3(servicio-de-seguros-aegiscore)"),
            ("FacturacionService", "N8nWebhookHandler", "retornarFacturaFiscal(urlPdf, sha256)"),
            ("N8nWebhookHandler", "CanalWhatsAppWebhookView", "despacharPDFPorWhatsApp(urlPdf)")
        ]),
        ("CU09", "15. Secuencia UML 2.5+ - CU09-MS1 (Reserva de Cobertura y Rollback Compensatorio Saga)", [
            ("Broker Apache Kafka (Saga)", "SagaKafkaConsumer", "orden.pago.calculada (SagaEvent)"),
            ("SagaKafkaConsumer", "PolizaCoberturaService", "descontarTechoAnualPoliza(polizaId, monto)"),
            ("PolizaCoberturaService", "PostgresPolizaRepository", "actualizarSaldoCobertura(polizaId, saldo)"),
            ("PolizaCoberturaService", "Broker Apache Kafka (Saga)", "cobertura.poliza.descontada (SuccessEvent)"),
            ("Broker Apache Kafka (Saga)", "SagaKafkaConsumer", "compensacion.saga.solicitada (Error en MS3)"),
            ("SagaKafkaConsumer", "PolizaCoberturaService", "compensarCoberturaSaga(polizaId, monto)"),
            ("PolizaCoberturaService", "PostgresPolizaRepository", "restituirSaldoCobertura(polizaId)"),
            ("PolizaCoberturaService", "Broker Apache Kafka (Saga)", "cobertura.poliza.compensada (RollbackEvent)")
        ]),
        ("CU10", "16. Secuencia UML 2.5+ - CU10-MS1 (Generación QR EMVCo y Conciliación de Pago Fiscal)", [
            ("Cliente Asegurado", "PasarelaPagoQREMVCoView", "handleAbrirModalQr(polizaId)"),
            ("PasarelaPagoQREMVCoView", "ApolloFederationClient", "generarQrCobro(polizaId, primaMensual)"),
            ("ApolloFederationClient", "PasarelaPagoQREMVCoView", "qrStringEMVCo + countdownExpiracion"),
            ("PasarelaPagoQREMVCoView", "ApolloFederationClient", "confirmarPagoQr(facturaId, idempotencyKey)"),
            ("ApolloFederationClient", "FacturacionDomainService", "registrarPagoQrConfirmado(facturaId, monto)"),
            ("FacturacionDomainService", "PostgresFacturaRepository", "confirmarPagoQr(facturaId, PAGADA)"),
            ("FacturacionDomainService", "PasarelaPagoQREMVCoView", "200 OK (Factura Pagada y Conciliada)")
        ])
    ]

    for cu_code, seq_title, steps in seq_descriptions:
        diag_seq = ET.SubElement(ea_diagrams, "diagram", {
            "xmi:id": f"EAID_DIAG_SEQ_{cu_code}_A",
            "name": seq_title
        })
        ET.SubElement(diag_seq, "properties", {"type": "Sequence", "name": seq_title})
        seq_elems = ET.SubElement(diag_seq, "elements")

        lx = 50
        lifelines_seen = {}
        for src, dst, msg in steps:
            for entity_name in [src, dst]:
                if entity_name not in lifelines_seen:
                    lifelines_seen[entity_name] = lx
                    ET.SubElement(seq_elems, "element", {
                        "name": entity_name,
                        "geometry": f"Left={lx};Top=40;Right={lx+140};Bottom=620;"
                    })
                    lx += 180

    # 4. Diagrama del Modelo de Dominio DDD
    diag_dom = ET.SubElement(ea_diagrams, "diagram", {
        "xmi:id": "EAID_DIAG_DOM_A",
        "name": "02. Modelo de Dominio DDD - Perfil A"
    })
    ET.SubElement(diag_dom, "properties", {"type": "Logical", "name": "Modelo de Dominio DDD Perfil A"})
    dom_elems = ET.SubElement(diag_dom, "elements")
    for did, dname, _, _ in domain_classes_data:
        ET.SubElement(dom_elems, "element", {
            "subject": did,
            "geometry": "Left=100;Top=100;Right=350;Bottom=280;"
        })

    # Formatear XML
    raw_str = ET.tostring(xmi, encoding="utf-8")
    parsed = minidom.parseString(raw_str)
    pretty_xml = parsed.toprettyxml(indent="  ", encoding="utf-8")

    out_paths = [
        os.path.join("docs-iconix-uml", "enterprise-architect", "aegiscore-perfil-a-ea17.xmi"),
        os.path.join("docs-iconix-uml", "enterprise-architect", "aegiscore-perfil-a-ea17.xml"),
        os.path.join("docs-iconix-uml", "aegiscore-perfil-a-iconix-uml25.xmi")
    ]

    for p in out_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(pretty_xml)
        print(f"Generado archivo XMI/XML: {p}")

    print(f"Éxito: Archivos XMI 2.1 y XML exportados para Enterprise Architect 17.2.")
    print(f"Total Clases BCE y Dominio exportadas: {len(all_bce_elements)}")
    print(f"Total Diagramas exportados: {len(ea_diagrams.findall('diagram'))}")


if __name__ == "__main__":
    build_xmi_perfil_a()
