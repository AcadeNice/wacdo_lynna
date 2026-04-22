<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Core\Session;
use App\Core\Security;
use App\Models\User;

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
            $db = \App\Core\Database::getInstance();
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
        $db = \App\Core\Database::getInstance();
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
