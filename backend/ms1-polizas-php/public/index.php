<?php
declare(strict_types=1);

/**
 * =============================================================================
 *  AegisCore AI - MS1: Core ERP de Pólizas, Clientes y Facturación (PHP 8.3)
 *  Patrón de Arquitectura: Domain-Driven Design (DDD) Táctico y Estratégico
 *  Casos de Uso Soportados: CU01, CU02, CU03, CU04, CU05, CU09 (Saga), CU10
 * =============================================================================
 */

require_once dirname(__DIR__) . '/src/autoload.php';

use AegisCore\Polizas\Application\Services\ApolloFederationResolver;
use AegisCore\Polizas\Application\Services\AuthOIDCController;
use AegisCore\Polizas\Application\Services\CatalogoPolizaApplicationService;
use AegisCore\Polizas\Application\Services\EmisionPolizaGraphQLController;
use AegisCore\Polizas\Application\Services\FacturacionService;
use AegisCore\Polizas\Application\Services\PolizaCoberturaService;
use AegisCore\Polizas\Application\Services\RecepcionPedidoService;
use AegisCore\Polizas\Domain\Facturacion\Services\FacturacionDomainService;
use AegisCore\Polizas\Domain\Poliza\Services\CotizacionPolizaDomainService;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use AegisCore\Polizas\Infrastructure\Idempotency\DynamoDb\DynamoDbSessionCacheRepository;
use AegisCore\Polizas\Infrastructure\Messaging\Kafka\SagaKafkaConsumer;
use AegisCore\Polizas\Infrastructure\Pdf\FacturaPdfGenerator;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\PdoPostgresConnection;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories\PostgresClienteRepository;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories\PostgresFacturaRepository;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories\PostgresPlanSeguroRepository;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories\PostgresPolizaRepository;
use AegisCore\Polizas\Presentation\GraphQL\SupergraphGraphQLEngine;

// Configurar cabeceras CORS para React PWA (3000), Angular (4200), SSO Shell y n8n (5678)
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, Idempotency-Key, X-Idempotency-Key, X-Client-Id');
header('Access-Control-Expose-Headers: X-Cache-Lookup, X-Document-Hash-SHA256, X-Idempotency-Key');

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// Ensamblaje del Contenedor de Inyección de Dependencias DDD
$pgConnection = new PdoPostgresConnection();
$clienteRepo = new PostgresClienteRepository($pgConnection);
$planRepo = new PostgresPlanSeguroRepository($pgConnection);
$polizaRepo = new PostgresPolizaRepository($pgConnection);
$facturaRepo = new PostgresFacturaRepository($pgConnection);
$dynamoRepo = new DynamoDbSessionCacheRepository();
$pdfGenerator = new FacturaPdfGenerator();

$cotizadorDomainService = new CotizacionPolizaDomainService();
$facturacionDomainService = new FacturacionDomainService();

$authController = new AuthOIDCController($clienteRepo, $dynamoRepo);
$federationResolver = new ApolloFederationResolver($clienteRepo, $polizaRepo, $planRepo, $facturaRepo, $dynamoRepo);
$catalogoService = new CatalogoPolizaApplicationService($planRepo, $clienteRepo);
$emisionController = new EmisionPolizaGraphQLController(
    $planRepo,
    $clienteRepo,
    $polizaRepo,
    $facturaRepo,
    $cotizadorDomainService,
    $facturacionDomainService
);
$facturacionService = new FacturacionService(
    $polizaRepo,
    $clienteRepo,
    $facturaRepo,
    $facturacionDomainService,
    $pdfGenerator
);
$recepcionPedidoService = new RecepcionPedidoService($emisionController, $facturacionService);
$polizaCoberturaService = new PolizaCoberturaService($polizaRepo);
$sagaKafkaConsumer = new SagaKafkaConsumer($polizaCoberturaService);
$graphqlEngine = new SupergraphGraphQLEngine(
    $federationResolver,
    $catalogoService,
    $emisionController,
    $facturacionService,
    $polizaRepo,
    $clienteRepo,
    $planRepo,
    $facturaRepo
);

