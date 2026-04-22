<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Core\Security;
use App\Core\Session;
use App\Models\Order;
use App\Models\OrderItem;
use App\Models\Product;
use App\Models\Menu;

class OrderController extends Controller
{
    public function index(): void
    {
        $orders = (new Order())->findRecent(100);
        $this->view('orders/index', compact('orders'));
    }

    public function create(): void
    {
        $products = (new Product())->findAllWithCategory();
        $menus    = (new Menu())->findAll('name ASC');
        $this->view('orders/create', compact('products', 'menus'));
    }

    public function store(): void
    {
        Security::checkCsrf();
        $orderModel = new Order();
        $orderId = $orderModel->create([
            'order_number' => trim($_POST['order_number'] ?? (string) rand(100,999)),
            'mode'         => $_POST['mode'] ?? 'sur-place',
            'status'       => 'pending',
            'total'        => 0,
            'created_by'   => Session::get('user_id'),
        ]);

        $itemModel = new OrderItem();
        $total = 0;
        $names  = $_POST['item_name']  ?? [];
        $qtys   = $_POST['item_qty']   ?? [];
        $prices = $_POST['item_price'] ?? [];
        for ($i = 0; $i < count($names); $i++) {
            if (empty($names[$i])) continue;
            $price = (float) ($prices[$i] ?? 0);
            $qty   = max(1, (int) ($qtys[$i] ?? 1));
            $itemModel->create([
                'order_id'   => $orderId,
                'name'       => $names[$i],
                'quantity'   => $qty,
                'unit_price' => $price,
            ]);
            $total += $price * $qty;
        }
        $orderModel->update($orderId, ['total' => $total]);
        $orderModel->logHistory($orderId, 'order_created', [
            'message' => 'Commande creee depuis le back-office.',
            'total'   => round($total, 2),
            'status'  => 'pending',
        ], (int) Session::get('user_id'));

        Session::flash('success', 'Commande creee.');
        $this->redirect('orders');
    }

    public function show(string $id): void
    {
        $order = (new Order())->findWithItems((int) $id);
        if (!$order) $this->redirect('orders');
        $this->view('orders/show', compact('order'));
    }

    public function edit(string $id): void
    {
        $order = (new Order())->findWithItems((int) $id);
        if (!$order) {
            Session::flash('error', 'Commande introuvable.');
            $this->redirect('orders');
            return;
        }

        if (($order['status'] ?? '') === 'delivered') {
            Session::flash('error', 'Cette commande est deja remise: modification verrouillee.');
            $this->redirect('orders/' . (int) $id);
            return;
        }

        $this->view('orders/edit', compact('order'));
    }

