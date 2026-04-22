<?php
namespace App\Controllers\Api;

use App\Core\Controller;
use App\Models\Menu;

class MenuApiController extends Controller
{
    public function index(): void
    {
        $this->json((new Menu())->allForApi());
    }
}
