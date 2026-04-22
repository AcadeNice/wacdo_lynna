<?php
namespace App\Controllers\Api;

use App\Core\Controller;
use App\Core\Database;
use App\Models\Order;
use App\Models\OrderItem;

/**
 * API REST — Reception des commandes depuis la borne (front-end).
 *
 * Endpoint : POST /api/commande
 * Content-Type : application/json
 *
 * Corps attendu :
 * {
 *   "orderNumber": "123",
 *   "mode": "sur-place" | "a-emporter",
 *   "chevalet": 42,          // optionnel (sur-place uniquement)
 *   "total": 15.80,
 *   "items": [
 *     {
 *       "productId": 3,
 *       "name": "Big Mac",
 *       "category": "burgers",
 *       "quantity": 2,
 *       "unitPrice": 5.50,
 *       "totalPrice": 11.00,
 *       "options": { "size": "Grand" }
 *     }
 *   ]
 * }
 *
 * Reponse 201 : { "success": true, "orderId": 5, "orderNumber": "123" }
 * Reponse 400 : { "error": "..." }
 * Reponse 500 : { "error": "Erreur interne" }
 */
class OrderApiController extends Controller
{
    /** Retourne les commandes recentes (diagnostic integration). */
    public function recentOrders(): void
    {
        try {
            header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
            header('Pragma: no-cache');
            header('Expires: 0');

            $rows = Database::getInstance()->fetchAll(
                "SELECT id, order_number, mode, status, chevalet, total, created_at
                 FROM orders
                 ORDER BY id DESC
                 LIMIT 50"
            );
            $this->json(['orders' => $rows]);
        } catch (\Throwable $e) {
            error_log('API /api/commandes/recentes — Erreur : ' . $e->getMessage());
            $this->json(['error' => 'Erreur interne du serveur.'], 500);
        }
    }

    /** Liste les numeros de chevalets actuellement occupes. */
    public function occupiedChevalets(): void
    {
        try {
            $pdo = Database::getInstance()->getPdo();
            $rows = $pdo->query(
                "SELECT chevalet FROM orders
                 WHERE mode = 'sur-place'
                   AND chevalet IS NOT NULL
                   AND status IN ('pending', 'preparing', 'ready')"
            )->fetchAll(\PDO::FETCH_ASSOC);

            $chevalets = array_values(array_unique(array_map(
                static fn(array $row): int => (int) $row['chevalet'],
                $rows
            )));

            sort($chevalets);

            $this->json(['chevalets' => $chevalets]);
        } catch (\Throwable $e) {
            error_log('API /api/chevalets/occupes — Erreur : ' . $e->getMessage());
            $this->json(['error' => 'Erreur interne du serveur.'], 500);
        }
    }

