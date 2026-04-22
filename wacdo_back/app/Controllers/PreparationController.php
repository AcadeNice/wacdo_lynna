<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Core\Security;
use App\Core\Session;
use App\Models\Order;

class PreparationController extends Controller
{
    public function index(): void
    {
        $orderModel = new Order();
        $pending   = $orderModel->findAllByStatus('pending');
        $preparing = $orderModel->findAllByStatus('preparing');
        $ready     = $orderModel->findAllByStatus('ready');
        $orders = array_merge($pending, $preparing, $ready);

        // Trier par date croissante
        usort($orders, fn($a, $b) => $a['created_at'] <=> $b['created_at']);

        // Charger les items de chaque commande
        foreach ($orders as &$order) {
            $order['items'] = $orderModel->getItems((int) $order['id']);
        }
        unset($order);

        // Compteurs par statut
        $counts = [
            'pending'   => count($pending),
            'preparing' => count($preparing),
            'ready'     => count($ready),
        ];

        $this->view('preparation/index', compact('orders', 'counts'));
    }

    public function markReady(string $id): void
    {
        Security::checkCsrf();
        $orderModel = new Order();
        $order = $orderModel->find((int) $id);
        if ($order) {
            $newStatus = match ($order['status']) {
                'pending'   => 'preparing',
                'preparing' => 'ready',
                default     => $order['status'],
            };
            $orderModel->updateStatus((int) $id, $newStatus);
        }
        Session::flash('success', 'Statut mis a jour.');
        $this->redirect('preparation');
    }
}
