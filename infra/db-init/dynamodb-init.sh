#!/usr/bin/env bash
# =============================================================================
#  AEGISCORE AI - Script de Inicialización de Amazon DynamoDB Local
#  Crea las tablas 'IdempotencyRecords' y 'SesionesSSO' en el contenedor local.
# =============================================================================
set -euo pipefail

ENDPOINT_URL="${DYNAMODB_ENDPOINT:-http://localhost:8000}"
AWS_REGION="${AWS_REGION:-us-east-1}"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-local}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-local}"

echo "============================================================================="
echo " AegisCore AI :: Inicializando DynamoDB Local en $ENDPOINT_URL"
echo "============================================================================="

# Esperar a que DynamoDB Local responda
echo "[*] Esperando a que DynamoDB Local este listo..."
until aws dynamodb list-tables --endpoint-url "$ENDPOINT_URL" --region "$AWS_REGION" > /dev/null 2>&1; do
  sleep 1
done
echo "[OK] DynamoDB Local respondiendo."

# 1. Tabla IdempotencyRecords (CU08, CU10)
if aws dynamodb describe-table --table-name IdempotencyRecords --endpoint-url "$ENDPOINT_URL" --region "$AWS_REGION" > /dev/null 2>&1; then
  echo "[-] Tabla 'IdempotencyRecords' ya existe."
else
  echo "[+] Creando tabla 'IdempotencyRecords'..."
  aws dynamodb create-table \
    --table-name IdempotencyRecords \
    --attribute-definitions \
      AttributeName=idempotency_key,AttributeType=S \
    --key-schema \
      AttributeName=idempotency_key,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url "$ENDPOINT_URL" \
    --region "$AWS_REGION"
  
  echo "[+] Habilitando TTL en 'IdempotencyRecords' (atributo 'ttl')..."
  aws dynamodb update-time-to-live \
    --table-name IdempotencyRecords \
    --time-to-live-specification "Enabled=true, AttributeName=ttl" \
    --endpoint-url "$ENDPOINT_URL" \
    --region "$AWS_REGION"
  echo "[OK] Tabla 'IdempotencyRecords' creada exitosamente."
fi

# 2. Tabla SesionesSSO (CU01)
if aws dynamodb describe-table --table-name SesionesSSO --endpoint-url "$ENDPOINT_URL" --region "$AWS_REGION" > /dev/null 2>&1; then
  echo "[-] Tabla 'SesionesSSO' ya existe."
else
  echo "[+] Creando tabla 'SesionesSSO'..."
  aws dynamodb create-table \
    --table-name SesionesSSO \
    --attribute-definitions \
      AttributeName=session_id,AttributeType=S \
    --key-schema \
      AttributeName=session_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url "$ENDPOINT_URL" \
    --region "$AWS_REGION"

  aws dynamodb update-time-to-live \
    --table-name SesionesSSO \
    --time-to-live-specification "Enabled=true, AttributeName=expires_at" \
    --endpoint-url "$ENDPOINT_URL" \
    --region "$AWS_REGION"
  echo "[OK] Tabla 'SesionesSSO' creada exitosamente."
fi

# Insertar un registro de prueba de Idempotencia
echo "[+] Insertando registro de prueba en IdempotencyRecords..."
aws dynamodb put-item \
  --table-name IdempotencyRecords \
  --item '{
    "idempotency_key": {"S": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"},
    "payload_hash": {"S": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
    "status": {"S": "COMPLETED"},
    "response_code": {"N": "201"},
    "response_body": {"S": "{\"numero_reclamo\":\"REC-2026-00492\",\"status\":\"CREATED\"}"},
    "client_id": {"S": "FLUTTER_PERITO_MOBILE_01"},
    "created_at": {"S": "2026-10-22T18:00:00Z"},
    "ttl": {"N": "1792713600"}
  }' \
  --endpoint-url "$ENDPOINT_URL" \
  --region "$AWS_REGION"

echo "============================================================================="
echo "[OK] Tablas de DynamoDB Local verificadas:"
aws dynamodb list-tables --endpoint-url "$ENDPOINT_URL" --region "$AWS_REGION"
echo "============================================================================="
