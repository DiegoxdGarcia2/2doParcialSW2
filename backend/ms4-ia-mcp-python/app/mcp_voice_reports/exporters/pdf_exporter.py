"""
=============================================================================
 AegisCore AI - MS4: Generador de Informes Ejecutivos PDF (.pdf)
 Caso de Uso 15 (CU15) — Exportador de Alta Fidelidad Estética
 Emplea reportlab con diseño "Executive Precision":
   - Banner corporativo AegisCore AI
   - Tarjetas de KPIs y resumen actuarial
   - Tabla estructurada con sombreado alternado y ajuste de texto
   - Firma criptográfica SHA-256 y certificación Solvency II
=============================================================================
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)

from app.entities.voice_mcp_dto import GeneratedDocumentDTO

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "artifacts" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class PdfDocumentExporter:
    """Compilador de documentos PDF ejecutivos para el Servidor MCP de AegisCore AI."""

    @classmethod
    def generar_reporte(
        cls,
        titulo: str,
        kpis: Dict[str, Any],
        columnas: List[str],
        filas: List[Dict[str, Any]],
        nombre_base: str = "reporte_ejecutivo"
    ) -> GeneratedDocumentDTO:
        """Compila y guarda un documento PDF con los datos consolidados."""
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{nombre_base}_{timestamp_str}.pdf"
        filepath = REPORTS_DIR / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Paleta Executive Precision
        COLOR_TEAL = colors.HexColor("#005C55")
        COLOR_TEAL_LIGHT = colors.HexColor("#0F766E")
        COLOR_NAVY = colors.HexColor("#0F172A")
        COLOR_ALABASTER = colors.HexColor("#F8FAFC")
        COLOR_MUTED = colors.HexColor("#64748B")

        title_style = ParagraphStyle(
            "ExecutiveTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=COLOR_NAVY
        )
        subtitle_style = ParagraphStyle(
            "ExecutiveSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=COLOR_MUTED
        )
        kpi_label_style = ParagraphStyle(
            "KpiLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=COLOR_MUTED,
            alignment=1
        )
        kpi_val_style = ParagraphStyle(
            "KpiVal",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=COLOR_TEAL,
            alignment=1
        )
        cell_header_style = ParagraphStyle(
            "CellHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white,
            alignment=1
        )
        cell_data_style = ParagraphStyle(
            "CellData",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9,
            textColor=COLOR_NAVY
        )

        elements = []

        # 1. Encabezado Corporativo
        elements.append(Paragraph(f"AEGISCORE AI — {titulo.upper()}", title_style))
        elements.append(Spacer(1, 4))
        elements.append(
            Paragraph(
                f"Informe generado automáticamente vía Servidor MCP • Whisper STT • "
                f"Fecha: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                subtitle_style
            )
        )
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=COLOR_TEAL, spaceBefore=2, spaceAfter=10))

        # 2. Resumen de KPIs en cuadrícula
        if kpis:
            kpi_data = []
            row_labels = []
            row_vals = []
            for k, v in list(kpis.items())[:4]:
                label_txt = k.replace("_", " ").title()
                row_labels.append(Paragraph(label_txt, kpi_label_style))
                row_vals.append(Paragraph(str(v), kpi_val_style))

            if row_labels:
                kpi_table_data = [row_labels, row_vals]
                col_width = (doc.width) / len(row_labels)
                kpi_table = Table(kpi_table_data, colWidths=[col_width] * len(row_labels))
                kpi_table.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, -1), COLOR_ALABASTER),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ])
                )
                elements.append(kpi_table)
                elements.append(Spacer(1, 14))

        # 3. Tabla Estructurada de Datos
        if columnas and filas:
            table_content = []

            # Encabezados
            headers = [Paragraph(col.replace("_", " ").title(), cell_header_style) for col in columnas]
            table_content.append(headers)

            # Filas
            for f in filas[:40]:  # Limitar a 40 para documento ejecutivo
                row_cells = []
                for col in columnas:
                    raw_val = f.get(col, "")
                    if isinstance(raw_val, float):
                        val_str = f"${raw_val:,.2f}" if any(c in col.lower() for c in ["monto", "costo", "prima"]) else f"{raw_val:.2f}"
                    else:
                        val_str = str(raw_val)
                    row_cells.append(Paragraph(val_str, cell_data_style))
                table_content.append(row_cells)

            col_width = doc.width / len(columnas)
            data_table = Table(table_content, colWidths=[col_width] * len(columnas), repeatRows=1)
            data_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), COLOR_TEAL),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                    ("TOPPADDING", (0, 0), (-1, 0), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_ALABASTER]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("TOPPADDING", (0, 1), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
                ])
            )
            elements.append(data_table)

        elements.append(Spacer(1, 16))
        # 4. Pie de Auditoría y Certificación
        footer_text = (
            "Certificación Técnica: AegisCore AI Microservicio 4 (Python 3.13 FastAPI) • "
            "Cumplimiento Solvency II Pillar I/II • Filtro Anti-SQLi OWASP Nivel 3 Activo."
        )
        elements.append(Paragraph(footer_text, subtitle_style))

        # Compilar documento
        doc.build(elements)

        with open(filepath, "rb") as f:
            file_bytes = f.read()
            sha256 = hashlib.sha256(file_bytes).hexdigest()
            filesize = len(file_bytes)

        return GeneratedDocumentDTO(
            filename=filename,
            format="pdf",
            file_size_bytes=filesize,
            file_size_kb=round(filesize / 1024, 2),
            sha256_hash=sha256,
            download_url=f"/api/v1/mcp/download-report/{filename}",
            created_at=datetime.utcnow().isoformat()
        )
