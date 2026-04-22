<?php $title = 'Commandes'; $e = fn($v) => \App\Core\Security::escape($v); ?>
<div class="card">
    <div class="card-header">
        <h2>Commandes</h2>
        <a href="<?= BASE_URL ?>/orders/create" class="btn btn-primary">+ Saisir commande</a>
    </div>
    <table class="table">
        <thead><tr><th>#</th><th>Numero</th><th>Mode</th><th>Statut</th><th>Total</th><th>Date</th><th>Actions</th></tr></thead>
        <tbody>
        <?php foreach ($orders as $o): ?>
        <tr>
            <td><?= $o['id'] ?></td>
            <td><a href="<?= BASE_URL ?>/orders/<?= $o['id'] ?>"><?= $e($o['order_number']) ?></a></td>
            <td><?= $e($o['mode']) ?></td>
            <td><span class="badge badge-<?= $o['status'] ?>"><?= $e($o['status']) ?></span></td>
            <td><?= number_format((float)$o['total'], 2, ',', ' ') ?> &euro;</td>
            <td><?= $o['created_at'] ?></td>
            <td class="actions">
                <a href="<?= BASE_URL ?>/orders/<?= $o['id'] ?>" class="btn btn-sm">Voir</a>
                <?php if ($o['status'] !== 'delivered'): ?>
                <a href="<?= BASE_URL ?>/orders/<?= $o['id'] ?>/edit" class="btn btn-sm">Modifier</a>
                <?php else: ?>
                <span class="badge">Verrouillee</span>
                <?php endif; ?>
                <?php if ($o['status'] === 'ready'): ?>
                <form method="POST" action="<?= BASE_URL ?>/orders/<?= $o['id'] ?>/deliver" class="inline-form">
                    <?= \App\Core\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-success">Remettre</button>
                </form>
                <?php endif; ?>
                <?php if ($o['status'] !== 'delivered'): ?>
                <form method="POST" action="<?= BASE_URL ?>/orders/<?= $o['id'] ?>/delete" class="inline-form">
                    <?= \App\Core\Security::csrfField() ?>
                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Supprimer cette commande ?')">Supprimer</button>
                </form>
                <?php endif; ?>
            </td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
