# -*- coding: utf-8 -*-
"""
Script para poblar todas las relaciones (Connectors, Messages y DiagramLinks)
en el archivo de proyecto SQLite (.qea) de Enterprise Architect 17.2.
Proyecto: AegisCore AI - Perfil B (CU06 al CU10)
"""
import sqlite3
import uuid

def populate_relationships():
    db_path = "docs-iconix-uml/enterprise-architect/aegiscore-perfil-b-ea17.qea"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Limpiar conectores y diagramlinks previos
    cur.execute("DELETE FROM t_connector")
    cur.execute("DELETE FROM t_diagramlinks")
    conn.commit()

    connector_counter = 0

    def add_connector(name, conn_type, start_id, end_id, diagram_id, seq_no=0, pt_y=0, direction="Source -> Destination"):
        nonlocal connector_counter
        connector_counter += 1
        guid = f"{{{uuid.uuid4()}}}".upper()
        
        cur.execute("""
            INSERT INTO t_connector (
                Connector_ID, Name, Direction, Connector_Type,
                SourceAccess, DestAccess, Start_Object_ID, End_Object_ID,
                SeqNo, RouteStyle, LineColor, DiagramID, PtStartY, PtEndY,
                ActionFlags, PDATA1, PDATA2, ea_guid, SourceStyle, DestStyle
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            connector_counter, name, direction, conn_type,
            "Public", "Public", start_id, end_id,
            seq_no, 3, -1, diagram_id, pt_y, pt_y,
            "Kind=Call;" if conn_type == "Sequence" else None,
            "Call" if conn_type == "Sequence" else None,
            "Synchronous" if conn_type == "Sequence" else None,
            guid, "Navigable=Non-Navigable;", "Navigable=Navigable;"
        ))

        cur.execute("""
            INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Geometry, Hidden)
            VALUES (?, ?, ?, ?)
        """, (diagram_id, connector_counter, "EDGE=2;", 0))

        return connector_counter

    # =========================================================================
    # 1. RELACIONES PARA DIAGRAMA DE CASOS DE USO (DiagramID: 1)
    # =========================================================================
    diag_uc_id = 1
    # Actores: Asegurado(2), Perito(3), Ajustador(4), Kafka(5)
    # UseCases: CU06(7), CU07(8), CU08(9), CU09(10), CU10(11)
    add_connector("Reporta Siniestro", "Use Case", 2, 7, diag_uc_id, direction="Source -> Destination")
    add_connector("Paga Prima QR", "Use Case", 2, 11, diag_uc_id, direction="Source -> Destination")
    add_connector("Atiende Emergencia", "Use Case", 3, 7, diag_uc_id, direction="Source -> Destination")
    add_connector("Inspecciona en Campo", "Use Case", 3, 8, diag_uc_id, direction="Source -> Destination")
    add_connector("Sincroniza Lote", "Use Case", 3, 9, diag_uc_id, direction="Source -> Destination")
    add_connector("Aprueba Liquidación", "Use Case", 4, 10, diag_uc_id, direction="Source -> Destination")
    add_connector("Compensa Transacción", "Use Case", 5, 10, diag_uc_id, direction="Source -> Destination")

    # =========================================================================
    # 2. RELACIONES PARA DIAGRAMAS DE ROBUSTEZ BCE (ICONIX)
    # =========================================================================
    
    # CU06 (DiagramID: 2)
    # Boundary: SiniestroSosMobileView(14), PushNotificationGateway(15)
    # Control: SiniestroEmergencyControl(16)
    # Entity: ExpedienteSiniestroEntity(17), PeritoGuardiaEntity(18)
    d2 = 2
    add_connector("1. Enviar coordenadas GPS y fotos", "Association", 14, 16, d2)
    add_connector("2. Consultar perito cercano (2dsphere)", "Association", 16, 18, d2)
    add_connector("3. Persistir expediente emergencia", "Association", 16, 17, d2)
    add_connector("4. Despachar alerta Push perito", "Association", 16, 15, d2)

    # CU07 (DiagramID: 3)
    # Boundary: CamaraPeritajeOfflineView(20), FormularioDanosOfflineView(21)
    # Control: PeritajeOfflineTFLiteControl(22)
    # Entity: InspeccionOfflineSQLiteEntity(23), ModeloTFLiteQuantized(24)
    d3 = 3
    add_connector("1. Capturar frames cámara", "Association", 20, 22, d3)
    add_connector("2. Inyectar tensores a TFLite", "Association", 22, 24, d3)
    add_connector("3. Proyectar clasificaciones y baremo", "Association", 22, 21, d3)
    add_connector("4. Confirmar peritaje y UUIDv4 Key", "Association", 21, 22, d3)
    add_connector("5. Insertar inspección SQLite local", "Association", 22, 23, d3)

    # CU08 (DiagramID: 4)
    # Boundary: ColaSincronizacionOfflineView(26), SiniestrosSyncRestController(27)
    # Control: SyncIdempotentControl(28)
    # Entity: IdempotencyRecordEntity(29), ExpedienteSiniestroDocument(30)
    d4 = 4
    add_connector("1. POST sync con Idempotency-Key", "Association", 26, 27, d4)
    add_connector("2. Interceptar y validar SHA-256", "Association", 27, 28, d4)
    add_connector("3. Verificar o crear lock en DynamoDB", "Association", 28, 29, d4)
    add_connector("4. Persistir peritaje en MongoDB", "Association", 28, 30, d4)
    add_connector("5. Actualizar estado a COMPLETED", "Association", 28, 29, d4)
    add_connector("6. Retornar 201 Created / Cache HIT", "Association", 28, 26, d4)

    # CU09 (DiagramID: 5)
    # Boundary: LiquidacionSiniestroAdminView(32)
    # Control: SagaLiquidacionOrchestratorControl(33), ReclamoEstadoControl_MS2(34), PolizaCoberturaControl_MS1(35)
    # Entity: SagaInstanceEntity(36), OrdenLiquidacionEntity(37), ContratoPolizaEntity(38)
    d5 = 5
    add_connector("1. Iniciar liquidación ($1,200 BOB)", "Association", 32, 33, d5)
    add_connector("2. Registrar instancia Saga INICIADA", "Association", 33, 36, d5)
    add_connector("3. Paso 1: Bloquear siniestro MS2", "Association", 33, 34, d5)
    add_connector("4. Paso 2: Reservar cobertura MS1", "Association", 33, 35, d5)
    add_connector("5. Paso 3: Asentar orden de pago MS3", "Association", 33, 37, d5)
    add_connector("6. [Rollback Kafka] Liberar cobertura", "Association", 33, 35, d5)
    add_connector("7. [Rollback Kafka] Revertir estado siniestro", "Association", 33, 34, d5)

    # CU10 (DiagramID: 6)
    # Boundary: CobroPrimaQRView(40), PasarelaPagoBCBWebhook(41)
    # Control: PagoPrimaQRControl(42)
    # Entity: TransaccionPagoQREntity(43), IdempotencyRecordEntity_Pagos(44)
    d6 = 6
    add_connector("1. Solicitar generación QR de cuota", "Association", 40, 42, d6)
    add_connector("2. Retornar QR EMV con Idempotency-Key", "Association", 42, 40, d6)
    add_connector("3. Webhook confirmación de pago", "Association", 41, 42, d6)
    add_connector("4. Validar idempotencia en DynamoDB", "Association", 42, 44, d6)
    add_connector("5. Asentar ingreso contable en PostgreSQL", "Association", 42, 43, d6)

    # =========================================================================
    # 3. REORDENAMIENTO DE LIFELINES Y MENSAJES DE SECUENCIA UML 2.5+
    # =========================================================================

    def update_lifeline_order(diag_id, ordered_obj_ids):
        lx = 60
        rx_width = 130
        spacing = 210
        for obj_id in ordered_obj_ids:
            cur.execute("""
                UPDATE t_diagramobjects
                SET RectLeft = ?, RectRight = ?, RectTop = -40, RectBottom = -480
                WHERE Diagram_ID = ? AND Object_ID = ?
            """, (lx, lx + rx_width, diag_id, obj_id))
            lx += spacing

    # --- Secuencia CU06 (DiagramID: 7) ---
    d7 = 7
    # Orden lógico de izquierda a derecha:
    # SiniestroSosMobileView(14) -> SiniestroEmergencyControl(16) -> PeritoGuardiaEntity(18) -> ExpedienteSiniestroEntity(17) -> PushNotificationGateway(15)
    update_lifeline_order(d7, [14, 16, 18, 17, 15])
    add_connector("1. procesarReporteEmergencia(dto)", "Sequence", 14, 16, d7, seq_no=1, pt_y=-90)
    add_connector("2. buscarPeritoMasCercano(coords, 25km)", "Sequence", 16, 18, d7, seq_no=2, pt_y=-135)
    add_connector("3. peritoSeleccionado", "Sequence", 18, 16, d7, seq_no=3, pt_y=-180)
    add_connector("4. guardarExpediente(expedienteDoc)", "Sequence", 16, 17, d7, seq_no=4, pt_y=-225)
    add_connector("5. despacharAlertaPush(peritoId)", "Sequence", 16, 15, d7, seq_no=5, pt_y=-270)
    add_connector("6. 201 Created (ExpedienteRegistradoDto)", "Sequence", 16, 14, d7, seq_no=6, pt_y=-315)

    # --- Secuencia CU07 (DiagramID: 8) ---
    d8 = 8
    # Orden lógico:
    # CamaraPeritajeOfflineView(20) -> PeritajeOfflineTFLiteControl(22) -> ModeloTFLiteQuantized(24) -> FormularioDanosOfflineView(21) -> InspeccionOfflineSQLiteEntity(23)
    update_lifeline_order(d8, [20, 22, 24, 21, 23])
    add_connector("1. capturarFotografiasEvidencia(bytes)", "Sequence", 20, 22, d8, seq_no=1, pt_y=-90)
    add_connector("2. ejecutarInferenciaLocalTFLite(tensors)", "Sequence", 22, 24, d8, seq_no=2, pt_y=-135)
    add_connector("3. retornoClasificacion(DanoGrave, 94.2%)", "Sequence", 24, 22, d8, seq_no=3, pt_y=-180)
    add_connector("4. proyectarOverlayYBaremo(1200 BOB)", "Sequence", 22, 21, d8, seq_no=4, pt_y=-225)
    add_connector("5. confirmarInspeccion(IdempotencyKey)", "Sequence", 21, 22, d8, seq_no=5, pt_y=-270)
    add_connector("6. insertarInspeccionLocal(key, hash, EN_COLA_SQLITE)", "Sequence", 22, 23, d8, seq_no=6, pt_y=-315)

    # --- Secuencia CU08 (DiagramID: 9) ---
    d9 = 9
    # Orden lógico:
    # ColaSincronizacionOfflineView(26) -> SiniestrosSyncRestController(27) -> SyncIdempotentControl(28) -> IdempotencyRecordEntity(29) -> ExpedienteSiniestroDocument(30)
    update_lifeline_order(d9, [26, 27, 28, 29, 30])
    add_connector("1. POST /peritaje/sync (Headers: Idempotency-Key)", "Sequence", 26, 27, d9, seq_no=1, pt_y=-90)
    add_connector("2. sincronizarLoteIdempotente(key, payload)", "Sequence", 27, 28, d9, seq_no=2, pt_y=-135)
    add_connector("3. GetItem(idempotencyKey) [DynamoDB < 5ms]", "Sequence", 28, 29, d9, seq_no=3, pt_y=-180)
    add_connector("4. PutItem(status: PROCESSING, TTL: 120s)", "Sequence", 28, 29, d9, seq_no=4, pt_y=-225)
    add_connector("5. insertOne(peritajeDoc) [MongoDB 7]", "Sequence", 28, 30, d9, seq_no=5, pt_y=-270)
    add_connector("6. UpdateItem(status: COMPLETED, 201 Created)", "Sequence", 28, 29, d9, seq_no=6, pt_y=-315)
    add_connector("7. HTTP 201 Created / Replay Cache HIT", "Sequence", 27, 26, d9, seq_no=7, pt_y=-360)

    # --- Secuencia CU09 (DiagramID: 10) ---
    d10 = 10
    # Orden lógico:
    # LiquidacionSiniestroAdminView(32) -> SagaLiquidacionOrchestratorControl(33) -> SagaInstanceEntity(36) -> ReclamoEstadoControl_MS2(34) -> PolizaCoberturaControl_MS1(35) -> OrdenLiquidacionEntity(37)
    update_lifeline_order(d10, [32, 33, 36, 34, 35, 37])
    add_connector("1. iniciarSagaLiquidacion(siniestroId, 1200 BOB)", "Sequence", 32, 33, d10, seq_no=1, pt_y=-90)
    add_connector("2. guardarSagaInstance(INICIADA)", "Sequence", 33, 36, d10, seq_no=2, pt_y=-135)
    add_connector("3. Paso 1: PATCH /bloquear (EN_LIQUIDACION)", "Sequence", 33, 34, d10, seq_no=3, pt_y=-180)
    add_connector("4. Paso 2: POST /bloquear-cobertura (1200 BOB)", "Sequence", 33, 35, d10, seq_no=4, pt_y=-225)
    add_connector("5. Paso 3: insertOrdenLiquidacion(montoNeto: 1080 BOB)", "Sequence", 33, 37, d10, seq_no=5, pt_y=-270)
    add_connector("6. [Rollback Kafka] SagaCompensatePolicyCoverageEvent", "Sequence", 33, 35, d10, seq_no=6, pt_y=-315)
    add_connector("7. [Rollback Kafka] SagaRevertClaimStatusEvent", "Sequence", 33, 34, d10, seq_no=7, pt_y=-360)
    add_connector("8. 200 OK / 422 Rollback Ejecutado", "Sequence", 33, 32, d10, seq_no=8, pt_y=-405)

    # --- Secuencia CU10 (DiagramID: 11) ---
    d11 = 11
    # Orden lógico:
    # CobroPrimaQRView(40) -> PagoPrimaQRControl(42) -> IdempotencyRecordEntity_Pagos(44) -> PasarelaPagoBCBWebhook(41) -> TransaccionPagoQREntity(43)
    update_lifeline_order(d11, [40, 42, 44, 41, 43])
    add_connector("1. solicitarGeneracionQR(polizaId, 350 BOB)", "Sequence", 40, 42, d11, seq_no=1, pt_y=-90)
    add_connector("2. retornarStringQREMVCo(Idempotency-Key)", "Sequence", 42, 40, d11, seq_no=2, pt_y=-135)
    add_connector("3. webhookConfirmacionPago(Idempotency-Key)", "Sequence", 41, 42, d11, seq_no=3, pt_y=-180)
    add_connector("4. validarIdempotenciaPago(key, hash)", "Sequence", 42, 44, d11, seq_no=4, pt_y=-225)
    add_connector("5. insertTransaccionContable(monto, PAGADO)", "Sequence", 42, 43, d11, seq_no=5, pt_y=-270)
    add_connector("6. mostrarComprobanteFiscalElectronico(REC-99120)", "Sequence", 42, 40, d11, seq_no=6, pt_y=-315)

    # =========================================================================
    # 4. RELACIONES PARA DIAGRAMA DE CLASES DEL DOMINIO (DiagramID: 12)
    # =========================================================================
    d12 = 12
    add_connector("contieneInspecciones", "Association", 17, 23, d12)
    add_connector("protegidoPorIdempotencia", "Dependency", 23, 29, d12)
    add_connector("orquestaLiquidacion", "Association", 17, 36, d12)
    add_connector("generaOrdenDesembolso", "Association", 36, 37, d12)
    add_connector("bloqueaSiniestro", "Association", 33, 34, d12)
    add_connector("reservaCobertura", "Association", 33, 35, d12)
    add_connector("controlIdempotencia", "Dependency", 43, 44, d12)
    add_connector("asientaTransaccion", "Association", 42, 43, d12)
    add_connector("administraExpediente", "Association", 16, 17, d12)
    add_connector("ejecutaInferenciaLocal", "Usage", 22, 24, d12)

    conn.commit()
    conn.close()

    print(f"Éxito: Se crearon {connector_counter} relaciones (Connectors) con sus diagramlinks correspondientes.")
    print("Todas las lifelines fueron reordenadas de izquierda a derecha (Boundary -> Control -> Entity -> Gateways).")

if __name__ == "__main__":
    populate_relationships()
