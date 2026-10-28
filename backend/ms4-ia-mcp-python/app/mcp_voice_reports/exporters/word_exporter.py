"""
=============================================================================
 AegisCore AI - MS4: Generador de Minutas e Informes Word (.docx)
 Caso de Uso 15 (CU15) — Exportador de Alta Fidelidad Estética
 Emplea python-docx con estilo "Executive Precision":
   - Títulos formales, viñetas ejecutivas y tablas corporativas
   - Sombreado de encabezados con paleta Teal (#005C55)
   - Resumen de KPIs y bloque de firma pericial / actuarial
   - Firma criptográfica SHA-256
=============================================================================
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from app.entities.voice_mcp_dto import GeneratedDocumentDTO

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "artifacts" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class WordDocumentExporter:
    """Compilador de informes y minutas Word (.docx) para el Servidor MCP de AegisCore AI."""

    @classmethod
    def generar_reporte(
        cls,
        titulo: str,
        kpis: Dict[str, Any],
        columnas: List[str],
        filas: List[Dict[str, Any]],
        nombre_base: str = "reporte_ejecutivo"
    ) -> GeneratedDocumentDTO:
        """Compila y guarda un documento Word (.docx) estructurado."""
        doc = docx.Document()

        # Configuración de márgenes (1 pulgada)
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        # Colores
        COLOR_TEAL_RGB = RGBColor(0, 92, 85)
        COLOR_NAVY_RGB = RGBColor(15, 23, 42)
        COLOR_MUTED_RGB = RGBColor(100, 116, 139)

        # 1. Título Corporativo
        p_title = doc.add_paragraph()
        run_title = p_title.add_run(f"AEGISCORE AI — {titulo.upper()}")
        run_title.font.name = "Calibri"
        run_title.font.size = Pt(18)
        run_title.font.bold = True
        run_title.font.color.rgb = COLOR_TEAL_RGB
        p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_title.paragraph_format.space_after = Pt(2)

        # Subtítulo de Metadatos
        p_sub = doc.add_paragraph()
        run_sub = p_sub.add_run(
            f"Informe Oficial emitido vía Servidor MCP (Model Context Protocol) • "
            f"Fecha: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        run_sub.font.name = "Calibri"
        run_sub.font.size = Pt(9)
        run_sub.font.italic = True
        run_sub.font.color.rgb = COLOR_MUTED_RGB
        p_sub.paragraph_format.space_after = Pt(14)

        # 2. Resumen Ejecutivo de Métricas Clave (KPIs)
        if kpis:
            p_kpi_head = doc.add_paragraph()
            run_kh = p_kpi_head.add_run("MÉTRICAS CLAVE CONSOLIDADAS")
            run_kh.font.bold = True
            run_kh.font.size = Pt(11)
            run_kh.font.color.rgb = COLOR_NAVY_RGB
            p_kpi_head.paragraph_format.space_after = Pt(6)

            kpi_table = doc.add_table(rows=2, cols=len(list(kpis.keys())[:4]))
            kpi_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            shading_kpi = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))

            for idx, (k, v) in enumerate(list(kpis.items())[:4]):
                # Fila 1: Label
                cell_lbl = kpi_table.cell(0, idx)
                cell_lbl._tc.get_or_add_tcPr().append(parse_xml(r'<w:shd {} w:fill="F8FAFC"/>'.format(nsdecls('w'))))
                p_l = cell_lbl.paragraphs[0]
                r_l = p_l.add_run(k.replace("_", " ").title())
                r_l.font.size = Pt(8.5)
                r_l.font.bold = True
                r_l.font.color.rgb = COLOR_MUTED_RGB
                p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER

                # Fila 2: Valor
                cell_val = kpi_table.cell(1, idx)
                cell_val._tc.get_or_add_tcPr().append(parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w'))))
                p_v = cell_val.paragraphs[0]
                r_v = p_v.add_run(str(v))
                r_v.font.size = Pt(12)
                r_v.font.bold = True
                r_v.font.color.rgb = COLOR_TEAL_RGB
                p_v.alignment = WD_ALIGN_PARAGRAPH.CENTER

            doc.add_paragraph().paragraph_format.space_after = Pt(10)

        # 3. Tabla Estructurada de Datos
        if columnas and filas:
            p_tab_head = doc.add_paragraph()
            run_th = p_tab_head.add_run("DETALLE OPERACIONAL Y REGISTROS")
            run_th.font.bold = True
            run_th.font.size = Pt(11)
            run_th.font.color.rgb = COLOR_NAVY_RGB
            p_tab_head.paragraph_format.space_after = Pt(6)

            table = doc.add_table(rows=1, cols=len(columnas))
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr_cells = table.rows[0].cells

            for idx, col in enumerate(columnas):
                hdr_cells[idx]._tc.get_or_add_tcPr().append(parse_xml(r'<w:shd {} w:fill="005C55"/>'.format(nsdecls('w'))))
                p = hdr_cells[idx].paragraphs[0]
                r = p.add_run(col.replace("_", " ").title())
                r.font.bold = True
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(255, 255, 255)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

            for r_idx, fila in enumerate(filas[:35]):
                row_cells = table.add_row().cells
                fill_color = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
                shd = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), fill_color))

                for c_idx, col in enumerate(columnas):
                    row_cells[c_idx]._tc.get_or_add_tcPr().append(parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), fill_color)))
                    p = row_cells[c_idx].paragraphs[0]
                    val = fila.get(col, "")
                    if isinstance(val, float):
                        val_str = f"${val:,.2f}" if any(c in col.lower() for c in ["monto", "costo", "prima"]) else f"{val:.2f}"
                    else:
                        val_str = str(val)
                    r = p.add_run(val_str)
                    r.font.size = Pt(8)
                    r.font.color.rgb = COLOR_NAVY_RGB

            doc.add_paragraph().paragraph_format.space_after = Pt(16)

        # 4. Bloque de Cierre y Firma Actuarial / Pericial
        p_footer = doc.add_paragraph()
        run_f = p_footer.add_run(
            "Certificación de Autenticidad: Documento generado por el Servidor MCP de AegisCore AI. "
            "Filtrado bajo estándares OWASP Anti-SQLi y respaldado en la persistencia distribuida de Neon PostgreSQL y MongoDB Atlas."
        )
        run_f.font.size = Pt(8)
        run_f.font.italic = True
        run_f.font.color.rgb = COLOR_MUTED_RGB

        # 5. Guardar archivo y calcular firma criptográfica
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{nombre_base}_{timestamp_str}.docx"
        filepath = REPORTS_DIR / filename
        doc.save(str(filepath))

        with open(filepath, "rb") as f:
            file_bytes = f.read()
            sha256 = hashlib.sha256(file_bytes).hexdigest()
            filesize = len(file_bytes)

        return GeneratedDocumentDTO(
            filename=filename,
            format="docx",
            file_size_bytes=filesize,
            file_size_kb=round(filesize / 1024, 2),
            sha256_hash=sha256,
            download_url=f"/api/v1/mcp/download-report/{filename}",
            created_at=datetime.utcnow().isoformat()
        )
