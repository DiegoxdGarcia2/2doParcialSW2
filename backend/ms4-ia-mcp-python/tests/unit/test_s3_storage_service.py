"""
=============================================================================
 AegisCore AI - MS4: Pruebas Unitarias de Amazon S3 y Taxonomía Jerárquica
 Valida:
   1. Construcción de claves jerárquicas: Cliente -> Vehículo -> Incidente
   2. Construcción de claves globales para reportes gerenciales
   3. Sanitización de caracteres para compatibilidad S3
   4. Resolución de jerarquía en PostgreSQL/MongoDB
   5. Estrategia de descarga dual (Local + S3 Pre-signed URL)
=============================================================================
"""

import io
from unittest.mock import MagicMock, patch
import pytest

from app.services.s3_storage_service import S3StorageService
from app.controls.crashnet_vision_control import crashnet_vision_control
from app.controls.voice_mcp_control import VoiceMcpControl


@pytest.fixture
def s3_service():
    """Instancia del servicio S3 para pruebas."""
    return S3StorageService()


def test_construir_s3_key_incidente_estandar(s3_service):
    """Verifica la taxonomía jerárquica: clientes/{cli}/vehiculos/{veh}/incidentes/{rec}/{cat}/{arch}"""
    key = s3_service.construir_s3_key_incidente(
        cliente_id="10293847",
        vehiculo_id="4028-PLK",
        reclamo_id="REC-2026-00492",
        categoria="evidencias",
        nombre_archivo="foto_frontal.jpg"
    )
    assert key == "clientes/10293847/vehiculos/4028-PLK/incidentes/REC-2026-00492/evidencias/foto_frontal.jpg"


def test_construir_s3_key_incidente_sanitizacion(s3_service):
    """Verifica que espacios y caracteres no permitidos sean sanitizados correctamente."""
    key = s3_service.construir_s3_key_incidente(
        cliente_id="CLI 9832/A",
        vehiculo_id="PLACA 123#XYZ",
        reclamo_id="REC 2026 001",
        categoria="peritaje ia",
        nombre_archivo="foto anotada #1.jpg"
    )
    assert " " not in key
    assert "#" not in key
    assert "/" in key  # Solo como separador de carpetas


def test_construir_s3_key_global(s3_service):
    """Verifica la generación de rutas para reportes globales/gerenciales."""
    key = s3_service.construir_s3_key_global(
        categoria="reportes-globales",
        nombre_archivo="reporte_solvencia.pdf"
    )
    assert key.startswith("reportes-globales/")
    assert key.endswith("/reporte_solvencia.pdf")


def test_obtener_url_publica(s3_service):
    """Verifica el formato canónico de URL en AWS S3."""
    key = "clientes/10293847/vehiculos/4028-PLK/incidentes/REC-2026-00492/evidencias/foto.jpg"
    url = s3_service.obtener_url_publica(key)
    assert f"https://{s3_service.bucket}.s3.{s3_service.region}.amazonaws.com/{key}" == url


def test_resolver_jerarquia_cliente_vehiculo_fallback():
    """Verifica que entradas vacías o inexistentes devuelvan el fallback ordenado."""
    cli, veh = crashnet_vision_control.resolver_jerarquia_cliente_vehiculo(
        numero_poliza="POL-INEXISTENTE-9999",
        numero_reclamo="REC-INEXISTENTE-9999"
    )
    assert cli == "CLI-GENERAL"
    assert veh == "VEH-GENERAL"


def test_resolver_jerarquia_cliente_vehiculo_real():
    """Verifica la resolución real en PostgreSQL para la póliza demo oficial."""
    cli, veh = crashnet_vision_control.resolver_jerarquia_cliente_vehiculo(
        numero_poliza="POL-2026-AUT-00892"
    )
    # En el dataset real de la BD, la póliza pertenece a un cliente y tiene placa 4028-PLK
    assert veh == "4028-PLK"
    assert cli != "" and cli != "CLI-GENERAL"


def test_s3_subida_mockeada_y_presigned(s3_service):
    """Verifica que el servicio llame a put_object y generate_presigned_url."""
    mock_boto = MagicMock()
    mock_boto.generate_presigned_url.return_value = "https://s3.amazonaws.com/test-presigned"
    s3_service._s3_client = mock_boto

    data = b"FAKE_IMAGE_DATA_BYTES"
    key = "clientes/test/vehiculos/test/incidentes/test/evidencias/foto.jpg"

    url = s3_service.subir_bytes(data, key, content_type="image/jpeg")
    assert url is not None
    mock_boto.put_object.assert_called_once()

    presigned = s3_service.generar_presigned_download_url(key)
    assert presigned == "https://s3.amazonaws.com/test-presigned"
    mock_boto.generate_presigned_url.assert_called_once_with(
        ClientMethod="get_object",
        Params={"Bucket": s3_service.bucket, "Key": key},
        ExpiresIn=s3_service.expiracion_default
    )


def test_descarga_dual_voice_mcp():
    """Verifica que la generación de reportes configure la URL local y la URL de S3."""
    mcp_control = VoiceMcpControl()
    
    # Generar reporte simulado
    doc = mcp_control.exportarReporteDocumento(
        titulo="Reporte de Prueba Dual",
        kpis={"ratio": "15%"},
        columnas=["id", "concepto", "monto"],
        filas=[{"id": 1, "concepto": "Prueba", "monto": 100}],
        formato="pdf",
        nombre_base="test_dual"
    )
    
    assert doc is not None
    assert doc.local_download_url.startswith("/api/v1/mcp/download-report/")
    assert doc.filename in doc.local_download_url
    assert doc.download_url is not None

