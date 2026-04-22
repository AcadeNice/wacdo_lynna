<?php
namespace App\Core;

/**
 * Bootstrap de l'application : session, routes, dispatch.
 */
class App
{
    public function run(): void
    {
        Session::start();

        $router = new Router();

        // Charger les routes
        require ROOT_PATH . '/routes/web.php';

        // URL propre depuis le query string
        $url = '/' . trim($_GET['url'] ?? '', '/');
        $method = $_SERVER['REQUEST_METHOD'];

        // CORS pour l'API
        if (str_starts_with($url, '/api/')) {
            header('Access-Control-Allow-Origin: *');
            header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
            header('Access-Control-Allow-Headers: Content-Type');
            if ($method === 'OPTIONS') {
                http_response_code(204);
                exit;
            }
        }

        $router->dispatch($method, $url);
    }
}