$uri = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';
$method = strtoupper($_SERVER['REQUEST_METHOD'] ?? 'GET');
$rawBody = file_get_contents('php://input') ?: '';
$jsonBody = json_decode($rawBody, true) ?? [];

$authHeader = $_SERVER['HTTP_AUTHORIZATION'] ?? null;
$idempotencyKey = $_SERVER['HTTP_IDEMPOTENCY_KEY'] ?? $_SERVER['HTTP_X_IDEMPOTENCY_KEY'] ?? null;

// ---------------------------------------------------------------------------
// 1. HEALTH CHECKS
// ---------------------------------------------------------------------------
if ($uri === '/health') {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode([
        'status' => 'UP',
        'service' => 'ms1-polizas-php',
        'pattern' => 'Domain-Driven Design (DDD)',
        'language' => 'PHP ' . PHP_VERSION,
        'use_cases' => ['CU01', 'CU02', 'CU03', 'CU04', 'CU05', 'CU09-Paso2-Saga'],
        'cloud_database' => 'Neon Serverless PostgreSQL + Amazon DynamoDB',
        'timestamp' => gmdate(DATE_ATOM),
    ]);
    exit;
}

if ($uri === '/health/db') {
    header('Content-Type: application/json; charset=utf-8');
    $pdo = $pgConnection->getPdo();
    if ($pdo !== null) {
        $version = $pdo->query('SELECT version()')->fetchColumn();
        echo json_encode([
            'status' => 'CONNECTED',
            'mode' => 'NEON_CLOUD_POSTGRESQL',
            'version' => substr((string)$version, 0, 60),
            'timestamp' => gmdate(DATE_ATOM),
        ]);
    } else {
        $state = $pgConnection->readState();
        echo json_encode([
            'status' => 'CONNECTED',
            'mode' => 'TRANSACTIONAL_SYNC_ENGINE',
            'clientes_count' => count($state['clientes']),
            'planes_count' => count($state['planes']),
            'polizas_count' => count($state['polizas']),
            'note' => $pgConnection->getLastError(),
            'timestamp' => gmdate(DATE_ATOM),
        ]);
    }
    exit;
}

// ---------------------------------------------------------------------------
// 2. CU01: KEYCLOAK SSO / OIDC + PKCE + DYNAMODB UNIFIED SESSION
// ---------------------------------------------------------------------------
if (($uri === '/api/v1/auth/oidc-token' || $uri === '/api/v1/auth/sso-session') && ($method === 'POST' || $method === 'GET')) {
    header('Content-Type: application/json; charset=utf-8');
    $params = $method === 'POST' ? $jsonBody : $_GET;
    $sessionResponse = $authController->autenticarUsuarioOIDC($params);
    echo json_encode($sessionResponse);
    exit;
}

if ($uri === '/api/v1/auth/sso-sessions' && $method === 'GET') {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode([
        'status' => 'OK',
        'sesiones' => $authController->listarSesionesSSOActivas(),
    ]);
    exit;
}

if ($uri === '/api/v1/auth/sso-logout' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    $sessionId = trim((string)($jsonBody['session_id'] ?? $jsonBody['sessionId'] ?? 'ALL'));
    echo json_encode($authController->cerrarSesionUnicaSSO($sessionId !== '' ? $sessionId : 'ALL'));
    exit;
}

