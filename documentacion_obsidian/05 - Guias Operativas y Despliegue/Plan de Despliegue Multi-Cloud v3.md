# 🌐 Plan de Despliegue Multi-Cloud v3 (Arquitectura Escalable)

> **Nota de Seguridad:** Los comandos completos con las credenciales reales de Neon PostgreSQL, MongoDB Atlas y AWS (`us-east-2`) se encuentran en [`docs/PLAN_DESPLIEGUE_MULTICLOUD_V3.md`](file:///d:/Proyectos/2doParcialSW2/docs/PLAN_DESPLIEGUE_MULTICLOUD_V3.md), archivo protegido en [`.gitignore`](file:///d:/Proyectos/2doParcialSW2/.gitignore#L16) para nunca exponer secretos en el repositorio.

## Resumen de Correcciones Arquitectónicas en v3
1. **Persistencia Cloud Real Intacta:** Conexión directa de los contenedores en GCP, AWS y Azure hacia **Neon Serverless PostgreSQL (`us-east-2`)**, **MongoDB Atlas (`cluster0.t4wz787`)** y **AWS DynamoDB + Amazon S3 (`servicio-de-seguros-aegiscore` en `us-east-2`)**.
2. **Túnel TCP para Kafka Local (`:9092`):** Uso de `ngrok tcp 9092` actualizando `KAFKA_ADVERTISED_LISTENERS` + fallback HTTP REST (`MS1_URL`, `MS2_URL`) en `MS3` para la Saga `CU09`.
3. **Acceso de `MF1 Angular` a `MS4 Python`:** Reemplazo de `--no-allow-unauthenticated` por `--allow-unauthenticated` en Cloud Run para evitar bloqueos `403` del proxy IAM de GCP.
4. **Escalabilidad Horizontal en `MS1 PHP`:** Configuración de `--concurrency 4` y `--min-instances 1` en Cloud Run junto con las variables de entorno de Amazon S3.

