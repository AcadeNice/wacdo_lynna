<?php
$title = $category ? 'Modifier categorie' : 'Nouvelle categorie';
$e = fn($v) => \App\Core\Security::escape($v);
$action = $category ? BASE_URL.'/categories/'.$category['id'] : BASE_URL.'/categories';
?>
<div class="card">
    <h2><?= $e($title) ?></h2>
    <form method="POST" action="<?= $action ?>">
        <?= \App\Core\Security::csrfField() ?>
        <div class="form-group">
            <label>Nom</label>
            <input type="text" name="name" value="<?= $e($category['name'] ?? '') ?>" required>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Icone (fichier)</label>
                <input type="text" name="icon" value="<?= $e($category['icon'] ?? '') ?>">
            </div>
            <div class="form-group">
                <label>Ordre d'affichage</label>
                <input type="number" name="display_order" value="<?= $category['display_order'] ?? 0 ?>">
            </div>
        </div>
        <button type="submit" class="btn btn-primary">Enregistrer</button>
        <a href="<?= BASE_URL ?>/categories" class="btn">Annuler</a>
    </form>
</div>
