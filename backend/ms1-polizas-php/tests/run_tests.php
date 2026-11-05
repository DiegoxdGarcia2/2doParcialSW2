<?php
declare(strict_types=1);

/**
 * =============================================================================
 *  AegisCore AI — Suite de Pruebas Automatizadas MS1 (PHP 8.3 / DDD + GraphQL)
 *  Cubre:
 *    - Value Objects DDD (PrimaMonetaria, VigenciaPoliza, BienAseguradoVehiculo)
 *    - Aggregate Root Poliza (Emisión, Descuento Cobertura Saga CU09 y Rollback)
 *    - CU01: AuthOIDCController (Login SSO OIDC + PKCE S256 + JWT RS256 + DynamoDB)
 *    - CU02: ApolloFederationResolver (Resumen Unificado GraphQL PostgreSQL+Mongo+Dynamo)
 *    - CU03: CatalogoPolizaApplicationService (Planes, Coberturas con FK y Clientes)
 *    - CU04: EmisionPolizaGraphQLController (Cotización, Validación IA Local y Emisión)
 *    - CU05: RecepcionPedidoService & FacturacionService (WhatsApp n8n -> PDF SHA-256)
 *    - CU09: SagaKafkaConsumer (DescontarCoberturaPolizaCommand y CompensarCoberturaCommand)
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
use AegisCore\Polizas\Domain\Poliza\Entities\Poliza;
use AegisCore\Polizas\Domain\Poliza\Services\CotizacionPolizaDomainService;
use AegisCore\Polizas\Domain\Poliza\ValueObjects\BienAseguradoVehiculo;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use AegisCore\Polizas\Domain\Shared\ValueObjects\PrimaMonetaria;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;
use AegisCore\Polizas\Domain\Shared\ValueObjects\VigenciaPoliza;
use AegisCore\Polizas\Infrastructure\Idempotency\DynamoDb\DynamoDbSessionCacheRepository;
use AegisCore\Polizas\Infrastructure\Messaging\Kafka\SagaKafkaConsumer;
use AegisCore\Polizas\Infrastructure\Pdf\FacturaPdfGenerator;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\PdoPostgresConnection;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories\PostgresClienteRepository;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories\PostgresFacturaRepository;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories\PostgresPlanSeguroRepository;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories\PostgresPolizaRepository;
use AegisCore\Polizas\Presentation\GraphQL\SupergraphGraphQLEngine;

$passed = 0;
$failed = 0;

function assertCase(string $name, callable $fn): void
{
    global $passed, $failed;
    try {
        $fn();
        echo "  [PASS] {$name}\n";
        $passed++;
    } catch (Throwable $e) {
        echo "  [FAIL] {$name} -> {$e->getMessage()}\n";
        $failed++;
    }
}

function assertTrue(bool $cond, string $msg = 'Assertion failed'): void
{
    if (!$cond) {
        throw new RuntimeException($msg);
    }
}

echo "=============================================================================\n";
echo " AEGISCORE AI - MS1 PHP 8.3 DDD & GRAPHQL TEST SUITE (PERFIL A: CU01-CU05)\n";
echo "=============================================================================\n";

$testStateFile = sys_get_temp_dir() . '/aegiscore_ms1_test_state_' . getmypid() . '.json';
$testDynamoFile = sys_get_temp_dir() . '/aegiscore_ms1_test_dynamo_' . getmypid() . '.json';

$pgConn = new PdoPostgresConnection($testStateFile);
$pgConn->resetStateToSeed();

$clienteRepo = new PostgresClienteRepository($pgConn);
$planRepo = new PostgresPlanSeguroRepository($pgConn);
$polizaRepo = new PostgresPolizaRepository($pgConn);
$facturaRepo = new PostgresFacturaRepository($pgConn);
$dynamoRepo = new DynamoDbSessionCacheRepository($testDynamoFile);
$pdfGenerator = new FacturaPdfGenerator();

$cotizadorDomain = new CotizacionPolizaDomainService();
$facturacionDomain = new FacturacionDomainService();

$authCtrl = new AuthOIDCController($clienteRepo, $dynamoRepo);
$fedResolver = new ApolloFederationResolver($clienteRepo, $polizaRepo, $planRepo, $facturaRepo, $dynamoRepo);
$catalogoSvc = new CatalogoPolizaApplicationService($planRepo, $clienteRepo);
$emisionCtrl = new EmisionPolizaGraphQLController(
    $planRepo,
    $clienteRepo,
    $polizaRepo,
    $facturaRepo,
    $cotizadorDomain,
    $facturacionDomain
);
$facturacionSvc = new FacturacionService($polizaRepo, $clienteRepo, $facturaRepo, $facturacionDomain, $pdfGenerator);
$recepcionSvc = new RecepcionPedidoService($emisionCtrl, $facturacionSvc);
$coberturaSvc = new PolizaCoberturaService($polizaRepo);
$sagaConsumer = new SagaKafkaConsumer($coberturaSvc);
$gql = new SupergraphGraphQLEngine(
    $fedResolver,
    $catalogoSvc,
    $emisionCtrl,
    $facturacionSvc,
    $polizaRepo,
    $clienteRepo,
    $planRepo,
    $facturaRepo
);

// 1. DDD Value Objects
assertCase('DDD ValueObject PrimaMonetaria calcula prima mensual y valida invariantes', function () {
    $prima = new PrimaMonetaria(720.00, 'USD');
    assertTrue($prima->calcularPrimaMensual()->monto() === 60.00, 'Mensual debe ser 60.00');
    $descontada = $prima->descontar(new PrimaMonetaria(120.00, 'USD'));
    assertTrue($descontada->monto() === 600.00, 'Descuento debe ser 600.00');
});

assertCase('DDD ValueObject VigenciaPoliza rechaza fechas invertidas y valida vigencia', function () {
    $vig = VigenciaPoliza::desdeMeses('2026-01-01', 12);
    assertTrue($vig->diasRestantes(new DateTimeImmutable('2026-06-01')) > 180, 'Debe tener >180 días restantes');

    $threw = false;
    try {
        new VigenciaPoliza('2027-01-01', '2026-01-01');
    } catch (DomainException) {
        $threw = true;
    }
    assertTrue($threw, 'Debió lanzar DomainException por rango de fechas inválido');
});

// 2. Aggregate Root Poliza y Saga (CU09)
assertCase('DDD AggregateRoot Poliza ejecuta descontarTechoAnualPoliza() y compensarCoberturaSaga()', function () {
    $poliza = Poliza::emitirNueva(
        UuidId::generate(),
        UuidId::generate(),
        VigenciaPoliza::desdeMeses('2026-10-01', 12),
        new PrimaMonetaria(720.00, 'USD'),
        25000.00,
        new BienAseguradoVehiculo('4028-PLK', '8AJBA3CD701982736', 'Toyota', 'Hilux 4x4', 2023, 34500.00)
    );

    $evDesc = $poliza->descontarTechoAnualPoliza(3000.00, 'saga-001', 'corr-001', 'REC-2026-00492');
    assertTrue($poliza->saldoCoberturaRestante()->monto() === 22000.00, 'Saldo tras descuento debe ser 22000');
    assertTrue($evDesc->getEventName() === 'CoberturaPolizaDescontadaEvent', 'Evento correcto');

    $evComp = $poliza->compensarCoberturaSaga(3000.00, 'saga-001', 'corr-001', 'REC-2026-00492');
    assertTrue($poliza->saldoCoberturaRestante()->monto() === 25000.00, 'Saldo tras rollback debe restituirse a 25000');
    assertTrue($evComp->getEventName() === 'CoberturaRestituidaEvent', 'Evento de compensación correcto');
});

// 3. CU01: SSO OIDC + PKCE + DynamoDB
assertCase('CU01 AuthOIDCController autentica con OAuth2/OIDC + PKCE S256 y guarda sesión en DynamoDB', function () use ($authCtrl) {
    $res = $authCtrl->autenticarUsuarioOIDC([
        'email' => 'carlos.mendoza@gmail.com',
        'code_verifier' => 'pkce-s256-challenge-verifier-2026',
    ]);
    assertTrue($res['authenticated'] === true, 'Autenticación debe ser exitosa');
    assertTrue($res['signature_algorithm'] === 'RS256', 'Firma debe ser RS256');
    assertTrue(count(explode('.', $res['access_token'])) === 3, 'JWT debe tener 3 segmentos');
    assertTrue(($res['sesion_unificada_dynamodb']['status'] ?? '') === 'ACTIVE_SSO_SESSION', 'Sesión activa en DynamoDB');

    $validacion = $authCtrl->validarTokenJwtRS256('Bearer ' . $res['access_token']);
    assertTrue($validacion['valido'] === true && $validacion['rol'] === 'CLIENTE', 'Token JWT validado correctamente');
});

// 4. CU02: Federación GraphQL (PostgreSQL + MongoDB + DynamoDB)
assertCase('CU02 GraphQL resumenUnificadoAsegurado consolida PostgreSQL, MongoDB y DynamoDB', function () use ($gql) {
    $query = <<<'GQL'
    query ResumenCliente($clienteId: ID!) {
      resumenUnificadoAsegurado(clienteId: $clienteId) {
        totalSaldoCoberturaDisponible
        cliente { id nombreCompleto scoreCrediticio }
        polizasActivas { id numeroPoliza saldoCoberturaRestante }
        siniestrosEnCurso { numeroReclamo estado }
        pagosPendientes { numeroFactura total }
      }
    }
    GQL;

    $res = $gql->execute($query, ['clienteId' => 'b0000001-0000-0000-0000-000000000001']);
    assertTrue(!isset($res['errors']), 'No debe haber errores GraphQL');
    $payload = $res['data']['resumenUnificadoAsegurado'] ?? [];
    assertTrue(($payload['cliente']['nombreCompleto'] ?? '') === 'Carlos Mendoza Roca', 'Cliente correcto');
    assertTrue(!empty($payload['polizasActivas']), 'Debe retornar pólizas activas de PostgreSQL');
    assertTrue(!empty($payload['siniestrosEnCurso']), 'Debe federar expedientes de siniestros de MongoDB');
    assertTrue(($payload['siniestrosEnCurso'][0]['numeroReclamo'] ?? '') === 'REC-2026-00492', 'Reclamo federado REC-2026-00492');
});

// 5. CU03: Catálogo de Planes, Coberturas con FK y Clientes
assertCase('CU03 GraphQL gestiona catálogo de Planes de Seguro, Coberturas con FK y Clientes', function () use ($gql) {
    $resPlanes = $gql->execute('query { listarPlanesSeguro { id codigo nombre primaBaseAnual coberturas { codigo sumaAseguradaMax } } }');
    assertTrue(count($resPlanes['data']['listarPlanesSeguro'] ?? []) >= 3, 'Debe listar al menos 3 planes iniciales');

    $resNuevoPlan = $gql->execute(
        'mutation CrearPlan($input: JSON!) { registrarPlanSeguro(input: $input) { id codigo nombre coberturas { codigo } } }',
        [
            'input' => [
                'codigo' => 'PLAN-HOGAR-360',
                'nombre' => 'Hogar Protegido 360',
                'tipo' => 'HOGAR',
                'primaBaseAnual' => 410.00,
                'deducibleBasePorcentaje' => 8.0,
            ],
        ]
    );
    assertTrue(($resNuevoPlan['data']['registrarPlanSeguro']['codigo'] ?? '') === 'PLAN-HOGAR-360', 'Plan creado');
});

assertCase('CU03 PdoPostgresConnection alterna estado activo/inactivo de planes (toggle-plan)', function () use ($pgConn) {
    $planId = 'a0000001-0000-0000-0000-000000000001';
    $updated1 = $pgConn->alternarEstadoPlanEnBd($planId);
    assertTrue($updated1 !== null, 'El plan debe existir');
    assertTrue($updated1['activo'] === false, 'El plan debe alternar a inactivo (false)');

    $updated2 = $pgConn->alternarEstadoPlanEnBd($planId);
    assertTrue($updated2 !== null, 'El plan debe existir');
    assertTrue($updated2['activo'] === true, 'El plan debe volver a activo (true)');

    $noExiste = $pgConn->alternarEstadoPlanEnBd('id-inexistente-xyz');
    assertTrue($noExiste === null, 'Debe retornar null para id inexistente');
});

// 6. CU04: Cotización en Línea, Validación IA Local Web y Emisión GraphQL
assertCase('CU04 GraphQL cotiza póliza, valida nitidez IA Local Web y emite contrato en PostgreSQL', function () use ($gql) {
    $resCot = $gql->execute(
        'mutation Cotizar($input: CotizarPolizaInput!) { cotizarPolizaEnLinea(input: $input) { primaCalculadaAnual primaCalculadaMensual descuentoScoreAplicado } }',
        [
            'input' => [
                'tipoPlan' => 'VEHICULAR',
                'planId' => 'a0000001-0000-0000-0000-000000000001',
                'edadConductor' => 32,
                'ciudad' => 'Santa Cruz',
                'datosBien' => [
                    'placa' => '5591-TXR',
                    'vin' => '5YJYGDEE3RF89104',
                    'marca' => 'Toyota',
                    'modelo' => 'Corolla Cross',
                    'anio' => 2024,
                    'valorComercial' => 28000.00,
                ],
            ],
        ]
    );
    assertTrue(($resCot['data']['cotizarPolizaEnLinea']['primaCalculadaAnual'] ?? 0) > 0, 'Prima anual calculada > 0');

    // Probar bloqueo cuando IA Local Web reporta documento borroso
    $resBlur = $gql->execute(
        'mutation Emitir($input: EmitirPolizaInput!) { emitirPoliza(input: $input) { id numeroPoliza } }',
        [
            'input' => [
                'clienteId' => 'b0000001-0000-0000-0000-000000000001',
                'planId' => 'a0000001-0000-0000-0000-000000000001',
                'canalVenta' => 'WEB_REACT',
                'tokenValidacionNitidezLocal' => 'BLURRY_REJECTED_SCORE_0.28',
                'datosBien' => [
                    'placa' => '5591-TXR',
                    'vin' => '5YJYGDEE3RF89104',
                    'marca' => 'Toyota',
                    'modelo' => 'Corolla Cross',
                    'anio' => 2024,
                    'valorComercial' => 28000.00,
                ],
            ],
        ]
    );
    assertTrue(isset($resBlur['errors']), 'Debe bloquear emisión cuando el documento es borroso según IA Local Web');

    // Emisión exitosa con token de nitidez válido
    $resEmit = $gql->execute(
        'mutation Emitir($input: EmitirPolizaInput!) { emitirPoliza(input: $input) { id numeroPoliza estado primaAnual facturas { numeroFactura total } } }',
        [
            'input' => [
                'clienteId' => 'b0000001-0000-0000-0000-000000000001',
                'planId' => 'a0000001-0000-0000-0000-000000000001',
                'canalVenta' => 'WEB_REACT',
                'tokenValidacionNitidezLocal' => 'TFJS-ONNX-LOCAL-OK-0.94',
                'datosBien' => [
                    'placa' => '5591-TXR',
                    'vin' => '5YJYGDEE3RF89104',
                    'marca' => 'Toyota',
                    'modelo' => 'Corolla Cross',
                    'anio' => 2024,
                    'valorComercial' => 28000.00,
                ],
            ],
        ]
    );
    assertTrue(!isset($resEmit['errors']), 'Emisión válida no debe tener errores');
    assertTrue(($resEmit['data']['emitirPoliza']['estado'] ?? '') === 'ACTIVA', 'Póliza emitida en estado ACTIVA');
});

// 7. CU05: Pedido de Póliza por WhatsApp n8n y Generación de Factura PDF con SHA-256
assertCase('CU05 RecepcionPedidoService y FacturacionService procesan pedido WhatsApp n8n y compilan PDF SHA-256', function () use ($recepcionSvc) {
    $res = $recepcionSvc->procesarPedidoPolizaWhatsApp([
        'telefono' => '+59171099887',
        'numero_documento' => '6234891-SC',
        'placa' => '6012-BGT',
        'plan_codigo' => 'PLAN-AUTO-FULL',
        'tipo_comprobante' => 'FACTURA',
    ]);
    assertTrue($res['status'] === 'SUCCESS', 'Pedido WhatsApp procesado con éxito');
    assertTrue(strlen($res['hash_digital_sha256']) === 64, 'Hash SHA-256 de 64 caracteres hexadecimales');
    assertTrue(
        str_contains($res['url_pdf'], '/api/v1/facturas/') || str_contains($res['url_pdf'], 'amazonaws.com/facturas/'),
        'URL de descarga PDF generada'
    );
});

// 8. CU09: Saga Kafka Consumer en MS1 PHP (Paso 2 Descuento y Rollback Compensación)
assertCase('CU09 SagaKafkaConsumer ejecuta Paso 2 (DescontarCoberturaPolizaCommand) y Rollback (CompensarCoberturaCommand)', function () use ($sagaConsumer) {
    $paso2Res = $sagaConsumer->handleKafkaMessage([
        'saga_id' => '99999999-0000-4000-8000-000000000099',
        'correlation_id' => '88888888-0000-4000-8000-000000000088',
        'event_type' => 'DescontarCoberturaPolizaCommand',
        'payload' => [
            'reclamo_id' => 'REC-2026-00492',
            'poliza_id' => 'd0000001-0000-0000-0000-000000000001',
            'monto_indemnizacion' => 2500.00,
        ],
    ]);
    assertTrue($paso2Res['event_type'] === 'CoberturaPolizaDescontadaEvent', 'Debe emitir CoberturaPolizaDescontadaEvent');

    $compRes = $sagaConsumer->handleKafkaMessage([
        'saga_id' => '99999999-0000-4000-8000-000000000099',
        'correlation_id' => '88888888-0000-4000-8000-000000000088',
        'event_type' => 'CompensarCoberturaCommand',
        'payload' => [
            'reclamo_id' => 'REC-2026-00492',
            'poliza_id' => 'd0000001-0000-0000-0000-000000000001',
            'monto_indemnizacion' => 2500.00,
            'motivo_fallo' => 'Fondos insuficientes en reserva técnica MS3',
        ],
    ]);
    assertTrue($compRes['event_type'] === 'CoberturaRestituidaEvent', 'Debe emitir CoberturaRestituidaEvent');
    assertTrue((float)$compRes['payload']['saldo_cobertura_restante'] === 25000.00, 'Saldo restituido exactamente a 25000.00');
});

@unlink($testStateFile);
@unlink($testDynamoFile);

echo "-----------------------------------------------------------------------------\n";
echo sprintf(" RESULTADO GLOBAL MS1 PHP 8.3: %d PASSED | %d FAILED\n", $passed, $failed);
echo "=============================================================================\n";

exit($failed > 0 ? 1 : 0);

