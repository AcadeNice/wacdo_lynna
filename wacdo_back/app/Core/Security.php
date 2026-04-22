<?php
namespace App\Core;

/**
 * Securite : CSRF, XSS, sanitisation.
 */
class Security
{
    /** Genere un jeton CSRF et le stocke en session. */
    public static function generateCsrfToken(): string
    {
        // Retourner le token existant pour éviter les regenerations multiples
        $existing = Session::get('csrf_token');
        if ($existing) {
            return $existing;
        }
        
        // Générer un nouveau token seulement s'il n'existe pas
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
