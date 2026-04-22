<?php
$title = $menu ? 'Modifier menu' : 'Nouveau menu';
$e = fn($v) => \App\Core\Security::escape($v);
$action = $menu ? BASE_URL.'/menus/'.$menu['id'] : BASE_URL.'/menus';
?>
<div class="card">
    <h2><?= $e($title) ?></h2>
    <form method="POST" action="<?= $action ?>">
        <?= \App\Core\Security::csrfField() ?>
        <div class="form-group">
            <label>Nom</label>
            <input type="text" name="name" value="<?= $e($menu['name'] ?? '') ?>" required>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Prix de base (&euro;)</label>
                <input type="number" step="0.01" name="base_price" value="<?= $menu['base_price'] ?? '' ?>" required>
            </div>
            <div class="form-group">
                <label>Image (chemin)</label>
                <input type="text" name="image" value="<?= $e($menu['image'] ?? '') ?>">
            </div>
        </div>
        <div class="form-group">
            <label>Description</label>
            <textarea name="description" rows="3"><?= $e($menu['description'] ?? '') ?></textarea>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="available" value="1" <?= ($menu['available'] ?? 1) ? 'checked' : '' ?>> Disponible</label>
        </div>
        <h3>Composition du menu</h3>
        <p class="hint">Selectionnez les produits disponibles pour chaque type :</p>
        <?php
        $types = ['burger' => 'Burgers', 'side' => 'Accompagnements', 'drink' => 'Boissons', 'sauce' => 'Sauces'];
        $existingComps = [];
        foreach ($compositions ?? [] as $comp) {
            $existingComps[$comp['type']][] = $comp['product_id'];
        }
        foreach ($types as $type => $label): ?>
        <div class="form-group">
            <label><?= $label ?></label>
            <select name="comp_<?= $type ?>[]" multiple class="multi-select">
                <?php foreach ($products as $p): ?>
                <option value="<?= $p['id'] ?>"
                    <?= in_array($p['id'], $existingComps[$type] ?? []) ? 'selected' : '' ?>>
                    <?= $e($p['name']) ?> (<?= $e($p['category_name'] ?? '') ?>)
                </option>
                <?php endforeach; ?>
            </select>
        </div>
        <?php endforeach; ?>
        <button type="submit" class="btn btn-primary">Enregistrer</button>
        <a href="<?= BASE_URL ?>/menus" class="btn">Annuler</a>
    </form>
</div>
