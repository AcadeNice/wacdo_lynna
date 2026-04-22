<?php $title = 'Utilisateurs'; $e = fn($v) => \App\Core\Security::escape($v); ?>
<div class="card">
    <div class="card-header">
        <h2>Utilisateurs</h2>
        <a href="<?= BASE_URL ?>/users/create" class="btn btn-primary">+ Nouveau</a>
    </div>
    <table class="table">
        <thead><tr><th>ID</th><th>Nom</th><th>Email</th><th>Role</th><th>Actif</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($users as $u): ?>
        <tr>
            <td><?= $u['id'] ?></td>
            <td><?= $e($u['username']) ?></td>
            <td><?= $e($u['email']) ?></td>
            <td><span class="badge badge-<?= $u['role'] ?>"><?= $e($u['role']) ?></span></td>
            <td><?= $u['active'] ? 'Oui' : 'Non' ?></td>
            <td class="actions">
                <a href="<?= BASE_URL ?>/users/<?= $u['id'] ?>/edit" class="btn btn-sm">Modifier</a>
                <form method="POST" action="<?= BASE_URL ?>/users/<?= $u['id'] ?>/delete" class="inline-form">
                    <?= \App\Core\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Supprimer ?')">Supprimer</button>
                </form>
            </td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
