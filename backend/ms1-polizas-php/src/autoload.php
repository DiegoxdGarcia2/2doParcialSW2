<?php
declare(strict_types=1);

/**
 * Cargador PSR-4 nativo para AegisCore\Polizas\ (MS1 PHP 8.3 DDD).
 * Si existe vendor/autoload.php lo incluye adicionalmente.
 */

$vendorAutoload = dirname(__DIR__) . '/vendor/autoload.php';
if (is_file($vendorAutoload)) {
    require_once $vendorAutoload;
}

spl_autoload_register(static function (string $class): void {
    $prefix = 'AegisCore\\Polizas\\';
    $baseDir = __DIR__ . DIRECTORY_SEPARATOR;

    $len = strlen($prefix);
    if (strncmp($prefix, $class, $len) !== 0) {
        return;
    }

    $relativeClass = substr($class, $len);
    $file = $baseDir . str_replace('\\', DIRECTORY_SEPARATOR, $relativeClass) . '.php';

    if (is_file($file)) {
        require_once $file;
    }
});

