/**
 * Wacdo - Application de commande (Borne)
 * Version réécrite avec nouvelle modal multi-étapes
 * Panier / commande / modal produit simple conservés
 * Ancienne logique menu supprimée
 */

/* Configuration */
const CONFIG = {
    DATA_URL: "../data",
    API_URL: "http://localhost/wacdo_lynna/wacdo_back/public/api",
    CATEGORIES_WITH_SIZES: ["boissons", "frites", "salades"],
    LARGE_PRICE: 0.5
};

/* État global */
const state = {
    products: {},
    cart: [],
    currentCategory: "menus",
    currentProduct: null,
    currentOptions: {}
};

/* Nouvelle structure pour le flow menu */
let menuFlow = {
    burger: null,
    menuType: null,
    accompagnement: null,
    boisson: null,
    sauce: null
};

/* Initialisation */
document.addEventListener("DOMContentLoaded", () => {
    initializeApp();
});

function getPendingOrderFromStorage() {
    const raw = sessionStorage.getItem("pendingOrder") || localStorage.getItem("pendingOrder");
    if (!raw) return null;

    try {
        return JSON.parse(raw);
    } catch (error) {
        console.error("Erreur lecture pendingOrder :", error);
        return null;
    }
}

function clearPendingOrderStorage() {
    sessionStorage.removeItem("pendingOrder");
    localStorage.removeItem("pendingOrder");
    sessionStorage.removeItem("finalizePendingOrder");
    sessionStorage.removeItem("chevalet");
}

/* Initialise l'application */
async function initializeApp() {
    try {
        await loadProducts();
        setupEventListeners();
        displayProducts(state.currentCategory);
        loadCartFromStorage();
        updateCartDisplay();

        // Numéro de commande (auto-généré)
        state.orderNumber = String(Math.floor(Math.random() * 900) + 100);
        const mode = sessionStorage.getItem("mode") || "sur-place";
        const modeLabel = mode === "a-emporter" ? "À emporter" : "Sur place";

        const orderNumEl = document.getElementById("order-display-number");
        const orderModeEl = document.getElementById("order-display-mode");
        const orderNumInput = document.getElementById("order-number");

        // Utilise par le flux sur-place (page chevalet)
        sessionStorage.setItem("orderNumber", state.orderNumber);

        if (orderNumEl) orderNumEl.textContent = state.orderNumber;
        if (orderModeEl) orderModeEl.textContent = `${modeLabel} - ${state.orderNumber}`;
        if (orderNumInput) orderNumInput.value = state.orderNumber;

    } catch (error) {
        console.error("Erreur init :", error);
        showNotification("Erreur lors du chargement", "error");
    }
}

/* Chargement JSON */
async function loadProducts() {
    const response = await fetch(`${CONFIG.DATA_URL}/produits.json`);
    if (!response.ok) throw new Error("Erreur HTTP : " + response.status);
    state.products = await response.json();
}

/* Écouteurs */
function setupEventListeners() {
    document.querySelectorAll(".cat-btn").forEach(btn => {
        btn.addEventListener("click", handleCategoryChange);
    });

    document.getElementById("clear-cart-btn").addEventListener("click", clearCart);
    document.getElementById("order-btn").addEventListener("click", handleOrderClick);
    document.getElementById("abandon-btn").addEventListener("click", handleAbandon);

    // Modal produit simple
    document.querySelectorAll(".modal-close")[0].addEventListener("click", closeProductModal);
    document.getElementById("product-modal").addEventListener("click", handleModalBackdropClick);

    document.getElementById("qty-plus").addEventListener("click", increaseQuantity);
    document.getElementById("qty-minus").addEventListener("click", decreaseQuantity);
    document.getElementById("add-to-cart-btn").addEventListener("click", handleAddToCart);

    // Modal commande
    document.querySelectorAll(".modal-close")[1].addEventListener("click", closeOrderModal);
    document.getElementById("order-modal").addEventListener("click", handleOrderModalBackdropClick);
    document.getElementById("order-form").addEventListener("submit", handleOrderSubmit);
}

