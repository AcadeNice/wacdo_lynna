<?php
$title = $user ? 'Modifier utilisateur' : 'Nouvel utilisateur';
$e = fn($v) => \App\Core\Security::escape($v);
$action = $user ? BASE_URL.'/users/'.$user['id'] : BASE_URL.'/users';
?>
<div class="card">
    <h2><?= $e($title) ?></h2>
    <form method="POST" action="<?= $action ?>">
        <?= \App\Core\Security::csrfField() ?>
        <div class="form-group">
            <label>Nom d'utilisateur</label>
            <input type="text" name="username" value="<?= $e($user['username'] ?? '') ?>" required>
        </div>
        <div class="form-group">
            <label>Email</label>
            <input type="email" name="email" value="<?= $e($user['email'] ?? '') ?>" required>
        </div>
        <div class="form-group">
            <label>Mot de passe<?= $user ? ' (laisser vide pour ne pas changer)' : '' ?></label>
            <input type="password" name="password" <?= $user ? '' : 'required' ?>>
        </div>
        <div class="form-group">
            <label>Role</label>
            <select name="role">
                <?php foreach (['admin','preparation','accueil'] as $r): ?>
                <option value="<?= $r ?>" <?= ($user['role'] ?? '') === $r ? 'selected' : '' ?>><?= ucfirst($r) ?></option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="active" value="1" <?= ($user['active'] ?? 1) ? 'checked' : '' ?>> Actif</label>
        </div>
        <button type="submit" class="btn btn-primary">Enregistrer</button>
        <a href="<?= BASE_URL ?>/users" class="btn">Annuler</a>
    </form>
</div>
