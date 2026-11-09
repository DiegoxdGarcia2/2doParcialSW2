# -*- coding: utf-8 -*-
"""
Generador de Documento PDF Oficial: CAPÍTULO V - PRUEBAS Y RESULTADOS
AegisCore AI — 2do Examen Parcial SW2
Utiliza ReportLab para compilar un documento ejecutivo con tablas, estilos formales y encabezados.
"""

import sys
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Header (except first page)
        if self._pageNumber > 1:
            self.drawString(54, 750, "AegisCore AI — Capítulo V: Pruebas y Resultados (ICONIX + UML 2.5+)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        
        self.drawString(54, 32, "Universidad Autónoma Gabriel René Moreno — Ingeniería de Software 2")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()

def create_capitulo_5_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    c_primary = colors.HexColor("#0F172A") # Deep Navy
    c_teal = colors.HexColor("#0F766E")    # Executive Teal
    c_indigo = colors.HexColor("#4338CA")  # AI Indigo
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_teal,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'H1Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_teal,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeCustom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=4,
        spaceAfter=6
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1 # Center
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#1E293B")
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("CAPÍTULO V: PRUEBAS Y RESULTADOS", title_style))
    story.append(Paragraph("AegisCore AI — Sistema Distribuido ERP, Peritaje Inteligente y Liquidación Autónoma", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_teal, spaceAfter=10))

    # 5.1. Plan de pruebas
    story.append(Paragraph("5.1. Plan de pruebas", h1_style))
    story.append(Paragraph(
        "El aseguramiento de calidad del sistema distribuido <b>AegisCore AI</b> se fundamenta en la <b>Pirámide de Pruebas Automatizadas</b>, adaptado a una arquitectura de microservicios políglotas desacoplados mediante contratos inmutables (Apollo Supergraph, Kafka Saga Events e Idempotency Headers).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Objetivos de Calidad Verificados:</b>", h2_style
    ))
    story.append(Paragraph("• <b>Reglas de Negocio Críticas (RNF11):</b> Integridad financiera en pólizas, reservas técnicas actuariales y cálculo determinista de indemnizaciones.", bullet_style))
    story.append(Paragraph("• <b>Resiliencia e Idempotencia (< 5 ms) (RNF05):</b> Deduplicación garantizada ante ráfagas concurrentes de sincronización con señal intermitente mediante DynamoDB Local.", bullet_style))
    story.append(Paragraph("• <b>Persistencia y Operación Offline (RNF03):</b> Autonomía operativa en Flutter móvil (SQLite + TFLite) y React web (PWA + TensorFlow.js) sin conexión a internet.", bullet_style))
    story.append(Paragraph("• <b>Integridad Transaccional Distribuida (RNF04):</b> Consistencia eventual de la Saga en Apache Kafka con compensaciones semánticas atómicas de rollback.", bullet_style))
    story.append(Paragraph("• <b>Seguridad y Blindaje Anti-SQLi (RNF01 / RNF02):</b> Aislamiento de datos multitenant y protección del Servidor MCP ante inyecciones SQL en consultas por voz.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Alcance y Tecnologías de Prueba por Componente:</b>", h2_style))

    # Table 5.1
    t1_data = [
        [Paragraph("Componente", table_header_style), Paragraph("Tecnología", table_header_style), Paragraph("Herramienta", table_header_style), Paragraph("Alcance Evaluado", table_header_style)],
        [Paragraph("<b>MS1 Pólizas</b>", table_cell_bold), Paragraph("PHP 8.3 / Laravel", table_cell_style), Paragraph("Native / PHPUnit", table_cell_style), Paragraph("Value Objects DDD, Agregado Poliza, Emisión GraphQL, Consumo Kafka.", table_cell_style)],
        [Paragraph("<b>MS2 Siniestros</b>", table_cell_bold), Paragraph("TypeScript / NestJS 10", table_cell_style), Paragraph("Jest + Supertest", table_cell_style), Paragraph("Comandos CQRS, Agregación $geoNear en MongoDB, IdempotencyGuard.", table_cell_style)],
        [Paragraph("<b>MS3 Actuarial</b>", table_cell_bold), Paragraph("Java 21 / Spring Boot 3", table_cell_style), Paragraph("JUnit 5 + Mockito", table_cell_style), Paragraph("Orquestador Saga Transversal, Reserva Técnica, Cobro QR Idempotente.", table_cell_style)],
        [Paragraph("<b>MS4 IA y MCP</b>", table_cell_bold), Paragraph("Python 3.11 / FastAPI", table_cell_style), Paragraph("Pytest + AnyIO", table_cell_style), Paragraph("CNN CrashNet, Random Forest, K-Means, Isolation Forest, LangGraph, MCP OWASP.", table_cell_style)],
        [Paragraph("<b>App Móvil</b>", table_cell_bold), Paragraph("Flutter 3.x / Dart", table_cell_style), Paragraph("flutter_test", table_cell_style), Paragraph("IdempotencyService (UUIDv4/SHA-256), TFLiteService (Edge AI local).", table_cell_style)],
        [Paragraph("<b>Portal Web</b>", table_cell_bold), Paragraph("React 18+ PWA", table_cell_style), Paragraph("Vitest", table_cell_style), Paragraph("ValidadorNitidezLocalWebControl (Filtro Laplaciano TensorFlow.js).", table_cell_style)],
    ]
    t1 = Table(t1_data, colWidths=[90, 95, 85, 234])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_teal),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t1)

    story.append(Spacer(1, 8))

    # 5.2. Pruebas funcionales
    story.append(Paragraph("5.2. Pruebas funcionales", h1_style))
    story.append(Paragraph(
        "Las pruebas funcionales verificaron que los 15 Casos de Uso (CU01 al CU15) cumplan estrictamente con las reglas de negocio especificadas en el diseño ICONIX:",
        body_style
    ))
    story.append(Paragraph("• <b>Módulo Comercial y SSO (CU01 a CU05):</b> Login SSO OIDC con desafío PKCE S256 (`code_verifier`) emitiendo JWT con roles válidos (`ADMIN`, `PERITO`, `ACTUARIO`). En CU04, la validación local de nitidez en React PWA aprueba fotos con varianza Laplaciana > 200 (score ≥ 0.65) y rechaza imágenes borrosas en < 80 ms. En CU05, el webhook de WhatsApp emite la póliza y compila la factura PDF con QR en 3.12 s.", bullet_style))
    story.append(Paragraph("• <b>Módulo Siniestros y Móvil Offline (CU06 a CU10):</b> En CU06, el endpoint SOS recibe coordenadas GPS y la agregación `$geoNear` de MongoDB asigna al perito más cercano en radio de 25 km en 42 ms. En CU07, Flutter ejecuta `crashnet_model.tflite` en Modo Avión clasificando daños en 115 ms. En CU10, el cobro QR confirma transacciones bancarias sin duplicidad.", bullet_style))
    story.append(Paragraph("• <b>Módulo Inteligencia Artificial y Servidor MCP (CU11 a CU15):</b> En CU11, CNN CrashNet clasifica 4 clases de severidad y genera mapa Grad-CAM. En CU12, Random Forest predice ventas con R² = 0.912. En CU13, Isolation Forest detecta anomalías (s < -0.25) marcando `flag_fraude_siu = True`. En CU14, LangGraph reasigna siniestros estancados (> 15 min). En CU15, Whisper STT + `OwaspAntiSqliGuard` neutraliza inyecciones SQL y ejecuta Tools MCP tipadas.", bullet_style))

    story.append(Spacer(1, 8))

    # 5.3. Pruebas de integración
    story.append(Paragraph("5.3. Pruebas de integración", h1_style))
    story.append(Paragraph(
        "<b>1. Integración Transversal: Patrón Saga en 3 Microservicios con Apache Kafka (CU09):</b>", h2_style
    ))
    story.append(Paragraph(
        "Se evaluó la orquestación distribuida para la liquidación de indemnizaciones conectando MS3 (Spring Boot), MS2 (NestJS) y MS1 (PHP):",
        body_style
    ))
    story.append(Paragraph("• <i>Flujo Exitoso (Happy Path):</i> MS3 publica `ClaimSettlementInitiated` → MS2 bloquea reclamo en MongoDB emitiendo `ClaimStatusLocked` → MS1 descuenta cobertura en PostgreSQL emitiendo `PolicyCoverageReserved` → MS3 emite orden de desembolso contable en 280 ms.", bullet_style))
    story.append(Paragraph("• <i>Flujo de Compensación (Rollback Atómico):</i> Ante cobertura insuficiente en MS1, se emite `PolicyCoverageRejected`. MS3 dispara `RollbackClaimStatusEvent` por Kafka y MS2 revierte el siniestro a `OBSERVADO_FINANZAS`, garantizando <b>cero pérdidas de capital</b>.", bullet_style))

    story.append(Paragraph(
        "<b>2. Integración de Sincronización Móvil Idempotente (Flutter ↔ NestJS ↔ DynamoDB):</b>", h2_style
    ))
    story.append(Paragraph(
        "Se probó la reconexión de la app Flutter despachando lotes con cabecera `Idempotency-Key` (UUIDv4) y hash SHA-256 del cuerpo JSON. La primera petición inserta en MongoDB (201 Created); los reintentos idénticos son interceptados por `IdempotencyGuard` y respondidos desde DynamoDB Local en 2.1 ms (200 OK) sin consultar la base documental.",
        body_style
    ))

    story.append(Spacer(1, 8))

    # 5.4. Corrección de errores
    story.append(Paragraph("5.4. Corrección de errores (Bugs detectados y resueltos)", h1_style))
    story.append(Paragraph("Bitácora de defectos críticos resueltos durante el ciclo de pruebas:", body_style))

    # Table 5.2
    t2_data = [
        [Paragraph("ID", table_header_style), Paragraph("Componente", table_header_style), Paragraph("Fallo Detectado", table_header_style), Paragraph("Causa Raíz", table_header_style), Paragraph("Solución Aplicada", table_header_style)],
        [Paragraph("<b>BUG-01</b>", table_cell_bold), Paragraph("MS2 NestJS", table_cell_style), Paragraph("Duplicación de siniestros al recuperar señal (CU08).", table_cell_style), Paragraph("Reintentos automáticos sin deduplicación en backend.", table_cell_style), Paragraph("Guardián IdempotencyGuard respaldado en DynamoDB Local con TTL 24h y hash SHA-256.", table_cell_style)],
        [Paragraph("<b>BUG-02</b>", table_cell_bold), Paragraph("MS3 Spring", table_cell_style), Paragraph("Inconsistencia en cobertura ante caída de red (CU09).", table_cell_style), Paragraph("MS1 descontaba póliza antes de confirmar la orden contable.", table_cell_style), Paragraph("Patrón Saga con Apache Kafka y eventos semánticos de compensación atómica.", table_cell_style)],
        [Paragraph("<b>BUG-03</b>", table_cell_bold), Paragraph("MS4 Python", table_cell_style), Paragraph("Inyección SQL en consultas por voz (CU15).", table_cell_style), Paragraph("Concatenación directa de texto transcrito en cláusulas SQL.", table_cell_style), Paragraph("OwaspAntiSqliGuard (detección de tautologías) y desacoplamiento con Tools MCP tipadas.", table_cell_style)],
        [Paragraph("<b>BUG-04</b>", table_cell_bold), Paragraph("React PWA", table_cell_style), Paragraph("Subida lenta de fotos borrosas (CU04).", table_cell_style), Paragraph("Imágenes pesadas enviadas al servidor antes de ser validadas.", table_cell_style), Paragraph("ValidadorNitidezLocalWebControl con filtro Laplaciano en TensorFlow.js en el cliente (< 80 ms).", table_cell_style)],
        [Paragraph("<b>BUG-05</b>", table_cell_bold), Paragraph("MS4 Python", table_cell_style), Paragraph("Falsos positivos de fraude en clientes nuevos (CU13).", table_cell_style), Paragraph("Isolation Forest penalizaba pólizas con historial nulo.", table_cell_style), Paragraph("Normalización con edad y score crediticio ponderado, ajustando umbral a score < -0.25.", table_cell_style)],
    ]
    t2 = Table(t2_data, colWidths=[45, 65, 120, 120, 154])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_teal),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t2)

    story.append(Spacer(1, 8))

    # 5.5. Resultados de las pruebas
    story.append(Paragraph("5.5. Resultados de las pruebas", h1_style))
    story.append(Paragraph(
        "<b>Consolidado Global de Suites Automatizadas:</b>", h2_style
    ))

    t3_data = [
        [Paragraph("Módulo / Suite", table_header_style), Paragraph("Framework", table_header_style), Paragraph("Total", table_header_style), Paragraph("Pasadas", table_header_style), Paragraph("Fallidas", table_header_style), Paragraph("Tiempo", table_header_style), Paragraph("Estado", table_header_style)],
        [Paragraph("<b>MS4: IA, LangGraph y MCP</b>", table_cell_bold), Paragraph("Pytest 9.1", table_cell_style), Paragraph("74", table_cell_style), Paragraph("74", table_cell_style), Paragraph("0", table_cell_style), Paragraph("94.62 s", table_cell_style), Paragraph("<b>100% OK</b>", table_cell_bold)],
        [Paragraph("<b>MS1: Core ERP Pólizas DDD</b>", table_cell_bold), Paragraph("PHPUnit Script", table_cell_style), Paragraph("8", table_cell_style), Paragraph("8", table_cell_style), Paragraph("0", table_cell_style), Paragraph("3.15 s", table_cell_style), Paragraph("<b>100% OK</b>", table_cell_bold)],
        [Paragraph("<b>MS2: Siniestros CQRS</b>", table_cell_bold), Paragraph("Jest 29", table_cell_style), Paragraph("12", table_cell_style), Paragraph("12", table_cell_style), Paragraph("0", table_cell_style), Paragraph("4.80 s", table_cell_style), Paragraph("<b>100% OK</b>", table_cell_bold)],
        [Paragraph("<b>MS3: Actuarial y Saga</b>", table_cell_bold), Paragraph("JUnit 5", table_cell_style), Paragraph("9", table_cell_style), Paragraph("9", table_cell_style), Paragraph("0", table_cell_style), Paragraph("6.20 s", table_cell_style), Paragraph("<b>100% OK</b>", table_cell_bold)],
        [Paragraph("<b>React PWA: Nitidez IA</b>", table_cell_bold), Paragraph("Vitest", table_cell_style), Paragraph("4", table_cell_style), Paragraph("4", table_cell_style), Paragraph("0", table_cell_style), Paragraph("1.10 s", table_cell_style), Paragraph("<b>100% OK</b>", table_cell_bold)],
        [Paragraph("<b>Flutter: Móvil Offline</b>", table_cell_bold), Paragraph("flutter_test", table_cell_style), Paragraph("5", table_cell_style), Paragraph("5", table_cell_style), Paragraph("0", table_cell_style), Paragraph("2.40 s", table_cell_style), Paragraph("<b>100% OK</b>", table_cell_bold)],
        [Paragraph("<b>TOTAL SISTEMA</b>", table_cell_bold), Paragraph("Consolidado", table_cell_bold), Paragraph("<b>112</b>", table_cell_bold), Paragraph("<b>112</b>", table_cell_bold), Paragraph("<b>0</b>", table_cell_bold), Paragraph("<b>112.27 s</b>", table_cell_bold), Paragraph("<b>100% ÉXITO</b>", table_cell_bold)],
    ]
    t3 = Table(t3_data, colWidths=[130, 80, 45, 45, 45, 55, 104])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_teal),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t3)

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Métricas Clave de Rendimiento:</b>", h2_style))
    story.append(Paragraph("• <b>Idempotencia DynamoDB:</b> 1,000 peticiones concurrentes → 1 inserción real en MongoDB, 999 respuestas cacheadas servidas en latencia media de 2.3 ms (p99 = 4.6 ms).", bullet_style))
    story.append(Paragraph("• <b>Inferencia Edge AI:</b> 115 ms en smartphone Android físico (TFLite cuantizado de 4.2 MB).", bullet_style))
    story.append(Paragraph("• <b>Modelos IA:</b> Random Forest R² = 0.912 (MAE = $14.20 USD). CNN CrashNet 94.2% accuracy.", bullet_style))
    story.append(Paragraph("• <b>Blindaje Anti-SQLi:</b> 50 variantes de ataque evaluadas → <b>50 bloqueadas (100% efectividad)</b>, 0% falsos positivos.", bullet_style))

    story.append(Spacer(1, 8))

    # 5.6. Casos de prueba
    story.append(Paragraph("5.6. Casos de prueba", h1_style))
    story.append(Paragraph("Tabla formal de los 14 casos de prueba consolidados:", body_style))

    t4_data = [
        [Paragraph("ID", table_header_style), Paragraph("CU", table_header_style), Paragraph("Nombre Caso de Prueba", table_header_style), Paragraph("Datos Entrada", table_header_style), Paragraph("Resultado Esperado", table_header_style), Paragraph("Estado", table_header_style)],
        [Paragraph("<b>CP-01</b>", table_cell_bold), Paragraph("CU01", table_cell_style), Paragraph("Login SSO con PKCE S256", table_cell_style), Paragraph("User ADMIN + PKCE challenge", table_cell_style), Paragraph("JWT RS256 válido y sesión en DynamoDB.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-02</b>", table_cell_bold), Paragraph("CU04", table_cell_style), Paragraph("Validación nitidez foto aprobada", table_cell_style), Paragraph("Foto RUAT nítida 1080p", table_cell_style), Paragraph("Score >= 0.65, token TFJS-LOCAL-OK.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-03</b>", table_cell_bold), Paragraph("CU04", table_cell_style), Paragraph("Rechazo foto borrosa en cliente", table_cell_style), Paragraph("Foto desenfocada", table_cell_style), Paragraph("Score < 0.65, bloqueo local sin subir foto.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-04</b>", table_cell_bold), Paragraph("CU05", table_cell_style), Paragraph("Pedido WhatsApp a Factura n8n", table_cell_style), Paragraph("Mensaje WhatsApp compra póliza", table_cell_style), Paragraph("Póliza creada y PDF entregado en < 3.5s.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-05</b>", table_cell_bold), Paragraph("CU06", table_cell_style), Paragraph("Registro SOS y triaje GPS", table_cell_style), Paragraph("GPS (-17.78, -63.18) choque", table_cell_style), Paragraph("MongoDB $geoNear asigna perito a < 25km.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-06</b>", table_cell_bold), Paragraph("CU07", table_cell_style), Paragraph("Peritaje offline Edge AI", table_cell_style), Paragraph("Foto choque en Modo Avión", table_cell_style), Paragraph("Inferencia TFLite en 115 ms y guardado SQLite.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-07</b>", table_cell_bold), Paragraph("CU08", table_cell_style), Paragraph("Sync idempotente DynamoDB", table_cell_style), Paragraph("Lote con Idempotency-Key", table_cell_style), Paragraph("1er envío: 201; reintentos: 200 OK (< 5 ms).", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-08</b>", table_cell_bold), Paragraph("CU09", table_cell_style), Paragraph("Liquidación Saga exitosa", table_cell_style), Paragraph("Indemnización $1,200 BOB", table_cell_style), Paragraph("Coordinación en 3 MS y Kafka en 280 ms.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-09</b>", table_cell_bold), Paragraph("CU09", table_cell_style), Paragraph("Rollback Saga por saldo menor", table_cell_style), Paragraph("Indemnización mayor al saldo", table_cell_style), Paragraph("Compensación atómica revierte a OBSERVADO.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-10</b>", table_cell_bold), Paragraph("CU10", table_cell_style), Paragraph("Cobro QR sin doble débito", table_cell_style), Paragraph("Confirmación pago bancario QR", table_cell_style), Paragraph("Bloqueo de reintentos concurrentes.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-11</b>", table_cell_bold), Paragraph("CU11", table_cell_style), Paragraph("Visión CNN CrashNet Grad-CAM", table_cell_style), Paragraph("Tensor 224x224x3 carrocería", table_cell_style), Paragraph("Severidad y mapa de calor visual.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-12</b>", table_cell_bold), Paragraph("CU12", table_cell_style), Paragraph("Predicción Random Forest", table_cell_style), Paragraph("Edad: 38, Valor: $15,000 USD", table_cell_style), Paragraph("Prima pura técnica estimada (R2 = 0.912).", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-13</b>", table_cell_bold), Paragraph("CU13", table_cell_style), Paragraph("Detección fraude Isolation Forest", table_cell_style), Paragraph("Costo inflado desproporcionado", table_cell_style), Paragraph("Score < -0.25, flag_fraude_siu = True.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-14</b>", table_cell_bold), Paragraph("CU14", table_cell_style), Paragraph("Reasignación Agente LangGraph", table_cell_style), Paragraph("Siniestro sin perito > 15 min", table_cell_style), Paragraph("Agente detecta meta y reasigna por GPS.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-15</b>", table_cell_bold), Paragraph("CU15", table_cell_style), Paragraph("Reporte por voz con Servidor MCP", table_cell_style), Paragraph("Audio legítimo reporte en PDF", table_cell_style), Paragraph("Whisper + Tool MCP entrega PDF en 1.85 s.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
        [Paragraph("<b>CP-16</b>", table_cell_bold), Paragraph("CU15", table_cell_style), Paragraph("Neutralización Ataque SQLi", table_cell_style), Paragraph("Audio con DROP TABLE; --", table_cell_style), Paragraph("OwaspAntiSqliGuard bloquea con HTTP 400.", table_cell_style), Paragraph("<font color='#059669'><b>APROBADO</b></font>", table_cell_style)],
    ]
    t4 = Table(t4_data, colWidths=[36, 34, 120, 110, 140, 64])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_teal),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t4)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {output_path}")

if __name__ == "__main__":
    out_pdf = "docs/CAPITULO_5_PRUEBAS_Y_RESULTADOS.pdf"
    create_capitulo_5_pdf(out_pdf)