// ---------------------------------------------------------------------------
// 3. CU02, CU03, CU04, CU05: SUPERGRAPH GRAPHQL ENDPOINT
// ---------------------------------------------------------------------------
if ($uri === '/graphql' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');

    // Validar contexto JWT RS256 de Keycloak SSO
    $jwtContext = $authController->validarTokenJwtRS256($authHeader);

    // Control de Idempotencia en mutaciones con cabecera Idempotency-Key
    $queryStr = (string)($jsonBody['query'] ?? '');
    $isMutation = str_contains($queryStr, 'mutation') || str_contains($queryStr, 'emitirPoliza');
    if ($isMutation && $idempotencyKey !== null && trim($idempotencyKey) !== '') {
        $cached = $dynamoRepo->verificarIdempotencyKey($idempotencyKey, $rawBody);
        if ($cached !== null) {
            if ($cached['conflict'] === 'PAYLOAD_MISMATCH') {
                http_response_code(422);
                echo json_encode([
                    'error' => 'IDEMPOTENCY_PAYLOAD_MISMATCH',
                    'message' => 'El cuerpo de la petición no coincide con el payload original registrado para este Idempotency-Key.',
                ]);
                exit;
            }
            header('X-Cache-Lookup: HIT_IDEMPOTENCY_DYNAMODB');
            http_response_code((int)$cached['http_status']);
            echo $cached['record']['response_body_cached'];
            exit;
        }
    }

    $variables = (array)($jsonBody['variables'] ?? []);
    $opName = isset($jsonBody['operationName']) ? (string)$jsonBody['operationName'] : null;

    $result = $graphqlEngine->execute($queryStr, $variables, $opName);
    $result['extensions'] = [
        'service' => 'ms1-polizas-php',
        'architecture' => 'DDD (Domain-Driven Design)',
        'sso_sub' => $jwtContext['sub'],
        'sso_role' => $jwtContext['rol'],
    ];

    if ($isMutation && $idempotencyKey !== null && trim($idempotencyKey) !== '' && !isset($result['errors'])) {
        $dynamoRepo->guardarRegistroIdempotencia($idempotencyKey, $rawBody, 200, $result);
        header('X-Cache-Lookup: MISS_STORED_DYNAMODB');
    }

    echo json_encode($result);
    exit;
}

// ---------------------------------------------------------------------------
// 4. CU05: FACTURACIÓN PDF AUTOMÁTICA Y FLUJO WHATSAPP N8N
// ---------------------------------------------------------------------------
if (($uri === '/api/facturas/generar-pdf' || $uri === '/api/v1/facturas/generar-pdf') && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    try {
        $polizaId = (string)($jsonBody['poliza_id'] ?? $jsonBody['polizaId'] ?? 'd0000001-0000-0000-0000-000000000001');
        $tipoComprobante = (string)($jsonBody['tipo_comprobante'] ?? $jsonBody['tipoComprobante'] ?? 'FACTURA');
        $res = $facturacionService->generarFacturaNotaVentaPDF($polizaId, $tipoComprobante);
        echo json_encode($res);
    } catch (DomainException $e) {
        http_response_code($e->getCode() ?: 422);
        echo json_encode(['error' => $e->getErrorCode(), 'message' => $e->getMessage()]);
    }
    exit;
}

if (preg_match('#^/api/v1/facturas/([^/]+)/pdf$#', $uri, $matches) && $method === 'GET') {
    $facturaId = urldecode($matches[1]);
    try {
        $pdfData = $facturacionService->obtenerBinarioPdfFactura($facturaId);
        header('Content-Type: application/pdf');
        header('Content-Disposition: inline; filename="' . $pdfData['filename'] . '"');
        header('X-Document-Hash-SHA256: ' . $pdfData['hash_sha256']);
        echo $pdfData['raw_pdf'];
    } catch (Throwable $e) {
        header('Content-Type: application/json; charset=utf-8');
        http_response_code(404);
        echo json_encode(['error' => 'INVOICE_PDF_NOT_FOUND', 'message' => $e->getMessage()]);
    }
    exit;
}

