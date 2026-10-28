"""
=============================================================================
 AegisCore AI - MS4: Generador de Planillas Excel (.xlsx)
 Caso de Uso 15 (CU15) — Exportador de Alta Fidelidad Estética
 Emplea openpyxl con estilos "Executive Precision":
   - Encabezados Executive Teal (#005C55)
   - Tipografía ejecutiva, bordes sutiles y zebra rows (#F8FAFC)
   - Formato numérico de moneda y cálculo de totales
   - Firma de integridad SHA-256
=============================================================================
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.entities.voice_mcp_dto import GeneratedDocumentDTO

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "artifacts" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class ExcelDocumentExporter:
    """Compilador de planillas ejecutivas Excel (.xlsx) para reportes aseguradores."""

    @classmethod
    def generar_reporte(
        cls,
        titulo: str,
        kpis: Dict[str, Any],
        columnas: List[str],
        filas: List[Dict[str, Any]],
        nombre_base: str = "reporte_ejecutivo"
    ) -> GeneratedDocumentDTO:
        """Compila y guarda una planilla Excel (.xlsx) con los datos provistos."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "AegisCore Report"
        ws.views.sheetView[0].showGridLines = True

        # Paleta Executive Precision
        COLOR_TEAL = "005C55"
        COLOR_TEAL_LIGHT = "0F766E"
        COLOR_BG_ZEBRA = "F8FAFC"
        COLOR_BORDER = "E2E8F0"

        font_title = Font(name="Calibri", size=16, bold=True, color="0F172A")
        font_subtitle = Font(name="Calibri", size=10, italic=True, color="64748B")
        font_kpi_label = Font(name="Calibri", size=9, bold=True, color="64748B")
        font_kpi_val = Font(name="Calibri", size=14, bold=True, color=COLOR_TEAL)
        font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        font_data = Font(name="Calibri", size=10, color="0F172A")
        font_footer = Font(name="Calibri", size=8, italic=True, color="94A3B8")

        fill_header = PatternFill(start_color=COLOR_TEAL, end_color=COLOR_TEAL, fill_type="solid")
        fill_zebra = PatternFill(start_color=COLOR_BG_ZEBRA, end_color=COLOR_BG_ZEBRA, fill_type="solid")
        fill_kpi = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

        border_thin = Border(
            left=Side(style="thin", color=COLOR_BORDER),
            right=Side(style="thin", color=COLOR_BORDER),
            top=Side(style="thin", color=COLOR_BORDER),
            bottom=Side(style="thin", color=COLOR_BORDER),
        )

        current_row = 1

        # 1. Título Corporativo
        ws.cell(row=current_row, column=1, value=f"AegisCore AI — {titulo.upper()}").font = font_title
        current_row += 1
        ws.cell(
            row=current_row,
            column=1,
            value=f"Generado automáticamente vía Protocolo MCP • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        ).font = font_subtitle
        current_row += 2

        # 2. Bloque de Tarjetas KPI
        if kpis:
            col_kpi = 1
            for kpi_key, kpi_val in kpis.items():
                label = kpi_key.replace("_", " ").title()
                ws.cell(row=current_row, column=col_kpi, value=label).font = font_kpi_label
                ws.cell(row=current_row, column=col_kpi).fill = fill_kpi
                ws.cell(row=current_row, column=col_kpi).border = border_thin

                val_cell = ws.cell(row=current_row + 1, column=col_kpi, value=kpi_val)
                val_cell.font = font_kpi_val
                val_cell.fill = fill_kpi
                val_cell.border = border_thin
                val_cell.alignment = Alignment(horizontal="center")
                col_kpi += 2
            current_row += 3

        # 3. Encabezados de Tabla
        start_table_row = current_row
        for col_idx, col_name in enumerate(columnas, start=1):
            cell = ws.cell(row=current_row, column=col_idx, value=col_name.replace("_", " ").title())
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border_thin
        current_row += 1

        # 4. Filas de Datos
        for row_idx, fila in enumerate(filas, start=current_row):
            is_zebra = (row_idx % 2 == 0)
            for col_idx, col_name in enumerate(columnas, start=1):
                val = fila.get(col_name, "")
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.font = font_data
                cell.border = border_thin
                if is_zebra:
                    cell.fill = fill_zebra

                # Formateo numérico si aplica
                if isinstance(val, (int, float)):
                    if any(c in col_name.lower() for c in ["monto", "costo", "prima", "precio", "estimado", "indemnizacion"]):
                        cell.number_format = '"$"#,##0.00'
                    elif "porcentaje" in col_name.lower() or "ratio" in col_name.lower():
                        cell.number_format = '0.00%'

        current_row += len(filas) + 2

        # 5. Ajuste automático de anchos de columna
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len and len(val_str) < 50:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        # 6. Guardar en disco y calcular Hash SHA-256
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{nombre_base}_{timestamp_str}.xlsx"
        filepath = REPORTS_DIR / filename
        wb.save(filepath)

        with open(filepath, "rb") as f:
            file_bytes = f.read()
            sha256 = hashlib.sha256(file_bytes).hexdigest()
            filesize = len(file_bytes)

        return GeneratedDocumentDTO(
            filename=filename,
            format="xlsx",
            file_size_bytes=filesize,
            file_size_kb=round(filesize / 1024, 2),
            sha256_hash=sha256,
            download_url=f"/api/v1/mcp/download-report/{filename}",
            created_at=datetime.utcnow().isoformat()
        )