/* Changement de catégorie */
function handleCategoryChange(e) {
    const category = e.currentTarget.dataset.category;
    state.currentCategory = category;

    document.querySelectorAll(".cat-btn").forEach(btn => {
        btn.classList.remove("active");
        btn.setAttribute("aria-selected", "false");
    });

    e.currentTarget.classList.add("active");
    e.currentTarget.setAttribute("aria-selected", "true");

    displayProducts(category);
}

/* Affichage produits */
function displayProducts(category) {
    const grid = document.getElementById("products-grid");
    const products = state.products[category] || [];

    if (products.length === 0) {
        grid.innerHTML = '<div class="empty-state"><p>Aucun produit disponible</p></div>';
        return;
    }

    grid.innerHTML = products.map(product => `
        <div class="product-card" role="listitem" data-product-id="${product.id}">
            <img src="../img${product.image}" alt="${escapeHtml(product.nom)}" class="product-image">
            <div class="product-info">
                <h3 class="product-name">${escapeHtml(product.nom)}</h3>
                <div class="product-price">${formatPrice(product.prix)}</div>
            </div>
        </div>
    `).join("");

    grid.querySelectorAll(".product-card").forEach(card => {
        card.addEventListener("click", () => handleProductClick(card));
    });
}

/* Clic produit */
function handleProductClick(card) {
    const productId = parseInt(card.dataset.productId, 10);
    const product = findProductById(productId);
    if (!product) return;

    state.currentProduct = product;

    if (state.currentCategory === "menus") {
        openMenuFlow(product); // 🔥 nouvelle modal multi-étapes
    } else {
        openProductModal(product); // modal simple
    }
}

/* Modal produit simple */
function openProductModal(product) {
    const modal = document.getElementById("product-modal");

    document.getElementById("modal-image").src = `../img${product.image}`;
    document.getElementById("modal-product-name").textContent = product.nom;
    document.getElementById("modal-product-price").textContent = formatPrice(product.prix);

    const hasSize = CONFIG.CATEGORIES_WITH_SIZES.includes(state.currentCategory);
    document.getElementById("size-options").style.display = hasSize ? "block" : "none";

    state.currentOptions = {
        quantity: 1,
        size: "regular"
    };

    document.getElementById("quantity-input").value = 1;
    document.querySelector('input[name="product-size"][value="regular"]').checked = true;

    modal.setAttribute("aria-hidden", "false");
    updateModalPrice();
}

function closeProductModal() {
    document.getElementById("product-modal").setAttribute("aria-hidden", "true");
}

function handleModalBackdropClick(e) {
    if (e.target === e.currentTarget) closeProductModal();
}

/* Quantité */
function increaseQuantity() {
    const input = document.getElementById("quantity-input");
    input.value = parseInt(input.value, 10) + 1;
    state.currentOptions.quantity = parseInt(input.value, 10);
    updateModalPrice();
}

function decreaseQuantity() {
    const input = document.getElementById("quantity-input");
    const val = parseInt(input.value, 10);
    if (val > 1) {
        input.value = val - 1;
        state.currentOptions.quantity = val - 1;
        updateModalPrice();
    }
}

/* Prix produit simple */
function calculateProductPrice() {
    const product = state.currentProduct;
    let price = product.prix;

    if (CONFIG.CATEGORIES_WITH_SIZES.includes(state.currentCategory)) {
        const sizeRadio = document.querySelector('input[name="product-size"]:checked');
        if (sizeRadio && sizeRadio.value === "large") {
            price += CONFIG.LARGE_PRICE;
        }
    }

    return price;
}

function updateModalPrice() {
    const price = calculateProductPrice();
    const quantity = state.currentOptions.quantity;
    const totalPrice = price * quantity;

    document.getElementById("modal-product-price").textContent = formatPrice(price);
    document.getElementById("modal-total-price").textContent = formatPrice(totalPrice);
}


