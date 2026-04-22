<?php
$title = 'Commande #' . ($order['order_number'] ?? '');
$e = fn($v) => \App\Core\Security::escape($v);
?>
<div class="card">
    <h2>Commande n&deg;<?= $e($order['order_number']) ?></h2>
    <div class="info-grid">
        <div><strong>Mode :</strong> <?= $e($order['mode']) ?></div>
        <div><strong>Statut :</strong> <span class="badge badge-<?= $order['status'] ?>"><?= $e($order['status']) ?></span></div>
        <div><strong>Chevalet :</strong> <?= $order['chevalet'] ?? '-' ?></div>
        <div><strong>Total :</strong> <?= number_format((float)$order['total'], 2, ',', ' ') ?> &euro;</div>
        <div><strong>Date :</strong> <?= $order['created_at'] ?></div>
    </div>
    <h3>Articles</h3>
    <table class="table">
        <thead><tr><th>Produit</th><th>Quantite</th><th>Prix unitaire</th><th>Sous-total</th></tr></thead>
        <tbody>
        <?php foreach ($order['items'] as $item): ?>
        <tr>
            <td><?= $e($item['name']) ?></td>
            <td><?= $item['quantity'] ?></td>
            <td><?= number_format((float)$item['unit_price'], 2, ',', ' ') ?> &euro;</td>
            <td><?= number_format((float)$item['unit_price'] * $item['quantity'], 2, ',', ' ') ?> &euro;</td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
    <?php if ($order['status'] === 'ready'): ?>
    <form method="POST" action="<?= BASE_URL ?>/orders/<?= $order['id'] ?>/deliver">
        <?= \App\Core\Security::csrfField() ?>
        <button type="submit" class="btn btn-success">Marquer comme remise au client</button>
    </form>
    <?php endif; ?>
    <?php if ($order['status'] !== 'delivered'): ?>
    <a href="<?= BASE_URL ?>/orders/<?= $order['id'] ?>/edit" class="btn btn-primary">Modifier la commande</a>
    <form method="POST" action="<?= BASE_URL ?>/orders/<?= $order['id'] ?>/delete" class="inline-form">
        <?= \App\Core\Security::csrfField() ?>
        <button type="submit" class="btn btn-danger" onclick="return confirm('Supprimer cette commande ?')">Supprimer</button>
    </form>
    <?php else: ?>
    <p class="hint">Cette commande est remise au client : modification et suppression verrouillees.</p>
    <?php endif; ?>

    <h3>Historique</h3>
    <?php if (!empty($order['history'])): ?>
    <table class="table">
        <thead><tr><th>Date</th><th>Action</th><th>Details</th></tr></thead>
        <tbody>
        <?php foreach ($order['history'] as $h): ?>
        <?php $d = json_decode($h['details'] ?? '{}', true); ?>
        <tr>
            <td><?= $e($h['created_at']) ?></td>
            <td><?= $e($h['action']) ?></td>
            <td><?= $e($d['message'] ?? '') ?></td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
    <?php else: ?>
    <p class="hint">Aucun historique disponible.</p>
    <?php endif; ?>

    <a href="<?= BASE_URL ?>/orders" class="btn">Retour</a>
</div>
