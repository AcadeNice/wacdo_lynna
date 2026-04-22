<?php $title = 'Menus'; $e = fn($v) => \App\Core\Security::escape($v); ?>
<div class="card">
    <div class="card-header">
        <h2>Menus</h2>
        <a href="<?= BASE_URL ?>/menus/create" class="btn btn-primary">+ Nouveau</a>
    </div>
    <table class="table">
        <thead><tr><th>ID</th><th>Nom</th><th>Prix de base</th><th>Dispo</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($menus as $m): ?>
        <tr>
            <td><?= $m['id'] ?></td>
            <td><?= $e($m['name']) ?></td>
            <td><?= number_format((float)$m['base_price'], 2, ',', ' ') ?> &euro;</td>
            <td><?= $m['available'] ? 'Oui' : 'Non' ?></td>
            <td class="actions">
                <a href="<?= BASE_URL ?>/menus/<?= $m['id'] ?>/edit" class="btn btn-sm">Modifier</a>
                <form method="POST" action="<?= BASE_URL ?>/menus/<?= $m['id'] ?>/delete" class="inline-form">
                    <?= \App\Core\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Supprimer ?')">Supprimer</button>
                </form>
            </td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
