/**
 * Wacdo - Sélection du mode de consommation
 * Stocke le mode choisi (sur-place / a-emporter) en sessionStorage
 * puis redirige vers la page de commande.
 */

document.getElementById("sur-place").addEventListener("click", function () {
  sessionStorage.setItem("mode", "sur-place");
  window.location.href = "../html/index.html";
});

document.getElementById("emporter").addEventListener("click", function () {
  sessionStorage.setItem("mode", "a-emporter");
  window.location.href = "../html/index.html";
});
