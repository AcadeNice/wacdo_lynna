<?php
$title = $product ? 'Modifier produit' : 'Nouveau produit';
$e = fn($v) => \App\Core\Security::escape($v);
$action = $product ? BASE_URL.'/products/'.$product['id'] : BASE_URL.'/products';
?>
<div class="card">
    <h2><?= $e($title) ?></h2>
    <form method="POST" action="<?= $action ?>" enctype="multipart/form-data">
        <?= \App\Core\Security::csrfField() ?>
        <div class="form-group">
            <label>Nom</label>
            <input type="text" name="name" value="<?= $e($product['name'] ?? '') ?>" required>
        </div>
        <div class="form-group">
            <label>Categorie</label>
            <select name="category_id" required>
                <option value="">-- Choisir --</option>
                <?php foreach ($categories as $c): ?>
                <option value="<?= $c['id'] ?>" <?= ($product['category_id'] ?? 0) == $c['id'] ? 'selected' : '' ?>><?= $e($c['name']) ?></option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Prix (&euro;)</label>
                <input type="number" step="0.01" name="price" value="<?= $product['price'] ?? '' ?>" required>
            </div>
            <div class="form-group">
                <label>Image (chemin)</label>
                <input type="text" name="image" value="<?= $e($product['image'] ?? '') ?>">
            </div>
        </div>
        <div class="form-group">
            <label>Ou uploader une image</label>
            <input type="file" name="image_file" accept="image/*">
        </div>
        <div class="form-group">
            <label>Description</label>
            <textarea name="description" rows="3"><?= $e($product['description'] ?? '') ?></textarea>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="available" value="1" <?= ($product['available'] ?? 1) ? 'checked' : '' ?>> Disponible</label>
        </div>
        <button type="submit" class="btn btn-primary">Enregistrer</button>
        <a href="<?= BASE_URL ?>/products" class="btn">Annuler</a>
    </form>
</div>
