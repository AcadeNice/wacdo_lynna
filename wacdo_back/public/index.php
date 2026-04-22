<?php
declare(strict_types=1);

/**
 * Wacdo Back-Office — Point d'entree unique.
 */

define('BASE_URL', '/wacdo_lynna/wacdo_back/public');
define('ROOT_PATH', dirname(__DIR__));

// Autoloader PSR-4
spl_autoload_register(function (string $class): void {
    $prefix = 'App\\';
    if (!str_starts_with($class, $prefix)) return;
    $relative = str_replace('\\', '/', substr($class, strlen($prefix)));
    $file = ROOT_PATH . '/app/' . $relative . '.php';
    if (file_exists($file)) require $file;
});

// Demarrage de l'application
$app = new App\Core\App();
$app->run();
