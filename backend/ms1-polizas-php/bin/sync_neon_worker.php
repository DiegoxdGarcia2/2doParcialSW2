<?php
declare(strict_types=1);

/**
 * Worker asíncrono en segundo plano para sincronización Write-Behind hacia Neon Serverless PostgreSQL.
 * Permite que el servidor HTTP responda en < 15 ms mientras persiste en la nube sin bloquear la UI.
 */

require_once dirname(__DIR__) . '/src/autoload.php';

use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\PdoPostgresConnection;

$conn = new PdoPostgresConnection();
$conn->flushStateToNeonNow();

