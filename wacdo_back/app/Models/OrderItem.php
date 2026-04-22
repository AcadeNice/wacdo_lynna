<?php
namespace App\Models;

use App\Core\Model;

class OrderItem extends Model
{
    protected string $table = 'order_items';
    protected array $fillable = ['order_id', 'product_id', 'menu_id', 'name', 'quantity', 'unit_price', 'options'];

    public function deleteByOrderId(int $orderId): void
    {
        $this->db->query("DELETE FROM order_items WHERE order_id = ?", [$orderId]);
    }
}