if (preg_match('#^/api/v1/polizas/([^/]+)/certificado-pdf$#', $uri, $mPolCert) && ($method === 'GET' || $method === 'POST')) {
    $polizaRef = urldecode($mPolCert[1]);
    $poliza = $polizaRepo->obtenerPorId($polizaRef) ?? $polizaRepo->obtenerPorNumero($polizaRef);
    if ($poliza === null) {
        header('Content-Type: application/json; charset=utf-8');
        http_response_code(404);
        echo json_encode(['error' => 'POLICY_NOT_FOUND', 'message' => 'No se encontró la póliza solicitada.']);
        exit;
    }
    $cliente = $clienteRepo->obtenerPorId($poliza->clienteId()->value());
    $plan = $planRepo->obtenerPorId($poliza->planId()->value());
    $certData = $pdfGenerator->compilarCertificadoPolizaPdf($poliza, $cliente, $plan ? $plan->toGraphQLArray() : null);

    if (isset($_GET['format']) && $_GET['format'] === 'json') {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode([
            'status' => 'OK',
            'numeroPoliza' => $poliza->numeroPoliza(),
            'filename' => $certData['filename'],
            'urlPdf' => $certData['url_pdf'],
            's3Url' => $certData['s3_url'],
            'localUrl' => $certData['local_url_pdf'],
            'hashSha256' => $certData['hash_sha256'],
        ]);
        exit;
    }

    header('Content-Type: application/pdf');
    header('Content-Disposition: inline; filename="' . $certData['filename'] . '"');
    header('X-Document-Hash-SHA256: ' . $certData['hash_sha256']);
    echo $certData['raw_pdf'];
    exit;
}

if ($uri === '/api/v1/s3/upload-documento' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    $base64Data = (string)($jsonBody['base64Data'] ?? '');
    $fileName = preg_replace('/[^A-Za-z0-9\-_\.]/', '_', (string)($jsonBody['fileName'] ?? ('RUAT-' . time() . '.png')));
    $folder = preg_replace('/[^A-Za-z0-9\-_]/', '', (string)($jsonBody['folder'] ?? 'documentos-ruat'));
    $contentType = (string)($jsonBody['contentType'] ?? 'image/png');

    if ($base64Data === '') {
        http_response_code(400);
        echo json_encode(['error' => 'EMPTY_DOCUMENT', 'message' => 'Debe enviar base64Data para subir a S3.']);
        exit;
    }

    if (str_contains($base64Data, ',')) {
        $parts = explode(',', $base64Data, 2);
        $base64Data = $parts[1];
    }
    $binary = base64_decode($base64Data, true);
    if ($binary === false) {
        http_response_code(400);
        echo json_encode(['error' => 'INVALID_BASE64', 'message' => 'El contenido base64 no es válido.']);
        exit;
    }

    $tmpDir = dirname(__DIR__) . '/public/facturas';
    if (!is_dir($tmpDir)) {
        @mkdir($tmpDir, 0775, true);
    }
    $localPath = $tmpDir . DIRECTORY_SEPARATOR . $fileName;
    @file_put_contents($localPath, $binary);
    $hashSha256 = hash('sha256', $binary);
    $s3Key = $folder . '/' . $fileName;
    $s3Url = $pdfGenerator->subirArchivoAS3($localPath, $s3Key, $contentType);

    echo json_encode([
        'uploaded' => $s3Url !== null,
        'bucket' => 'servicio-de-seguros-aegiscore',
        'key' => $s3Key,
        's3Url' => $s3Url ?: ('http://localhost:8001/facturas/' . $fileName),
        'hashSha256' => $hashSha256,
        'bytes' => strlen($binary),
        'timestamp' => gmdate(DATE_ATOM),
    ]);
    exit;
}

if ($uri === '/api/v1/whatsapp/pedido-poliza' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    try {
        $res = $recepcionPedidoService->procesarPedidoPolizaWhatsApp($jsonBody);
        http_response_code(201);
        echo json_encode($res);
    } catch (DomainException $e) {
        http_response_code($e->getCode() ?: 422);
        echo json_encode(['error' => $e->getErrorCode(), 'message' => $e->getMessage()]);
    }
    exit;
}

