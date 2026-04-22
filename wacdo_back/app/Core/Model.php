<?php
namespace App\Core;

/**
 * Classe de base pour tous les modeles.
 * Fournit les operations CRUD via PDO (requetes preparees).
 */
abstract class Model
{
    protected string $table;
    protected string $primaryKey = 'id';
    protected array $fillable = [];
    protected Database $db;

    public function __construct()
    {
        $this->db = Database::getInstance();
    }

    public function find(int $id): ?array
    {
        return $this->db->fetch(
            "SELECT * FROM {$this->table} WHERE {$this->primaryKey} = ?", [$id]
        );
    }

    public function findAll(string $orderBy = 'id ASC'): array
    {
        return $this->db->fetchAll("SELECT * FROM {$this->table} ORDER BY {$orderBy}");
    }

    public function findBy(string $column, mixed $value): ?array
    {
        return $this->db->fetch(
            "SELECT * FROM {$this->table} WHERE {$column} = ?", [$value]
        );
    }

    public function findAllBy(string $column, mixed $value, string $orderBy = 'id ASC'): array
    {
        return $this->db->fetchAll(
            "SELECT * FROM {$this->table} WHERE {$column} = ? ORDER BY {$orderBy}",
            [$value]
        );
    }

    public function create(array $data): int
    {
        $filtered = array_intersect_key($data, array_flip($this->fillable));
        $cols = implode(', ', array_keys($filtered));
        $ph   = implode(', ', array_fill(0, count($filtered), '?'));
        $this->db->query("INSERT INTO {$this->table} ({$cols}) VALUES ({$ph})", array_values($filtered));
        return (int) $this->db->lastInsertId();
    }

    public function update(int $id, array $data): bool
    {
        $filtered = array_intersect_key($data, array_flip($this->fillable));
        if (empty($filtered)) return false;
        $set = implode(', ', array_map(fn($c) => "{$c} = ?", array_keys($filtered)));
        $vals = array_values($filtered);
        $vals[] = $id;
        $this->db->query("UPDATE {$this->table} SET {$set} WHERE {$this->primaryKey} = ?", $vals);
        return true;
    }

    public function delete(int $id): bool
    {
        $this->db->query("DELETE FROM {$this->table} WHERE {$this->primaryKey} = ?", [$id]);
        return true;
    }

    public function count(): int
    {
        $r = $this->db->fetch("SELECT COUNT(*) as total FROM {$this->table}");
        return (int) ($r['total'] ?? 0);
    }

    public function countBy(string $column, mixed $value): int
    {
        $r = $this->db->fetch("SELECT COUNT(*) as total FROM {$this->table} WHERE {$column} = ?", [$value]);
        return (int) ($r['total'] ?? 0);
    }
}