/* ================================
   AJOUT AU PANIER (produits simples)
   ================================ */

function handleAddToCart() {
    const price = calculateProductPrice();

    const cartItem = {
        id: Date.now(),
        productId: state.currentProduct.id,
        name: state.currentProduct.nom,
        category: state.currentCategory,
        price: price,
        quantity: state.currentOptions.quantity,
        image: state.currentProduct.image,
        options: JSON.parse(JSON.stringify(state.currentOptions))
    };

    state.cart.push(cartItem);
    saveCartToStorage();
    updateCartDisplay();
    closeProductModal();
    showNotification("Produit ajouté au panier !", "success");
}

/* ================================
   AFFICHAGE DU PANIER
   ================================ */

function updateCartDisplay() {
    const cartItems = document.getElementById("cart-items");

    if (state.cart.length === 0) {
        cartItems.innerHTML = '<div class="empty-state"><p>Panier vide</p></div>';
        document.getElementById("order-btn").disabled = true;
    } else {
        cartItems.innerHTML = state.cart.map((item, index) => {
            const details = getCartItemDetails(item);
            return `
                <div class="cart-item" role="listitem">
                    <div class="cart-item-header">
                        <div class="cart-item-name">${item.quantity} ${escapeHtml(item.name)}</div>
                        <button class="cart-item-remove" aria-label="Supprimer" data-index="${index}">&times;</button>
                    </div>
                    ${details ? `<div class="cart-item-details">${details}</div>` : ""}
                    <div class="cart-item-footer">
                        <div class="cart-item-qty">
                            <button aria-label="Diminuer" data-action="decrease" data-index="${index}">&minus;</button>
                            <span>${item.quantity}</span>
                            <button aria-label="Augmenter" data-action="increase" data-index="${index}">+</button>
                        </div>
                        <div class="cart-item-price">${formatPrice(item.price * item.quantity)}</div>
                    </div>
                </div>
            `;
        }).join("");

        // Suppression
        cartItems.querySelectorAll(".cart-item-remove").forEach(btn => {
            btn.addEventListener("click", () => {
                removeFromCart(parseInt(btn.dataset.index, 10));
            });
        });

        // Quantités
        cartItems.querySelectorAll(".cart-item-qty button").forEach(btn => {
            btn.addEventListener("click", () => {
                const action = btn.dataset.action;
                const idx = parseInt(btn.dataset.index, 10);

                if (action === "increase") {
                    state.cart[idx].quantity++;
                } else if (action === "decrease" && state.cart[idx].quantity > 1) {
                    state.cart[idx].quantity--;
                }

                saveCartToStorage();
                updateCartDisplay();
            });
        });

        document.getElementById("order-btn").disabled = false;
    }

    updateCartSummary();
}

/* ================================
   DÉTAILS D’UN ARTICLE (puces)
   ================================ */

function getCartItemDetails(item) {
    if (item.category !== "menus") return "";
    const bullets = [];

    if (item.options.accompagnement) {
        const side = findProductById(item.options.accompagnement);
        if (side) bullets.push(side.nom.toLowerCase());
    }

    if (item.options.boisson) {
        const drink = findProductById(item.options.boisson);
        if (drink) bullets.push(drink.nom.toLowerCase());
    }

    if (item.options.sauce) {
        const sauce = findProductById(item.options.sauce);
        if (sauce) bullets.push(sauce.nom.toLowerCase());
    }

    return bullets.map(b => "· " + escapeHtml(b)).join("<br>");
}

/* ================================
   SUPPRESSION D’UN ARTICLE
   ================================ */

function removeFromCart(index) {
    state.cart.splice(index, 1);
    saveCartToStorage();
    updateCartDisplay();
}

/* ================================
   VIDER LE PANIER
   ================================ */

function clearCart() {
    if (confirm("Êtes-vous sûr de vouloir vider le panier ?")) {
        state.cart = [];
        saveCartToStorage();
        updateCartDisplay();
        showNotification("Panier vide", "info");
    }
}

