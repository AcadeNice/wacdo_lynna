/**
 * Wacdo - Écran final
 * Bouton "Nouvelle commande"
 */

document.getElementById("new-order-btn").addEventListener("click", () => {

  // Nettoyer les données de session
  sessionStorage.removeItem("mode");
  sessionStorage.removeItem("chevalet");
  sessionStorage.removeItem("pendingOrder");

  // Redirection vers la sélection du mode
  window.location.href = "../html/mode-selection.html";
});
