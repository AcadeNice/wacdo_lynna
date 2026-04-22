# Wacdo Back-Office (Bloc 2)

## Architecture
- **Langage** : PHP 8+ (POO, heritage, interfaces)
- **Architecture** : MVC (Models / Views / Controllers)
- **Base de donnees** : MySQL / MariaDB
- **Autoloading** : PSR-4 (manuel)
- **Securite** : CSRF, XSS, bcrypt, PDO prepare

## Installation

1. **Creer la base de donnees** :
   ```bash
   php setup.php
   ```

2. **Configurer Apache** : le dossier `public/` est le document root.
   Assurez-vous que `mod_rewrite` est active.

3. **Acces** : http://localhost/wacdo_lynna/wacdo_back/public/login

## Comptes par defaut
| Utilisateur | Mot de passe | Role |
|-------------|-------------|------|
| admin | Wacdo2024! | Administration |
| preparation | Wacdo2024! | Preparation |
| accueil | Wacdo2024! | Accueil |

## API REST
| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | /api/produits | Liste des produits par categorie |
| GET | /api/produits/{categorie} | Produits d'une categorie |
| GET | /api/menus | Liste des menus |
| POST| /api/commande | Recevoir une commande (JSON) |

## Structure
```
app/
  Controllers/   - Controleurs (logique metier)
  Models/        - Modeles (acces donnees)
  Views/         - Vues (templates PHP)
  Core/          - Framework (Router, DB, Session, Security)
config/          - Configuration
routes/          - Definitions des routes
public/          - Point d'entree (index.php, CSS, JS)
sql/             - Schema et donnees initiales
```

## Base de donnees
- **users** : utilisateurs internes (admin, preparation, accueil)
- **categories** : categories de produits
- **products** : produits avec prix et images
- **menus** : menus avec composition
- **menu_compositions** : liaison menu-produits
- **orders** : commandes avec statut
- **order_items** : articles d'une commande
- **security_logs** : journal de securite
