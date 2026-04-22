<?php
$title = 'Modifier commande #' . ($order['order_number'] ?? '');
$e = fn($v) => \App\Core\Security::escape($v);
?>
<div class="card">
    <h2>Modifier la commande n&deg;<?= $e($order['order_number']) ?></h2>

    <form method="POST" action="<?= BASE_URL ?>/orders/<?= $order['id'] ?>" id="order-edit-form">
        <?= \App\Core\Security::csrfField() ?>

        <div class="form-row">
            <div class="form-group">
                <label>Numero de commande</label>
                <input type="text" name="order_number" value="<?= $e($order['order_number']) ?>" required>
            </div>

            <div class="form-group">
                <label>Mode</label>
                <select name="mode" id="order-mode" onchange="toggleChevalet()">
                    <option value="sur-place" <?= $order['mode'] === 'sur-place' ? 'selected' : '' ?>>Sur place</option>
                    <option value="a-emporter" <?= $order['mode'] === 'a-emporter' ? 'selected' : '' ?>>A emporter</option>
                </select>
            </div>

            <div class="form-group" id="chevalet-group" style="display:none">
                <label>Chevalet</label>
                <input type="number" name="chevalet" min="1" value="<?= $order['chevalet'] !== null ? (int) $order['chevalet'] : '' ?>">
            </div>

            <div class="form-group">
                <label>Statut</label>
                <select name="status">
                    <?php $statuses = ['pending' => 'En attente', 'preparing' => 'En preparation', 'ready' => 'Prete', 'delivered' => 'Remise', 'cancelled' => 'Annulee']; ?>
                    <?php foreach ($statuses as $value => $label): ?>
                    <option value="<?= $value ?>" <?= $order['status'] === $value ? 'selected' : '' ?>><?= $label ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
        </div>

        <h3>Articles</h3>
        <div id="items-container">
            <?php if (!empty($order['items'])): ?>
                <?php foreach ($order['items'] as $item): ?>
                <div class="item-row form-row">
                    <div class="form-group" style="flex:2">
                        <input type="text" name="item_name[]" value="<?= $e($item['name']) ?>" placeholder="Nom du produit">
                    </div>
                    <div class="form-group">
                        <input type="number" name="item_qty[]" min="1" value="<?= (int) $item['quantity'] ?>" placeholder="Qte">
                    </div>
                    <div class="form-group">
                        <input type="number" step="0.01" min="0" name="item_price[]" value="<?= (float) $item['unit_price'] ?>" placeholder="Prix unitaire">
                    </div>
                    <div class="form-group">
                        <button type="button" class="btn btn-danger" onclick="removeItemRow(this)">Retirer</button>
                    </div>
                </div>
                <?php endforeach; ?>
            <?php else: ?>
                <div class="item-row form-row">
                    <div class="form-group" style="flex:2"><input type="text" name="item_name[]" placeholder="Nom du produit"></div>
                    <div class="form-group"><input type="number" name="item_qty[]" value="1" min="1" placeholder="Qte"></div>
                    <div class="form-group"><input type="number" step="0.01" min="0" name="item_price[]" placeholder="Prix unitaire"></div>
                    <div class="form-group"><button type="button" class="btn btn-danger" onclick="removeItemRow(this)">Retirer</button></div>
                </div>
            <?php endif; ?>
        </div>

        <button type="button" class="btn" onclick="addItemRow()">+ Ajouter un article</button>
        <hr>
        <button type="submit" class="btn btn-primary">Enregistrer les modifications</button>
        <a href="<?= BASE_URL ?>/orders/<?= $order['id'] ?>" class="btn">Annuler</a>
    </form>
</div>

<script>
function addItemRow() {
    const c = document.getElementById('items-container');
    const row = document.createElement('div');
    row.className = 'item-row form-row';
    row.innerHTML = '<div class="form-group" style="flex:2"><input type="text" name="item_name[]" placeholder="Nom du produit"></div>'
        + '<div class="form-group"><input type="number" name="item_qty[]" value="1" min="1" placeholder="Qte"></div>'
        + '<div class="form-group"><input type="number" step="0.01" min="0" name="item_price[]" placeholder="Prix unitaire"></div>'
        + '<div class="form-group"><button type="button" class="btn btn-danger" onclick="removeItemRow(this)">Retirer</button></div>';
    c.appendChild(row);
}

function removeItemRow(btn) {
    const rows = document.querySelectorAll('#items-container .item-row');
    if (rows.length <= 1) {
        return;
    }
    btn.closest('.item-row').remove();
}

function toggleChevalet() {
    const mode = document.getElementById('order-mode').value;
    const group = document.getElementById('chevalet-group');
    group.style.display = (mode === 'sur-place') ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', toggleChevalet);
</script>
