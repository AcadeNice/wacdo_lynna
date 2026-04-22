<?php
/**
 * Wacdo — Script d'installation CLI.
 * Usage : php setup.php
 */
echo "=== Wacdo Back-End — Installation ===\n\n";

$config = require __DIR__ . '/config/database.php';

// Connexion sans base
$dsn = "mysql:host={$config['host']};charset={$config['charset']}";
try {
    $pdo = new PDO($dsn, $config['username'], $config['password'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    ]);
} catch (PDOException $e) {
    die("Erreur connexion MySQL : " . $e->getMessage() . "\n");
}

// Schema
echo "Creation de la base et des tables...\n";
$sql = file_get_contents(__DIR__ . '/sql/schema.sql');
$pdo->exec($sql);
echo "  OK\n";

// Selectionner la base
$pdo->exec("USE {$config['database']}");

// Utilisateurs par defaut
echo "Insertion des utilisateurs par defaut...\n";
$users = [
    ['admin',       'admin@wacdo.fr',   'admin'],
    ['preparation', 'prep@wacdo.fr',    'preparation'],
    ['accueil',     'accueil@wacdo.fr', 'accueil'],
];
$stmt = $pdo->prepare("INSERT IGNORE INTO users (username, email, password, role) VALUES (?, ?, ?, ?)");
foreach ($users as [$user, $email, $role]) {
    $hash = password_hash('Wacdo2024!', PASSWORD_BCRYPT);
    $stmt->execute([$user, $email, $hash, $role]);
}
echo "  OK (mot de passe : Wacdo2024!)\n";

// Categories
echo "Insertion des categories...\n";
$cats = [
    ['Menus',    'menus',    'menus.png',    1],
    ['Burgers',  'burgers',  'burgers.png',  2],
    ['Frites',   'frites',   'frites.png',   3],
    ['Boissons', 'boissons', 'boissons.png', 4],
    ['Salades',  'salades',  'salades.png',  5],
    ['Wraps',    'wraps',    'wraps.png',    6],
    ['Encas',    'encas',    'encas.png',    7],
    ['Desserts', 'desserts', 'desserts.png', 8],
    ['Sauces',   'sauces',   'sauces.png',   9],
];
$stmt = $pdo->prepare("INSERT IGNORE INTO categories (name, slug, icon, display_order) VALUES (?, ?, ?, ?)");
foreach ($cats as $c) { $stmt->execute($c); }
echo "  OK\n";

// Produits (exemples)
echo "Insertion des produits...\n";
$products = [
    [2,'Le 280','',6.80,'/burgers/280.png'],
    [2,'Big Tasty','',5.90,'/burgers/BIG_TASTY_1_VIANDE.png'],
    [2,'Big Mac','',5.50,'/burgers/BIGMAC.png'],
    [2,'CBO','',6.10,'/burgers/CBO.png'],
    [2,'MC Chicken','',5.30,'/burgers/MCCHICKEN.png'],
    [2,'Royal Cheese','',4.90,'/burgers/ROYALCHEESE.png'],
    [2,'Royal Deluxe','',5.20,'/burgers/ROYALDELUXE.png'],
    [3,'Petite Frite','',1.45,'/frites/PETITE_FRITE.png'],
    [3,'Moyenne Frite','',2.75,'/frites/MOYENNE_FRITE.png'],
    [3,'Grande Frite','',3.50,'/frites/GRANDE_FRITE.png'],
    [3,'Potatoes','',2.15,'/frites/POTATOES.png'],
    [4,'Coca-Cola','',2.50,'/boissons/coca.png'],
    [4,'Sprite','',2.50,'/boissons/sprite.png'],
    [4,'Fanta','',2.50,'/boissons/fanta.png'],
    [4,'Eau','',1.50,'/boissons/eau.png'],
    [9,'Ketchup','',0.50,'/sauces/ketchup.png'],
    [9,'Mayonnaise','',0.50,'/sauces/mayonnaise.png'],
    [9,'Sauce Curry','',0.50,'/sauces/curry.png'],
];
$stmt = $pdo->prepare("INSERT INTO products (category_id, name, description, price, image) VALUES (?, ?, ?, ?, ?)");
foreach ($products as $p) { $stmt->execute($p); }
echo "  OK\n";

// Menus
echo "Insertion des menus...\n";
$menus = [
    ['Menu Le 280','', 8.80,'/burgers/280.png'],
    ['Menu Big Mac','', 8.00,'/burgers/BIGMAC.png'],
    ['Menu Big Tasty','', 10.60,'/burgers/BIG_TASTY_1_VIANDE.png'],
    ['Menu CBO','', 10.90,'/burgers/CBO.png'],
];
$stmt = $pdo->prepare("INSERT INTO menus (name, description, base_price, image) VALUES (?, ?, ?, ?)");
foreach ($menus as $m) { $stmt->execute($m); }
echo "  OK\n";

echo "\n=== Installation terminee ! ===\n";
echo "Acces : http://localhost/wacdo_lynna/wacdo_back/public/login\n";
echo "Admin  : admin / Wacdo2024!\n";
