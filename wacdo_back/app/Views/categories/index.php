<?php $title = 'Categories'; $e = fn($v) => \App\Core\Security::escape($v); ?>
<div class="card">
    <div class="card-header">
        <h2>Categories</h2>
        <a href="<?= BASE_URL ?>/categories/create" class="btn btn-primary">+ Nouvelle</a>
    </div>
    <table class="table">
        <thead><tr><th>Ordre</th><th>Nom</th><th>Slug</th><th>Icone</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($categories as $c): ?>
        <tr>
            <td><?= $c['display_order'] ?></td>
            <td><?= $e($c['name']) ?></td>
            <td><code><?= $e($c['slug']) ?></code></td>
            <td><?= $e($c['icon'] ?? '-') ?></td>
            <td class="actions">
                <a href="<?= BASE_URL ?>/categories/<?= $c['id'] ?>/edit" class="btn btn-sm">Modifier</a>
                <form method="POST" action="<?= BASE_URL ?>/categories/<?= $c['id'] ?>/delete" class="inline-form">
                    <?= \App\Core\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Supprimer ?')">Supprimer</button>
                </form>
            </td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
