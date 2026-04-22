<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Core\Security;
use App\Core\Session;
use App\Models\Menu;
use App\Models\Product;

class MenuController extends Controller
{
    public function index(): void
    {
        $menus = (new Menu())->findAllWithComposition();
        $this->view('menus/index', compact('menus'));
    }

    public function create(): void
    {
        $products = (new Product())->findAllWithCategory();
        $this->view('menus/form', ['menu' => null, 'products' => $products, 'compositions' => []]);
    }

    public function store(): void
    {
        Security::checkCsrf();
        $data = $this->validated();
        $menuModel = new Menu();
        $id = $menuModel->create($data);
        $this->saveCompositions($menuModel, $id);
        Session::flash('success', 'Menu cree.');
        $this->redirect('menus');
    }

    public function edit(string $id): void
    {
        $menuModel = new Menu();
        $menu = $menuModel->find((int) $id);
        if (!$menu) $this->redirect('menus');
        $products     = (new Product())->findAllWithCategory();
        $compositions = (new \App\Core\Database())->fetchAll(
            "SELECT * FROM menu_compositions WHERE menu_id = ?", [(int) $id]
        );
        $this->view('menus/form', compact('menu', 'products', 'compositions'));
    }

    public function update(string $id): void
    {
        Security::checkCsrf();
        $menuModel = new Menu();
        $menuModel->update((int) $id, $this->validated());
        $menuModel->clearCompositions((int) $id);
        $this->saveCompositions($menuModel, (int) $id);
        Session::flash('success', 'Menu mis a jour.');
        $this->redirect('menus');
    }

    public function destroy(string $id): void
    {
        Security::checkCsrf();
        (new Menu())->delete((int) $id);
        Session::flash('success', 'Menu supprime.');
        $this->redirect('menus');
    }

    private function validated(): array
    {
        return [
            'name'        => trim($_POST['name'] ?? ''),
            'description' => trim($_POST['description'] ?? ''),
            'base_price'  => (float) ($_POST['base_price'] ?? 0),
            'image'       => trim($_POST['image'] ?? ''),
            'available'   => isset($_POST['available']) ? 1 : 0,
        ];
    }

    private function saveCompositions(Menu $menuModel, int $menuId): void
    {
        $types = ['burger', 'side', 'drink', 'sauce'];
        foreach ($types as $type) {
            $ids = $_POST['comp_' . $type] ?? [];
            if (!is_array($ids)) $ids = [$ids];
            foreach ($ids as $pid) {
                if ((int) $pid > 0) {
                    $menuModel->addComposition($menuId, (int) $pid, $type);
                }
            }
        }
    }
}
