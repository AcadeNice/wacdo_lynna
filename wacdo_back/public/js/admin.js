/**
 * Wacdo Back-Office — JavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss les alertes apres 4 secondes
    document.querySelectorAll('.alert').forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.3s';
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 300);
        }, 4000);
    });

    // Marquer le lien actif dans la sidebar
    var path = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(function(link) {
        if (path.indexOf(link.getAttribute('href')) !== -1 && link.getAttribute('href') !== '#') {
            link.classList.add('active');
        }
    });
});
