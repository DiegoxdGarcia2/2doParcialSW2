"""
=============================================================================
 AegisCore AI - MS4: Script de Sincronización y Verificación End-to-End de Amazon S3
 Perfil C (CU11 a CU15)
 Bucket Objetivo: servicio-de-seguros-aegiscore (us-east-2)
=============================================================================
"""

import sys
import os
from pathlib import Path

# Configurar encoding seguro para consola Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Agregar directorio raíz del microservicio al sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings
from app.services.s3_storage_service import s3_storage_service
from app.controls.random_forest_service import actuarial_control
from app.controls.unsupervised_fraud_control import unsupervised_control
from app.controls.crashnet_vision_control import crashnet_vision_control
from app.controls.langgraph_autonomous_agent import langgraph_agent_control
from app.controls.voice_mcp_control import VoiceMcpControl
from app.entities.dl_vision_dto import DamageAnalysisInputDTO


def ejecutar_sincronizacion_s3_perfil_c():
    print("=" * 80)
    print("🚀 INICIANDO SINCRONIZACIÓN Y POBLACIÓN DE AMAZON S3 - PERFIL C")
    print(f"Bucket: {s3_storage_service.bucket} | Región: {s3_storage_service.region}")
    print("=" * 80)

    # 1. Comprobar Conexión
    ok, msg = s3_storage_service.verificar_conexion_bucket()
    print(f"\n[PASO 1] Estado Conexión Bucket: {ok} -> {msg}")
    if not ok:
        print("❌ Error: No se puede conectar a Amazon S3. Abortando.")
        return False

    # 2. Sincronizar Model Registry ML (CU12 & CU13)
    print("\n[PASO 2] Sincronizando Model Registry en S3 (modelos-ml/v2.1/)...")
    res_rf = actuarial_control.sincronizar_modelos_en_s3(version="v2.1")
    for fname, data in res_rf.items():
        print(f"  -> RF Model: {fname} -> {data['status']} ({data['size_bytes']:,} bytes) | S3: {data['s3_key']}")

    res_unsup = unsupervised_control.sincronizar_modelos_en_s3(version="v2.1")
    for fname, data in res_unsup.items():
        print(f"  -> Unsup Model: {fname} -> {data['status']} ({data['size_bytes']:,} bytes) | S3: {data['s3_key']}")

    # 3. CU11 - Pipeline Peritaje Técnico con PDF, LiDAR y Evidencia S3
    print("\n[PASO 3] Ejecutando CU11 (Peritaje Inteligente + Dictamen PDF S3)...")
    input_dto = DamageAnalysisInputDTO(
        numero_reclamo="REC-2026-00492",
        numero_poliza="POL-2026-AUT-00892",
        angulo_toma="FRONTAL_CUARTO_DERECHO",
        modelo_vehiculo="Toyota RAV4 2024"
    )
    assessment = crashnet_vision_control.analizar_fotografia_siniestro(input_dto)
    print(f"  -> Reclamo: {assessment.numero_reclamo}")
    print(f"  -> Gravedad IA: {assessment.gravedad_global} (Score: {assessment.score_danos_global})")
    print(f"  -> Reparación Bruta: ${assessment.liquidacion_financiera.costo_total_reparacion_usd:,.2f} USD")
    print(f"  -> S3 Dictamen PDF URL: {assessment.s3_dictamen_pdf_url}")
    print(f"  -> S3 Key Dictamen: {assessment.s3_key_dictamen}")
    print(f"  -> S3 Telemetría LiDAR: {assessment.s3_telemetria_lidar_url}")

    # 4. CU14 - Auditoría de Ciclos LangGraph en S3
    print("\n[PASO 4] Ejecutando CU14 (Ciclo Autónomo LangGraph + Auditoría S3)...")
    try:
        run_res = langgraph_agent_control.ejecutar_ciclo_autonomo()
        print(f"  -> Ciclo ID: {run_res.ciclo_id} | Duración: {run_res.duracion_total_ms} ms")
        print(f"  -> Skills Disparadas: {len(run_res.skills_disparadas)}")
    except Exception as e_agent:
        print(f"  -> Advertencia en ciclo LangGraph: {e_agent}")

    # 5. CU15 - Reporte Generativo Dual MCP en S3
    print("\n[PASO 5] Ejecutando CU15 (Voz MCP -> Reportes Duales S3)...")
    mcp_ctrl = VoiceMcpControl()
    doc_pdf = mcp_ctrl.exportarReporteDocumento(
        titulo="Reporte Oficial Solvencia y Reservas Técnicas",
        kpis={"ratio_siniestralidad": "26.7%", "reserva_tecnica": "$1,450,000 USD", "solvencia_ii": "142%"},
        columnas=["id", "mes", "polizas_activas", "primas_cobradas", "siniestros_pagados"],
        filas=[
            {"id": 1, "mes": "Enero 2026", "polizas_activas": 120, "primas_cobradas": "$125,000", "siniestros_pagados": "$32,000"},
            {"id": 2, "mes": "Febrero 2026", "polizas_activas": 145, "primas_cobradas": "$152,000", "siniestros_pagados": "$41,000"},
            {"id": 3, "mes": "Marzo 2026", "polizas_activas": 160, "primas_cobradas": "$168,000", "siniestros_pagados": "$38,500"}
        ],
        formato="pdf",
        nombre_base="reporte_solvencia_s3"
    )
    print(f"  -> Reporte PDF S3 URL: {doc_pdf.download_url}")
    print(f"  -> S3 Key: {doc_pdf.s3_key}")
    print(f"  -> SHA-256: {doc_pdf.sha256_hash}")

    # 6. Listado de Objetos en S3
    print("\n[PASO 6] Consultando Inventario Activo en el Bucket AWS S3...")
    try:
        client = s3_storage_service._s3_client
        resp = client.list_objects_v2(Bucket=s3_storage_service.bucket)
        contents = resp.get("Contents", [])
        print(f"  Total Objetos en '{s3_storage_service.bucket}': {len(contents)}")
        for obj in contents[:20]:
            print(f"    - {obj['Key']} ({obj['Size']:,} bytes)")
        if len(contents) > 20:
            print(f"    ... y {len(contents) - 20} objetos más.")
    except Exception as e_ls:
        print(f"  Error listando bucket: {e_ls}")

    print("\n" + "=" * 80)
    print("✅ SINCRONIZACIÓN Y POBLACIÓN DE AMAZON S3 COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    return True


if __name__ == "__main__":
    ejecutar_sincronizacion_s3_perfil_c()
