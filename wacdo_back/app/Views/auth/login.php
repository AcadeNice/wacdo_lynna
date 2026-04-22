<?php use App\Core\Security; ?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wacdo — Connexion</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="<?= BASE_URL ?>/css/admin.css">
</head>
<body class="login-page">
    <div class="login-box">
        <div class="login-logo"><span class="logo-w">W</span></div>
        <h1>Connexion</h1>
        <?php if (!empty($error)): ?>
            <div class="alert alert-error"><?= Security::escape($error) ?></div>
        <?php endif; ?>
        <form method="POST" action="<?= BASE_URL ?>/login">
            <?= Security::csrfField() ?>
            <div class="form-group">
                <label for="username">Nom d'utilisateur</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Mot de passe</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary btn-full">Se connecter</button>
        </form>
    </div>
</body>
</html>
