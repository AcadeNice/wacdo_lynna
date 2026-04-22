/**
 * Wacdo - Saisie du numéro de chevalet
 */

const API_URL = "http://localhost/wacdo_lynna/wacdo_back/public/api";

const input = document.getElementById("chevalet-number");
const submitBtn = document.getElementById("submit-chevalet");
const pendingOrderRaw = sessionStorage.getItem("pendingOrder");

let occupiedChevalets = [];

// Sans commande en attente, retour a l'accueil de commande.
if (!pendingOrderRaw) {
  window.location.href = "../html/index.html";
}

async function loadOccupiedChevalets() {
  try {
    const response = await fetch(`${API_URL}/chevalets/occupes`, {
      headers: { "Accept": "application/json" }
    });
    if (!response.ok) return;
    const data = await response.json();
    occupiedChevalets = Array.isArray(data.chevalets) ? data.chevalets.map(Number) : [];
  } catch (error) {
    console.error("Erreur chargement chevalets occupes:", error);
  }
}

function isChevaletAvailable(value) {
  const chevalet = Number(value);
  if (!Number.isInteger(chevalet) || chevalet < 1) return false;
  return !occupiedChevalets.includes(chevalet);
}

// Activation du bouton quand un numéro est saisi
input.addEventListener("input", () => {
  const value = input.value.trim();

  if (value !== "" && isChevaletAvailable(value)) {
    submitBtn.disabled = false;
  } else {
    submitBtn.disabled = true;
  }
});

// Validation
submitBtn.addEventListener("click", async () => {
  const chevalet = input.value.trim();

  if (!chevalet || !isChevaletAvailable(chevalet)) {
    alert("Ce numero de chevalet est deja utilise. Merci d'en choisir un autre.");
    submitBtn.disabled = true;
    return;
  }

  const pendingOrder = JSON.parse(pendingOrderRaw);
  pendingOrder.chevalet = Number(chevalet);

  try {
    const response = await fetch(`${API_URL}/commande`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(pendingOrder)
    });

    const result = await response.json();

    if (!response.ok) {
      const errMsg = result.error || "Erreur lors de l'envoi de la commande";
      alert(errMsg);
      return;
    }

    // Stocker pour affichage eventuel sur ecran final
    sessionStorage.setItem("chevalet", chevalet);
    sessionStorage.removeItem("pendingOrder");
    localStorage.removeItem("wacdo_cart");

    // Redirection vers l'écran final
    window.location.href = "../html/success.html";
  } catch (error) {
    console.error("Erreur envoi commande sur place:", error);
    alert("Erreur reseau lors de l'enregistrement de la commande.");
  }
});

loadOccupiedChevalets();

setInterval(loadOccupiedChevalets, 10000);
