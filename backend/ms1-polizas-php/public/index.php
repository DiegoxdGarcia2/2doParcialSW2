<?php
declare(strict_types=1);

/**
 * AegisCore AI - MS1: Core ERP de Pólizas y Facturación (PHP 8.3 / DDD)
 * Endpoint HTTP y GraphQL preliminar
 */

header('Content-Type: application/json; charset=utf-8');

$uri = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);

if ($uri === '/health') {
    echo json_encode([
        'status' => 'UP',
        'service' => 'ms1-polizas-php',
        'pattern' => 'Domain-Driven Design (DDD)',
        'language' => 'PHP ' . PHP_VERSION,
        'timestamp' => date(DATE_ATOM)
    ]);
    exit;
}

if ($uri === '/graphql') {
    $rawInput = file_get_contents('php://input');
    $input = json_decode($rawInput, true) ?? [];
    $query = $input['query'] ?? '';

    // Mock / Resolver básico para pruebas de conectividad de la célula
    echo json_encode([
        'data' => [
            'service' => 'ms1-polizas-php',
            'status' => 'READY_FOR_DDD_RESOLVERS',
            'receivedQuery' => substr($query, 0, 100)
        ]
    ]);
    exit;
}

echo json_encode([
    'service' => 'ms1-polizas-php',
    'status' => 'OPERATIONAL',
    'endpoints' => [
        'GET /health' => 'Health check',
        'POST /graphql' => 'GraphQL API (Subgrafo de Pólizas y Facturas)'
    ]
]);