// ---------------------------------------------------------------------------
// CU03: GESTIÓN DE CATÁLOGO — ACTIVAR / DESACTIVAR PLAN DE SEGURO
// ---------------------------------------------------------------------------
if ($uri === '/api/v1/catalogo/toggle-plan' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    $planId = trim((string)($jsonBody['planId'] ?? $jsonBody['plan_id'] ?? ''));
    if ($planId === '') {
        http_response_code(400);
        echo json_encode([
            'status' => 'ERROR',
            'error' => 'MISSING_PLAN_ID',
            'message' => 'El campo planId es obligatorio para alternar el estado del plan.',
        ]);
        exit;
    }

    $updatedPlan = $pgConnection->alternarEstadoPlanEnBd($planId);
    if ($updatedPlan === null) {
        http_response_code(404);
        echo json_encode([
            'status' => 'ERROR',
            'error' => 'PLAN_NOT_FOUND',
            'message' => "No se encontró el plan con ID o código '{$planId}'.",
        ]);
        exit;
    }

    echo json_encode([
        'status' => 'OK',
        'plan' => $updatedPlan,
    ]);
    exit;
}

// ---------------------------------------------------------------------------
// 5. CU09 (APOYO SAGA MS1 PHP): DESCUENTO Y COMPENSACIÓN DE COBERTURA
// ---------------------------------------------------------------------------
if ($uri === '/api/v1/saga/descontar-cobertura' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    $jsonBody['event_type'] = 'DescontarCoberturaPolizaCommand';
    $eventResult = $sagaKafkaConsumer->handleKafkaMessage($jsonBody);
    $statusCode = ($eventResult['event_type'] ?? '') === 'DescuentoCoberturaFallidoEvent' ? 422 : 200;
    http_response_code($statusCode);
    echo json_encode($eventResult);
    exit;
}

if ($uri === '/api/v1/saga/compensar-cobertura' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    $jsonBody['event_type'] = 'CompensarCoberturaCommand';
    $eventResult = $sagaKafkaConsumer->handleKafkaMessage($jsonBody);
    echo json_encode($eventResult);
    exit;
}

// ---------------------------------------------------------------------------
// 6. CU10 (SOPORTE PASARELA REACT): COBRO PRIMA QR CON SANDBOX SIP & POSTGRESQL
// ---------------------------------------------------------------------------
if ($uri === '/api/v1/pagos-qr' && $method === 'GET') {
    header('Content-Type: application/json; charset=utf-8');
    $polizaId = isset($_GET['poliza_id']) ? (string)$_GET['poliza_id'] : null;
    echo json_encode([
        'status' => 'OK',
        'pagos' => $pgConnection->listarPagosQrDeBd($polizaId),
    ]);
    exit;
}

