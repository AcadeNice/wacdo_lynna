<?php
namespace App\Models;

use App\Core\Model;

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