    /** Reception et validation d'une commande. */
    public function store(): void
    {
        // --- 1. Lecture et decodage du JSON ---
        $raw = file_get_contents('php://input');
        $input = json_decode($raw, true);

        error_log('API /api/commande — Payload recu: ' . substr((string) $raw, 0, 1000));

        if (!$input || !is_array($input)) {
            $this->json(['error' => 'JSON invalide ou corps vide.'], 400);
            return;
        }

        // --- 2. Validation des champs obligatoires ---
        $errors = [];

        // Mode : doit etre 'sur-place' ou 'a-emporter'
        $mode = $input['mode'] ?? '';
        if (!in_array($mode, ['sur-place', 'a-emporter'], true)) {
            $errors[] = 'Le champ "mode" doit valoir "sur-place" ou "a-emporter".';
        }

        // Total : nombre positif
        $total = isset($input['total']) ? (float) $input['total'] : -1;
        if ($total < 0) {
            $errors[] = 'Le champ "total" doit etre un nombre positif.';
        }

        // Items : tableau non vide
        $items = $input['items'] ?? [];
        if (!is_array($items) || count($items) === 0) {
            $errors[] = 'La commande doit contenir au moins un article.';
        }

        // Validation de chaque item
        foreach ($items as $i => $item) {
            $idx = $i + 1;
            if (empty($item['name']) || !is_string($item['name'])) {
                $errors[] = "Article #{$idx} : le champ \"name\" est requis.";
            }
            if (!isset($item['quantity']) || (int) $item['quantity'] < 1) {
                $errors[] = "Article #{$idx} : la quantite doit etre >= 1.";
            }
            if (!isset($item['unitPrice']) && !isset($item['totalPrice'])) {
                $errors[] = "Article #{$idx} : un prix est requis (unitPrice ou totalPrice).";
            }
        }

        if (!empty($errors)) {
            $this->json(['error' => 'Donnees invalides.', 'details' => $errors], 400);
            return;
        }

        // --- 3. Numero de commande ---
        $orderNumber = trim($input['orderNumber'] ?? '');
        if ($orderNumber === '') {
            $orderNumber = (string) rand(100, 999);
        }
        // Securisation : max 20 chars, alphanum + tirets
        $orderNumber = substr(preg_replace('/[^a-zA-Z0-9\-]/', '', $orderNumber), 0, 20);

        // Chevalet obligatoire en sur-place + validation basique
        $chevalet = null;
        if ($mode === 'sur-place') {
            if (!isset($input['chevalet'])) {
                $this->json(['error' => 'Le numero de chevalet est obligatoire pour le sur-place.'], 400);
                return;
            }

            $chevalet = (int) $input['chevalet'];
            if ($chevalet < 1 || $chevalet > 999) {
                $this->json(['error' => 'Le numero de chevalet doit etre compris entre 1 et 999.'], 400);
                return;
            }
        }

        // --- 4. Insertion en base (transaction) ---
        try {
            $pdo = Database::getInstance()->getPdo();
            $pdo->beginTransaction();

            if ($mode === 'sur-place') {
                $occupied = $pdo->prepare(
                    "SELECT id FROM orders
                     WHERE mode = 'sur-place'
                       AND chevalet = ?
                       AND status IN ('pending', 'preparing', 'ready')
                     LIMIT 1"
                );
                $occupied->execute([$chevalet]);

                if ($occupied->fetch()) {
                    $pdo->rollBack();
                    $this->json(['error' => 'Ce numero de chevalet est deja utilise.'], 409);
                    return;
                }
            }

            $orderModel = new Order();
            $orderId = $orderModel->create([
                'order_number' => $orderNumber,
                'mode'         => $mode,
                'status'       => 'pending',
                'chevalet'     => $chevalet,
                'total'        => round($total, 2),
            ]);

            $itemModel = new OrderItem();
            $computedTotal = 0;

            // Liste des product_id valides en base
            $validProductIds = array_map('intval', array_column(
                $pdo->query("SELECT id FROM products")->fetchAll(\PDO::FETCH_ASSOC),
                'id'
            ));

            foreach ($items as $item) {
                $unitPrice = (float) ($item['unitPrice'] ?? $item['totalPrice'] ?? 0);
                $quantity  = max(1, (int) ($item['quantity'] ?? 1));

                // Si le product_id du front ne correspond pas à un produit en base → NULL
                $productId = !empty($item['productId']) ? (int) $item['productId'] : null;
                if ($productId !== null && !in_array($productId, $validProductIds)) {
                    $productId = null;
                }

                $itemModel->create([
                    'order_id'   => $orderId,
                    'product_id' => $productId,
                    'name'       => mb_substr(trim($item['name']), 0, 150),
                    'quantity'   => $quantity,
                    'unit_price' => round($unitPrice, 2),
                    'options'    => json_encode($item['options'] ?? [], JSON_UNESCAPED_UNICODE),
                ]);

                $computedTotal += $unitPrice * $quantity;
            }

            // Recalcul du total cote serveur (securite)
            $orderModel->update($orderId, ['total' => round($computedTotal, 2)]);

            $pdo->commit();

            error_log(sprintf(
                'API /api/commande — OK id=%d mode=%s chevalet=%s total=%.2f',
                $orderId,
                $mode,
                $chevalet === null ? 'null' : (string) $chevalet,
                round($computedTotal, 2)
            ));

            // --- 5. Reponse 201 Created ---
            $this->json([
                'success'     => true,
                'orderId'     => $orderId,
                'orderNumber' => $orderNumber,
                'total'       => round($computedTotal, 2),
                'status'      => 'pending',
            ], 201);

        } catch (\Throwable $e) {
            if ($pdo->inTransaction()) {
                $pdo->rollBack();
            }
            error_log('API /api/commande — Erreur : ' . $e->getMessage());
            $this->json(['error' => 'Erreur interne du serveur.'], 500);
        }
    }
}
