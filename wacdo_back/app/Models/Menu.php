<?php
namespace App\Models;

use App\Core\Model;

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
