/* ARMORA Marketplace Framework - light enhancements for Apps Store description pages */
(function () {
  'use strict';

  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      var id = link.getAttribute('href').slice(1);
      var target = document.getElementById(id);
      if (target) {
        event.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  document.querySelectorAll('.armora-gallery img').forEach(function (img) {
    img.addEventListener('click', function () {
      if (!img.dataset.full) {
        return;
      }
      window.open(img.dataset.full || img.src, '_blank', 'noopener');
    });
  });
})();