if ($uri === '/api/v1/pagos-qr' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    $idemKey = $idempotencyKey ?? (string)($jsonBody['idempotencyKey'] ?? '');
    if ($idemKey === '') {
        http_response_code(400);
        echo json_encode(['error' => 'MISSING_IDEMPOTENCY_KEY', 'message' => 'La cabecera Idempotency-Key (UUIDv4) es obligatoria.']);
        exit;
    }

    $cached = $dynamoRepo->verificarIdempotencyKey($idemKey, $rawBody);
    if ($cached !== null) {
        if ($cached['conflict'] === 'PAYLOAD_MISMATCH') {
            http_response_code(422);
            echo json_encode([
                'error' => 'IDEMPOTENCY_PAYLOAD_MISMATCH',
                'message' => 'El cuerpo de la petición no coincide con el payload original registrado para este Idempotency-Key.',
            ]);
            exit;
        }
        header('X-Cache-Lookup: HIT_IDEMPOTENCY_DYNAMODB');
        http_response_code(200);
        $cachedBody = json_decode((string)$cached['record']['response_body_cached'], true) ?? [];
        $cachedBody['fueIdempotente'] = true;
        $cachedBody['cacheHit'] = 'HIT_IDEMPOTENCY_DYNAMODB (<5ms)';
        echo json_encode($cachedBody);
        exit;
    }

    $polizaId = (string)($jsonBody['polizaId'] ?? 'd0000001-0000-0000-0000-000000000001');
    $facturaId = isset($jsonBody['facturaId']) && $jsonBody['facturaId'] !== '' ? (string)$jsonBody['facturaId'] : null;
    $numeroCuota = (int)($jsonBody['numeroCuota'] ?? 1);
    $monto = (float)($jsonBody['monto'] ?? 60.00);
    $bancoSandbox = (string)($jsonBody['bancoSandbox'] ?? 'Banco Nacional / SIP QR Simple (Sandbox)');
    $pagoId = \AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId::generate()->value();
    $codigoAuth = 'SIP-QR-' . strtoupper(substr(md5($idemKey), 0, 8));

    $responsePayload = [
        'id' => $pagoId,
        'polizaId' => $polizaId,
        'facturaId' => $facturaId,
        'numeroCuota' => $numeroCuota,
        'monto' => round($monto, 2),
        'moneda' => 'USD',
        'idempotencyKey' => $idemKey,
        'qrImagenPayload' => sprintf('00020101021226580014BO.SIP.QRSIMPLE0112%s5204630053038405406%.2f5802BO5916AEGISCORE SEGUROS6010SANTA CRUZ6304%s', substr($idemKey, 0, 12), $monto, substr($codigoAuth, -4)),
        'estado' => 'EXITOSO',
        'codigoAutorizacion' => $codigoAuth,
        'bancoSandbox' => $bancoSandbox,
        'sandboxVoucherUrl' => 'http://localhost:8001/sandbox/qr-checkout/' . $pagoId,
        'fechaPago' => gmdate(DATE_ATOM),
        'fueIdempotente' => false,
        'cacheHit' => 'MISS_FIRST_EXECUTION',
    ];

    $pgConnection->registrarPagoQrEnBd($responsePayload, $facturaId);
    $dynamoRepo->guardarRegistroIdempotencia($idemKey, $rawBody, 201, $responsePayload, 'REACT_PWA');
    header('X-Cache-Lookup: MISS_STORED_DYNAMODB');
    http_response_code(201);
    echo json_encode($responsePayload);
    exit;
}

