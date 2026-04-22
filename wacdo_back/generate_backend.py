#!/usr/bin/env python3
"""Generate Wacdo Back-End application (Bloc 2) — MVC PHP 8+."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
files = {}

# ============================================================
#  COMPOSER
# ============================================================
files["composer.json"] = """{
    "name": "wacdo/back-office",
    "description": "Wacdo - Back-office administration (Bloc 2)",
    "type": "project",
    "require": { "php": ">=8.0" },
    "autoload": {
        "psr-4": { "App\\\\": "app/" }
    }
}
"""

# ============================================================
#  ROOT .htaccess
# ============================================================
files[".htaccess"] = """RewriteEngine On
RewriteRule ^$ public/ [L]
RewriteRule (.*) public/$1 [L]
"""

# ============================================================
#  CONFIG
# ============================================================
files["config/database.php"] = """<?php
return [
    'host'     => 'localhost',
    'database' => 'wacdo',
    'username' => 'root',
    'password' => '',
    'charset'  => 'utf8mb4',
];
"""

# ============================================================
#  SQL SCHEMA
# ============================================================
files["sql/schema.sql"] = """-- Wacdo Back-End — Schema MySQL / MariaDB
CREATE DATABASE IF NOT EXISTS wacdo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE wacdo;

-- Utilisateurs (internes)
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    email       VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    role        ENUM('admin','preparation','accueil') NOT NULL DEFAULT 'accueil',
    active      TINYINT(1) NOT NULL DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Categories
