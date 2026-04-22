<?php
$title = 'Preparation des commandes';
$e = fn($v) => \App\Core\Security::escape($v);
$statusLabels = [
    'pending'   => 'En attente',
    'preparing' => 'En preparation',
    'ready'     => 'Prete',
];
$statusColors = [
    'pending'   => '#f39c12',
    'preparing' => '#3498db',
    'ready'     => '#27AE60',
];
?>

<!-- Compteurs par statut -->
<div class="prep-counters">
    <div class="prep-counter prep-counter-pending">
        <span class="counter-value"><?= $counts['pending'] ?></span>
        <span class="counter-label">En attente</span>
    </div>
    <div class="prep-counter prep-counter-preparing">
        <span class="counter-value"><?= $counts['preparing'] ?></span>
        <span class="counter-label">En preparation</span>
    </div>
    <div class="prep-counter prep-counter-ready">
        <span class="counter-value"><?= $counts['ready'] ?></span>
        <span class="counter-label">Pretes</span>
    </div>
</div>

<div class="card">
    <div class="card-header">
        <h2>File de preparation</h2>
        <span class="hint">Rafraichissement auto toutes les 15s</span>
    </div>

    <?php if (empty($orders)): ?>
    <p class="empty-msg">Aucune commande en attente.</p>
    <?php else: ?>
    <div class="prep-grid">
        <?php foreach ($orders as $o): ?>
        <div class="prep-card prep-<?= $o['status'] ?>">
            <!-- En-tete -->
            <div class="prep-header">
                <strong class="prep-order-num">#<?= $e($o['order_number']) ?></strong>
                <span class="badge badge-<?= $o['status'] ?>"><?= $e($statusLabels[$o['status']] ?? $o['status']) ?></span>
            </div>

            <!-- Infos mode / chevalet / total / heure -->
            <div class="prep-info">
                <span class="prep-mode"><?= $o['mode'] === 'sur-place' ? 'Sur place' : 'A emporter' ?></span>
                <?php if ($o['chevalet']): ?>
                    <span class="prep-chevalet">Chevalet <?= (int) $o['chevalet'] ?></span>
                <?php endif; ?>
                <span class="prep-total"><?= number_format((float)$o['total'], 2, ',', ' ') ?> &euro;</span>
                <span class="prep-time"><?= date('H:i', strtotime($o['created_at'])) ?></span>
            </div>

            <!-- Detail des articles -->
            <?php if (!empty($o['items'])): ?>
            <div class="prep-items">
                <?php foreach ($o['items'] as $item): ?>
                <div class="prep-item">
                    <span class="prep-item-qty"><?= (int) $item['quantity'] ?>x</span>
                    <span class="prep-item-name"><?= $e($item['name']) ?></span>
                    <?php
                    $opts = json_decode($item['options'] ?? '{}', true);
                    if (!empty($opts)):
                    ?>
                    <span class="prep-item-opts">
                        <?php foreach ($opts as $k => $v): ?>
                            <small><?= $e($k) ?>: <?= $e($v) ?></small>
                        <?php endforeach; ?>
                    </span>
                    <?php endif; ?>
                </div>
                <?php endforeach; ?>
            </div>
            <?php endif; ?>

            <!-- Bouton d'action -->
            <?php if ($o['status'] !== 'ready'): ?>
            <form method="POST" action="<?= BASE_URL ?>/preparation/<?= $o['id'] ?>/ready">
                <?= \App\Core\Security::csrfField() ?>
                <button type="submit" class="btn <?= $o['status'] === 'pending' ? 'btn-primary' : 'btn-success' ?> btn-full">
                    <?= $o['status'] === 'pending' ? 'Commencer la preparation' : 'Marquer comme prete' ?>
                </button>
            </form>
            <?php else: ?>
            <div class="prep-done">Prete &mdash; en attente de remise au client</div>
            <?php endif; ?>
        </div>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>
</div>

<!-- Auto-refresh toutes les 15 secondes -->
<script>
setTimeout(function() { window.location.reload(); }, 15000);
</script>
