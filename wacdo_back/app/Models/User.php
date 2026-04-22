<?php
namespace App\Models;

use App\Core\Model;

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
