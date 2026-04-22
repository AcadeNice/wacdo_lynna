<?php
$title = 'Saisir une commande';
$e = fn($v) => \App\Core\Security::escape($v);
?>
<div class="card">
    <h2>Nouvelle commande (comptoir / telephone)</h2>
    <form method="POST" action="<?= BASE_URL ?>/orders" id="order-form">
        <?= \App\Core\Security::csrfField() ?>
        <div class="form-row">
            <div class="form-group">
                <label>Numero de commande</label>
                <input type="text" name="order_number" value="<?= rand(100,999) ?>" required>
            </div>
            <div class="form-group">
                <label>Mode</label>
                <select name="mode">
                    <option value="sur-place">Sur place</option>
                    <option value="a-emporter">A emporter</option>
                </select>
            </div>
        </div>
        <h3>Articles</h3>
        <div id="items-container">
            <div class="item-row form-row">
                <div class="form-group" style="flex:2"><input type="text" name="item_name[]" placeholder="Nom du produit"></div>
                <div class="form-group"><input type="number" name="item_qty[]" value="1" min="1" placeholder="Qte"></div>
                <div class="form-group"><input type="number" step="0.01" name="item_price[]" placeholder="Prix unitaire"></div>
            </div>
        </div>
        <button type="button" class="btn" onclick="addItemRow()">+ Ajouter un article</button>
        <hr>
        <button type="submit" class="btn btn-primary">Enregistrer la commande</button>
        <a href="<?= BASE_URL ?>/orders" class="btn">Annuler</a>
    </form>
</div>
<script>
function addItemRow() {
    const c = document.getElementById('items-container');
    const row = document.createElement('div');
    row.className = 'item-row form-row';
    row.innerHTML = '<div class="form-group" style="flex:2"><input type="text" name="item_name[]" placeholder="Nom du produit"></div>'
        + '<div class="form-group"><input type="number" name="item_qty[]" value="1" min="1" placeholder="Qte"></div>'
        + '<div class="form-group"><input type="number" step="0.01" name="item_price[]" placeholder="Prix unitaire"></div>';
    c.appendChild(row);
}
</script>
