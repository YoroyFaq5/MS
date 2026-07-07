// MAFIA STYLE — main.js

// Auto-dismiss alerts after 5s
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert.alert-success, .alert.alert-info').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 5000);
  });
});

// Navbar scroll-shrink — toggles #main-nav.is-scrolled (see main.css),
// a small height/logo shrink once the page scrolls past the hero.
(() => {
  const nav = document.getElementById('main-nav');
  if (!nav) return;
  const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 24);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
})();
