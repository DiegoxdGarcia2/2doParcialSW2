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
        'cloud_database' => 'Neon Serverless PostgreSQL (SSL required)',
        'timestamp' => date(DATE_ATOM)
    ]);
    exit;
}

if ($uri === '/health/db') {
    try {
        $dsn = getenv('DATABASE_URL') ?: ('pgsql:host=' . (getenv('DB_HOST') ?: '127.0.0.1') . ';port=' . (getenv('DB_PORT') ?: '5432') . ';dbname=' . (getenv('DB_DATABASE') ?: 'neondb') . ';sslmode=' . (getenv('DB_SSLMODE') ?: 'require'));
        $user = getenv('DB_USERNAME') ?: 'neondb_owner';
        $pass = getenv('DB_PASSWORD') ?: '';
        $pdo = new PDO($dsn, $user, $pass, [PDO::ATTR_TIMEOUT => 5]);
        $version = $pdo->query('SELECT version()')->fetchColumn();
        echo json_encode([
            'status' => 'CONNECTED',
            'database' => 'Neon PostgreSQL',
            'version' => substr((string)$version, 0, 40),
            'timestamp' => date(DATE_ATOM)
        ]);
    } catch (Throwable $e) {
        http_response_code(500);
        echo json_encode([
            'status' => 'ERROR',
            'error' => $e->getMessage()
        ]);
    }
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
