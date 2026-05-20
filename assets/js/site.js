/* SavingsRE â shared site script
   Defensive: every element is feature-detected before binding. */
(function () {
  'use strict';

  // ââ GA4 setup âââââââââââââââââââââââââââââââââââââââââ
  var GA_ID = 'G-GYL4MLT1C6';
  if (!window.dataLayer) window.dataLayer = [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  // Inject the gtag.js loader if not already present
  if (!document.querySelector('script[src*="googletagmanager.com/gtag/js"]')) {
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
  }
  window.gtag('js', new Date());
  // Tracking helpers â exposed globally so inline onclicks keep working
  window.trackMLS = function (seg) { window.dataLayer = window.dataLayer || []; window.dataLayer.push({ event: 'mls_link_click', segment: seg }); };
  window.trackInsurance = function () { window.dataLayer = window.dataLayer || []; window.dataLayer.push({ event: 'insurance_cta_click', destination: 'alphageninsurance.com' }); };
  window.trackSchedule = function () { window.dataLayer = window.dataLayer || []; window.dataLayer.push({ event: 'schedule_click', destination: 'calendar.app.google' }); };
  window.trackPhone = function () { window.dataLayer = window.dataLayer || []; window.dataLayer.push({ event: 'phone_click', phone_number: '+15612200402', link_label: 'header_cta' }); };

  // ââ DOM ready âââââââââââââââââââââââââââââââââââââââââ
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    // Header scroll shadow
    var header = document.getElementById('site-header') || document.querySelector('header');
    if (header) {
      window.addEventListener('scroll', function () {
        if (window.scrollY > 80) header.classList.add('scrolled');
        else header.classList.remove('scrolled');
      }, { passive: true });
    }

    // Mobile menu â modern pattern: .mobile-toggle button + #nav-links list
    var modernToggle = document.getElementById('mobile-toggle');
    var modernNav = document.getElementById('nav-links');
    if (modernToggle && modernNav) {
      var openIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
      var closeIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';

      modernToggle.addEventListener('click', function () {
        var isOpen = modernNav.classList.toggle('open');
        modernToggle.setAttribute('aria-expanded', isOpen);
        modernToggle.innerHTML = isOpen ? closeIcon : openIcon;
      });

      modernNav.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
          modernNav.classList.remove('open');
          modernToggle.setAttribute('aria-expanded', 'false');
          modernToggle.innerHTML = openIcon;
        });
      });
    }

    // Mobile menu â also bind the standard slide-down panel pattern
    // (.mobile-toggle / .hamburger) â (#mobile-nav / #mobileNav / .mobile-nav)
    var altToggle = document.querySelector('.mobile-toggle, .hamburger');
    var altPanel = document.getElementById('mobile-nav') || document.getElementById('mobileNav') || document.querySelector('.mobile-nav');
    if (altToggle && altPanel && altPanel !== modernNav) {
      altToggle.addEventListener('click', function () {
        altPanel.classList.toggle('open');
      });
      altPanel.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () { altPanel.classList.remove('open'); });
      });
    }
  });
})();
