<#
.SYNOPSIS
    Inicializa las tablas de Amazon DynamoDB Local para AegisCore AI en Windows.
#>
[CmdletBinding()]
param(
    [string]$EndpointUrl = "http://localhost:8000",
    [string]$Region = "us-east-1"
)

$env:AWS_ACCESS_KEY_ID = "local"
$env:AWS_SECRET_ACCESS_KEY = "local"

Write-Host "=============================================================================" -ForegroundColor Cyan
Write-Host " AegisCore AI :: Inicializando DynamoDB Local en $EndpointUrl" -ForegroundColor Cyan
Write-Host "=============================================================================" -ForegroundColor Cyan

# 1. Tabla IdempotencyRecords
Write-Host "[*] Verificando tabla 'IdempotencyRecords'..." -ForegroundColor Yellow
$tables = aws dynamodb list-tables --endpoint-url $EndpointUrl --region $Region 2>$null | ConvertFrom-Json

if ($tables.TableNames -contains "IdempotencyRecords") {
    Write-Host "[-] Tabla 'IdempotencyRecords' ya existe." -ForegroundColor Gray
} else {
    Write-Host "[+] Creando tabla 'IdempotencyRecords'..." -ForegroundColor Green
    aws dynamodb create-table `
        --table-name IdempotencyRecords `
        --attribute-definitions AttributeName=idempotency_key,AttributeType=S `
        --key-schema AttributeName=idempotency_key,KeyType=HASH `
        --billing-mode PAY_PER_REQUEST `
        --endpoint-url $EndpointUrl `
        --region $Region | Out-Null

    aws dynamodb update-time-to-live `
        --table-name IdempotencyRecords `
        --time-to-live-specification "Enabled=true, AttributeName=ttl" `
        --endpoint-url $EndpointUrl `
        --region $Region | Out-Null
    Write-Host "[OK] Tabla 'IdempotencyRecords' creada exitosamente." -ForegroundColor Green
}

# 2. Tabla SesionesSSO
Write-Host "[*] Verificando tabla 'SesionesSSO'..." -ForegroundColor Yellow
if ($tables.TableNames -contains "SesionesSSO") {
    Write-Host "[-] Tabla 'SesionesSSO' ya existe." -ForegroundColor Gray
} else {
    Write-Host "[+] Creando tabla 'SesionesSSO'..." -ForegroundColor Green
    aws dynamodb create-table `
        --table-name SesionesSSO `
        --attribute-definitions AttributeName=session_id,AttributeType=S `
        --key-schema AttributeName=session_id,KeyType=HASH `
        --billing-mode PAY_PER_REQUEST `
        --endpoint-url $EndpointUrl `
        --region $Region | Out-Null

    aws dynamodb update-time-to-live `
        --table-name SesionesSSO `
        --time-to-live-specification "Enabled=true, AttributeName=expires_at" `
        --endpoint-url $EndpointUrl `
        --region $Region | Out-Null
    Write-Host "[OK] Tabla 'SesionesSSO' creada exitosamente." -ForegroundColor Green
}

Write-Host "=============================================================================" -ForegroundColor Cyan
Write-Host "[OK] Tablas de DynamoDB Local activas:" -ForegroundColor Green
aws dynamodb list-tables --endpoint-url $EndpointUrl --region $Region
Write-Host "=============================================================================" -ForegroundColor Cyan
