<?php
namespace App\Models;

use App\Core\Model;

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
        $order['history'] = $this->getHistory($id);
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

    /** Retourne les items d'une commande. */
    public function getItems(int $orderId): array
    {
        return $this->db->fetchAll(
            "SELECT * FROM order_items WHERE order_id = ? ORDER BY id ASC", [$orderId]
        );
    }

    public function logHistory(int $orderId, string $action, array $payload = [], ?int $userId = null): void
    {
        $details = json_encode(array_merge(['order_id' => $orderId], $payload), JSON_UNESCAPED_UNICODE);
        $this->db->query(
            "INSERT INTO security_logs (user_id, action, details, ip_address, user_agent) VALUES (?, ?, ?, ?, ?)",
            [
                $userId,
                $action,
                $details,
                $_SERVER['REMOTE_ADDR'] ?? '',
                substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 500),
            ]
        );
    }

    public function getHistory(int $orderId): array
    {
        return $this->db->fetchAll(
            "SELECT action, details, created_at, user_id
             FROM security_logs
             WHERE action IN ('order_created', 'order_updated', 'order_deleted', 'order_delivered')
               AND details LIKE ?
             ORDER BY created_at DESC",
            ['%\"order_id\":' . (int) $orderId . '%']
        );
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
