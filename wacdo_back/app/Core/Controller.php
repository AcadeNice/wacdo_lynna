<?php
namespace App\Core;

/**
 * Classe de base pour tous les controleurs.
 * Fournit le rendu des vues, la redirection et les reponses JSON.
 */
abstract class Controller
{
    /** Rend une vue dans le layout admin. */
    protected function view(string $template, array $data = []): void
    {
        $data['_user_role'] = Session::get('user_role');
        $data['_username']  = Session::get('username');
        extract($data);
        ob_start();
        require ROOT_PATH . '/app/Views/' . $template . '.php';
        $content = ob_get_clean();
        require ROOT_PATH . '/app/Views/layout.php';
    }

    /** Rend une vue sans layout. */
    protected function viewRaw(string $template, array $data = []): void
    {
        extract($data);
        require ROOT_PATH . '/app/Views/' . $template . '.php';
    }

    /** Redirige vers une URL. */
    protected function redirect(string $path): void
    {
        header('Location: ' . BASE_URL . '/' . ltrim($path, '/'));
        exit;
    }

    /** Reponse JSON. */
    protected function json(mixed $data, int $code = 200): void
    {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        header('Access-Control-Allow-Origin: *');
        echo json_encode($data, JSON_UNESCAPED_UNICODE);
        exit;
    }
}
