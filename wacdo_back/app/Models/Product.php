<?php
namespace App\Models;

use App\Core\Model;

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
