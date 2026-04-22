<?php
namespace App\Controllers\Api;

use App\Core\Controller;
use App\Models\Product;

class ProductApiController extends Controller
{
    public function index(): void
    {
        $this->json((new Product())->allGroupedByCategory());
    }

    public function byCategory(string $category): void
    {
        $products = (new Product())->findByCategorySlug($category);
        $result = array_map(fn($p) => [
            'id'   => $p['id'],
            'nom'  => $p['name'],
            'prix' => (float) $p['price'],
            'image'=> $p['image'],
        ], $products);
        $this->json($result);
    }
}
