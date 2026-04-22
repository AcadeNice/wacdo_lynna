<?php
namespace App\Core;

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