if (preg_match('#^/sandbox/qr-checkout/([^/]+)$#', $uri, $mCheckout) && $method === 'GET') {
    $checkoutId = urldecode($mCheckout[1]);
    $pagos = $pgConnection->listarPagosQrDeBd();
    $found = null;
    foreach ($pagos as $p) {
        if ($p['id'] === $checkoutId || $p['codigoAutorizacion'] === $checkoutId) {
            $found = $p;
            break;
        }
    }
    if ($found === null) {
        $found = [
            'id' => $checkoutId,
            'polizaId' => 'POL-2026-AUT-00892',
            'numeroCuota' => 1,
            'monto' => 60.00,
            'moneda' => 'USD',
            'idempotencyKey' => $checkoutId,
            'codigoAutorizacion' => 'SIP-QR-' . strtoupper(substr(md5($checkoutId), 0, 8)),
            'bancoSandbox' => 'Banco Nacional / SIP QR Simple (Sandbox)',
            'estado' => 'EXITOSO',
            'fechaPago' => gmdate(DATE_ATOM),
        ];
    }

    header('Content-Type: text/html; charset=utf-8');
    echo '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"/><title>Comprobante Bancario QR Sandbox — ' . htmlspecialchars($found['codigoAutorizacion']) . '</title>';
    echo '<script src="https://cdn.tailwindcss.com"></script></head>';
    echo '<body class="bg-slate-900 text-slate-100 min-h-screen flex items-center justify-center p-6 font-sans">';
    echo '<div class="max-w-md w-full bg-white text-slate-900 rounded-2xl shadow-2xl overflow-hidden border border-slate-200">';
    echo '<div class="bg-[#005C55] text-white p-6 text-center space-y-1">';
    echo '<span class="px-3 py-0.5 rounded-full bg-white/20 text-[11px] font-mono uppercase">Sandbox SIP / QR Simple Bolivia</span>';
    echo '<h1 class="text-xl font-bold pt-1">Comprobante de Pago Electrónico</h1>';
    echo '<p class="text-xs text-teal-100">Transacción Liquidada en Tiempo Real</p>';
    echo '</div>';
    echo '<div class="p-6 space-y-4 text-xs">';
    echo '<div class="text-center pb-4 border-b border-slate-100">';
    echo '<span class="text-slate-400 uppercase tracking-wider text-[10px] block">Monto Debitado</span>';
    echo '<span class="text-3xl font-extrabold font-mono text-[#005C55]">USD ' . number_format((float)$found['monto'], 2) . '</span>';
    echo '</div>';
    echo '<div class="space-y-2.5">';
    echo '<div class="flex justify-between"><span class="text-slate-500">Código Autorización:</span><strong class="font-mono">' . htmlspecialchars($found['codigoAutorizacion']) . '</strong></div>';
    echo '<div class="flex justify-between"><span class="text-slate-500">Entidad Financiera:</span><strong>' . htmlspecialchars($found['bancoSandbox']) . '</strong></div>';
    echo '<div class="flex justify-between"><span class="text-slate-500">Póliza / Referencia:</span><strong class="font-mono">' . htmlspecialchars($found['polizaId']) . ' (Cuota #' . (int)$found['numeroCuota'] . ')</strong></div>';
    echo '<div class="flex justify-between"><span class="text-slate-500">Llave Idempotencia:</span><span class="font-mono text-[11px]">' . htmlspecialchars($found['idempotencyKey']) . '</span></div>';
    echo '<div class="flex justify-between"><span class="text-slate-500">Fecha y Hora UTC:</span><span class="font-mono">' . htmlspecialchars($found['fechaPago']) . '</span></div>';
    echo '<div class="flex justify-between"><span class="text-slate-500">Estado:</span><span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">' . htmlspecialchars($found['estado']) . '</span></div>';
    echo '</div>';
    echo '<div class="pt-4 border-t border-slate-100 flex gap-2">';
    echo '<button onclick="window.print()" class="flex-1 py-2.5 rounded-xl bg-slate-900 text-white font-semibold hover:bg-slate-800">Imprimir Comprobante</button>';
    echo '<button onclick="window.close()" class="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-semibold hover:bg-slate-50">Cerrar</button>';
    echo '</div>';
    echo '</div></div></body></html>';
    exit;
}

header('Content-Type: application/json; charset=utf-8');
echo json_encode([
    'service' => 'ms1-polizas-php',
    'status' => 'OPERATIONAL',
    'pattern' => 'Domain-Driven Design (DDD)',
    'endpoints' => [
        'GET /health' => 'Health check del microservicio',
        'GET /health/db' => 'Estado de conexión a PostgreSQL / Neon Cloud',
        'POST /api/v1/auth/oidc-token' => 'CU01: Login Único SSO OIDC + PKCE + DynamoDB Session',
        'POST /graphql' => 'CU02, CU03, CU04, CU05: Subgrafo GraphQL Federado',
        'POST /api/facturas/generar-pdf' => 'CU05: Generador de Factura / Nota de Venta en PDF con SHA-256',
        'GET /api/v1/facturas/{id}/pdf' => 'CU05: Descarga directa de Factura en PDF',
        'POST /api/v1/whatsapp/pedido-poliza' => 'CU05: Webhook n8n WhatsApp -> ERP -> Factura PDF',
        'POST /api/v1/catalogo/toggle-plan' => 'CU03: Alternar estado activo/inactivo de un plan de seguro',
        'POST /api/v1/saga/descontar-cobertura' => 'CU09 Paso 2: Descontar techo anual de cobertura en Saga',
        'POST /api/v1/saga/compensar-cobertura' => 'CU09 Rollback: Restituir cobertura en compensación Saga',
        'POST /api/v1/pagos-qr' => 'CU10: Cobro de prima QR con Idempotency-Key en DynamoDB',
    ],
]);
