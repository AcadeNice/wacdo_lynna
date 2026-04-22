<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Core\Security;
use App\Core\Session;
use App\Models\Category;

class CategoryController extends Controller
{
    public function index(): void
    {
        $categories = (new Category())->findAllOrdered();
        $this->view('categories/index', compact('categories'));
    }

    public function create(): void
    {
        $this->view('categories/form', ['category' => null]);
    }

    public function store(): void
    {
        Security::checkCsrf();
        $data = $this->validated();
        (new Category())->create($data);
        Session::flash('success', 'Categorie creee.');
        $this->redirect('categories');
    }

    public function edit(string $id): void
    {
        $category = (new Category())->find((int) $id);
        if (!$category) $this->redirect('categories');
        $this->view('categories/form', compact('category'));
    }

    public function update(string $id): void
    {
        Security::checkCsrf();
        (new Category())->update((int) $id, $this->validated());
        Session::flash('success', 'Categorie mise a jour.');
        $this->redirect('categories');
    }

    public function destroy(string $id): void
    {
        Security::checkCsrf();
        (new Category())->delete((int) $id);
        Session::flash('success', 'Categorie supprimee.');
        $this->redirect('categories');
    }

    private function validated(): array
    {
        $name = trim($_POST['name'] ?? '');
        return [
            'name'          => $name,
            'slug'          => strtolower(preg_replace('/[^a-z0-9]+/', '-', strtolower($name))),
            'icon'          => trim($_POST['icon'] ?? ''),
            'display_order' => (int) ($_POST['display_order'] ?? 0),
        ];
    }
}
