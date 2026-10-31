"""
=============================================================================
 AegisCore AI - MS4: [CONTROL/SERVICE] Servicio de Almacenamiento Amazon S3
 Encapsula operaciones con boto3 para evidencias multimedia, reportes ejecutivos
 y audios periciales, organizados bajo la taxonomía jerárquica de dominio:
 Cliente -> Vehículo -> Incidente / Siniestro
=============================================================================
"""

import io
import re
import datetime
from typing import Optional, Dict, Any, Tuple
from app.core.config import settings

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError, BotoCoreError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


class S3StorageService:
    """
    Servicio de Almacenamiento de Objetos en la Nube con Amazon AWS S3.
    Maneja persistencia de evidencias, generación de URLs presignadas y
    soporta fallback ordenado si las credenciales no están configuradas.
    """

    def __init__(self):
        self.bucket = settings.S3_BUCKET_NAME
        self.region = settings.AWS_S3_REGION
        self.access_key = settings.AWS_S3_ACCESS_KEY_ID
        self.secret_key = settings.AWS_S3_SECRET_ACCESS_KEY
        self.expiracion_default = settings.S3_PRESIGNED_EXPIRATION_SECONDS
        self._s3_client = None

        if HAS_BOTO3 and self.access_key and self.secret_key:
            try:
                self._s3_client = boto3.client(
                    "s3",
                    region_name=self.region,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    config=Config(signature_version="s3v4")
                )
            except Exception as e:
                print(f"[S3StorageService] Advertencia al instanciar cliente S3: {e}")
                self._s3_client = None

    @property
    def is_configured(self) -> bool:
        """Retorna True si el cliente boto3 está configurado y listo."""
        return self._s3_client is not None

    # -----------------------------------------------------------------------
    # Método Auxiliar: Sanitizar segmentos de ruta para S3
    # -----------------------------------------------------------------------
    @staticmethod
    def _sanitizar_segmento(segmento: Optional[str], fallback: str = "DESCONOCIDO") -> str:
        if not segmento or not str(segmento).strip():
            return fallback
        # Reemplazar espacios y caracteres no alfanuméricos simples
        limpio = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', str(segmento).strip())
        return limpio or fallback

    # -----------------------------------------------------------------------
    # Operación UML: construir_s3_key_incidente()
    # -----------------------------------------------------------------------
    def construir_s3_key_incidente(
        self,
        cliente_id: str,
        vehiculo_id: str,
        reclamo_id: str,
        categoria: str,
        nombre_archivo: str
    ) -> str:
        """
        Construye la clave jerárquica de S3:
        clientes/{cliente_id}/vehiculos/{vehiculo_id}/incidentes/{reclamo_id}/{categoria}/{nombre_archivo}
        """
        cli = self._sanitizar_segmento(cliente_id, "CLI-GENERAL")
        veh = self._sanitizar_segmento(vehiculo_id, "VEH-GENERAL")
        rec = self._sanitizar_segmento(reclamo_id, "REC-GENERAL")
        cat = self._sanitizar_segmento(categoria, "evidencias")
        arch = self._sanitizar_segmento(nombre_archivo, f"archivo_{int(datetime.datetime.now().timestamp())}.dat")
        return f"clientes/{cli}/vehiculos/{veh}/incidentes/{rec}/{cat}/{arch}"

    # -----------------------------------------------------------------------
    # Operación UML: construir_s3_key_global()
    # -----------------------------------------------------------------------
    def construir_s3_key_global(
        self,
        categoria: str,
        nombre_archivo: str
    ) -> str:
        """
        Construye claves para reportes gerenciales no asociados a un único reclamo:
        reportes-globales/{año}/{mes}/{nombre_archivo}
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        cat = self._sanitizar_segmento(categoria, "reportes-globales")
        arch = self._sanitizar_segmento(nombre_archivo, f"reporte_{int(now.timestamp())}.dat")
        return f"{cat}/{now.year}/{now.month:02d}/{arch}"

    # -----------------------------------------------------------------------
    # Operación UML: obtener_url_publica()
    # -----------------------------------------------------------------------
    def obtener_url_publica(self, s3_key: str) -> str:
        """Retorna la URL estándar de acceso en AWS S3 para el objeto."""
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"

    # -----------------------------------------------------------------------
    # Operación UML: subir_bytes()
    # -----------------------------------------------------------------------
    def subir_bytes(
        self,
        datos_bytes: bytes,
        s3_key: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Sube un array de bytes directamente a S3 y retorna su URL final.
        """
        if not self.is_configured:
            return None

        try:
            extra_args = {"ContentType": content_type}
            if metadata:
                extra_args["Metadata"] = metadata

            self._s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=datos_bytes,
                **extra_args
            )
            return self.obtener_url_publica(s3_key)
        except Exception as e:
            print(f"[S3StorageService] Error al subir bytes a S3 ({s3_key}): {e}")
            return None

    # -----------------------------------------------------------------------
    # Operación UML: subir_buffer()
    # -----------------------------------------------------------------------
    def subir_buffer(
        self,
        buffer: io.BytesIO,
        s3_key: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Sube el contenido de un buffer en memoria hacia S3.
        """
        if not self.is_configured:
            return None

        try:
            buffer.seek(0)
            extra_args = {"ContentType": content_type}
            if metadata:
                extra_args["Metadata"] = metadata

            self._s3_client.upload_fileobj(
                buffer,
                self.bucket,
                s3_key,
                ExtraArgs=extra_args
            )
            return self.obtener_url_publica(s3_key)
        except Exception as e:
            print(f"[S3StorageService] Error al subir buffer a S3 ({s3_key}): {e}")
            return None

    # -----------------------------------------------------------------------
    # Operación UML: generar_presigned_download_url()
    # -----------------------------------------------------------------------
    def generar_presigned_download_url(
        self,
        s3_key: str,
        expiracion_segundos: Optional[int] = None
    ) -> Optional[str]:
        """
        Genera una URL presignada con expiración temporal (default 900s / 15m)
        para permitir descarga segura desde navegadores o apps móviles.
        """
        if not self.is_configured:
            return None

        ttl = expiracion_segundos or self.expiracion_default
        try:
            url = self._s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket, "Key": s3_key},
                ExpiresIn=ttl
            )
            return url
        except Exception as e:
            print(f"[S3StorageService] Error al generar Pre-signed URL para {s3_key}: {e}")
            return None

    # -----------------------------------------------------------------------
    # Operación UML: verificar_conexion_bucket()
    # -----------------------------------------------------------------------
    def verificar_conexion_bucket(self) -> Tuple[bool, str]:
        """
        Comprueba si el cliente tiene acceso al bucket configurado.
        """
        if not self.is_configured:
            return False, "S3 no configurado (faltan credenciales o librería boto3)"

        try:
            self._s3_client.head_bucket(Bucket=self.bucket)
            return True, f"Conexión exitosa a bucket '{self.bucket}' en '{self.region}'"
        except ClientError as e:
            code = e.response.get('Error', {}).get('Code', 'Unknown')
            msg = e.response.get('Error', {}).get('Message', str(e))
            return False, f"Error S3 [{code}]: {msg}"
        except Exception as e:
            return False, f"Excepción general: {str(e)}"


# Instancia Singleton compartida
s3_storage_service = S3StorageService()

