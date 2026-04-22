-- Wacdo Back-End — Schema MySQL / MariaDB
CREATE DATABASE IF NOT EXISTS wacdo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE wacdo;

-- Utilisateurs (internes)
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    email       VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    role        ENUM('admin','preparation','accueil') NOT NULL DEFAULT 'accueil',
    active      TINYINT(1) NOT NULL DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Categories
CREATE TABLE IF NOT EXISTS categories (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    slug          VARCHAR(100) NOT NULL UNIQUE,
    icon          VARCHAR(255) DEFAULT NULL,
    display_order INT DEFAULT 0,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Produits
CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name        VARCHAR(150) NOT NULL,
    description TEXT,
    price       DECIMAL(8,2) NOT NULL,
    image       VARCHAR(255) DEFAULT NULL,
    available   TINYINT(1) NOT NULL DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Menus
CREATE TABLE IF NOT EXISTS menus (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    description TEXT,
    base_price  DECIMAL(8,2) NOT NULL,
    image       VARCHAR(255) DEFAULT NULL,
    available   TINYINT(1) NOT NULL DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Composition des menus
CREATE TABLE IF NOT EXISTS menu_compositions (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    menu_id    INT NOT NULL,
    product_id INT NOT NULL,
    type       ENUM('burger','side','drink','sauce') NOT NULL,
    is_default TINYINT(1) DEFAULT 0,
    FOREIGN KEY (menu_id)    REFERENCES menus(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Commandes
CREATE TABLE IF NOT EXISTS orders (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(20) NOT NULL,
    mode         ENUM('sur-place','a-emporter') NOT NULL DEFAULT 'sur-place',
    status       ENUM('pending','preparing','ready','delivered','cancelled') NOT NULL DEFAULT 'pending',
    chevalet     INT DEFAULT NULL,
    total        DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_by   INT DEFAULT NULL,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Items de commande
CREATE TABLE IF NOT EXISTS order_items (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    order_id   INT NOT NULL,
    product_id INT DEFAULT NULL,
    menu_id    INT DEFAULT NULL,
    name       VARCHAR(150) NOT NULL,
    quantity   INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(8,2) NOT NULL,
    options    JSON DEFAULT NULL,
    FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)  ON DELETE SET NULL,
    FOREIGN KEY (menu_id)    REFERENCES menus(id)     ON DELETE SET NULL
) ENGINE=InnoDB;

-- Logs de securite
CREATE TABLE IF NOT EXISTS security_logs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT DEFAULT NULL,
    action     VARCHAR(100) NOT NULL,
    details    TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
