<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Models\Order;
use App\Models\Product;
use App\Models\User;

class DashboardController extends Controller
{
    public function index(): void
    {
        $orderModel   = new Order();
        $productModel = new Product();
        $userModel    = new User();

        $stats = $orderModel->todayStats();
        $stats['products'] = $productModel->count();
        $stats['users']    = $userModel->count();
        $recentOrders = $orderModel->findRecent(10);

        $this->view('dashboard/index', compact('stats', 'recentOrders'));
    }
}
