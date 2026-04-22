<?php
/**
 * Definition des routes de l'application.
 * $router est une instance de App\Core\Router.
 */

// Auth
$router->get('/login',  'AuthController@showLogin', ['guest']);
$router->post('/login', 'AuthController@login',     ['guest']);
$router->get('/logout', 'AuthController@logout',     ['auth']);

// Dashboard
$router->get('/',          'DashboardController@index', ['auth']);
$router->get('/dashboard', 'DashboardController@index', ['auth']);

// Utilisateurs (admin uniquement)
$router->get('/users',              'UserController@index',  ['admin']);
$router->get('/users/create',       'UserController@create', ['admin']);
$router->post('/users',             'UserController@store',  ['admin']);
$router->get('/users/{id}/edit',    'UserController@edit',   ['admin']);
$router->post('/users/{id}',        'UserController@update', ['admin']);
$router->post('/users/{id}/delete', 'UserController@destroy',['admin']);

// Produits (admin)
$router->get('/products',              'ProductController@index',  ['admin']);
$router->get('/products/create',       'ProductController@create', ['admin']);
$router->post('/products',             'ProductController@store',  ['admin']);
$router->get('/products/{id}/edit',    'ProductController@edit',   ['admin']);
$router->post('/products/{id}',        'ProductController@update', ['admin']);
$router->post('/products/{id}/delete', 'ProductController@destroy',['admin']);

// Categories (admin)
$router->get('/categories',              'CategoryController@index',  ['admin']);
$router->get('/categories/create',       'CategoryController@create', ['admin']);
$router->post('/categories',             'CategoryController@store',  ['admin']);
$router->get('/categories/{id}/edit',    'CategoryController@edit',   ['admin']);
$router->post('/categories/{id}',        'CategoryController@update', ['admin']);
$router->post('/categories/{id}/delete', 'CategoryController@destroy',['admin']);

// Menus (admin)
$router->get('/menus',              'MenuController@index',  ['admin']);
$router->get('/menus/create',       'MenuController@create', ['admin']);
$router->post('/menus',             'MenuController@store',  ['admin']);
$router->get('/menus/{id}/edit',    'MenuController@edit',   ['admin']);
$router->post('/menus/{id}',        'MenuController@update', ['admin']);
$router->post('/menus/{id}/delete', 'MenuController@destroy',['admin']);

// Commandes (admin + accueil)
$router->get('/orders',              'OrderController@index',   ['staff']);
$router->get('/orders/create',       'OrderController@create',  ['staff']);
$router->post('/orders',             'OrderController@store',   ['staff']);
$router->get('/orders/{id}/edit',    'OrderController@edit',    ['staff']);
$router->post('/orders/{id}',        'OrderController@update',  ['staff']);
$router->post('/orders/{id}/delete', 'OrderController@destroy', ['staff']);
$router->get('/orders/{id}',         'OrderController@show',    ['staff']);
$router->post('/orders/{id}/deliver','OrderController@deliver', ['staff']);

// Preparation (admin + preparation)
$router->get('/preparation',              'PreparationController@index',     ['all_roles']);
$router->post('/preparation/{id}/ready',  'PreparationController@markReady', ['all_roles']);

// API publique (pas de middleware auth)
$router->get('/api/produits',            'Api\\ProductApiController@index');
$router->get('/api/produits/{category}', 'Api\\ProductApiController@byCategory');
$router->get('/api/menus',               'Api\\MenuApiController@index');
$router->get('/api/commandes/recentes',  'Api\\OrderApiController@recentOrders');
$router->get('/api/chevalets/occupes',   'Api\\OrderApiController@occupiedChevalets');
$router->post('/api/commande',           'Api\\OrderApiController@store');
