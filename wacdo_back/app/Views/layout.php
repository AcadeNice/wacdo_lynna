<?php
use App\Core\Security;
use App\Core\Session;
$e = fn($v) => Security::escape($v);
$_success = Session::getFlash('success');
$_error   = Session::getFlash('error');
$_role    = $_user_role ?? '';
$_uname   = $_username ?? '';
?><!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wacdo Admin<?= isset($title) ? ' — '.$e($title) : '' ?></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="<?= BASE_URL ?>/css/admin.css">
</head>
<body>
<div class="app-layout">
    <aside class="sidebar">
        <div class="sidebar-logo">
            <span class="logo-w">W</span>
            <span class="logo-text">Wacdo</span>
        </div>
        <nav class="sidebar-nav">
            <a href="<?= BASE_URL ?>/dashboard" class="nav-link">Dashboard</a>
            <?php if ($_role === 'admin'): ?>
            <a href="<?= BASE_URL ?>/products" class="nav-link">Produits</a>
            <a href="<?= BASE_URL ?>/categories" class="nav-link">Categories</a>
            <a href="<?= BASE_URL ?>/menus" class="nav-link">Menus</a>
            <?php endif; ?>
            <?php if (in_array($_role, ['admin','accueil'])): ?>
            <a href="<?= BASE_URL ?>/orders" class="nav-link">Commandes</a>
            <?php endif; ?>
            <a href="<?= BASE_URL ?>/preparation" class="nav-link">Preparation</a>
            <?php if ($_role === 'admin'): ?>
            <a href="<?= BASE_URL ?>/users" class="nav-link">Utilisateurs</a>
            <?php endif; ?>
        </nav>
        <div class="sidebar-footer">
            <span class="sidebar-user"><?= $e($_uname) ?> (<?= $e($_role) ?>)</span>
            <a href="<?= BASE_URL ?>/logout" class="nav-link logout-link">Deconnexion</a>
        </div>
    </aside>
    <main class="main-area">
        <header class="topbar">
            <h1 class="page-title"><?= $e($title ?? 'Back-office') ?></h1>
        </header>
        <?php if ($_success): ?>
        <div class="alert alert-success"><?= $e($_success) ?></div>
        <?php endif; ?>
        <?php if ($_error): ?>
        <div class="alert alert-error"><?= $e($_error) ?></div>
        <?php endif; ?>
        <div class="content-area">
            <?= $content ?>
        </div>
    </main>
</div>
<script src="<?= BASE_URL ?>/js/admin.js"></script>
</body>
</html>
