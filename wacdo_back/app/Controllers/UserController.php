<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Core\Security;
use App\Core\Session;
use App\Models\User;

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