/* ================================
   TOTALS PANIER
   ================================ */

function updateCartSummary() {
    const subtotal = state.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const delivery = 0;
    const total = subtotal + delivery;

    const subtotalEl = document.getElementById("subtotal");
    const deliveryEl = document.getElementById("delivery");
    const totalEl = document.getElementById("total");

    if (subtotalEl) subtotalEl.textContent = formatPrice(subtotal);
    if (deliveryEl) deliveryEl.textContent = formatPrice(delivery);
    if (totalEl) totalEl.textContent = formatPrice(total);

    const cartTotalEl = document.getElementById("cart-total-display");
    if (cartTotalEl) cartTotalEl.textContent = formatPrice(total);
}

/* ================================
   ABANDON DE COMMANDE
   ================================ */

function handleAbandon() {
    if (state.cart.length === 0 || confirm("Abandonner la commande en cours ?")) {
        state.cart = [];
        saveCartToStorage();
        sessionStorage.removeItem("mode");
        window.location.href = "../html/mode-selection.html";
    }
}

/* ================================
   UTILITAIRES
   ================================ */

function findProductById(id) {
    for (const category in state.products) {
        const found = state.products[category].find(p => p.id === id);
        if (found) return found;
    }
    return null;
}

function formatPrice(price) {
    return new Intl.NumberFormat("fr-FR", {
        style: "currency",
        currency: "EUR",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(price);
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

function showNotification(message, type = "info") {
    const colors = {
        success: "#2ec934",
        error: "#dc2f02",
        info: "#3498db"
    };

    const notification = document.createElement("div");
    notification.style.cssText =
        "position: fixed; top: 20px; right: 20px; padding: 14px 20px;" +
        "background:" + (colors[type] || colors.info) + ";" +
        "color:#fff; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.15);" +
        "z-index:2000; animation:slideInRight 0.3s ease; font-weight:500; font-size:14px;" +
        "font-family:Inter,sans-serif; max-width:360px;";
    notification.textContent = message;
    notification.setAttribute("role", "alert");
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = "slideOutRight 0.3s ease";
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/* ================================
   LOCAL STORAGE
   ================================ */

function saveCartToStorage() {
    try {
        localStorage.setItem("wacdo_cart", JSON.stringify(state.cart));
    } catch (error) {
        console.error("Erreur sauvegarde panier :", error);
    }
}

function loadCartFromStorage() {
    try {
        const saved = localStorage.getItem("wacdo_cart");
        if (saved) state.cart = JSON.parse(saved);
    } catch (error) {
        console.error("Erreur chargement panier :", error);
        state.cart = [];
    }
}


/* ================================
   MODAL COMMANDE
   ================================ */

function handleOrderClick() {
    if (state.cart.length === 0) {
        showNotification("Veuillez ajouter des produits au panier", "error");
        return;
    }

    displayOrderSummary();
    document.getElementById("order-modal").setAttribute("aria-hidden", "false");
}

function closeOrderModal() {
    document.getElementById("order-modal").setAttribute("aria-hidden", "true");
}

function handleOrderModalBackdropClick(e) {
    if (e.target === e.currentTarget) closeOrderModal();
}

/* ================================
   RÉCAPITULATIF DE COMMANDE
   ================================ */

function displayOrderSummary() {
    const summary = document.getElementById("order-summary");
    const total = state.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

    summary.innerHTML = state.cart.map(item => `
        <div class="order-summary-item">
            <div class="order-summary-item-name">
                ${escapeHtml(item.name)} x${item.quantity}
            </div>
            <div class="order-summary-item-details">
                ${getCartItemDetails(item)}<br>
                <strong>${formatPrice(item.price * item.quantity)}</strong>
            </div>
        </div>
    `).join("");

    document.getElementById("order-total").textContent = formatPrice(total);
}

/* ================================
   SOUMISSION DE COMMANDE
   ================================ */

async function handleOrderSubmit(e) {
    e.preventDefault();

    const orderNumber = state.orderNumber;

    try {
        const orderData = {
            orderNumber: orderNumber,
            timestamp: new Date().toISOString(),
            mode: sessionStorage.getItem("mode") || "sur-place",
            items: state.cart.map(item => ({
                productId: null,
                name: item.name,
                category: item.category,
                quantity: item.quantity,
                unitPrice: item.price,
                totalPrice: item.price * item.quantity,
                options: item.options
            })),
            total: state.cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
        };

        const mode = sessionStorage.getItem("mode") || "sur-place";
        if (mode === "sur-place") {
            // En mode sur-place, on finalise la commande depuis la page chevalet
            // pour garantir que le numero de chevalet est bien enregistre en base.
            const pendingOrderJson = JSON.stringify(orderData);
            sessionStorage.setItem("pendingOrder", pendingOrderJson);
            localStorage.setItem("pendingOrder", pendingOrderJson);
            closeOrderModal();
            window.location.href = "../html/chevalet.html";
            return;
        }

        await submitOrder(orderData);

        sessionStorage.removeItem("pendingOrder");
        localStorage.removeItem("pendingOrder");
        sessionStorage.removeItem("finalizePendingOrder");
        sessionStorage.removeItem("chevalet");

        state.cart = [];
        saveCartToStorage();
        closeOrderModal();

        if (mode === "a-emporter") {
            window.location.href = "../html/success.html";
        }

    } catch (error) {
        console.error("Erreur soumission :", error);
        showNotification("Erreur lors de la soumission de la commande", "error");
    }
}

/* ================================
   ENVOI AU BACK-END
   ================================ */

async function submitOrder(orderData) {
    console.log("Envoi commande :", JSON.stringify(orderData, null, 2));

    const response = await fetch(`${CONFIG.API_URL}/commande`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        body: JSON.stringify(orderData)
    });

    const result = await response.json();

    if (!response.ok) {
        const errMsg = result.error || "Erreur lors de l'envoi de la commande";
        throw new Error(errMsg);
    }

    console.log("Commande acceptée — ID serveur :", result.orderId);
    return result;
}


/* ============================================================
   NOUVELLE MODAL MULTI-ÉTAPES (MENU FLOW)
   ============================================================ */

const menuModal = document.getElementById("menu-flow-modal");
const menuModalBody = menuModal.querySelector(".modal-step-body");
const menuModalBtn = menuModal.querySelector(".modal-step-button");
const menuModalBack = menuModal.querySelector(".modal-step-back");
const menuModalClose = menuModal.querySelector(".modal-step-close");

let currentStep = "burger";

/* Ouvre le flow menu */
function openMenuFlow(product) {
    state.currentProduct = product;

    // Reset flow
    menuFlow = {
        burger: null,
        accompagnement: null,
        boisson: null,
        sauce: null
    };

    currentStep = "burger";
    renderStep();

    menuModal.setAttribute("aria-hidden", "false");
}

/* Ferme le flow */
function closeMenuFlow() {
    menuModal.setAttribute("aria-hidden", "true");
}

/* Navigation */
menuModalBack.addEventListener("click", () => {
    if (currentStep === "burger") {
        closeMenuFlow();
        return;
    }
    if (currentStep === "accompagnement") currentStep = "burger";
    else if (currentStep === "boisson") currentStep = "accompagnement";
    else if (currentStep === "sauce") currentStep = "boisson";

    renderStep();
});

menuModalClose.addEventListener("click", closeMenuFlow);

/* Rendu d'une étape */
function renderStep() {
    let title = "";
    let subtitle = "";
    let items = [];

    if (currentStep === "burger") {
        title = "Choisissez votre burger";
        subtitle = "Sélectionnez un burger pour votre menu";
        items = state.products.burgers || [];
    }

    if (currentStep === "accompagnement") {
        title = "Choisissez votre accompagnement";
        subtitle = "Frites ou salade ?";
        items = [...(state.products.frites || []), ...(state.products.salades || [])];
    }

    if (currentStep === "boisson") {
        title = "Choisissez votre boisson";
        subtitle = "Sélectionnez une boisson pour votre menu";
        items = state.products.boissons || [];
    }

    if (currentStep === "sauce") {
        title = "Choisissez votre sauce";
        subtitle = "Sélectionnez une sauce pour votre menu";
        items = state.products.sauces || [];
    }

    menuModalBody.innerHTML = `
        <h2 class="modal-step-title">${title}</h2>
        <p class="modal-step-subtitle">${subtitle}</p>

        <div class="modal-step-grid">
            ${items.map(item => `
                <div class="modal-step-card" data-id="${item.id}">
                    <img src="../img${item.image}" alt="${escapeHtml(item.nom)}">
                    <div class="modal-step-card-title">${escapeHtml(item.nom)}</div>
                    ${item.prix ? `<div class="modal-step-card-desc">${formatPrice(item.prix)}</div>` : ""}
                </div>
            `).join("")}
        </div>
    `;

    // Sélection
    menuModalBody.querySelectorAll(".modal-step-card").forEach(card => {
        card.addEventListener("click", () => {
            menuModalBody.querySelectorAll(".modal-step-card").forEach(c => c.classList.remove("selected"));
            card.classList.add("selected");

            const id = parseInt(card.dataset.id, 10);

            if (currentStep === "burger") menuFlow.burger = id;
            if (currentStep === "accompagnement") menuFlow.accompagnement = id;
            if (currentStep === "boisson") menuFlow.boisson = id;
            if (currentStep === "sauce") menuFlow.sauce = id;
        });
    });

    // Bouton
    if (currentStep === "sauce") {
        menuModalBtn.textContent = "Ajouter au panier";
    } else {
        menuModalBtn.textContent = "Continuer";
    }
}

/* Validation */
menuModalBtn.addEventListener("click", () => {
    if (currentStep === "burger" && !menuFlow.burger) {
        showNotification("Veuillez choisir un burger", "error");
        return;
    }
    if (currentStep === "accompagnement" && !menuFlow.accompagnement) {
        showNotification("Veuillez choisir un accompagnement", "error");
        return;
    }
    if (currentStep === "boisson" && !menuFlow.boisson) {
        showNotification("Veuillez choisir une boisson", "error");
        return;
    }
    if (currentStep === "sauce" && !menuFlow.sauce) {
        showNotification("Veuillez choisir une sauce", "error");
        return;
    }

    if (currentStep === "burger") currentStep = "accompagnement";
    else if (currentStep === "accompagnement") currentStep = "boisson";
    else if (currentStep === "boisson") currentStep = "sauce";
    else if (currentStep === "sauce") {
        addMenuToCart();
        closeMenuFlow();
        return;
    }

    renderStep();
});

/* Ajout du menu au panier */
function addMenuToCart() {
    const product = state.currentProduct;

    const burger = findProductById(menuFlow.burger);
    const side = findProductById(menuFlow.accompagnement);
    const drink = findProductById(menuFlow.boisson);
    const sauce = findProductById(menuFlow.sauce);

    let totalPrice = product.prix;
    if (burger) totalPrice += burger.prix;
    if (side) totalPrice += side.prix;
    if (drink) totalPrice += drink.prix;
    if (sauce) totalPrice += sauce.prix;

    const cartItem = {
        id: Date.now(),
        productId: product.id,
        name: product.nom,
        category: "menus",
        price: totalPrice,
        quantity: 1,
        image: product.image,
        options: {
            burger: menuFlow.burger,
            accompagnement: menuFlow.accompagnement,
            boisson: menuFlow.boisson,
            sauce: menuFlow.sauce
        }
    };

    state.cart.push(cartItem);
    saveCartToStorage();
    updateCartDisplay();
    showNotification("Menu ajouté au panier !", "success");
}