CREATE TABLE IF NOT EXISTS categories (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    slug          VARCHAR(100) NOT NULL UNIQUE,
    icon          VARCHAR(255) DEFAULT NULL,
    display_order INT DEFAULT 0,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Produits
CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name        VARCHAR(150) NOT NULL,
    description TEXT,
    price       DECIMAL(8,2) NOT NULL,
    image       VARCHAR(255) DEFAULT NULL,
    available   TINYINT(1) NOT NULL DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Menus
CREATE TABLE IF NOT EXISTS menus (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    description TEXT,
    base_price  DECIMAL(8,2) NOT NULL,
    image       VARCHAR(255) DEFAULT NULL,
    available   TINYINT(1) NOT NULL DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Composition des menus
CREATE TABLE IF NOT EXISTS menu_compositions (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    menu_id    INT NOT NULL,
    product_id INT NOT NULL,
    type       ENUM('burger','side','drink','sauce') NOT NULL,
    is_default TINYINT(1) DEFAULT 0,
    FOREIGN KEY (menu_id)    REFERENCES menus(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Commandes
CREATE TABLE IF NOT EXISTS orders (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(20) NOT NULL,
    mode         ENUM('sur-place','a-emporter') NOT NULL DEFAULT 'sur-place',
    status       ENUM('pending','preparing','ready','delivered','cancelled') NOT NULL DEFAULT 'pending',
    chevalet     INT DEFAULT NULL,
    total        DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_by   INT DEFAULT NULL,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Items de commande
CREATE TABLE IF NOT EXISTS order_items (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    order_id   INT NOT NULL,
    product_id INT DEFAULT NULL,
    menu_id    INT DEFAULT NULL,
    name       VARCHAR(150) NOT NULL,
    quantity   INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(8,2) NOT NULL,
    options    JSON DEFAULT NULL,
    FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)  ON DELETE SET NULL,
    FOREIGN KEY (menu_id)    REFERENCES menus(id)     ON DELETE SET NULL
) ENGINE=InnoDB;

-- Logs de securite
CREATE TABLE IF NOT EXISTS security_logs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT DEFAULT NULL,
    action     VARCHAR(100) NOT NULL,
    details    TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
"""

# ============================================================
#  SETUP SCRIPT (CLI)
# ============================================================
files["setup.php"] = """<?php
/**
 * Wacdo — Script d'installation CLI.
 * Usage : php setup.php
 */
echo "=== Wacdo Back-End — Installation ===\\n\\n";

$config = require __DIR__ . '/config/database.php';

// Connexion sans base
$dsn = "mysql:host={$config['host']};charset={$config['charset']}";
try {
    $pdo = new PDO($dsn, $config['username'], $config['password'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    ]);
} catch (PDOException $e) {
    die("Erreur connexion MySQL : " . $e->getMessage() . "\\n");
}

// Schema
echo "Creation de la base et des tables...\\n";
$sql = file_get_contents(__DIR__ . '/sql/schema.sql');
$pdo->exec($sql);
echo "  OK\\n";

// Selectionner la base
$pdo->exec("USE {$config['database']}");

// Utilisateurs par defaut
echo "Insertion des utilisateurs par defaut...\\n";
$users = [
    ['admin',       'admin@wacdo.fr',   'admin'],
    ['preparation', 'prep@wacdo.fr',    'preparation'],
    ['accueil',     'accueil@wacdo.fr', 'accueil'],
];
$stmt = $pdo->prepare("INSERT IGNORE INTO users (username, email, password, role) VALUES (?, ?, ?, ?)");
foreach ($users as [$user, $email, $role]) {
    $hash = password_hash('Wacdo2024!', PASSWORD_BCRYPT);
    $stmt->execute([$user, $email, $hash, $role]);
}
echo "  OK (mot de passe : Wacdo2024!)\\n";

// Categories
echo "Insertion des categories...\\n";
$cats = [
    ['Menus',    'menus',    'menus.png',    1],
    ['Burgers',  'burgers',  'burgers.png',  2],
    ['Frites',   'frites',   'frites.png',   3],
    ['Boissons', 'boissons', 'boissons.png', 4],
    ['Salades',  'salades',  'salades.png',  5],
    ['Wraps',    'wraps',    'wraps.png',    6],
    ['Encas',    'encas',    'encas.png',    7],
    ['Desserts', 'desserts', 'desserts.png', 8],
    ['Sauces',   'sauces',   'sauces.png',   9],
];
$stmt = $pdo->prepare("INSERT IGNORE INTO categories (name, slug, icon, display_order) VALUES (?, ?, ?, ?)");
foreach ($cats as $c) { $stmt->execute($c); }
echo "  OK\\n";

// Produits (exemples)
echo "Insertion des produits...\\n";
$products = [
    [2,'Le 280','',6.80,'/burgers/280.png'],
    [2,'Big Tasty','',5.90,'/burgers/BIG_TASTY_1_VIANDE.png'],
    [2,'Big Mac','',5.50,'/burgers/BIGMAC.png'],
    [2,'CBO','',6.10,'/burgers/CBO.png'],
    [2,'MC Chicken','',5.30,'/burgers/MCCHICKEN.png'],
    [2,'Royal Cheese','',4.90,'/burgers/ROYALCHEESE.png'],
    [2,'Royal Deluxe','',5.20,'/burgers/ROYALDELUXE.png'],
    [3,'Petite Frite','',1.45,'/frites/PETITE_FRITE.png'],
    [3,'Moyenne Frite','',2.75,'/frites/MOYENNE_FRITE.png'],
    [3,'Grande Frite','',3.50,'/frites/GRANDE_FRITE.png'],
    [3,'Potatoes','',2.15,'/frites/POTATOES.png'],
    [4,'Coca-Cola','',2.50,'/boissons/coca.png'],
    [4,'Sprite','',2.50,'/boissons/sprite.png'],
    [4,'Fanta','',2.50,'/boissons/fanta.png'],
    [4,'Eau','',1.50,'/boissons/eau.png'],
    [9,'Ketchup','',0.50,'/sauces/ketchup.png'],
    [9,'Mayonnaise','',0.50,'/sauces/mayonnaise.png'],
    [9,'Sauce Curry','',0.50,'/sauces/curry.png'],
];
$stmt = $pdo->prepare("INSERT INTO products (category_id, name, description, price, image) VALUES (?, ?, ?, ?, ?)");
foreach ($products as $p) { $stmt->execute($p); }
echo "  OK\\n";

// Menus
echo "Insertion des menus...\\n";
$menus = [
    ['Menu Le 280','', 8.80,'/burgers/280.png'],
    ['Menu Big Mac','', 8.00,'/burgers/BIGMAC.png'],
    ['Menu Big Tasty','', 10.60,'/burgers/BIG_TASTY_1_VIANDE.png'],
    ['Menu CBO','', 10.90,'/burgers/CBO.png'],
];
$stmt = $pdo->prepare("INSERT INTO menus (name, description, base_price, image) VALUES (?, ?, ?, ?)");
foreach ($menus as $m) { $stmt->execute($m); }
echo "  OK\\n";

echo "\\n=== Installation terminee ! ===\\n";
echo "Acces : http://localhost/wacdo_lynna/wacdo_back/public/login\\n";
echo "Admin  : admin / Wacdo2024!\\n";
"""

# ============================================================
#  PUBLIC / ENTRY POINT
# ============================================================
files["public/index.php"] = """<?php
declare(strict_types=1);

/**
 * Wacdo Back-Office — Point d'entree unique.
 */

define('BASE_URL', '/wacdo_lynna/wacdo_back/public');
define('ROOT_PATH', dirname(__DIR__));

// Autoloader PSR-4
spl_autoload_register(function (string $class): void {
    $prefix = 'App\\\\';
    if (!str_starts_with($class, $prefix)) return;
    $relative = str_replace('\\\\', '/', substr($class, strlen($prefix)));
    $file = ROOT_PATH . '/app/' . $relative . '.php';
    if (file_exists($file)) require $file;
});

// Demarrage de l'application
$app = new App\\Core\\App();
$app->run();
"""

files["public/.htaccess"] = """RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php?url=$1 [QSA,L]
"""

# ============================================================
#  CORE — Database
# ============================================================
files["app/Core/Database.php"] = """<?php
namespace App\\Core;

/**
 * Singleton PDO — Connexion securisee a la base de donnees.
 * Utilise des requetes preparees pour prevenir les injections SQL.
 */
class Database
{
    private static ?Database $instance = null;
    private \\PDO $pdo;

    private function __construct()
    {
        $config = require ROOT_PATH . '/config/database.php';
        $dsn = "mysql:host={$config['host']};dbname={$config['database']};charset={$config['charset']}";
        $this->pdo = new \\PDO($dsn, $config['username'], $config['password'], [
            \\PDO::ATTR_ERRMODE            => \\PDO::ERRMODE_EXCEPTION,
            \\PDO::ATTR_DEFAULT_FETCH_MODE => \\PDO::FETCH_ASSOC,
            \\PDO::ATTR_EMULATE_PREPARES   => false,
        ]);
    }

    public static function getInstance(): self
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    public function query(string $sql, array $params = []): \\PDOStatement
    {
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        return $stmt;
    }

    public function fetch(string $sql, array $params = []): ?array
    {
        $result = $this->query($sql, $params)->fetch();
        return $result ?: null;
    }

    public function fetchAll(string $sql, array $params = []): array
    {
        return $this->query($sql, $params)->fetchAll();
    }

    public function lastInsertId(): string
    {
        return $this->pdo->lastInsertId();
    }

    public function getPdo(): \\PDO
    {
        return $this->pdo;
    }
}
"""

# ============================================================
#  CORE — Session
# ============================================================
files["app/Core/Session.php"] = """<?php
namespace App\\Core;

/**
 * Gestion securisee des sessions.
 */
class Session
{
    public static function start(): void
    {
        if (session_status() === PHP_SESSION_NONE) {
            ini_set('session.cookie_httponly', '1');
            ini_set('session.use_strict_mode', '1');
            session_start();
        }
    }

    public static function set(string $key, mixed $value): void
    {
        $_SESSION[$key] = $value;
    }

    public static function get(string $key, mixed $default = null): mixed
    {
        return $_SESSION[$key] ?? $default;
    }

    public static function has(string $key): bool
    {
        return isset($_SESSION[$key]);
    }

    public static function remove(string $key): void
    {
        unset($_SESSION[$key]);
    }

    public static function destroy(): void
    {
        session_destroy();
        $_SESSION = [];
    }

    public static function regenerate(): void
    {
        session_regenerate_id(true);
    }

    /** Messages flash (affiches une seule fois). */
    public static function flash(string $key, string $message): void
    {
        $_SESSION['_flash'][$key] = $message;
    }

    public static function getFlash(string $key): ?string
    {
        $msg = $_SESSION['_flash'][$key] ?? null;
        unset($_SESSION['_flash'][$key]);
        return $msg;
    }
}
"""

# ============================================================
#  CORE — Security
# ============================================================
files["app/Core/Security.php"] = """<?php
namespace App\\Core;

/**
 * Securite : CSRF, XSS, sanitisation.
 */
class Security
{
    /** Genere un jeton CSRF et le stocke en session. */
    public static function generateCsrfToken(): string
    {
        $token = bin2hex(random_bytes(32));
        Session::set('csrf_token', $token);
        return $token;
    }

    /** Verifie le jeton CSRF soumis. */
    public static function verifyCsrfToken(string $token): bool
    {
        $stored = Session::get('csrf_token');
        if ($stored === null) return false;
        return hash_equals($stored, $token);
    }

    /** Champ hidden HTML pour CSRF. */
    public static function csrfField(): string
    {
        $token = self::generateCsrfToken();
        return '<input type="hidden" name="_token" value="' . $token . '">';
    }

    /** Echappe les caracteres HTML (protection XSS). */
    public static function escape(mixed $value): string
    {
        return htmlspecialchars((string) $value, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    }

    /** Verifie le token CSRF d'une requete POST. */
    public static function checkCsrf(): void
    {
        $token = $_POST['_token'] ?? '';
        if (!self::verifyCsrfToken($token)) {
            http_response_code(403);
            die('Erreur de securite : jeton CSRF invalide.');
        }
    }
}
"""

# ============================================================
#  CORE — Middleware
# ============================================================
files["app/Core/Middleware.php"] = """<?php
namespace App\\Core;

/**
 * Middleware d'autorisation par role.
 */
class Middleware
{
    /** Dispatch un middleware par nom. */
    public static function handle(string $name): void
    {
        match ($name) {
            'auth'        => self::auth(),
            'guest'       => self::guest(),
            'admin'       => self::role('admin'),
            'preparation' => self::role('preparation'),
            'accueil'     => self::role('accueil'),
            'staff'       => self::anyRole(['admin', 'accueil']),
            'all_roles'   => self::anyRole(['admin', 'preparation', 'accueil']),
            default       => null,
        };
    }

    /** Verifie que l'utilisateur est connecte. */
    private static function auth(): void
    {
        if (!Session::has('user_id')) {
            header('Location: ' . BASE_URL . '/login');
            exit;
        }
    }

    /** Verifie que l'utilisateur n'est PAS connecte. */
    private static function guest(): void
    {
        if (Session::has('user_id')) {
            header('Location: ' . BASE_URL . '/dashboard');
            exit;
        }
    }

    /** Verifie un role precis. */
    private static function role(string $role): void
    {
        self::auth();
        if (Session::get('user_role') !== $role) {
            http_response_code(403);
            die('Acces interdit : role "' . $role . '" requis.');
        }
    }

    /** Verifie que le role est dans une liste. */
    private static function anyRole(array $roles): void
    {
        self::auth();
        if (!in_array(Session::get('user_role'), $roles, true)) {
            http_response_code(403);
            die('Acces interdit.');
        }
    }
}
"""

# ============================================================
#  CORE — Base Controller
# ============================================================
files["app/Core/Controller.php"] = """<?php
namespace App\\Core;

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
"""

# ============================================================
#  CORE — Base Model
# ============================================================
files["app/Core/Model.php"] = """<?php
namespace App\\Core;

/**
 * Classe de base pour tous les modeles.
 * Fournit les operations CRUD via PDO (requetes preparees).
 */
abstract class Model
{
    protected string $table;
    protected string $primaryKey = 'id';
    protected array $fillable = [];
    protected Database $db;

    public function __construct()
    {
        $this->db = Database::getInstance();
    }

    public function find(int $id): ?array
    {
        return $this->db->fetch(
            "SELECT * FROM {$this->table} WHERE {$this->primaryKey} = ?", [$id]
        );
    }

    public function findAll(string $orderBy = 'id ASC'): array
    {
        return $this->db->fetchAll("SELECT * FROM {$this->table} ORDER BY {$orderBy}");
    }

    public function findBy(string $column, mixed $value): ?array
    {
        return $this->db->fetch(
            "SELECT * FROM {$this->table} WHERE {$column} = ?", [$value]
        );
    }

    public function findAllBy(string $column, mixed $value, string $orderBy = 'id ASC'): array
    {
        return $this->db->fetchAll(
            "SELECT * FROM {$this->table} WHERE {$column} = ? ORDER BY {$orderBy}",
            [$value]
        );
    }

    public function create(array $data): int
    {
        $filtered = array_intersect_key($data, array_flip($this->fillable));
        $cols = implode(', ', array_keys($filtered));
        $ph   = implode(', ', array_fill(0, count($filtered), '?'));
        $this->db->query("INSERT INTO {$this->table} ({$cols}) VALUES ({$ph})", array_values($filtered));
        return (int) $this->db->lastInsertId();
    }

    public function update(int $id, array $data): bool
    {
        $filtered = array_intersect_key($data, array_flip($this->fillable));
        if (empty($filtered)) return false;
        $set = implode(', ', array_map(fn($c) => "{$c} = ?", array_keys($filtered)));
        $vals = array_values($filtered);
        $vals[] = $id;
        $this->db->query("UPDATE {$this->table} SET {$set} WHERE {$this->primaryKey} = ?", $vals);
        return true;
    }

    public function delete(int $id): bool
    {
        $this->db->query("DELETE FROM {$this->table} WHERE {$this->primaryKey} = ?", [$id]);
        return true;
    }

    public function count(): int
    {
        $r = $this->db->fetch("SELECT COUNT(*) as total FROM {$this->table}");
        return (int) ($r['total'] ?? 0);
    }

    public function countBy(string $column, mixed $value): int
    {
        $r = $this->db->fetch("SELECT COUNT(*) as total FROM {$this->table} WHERE {$column} = ?", [$value]);
        return (int) ($r['total'] ?? 0);
    }
}
"""

# ============================================================
#  CORE — Router
# ============================================================
files["app/Core/Router.php"] = """<?php
namespace App\\Core;

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

            $pattern = preg_replace('#\\{(\\w+)\\}#', '(?P<$1>[^/]+)', $route['uri']);
            if (preg_match('#^' . $pattern . '$#', $uri, $matches)) {
                // Middlewares
                foreach ($route['mw'] as $m) {
                    Middleware::handle($m);
                }
                // Resoudre Controller@method
                [$class, $func] = explode('@', $route['action']);
                $fqcn = "App\\\\Controllers\\\\{$class}";
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
"""

# ============================================================
#  CORE — App (bootstrap)
# ============================================================
files["app/Core/App.php"] = """<?php
namespace App\\Core;

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
"""

# ============================================================
#  ROUTES
# ============================================================
files["routes/web.php"] = """<?php
/**
 * Definition des routes de l'application.
 * $router est une instance de App\\Core\\Router.
 */

// Auth
$router->get('/login',  'AuthController@showLogin', ['guest']);
$router->post('/login', 'AuthController@login',     ['guest']);
$router->get('/logout', 'AuthController@logout',     ['auth']);

// Dashboard
$router->get('/',          'DashboardController@index', ['auth']);
$router->get('/dashboard', 'DashboardController@index', ['auth']);

// Utilisateurs (admin uniquement)
$router->get('/users',              'UserController@index',  ['admin']);
$router->get('/users/create',       'UserController@create', ['admin']);
$router->post('/users',             'UserController@store',  ['admin']);
$router->get('/users/{id}/edit',    'UserController@edit',   ['admin']);
$router->post('/users/{id}',        'UserController@update', ['admin']);
$router->post('/users/{id}/delete', 'UserController@destroy',['admin']);

// Produits (admin)
$router->get('/products',              'ProductController@index',  ['admin']);
$router->get('/products/create',       'ProductController@create', ['admin']);
$router->post('/products',             'ProductController@store',  ['admin']);
$router->get('/products/{id}/edit',    'ProductController@edit',   ['admin']);
$router->post('/products/{id}',        'ProductController@update', ['admin']);
$router->post('/products/{id}/delete', 'ProductController@destroy',['admin']);

// Categories (admin)
$router->get('/categories',              'CategoryController@index',  ['admin']);
$router->get('/categories/create',       'CategoryController@create', ['admin']);
$router->post('/categories',             'CategoryController@store',  ['admin']);
$router->get('/categories/{id}/edit',    'CategoryController@edit',   ['admin']);
$router->post('/categories/{id}',        'CategoryController@update', ['admin']);
$router->post('/categories/{id}/delete', 'CategoryController@destroy',['admin']);

// Menus (admin)
$router->get('/menus',              'MenuController@index',  ['admin']);
$router->get('/menus/create',       'MenuController@create', ['admin']);
$router->post('/menus',             'MenuController@store',  ['admin']);
$router->get('/menus/{id}/edit',    'MenuController@edit',   ['admin']);
$router->post('/menus/{id}',        'MenuController@update', ['admin']);
$router->post('/menus/{id}/delete', 'MenuController@destroy',['admin']);

// Commandes (admin + accueil)
$router->get('/orders',              'OrderController@index',   ['staff']);
$router->get('/orders/create',       'OrderController@create',  ['staff']);
$router->post('/orders',             'OrderController@store',   ['staff']);
$router->get('/orders/{id}',         'OrderController@show',    ['staff']);
$router->post('/orders/{id}/deliver','OrderController@deliver', ['staff']);

// Preparation (admin + preparation)
$router->get('/preparation',              'PreparationController@index',     ['all_roles']);
$router->post('/preparation/{id}/ready',  'PreparationController@markReady', ['all_roles']);

// API publique (pas de middleware auth)
$router->get('/api/produits',            'Api\\\\ProductApiController@index');
$router->get('/api/produits/{category}', 'Api\\\\ProductApiController@byCategory');
$router->get('/api/menus',               'Api\\\\MenuApiController@index');
$router->post('/api/commande',           'Api\\\\OrderApiController@store');
"""

# ============================================================
#  MODELS
# ============================================================
files["app/Models/User.php"] = """<?php
namespace App\\Models;

use App\\Core\\Model;

class User extends Model
{
    protected string $table = 'users';
    protected array $fillable = ['username', 'email', 'password', 'role', 'active'];

    public function findByUsername(string $username): ?array
    {
        return $this->findBy('username', $username);
    }

    public function findByEmail(string $email): ?array
    {
        return $this->findBy('email', $email);
    }
}
"""

files["app/Models/Category.php"] = """<?php
namespace App\\Models;

use App\\Core\\Model;

class Category extends Model
{
    protected string $table = 'categories';
    protected array $fillable = ['name', 'slug', 'icon', 'display_order'];

    public function findAllOrdered(): array
    {
        return $this->db->fetchAll("SELECT * FROM categories ORDER BY display_order ASC");
    }

    public function findBySlug(string $slug): ?array
    {
        return $this->findBy('slug', $slug);
    }
}
"""

files["app/Models/Product.php"] = """<?php
namespace App\\Models;

use App\\Core\\Model;

class Product extends Model
{
    protected string $table = 'products';
    protected array $fillable = ['category_id', 'name', 'description', 'price', 'image', 'available'];

    public function findWithCategory(int $id): ?array
    {
        return $this->db->fetch(
            "SELECT p.*, c.name as category_name, c.slug as category_slug
             FROM products p JOIN categories c ON p.category_id = c.id
             WHERE p.id = ?", [$id]
        );
    }

    public function findAllWithCategory(): array
    {
        return $this->db->fetchAll(
            "SELECT p.*, c.name as category_name
             FROM products p JOIN categories c ON p.category_id = c.id
             ORDER BY c.display_order, p.name"
        );
    }

    public function findByCategory(int $categoryId): array
    {
        return $this->findAllBy('category_id', $categoryId, 'name ASC');
    }

    public function findByCategorySlug(string $slug): array
    {
        return $this->db->fetchAll(
            "SELECT p.* FROM products p
             JOIN categories c ON p.category_id = c.id
             WHERE c.slug = ? AND p.available = 1
             ORDER BY p.name", [$slug]
        );
    }

    /** Retourne tous les produits groupes par categorie (format API). */
    public function allGroupedByCategory(): array
    {
        $rows = $this->db->fetchAll(
            "SELECT p.id, p.name as nom, p.price as prix, p.image, c.slug as cat
             FROM products p JOIN categories c ON p.category_id = c.id
             WHERE p.available = 1
             ORDER BY c.display_order, p.name"
        );
        $grouped = [];
        foreach ($rows as $r) {
            $cat = $r['cat'];
            unset($r['cat']);
            $r['prix'] = (float) $r['prix'];
            $grouped[$cat][] = $r;
        }
        return $grouped;
    }
}
"""

files["app/Models/Menu.php"] = """<?php
namespace App\\Models;

use App\\Core\\Model;

class Menu extends Model
{
    protected string $table = 'menus';
    protected array $fillable = ['name', 'description', 'base_price', 'image', 'available'];

    /** Retourne tous les menus avec leur composition. */
    public function findAllWithComposition(): array
    {
        $menus = $this->findAll('name ASC');
        foreach ($menus as &$menu) {
            $menu['compositions'] = $this->db->fetchAll(
                "SELECT mc.*, p.name as product_name
                 FROM menu_compositions mc
                 JOIN products p ON mc.product_id = p.id
                 WHERE mc.menu_id = ?", [$menu['id']]
            );
        }
        return $menus;
    }

    /** Format API pour le front-end. */
    public function allForApi(): array
    {
        $menus = $this->db->fetchAll(
            "SELECT id, name as nom, base_price as prix, image
             FROM menus WHERE available = 1 ORDER BY name"
        );
        foreach ($menus as &$m) {
            $m['prix'] = (float) $m['prix'];
        }
        return $menus;
    }

    /** Ajoute une composition. */
    public function addComposition(int $menuId, int $productId, string $type, bool $isDefault = false): void
    {
        $this->db->query(
            "INSERT INTO menu_compositions (menu_id, product_id, type, is_default) VALUES (?, ?, ?, ?)",
            [$menuId, $productId, $type, $isDefault ? 1 : 0]
        );
    }

    /** Supprime les compositions d'un menu. */
    public function clearCompositions(int $menuId): void
    {
        $this->db->query("DELETE FROM menu_compositions WHERE menu_id = ?", [$menuId]);
    }
}
"""

files["app/Models/Order.php"] = """<?php
namespace App\\Models;

use App\\Core\\Model;

class Order extends Model
{
    protected string $table = 'orders';
    protected array $fillable = ['order_number', 'mode', 'status', 'chevalet', 'total', 'created_by'];

    public function findWithItems(int $id): ?array
    {
        $order = $this->find($id);
        if (!$order) return null;
        $order['items'] = $this->db->fetchAll(
            "SELECT * FROM order_items WHERE order_id = ?", [$id]
        );
        return $order;
    }

    public function findAllByStatus(string $status): array
    {
        return $this->db->fetchAll(
            "SELECT * FROM orders WHERE status = ? ORDER BY created_at ASC", [$status]
        );
    }

    public function findRecent(int $limit = 50): array
    {
        return $this->db->fetchAll(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", [$limit]
        );
    }

    public function updateStatus(int $id, string $status): void
    {
        $this->db->query("UPDATE orders SET status = ? WHERE id = ?", [$status, $id]);
    }

    /** Statistiques pour le dashboard. */
    public function todayStats(): array
    {
        $today = date('Y-m-d');
        return [
            'total'    => (int) ($this->db->fetch("SELECT COUNT(*) as c FROM orders WHERE DATE(created_at) = ?", [$today])['c'] ?? 0),
            'pending'  => (int) ($this->db->fetch("SELECT COUNT(*) as c FROM orders WHERE status IN ('pending','preparing') AND DATE(created_at) = ?", [$today])['c'] ?? 0),
            'revenue'  => (float) ($this->db->fetch("SELECT COALESCE(SUM(total),0) as s FROM orders WHERE DATE(created_at) = ? AND status != 'cancelled'", [$today])['s'] ?? 0),
        ];
    }
}
"""

files["app/Models/OrderItem.php"] = """<?php
namespace App\\Models;

use App\\Core\\Model;

class OrderItem extends Model
{
    protected string $table = 'order_items';
    protected array $fillable = ['order_id', 'product_id', 'menu_id', 'name', 'quantity', 'unit_price', 'options'];
}
"""

# ============================================================
#  CONTROLLERS — Auth
# ============================================================
files["app/Controllers/AuthController.php"] = """<?php
namespace App\\Controllers;

use App\\Core\\Controller;
use App\\Core\\Session;
use App\\Core\\Security;
use App\\Models\\User;

class AuthController extends Controller
{
    public function showLogin(): void
    {
        $this->viewRaw('auth/login', [
            'error' => Session::getFlash('error'),
        ]);
    }

    public function login(): void
    {
        Security::checkCsrf();

        $username = trim($_POST['username'] ?? '');
        $password = $_POST['password'] ?? '';

        if ($username === '' || $password === '') {
            Session::flash('error', 'Veuillez remplir tous les champs.');
            $this->redirect('login');
        }

        $userModel = new User();
        $user = $userModel->findByUsername($username);

        if (!$user || !password_verify($password, $user['password'])) {
            // Log tentative echouee
            $db = \\App\\Core\\Database::getInstance();
            $db->query(
                "INSERT INTO security_logs (user_id, action, details, ip_address, user_agent) VALUES (?, ?, ?, ?, ?)",
                [null, 'login_failed', "Tentative pour : {$username}", $_SERVER['REMOTE_ADDR'] ?? '', substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 500)]
            );
            Session::flash('error', 'Identifiants incorrects.');
            $this->redirect('login');
        }

        if (!$user['active']) {
            Session::flash('error', 'Compte desactive.');
            $this->redirect('login');
        }

        // Connexion reussie
        Session::regenerate();
        Session::set('user_id', $user['id']);
        Session::set('username', $user['username']);
        Session::set('user_role', $user['role']);

        // Log
        $db = \\App\\Core\\Database::getInstance();
        $db->query(
            "INSERT INTO security_logs (user_id, action, ip_address, user_agent) VALUES (?, ?, ?, ?)",
            [$user['id'], 'login_success', $_SERVER['REMOTE_ADDR'] ?? '', substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 500)]
        );

        $this->redirect('dashboard');
    }

    public function logout(): void
    {
        Session::destroy();
        header('Location: ' . BASE_URL . '/login');
        exit;
    }
}
"""

# ============================================================
#  CONTROLLERS — Dashboard
# ============================================================
files["app/Controllers/DashboardController.php"] = """<?php
namespace App\\Controllers;

use App\\Core\\Controller;
use App\\Models\\Order;
use App\\Models\\Product;
use App\\Models\\User;

class DashboardController extends Controller
{
    public function index(): void
    {
        $orderModel   = new Order();
        $productModel = new Product();
        $userModel    = new User();

        $stats = $orderModel->todayStats();
        $stats['products'] = $productModel->count();
        $stats['users']    = $userModel->count();
        $recentOrders = $orderModel->findRecent(10);

        $this->view('dashboard/index', compact('stats', 'recentOrders'));
    }
}
"""

# ============================================================
#  CONTROLLERS — Users CRUD
# ============================================================
files["app/Controllers/UserController.php"] = """<?php
namespace App\\Controllers;

use App\\Core\\Controller;
use App\\Core\\Security;
use App\\Core\\Session;
use App\\Models\\User;

class UserController extends Controller
{
    public function index(): void
    {
        $users = (new User())->findAll('username ASC');
        $this->view('users/index', compact('users'));
    }

    public function create(): void
    {
        $this->view('users/form', ['user' => null]);
    }

    public function store(): void
    {
        Security::checkCsrf();
        $data = $this->validated();
        $data['password'] = password_hash($data['password'], PASSWORD_BCRYPT);
        (new User())->create($data);
        Session::flash('success', 'Utilisateur cree.');
        $this->redirect('users');
    }

    public function edit(string $id): void
    {
        $user = (new User())->find((int) $id);
        if (!$user) $this->redirect('users');
        $this->view('users/form', compact('user'));
    }

    public function update(string $id): void
    {
        Security::checkCsrf();
        $data = $this->validated(false);
        if (!empty($data['password'])) {
            $data['password'] = password_hash($data['password'], PASSWORD_BCRYPT);
        } else {
            unset($data['password']);
        }
        (new User())->update((int) $id, $data);
        Session::flash('success', 'Utilisateur mis a jour.');
        $this->redirect('users');
    }

    public function destroy(string $id): void
    {
        Security::checkCsrf();
        (new User())->delete((int) $id);
        Session::flash('success', 'Utilisateur supprime.');
        $this->redirect('users');
    }

    private function validated(bool $requirePassword = true): array
    {
        $data = [
            'username' => trim($_POST['username'] ?? ''),
            'email'    => trim($_POST['email'] ?? ''),
            'role'     => $_POST['role'] ?? 'accueil',
            'active'   => isset($_POST['active']) ? 1 : 0,
        ];
        if ($requirePassword || !empty($_POST['password'])) {
            $data['password'] = $_POST['password'] ?? '';
        }
        return $data;
    }
}
"""

# ============================================================
#  CONTROLLERS — Products CRUD
# ============================================================
files["app/Controllers/ProductController.php"] = """<?php
namespace App\\Controllers;

use App\\Core\\Controller;
use App\\Core\\Security;
use App\\Core\\Session;
use App\\Models\\Product;
use App\\Models\\Category;

class ProductController extends Controller
{
    public function index(): void
    {
        $products = (new Product())->findAllWithCategory();
        $this->view('products/index', compact('products'));
    }

    public function create(): void
    {
        $categories = (new Category())->findAllOrdered();
        $this->view('products/form', ['product' => null, 'categories' => $categories]);
    }

    public function store(): void
    {
        Security::checkCsrf();
        $data = $this->validated();
        $data['image'] = $this->handleUpload() ?: ($data['image'] ?? '');
        (new Product())->create($data);
        Session::flash('success', 'Produit cree.');
        $this->redirect('products');
    }

    public function edit(string $id): void
    {
        $product    = (new Product())->find((int) $id);
        $categories = (new Category())->findAllOrdered();
        if (!$product) $this->redirect('products');
        $this->view('products/form', compact('product', 'categories'));
    }

    public function update(string $id): void
    {
        Security::checkCsrf();
        $data = $this->validated();
        $uploaded = $this->handleUpload();
        if ($uploaded) $data['image'] = $uploaded;
        (new Product())->update((int) $id, $data);
        Session::flash('success', 'Produit mis a jour.');
        $this->redirect('products');
    }

    public function destroy(string $id): void
    {
        Security::checkCsrf();
        (new Product())->delete((int) $id);
        Session::flash('success', 'Produit supprime.');
        $this->redirect('products');
    }

    private function validated(): array
    {
        return [
            'category_id' => (int) ($_POST['category_id'] ?? 0),
            'name'        => trim($_POST['name'] ?? ''),
            'description' => trim($_POST['description'] ?? ''),
            'price'       => (float) ($_POST['price'] ?? 0),
            'image'       => trim($_POST['image'] ?? ''),
            'available'   => isset($_POST['available']) ? 1 : 0,
        ];
    }

    private function handleUpload(): string
    {
        if (!isset($_FILES['image_file']) || $_FILES['image_file']['error'] !== UPLOAD_ERR_OK) {
            return '';
        }
        $file = $_FILES['image_file'];
        $ext  = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if (!in_array($ext, ['jpg','jpeg','png','gif','webp'])) return '';
        $name = uniqid('prod_') . '.' . $ext;
        $dest = ROOT_PATH . '/public/uploads/' . $name;
        if (!is_dir(dirname($dest))) mkdir(dirname($dest), 0755, true);
        move_uploaded_file($file['tmp_name'], $dest);
        return '/uploads/' . $name;
    }
}
"""

# ============================================================
#  CONTROLLERS — Categories CRUD
# ============================================================
files["app/Controllers/CategoryController.php"] = """<?php
namespace App\\Controllers;

use App\\Core\\Controller;
use App\\Core\\Security;
use App\\Core\\Session;
use App\\Models\\Category;

class CategoryController extends Controller
{
    public function index(): void
    {
        $categories = (new Category())->findAllOrdered();
        $this->view('categories/index', compact('categories'));
    }

    public function create(): void
    {
        $this->view('categories/form', ['category' => null]);
    }

    public function store(): void
    {
        Security::checkCsrf();
        $data = $this->validated();
        (new Category())->create($data);
        Session::flash('success', 'Categorie creee.');
        $this->redirect('categories');
    }

    public function edit(string $id): void
    {
        $category = (new Category())->find((int) $id);
        if (!$category) $this->redirect('categories');
        $this->view('categories/form', compact('category'));
    }

    public function update(string $id): void
    {
        Security::checkCsrf();
        (new Category())->update((int) $id, $this->validated());
        Session::flash('success', 'Categorie mise a jour.');
        $this->redirect('categories');
    }

    public function destroy(string $id): void
    {
        Security::checkCsrf();
        (new Category())->delete((int) $id);
        Session::flash('success', 'Categorie supprimee.');
        $this->redirect('categories');
    }

    private function validated(): array
    {
        $name = trim($_POST['name'] ?? '');
        return [
            'name'          => $name,
            'slug'          => strtolower(preg_replace('/[^a-z0-9]+/', '-', strtolower($name))),
            'icon'          => trim($_POST['icon'] ?? ''),
            'display_order' => (int) ($_POST['display_order'] ?? 0),
        ];
    }
}
"""

# ============================================================
#  CONTROLLERS — Menus CRUD
# ============================================================
files["app/Controllers/MenuController.php"] = """<?php
namespace App\\Controllers;

use App\\Core\\Controller;
use App\\Core\\Security;
use App\\Core\\Session;
use App\\Models\\Menu;
use App\\Models\\Product;

class MenuController extends Controller
{
    public function index(): void
    {
        $menus = (new Menu())->findAllWithComposition();
        $this->view('menus/index', compact('menus'));
    }

    public function create(): void
    {
        $products = (new Product())->findAllWithCategory();
        $this->view('menus/form', ['menu' => null, 'products' => $products, 'compositions' => []]);
    }

    public function store(): void
    {
        Security::checkCsrf();
        $data = $this->validated();
        $menuModel = new Menu();
        $id = $menuModel->create($data);
        $this->saveCompositions($menuModel, $id);
        Session::flash('success', 'Menu cree.');
        $this->redirect('menus');
    }

    public function edit(string $id): void
    {
        $menuModel = new Menu();
        $menu = $menuModel->find((int) $id);
        if (!$menu) $this->redirect('menus');
        $products     = (new Product())->findAllWithCategory();
        $compositions = (new \\App\\Core\\Database())->fetchAll(
            "SELECT * FROM menu_compositions WHERE menu_id = ?", [(int) $id]
        );
        $this->view('menus/form', compact('menu', 'products', 'compositions'));
    }

    public function update(string $id): void
    {
        Security::checkCsrf();
        $menuModel = new Menu();
        $menuModel->update((int) $id, $this->validated());
        $menuModel->clearCompositions((int) $id);
        $this->saveCompositions($menuModel, (int) $id);
        Session::flash('success', 'Menu mis a jour.');
        $this->redirect('menus');
    }

    public function destroy(string $id): void
    {
        Security::checkCsrf();
        (new Menu())->delete((int) $id);
        Session::flash('success', 'Menu supprime.');
        $this->redirect('menus');
    }

    private function validated(): array
    {
        return [
            'name'        => trim($_POST['name'] ?? ''),
            'description' => trim($_POST['description'] ?? ''),
            'base_price'  => (float) ($_POST['base_price'] ?? 0),
            'image'       => trim($_POST['image'] ?? ''),
            'available'   => isset($_POST['available']) ? 1 : 0,
        ];
    }

    private function saveCompositions(Menu $menuModel, int $menuId): void
    {
        $types = ['burger', 'side', 'drink', 'sauce'];
        foreach ($types as $type) {
            $ids = $_POST['comp_' . $type] ?? [];
            if (!is_array($ids)) $ids = [$ids];
            foreach ($ids as $pid) {
                if ((int) $pid > 0) {
                    $menuModel->addComposition($menuId, (int) $pid, $type);
                }
            }
        }
    }
}
"""

# ============================================================
#  CONTROLLERS — Orders
# ============================================================
files["app/Controllers/OrderController.php"] = """<?php
namespace App\\Controllers;

use App\\Core\\Controller;
use App\\Core\\Security;
use App\\Core\\Session;
use App\\Models\\Order;
use App\\Models\\OrderItem;
use App\\Models\\Product;
use App\\Models\\Menu;

class OrderController extends Controller
{
    public function index(): void
    {
        $orders = (new Order())->findRecent(100);
        $this->view('orders/index', compact('orders'));
    }

    public function create(): void
    {
        $products = (new Product())->findAllWithCategory();
        $menus    = (new Menu())->findAll('name ASC');
        $this->view('orders/create', compact('products', 'menus'));
    }

    public function store(): void
    {
        Security::checkCsrf();
        $orderModel = new Order();
        $orderId = $orderModel->create([
            'order_number' => trim($_POST['order_number'] ?? (string) rand(100,999)),
            'mode'         => $_POST['mode'] ?? 'sur-place',
            'status'       => 'pending',
            'total'        => 0,
            'created_by'   => Session::get('user_id'),
        ]);

        $itemModel = new OrderItem();
        $total = 0;
        $names  = $_POST['item_name']  ?? [];
        $qtys   = $_POST['item_qty']   ?? [];
        $prices = $_POST['item_price'] ?? [];
        for ($i = 0; $i < count($names); $i++) {
            if (empty($names[$i])) continue;
            $price = (float) ($prices[$i] ?? 0);
            $qty   = max(1, (int) ($qtys[$i] ?? 1));
            $itemModel->create([
                'order_id'   => $orderId,
                'name'       => $names[$i],
                'quantity'   => $qty,
                'unit_price' => $price,
            ]);
            $total += $price * $qty;
        }
        $orderModel->update($orderId, ['total' => $total]);

        Session::flash('success', 'Commande creee.');
        $this->redirect('orders');
    }

    public function show(string $id): void
    {
        $order = (new Order())->findWithItems((int) $id);
        if (!$order) $this->redirect('orders');
        $this->view('orders/show', compact('order'));
    }

    public function deliver(string $id): void
    {
        Security::checkCsrf();
        (new Order())->updateStatus((int) $id, 'delivered');
        Session::flash('success', 'Commande remise au client.');
        $this->redirect('orders');
    }
}
"""

# ============================================================
#  CONTROLLERS — Preparation
# ============================================================
files["app/Controllers/PreparationController.php"] = """<?php
namespace App\\Controllers;

use App\\Core\\Controller;
use App\\Core\\Security;
use App\\Core\\Session;
use App\\Models\\Order;

class PreparationController extends Controller
{
    public function index(): void
    {
        $orderModel = new Order();
        $pending  = $orderModel->findAllByStatus('pending');
        $preparing = $orderModel->findAllByStatus('preparing');
        $ready    = $orderModel->findAllByStatus('ready');
        $orders = array_merge($pending, $preparing, $ready);
        // Trier par date croissante
        usort($orders, fn($a, $b) => $a['created_at'] <=> $b['created_at']);
        $this->view('preparation/index', compact('orders'));
    }

    public function markReady(string $id): void
    {
        Security::checkCsrf();
        $orderModel = new Order();
        $order = $orderModel->find((int) $id);
        if ($order) {
            $newStatus = match ($order['status']) {
                'pending'   => 'preparing',
                'preparing' => 'ready',
                default     => $order['status'],
            };
            $orderModel->updateStatus((int) $id, $newStatus);
        }
        Session::flash('success', 'Statut mis a jour.');
        $this->redirect('preparation');
    }
}
"""

# ============================================================
#  API CONTROLLERS
# ============================================================
files["app/Controllers/Api/ProductApiController.php"] = """<?php
namespace App\\Controllers\\Api;

use App\\Core\\Controller;
use App\\Models\\Product;

class ProductApiController extends Controller
{
    public function index(): void
    {
        $this->json((new Product())->allGroupedByCategory());
    }

    public function byCategory(string $category): void
    {
        $products = (new Product())->findByCategorySlug($category);
        $result = array_map(fn($p) => [
            'id'   => $p['id'],
            'nom'  => $p['name'],
            'prix' => (float) $p['price'],
            'image'=> $p['image'],
        ], $products);
        $this->json($result);
    }
}
"""

files["app/Controllers/Api/MenuApiController.php"] = """<?php
namespace App\\Controllers\\Api;

use App\\Core\\Controller;
use App\\Models\\Menu;

class MenuApiController extends Controller
{
    public function index(): void
    {
        $this->json((new Menu())->allForApi());
    }
}
"""

files["app/Controllers/Api/OrderApiController.php"] = """<?php
namespace App\\Controllers\\Api;

use App\\Core\\Controller;
use App\\Models\\Order;
use App\\Models\\OrderItem;

class OrderApiController extends Controller
{
    /** Reception d'une commande depuis la borne (front-end). */
    public function store(): void
    {
        $input = json_decode(file_get_contents('php://input'), true);
        if (!$input) {
            $this->json(['error' => 'JSON invalide'], 400);
        }

        $orderModel = new Order();
        $orderId = $orderModel->create([
            'order_number' => $input['orderNumber'] ?? (string) rand(100,999),
            'mode'         => $input['mode'] ?? 'sur-place',
            'status'       => 'pending',
            'chevalet'     => $input['chevalet'] ?? null,
            'total'        => (float) ($input['total'] ?? 0),
        ]);

        $itemModel = new OrderItem();
        foreach ($input['items'] ?? [] as $item) {
            $itemModel->create([
                'order_id'   => $orderId,
                'product_id' => $item['productId'] ?? null,
                'name'       => $item['name'] ?? 'Produit',
                'quantity'   => (int) ($item['quantity'] ?? 1),
                'unit_price' => (float) ($item['unitPrice'] ?? $item['totalPrice'] ?? 0),
                'options'    => json_encode($item['options'] ?? []),
            ]);
        }

        $this->json(['success' => true, 'orderId' => $orderId], 201);
    }
}
"""

# ============================================================
#  VIEWS — Layout
# ============================================================
files["app/Views/layout.php"] = """<?php
use App\\Core\\Security;
use App\\Core\\Session;
$e = fn($v) => Security::escape($v);
$_success = Session::getFlash('success');
$_error   = Session::getFlash('error');
$_role    = $_user_role ?? '';
$_uname   = $_username ?? '';
?><!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wacdo Admin<?= isset($title) ? ' — '.$e($title) : '' ?></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="<?= BASE_URL ?>/css/admin.css">
</head>
<body>
<div class="app-layout">
    <aside class="sidebar">
        <div class="sidebar-logo">
            <span class="logo-w">W</span>
            <span class="logo-text">Wacdo</span>
        </div>
        <nav class="sidebar-nav">
            <a href="<?= BASE_URL ?>/dashboard" class="nav-link">Dashboard</a>
            <?php if ($_role === 'admin'): ?>
            <a href="<?= BASE_URL ?>/products" class="nav-link">Produits</a>
            <a href="<?= BASE_URL ?>/categories" class="nav-link">Categories</a>
            <a href="<?= BASE_URL ?>/menus" class="nav-link">Menus</a>
            <?php endif; ?>
            <?php if (in_array($_role, ['admin','accueil'])): ?>
            <a href="<?= BASE_URL ?>/orders" class="nav-link">Commandes</a>
            <?php endif; ?>
            <a href="<?= BASE_URL ?>/preparation" class="nav-link">Preparation</a>
            <?php if ($_role === 'admin'): ?>
            <a href="<?= BASE_URL ?>/users" class="nav-link">Utilisateurs</a>
            <?php endif; ?>
        </nav>
        <div class="sidebar-footer">
            <span class="sidebar-user"><?= $e($_uname) ?> (<?= $e($_role) ?>)</span>
            <a href="<?= BASE_URL ?>/logout" class="nav-link logout-link">Deconnexion</a>
        </div>
    </aside>
    <main class="main-area">
        <header class="topbar">
            <h1 class="page-title"><?= $e($title ?? 'Back-office') ?></h1>
        </header>
        <?php if ($_success): ?>
        <div class="alert alert-success"><?= $e($_success) ?></div>
        <?php endif; ?>
        <?php if ($_error): ?>
        <div class="alert alert-error"><?= $e($_error) ?></div>
        <?php endif; ?>
        <div class="content-area">
            <?= $content ?>
        </div>
    </main>
</div>
<script src="<?= BASE_URL ?>/js/admin.js"></script>
</body>
</html>
"""

# ============================================================
#  VIEWS — Auth
# ============================================================
files["app/Views/auth/login.php"] = """<?php use App\\Core\\Security; ?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wacdo — Connexion</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="<?= BASE_URL ?>/css/admin.css">
</head>
<body class="login-page">
    <div class="login-box">
        <div class="login-logo"><span class="logo-w">W</span></div>
        <h1>Connexion</h1>
        <?php if (!empty($error)): ?>
            <div class="alert alert-error"><?= Security::escape($error) ?></div>
        <?php endif; ?>
        <form method="POST" action="<?= BASE_URL ?>/login">
            <?= Security::csrfField() ?>
            <div class="form-group">
                <label for="username">Nom d'utilisateur</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Mot de passe</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary btn-full">Se connecter</button>
        </form>
    </div>
</body>
</html>
"""

# ============================================================
#  VIEWS — Dashboard
# ============================================================
files["app/Views/dashboard/index.php"] = """<?php $title = 'Tableau de bord'; $e = fn($v) => \\App\\Core\\Security::escape($v); ?>
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value"><?= $stats['total'] ?></div>
        <div class="stat-label">Commandes aujourd'hui</div>
    </div>
    <div class="stat-card stat-warning">
        <div class="stat-value"><?= $stats['pending'] ?></div>
        <div class="stat-label">En attente</div>
    </div>
    <div class="stat-card stat-success">
        <div class="stat-value"><?= number_format($stats['revenue'], 2, ',', ' ') ?> &euro;</div>
        <div class="stat-label">Chiffre du jour</div>
    </div>
    <div class="stat-card">
        <div class="stat-value"><?= $stats['products'] ?></div>
        <div class="stat-label">Produits</div>
    </div>
</div>
<div class="card">
    <h2>Dernieres commandes</h2>
    <table class="table">
        <thead><tr><th>#</th><th>Numero</th><th>Mode</th><th>Statut</th><th>Total</th><th>Date</th></tr></thead>
        <tbody>
        <?php foreach ($recentOrders as $o): ?>
        <tr>
            <td><?= $o['id'] ?></td>
            <td><a href="<?= BASE_URL ?>/orders/<?= $o['id'] ?>"><?= $e($o['order_number']) ?></a></td>
            <td><?= $e($o['mode']) ?></td>
            <td><span class="badge badge-<?= $o['status'] ?>"><?= $e($o['status']) ?></span></td>
            <td><?= number_format((float)$o['total'], 2, ',', ' ') ?> &euro;</td>
            <td><?= $o['created_at'] ?></td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
"""

# ============================================================
#  VIEWS — Users
# ============================================================
files["app/Views/users/index.php"] = """<?php $title = 'Utilisateurs'; $e = fn($v) => \\App\\Core\\Security::escape($v); ?>
<div class="card">
    <div class="card-header">
        <h2>Utilisateurs</h2>
        <a href="<?= BASE_URL ?>/users/create" class="btn btn-primary">+ Nouveau</a>
    </div>
    <table class="table">
        <thead><tr><th>ID</th><th>Nom</th><th>Email</th><th>Role</th><th>Actif</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($users as $u): ?>
        <tr>
            <td><?= $u['id'] ?></td>
            <td><?= $e($u['username']) ?></td>
            <td><?= $e($u['email']) ?></td>
            <td><span class="badge badge-<?= $u['role'] ?>"><?= $e($u['role']) ?></span></td>
            <td><?= $u['active'] ? 'Oui' : 'Non' ?></td>
            <td class="actions">
                <a href="<?= BASE_URL ?>/users/<?= $u['id'] ?>/edit" class="btn btn-sm">Modifier</a>
                <form method="POST" action="<?= BASE_URL ?>/users/<?= $u['id'] ?>/delete" class="inline-form">
                    <?= \\App\\Core\\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Supprimer ?')">Supprimer</button>
                </form>
            </td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
"""

files["app/Views/users/form.php"] = """<?php
$title = $user ? 'Modifier utilisateur' : 'Nouvel utilisateur';
$e = fn($v) => \\App\\Core\\Security::escape($v);
$action = $user ? BASE_URL.'/users/'.$user['id'] : BASE_URL.'/users';
?>
<div class="card">
    <h2><?= $e($title) ?></h2>
    <form method="POST" action="<?= $action ?>">
        <?= \\App\\Core\\Security::csrfField() ?>
        <div class="form-group">
            <label>Nom d'utilisateur</label>
            <input type="text" name="username" value="<?= $e($user['username'] ?? '') ?>" required>
        </div>
        <div class="form-group">
            <label>Email</label>
            <input type="email" name="email" value="<?= $e($user['email'] ?? '') ?>" required>
        </div>
        <div class="form-group">
            <label>Mot de passe<?= $user ? ' (laisser vide pour ne pas changer)' : '' ?></label>
            <input type="password" name="password" <?= $user ? '' : 'required' ?>>
        </div>
        <div class="form-group">
            <label>Role</label>
            <select name="role">
                <?php foreach (['admin','preparation','accueil'] as $r): ?>
                <option value="<?= $r ?>" <?= ($user['role'] ?? '') === $r ? 'selected' : '' ?>><?= ucfirst($r) ?></option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="active" value="1" <?= ($user['active'] ?? 1) ? 'checked' : '' ?>> Actif</label>
        </div>
        <button type="submit" class="btn btn-primary">Enregistrer</button>
        <a href="<?= BASE_URL ?>/users" class="btn">Annuler</a>
    </form>
</div>
"""

# ============================================================
#  VIEWS — Products
# ============================================================
files["app/Views/products/index.php"] = """<?php $title = 'Produits'; $e = fn($v) => \\App\\Core\\Security::escape($v); ?>
<div class="card">
    <div class="card-header">
        <h2>Produits</h2>
        <a href="<?= BASE_URL ?>/products/create" class="btn btn-primary">+ Nouveau</a>
    </div>
    <table class="table">
        <thead><tr><th>ID</th><th>Nom</th><th>Categorie</th><th>Prix</th><th>Dispo</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($products as $p): ?>
        <tr>
            <td><?= $p['id'] ?></td>
            <td><?= $e($p['name']) ?></td>
            <td><?= $e($p['category_name']) ?></td>
            <td><?= number_format((float)$p['price'], 2, ',', ' ') ?> &euro;</td>
            <td><?= $p['available'] ? 'Oui' : 'Non' ?></td>
            <td class="actions">
                <a href="<?= BASE_URL ?>/products/<?= $p['id'] ?>/edit" class="btn btn-sm">Modifier</a>
                <form method="POST" action="<?= BASE_URL ?>/products/<?= $p['id'] ?>/delete" class="inline-form">
                    <?= \\App\\Core\\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Supprimer ?')">Supprimer</button>
                </form>
            </td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
"""

files["app/Views/products/form.php"] = """<?php
$title = $product ? 'Modifier produit' : 'Nouveau produit';
$e = fn($v) => \\App\\Core\\Security::escape($v);
$action = $product ? BASE_URL.'/products/'.$product['id'] : BASE_URL.'/products';
?>
<div class="card">
    <h2><?= $e($title) ?></h2>
    <form method="POST" action="<?= $action ?>" enctype="multipart/form-data">
        <?= \\App\\Core\\Security::csrfField() ?>
        <div class="form-group">
            <label>Nom</label>
            <input type="text" name="name" value="<?= $e($product['name'] ?? '') ?>" required>
        </div>
        <div class="form-group">
            <label>Categorie</label>
            <select name="category_id" required>
                <option value="">-- Choisir --</option>
                <?php foreach ($categories as $c): ?>
                <option value="<?= $c['id'] ?>" <?= ($product['category_id'] ?? 0) == $c['id'] ? 'selected' : '' ?>><?= $e($c['name']) ?></option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Prix (&euro;)</label>
                <input type="number" step="0.01" name="price" value="<?= $product['price'] ?? '' ?>" required>
            </div>
            <div class="form-group">
                <label>Image (chemin)</label>
                <input type="text" name="image" value="<?= $e($product['image'] ?? '') ?>">
            </div>
        </div>
        <div class="form-group">
            <label>Ou uploader une image</label>
            <input type="file" name="image_file" accept="image/*">
        </div>
        <div class="form-group">
            <label>Description</label>
            <textarea name="description" rows="3"><?= $e($product['description'] ?? '') ?></textarea>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="available" value="1" <?= ($product['available'] ?? 1) ? 'checked' : '' ?>> Disponible</label>
        </div>
        <button type="submit" class="btn btn-primary">Enregistrer</button>
        <a href="<?= BASE_URL ?>/products" class="btn">Annuler</a>
    </form>
</div>
"""

# ============================================================
#  VIEWS — Categories
# ============================================================
files["app/Views/categories/index.php"] = """<?php $title = 'Categories'; $e = fn($v) => \\App\\Core\\Security::escape($v); ?>
<div class="card">
    <div class="card-header">
        <h2>Categories</h2>
        <a href="<?= BASE_URL ?>/categories/create" class="btn btn-primary">+ Nouvelle</a>
    </div>
    <table class="table">
        <thead><tr><th>Ordre</th><th>Nom</th><th>Slug</th><th>Icone</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($categories as $c): ?>
        <tr>
            <td><?= $c['display_order'] ?></td>
            <td><?= $e($c['name']) ?></td>
            <td><code><?= $e($c['slug']) ?></code></td>
            <td><?= $e($c['icon'] ?? '-') ?></td>
            <td class="actions">
                <a href="<?= BASE_URL ?>/categories/<?= $c['id'] ?>/edit" class="btn btn-sm">Modifier</a>
                <form method="POST" action="<?= BASE_URL ?>/categories/<?= $c['id'] ?>/delete" class="inline-form">
                    <?= \\App\\Core\\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Supprimer ?')">Supprimer</button>
                </form>
            </td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
"""

files["app/Views/categories/form.php"] = """<?php
$title = $category ? 'Modifier categorie' : 'Nouvelle categorie';
$e = fn($v) => \\App\\Core\\Security::escape($v);
$action = $category ? BASE_URL.'/categories/'.$category['id'] : BASE_URL.'/categories';
?>
<div class="card">
    <h2><?= $e($title) ?></h2>
    <form method="POST" action="<?= $action ?>">
        <?= \\App\\Core\\Security::csrfField() ?>
        <div class="form-group">
            <label>Nom</label>
            <input type="text" name="name" value="<?= $e($category['name'] ?? '') ?>" required>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Icone (fichier)</label>
                <input type="text" name="icon" value="<?= $e($category['icon'] ?? '') ?>">
            </div>
            <div class="form-group">
                <label>Ordre d'affichage</label>
                <input type="number" name="display_order" value="<?= $category['display_order'] ?? 0 ?>">
            </div>
        </div>
        <button type="submit" class="btn btn-primary">Enregistrer</button>
        <a href="<?= BASE_URL ?>/categories" class="btn">Annuler</a>
    </form>
</div>
"""

# ============================================================
#  VIEWS — Menus
# ============================================================
files["app/Views/menus/index.php"] = """<?php $title = 'Menus'; $e = fn($v) => \\App\\Core\\Security::escape($v); ?>
<div class="card">
    <div class="card-header">
        <h2>Menus</h2>
        <a href="<?= BASE_URL ?>/menus/create" class="btn btn-primary">+ Nouveau</a>
    </div>
    <table class="table">
        <thead><tr><th>ID</th><th>Nom</th><th>Prix de base</th><th>Dispo</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($menus as $m): ?>
        <tr>
            <td><?= $m['id'] ?></td>
            <td><?= $e($m['name']) ?></td>
            <td><?= number_format((float)$m['base_price'], 2, ',', ' ') ?> &euro;</td>
            <td><?= $m['available'] ? 'Oui' : 'Non' ?></td>
            <td class="actions">
                <a href="<?= BASE_URL ?>/menus/<?= $m['id'] ?>/edit" class="btn btn-sm">Modifier</a>
                <form method="POST" action="<?= BASE_URL ?>/menus/<?= $m['id'] ?>/delete" class="inline-form">
                    <?= \\App\\Core\\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Supprimer ?')">Supprimer</button>
                </form>
            </td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
"""

files["app/Views/menus/form.php"] = """<?php
$title = $menu ? 'Modifier menu' : 'Nouveau menu';
$e = fn($v) => \\App\\Core\\Security::escape($v);
$action = $menu ? BASE_URL.'/menus/'.$menu['id'] : BASE_URL.'/menus';
?>
<div class="card">
    <h2><?= $e($title) ?></h2>
    <form method="POST" action="<?= $action ?>">
        <?= \\App\\Core\\Security::csrfField() ?>
        <div class="form-group">
            <label>Nom</label>
            <input type="text" name="name" value="<?= $e($menu['name'] ?? '') ?>" required>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Prix de base (&euro;)</label>
                <input type="number" step="0.01" name="base_price" value="<?= $menu['base_price'] ?? '' ?>" required>
            </div>
            <div class="form-group">
                <label>Image (chemin)</label>
                <input type="text" name="image" value="<?= $e($menu['image'] ?? '') ?>">
            </div>
        </div>
        <div class="form-group">
            <label>Description</label>
            <textarea name="description" rows="3"><?= $e($menu['description'] ?? '') ?></textarea>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="available" value="1" <?= ($menu['available'] ?? 1) ? 'checked' : '' ?>> Disponible</label>
        </div>
        <h3>Composition du menu</h3>
        <p class="hint">Selectionnez les produits disponibles pour chaque type :</p>
        <?php
        $types = ['burger' => 'Burgers', 'side' => 'Accompagnements', 'drink' => 'Boissons', 'sauce' => 'Sauces'];
        $existingComps = [];
        foreach ($compositions ?? [] as $comp) {
            $existingComps[$comp['type']][] = $comp['product_id'];
        }
        foreach ($types as $type => $label): ?>
        <div class="form-group">
            <label><?= $label ?></label>
            <select name="comp_<?= $type ?>[]" multiple class="multi-select">
                <?php foreach ($products as $p): ?>
                <option value="<?= $p['id'] ?>"
                    <?= in_array($p['id'], $existingComps[$type] ?? []) ? 'selected' : '' ?>>
                    <?= $e($p['name']) ?> (<?= $e($p['category_name'] ?? '') ?>)
                </option>
                <?php endforeach; ?>
            </select>
        </div>
        <?php endforeach; ?>
        <button type="submit" class="btn btn-primary">Enregistrer</button>
        <a href="<?= BASE_URL ?>/menus" class="btn">Annuler</a>
    </form>
</div>
"""

# ============================================================
#  VIEWS — Orders
# ============================================================
files["app/Views/orders/index.php"] = """<?php $title = 'Commandes'; $e = fn($v) => \\App\\Core\\Security::escape($v); ?>
<div class="card">
    <div class="card-header">
        <h2>Commandes</h2>
        <a href="<?= BASE_URL ?>/orders/create" class="btn btn-primary">+ Saisir commande</a>
    </div>
    <table class="table">
        <thead><tr><th>#</th><th>Numero</th><th>Mode</th><th>Statut</th><th>Total</th><th>Date</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($orders as $o): ?>
        <tr>
            <td><?= $o['id'] ?></td>
            <td><a href="<?= BASE_URL ?>/orders/<?= $o['id'] ?>"><?= $e($o['order_number']) ?></a></td>
            <td><?= $e($o['mode']) ?></td>
            <td><span class="badge badge-<?= $o['status'] ?>"><?= $e($o['status']) ?></span></td>
            <td><?= number_format((float)$o['total'], 2, ',', ' ') ?> &euro;</td>
            <td><?= $o['created_at'] ?></td>
            <td class="actions">
                <a href="<?= BASE_URL ?>/orders/<?= $o['id'] ?>" class="btn btn-sm">Voir</a>
                <?php if ($o['status'] === 'ready'): ?>
                <form method="POST" action="<?= BASE_URL ?>/orders/<?= $o['id'] ?>/deliver" class="inline-form">
                    <?= \\App\\Core\\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-success">Remettre</button>
                </form>
                <?php endif; ?>
            </td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
"""

files["app/Views/orders/create.php"] = """<?php
$title = 'Saisir une commande';
$e = fn($v) => \\App\\Core\\Security::escape($v);
?>
<div class="card">
    <h2>Nouvelle commande (comptoir / telephone)</h2>
    <form method="POST" action="<?= BASE_URL ?>/orders" id="order-form">
        <?= \\App\\Core\\Security::csrfField() ?>
        <div class="form-row">
            <div class="form-group">
                <label>Numero de commande</label>
                <input type="text" name="order_number" value="<?= rand(100,999) ?>" required>
            </div>
            <div class="form-group">
                <label>Mode</label>
                <select name="mode">
                    <option value="sur-place">Sur place</option>
                    <option value="a-emporter">A emporter</option>
                </select>
            </div>
        </div>
        <h3>Articles</h3>
        <div id="items-container">
            <div class="item-row form-row">
                <div class="form-group" style="flex:2"><input type="text" name="item_name[]" placeholder="Nom du produit"></div>
                <div class="form-group"><input type="number" name="item_qty[]" value="1" min="1" placeholder="Qte"></div>
                <div class="form-group"><input type="number" step="0.01" name="item_price[]" placeholder="Prix unitaire"></div>
            </div>
        </div>
        <button type="button" class="btn" onclick="addItemRow()">+ Ajouter un article</button>
        <hr>
        <button type="submit" class="btn btn-primary">Enregistrer la commande</button>
        <a href="<?= BASE_URL ?>/orders" class="btn">Annuler</a>
    </form>
</div>
<script>
function addItemRow() {
    const c = document.getElementById('items-container');
    const row = document.createElement('div');
    row.className = 'item-row form-row';
    row.innerHTML = '<div class="form-group" style="flex:2"><input type="text" name="item_name[]" placeholder="Nom du produit"></div>'
        + '<div class="form-group"><input type="number" name="item_qty[]" value="1" min="1" placeholder="Qte"></div>'
        + '<div class="form-group"><input type="number" step="0.01" name="item_price[]" placeholder="Prix unitaire"></div>';
    c.appendChild(row);
}
</script>
"""

files["app/Views/orders/show.php"] = """<?php
$title = 'Commande #' . ($order['order_number'] ?? '');
$e = fn($v) => \\App\\Core\\Security::escape($v);
?>
<div class="card">
    <h2>Commande n&deg;<?= $e($order['order_number']) ?></h2>
    <div class="info-grid">
        <div><strong>Mode :</strong> <?= $e($order['mode']) ?></div>
        <div><strong>Statut :</strong> <span class="badge badge-<?= $order['status'] ?>"><?= $e($order['status']) ?></span></div>
        <div><strong>Chevalet :</strong> <?= $order['chevalet'] ?? '-' ?></div>
        <div><strong>Total :</strong> <?= number_format((float)$order['total'], 2, ',', ' ') ?> &euro;</div>
        <div><strong>Date :</strong> <?= $order['created_at'] ?></div>
    </div>
    <h3>Articles</h3>
    <table class="table">
        <thead><tr><th>Produit</th><th>Quantite</th><th>Prix unitaire</th><th>Sous-total</th></tr></thead>
        <tbody>
        <?php foreach ($order['items'] as $item): ?>
        <tr>
            <td><?= $e($item['name']) ?></td>
            <td><?= $item['quantity'] ?></td>
            <td><?= number_format((float)$item['unit_price'], 2, ',', ' ') ?> &euro;</td>
            <td><?= number_format((float)$item['unit_price'] * $item['quantity'], 2, ',', ' ') ?> &euro;</td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
    <?php if ($order['status'] === 'ready'): ?>
    <form method="POST" action="<?= BASE_URL ?>/orders/<?= $order['id'] ?>/deliver">
        <?= \\App\\Core\\Security::csrfField() ?>
        <button type="submit" class="btn btn-success">Marquer comme remise au client</button>
    </form>
    <?php endif; ?>
    <a href="<?= BASE_URL ?>/orders" class="btn">Retour</a>
</div>
"""

# ============================================================
#  VIEWS — Preparation
# ============================================================
files["app/Views/preparation/index.php"] = """<?php $title = 'Preparation des commandes'; $e = fn($v) => \\App\\Core\\Security::escape($v); ?>
<div class="card">
    <h2>File de preparation</h2>
    <p class="hint">Les commandes sont triees par heure croissante.</p>
    <?php if (empty($orders)): ?>
    <p class="empty-msg">Aucune commande en attente.</p>
    <?php else: ?>
    <div class="prep-grid">
        <?php foreach ($orders as $o): ?>
        <div class="prep-card prep-<?= $o['status'] ?>">
            <div class="prep-header">
                <strong>#<?= $e($o['order_number']) ?></strong>
                <span class="badge badge-<?= $o['status'] ?>"><?= $e($o['status']) ?></span>
            </div>
            <div class="prep-info">
                <span><?= $e($o['mode']) ?></span>
                <?php if ($o['chevalet']): ?><span>Chevalet: <?= $o['chevalet'] ?></span><?php endif; ?>
                <span><?= number_format((float)$o['total'], 2, ',', ' ') ?> &euro;</span>
                <span class="prep-time"><?= date('H:i', strtotime($o['created_at'])) ?></span>
            </div>
            <?php if ($o['status'] !== 'ready'): ?>
            <form method="POST" action="<?= BASE_URL ?>/preparation/<?= $o['id'] ?>/ready">
                <?= \\App\\Core\\Security::csrfField() ?>
                <button type="submit" class="btn btn-success btn-full">
                    <?= $o['status'] === 'pending' ? 'Commencer' : 'Prete' ?>
                </button>
            </form>
            <?php else: ?>
            <div class="prep-done">Prete — en attente de remise</div>
            <?php endif; ?>
        </div>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>
</div>
"""

# ============================================================
#  PUBLIC — CSS
# ============================================================
files["public/css/admin.css"] = """/* =============================================
   Wacdo Back-Office — Admin Styles
   Police Inter · Jaune #FFC72C · Vert #27AE60
   ============================================= */
:root {
    --yellow: #FFC72C;
    --green: #27AE60;
    --red: #E74C3C;
    --dark: #222222;
    --gray: #6c757d;
    --light: #f5f5f5;
    --white: #ffffff;
    --sidebar-w: 240px;
    --radius: 8px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', sans-serif; background: var(--light); color: var(--dark); font-size: 14px; }

/* Layout */
.app-layout { display: flex; min-height: 100vh; }
.sidebar { width: var(--sidebar-w); background: var(--dark); color: var(--white); display: flex; flex-direction: column; position: fixed; top: 0; left: 0; height: 100vh; z-index: 100; }
.sidebar-logo { padding: 24px 20px; text-align: center; border-bottom: 2px solid var(--yellow); }
.logo-w { color: var(--yellow); font-size: 32px; font-weight: 700; }
.logo-text { color: var(--yellow); font-size: 18px; font-weight: 600; margin-left: 4px; }
.sidebar-nav { flex: 1; padding: 16px 0; display: flex; flex-direction: column; gap: 2px; }
.nav-link { display: block; padding: 12px 24px; color: #ccc; text-decoration: none; font-weight: 500; transition: all .2s; border-left: 3px solid transparent; }
.nav-link:hover, .nav-link.active { color: var(--white); background: rgba(255,255,255,.08); border-left-color: var(--yellow); }
.sidebar-footer { padding: 16px 20px; border-top: 1px solid rgba(255,255,255,.1); font-size: 12px; }
.sidebar-user { display: block; margin-bottom: 8px; color: #aaa; }
.logout-link { color: var(--red) !important; font-size: 13px; }
.main-area { margin-left: var(--sidebar-w); flex: 1; display: flex; flex-direction: column; }
.topbar { background: var(--white); padding: 16px 32px; border-bottom: 3px solid var(--yellow); }
.page-title { font-size: 20px; font-weight: 700; }
.content-area { padding: 24px 32px; flex: 1; }

/* Cards */
.card { background: var(--white); border-radius: var(--radius); box-shadow: 0 1px 4px rgba(0,0,0,.08); padding: 24px; margin-bottom: 24px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.card-header h2 { margin: 0; font-size: 18px; }

/* Tables */
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }
.table th { font-weight: 600; color: var(--gray); font-size: 12px; text-transform: uppercase; letter-spacing: .5px; }
.table tr:hover { background: #fafafa; }
.actions { display: flex; gap: 6px; align-items: center; }
.inline-form { display: inline; }

/* Buttons */
.btn { display: inline-block; padding: 8px 16px; border: 1px solid #ddd; border-radius: var(--radius); font-size: 13px; font-weight: 500; cursor: pointer; text-decoration: none; color: var(--dark); background: var(--white); transition: all .2s; font-family: inherit; }
.btn:hover { background: #f0f0f0; }
.btn-primary { background: var(--yellow); color: var(--dark); border-color: var(--yellow); }
.btn-primary:hover { background: #e6b326; }
.btn-success { background: var(--green); color: var(--white); border-color: var(--green); }
.btn-success:hover { background: #219653; }
.btn-danger { background: var(--red); color: var(--white); border-color: var(--red); }
.btn-danger:hover { background: #c0392b; }
.btn-sm { padding: 4px 10px; font-size: 12px; }
.btn-full { width: 100%; text-align: center; }

/* Forms */
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-weight: 500; margin-bottom: 6px; font-size: 13px; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: var(--radius); font-size: 14px; font-family: inherit; transition: border-color .2s; }
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: var(--yellow); box-shadow: 0 0 0 3px rgba(255,199,44,.2); }
.form-row { display: flex; gap: 16px; }
.form-row .form-group { flex: 1; }
.multi-select { height: 120px; }

/* Alerts */
.alert { padding: 12px 24px; margin: 16px 32px 0; border-radius: var(--radius); font-weight: 500; }
.alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

/* Badges */
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .3px; }
.badge-pending    { background: #fff3cd; color: #856404; }
.badge-preparing  { background: #cce5ff; color: #004085; }
.badge-ready      { background: #d4edda; color: #155724; }
.badge-delivered  { background: #e2e3e5; color: #383d41; }
.badge-cancelled  { background: #f8d7da; color: #721c24; }
.badge-admin      { background: var(--yellow); color: var(--dark); }
.badge-preparation{ background: #cce5ff; color: #004085; }
.badge-accueil    { background: #d4edda; color: #155724; }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--white); border-radius: var(--radius); padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,.08); border-left: 4px solid var(--yellow); }
.stat-card.stat-warning { border-left-color: #f39c12; }
.stat-card.stat-success { border-left-color: var(--green); }
.stat-value { font-size: 28px; font-weight: 700; }
.stat-label { font-size: 13px; color: var(--gray); margin-top: 4px; }

/* Info grid */
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 24px; padding: 16px; background: var(--light); border-radius: var(--radius); }

/* Preparation */
.prep-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.prep-card { background: var(--white); border-radius: var(--radius); padding: 16px; border: 2px solid #eee; transition: border-color .2s; }
.prep-pending   { border-color: #f39c12; }
.prep-preparing { border-color: #3498db; }
.prep-ready     { border-color: var(--green); }
.prep-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 16px; }
.prep-info { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; font-size: 13px; color: var(--gray); }
.prep-time { font-weight: 600; color: var(--dark); }
.prep-done { text-align: center; padding: 8px; background: #d4edda; border-radius: var(--radius); color: #155724; font-weight: 500; }
.empty-msg { text-align: center; padding: 40px; color: var(--gray); }
.hint { font-size: 13px; color: var(--gray); margin-bottom: 12px; }
hr { border: none; border-top: 1px solid #eee; margin: 16px 0; }

/* Login */
.login-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: var(--dark); }
.login-box { background: var(--white); padding: 40px; border-radius: 12px; width: 100%; max-width: 400px; box-shadow: 0 8px 32px rgba(0,0,0,.3); }
.login-box .login-logo { text-align: center; margin-bottom: 24px; }
.login-box .login-logo .logo-w { font-size: 48px; }
.login-box h1 { text-align: center; font-size: 22px; margin-bottom: 24px; }
.login-box .alert { margin: 0 0 16px; }

/* Responsive */
@media (max-width: 768px) {
    .sidebar { display: none; }
    .main-area { margin-left: 0; }
    .content-area { padding: 16px; }
    .form-row { flex-direction: column; gap: 0; }
}
"""

# ============================================================
#  PUBLIC — JS
# ============================================================
files["public/js/admin.js"] = """/**
 * Wacdo Back-Office — JavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss les alertes apres 4 secondes
    document.querySelectorAll('.alert').forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.3s';
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 300);
        }, 4000);
    });

    // Marquer le lien actif dans la sidebar
    var path = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(function(link) {
        if (path.indexOf(link.getAttribute('href')) !== -1 && link.getAttribute('href') !== '#') {
            link.classList.add('active');
        }
    });
});
"""

# ============================================================
#  README
# ============================================================
files["README.md"] = """# Wacdo Back-Office (Bloc 2)

## Architecture
- **Langage** : PHP 8+ (POO, heritage, interfaces)
- **Architecture** : MVC (Models / Views / Controllers)
- **Base de donnees** : MySQL / MariaDB
- **Autoloading** : PSR-4 (manuel)
- **Securite** : CSRF, XSS, bcrypt, PDO prepare

## Installation

1. **Creer la base de donnees** :
   ```bash
   php setup.php
   ```

2. **Configurer Apache** : le dossier `public/` est le document root.
   Assurez-vous que `mod_rewrite` est active.

3. **Acces** : http://localhost/wacdo_lynna/wacdo_back/public/login

## Comptes par defaut
| Utilisateur | Mot de passe | Role |
|-------------|-------------|------|
| admin | Wacdo2024! | Administration |
| preparation | Wacdo2024! | Preparation |
| accueil | Wacdo2024! | Accueil |

## API REST
| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/produits | Liste des produits par categorie |
| GET | /api/produits/{categorie} | Produits d'une categorie |
| GET | /api/menus | Liste des menus |
| POST | /api/commande | Recevoir une commande (JSON) |

## Structure
```
app/
  Controllers/   - Controleurs (logique metier)
  Models/        - Modeles (acces donnees)
  Views/         - Vues (templates PHP)
  Core/          - Framework (Router, DB, Session, Security)
config/          - Configuration
routes/          - Definitions des routes
public/          - Point d'entree (index.php, CSS, JS)
sql/             - Schema et donnees initiales
```

## Base de donnees
- **users** : utilisateurs internes (admin, preparation, accueil)
- **categories** : categories de produits
- **products** : produits avec prix et images
- **menus** : menus avec composition
- **menu_compositions** : liaison menu-produits
- **orders** : commandes avec statut
- **order_items** : articles d'une commande
- **security_logs** : journal de securite
"""

# ============================================================
#  WRITE ALL FILES
# ============================================================
for path, content in files.items():
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    text = content.lstrip('\n')
    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)
    lines = text.count('\n') + 1
    print(f"  \u2713 {path} ({lines} lines)")

print(f"\n  All {len(files)} files written successfully!")
