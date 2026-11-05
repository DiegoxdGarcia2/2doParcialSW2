# -*- coding: utf-8 -*-
"""
Generador de Modelo XML/XMI 2.1 para Enterprise Architect 17.2
Proyecto: AegisCore AI - Perfil B (CU06 al CU10)
ICONIX + UML 2.5+: Casos de Uso, Diagramas de Robustez BCE, Diagramas de Secuencia y Diagrama de Clases
"""
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom

def gen_id(prefix="EAID"):
    return f"{prefix}_{uuid.uuid4().hex[:8].upper()}"

def build_xmi():
    xmi = ET.Element("xmi:XMI", {
        "xmi:version": "2.1",
        "xmlns:uml": "http://schema.omg.org/spec/UML/2.1",
        "xmlns:xmi": "http://schema.omg.org/spec/XMI/2.1"
    })

    doc = ET.SubElement(xmi, "xmi:Documentation", {
        "exporter": "Enterprise Architect",
        "exporterVersion": "17.2",
        "name": "AegisCore_AI_Perfil_B_ICONIX"
    })

    model = ET.SubElement(xmi, "uml:Model", {
        "xmi:type": "uml:Model",
        "name": "EA_Model_AegisCore_Perfil_B",
        "visibility": "public"
    })

    # Actores Globales
    actor_asegurado_id = "EAID_ACT_ASEGURADO"
    actor_perito_id = "EAID_ACT_PERITO"
    actor_ajustador_id = "EAID_ACT_AJUSTADOR"
    actor_kafka_id = "EAID_ACT_KAFKA"

    act_aseg = ET.SubElement(model, "packagedElement", {
        "xmi:type": "uml:Actor", "xmi:id": actor_asegurado_id, "name": "Cliente Asegurado", "visibility": "public"
    })
    act_per = ET.SubElement(model, "packagedElement", {
        "xmi:type": "uml:Actor", "xmi:id": actor_perito_id, "name": "Perito de Campo", "visibility": "public"
    })
    act_ajus = ET.SubElement(model, "packagedElement", {
        "xmi:type": "uml:Actor", "xmi:id": actor_ajustador_id, "name": "Ajustador de Siniestros", "visibility": "public"
    })
    act_kaf = ET.SubElement(model, "packagedElement", {
        "xmi:type": "uml:Actor", "xmi:id": actor_kafka_id, "name": "Broker Apache Kafka (Saga)", "visibility": "public"
    })

    # Paquete Casos de Uso
    pkg_uc = ET.SubElement(model, "packagedElement", {
        "xmi:type": "uml:Package", "xmi:id": "EAID_PKG_USECASES", "name": "01_Casos_de_Uso_Perfil_B"
    })
    
    usecases = [
        ("EAID_UC06", "CU06: Reportar Siniestro Vial SOS con Triaje Automático"),
        ("EAID_UC07", "CU07: Inspeccionar Daños Offline en Terreno con Edge AI"),
        ("EAID_UC08", "CU08: Sincronizar Expediente con Idempotencia en DynamoDB"),
        ("EAID_UC09", "CU09: Liquidar y Pagar Indemnización de Siniestro (Saga Transversal)"),
        ("EAID_UC10", "CU10: Procesar Cobro Recurrente de Primas y Pago QR Idempotente")
    ]
    for ucid, ucname in usecases:
        ET.SubElement(pkg_uc, "packagedElement", {
            "xmi:type": "uml:UseCase", "xmi:id": ucid, "name": ucname, "visibility": "public"
        })

    # Paquete Análisis y Diseño ICONIX (BCE)
    pkg_iconix = ET.SubElement(model, "packagedElement", {
        "xmi:type": "uml:Package", "xmi:id": "EAID_PKG_ICONIX", "name": "02_Analisis_y_Diseno_ICONIX_BCE"
    })

    # Definición de Clases BCE por Caso de Uso
    cu_modules = [
        {
            "id": "EAID_PKG_BCE_CU06",
            "name": "CU06_Siniestro_SOS_Triaje",
            "boundaries": [
                ("EAID_B_CU06_1", "SiniestroSosMobileView", ["presionarBotonSOS()", "mostrarConfirmacionSiniestro()"]),
                ("EAID_B_CU06_2", "PushNotificationGateway", ["despacharAlertaPerito()"])
            ],
            "controls": [
                ("EAID_C_CU06_1", "SiniestroEmergencyControl", [
                    "procesarReporteEmergencia(ReporteEmergenciaDto)",
                    "validarCoordenadasGeograficas()",
                    "calcularPrioridadTriajeGeoespacial(coordenadas, fotos)",
                    "notificarPeritoMasCercano(peritoId, expedienteId)"
                ])
            ],
            "entities": [
                ("EAID_E_CU06_1", "ExpedienteSiniestroEntity", [
                    ("idExpediente", "String"), ("coordenadasGPS", "GeoJSON"), ("severidad", "String"), ("estado", "String")
                ]),
                ("EAID_E_CU06_2", "PeritoGuardiaEntity", [
                    ("idPerito", "String"), ("nombre", "String"), ("ubicacionGPS", "GeoJSON"), ("disponible", "Boolean")
                ])
            ]
        },
        {
            "id": "EAID_PKG_BCE_CU07",
            "name": "CU07_Inspeccion_Offline_EdgeAI",
            "boundaries": [
                ("EAID_B_CU07_1", "CamaraPeritajeOfflineView", ["enfocarParteDanada()", "renderizarOverlayDeteccion()"]),
                ("EAID_B_CU07_2", "FormularioDanosOfflineView", ["completarBaremo()", "guardarInspeccion()"])
            ],
            "controls": [
                ("EAID_C_CU07_1", "PeritajeOfflineTFLiteControl", [
                    "capturarFotografiasEvidencia(cameraImageBytes)",
                    "ejecutarInferenciaLocalTFLite(preprocessedImage)",
                    "generarIdempotencyKeyUUIDv4()",
                    "persistirInspeccionLocal(DatosPeritaje)"
                ])
            ],
            "entities": [
                ("EAID_E_CU07_1", "InspeccionOfflineSQLiteEntity", [
                    ("localId", "Integer"), ("idempotencyKey", "UUIDv4"), ("hashSHA256", "String"), ("estado", "String")
                ]),
                ("EAID_E_CU07_2", "ModeloTFLiteQuantized", [
                    ("assetPath", "String"), ("tamanoBytes", "Integer"), ("inputShape", "String"), ("confidenceScore", "Float")
                ])
            ]
        },
        {
            "id": "EAID_PKG_BCE_CU08",
            "name": "CU08_Sincronizacion_Idempotencia_DynamoDB",
            "boundaries": [
                ("EAID_B_CU08_1", "ColaSincronizacionOfflineView", ["presionarBotonSincronizarCola()", "actualizarUIConResultado()"]),
                ("EAID_B_CU08_2", "SiniestrosSyncRestController", ["recibirLoteSincronizacion(IdempotencyKey, Payload)"])
            ],
            "controls": [
                ("EAID_C_CU08_1", "SyncIdempotentControl", [
                    "extraerLotePendienteSQLite()",
                    "computarSha256Payload()",
                    "adquirirBloqueoIdempotenteDynamoDB(idempotencyKey, hash)",
                    "sincronizarConMS2Backend(payload)",
                    "marcarSincronizadoSQLite(idempotencyKey)"
                ])
            ],
            "entities": [
                ("EAID_E_CU08_1", "IdempotencyRecordEntity", [
                    ("idempotencyKey", "UUIDv4"), ("requestHashSHA256", "String"), ("status", "String"), ("ttl", "Long"), ("responseBody", "String")
                ]),
                ("EAID_E_CU08_2", "ExpedienteSiniestroDocument", [
                    ("idExpediente", "String"), ("fotosPericiales", "List<String>"), ("estadoSync", "String")
                ])
            ]
        },
        {
            "id": "EAID_PKG_BCE_CU09",
            "name": "CU09_Liquidacion_Saga_Transversal",
            "boundaries": [
                ("EAID_B_CU09_1", "LiquidacionSiniestroAdminView", ["autorizarLiquidacionSiniestro()", "mostrarEstadoSaga()"])
            ],
            "controls": [
                ("EAID_C_CU09_1", "SagaLiquidacionOrchestratorControl", [
                    "iniciarSagaLiquidacion(siniestroId, monto)",
                    "solicitarBloqueoExpedienteMS2(siniestroId)",
                    "solicitarReservaCoberturaMS1(polizaId, monto)",
                    "calcularMontoIndemnizableYDesembolso()",
                    "ejecutarRollbackSemantico(causaFallo)"
                ]),
                ("EAID_C_CU09_2", "ReclamoEstadoControl_MS2", ["bloquearSiniestro()", "revertirEstadoSiniestro()"]),
                ("EAID_C_CU09_3", "PolizaCoberturaControl_MS1", ["reservarCobertura()", "liberarCobertura()"])
            ],
            "entities": [
                ("EAID_E_CU09_1", "SagaInstanceEntity", [
                    ("sagaId", "String"), ("siniestroId", "String"), ("estadoSaga", "String"), ("pasoActual", "String"), ("fechaCreacion", "Timestamp")
                ]),
                ("EAID_E_CU09_2", "OrdenLiquidacionEntity", [
                    ("idLiquidacion", "String"), ("montoBruto", "BigDecimal"), ("deducible", "BigDecimal"), ("montoNeto", "BigDecimal")
                ]),
                ("EAID_E_CU09_3", "ContratoPolizaEntity", [
                    ("polizaId", "String"), ("limiteAnual", "BigDecimal"), ("coberturaDisponible", "BigDecimal")
                ])
            ]
        },
        {
            "id": "EAID_PKG_BCE_CU10",
            "name": "CU10_Cobro_Recurrente_PagoQR",
            "boundaries": [
                ("EAID_B_CU10_1", "CobroPrimaQRView", ["solicitarGeneracionQR()", "mostrarComprobanteFiscal()"]),
                ("EAID_B_CU10_2", "PasarelaPagoBCBWebhook", ["recibirConfirmacionPago(IdempotencyKey, CallbackData)"])
            ],
            "controls": [
                ("EAID_C_CU10_1", "PagoPrimaQRControl", [
                    "generarCobroQREMV(polizaId, monto, expiraMinutos)",
                    "validarIdempotenciaPago(idempotencyKey, hash)",
                    "asentarTransaccionContable(polizaId, monto)",
                    "notificarRenovacionPolizaMS1(polizaId)"
                ])
            ],
            "entities": [
                ("EAID_E_CU10_1", "TransaccionPagoQREntity", [
                    ("idTransaccion", "String"), ("polizaId", "String"), ("montoBOB", "BigDecimal"), ("estadoPago", "String"), ("emvQRString", "String")
                ]),
                ("EAID_E_CU10_2", "IdempotencyRecordEntity_Pagos", [
                    ("idempotencyKey", "UUIDv4"), ("comprobanteFiscal", "String"), ("status", "String")
                ])
            ]
        }
    ]

    all_elements = []

    for mod in cu_modules:
        pkg_mod = ET.SubElement(pkg_iconix, "packagedElement", {
            "xmi:type": "uml:Package", "xmi:id": mod["id"], "name": mod["name"]
        })
        
        # Boundaries
        for bid, bname, bops in mod["boundaries"]:
            b_elem = ET.SubElement(pkg_mod, "packagedElement", {
                "xmi:type": "uml:Class", "xmi:id": bid, "name": bname, "visibility": "public"
            })
            for op in bops:
                ET.SubElement(b_elem, "ownedOperation", {"xmi:id": f"OP_{bid}_{abs(hash(op))%100000}", "name": op})
            all_elements.append((bid, bname, "Boundary", "boundary"))

        # Controls
        for cid, cname, cops in mod["controls"]:
            c_elem = ET.SubElement(pkg_mod, "packagedElement", {
                "xmi:type": "uml:Class", "xmi:id": cid, "name": cname, "visibility": "public"
            })
            for op in cops:
                ET.SubElement(c_elem, "ownedOperation", {"xmi:id": f"OP_{cid}_{abs(hash(op))%100000}", "name": op})
            all_elements.append((cid, cname, "Control", "control"))

        # Entities
        for eid, ename, eatts in mod["entities"]:
            e_elem = ET.SubElement(pkg_mod, "packagedElement", {
                "xmi:type": "uml:Class", "xmi:id": eid, "name": ename, "visibility": "public"
            })
            for aname, atype in eatts:
                ET.SubElement(e_elem, "ownedAttribute", {
                    "xmi:type": "uml:Property", "xmi:id": f"ATT_{eid}_{abs(hash(aname))%100000}", "name": aname
                })
            all_elements.append((eid, ename, "Entity", "entity"))

    # Extensiones específicas para Enterprise Architect 17.2
    ea_ext = ET.SubElement(xmi, "xmi:Extension", {
        "extender": "Enterprise Architect",
        "extenderID": "6.5"
    })

    ea_elements = ET.SubElement(ea_ext, "elements")
    for elid, elname, eltype, elstereo in all_elements:
        elem = ET.SubElement(ea_elements, "element", {
            "xmi:idref": elid, "name": elname, "type": eltype
        })
        ET.SubElement(elem, "properties", {"sType": eltype, "scope": "public"})
        ET.SubElement(elem, "extendedProperties", {"stereotype": elstereo})

    # Diagramas para Enterprise Architect
    ea_diagrams = ET.SubElement(ea_ext, "diagrams")

    # Diagrama de Casos de Uso
    diag_uc = ET.SubElement(ea_diagrams, "diagram", {"xmi:id": "EAID_DIAG_UC", "name": "Diagrama de Casos de Uso Perfil B (CU06-CU10)"})
    ET.SubElement(diag_uc, "properties", {"type": "Use Case", "name": "Diagrama de Casos de Uso Perfil B"})
    diag_uc_elems = ET.SubElement(diag_uc, "elements")
    y_pos = 50
    for ucid, ucname in usecases:
        ET.SubElement(diag_uc_elems, "element", {
            "subject": ucid, "geometry": f"Left=300;Top={y_pos};Right=560;Bottom={y_pos+70};"
        })
        y_pos += 90
    ET.SubElement(diag_uc_elems, "element", {"subject": actor_asegurado_id, "geometry": "Left=60;Top=60;Right=130;Bottom=170;"})
    ET.SubElement(diag_uc_elems, "element", {"subject": actor_perito_id, "geometry": "Left=60;Top=220;Right=130;Bottom=330;"})
    ET.SubElement(diag_uc_elems, "element", {"subject": actor_ajustador_id, "geometry": "Left=60;Top=380;Right=130;Bottom=490;"})

    # Diagramas de Robustez BCE por Caso de Uso
    for i, mod in enumerate(cu_modules, start=6):
        diag_rob = ET.SubElement(ea_diagrams, "diagram", {
            "xmi:id": f"EAID_DIAG_ROB_CU0{i}",
            "name": f"Robustez BCE - CU0{i}: {mod['name']}"
        })
        ET.SubElement(diag_rob, "properties", {"type": "Analysis", "name": f"Robustez BCE CU0{i}"})
        rob_elems = ET.SubElement(diag_rob, "elements")

        # Boundaries a la izquierda
        bx = 50
        by = 80
        for bid, _, _ in mod["boundaries"]:
            ET.SubElement(rob_elems, "element", {"subject": bid, "geometry": f"Left={bx};Top={by};Right={bx+160};Bottom={by+80};"})
            by += 110

        # Controls al centro
        cx = 300
        cy = 100
        for cid, _, _ in mod["controls"]:
            ET.SubElement(rob_elems, "element", {"subject": cid, "geometry": f"Left={cx};Top={cy};Right={cx+220};Bottom={cy+90};"})
            cy += 120

        # Entities a la derecha
        ex = 600
        ey = 80
        for eid, _, _ in mod["entities"]:
            ET.SubElement(rob_elems, "element", {"subject": eid, "geometry": f"Left={ex};Top={ey};Right={ex+180};Bottom={ey+80};"})
            ey += 110

    # Diagramas de Secuencia UML 2.5+
    seq_descriptions = [
        ("CU06", "CU06: Secuencia Triaje y Asignación Pericial SOS", [
            ("Cliente Asegurado", "SiniestroSosMobileView", "presionarBotonSOS()"),
            ("SiniestroSosMobileView", "SiniestroEmergencyControl", "procesarReporteEmergencia(dto)"),
            ("SiniestroEmergencyControl", "ExpedienteSiniestroEntity", "insertOne(expedienteDocument)"),
            ("SiniestroEmergencyControl", "PushNotificationGateway", "despacharAlertaPerito(peritoId)")
        ]),
        ("CU07", "CU07: Secuencia Inspección Offline con Inferencia TFLite", [
            ("Perito de Campo", "CamaraPeritajeOfflineView", "enfocarParteDanada()"),
            ("CamaraPeritajeOfflineView", "PeritajeOfflineTFLiteControl", "capturarFotografiasEvidencia(bytes)"),
            ("PeritajeOfflineTFLiteControl", "ModeloTFLiteQuantized", "ejecutarInferenciaLocalTFLite(tensors)"),
            ("PeritajeOfflineTFLiteControl", "InspeccionOfflineSQLiteEntity", "insertarInspeccionLocal(uuid, hash, datos)")
        ]),
        ("CU08", "CU08: Secuencia Sincronización Idempotente con DynamoDB", [
            ("Perito de Campo", "ColaSincronizacionOfflineView", "presionarBotonSincronizarCola()"),
            ("ColaSincronizacionOfflineView", "SiniestrosSyncRestController", "POST /api/v1/siniestros/peritaje/sync"),
            ("SiniestrosSyncRestController", "SyncIdempotentControl", "validarIdempotencia(key, hash)"),
            ("SyncIdempotentControl", "IdempotencyRecordEntity", "PutItem(PROCESSING)"),
            ("SyncIdempotentControl", "ExpedienteSiniestroDocument", "insertOne(mongoDoc)"),
            ("SyncIdempotentControl", "IdempotencyRecordEntity", "UpdateItem(COMPLETED, 201 Created)")
        ]),
        ("CU09", "CU09: Secuencia Liquidación Saga Transversal y Rollback", [
            ("Ajustador de Siniestros", "LiquidacionSiniestroAdminView", "autorizarLiquidacion(siniestroId, monto)"),
            ("LiquidacionSiniestroAdminView", "SagaLiquidacionOrchestratorControl", "iniciarSagaLiquidacion(cmd)"),
            ("SagaLiquidacionOrchestratorControl", "ReclamoEstadoControl_MS2", "bloquearSiniestro(EN_LIQUIDACION)"),
            ("SagaLiquidacionOrchestratorControl", "PolizaCoberturaControl_MS1", "reservarCobertura(monto)"),
            ("SagaLiquidacionOrchestratorControl", "OrdenLiquidacionEntity", "insertOrdenLiquidacion(deducible, neto)"),
            ("SagaLiquidacionOrchestratorControl", "Broker Apache Kafka (Saga)", "publicarRollbackSiFalla(CompensateEvent)")
        ]),
        ("CU10", "CU10: Secuencia Cobro Recurrente y Pago QR Idempotente", [
            ("Cliente Asegurado", "CobroPrimaQRView", "solicitarPagoCuota(polizaId)"),
            ("CobroPrimaQRView", "PagoPrimaQRControl", "generarCobroQREMV(polizaId, monto)"),
            ("PasarelaPagoBCBWebhook", "PagoPrimaQRControl", "confirmarPagoWebhook(key, hash)"),
            ("PagoPrimaQRControl", "IdempotencyRecordEntity_Pagos", "validarIdempotenciaDynamoDB(key)"),
            ("PagoPrimaQRControl", "TransaccionPagoQREntity", "insertTransaccionContable(monto, PAGADO)")
        ])
    ]

    for cu_code, seq_title, steps in seq_descriptions:
        diag_seq = ET.SubElement(ea_diagrams, "diagram", {
            "xmi:id": f"EAID_DIAG_SEQ_{cu_code}",
            "name": seq_title
        })
        ET.SubElement(diag_seq, "properties", {"type": "Sequence", "name": seq_title})
        seq_elems = ET.SubElement(diag_seq, "elements")
        
        # Posicionar Lifelines horizontalmente
        lx = 50
        lifelines_seen = {}
        for src, dst, msg in steps:
            for entity_name in [src, dst]:
                if entity_name not in lifelines_seen:
                    lifelines_seen[entity_name] = lx
                    ET.SubElement(seq_elems, "element", {
                        "name": entity_name,
                        "geometry": f"Left={lx};Top=40;Right={lx+130};Bottom=450;"
                    })
                    lx += 170

    # Formatear XML bonito con minidom
    raw_str = ET.tostring(xmi, encoding="utf-8")
    parsed = minidom.parseString(raw_str)
    pretty_xml = parsed.toprettyxml(indent="  ", encoding="utf-8")

    out_path = "docs-iconix-uml/enterprise-architect/aegiscore-perfil-b-ea17.xml"
    with open(out_path, "wb") as f:
        f.write(pretty_xml)
    print(f"XMI 2.1 para Enterprise Architect 17.2 generado exitosamente en: {out_path}")
    print(f"Total Clases BCE exportadas: {len(all_elements)}")
    print(f"Total Diagramas generados: 1 (Casos de Uso) + 5 (Robustez) + 5 (Secuencia) = 11 diagramas")

if __name__ == "__main__":
    build_xmi()
