<?php $title = 'Tableau de bord'; $e = fn($v) => \App\Core\Security::escape($v); ?>
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value"><?= $stats['total'] ?></div>
        <div class="stat-label">Commandes aujourd'hui</div>
    </div>
    <div class="stat-card stat-warning">
        <div class="stat-value"><?= $stats['pending'] ?></div>
        <div class="stat-label">En attente</div>
    </div>
    <div class="stat-card stat-success">
        <div class="stat-value"><?= number_format($stats['revenue'], 2, ',', ' ') ?> &euro;</div>
        <div class="stat-label">Chiffre du jour</div>
    </div>
    <div class="stat-card">
        <div class="stat-value"><?= $stats['products'] ?></div>
        <div class="stat-label">Produits</div>
    </div>
</div>
<div class="card">
    <h2>Dernieres commandes</h2>
    <table class="table">
        <thead><tr><th>#</th><th>Numero</th><th>Mode</th><th>Statut</th><th>Total</th><th>Date</th></tr></thead>
        <tbody>
        <?php foreach ($recentOrders as $o): ?>
        <tr>
            <td><?= $o['id'] ?></td>
            <td><a href="<?= BASE_URL ?>/orders/<?= $o['id'] ?>"><?= $e($o['order_number']) ?></a></td>
            <td><?= $e($o['mode']) ?></td>
            <td><span class="badge badge-<?= $o['status'] ?>"><?= $e($o['status']) ?></span></td>
            <td><?= number_format((float)$o['total'], 2, ',', ' ') ?> &euro;</td>
            <td><?= $o['created_at'] ?></td>
        </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
