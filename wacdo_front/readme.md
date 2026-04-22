# Wacdo - Borne Numérique de Commande

## 🚀 Accès à la Borne

**Point d'entrée:** `html/mode-selection.html`

### En développement
```bash
cd /srv/http/wacdo_lynna/wacdo_front
php -S localhost:8000
# Puis accédez à: http://localhost:8000/html/mode-selection.html
```

### En production
Accédez à: `http://votre-serveur/wacdo_lynna/wacdo_front/html/mode-selection.html`

## 📁 Structure du Projet

```
wacdo_front/
├── html/                    # Pages kiosk
│   ├── mode-selection.html  # Écran d'accueil (sur-place / à-emporter)
│   ├── index.html           # Interface principale (commande produits)
│   ├── chevalet.html        # Saisie numéro de table (sur-place)
│   └── success.html         # Confirmation de commande
├── css/                     # Feuilles de style
│   ├── styles.css           # Styles principaux
│   ├── mode-selection.css   # Styles écran d'accueil
│   ├── chevalet.css         # Styles saisie chevalet
│   └── success.css          # Styles confirmation
├── js/                      # Scripts JavaScript
│   ├── app.js               # Logique principale
│   ├── mode-selection.js    # Gestion mode sélection
│   ├── chevalet.js          # Gestion chevalet
│   └── success.js           # Gestion confirmation
├── img/                     # Images et ressources
│   ├── images/              # Logo, illustrations
│   └── categories/          # Icônes catégories
└── data/                    # Données produits
    ├── produits.json        # Catalogue produits
    └── categories.json      # Définitions catégories

```

## 🔗 Flux Utilisateur

1. **Mode sélection** → Sur-place ou À-emporter
2. **Commande** → Parcourir catégories, ajouter produits, modifier panier
3. **Sur-place uniquement** → Saisir numéro de chevalet
4. **Confirmation** → Message de remerciement

## 🎨 Design Tokens

- **Couleur primaire:** #FFC72C (jaune)
- **Police:** Inter (Google Fonts)
- **Résolution cible:** 1920×1080 (borne tactile)

## 📚 Ressources

- Données produits: `data/produits.json`
- Catégories: `data/categories.json`
- Configuration: `.htaccess` (Apache)

