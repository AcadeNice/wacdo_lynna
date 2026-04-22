<?php
namespace App\Controllers;

use App\Core\Controller;
use App\Core\Security;
use App\Core\Session;
use App\Models\Product;
use App\Models\Category;

class ProductController extends Controller
{
    public function index(): void
    {
        $products = (new Product())->findAllWithCategory();
        $this->view('products/index', compact('products'));
    }

    public function create(): void
    {
        $categories = (new Category())->findAllOrdered();
        $this->view('products/form', ['product' => null, 'categories' => $categories]);
    }

    public function store(): void
    {
        Security::checkCsrf();
        $data = $this->validated();
        $data['image'] = $this->handleUpload() ?: ($data['image'] ?? '');
        (new Product())->create($data);
        Session::flash('success', 'Produit cree.');
        $this->redirect('products');
    }

    public function edit(string $id): void
    {
        $product    = (new Product())->find((int) $id);
        $categories = (new Category())->findAllOrdered();
        if (!$product) $this->redirect('products');
        $this->view('products/form', compact('product', 'categories'));
    }

    public function update(string $id): void
    {
        Security::checkCsrf();
        $data = $this->validated();
        $uploaded = $this->handleUpload();
        if ($uploaded) $data['image'] = $uploaded;
        (new Product())->update((int) $id, $data);
        Session::flash('success', 'Produit mis a jour.');
        $this->redirect('products');
    }

    public function destroy(string $id): void
    {
        Security::checkCsrf();
        (new Product())->delete((int) $id);
        Session::flash('success', 'Produit supprime.');
        $this->redirect('products');
    }

    private function validated(): array
    {
        return [
            'category_id' => (int) ($_POST['category_id'] ?? 0),
            'name'        => trim($_POST['name'] ?? ''),
            'description' => trim($_POST['description'] ?? ''),
            'price'       => (float) ($_POST['price'] ?? 0),
            'image'       => trim($_POST['image'] ?? ''),
            'available'   => isset($_POST['available']) ? 1 : 0,
        ];
    }

    private function handleUpload(): string
    {
        if (!isset($_FILES['image_file']) || $_FILES['image_file']['error'] !== UPLOAD_ERR_OK) {
            return '';
        }
        $file = $_FILES['image_file'];
        $ext  = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if (!in_array($ext, ['jpg','jpeg','png','gif','webp'])) return '';
        $name = uniqid('prod_') . '.' . $ext;
        $dest = ROOT_PATH . '/public/uploads/' . $name;
        if (!is_dir(dirname($dest))) mkdir(dirname($dest), 0755, true);
        move_uploaded_file($file['tmp_name'], $dest);
        return '/uploads/' . $name;
    }
}
