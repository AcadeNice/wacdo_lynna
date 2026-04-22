<?php $title = 'Produits'; $e = fn($v) => \App\Core\Security::escape($v); ?>
<div class="card">
    <div class="card-header">
        <h2>Produits</h2>
        <a href="<?= BASE_URL ?>/products/create" class="btn btn-primary">+ Nouveau</a>
    </div>
    <table class="table">
        <thead><tr><th>ID</th><th>Nom</th><th>Categorie</th><th>Prix</th><th>Dispo</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($products as $p): ?>
        <tr>
            <td><?= $p['id'] ?></td>
            <td><?= $e($p['name']) ?></td>
            <td><?= $e($p['category_name']) ?></td>
            <td><?= number_format((float)$p['price'], 2, ',', ' ') ?> &euro;</td>
            <td><?= $p['available'] ? 'Oui' : 'Non' ?></td>
            <td class="actions">
                <a href="<?= BASE_URL ?>/products/<?= $p['id'] ?>/edit" class="btn btn-sm">Modifier</a>
                <form method="POST" action="<?= BASE_URL ?>/products/<?= $p['id'] ?>/delete" class="inline-form">
                    <?= \App\Core\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Supprimer ?')">Supprimer</button>
                </form>
            </td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