    public function update(string $id): void
    {
        Security::checkCsrf();

        $orderModel = new Order();
        $itemModel  = new OrderItem();
        $orderId    = (int) $id;
        $order      = $orderModel->find($orderId);

        if (!$order) {
            Session::flash('error', 'Commande introuvable.');
            $this->redirect('orders');
            return;
        }

        if (($order['status'] ?? '') === 'delivered') {
            Session::flash('error', 'Cette commande est deja remise: modification verrouillee.');
            $this->redirect('orders/' . $orderId);
            return;
        }

        $oldSnapshot = $orderModel->findWithItems($orderId);

        $mode = $_POST['mode'] ?? 'sur-place';
        if (!in_array($mode, ['sur-place', 'a-emporter'], true)) {
            $mode = 'sur-place';
        }

        $status = $_POST['status'] ?? 'pending';
        if (!in_array($status, ['pending', 'preparing', 'ready', 'delivered', 'cancelled'], true)) {
            $status = $order['status'] ?? 'pending';
        }

        $chevalet = null;
        if ($mode === 'sur-place' && isset($_POST['chevalet']) && $_POST['chevalet'] !== '') {
            $chevalet = max(1, (int) $_POST['chevalet']);
        }

        $orderNumber = trim($_POST['order_number'] ?? (string) ($order['order_number'] ?? rand(100,999)));
        if ($orderNumber === '') {
            $orderNumber = (string) rand(100,999);
        }

        $orderModel->update($orderId, [
            'order_number' => $orderNumber,
            'mode'         => $mode,
            'status'       => $status,
            'chevalet'     => $chevalet,
        ]);

        $itemModel->deleteByOrderId($orderId);

        $total = 0;
        $names  = $_POST['item_name']  ?? [];
        $qtys   = $_POST['item_qty']   ?? [];
        $prices = $_POST['item_price'] ?? [];

        for ($i = 0; $i < count($names); $i++) {
            $name = trim((string) ($names[$i] ?? ''));
            if ($name === '') continue;

            $qty   = max(1, (int) ($qtys[$i] ?? 1));
            $price = max(0, (float) ($prices[$i] ?? 0));

            $itemModel->create([
                'order_id'   => $orderId,
                'name'       => $name,
                'quantity'   => $qty,
                'unit_price' => $price,
            ]);

            $total += $price * $qty;
        }

        $orderModel->update($orderId, ['total' => round($total, 2)]);
        $newSnapshot = $orderModel->findWithItems($orderId);
        $orderModel->logHistory($orderId, 'order_updated', [
            'message' => 'Commande modifiee depuis le back-office.',
            'before'  => [
                'order_number' => $oldSnapshot['order_number'] ?? null,
                'mode'         => $oldSnapshot['mode'] ?? null,
                'status'       => $oldSnapshot['status'] ?? null,
                'chevalet'     => $oldSnapshot['chevalet'] ?? null,
                'total'        => $oldSnapshot['total'] ?? null,
                'items_count'  => isset($oldSnapshot['items']) ? count($oldSnapshot['items']) : 0,
            ],
            'after' => [
                'order_number' => $newSnapshot['order_number'] ?? null,
                'mode'         => $newSnapshot['mode'] ?? null,
                'status'       => $newSnapshot['status'] ?? null,
                'chevalet'     => $newSnapshot['chevalet'] ?? null,
                'total'        => $newSnapshot['total'] ?? null,
                'items_count'  => isset($newSnapshot['items']) ? count($newSnapshot['items']) : 0,
            ],
        ], (int) Session::get('user_id'));

        Session::flash('success', 'Commande mise a jour.');
        $this->redirect('orders/' . $orderId);
    }

    public function destroy(string $id): void
    {
        Security::checkCsrf();

        $orderModel = new Order();
        $orderId = (int) $id;
        $order = $orderModel->find($orderId);

        if (!$order) {
            Session::flash('error', 'Commande introuvable.');
            $this->redirect('orders');
            return;
        }

        if (($order['status'] ?? '') === 'delivered') {
            Session::flash('error', 'Cette commande est deja remise: suppression verrouillee.');
            $this->redirect('orders/' . $orderId);
            return;
        }

        $orderModel->logHistory($orderId, 'order_deleted', [
            'message'      => 'Commande supprimee depuis le back-office.',
            'order_number' => $order['order_number'] ?? null,
            'mode'         => $order['mode'] ?? null,
            'status'       => $order['status'] ?? null,
            'total'        => $order['total'] ?? null,
        ], (int) Session::get('user_id'));

        $orderModel->delete($orderId);

        Session::flash('success', 'Commande supprimee.');
        $this->redirect('orders');
    }

    public function deliver(string $id): void
    {
        Security::checkCsrf();
        $orderModel = new Order();
        $orderId = (int) $id;
        $order = $orderModel->find($orderId);

        if (!$order) {
            Session::flash('error', 'Commande introuvable.');
            $this->redirect('orders');
            return;
        }

        $orderModel->updateStatus($orderId, 'delivered');
        $orderModel->logHistory($orderId, 'order_delivered', [
            'message' => 'Commande marquee comme remise au client.',
        ], (int) Session::get('user_id'));
        Session::flash('success', 'Commande remise au client.');
        $this->redirect('orders');
    }
}
