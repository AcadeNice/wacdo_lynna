<?php
namespace App\Core;

/**
 * Routeur simple avec support des parametres dynamiques et middlewares.
 */
class Router
{
    private array $routes = [];

    public function get(string $uri, string $action, array $mw = []): self
    {
        return $this->add('GET', $uri, $action, $mw);
    }

    public function post(string $uri, string $action, array $mw = []): self
    {
        return $this->add('POST', $uri, $action, $mw);
    }

    private function add(string $method, string $uri, string $action, array $mw): self
    {
        $this->routes[] = compact('method', 'uri', 'action', 'mw');
        return $this;
    }

    public function dispatch(string $method, string $uri): void
    {
        foreach ($this->routes as $route) {
            if ($route['method'] !== $method) continue;

            $pattern = preg_replace('#\{(\w+)\}#', '(?P<$1>[^/]+)', $route['uri']);
            if (preg_match('#^' . $pattern . '$#', $uri, $matches)) {
                // Middlewares
                foreach ($route['mw'] as $m) {
                    Middleware::handle($m);
                }
                // Resoudre Controller@method
                [$class, $func] = explode('@', $route['action']);
                $fqcn = "App\\Controllers\\{$class}";
                $instance = new $fqcn();
                $params = array_filter($matches, 'is_string', ARRAY_FILTER_USE_KEY);
                call_user_func_array([$instance, $func], array_values($params));
                return;
            }
        }
        http_response_code(404);
        echo '<h1>404 — Page non trouvee</h1>';
    }
}
